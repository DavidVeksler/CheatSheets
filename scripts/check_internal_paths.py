#!/usr/bin/env python3
"""Verify conf/nginx/internal-paths.conf is live: internals 404, public files 200.

Usage:
    python3 scripts/check_internal_paths.py                       # live site
    python3 scripts/check_internal_paths.py --base http://localhost:8089

Exit 0 when every URL returns its expected status, 1 otherwise. Stdlib only.
Keep the two lists in step with the drop-in's comments.
"""
import argparse
import sys
import urllib.error
import urllib.request

MUST_BLOCK = [
    "/marketing/reddit-drafts/2026-07-19.md",
    "/marketing/reddit-subreddit-map.json",
    "/docs/marketing.md",
    "/TODO/TODO.md",
    "/scripts/deploy.py",
    "/scripts/rainbow/data.json",
    "/deploy/DEPLOY.md",
    "/conf/nginx/redirects.conf",
    "/lib/env.php",
    "/AGENTS.md",
    "/weekly-freshness-update.md",
    "/seo_updater.py",
    "/deploy.ps1",
    "/SEO_PROMPT.txt",
    "/requirements.txt",
    "/check-category-map.php",
    "/.metadata-cache.json",
    "/.git/HEAD",
]

MUST_SERVE = [
    "/",
    "/llms.txt",
    "/llms-full.txt",
    "/catalog.json",
    "/robots.txt",
    "/sitemap.php",
    "/git-scm.html",
    "/housing-comparison-data.json",
    "/art-of-war-sun-tzu-english.json",
    "/docs/how-do-rainbows-work-production.md",
    "/scripts/grass_green/build_spectra.py",
    "/radio",
]

# README.md, *.sh and the like already get a 403 from WordOps; either status blocks.
BLOCKED = {403, 404}


def status(url):
    req = urllib.request.Request(url, method="GET", headers={"User-Agent": "cheatsheets-internal-paths-check"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return resp.status
    except urllib.error.HTTPError as err:
        return err.code


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--base", default="https://cheatsheets.davidveksler.com")
    base = ap.parse_args().base.rstrip("/")

    failures = 0
    for path in MUST_BLOCK:
        code = status(base + path)
        ok = code in BLOCKED
        failures += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {code} {path}  (want 404)")
    for path in MUST_SERVE:
        code = status(base + path)
        ok = code == 200
        failures += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {code} {path}  (want 200)")

    print(f"\n{failures} failure(s)" if failures else "\nall checks passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
