#!/usr/bin/env python3
"""Referral-channel report for cheatsheets.davidveksler.com from the origin nginx logs.

Cloudflare's free plan exposes no referrers and the sheets carry no GA4, so the origin
access logs are the only referrer source. logrotate keeps ~3 weeks (weekly, rotate 2).

Runs ON the server (stdlib only); pipe it over ssh:
    ssh johngalt@198.211.102.9 'python3 - --md' < scripts/referrer_report.py

Human filter (browser UAs lie, so it is heuristic): GET 200/304 on a sheet (.html), the
homepage, or a hub slug with no facet query string; drop self-declared bots, the
rel-audit crawler, and any IP with >40 page hits in a day; count one hit per IP/page/hour.
"""
import collections
import gzip
import json
import re
import sys
import urllib.parse
from datetime import datetime

LOG_DIR = "/var/log/nginx/"
FILES = ["cheatsheets.davidveksler.com.access.log.2.gz",
         "cheatsheets.davidveksler.com.access.log.1",
         "cheatsheets.davidveksler.com.access.log"]
MAX_PAGES_PER_IP_DAY = 40
LINE = re.compile(r'^(\S+) \S+ \S+ \[([^\]]+)\] (\S+) "(\S+) (\S+) [^"]*" (\d{3}) \d+ "([^"]*)" "([^"]*)"')
BOT = re.compile(r'bot|crawl|spider|slurp|curl|wget|python|headless|http-client|go-http|java/|okhttp|axios|'
                 r'node-fetch|scrapy|feed|preview|monitor|uptime|lighthouse|facebookexternalhit|embedly|'
                 r'whatsapp|telegram|discord|slack|skype|semrush|ahrefs|mj12|petal|yandex|bytespider|gptbot|'
                 r'claude|perplexity|chatgpt-user|oai-searchbot|amazonbot|applebot|ccbot|dataforseo|'
                 r'barkrowler|seznam|meta-external|zgrab|nuclei|censys|expanse|scan|rel-audit', re.I)
AI = re.compile(r'chatgpt|openai|perplexity|claude\.ai|gemini|notebook\.google|copilot|you\.com|phind|deepseek|'
                r'grok|meta\.ai|poe\.com|mistral|doubao|duck\.ai|vertexaisearch')
SEARCH = re.compile(r'(^|\.)(google\.|bing\.com|duckduckgo|yahoo\.|yandex|ecosia|brave\.com|startpage|qwant|'
                    r'baidu|naver|kagi|nortonsafesearch)|googlequicksearchbox')
SOCIAL = re.compile(r'(^|\.)(t\.co|x\.com|twitter\.com|facebook\.com|linkedin|lnkd\.in|instagram|threads\.net|'
                    r'bsky|mastodon|youtube\.com|tiktok|pinterest)|com\.linkedin\.android')
OWN = re.compile(r'davidveksler\.com|freecapitalists|walletrecovery|vellum\.capital|objectivismonline|'
                 r'coloradofirearmswatch|whopaysforai|richagent')


def channel(host, utm):
    h, u = host.lower(), utm.lower()
    if h == "cheatsheets.davidveksler.com":
        return "Internal"
    if AI.search(u) or AI.search(h):
        return "AI assistant"
    if "reddit" in u or "reddit" in h:
        return "Reddit"
    if u in ("linkedin", "facebook", "x", "twitter", "bluesky") or SOCIAL.search(h):
        return "Social"
    if re.search(r"newsletter|email|resend", u) or re.search(r"mail\.|outlook|gmail", h):
        return "Email/newsletter"
    if not h:
        return "Other site" if u else "Direct / no referrer"
    if SEARCH.search(h):
        return "Search engine"
    if re.search(r"news\.ycombinator|lobste\.rs", h):
        return "HN/Lobsters"
    if OWN.search(h):
        return "Own network"
    return "Other site"


def is_page(path):
    p, _, q = path.partition("?")
    if q and "utm_" not in q:
        return False
    return p.endswith(".html") or p == "/" or bool(re.fullmatch(r"/[a-z0-9-]+", p))


def main():
    hits, seen, per_ip_day = [], set(), collections.Counter()
    for f in FILES:
        opener = gzip.open if f.endswith(".gz") else open
        try:
            fh = opener(LOG_DIR + f, "rt", errors="replace")
        except FileNotFoundError:
            continue
        with fh:
            for line in fh:
                m = LINE.match(line)
                if not m:
                    continue
                ip, ts, _, meth, path, st, ref, ua = m.groups()
                if meth != "GET" or st not in ("200", "304") or not is_page(path):
                    continue
                if BOT.search(ua) or not re.search(r"Mozilla|Opera", ua):
                    continue
                dt = datetime.strptime(ts.split()[0], "%d/%b/%Y:%H:%M:%S")
                key = (ip, path.split("?")[0], dt.strftime("%Y%m%d%H"))
                if key in seen:
                    continue
                seen.add(key)
                per_ip_day[(ip, dt.date())] += 1
                hits.append((ip, dt, path, ref))

    total, weekly = collections.Counter(), collections.defaultdict(collections.Counter)
    hosts, landing, days = collections.Counter(), collections.defaultdict(collections.Counter), set()
    for ip, dt, path, ref in hits:
        if per_ip_day[(ip, dt.date())] > MAX_PAGES_PER_IP_DAY:
            continue
        utm = (urllib.parse.parse_qs(urllib.parse.urlsplit(path).query).get("utm_source") or [""])[0]
        host = (urllib.parse.urlsplit(ref).hostname or "") if ref not in ("-", "") else ""
        ch = channel(host, utm)
        days.add(dt.date())
        total[ch] += 1
        weekly[dt.strftime("%G-W%V")][ch] += 1
        if ch != "Internal":
            landing[ch][path.split("?")[0]] += 1
            hosts[(ch, "utm:" + utm if utm else host)] += 1

    out = {"window": [str(min(days)), str(max(days)), len(days)] if days else None,
           "total": total.most_common(),
           "weekly": {k: dict(v) for k, v in sorted(weekly.items())},
           "sources": [(c, h, n) for (c, h), n in hosts.most_common(60) if h],
           "landing": {c: v.most_common(10) for c, v in landing.items()}}
    if "--md" not in sys.argv:
        print(json.dumps(out, indent=1))
        return
    external = sum(n for c, n in total.items() if c != "Internal")
    print(f"Window {out['window'][0]} to {out['window'][1]} ({out['window'][2]} days), "
          f"{external} external landings\n\n| Channel | Landings | Share |\n|---|---|---|")
    for c, n in total.most_common():
        if c != "Internal":
            print(f"| {c} | {n} | {100 * n / external:.1f}% |")
    print("\n| Channel | Source | Landings |\n|---|---|---|")
    for c, h, n in out["sources"][:30]:
        print(f"| {c} | {h} | {n} |")
    for c, rows in out["landing"].items():
        print(f"\n{c}: " + ", ".join(f"{p} ({n})" for p, n in rows[:6]))


if __name__ == "__main__":
    main()
