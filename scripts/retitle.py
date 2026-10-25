#!/usr/bin/env python3
"""Retitle (and optionally re-describe) a sheet everywhere the title is repeated.

A title change touches six places that drift if edited by hand: <title>, og:title,
twitter:title, every JSON-LD string equal to the old title (headline, breadcrumb
name), and the footer breadcrumb's aria-current span. --desc does the same for the
meta description, og:description, twitter:description and JSON-LD strings equal to
the old description.

Usage:
  python scripts/retitle.py judo.html "Judo Moves and Throws: Techniques and Groundwork"
  python scripts/retitle.py judo.html "New title" --desc "New 150-200 char description"
  python scripts/retitle.py judo.html "New title" --dry-run

Afterwards: run scripts/build_catalog.py (catalog titles) and scripts/seo_check.py,
and log the before/after in docs/seo-progress.md so the next GSC pulse reads the break.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LD_RE = re.compile(r'(<script[^>]*type="application/ld\+json"[^>]*>)(.*?)(</script>)', re.S | re.I)
JSON_STR_RE = re.compile(r'"((?:[^"\\]|\\.)*)"')


def attr_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


def text_escape(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def set_meta(src: str, key: str, value: str) -> tuple[str, int]:
    pat = re.compile(r'<meta\b[^>]*\b(?:property|name)="%s"[^>]*>' % re.escape(key), re.I)

    def sub(m: re.Match) -> str:
        return re.sub(r'content="[^"]*"', lambda _: 'content="%s"' % attr_escape(value), m.group(0), count=1)

    return pat.subn(sub, src)


def get_meta(src: str, key: str) -> str | None:
    m = re.search(r'<meta\b[^>]*\b(?:property|name)="%s"[^>]*>' % re.escape(key), src, re.I)
    if not m:
        return None
    c = re.search(r'content="([^"]*)"', m.group(0))
    return html.unescape(c.group(1)) if c else None


def replace_json_strings(src: str, old: str, new: str) -> tuple[str, int]:
    """Replace JSON-LD string values that decode to `old` exactly."""
    count = 0

    def in_block(m: re.Match) -> str:
        nonlocal count

        def one(sm: re.Match) -> str:
            nonlocal count
            try:
                val = json.loads('"%s"' % sm.group(1))
            except json.JSONDecodeError:
                return sm.group(0)
            if val == old:
                count += 1
                return json.dumps(new, ensure_ascii=False)
            return sm.group(0)

        return m.group(1) + JSON_STR_RE.sub(one, m.group(2)) + m.group(3)

    return LD_RE.sub(in_block, src), count


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file")
    ap.add_argument("title")
    ap.add_argument("--desc")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    path = Path(a.file)
    if not path.is_absolute():
        path = ROOT / path
    src = path.read_text(encoding="utf-8")
    report: list[str] = []

    m = re.search(r"(<title[^>]*>)(.*?)(</title>)", src, re.S | re.I)
    if not m:
        print(f"{path.name}: no <title>", file=sys.stderr)
        return 1
    old_title = html.unescape(m.group(2).strip())
    inner = m.group(2)
    new_inner = inner.replace(inner.strip(), text_escape(a.title)) if inner.strip() else text_escape(a.title)
    src = src[: m.start(2)] + new_inner + src[m.end(2):]
    report.append(f"title: {old_title!r} -> {a.title!r} ({len(a.title)} chars)")

    for key in ("og:title", "twitter:title"):
        src, n = set_meta(src, key, a.title)
        report.append(f"{key}: {n}")
    src, n = replace_json_strings(src, old_title, a.title)
    report.append(f"json-ld strings == old title: {n}")
    crumb_old = '<span aria-current="page">%s</span>' % text_escape(old_title)
    n = src.count(crumb_old)
    src = src.replace(crumb_old, '<span aria-current="page">%s</span>' % text_escape(a.title))
    report.append(f"breadcrumb span: {n}")

    if a.desc:
        old_desc = get_meta(src, "description")
        for key in ("description", "og:description", "twitter:description"):
            src, n = set_meta(src, key, a.desc)
            report.append(f"{key}: {n}")
        if old_desc:
            src, n = replace_json_strings(src, old_desc, a.desc)
            report.append(f"json-ld strings == old desc: {n}")
        report.append(f"desc length: {len(a.desc)}")
        if not 150 <= len(a.desc) <= 200:
            report.append("WARNING: description outside 150-200 chars")

    if len(a.title) > 60:
        report.append("WARNING: title over 60 chars")
    if "—" in a.title or (a.desc and "—" in a.desc):
        report.append("WARNING: em dash in new copy")
    leftover = src.count(text_escape(old_title)) + src.count(attr_escape(old_title))
    if leftover and old_title != a.title:
        report.append(f"note: old title text still appears {leftover}x (body copy or alt text; review by hand)")

    print(f"{path.name}" + (" (dry run)" if a.dry_run else ""))
    for line in report:
        print("  " + line)
    if not a.dry_run:
        path.write_text(src, encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
