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

Staleness is read from, in order of preference:
  1. JSON-LD  "dateModified": "YYYY-MM-DD"
  2. a visible  Last verified: <Month D, YYYY>  line
  3. the file's last git commit date

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

# Section 7: whole topics that are essentially evergreen. These still deserve an
# occasional freshness-stamp pass, but they never justify a research Worker, so
# they are held out of the default batch. Matched as substrings of the filename.
EVERGREEN_MARKERS = (
    "philosophy", "objectivism", "stoicism", "religion", "bible", "theology",
    "anatomy", "bjj", "judo", "karate", "wrestling", "boxing", "martial",
    "cooking", "recipe", "whitepaper", "history-of", "latin", "chess",
    "mathematics", "logic-fallacies", "rhetoric",
)

# Per weekly-freshness-update.md section 2: a Worker budgets ~8-15 focused
# searches. Plan against the ceiling, not the average, or the last batch of the
# run is the one that starves.
SEARCHES_PER_WORKER = 15
DEFAULT_SESSION_BUDGET = 200
# Leave the Selector itself room to breathe rather than spending the pool to
# the last call.
BUDGET_HEADROOM = 20

JSONLD_DATE = re.compile(r'"dateModified"\s*:\s*"(\d{4}-\d{2}-\d{2})"')
VISIBLE_DATE = re.compile(
    r"Last verified:?\s*([A-Z][a-z]+ \d{1,2}, \d{4}|\d{4}-\d{2}-\d{2})", re.I
)


def _parse_visible(raw: str) -> dt.date | None:
    raw = raw.strip()
    for fmt in ("%Y-%m-%d", "%B %d, %Y", "%b %d, %Y"):
        try:
            return dt.datetime.strptime(raw, fmt).date()
        except ValueError:
            continue
    return None


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


def last_verified(path: Path) -> tuple[dt.date | None, str]:
    """Return (date, where it came from) for one cheatsheet."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None, "unreadable"

    m = JSONLD_DATE.search(text)
    if m:
        try:
            return dt.datetime.strptime(m.group(1), "%Y-%m-%d").date(), "json-ld"
        except ValueError:
            pass

    m = VISIBLE_DATE.search(text)
    if m:
        parsed = _parse_visible(m.group(1))
        if parsed:
            return parsed, "visible"

    git = _git_date(path)
    if git:
        return git, "git"
    return None, "unknown"


def is_evergreen(name: str) -> bool:
    stem = name.lower()
    return any(marker in stem for marker in EVERGREEN_MARKERS)


def scan(today: dt.date) -> list[dict]:
    rows = []
    for path in sorted(REPO_ROOT.glob("*.html")):
        date, source = last_verified(path)
        rows.append({
            "file": path.name,
            "last_verified": date.isoformat() if date else None,
            "date_source": source,
            # An unknown date is treated as maximally stale on purpose: a file
            # carrying no freshness marker at all is the one most likely to be
            # quietly wrong.
            "age_days": (today - date).days if date else 10_000,
            "evergreen": is_evergreen(path.stem),
        })
    rows.sort(key=lambda r: (-r["age_days"], r["file"]))
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
              f"{row['age_days']:>5}d  ({row['date_source']})")
    if deferred:
        print()
        print(f"# {len(deferred)} eligible files deferred to a later run. "
              f"Oldest deferred: {deferred[0]['file']} "
              f"({deferred[0]['age_days']}d).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
