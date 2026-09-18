#!/usr/bin/env python3
"""Validate category-hubs.json against catalog.json. Exit 1 on any failure.

Run by scripts/deploy.py --check (so the pre-push hook and the deploy pipeline
both gate on it). Rules:

  - every category in catalog.json has a hub entry, and every hub entry names a
    category that exists
  - slug: lowercase [a-z0-9-], unique, and does not collide with a root file
    (a sheet called radio.html would shadow /radio in nginx's try_files)
  - title <= 60 chars, description 150-200 chars (the same gate seo_check.py
    applies to the sheets)
  - h1 and at least one intro paragraph present; no em dashes anywhere
  - start_here: 1-5 entries, each file catalogued AND filed under that category
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


def main() -> int:
    errors: list[str] = []
    try:
        hubs = json.loads((ROOT / "category-hubs.json").read_text(encoding="utf-8"))["hubs"]
        catalog = json.loads((ROOT / "catalog.json").read_text(encoding="utf-8"))
    except (OSError, ValueError, KeyError) as exc:
        print(f"check_hubs: cannot load inputs: {exc}")
        return 1

    cat_names = [c["name"] for c in catalog.get("categories", [])]
    by_file = {s["file"]: s for s in catalog.get("sheets", [])}

    for name in cat_names:
        if name not in hubs:
            errors.append(f"category {name!r} has no entry in category-hubs.json")
    seen_slugs: dict[str, str] = {}
    for name, hub in hubs.items():
        where = f"[{name}]"
        if name not in cat_names:
            errors.append(f"{where} is not a category in catalog.json")
        slug = str(hub.get("slug", ""))
        if not SLUG_RE.match(slug):
            errors.append(f"{where} slug {slug!r} must match [a-z0-9][a-z0-9-]*")
        elif slug in seen_slugs:
            errors.append(f"{where} slug {slug!r} already used by [{seen_slugs[slug]}]")
        else:
            seen_slugs[slug] = name
            if (ROOT / slug).exists():
                errors.append(f"{where} slug {slug!r} collides with a file or directory at the repo root")
        title = str(hub.get("title", ""))
        desc = str(hub.get("description", ""))
        if not title or len(title) > 60:
            errors.append(f"{where} title is {len(title)} chars (max 60)")
        if not 150 <= len(desc) <= 200:
            errors.append(f"{where} description is {len(desc)} chars (need 150-200)")
        if not str(hub.get("h1", "")).strip():
            errors.append(f"{where} h1 missing")
        intro = hub.get("intro")
        if not isinstance(intro, list) or not any(isinstance(p, str) and p.strip() for p in intro):
            errors.append(f"{where} intro needs at least one paragraph")
        text = " ".join([title, desc, str(hub.get("h1", ""))] + [p for p in (intro or []) if isinstance(p, str)])
        if "—" in text:
            errors.append(f"{where} contains an em dash")
        start = hub.get("start_here")
        if not isinstance(start, list) or not 1 <= len(start) <= 5:
            errors.append(f"{where} start_here needs 1-5 entries")
        else:
            for entry in start:
                f = str(entry.get("file", "")) if isinstance(entry, dict) else ""
                if f not in by_file:
                    errors.append(f"{where} start_here {f!r} is not in catalog.json")
                elif by_file[f].get("category") != name:
                    errors.append(f"{where} start_here {f!r} is filed under {by_file[f].get('category')!r}")
                if isinstance(entry, dict) and "—" in str(entry.get("why", "")):
                    errors.append(f"{where} start_here {f!r} why contains an em dash")

    if errors:
        for e in errors:
            print("check_hubs: " + e)
        return 1
    print(f"check_hubs: {len(hubs)} hubs valid ({', '.join(sorted(seen_slugs))})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
