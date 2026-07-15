# TODO: starlink-satellite-anatomy.html

Target file: `starlink-satellite-anatomy.html`

## Why this topic

SpaceX publishes no coherent spec sheet for its satellites. Engineering data is
fragmented across FCC filings, spacex.com update posts, conference talks,
Wikipedia, Grokipedia, and enthusiast Substacks — and it changes every hardware
generation. No single page puts V1.0 → V1.5 → V2 Mini → V2 Mini Optimized → V3
side by side with subsystem-level detail. Aggregation of fragmented, volatile,
high-interest data is the moat. Catalyst: first operational V3 deployment via
Starship Flight 13 (targeted July 16, 2026) will drive a sustained wave of
"starlink v3 specs" queries against stale content.

## Targeting

- Primary query: `starlink satellite specs`
- Secondary queries:
  - `starlink v3 vs v2 mini`
  - `starlink satellite laser links` / `starlink inter-satellite links bandwidth`
  - `starlink hall thruster argon`
  - `how big is a starlink satellite` / `starlink satellite mass`
  - `starlink satellite deployment pez dispenser`
- Mode: RESEARCH (curiosity/reference intent, not crisis). Optimize for
  bookmark-and-return and social sharing, not panic scanning.
- Title: `Starlink Satellite Anatomy: V1 to V3 Engineering Specs (2026)`
- H1: `Starlink Satellite Anatomy — Every Generation, Every Subsystem`
- Meta description (draft, ~170 chars): `Complete Starlink satellite spec
  reference: V1.0 through V3 mass, throughput, laser links, Hall thrusters,
  solar arrays, and deployment — every generation compared.`
- Reader outcome: reader can answer any "what are the actual numbers" question
  about Starlink spacecraft hardware in under 30 seconds, and understands how
  each subsystem evolved and why.
- Success metric: ranks page-1 for `starlink v3 vs v2 mini` within 90 days;
  exploded-view diagram picked up by at least one aggregator/forum thread.

## Volatile-facts register

| Fact | Rating | Notes |
|---|---|---|
| V1.0/V1.5 mass, dims, orbit shells | STABLE | Historical, well documented |
| V2 Mini mass (~800 kg), ~80–100 Gbps downlink | SLOW-DRIFT | "Optimized" variant differs; verify both |
| V3 mass (~2,000 kg), 1 Tbps down / 160–200 Gbps up, ~4 Tbps total | VOLATILE | SpaceX CLAIMS, not measurements. Label as design targets. Pre-launch as of July 2026 |
| V3 solar array power (10–12 kW reported) | VOLATILE | Enthusiast estimate; find primary source or label estimate |
| Laser ISL: count per sat, ~100 Gbps/link, ~9,000 lasers constellation-wide | SLOW-DRIFT | SpaceX conference figures; verify per-generation link counts |
| Thruster: krypton (V1) → argon (V2 Mini) Hall effect; thrust/Isp figures | SLOW-DRIFT | V2 argon thruster: 170 mN / 2,500 s Isp claimed — verify from SpaceX 2023 announcement |
| Constellation size, sats launched per vehicle | VOLATILE | Changes weekly; use "as of <date>" framing and round numbers |
| Orbital shells / VLEO plans | VOLATILE | FCC filings in flux (15,000-sat VLEO application pending) |
| Deorbit/design-life policy (~5 yr, demisable design) | SLOW-DRIFT | |
| Flight 13 / first operational V3 deployment status | VOLATILE | May occur during implementation — check day of publish |

Verification rule: no number ships without a primary or near-primary source
(spacex.com/updates, FCC IBFS filings, SpaceX progress reports, direct Musk/
SpaceX statements). Wikipedia/Grokipedia/Substack figures are leads, not sources.

## Index category

Map to existing category set at implementation time — inspect `category-map.php`.
Likely fits a science/engineering or technology reference bucket; do NOT create
a new category for a single page.

## Jurisdiction / scope

Global; no jurisdiction-specific content. All units metric-first with imperial
in parentheses.

## Reading conditions

