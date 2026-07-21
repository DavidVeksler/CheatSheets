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

### Interim AI-crawler pull — Cloudflare, 7 days (2026-07-14 → 2026-07-20)

Pulled 2026-07-21, host-filtered to `cheatsheets.davidveksler.com`, zone `davidveksler.com` (Free).
Method note: the free plan caps `httpRequestsAdaptiveGroups` at a 1-day range and ~8-day retention,
so this is 7 individual 1-day queries summed (2026-07-13 had already rolled off). Interim datapoint
between the 2026-07-11 baseline and the 2026-08-06 checkpoint, captured now because the window
otherwise disappears.

| User agent | Requests (7d) | vs. 2026-07-11 baseline |
|---|---|---|
| ChatGPT-User | 4,925 | down (6,945) |
| Bytespider | 1,029 | ~flat (1,184) |
| PerplexityBot | 651 | **up ~2x (341)** |
| Amazonbot | 415 | down (600) |
| Applebot | 186 | down (278) |
| DuckAssistBot | 80 | up (65) |
| GPTBot | 51 | down (102) |
| ClaudeBot | 45 | down (135) |
| Claude-User | 35 | down (63) |
| OAI-SearchBot | 29 | down (186) |
| GoogleOther | 19 | down (620) |
| MistralAI | 16 | ~flat |
| **TOTAL** | **7,481 (~1,068/day)** | down from ~10,573 (~1,510/day) |

- **Total AI run-rate is down ~30% week-over-week**, driven mostly by ChatGPT-User and the
  Google/OAI search-indexers; **PerplexityBot roughly doubled**. Treat as one noisy week, not a trend —
  ChatGPT-User volume tracks how often pages surface in live answers and swings. The real read comes
  at the 2026-08-06 checkpoint against the same method.
- `ai-frontier.html` remains the #1 fetched page (1,574 ChatGPT-User fetches), followed by `/` (656),
  `humanoid-robots.html` (440), `bitcoin-whitepaper.html` (244), `orbital-rockets-comparison.html`
  (190), `boom-supersonic.html` (182). The citability play still concentrates on the same flagships.

### Infra verification — 2026-07-21

- **404 handling is fixed:** `/no-such-page-xyz-test` returns `404 text/html`; `robots.txt` returns
  `200 text/plain`. The AGENTS.md known-issue (404s served as 200 homepage HTML) is resolved live.
- **Caching headers live:** cheatsheet HTML sends `cache-control: public, max-age=1800`; images send a
  long-lived cache (`max-age=315360000`). Both fine; the image TTL differs from the documented
  `max-age=604800, immutable` but is benign.
- **`llms.txt` fix is committed but NOT yet live** — the live file still shows 0 of the 3 new pillars.
  Needs a deploy to reach the crawlers.
- **Checkpoint scheduled task not verifiable from this session.** The macOS `scheduled-tasks` MCP
  reports zero tasks; the routine fleet (incl. `cheatsheets-pivot-checkpoint`) lives in the Windows
  desktop-app registry, which a darwin session can't see. Confirm on the Windows box that the
  one-time 2026-08-06 task is still present and enabled. Not recreated here (duplicate risk).
