# Spec: Red State vs Blue State Economies — The Actual Numbers

**Target file:** `red-vs-blue-state-economies.html`
**Batch:** see `economics-batch-2026-08.md` (sheet 3 of 4 in build order).

## Why this topic

Two measured queries: **"red states vs blue states economy" (5,843 impressions,
incumbent at position 1.5 converting only 2.70%)** and **"total gdp of red vs
blue states" (2,411 impressions, position 1.6, 5.85%)**. The incumbent already
ranks #1–2 and still leaks ~95% of clicks, because what it serves is an
editorial with a thesis. Searchers on this query are split across both tribes
and each side smells the other side's spin instantly.

The angle that wins: **a scoreboard with no thesis.** Every measure that
partisans cite — total GDP, per-capita income, growth, cost-of-living-adjusted
income, taxes, unemployment, migration — in one page, every number sourced and
dated, with the denominator honesty of the batch sibling
(`us-states-vs-countries-gdp.html`). Both sides can cite it; that is the
success condition, not a bug. This is the hardest fight in the batch (incumbent
at position 1.5) and the page only wins by being visibly more trustworthy than
an argument.

## Targeting

- **Primary query:** `red states vs blue states economy` (5,843 impr., pos 1.5 @ 2.70%)
- **Secondary:** `total gdp of red vs blue states` (2,411 impr.),
  `red state economies vs blue state economies`, `do red or blue states pay more taxes`,
  `red state vs blue state migration`, `blue states subsidize red states`
- **Mode:** research / argument-settling. Question H2s matching real queries,
  including the federal balance-of-payments question — it's the most common
  escalation in this argument and omitting it would look evasive.

## Draft title / H1 / meta

- `<title>`: `Red State vs Blue State Economies: The Actual Numbers` (53 chars)
- **H1:** `Red vs Blue State Economies: Every Measure, Sourced`
- **Meta description (draft):**
  `Red states vs blue states compared on real data: total GDP, per-capita income, cost-of-living-adjusted earnings, taxes, growth, migration, and federal balance — every state, every source cited.`

## Reader outcome

The reader can answer any "which states are doing better?" claim by naming the
measure it rests on, quoting the actual figure for that measure, and stating
the one measure that most complicates it — instead of trading totals against
per-capitas past each other.

## Success metric

Organic entries on the primary query plus **citation by both sides**: the page
succeeds when it is linked in arguments as the neutral source. Bookmark/return
traffic and AI answer-engine citation are the KPIs; this page is also a
candidate for the popularity-score feed.

## Content approach

**Classification rule, stated on-page:** red/blue by the 2024 presidential
result (fixed until Nov 2028 — a freshness gift), with a visible list of which
states fall where and a one-line note on states that flipped since 2020. No
"purple" fudging in the headline numbers; a footnote table shows how verdicts
move if the 6 closest states are excluded.

1. **Quick Reference: the scoreboard** (signature element) — one table, ~10
   measure rows × two columns (Red total/avg, Blue total/avg) + a "what this
   measure actually tells you" column: total GDP; GDP per capita; median
   household income; RPP-adjusted median income; real GDP growth (5-yr);
   unemployment; net domestic migration; state+local tax burden; federal
   balance of payments per capita; poverty rate (supplemental measure). Every
   cell a real number with year.
2. **The full 50-state ledger:** every state + DC, columns: 2024 result, GDP,
   GDP per capita, RPP-adjusted per-capita income, 5-yr growth, net domestic
   migration, tax burden. Static-sorted by GDP; works without JS.
3. **The verdict flips table:** ~6 rows showing which side "wins" under each
   measure — the honest core of the page, mirroring the batch's
   measure-flipping method.
4. **Migration deep-dive:** where movers actually go (top-10 gainer/loser
   states with Census figures), and the composition caveat (retirees vs
   workers, income of movers — IRS SOI migration data).
5. **The federal balance question:** "do blue states subsidize red states?"
   answered with the actual balance-of-payments figures (Rockefeller
   Institute), plus the two standard complications (federal salaries/military
   bases; progressive taxation means rich states pay more by design).
6. **Common mistakes** (mandatory): totals vs per-capita (California's economy
   is huge *and* Mississippi comparisons need denominators); ignoring cost of
   living cuts both ways; attributing state outcomes to current governance
   (oil in Alaska, finance in NY predate any incumbent); migration ≠ verdict
   on policy alone (weather, housing supply); cherry-picking the time window;
   treating DC as a state in per-capita rankings.
7. **Related sheets** footer per cross-link map.

## Volatile-facts register

**Overall: VOLATILE.** The classification is stable until Nov 2028; the data
rots annually:
- BEA state GDP + per-capita income + RPPs: annual (re-verify each pass).
- Census net domestic migration: annual, December release.
- Tax Foundation burden figures: annual.
- Rockefeller Institute balance of payments: annual, ~1-yr lag.
- BLS state unemployment: monthly — quote it as "as of <Mon YYYY>".
One prominent "Data years used" block near the top, per-table year tags. On
the weekly-freshness rotation from day one. **Election-cycle hazard:** the
whole classification changes after Nov 2028; diarize a rebuild.

## Index category

`Economics & Politics` (batch decision).

## Reading conditions

Phone, mid-argument, elevated blood pressure, both political tribes. The
scoreboard must fit one phone screen per measure-row group and screenshot
clean at 375 px. Neutrality is a *rendering* requirement too: identical visual
weight for both columns — no red/blue color coding that makes one side look
like the warning color. Print: scoreboard + verdict-flips on page one.

## Cross-link map

- **Internal outbound:** `us-states-vs-countries-gdp.html` (same sources, same
  method — link both ways), `the-household-numbers.html`,
  `housing-comparison.html` (migration section), `index-investing-tax-advantaged.html`
  (tax burden adjacency), `economic-systems-compared.html`.
- **External outbound (subject to `~/Projects/seo-crosslinking/`):** wiki
  concept pages only where a term needs a definition; no archive links forced —
  this page has the weakest natural archive tie in the batch, and a strained
  link is worse than none.

## og:image / shareable artifact

The scoreboard, both columns, dark theme — deliberately neutral palette (see
design). Also the screenshot-this artifact.

## Jurisdiction scope

US-only by construction. All figures USD. Say once that state-level data lags
national data by up to a year.

## Density targets

Scoreboard 10 measures; state ledger 51 rows × 7 data columns; verdict-flips
~6 rows; migration tables 2 × 10 rows; federal-balance table ≥ 10 rows; common
mistakes ≥ 6. Far past the floor.

## Research sources (verify against these, per Rule 1)

BEA (GDP, income, RPPs), Census (population, domestic migration, poverty),
BLS (unemployment), IRS SOI (migration by income), Tax Foundation (burden),
Rockefeller Institute (balance of payments), official state election results
(2024 classification). Primary sources only; never a partisan think-tank
number without the underlying government series.

## Visual design

**Identity: sports scoreboard / box score** — the neutrality metaphor made
visual. Charcoal field, scoreboard-amber numerals in a tabular-figures mono
face, the two columns labeled in *equal-weight neutral tones* (e.g., slate vs
bronze — **not** red vs blue, which pre-loads the verdict color-emotionally;
state the choice in a footnote, it's part of the page's credibility). Light
theme: newsprint box-score. Signature element built first: the scoreboard as a
stadium board. No JS required anywhere; one interactive element max (a CSS-only
highlight of a hovered ledger row).