Desktop research session and mobile social-referral traffic in equal measure.
Mobile: master table must degrade to horizontally scrollable or stacked cards
at 375px with no overflow. Print: master spec table and anatomy diagram must
survive grayscale printing (this page is plausibly printed as a poster/handout).

## Cross-link map

- Out: satellite-link-budget page (if/when built — "compute the downlink
  yourself"), any existing networking/RF-adjacent pages found in corpus.
- In: from index category page; add reciprocal links only to existing local
  pages where natural.

## Content approach

Quick-reference block (top): single master table, one column per generation
(V1.0, V1.5, V2 Mini, V2 Mini Optimized, V3): launch mass, stowed/deployed
dimensions, solar array area & power, downlink/uplink/total throughput, laser
ISL count & per-link rate, thruster type/propellant/thrust/Isp, launch vehicle,
sats per launch, orbit shell & altitude, design life, first launch date, status.
Target: ~15 rows × 5 generations. This table IS the page.

Sections (fundamentals → working knowledge → edge):
1. **Bus & structure** — flat-panel stackable design rationale, mass growth
   ~260 kg → ~2,000 kg, why Starship is a hard dependency for V3.
2. **Phased-array payload** — Ku/Ka/E-band usage by generation, beamforming,
   digital vs analog arrays, direct-to-cell antenna on V2 Mini DTC variants.
   Table: frequency bands by generation and function (user/gateway/ISL/TT&C).
3. **Laser inter-satellite links** — link count per sat, ~100 Gbps per link,
   ~5,400 km max range figures, mesh routing implications (ground-station
   independence), constellation-wide laser count.
4. **Propulsion** — Hall-effect thruster evolution: krypton → argon economics
   (cost/kg comparison table vs xenon), thrust/Isp figures, what stationkeeping
   and collision-avoidance duty actually looks like (autonomous maneuver counts).
5. **Power** — solar array evolution, single vs dual arrays, kW by generation,
   eclipse battery operation.
6. **Deployment & lifecycle** — Falcon 9 stack-and-tension-rod release vs
   Starship PEZ dispenser mechanics, checkout/orbit-raising phases, 5-year life,
   demisable deorbit design.
7. **Common misconceptions** — anti-pattern block: "V3 = bigger V2" (full
   silicon refresh), "throughput = user speed" (terminal + plan limited),
   "satellites connect users directly to each other," conflating dish
   generations with satellite generations.

Expected major tables: master spec table (~15×5), frequency-band table (~8 rows),
propellant economics table (~4 rows), laser ISL by generation (~5 rows).

## Research sources (verify during implementation — do NOT recall from memory)

- spacex.com/updates (2026 progress posts — V3 capacity claims, PEZ dispenser)
- FCC IBFS filings (Gen2 modification, pending VLEO application)
- SpaceX Starlink spec PDFs at starlink.com/public-files (terminal side, for
  cross-reference only)
- Jonathan McDowell's planet4589.org Starlink stats (launch counts, orbit data —
  best independent source)
- SpaceX 2023 argon Hall thruster announcement (thrust/Isp)
- Flight 13 outcome — MUST check on publish day; page must state actual V3
  deployment status, not "expected"

Must-not-recall facts: every number in the master table, all FCC filing
statuses, constellation counts, Flight 13 outcome.

## Visual design

- Aesthetic: dark "mission control" palette — near-black background, cool grays,
  single accent (Starlink-ish cyan or signal amber) for data highlights. Dense,
  technical, no consumer-blog softness.
- Signature visual: annotated exploded-view SVG of a V3 satellite — solar
  arrays, phased arrays, laser terminals, Hall thruster, avionics — each callout
  linking to its section. Build this FIRST; it is the shareable artifact and
  the og:image source.
- Secondary visual: to-scale silhouette lineup of all five generations next to
  a human figure (mass/size growth at a glance).
- og:image: 1200x630 screenshot of the exploded view over the dark palette.
- Mobile: exploded view degrades to stacked callout cards; master table scrolls
  horizontally with sticky first column.
- Print: light-background print stylesheet; diagram and master table on page 1.