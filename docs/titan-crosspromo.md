# Titan cross-promotion: propulsion calculator

`rocket-equation-calculator.html` is a standalone ideal rocket equation tool and
propulsion reference. It promotes Titan 2100 through useful fictional worked
configurations. Concept research and the unresolved keyword-volume check remain
in `research/2026-11-04-titan-concept.md`. David authorized proceeding provisionally
without search-volume estimates on 2026-11-04. No volume claim belongs in the page.

## Basis and scope

- Real formulas use the primary sources listed on the page. All calculator
  inputs are assumptions; a result does not establish engine feasibility.
- Chemical and ion configurations are teaching examples, not named vehicles.
- Long Passage, Titan cargo tug and Titan ascent are fictional designs. Their
  current inputs came from the sibling `titan-2095/assets/data/vehicles.json`.
  Preserve design/challenge labelling; never turn a source's proposed capability
  into measured or flown performance. The DFD reference row uses the **56.5 km/s,
  40 N design point** stated in Razin 2014, independently of Titan's 200 km/s.
- Post-burn mass includes payload, power supply, engines, structure and reserves.
  The tool assumes constant effective exhaust velocity and constant thrust (also
  constant for a chosen fixed jet power at a fixed exhaust velocity).
- Jet power is an axial-exhaust approximation. Effective velocity may include
  pressure thrust; do not relabel calculated equivalent jet power as measured
  thermal/electrical source power. Low-thrust trajectory, drag, gravity, steering,
  engine cycling and relativistic physics are outside this tool.
- The plot holds required ideal delta-v and directed jet power fixed while
  changing exhaust velocity. It does not hold engineering hardware mass fixed.
  Left propellant-fraction axis is linear; right thrust axis is logarithmic.

## Acceptance and reproduction

```powershell
python -m http.server 8766 --bind 127.0.0.1
python scripts/check_rocket_equation.py --base http://127.0.0.1:8766 --render-og
```

Browser QA needs Python Playwright/Chromium and the existing sibling
`Habitat/node_modules/axe-core/axe.min.js` for axe. It tests five presets against
independent numeric expectations, inverse mode, unit changes, fixed-power thrust,
invalid/zero/tiny inputs, clipboard fallback, shared-URL reload, layout at 360,
375, 768 and 1440 px in both themes, chart labels, duplicate IDs, serious/critical
axe findings and runtime errors. Captures/report/print output stay local in
`.visual-qa/rocket-equation/`; only the required OG image is committed.

`--render-og` generates `images/rocket-equation-calculator.png` (1200x630) directly
from the working Long Passage calculator and chart with transient layout CSS.
No external image, font, framework, live Titan asset or simulated audio is loaded.
The ship illustration is inline SVG with shaded hulls, cylindrical tanks,
radiator sheets and a plasma plume. Use SVG or an image API for illustrations;
do not substitute ASCII or text-glyph drawings. Its responsive labels are HTML.

On this Windows host, PHP initially had no loaded ini and lacked `mbstring`.
Rendered-index checks passed after enabling the already-installed extension with
a process-local `PHP_INI_SCAN_DIR` under the ignored QA output folder. No global
PHP configuration was changed. Run repository gates with a PHP configuration
that loads `mbstring`, as the existing Explorer requires it.

Selected independent expectations:

| Case | Ideal delta-v | Consumed mass | Engine-on time |
| --- | --- | --- | --- |
| Chemical: 100,000→10,000 kg, 350 s, 1 MN | 7,903.2261358 m/s | 90,000 kg | 308.909475 s |
| Ion: 1,200→1,000 kg, 3,000 s, 0.1 N | 5,363.8910848 m/s | 200 kg | 58,839,900 s |
| Long Passage: 10,000 t, 100 km/s, 200 km/s exhaust, 63.7 kN | 100,000 m/s | 3,934,693.4029 kg | 12,353,825.4407 s |

The page exposes `window.rocketCalculator.solve`, `presets` and `getResult` for
acceptance checks. No runtime files are required beyond the single HTML page.
Shared configuration uses a whitelisted URL query; the canonical always excludes
query state. No persistence or external service is required for the calculator.

## Drift and measurement

Recheck NASA survey ranges against the explicitly scoped small-spacecraft Table
4-1 when refreshing. Nuclear-thermal and DFD entries refer to dated design studies.
Reconcile fictional presets with Titan's generated budget if its inputs change;
small differences from its rounded derived fields are expected and disclosed.

Outgoing links use `utm_source=cheatsheets&utm_medium=referral&utm_campaign=titan_crosspromo&utm_content=<section>`.
Destinations are `/fleet/`, `/nuclear/inside-the-fusion-drive/` and
`/chemistry/reactions/`. HTTP source checks returned 403 in this session, so a
live browser check of those destinations is still needed before publication.
Their owning local sources and routing were inspected. Do not interpret a bot
403 as a broken public page.

Related links come from the spaceflight hub and artificial-gravity sheet; the
new page links to the launch-vehicle comparison, artificial gravity and life
support. It belongs to Engineering & Science. Catalog, breadcrumb, sitemap
discovery and both llms indexes follow the repository's normal content path.

After deployment approval and publication, establish a Search Console baseline
for the exact calculator query family and page. Review at 30/60/90 days. Verify
Titan's available referral telemetry before promising campaign attribution.
