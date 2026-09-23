# SEO planning: cheatsheets.davidveksler.com

Durable site-wide SEO working doc; update in place. Numbers are snapshots: re-pull before trusting anything older than a few weeks. Dated results go in [`../docs/seo-progress.md`](../docs/seo-progress.md). Prior pulses, audits, and the 2026-08-06 checkpoint tables are in this file's git history.

Per-cluster: [`META-crypto-custody-cluster-seo.md`](META-crypto-custody-cluster-seo.md) (9 custody sheets, day-30/60/90 gates). Dev spokes: [`META-dev-spoke-content-plan.md`](META-dev-spoke-content-plan.md).

## Tooling

- GSC property `https://cheatsheets.davidveksler.com/`. Prefer [`../scripts/gsc_query.py`](../scripts/gsc_query.py) (direct API, raw rows stay on disk, prints aggregates) over the `search-console` MCP for mining:
  ```
  python scripts/gsc_query.py --days 90 --dim query --zero-click --min-impr 100 --sort impressions
  python scripts/gsc_query.py --days 90 --dim page query --query-contains "new glenn"
  ```
- Before trusting a range pull, sanity-check with a `date`-dimension pull returning distinct days (GSC once served a single cached day for every range).
- MCP `list_sitemaps` fails with an `int64` unmarshal error (client bug, not a sitemap defect); check sitemap status in the GSC web UI.
- Cloudflare AI-crawler pulls: free plan keeps ~8 days, so compare 7-day windows, host-filtered to `cheatsheets.davidveksler.com`.
- GA4 property `543339529`: `analytics-mcp` is not connected and no GA4 credential is on disk, so AI-referral numbers can't be pulled. **Open: connect it.**
- Parse `<head>` with a real HTML parser and validate each `ld+json` block separately (regex audits produced false positives: reversed attribute order, multiple JSON-LD blocks, SVG `<title>`). `scripts/seo_check.py` does this.

## Standing rules

- **Judge pages by their goal.** Four goals: personal study, personal brand, agentic case study (organic traffic is the KPI), advocacy (reach). Only case-study and advocacy pages are judged on search. Never prune or deprioritize for low demand without checking the goal. Nothing gets pruned.
- **No site-wide CTR target.** Much low CTR is SERP-feature / AI Overview absorption (signature: position 2-7 with zero clicks, e.g. `judo.html` "judo guide", `martial-arts-cheatsheet.html` "martial arts guide" 11,654 impr @ 5.9). Don't chase those with title work.
- **The fixable lever is the listing:** query-aligned titles containing the words users type (validated on `ai-frontier.html`: "frontier ai labs list" moved from position 5-8 to 2-3).
- **Guard-rail for title changes:** if a rewritten title drops position at flat impressions, revert that page. Pull page×query before reverting; an impressions collapse usually means a lost head query, not a bad title.
- `ai-frontier.html` owns the "frontier ai labs / companies / models / providers / list" family. Any AI page must diff its target queries against it; never build a second generic AI-labs list.
- New pages are measured on their own baseline from launch, never folded into another comparison.
- `anduril-products.html` stays a 404 (no redirect, no 410); don't promote the topic.
- `versioncontrol.html` (DVCS/Mercurial intent) and `git-scm.html` (interactive Git) stay separate.
- `postgresql.html`: no content additions (18k words; its rank problem is off-page).
- `llms.txt` leads with a curated "Strongest pages" section (pages with demonstrated search/AI demand), full category index below. Every new sheet and pillar gets a category-section entry (pillars have shipped missing from it before).
- New topics must pass the niche-utility test ([`README.md`](README.md) Rule 0).

### Reusable pillar spec

A pillar is not a bare link list (doorway/thin risk). Each needs: head term in H1 + 2-3 sentence scope intro; one synthesizing artifact the spokes don't duplicate (cross-spoke table, decision framework, or landscape map); keyword-anchored spoke index with one-line value props; a reciprocal "Part of: [Pillar]" link near the top of each spoke; `CollectionPage` + `ItemList` (or `BreadcrumbList`) JSON-LD; title ≤ 60 with the head term, description 150-200, `seo_check.py` clean; `category-map.php` entry; one pillar per commit with its preview image.

