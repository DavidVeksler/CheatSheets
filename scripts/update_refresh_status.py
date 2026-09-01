#!/usr/bin/env python3
"""Selector-only helper: record that a cheatsheet was reviewed this run.

Workers never touch refresh-status.json directly -- they run concurrently
(weekly-freshness-update.md section 1) and hand-editing a shared JSON file
from parallel processes is exactly how you lose updates to a race. Instead
each Worker reports its outcome, and the Selector -- a single process, after
all Workers finish -- calls this once per file to write the result.

Usage:
    python scripts/update_refresh_status.py FILE.html --date 2026-09-01 \\
        --note "PostgreSQL/MySQL version numbers checked against release notes"

    # Worker could not verify anything this run -- leave the file's entry
    # untouched (do not call this for it at all). There is no --unverified
    # flag on purpose: an unreviewed file simply keeps its old last_reviewed
    # date, which is the honest state.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
REFRESH_STATUS_PATH = REPO_ROOT / "refresh-status.json"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                  formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file", help="cheatsheet filename, e.g. databases.html")
    ap.add_argument("--date", required=True, help="YYYY-MM-DD, today's date")
    ap.add_argument("--note", default="", help="short summary of what was reviewed")
    args = ap.parse_args(argv)

    target = REPO_ROOT / args.file
    if not target.exists():
        print(f"error: {args.file} not found in repo root", file=sys.stderr)
        return 1

    if REFRESH_STATUS_PATH.exists():
        data = json.loads(REFRESH_STATUS_PATH.read_text(encoding="utf-8"))
    else:
        data = {"_comment": (
            "Tracks when each cheatsheet's volatile facts were last reviewed "
            "by the weekly-freshness-update routine. The routine (Selector, "
            "after collecting Worker reports) is the only writer. See "
            "weekly-freshness-update.md. Do not add visible date stamps or "
            "JSON-LD dateModified to the pages themselves."
        ), "files": {}}

    data.setdefault("files", {})[args.file] = {
        "last_reviewed": args.date,
        "source": "routine",
        "note": args.note,
    }

    REFRESH_STATUS_PATH.write_text(
        json.dumps(data, indent=2, sort_keys=False) + "\n", encoding="utf-8"
    )
    print(f"refresh-status.json: {args.file} -> last_reviewed {args.date}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
