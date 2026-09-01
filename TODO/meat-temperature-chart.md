# Spec: Meat temperatures — pull, rest and serve

**Target file:** `meat-temperature-chart.html`
**Batch:** [niche-utility-batch-2026-08.md](niche-utility-batch-2026-08.md) (sheet 9 of 10).

## Why this topic

`cooking-guide.html` is **15,663 words** and earns 4 clicks on 1,903 impressions at position 20.1.
It is a course, not a lookup — and the site has no cooking artifact anyone can use with a probe in
one hand. The single highest-frequency kitchen question ("what temperature do I pull this at")
has no home here.

The competitive field is dominated by two kinds of page that are each half-right. Government
sources publish **safe minimum internal temperatures** that are legally defensible and, for beef
and pork, produce results most cooks consider overdone. Food-enthusiast sites publish **preferred
doneness temperatures** with no safety framing at all. The reader is left to reconcile them alone,
usually badly.

The differentiator is stating the reconciliation explicitly: **safety is a time-and-temperature
pair, not a single number.** Poultry held at 60 °C for long enough is as safe as poultry flashed
to 74 °C, which is exactly why sous vide works and exactly what neither camp explains on the page
where people look up the number. A chart that gives the pull temperature, the finished doneness,
the carryover that connects them, and the pasteurization time for the lower temperatures is
strictly more useful than either incumbent — and it is the kind of quantified, sourced table this
site is built to produce.

## Targeting

- **Primary query:** `meat temperature chart`
- **Secondary:** `steak doneness temperature`, `pork internal temp`, `chicken internal temp`,
  `sous vide time and temperature chart`, `carryover cooking temperature`,
  `brisket done temperature`, `turkey internal temp`
- **Mode:** operational, mid-cook, recurring. The reader returns to this page every time they
  cook; optimize for fast re-lookup and printing.

## Draft title / H1 / meta

- `<title>`: `Meat Temperature Chart: Doneness, Carryover, Sous Vide` (54 chars)
- **H1:** `Meat Temperatures: Pull, Rest and Serve`
- **Meta description (draft):**
  `Pull temperatures and final doneness for beef, pork, poultry, lamb and fish, with carryover by thickness, USDA safety minimums and sous vide pasteurization times.` (161 chars)

## Reader outcome

The reader can decide, for the specific cut in front of them, what temperature to pull it at to
land on the doneness they want after resting — and can say whether that result is safe, citing a
time-and-temperature basis rather than a folk rule.

## Success metric

Organic entries on the chart query family, and **return-direct plus print traffic** — the KPI that
matters is a page reopened every Sunday. Secondary: a measurable referral from
`cooking-guide.html` (this page should become that page's most-clicked outbound link, which also
tests whether the long-form guide can be rescued by giving it an artifact).

## Content approach

Every temperature in **both °F and °C in the same cell**, always. No conversion tables, no
toggles: the audience is split and a toggle is a JavaScript dependency on a page that should not
need one.

1. **Quick Reference: the wall chart** (signature element) — the whole thing in one screen: rows
   for beef steak, beef roast, ground beef, pork chop, pork shoulder, chicken breast, chicken
   thigh, whole poultry, turkey breast, lamb, duck breast, fish, shrimp; columns for pull temp,
   final temp, and the one-line doneness description. This is the artifact people print and the
   og:image.
2. **Doneness ladder for beef and lamb** — rare through well done, each band with its temperature
   range, what is happening to the muscle proteins and myoglobin at that band, and what the cut
   looks and feels like. Include the touch test with the honest note that it is unreliable below
   an inch of thickness.
3. **Carryover cooking** — the section that makes the chart usable: expected temperature rise by
   thickness, cooking method and resting environment, presented as a table (a 1-inch steak from a
   hot pan versus a 4-inch prime rib from a 250 °F oven are different by several degrees), plus
   how long to rest and the evidence on resting and juice retention.
4. **Safety: the time-and-temperature core** — the USDA single-number minimums stated plainly
   first, then the pasteurization tables: log-reduction time at temperature for poultry and for
   whole-muscle beef and pork, with the standard 7-log target named and the source cited. State
   the surface-versus-interior distinction for whole-muscle versus ground, and the reason
   intact-muscle beef can be served rare while ground beef cannot.
