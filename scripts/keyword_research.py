"""Fetch a reproducible keyword shortlist without storing DataForSEO credentials.

Usage: python scripts/keyword_research.py keywords.txt --output report.json
Default market: United States, English. API requests incur DataForSEO charges.
"""
import argparse
import base64
import datetime
import json
from pathlib import Path
import urllib.request
import urllib.error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("keywords", type=Path, help="One keyword per line")
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--env", type=Path, default=Path.home() / "Projects/.dataforseo.env")
    parser.add_argument("--location", type=int, default=2840)
    parser.add_argument("--language", default="en")
    args = parser.parse_args()
    if args.output.exists():
        parser.error("Output exists; choose a new filename to preserve prior evidence")
    credentials = {}
    for line in args.env.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.removeprefix("export ").split("=", 1)
            credentials[key.strip()] = value.strip().strip("\"'")
    keywords = list(dict.fromkeys(line.strip() for line in args.keywords.read_text(encoding="utf-8-sig").splitlines() if line.strip() and not line.lstrip().startswith("#")))
    if not 1 <= len(keywords) <= 700:
        parser.error("Provide 1 to 700 keywords per request")
    payload = [{"keywords": keywords, "location_code": args.location,
                "language_code": args.language, "include_serp_info": True}]
    endpoint = "https://api.dataforseo.com/v3/dataforseo_labs/google/keyword_overview/live"
    auth = base64.b64encode((credentials["DATAFORSEO_LOGIN"] + ":" + credentials["DATAFORSEO_PASSWORD"]).encode()).decode()
    request = urllib.request.Request(endpoint, data=json.dumps(payload).encode(), headers={
        "Authorization": "Basic " + auth, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            result = json.load(response)
    except urllib.error.HTTPError as error:
        raise SystemExit(f"DataForSEO HTTP {error.code}: {error.reason}. No volume report written.") from None
    if result.get("status_code") != 20000 or result.get("tasks_error"):
        raise SystemExit("DataForSEO request failed: " + str(result.get("status_code")))
    for task in result.get("tasks", []):
        if task.get("status_code") != 20000:
            raise SystemExit("DataForSEO task failed: " + str(task.get("status_code")))
    report = {"retrieved_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
              "endpoint": endpoint, "request": payload, "response": result}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Market: location {args.location}, language {args.language}")
    print("Keyword | monthly search volume | organic difficulty (0-100) | volume updated")
    for task in result.get("tasks", []):
        for group in task.get("result") or []:
            for item in group.get("items") or []:
                info = item.get("keyword_info") or {}
                props = item.get("keyword_properties") or {}
                print(f"{item['keyword']} | {info.get('search_volume')} | {props.get('keyword_difficulty')} | {info.get('last_updated_time')}")
    print("Cost (USD):", result.get("cost"))
    print("Saved:", args.output)


if __name__ == "__main__":
    main()
