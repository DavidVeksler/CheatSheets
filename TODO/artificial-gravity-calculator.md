# Spec: Artificial gravity calculator and rotating-habitat reference

**Target:** `artificial-gravity-calculator.html`
**Status:** specification only; not yet traffic-ranked.
**Purpose:** a spin-gravity calculator plus a dense design reference (formulas, comfort limits, historical designs, the odd physics of living in spin). The secondary goal is cross-promotion: every section uses **Concordia** (https://concordia.davidveksler.com/), David's browser-explorable 1 g space settlement, as its worked example and links to the place on that site where the reader can see it.

## Why this topic

- **Passes Rule 0 twice.** It is a calculator (people building a game, a story, a class exercise or a settlement design keep it open while they size a rotor) and a comparison table with exact specs (Stanford torus vs Bernal sphere vs O'Neill cylinder vs Kalpana One). AI answers get the arithmetic right but routinely mangle the comfort limits, mix up which limit is SP-413 and which is Globus and Hall, and invent design dimensions. A verified side-by-side table with sources beats them.
- **Fills a gap in the cluster.** `space-habitats-life-support.html` covers air, water, heat and shielding and mentions rotation once. Nothing on the site covers spin gravity.
- **Why Concordia makes the page better, not just promoted.** A worked example that runs through every section (one rotor, 2,500 m radius, 0.598 rpm, 1 g) is easier to learn from than abstract formulas, and the reader can then walk the street, ride the train that weighs 0.66 g, or climb to the 0.82 g sky in the browser. The page must be fully useful without a single click out.

## Honesty contract (read before writing a word)

- **Concordia is a design study set in 2045, not a real or planned project.** Every Concordia number carries a small `design value` tag (a pill or superscript, styled once). One sentence near the top says what it is: a fully modelled settlement you can explore in a browser, built to show what the physics on this page looks like at city scale. No "planned", "proposed by", "will be built".
- **Real physics and real history cite sources** (Rule 1 applies to both: numbers in this spec are anchors). Concordia numbers come only from the Habitat repo's `docs/site/facts.md` (sections 2, 3, 5, 15) and the site's widget core `site/js/widgets/core.mjs`; when the two disagree with the live site, the live site wins.
- **Leave out the station's economy and backstory** (AGI, charter, dividends). That lore is speculative and would cost the page its credibility. Physics, geometry and design only.
- One clear statement of the model's limits: rigid rotor, no air drag on falling objects, uniform spin.

## Targeting

- **Primary query:** artificial gravity calculator.
- **Secondary queries:** how fast does a space station need to spin for 1g; artificial gravity rpm comfort; o'neill cylinder vs stanford torus; rotating space station gravity formula; coriolis effect rotating space station; o'neill cylinder size.
- **Intent:** research mode, low stress. Readers: SF writers and worldbuilders, game designers and players (Space Engineers, KSP mods), physics students and teachers, space settlement enthusiasts (NSS readers).
- **Scope:** worldwide; physics has no jurisdiction. SI units first, with feet and mph in the calculator output as a secondary line.

## Draft title / H1 / meta

- `<title>`: `Artificial Gravity Calculator: Spin Rate, RPM and Comfort` (57 chars)
- **H1:** `Artificial gravity: how fast to spin, and how big to build`
- **Meta description (draft, 150 to 200):** `Calculate spin rate, rim speed, gravity gradient and Coriolis for any rotating habitat, check it against comfort limits, and compare the Stanford torus, O'Neill cylinder and Concordia.`
- Question-shaped H2s where natural: "How fast must it spin for 1 g?", "How much spin can people tolerate?", "Why is the floor curved upward?"

## Reader outcome

Given a radius or a spin rate, the reader can compute the gravity, rim speed, head-to-foot gradient and walking Coriolis, place the design in a published comfort band, explain why a small centrifuge feels nothing like a large rotor, and compare it against five historical designs and Concordia.

## Success metric

- Organic entries on the primary and secondary queries (Search Console, baseline in `docs/seo-progress.md` at launch).
- **Referral clicks to concordia.davidveksler.com.** Outbound Concordia links carry `?utm_source=cheatsheets&utm_medium=referral&utm_campaign=concordia_crosspromo&utm_content=<section-slug>` (outbound links only; the "no UTMs in internal links" rule in `marketing-campaign-plan.md` still holds). Measure with the `cloudflare-stats` skill on the Concordia zone: requests whose query string or referrer shows the campaign. Confirm at build that the Concordia zone exposes query strings or referrer hosts in GraphQL; if not, report referrer-host counts only.
- Shares of the signature chart.

## Content approach

Order is fixed; the calculator sits immediately after Quick Reference so a searcher on the primary query sees it in the first screen on desktop.

1. **Quick Reference** (8 to 10 lines). The formulas, each with one Concordia value:
   - g = ω²r; rpm = 60ω / 2π; rim speed v = ωr; period T = 2π / ω.
   - Gravity at height h above the floor: g(h) = g₀ (1 − h / R).
   - Head-to-foot gradient: Δg / g = height / R.
   - Coriolis on a walker: a = 2ωv.
   - Apparent weight on a train moving along the rim: (ωR ± v)² / R.
   - Rules of thumb (radius needed for 1 g; anchors computed with g₀ = 9.80665): 1 rpm 894 m; 2 rpm 224 m; 3 rpm 99 m; 4 rpm 56 m; 6 rpm 25 m; 10 rpm 9 m. Globus and Hall's table gives 895.47 m at 1 rpm (a slightly different g); use g₀ = 9.80665 throughout the page and say so once.
   - Concordia line: R 2,500 m, ω 0.0626 rad/s, 0.598 rpm, period about 100.3 s, rim speed about 156.6 m/s, 1.0 g at the ground (`design value`).
2. **Spin calculator + "spin chart"** (the signature element; see Visual design). Inputs: radius (m) and either spin rate (rpm) or target gravity (g); person height (default 1.8 m); walking speed (default 1.4 m/s). Outputs: ω, rpm, period, rim speed, rim g, head-to-foot gradient (percent), walking Coriolis (m/s² and as a percent of local g), the Globus and Hall band, an SP-413 flag (above 1 rpm), and "radius for 1 g at this rpm". Preset chips: every row of the comparison table. The chart plots radius (log x) against rpm (log y) with iso-g lines (0.1, 0.38 Mars, 0.5, 1 g), the comfort bands shaded, every design as a labelled dot, and the reader's current design as a live marker.
3. **How spin makes weight.** Short mental model: the floor pushes you toward the axis; there is no force pulling you "down"; what you feel is the floor's push. Worked example: Concordia 2,500 m at 0.0626 rad/s gives 0.999 g. Small vs large: a 10 m centrifuge at 1 g spins at 9.5 rpm with an 18 percent head-to-foot gradient; Concordia's gradient is 0.07 percent. Link: Concordia `/science/artificial-gravity/`.
4. **Gravity fades with height.** Table for a Concordia rotor: ground 1.00 g; 250 m 0.90 g; 450 m (the artificial sky) 0.82 g; 1,000 m 0.60 g; 1,250 m 0.50 g; 2,000 m 0.20 g; axis 0 g. Air pressure also falls toward the axis in a spinning atmosphere: about 95 percent of ground pressure at the sky, about 86 percent at the axis (isothermal model, `design value`). Link: `/explore/?overlay=gravity` (engineer mode, gravity overlay).
5. **Coriolis, gradients and the inner ear.** Why turning your head at high rpm causes nausea (cross-coupled stimulation of the semicircular canals), why walking spinward makes you heavier and antispinward lighter, why the effect scales with ω and therefore shrinks with radius. Worked example: walking 1.4 m/s at Concordia gives Coriolis of 0.018 g (1.8 percent of weight); the same walk at 2 rpm (224 m radius) gives 0.06 g. Link: `/discover/train-weight/`.
6. **How much spin can people tolerate?** Four tables (anchors and URLs in "Sourced anchors" below):
   - **NASA SP-413 (1975 study, published 1977) design criteria** from chapters 3 and 4: gravity 0.95 ± 0.05 g (chapter 3 text says "between 0.9 g and 1 g"; the web transcription of Table 3-3 has a typo, "± 0.5"); 1 rpm upper limit for the principal living quarters; adaptation possible below 3 rpm; Coriolis example (a 0.55 m jump lands about 5.3 cm to the side). SP-413 sets **no** gravity-gradient limit: say so rather than invent one. Chapter 4's relaxed case (0.85 ± 0.15 g at 1.9 rpm) is one line.
   - **Globus and Hall 2017, "Space Settlement Population Rotation Tolerance"**, the four recommendations (2, 4, 6, 30 rpm), plus the paper's radius-for-1 g table. Note that the paper calls these conservative because the data come from short radii, and that it calls 2 rpm "universally agreed to be good" across five historical comfort charts.
   - **The five historical comfort charts** as tabulated on Hall's SpinCalc (Hill and Schnitzer 1962, Gilruth 1969, Gordon and Gervais 1969, Stone 1973, Cramer 1985): minimum radius, maximum rpm, maximum rim speed, g range, with "not stated" cells kept as such. The Hill and Schnitzer rim-speed cell is ambiguous on the page: verify or mark it.
   - **Experiments behind those numbers** (5 to 6 rows): Pensacola Slow Rotation Room (Reason and Graybiel 1969: 15 ft room, stepped to 10 rpm, six of ten subjects reached it, "rotation may safely commence at 2 rpm"); Graybiel 1977 rpm findings (1.0, 3.0, 5.4, 10 rpm; cite as quoted by Hall unless the original proceedings are found); Lackner and DiZio 2003 (adaptation to 10 rpm with practice); Gemini XI tether (1966, about 0.00015 g; the flown rotation rate is unverified, so omit it); NASA/DLR short-radius centrifuge bed-rest pilot (21 days, encouraging, not conclusive); JAXA mouse centrifuge on the ISS (Shiba 2017: 1 g group kept bone and muscle that the microgravity group lost).
7. **Rotating habitat designs compared** (the major table; see Density targets). Columns: design, year and source, shape and size, radius (m), rpm, rim g, rim speed (m/s), population, shielding, Globus and Hall band. Rows, oldest first (anchors below; "derived" means computed from the sourced radius and rpm and marked as such on the page):
   - **O'Neill cylinder, 1974 "Model 4"** (*Physics Today*): radius 3,200 m, length 32 km, period 114 s (0.526 rpm derived), Earth-normal, 0.2 to 20 million, self-shielded by atmosphere, soil and structure (7.5 t/m² averaged). Note the paper's own conflict: text says about 16 mi long, Table 1 says 32 km. Below the main table, O'Neill's four-stage ladder (Models 1 to 4: 100 m / 21 s / 10,000 up to 3,200 m / 114 s / 20 million) as a small sub-table: it is the cleanest illustration of "comfort pushes radius up".
   - **Stanford torus** (SP-413): major radius 830 m, tube 130 m (65 m minor radius, outer 895 m), 1 rpm, 0.95 ± 0.05 g design, 10,000 people, about 10 Mt non-rotating slag shield (4.5 t/m²); six spokes.
   - **Island One / Bernal sphere** (1976 to 1977 Ames study): sphere about a mile in circumference (radius about 256 m derived), about 1.9 rpm, Earth-normal at the equator falling to zero at the poles, about 10,000 people, non-rotating slag shell (tonnage not found; "not stated"). The common "500 m diameter" figure appears only in Wikipedia mirrors: do not use it unless a primary source turns up.
   - **Island Three** (*The High Frontier*, 1976): counter-rotating pair, each about 20 mi long and 4 mi in diameter, several million people; rpm "not stated" (do not reuse the 1974 period without saying so).
   - **Kalpana One** (Globus and others, 2007 revision): cylinder, radius 250 m, length 325 m, capped at 2 rpm (1.89 rpm derived for 1 g), 1 g at the hull, 3,000 people, up to 10 t/m² regolith inside the hull, about 7 Mt.
   - **Concordia** (design study, set in 2045): four rotors, each radius 2,500 m, length 2,500 m, 0.598 rpm, 1.0 g, about 1 to 1.2 million people in all, plus the counter-rotating industrial rotor (2,300 m, about 0.42 rpm, about 0.45 g) as a sub-row (`design value`; facts.md section 2).
   - **Optional rows, only if sourced at build:** von Braun wheel (1952 *Collier's*), Nautilus-X (2011; it never flew and no dimensions were found). Drop them rather than ship anchors.
   - **Footnote, Bernal 1929:** J. D. Bernal's sphere in *The World, the Flesh and the Devil* did **not** rotate (about ten miles across, 20,000 to 30,000 people, "absence of gravitation"). The spinning "Bernal sphere" is O'Neill's later design that borrowed the name. Source is secondary (arXiv 1806.01322 quoting p. 23); check the book text if available.
   - Below the table, one line per design on what it traded (the torus's 1 rpm limit forced an 830 m wheel; Kalpana One bought a small hull with 2 rpm; O'Neill's ladder shows population growing with radius). Link: Concordia glossary `/glossary/#o-neill-cylinder`, `/glossary/#stanford-torus`.
8. **Field guide: life inside a spinning world** (10 to 12 cards; the shareable middle of the page). Each card: the surprise in one line, the number, why, and one "see it" link. Candidates (verify each derivation; links are Concordia):
   - The ground curves up and over your head. Walk 8 km along the rim and you have gone 183 degrees: your feet point where your head was. 15.7 km once round. `/discover/ground-curves-up/` and `/explore/?viewpoint=residential-street`.
   - A train can weigh 0.66 g one way and 1.33 g the other (100 km/h against the spin, 90 km/h with it, on the 2,455 m metro radius). `/discover/train-weight/` and `/explore/?chapter=metro`.
   - A dropped object lands slightly antispinward of the point straight below it, because it keeps the slower tangential speed of the height it started from. Give the offset for a 2 m drop and a 100 m drop at Concordia (compute, show the formula).
   - Climb a tower and you get lighter: 0.82 g at the 450 m sky. `/explore/?viewpoint=artificial-sky-breakthrough`.
   - Above the sky the far side of the city hangs overhead, 4,550 m away and upside down. `/discover/above-the-sky/`.
   - Gliding gets easier the higher you go (lower weight, thinner air: net effect from the Concordia glider model). `/science/gliding/` and `/explore/?viewpoint=glider-over-city`.
   - Near the axis you float; the lift up there is a ride from 1 g to zero. `/explore/?chapter=ascender` and `/explore/?chapter=axisTransfer`.
   - You cannot simply steer a spinning cylinder: four rotors spinning one way would need about 4.1 MN at each end of the hull to turn it 1 degree a day; counter-rotating pairs make it about 1,000 times easier. `/discover/why-not-spin/` and `/explore/?overlay=momentum`.
   - Throwing a ball spinward vs antispinward (it curves; give the qualitative rule and one number if derivable cleanly).
   - Pouring and splashing look normal at large radius; at 4 rpm a pour visibly deflects (only if a source or a clean derivation supports it; otherwise cut).
   - Air pressure is lower near the axis (about 86 percent of ground pressure, `design value`).
9. **Engineering consequences of spin** (5 to 6 entries, one line each plus a number): why rotors get big (comfort pushes radius up; hoop stress and mass push it down), why the hull is pressure-separate from structure, why rotors float on magnetic bearings instead of wheels, why spin-up takes days to weeks, why rotors are paired. Link out to Concordia `/science/structure/` and `/science/counter-rotation/` once each. If a subtopic grows past three lines, link it and move on (README Rule 4).
10. **Common mistakes** (mandatory, 8 or more). Anchors: "Bernal's 1929 sphere spun" (it did not; see the footnote); "SP-413 set a gravity-gradient limit" (it did not); "rpm alone sets gravity" (radius matters as much); "a small centrifuge at 1 g feels like Earth" (10 m needs 9.5 rpm and an 18 percent gradient); "the curved floor feels like a slope" (it feels flat underfoot); "Coriolis only matters if you move up or down" (any motion not parallel to the axis); "one big cylinder can be pointed anywhere" (gyroscopic stiffness; needs counter-rotation); "gravity is the same at head and feet"; "spin gravity is free once spinning" (bearings, trim mass, balancing as people move); "L5 is stable so nothing needs stationkeeping" (Earth-Moon L5 is perturbed by the Sun; Concordia uses active stationkeeping).
11. **Explore it** (closing CTA block, one card): a Concordia hero image and three buttons: "Take the guided tour" (`/explore/?mode=story`), "Explore freely" (`/explore/?mode=explore`), "Read the science" (`/science/artificial-gravity/`).
12. **Related** (Rule 6).

**Link budget:** at most one Concordia link per section (two in a field-guide card: the explainer and the sim view), plus the Explore block and the Quick Reference Concordia line. Never iframe or embed the simulation: it is a heavy WebGL app and would break the Core Web Vitals gate. Plain links, no `nofollow` (same owner). Every deep-link id above comes from Habitat `site/data/sim-index.json` as of 2026-10-14; re-check them at build.

## Volatile-facts register

Overall rating: **STABLE** (physics and history), with one volatile register:

| Fact | Rot rate | Re-verification |
| --- | --- | --- |
| Concordia deep links (`viewpoint`, `chapter`, `overlay` ids; `/discover/` and `/science/` paths) | Months: the site is under active development | Link-check all Concordia URLs on each freshness pass; ids from `site/data/sim-index.json` |
| Concordia design values (radius, spin, sky height, metro radius, air pressure) | Slow: a canon change in the Habitat repo | Diff against Habitat `docs/site/facts.md` sections 2, 5, 15 |
| Historical design dimensions, comfort limits | Stable | Source links only |
| Nautilus-X or any current commercial spin-station concept, if added | Fast | Avoid adding live commercial projects; if added, date them inline |

## Index category

Existing `Engineering & Science` in `category-map.php` (same as `space-habitats-life-support.html`, `rockets-and-spaceflight.html`, `orbital-rockets-comparison.html`).

## Reading conditions

Desktop or laptop for designers and students working a problem with the calculator; phone for curious readers arriving from search or social. The calculator must work one-handed at 375 px (stacked inputs, numeric keyboard, outputs visible without scrolling past the inputs). Classroom projection: the chart is legible at 1080p from across a room. Print: Quick Reference, comfort tables and the comparison table print cleanly; the calculator prints as its current output values.

## Cross-link map

- **Outbound (this repo):** `space-habitats-life-support.html` (the life-support half of habitat design), `rockets-and-spaceflight.html`, `orbital-rockets-comparison.html` (getting the mass up there), `black-hole-flight-simulator.html` (the other physics simulator on the site).
- **Reciprocal (this repo):** add a Related link to this page from `space-habitats-life-support.html` and `rockets-and-spaceflight.html`.
- **Concordia (outbound, per section):** as listed in Content approach.
- **Concordia (inbound, separate change in the Habitat repo, behind David's deploy gate):** add this page to the `related` or a "Reference" link on `/science/artificial-gravity/`. Do not make that change as part of this build.
- **Paths:** add to a space trail in `paths.json` if one exists, otherwise propose one (life support → artificial gravity → rockets).

## og:image / shareable artifact

The **spin chart** with every design dot labelled and Concordia highlighted, rendered at 1200 x 630. The field-guide card "The ground curves up and over your head" is the secondary screenshot artifact.

## Density targets

- Quick Reference: 8 to 10 lines.
- Calculator: 9 outputs, 6 presets (one per comparison row) plus the O'Neill Models 1 to 3.
- Comparison table: 6 rows (5 historical designs plus Concordia; up to 8 with the optional rows) x 10 columns, every cell sourced, derived or "not stated"; the O'Neill ladder sub-table (4 rows); the Bernal 1929 footnote.
- Comfort: SP-413 criteria (all stated), Globus and Hall 4 rows, experiments 4 to 6 rows.
- Field guide: 10 to 12 cards.
- Engineering consequences: 5 to 6. Common mistakes: 8 or more.
- Total substantive entries: 45 or more.

## Sourced anchors (pre-research, 2026-10-14)

A research pass read these primary texts while the spec was written. The values in Content approach sections 6 and 7 come from them. They are still anchors under Rule 1: re-open each source at build, and the source wins.

| Source | What it anchors | URL |
| --- | --- | --- |
| NASA SP-413 ch. 3 | 0.9 to 1 g; 1 rpm limit; below 3 rpm adaptation; Coriolis jump example; no gradient limit | https://nss.org/settlement/nasa/75SummerStudy/Chapt3.html |
| NASA SP-413 ch. 4 and 5 | Torus R_maj 830 m, R_min 65 m, 1 rpm, 0.95 ± 0.05 g, 10,000 people, about 10 Mt shield at 4.5 t/m²; relaxed 0.85 g at 1.9 rpm case | https://nss.org/settlement/nasa/75SummerStudy/Chapt4.html, https://nss.org/settlement/nasa/75SummerStudy/Chapt5.html |
| O'Neill, "The Colonization of Space", *Physics Today*, Sept 1974 | Models 1 to 4 (Table 1); Model 4 R 3,200 m, 32 km, 114 s | https://aip.brightspotcdn.com/PTO.v27.i9.32_1.online.pdf |
| NSS, O'Neill cylinder (quoting *The High Frontier*) | Island Three pair, about 20 mi by 4 mi, several million | https://nss.org/o-neill-cylinder-space-settlement/ |
| L5 News, Sept 1976; NSS Bernal sphere page | Island One sphere, about 1 mile circumference, about 1.9 rpm, about 10,000 | https://www.nss.org/wp-content/uploads/2017/07/L5-News-1976-09.pdf, https://nss.org/bernal-sphere-space-settlement-detail/ |
| Globus and others, Kalpana One (2007) | R 250 m, L 325 m, at most 2 rpm, 3,000 people, up to 10 t/m², about 7 Mt | https://nss.org/wp-content/uploads/2017/07/Kalpana-One-2007.pdf |
| Globus and Hall 2017 | Four rotation recommendations; radius-for-1 g table | https://nss.org/wp-content/uploads/NSS-JOURNAL-Space-Settlement-Population-Rotation-Tolerance.pdf |
| Hall, SpinCalc | Five historical comfort charts; Graybiel 1977 and Lackner and DiZio 2003 quotations; formula statements | https://www.artificial-gravity.com/sw/SpinCalc/ |
| Reason and Graybiel 1969 (NTRS 19700005540) | Pensacola Slow Rotation Room, 10 rpm, start at 2 rpm | https://ntrs.nasa.gov/api/citations/19700005540/downloads/19700005540.pdf |
| NASA Gemini XI pages | Tether, about 0.00015 g | https://www.nasa.gov/missions/gemini/gemini-xi/demanding-gemini-xi-mission-flies-on-top-of-the-world/ |
| NTRS 20070016631 | Short-radius centrifuge bed-rest pilot | https://ntrs.nasa.gov/citations/20070016631 |
| Shiba and others 2017, *Scientific Reports* | ISS mouse centrifuge (JAXA MARS) | https://pmc.ncbi.nlm.nih.gov/articles/PMC5589811/ |
| arXiv 1806.01322 | Bernal 1929 sphere did not rotate (secondary) | https://arxiv.org/pdf/1806.01322 |
| Habitat repo `docs/site/facts.md` sections 2, 3, 5, 15; `site/js/widgets/core.mjs` | All Concordia values | local, `~/Projects/Habitat` |

**Unverified, so do not ship without a source:** von Braun wheel figures, Nautilus-X dimensions, Island One diameter beyond "about a mile round", Island One shield mass, Island Three rpm, Gemini XI rotation rate, Graybiel 1977 original text, the vector form a = −2ω × v (cite a standard mechanics text; SpinCalc states only the ratio).

## Calculator implementation notes

- Port the pure functions `spinDesign`, `comfortBand` and `metroWeight` from Habitat `site/js/widgets/core.mjs` inline (single-file rule). Same author; keep the function names so the two stay diffable.
- Acceptance check values (all from that core; the build must reproduce them):
  - `spinDesign(2500, 1)`: ω 0.06263 rad/s, 0.598 rpm, period 100.3 s, rim speed 156.6 m/s, gradient 0.072 percent, Coriolis at 1.4 m/s 0.0179 g.
  - `spinDesign(10, 1)`: 9.46 rpm, period 6.34 s, gradient 18 percent, Coriolis 0.283 g.
  - `spinDesign(224, 1)`: 2.00 rpm, period 30.0 s, rim speed 46.9 m/s, gradient 0.80 percent.
  - `metroWeight(100, 'antispinward')` 0.658 g; `metroWeight(90, 'spinward')` 1.326 g.
  - Concordia gravity at 0, 250, 450, 1,000, 1,250, 2,000, 2,500 m up: 0.999, 0.899, 0.819, 0.599, 0.500, 0.200, 0.000 g.
- Inputs validate (radius 1 m to 100 km, rpm 0.01 to 60); the calculator remembers the last design in `localStorage` with feature detection.
- One interactive element (calculator plus chart); no 3D, no animation required. An optional slow rotating rotor cross-section beside the outputs only inside `prefers-reduced-motion: no-preference`.

## Visual design

**Language: a 1970s NASA study report meets an engineer's slide rule.** Warm report paper, ink linework, one safety-orange accent, tabular numerals. It nods to SP-413 without imitating NASA branding (no logos, no "NASA" lettering as decoration).

- **Palette (light):** paper `#F4F1E8`, ink `#1B2330`, muted ink `#55606E`, rule `#C9C3B4`, accent orange `#C8551F`, chart blue `#2F6DA3`. Comfort bands (fills at low opacity behind the chart, labels in ink): band 1 green `#3E8E5A`, band 2 amber `#B8891F`, band 3 orange `#C8551F`, band 4 red `#B23A3A`. Concordia highlight: blue `#2F6DA3` with a ring.
- **Palette (dark):** background `#10151D`, surface `#18202B`, text `#E6E2D6`, muted `#A3ABB5`, rule `#2E3846`; accents lightened to pass 4.5:1.
- **Type:** headings `Georgia, 'Times New Roman', serif`; body `system-ui` stack; every number in `ui-monospace` with `font-variant-numeric: tabular-nums`.
- **Signature element: the spin chart.** Log-log plot, radius 1 m to 10 km against 0.1 to 60 rpm. Iso-g lines are straight diagonals on log-log axes (rpm ∝ r^-1/2), labelled at the right edge. Comfort bands are horizontal stripes (they depend on rpm only). Design dots carry short labels with leader lines that never cross; Concordia sits far down and right in band 1 with a ring. The live marker moves as inputs change and snaps to a preset when a chip is chosen. Inline SVG, computed; no chart library needed. At 375 px the chart goes full width above the outputs and labels collapse to numbered dots with a legend.
- **Field-guide cards:** a small rotor cross-section glyph per card showing where the effect happens (floor, sky, axis), the number set large in monospace, the "see it" link as a text button.
- **Concordia images:** two at most (the Explore block hero, and optionally one inline in "Gravity fades with height"), copied from the Concordia site's published hero screenshots into `images/`, WebP, `loading="lazy"`, width and height set, alt text that describes the scene. Credit line: "Rendered in the Concordia simulation" linking to the site.

## Build sequence

1. Outline per README Rule 2, including the comparison-table row list and one fully sourced exemplar row (Stanford torus).
2. Verify every non-Concordia number against the sources above; pull Concordia values from `facts.md` and the core.
3. Build the calculator and spin chart first and check them against the acceptance values.
4. Write the sections; run the repo's gates (`docs/content.md`); test the chart and calculator at 375 px and in print.
5. Link-check every Concordia URL; add the reciprocal Related links; register in `category-map.php`; generate the og:image from the chart.
6. Delete this spec when the page ships.
