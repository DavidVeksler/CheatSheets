#!/usr/bin/env python3
"""Build the deterministic raw material for one newsletter issue.

READ-ONLY. Never edits a cheatsheet, never sends anything, never touches
Resend. It only computes *what happened* in the covered month from sources
already in the repo, so the routine that writes the issue can only cite
facts that are actually true — see docs/newsletter.md §6.

Sources
-------
  * New pages       -- git log --diff-filter=A over the window
  * Updated pages    -- git log --diff-filter=M --numstat, summed per file,
                         floored at UPDATED_LINE_THRESHOLD so the weekly
                         freshness job's date-stamp commits don't fill the
                         issue with noise
  * Most-read        -- popularity.json dailyViews, top N, excluding anything
                         already listed under "new"
  * Titles/descriptions/images -- read from catalog.json (scripts/build_catalog.py's
                         output; the extraction lives there once, not reimplemented here)
  * Category          -- category-map.php (regex-parsed; it's a flat PHP
                         array literal)

An issue "YYYY-MM" covers the *previous* calendar month (published on the
1st, digesting the month that just ended).

Usage:
    python scripts/newsletter_digest.py                    # current month's issue
    python scripts/newsletter_digest.py --issue 2026-09
    python scripts/newsletter_digest.py --issue 2026-09 --output newsletter/digest-2026-09.json

Exit codes: 0 ok (met the skip threshold), 2 git/repo error,
3 below the skip threshold (digest is still written for inspection).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Tuple

REPO_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from newsletter_common import newsletter_dir  # noqa: E402

UPDATED_LINE_THRESHOLD = 50   # summed insertions+deletions in-window to count as "substantially updated"
POPULAR_TOP_N = 5
SKIP_THRESHOLD = 3            # len(new) + len(updated) below this -> no issue this month


def load_catalog() -> Dict[str, Dict]:
    """filename -> catalog.json sheet entry (title, description, image, ...).

    catalog.json is the single extraction of every sheet's metadata
    (scripts/build_catalog.py); reading it here means this script never
    re-parses HTML and can't drift from what the index actually shows.
    """
    path = REPO_DIR / "catalog.json"
    if not path.exists():
        raise RuntimeError("catalog.json is missing. Run: python3 scripts/build_catalog.py")
    data = json.loads(path.read_text(encoding="utf-8"))
    return {s["file"]: s for s in data.get("sheets", [])}


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(REPO_DIR), *args], capture_output=True, text=True, encoding="utf-8"
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed:\n{result.stderr}")
    return result.stdout


def issue_window(issue: str) -> Tuple[str, str]:
    """'YYYY-MM' -> (first day of the *previous* month, first day of this month), both ISO dates."""
    year, month = (int(part) for part in issue.split("-"))
    first_of_issue_month = dt.date(year, month, 1)
    last_of_prev_month = first_of_issue_month - dt.timedelta(days=1)
    first_of_prev_month = last_of_prev_month.replace(day=1)
    return first_of_prev_month.isoformat(), first_of_issue_month.isoformat()


def load_category_map() -> Dict[str, str]:
    text = (REPO_DIR / "category-map.php").read_text(encoding="utf-8")
    return dict(re.findall(r"'([^']+\.html)'\s*=>\s*'([^']+)'", text))


def find_new_pages(since: str, until: str) -> Dict[str, Dict[str, str]]:
    """filename -> {commit, date} for the (chronologically) latest add in the window."""
    out = git(
        "log", f"--since={since}", f"--until={until}", "--diff-filter=A",
        "--name-status", "--reverse", "--pretty=format:C|%h|%aI", "--", "*.html",
    )
    result: Dict[str, Dict[str, str]] = {}
    commit_hash = commit_date = None
    for line in out.splitlines():
        if line.startswith("C|"):
            _, commit_hash, commit_date = line.split("|", 2)
        elif line.startswith("A\t") and commit_hash:
            fname = line.split("\t", 1)[1]
            if "/" not in fname and fname.endswith(".html"):
                result[fname] = {"commit": commit_hash, "date": commit_date[:10]}
    return result


def find_updated_pages(since: str, until: str, exclude: set) -> Dict[str, Dict]:
    """filename -> {lines_changed, commits[], summary_hint} for modified (not added) files."""
    out = git(
        "log", f"--since={since}", f"--until={until}", "--diff-filter=M",
        "--numstat", "--pretty=format:C|%h|%aI|%s", "--", "*.html",
    )
    changes: Dict[str, Dict] = {}
    commit_hash = subject = None
    for raw in out.splitlines():
        if raw.startswith("C|"):
            _, commit_hash, _commit_date, subject = raw.split("|", 3)
            continue
        line = raw.strip()
        if not line:
            continue
        parts = line.split("\t")
        if len(parts) != 3:
            continue
        ins, dels, fname = parts
        if "/" in fname or not fname.endswith(".html") or fname in exclude:
            continue
        ins_n = int(ins) if ins.isdigit() else 0
        dels_n = int(dels) if dels.isdigit() else 0
        entry = changes.get(fname)
        if entry is None:
            entry = {"lines_changed": 0, "commits": [], "summary_hint": subject}
            changes[fname] = entry
        entry["lines_changed"] += ins_n + dels_n
        if commit_hash not in entry["commits"]:
            entry["commits"].append(commit_hash)
        # Prefer a substantive commit subject over a freshness date-stamp one — log is
        # newest-first, so without this a file touched by both ends up with the least
        # useful "what changed" hint just because it's the most recent commit.
        if entry["summary_hint"].startswith("Weekly freshness update") and not subject.startswith("Weekly freshness update"):
            entry["summary_hint"] = subject
    return {f: c for f, c in changes.items() if c["lines_changed"] >= UPDATED_LINE_THRESHOLD}


def load_popular(top_n: int, exclude: set, valid_files: set) -> List[Dict]:
    pop_path = REPO_DIR / "popularity.json"
    if not pop_path.exists():
        return []
    data = json.loads(pop_path.read_text(encoding="utf-8"))
    daily = data.get("dailyViews", {})
    ranked = sorted(
        ((f, v) for f, v in daily.items() if f in valid_files and f not in exclude),
        key=lambda kv: kv[1], reverse=True,
    )
    return [{"file": f, "daily_views": v} for f, v in ranked[:top_n]]


def build_item(catalog_by_file: Dict[str, Dict], filename: str, category_map: Dict[str, str], extra: Dict) -> Dict:
    sheet = catalog_by_file.get(filename, {})
    item = {
        "file": filename,
        "title": sheet.get("title", filename),
        "description": sheet.get("description", ""),
        "og_image": sheet.get("image"),
        "category": category_map.get(filename, "Other"),
    }
    item.update(extra)
    return item


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--issue", default=dt.date.today().strftime("%Y-%m"), help="Issue month, YYYY-MM (default: current month).")
    parser.add_argument("--output", default=None, help="Output path (default: newsletter/digest-<issue>.json).")
    args = parser.parse_args()

    if not re.match(r"^\d{4}-\d{2}$", args.issue):
        parser.error("--issue must be YYYY-MM")

    try:
        since, until = issue_window(args.issue)
        catalog_by_file = load_catalog()
        catalogued = set(catalog_by_file)  # catalog.json already applies the exclusion/hide rules
        category_map = load_category_map()

        new_raw = find_new_pages(since, until)
        # Drop anything renamed/deleted again within the same window — e.g. added under
        # one name and rebranded to another a week later. Only the file that survives to
        # today is addressable in a newsletter link.
        new_raw = {f: info for f, info in new_raw.items() if (REPO_DIR / f).exists()}
        new_filenames = set(new_raw) & catalogued
        # Dedup: a page added and further edited within the same window is
        # "new", not also "updated". Files outside the catalog (hidden via
        # catalog-overrides.json, or the one hardcoded exclusion) are dropped
        # by the "if f in catalogued" filters on new_items/updated_items below.
        updated_raw = find_updated_pages(since, until, exclude=set(new_raw))
        updated_raw = {f: info for f, info in updated_raw.items() if (REPO_DIR / f).exists()}

        new_items = [
            build_item(catalog_by_file, f, category_map, {"added": info["date"], "commit": info["commit"]})
            for f, info in sorted(new_raw.items(), key=lambda kv: kv[1]["date"])
            if f in catalogued
        ]
        updated_items = [
            build_item(catalog_by_file, f, category_map, {
                "lines_changed": info["lines_changed"],
                "commits": info["commits"],
                "summary_hint": info["summary_hint"],
            })
            for f, info in sorted(updated_raw.items(), key=lambda kv: -kv[1]["lines_changed"])
            if f in catalogued
        ]

        valid_files = catalogued
        popular_raw = load_popular(POPULAR_TOP_N, exclude=new_filenames, valid_files=valid_files)
        popular_items = [
            build_item(catalog_by_file, p["file"], category_map, {"daily_views": p["daily_views"]})
            for p in popular_raw
        ]

        commits_in_window = git("rev-list", "--count", f"--since={since}", f"--until={until}", "HEAD").strip()

        digest = {
            "issue": args.issue,
            "window": {"from": since, "to": until},
            "new": new_items,
            "updated": updated_items,
            "popular": popular_items,
            "stats": {
                "total_pages": len(valid_files),
                "commits_in_window": int(commits_in_window) if commits_in_window.isdigit() else 0,
            },
        }
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    output = Path(args.output) if args.output else newsletter_dir() / f"digest-{args.issue}.json"
    output.write_text(json.dumps(digest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    item_count = len(new_items) + len(updated_items)
    print(f"Wrote {output} — {len(new_items)} new, {len(updated_items)} updated, {len(popular_items)} popular.")
    if item_count < SKIP_THRESHOLD:
        print(f"Below skip threshold ({item_count} < {SKIP_THRESHOLD}) — no issue this month.", file=sys.stderr)
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
