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

## Fresh pulse — last 28 days (2026-06-23 → 2026-07-20)

Pulled 2026-07-21. Full numbers in [`docs/seo-progress.md`](../docs/seo-progress.md). Strategy
unchanged; still under the title/consolidation freeze until the 2026-08-06 checkpoint.

- `ai-frontier.html`: **158 clicks / 51,150 impressions / 0.31% CTR / position 9.0** — clicks and
  position both improving across the last three pulses (138→158 clicks; 9.9→9.0 position). Frontier-AI
  query family holds positions 2–6.
- `baofeng-uv5r-quick-ref.html`: 59 / 1,493 / 3.95% / 7.7. `orbital-rockets-comparison.html`: 31 /
  9,897 / 0.31% / 10.0. `shabbat-services-cheatsheet.html`: 30 / 603 / 4.98% / 8.2.
- New/notable: `global_cuisine_guide.html` (20 clicks, new to top pages), `ham-radio-technician.html`
  (17 clicks, 5.67% CTR), `yudkowsky-rationality-ai-cheatsheet.html` (10 clicks, position 5.9).
- **Post-freeze striking-distance queue:** `azure-devops.html` wins its head term ("azure devops
  cheat sheet", position 2, 20% CTR) but sits at page-level position 20.7 — long-tail coverage gap.
  Dev spokes ranking far back: `databases` 26.6, `dotnet-cheatsheet` 24.6, `postgresql` 22.7,
  `clean-architecture-dotnet` 30.7, `aws-vs-azure` 53.6, `git-scm` 51.7. Content/coverage signals to
  review after 2026-08-06, not listing fixes. **Diagnosed and specced 2026-07-21 in
  [`dev-spoke-content-plan.md`](dev-spoke-content-plan.md)** — per-page query families, root-cause
  (authority/depth, not titles), and ready-to-execute content actions. Key calls: Tier 1 =
  `azure-devops` (thin, add best-practices section) + `dotnet-cheatsheet` (add C# keywords table, 408
  impr @ pos 28); `postgresql` is already deep+fresh so its pos-45 is off-page, **not** a content
  gap — do not add words there.
- **Fix shipped this pulse (freeze-safe):** the three pillars launched 2026-07-15
  (`ai-models-compared`, `ai-safety-existential-risk`, `rockets-and-spaceflight`) had been omitted
  from `llms.txt`; added them to the AI-crawler discovery index in their category sections. Only the
  upgraded `software-development-guides.html` had been present.

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

**The 2026-08-06 checkpoint has run — verdict CONTINUE INVESTING, freeze lifted.** See
"Decision checkpoint — verdict" below. Status as of 2026-08-12:

1. ✅ **Tier 1 of `dev-spoke-content-plan.md` was already executed 2026-07-21** in commit
   `4870e04` ("Expand Azure DevOps and C# reference sections") — both the Azure DevOps
   Best Practices section and the C# Keywords Cheat Sheet table shipped, ahead of the freeze
   actually lifting. Nothing left to do here; re-pull each query family once range data is
   available again (see tooling note below) to measure lift.
2. ✅ **`martial-arts-cheatsheet` guard-rail flag diagnosed 2026-08-24 — the title is innocent.**
   A 90-day page×query pull shows the page holding **11,654 impressions at position 5.9 with zero
   clicks** on the single query "martial arts guide". The impressions never disappeared; the
   27-day checkpoint window clipped them. This is the `judo.html` SERP-feature signature, not a
   title losing relevance. **Do not revert.** `postgresql` was already reverted 2026-08-12.
3. ⏳ Connect `analytics-mcp` (GA4 property 543339529) so the AI-referral leg is measurable again.

✅ **RESOLVED 2026-08-24 — see the 2026-08-24 pull below. Range queries work again; the note
below is kept for the record.** ⚠️ **Tooling note (2026-08-12): GSC range queries were
non-functional, both via the
`search-console` MCP tool and the live Search Console web UI.** Any query — API or a manual
custom date range set through the UI's date picker (verified with David's own
`heroic@gmail.com` account) — collapses to a single cached day, **2026-08-10**, with identical
totals (39 clicks / 10.5K impressions / 13.3 avg. position) regardless of the requested
`start_date`/`end_date`. This was confirmed three ways on the API side (totals, `date`-dimension,
wide-range) and independently in the browser after explicitly setting a custom range. It is not a
client-side bug to route around — the property genuinely isn't serving range data right now.
**Do not trust any "28-day"/"90-day" pull from this session or until this is confirmed fixed** —
re-verify with a `dimensions:["date"]` pull spanning several distinct dates before relying on a
range number again. The 2026-07-14 `list_sitemaps` API call still separately errors with `cannot
unmarshal string into … warnings of type int64`; that one is a known MCP-server parsing bug, not
evidence of a sitemap defect — check submission status in the Search Console web UI instead.

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

