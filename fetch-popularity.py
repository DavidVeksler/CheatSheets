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
  5. Saves result back to popularity.json.

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
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"lastUpdated": None, "scores": {}, "dailyViews": {}}


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

    popularity["lastUpdated"] = today
    popularity["scores"] = scores
    popularity["dailyViews"] = dict(new_counts)  # raw, undecayed — last complete 24h

    save_popularity(popularity)
    print(f"Saved {len(scores)} page scores and {len(new_counts)} daily view counts to popularity.json — done.")


if __name__ == "__main__":
    main()
