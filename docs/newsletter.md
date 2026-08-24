# Newsletter — feature spec

**Status:** Phases 1–2 code-complete (2026-08-23), **not live**. Phase 0 (domain
verification, DNS, keys, postal address) hasn't run, so `subscribe.php` fails closed
until it does. See the phasing table in §9 for what exists vs what's still to build.
**Owner:** David Veksler · **Drafted:** 2026-08-23 · **Provider:** [Resend](https://resend.com)

Turns the existing signup form on `index.php` / `how-its-built.html` into a real,
compliant, mostly-autonomous monthly newsletter. The pipeline that already produces
and governs 181 reference pages becomes the content source: the issue is *computed*
from git history, freshness runs, and Cloudflare traffic — not written from scratch.

When this ships, this file becomes the runbook. Add a row to the AGENTS.md doc-routing
table pointing at it and replace the **Email signup endpoint** section there with a
pointer here.

---

## 1. Where it stands today

| Piece | Today | Gap |
|---|---|---|
| Signup form | `index.php` ~L821, `how-its-built.html`; one field + honeypot (`website`), no JS dependency | Copy promises "occasional email"; nothing has ever been sent |
| Endpoint | [`subscribe.php`](../subscribe.php) — validates, appends to `.subscribers.jsonl`, `mail()`s a notification to `CHEATSHEET_NOTIFY_EMAIL` | No confirmation email, no dedup, no unsubscribe, no suppression |
| List store | `.subscribers.jsonl` on the server (gitignored) | Append-only; a resubscribe or unsubscribe has nowhere to go |
| Sending | PHP `mail()` on the DO box | Unauthenticated bulk mail from a shared host lands in spam |
| Compliance | none | No unsubscribe link, no `List-Unsubscribe`, no postal address, no DMARC |

**Verdict:** the intake is fine and privacy-clean; everything downstream of intake
does not exist. This spec keeps the intake shape (one field, works without JS,
no third-party script on the page) and builds the rest behind it.

---

## 2. Design decisions

### 2.1 Resend is the list of record; the server holds no list authority

Resend Segments already implement the parts that are expensive to get right:
hosted unsubscribe, a global `unsubscribed` flag, an account-level suppression list,
and `List-Unsubscribe` / one-click unsubscribe headers on broadcasts. Rebuilding
those in PHP is the wrong trade.

So: `.subscribers.jsonl` demotes from "source of truth" to **intake queue and audit
log**. Resend holds the sendable list.

### 2.2 The web server never gets a full-access API key

Resend's Contacts API needs a full-access key. The DO box is a shared WordOps host
running a public form — a full-access mail key there can send as the domain *and*
read/modify the entire contact list. Don't put it there.

**Split:**

| Key | Lives | Scope | Used by |
|---|---|---|---|
| `RESEND_SENDING_KEY` | DO server env (php-fpm pool), alongside `CHEATSHEET_NOTIFY_EMAIL` | **Sending access only** | `subscribe.php` — sends the one confirmation email |
| `RESEND_API_KEY` | `~/Projects/.resend.env` on the Windows box (already there) | Full access | The monthly routine — syncs contacts, creates the draft broadcast |

Contacts flow **one way**: server intake queue → (SSH pull by the routine) → Resend.
Unsubscribes and bounces stay entirely inside Resend and are never mirrored back to
the server. The server therefore has no reason to hold contact-write access.

*Alternative, only if the SSH pull proves annoying:* let `subscribe.php` write contacts
directly with a full-access key. Simpler, one fewer moving part, materially worse
blast radius. Not recommended.

### 2.3 Double opt-in, stateless

A public form with only a honeypot will collect typo'd addresses and spam-trap
injections, and a poisoned list is close to unrecoverable for a domain's reputation.
Confirm before a contact ever reaches Resend.

Stateless HMAC token — no database, no session, nothing to expire on a cron:

```
payload = base64url(email) . "." . issued_unix_ts
sig     = base64url( hmac_sha256(payload, NEWSLETTER_TOKEN_SECRET) )
link    = https://cheatsheets.davidveksler.com/confirm.php?p=<payload>&s=<sig>
```

- `NEWSLETTER_TOKEN_SECRET`: 32+ random bytes, server env only, never in the repo.
- Verify with `hash_equals()` (constant time). Reject if `now - issued_ts > 7 days`.
- `confirm.php` appends the address to `.confirmed.jsonl` and shows a confirmation page.
- Re-confirming an already-confirmed address is a no-op that still shows success.

### 2.4 Sending subdomain, not the apex

Send from **`updates.cheatsheets.davidveksler.com`**. Resend recommends a dedicated
subdomain so newsletter reputation is isolated from anything else `davidveksler.com`
ever sends, and it keeps a bad month from contaminating the rest of the fleet.

From address: `Cheatsheets <hello@updates.cheatsheets.davidveksler.com>`, `reply_to`
a real inbox David reads (replies to a newsletter are the highest-signal feedback
this site can get — do not use a no-reply).

### 2.5 The routine drafts; David sends

Per the global rule (*routines never send*), the monthly routine ends by creating a
**draft** broadcast and committing the archive page. Sending is a separate, explicit,
human-run command — the same shape as `deploy.sh`. Autonomy tier: **draft**, and it
stays there.

---

## 3. Architecture

```
                          ┌─── browser ───┐
  index.php form  ───POST──▶  subscribe.php
  how-its-built.html        │   ├─ validate + honeypot
  newsletter.php            │   ├─ append .subscribers.jsonl   (intake queue)
                            │   └─ Resend /emails ─▶ confirmation email
                            │                            │
                            ◀────── click token ─────────┘
                              confirm.php
                                └─ append .confirmed.jsonl    (sendable queue)

  ── monthly, on the Windows box (Claude routine) ──────────────────────
  scripts/newsletter_digest.py     git log + popularity.json + page meta
        │                          → newsletter/digest-YYYY-MM.json
        ▼
  Claude routine writes copy → newsletter/YYYY-MM.html  (archive page)
        │                    → newsletter/YYYY-MM.email.html (table-layout email)
        ▼
  scripts/newsletter_sync.py     ssh pull .confirmed.jsonl → Resend contacts
  scripts/newsletter_broadcast.py  POST /broadcasts  (draft, send:false)
        ▼
  ── human gate ──  scripts/newsletter_send.py --issue YYYY-MM --yes
```

### 3.1 Files

**New**

| Path | What |
|---|---|
| `lib/resend.php` | ~80-line cURL client: `sendEmail()` only. No dependencies, no Composer. |
| `lib/newsletter.php` | Token mint/verify, queue append helpers, shared by `subscribe.php` and `confirm.php`. |
| `confirm.php` | Double opt-in endpoint. |
| `newsletter.php` | Public archive index + signup. Also the "read a past issue" landing page. |
| `newsletter/YYYY-MM.html` | One archive page per issue (full metadata, passes the SEO gate). |
| `newsletter/YYYY-MM.email.html` | Email-safe HTML for the same issue. Not served. |
| `newsletter/digest-YYYY-MM.json` | Deterministic raw material for the issue. Committed (it is the audit trail). |
| `newsletter/broadcast-YYYY-MM.json` | `{issue, broadcast_id, segment_id, subject, created, sent, sent_at?}` — written by `newsletter_broadcast.py`, updated in place by `newsletter_send.py`. Committed; it's the record of when (or whether) an issue actually sent. |
| `scripts/newsletter_common.py` | Shared: `.resend.env` loader, minimal stdlib `resend_request()`, `newsletter_dir()`. |
| `scripts/newsletter_digest.py` | Builds the digest JSON. Stdlib + the repo's existing bs4 (reuses `generate-metadata.py`'s extraction by import, not duplication). No LLM. |
| `scripts/newsletter_sync.py` | SSH-pulls `.confirmed.jsonl`, upserts Resend contacts, reports deltas. Add-only — never unsubscribes or deletes. |
| `scripts/newsletter_broadcast.py` | Creates the **draft** broadcast (`send` left at its default `false`; no `--send` flag exists on this script). Writes `newsletter/broadcast-<issue>.json` as the audit/handoff record for `newsletter_send.py`. |
| `scripts/newsletter_send.py` | The human gate: preflight → preview → `[y/N]` → send → verify. Not run by the routine. |
| `.claude/skills/cheatsheets-newsletter-monthly/SKILL.md` | The routine. |

