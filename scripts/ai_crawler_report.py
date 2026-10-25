#!/usr/bin/env python3
"""AI-agent requests to cheatsheets.davidveksler.com over the last 7 full UTC days.

Cloudflare GraphQL (httpRequestsAdaptiveGroups, host-filtered), grouped by user agent
and bucketed by the AI crawler/agent name in the UA string. The free plan keeps ~8 days,
so compare 7-day windows run with this same script; log results in docs/seo-progress.md.

Token: CLOUDFLARE_API_TOKEN in ~/Projects/.cloudflare.env (never printed).

  python scripts/ai_crawler_report.py            # last 7 full days
  python scripts/ai_crawler_report.py --end 2026-10-24
"""
from __future__ import annotations

import argparse
import json
import re
import urllib.request
from datetime import date, timedelta
from pathlib import Path

ZONE = "3d96473d69977c5c828b3079d9b9869c"  # davidveksler.com
HOST = "cheatsheets.davidveksler.com"
AI = re.compile(
    r"GPTBot|ChatGPT-User|OAI-SearchBot|ClaudeBot|Claude-User|Claude-SearchBot|anthropic|"
    r"PerplexityBot|Perplexity-User|Google-Extended|Bytespider|Amazonbot|meta-externalagent|"
    r"CCBot|Applebot|DuckAssist|cohere|MistralAI|YouBot|Gemini",
    re.I,
)


def token() -> str:
    env = (Path.home() / "Projects" / ".cloudflare.env").read_text(encoding="utf-8")
    return re.search(r"CLOUDFLARE_API_TOKEN=(\S+)", env).group(1)


def day_groups(tok: str, day: str) -> list[dict]:
    query = """{ viewer { zones(filter:{zoneTag:"%s"}) { httpRequestsAdaptiveGroups(
      filter:{datetime_geq:"%sT00:00:00Z", datetime_leq:"%sT23:59:59Z", clientRequestHTTPHost:"%s"},
      limit:5000, orderBy:[count_DESC]) { count dimensions { userAgent } } } } }""" % (ZONE, day, day, HOST)
    req = urllib.request.Request(
        "https://api.cloudflare.com/client/v4/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": f"Bearer {tok}", "Content-Type": "application/json"},
        method="POST",
    )
    body = json.load(urllib.request.urlopen(req, timeout=60))
    if body.get("errors"):
        raise SystemExit(f"Cloudflare error: {body['errors'][0]['message']}")
    return body["data"]["viewer"]["zones"][0]["httpRequestsAdaptiveGroups"]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--end", default=(date.today() - timedelta(days=1)).isoformat())
    a = ap.parse_args()
    tok, end = token(), date.fromisoformat(a.end)
    buckets: dict[str, int] = {}
    total = 0
    for i in range(7):
        for g in day_groups(tok, (end - timedelta(days=i)).isoformat()):
            total += g["count"]
            m = AI.search(g["dimensions"]["userAgent"] or "")
            if m:
                k = m.group(0).lower()
                buckets[k] = buckets.get(k, 0) + g["count"]
    print(f"{HOST} {(end - timedelta(days=6)).isoformat()} -> {end.isoformat()}")
    print(f"all requests (top 5,000 UA groups/day): {total:,}")
    print(f"AI-agent requests: {sum(buckets.values()):,}")
    for k, v in sorted(buckets.items(), key=lambda x: -x[1]):
        print(f"  {k:20} {v:6,}")


if __name__ == "__main__":
    main()
