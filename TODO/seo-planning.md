# SEO planning — cheatsheets.davidveksler.com

Placeholder working doc for ongoing SEO strategy. Not a spec for a single cheatsheet (see
`TODO/README.md` for that) — this is the durable planning surface for search-visibility work
across the whole site. Update in place; don't delete after one pass.

Data source: Google Search Console property `https://cheatsheets.davidveksler.com/`
(MCP tool `search-console`). Re-pull before trusting numbers below more than a few weeks old —
this doc is a snapshot, not a live dashboard.

## Ground rule: judge per site goal, not site-wide

Per memory `cheatsheets-site-goals`, pages serve four different goals (personal study, personal
brand/portfolio, agentic-automation case study, political advocacy). Only goal-3 (case study —
"organic traffic proves the approach works") and goal-4 (advocacy — reach/persuasion) pages
should be judged on search performance. Never recommend pruning or deprioritizing a page for low
search demand without first checking which goal it serves.

## Baseline snapshot — last 28 days (2026-06-12 to 2026-07-09)

### Top pages by clicks

| Page | Clicks | Impressions | CTR | Avg. position |
|---|---|---|---|---|
| ai-frontier.html | 123 | 42,978 | 0.29% | 10.2 |
| baofeng-uv5r-quick-ref.html | 62 | 1,323 | 4.69% | 7.4 |
| orbital-rockets-comparison.html | 44 | 11,713 | 0.38% | 10.4 |
| ashihara-karate.html | 24 | 1,981 | 1.21% | 8.6 |
| shabbat-services-cheatsheet.html | 22 | 449 | 4.90% | 8.6 |
| brazilian-jiu-jitsu.html | 17 | 409 | 4.16% | 14.2 |
| veterinary-diagnostics.html | 17 | 184 | 9.24% | 18.3 |
| operator-loadouts.html | 16 | 1,662 | 0.96% | 7.4 |
| martial-arts-cheatsheet.html | 10 | 6,510 | 0.15% | 7.0 |

Full pull: 25 pages, see raw GSC query for the rest.

### Top queries by clicks

| Query | Clicks | Impressions | CTR | Avg. position |
|---|---|---|---|---|
| frontier ai companies | 7 | 266 | 2.6% | 5.5 |
| baofeng uv-5r programming cheat sheet | 6 | 237 | 2.5% | 7.5 |
| frontier model providers | 5 | 81 | 6.2% | 3.1 |
| what are the current frontier ai models | 5 | 91 | 5.5% | 6.6 |
| list of frontier ai models | 4 | 156 | 2.6% | 4.7 |

The "frontier ai" query family (companies/models/labs/providers) dominates clicks — several
variants already rank position 3-8. `ai-frontier.html` is the site's clear traffic driver.

### Striking-distance opportunities (high impressions, low CTR, position 7-20)

These pages get real search visibility but a poor click-through rate relative to it — the
highest-leverage targets for on-page/title/meta work rather than new content:

- **ai-frontier.html** — 42,978 impressions, 0.29% CTR, position 10.2. Biggest single lever on
  the site: even a modest CTR lift at this impression volume outweighs most new-page work.
- **orbital-rockets-comparison.html** — 11,713 impressions, 0.38% CTR, position 10.4.
- **martial-arts-cheatsheet.html** — 6,510 impressions, 0.15% CTR, position 7.0. Position is
  already good; title/snippet is likely the problem, not ranking.
- **google-ai-studio-guide.html** — 2,337 impressions, 0.43% CTR, position 10.7.
- **compression-algorithms.html** — 1,545 impressions, 0.32% CTR, position 18.0.
- **tesla-products.html** — 1,961 impressions, 0.31% CTR, position 12.8.

## Full audit — 2026-07-09

A 180-day pull (2026-01-10 → 2026-07-08) plus a parsed metadata sweep of all 151 files superseded the
28-day snapshot above. See **[`seo-audit-2026-07-09.md`](seo-audit-2026-07-09.md)** for findings and
**[`seo-implementation-spec.md`](seo-implementation-spec.md)** for the executable spec.

Headline conclusions (do not re-derive these; re-pull data instead):

1. **Two different causes of low CTR, only one fixable.** A large share of impressions are absorbed by
   AI Overviews / SERP features — e.g. `judo.html` earned 17,854 impressions and **2 clicks** on the
   single query "judo guide" at position 7.0. Do not set a site-wide CTR target; it will drown the
   signal from work that does matter.
2. **The fixable cause is the listing itself.** 82/151 titles exceed 60 chars (truncated); 52
   descriptions exceed 200. Worse, titles don't contain the words users type — `ai-frontier.html`
   (47% of all site clicks) ranks 2.4–6.0 for "frontier ai **companies**/**labs**/**list**", none of
   which appear in its title.