**Modified**

| Path | Change |
|---|---|
| `subscribe.php` | Mint token, send confirmation via Resend, keep the jsonl append and the owner notification. Response copy changes to "check your inbox". |
| `index.php` | Signup copy → monthly + archive link; footer link to `newsletter.php`. |
| `how-its-built.html` | Same copy change. |
| `sitemap.php` | Scans root only (`scandir('.')` + `is_file`). Add a second pass over `newsletter/*.html` at priority `0.5`. |
| `AGENTS.md` | Doc-routing row; replace the **Email signup endpoint** section with a pointer here. |
| `docs/marketing.md` | Newsletter as a promotion channel + its KPIs. |
| `.gitignore` | Add `/.confirmed.jsonl`. |

`index.php` and `sitemap.php` both scan the repo root and skip non-files, so a
`newsletter/` **directory** is invisible to them by default — that is why the sitemap
needs an explicit second pass and why archive pages must not live in the root (they
would show up as cheatsheet cards).

---

## 4. Resend API contract

Verified against Resend docs, 2026-08-23. Resend renamed **Audiences → Segments** in
early 2026; `audience_id` still works as a deprecated alias. Use `segment_id`.

| Operation | Call |
|---|---|
| Send confirmation email | `POST https://api.resend.com/emails` |
| Create contact | `POST /contacts` — `email`, optional `first_name`, `last_name`, `unsubscribed`, `properties`, `segments[]`, `topics[]` |
| List contacts | `GET /contacts` (optionally scoped by `segment_id`) |
| Create broadcast | `POST /broadcasts` — required `segment_id`, `from`, `subject`; optional `reply_to`, `html`, `text`, `name`, `send` (default `false`), `scheduled_at`, `topic_id` |
| Send broadcast | `POST /broadcasts/{id}/send` — optional `scheduled_at` (ISO 8601 or natural language) |

