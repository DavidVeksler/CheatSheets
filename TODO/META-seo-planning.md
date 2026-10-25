# SEO planning: cheatsheets.davidveksler.com

Durable site-wide SEO working doc; update in place. Numbers are snapshots: re-pull before trusting anything older than a few weeks. Dated results go in [`../docs/seo-progress.md`](../docs/seo-progress.md). Prior pulses, audits, and the 2026-08-06 checkpoint tables are in this file's git history.

Per-cluster: [`META-crypto-custody-cluster-seo.md`](META-crypto-custody-cluster-seo.md) (9 custody sheets, day-30/60/90 gates). Dev spokes: [`META-dev-spoke-content-plan.md`](META-dev-spoke-content-plan.md).

## Tooling

- GSC property `https://cheatsheets.davidveksler.com/`. Prefer [`../scripts/gsc_query.py`](../scripts/gsc_query.py) (direct API, raw rows stay on disk, prints aggregates) over the `search-console` MCP for mining:
  ```
  python scripts/gsc_query.py --days 90 --dim query --zero-click --min-impr 100 --sort impressions
  python scripts/gsc_query.py --days 90 --dim page query --query-contains "new glenn"
  ```
- On the Mac run it with the repo venv (`.venv/bin/python scripts/gsc_query.py`, needs `requests` + `cryptography`); the key path is auto-detected (Windows path, then `~/.config/gsc-mcp/service-account.json`). Use `--dim page` for totals: page x query rows drop anonymized queries and undercount badly (the 2026-10-24 log's "222 clicks" was such a pull).
- Title changes: `scripts/retitle.py <file> "<title>" --desc "<desc>"` updates title, OG/X, JSON-LD and breadcrumb in one pass; then `scripts/check_llms.py --sync` and log before/after in `seo-progress.md`.
- Before trusting a range pull, sanity-check with a `date`-dimension pull returning distinct days (GSC once served a single cached day for every range).
- MCP `list_sitemaps` fails with an `int64` unmarshal error (client bug, not a sitemap defect); check sitemap status in the GSC web UI.
- Cloudflare AI-crawler pulls: `scripts/ai_crawler_report.py` (7 full days, host-filtered, UA buckets). Free plan keeps ~8 days, so compare 7-day windows from this same script.
- GA4 property `543339529`: `analytics-mcp` is not connected and no GA4 credential is on disk, so AI-referral numbers can't be pulled. **Open: connect it.**
- Parse `<head>` with a real HTML parser and validate each `ld+json` block separately (regex audits produced false positives: reversed attribute order, multiple JSON-LD blocks, SVG `<title>`). `scripts/seo_check.py` does this.

## Standing rules

- **Judge pages by their goal.** Four goals: personal study, personal brand, agentic case study (organic traffic is the KPI), advocacy (reach). Only case-study and advocacy pages are judged on search. Never prune or deprioritize for low demand without checking the goal. Nothing gets pruned.
- **No site-wide CTR target.** Much low CTR is SERP-feature / AI Overview absorption (signature: position 2-7 with zero clicks, e.g. `judo.html` "judo guide", `martial-arts-cheatsheet.html` "martial arts guide" 11,654 impr @ 5.9). Don't chase those with title work.
- **The fixable lever is the listing:** query-aligned titles containing the words users type (validated on `ai-frontier.html`: "frontier ai labs list" moved from position 5-8 to 2-3).
- **Guard-rail for title changes:** if a rewritten title drops position at flat impressions, revert that page. Pull page×query before reverting; an impressions collapse usually means a lost head query, not a bad title.
- `ai-frontier.html` owns the "frontier ai labs / companies / models / providers / list" family. Any AI page must diff its target queries against it; never build a second generic AI-labs list.
- New pages are measured on their own baseline from launch, never folded into another comparison.
- `anduril-products.html` (and `defense-autonomy-platforms.html`) 301 to `autonomous-defense-systems.html` (deliberate since 2026-07-09, `deploy/cloudflare/redirects.txt`). Never restore the page; don't promote the brand topic.
- `versioncontrol.html` (DVCS/Mercurial intent) and `git-scm.html` (interactive Git) stay separate.
- `postgresql.html`: no content additions (18k words; its rank problem is off-page).
- `llms.txt` leads with a curated "Strongest pages" section (pages with demonstrated search/AI demand), full category index below. Coverage of both `llms.txt` and `llms-full.txt` is a deploy gate (`scripts/check_llms.py`, `--fix` adds missing sheets, `--sync` refreshes index entries after retitles); curating "Strongest pages" stays manual, from 28-day GSC clicks.
- New topics must pass the niche-utility test ([`README.md`](README.md) Rule 0).

### Reusable pillar spec

A pillar is not a bare link list (doorway/thin risk). Each needs: head term in H1 + 2-3 sentence scope intro; one synthesizing artifact the spokes don't duplicate (cross-spoke table, decision framework, or landscape map); keyword-anchored spoke index with one-line value props; a reciprocal "Part of: [Pillar]" link near the top of each spoke; `CollectionPage` + `ItemList` (or `BreadcrumbList`) JSON-LD; title ≤ 60 with the head term, description 150-200, `seo_check.py` clean; `category-map.php` entry; one pillar per commit with its preview image.

Shipped pillars: `rockets-and-spaceflight`, `software-development-guides`, `ai-models-compared` (scoped to "which ai model / ai model comparison / ai api pricing"), `ai-safety-existential-risk` ("ai existential risk / x-risk / p(doom)"), `ai-datacenter-infrastructure` ("ai data center / ai infrastructure / data center power"), `crypto-custody-index`. Next candidate (unbuilt): a humanoid/hardware pillar over `humanoid-robots` and `tesla-products`.

## Current state (latest pull 2026-10-25, 28 days to 10-22)

1,211 clicks / 126,462 impressions (page dim), clicks +16% on the prior 28 days, daily clicks 30-45, CTR ~1.0-1.5%. `starlink-satellite-anatomy.html` is now the #1 click page (238, was 53) after Starship Flight 14 put the first V3s in orbit; `ai-frontier.html` 193 clicks, impressions down 69% (lost date-stamped fan-out queries, head query held). Task-shaped pages still own CTR (`baofeng-uv5r-quick-ref` 5.0%, `ham-radio-technician` 7.9%, `death-logistics` 10.2%). Hubs: `/ai-safety` 90 and `/philosophy-religion` 53 impressions in 30 days (bar met), 7 hubs at zero.

AI distribution: 7,737 AI-agent requests/7d (2026-10-18 to 10-24; ChatGPT-User 1,391, PerplexityBot 981, OAI-SearchBot 642, Claude-User 554) vs 11,129/7d at 2026-08-06; method may differ, re-pull with the same UA-regex script before calling it a drop. Live technical health is clean (225/225 sitemap URLs 200, self-canonical, one H1, valid JSON-LD).

## Strategy (set 2026-10-25)

Ranked by expected clicks per hour of work, from what the last three months of data show:

1. **Event-driven freshness on spec pages.** Starlink went 53 -> 238 clicks in the month a launch happened, while the page still said V3 had not flown. When a tracked event lands (launch, model release, product ship), the matching page is updated within days, not at the weekly freshness sweep. Watch list: starlink-satellite-anatomy, orbital-rockets-comparison, ai-frontier, ai-model-release-log, humanoid-robots, tesla-products, boom-supersonic.
2. **Listing alignment (titles/descriptions).** Monthly round with `retitle.py`, aimed at human query families at positions 4-20 with low CTR; never at agent fan-out queries or SERP-feature absorption. Guard rail unchanged.
3. **Answer blocks for conversational search.** Most of Starlink's clicks are anonymized, conversational queries (AI Mode style). Put a question-shaped H2/H3 plus a 2-4 sentence sourced answer near the top of spec pages ("How big is X?", "X vs Y size").
4. **Entity headings on list pages.** Pages that cover many named things (brokers, rockets, labs, throws) need one real heading and id per entity so per-entity queries match (privacy page had one H2 for 18 brokers).
5. **Off-page for stuck head terms.** git-scm (git commands, pos 64), semiconductor (wafer fabrication, pos 40-50), postgresql: on-page is done; they need links. Route through cold outreach (`docs/cold-outreach.md`) and the cross-linking plan, not more title work.
6. **AI answer engines.** Keep `llms.txt` complete (gated) and curated; track AI-agent run-rate weekly with one fixed script; add ChatGPT/Claude/Perplexity visibility spot-checks for the top 10 pages.
7. **Hubs.** Bar met; next lever is internal links into the 7 zero-impression hubs (start-here blocks from strong sheets), not new hubs.

## Active measurement baselines

| Page / area | Baseline from | Re-pull | Query family |
|---|---|---|---|
| Category hubs `/<slug>` + homepage | 2026-09-17 | 30-day bar met 2026-10-25 (ai-safety 90, philosophy-religion 53); re-pull 2026-11-16 and 12-16 | per-hub; "<topic> cheat sheet(s)" family; watch the 7 zero-impression hubs |
| Title round 1 (orbital-rockets, ai-frontier, ashihara) | 2026-10-24 | 28 days after deploy | see `seo-progress.md` 2026-10-24 |
| Title round 2 (10 pages incl. starlink, judo, BJJ, privacy) + orbital size chart | 2026-10-25 | 28 days after deploy | see `seo-progress.md` 2026-10-25 |
| `postgresql.html` title revert (`a385796`) | 2026-08-12 | next pull | "postgres cheat sheet", "postgresql commands cheat sheet", "psql cheat sheet"; compare vs post-WP1 27.82 and pre-WP1 13.13 |
| Dev spokes (azure-devops, dotnet, clean-architecture, databases) | 2026-07-21 | next pull | see dev-spoke plan |
| `homelessness-externalized-costs.html` retitle | 2026-09-10 | next pull | expect old-title query history to reset; judge by advocacy goal |
| Crypto custody cluster | 2026-08-31 | 2026-10-01 / 11-01 / 12-01 | see custody doc |

## Open work queue

| Item | Evidence | Action |
|---|---|---|
| Deploy rounds 1 + 2 | pushed 2026-10-24/25, not live | David's go-ahead, then `scripts/deploy-cloudflare.sh`; start the 28-day clocks |
| Starlink V3 watch | #1 page; V3 mass/dimensions still undisclosed; Wikipedia infobox showed "v3: 46" on 10-23 vs 26 confirmed | re-check SpaceX/FCC for V3 mass and further Starship V3 launches; update table within days of news |
| `boom-supersonic.html` | "boom overture" 595 @ 13.3, range 222 @ 7.6, speed 209 @ 8.6, 0-1 clicks | title already aligned; add a top-of-page answer block (range, speed, seats, first flight) |
| `anapanasati-mindfulness-of-breathing.html` | "anapanasati" 1,421 @ 9.8, 6 clicks | head term; check SERP shape before touching the title |
| `privacy-data-broker-opt-out.html` follow-ups | Whitepages, TruePeopleSearch, PeopleFinders, FastPeopleSearch (`/removal` vs `/optout`), MyLife, That'sThem, Acxiom block automated fetches; nuwber.com did not resolve 2026-10-25 | verify by hand in a browser |
| `orbital-rockets-comparison.html` | Long March 5 liftoff mass sources conflict (643 t vs ~852 t) | find a CALT primary figure |
| `islam.html` | "sharia law" family 726 impr @ 2.0-2.5, 0 clicks | likely SERP-feature absorption; measure before investing |
| `home-electrical-basics.html` | wire gauge / NEC ampacity idea (rejected as a separate page) | fold a numeric ampacity table into the page |
| HVAC / furnace blink codes | good utility shape | candidate for the next niche batch |
| Hardware pillar | humanoid-robots + tesla-products + starlink + orbital | candidate pillar (spec in "Reusable pillar spec") |
| `index.php` SEO tiers 2-4 | not started | indexable curated paths; homepage "browse by field" block; WebSite/SearchAction + Person `@id` alignment |
| AI-crawler baseline | 7,737/7d vs 11,129 (method may differ) | re-baseline weekly with `scripts/ai_crawler_report.py` (committed 2026-10-25); a candidate for the weekly KPI routine |
| GA4 connection | referral leg unmeasurable | connect `analytics-mcp` |
