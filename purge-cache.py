#!/usr/bin/env python3
"""
Purge Cloudflare's edge cache for cheatsheet HTML files that changed between
two git revisions. Called from .git/hooks/post-receive on every deploy to
main, so cached pages don't serve stale content until their max-age(1800s)
Cache-Control (see conf/nginx/cache-control.conf on the server) expires.

Required env vars (loaded from .cloudflare.env if present, see .gitignore):
  CLOUDFLARE_API_TOKEN  – Bearer token with Zone Cache Purge:Purge permission
  CLOUDFLARE_ZONE_ID    – Zone ID (optional; auto-detected from first zone if absent)

Usage:
  python3 purge-cache.py <oldrev> <newrev>

Only *.html files are purged — the nginx Cache-Control rule and the
Cloudflare Cache Rule both scope to .html, so nothing else is edge-cached.
Deleted/renamed files are purged too (in case a stale copy is still cached
under the old URL). Exits 0 even on failure — a purge problem shouldn't be
treated as a failed deploy, since the git update already succeeded.
"""
import json
import os
import subprocess
import sys
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(REPO_DIR, ".cloudflare.env")
CLOUDFLARE_REST = "https://api.cloudflare.com/client/v4"
SITE_ORIGIN = "https://cheatsheets.davidveksler.com"
EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"  # git's empty-tree hash
BATCH_SIZE = 30  # Cloudflare purge_cache accepts up to 30 URLs per call


def load_env_file(path: str) -> None:
    """Populate os.environ from a simple KEY=VALUE file, without overriding vars already set."""
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ.setdefault(key, value)


def cf_request(token: str, method: str, path: str, body: dict = None) -> dict:
    data = json.dumps(body).encode() if body is not None else None
    req = Request(
        f"{CLOUDFLARE_REST}{path}",
        data=data,
        method=method,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    with urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def get_zone_id(token: str) -> str:
    zone_id = os.environ.get("CLOUDFLARE_ZONE_ID")
    if zone_id:
        return zone_id
    data = cf_request(token, "GET", "/zones?per_page=50")
    zones = data.get("result") or []
    if not zones:
        raise RuntimeError("No zones visible to this Cloudflare token — set CLOUDFLARE_ZONE_ID explicitly.")
    return zones[0]["id"]


def changed_html_files(oldrev: str, newrev: str) -> list[str]:
    if oldrev.strip("0") == "":
        oldrev = EMPTY_TREE
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=ACMRD", oldrev, newrev, "--", "*.html"],
        cwd=REPO_DIR, capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git diff failed:\n{result.stdout}{result.stderr}")
    return [line for line in result.stdout.splitlines() if line]


def purge_urls(token: str, zone_id: str, urls: list[str]) -> None:
    for i in range(0, len(urls), BATCH_SIZE):
        batch = urls[i : i + BATCH_SIZE]
        resp = cf_request(token, "POST", f"/zones/{zone_id}/purge_cache", {"files": batch})
        if not resp.get("success"):
            raise RuntimeError(f"Purge failed for {batch}: {resp.get('errors')}")
        print(f"Purged {len(batch)} URL(s): {', '.join(batch)}")


def main() -> None:
    if len(sys.argv) != 3:
        print("Usage: purge-cache.py <oldrev> <newrev>", file=sys.stderr)
        sys.exit(1)
    oldrev, newrev = sys.argv[1], sys.argv[2]

    load_env_file(ENV_FILE)
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if not token:
        print(f"ERROR: CLOUDFLARE_API_TOKEN not set (checked {ENV_FILE}) — skipping purge.", file=sys.stderr)
        sys.exit(1)

    files = changed_html_files(oldrev, newrev)
    if not files:
        print("No .html files changed — nothing to purge.")
        return

    urls = [f"{SITE_ORIGIN}/{path}" for path in files]
    zone_id = get_zone_id(token)
    purge_urls(token, zone_id, urls)


if __name__ == "__main__":
    try:
        main()
    except (URLError, HTTPError, RuntimeError) as e:
        print(f"ERROR: cache purge failed: {e}", file=sys.stderr)
        sys.exit(1)