### Verdict — **CONTINUE INVESTING** (2026-08-06)

Ran 2026-08-06 by the `cheatsheets-pivot-checkpoint` scheduled task. The rule is met on the
**WP1-clicks leg**: clicks rose materially and aggregate position improved rather than fell.
The AI-distribution leg is roughly flat-to-slightly-up and did **not** independently clear the
"clearly above ~1,500/day" bar, so it neither carries nor blocks the verdict.

**Windows.** GSC data ends 2026-08-04, so the comparison is 27-day windows, not 28:
after = **2026-07-09 → 2026-08-04**, before = **2026-06-12 → 2026-07-08**. `ai-frontier.html`
uses its own 26-day windows per the measurement adjustment: after = 2026-07-10 → 2026-08-04,
before = 2026-06-14 → 2026-07-09.

#### (1) WP1 pages — primary metric

The WP1 set is the 15 pages in `4a8383b` plus `judo.html` from the `51abbba` correction = 16.

| Metric | Before | After | Δ |
|---|---|---|---|
| Clicks, all 16 | 286 | **383** | **+97 (+33.9%)** |
| Clicks, excluding `ai-frontier` | 154 | **176** | **+22 (+14.3%)** |
| Impression-weighted avg position, all 16 | 10.93 | **10.17** | **+0.76 better** |
| Impressions, all 16 | 86,261 | 80,094 | −7.1% |

Per page (clicks before→after, position before→after):

| Page | Clicks | Position | Impressions |
|---|---|---|---|
| ai-frontier | 132 → 207 | 10.07 → **8.30** | 45,878 → 44,003 |
| orbital-rockets-comparison | 44 → 46 | 10.42 → **9.57** | 12,002 → 11,652 |
| ashihara-karate | 24 → 24 | 8.57 → 8.36 | 2,065 → 2,183 |
| google-ai-studio-guide | 12 → 19 | 10.52 → **9.25** | 2,424 → 2,886 |
| operator-loadouts | 16 → 19 | 7.44 → 7.82 | 1,711 → 1,621 |
| tesla-products | 7 → 15 | 12.61 → 13.40 | 2,040 → 1,892 |
| judo | 15 → 11 | 14.27 → 13.78 | 719 → 1,528 |
| anapanasati-mindfulness-of-breathing | 8 → 10 | 16.34 → 15.12 | 662 → 716 |
| martial-arts-cheatsheet | 10 → 9 | 7.01 → **18.29** ⚠️ | 6,524 → 848 |
| clean-architecture-dotnet | 4 → 7 | 29.58 → 29.83 | 459 → 712 |
| compression-algorithms | 5 → 7 | 17.94 → 20.33 | 1,576 → 1,399 |
| postgresql | 2 → 4 | 13.13 → **27.82** ⚠️ | 2,528 → 2,309 |
| databases | 6 → 3 | 26.54 → 27.52 | 402 → 490 |
| humanoid-robots | 1 → 2 | 18.84 → **9.98** | 1,909 → 4,524 |
| bitcoin-whitepaper | 0 → 0 | 10.40 → **7.57** | 3,172 → 2,585 |
| javascript-for-architects | 0 → 0 | 23.93 → 20.50 | 2,190 → 746 |

Nine of sixteen pages improved position; the aggregate guard-rail passes on an
impression-weighted basis (10.93 → 10.17). The unweighted per-page mean drifts the other way
(14.85 → 15.46) entirely because of the two flagged pages below — that is a two-page problem,
not a set-wide one.

**Guard-rail flags (two pages, revert candidates — diagnose before acting):**

- ⚠️ **`martial-arts-cheatsheet.html`** — position 7.01 → 18.29 with impressions collapsing
  6,524 → 848 (−87%). Clicks held (10 → 9). An impressions collapse *plus* a position drop is
  the signature of losing one high-volume head query, not of a title losing broad relevance —
  the same SERP-feature dynamic already documented for `judo.html`. Pull page×query for this
  page before reverting; the rewrite may be innocent.