3. **Metadata hygiene is better than it looks.** Canonical, og:image, and twitter:card coverage is
   100%. The genuine gaps are 21 pages with no JSON-LD and 3 `<h1>` defects.

⚠️ **Methodology warning.** A first pass using naïve regexes reported ~67 pages missing
description/canonical/og:image and 5 with invalid JSON-LD. **All were false positives:** these files
use reversed attribute order (`content="…" name="description"`), several carry multiple `ld+json`
blocks, and inline **SVG `<title>`** elements pollute a naïve `<title>` match. Always parse the
`<head>` with a real HTML parser and validate each `ld+json` block independently. The acceptance-gate
script in the implementation spec does both — reuse it rather than writing a fresh regex.

## Open questions / next steps

- [x] ~~Diagnose why `ai-frontier.html` CTR is so low despite good position~~ → title omits the query
  nouns (*companies*, *labs*, *list*); rewrite specced in WP1.
- [x] ~~Pull a longer window (90/180 days) for trend direction~~ → 180-day pull done 2026-07-09.
- [x] ~~Cross-reference striking-distance pages against metadata checks~~ → done; it's metadata, not
  content depth.
- [x] **Decision (2026-07-10):** leave `anduril-products.html` as a 404; do not return `410 Gone` and
  do not redirect it. It was deliberately removed for trademark exposure.
- [ ] **David's decision:** cannibalization — `versioncontrol.html` vs `git-scm.html`.
  **Update 2026-07-12, fresh 28-day data:** the overlap has largely self-resolved.
  `versioncontrol.html` collapsed to **12 impressions / 6 queries**, all Mercurial/DVCS-comparison
  intent (`mercurial dvcs`, hosting-platform comparisons) — the 4,904-impression figure was an
  artifact of the 180-day window. `git-scm.html` now owns the git intent but ranks **50–70** for
  the big-head queries (`git commands`, `git cheat sheet` — dominated by github.com's official PDF;
  realistically unwinnable) while winning real clicks at position 10–16 on
  `git cheat sheet interactive` / `interactive git cheat sheet` (3 clicks, 27% CTR on the former).
  **Recommendation: leave both; do not consolidate.** They no longer compete on the same queries.
  If anything, lean `git-scm.html` further into the "interactive" differentiator it already wins on.
- [ ] Contextual internal linking pass (`SEO_PROMPT.txt` footer procedure). Deferred until the
  metadata pass is measured. Flagship `ai-frontier.html` has only 5 inbound contextual links.
- [ ] `list_sitemaps` MCP call currently **errors** (`cannot unmarshal string into … warnings of type
  int64`) — an MCP-server bug, not a sitemap problem. Check coverage via the GSC web UI instead.

## Follow-ups left open by the 2026-07-09 metadata pass

All five closed as of the 2026-07-12 sweep (most were fixed by concurrent sessions between 07-10
and 07-12; verified rather than assumed):

- [x] ~~`humanoid-robots.html` visible/title incoherence~~ → verified 2026-07-12: `<title>`,
  `<h1>`, and JSON-LD `headline` now all read "Humanoid Robots 2026: Every Company, Robot and Spec
  Compared". `ai-frontier.html` likewise fully coherent.
- [x] ~~7 pages with stale JSON-LD `headline`~~ → fixed 2026-07-12. An interim fix had synced
  `headline` to `<title>`, which is exactly what the spec's corrected rule 3 forbids; realigned all
  7 to the visible `<h1>` (`audit-odds`, `baofeng-uv5r-ham-guide`, `baofeng-uv5r-quick-ref`,
  `engineering-metals-selection`, `future-of-warfare-technology`, `samsung-bespoke-oven-guide`,
  `the-cliff-map`).
- [x] ~~`javascript-for-architects.html` unescaped HTML in code samples~~ → verified 2026-07-12:
  no raw non-`code`/`span`/`br` tags remain inside any `<pre>` block.
- [x] ~~`human-skeleton.html` stub body content~~ → verified 2026-07-12: `anatomicalData` now
  carries real axial/appendicular study content; no "Further details would describe" stubs remain.
- [x] ~~`autonomous-defense-systems.html` over-long metadata~~ → verified 2026-07-12: title 60
  chars, description 186; passes the acceptance gate.

**Corpus status 2026-07-12: the acceptance-gate script reports 0 failures across all root HTML
files** (titles ≤60, descriptions 150–200, canonical, valid JSON-LD). Metadata hygiene is done;
remaining SEO leverage is in content, ranking, and the AI-citability layer — not tags.

## AI distribution — baseline (2026-07-11)

