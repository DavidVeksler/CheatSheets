"""The 2026-09-28 .php URL retirement, for the parity gates.

The public URLs dropped .php: /index.php -> / (or the hub slug for ?category=),
/popularity.php -> /popularity, /sitemap.php -> /sitemap.xml, /subscribe.php ->
/subscribe, /confirm.php -> /confirm. Production served the old spellings until the
first deploy after the rename, so parity_body_recheck.py and compare_explorer.py map
production's links onto the new ones before comparing. Once that deploy is live the
mapping matches nothing and is a no-op. Stdlib only.
"""
from __future__ import annotations

import json
import re
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Old path -> the path the site Worker 301s it to (query kept).
REDIRECTS = {"/index.php": "/", "/popularity.php": "/popularity", "/sitemap.php": "/sitemap.xml",
             "/confirm.php": "/confirm"}
# New URLs that must answer 200 (the forms endpoints need a POST or a token, so not here).
CLEAN_PAGES = ["/popularity", "/sitemap.xml"]

_ATTR = re.compile(r'\b(href|action|content)="((?:https://cheatsheets\.davidveksler\.com)?/?)'
                   r'(index|popularity|sitemap|subscribe)\.php((?:\?[^"]*)?)"')
_SITEMAP_LINE = re.compile(r"(?m)^(-? ?Sitemap: https://cheatsheets\.davidveksler\.com/)sitemap\.php$")


def _slugs() -> dict[str, str]:
    hubs = json.loads((ROOT / "category-hubs.json").read_text(encoding="utf-8"))["hubs"]
    return {k: v["slug"] for k, v in hubs.items() if isinstance(v, dict) and v.get("slug")}


def rename_links(text: str) -> str:
    """Rewrite old .php links in an HTML or text body to the URLs the rename produced."""
    slugs = _slugs()

    def sub(m: re.Match) -> str:
        attr, prefix, page, query = m.groups()
        if page == "index":
            cat = urllib.parse.parse_qs(query[1:].replace("&amp;", "&")).get("category", [""])[0]
            if cat in slugs:
                return f'{attr}="/{slugs[cat]}"'
            return f'{attr}="{prefix or "/"}{query}"' if prefix else f'{attr}="/{query}"'
        new = {"popularity": "popularity", "sitemap": "sitemap.xml", "subscribe": "subscribe"}[page]
        return f'{attr}="{prefix}{new}{query}"'

    return _SITEMAP_LINE.sub(r"\1sitemap.xml", _ATTR.sub(sub, text))
