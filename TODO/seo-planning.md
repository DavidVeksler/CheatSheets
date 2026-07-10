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
- [ ] **David's decision:** return `410 Gone` for `anduril-products.html`? It was deliberately removed
  (commit `5a5db5e`, trademark exposure) but earned 295 clicks / 90,225 impressions at position 6.6
  over the window, and now serves a bare 404. Recommended: 410, no redirect.
- [ ] **David's decision:** cannibalization — `versioncontrol.html` (4,904 impressions, **0 clicks**)
  overlaps `git-scm.html` (position 36.8). Consolidate, differentiate, or leave? Per the site-goals
  rule, check which goal each serves first.
- [ ] Contextual internal linking pass (`SEO_PROMPT.txt` footer procedure). Deferred until the
  metadata pass is measured. Flagship `ai-frontier.html` has only 5 inbound contextual links.
- [ ] `list_sitemaps` MCP call currently **errors** (`cannot unmarshal string into … warnings of type
  int64`) — an MCP-server bug, not a sitemap problem. Check coverage via the GSC web UI instead.

## Measurement plan

Re-pull **2026-08-06** (28 days after the metadata pass lands), same 180-day window for comparability.

- **Primary metric:** clicks on the 16 WP1 pages, before vs. after, at roughly constant position.
- **Guard-rail:** average position on those pages must not fall. A rewritten title that drops position
  lost relevance — revert that one page.
- **Do not** use site-wide CTR as the metric (see conclusion 1).

## Log

- 2026-07-09 — Doc created, seeded with first GSC baseline pull (28-day window). No changes made yet.
- 2026-07-09 — Full audit: 180-day GSC pull + parsed metadata sweep of all 151 files. Wrote
  `seo-audit-2026-07-09.md` and `seo-implementation-spec.md`. Corrected three false-positive classes
  from the naïve-regex first pass. Metadata pass (WP1–WP6) dispatched for implementation.