Context for the July 2026 strategic pivot: the site continues as a **niche-reference +
AI-citability play**, not a broad-SEO traffic play. This section is the baseline for judging
whether AI-mediated distribution is material. Sources: Cloudflare GraphQL analytics
(zone `davidveksler.com`, host-filtered to `cheatsheets.davidveksler.com`) and GA4 property
543339529. Re-pull with the same method at each checkpoint.

### (a) AI crawler / agent traffic — Cloudflare, 7 days (2026-07-04 → 2026-07-10)

⚠️ **Window caveat:** the Cloudflare free plan caps `httpRequestsAdaptiveGroups` history at
~8 days, so a 90-day crawler pull is not possible — this baseline is a 7-day window. Treat it
as a weekly run-rate (~1,500 AI requests/day) and compare like-for-like windows at checkpoints.

| User agent | Requests (7d) | What it is |
|---|---|---|
| ChatGPT-User | 6,945 | Live page fetches on behalf of ChatGPT users answering questions |
| Bytespider | 1,184 | ByteDance trainer (mostly `/cdn-cgi/*` + `history.php` noise) |
| GoogleOther | 620 | Google non-search crawler (mostly `history.php` + `/cdn-cgi/*`) |
| Amazonbot | 600 | Amazon/Alexa (mostly `history.php`) |
| PerplexityBot | 341 | Perplexity indexer |
| Applebot | 278 | Apple/Siri (mostly `/cdn-cgi/*`) |
| OAI-SearchBot | 186 | ChatGPT Search indexer |
| ClaudeBot | 135 | Anthropic trainer/indexer |
| GPTBot | 102 | OpenAI trainer |
| DuckAssistBot | 65 | DuckDuckGo AI |
| Claude-User | 63 | Live fetches on behalf of Claude users |
| meta-externalagent / MistralAI / CCBot | 54 | Minor trainers |
| **Total** | **10,573** | ≈ 1,510/day |

Top pages fetched by ChatGPT-User: `ai-frontier.html` (1,638), `humanoid-robots.html` (609),
`/` (590), `boom-supersonic.html` (454), `bitcoin-whitepaper.html` (444),
`orbital-rockets-comparison.html` (346). PerplexityBot's top real page is also
`ai-frontier.html` (116).

### (b) AI referral traffic — GA4, 90 days (2026-04-12 → 2026-07-10)

| Source | Sessions | Landing pages |
|---|---|---|
| chatgpt.com | 4 | anduril-products (2, now 404), bitcoin-wallet, orbital-rockets-comparison |
| gemini.google.com | 3 | geoengineering-approaches, google-ai-studio-guide, judo |
| perplexity.ai / claude.ai / copilot | 0 | — |
| **Total AI referrals** | **7** | ≈ 0.5% of 1,537 total sessions |

Site context, same 90 days: Direct 909, Organic Search 437, Organic Social 173, Referral 11,
AI Assistant 7.

### Interpretation

AI systems consume this site heavily but send almost no clicks: **~7,000 ChatGPT-User fetches
in a week vs. 4 chatgpt.com referral sessions in a quarter.** The content is being read into
answers, not linked from them. That is the citability play working at the consumption layer
and invisible at the referral layer — so judge future checkpoints on *both* crawler run-rate
(is AI demand growing?) and referrals (is any of it attributable?), and never on referrals
alone. `ai-frontier.html` is the #1 target for both Google searchers and AI agents.

