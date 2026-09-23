# Newsletter: spec and runbook

**Status: not sending.** Phases 1-2 code complete; Phase 0 partly done (§9). Provider: [Resend](https://resend.com). Section numbers are cited by `scripts/newsletter_*.py` and the routine skill; keep them stable.

A monthly issue computed from git history + `popularity.json`, not written from scratch. Signup forms: `index.php`, `how-its-built.html` (one field + `website` honeypot, no JS dependency, no third-party script).

## 1. Current state

| Piece | State |
|---|---|
| Intake | `subscribe.php` → `.subscribers.jsonl` (gitignored intake queue + audit log), sends confirmation via Resend, optional owner notice to `CHEATSHEET_NOTIFY_EMAIL` |
| Confirm | `confirm.php` → `.confirmed.jsonl` (sendable queue) |
| List of record | Resend segment (hosted unsubscribe, suppression, `List-Unsubscribe`) |
| Server secrets | `.newsletter.env` next to the code (gitignored, `chmod 600`), loaded by `lib/env.php`; template `.newsletter.env.example`. Real env vars win. No php-fpm pool env: the site shares WordOps' `www` pool, so pool env would leak to other sites. |

## 2. Binding decisions

### 2.1 Resend holds the list
Server files are intake queue and audit log only; Resend holds the sendable list and handles unsubscribes/suppression.

### 2.2 Key split
| Key | Lives | Scope | Used by |
|---|---|---|---|
| `RESEND_SENDING_KEY` | server `.newsletter.env` | Sending only, restricted to `updates.cheatsheets.davidveksler.com` | `subscribe.php` confirmation email |
| `RESEND_API_KEY` | `~/Projects/.resend.env` (Windows box) | Full access | Monthly routine: contact sync, draft broadcast |

Contacts flow one way: server queue → SSH pull by the routine → Resend. Unsubscribes/bounces stay in Resend. Never put a full-access key on the web server.

### 2.3 Double opt-in, stateless HMAC
```
payload = base64url(email) . "." . issued_unix_ts
sig     = base64url( hmac_sha256(payload, NEWSLETTER_TOKEN_SECRET) )
link    = https://cheatsheets.davidveksler.com/confirm.php?p=<payload>&s=<sig>
```
Secret: 32+ random bytes, server only. Verify with `hash_equals()`; reject if older than 7 days. Re-confirming is a no-op that shows success. Rotating the secret invalidates unclicked links.

### 2.4 Sending subdomain
From `Cheatsheets <hello@updates.cheatsheets.davidveksler.com>` (isolates reputation from `davidveksler.com`). `reply_to` is a real inbox David reads, never no-reply.

### 2.5 Routine drafts, David sends
Autonomy tier: draft, permanently.

## 3. Architecture

```
index.php / how-its-built.html form ─POST─▶ subscribe.php
    ├─ validate + honeypot → .subscribers.jsonl
    └─ Resend /emails → confirmation email ─click─▶ confirm.php → .confirmed.jsonl

monthly, Windows box (routine):
  scripts/newsletter_digest.py    git log + popularity.json + catalog.json → newsletter/digest-YYYY-MM.json
  routine writes                  newsletter/YYYY-MM.html (archive) + newsletter/YYYY-MM.email.html
  scripts/newsletter_sync.py      SSH pull .confirmed.jsonl → Resend contacts (add-only)
  scripts/newsletter_broadcast.py POST /broadcasts, draft (send:false; no --send flag)
                                  → newsletter/broadcast-YYYY-MM.json
human gate: scripts/newsletter_send.py --issue YYYY-MM   (preflight, preview, [y/N], send, verify)
```

| Path | Role |
|---|---|
| `lib/resend.php` | cURL client, `sendEmail()` only, no Composer |
| `lib/newsletter.php` | token mint/verify, queue helpers |
| `lib/env.php` | loads `.newsletter.env` |
| `scripts/newsletter_common.py` | `.resend.env` loader, stdlib `resend_request()`, `newsletter_dir()` |
| `newsletter/digest-YYYY-MM.json` | committed audit trail of issue facts |
| `newsletter/broadcast-YYYY-MM.json` | `{issue, broadcast_id, segment_id, subject, created, sent, sent_at?}`; record of whether an issue sent |
| `.claude/skills/cheatsheets-newsletter-monthly/SKILL.md` | the routine |

Archive pages live in `newsletter/`, never the root (root `.html` becomes a cheatsheet card). nginx (`conf/nginx/internal-paths.conf`) serves only `newsletter/YYYY-MM.html` from that folder; every other file there 404s.

## 4. Resend API

`segment_id` (Audiences were renamed Segments; `audience_id` is a deprecated alias). Auth `Authorization: Bearer <key>`.

| Operation | Call |
|---|---|
| Confirmation email | `POST https://api.resend.com/emails` |
| Create / list contacts | `POST /contacts` (`email`, `unsubscribed`, `segments[]`, ...) / `GET /contacts` |
| Create broadcast | `POST /broadcasts` (`segment_id`, `from`, `subject`; optional `reply_to`, `html`, `text`, `name`, `send`=false, `scheduled_at`, `topic_id`) |
| Send broadcast | `POST /broadcasts/{id}/send` |

Merge tags: `{{{RESEND_UNSUBSCRIBE_URL}}}`. No names collected, so no personalization.

**Before exceeding 100 recipients:** Free plan caps 100 emails/day, 3,000/month, 1,000 contacts; whether broadcasts count against the daily cap is unclear. Test with a small segment or upgrade to Pro ($20/mo) first. Watch `newsletter_sync.py` dedup by hand on its first live run (list-then-create; POST /contacts behavior on existing contacts is undocumented).

## 5. DNS and deliverability

Domain `updates.cheatsheets.davidveksler.com` in Resend (id `ede06e7b-8a45-4eb0-bef7-c70682bdf020`, `us-east-1`), verified. Records in the `davidveksler.com` Cloudflare zone (`3d96473d69977c5c828b3079d9b9869c`), all DNS-only (unproxied):

| Name | Type | Value |
|---|---|---|
| `send.updates.cheatsheets` | MX | `feedback-smtp.us-east-1.amazonses.com`, priority 10 |
| `send.updates.cheatsheets` | TXT | `v=spf1 include:amazonses.com ~all` |
| `resend._domainkey.updates.cheatsheets` | TXT | DKIM key (see Resend domain object) |
| `_dmarc.updates.cheatsheets` | TXT | `v=DMARC1; p=none;` (no `rua=` yet) |

Gmail/Yahoo bulk rules: SPF+DKIM alignment, DMARC, one-click unsubscribe, complaint rate < 0.3%. CAN-SPAM requires a physical postal address (PO box OK) in every email; no send without it.

## 6. Content model

`newsletter_digest.py --issue YYYY-MM` digests the prior month into `{issue, window, new[], updated[], popular[], stats}`:

- **New:** `git log --diff-filter=A` on `*.html` in window.
- **Updated:** `--diff-filter=M --numstat`, ≥ 50 changed lines (filters freshness noise).
- **Popular:** `popularity.json` `dailyViews` top 5, excluding new items.
- Titles/descriptions/images from `catalog.json`; category from `category-map.php`.

| Section | Length | Source |
|---|---|---|
| Intro | 2-3 sentences | written (the only generative part) |
| New this month | 3-8 | `digest.new` |
| Substantially updated | 0-5 | `digest.updated` |
| Most-read | 5 | `digest.popular` |
| From the pipeline | one note | system changes, tie to `how-its-built.html` |
| Footer | | unsubscribe tag, archive link, postal address |

**Skip rule:** `len(new) + len(updated) < 3` → no issue (digest exits 3). Voice: David-voice; each one-liner says what the page is *for*. UTM on every link: `?utm_source=newsletter&utm_medium=email&utm_campaign=cheatsheets_monthly&utm_content=YYYY-MM`.

## 7. Email HTML rules (site design rules do not apply)

- Single-column table layout, max 600px, centered; all CSS inline; one `<style>` only for `@media` / `prefers-color-scheme` as progressive enhancement.
- `<meta name="color-scheme" content="light dark">` + `supported-color-schemes`; colors must survive Outlook/Gmail inversion.
- Images: absolute `https://`, explicit `width`/`height`, meaningful `alt`; must read fine with images blocked.
- Always write an explicit plain-text alternative.
- No web fonts, JS, background images, `position`, `<details>`, `light-dark()`, Grid, CDN.
- HTML < 102 KB (Gmail clips and hides the unsubscribe link).
- Before first send test Gmail web, iOS Mail, Outlook web, light and dark.

The archive page `newsletter/YYYY-MM.html` is a normal site page (site rules + SEO gate).

## 8. The routine

`cheatsheets-newsletter-monthly`: 1st of month, 03:00 local, draft tier, default model. This file wins over its SKILL.md.

1. `python scripts/newsletter_digest.py --issue YYYY-MM`; exit 3 → report "no issue", commit nothing.
2. Write `newsletter/YYYY-MM.html` and `newsletter/YYYY-MM.email.html` from the digest only.
3. `python scripts/seo_check.py newsletter/YYYY-MM.html` must pass.
4. `python scripts/newsletter_sync.py` → report `+N new, M total`.
5. `python scripts/newsletter_broadcast.py --issue YYYY-MM` → draft id + dashboard URL.
6. Commit and push; report counts, subscriber delta, broadcast id.

**Hard limits:** never send (no `/send`, `send: true`, or `scheduled_at`); never deploy; never delete/unsubscribe a contact; no item absent from the digest; max one issue and one draft broadcast per run; fail closed on empty digest, SEO failure, negative sync delta, or Resend non-2xx; ntfy only on failure or subscriber delta beyond ±20.

**David then:** reviews the draft in Resend and runs `python scripts/newsletter_send.py --issue YYYY-MM`. The archive page ships via `./deploy.sh`.

## 9. Phasing

| Phase | Scope | Done when | Status |
|---|---|---|---|
| 0. Prerequisites | domain, DNS, keys, secrets, segment, postal address | test email passes SPF+DKIM+DMARC at mail-tester.com (≥ 9/10) | Domain verified, DNS live, sending key + token secret + "Cheatsheets Newsletter" audience created server-side (commit `fdbdad3`). **Open:** `RESEND_SEGMENT_ID` in `~/Projects/.resend.env` (absent), postal address, reply-to inbox, DMARC `rua=`, mail-tester run |
| 1. Intake | `lib/*.php`, `subscribe.php`, `confirm.php` | real signup → confirmation → `.confirmed.jsonl`, with and without JS | Code complete; live test [UNVERIFIED] |
| 2. Pipeline | digest/sync/broadcast/send scripts + routine | draft broadcast built only from digest facts | Code complete; digest verified on real history; live Resend calls untested |
| 3. Archive + conversion | `newsletter.php` archive index, archive pages, `sitemap.php` pass over `newsletter/*.html` (priority 0.5), signup copy → "monthly" + archive link | archive ranks for its own title; copy matches reality | Not started |
| 4. Hardening | Turnstile, `resend-webhook.php` (bounced/complained/suppression), reconciliation | events recorded without manual work | Not started; wait for abuse/bounce evidence |

Signup copy still says "Occasional email ... no tracking" (`index.php`, `how-its-built.html`); Phase 3 changes it.

## 10. Open questions

1. **Postal address** (blocking): home, PO box, or registered agent.
2. **Reply-to inbox** (blocking): then set DMARC `rua=mailto:<address>`; move to `p=quarantine` after a month of clean reports.
3. Cadence: monthly assumed.
4. Segments: one list vs interest topics (AI / martial arts / finance / prepping); topics probably worth it by issue 3.
5. Existing `.subscribers.jsonl` addresses never confirmed: send one re-permission email through double opt-in, drop non-confirmers; never import silently. Count them on the server first.
6. Plan tier: Free until the §4 daily-cap question is settled or the list passes 100.

## 11. Measurement

Append monthly to [`seo-progress.md`](seo-progress.md).

| Metric | Target | Floor |
|---|---|---|
| Confirm rate | ≥ 60% | < 40%: confirmation landing in spam |
| Open rate | ≥ 40% | < 25%: subjects/relevance |
| Click rate | ≥ 8% | < 4%: weak one-liners |
| Unsubscribe | < 0.5% | > 2% on an issue: issue missed |
| Complaint | < 0.1% | **> 0.3%: stop sending and diagnose** |
| Bounce | < 2% | > 5%: clean the list |
| Newsletter → site sessions | UTM in Cloudflare | |

Open/click tracking adds a pixel to the email (the site stays script-free). If David keeps no-tracking end to end, disable it and measure confirm, unsubscribe, complaint, bounce, and UTM sessions only.

## 12. Rejected alternatives

- PHP `mail()` from the DO box: unauthenticated, no DKIM/unsubscribe/bounces; lands in spam.
- Buttondown / Kit / MailerLite: they own list and templates; Resend keeps issues in git and sends in a script.
- Full-access Resend key on the web server (§2.2).
- Single opt-in: honeypot-only public forms collect spam traps.
- Archive pages in the repo root (§3).
- Routine sends autonomously: violates never-send; email can't be rolled back.
