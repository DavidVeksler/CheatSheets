# Spec: US States vs Countries — GDP Comparisons Done Right

**Target file:** `us-states-vs-countries-gdp.html`
**Batch:** see `economics-batch-2026-08.md` (sheet 2 of 4 in build order).

## Why this topic

"Mississippi gdp per capita vs uk" carries **5,028 impressions with the
incumbent at position 4.3 and 1.89% CTR** — a viral-debate query ("America's
poorest state is richer than Britain") that resurfaces every few months, and
every ranking page answers it with one cherry-picked measure. The honest answer
is that the verdict depends on the measure, and *showing all the measures side
by side with real numbers* is exactly what none of the incumbents do and
exactly what this site's format does.

The angle: **a methodology sheet wearing a listicle's clothes.** The reader
comes for "is Mississippi richer than the UK?"; the page answers it five ways,
shows where the answer flips, and leaves the reader permanently harder to fool
by any single-measure comparison. That skill transfers to every "California
would be the world's 4th largest economy" headline.

## Targeting

- **Primary query:** `mississippi gdp per capita vs uk` (5,028 impr., incumbent pos 4.3 @ 1.89%)
- **Secondary:** `us states compared to countries gdp`, `california gdp vs countries`,
  `is mississippi richer than the uk`, `texas economy compared to countries`,
  `us state gdp vs country gdp`
- **Mode:** research / argument-settling. H2s in question form matching real
  phrasings: "Is Mississippi really richer than the UK?", "Which countries
  match each US state's economy?"

## Draft title / H1 / meta

- `<title>`: `Is Mississippi Richer Than the UK? US States vs Countries` (57 chars)
- **H1:** `US States vs National Economies: the Honest Comparison`
- **Meta description (draft):**
  `US state GDP compared to whole countries, done honestly: nominal, PPP, price levels, and consumption measures — with the Mississippi vs UK question worked step by step to a real verdict.`

## Reader outcome

The reader can answer "is state X richer than country Y?" with the right
measure for the question being asked, cite the actual figures, and name the
two biggest distortions (price levels, and GDP ≠ household living standards)
in any state-vs-country comparison they meet in the wild.

## Success metric

Organic entries on the primary query, plus share/screenshot traffic on the
worked example (this is a link-drop page for internet arguments — bookmark and
return-direct traffic count). AI answer-engine citation on the primary query.

## Content approach

1. **Quick Reference: the verdict box** — the Mississippi vs UK answer under
   each of 5 measures in one small table (nominal GDP per capita; PPP-adjusted;
   RPP-adjusted state figure; AIC per capita; median equivalised household
   disposable income), each row a real number pair, a winner, and a one-line
   "what this measure actually measures".
2. **The worked example** (signature element): Mississippi vs UK stepped
   through measure by measure — start from BEA state GDP and ONS/IMF UK
   figures, apply each adjustment with the arithmetic visible, watch the gap
   move. Every step lands on a real number (Rule 3). End with the honest
   verdict sentence for each version of the question ("produces more per
   person" vs "lives better").
3. **The big match table:** all 50 states + DC → the nearest whole national
   economy by nominal GDP (the classic map, as a verified table with both
   figures shown, not just the country name). 51 rows.
4. **States vs G20 per-capita table:** ~15 large states and the G20 economies
   interleaved and ranked under nominal and PPP columns side by side, so the
   re-ranking between measures is visible in one scan.
5. **Why the measures disagree** — 5–6 entries: market exchange rates vs PPP;
   regional price parities within the US; GDP counts production not
   consumption (Ireland's distortion as the canonical example, with the
   modified-GNI number); healthcare and government services accounting; hours
   worked; mean vs median.
6. **Common mistakes** (mandatory): comparing a state's nominal GDP to a
   country's PPP figure (the most common internet sin); treating GDP per
   capita as take-home income; ignoring that US states share a currency so
   PPP applies differently; "California 4th largest economy" without saying
   nominal; using stale IMF year-mismatched figures.
7. **Related sheets** footer per cross-link map.

## Volatile-facts register

**Overall: VOLATILE — annual data.** Every figure rots on a schedule:
- BEA state GDP and RPPs: annual releases (RPPs ~December, GDP revised
  quarterly) — re-verify both at each freshness pass.
- IMF WEO country figures: April + October updates.
- OECD AIC / household income: annual, ~18-month lag; use the latest common
  year and say which year every table uses.
Tag every table with its data year in the header, not per-cell. The page
carries one prominent "All figures: <year>, sources below" line. This page
should be on the weekly-freshness rotation from day one.

## Index category

`Economics & Politics` (batch decision).

## Reading conditions

Phone, mid-argument, possibly in a comment thread — the verdict box must be
the first screen and screenshot-clean at 375 px. Tables scroll horizontally in
wrappers. Print: verdict box + worked example on page one.

## Cross-link map

- **Internal outbound:** `red-vs-blue-state-economies.html` (batch sibling,
  same data sources — link both ways), `the-household-numbers.html`,
  `housing-comparison.html` (cost-of-living adjacency),
  `economic-systems-compared.html`.
- **External outbound (subject to `~/Projects/seo-crosslinking/`):** wiki
  concept pages where terms are used (e.g., Purchasing power parity if the
  wiki holds it); archive links only if a cited primary text is actually held.

## og:image / shareable artifact

The verdict box (5 measures, 5 verdicts) rendered as a card — it is both the
social preview and the screenshot-this artifact. Dark theme.

## Jurisdiction scope

US states vs OECD/G20 countries. All dollar figures USD; state your exchange
rate/PPP source per table. Non-US readers are half the audience (it's their
country being compared) — never write "our states".

## Density targets

Verdict box 5 rows; worked example ≥ 5 fully-computed steps; match table 51
rows; per-capita interleave ~35 rows; measure explanations 5–6 entries; common
mistakes ≥ 5. Well past the floor.

## Research sources (verify against these, per Rule 1)

BEA (state GDP, RPPs), Census (population), IMF WEO and World Bank (country
GDP, nominal and PPP), OECD (AIC, household disposable income, price levels),
ONS (UK figures), CSO Ireland (modified GNI). Primary statistical agencies
only — never a Wikipedia table or a news article as the cited source.

## Visual design

**Identity: split-flap departures board / international arrivals** — the page
is about crossing borders with numbers. Dark navy board, amber monospaced
figures, flag-free (no flag emoji clutter — country names in small caps).
Signature element built first: the worked example as a sequence of board rows
that "flip" between measures (CSS-only, reduced-motion gated; static stacked
rows when motion is off). Light theme: airport-signage white with the same
type system. One interactive element max: a measure-picker for the big table
is tempting — **don't**; show columns side by side instead, it works without
JS and the side-by-side re-ranking is the whole lesson.
