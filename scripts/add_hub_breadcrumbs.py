#!/usr/bin/env python3
"""Give every catalogued sheet a breadcrumb back to its category hub.

Why: the 15 category hubs (/<slug>, see category-hubs.json) had zero inbound
links from the sheets themselves, only the index rail and the sitemap, so
search engines treated them as filter states rather than pages. A breadcrumb
on every sheet is ~200 contextual inbound links per hub cluster from one
templated change, plus BreadcrumbList structured data for the SERP trail.

What it writes into each sheet, once, marked `data-site-breadcrumb`:

    <nav class="cs-breadcrumb" data-site-breadcrumb aria-label="Breadcrumb" ...>
      <a href="./">Cheat sheets</a> › <a href="ai-safety">AI &amp; Safety cheat sheets</a> › <span aria-current="page">Page title</span>
    </nav>
    <script type="application/ld+json" data-site-breadcrumb-ld>{BreadcrumbList}</script>

Placement, first match wins: just before the `data-site-build-note` paragraph
(the shared footer block on most sheets), else before the `data-seo-related-links`
block, else before the last `</footer>`, else before `</body>`. Re-running
replaces the existing block in place, so a category move or a title change
is picked up by running it again.

    python3 scripts/add_hub_breadcrumbs.py            # write
    python3 scripts/add_hub_breadcrumbs.py --check    # exit 1 if any sheet is stale

The --check mode is what scripts/deploy.py --check runs; it fails closed when a
new sheet ships without its breadcrumb or a hub slug changes.
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG = ROOT / "catalog.json"
HUBS = ROOT / "category-hubs.json"
SITE = "https://cheatsheets.davidveksler.com/"

BLOCK_RE = re.compile(
    r"[ \t]*<nav class=\"cs-breadcrumb\" data-site-breadcrumb[\s\S]*?</nav>\s*"
    r"<script type=\"application/ld\+json\" data-site-breadcrumb-ld>[\s\S]*?</script>\n?",
    re.IGNORECASE,
)
ANCHORS = [
    re.compile(r"[ \t]*<p class=\"cheatsheets-build-note[^>]*data-site-build-note", re.IGNORECASE),
    re.compile(r"[ \t]*<div class=\"related-cheatsheets[^>]*data-seo-related-links", re.IGNORECASE),
]


def build_block(sheet: dict, hub: dict, category: str) -> str:
    slug = hub["slug"]
    title = sheet["title"].strip()
    cat_label = f"{category} cheat sheets"
    ld = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Cheat sheets", "item": SITE},
            {"@type": "ListItem", "position": 2, "name": category, "item": SITE + slug},
            {"@type": "ListItem", "position": 3, "name": title},
        ],
    }
    ld_json = json.dumps(ld, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return (
        '<nav class="cs-breadcrumb" data-site-breadcrumb aria-label="Breadcrumb" '
        'style="margin:1.25rem auto 0;max-width:72ch;text-align:center;font-size:.88em;line-height:1.6;">\n'
        f'  <a href="./">Cheat sheets</a> <span aria-hidden="true">&rsaquo;</span> '
        f'<a href="{html.escape(slug)}">{html.escape(cat_label)}</a> <span aria-hidden="true">&rsaquo;</span> '
        f'<span aria-current="page">{html.escape(title)}</span>\n'
        '</nav>\n'
        f'<script type="application/ld+json" data-site-breadcrumb-ld>{ld_json}</script>\n'
    )


def place(source: str, block: str) -> str | None:
    """Insert the block at the first matching anchor; None if no anchor exists."""
    for rx in ANCHORS:
        m = rx.search(source)
        if m:
            return source[: m.start()] + block + source[m.start():]
    i = source.lower().rfind("</footer>")
    if i != -1:
        return source[:i] + block + source[i:]
    i = source.lower().rfind("</body>")
    if i != -1:
        return source[:i] + block + source[i:]
    return None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="report stale or missing breadcrumbs, change nothing")
    args = ap.parse_args()

    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    hubs = json.loads(HUBS.read_text(encoding="utf-8"))["hubs"]

    stale: list[str] = []
    written = 0
    skipped: list[str] = []
    for sheet in catalog["sheets"]:
        category = sheet.get("category", "")
        hub = hubs.get(category)
        if not hub or not hub.get("slug"):
            skipped.append(f"{sheet['file']}: category {category!r} has no hub slug")
            continue
        path = ROOT / sheet["file"]
        if not path.is_file():
            skipped.append(f"{sheet['file']}: not on disk")
            continue
        source = path.read_text(encoding="utf-8")
        block = build_block(sheet, hub, category)
        existing = BLOCK_RE.search(source)
        if existing:
            if existing.group(0).strip() == block.strip():
                continue
            updated = source[: existing.start()] + block + source[existing.end():]
        else:
            updated = place(source, block)
            if updated is None:
                skipped.append(f"{sheet['file']}: no footer/body anchor")
                continue
        stale.append(sheet["file"])
        if not args.check:
            path.write_text(updated, encoding="utf-8", newline="\n")
            written += 1

    for line in skipped:
        print("skip: " + line, file=sys.stderr)
    if args.check:
        if stale:
            print(f"{len(stale)} sheet(s) need a breadcrumb update: " + ", ".join(stale[:8])
                  + (" ..." if len(stale) > 8 else ""))
            print("fix with: python3 scripts/add_hub_breadcrumbs.py")
            return 1
        print(f"breadcrumbs current on {len(catalog['sheets']) - len(skipped)} sheets")
        return 0
    print(f"wrote {written} sheet(s); {len(catalog['sheets']) - len(skipped) - written} already current")
    return 1 if skipped else 0


if __name__ == "__main__":
    sys.exit(main())