- ⚠️ **`postgresql.html`** — position 13.13 → 27.82 at roughly flat impressions
  (2,528 → 2,309), clicks 2 → 4. This is the cleanest revert candidate of the two: impressions
  held, so the page still surfaces, it just ranks worse. Note this page is already excluded
  from content work per `dev-spoke-content-plan.md` (deep + fresh; its ranking problem was
  judged off-page), which makes a title revert the cheap first thing to try.

Six other pages slipped position by <2.5 places (clean-architecture-dotnet, operator-loadouts,
tesla-products, databases, compression-algorithms) — all within noise, and four of them gained
clicks. No action.

#### (2) `ai-frontier.html` — its own baseline

| Metric | Before (06-14 → 07-09) | After (07-10 → 08-04) | Δ |
|---|---|---|---|
| Clicks | 127 | **204** | **+61%** |
| Impressions | 45,724 | 40,697 | −11% |
| CTR | 0.28% | **0.50%** | **+79%** |
| Avg position | 9.92 | **8.29** | **+1.63 better** |

Fewer impressions, far more clicks, better position — the query-aligned rewrite is working
exactly as intended. The frontier-AI query family confirms it:

| Query | Before (clicks / pos) | After (clicks / pos) |
|---|---|---|
| frontier ai labs list | 2 / 7.79 | **21 / 2.55** |
| list of frontier ai labs | 2 / 6.12 | **7 / 2.32** |
| frontier labs list | 2 / 5.45 | **5 / 1.90** |
| top frontier ai labs | — | 4 / 5.21 |
| ai frontier labs list | 1 / 4.92 | 3 / 2.11 |
| list of frontier labs | — | 3 / 2.15 |
| frontier ai companies | 7 / 5.36 | 8 / 5.01 |
| frontier model providers | 5 / 3.19 | 2 / 1.78 |
| list of frontier ai models | 4 / 4.85 | 3 / 4.47 |

The "…labs list" cluster went from position 5–8 to position 2–3 and now supplies the bulk of
the page's clicks. Fragment URLs (`#title-openai`, `#title-anthropic`, …) carried 23,690
impressions and 2 clicks in the after window — SERP-feature exposure, as previously ruled, not
a blue-link CTR failure.

#### (3) AI distribution

**Cloudflare crawler run-rate, 7 days 2026-07-30 → 2026-08-05** (same method as the
2026-07-11 baseline; free-plan history cap forces a one-day-per-request loop):

| User agent | Requests (7d) | vs. 2026-07-11 baseline |
|---|---|---|
| ChatGPT-User | 7,135 | 6,945 (+2.7%) |
| Bytespider | 1,646 | 1,184 (+39%) |
| PerplexityBot | 841 | 341 (**+147%**) |
| Amazonbot | 550 | 600 (−8%) |
| Applebot | 181 | 278 (−35%) |
| OAI-SearchBot | 173 | 186 (−7%) |
| DuckAssistBot | 133 | 65 (+105%) |
| Claude-User | 128 | 63 (+103%) |
| ClaudeBot | 88 | 135 (−35%) |
| GPTBot | 75 | 102 (−26%) |
| Google-Extended | 71 | not separately reported |
| Claude-SearchBot | 50 | not separately reported |
| meta-externalagent / CCBot / MistralAI | 49 | 54 |
| GoogleOther | 9 | 620 (−99%) |
| Perplexity-User / cohere | 0 | — |
| **Total** | **11,129** (≈1,590/day) | 10,573 (≈1,510/day), **+5.3%** |

ChatGPT-User is 64% of the total (was 66%). Top ChatGPT-User pages: `ai-frontier.html` 1,664,
`humanoid-robots.html` 1,226, `/` 560, `ai-coding-agents-compared.html` 544,
`starlink-satellite-anatomy.html` 350, `boom-supersonic.html` 322. PerplexityBot's top real
page is again `ai-frontier.html` (123).

Read: the run-rate **recovered** from the 2026-07-21 interim dip (~1,068/day) to slightly above
the July baseline. +5.3% is *not* "clearly above ~1,500/day" — call the crawler leg **flat**.
The genuine movement is compositional: Perplexity, DuckDuckGo AI, and Claude-User roughly
doubled off small bases while `GoogleOther` all but vanished (that agent's baseline was mostly
`history.php` + `/cdn-cgi/*` noise, so its collapse is not a content signal). `humanoid-robots`
doubled its ChatGPT-User pull and `ai-coding-agents-compared` entered the top four — both are
new AI-side demand not visible in Google clicks.

