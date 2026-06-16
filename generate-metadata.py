#!/usr/bin/env python3
"""Scan every cheatsheet HTML file and emit a single metadata JSON file.

This is a faithful port of the metadata extraction in ``index.php`` so the
generated JSON matches what the PHP page would produce at request time:
title, description (with ``og:description`` fallback), and an absolute
``og:image`` URL. A few extra fields useful to a JS/static consumer are
included (``keywords``, ``dateModified``); trim the SELECTED_FIELDS list
below if you want a leaner file.

Usage:
    python generate-metadata.py [--output cheatsheets.json]
                                [--base-url https://cheatsheets.davidveksler.com/]
"""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import urljoin

try:
    from bs4 import BeautifulSoup, FeatureNotFound
except ImportError:
    raise SystemExit(
        "Error: BeautifulSoup is not installed. Run: python3 -m pip install beautifulsoup4 lxml"
    )

# --- Configuration (kept in sync with index.php) ---
DEFAULT_BASE_URL = "https://cheatsheets.davidveksler.com/"

# Mirror the $excludedItems list in index.php so the two stay consistent.
EXCLUDED_FILES = {
    "index.php",
    "LICENSE",
    "README.md",
    "PROMPT.txt",
    "etz-chaim-tree-of-life.html",
}

# Fields written to the JSON, in order. Drop entries here to slim the output.
SELECTED_FIELDS = ("title", "description", "image", "url", "keywords", "dateModified")


def get_parser() -> str:
    """Prefer lxml (faster, more lenient); fall back to the stdlib parser."""
    try:
        BeautifulSoup("<html></html>", "lxml")
        return "lxml"
    except FeatureNotFound:
        return "html.parser"


HTML_PARSER = get_parser()


def humanize(filename: str) -> str:
    """Fallback title from filename, matching index.php's ucwords() behavior."""
    stem = Path(filename).stem
    return stem.replace("-", " ").replace("_", " ").title()


def meta_content(soup: BeautifulSoup, *, name: str = None, prop: str = None) -> Optional[str]:
    """Return the trimmed @content of a <meta name=...> or <meta property=...>."""
    if name is not None:
        tag = soup.find("meta", attrs={"name": name})
    else:
        tag = soup.find("meta", attrs={"property": prop})
    if tag and tag.get("content"):
        return tag["content"].strip()
    return None


def extract_date_modified(soup: BeautifulSoup) -> Optional[str]:
    """Pull dateModified (fallback datePublished) from the first JSON-LD block."""
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        if not script.string:
            continue
        try:
            data = json.loads(script.string)
        except (json.JSONDecodeError, TypeError):
            continue
        if isinstance(data, list):
            data = next((d for d in data if isinstance(d, dict)), {})
        if isinstance(data, dict):
            value = data.get("dateModified") or data.get("datePublished")
            if value:
                return str(value).strip()
    return None


def extract_metadata(path: Path, base_url: str) -> Dict[str, Optional[str]]:
    """Extract one cheatsheet's metadata, mirroring index.php's extractMetadata()."""
    filename = path.name
    url = urljoin(base_url, filename)

    meta: Dict[str, Optional[str]] = {
        "title": humanize(filename),
        "description": f"Explore this {humanize(filename)} cheatsheet for a concise overview of key concepts.",
        "image": None,
        "url": url,
        "keywords": None,
        "dateModified": None,
    }

    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), HTML_PARSER)

    if soup.title and soup.title.string:
        meta["title"] = soup.title.string.strip()

    # description: meta[name=description] -> og:description -> default
    description = meta_content(soup, name="description") or meta_content(soup, prop="og:description")
    if description:
        meta["description"] = description

    # og:image resolved to an absolute URL against the cheatsheet's own URL
    og_image = meta_content(soup, prop="og:image")
    if og_image:
        meta["image"] = urljoin(url, og_image)

    meta["keywords"] = meta_content(soup, name="keywords")
    meta["dateModified"] = extract_date_modified(soup)

    return {key: meta[key] for key in SELECTED_FIELDS}


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate cheatsheet metadata JSON.")
    parser.add_argument("--output", default="cheatsheets.json", help="Output JSON path.")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL, help="Canonical site base URL.")
    parser.add_argument("--dir", default=".", help="Directory to scan for *.html files.")
    args = parser.parse_args()

    base_url = args.base_url if args.base_url.endswith("/") else args.base_url + "/"
    root = Path(args.dir)

    sheets: List[Dict[str, Optional[str]]] = []
    for path in sorted(root.glob("*.html")):
        if path.name in EXCLUDED_FILES:
            continue
        sheets.append(extract_metadata(path, base_url))

    # Sort by title, case-insensitive, matching index.php's usort(strcasecmp).
    sheets.sort(key=lambda s: (s["title"] or "").casefold())

    payload = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "baseUrl": base_url,
        "count": len(sheets),
        "cheatsheets": sheets,
    }

    Path(args.output).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote {len(sheets)} cheatsheets to {args.output}")


if __name__ == "__main__":
    main()