Auth: `Authorization: Bearer <key>`.

**Merge tags** (broadcasts only): `{{{RESEND_UNSUBSCRIBE_URL}}}` for the unsubscribe
link, `{{{contact.first_name|there}}}` with a fallback. This list does not collect
names, so personalization is out of scope for v1.

**Constraint to check before the first send over 100 recipients:** the Free plan is
capped at 3,000 emails/month and **100 emails/day**; marketing plans are billed by
contacts (Free = 1,000 contacts) and documented as *not* limited by emails sent. Whether
a broadcast counts against the transactional daily cap is not stated clearly enough to
rely on. Verify with a test broadcast to a small segment, or upgrade to Pro ($20/mo,
50K emails) before crossing 100 subscribers. Do not discover this mid-send.

---

## 5. DNS and deliverability (Phase 0 — blocking)

**Done (2026-08-24).** Domain `updates.cheatsheets.davidveksler.com` created in Resend
(id `ede06e7b-8a45-4eb0-bef7-c70682bdf020`, region `us-east-1`) and all four records
added to the `davidveksler.com` Cloudflare zone (id `3d96473d69977c5c828b3079d9b9869c`)
via the API, **proxy off (DNS only)** on every one, confirmed resolving from two
independent public resolvers (Cloudflare DoH, Google DoH):

| Name | Type | Value | Status |
|---|---|---|---|
| `send.updates.cheatsheets` | MX | `feedback-smtp.us-east-1.amazonses.com`, priority 10 | Live, resolving |
| `send.updates.cheatsheets` | TXT | `v=spf1 include:amazonses.com ~all` | Live, resolving |
| `resend._domainkey.updates.cheatsheets` | TXT | DKIM public key (see the domain object in Resend) | Live, resolving |
| `_dmarc.updates.cheatsheets` | TXT | `v=DMARC1; p=none;` | Live, resolving — **no `rua=` yet**, see below |

**Still open:**
- Resend's own verification check was still `pending` (not yet flipped to `verified`)
  as of the DNS work above, despite all three of its required records resolving
  correctly — that's normal, Resend polls asynchronously. Check status with
  `GET /domains/ede06e7b-8a45-4eb0-bef7-c70682bdf020` (or the dashboard) before relying
  on this domain to send; do not assume verified without checking.
