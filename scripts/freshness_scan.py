#!/usr/bin/env python3
"""Freshness selector for the cheatsheets-weekly-freshness routine.

READ-ONLY. This script never edits a cheatsheet, never touches the network, and
never bumps a date. It only decides *which* files the Selector should dispatch
Workers for this run, oldest-first.

Why this exists
---------------
weekly-freshness-update.md section 9 used to carry a hand-typed list of "the
known dated set". It drifted badly: it named ~43 files while the repo had 173,
and it omitted the entire AI-models / AI-datacenter cluster, which is the
fastest-drifting content here. A hand-maintained list of files in a prose doc
is exactly the thing that should be computed, so it is.

It also enforces the search budget. The 2026-07-26 run dispatched Workers for
56 files at 8-15 searches each against a 200-call session cap
(CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION), exhausted the pool at 9 of 14
batches, and the late Workers then "succeeded" while doing zero verification --
still bumping "Last verified" to today. Silent false provenance is a worse
failure than an incomplete run, so --limit defaults to a batch that actually
fits under the cap, and the script refuses to emit a plan that cannot.

Where staleness comes from (as of 2026-09-01)
----------------------------------------------
Cheatsheets no longer carry a visible "Last verified" line or a JSON-LD
`dateModified` field -- that stamp turned into makework, where the routine's
only real weekly output was bumping a date on a page nobody had actually
re-verified. Review status now lives in refresh-status.json at the repo root,
written once per run by the Selector after it collects every Worker's report
(never by a Worker directly, so concurrent Workers can't race on one shared
file). Staleness is read from, in order of preference:
  1. refresh-status.json "files"."<name>"."last_reviewed"  (YYYY-MM-DD)
  2. the file's last git commit date

Usage:
    python scripts/freshness_scan.py                  # this run's batch
    python scripts/freshness_scan.py --limit 20
    python scripts/freshness_scan.py --all            # full ranking, no cut
    python scripts/freshness_scan.py --json           # machine-readable
    python scripts/freshness_scan.py --include-evergreen

Exit codes: 0 ok, 2 no repo files found, 3 the requested batch cannot fit the
search budget.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REFRESH_STATUS_PATH = REPO_ROOT / "refresh-status.json"

# Section 7: whole topics that are essentially evergreen. These never justify a
# research Worker, so they are held out of the default batch.
#
# These are matched against hyphen/underscore-delimited tokens of the filename,
# not raw substrings. The original substring list silently missed most of the
# corpus it was meant to catch: it listed "philosophy"/"bjj"/"martial" while the
# actual files are named anatta-not-self.html, satipatthana-four-foundations.html,
# brazilian-jiu-jitsu.html and art-of-war-sun-tzu.html -- none of which contain
# any listed marker. On 2026-09-06 that put four Buddhist-doctrine pages and Sun
# Tzu into a 12-file budget whose whole purpose is verifying facts that drift.
EVERGREEN_PATTERNS = (
    # religion & doctrine
    r"buddhis[mt]", r"buddha", r"anatta", r"anapanasati", r"satipatthana",
    r"dhamma|dharma", r"hindrances", r"right-speech", r"craving", r"anger",
    r"islam", r"judaism", r"shabbat", r"etz-chaim", r"torah", r"bible",
    r"theology", r"religion", r"christian",
    # philosophy & rhetoric
    r"philosophy", r"objectivism", r"stoicism", r"logic-fallacies", r"rhetoric",
    r"art-of-war", r"aphorisms",
    # martial arts & technique
    r"bjj", r"jiu-jitsu", r"judo", r"karate", r"wrestling", r"boxing", r"martial",
    # anatomy, cooking, timeless reference
    r"anatomy", r"skeleton", r"human-evolution", r"cooking", r"recipe",
    r"cuisine", r"whitepaper", r"history-of", r"latin", r"chess",
    r"mathematics", r"celestial-navigation", r"stellar-lifecycle",
)

# Section 9a ranks by "staleness x volatility", but the original implementation
# only ever computed staleness, with the filename as tie-break. That is not a
# tie-break in practice: on 2026-09-06, 83 of 121 eligible files sat at exactly
# 54 days, so the batch was chosen alphabetically. Seven runs of pure a-through-b
# would have to clear before the AI / crypto / cloud cluster was reached -- the
# very cluster this script's docstring says it was written to stop omitting.
#
# So each file gets an expected review interval by topic, and files rank by how
# far past their own interval they are (age / interval), not by raw age. A
# 35-day-old AI-model page is more overdue than a 54-day-old page on how
# burglars pick locks, which is the judgment section 9a asks for.
FAST_PATTERNS = (  # drifts in weeks: model lineups, prices, live product specs
    r"^ai($|-|_)", r"-ai($|-|_)", r"^ai(risk|safety|studio)", r"(^|-|_)agi($|-|_)", r"(^|-|_)llm($|-|_)", r"(^|-|_)gpt", r"aisafety", r"airisk",
    r"doom", r"prompt", r"bitcoin", r"(^|-|_)crypto($|-|_)", r"wallet", r"exchanges",
    r"tesla", r"robots?", r"humanoid", r"aws", r"azure", r"cloud", r"gpu",
    r"smartphone", r"iphone", r"google",
)
MEDIUM_PATTERNS = (  # drifts in months: versions, standards, markets, regulation
    r"git", r"scm", r"versioncontrol", r"sql", r"databases", r"dotnet",
    r"javascript", r"python", r"devops", r"microservices", r"architecture",
    r"compression", r"cryptography", r"quantum", r"rockets", r"orbital",
    r"supersonic", r"warfare", r"firearms", r"calibers", r"operator",
    r"loadouts", r"nuclear", r"reactor", r"terawatt", r"geoengineering",
    r"materials", r"metals", r"housing", r"insurance", r"currency", r"audit",
    r"court", r"contract", r"estate", r"debt", r"claims", r"scrum",
    r"automotive", r"veterinary", r"medical", r"language-design", r"capitalism",
)
FAST_DAYS, MEDIUM_DAYS, SLOW_DAYS = 30, 60, 120

# Per weekly-freshness-update.md section 2: a Worker budgets ~8-15 focused
# searches. Plan against the ceiling, not the average, or the last batch of the
# run is the one that starves.
SEARCHES_PER_WORKER = 15
DEFAULT_SESSION_BUDGET = 200
# Leave the Selector itself room to breathe rather than spending the pool to
# the last call.
BUDGET_HEADROOM = 20


def _load_refresh_status() -> dict:
    if not REFRESH_STATUS_PATH.exists():
        return {}
    try:
        data = json.loads(REFRESH_STATUS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data.get("files", {})


def _git_date(path: Path) -> dt.date | None:
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%cs", "--", path.name],
            cwd=REPO_ROOT, capture_output=True, text=True, timeout=15,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    stamp = out.stdout.strip()
    if not stamp:
        return None
    try:
        return dt.datetime.strptime(stamp, "%Y-%m-%d").date()
    except ValueError:
        return None


def last_verified(path: Path, statuses: dict) -> tuple[dt.date | None, str]:
    """Return (date, where it came from) for one cheatsheet."""
    entry = statuses.get(path.name)
    if entry and entry.get("last_reviewed"):
        try:
            return (
                dt.datetime.strptime(entry["last_reviewed"], "%Y-%m-%d").date(),
                "refresh-status.json",
            )
        except ValueError:
            pass

    git = _git_date(path)
    if git:
        return git, "git"
    return None, "unknown"


def _matches(stem: str, patterns: tuple[str, ...]) -> bool:
    return any(re.search(p, stem) for p in patterns)


def is_evergreen(name: str) -> bool:
    return _matches(name.lower(), EVERGREEN_PATTERNS)


def review_interval(name: str) -> int:
    """Expected days between reviews for one file, by topic volatility."""
    stem = name.lower()
    if _matches(stem, FAST_PATTERNS):
        return FAST_DAYS
    if _matches(stem, MEDIUM_PATTERNS):
        return MEDIUM_DAYS
    return SLOW_DAYS


def scan(today: dt.date) -> list[dict]:
    statuses = _load_refresh_status()
    rows = []
    for path in sorted(REPO_ROOT.glob("*.html")):
        date, source = last_verified(path, statuses)
        # An unknown date is treated as maximally stale on purpose: a file
        # carrying no freshness marker at all is the one most likely to be
        # quietly wrong.
        age = (today - date).days if date else 10_000
        interval = review_interval(path.stem)
        rows.append({
            "file": path.name,
            "last_verified": date.isoformat() if date else None,
            "date_source": source,
            "age_days": age,
            "review_interval_days": interval,
            # Section 9a's "staleness x volatility": how far past its own
            # expected review interval this file is. 1.0 == exactly due.
            "overdue_ratio": round(age / interval, 3),
            "evergreen": is_evergreen(path.stem),
        })
    rows.sort(key=lambda r: (-r["overdue_ratio"], -r["age_days"], r["file"]))
    return rows


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--limit", type=int, default=None,
                    help="files to dispatch this run (default: the most the "
                         "search budget allows)")
    ap.add_argument("--min-age-days", type=int, default=30,
                    help="skip anything refreshed more recently (default 30)")
    ap.add_argument("--budget", type=int, default=DEFAULT_SESSION_BUDGET,
                    help=f"session WebSearch cap (default {DEFAULT_SESSION_BUDGET})")
    ap.add_argument("--all", action="store_true",
                    help="print the full ranking, ignoring the batch limit")
    ap.add_argument("--include-evergreen", action="store_true",
                    help="include section 7 evergreen topics")
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    args = ap.parse_args(argv)

    today = dt.date.today()
    rows = scan(today)
    if not rows:
        print(f"No .html cheatsheets found under {REPO_ROOT}", file=sys.stderr)
        return 2

    max_batch = max(1, (args.budget - BUDGET_HEADROOM) // SEARCHES_PER_WORKER)
    eligible = [r for r in rows if r["age_days"] >= args.min_age_days]
    if not args.include_evergreen:
        eligible = [r for r in eligible if not r["evergreen"]]

    if args.all:
        batch, deferred = eligible, []
    else:
        limit = args.limit if args.limit is not None else max_batch
        if limit > max_batch:
            print(
                f"Refusing to plan {limit} files: at {SEARCHES_PER_WORKER} searches "
                f"per Worker that needs {limit * SEARCHES_PER_WORKER} calls against a "
                f"{args.budget} cap. Max safe batch is {max_batch}. Raise "
                f"CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION or split across runs.",
                file=sys.stderr,
            )
            return 3
        batch, deferred = eligible[:limit], eligible[limit:]

    if args.json:
        print(json.dumps({
            "generated": today.isoformat(),
            "total_files": len(rows),
            "eligible": len(eligible),
            "max_safe_batch": max_batch,
            "batch": batch,
            "deferred_count": len(deferred),
        }, indent=2))
        return 0

    print(f"# Freshness plan for {today.isoformat()}")
    print(f"# {len(rows)} cheatsheets scanned, {len(eligible)} eligible "
          f"(stale >= {args.min_age_days}d"
          f"{'' if args.include_evergreen else ', evergreen held back'})")
    print(f"# Dispatching {len(batch)}; max safe batch is {max_batch} at a "
          f"{args.budget}-call budget.")
    print()
    for row in batch:
        stamp = row["last_verified"] or "no date found"
        print(f"  {row['file']:<48} {stamp:>12}  "
              f"{row['age_days']:>5}d  due/{row['review_interval_days']}d  "
              f"x{row['overdue_ratio']:<5}  ({row['date_source']})")
    if deferred:
        print()
        print(f"# {len(deferred)} eligible files deferred to a later run. "
              f"Oldest deferred: {deferred[0]['file']} "
              f"({deferred[0]['age_days']}d).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
