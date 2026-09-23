# SEO progress log

Append-only KPI log for cheatsheets.davidveksler.com, newest block on top. Each entry: date, window, source, numbers; terse. Strategy lives in [`../TODO/META-seo-planning.md`](../TODO/META-seo-planning.md); shared-link measurement in [`../TODO/marketing-campaign-plan.md`](../TODO/marketing-campaign-plan.md). Older blocks: [`archive/seo-progress-2026.md`](archive/seo-progress-2026.md).

<!-- KPI blocks are appended below this line, newest first -->

## 2026-09-17 — Homepage and category-hub baseline (index.php SEO tier 1)

Pulled 2026-09-17 via `scripts/gsc_query.py` and the `search-console` MCP, 90 days
(2026-06-18 → 2026-09-15). Baseline for judging the hub work shipped the same day.

### Front door — 90 days

| URL | Clicks | Impressions | CTR | Position |
|---|---|---|---|---|
| `/` (homepage) | 11 | 2,410 | 0.46% | 17.9 |
| `?cat=AI & Safety` (both encodings) | 0 | 70 | 0% | 7.1 |
| other 14 `?cat=` pages combined | 0 | 18 | 0% | n/a |
| `index.php?category=AI & Safety` (legacy) | 0 | 8 | 0% | 7.9 |

Homepage queries that GSC will name: `site:` searches, "david veksler" (15 impr @ 9.7),
"technology cheat sheets" (16 @ 42.8), "cheatsheets" (1 @ 43), leftover "anduril" queries from
the withdrawn page. Everything else is anonymised long tail. Site-wide, the two-word "cheat sheet"
query family shows real demand the hubs did not capture: "git cheat sheet" 163 impr @ 70,
"database management system cheat sheet" 76 @ 38, "cooking cheat sheets" 56 @ 29,
"ham radio cheat sheet" 84 @ 9.2, "technology cheat sheets" 16 @ 42.8.

Diagnosis (code, not data): 0 of 200 sheets linked to any `?cat=` page; the rail used `+`
encoding while canonical/sitemap used `%20`; hub titles targeted the category name
("AI & Safety Cheatsheets (22)"), which nobody types; hub body was one generated sentence.

### Shipped 2026-09-17

Category hubs moved to `/<slug>` (15 slugs in `category-hubs.json`) with hand-written title,
description, H1, intro and start-here list; `?cat=`, `?category=` and `/<slug>/` 301 to the
slug; every sheet carries a footer breadcrumb + `BreadcrumbList` to its hub (200 new inbound
links per cluster); sitemap `lastmod` for hubs now tracks the newest sheet commit in the category
instead of the catalog build time; homepage title moved to the two-word form with the live count.
Requires the nginx drop-in `conf/nginx/category-hubs.conf` to be live before the deploy.

**Re-pull on or after 2026-10-17** (30 days) and again at 60/90: per-hub clicks/impressions/position,
the "cheat sheet(s)" query family positions above, and whether the breadcrumb trail appears in
SERPs for sheet pages. Success bar for continuing hub investment: any hub with >= 50 impressions
in the 30-day window, or the "ham radio cheat sheet" / "git cheat sheet" families moving to page 1.

## 2026-09-10 — Title change: homelessness-externalized-costs.html

Not a measurement pulse. Recording a deliberate title/URL-metadata change so the next pulse reads
the discontinuity correctly.

| Field | Before | After |
|---|---|---|
| `<title>` | Homelessness: The Cost of Removing the Bottom Rungs | Homelessness: The Costs We Hide and the Options We Banned |
| H1 | Remove the bottom rungs. The street becomes the fallback. | Homelessness tracks rents. Rents track the rules. |
| Primary query target | "cost of homelessness" framing | "why is homelessness higher in california than west virginia", "homelessness rent vs poverty" |

The page was rewritten from an externalized-cost essay into a tiered argument (rent explains where,
individual factors explain who), so the query set it should match changes with it. **Expect GSC
history for the old title's queries to reset**; do not read the drop in the next pulse as a ranking
loss. Slug and canonical URL are unchanged. Judged by the advocacy goal, not by traffic.

## 2026-08-24 — GSC pulse + demand mining

Pulled with the new [`scripts/gsc_query.py`](../scripts/gsc_query.py) (direct Search Analytics
API, local aggregation). **GSC range queries are functional again** — the 2026-08-12 failure where
every range collapsed to a single cached day has cleared, verified with a `date`-dimension pull
returning 29 distinct days.

### Site totals — 28 days (2026-07-25 → 2026-08-22)

| Metric | Value |
|---|---|
| Clicks | **882** (~31.5/day) |
| Impressions | **185,055** |
| CTR | **0.48%** |
| Avg. position | ~12.4 |

### Top pages — same window

| Page | Clicks | Impressions | CTR | Position |
|---|---|---|---|---|
| ai-frontier.html | 256 | 57,781 | 0.44% | 8.10 |
| baofeng-uv5r-quick-ref.html | 72 | 1,860 | 3.87% | 8.46 |
| brazilian-jiu-jitsu.html | 49 | 2,012 | 2.44% | 17.43 |
| orbital-rockets-comparison.html | 44 | 11,208 | 0.39% | 9.84 |
| shabbat-services-cheatsheet.html | 28 | 1,065 | 2.63% | 9.43 |
| ham-radio-technician.html | 26 | 323 | **8.05%** | 13.95 |
| google-ai-studio-guide.html | 24 | 2,898 | 0.83% | 8.83 |
| starlink-satellite-anatomy.html | 22 | 2,088 | 1.05% | 13.48 |
| ashihara-karate.html | 21 | 3,412 | 0.62% | 8.85 |
| judo.html | 21 | 1,956 | 1.07% | 13.46 |
| operator-loadouts.html | 21 | 1,695 | 1.24% | 8.74 |
| azure-devops.html | 17 | 429 | 3.96% | 20.31 |

`ai-frontier.html` improves for the fifth consecutive pulse (123 → 134 → 158 → 207 → 256 clicks;
position 10.2 → 8.10). The niche-utility CTR pattern holds unchanged: task-shaped pages convert at
2.6–8.1%, broad pages at 0.4–0.6% regardless of position.

### Unclaimed demand — 90 days (2026-05-25 → 2026-08-22)

81 queries with **zero clicks and ≥100 impressions**. Largest items: "martial arts guide" (11,654
impressions @ 5.9 — SERP-feature absorption, resolves the open `martial-arts-cheatsheet` guard-rail
flag as innocent), the month-stamped AI-release family (~2,400 impressions @ 5–12), the New Glenn
head-to-head family (~2,300 @ 6–11), and "eid cheat sheet" (317 @ 8.7). Full triage and the
resulting ten specs: [`TODO/META-niche-utility-batch-2026-08.md`](../TODO/META-niche-utility-batch-2026-08.md).

AI-crawler and GA4 legs not re-pulled this session — no change to the 2026-08-06 figures.