Shipped pillars: `rockets-and-spaceflight`, `software-development-guides`, `ai-models-compared` (scoped to "which ai model / ai model comparison / ai api pricing"), `ai-safety-existential-risk` ("ai existential risk / x-risk / p(doom)"), `ai-datacenter-infrastructure` ("ai data center / ai infrastructure / data center power"), `crypto-custody-index`. Next candidate (unbuilt): a humanoid/hardware pillar over `humanoid-robots` and `tesla-products`.

## Current state (latest pull 2026-08-24, 28 days)

882 clicks / 185,055 impressions / 0.48% CTR / position ~12.4. `ai-frontier.html` 256 clicks / 57,781 impr / position 8.10, improving five pulses running. Task-shaped pages own CTR (2.6-8.1%: `ham-radio-technician`, `azure-devops`, `baofeng-uv5r-quick-ref`, `shabbat-services-cheatsheet`, `veterinary-diagnostics`); broad pages sit at 0.4-0.6% regardless of position.

AI distribution: AI systems read the site heavily but send almost no clicks. Crawler baseline 10,573 requests/7d (2026-07-04→10), 11,129/7d at 2026-08-06 (flat, ChatGPT-User ~64%); GA4 AI referrals 7 sessions/90d at baseline, not re-pulled since. Judge on both crawler run-rate and referrals, never referrals alone.

2026-08-06 checkpoint verdict: **continue investing** (WP1 title-pass pages +33.9% clicks at better position). Title freeze lifted.

## Active measurement baselines

| Page / area | Baseline from | Re-pull | Query family |
|---|---|---|---|
| Category hubs `/<slug>` + homepage | 2026-09-17 | 2026-10-17, then 60/90 days | per-hub; "<topic> cheat sheet(s)" family. Continue hub investment if any hub gets ≥ 50 impr in 30 days, or "ham radio cheat sheet" / "git cheat sheet" reach page 1 |
| `postgresql.html` title revert (`a385796`) | 2026-08-12 | next pull | "postgres cheat sheet", "postgresql commands cheat sheet", "psql cheat sheet"; compare vs post-WP1 27.82 and pre-WP1 13.13 |
| Dev spokes (azure-devops, dotnet, clean-architecture, databases) | 2026-07-21 | next pull | see dev-spoke plan |
| `homelessness-externalized-costs.html` retitle | 2026-09-10 | next pull | expect old-title query history to reset; judge by advocacy goal |
| Crypto custody cluster | 2026-08-31 | 2026-10-01 / 11-01 / 12-01 | see custody doc |

## Open work queue

| Item | Evidence (90d to 2026-08-22) | Action |
|---|---|---|
| `orbital-rockets-comparison.html` | New Glenn head-to-head family ≈ 2,300 impr, 0 clicks, pos 6-11 | Add a side-by-side dimensions block + to-scale visual to this page; no second rocket page (cannibalization) |
| `privacy-data-broker-opt-out.html` | "data broker been verified opt out" 239 @ 28.6; "www.checkpeople.com/opt-out" 121 @ 48.3 | Page has one H2; add per-broker sections with the literal opt-out URL |
| `islam.html` | "sharia law" family 726 impr @ 2.0-2.5, 0 clicks | Likely SERP-feature absorption; measure before investing |
| `home-electrical-basics.html` | wire gauge / NEC ampacity idea (rejected as a separate page) | Fold a numeric ampacity table into the page |
| HVAC / furnace blink codes | good utility shape | Candidate for the next niche batch |
| `index.php` SEO tiers 2-4 | not started | indexable curated paths; homepage "browse by field" block; WebSite/SearchAction + Person `@id` alignment; link-equity shaping on the ~400-link homepage grid |
| GA4 connection | referral leg unmeasurable | connect `analytics-mcp` |
