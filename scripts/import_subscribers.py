#!/usr/bin/env python3
"""Copy the droplet's newsletter stores into the forms Worker's D1 database.

    python3 scripts/import_subscribers.py            # plan: counts only
    python3 scripts/import_subscribers.py --apply    # insert, then verify droplet == D1

Sources (read-only over ssh, `sudo -n cat`), written by the PHP endpoints:
  .subscribers.jsonl  intake / audit log   -> D1 subscribers (ts, email, src)
  .confirmed.jsonl    sendable queue        -> D1 confirmed   (ts, email), unique per address

Idempotent: an intake row is keyed on (ts, email, src) and counted as a multiset, a
confirmed row on the lower-cased address; only what D1 lacks is inserted, so a re-run
inserts nothing and rows the Worker writes itself are never touched. Run it once when
D1 is created and again right after the route goes live (spec §6).

These are subscribers' email addresses: nothing here prints, logs or writes one to
the repo. Output is counts. The SQL batch lives in a private temp dir, deleted after
use. Fails closed on an unparseable line. Stdlib only.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import newsletter_d1 as D  # noqa: E402

SSH = os.environ.get("CS_SSH", "johngalt@198.211.102.9")
DOCROOT = "/var/www/cheatsheets.davidveksler.com/htdocs"
FILES = {"subscribers": DOCROOT + "/.subscribers.jsonl", "confirmed": DOCROOT + "/.confirmed.jsonl"}
BATCH = 200


class SourceError(RuntimeError):
    pass


def droplet_rows(kind: str) -> list[dict]:
    r = subprocess.run(["ssh", "-o", "BatchMode=yes", "-o", "ConnectTimeout=15", SSH,
                        f"if [ -f {FILES[kind]} ]; then sudo -n cat {FILES[kind]}; fi"],
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        raise SourceError(f"ssh read of {FILES[kind]} failed (exit {r.returncode})")
    rows = []
    for n, line in enumerate(r.stdout.splitlines(), 1):
        if not line.strip():
            continue
        try:
            rec = json.loads(line)
            email, ts = rec["email"], rec["ts"]
            if not isinstance(email, str) or not isinstance(ts, str) or "@" not in email:
                raise ValueError("bad field types")
        except (ValueError, KeyError) as exc:
            raise SourceError(f"{kind} line {n} unparseable ({type(exc).__name__}); nothing imported")
        src = rec.get("src")
        rows.append({"ts": ts, "email": email, "src": src if isinstance(src, str) else None})
    return rows


def plan(kind: str, src: list[dict], dst: list[dict]) -> list[dict]:
    if kind == "subscribers":
        key = lambda r: (r["ts"], r["email"], r.get("src"))  # noqa: E731
        need = Counter(key(r) for r in src) - Counter(key(r) for r in dst)
        out = []
        for r in src:
            if need[key(r)] > 0:
                need[key(r)] -= 1
                out.append(r)
        return out
    have = {r["email"].lower() for r in dst}
    out, seen = [], set()
    for r in src:
        e = r["email"].lower()
        if e not in have and e not in seen:
            seen.add(e)
            out.append(r)
    return out


def d1_rows(kind: str) -> list[dict]:
    cols = "ts, email, src" if kind == "subscribers" else "ts, email"
    return D.execute(f"SELECT {cols} FROM {kind} ORDER BY id")


def insert(kind: str, rows: list[dict]) -> None:
    for i in range(0, len(rows), BATCH):
        if kind == "subscribers":
            stmts = [f"INSERT INTO subscribers (ts, email, src) VALUES ({D.sql_str(r['ts'])}, {D.sql_str(r['email'])}, "
                     f"{D.sql_str(r['src'])});" for r in rows[i:i + BATCH]]
        else:
            stmts = [f"INSERT OR IGNORE INTO confirmed (ts, email) VALUES ({D.sql_str(r['ts'])}, {D.sql_str(r['email'])});"
                     for r in rows[i:i + BATCH]]
        D.execute(statements=stmts)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--apply", action="store_true", help="insert the missing rows (default: dry run)")
    a = ap.parse_args()
    failed = False
    for kind in ("subscribers", "confirmed"):
        try:
            src, dst = droplet_rows(kind), d1_rows(kind)
            todo = plan(kind, src, dst)
            print(f"{kind:<11} droplet {len(src):4d} rows, D1 {len(dst):4d} rows, to import {len(todo):4d}")
            if todo and a.apply:
                insert(kind, todo)
                left = plan(kind, src, d1_rows(kind))
                print(f"{kind:<11} imported {len(todo)}; droplet rows still missing from D1: {len(left)}")
                failed |= bool(left)
        except (SourceError, D.D1Error) as exc:
            print(f"{kind}: {D.redact(str(exc))}", file=sys.stderr)
            failed = True
    if not a.apply:
        print("dry run: nothing written (use --apply)")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
