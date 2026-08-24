#!/usr/bin/env python3
"""Pull confirmed newsletter signups from production and upsert them into Resend.

See docs/newsletter.md §2.2, §3, §8. SSH-pulls .confirmed.jsonl (gitignored)
from the production docroot — the web server never gets contact-write access,
contacts flow one way, server -> Resend, via this script. Only ever *adds*
contacts: never deletes, unsubscribes, or overwrites one. Unsubscribes and
bounces live entirely inside Resend and are never synced back here.

Resend's current Global Contacts model does not clearly document upsert
semantics for POST /contacts on an email that's already a contact elsewhere
(checked 2026-08-23: the public docs don't say). This script defends against
that gap by listing known contacts first and only creating addresses it
doesn't already see, and treats a single create failure as non-fatal so one
bad row can't sink the whole sync — but watch the first live run by hand
against the Resend dashboard before trusting it unattended.

Usage:
    python scripts/newsletter_sync.py                                  # pull + sync
    python scripts/newsletter_sync.py --dry-run                        # pull + report only
    python scripts/newsletter_sync.py --local-file path/to/confirmed.jsonl  # skip SSH (testing)
    python scripts/newsletter_sync.py --segment-id seg_xxx              # override RESEND_SEGMENT_ID
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import List, Set, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
from newsletter_common import load_env_file, resend_request  # noqa: E402

PROD_USER = "johngalt"
PROD_HOST = "direct.vellum.capital"
PROD_PATH = "/var/www/cheatsheets.davidveksler.com/htdocs/.confirmed.jsonl"

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def pull_confirmed_via_ssh() -> str:
    result = subprocess.run(
        ["ssh", f"{PROD_USER}@{PROD_HOST}", "cat", PROD_PATH],
        capture_output=True, text=True, encoding="utf-8", timeout=30,
    )
    if result.returncode != 0:
        # A fresh deploy with zero confirmations yet is not an error worth aborting on.
        if "No such file" in result.stderr:
            return ""
        raise RuntimeError(f"ssh pull failed: {result.stderr.strip()}")
    return result.stdout


def parse_confirmed(text: str) -> List[str]:
    emails: List[str] = []
    seen: Set[str] = set()
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            continue
        email = str(record.get("email", "")).strip().lower()
        if email and email not in seen and EMAIL_RE.match(email):
            seen.add(email)
            emails.append(email)
    return emails


def list_known_emails(segment_id: str) -> Set[str]:
    """Best-effort pagination — defensive against undocumented response shape."""
    known: Set[str] = set()
    cursor = None
    for _ in range(200):  # hard stop so a pagination bug can't loop forever
        path = f"/contacts?segment_id={segment_id}"
        if cursor:
            path += f"&after={cursor}"
        resp = resend_request("GET", path)
        data = resp.get("data") or []
        for contact in data:
            email = str(contact.get("email", "")).strip().lower()
            if email:
                known.add(email)
        cursor = resp.get("after") or (resp.get("pagination") or {}).get("after")
        if not data or not cursor:
            break
    return known


def create_contact(email: str, segment_id: str) -> Tuple[bool, str]:
    try:
        resend_request("POST", "/contacts", {"email": email, "segments": [segment_id]})
        return True, "created"
    except RuntimeError as exc:
        return False, str(exc)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--segment-id", default=None, help="Overrides RESEND_SEGMENT_ID.")
    parser.add_argument("--dry-run", action="store_true", help="Report what would be added; write nothing.")
    parser.add_argument("--local-file", default=None, help="Use a local .confirmed.jsonl instead of SSH-pulling production.")
    args = parser.parse_args()

    load_env_file()
    segment_id = args.segment_id or os.environ.get("RESEND_SEGMENT_ID", "").strip()
    if not segment_id:
        print(
            "ERROR: no segment id. Pass --segment-id or set RESEND_SEGMENT_ID in "
            "~/Projects/.resend.env — the segment is created once in the Resend "
            "dashboard during Phase 0 (docs/newsletter.md §9).",
            file=sys.stderr,
        )
        return 2

    try:
        text = Path(args.local_file).read_text(encoding="utf-8") if args.local_file else pull_confirmed_via_ssh()
        confirmed = parse_confirmed(text)
        print(f"Pulled {len(confirmed)} confirmed address(es).")

        known = list_known_emails(segment_id)
        print(f"Resend already has {len(known)} contact(s) in this segment.")
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    to_add = [e for e in confirmed if e not in known]

    if args.dry_run:
        print(f"[dry-run] would add {len(to_add)} new contact(s).")
        return 0

    added = 0
    failed: List[Tuple[str, str]] = []
    for email in to_add:
        ok, detail = create_contact(email, segment_id)
        if ok:
            added += 1
        else:
            failed.append((email, detail))

    print(f"+{added} new, {len(known) + added} total, {len(failed)} error(s).")
    for email, detail in failed:
        print(f"  FAILED {email}: {detail}", file=sys.stderr)

    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
