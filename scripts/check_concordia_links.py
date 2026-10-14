#!/usr/bin/env python3
"""Link-check every concordia.davidveksler.com URL on the CheatSheets pages that cross-promote Concordia.

Concordia is under active development, so deep-link ids rot in months. This checks each outbound link against
the Habitat repo's generated `site/data/sim-index.json` (viewpoints, chapters, overlays, glossary) and its
`site/content/` pages, and that the outbound UTM shape is intact. See docs/concordia-crosspromo.md.

    python3 scripts/check_concordia_links.py                # check every sheet that links to Concordia
    python3 scripts/check_concordia_links.py page.html      # one sheet
    python3 scripts/check_concordia_links.py --live         # also HEAD every page path on the live site

The Habitat repo is read from $HABITAT_REPO, default ~/Projects/Habitat. Exits 1 on any failure.
"""
from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
import urllib.request
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parent.parent
HABITAT = Path(os.environ.get("HABITAT_REPO", Path.home() / "Projects" / "Habitat"))
HOST = "concordia.davidveksler.com"
LINK_RE = re.compile(r'href="(https://' + re.escape(HOST) + r'[^"]*)"')
UTM = {"utm_source": "cheatsheets", "utm_medium": "referral", "utm_campaign": "concordia_crosspromo"}
MODES = {"story", "explore", "engineer"}


def load_index() -> dict:
    p = HABITAT / "site" / "data" / "sim-index.json"
    if not p.is_file():
        sys.exit(f"missing {p}: set HABITAT_REPO to a Habitat checkout")
    return json.loads(p.read_text(encoding="utf-8"))


def check_url(url: str, index: dict) -> list[str]:
    errs: list[str] = []
    u = urlsplit(html.unescape(url))
    q = parse_qs(u.query)
    for k, v in UTM.items():
        if q.get(k) != [v]:
            errs.append(f"{k} is not {v!r}")
    if not q.get("utm_content"):
        errs.append("utm_content missing")
    path = u.path or "/"
    if path == "/explore/":
        vps = {v["id"] for v in index["viewpoints"]}
        chs = {c["key"] for c in index["chapters"]}
        ovs = {o["slug"] for o in index["overlays"]}
        if "viewpoint" in q and q["viewpoint"][0] not in vps:
            errs.append(f"unknown viewpoint {q['viewpoint'][0]}")
        if "chapter" in q and q["chapter"][0] not in chs:
            errs.append(f"unknown chapter {q['chapter'][0]}")
        if "overlay" in q and q["overlay"][0] not in ovs:
            errs.append(f"unknown overlay {q['overlay'][0]}")
        if "mode" in q and q["mode"][0] not in MODES:
            errs.append(f"unknown mode {q['mode'][0]}")
    elif path == "/glossary/":
        slugs = {g["slug"] for g in index["glossaryTerms"]}
        if u.fragment and u.fragment not in slugs:
            errs.append(f"unknown glossary term #{u.fragment}")
    elif path != "/":
        m = re.fullmatch(r"/(science|discover|places|station)/([a-z0-9-]+)/", path)
        if not m or not (HABITAT / "site" / "content" / m.group(1) / f"{m.group(2)}.md").is_file():
            errs.append(f"no content page for {path}")
    return errs


def live_ok(url: str) -> str | None:
    u = urlsplit(html.unescape(url))
    target = f"https://{HOST}{u.path or '/'}"
    try:
        req = urllib.request.Request(target, method="HEAD", headers={"User-Agent": "cheatsheets-link-check"})
        with urllib.request.urlopen(req, timeout=20) as r:
            return None if r.status == 200 else f"HTTP {r.status}"
    except Exception as e:  # noqa: BLE001
        return str(e)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="*")
    ap.add_argument("--live", action="store_true")
    a = ap.parse_args()
    files = [ROOT / f for f in a.files] if a.files else sorted(
        p for p in ROOT.glob("*.html") if HOST in p.read_text(encoding="utf-8", errors="replace"))
    index = load_index()
    bad = total = 0
    seen_live: dict[str, str | None] = {}
    for f in files:
        text = f.read_text(encoding="utf-8")
        urls = LINK_RE.findall(text)
        for url in urls:
            total += 1
            errs = check_url(url, index)
            if a.live:
                path = urlsplit(html.unescape(url)).path
                if path not in seen_live:
                    seen_live[path] = live_ok(url)
                if seen_live[path]:
                    errs.append("live: " + seen_live[path])
            if errs:
                bad += 1
                print(f"FAIL {f.name}: {html.unescape(url)}\n     " + "; ".join(errs))
    print(f"{total} Concordia links in {len(files)} file(s), {bad} failing")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
