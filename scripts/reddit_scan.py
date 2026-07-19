#!/usr/bin/env python3
"""Reddit opportunity scanner for the cheatsheets-reddit-daily-drafts routine.

READ-ONLY. This script never posts, votes, comments, or writes to Reddit.

Two modes:

  --print-urls  (PRIMARY, no network, no credentials)
      Build the browser navigation plan from the map + rotation state: the old.reddit
      search URL for each eligible subreddit, its cheatsheets, caution level, and whether
      it is due for an original post. The routine drives David's logged-in Chrome through
      these URLs and extracts candidates with scripts/reddit-extract.js. This is the
      supported path because Reddit blocks unauthenticated JSON (403) AND is not currently
      issuing "script" OAuth apps.

  (default)     OAuth scan  -- CURRENTLY UNAVAILABLE: kept for if/when Reddit re-enables
      "script" apps. Uses a read-only token to query search server-side and write a
      candidates file. Credentials load from env vars or ~/Projects/.reddit.env (same
      central-env pattern as .cloudflare.env; never commit them). Setup, when it works:
        1. https://www.reddit.com/prefs/apps -> "create another app" -> type "script".
        2. Note the client id (under the app name) and the secret.
        3. Put REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET / REDDIT_USERNAME /
           REDDIT_PASSWORD in ~/Projects/.reddit.env.

Exit codes: 0 ok, 2 bad map, 3 missing/invalid credentials (use --print-urls + browser
discovery per docs/reddit-daily-drafts.md), 4 network/API failure.

Binding spec: docs/reddit-daily-drafts.md. Map: marketing/reddit-subreddit-map.json.
Extractor: scripts/reddit-extract.js.

Usage:
    python scripts/reddit_scan.py --print-urls        # browser navigation plan (primary)
    python scripts/reddit_scan.py --print-urls --days 3
    python scripts/reddit_scan.py                      # OAuth scan (needs script app)
    python scripts/reddit_scan.py --limit-subs 5 --dry-run
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DEFAULT_MAP = REPO / "marketing" / "reddit-subreddit-map.json"
DRAFTS_DIR = REPO / "marketing" / "reddit-drafts"
ROTATION_FILE = DRAFTS_DIR / ".rotation.json"
ENV_FILE = Path.home() / "Projects" / ".reddit.env"
SITE = "https://cheatsheets.davidveksler.com/"
UTM = "utm_source=reddit&utm_medium=social&utm_campaign=agentic_cheatsheets_2026&utm_content="

# A unique, honest UA per Reddit API rules: <platform>:<app id>:<version> (by /u/<user>)
USER_AGENT = "python:cheatsheets-reddit-scan:1.0 (read-only opportunity finder)"

QUESTION_WORDS = ("how", "what", "which", "why", "where", "when", "who", "should i",
                  "help", "recommend", "beginner", "vs", "compare", "best")
SKIP_TITLE_MARKERS = ("[meta]", "megathread", "daily thread", "weekly thread",
                      "for sale", "wts", "wtb", "giveaway")


def load_credentials() -> dict | None:
    creds = {k: os.environ.get(k) for k in
             ("REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "REDDIT_USERNAME", "REDDIT_PASSWORD")}
    if not all(creds.values()) and ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if k in creds and not creds[k]:
                creds[k] = v
    return creds if all(creds.values()) else None


def get_token(creds: dict) -> str | None:
    auth = base64.b64encode(
        f"{creds['REDDIT_CLIENT_ID']}:{creds['REDDIT_CLIENT_SECRET']}".encode()).decode()
    body = urllib.parse.urlencode({
        "grant_type": "password",
        "username": creds["REDDIT_USERNAME"],
        "password": creds["REDDIT_PASSWORD"],
        "scope": "read",
    }).encode()
    req = urllib.request.Request(
        "https://www.reddit.com/api/v1/access_token", data=body,
        headers={"Authorization": f"Basic {auth}", "User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode("utf-8")).get("access_token")
    except urllib.error.HTTPError as e:
        print(f"Token request failed: HTTP {e.code} {e.read().decode('utf-8', 'ignore')[:200]}",
              file=sys.stderr)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
        print(f"Token request failed: {e}", file=sys.stderr)
    return None


def http_get_json(url: str, token: str, retries: int = 3) -> dict | None:
    req = urllib.request.Request(
        url, headers={"Authorization": f"bearer {token}", "User-Agent": USER_AGENT})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 5 * (attempt + 1)
                print(f"  429 rate-limited, backing off {wait}s", file=sys.stderr)
                time.sleep(wait)
                continue
            print(f"  HTTP {e.code} for {url}", file=sys.stderr)
            return None
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            print(f"  request failed ({e}); retry {attempt + 1}/{retries}", file=sys.stderr)
            time.sleep(2 * (attempt + 1))
    return None


def build_query(terms: list[str], max_terms: int = 6) -> str:
    picked = [t for t in terms[:max_terms] if t]
    quoted = [f'"{t}"' if " " in t else t for t in picked]
    return "(" + " OR ".join(quoted) + ")"


def build_search_url(sub: str, terms: list[str], days: int) -> str:
    """old.reddit HTML search URL the routine navigates to in the browser."""
    t_window = "week" if days <= 7 else "month"
    qs = urllib.parse.urlencode({"q": build_query(terms), "restrict_sr": "1",
                                 "sort": "new", "t": t_window})
    return f"https://old.reddit.com/r/{urllib.parse.quote(sub)}/search/?{qs}"


def print_urls(cfg: dict, subs: list[dict], rotation: dict, now: float, days: int) -> int:
    """Emit the browser navigation plan as JSON. No network, no credentials."""
    utm = "utm_source=reddit&utm_medium=social&utm_campaign=agentic_cheatsheets_2026&utm_content="
    plan = []
    for entry in subs:
        sheets = entry.get("cheatsheets", [])
        slug = sheets[0].replace(".html", "").replace("_", "-") if sheets else entry["subreddit"].lower()
        plan.append({
            "subreddit": entry["subreddit"],
            "audience": entry.get("audience", ""),
            "caution": entry.get("caution", "normal"),
            "discover": entry.get("caution") != "skip-unless-asked",
            "post_eligible": eligible_for_post(entry, rotation, now),
            "search_url": build_search_url(entry["subreddit"], entry.get("search_terms", []), days),
            "cheatsheets": [SITE + s + "?" + utm + slug for s in sheets],
            "cheatsheet_files": sheets,
            "notes": entry.get("notes", ""),
        })
    out = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "days_window": days,
        "method": "browser",
        "extractor": "scripts/reddit-extract.js",
        "count": len(plan),
        "plan": plan,
        "note": "Navigate David's logged-in Chrome to each search_url where discover=true, "
                "inject reddit-extract.js, then judge/draft per docs/reddit-daily-drafts.md. "
                "skip-unless-asked subs (discover=false) are listed for reference only.",
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


def score_thread(post: dict, terms: list[str], now: float) -> tuple[int, list[str]]:
    title = (post.get("title") or "").lower()
    body = (post.get("selftext") or "").lower()
    hay = title + " " + body
    matched = sorted({t for t in terms if t and t.lower() in hay})
    score = len(matched) * 10
    if any(q in title for q in QUESTION_WORDS) or title.rstrip().endswith("?"):
        score += 15
    age_h = max(0.0, (now - post.get("created_utc", now)) / 3600.0)
    if age_h < 24:
        score += 12
    elif age_h < 72:
        score += 6
    nc = post.get("num_comments", 0)
    if nc < 5:
        score += 8
    elif nc < 20:
        score += 3
    if post.get("is_self"):
        score += 4
    return score, matched


def scan_subreddit(entry: dict, token: str, days: int, now: float) -> list[dict]:
    sub = entry["subreddit"]
    terms = entry.get("search_terms", [])
    if not terms:
        return []
    q = build_query(terms)
    t_window = "week" if days <= 7 else "month"
    url = (f"https://oauth.reddit.com/r/{urllib.parse.quote(sub)}/search?"
           + urllib.parse.urlencode({"q": q, "restrict_sr": "on", "sort": "new",
                                     "t": t_window, "limit": 25}))
    data = http_get_json(url, token)
    if not data:
        return []
    cutoff = now - days * 86400
    out = []
    for child in data.get("data", {}).get("children", []):
        post = child.get("data", {})
        if post.get("created_utc", 0) < cutoff:
            continue
        title_l = (post.get("title") or "").lower()
        if any(m in title_l for m in SKIP_TITLE_MARKERS):
            continue
        if post.get("stickied") or post.get("over_18"):
            continue
        score, matched = score_thread(post, terms, now)
        if not matched:
            continue
        sheets = entry.get("cheatsheets", [])
        slug = sheets[0].replace(".html", "").replace("_", "-") if sheets else sub.lower()
        out.append({
            "subreddit": sub,
            "audience": entry.get("audience", ""),
            "caution": entry.get("caution", "normal"),
            "title": post.get("title"),
            "permalink": "https://www.reddit.com" + post.get("permalink", ""),
            "created_utc": post.get("created_utc"),
            "age_hours": round((now - post.get("created_utc", now)) / 3600.0, 1),
            "num_comments": post.get("num_comments", 0),
            "is_self": post.get("is_self", False),
            "matched_terms": matched,
            "score": score,
            "cheatsheets": [SITE + s + "?" + UTM + slug for s in sheets],
            "cheatsheet_files": sheets,
        })
    out.sort(key=lambda r: r["score"], reverse=True)
    return out[:3]  # per-sub cap so no single community dominates


def eligible_for_post(entry: dict, rotation: dict, now: float) -> bool:
    if entry.get("caution") == "skip-unless-asked":
        return False
    last = rotation.get(entry["subreddit"])
    if not last:
        return True
    try:
        last_ts = datetime.fromisoformat(last).replace(tzinfo=timezone.utc).timestamp()
    except ValueError:
        return True
    return (now - last_ts) >= entry.get("post_cadence_days", 45) * 86400


CREDS_HELP = (
    "No Reddit credentials found. The scanner needs a read-only OAuth 'script' app.\n"
    "Set REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET / REDDIT_USERNAME / REDDIT_PASSWORD in\n"
    f"the environment or {ENV_FILE} (see this file's docstring for the 3-step setup).\n"
    "Until then the routine should fall back to browser-based discovery "
    "(docs/reddit-daily-drafts.md)."
)


def main() -> int:
    ap = argparse.ArgumentParser(description="Read-only Reddit opportunity scanner (OAuth).")
    ap.add_argument("--map", type=Path, default=DEFAULT_MAP)
    ap.add_argument("--days", type=int, default=7, help="Only threads newer than N days.")
    ap.add_argument("--limit-subs", type=int, default=0, help="Scan only the first N subs.")
    ap.add_argument("--sleep", type=float, default=1.0, help="Seconds between subreddit requests.")
    ap.add_argument("--dry-run", action="store_true", help="Print summary, write no files.")
    ap.add_argument("--print-urls", action="store_true",
                    help="Emit the browser navigation plan (no network/creds) and exit. PRIMARY mode.")
    args = ap.parse_args()

    if not args.map.exists():
        print(f"Map not found: {args.map}", file=sys.stderr)
        return 2
    cfg = json.loads(args.map.read_text(encoding="utf-8"))
    subs = cfg.get("subreddits", [])
    if args.limit_subs:
        subs = subs[:args.limit_subs]

    rotation = {}
    if ROTATION_FILE.exists():
        try:
            rotation = json.loads(ROTATION_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            rotation = {}

    if args.print_urls:
        now = datetime.now(timezone.utc).timestamp()
        return print_urls(cfg, subs, rotation, now, args.days)

    creds = load_credentials()
    if not creds:
        print(CREDS_HELP, file=sys.stderr)
        return 3
    token = get_token(creds)
    if not token:
        print("Could not obtain an OAuth token; check credentials.\n" + CREDS_HELP, file=sys.stderr)
        return 3

    now = datetime.now(timezone.utc).timestamp()
    candidates: list[dict] = []
    post_eligible: list[str] = []
    failures = 0
    for i, entry in enumerate(subs):
        print(f"[{i + 1}/{len(subs)}] r/{entry['subreddit']}", file=sys.stderr)
        try:
            candidates.extend(scan_subreddit(entry, token, args.days, now))
        except Exception as e:  # one sub failing must not sink the run
            print(f"  error scanning r/{entry['subreddit']}: {e}", file=sys.stderr)
            failures += 1
        if eligible_for_post(entry, rotation, now):
            post_eligible.append(entry["subreddit"])
        if i < len(subs) - 1:
            time.sleep(args.sleep)

    candidates.sort(key=lambda r: r["score"], reverse=True)
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    result = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "date": date_str,
        "days_window": args.days,
        "subs_scanned": len(subs),
        "sub_failures": failures,
        "comment_opportunities": candidates,
        "post_eligible_subreddits": post_eligible,
        "note": "Candidates only. The routine judges each one against docs/reddit-daily-drafts.md, "
                "checks current subreddit rules, and drafts. Nothing here is approved to post.",
    }

    print(f"\nScanned {len(subs)} subs ({failures} failed) -> {len(candidates)} comment "
          f"candidates; {len(post_eligible)} subs eligible for an original post.", file=sys.stderr)
    for c in candidates[:10]:
        print(f"  [{c['score']:>3}] r/{c['subreddit']} ({c['num_comments']}c, {c['age_hours']}h): "
              f"{c['title'][:70]}", file=sys.stderr)

    if args.dry_run:
        print("\n(dry-run: no files written)", file=sys.stderr)
        return 0

    DRAFTS_DIR.mkdir(parents=True, exist_ok=True)
    out_path = DRAFTS_DIR / f"{date_str}-candidates.json"
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {out_path.relative_to(REPO)}", file=sys.stderr)
    return 4 if failures and not candidates else 0


if __name__ == "__main__":
    raise SystemExit(main())
