#!/usr/bin/env python3
"""
Pull yesterday's per-path view counts from Cloudflare GraphQL Analytics and
accumulate them into popularity.json with 30-day exponential decay.

Required env vars:
  CLOUDFLARE_API_TOKEN  – Bearer token with Zone Analytics:Read permission
  CLOUDFLARE_ZONE_ID    – Zone ID (optional; auto-detected from first zone if absent)

Run this once a day (e.g. via GitHub Actions). Each run:
  1. Fetches yesterday's GET request counts grouped by URL path.
  2. Multiplies every existing score by DECAY_FACTOR (≈ 0.967, 30-day half-life).
  3. Adds yesterday's raw counts on top of the decayed scores.
  4. Also stores yesterday's raw (undecayed) counts as "dailyViews", a simple
     last-24-hours view count used for the popularity page's daily panel.
  5. Adds yesterday's raw counts to "totalViews", a cumulative (never-decayed)
     lifetime view counter per page, and to "totalViewsHistory", a per-day
     total-site view count keyed by ISO date (kept for the last 90 days) so
     the popularity page can chart a trend line.
  6. Adds yesterday's raw counts, per catalogued .html file, to "dailyHistory"
     ({"<file>": {"<ISO date>": views, ...}}), a rolling 30-day ring buffer
     per file (see accumulate_daily_history) that feeds the index.php
     Explorer drawer's per-sheet sparkline. The accumulation step is a pure
     function so it can be unit-tested with synthetic counts without calling
     Cloudflare (see scripts/test_fetch_popularity.py).
  7. Saves result back to popularity.json.

The decay means a page visited 1,000 times today will score ~630 after 15 days,
~370 after 30 days, ~50 after 90 days – natural "trending" window.

Note: referrer-host breakdowns (clientRefererHost) are NOT fetched here —
Cloudflare gates that GraphQL field behind Pro plan or higher, and this zone
is on the Free plan, so the field is permanently inaccessible regardless of
token scopes.
"""
import json
import os
import sys
from datetime import date, timedelta
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

CLOUDFLARE_GQL = "https://api.cloudflare.com/client/v4/graphql"
CLOUDFLARE_REST = "https://api.cloudflare.com/client/v4"
POPULARITY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "popularity.json")
DECAY_FACTOR = 29 / 30   # ≈ 0.9667; score halves roughly every 30 days


