#!/usr/bin/env python3
"""Gate: every catalogued sheet is listed in llms.txt and llms-full.txt. Exit 1 on failure.

Both files are hand-curated (llms.txt leads with a "Strongest pages" section; each
has a category index below), so they drift: 25 sheets, including the site's top
search page, were missing from llms.txt when this gate was added (2026-10-25).

Rules:
  - every sheet in catalog.json appears (by URL) in the category index of both files
  - every cheatsheets.davidveksler.com/*.html URL in either file is a catalogued sheet
    or an existing file (no dead links)

--fix appends each missing sheet as "- [title](url): description" at the end of its
category section (catalog title and description, em dashes replaced), then re-checks.
--sync also rewrites existing category-index entries to the current catalog title and
description (run after retitles). Neither touches the "Strongest pages" section or the
file header: curating those stays a human/agent judgment call.
Run by scripts/build_site.py as a deploy gate.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASE = "https://cheatsheets.davidveksler.com/"
FILES = ["llms.txt", "llms-full.txt"]
URL_RE = re.compile(re.escape(BASE) + r"([A-Za-z0-9_.-]+\.html)")


def entry(sheet: dict) -> str:
    desc = (sheet.get("description") or "").replace(" — ", ", ").replace("—", ", ")
    return f"- [{sheet['title']}]({sheet['url']}): {desc}".rstrip(": ")


def missing_in(text: str, sheets: list[dict]) -> list[dict]:
    listed = set(URL_RE.findall(text))
    return [s for s in sheets if s["file"] not in listed]


def insert(text: str, sheet: dict) -> tuple[str, bool]:
    lines = text.split("\n")
    head = f"## {sheet['category']}"
    try:
        start = next(i for i, l in enumerate(lines) if l.strip() == head)
    except StopIteration:
        return text, False
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
    last = max((i for i in range(start + 1, end) if lines[i].startswith("- ")), default=start)
    lines.insert(last + 1, entry(sheet))
    return "\n".join(lines), True


def sync(text: str, by_file: dict[str, dict]) -> tuple[str, int]:
    """Rewrite entries below the first category heading to catalog title/description."""
    lines = text.split("\n")
    cats = {s["category"] for s in by_file.values()}
    in_index, changed = False, 0
    for i, line in enumerate(lines):
        if line.startswith("## "):
            in_index = in_index or line[3:].strip() in cats
            continue
        m = URL_RE.search(line)
        if in_index and line.startswith("- [") and m and m.group(1) in by_file:
            new = entry(by_file[m.group(1)])
            if new != line:
                lines[i], changed = new, changed + 1
    return "\n".join(lines), changed


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--fix", action="store_true")
    ap.add_argument("--sync", action="store_true")
    a = ap.parse_args()

    sheets = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))["sheets"]
    known = {s["file"] for s in sheets}
    errors: list[str] = []

    for name in FILES:
        path = ROOT / name
        text = path.read_text(encoding="utf-8")
        if a.sync:
            text, n = sync(text, {s["file"]: s for s in sheets})
            path.write_text(text, encoding="utf-8")
            print(f"{name}: synced {n} entries")
        miss = missing_in(text, sheets)
        if (a.fix or a.sync) and miss:
            for s in miss:
                text, ok = insert(text, s)
                print(f"{name}: {'added' if ok else 'NO SECTION for'} {s['file']} ({s['category']})")
            path.write_text(text, encoding="utf-8")
            miss = missing_in(text, sheets)
        for s in miss:
            errors.append(f"{name}: missing {s['file']} (category {s['category']})")
        for f in sorted(set(URL_RE.findall(text))):
            if f not in known and not (ROOT / f).exists():
                errors.append(f"{name}: dead link {BASE}{f}")

    for e in errors:
        print(e, file=sys.stderr)
    print(f"check_llms: {len(errors)} problem(s), {len(sheets)} sheets")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
