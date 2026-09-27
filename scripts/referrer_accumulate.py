#!/usr/bin/env python3
"""Accumulate daily referrer aggregates into a long-term store (.referrers.json).

The origin nginx logs are the only referrer source (Cloudflare Free hides referrers) and
logrotate keeps ~3 weeks, so this runs nightly ON the server and folds every complete day
still in the logs into a store that outlives them. popularity.php reads the store.

    python3 scripts/referrer_accumulate.py            # update <repo>/.referrers.json
    python3 scripts/referrer_accumulate.py --dry-run  # print what would be added

Server cron (johngalt, after the 04:00 cheatsheets-pull.sh): see deploy/DEPLOY.md.

A day is written once, when complete (before today, UTC log time) and absent from the
store, so a missed night is backfilled from the logs on the next run and re-runs are
no-ops. The oldest day in the logs is skipped unless its lines start by 00:10 (a partial
day would understate that date forever). Only aggregates are kept: no IPs, no referrer
paths, and private-network hosts collapse to "(private network)".

Store schema 1:
  {"schema": 1, "generated": ISO-UTC,
   "days": {"YYYY-MM-DD": {"channels": {channel: landings},     # includes "Internal"
                           "sources":  {channel: {source: n}},  # top SOURCE_CAP per channel
                           "landing":  {channel: {path: n}}}}}  # top LANDING_CAP per channel
"""
import argparse
import collections
import ipaddress
import json
import os
import re
import sys
from datetime import date, datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import referrer_report as rr  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORE = os.path.join(ROOT, ".referrers.json")
SCHEMA = 1
SOURCE_CAP = 50
LANDING_CAP = 30
RETAIN_DAYS = 1830  # ~5 years
PRIVATE_TLDS = {"local", "internal", "lan", "corp", "home", "intranet", "localdomain", "localhost"}
UTM_OK = re.compile(r"[a-z0-9._-]{1,40}")


def clean_source(source):
    """Public hostname or utm tag, or a placeholder that reveals nothing about a reader."""
    if source.startswith("utm:"):
        tag = source[4:].lower()
        return "utm:" + tag if UTM_OK.fullmatch(tag) else "utm:(other)"
    host = source.lower().rstrip(".")
    if not host:
        return ""
    try:
        ipaddress.ip_address(host.strip("[]"))
        return "(private network)"
    except ValueError:
        pass
    if "." not in host or host.rsplit(".", 1)[1] in PRIVATE_TLDS:
        return "(private network)"
    return host


def aggregate(events):
    """events: iterable of (date, channel, source, path) -> {iso_date: day_record}."""
    days = collections.defaultdict(lambda: {"channels": collections.Counter(),
                                            "sources": collections.defaultdict(collections.Counter),
                                            "landing": collections.defaultdict(collections.Counter)})
    for day, ch, source, path in events:
        rec = days[day.isoformat()]
        rec["channels"][ch] += 1
        if ch == "Internal":
            continue
        rec["landing"][ch][path] += 1
        src = clean_source(source)
        if src:
            rec["sources"][ch][src] += 1
    return {d: {"channels": dict(r["channels"].most_common()),
                "sources": {c: dict(v.most_common(SOURCE_CAP)) for c, v in r["sources"].items()},
                "landing": {c: dict(v.most_common(LANDING_CAP)) for c, v in r["landing"].items()}}
            for d, r in days.items()}


def merge(store, new_days, today):
    """Add days not already stored, prune past RETAIN_DAYS. Returns (store, added dates)."""
    stored = store.setdefault("days", {})
    added = sorted(d for d in new_days if d not in stored and d < today.isoformat())
    for d in added:
        stored[d] = new_days[d]
    cutoff = (today - timedelta(days=RETAIN_DAYS)).isoformat()
    store["days"] = {d: stored[d] for d in sorted(stored) if d >= cutoff}
    store["schema"] = SCHEMA
    return store, added


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        return {"schema": SCHEMA, "days": {}}
    if data.get("schema") != SCHEMA or not isinstance(data.get("days"), dict):
        sys.exit(f"ERROR: {path} has an unknown schema; refusing to overwrite it")
    return data


def save(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"), sort_keys=True)
        f.write("\n")
    os.chmod(tmp, 0o644)
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--store", default=STORE)
    ap.add_argument("--log-dir", default=rr.LOG_DIR)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    today = datetime.now(timezone.utc).date()
    store = load(args.store)
    have = set(store.get("days", {}))
    hits, per_ip_day, first_seen = rr.read_hits(
        args.log_dir, keep_day=lambda d: d < today and d.isoformat() not in have)
    if first_seen is None:
        sys.exit(f"ERROR: no parseable log lines under {args.log_dir}")

    events = [(dt.date(), ch, src, path) for dt, ch, src, path in rr.classify(hits, per_ip_day)]
    new_days = aggregate(events)
    if first_seen.hour or first_seen.minute > 10:
        new_days.pop(first_seen.date().isoformat(), None)  # partial oldest day

    store, added = merge(store, new_days, today)
    store["generated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    for d in added:
        ch = store["days"][d]["channels"]
        ext = sum(n for c, n in ch.items() if c != "Internal")
        print(f"{d}: {ext} external landings ({', '.join(f'{c} {n}' for c, n in ch.items() if c != 'Internal')})")
    print(f"{'Would add' if args.dry_run else 'Added'} {len(added)} day(s); "
          f"store holds {len(store['days'])} day(s)")
    if not args.dry_run and added:
        save(args.store, store)


if __name__ == "__main__":
    main()
