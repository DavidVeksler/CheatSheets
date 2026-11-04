# Titan cross-promotion: concept decision

Research date: 2026-11-04. David authorized proceeding provisionally without
keyword-volume data. Implemented locally as `rocket-equation-calculator.html`;
operating contract: `../titan-crosspromo.md`. No deployment authorized.

## Recommendation

Build **Rocket Equation Calculator: Chemical, Ion & Fusion**, provisionally at
`rocket-equation-calculator.html`. Its working promise is: compare how much
propellant, thrust, burn time and jet power a spacecraft needs, and understand why
a high-exhaust-velocity engine still may accelerate slowly.

This combines the fleet and fusion candidates into one task-oriented tool. The
chemistry lab supports a smaller fuel-versus-reaction-mass explanation. It follows
the artificial-gravity sheet's pattern: useful standalone calculator first,
clearly identified Titan design examples and contextual links second.

**Keyword demand is unverified.** Do not describe the proposed query as validated,
low competition, or a traffic opportunity of a quantified size until the saved
keyword shortlist is run successfully and the SERP is assessed.

## Evidence and limits

- DataForSEO Labs keyword-overview request failed with HTTP 402 Payment Required.
  A read-only account check succeeded and reported a USD -0.054 balance. No search
  volumes or keyword-difficulty scores were obtained. Credentials remain in the
  central env file, outside the repository.
- Search Console, domain property `sc-domain:cheatsheets.davidveksler.com`, web
  search, 2026-10-04 through 2026-11-01: the existing
  `orbital-rockets-comparison.html` had 5,620 impressions and 32 clicks; the
  `rockets-and-spaceflight.html` hub had 438 impressions and 1 click;
  `space-habitats-life-support.html` had 195 impressions and 0 clicks. These are
  page-only totals, not sums of query rows (which omit anonymized queries).
- No artificial-gravity page row appeared in the page report for that interval.
  The Concordia page is a format precedent, not evidence of organic success.
- Query/page rows included `rocket size comparison` (171 impressions) and
  `rocket comparison` (21 impressions for the comparison page, 16 for the hub).
  These validate adjacent comparison interest, not demand for a calculator.
- Search results for rocket-equation calculators include many similar tools.
  A basic delta-v form offers little differentiation. A power/thrust comparison
  is the proposed reason to use this page instead.
- The three Titan URLs could not be opened by the web reader; direct HTTP checks
  also returned 403, so these checks do not establish whether a browser can load
  the pages. Their current local
  owning sources were inspected: `titan-2095/content/site/reactions.md`,
  `content/explainers/inside-the-fusion-drive.md`, `content/site/fleet.md`,
  `content/explainers/energy-per-kilogram.md`, and `docs/vehicles/README.md`.
  Live URL checks remain necessary before page publication.

## Candidate comparison

| Concept | Search intent to validate | Standalone utility | Titan fit | Decision |
| --- | --- | --- | --- | --- |
| Rocket equation / propulsion tradeoffs | rocket equation calculator; delta v calculator; specific impulse calculator | Solve mass ratio, propellant, burn time, acceleration and power; compare engines for the same task | Strong: fleet presets plus fusion deep zoom | Provisional first choice |
| Fuel energy density comparison | energy density of fuels; energy density comparison; reaction energy calculator | Compare energies on a consistent mass basis, distinguish fuel-only from fuel-plus-oxidizer | Strong: reaction lab and fusion/fission | Runner-up if demand or SERP is better |
| Fusion reaction reference | fusion reactions; helium 3 fusion; fusion propulsion | Compare reaction products, energy partition, neutron implications | Strongest single deep link; narrower tool use | Supporting section, or separate future sheet |
| General chemistry reactions | chemical reactions; chemical reaction calculator | Usually implies balancing, stoichiometry or equilibrium | Weak unless a full chemistry solver is built | Reject broad framing: would mismatch the offered utility |
| Fictional fleet comparison | spacecraft propulsion comparison; rocket engine comparison | Compare exact design specifications | Strong brand fit; duplicates existing launch-vehicle comparison if framed broadly | Use presets, not the main title |

The energy-density alternative must use explicit denominators: MJ/kg of fuel,
complete reacting mixture, or storage system are different quantities. It must
also distinguish reaction energy from practical engine output. It should not
target generic `chemical reaction calculator` without meeting solver intent.

## Refined page concept

**Draft title:** Rocket Equation Calculator: Chemical, Ion & Fusion

**Draft H1:** Rocket equation calculator and propulsion comparison

**Draft description:** Calculate delta-v, propellant mass and burn time. Compare
chemical, ion, nuclear thermal and fusion propulsion, with sourced examples and
Titan's fictional fleet.

**Target queries, provisional:** primary `rocket equation calculator`; secondary
`delta v calculator`, `specific impulse calculator`, `spacecraft propulsion`,
`fusion propulsion`. Audience: spacecraft designers, students, simulation players
and science-fiction worldbuilders doing preliminary calculations.

**Niche utility test:** users can leave the calculator open while changing a
vehicle's mass and propulsion assumptions. A live tradeoff plot and comparable
presets supply repeat-use value beyond an explanatory chat response.

**Signature visual:** one linked calculator and tradeoff plot. At a fixed required
delta-v, show propellant fraction against exhaust velocity, alongside thrust and
burn time at a chosen power or thrust. Make the constraint explicit. More exhaust
velocity saves propellant but reduces thrust at fixed directed jet power.