⚠️ **GA4 referral leg not re-pulled this run — source unavailable, not a null result.** The
`analytics-mcp` server is not connected in the scheduled-task session and no GA4 credential
exists on disk (the only Google service account present,
`search-console-mcp@gen-lang-client-0919305470`, is Search Console-scoped). The 90-day AI-referral
number is therefore **unknown**, not zero, and the 7-referrals/90d baseline stands unrefreshed.
This does not change the verdict: the WP1 leg alone satisfies the rule, and the pre-registered
downshift trigger requires *both* legs flat-to-down. **Action:** connect `analytics-mcp` (GA4
property 543339529) before the next checkpoint, or the referral half of the AI thesis stays
unmeasurable.

#### Decision

**CONTINUE INVESTING.** WP1 clicks +33.9% (+14.3% excluding `ai-frontier`) with
impression-weighted position improving 10.93 → 10.17 clears the primary criterion on its own.
`ai-frontier` is the standout (+61% clicks, +1.63 position, CTR nearly doubled) and validates
query-aligned titling as the repeatable lever. AI distribution is flat in volume but shifting
in composition; it neither supports nor blocks the call this quarter.

Consequences:

1. **The title/consolidation freeze is lifted.** The queued post-freeze work in
   [`dev-spoke-content-plan.md`](dev-spoke-content-plan.md) (Tier 1: `azure-devops`
   best-practices section, `dotnet-cheatsheet` C# keywords table) is now unblocked.
2. **Two guard-rail flags to diagnose first**, before any new title work:
   `martial-arts-cheatsheet` and `postgresql` (details above). Pull page×query for each; revert
   the title only if the diagnosis implicates it.
3. **Nothing is deleted or pruned** — per the site-goals ground rule, non-goal-3 pages are not
   judged on traffic.
4. **Fix the GA4 gap** before the next checkpoint so the referral leg is measurable.

The one-time scheduled task (`cheatsheets-pivot-checkpoint`) has now fired and can be retired.

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

Status: **all four pillars shipped 2026-07-15** (commits for P1 aerospace, P3 developer upgrade,
P2 AI-model + AI-safety hubs; P4 martial-arts had shipped earlier in `d32503b`). The per-pillar
build specs (P1–P4) and sequencing that used to live here have been removed now that they are done;
the durable **reusable pillar spec** and structural rationale below are kept for the next pillar.
What shipped:

- **P1 — `rockets-and-spaceflight.html`** (new): launch-vehicle comparison table + "spaceflight
  stack" over 5 spokes; reciprocal backlinks + rocket-card id anchors in the deep dive. New baseline
  from 2026-07-15 on the `rocket comparison / orbital rockets / launch vehicle comparison` family.
- **P3 — `software-development-guides.html`** (upgraded): added a "Start by role or task" routing
  matrix; wired spoke→pillar backlinks into all 20 Software & DevOps spokes.
- **P2a — `ai-models-compared.html`** (new): which-model-for-which-job decision table + four-axis
  framework over 7 tooling spokes. Scoped to `which ai model / ai model comparison / ai api pricing`
  — deliberately **not** the frontier-labs family owned by `ai-frontier`.
- **P2b — `ai-safety-existential-risk.html`** (new): safety landscape + concept glossary over 8
  risk/safety/AGI spokes. Scoped to `ai existential risk / ai x-risk / p(doom)`.
- All four hubs cross-link (the three AI hubs route between distinct intents); each is registered in
  `category-map.php`, carries `CollectionPage` + `ItemList` schema, and passes `scripts/seo_check.py`.

**Measurement:** each new pillar starts its own baseline from its 2026-07-15 launch and is **not**
folded into the WP1 or `ai-frontier` comparisons, keeping the 2026-08-06 checkpoint clean. Re-pull
each hub's page filter against its target query family after ~28 days.

⚠️ **Note on the P1 build:** a prior session had left an untracked `rockets-and-spaceflight.html`
plus discarded companion edits in the working tree; it was never git-added and was overwritten during
this build (unrecoverable). The shipped page follows the spec below and passed the gate; flag if any
prior-version content was wanted.

The section below is grounded in a fresh 180-day GSC pull (2026-01-15 → 2026-07-13, pages +
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

### Shipped pillars (P1–P4) — done 2026-07-15

The detailed P1–P4 build specs and sequencing that lived here have been removed now that all four
are shipped (see the status summary at the top of this section for what each hub is and its query
scope). Two durable notes preserved for the next pillar:

- **`ai-frontier.html` keeps the "frontier ai labs / companies / models / providers / list" family
  (pos 2–6).** Any future AI pillar must diff its target queries against ai-frontier's and re-word
  on overlap. The two shipped AI hubs (`ai-models-compared`, `ai-safety-existential-risk`) were
  scoped this way.
- **P5 shipped 2026-07-21 — `ai-datacenter-infrastructure.html`:** the AI-infrastructure / datacenter
  pillar over `ai-accelerator-comparison`, `ai-infrastructure-numbers`, `datacenter-power-chain`,
  `datacenter-cooling-thresholds`, `data-center-myths`, `data-center-community-impact`, and
  `semiconductor-manufacturing`. Layer-by-layer stack map + constraints grid + keyword-anchored spoke
  index; CollectionPage+ItemList schema; reciprocal backlinks in all 7 spokes; llms.txt now covers the
  pillar + all 7 spokes (5 had been missing). Own measurement baseline from 2026-07-21 on the
  `ai data center / ai infrastructure / data center power` family. Committed, not pushed.
- **Next candidate (not built):** a humanoid/hardware pillar. The aerospace pillar's "frontier
  hardware" aside links `humanoid-robots` (61K impr) and `tesla-products` (89K impr) without absorbing
  them, so they remain free to seed a separate hardware pillar later.

## Fresh pull + demand mining — 2026-08-24

Pulled 2026-08-24 with a new script, [`scripts/gsc_query.py`](../scripts/gsc_query.py), which
talks to the Search Analytics API directly, keeps raw rows on disk, and prints only the
aggregate asked for. It exists because the `search-console` MCP tool returns rows sorted by
clicks straight into an agent's context, which makes exactly the analysis that matters here —
high-impression *zero-click* queries — impractical. Use it for future pulls:

```
python scripts/gsc_query.py --days 90 --dim query --zero-click --min-impr 100 --sort impressions
python scripts/gsc_query.py --days 90 --dim page query --query-contains "new glenn"
```

✅ **GSC range queries work again.** A `dimensions:["date"]` pull over 2026-07-25 → 2026-08-22
returns 29 distinct days with distinct totals. The 2026-08-12 collapse-to-a-single-cached-day
failure has cleared; range numbers are trustworthy. The `list_sitemaps` MCP unmarshal bug is a
separate, still-open client issue.

### Site health — 28 days (2026-07-25 → 2026-08-22)

**882 clicks / 185,055 impressions / 0.48% CTR / position ~12.4.**

- `ai-frontier.html`: **256 clicks / 57,781 impressions / 0.44% CTR / position 8.10** — the
  climb continues across every pulse: 123 → 134 → 158 → 207 (26d) → 256.
- Niche-utility pages still own CTR: `ham-radio-technician` 26 clicks @ **8.05%**,
  `azure-devops` 17 @ 3.96%, `baofeng-uv5r-quick-ref` 72 @ 3.87%,
  `shabbat-services-cheatsheet` 28 @ 2.63%, `veterinary-diagnostics` 8 @ 2.61%.
- Movers: `brazilian-jiu-jitsu` 17 → **49 clicks**; `starlink-satellite-anatomy` (built 2026-07)
  already at 22; `global_cuisine_guide` 20; `engineering-metals-selection` 14.

### Demand mining — 90 days (2026-05-25 → 2026-08-22, 10,257 query rows)

Method: rank by impressions, keep rows with **zero clicks and ≥100 impressions** — 81 queries
where Google shows the site and nobody arrives. Sorted into three buckets: unclaimed demand a new
page can serve, demand an existing page half-serves, and demand nothing can serve (SERP features).

**Bucket 1 — new pages.** Ten specs written, with the per-spec evidence, the rejected candidates
and the build order, in [`niche-utility-batch-2026-08.md`](niche-utility-batch-2026-08.md). The
largest single item is the **AI model release log** (~2,400 impressions/90d across month-stamped
release queries at positions 5–12, all zero clicks) — scoped explicitly off `ai-frontier`'s
frontier-labs family, per the standing rule.

**Bucket 2 — optimization queue (existing pages, not new ones):**

| Item | Evidence | Action |
|---|---|---|
| `martial-arts-cheatsheet.html` | "martial arts guide": **11,654 impressions, position 5.9, 0 clicks** | Guard-rail flag resolved — SERP-feature absorption, not a title defect. Do not revert. |
| `orbital-rockets-comparison.html` | New Glenn head-to-head family ≈2,300 impr/90d, 0 clicks, positions 6–11 | Answer-shape gap, not a title gap. Add a side-by-side dimensions block + to-scale visual **to this page**; a second rocket-size page would cannibalize it. |
| `privacy-data-broker-opt-out.html` | "data broker been verified opt out" 239 @ 28.6; "www.checkpeople.com/opt-out" 121 @ 48.3 | Page has one H2. Add per-broker sections carrying the literal opt-out URL. |
| `islam.html` | "sharia law" 289 @ 2.5, "sharia law rules" 219 @ 2.0, "what is sharia law" 218 @ 2.4 — all zero clicks | Measure before investing; position 2 with zero clicks is the SERP-feature signature. |
| `cooking-guide.html` | 15,663 words, 4 clicks / 1,903 impr @ 20.1 | No lookup artifact. The batch's meat-temperature card is the fix; link it from the top of the guide. |
| Dev spokes | "git commands" 504 @ 61.3, "c# keywords cheat sheet" 378 @ 27.9, "aws vs azure services" 212 @ 62.5, ".net clean architecture" 199 @ 39.6 | Unchanged diagnosis: authority, not titles (`dev-spoke-content-plan.md`). No new dev pages. |

**Bucket 3 — do not chase.** "ashihara" (563 @ 9.9), the `ai-frontier` fragment URLs, and the
position-1-to-2 zero-click rows above are SERP-feature/AI-Overview absorption. Chasing them with
title work has no mechanism to succeed.

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
- 2026-07-15 — **Built all four pillars.** P1 `rockets-and-spaceflight.html` (new), P3
  `software-development-guides.html` (role/task routing matrix + 20 spoke backlinks), P2a
  `ai-models-compared.html` and P2b `ai-safety-existential-risk.html` (both new, scoped off
  ai-frontier's frontier-labs family). Each: CollectionPage+ItemList schema, reciprocal spoke→pillar
  backlinks, category-map registration, 1200×630 preview, passes `scripts/seo_check.py`; committed
  one pillar per commit, not pushed. Removed the completed P1–P4 build specs from this doc. Each hub
  starts its own measurement baseline from 2026-07-15. Note: overwrote a prior untracked P1 file
  (unrecoverable — never git-added).
- 2026-07-21 — Fresh 28-day GSC pulse (recorded above + in `docs/seo-progress.md`). `ai-frontier`
  still climbing (158 clicks / position 9.0). No title/consolidation changes (freeze holds until
  2026-08-06). Found and fixed a discovery gap: the three new pillars were missing from `llms.txt`;
  added them. Queued post-freeze content/coverage work for under-ranking dev spokes (azure-devops,
  databases, postgresql, aws-vs-azure, git-scm, clean-architecture, dotnet).
- 2026-07-21 — Built **P5**, the AI-infrastructure/datacenter pillar (`ai-datacenter-infrastructure.html`),
  freeze-safe as new content. Ran an interim Cloudflare AI-crawler pull (~1,068/day, down from ~1,510
  baseline; Perplexity up) and verified live infra (404s fixed, caching present). Staged copy-paste
  marketing posts with tracked UTM URLs in `marketing/ready-to-post.md`. Flag: the 08-06 checkpoint
  scheduled task is not visible from this macOS session (Windows desktop registry) — confirm it exists.
- 2026-07-21 — Prepped the post-freeze dev-spoke content work: pulled 90-day page×query data, diagnosed
  each under-ranking dev spoke, and wrote `TODO/dev-spoke-content-plan.md` (ready-to-execute after
  2026-08-06). Root cause is authority/depth, not titles (every page already has its head keyword in
  its title yet ranks pos 40–87). Tier 1: `azure-devops` (thin — add best-practices section) and
  `dotnet-cheatsheet` (add a C# keywords table for the 408-impr "c# keywords cheat sheet" query).
  Explicitly excluded `postgresql` from content work (already 18k words + fresh; its pos-45 is off-page).
- 2026-08-12 — GSC check-in. Confirmed Tier 1 of `dev-spoke-content-plan.md` was already shipped
  2026-07-21 (`4870e04`) — doc was stale, corrected. Traced `postgresql.html`'s guard-rail flag to
  its exact cause: commit `4a8383b` (2026-07-09, WP1 metadata pass) changed the title from
  "PostgreSQL Power User Cheatsheet - Advanced Guide for DBAs & Developers" (73 chars, over the
  60-char standard) to "PostgreSQL Cheat Sheet: Commands, Tuning and Advanced SQL" (59 chars) —
  this is the exact change coincident with the 13.13 → 27.82 position drop at flat impressions
  recorded in the 08-06 checkpoint. Could not get fresh range data to confirm the drop persists
  today (see tooling note below). **David chose to revert** rather than wait; shipped in
  `a385796` — new title "PostgreSQL Power User Cheat Sheet for DBAs & Devs" (49 chars, compliant)
  recovers the pre-WP1 audience framing and also fixes a title/H1 mismatch introduced by the WP1
  change (H1 still read "PostgreSQL Power User Cheatsheet" while the title said something
  unrelated). Description/keywords left untouched — the WP1 rewrite fixed a real defect there
  (doubled-space typo, over-length emoji-laden original), so only the title regressed.
  **New measurement baseline from 2026-08-12**, separate from the WP1 table above: re-pull this
  page's `postgres cheat sheet` / `postgresql commands cheat sheet` / `psql cheat sheet` query
  family once GSC range queries work again, compare position against the post-WP1 27.82 and the
  pre-WP1 13.13. `martial-arts-cheatsheet.html`'s flag is still open — undiagnosed, no title
  changed there this session.
- 2026-08-06 — **Ran the pre-registered decision checkpoint. Verdict: CONTINUE INVESTING.** WP1 pages
  286 → 383 clicks (+33.9%; +14.3% excluding `ai-frontier`) with impression-weighted position
  improving 10.93 → 10.17, so the primary criterion passes on its own. `ai-frontier` on its own
  baseline: 127 → 204 clicks (+61%), CTR 0.28% → 0.50%, position 9.92 → 8.29; the "frontier ai labs
  list" cluster moved from position 5–8 to 2–3. AI crawler run-rate 11,129/7d (~1,590/day) vs. the
  ~1,510/day baseline — recovered from the 07-21 dip but only +5.3%, so the AI leg is judged **flat**
  (Perplexity +147%, Claude-User +103%, DuckAssistBot +105% off small bases; `GoogleOther` collapsed
  99%, but its baseline was `history.php`/`cdn-cgi` noise). **GA4 referral leg not re-pulled — source
  unavailable, not zero:** no `analytics-mcp` server in the scheduled-task session and no GA4
  credential on disk. Flagged two guard-rail failures for diagnosis before revert:
  `martial-arts-cheatsheet` (pos 7.01 → 18.29, impressions −87% — looks like a lost head query, not a
  title defect) and `postgresql` (pos 13.13 → 27.82 at flat impressions — the cleaner revert
  candidate). Freeze lifted; `dev-spoke-content-plan.md` Tier 1 unblocked. Nothing pruned. Windows
  were 27 days, not 28, because GSC data ends 2026-08-04.
- 2026-08-24 — **Fresh GSC pull + demand mining + 10 new specs.** Confirmed GSC range queries work
  again (the 2026-08-12 tooling warning is resolved and marked as such above). Wrote
  `scripts/gsc_query.py` so future pulls can mine zero-click demand without dumping 10k rows into an
  agent's context. 28-day site health: 882 clicks / 185,055 impressions / 0.48% CTR, with
  `ai-frontier` at 256 clicks / position 8.10 (fifth consecutive improving pulse). Mined the 90-day
  query set for zero-click, ≥100-impression queries (81 of them) and split them into new-page demand,
  optimization work, and SERP-feature noise. Diagnosed the open `martial-arts-cheatsheet` guard-rail
  flag: 11,654 impressions at position 5.9 with zero clicks on "martial arts guide" — the title is
  innocent, do not revert. Specced ten niche-utility cheatsheets in
  `TODO/niche-utility-batch-2026-08.md` plus one file per sheet, all passing the title/description
  constraints of `scripts/seo_check.py` at spec time. Build order is seasonal-first: the High Holiday
  services follow-along has a hard 2026-09-01 deadline.
