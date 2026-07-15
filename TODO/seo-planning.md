# SEO planning — cheatsheets.davidveksler.com

Durable working doc for ongoing SEO strategy. Not a spec for a single cheatsheet (see
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

## Fresh pulse — last 28 days (2026-06-16 to 2026-07-13)

Pulled 2026-07-14 through the Search Console API. The strategy is unchanged:

- `ai-frontier.html`: **134 clicks / 50,311 impressions / 0.27% CTR / position 9.7**.
- `baofeng-uv5r-quick-ref.html`: **63 / 1,486 / 4.24% / 7.8**.
- `orbital-rockets-comparison.html`: **42 / 11,526 / 0.36% / 10.7**.
- `shabbat-services-cheatsheet.html`: **27 / 494 / 5.47% / 8.7**.
- `veterinary-diagnostics.html`: **18 / 184 / 9.78% / 16.5**.

The broad AI page still supplies scale, while task-shaped niche references still supply the strongest
CTR. Keep the niche-utility topic gate; do not read low CTR on SERP-feature-heavy broad queries as a
site-wide quality verdict.

## Full audit — 2026-07-09

A 180-day pull (2026-01-10 → 2026-07-08) plus a parsed metadata sweep of the then-current 151-file
corpus drove work packages WP1–WP6. All six packages are complete in commits `4a8383b`, `04252ad`,
`42727af`, `3bf35f1`, `bfb691a`, and `e8cfd07`. The finished implementation spec has been removed from
`TODO/`; the reusable gate now lives at [`scripts/seo_check.py`](../scripts/seo_check.py).

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
`<head>` with a real HTML parser and validate each `ld+json` block independently.
[`scripts/seo_check.py`](../scripts/seo_check.py) preserves both requirements.

## Current next step

The only pre-registered action is the 2026-08-06 measurement checkpoint below. Do not make another
query-driven title or consolidation change before that result unless a correctness defect appears.

Tooling note: the 2026-07-14 `list_sitemaps` API call still errors with `cannot unmarshal string into
… warnings of type int64`. This is an MCP-server parsing bug, not evidence of a sitemap defect; check
submission status in the Search Console web UI.

## Closed decisions and implementation evidence

- `anduril-products.html` stays a 404: no redirect and no `410 Gone`.
- `versioncontrol.html` and `git-scm.html` stay separate. Fresh data showed Mercurial/DVCS-comparison
  intent on the former and interactive-Git intent on the latter, so the apparent cannibalization had
  self-resolved.
- The 2026-07-14 contextual-linking pass added reciprocal category-local discovery links across all
  160 pages. A parsed graph check reports **0 orphan pages**, **minimum 4 inbound links per page**,
  `ai-frontier.html` at 9 inbound links, and `how-its-built.html` at 160.

## Metadata-pass closure

The 2026-07-12 sweep verified and closed all five follow-ups: humanoid/AI-frontier heading coherence,
seven stale JSON-LD headlines, unescaped JavaScript examples, the human-skeleton content stub, and
autonomous-defense metadata. These are no longer TODO items.

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

## Pillar-page strategy — 2026-07-15

Status: **plan only, not yet built.** This section is the durable spec; no pillar pages have been
created or modified yet. Grounded in a fresh 180-day GSC pull (2026-01-15 → 2026-07-13, pages +
queries) taken 2026-07-15.

### The structural gap

The 13 categories in `category-map.php` exist **only as filter chips on the `index.php` gallery**.
There is no dedicated *pillar page* per cluster — a hub that targets a broad head keyword, carries
independently useful synthesizing content, and links out to every spoke with keyword-rich anchor
text (with each spoke linking back up). Today the ~185 spokes spend internal-link equity only
laterally (the 2026-07-14 category-local reciprocal pass), never up into a hub that ranks for the
head term. Pillars are the biggest untapped *structural* lever and are **outside the 2026-08-06
freeze**, which covers title/consolidation edits on existing pages, not new hub content.

### Why the data supports pillars

1. The **`"[topic] cheat sheet"` head modifier converts extremely well** — exactly what a pillar
   targets: `azure devops cheat sheet` (pos 2.2, 27% CTR), `bjj cheat sheet` (pos 1.5, 41% CTR),
   `databases cheat sheet` (pos 4.0, 18% CTR), plus `ham radio`, `clean architecture`,
   `material(s) science`, `.net` cheat-sheet variants all ranking.
2. Several clusters have **strong spokes but no aggregating hub** (rockets, dev, AI-tools), so the
   head term is un-owned even though the site has deep supporting content.

### Reusable pillar spec (applies to every pillar below)

A pillar is **not** a bare link list (that risks a Google "doorway/thin" classification and fails
the site's niche-utility gate). Each pillar must:

- **H1 + intro:** head term in the H1; 2–3 sentence intro that defines the cluster and its scope.
- **Independently useful core:** at least one synthesizing artifact the spokes don't duplicate —
  a cross-spoke comparison table, a "which one do I need" decision framework, or a landscape map.
- **Keyword-anchored spoke index:** every cluster spoke linked with descriptive anchor text
  (the spoke's own head term, not "click here") + a one-line value prop.
- **Reciprocal spoke→pillar link:** a "Part of: **[Pillar]**" contextual link near the top of each
  spoke. Reciprocity is what makes the hub accrue authority.
- **Schema:** `CollectionPage` + `ItemList` enumerating member pages (or `BreadcrumbList`).
- **Metadata + gate:** title ≤60 chars including the head term; description 150–200; must pass
  [`scripts/seo_check.py`](../scripts/seo_check.py) with 0 failures.
- **Registration:** add the new file to `category-map.php` (and it auto-appears in `index.php` /
  `sitemap.php`). Ship one pillar per commit with its `images/*.png` preview, per AGENTS.md.
- **Measurement:** each pillar is a **new page** → measured on its own baseline from launch date,
  never folded into the WP1 title-experiment comparison. This keeps the 2026-08-06 checkpoint clean.

### P1 — Aerospace pillar (BUILD NEW; highest leverage, zero cannibalization)

- **Head terms (from real queries):** `rocket comparison`, `orbital rockets`, `launch vehicle
  comparison`, `rocket size/payload/thrust comparison`, `new glenn vs falcon heavy`,
  `compare rockets`, `rockets by payload capacity`. All rank pos 4–9 today via one spoke.
- **Proposed page:** `rockets-and-spaceflight.html` — H1 e.g. "Orbital Rocket Comparison &
  Spaceflight Cheat Sheet." Core artifact: a live launch-vehicle comparison table (payload to
  LEO/GTO, thrust, reusability, status, first flight) that generalizes the head query family.
- **Anchor spoke:** `orbital-rockets-comparison.html` — **383 clicks / 156,720 impr / pos 7.9**.
- **Spokes to cluster:** `orbital-rockets-comparison`, `boom-supersonic`, `starlink-satellite-anatomy`,
  `space-habitats-life-support`, `stellar-lifecycle` (adjacent astro), plus cross-links to
  `humanoid-robots` and `tesla-products` under a "frontier hardware" aside (those two are also
  their own high-impression assets — 61K and 89K impr — and could later seed a separate hardware
  pillar; do not absorb them fully here).
- **Why first:** no existing hub owns this head term, so there is **no cannibalization risk**, and
  the anchor spoke is the #2 traffic page site-wide. Cleanest, safest, highest-EV build.

### P2 — AI pillar family (BUILD NEW, but scope carefully to avoid cannibalizing `ai-frontier`)

`ai-frontier.html` (607 clicks / 276K impr) **already owns** the "frontier ai labs / models /
companies / providers / list" query family (positions 2–6). **A new AI pillar must not target
those terms** or it will cannibalize the crown jewel. Instead split the ~17-page AI cluster into a
small hierarchy with distinct intents:

- **`ai-frontier.html` stays the "frontier labs" pillar** (leave its head-term ownership intact).
- **New pillar A — "AI models compared / which AI model to use"** (distinct *decision/tooling*
  intent, not "list of labs"). Clusters: `ai-model-picker`, `ai-model-api-pricing`,
  `ai-coding-agents-compared`, `open-weight-ai-models`, `google-ai-studio-guide` (163 clicks),
  `prompt-builder`, `ai-progress-dashboard`. Head terms: `which ai model should i use`,
  `ai model comparison`, `ai api pricing`, `ai coding agents compared`.
- **New pillar B — "AI safety & existential-risk"** (advocacy goal-4). Clusters: `airisk`,
  `aisafety`, `ai-risk-timeline`, `p-doom-calculator` (32 clicks, `p(doom) calculator` pos 4.7),
  `p-doom-test-harness`, `yudkowsky-rationality-ai-cheatsheet`, `agi-development-guide`,
  `governing-agentic-ai`. Head terms: `ai existential risk`, `ai x-risk`, `p(doom)`.
- **AI-infrastructure** (`ai-accelerator-comparison`, `ai-infrastructure-numbers`, `datacenter-*`,
  `semiconductor-manufacturing`) is currently in **Engineering & Science**; keep it there and let
  the aerospace/hardware pillar or a future "AI datacenter" pillar own it — don't stretch pillar A
  over hardware.
- **Guardrail:** before shipping, diff the new pillars' target queries against `ai-frontier`'s
  ranking queries; any overlap on "frontier/labs/models list" terms → re-word the pillar.

### P3 — Developer pillar (UPGRADE existing thin hub)

- **Existing page:** `software-development-guides.html` is already categorized as the Software hub
  but is thin. Upgrade it in place into a real pillar rather than creating a competitor.
- **Head terms:** `software engineering cheat sheet`, `developer cheat sheets`, plus it routes to
  the strong individual `"[X] cheat sheet"` spokes that already rank: `azure devops cheat sheet`
  (132 clicks, pos 2.2), `databases cheat sheet` (68), `clean architecture cheat sheet` (90),
  `.net cheat sheet`, `git cheat sheet interactive`.
- **Spokes:** all 20 **Software & DevOps** pages in `category-map.php`.
- **Core artifact:** a "by role / by task" routing matrix (e.g. architect → `*-for-architects`,
  ops → `modern-devops-pipelines` / `observability` / `linux-server-hardening`) so it isn't a bare
  index.

### P4 — Martial arts pillar (OPTIMIZE existing; CTR problem, not ranking)

- **Existing page:** `martial-arts-cheatsheet.html` — pos **7.0**, 37,834 impr, but **0.12% CTR**.
  Ranking is fine; the **title/snippet is the failure**. This is an optimize + cluster job.
- **Spokes:** `brazilian-jiu-jitsu` (208 clicks, `bjj cheat sheet` pos 1.5), `judo` (103),
  `ashihara-karate` (147), `art-of-war-sun-tzu`.
- **Head terms:** `martial arts techniques`, `martial arts cheat sheet`, `martial arts moves`.
- ⚠️ **Freeze interaction:** rewriting this page's title *is* a query-driven title change, which the
  2026-08-06 freeze defers. Either wait until after the checkpoint, or (like `boom-supersonic` on
  07-12) log it as its own separate baseline so it doesn't confound the WP1 comparison. The
  spoke→pillar *link wiring* is not a title change and can proceed anytime.

### Sequencing recommendation

1. **P1 (aerospace)** first — safest, highest EV, no cannibalization, no freeze interaction.
2. **P3 (developer upgrade)** — no cannibalization (upgrading the designated hub), strong
   `"[X] cheat sheet"` demand.
3. **P2 (AI family)** — highest demand but needs the anti-cannibalization diff before shipping.
4. **P4 (martial arts)** link-wiring anytime; title rewrite after 2026-08-06 or as a logged baseline.

Each pillar ships as its own commit (pillar `.html` + preview `images/*.png` + `category-map.php`
line + spoke→pillar link edits), and starts its own measurement baseline from launch.

## Log

- 2026-07-09 — Doc created, seeded with first GSC baseline pull (28-day window). No changes made yet.
- 2026-07-09 — Full audit: 180-day GSC pull + parsed metadata sweep of all 151 files. Wrote
  the audit and implementation spec. Corrected three false-positive classes from the naïve-regex
  first pass. Metadata pass (WP1–WP6) dispatched for implementation.
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
  self-resolved, recommend leaving both. Not pushed.
- 2026-07-14 — Re-pulled a fresh 28-day GSC pulse; the broad-AI-scale/niche-utility-CTR pattern held.
  Ran the deferred contextual-linking pass across all 160 pages (0 orphans, minimum 4 inbound links),
  moved the SEO gate into `scripts/seo_check.py`, and removed the fully implemented metadata spec
  from `TODO/`.
- 2026-07-15 — Pulled a fresh 180-day GSC page+query snapshot and wrote the **pillar-page strategy**
  section above (four pillars: aerospace / AI-family / developer / martial-arts). Plan only — no
  pillar pages built yet, per decision to review the strategy first. Recommended build order P1→P3→P2,
  with P4 link-wiring anytime and its title rewrite gated on the 2026-08-06 freeze.