Action taken 2026-07-11: `/llms.txt` already existed (shipped 2026-07-09 as metadata-pass WP6,
full categorized index). Restructured it to lead with a curated "Strongest pages" section — the
~22 pages with demonstrated search/AI demand — per [llmstxt.org](https://llmstxt.org/)'s
curated-core convention, keeping the full index below. Redeployed.

## Measurement plan

Re-pull **2026-08-06** (28 days after the metadata pass lands), same 180-day window for comparability.

- **Primary metric:** clicks on the 16 WP1 pages, before vs. after, at roughly constant position.
- **Guard-rail:** average position on those pages must not fall. A rewritten title that drops position
  lost relevance — revert that one page.
- **Do not** use site-wide CTR as the metric (see conclusion 1).
- **Added 2026-07-11:** also re-pull the AI-distribution numbers with the same method as the
  baseline above — Cloudflare AI-crawler UAs (7-day window, host-filtered) and GA4 AI referral
  sessions (90-day window, sources chatgpt.com / perplexity.ai / claude.ai / gemini.google.com /
  copilot) — and compare against the 2026-07-11 baseline (~10,573 crawler requests/7d;
  7 referral sessions/90d).
- `ai-frontier.html` is measured as its own new baseline from **2026-07-10** (see "Measurement
  adjustment" below), not as part of the WP1-page comparison.
- **Added 2026-07-12:** `boom-supersonic.html` is measured as its own baseline from **2026-07-12**
  (query-aligned title/description rewrite; outside the WP1 set, so it does not confound the WP1
  comparison). Pre-change 28 days: 2 clicks / 2,098 impressions / position 9.4; query family is
  "boom overture range / speed mach 1.7 / timeline" at positions 8–10. Judge clicks and CTR on
  that family at roughly constant position.

## Decision checkpoint — verdict (run on or after 2026-08-06)

Fill this in when the checkpoint runs; the decision rule is fixed now so the August pull is
judged against pre-registered criteria, not vibes.

- **Continue investing** if WP1-page clicks improved at roughly constant position, **and/or**
  AI citation traffic is material (crawler run-rate clearly above the ~1,500/day baseline, or
  AI referrals growing beyond single digits per quarter).
- **Downshift to pure maintenance** if both are flat-to-down: no new pages except
  personal-study ones; freshness job and existing pages stay. **Do not delete or prune
  anything** — per the site-goals ground rule, non-goal-3 pages are not judged on traffic.

**Verdict (pending):** _to be written at the checkpoint._

A one-time scheduled task (`cheatsheets-pivot-checkpoint`, Claude scheduled-tasks, fires
2026-08-06 09:00 local) runs this checkpoint automatically: GSC re-pull, AI-distribution
re-pull, verdict written here, committed but not pushed.

## AI frontier implementation — 2026-07-10

Implemented the strategic-page changes following the competitor/GSC review:

- Replaced the unprovable “Complete List” promise with a query-aligned, scoped title and visible H1.
- Rebuilt the quick-reference map around model posture, access, strategy, and first use; removed unstable cross-company valuation figures from the comparison table.
- Added an explicit scope/method statement, official-source links for every profiled lab, and a visible update policy. The table is a curated seven-lab comparison, not a claim to enumerate every capable provider.
- Added three reciprocal contextual links into the flagship from the AI coding-agent, Ubuntu AI-developer, and AI safety pages, bringing contextual inbound links from five to eight.
- Added two intentionally non-overlapping follow-on specs: open-weight deployment and API pricing/capacity. Do not build a second generic AI-labs list.

### Measurement adjustment

The July 9 title experiment was superseded on July 10 because “Complete List” could not be supported by a seven-lab page. Measure the revised page as a new baseline from **2026-07-10 to 2026-08-06**, using the page filter and the frontier-AI query family. Compare clicks, CTR, and position against the preceding equal-length period; interpret high-impression zero-click fragment URLs as SERP-feature exposure, not a direct blue-link CTR failure.

## Log

- 2026-07-09 — Doc created, seeded with first GSC baseline pull (28-day window). No changes made yet.
- 2026-07-09 — Full audit: 180-day GSC pull + parsed metadata sweep of all 151 files. Wrote
  `seo-audit-2026-07-09.md` and `seo-implementation-spec.md`. Corrected three false-positive classes
  from the naïve-regex first pass. Metadata pass (WP1–WP6) dispatched for implementation.
- 2026-07-10 — Implemented the AI frontier strategic refresh, cluster links, and two differentiated follow-on specs. Awaiting the new 28-day measurement window before judging CTR or position impact.
- 2026-07-11 — Strategic pivot to niche-reference + AI-citability. Recorded the AI-distribution baseline (Cloudflare crawler UAs + GA4 AI referrals) and restructured `/llms.txt` around a curated strongest-pages section.
- 2026-07-11 — Added the AI-distribution re-pull to the 2026-08-06 measurement plan, pre-registered the continue-vs-maintenance decision rule, and scheduled the checkpoint (`cheatsheets-pivot-checkpoint`, one-time 2026-08-06). Content policy (niche utility test) added to `TODO/README.md`.
- 2026-07-12 — Coherence sweep + one new striking-distance rewrite. Fresh 28-day GSC pull (2026-06-13
  → 2026-07-10): `ai-frontier.html` 138 clicks / 50,562 impressions / position 9.9 (up from 123 /
  42,978 in the prior window — impressions growing). Verified and closed all five 07-09 follow-ups;
  realigned 7 pages' JSON-LD `headline` to their visible `<h1>`; acceptance gate now 0 failures
  corpus-wide. Rewrote `boom-supersonic.html` title/description around its real query family
  ("Boom Supersonic Overture: Specs, Range, Speed & Timeline" — every claim verified against the
  page body). Answered the versioncontrol/git-scm cannibalization question with fresh data:
  self-resolved, recommend leaving both. Internal-linking pass stays deferred until the 2026-08-06
  checkpoint, per the pre-registered plan. Not pushed.