- The DMARC record was added at the safe default `p=none` with **no `rua=` monitoring
  address** — open question #2 in §10 (reply-to inbox) needs an answer first. Once
  there's an inbox to point it at, update the TXT record to
  `v=DMARC1; p=none; rua=mailto:<address>`, and move to `p=quarantine` after a month
  of clean reports.
- The `davidveksler.com` root domain was already a verified Resend domain before this
  work (used for something else in the fleet) — unrelated to this subdomain, no
  conflict, just noted for context.

DMARC is not required for Resend verification but **is** required by Gmail/Yahoo bulk
sender rules, along with SPF+DKIM alignment, one-click unsubscribe, and keeping the
spam complaint rate under 0.3%. Resend supplies the unsubscribe headers on broadcasts;
the rest is on this table.

**Also blocking:** CAN-SPAM requires a valid physical postal address in every
commercial email. A PO box is fine. There is no way to ship without one — see §10.

---

## 6. Content model

The issue is computed first, written second. `scripts/newsletter_digest.py` produces:

```json
{
  "issue": "2026-09",
  "window": { "from": "2026-08-01", "to": "2026-08-31" },
  "new": [
    { "file": "ham-radio-technician.html", "title": "...", "description": "...",
      "og_image": "images/ham-radio-technician.png", "added": "2026-08-23",
      "commit": "c118ba1", "category": "Radio" }
  ],
  "updated": [
    { "file": "capitalism.html", "title": "...", "lines_changed": 214,
      "commits": ["006c0a6"], "summary_hint": "Removed broken links" }
  ],
  "popular": [ { "file": "ai-frontier.html", "title": "...", "daily_views": 204 } ],
  "stats": { "total_pages": 181, "commits_in_window": 37 }
}
```

Sources, all already in the repo:

- **New pages** — `git log --since=<from> --diff-filter=A --name-only -- '*.html'`
- **Updated pages** — `git log --since=<from> --diff-filter=M --numstat -- '*.html'`,
  **threshold ≥ 50 changed lines** so the weekly freshness job's date-stamp commits
  do not fill the issue with noise.
- **Popular** — `popularity.json` → `dailyViews`, top 5, excluding anything already
  listed under *new*.
- **Titles / descriptions / images** — same extraction as `generate-metadata.py`.
- **Category** — `category-map.php`.

### Issue structure

| Section | Length | Source |
|---|---|---|
| Intro | 2–3 sentences | Written. The only genuinely generative part. |
| New this month | 3–8 items | `digest.new` |
| Substantially updated | 0–5 items | `digest.updated` |
| Most-read | top 5 | `digest.popular` |
| From the pipeline | one short note | What changed in the system itself — ties to `how-its-built.html` |
| Footer | — | Unsubscribe merge tag, archive link, postal address |

**Skip rule:** if `len(new) + len(updated) < 3`, the routine reports "no issue this
month" and exits without drafting. An empty newsletter costs more than a missed one.

**Voice:** David-voice per the global standard — no em dashes, no unverifiable claims,
no "we're excited to". Every item's one-liner must say what the page is *for*, not that
it exists.

**UTM on every link:**
`?utm_source=newsletter&utm_medium=email&utm_campaign=cheatsheets_monthly&utm_content=YYYY-MM`

---

## 7. Email HTML rules (the site's design guidance does not apply)

Email clients are a 2005 rendering target. Nothing from AGENTS.md's Modern Platform
Baseline survives — no `light-dark()`, no Grid, no container queries, no `@layer`,
no `<details>`, no external CSS, no CDN anything.

- Single-column **table** layout, max 600px, centered.
- **All CSS inline** on the elements. One `<style>` block only for `@media` and
  `prefers-color-scheme`, and treat both as progressive enhancement.
- `<meta name="color-scheme" content="light dark">` + `supported-color-schemes`.
  Do not rely on dark-mode CSS; pick colors that survive Outlook and Gmail inverting them.
- Images: absolute `https://` URLs, explicit `width`/`height`, meaningful `alt`
  (many clients block images by default — the email must read fine with none loaded).
- Always ship a **plain-text alternative**. Resend auto-generates one from `html`;
  write it explicitly instead so the link list is readable.
