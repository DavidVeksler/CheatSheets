#!/usr/bin/env python3
"""Query Google Search Console Search Analytics directly, with local aggregation.

Why this exists: the `search-console` MCP tool returns rows sorted by clicks and
dumps them straight into an agent's context, which makes the interesting analyses
(zero-click high-impression queries, query families, page x query gaps) impractical.
This script talks to the API itself, keeps the raw rows on disk, and prints only
the aggregate you asked for.

Auth: the same service-account JSON the MCP server uses
(C:\\Users\\veksl\\.claude\\mcp-servers\\gsc-service-account.json), overridable via
GOOGLE_SERVICE_ACCOUNT_FILE. Only `cryptography` and `requests` are required.

Examples
--------
  # top queries by impressions (not clicks), last 28 days
  python scripts/gsc_query.py --days 28 --dim query --sort impressions --top 60

  # queries with impressions but no clicks, position 5-30 (opportunity pool)
  python scripts/gsc_query.py --days 28 --dim query --zero-click --min-impr 50

  # page x query for one page
  python scripts/gsc_query.py --days 28 --dim page query --page baofeng-uv5r-quick-ref.html

  # dump raw rows to JSON for further analysis
  python scripts/gsc_query.py --days 90 --dim query --json out.json
"""
from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
import sys
import time

import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

SITE = "https://cheatsheets.davidveksler.com/"
DEFAULT_KEY = r"C:\Users\veksl\.claude\mcp-servers\gsc-service-account.json"
SCOPE = "https://www.googleapis.com/auth/webmasters.readonly"
TOKEN_URL = "https://oauth2.googleapis.com/token"


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def access_token(key_file: str) -> str:
    with open(key_file, encoding="utf-8") as fh:
        sa = json.load(fh)
    now = int(time.time())
    header = _b64(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
    claims = _b64(
        json.dumps(
            {
                "iss": sa["client_email"],
                "scope": SCOPE,
                "aud": TOKEN_URL,
                "iat": now,
                "exp": now + 3600,
            }
        ).encode()
    )
    signing_input = f"{header}.{claims}".encode()
    key = serialization.load_pem_private_key(sa["private_key"].encode(), password=None)
    signature = key.sign(signing_input, padding.PKCS1v15(), hashes.SHA256())
    assertion = f"{header}.{claims}.{_b64(signature)}"
    resp = requests.post(
        TOKEN_URL,
        data={
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": assertion,
        },
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["access_token"]


def fetch(token: str, site: str, start: str, end: str, dims: list[str],
          row_limit: int, filters: list[dict] | None) -> list[dict]:
    url = (
        "https://www.googleapis.com/webmasters/v3/sites/"
        + requests.utils.quote(site, safe="")
        + "/searchAnalytics/query"
    )
    rows: list[dict] = []
    start_row = 0
    while True:
        body = {
            "startDate": start,
            "endDate": end,
            "dimensions": dims,
            "rowLimit": min(25000, row_limit - len(rows)),
            "startRow": start_row,
        }
        if filters:
            body["dimensionFilterGroups"] = [{"filters": filters}]
        resp = requests.post(
            url, json=body, headers={"Authorization": f"Bearer {token}"}, timeout=60
        )
        resp.raise_for_status()
        batch = resp.json().get("rows", [])
        rows.extend(batch)
        if len(batch) < body["rowLimit"] or len(rows) >= row_limit:
            break
        start_row += len(batch)
    return rows


def main() -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--site", default=SITE)
    ap.add_argument("--days", type=int, default=28,
                    help="window length, ending --end (default 28)")
    ap.add_argument("--end", default=None,
                    help="end date YYYY-MM-DD (default: 3 days ago, GSC lag)")
    ap.add_argument("--start", default=None, help="explicit start date, overrides --days")
    ap.add_argument("--dim", nargs="+", default=["query"],
                    choices=["query", "page", "date", "country", "device"])
    ap.add_argument("--page", default=None, help="substring filter on page URL")
    ap.add_argument("--query-contains", default=None, help="substring filter on query")
    ap.add_argument("--row-limit", type=int, default=25000)
    ap.add_argument("--sort", default="clicks",
                    choices=["clicks", "impressions", "ctr", "position"])
    ap.add_argument("--top", type=int, default=50)
    ap.add_argument("--min-impr", type=int, default=0)
    ap.add_argument("--zero-click", action="store_true",
                    help="only rows with 0 clicks (unclaimed demand)")
    ap.add_argument("--max-position", type=float, default=None)
    ap.add_argument("--json", default=None, help="write all fetched rows here")
    args = ap.parse_args()

    end = args.end or (dt.date.today() - dt.timedelta(days=3)).isoformat()
    start = args.start or (
        dt.date.fromisoformat(end) - dt.timedelta(days=args.days - 1)
    ).isoformat()

    filters = []
    if args.page:
        filters.append({"dimension": "page", "operator": "contains", "expression": args.page})
    if args.query_contains:
        filters.append({"dimension": "query", "operator": "contains",
                        "expression": args.query_contains})

    token = access_token(os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE", DEFAULT_KEY))
    rows = fetch(token, args.site, start, end, args.dim, args.row_limit, filters or None)

    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump({"start": start, "end": end, "dims": args.dim, "rows": rows}, fh)

    sel = rows
    if args.zero_click:
        sel = [r for r in sel if r["clicks"] == 0]
    if args.min_impr:
        sel = [r for r in sel if r["impressions"] >= args.min_impr]
    if args.max_position is not None:
        sel = [r for r in sel if r["position"] <= args.max_position]
    reverse = args.sort != "position"
    sel.sort(key=lambda r: r[args.sort], reverse=reverse)

    print(f"# {args.site}  {start} -> {end}  dims={'+'.join(args.dim)}")
    print(f"# fetched {len(rows)} rows, showing {min(args.top, len(sel))} of {len(sel)} "
          f"after filters, sorted by {args.sort}")
    tot_c = sum(r["clicks"] for r in rows)
    tot_i = sum(r["impressions"] for r in rows)
    print(f"# totals: {tot_c} clicks / {tot_i} impressions")
    for r in sel[: args.top]:
        keys = " | ".join(k.replace("https://cheatsheets.davidveksler.com/", "") for k in r["keys"])
        print(f"{r['clicks']:>5} {r['impressions']:>7} {r['ctr']*100:>6.2f}% "
              f"{r['position']:>6.1f}  {keys}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
