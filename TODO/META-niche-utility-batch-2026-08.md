# Batch: Niche-utility cheatsheets — 2026-08 (10 specs)

Brainstormed and specced 2026-08-24 from a fresh Search Console pull. Every candidate here
had to pass `TODO/README.md` **Rule 0** (the niche-utility test) before it got a spec: a page
a person keeps open *while doing a task*, not an overview an AI chat already answered.

Per-spec files in this folder:

| # | Spec | Target file | Category | Shape |
|---|---|---|---|---|
| 1 | [gmrs-frs-murs-card.md](gmrs-frs-murs-card.md) | `gmrs-frs-murs-card.html` | Radio | Device programming |
| 2 | [meshtastic-field-config.md](meshtastic-field-config.md) | `meshtastic-field-config.html` | Radio | Device programming |
| 3 | [high-holiday-services.md](high-holiday-services.md) | `high-holiday-services-cheatsheet.html` | Philosophy & Religion | Ritual follow-along |
| 4 | [eid-prayer-cheatsheet.md](eid-prayer-cheatsheet.md) | `eid-prayer-cheatsheet.html` | Philosophy & Religion | Ritual follow-along |
| 5 | [pet-poison-triage.md](pet-poison-triage.md) | `pet-poison-triage.html` | Health & Fitness | Field diagnostics |
| 6 | [fastener-torque-tap-drill.md](fastener-torque-tap-drill.md) | `fastener-torque-tap-drill.html` | Engineering & Science | Dense numeric table |
| 7 | [connector-pinouts.md](connector-pinouts.md) | `connector-pinouts.html` | Engineering & Science | Dense numeric table |
| 8 | [appliance-error-codes.md](appliance-error-codes.md) | `appliance-error-codes.html` | Home & Lifestyle | Field diagnostics |
| 9 | [meat-temperature-chart.md](meat-temperature-chart.md) | `meat-temperature-chart.html` | Home & Lifestyle | Dense numeric table |
| 10 | [ai-model-release-log.md](ai-model-release-log.md) | `ai-model-release-log.html` | AI & Safety | Dated register |

## The SEO research behind this batch

**Data.** Google Search Console, property `https://cheatsheets.davidveksler.com/`, pulled
2026-08-24 with the new [`scripts/gsc_query.py`](../scripts/gsc_query.py). Two windows:
28 days (2026-07-25 → 2026-08-22) for site health, 90 days (2026-05-25 → 2026-08-22,
10,257 query rows) for demand mining.

⚠️ **Correction to the 2026-08-12 tooling note in `seo-planning.md`: GSC range queries work
again.** A `dimensions:["date"]` pull returns 29 distinct days with distinct totals, so the
"everything collapses to 2026-08-10" failure has cleared. Range numbers are trustworthy again.

**Site health, 28 days:** 882 clicks / 185,055 impressions / 0.48% CTR. `ai-frontier.html` is
still compounding — 256 clicks / 57,781 impressions / position **8.10**, up from 123 → 134 →
158 → 207 across the prior pulses. Niche-utility pages continue to hold the CTR crown:
`ham-radio-technician` 8.05%, `azure-devops` 3.96%, `baofeng-uv5r-quick-ref` 3.87%,
`shabbat-services-cheatsheet` 2.63%, `veterinary-diagnostics` 2.61%. `brazilian-jiu-jitsu`
tripled to 49 clicks and `starlink-satellite-anatomy` (a 2026-07 build) is already at 22.

**The demand-mining method.** Rank the 90-day query set by *impressions* rather than clicks,
then keep only rows with **zero clicks and ≥100 impressions** — queries where Google already
shows the site and nobody arrives. 81 such queries. Three things fall out of that list:

1. **Unclaimed demand a new page can serve** → the specs in this batch.
2. **Demand an existing page half-serves** → optimizations, listed below. Not new pages.
3. **Demand nothing can serve** → SERP-feature / AI-Overview absorption. Do not chase.

### Evidence per spec