- No web fonts, no JS, no background images, no `position`.
- Target under 102 KB of HTML — Gmail clips above that and hides the unsubscribe link.
- Test before the first send: Gmail web + iOS Mail + Outlook web, light and dark.

The `newsletter/YYYY-MM.html` **archive** page is a normal site page and follows the
usual site rules and SEO gate. The two files share content, not markup.

---

## 8. The routine

`.claude/skills/cheatsheets-newsletter-monthly/SKILL.md`

- **Name:** `cheatsheets-newsletter-monthly` · **Schedule:** 1st of the month, 03:00
  local · **Tier:** draft · **Model:** default
- **Runbook-backed:** this file wins on any disagreement.

**Steps**

1. `python scripts/newsletter_digest.py --issue YYYY-MM` → digest JSON.
2. If under the skip threshold: report, commit nothing, exit 0.
3. Write `newsletter/YYYY-MM.html` (archive) and `newsletter/YYYY-MM.email.html`.
4. `python scripts/seo_check.py newsletter/YYYY-MM.html` — must pass.
5. `python scripts/newsletter_sync.py` — pull confirmed addresses, upsert contacts,
   report `+N new, M total`.
6. `python scripts/newsletter_broadcast.py --issue YYYY-MM` → draft broadcast, print
   its id and dashboard URL.
7. Commit and push. Report: item counts, subscriber delta, broadcast id, one-line
   diff summary.

**Hard limits**

- **Never send.** No `POST /broadcasts/{id}/send`, no `send: true`, no `scheduled_at`.
- Never deploy. Never delete or unsubscribe a contact.
- Never invent an item that is not in the digest JSON — the digest is the only
  admissible source of facts about what shipped.
- Max one issue per run, max one draft broadcast per run.
- Fail closed: on any anomaly (digest empty, SEO gate fails, sync delta negative,
  Resend non-2xx) change nothing further, report, exit.
- ntfy only on failure or on a subscriber delta above ±20.

**Then David:** reviews the draft in the Resend dashboard, and sends with

```bash
python scripts/newsletter_send.py --issue 2026-09
```

which reprints the recipient count and subject, prompts `[y/N]`, sends, then verifies
the broadcast status. Deploying the archive page stays on the normal `./deploy.sh` gate.

---

## 9. Phasing

| Phase | Scope | Done when | Status |
|---|---|---|---|
| **0. Prerequisites** | Verify `updates.` subdomain in Resend, four DNS records, two API keys, `NEWSLETTER_TOKEN_SECRET` + `RESEND_SENDING_KEY` in the php-fpm env, postal address chosen, a Resend segment created (its id goes in `RESEND_SEGMENT_ID`) | A test email from Resend passes SPF+DKIM+DMARC at `mail-tester.com` (aim ≥ 9/10) | **In progress** — domain created + all 4 DNS records live (§5, 2026-08-24); still open: Resend verification flipping to `verified`, `RESEND_SENDING_KEY`, `NEWSLETTER_TOKEN_SECRET`, `RESEND_SEGMENT_ID`, postal address, DMARC `rua=` (§10) |
| **1. Intake** | `lib/resend.php`, `lib/newsletter.php`, `subscribe.php` changes, `confirm.php` | A real signup produces a confirmation email whose link flips the address into `.confirmed.jsonl`, with and without JS | **Code complete**, unverified live (needs Phase 0) |
| **2. Pipeline** | `scripts/newsletter_digest.py`, `newsletter_sync.py`, `newsletter_broadcast.py`, `newsletter_send.py`, the `cheatsheets-newsletter-monthly` routine | A draft broadcast for the current month exists in Resend, built only from digest facts | **Code complete** — digest verified against real repo history (2026-09 issue: 8 new, 8 updated, 5 popular); sync/broadcast/send verified for error paths only, live Resend calls untested (needs Phase 0 credentials) |
| **3. Archive + conversion** | `newsletter.php`, archive pages, sitemap pass, signup copy | `newsletter.php` lists past issues and ranks for its own title; signup copy matches reality | Not started |
| **4. Hardening** | Turnstile on the form, `resend-webhook.php` for `email.bounced` / `email.complained` / `suppression.added`, suppression reconciliation into the intake queue | Complaint and bounce events are recorded and reconciled without manual work | Not started |

