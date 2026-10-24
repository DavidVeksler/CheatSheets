# Concordia cross-promotion (artificial-gravity-calculator.html)

`artificial-gravity-calculator.html` is a spin-gravity calculator and reference that uses **Concordia** (https://concordia.davidveksler.com/, David's browser-explorable 1 g settlement design study; repo `~/Projects/Habitat`) as its worked example. The page must stay fully useful without a click out. Built 2026-10-14 from a spec that is now deleted; this file keeps what the spec knew and the page cannot show.

## Honesty contract

- Concordia is a **design study set in 2045**, never "planned", "proposed by" or "will be built". Every Concordia number carries the `design value` tag (`.dv`, one style). The disclosure sits in the masthead and the Explore block.
- Concordia numbers come only from Habitat `docs/site/facts.md` sections 2, 5, 15 and `site/js/widgets/core.mjs`; if they disagree with the live site, the live site wins. Leave out its economy and backstory (AGI, charter, dividends).
- Real physics and history carry primary sources (listed in the page's Sources section). Anything unverified is left out, not shipped as an anchor: von Braun wheel and Nautilus-X figures, Island One shield mass and diameter beyond "about a mile round", Island Three rpm, the Gemini XI rotation rate, the vector form of the Coriolis term.
- Never embed or iframe the simulation (WebGL, heavy). Plain links, no `nofollow` (same owner). At most one Concordia link per section (two per field-guide card); extras only in the Explore block and the Quick Reference line.

## Outbound link shape and measurement

`https://concordia.davidveksler.com/<path>?<params>&utm_source=cheatsheets&utm_medium=referral&utm_campaign=concordia_crosspromo&utm_content=<section-slug>`. UTMs on outbound links only; the "no UTMs on internal links" rule in `TODO/marketing-campaign-plan.md` still holds. Measure with the `cloudflare-stats` skill on the Concordia zone (requests whose query string or referrer shows the campaign); if that zone does not expose query strings or referrer hosts in GraphQL, report referrer-host counts only. Also track organic entries on the primary query "artificial gravity calculator" in Search Console (baseline in `seo-progress.md` once the page is live).

## Volatile facts (re-verify on each freshness pass)

| Fact | Rot | How |
| --- | --- | --- |
| Concordia deep links (`viewpoint`, `chapter`, `overlay` ids; `/discover/`, `/science/`, `/glossary/#slug`) | Months (site under active development) | `python3 scripts/check_concordia_links.py [--live]` (reads `~/Projects/Habitat/site/data/sim-index.json`; set `HABITAT_REPO` to override) |
| Concordia design values (radius 2,500 m, 0.0626 rad/s, sky 450 m, metro 2,455 m, air-pressure ratios) | Slow (canon change) | Diff `docs/site/facts.md` sections 2, 5, 15; re-run the page's acceptance values (below) |
| Historical designs, comfort limits | Stable | Source links only |

The page's `spinDesign`, `comfortBand`, `metroWeight` and `gravityAtHeight` are ported from Habitat `site/js/widgets/core.mjs` with the same names so the two stay diffable. Acceptance values the port must reproduce: `spinDesign(2500, 1)` gives 0.598 rpm, 100.3 s, 156.6 m/s, 0.072 % gradient, 0.0179 g Coriolis; `spinDesign(10, 1)` 9.46 rpm, 18 %, 0.283 g; `spinDesign(224, 1)` 2.00 rpm, 46.9 m/s, 0.80 %; `metroWeight(100, 'antispinward')` 0.658 g, `metroWeight(90, 'spinward')` 1.326 g; gravity at 0, 250, 450, 1,000, 1,250, 2,000, 2,500 m up 0.999, 0.899, 0.819, 0.599, 0.500, 0.200, 0.000 g. In a browser they are on `window.spinChart`.

## Verified corrections to the original spec (source wins)

- Hall's SpinCalc column is **minimum** tangential velocity, not maximum; Gilruth's row carries "optimum 2 rpm".
- SP-413 gives the torus tube diameter (130 m) and six 15 m spokes in chapter 5; shield 9.9 Mt, 4.5 t/m², described as passive and rotated far below 1 rpm or not at all (not strictly "non-rotating").
- O'Neill 1974: 7.5 t/m² is the averaged surface density of the structure, not a separate shield; Table 1 radii 100, 320, 1,000, 3,200 m, periods 21, 36, 63, 114 s.
- Globus and Hall do not use the phrase "universally agreed" for 2 rpm, so the page does not either. NSS's Island Three page does not quote *The High Frontier* or give an rpm.
- The wording "absence of gravitation" for Bernal 1929 was not found; the page says the 1929 globe is generally described as non-rotating and that the book text was not checked.

## Files

`artificial-gravity-calculator.html`; `images/artificial-gravity-calculator.png` (og, from `python3 scripts/render_og_artificial_gravity.py`, which redraws the live chart); `images/concordia-park-800.webp`, `images/concordia-sky-800.webp` (Concordia's published hero stills, 800 px); `scripts/check_concordia_links.py`.

## Open follow-up (not part of this build, behind David's deploy gate)

In the Habitat repo, add this page to the `related` list (or a "Reference" link) on `/science/artificial-gravity/` so the link goes both ways.

## Original graphics (2026-10-24)

The sheet embeds a masthead diagram, a live rotor section driven by its existing
calculator results, six shared reference plates and eleven distinct field-guide
illustrations. Reference plates come from the sibling Habitat repo's
`scripts/site/build-editorial-graphics.py`; the published sheet has no runtime
dependency on that repo. Figures explicitly identify conceptual drawing scales
and the pressure model. The original formulas and historical tables remain.

- Rebuild: `python scripts/build_gravity_illustrations.py` (`HABITAT_REPO` can
  override the sibling checkout); `--check` verifies the embedded drawings.
- Browser acceptance: start `python -m http.server 8765`, then run
  `python scripts/check_gravity_illustrations.py`. It checks live presets, edits,
  invalid-input preservation, SVG label bounds, duplicate IDs, page overflow and
  serious/critical accessibility findings at 360 and 1440 pixels in both themes.
  Screenshots and the report go to `.visual-qa/gravity-illustrations/`.
- Scrolling illustrations and existing reference-table containers accept keyboard
  focus on narrow screens. No animation or additional external asset is required.