5. **Sous vide time-and-temperature table** — by protein and thickness: temperature, minimum time
   for pasteurization, maximum time before texture degrades, and the resulting doneness. This is
   the densest table on the page and the one with the least good competition.
6. **Low-and-slow and the stall** — brisket, pork shoulder and ribs: why the "done" temperature is
   a texture endpoint (probe tenderness) rather than a number, the collagen-conversion window, the
   stall and its cause (evaporative cooling), and what wrapping actually changes.
7. **Poultry specifics** — why breast and thigh want different endpoints, why the pop-up timer
   overcooks, where to actually probe a whole bird, the pink-near-the-bone myth (myoglobin and
   bone marrow, not undercooking), and the brining-versus-carryover interaction.
8. **Fish and shellfish** — a table by species type: temperature bands for translucent through
   firm, the salmon and tuna preferences that differ from the safety minimum, and the parasite
   note for raw preparations (freezing requirements, stated once with the regulatory basis).
9. **Thermometers** — instant-read versus leave-in versus infrared (and what infrared cannot do),
   probe placement by cut, the ice-water and boiling-water calibration checks with the altitude
   correction, and response-time expectations. No brand recommendations.
10. **Reheating, holding and the danger zone** — holding temperatures, the 2-hour/4-hour rules,
    reheating minimums, and the sous vide holding case that looks like it violates the rule and
    does not.
11. **Common mistakes** (mandatory): cooking to final temperature instead of pull temperature;
    probing through to the pan; trusting the oven's own probe without calibration; resting a thin
    steak until it is cold; applying the whole-muscle rare rule to ground meat; using the USDA
    pork number from before the 2011 revision; treating the sous vide table's minimum time as an
    upper limit.
12. **Related sheets** footer per the cross-link map.

## Volatile-facts register

**Overall: STABLE, with a documented revision hazard.**
- USDA/FSIS minimum internal temperatures: revised rarely but consequentially — pork moved from
  160 °F to 145 °F in 2011 and half the internet still prints the old number. Verify against the
  current FSIS page each pass and **date the safety section inline**.
- Pasteurization time tables: derived from published thermal-death-time data; stable.
- Physics of carryover and collagen conversion: permanent.
Annual freshness rotation; the FSIS section is the named check target.

## Index category

`Home & Lifestyle`.

## Reading conditions

**Kitchen or grill: phone or tablet propped against a canister, hands greasy or gloved, steam,
sometimes outdoors at dusk, glancing rather than reading.** Consequences: the wall chart must be
legible from ~60 cm at a glance (large tabular figures, generous row height, strong row banding),
high contrast in both themes, no hover-dependent information, and nothing that requires a precise
tap. **Print stylesheet is a first-class deliverable**: the wall chart must print to one page that
survives being taped inside a cabinet door, and the sous vide table to a second.

## Cross-link map

- **Internal outbound:** `cooking-guide.html` (the long-form parent — link both ways, and this is
  the more important direction: the guide needs this page as its lookup),
  `global_cuisine_guide.html`, `samsung-bespoke-oven-guide.html` (oven modes and probe use),
  `home-maintenance-guide.html`.
- **Reciprocal inbound:** a prominent link from `cooking-guide.html` — placed near the top, not in
  a footer, since that page's problem is the absence of a lookup.
- **External outbound:** FSIS, FDA Food Code, and the published thermal-death-time literature.

## og:image / shareable artifact

The wall chart, light theme, at 1200×630 — cropped to the beef/pork/poultry rows so the °F/°C
pairs stay legible at card size.

## Jurisdiction scope

US safety guidance (FSIS/FDA Food Code) is the stated baseline, with a short note that UK/EU
guidance differs on some cuts (notably poultry and burger service) and that the underlying
time-and-temperature science is identical — the divergence is regulatory risk tolerance, not
biology. One line, not a second chart.

## Density targets

Wall chart ≥ 13 rows; doneness ladder ≥ 6 bands; carryover table ≥ 8 combinations; pasteurization
tables ≥ 12 temperature rows across two proteins; sous vide table ≥ 20 rows (protein × thickness ×
temperature); fish table ≥ 6 species groups; thermometer section ≥ 4 types; common mistakes ≥ 7.
Every temperature in °F and °C.