Phases 1–2 are the minimum shippable newsletter, and their code is now in the repo.
`newsletter_sync.py`'s contact-dedup logic in particular should be watched by hand on
its first live run — Resend's public docs don't clearly state POST /contacts' behavior
on an email that's already a contact elsewhere in the Global Contacts model (checked
2026-08-23), so the script defends with a list-then-create pattern rather than assuming.
Phase 3 is where the compounding is (an indexable archive is both a conversion page and
an AI-answer-engine surface). Phase 4 waits for evidence of abuse or bounce volume.

---

## 10. Blockers and open questions

**Blocking — needed before Phase 0 can finish:**

1. **Postal address for the email footer.** Legally required. Home address, PO box,
   or a registered agent — David's call, and there is no shipping without it.
2. **Reply-to inbox.** Which address should replies land in?

**Decisions worth making now:**

3. **Cadence.** Spec assumes monthly. Weekly would need ~3 new pages/week to stay
   honest; the repo produces closer to that in a good month.
4. **Segment topology.** One `confirmed` segment, or split by interest (AI / martial
   arts / finance / prepping)? The corpus spans wildly different audiences and a
   single list guarantees most of every issue is irrelevant to most readers. Topics
   would let readers self-select. Costs a preference page; probably worth it by issue 3.
5. **Existing `.subscribers.jsonl` addresses.** Anyone already in the file signed up
   under the old copy and never confirmed. Recommended: send them a single one-time
   re-permission email through the double opt-in flow, and drop everyone who does not
   confirm. Importing them silently is the fastest route to a complaint rate that
   costs the domain its reputation. Check how many addresses are actually in there on
   the server before deciding — it may be a handful.
6. **Plan tier.** Free until the daily-cap question in §4 is settled or the list
   crosses 100.

---

## 11. Measurement

Append to [`seo-progress.md`](seo-progress.md) monthly alongside the GSC/Cloudflare pull.

| Metric | Target | Hard floor |
|---|---|---|
| Confirm rate (confirmed / submitted) | ≥ 60% | < 40% means the confirmation email is landing in spam |
| Open rate | ≥ 40% | Opt-in niche technical list; below 25% means subject lines or relevance |
| Click rate | ≥ 8% | Below 4% means the item one-liners are not doing their job |
| Unsubscribe rate | < 0.5% | > 2% on an issue means that issue missed |
| Complaint rate | < 0.1% | **> 0.3% and Gmail starts filtering — stop sending and diagnose** |
| Bounce rate | < 2% | > 5% means the list needs cleaning |
| Newsletter → site sessions | tracked via UTM in Cloudflare | — |

Open and click rates require tracking pixels/link rewriting, which Resend can enable
per-domain. That is a deliberate trade against the site's current no-tracking stance:
the site itself stays script-free either way, but the *email* would carry a pixel.
If David prefers to keep the no-tracking promise end to end, disable open/click
tracking and measure with UTM-attributed sessions only — the metrics table above
then collapses to confirm rate, unsubscribe, complaint, bounce, and sessions.

---

## 12. Rejected alternatives

| Option | Why not |
|---|---|
| Keep PHP `mail()` and send from the DO box | Unauthenticated bulk mail from a shared WordOps host. No DKIM alignment, no unsubscribe infrastructure, no bounce handling. Would land in spam and take the domain's reputation with it. |
| Buttondown / Kit / MailerLite | Fine products, but they own the list and the templates. This repo's whole thesis is that the pipeline is in git and auditable. Resend is an API, which keeps the issue in the repo and the send in a script. |
| Full-access Resend key on the web server | One public form away from full contact-list access. §2.2. |
| Single opt-in | A honeypot-only public form on an indexed site collects traps. One poisoned list is worse than every subscriber the confirmation step costs. |
| Archive pages in the repo root | `index.php` and `sitemap.php` scan the root for `*.html` — they would render as cheatsheet cards and dilute the corpus. |
| Routine sends autonomously | Violates the standing never-send rule, and an email is the one artifact here that cannot be rolled back. |
