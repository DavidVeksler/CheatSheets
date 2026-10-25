# SEO progress log

Append-only KPI log for cheatsheets.davidveksler.com, newest block on top. Each entry: date, window, source, numbers; terse. Strategy lives in [`../TODO/META-seo-planning.md`](../TODO/META-seo-planning.md); shared-link measurement in [`../TODO/marketing-campaign-plan.md`](../TODO/marketing-campaign-plan.md). Older blocks: [`archive/seo-progress-2026.md`](archive/seo-progress-2026.md).

<!-- KPI blocks are appended below this line, newest first -->

## 2026-10-25: Deployed title rounds 1 + 2 (not a measurement pulse)

Deployed 41b6a58 at 12:33 UTC (Worker version 4f1ddd1f, parity smoke pass, live verify OK). Live-checked on
the plain URLs: Starlink title, V3 status card, "How big is a Starlink V3 satellite?" and Flight 14 table
cell; orbital-rockets `#size-chart` SVG and answers, round-1 title. **28-day clocks start today:** re-pull
the 2026-10-24 and 2026-10-25 title tables by page x query on or after **2026-11-22**.

## 2026-10-25: Overnight SEO run (measurement pulse + optimization round)

**GSC, 28 days (2026-09-25 to 10-22) vs prior 28 (08-28 to 09-24), page dimension:** 1,211 clicks /
126,462 impr vs 1,040 / 189,218. Clicks **+16%**; impressions -33%, almost all from `ai-frontier.html`
(66,001 -> 20,488: lost date-stamped fan-out queries like "openai google anthropic ... february 2026" and
#title-* fragment impressions; its head query "frontier ai companies" held at pos ~5). Daily clicks
run 30-45 through October, CTR ~1.0-1.5% (was 0.4-0.6% in August). **Correction:** the 2026-10-24 block's
"222 clicks / 26,358 impressions" was a bad pull; the real 28-day figure is ~1,000-1,200 clicks.

| Page (28d) | Clicks prev -> now | Impr prev -> now | Pos |
|---|---|---|---|
| starlink-satellite-anatomy | 53 -> **238** | 3,982 -> 6,863 | 9.4 -> 7.4 |
| ai-frontier | 266 -> 193 | 66,001 -> 20,488 | 7.3 -> 7.7 |
| baofeng-uv5r-quick-ref | 75 -> 64 | 1,594 -> 1,288 | 6.8 -> 6.0 |
| orbital-rockets-comparison | 46 -> 50 | 7,485 -> 8,771 | 8.2 -> 7.9 |
| lifestyle-calculator | 42 -> 49 | 1,441 -> 2,608 | 9.5 -> 7.6 |
| red-vs-blue-state-economies | 3 -> 25 | 33 -> 710 | 8.4 -> 5.5 |
| fastener-torque-tap-drill | 0 -> 10 | 101 -> 1,004 | 5.2 -> 7.1 |

Starlink's jump tracks Starship Flight 14 (2026-09-28, first 26 V3 satellites); most of its clicks are
anonymized or conversational ("show me picture", "expand on both"), i.e. AI Mode style.

**Category hubs (30-day re-pull, due 10-17):** `/ai-safety` 90 impr, `/philosophy-religion` 53,
`/home-lifestyle` 31, `/security-privacy` 29; 7 hubs have no impressions yet. Two hubs clear the >= 50
bar, so **continue hub investment**. Old `?cat=` URLs still draw ~90 impr (301s working; Google catching up).
"cheat sheet" family: `git cheat sheet` still pos 45-76 (off-page problem); "baofeng uv-5r cheat sheet" pos 1.8-3.

**AI crawlers (Cloudflare, host-filtered, 2026-10-18 to 10-24):** 7,737 AI-agent requests vs 11,129/7d
baseline (2026-08-06). ChatGPT-User 1,391 (was ~64% of baseline, ~7.1k), PerplexityBot 981,
OAI-SearchBot 642, Claude-User 554, DuckAssist 495, ClaudeBot 441, GPTBot 409. The baseline's method
may differ (UA regex over adaptive groups here); re-pull with the same script before reading this as a drop.

**Live technical audit:** all 225 sitemap URLs 200, self-canonical, exactly one H1, valid JSON-LD, no
noindex/X-Robots-Tag; `seo_check.py` 0 failures. `anduril-products.html` 301s to
autonomous-defense-systems (deliberate since 2026-07-09; the planning doc's "stays a 404" rule was stale).

**Changes (pushed, not deployed):**

| Page | Target query family (90d impr @ pos) | Title before -> after |
|---|---|---|
| starlink-satellite-anatomy | starlink v3 satellite size/specs/weight/mass/dimensions (~1,500 @ 6-10) | Starlink Satellite Anatomy: V1-V3 Engineering Specs (2026) -> Starlink V3 Satellite Specs: Size, Mass & V1-V3 Anatomy |
| judo | judo moves 216 @ 13.3, all judo throws 161 @ 9.3 | Judo Guide: Throws, Groundwork and Core Principles -> Judo Throws and Moves: Techniques, Groundwork, Principles |
| brazilian-jiu-jitsu | bjj positions chart 136 @ 8.9, bjj cheat sheet 38 @ 1.3 | Brazilian Jiu-Jitsu: Positions, Guards & Submissions -> BJJ Cheat Sheet: Positions Chart, Guards & Submissions |
| martial-arts-cheatsheet | martial arts moves 408 @ 11.3, moves list 73 @ 8 | Martial Arts Guide: Styles, Techniques, Moves & Comparison -> Martial Arts Guide: Moves List, Styles & Comparison Chart |
| leadership | 15 commitments of conscious leadership 171 @ 18.2 | The 15 Commitments of Conscious Leadership -> ...: Summary & List |
| objectivism | objectivism philosophy 107 @ 8.1 | Objectivism: The Philosophy of Ayn Rand (em dash) A Cheatsheet -> Objectivism: Ayn Rand's Philosophy, Ethics and Politics |
| git-scm | git commands 731 @ 64, git cheat sheet 207 @ 70 | Git Cheatsheet: Commands & Workflows -> Git Cheat Sheet: Commands List and Workflows |
| semiconductor-manufacturing | wafer processing/fabrication/manufacturing (~1,200 @ 40-50) | ...: Wafer to Chip Process Guide -> Semiconductor Manufacturing: Wafer Fabrication Process Flow |
| automotive-innovation-timeline | automotive innovations 204 @ 20.6, "what automotive innovation defined the 1940s?" | ...: From Model T to Tesla -> Automotive Innovations by Decade: Model T to Tesla Timeline |
| privacy-data-broker-opt-out | nuwber opt-out family ~400 @ 22-36, "data broker been verified opt out" 193 @ 22.8 | Privacy: Data Broker Opt-Out Guide -> Data Broker Opt-Out List: Nuwber, Spokeo, Whitepages & More |

Content: Starlink V3 status corrected (first 26 flew 2026-09-28) plus a sourced "How big is a Starlink V3
satellite?" answer; orbital-rockets gets a to-scale size chart, height/diameter table and two direct
answers (title untouched, it changed 10-24) and 5 spec fixes; privacy page gets per-broker h3/h4 headings,
a 21-row summary table and re-verified URLs (Radaris now a court-transfer notice; nuwber.com not resolving).
`llms.txt` was missing 25 catalogued sheets (incl. Starlink) and `llms-full.txt` 21; both fixed and now gated.

**Re-pull 28 days after deploy:** each row above by page x query; guard rail applies (position drop at
flat impressions -> revert that page).

## 2026-10-24: Title round (not a measurement pulse)

GSC 28 days (2026-09-24 to 10-21): 222 clicks / 26,358 impressions. Most zero-click, high-impression
queries on humanoid-robots, meat-temperature-chart, er-triage and javascript-for-architects are long
agent-style fan-out queries (`+usda fsis ...`, `+mdn ...`), not CTR opportunities; left alone. Title
changes aimed at real human queries, so the next pulse reads the break:

| Page | Query it targets (impr, pos) | Title before -> after |
|---|---|---|
| orbital-rockets-comparison | falcon heavy vs starship (240 @ 7.4), starship vs falcon 9 (210 @ 9.6), 0 clicks | Starship vs New Glenn vs Falcon Heavy Size Comparison (2026) -> Falcon Heavy vs Starship vs Falcon 9: Size Comparison |
| ai-frontier | frontier ai companies (374 @ 4.3, 1.6% CTR) | 8 Frontier AI Labs Compared (2026): OpenAI vs Anthropic -> Frontier AI Companies Compared (2026): 8 Labs Ranked |
| ashihara-karate | ashihara kaikan (124 @ 3.8, 0 clicks) | Ashihara Karate: Sabaki, Strikes and Kata Cheatsheet -> Ashihara Karate (Kaikan): Sabaki, Strikes and Kata |

Pushed 2026-10-24, not deployed. Re-pull these three queries 28 days after deploy.

## 2026-09-24: Facet crawl trap closed (not a measurement pulse)

Deployed 04:27 UTC: `conf/nginx/facet-trap.conf` (302 for filter/sort/view URLs with our own
Referer and no `cs_js` cookie), `rel="nofollow"` on facet links, robots.txt `Disallow` for
`shape|fresh|sort|interactive|view`. Before: 664k of 701k weekly requests were facet URLs
(~497k with our Referer, ~117k with none; GoogleOther ~21k). Expect origin requests, log size and
the "direct" bucket in `scripts/referrer_report.py` to drop sharply from this date; do not read it
as lost human traffic. No-Referer facet scrapers are not covered by the 302; re-check their volume
in the next pulse.

## 2026-09-23: Referral-channel baseline (origin logs + 16 months of GSC)

Sources: `scripts/referrer_report.py` over the nginx logs (2026-09-06 → 09-24, 19 days, the full
window logrotate keeps), GSC by date since 2025-05-26, and GA4 `properties/543339529` (readable with
the GSC service account). Cloudflare's free plan has no referrers, and **GA4 only recorded
2026-06-25 → 07-03 (9 days, 1,540 sessions), then went silent**, so nothing keeps referrer history
past ~3 weeks.

GA4's 9 days: direct 909, Google 253, Reddit 168 (data-center-myths launch), DDG 79, Bing 72,
Yahoo 23, ChatGPT 4, Gemini 3. Top landings: /history.php 230, data-center-myths 162, / 145, ai-frontier 140.

| Channel (19 days, human-filtered) | Landings | Share |
|---|---|---|
| Direct / no referrer | 16,733 | 80.7% (inflated by browser-UA scrapers; not trustworthy) |
| Search (Google 2,383, DDG 482, Bing 390, other 183) | 3,438 | 16.6% |
| AI assistants (ChatGPT 345, Gemini 40, Copilot 8, Perplexity 6, other 11) | 410 | 2.0% |
| Reddit | 64 | 0.3% |
| Other sites, social, own network | 79 | 0.4% |

Google in the logs (2,383) is ~4x GSC clicks for the same days (617); for ai-frontier it is 961 vs 166.
The Google-referred hits come from 653 distinct IPs, mostly desktop Chrome, some from Google's own
2001:4860 range, which suggests SERP prefetch/prerender or Discover rather than clicks. Use GSC for
search volume and the logs only for channel mix.

GSC clicks/day by month: 2025-06 5.1, 09 15.4, 11 21.4, 2026-02 24.5, 04 18.7, 06 22.0, 07 25.7,
08 31.9, 09 (1-21) 37.5. All-time top pages: ai-frontier 1,479, anduril-products 1,060 (withdrawn),
orbital-rockets 518, brazilian-jiu-jitsu 507, google-ai-studio 440, baofeng-uv5r-quick-ref 380.
Desktop 66% of clicks; US 44%, then GB, CA, IN, AU.

ChatGPT lands on human-skeleton (141) and ai-accelerator-comparison (122) rather than on the search
winners. Reddit lands on operator-loadouts (24) and the .NET sheets.

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
resulting ten specs: [`archive/niche-utility-batch-2026-08.md`](archive/niche-utility-batch-2026-08.md).

AI-crawler and GA4 legs not re-pulled this session — no change to the 2026-08-06 figures.
