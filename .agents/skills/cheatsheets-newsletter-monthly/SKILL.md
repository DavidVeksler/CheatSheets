---
name: cheatsheets-newsletter-monthly
description: >-
  Monthly newsletter drafter for cheatsheets.davidveksler.com. Computes the issue from
  git history + popularity.json, writes the archive page and email HTML, syncs confirmed
  subscribers into Resend, and creates a DRAFT broadcast. Use when David asks to run the
  newsletter routine or draft this month's issue. Draft-only: it never sends. David sends
  with scripts/newsletter_send.py after reviewing the draft.
---

# cheatsheets-newsletter-monthly

Draft-tier routine. Schedule: 1st of the month, 03:00 local.

**The binding spec is the runbook: [`docs/newsletter.md`](../../../docs/newsletter.md).**
This file is a summary. If they disagree, the runbook wins. Read it before acting,
especially §6 (content model), §7 (email HTML rules), and §9 (phasing/prerequisites).

**Do not run this until Phase 0 of the spec is done** (domain verified, DNS records live,
`RESEND_SEGMENT_ID` set in `~/Projects/.resend.env`, `NEWSLETTER_TOKEN_SECRET` and
`RESEND_SENDING_KEY` set on the web server). If any of those checks fail, stop and report
instead of improvising a workaround.

## Procedure

1. **Digest:** `python scripts/newsletter_digest.py --issue YYYY-MM` (issue = the
   upcoming month; it digests the month that just ended). Exit code 3 means the digest
   didn't clear the skip threshold (`docs/newsletter.md` §6) — **stop here, report "no
   issue this month", commit nothing, exit.** Exit code 2 is a real error — stop and report.
2. **Write the issue** from `newsletter/digest-YYYY-MM.json` **only** — every fact in the
   issue must trace to a field in that file. Do not add news, opinions, or claims the
   digest doesn't contain.
   - `newsletter/YYYY-MM.html` — a normal site page, full metadata, passes the SEO gate,
     follows the site's usual design rules (this page is NOT email — Modern Platform
     Baseline applies here same as any cheatsheet).
   - `newsletter/YYYY-MM.email.html` — email-safe HTML per §7 (inline styles, table
     layout, no external CSS/JS, `{{{RESEND_UNSUBSCRIBE_URL}}}` merge tag in the footer,
     absolute image URLs, plain-text alternative at `newsletter/YYYY-MM.txt`).
   - David-voice: no em dashes, no unverifiable claims, no "we're excited to." Every
     item's one-liner says what the page is *for*.
   - UTM every link: `?utm_source=newsletter&utm_medium=email&utm_campaign=cheatsheets_monthly&utm_content=YYYY-MM`.
3. **SEO gate:** `python scripts/seo_check.py newsletter/YYYY-MM.html` — must pass before
   continuing.
4. **Sync subscribers:** `python scripts/newsletter_sync.py`. Report the `+N new, M total`
   line. A sync error is non-fatal to drafting (report it, continue to step 5) but must be
   surfaced clearly — do not silently proceed as if the list is current.
5. **Draft the broadcast:**
   `python scripts/newsletter_broadcast.py --issue YYYY-MM --subject "<subject line>"`.
   This creates the broadcast with `send` left at its default (false) — a draft. It writes
   `newsletter/broadcast-YYYY-MM.json` with the broadcast id.
6. **Commit and push** everything from this run (digest JSON, archive page, email HTML,
   text alternative, broadcast state file). One commit for the issue.
7. **Report:** item counts (new/updated/popular), subscriber delta, broadcast id and
   dashboard link, one-line diff summary. Quiet success is fine — "drafted issue 2026-09,
   8 new + 8 updated, +3 subscribers (41 total), broadcast bc_xxx" is a complete report.

## Hard limits

- **Never send.** No call to `newsletter_send.py`, no `POST /broadcasts/{id}/send`, no
  `send: true` on the create call. `newsletter_broadcast.py` has no `--send` flag —
  if you find yourself wanting one, stop, that means you're about to violate this rule.
- Never deploy the archive page — that stays on the normal `./deploy.sh` gate, run by David.
- Never delete, unsubscribe, or overwrite a Resend contact. `newsletter_sync.py` only adds.
- Never invent an item not present in the digest JSON.
- Max one issue per run, max one draft broadcast per run.
- Fail closed: digest error, SEO gate failure, or a Resend non-2xx on the broadcast create
  → stop, change nothing further, report the specific failure.
- ntfy only on failure or when the subscriber delta exceeds ±20.

## Then David

Reviews the draft in the Resend dashboard, then from the repo root:

```bash
python scripts/newsletter_send.py --issue 2026-09
```

Prints the recipient count and subject, prompts `[y/N]`, sends, verifies, and updates
`newsletter/broadcast-YYYY-MM.json` with the send timestamp — commit that update.