def cf_get(token: str, path: str) -> dict:
    req = Request(
        f"{CLOUDFLARE_REST}{path}",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    with urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def cf_gql(token: str, query: str) -> dict:
    body = json.dumps({"query": query}).encode()
    req = Request(
        CLOUDFLARE_GQL,
        data=body,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    with urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def get_zone_id(token: str) -> str:
    data = cf_get(token, "/zones?per_page=50")
    zones = data.get("result", [])
    if not zones:
        raise ValueError("No zones found for this token")
    # Prefer davidveksler.com; fall back to first zone
    for zone in zones:
        if "davidveksler.com" in zone.get("name", ""):
            return zone["id"]
    return zones[0]["id"]


def fetch_path_counts(token: str, zone_id: str, day: str) -> dict[str, int]:
    """
    Query Cloudflare httpRequestsAdaptiveGroups for GET requests on `day`
    (ISO date string, e.g. "2026-06-28"), grouped by clientRequestPath.

    Returns path_counts: {filename: count} for top-level .html files.
    """
    query = """
    {
      viewer {
        zones(filter: { zoneTag: "%s" }) {
          httpRequestsAdaptiveGroups(
            limit: 5000
            filter: {
              date_geq: "%s"
              date_leq: "%s"
              requestSource: "eyeball"
            }
            orderBy: [count_DESC]
          ) {
            count
            dimensions {
              clientRequestPath
            }
          }
        }
      }
    }
    """ % (zone_id, day, day)

    result = cf_gql(token, query)

    if "errors" in result and result["errors"]:
        raise RuntimeError(f"Cloudflare GraphQL error: {result['errors']}")

    zone = result["data"]["viewer"]["zones"][0]

    path_counts: dict[str, int] = {}
    for g in zone["httpRequestsAdaptiveGroups"]:
        path: str = g["dimensions"]["clientRequestPath"]
        count: int = g["count"]
        # Keep only top-level .html files (no sub-paths, no query strings)
        filename = path.lstrip("/").split("?")[0]
        if filename.endswith(".html") and "/" not in filename and filename:
            path_counts[filename] = path_counts.get(filename, 0) + count

    return path_counts


def load_popularity() -> dict:
    if os.path.exists(POPULARITY_FILE):
        try:
            with open(POPULARITY_FILE, encoding="utf-8") as f:
                data = json.load(f)
                data.setdefault("totalViews", {})
                data.setdefault("totalViewsHistory", {})
                data.setdefault("dailyHistory", {})
                return data
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "lastUpdated": None, "scores": {}, "dailyViews": {}, "totalViews": {},
        "totalViewsHistory": {}, "dailyHistory": {},
    }


def accumulate_daily_history(
    daily_history: dict[str, dict[str, int]],
    new_counts: dict[str, int],
    day: str,
    cutoff: str,
    seed_views: dict[str, int] | None = None,
    seed_date: str | None = None,
) -> dict[str, dict[str, int]]:
    """Pure function: return an updated per-file 30-day daily-view ring buffer.

    ``daily_history`` is the existing ``{"<file>": {"<ISO date>": views}}``
    structure (may be empty). ``new_counts`` is one day's per-path counts
    (already restricted to top-level ``.html`` files by
    ``fetch_path_counts``, but filtered again here so a caller passing
    unfiltered data can't leak a non-.html key in). ``day`` is the ISO date
    those counts belong to; ``cutoff`` is the oldest ISO date to keep
    (inclusive) — dates before it are pruned, giving each file a rolling
    window rather than an ever-growing history.

    ``seed_views``/``seed_date``: when ``daily_history`` is empty (this
    feature's first run against an existing popularity.json), the caller may
    pass the *already-recorded* ``dailyViews`` snapshot and the date it
    represents so the sparkline has one real data point immediately instead
    of an empty chart for 30 days. This never fabricates numbers — it reuses
    a count Cloudflare already reported and stores it under its own date.
    Only fires when ``daily_history`` starts empty, so it can't overwrite or
    duplicate real accumulated history on later runs.

    Every existing key of the popularity.json schema and its semantics are
    left untouched by this function; it only computes the "dailyHistory"
    value.
    """
    result: dict[str, dict[str, int]] = {
        f: dict(days) for f, days in daily_history.items() if f.endswith(".html")
    }

    if not result and seed_views and seed_date:
        for filename, views in seed_views.items():
            if filename.endswith(".html") and views:
                result.setdefault(filename, {})[seed_date] = int(views)

    for filename, count in new_counts.items():
        if not filename.endswith(".html"):
            continue
        result.setdefault(filename, {})[day] = int(count)

    pruned: dict[str, dict[str, int]] = {}
    for filename, days in result.items():
        kept = {d: v for d, v in days.items() if d >= cutoff}
        if kept:
            pruned[filename] = kept
    return pruned


def save_popularity(data: dict) -> None:
    with open(POPULARITY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, sort_keys=True)
        f.write("\n")


def main() -> None:
    token = os.environ.get("CLOUDFLARE_API_TOKEN", "").strip()
    if not token:
        print("ERROR: CLOUDFLARE_API_TOKEN is not set", file=sys.stderr)
        sys.exit(1)

    zone_id = os.environ.get("CLOUDFLARE_ZONE_ID", "").strip() or get_zone_id(token)
    print(f"Using zone: {zone_id}")

    today = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    popularity = load_popularity()

    if popularity.get("lastUpdated") == today:
        print("Already updated today — skipping.")
        return

    print(f"Fetching path analytics for {yesterday}…")
    try:
        new_counts = fetch_path_counts(token, zone_id, yesterday)
    except (URLError, HTTPError, RuntimeError, KeyError) as exc:
        print(f"ERROR fetching path analytics: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"  {sum(new_counts.values())} page views across {len(new_counts)} HTML paths")

    scores: dict[str, float] = popularity.get("scores", {})

    # Apply decay to every existing score
    for key in list(scores):
        scores[key] *= DECAY_FACTOR

    # Add yesterday's counts
    for filename, count in new_counts.items():
        scores[filename] = scores.get(filename, 0.0) + count

    # Prune near-zero entries to keep the file lean
    scores = {k: round(v, 4) for k, v in scores.items() if v >= 0.1}

    # Cumulative, never-decayed lifetime view counter per page
    total_views: dict[str, int] = popularity.get("totalViews", {})
    for filename, count in new_counts.items():
        total_views[filename] = total_views.get(filename, 0) + count

    # Per-day total-site view count, kept for the last 90 days (trend line)
    history: dict[str, int] = popularity.get("totalViewsHistory", {})
    history[yesterday] = sum(new_counts.values())
    cutoff90 = (date.today() - timedelta(days=90)).isoformat()
    history = {d: v for d, v in history.items() if d >= cutoff90}

    # Per-file 30-day daily-view ring buffer for the index.php Explorer
    # drawer's sparkline. Seeded from the dailyViews snapshot this popularity.json
    # already had on this feature's first run, so the sparkline is not empty
    # for 30 days; see accumulate_daily_history's docstring.
    cutoff30 = (date.today() - timedelta(days=30)).isoformat()
    daily_history = accumulate_daily_history(
        popularity.get("dailyHistory", {}), new_counts, yesterday, cutoff30,
        seed_views=popularity.get("dailyViews"), seed_date=popularity.get("lastUpdated"),
    )

    popularity["lastUpdated"] = today
    popularity["scores"] = scores
    popularity["dailyViews"] = dict(new_counts)  # raw, undecayed — last complete 24h
    popularity["totalViews"] = total_views
    popularity["totalViewsHistory"] = history
    popularity["dailyHistory"] = daily_history

    save_popularity(popularity)
    print(f"Saved {len(scores)} page scores, {len(new_counts)} daily view counts, "
          f"{len(total_views)} lifetime totals, {len(daily_history)} per-file "
          f"histories to popularity.json — done.")


if __name__ == "__main__":
    main()
