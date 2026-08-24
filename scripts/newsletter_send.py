#!/usr/bin/env python3
"""The human gate for actually sending a newsletter issue. Not run by any routine.

See docs/newsletter.md §8, §12 ("routine sends autonomously" is a rejected
alternative — an email is the one artifact here that can't be rolled back).
Mirrors deploy.sh's shape: preflight -> preview -> confirm -> send -> verify.

Usage:
    python scripts/newsletter_send.py --issue 2026-09              # interactive confirm
    python scripts/newsletter_send.py --issue 2026-09 --yes        # skip the prompt
    python scripts/newsletter_send.py --issue 2026-09 --dry-run    # preflight + preview only
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from newsletter_common import load_env_file, newsletter_dir, resend_request  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--issue", required=True, help="Issue month, YYYY-MM.")
    parser.add_argument("--yes", action="store_true", help="Skip the confirm prompt.")
    parser.add_argument("--dry-run", action="store_true", help="Preflight + preview only, do not send.")
    parser.add_argument("--scheduled-at", default=None, help="ISO 8601 or natural language (e.g. 'in 1 hour'). Default: send now.")
    args = parser.parse_args()

    load_env_file()

    # --------------------------------------------------------------- Preflight ----
    state_path = newsletter_dir() / f"broadcast-{args.issue}.json"
    if not state_path.exists():
        print(
            f"ERROR: {state_path} not found. Run newsletter_broadcast.py for this issue first.",
            file=sys.stderr,
        )
        return 2

    state = json.loads(state_path.read_text(encoding="utf-8"))
    if state.get("sent"):
        print(f"ERROR: issue {args.issue} is already marked sent (at {state.get('sent_at', '?')}).", file=sys.stderr)
        print("Refusing to send the same issue twice. Delete the 'sent' flag in", state_path, "if this is deliberate.", file=sys.stderr)
        return 1

    broadcast_id = state["broadcast_id"]

    # ----------------------------------------------------------------- Preview ----
    print(f"Issue:      {args.issue}")
    print(f"Broadcast:  {broadcast_id}")
    print(f"Subject:    {state.get('subject', '?')}")
    print(f"Segment:    {state.get('segment_id', '?')}")
    print(f"Created:    {state.get('created', '?')}")
    print(f"Dashboard:  https://resend.com/broadcasts/{broadcast_id}")

    if args.dry_run:
        print("\n[dry-run] Preflight + preview only. Nothing sent.")
        return 0

    # ------------------------------------------------------------------ Confirm ----
    if not args.yes:
        answer = input(f"\nSend broadcast {broadcast_id} now? [y/N] ").strip().lower()
        if answer != "y":
            print("Aborted. Nothing sent.")
            return 1

    # -------------------------------------------------------------------- Send ----
    payload = {}
    if args.scheduled_at:
        payload["scheduled_at"] = args.scheduled_at

    try:
        resp = resend_request("POST", f"/broadcasts/{broadcast_id}/send", payload or None)
    except RuntimeError as exc:
        print(f"ERROR: send failed: {exc}", file=sys.stderr)
        return 2

    # ------------------------------------------------------------------ Verify ----
    state["sent"] = True
    state["sent_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    state["send_response_id"] = resp.get("id")
    state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")

    print(f"Sent. Resend send id: {resp.get('id', '?')}")
    print(f"State updated: {state_path}")
    print("Commit that file so the send is on the record.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
