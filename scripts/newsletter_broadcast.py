#!/usr/bin/env python3
"""Create a DRAFT broadcast in Resend for one newsletter issue. Never sends.

See docs/newsletter.md §8. Reads newsletter/YYYY-MM.email.html (and its
plain-text sibling, if present) and creates the broadcast with send left at
its default (false). Sending is a separate, explicit, human-run step —
scripts/newsletter_send.py — per the standing rule that routines draft and
David sends.

Refuses outright if asked to send: there is no --send flag on this script,
on purpose. If you're looking for that, you want newsletter_send.py.

Usage:
    python scripts/newsletter_broadcast.py --issue 2026-09
    python scripts/newsletter_broadcast.py --issue 2026-09 --subject "September: 8 new references"
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from newsletter_common import REPO_DIR, load_env_file, newsletter_dir, resend_request  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--issue", required=True, help="Issue month, YYYY-MM.")
    parser.add_argument("--subject", required=True, help="Email subject line.")
    parser.add_argument("--segment-id", default=None, help="Overrides RESEND_SEGMENT_ID.")
    parser.add_argument("--from-address", default=None, help="Overrides NEWSLETTER_FROM_ADDRESS.")
    parser.add_argument("--reply-to", default=None, help="Overrides NEWSLETTER_REPLY_TO.")
    parser.add_argument("--email-html", default=None, help="Path to the email-safe HTML (default: newsletter/<issue>.email.html).")
    parser.add_argument("--name", default=None, help="Internal broadcast reference name (default: cheatsheets-<issue>).")
    args = parser.parse_args()

    load_env_file()
    segment_id = args.segment_id or os.environ.get("RESEND_SEGMENT_ID", "").strip()
    if not segment_id:
        print(
            "ERROR: no segment id. Pass --segment-id or set RESEND_SEGMENT_ID in "
            "~/Projects/.resend.env (docs/newsletter.md §9).",
            file=sys.stderr,
        )
        return 2

    from_address = args.from_address or os.environ.get(
        "NEWSLETTER_FROM_ADDRESS", "Cheatsheets <hello@updates.cheatsheets.davidveksler.com>"
    )
    reply_to = args.reply_to or os.environ.get("NEWSLETTER_REPLY_TO", "")

    html_path = Path(args.email_html) if args.email_html else REPO_DIR / "newsletter" / f"{args.issue}.email.html"
    if not html_path.exists():
        print(f"ERROR: {html_path} does not exist. Write it before drafting the broadcast.", file=sys.stderr)
        return 2
    html = html_path.read_text(encoding="utf-8")

    text_path = html_path.with_suffix("").with_suffix(".txt")
    text = text_path.read_text(encoding="utf-8") if text_path.exists() else None

    payload = {
        "segment_id": segment_id,
        "from": from_address,
        "subject": args.subject,
        "html": html,
        "name": args.name or f"cheatsheets-{args.issue}",
        # "send" intentionally omitted -> defaults to false (draft). Never set true here.
    }
    if reply_to:
        payload["reply_to"] = reply_to
    if text:
        payload["text"] = text

    try:
        resp = resend_request("POST", "/broadcasts", payload)
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    broadcast_id = resp.get("id", "?")

    # Persisted (and committed — it's the audit trail for when/whether this issue
    # sent) so newsletter_send.py doesn't need an unverified "list broadcasts" call
    # to find this issue's draft. newsletter_send.py updates "sent" in place after send.
    state_path = newsletter_dir() / f"broadcast-{args.issue}.json"
    state_path.write_text(
        json.dumps(
            {
                "issue": args.issue,
                "broadcast_id": broadcast_id,
                "segment_id": segment_id,
                "subject": args.subject,
                "created": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "sent": False,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Draft broadcast created: {broadcast_id}")
    print(f"Review at https://resend.com/broadcasts/{broadcast_id}")
    print(f"State saved to {state_path}")
    print("Not sent. Send with: python scripts/newsletter_send.py --issue " + args.issue)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