## Research sources (verify against these, per Rule 1)

USDA FSIS safe minimum internal temperature guidance; FDA Food Code (time/temperature control for
safety, including the pasteurization time tables in Annex form); Baldwin's published sous vide
pasteurization tables and the underlying thermal-death-time literature; Cooking for Geeks / Modernist
Cuisine only for corroboration of technique, never as the sole source for a safety number. Every
safety figure traces to a regulator or to peer-reviewed thermal-death-time data.

## Visual design

**Identity: enamel diner wall chart.** Thick-ruled enamel-sign aesthetic — cream ground, deep
maroon rules, a butcher's-chart typographic feel with a condensed slab face for headings and true
tabular figures for every temperature. Dark mode is the same chart in a night kitchen: charcoal
ground, warm cream ink, ember accent. The doneness ladder is rendered as a horizontal gradient
bar from rare to well with the temperature bands marked along it — drawn as inline SVG, and
labelled in text at every band so it survives greyscale printing and colour-blind reading. The
wall chart is built first and best. No JavaScript anywhere; no unit toggle by design.

**Palette and type tokens — binding.** Diner mode: enamel cream `#F6E8CF`, maroon `#6B1F2B`,
bottle green `#285C45`, ember `#D66A2C`, rule shadow `#C9B89A`. Night-kitchen mode: charcoal
`#211A17`, warm ink `#F5E8D4`, ember `#EE7650`, sage `#A9C77D`, dim rule `#67564C`. Use a condensed
slab-like system stack for sign headings, a highly legible system sans for guidance and tabular
figures for every °F/°C pair. Colour may suggest doneness but words, texture and temperature must
always carry the result.

**Composition contract — build a kitchen instrument wall, not a recipe-card grid.** The recent
pages are the quality reference for labelled SVG and quantitative axes; this page should feel
warmer, more physical and more varied than their engineering-register shell:

1. **Enamel-sign masthead:** a shallow sign with the H1, one-sentence reconciliation of safety
   versus doneness and a riveted `LAST VERIFIED` plaque. Keep the useful wall chart visible in the
   first viewport; do not spend the screen on a large food photograph or marketing hero.
2. **Wall chart:** one uninterrupted, heavy-ruled lookup surface with protein silhouettes as row
   locators, oversized pull → rest → final figures and safety notes printed in the same row. It is
   not a collection of protein cards.
3. **Doneness thermal rail:** the six bands form one long cut-section/temperature rail with
   labelled muscle changes and appearance descriptors. Provide hatching and boundary ticks so it
   remains usable in monochrome; never rely on red-to-brown colour alone.
4. **Carryover trajectories:** small-multiple line plots share the same elapsed-minute axis for a
   thin steak, thick roast, poultry breast and shoulder. Plot pull, peak and settled temperature;
   the curves make thickness/method differences visible before the table is read.
5. **Safety time-temperature field:** a proper temperature-versus-hold-time plot with labelled
   curves/steps for the sourced lethality targets, paired with the regulatory table. Do not turn
   safety into a speedometer or a green/red badge.
6. **Low-and-slow strip chart:** brisket and pork shoulder get a recorder-like cook curve with the
   stall shaded and wrapping marked as an intervention. This section should feel like a pit log,
   visually distinct from the enamel reference above it.
7. **Probe-placement plates:** simple inline-SVG silhouettes of steak, whole bird, breast and fish
   show probe entry, sensing tip and bone/pan errors with leader lines. No stock photography and
   no decorative animal illustrations.
8. **Calibration and holding instruments:** ice/boiling calibration use two compact thermometer
   scales; reheating/holding use a 24-hour clock strip and temperature rail. These replace another
   generic comparison-card row.

**Page rhythm and anti-patterns.** Sequence sign → wall chart → thermal rail → data plots → sous
vide ledger → pit-log curve → probe plates → instrument strip → checklist. Alternate full-width
lookup surfaces with airy diagrams and compact two-up figures; avoid recipe cards, glossy food
photography, chef-hat icons, circular gauges, glass effects and repeated equal-height tiles. In
print, page 1 is the wall chart and page 2 is the sous-vide/safety sheet; ornamental textures drop
out. The 1200×630 preview is the wall chart with the pull → rest → final reading path intact.