**One coherent tool, two modes:**

1. Vehicle mode: wet mass, post-burn mass, Isp/exhaust velocity, thrust. Derive
   ideal delta-v, propellant fraction, mass flow, initial/final acceleration, burn
   duration and equivalent kinetic jet power where the exhaust model applies.
2. Mission mode: required ideal delta-v, post-burn mass, Isp/exhaust velocity and
   thrust or jet-power constraint. Solve required wet mass and propellant, then
   the same time/power outputs. Explain ideal-impulse capability versus trajectory.

Use standard gravity only as the Isp conversion constant. Distinguish effective
exhaust velocity (including pressure thrust) from actual directed exhaust speed;
the simple kinetic-power formula applies to the appropriate idealized exhaust
model, not every engine with the same tabulated Isp.

## Proposed coverage

| Section | Required content and depth |
| --- | --- |
| Quick reference | Delta-v, Isp, mass ratio, propellant fraction, thrust, mass flow, acceleration, jet power; units and assumptions |
| Calculator | Both modes; editable units; accessible numeric output; invalid-input handling; reset; shareable inputs |
| Propulsion comparison | At least 8 sourced rows: cold gas, monopropellant, methalox, hydrolox, solid, nuclear thermal, Hall, gridded ion; add fusion as concept with a separate status label |
| Worked examples | At least 3 fully calculated cases: chemical stage, electric spacecraft and the Long Passage design/challenge preset |
| Why fusion does not mean instant acceleration | Fuel versus reaction mass; energy versus power; exhaust velocity versus thrust; waste heat and radiator burden |
| Common mistakes | At least 8: wet/dry mass, Isp units, local gravity conversion, delta-v versus speed/time, propellant versus fuel, power basis, thrust versus efficiency, ideal losses |
| Explore Titan | Contextual fleet, fusion-drive and reaction-lab links; design/challenge disclosure; plain links without embedding the sim |
| Sources and related sheets | Primary citations; launch-vehicle comparison, space habitats and artificial-gravity calculator |

Minimum 20 substantive reference entries overall. Compare in-space propulsion,
not launch-vehicle payload/size, so the new page complements the existing rocket
comparison. Desktop desk use and phone reference; tables scroll accessibly,
numeric results remain readable at 375 px, and the worked cases print clearly.
Category: Engineering & Science (`/engineering-science`), checked against
`category-hubs.json`.

## Sources and honesty contract

- Ideal rocket equation and inverse mass ratio: NASA Glenn,
  https://www1.grc.nasa.gov/beginners-guide-to-aeronautics/ideal-rocket-equation/
  (accessed 2026-11-04).
- Isp, equivalent velocity and pressure-thrust term: NASA Glenn,
  https://www.grc.nasa.gov/www/k-12/airplane/specimp.html
  (accessed 2026-11-04).
- Electric propulsion categories and verified performance: NASA,
  https://www.nasa.gov/smallsat-institute/sst-soa/in-space_propulsion/
  (accessed 2026-11-04). Verify each named engine against its own primary source.
- Fusion concepts: Razin et al. 2014,
  https://collaborate.princeton.edu/en/publications/a-direct-fusion-drive-for-rocket-propulsion/;
  inspect the paper during implementation before assigning any performance range.
- Titan presets: generated `titan-2095/assets/data/vehicles.json` and its generating
  `scripts/analysis/vehicle_budget.py`, checked against published pages. Preserve
  physics/design/challenge basis tags. Values marked verify remain excluded from
  claims about real engines. Never present the Long Passage as a real mission.

The Long Passage is an especially useful *illustrative* distinction: its energy
fuel and its hydrogen reaction mass are separate quantities. Only ship a preset
after its current generated numbers and assumptions are checked together.

Outbound links use `utm_source=cheatsheets&utm_medium=referral&utm_campaign=titan_crosspromo&utm_content=<section>`.
Deep links: `/fleet/`, `/nuclear/inside-the-fusion-drive/`,
`/chemistry/reactions/`. Keep the page fully useful without clicking out. Use
section-relevant deep links and an Explore block, following the existing
Concordia cross-promotion model. No heavy simulation embed.

## Search-volume decision gate and next step

After the user restores DataForSEO funding, run:

```powershell
python scripts/keyword_research.py docs/research/2026-11-04-titan-keywords.txt --output docs/research/2026-11-04-titan-keywords-us.json
```

The script uses United States, English, and returns monthly-volume estimates,
organic difficulty when available, update timestamps and request cost. Do not sum
near-synonym volumes as independent demand; do not confuse advertising competition
with organic difficulty. Null values mean unavailable, not zero. Inspect the data's
latest month and age before calling it current. Query global/other markets only
as a separately labelled comparison if needed.

For a future demand check, compare the calculator versus energy-density angle using exact tool-query demand,
intent fit, competitive results and the opportunity to offer a distinctive tool.
Do not select a broad phrase just because its volume is larger. Then promote this
concept if needed. The calculator was selected provisionally with David's approval;
this research does not establish that its target keyword has measured demand.

Success: organic entries on validated calculator queries, calculator use and
qualified referrals into Titan. Establish Search Console baselines on publication;
check 30/60/90 days. Confirm which referral measurement Titan actually supports
before promising campaign counts. Physical equations are stable; engine data,
Titan presets and deep links need periodic rechecking. No deployment authorized.