| Spec | Measured or structural evidence |
|---|---|
| 1. GMRS/FRS/MURS | Cluster proof, not query proof: the Radio category owns the site's best CTR (`ham-radio-technician` 8.05%, `baofeng-uv5r-quick-ref` 3.87%) and "baofeng uv-5r programming cheat sheet" alone is 760 impr/90d at position 6.5. GMRS/FRS is the same buyer one step earlier — the unlicensed radio already in the drawer. |
| 2. Meshtastic | Same cluster, zero site coverage; the config-vs-range tradeoff is exactly the "keep open while programming the device" shape that wins here. An off-GSC bet, judged on its own baseline. |
| 3. High Holidays | `shabbat-services-cheatsheet.html` is the model: 1,065 impressions, **2.63% CTR** from a 2,762-word page. Seasonal: Rosh Hashanah 2026 begins sundown **Fri 2026-09-11**, Yom Kippur sundown **Sun 2026-09-20**. Ship by 2026-09-01 or wait a year. |
| 4. Eid prayer | `"eid cheat sheet"` — **317 impressions / 90d, position 8.7, zero clicks**, currently landing on the broad `islam.html`. Google already associates the site with the query; nothing here answers it in follow-along form. |
| 5. Pet poison | `veterinary-diagnostics.html` earns the site's highest CTR class on tiny volume; its crisis-mode sibling ("what dose is actually dangerous") is missing. Single-toxin chocolate calculators are saturated — the gap is the **multi-toxin, ER-or-not** card. |
| 6. Fasteners | Structural: shop-wall reference, permanent demand, no site coverage; the nearest neighbours (`engineering-metals-selection`, `hiring-a-contractor`, `auto-repair-decoder`) all point at a lookup this page would terminate. |
| 7. Pinouts | Structural, same argument; also the one dev-adjacent page in the batch that does **not** depend on the site's weak dev-cluster authority, because it competes on table density rather than tutorial depth. |
| 8. Appliance codes | `"samsung bespoke oven microwave combo instructions"` sits at **position 1.2 with zero clicks** (188 impressions) — appliance-manual queries rank trivially for this site. The cross-brand decoder multiplies that shape across five brands. |
| 9. Meat temps | `cooking-guide.html` is 15,663 words with **no lookup artifact**: 4 clicks / 1,903 impressions at position 20.1. The card is the missing entry point, not more prose. |
| 10. AI release log | The largest single unclaimed pool on the site: month-stamped release queries — "ai frontier models developments last 24 hours" (1,054), "frontier ai model releases july 2026" (347), "latest frontier ai models june 2026" (215), "frontier ai models 2026" (202), "top frontier ai models july 2026" (159), "latest frontier ai models july 2026" (149), "current frontier ai models july 2026" (132), "frontier ai model releases june 2026" (111) — ≈2,400 impressions/90d at positions 5–12, **all zero clicks**. |

### Optimizations found, deliberately NOT built as new pages

These belong in `seo-planning.md`'s work queue, not in this folder:

- **`martial-arts-cheatsheet.html` — "martial arts guide": 11,654 impressions, position 5.9,
  0 clicks over 90 days.** The largest single line item in the entire pull. It also settles the
  2026-08-06 guard-rail flag: the impressions never vanished, the 28-day window just clipped
  them. Zero clicks at position 5.9 is the `judo.html` SERP-feature signature, so **diagnose
  before touching the title** — the flagged rewrite looks innocent.
- **New Glenn head-to-head family:** ~2,300 impressions / 90d, zero clicks, positions 6–11, all
  landing on `orbital-rockets-comparison.html` — which already carries "New Glenn" in its title.
  This is an answer-shape gap (searchers want side-by-side dimensions and a to-scale visual), not
  a title gap, and **not** a new page: a second rocket-size page would cannibalize one that
  already ranks 6th. Add the head-to-head block there instead.
- **`privacy-data-broker-opt-out.html`:** "data broker been verified opt out" (239 impressions,
  position 28.6) and "www.checkpeople.com/opt-out" (121, position 48.3) — the page has exactly
  one H2. Per-broker sections carrying the literal opt-out URL are what these searchers want.
- **`islam.html`:** ranks position 2.0–2.5 on "sharia law" / "sharia law rules" / "what is sharia
  law" (726 impressions combined) with zero clicks. Almost certainly SERP-feature absorption;
  measure before investing.
- **Dev spokes** ("git commands" 504 impressions @ 61.3, "c# keywords cheat sheet" 378 @ 27.9,
  "aws vs azure services" 212 @ 62.5, ".net clean architecture" 199 @ 39.6): unchanged diagnosis
  from `dev-spoke-content-plan.md` — authority, not titles. No new dev page is in this batch for
  precisely that reason.

### Candidates rejected

- **Rocket size comparison page** — cannibalizes `orbital-rockets-comparison.html` (see above).
- **Wire gauge / NEC ampacity card** — too close to `home-electrical-basics.html`; fold the
  numeric table into that page instead.
- **Furnace/HVAC blink codes** — good shape, but two "error code decoder" builds in one batch is
  a formula, not a batch. Next batch, timed for October.
- **Blackjack basic strategy / poker odds card** — passes the utility test, fails the site's
  subject identity.
- **A second AI-labs list** — explicitly forbidden by `seo-planning.md`. Spec 10 is a dated
  chronological register, and its Targeting section pins the query diff against `ai-frontier`.

## Build order

1. **`high-holiday-services-cheatsheet.html` — hard deadline 2026-09-01** (seasonal window).
2. `ai-model-release-log.html` — largest measured unclaimed demand; every week unbuilt is demand
   spent.
3. `gmrs-frs-murs-card.html` — strongest cluster fit, cheapest verification.
4. `pet-poison-triage.html`, `meat-temperature-chart.html` — evergreen crisis/kitchen shapes.
5. `fastener-torque-tap-drill.html`, `connector-pinouts.html` — bench pair, shared design
   language; build them back to back.
6. `appliance-error-codes.html`, `meshtastic-field-config.html`, `eid-prayer-cheatsheet.html` —
   Eid can wait for the pre-Ramadan window (Ramadan 2027 begins ≈ Feb 2027; ship by January).

One page per commit with its `images/*.png` preview, its `category-map.php` line, and its
`llms.txt` entry, per AGENTS.md. Each page is measured on **its own baseline from its launch
date** — never folded into the WP1 or `ai-frontier` comparisons.
