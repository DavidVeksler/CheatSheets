#!/usr/bin/env python3
"""Strict re-check of the differences deploy/parity-allow.txt waves through.

cf_parity.py (cf-static-kit) compares production (droplet behind the zone) with a
workers.dev preview (outside the zone). The allow file lets some differences through
on named paths; every one whose reason names this script is proven here to be only
the stated effect, or the deploy fails (spec §5):

- sheets (.html): the zone's Cloudflare Fonts feature swaps Google Fonts <link>s for
  an inline /cf-fonts/ @font-face <style> on the droplet side (it keeps doing so after
  cutover). cf_parity's normalizer misses the self-closing `<link ... />` form used
  by many sheets (kit bug, reported). Also three sheets link history.php, now GitHub.
- /catalog.json: rebuilt on the branch; same sheets, only the build stamp, inputs
  hash, map layout floats and the edited sheets' dates may differ.
- binary assets (/images/...): the zone's edge cache serves a stale copy (10-year
  max-age, only HTML was ever purged); the candidate must equal the droplet origin
  itself, fetched directly (pinned to the droplet IP).
- /history.php URLs: 301 to exactly the GitHub page for the same view.

    python3 scripts/parity_body_recheck.py .wrangler/parity-<sha>.json [--base origin/main]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
from pathlib import Path

KIT = os.environ.get("CF_KIT", os.path.join(os.path.expanduser("~"), "Projects", "cf-static-kit"))
sys.path.insert(0, os.path.join(KIT, "scripts"))
import cf_parity as P  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DROPLET_IP = os.environ.get("CS_DROPLET_IP", "198.211.102.9")
HOST = "cheatsheets.davidveksler.com"
GH = "https://github.com/DavidVeksler/CheatSheets"

CF_FONTS = re.compile(r'<style type="text/css">@font-face \{[^<]*?/cf-fonts/[^<]*</style>')
GOOGLE_FONTS = re.compile(r'<link\b[^>]*\bhref="https://fonts\.(?:googleapis|gstatic)\.com[^"]*"[^>]*>')
HISTORY_HREF = ('href="history.php"', f'href="{GH}/commits/main/"')
HISTORY = {
    "/history.php": f"{GH}/commits/main/",
    "/history.php?page=2": f"{GH}/commits/main/",
    "/history.php?q=judo": f"{GH}/commits/main/",
    "/history.php?file=judo.html": f"{GH}/commits/main/judo.html",
    "/history.php?file=scripts/build_catalog.py": f"{GH}/commits/main/scripts/build_catalog.py",
    "/history.php?commit=455f434": f"{GH}/commit/455f434",
}


def origin_fetch(path: str) -> bytes:
    r = subprocess.run(["curl", "-sk", "--max-time", "30", "--resolve", f"{HOST}:443:{DROPLET_IP}",
                        f"https://{HOST}{path}"], capture_output=True)
    return r.stdout if r.returncode == 0 else b""


def changed_sheets(base: str) -> set[str]:
    r = subprocess.run(["git", "diff", "--name-only", f"{base}..HEAD", "--", "*.html"], cwd=ROOT,
                       capture_output=True, text=True)
    return {p for p in r.stdout.split() if "/" not in p}


def html_explained(prod: dict, cand: dict) -> bool:
    pt = prod["body"].decode("utf-8", "replace")
    ct = cand["body"].decode("utf-8", "replace")
    pt = CF_FONTS.sub("", pt).replace(*HISTORY_HREF)
    ct = GOOGLE_FONTS.sub("", ct)
    pt = GOOGLE_FONTS.sub("", pt)  # preconnect links the zone leaves in place
    return P.norm_body(pt.encode(), "text/html") == P.norm_body(ct.encode(), "text/html")


def catalog_explained(prod: dict, cand: dict, changed: set[str]) -> bool:
    try:
        a, b = json.loads(prod["body"]), json.loads(cand["body"])
    except ValueError:
        return False
    for d in (a, b):
        d.pop("generated", None)
        d.pop("inputs_hash", None)
        for s in d.get("sheets", []):
            # The map layout (x, y) is a force simulation whose floats vary with the
            # machine and Python that ran build_catalog.py; it moves every rebuild.
            s.pop("x", None)
            s.pop("y", None)
            if s.get("file") in changed:
                s.pop("updated", None)
    return a == b


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("report")
    ap.add_argument("--base", default="origin/main")
    a = ap.parse_args()
    rep = json.load(open(a.report, encoding="utf-8"))
    changed = changed_sheets(a.base)
    paths = sorted({x[0] for x in rep["allowed"] if x[1] in ("body", "*") and "parity_body_recheck" in x[2]})
    bad, ok = [], 0
    for path in paths:
        prod, cand = P.fetch(rep["prod"] + path), P.fetch(rep["candidate"] + path)
        if prod["status"] != 200 or cand["status"] != 200:
            bad.append((path, f"status {prod['status']}/{cand['status']}"))
            continue
        ctype = prod["headers"].get("content-type", "").split(";")[0].strip()
        if path == "/catalog.json":
            good = catalog_explained(prod, cand, changed)
        elif ctype == "text/html":
            good = html_explained(prod, cand)
        else:
            origin = origin_fetch(path)
            good = bool(origin) and hashlib.sha256(origin).digest() == hashlib.sha256(cand["body"]).digest()
        if good:
            ok += 1
        else:
            bad.append((path, "body not explained"))
    for path, target in HISTORY.items():
        c = P.fetch(rep["candidate"] + path)
        if c["status"] != 301 or c["headers"].get("location") != target:
            bad.append((path, f"expected 301 {target}, got {c['status']} {c['headers'].get('location')}"))
        else:
            ok += 1
    for path, why in bad:
        print(f"  NOT EXPLAINED {path}: {why}")
    print(f"parity_body_recheck: {ok} allowed differences proven, {len(bad)} not explained")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
