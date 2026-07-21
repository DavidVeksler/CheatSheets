# SEO progress log

Append-only KPI/measurement log for cheatsheets.davidveksler.com. Newest block on top. Measurement is **pulled, not eyeballed** — Search Console (via the `search-console` MCP) for queries/impressions/clicks/position, and Cloudflare (via the `cloudflare-stats` skill) for traffic/bandwidth.

This is the dated **results** log. Related docs:

- `TODO/seo-planning.md` — the durable SEO working doc (GSC baseline, striking-distance opportunities, decision rules). Strategy lives there; numbers land here.
- `TODO/marketing-campaign-plan.md` — campaign assets, UTM conventions, and the shared-link measurement log.
- `docs/marketing.md` — the marketing quick-path router.

Each entry: date, window covered, source, and the numbers. Keep it terse.

<!-- KPI blocks are appended below this line, newest first -->

## 2026-07-21 — 28-day GSC pulse (2026-06-23 → 2026-07-20)

Source: Search Console API, property `https://cheatsheets.davidveksler.com/`. Pre-checkpoint
pulse (the pre-registered decision checkpoint is 2026-08-06). No title/consolidation changes made
— under the freeze. Top pages by clicks:

| Page | Clicks | Impressions | CTR | Position | Note vs. prior pulse |
|---|---|---|---|---|---|
| ai-frontier.html | 158 | 51,150 | 0.31% | 9.0 | clicks 138→158, position 9.9→9.0 (both improving) |
| baofeng-uv5r-quick-ref.html | 59 | 1,493 | 3.95% | 7.7 | steady |
| orbital-rockets-comparison.html | 31 | 9,897 | 0.31% | 10.0 | steady |
| shabbat-services-cheatsheet.html | 30 | 603 | 4.98% | 8.2 | up |
| ashihara-karate.html | 22 | 2,041 | 1.08% | 8.2 | steady |
| global_cuisine_guide.html | 20 | 1,465 | 1.37% | 12.5 | new entrant to top pages |
| ham-radio-technician.html | 17 | 300 | 5.67% | 9.0 | strong CTR |
| azure-devops.html | 16 | 352 | 4.55% | 20.7 | see striking-distance note |
| yudkowsky-rationality-ai-cheatsheet.html | 10 | 2,824 | 0.35% | 5.9 | good position, low CTR |

- **`ai-frontier.html` trajectory is positive** — clicks and average position both improving across
  the last three pulses; the "frontier ai companies/labs/models/providers/list" query family holds
  positions 2–6. Still the #1 traffic driver by a wide margin.
- **Pillars (shipped 2026-07-15) not yet in the top 40 pages** — expected at ~6 days old; each is on
  its own baseline from launch (see planning doc). Judge after ~28 days.
- **Striking-distance note for the post-2026-08-06 window (do NOT act during the freeze):**
  `azure-devops.html` ranks position 2 with 20% CTR on its head term "azure devops cheat sheet" yet
  sits at page-level position 20.7 across 352 impressions — the head term is won, the long tail is
  not. Several other dev spokes rank far back: `databases.html` 26.6, `dotnet-cheatsheet.html` 24.6,
  `postgresql.html` 22.7 (2,507 impr, 0.16% CTR), `clean-architecture-dotnet.html` 30.7,
  `aws-vs-azure.html` 53.6, `git-scm.html` 51.7. These are content/coverage signals, not listing
  fixes — candidates to review once the freeze lifts.
- **Optimization shipped this pulse (freeze-safe, not a title change):** added the three new pillars
  (`ai-models-compared`, `ai-safety-existential-risk`, `rockets-and-spaceflight`) to `llms.txt`; they
  had been omitted from the AI-crawler discovery index when they launched 2026-07-15.
