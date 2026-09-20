# Rainbow production notebook

## Reviewed outline, before implementation

The page follows eight linked chapters with four substantive entries each:

1. **See / fundamentals:** Sun-rain-eye arrangement; continuous spectrum; angular appearance; horizon-cut circle.
2. **Trace / fundamentals:** entry refraction; dispersion; partial internal reflection; exit refraction.
3. **Locate / working:** antisolar point; observer-centered cone; Sun elevation and elevated observers; changed contributing drops.
4. **Derive / working:** Snell angles; impact parameter; stationary deflection; neighboring-ray concentration and a completed n=4/3 example.
5. **Compare / working:** two reflections; reversed colors; primary/secondary regions; Alexander's band.
6. **Resolve / advanced:** ray singularity; evaluated Airy profile; size-dependent fringes; polarization.
7. **Calculate / research:** size parameter; sphere amplitudes; Debye contributions; illumination and distribution averaging.
8. **Investigate / research:** nonsphericity; higher orders; fold-caustic derivation; convergence and three falsifiable experiments.

The two tables contain primary, secondary, supernumerary, fogbow, higher-order and glory rows; and ray, Airy, Lorenz-Mie, Debye and nonspherical-method rows respectively. Bow exemplar: primary / refraction-one partial reflection-refraction / near 42 degrees from the antisolar axis with red outside / concentrated ray family / does not determine fringe structure or visibility. Model exemplar: geometric rays / sphere, index and incident direction / paths and stationary deflection / no interference or finite caustic intensity / locate the bow before switching to a wave model.

## Research and numerical plan

- Derive stationary primary/secondary directions independently from Snell's law; cross-check Laven's primary research.
- Obtain visible-water indices from the IAPWS refractive-index release, declaring density, temperature, wavelength and the unit-index surrounding medium idealization.
- Evaluate the fold Airy function with SciPy; derive the angular scale from the second derivative of deflection with respect to normalized impact parameter. Check analytic Ai(0) and published rainbow conventions.
- Compute sphere amplitudes with miepython, validate a published MIEV0 case, then cross-check the chosen lossless-water cases against an independent Riccati-Bessel implementation and order convergence.
- Treat atmospheric raster and spectral design colors as illustration. All explanatory geometry is calculated SVG; all wave plots are monochromatic.

## Sources and conventions

All source URLs below returned HTTP 200 during implementation on 2026-09-19. The
per-URL results and redirect target are in `scripts/rainbow/source-validation.json`.

- [Lock, Können and Laven (2024)](https://www.philiplaven.com/Publications/JQSRT-312-108794_pre-print.pdf), equations 2.1–2.6 and section 3: accumulated deflection, stationary ray, cubic coefficient and Airy scaling. Original Airy theory is only a qualitative shape model for the displayed small-drop cases. We do not claim numerical agreement with full Mie or implement generalized Airy theory.
- [IAPWS R9-97](https://iapws.org/technical-guidance/release/Rindex.download), equation 1 and Table 2: refractive index relative to vacuum. Inputs are 293.15 K, 998.2 kg/m³ and wavelengths 0.450, 0.550 and 0.650 μm. Exterior index is explicitly simplified to 1, not a moist-air calculation. Release validity covers these inputs; the reported visible/ambient fit uncertainty is 1.5e-5. Displaying five decimals does not claim that many independently measured digits.
- [Laven (2003)](https://www.philiplaven.com/Publications/AO-42-03-p436.pdf), Fig. 2(a): radius 100 μm, wavelength 650 nm, relative real index 1.332, perpendicular polarization, scattering angles 137–145° in 0.01° steps. We reproduce these inputs, not a digitized image. The 25 and 50 μm cases are original computations with the other inputs unchanged.
- [miepython normalization](https://miepython.readthedocs.io/en/latest/03a_normalization.html): Wiscombe normalization and printed MIEV0 case 14. With S1 perpendicular and S2 parallel, the unpolarized angular integral is πx²Qsca. A physical irradiance ratio includes 1/(kR)². Complex-amplitude time-sign conventions differ between implementations; comparisons here use squared magnitudes.
- [Lee and Laven (2011)](https://www.philiplaven.com/Publications/AO-50-28-F152.pdf): sunward tertiary geometry and conditional visibility.
- [Sadeghi et al. (2012)](https://cs.dartmouth.edu/~wjarosz/publications/sadeghi11physically.html): wavefront methods and nonspherical drops.
- [Laven (2005)](https://www.philiplaven.com/Publications/AO-44-27-p5675.pdf): glory backscattering. It is a contrasting phenomenon, not a small primary rainbow.

### Angles and units

Vectors indicate propagation. At a surface, i and r are measured from the normal.
For Debye index p, the number of internal reflections is p−1. Accumulated deflection
is Θ=(p−1)π+2i−2pr; scattering angle is θ=acos(cos Θ), and antisolar angular radius
is β=π−θ. Radians are used in the equations, degrees in figure axes. The primary
stationary impact ratio is sqrt((4−n²)/3). For n=4/3 the result is i=59.3911023403°,
r=40.2029658866°, θ=137.9703411343°, β=42.0296588657°. The corresponding secondary
radius is 50.9780935257°.

For the wave cases, x=2πa/λ and
h=(9/4)sqrt(4−n²)/(n²−1)^(3/2)=4.927462196204 at n=1.332. The plotted Airy argument is
z=x^(2/3)(β−βR)/h^(1/3). Its angular scale is h^(1/3)/x^(2/3), in radians. For the
100 μm case this is 0.9972852404°; βR=42.2237504138°. Ai(0)²=0.1260449190.
The Airy maximum at z≈−1.018793 is therefore at β≈41.2077°.

### Numerical verification

`compute.py` checks the library against printed MIEV0 test case 14 at four angles.
The allowed absolute intensity error is half the last printed decimal place,
5e-7; observed maximum is 3.1812e-7. The selected water-drop curves are independently
evaluated using direct SciPy spherical-Bessel coefficients and explicit angular
recurrences, at the same series truncation as the library. The largest difference,
relative to each polarization's peak, is 2.88e-11 (acceptance 1e-8, well beyond
figure precision). Adding 20 orders to the independent series changes the curves
by at most 4.81e-8 of peak, below the library's documented approximate 1e-6 truncation
target. Comparing a ceil-based truncation with the library's integer truncation
initially mixed two error sources; the final checks separate same-order agreement
from the additional-tail test. No tolerance was loosened to conceal disagreement.

Ai(0) is checked against 1/(3^(2/3) Gamma(2/3)). The Airy curve is computed with
SciPy, not fitted or drawn by eye. Mie arrays retain eight decimal places, Airy
arrays ten. Neither curve includes solar-disk, size-distribution or wavelength
averaging. Each comparison curve is independently peak-normalized over β=35–43°;
the polarization panel instead uses one shared perpendicular peak denominator.

## Figure manifest

All SVG geometry and plots are author-created from the equations above. Run
`node scripts/rainbow/build.cjs` to regenerate inline static states and the vector
download; the page itself has no build or runtime dependency on these scripts.

| Figure ID / output | Source and parameters | Frame, method and scope | Validation |
|---|---|---|---|
| Opening landscape | OpenAI-generated art; provenance below | Decorative raster, 1536×1024; no optical claim | Inspected: rain ahead, lit foreground, no Sun disk or baked-in bow |
| Hero bow | SVG circular arcs; red outside violet | Observer-centered compositional illustration; schematic intensity and RGB | Visual color-order review; never used as quantitative data |
| `trace-figure` | Snell/reflection, n=4/3, stationary impact | Unit-radius sphere section, incident vector (1,0); exact intersections | Boundary, Snell, reflection and deflection invariants |
| `cone-figure`, `full-cone` | 650 nm IAPWS ray index; Sun default 15° | World x lateral, y forward, z up; observer A=(0,0,.1), B=(1.2,0,.1); fixed sampled rain volume | Eye is cone apex; dot-product half-angle tests for five elevations |
| Cone camera | Eye (12,−5,9), target (0,3,1), up z | Orthographic basis right=normalize(forward×up), camera-up=right×forward; scale 36, SVG offset (310,252). Transparent faces and droplets depth-sorted; sightline overlays remain visible as annotations | Projected bounds inspected, labeled horizon plane and axis |
| Sample selection / D | Fixed field; βR−1° < βdrop ≤ βR | A one-degree bin *inside* the primary ray region, not a visibility/intensity model. D is the first selected fixed-field sample. Invert the lower-impact ray branch by bisection to draw D's actual drop path | Every selected sample has a recovered ray with matching β to 1e-9 degrees; A/B contributor sets differ |
| `sky-figure` | Shared 3D cone directions and selected drops | Orthographic sky projection looking horizontally along +y: (170+170vx,180−170vz); clip at horizon. D uses same selected index as space view | Projected samples align; at Sun 60° no above-ground selected primary paths |
| `side-figure` | β and Sun elevation from shared state | Orthographic side section; below-ground construction deliberately clipped away from caption | Angles recomputed at range endpoints, no nonfinite coordinates |
| `inset-figure` | D's recovered impact and 650 nm index | A rotated drop section; same physical scattering angle as selected sightline | Updates with observer/Sun; empty state when no D exists |
| `elevated-figure` | Sun 15°, same direction construction | Fixed elevated-observer illustration without ground clipping; complete circle requires drops below eye level | Label states fixed parameters, not linked to the ground-observer slider |
| `ray-figure`, `deflection-figure` | Three IAPWS wavelength presets, b/a in [0,.99] | Exact trace and analytic primary θ(u); optional neighboring impacts ±.028 and ±.055, clamped to valid domain | 48 independent ray cases, both reflection counts, endpoint finiteness and spectral ordering |
| `primary-figure`, `secondary-figure` | n=4/3 at each family's stationary impact | One versus two reflections, same geometry routines | Radii 42.029659° and 50.978094° |
| `sky-slice` | Approximate visible-primary/secondary regions | Radial observer-view schematic, not colorimetric scattering output | Reversed order, band explicitly “less light ≠ no light” |
| `density-figure` | Local fold Jacobian 1/sqrt(βR−β) | Normalized to 1 at one degree inside edge; display clipped at 5; not absolute intensity | Analytic asymptote and singular edge labeled |
| `wave-figure`, `wave-mobile` | Committed 25/50/100 μm cases, 650 nm, n=1.332 | β 35–43° at .01°; independently normalized Airy shape and full perpendicular Mie intensity | Independent computation and truncation checks above |
| `polarization-figure` | Same case arrays | Both polarizations divided by perpendicular peak; preserves relative strength | S1/S2 convention explicit; updates with size preset |
| `signature.svg`, social PNG | Finished vector plate plus atmospheric art | Static A/15° state; SVG download and exactly 1200×630 preview | Rendered in Chrome and visually inspected |

## Atmospheric asset provenance

- Tool: built-in `image_gen.imagegen`; model identifier not exposed by the tool.
- Generated output ID: `exec-6d33f8f6-8d62-4297-8508-028ee6a034dc.png`, session `01a0bb2b-b017-7412-b8e3-713d45bb6649`.
- Final project asset: `images/how-do-rainbows-work/rain-landscape.webp` (70,938 bytes).
- No generative edits. Pillow encodes the unchanged 1536×1024 source as WebP, quality 82, method 6. Original retained in Codex's generated-image storage. The final page uses CSS cover cropping (desktop focal position center/66%, mobile 57%/center); no pixel warping of scientific diagrams.
- The social image is rendered from the finished SVG and landscape, not generated as a scientific diagram.

Prompt used with the built-in tool:

> Use case: photorealistic-natural. Asset type: original atmospheric background plate for an illustrated scientific web essay, landscape 1536 by 1024. Panoramic editorial landscape immediately after a rain shower: a broad dark distant curtain of rain over subtle rolling grassland, low horizon at the bottom fifth, luminous moist atmosphere, natural restrained detail. Light comes from behind the camera, illuminating the foreground softly while rain ahead stays dark. Generous quiet storm-blue sky for composited typography and a separately drawn rainbow. No rainbow whatsoever, no Sun disk, no person, no text, no diagram, no labels, no lens flare, no roads or buildings. Fine natural cloud texture, no dramatic bright opening that could be mistaken for a sunward view. Palette storm blue gray, muted olive terrain, pale daylight.

## Reproduce and check

Development only: Python 3.14, Node 24.16.0, installed Chrome. Exact scientific
package versions are pinned in `scripts/rainbow/requirements.txt`: NumPy 2.5.3,
SciPy 1.18.1, miepython 3.3.0 and iapws 1.5.5. Browser tooling uses Playwright
1.63.0. The optional accessibility audit used axe-core 4.13.0.

```powershell
python -m venv .venv-rainbow
./.venv-rainbow/Scripts/python -m pip install -r scripts/rainbow/requirements.txt
./.venv-rainbow/Scripts/python scripts/rainbow/compute.py
node scripts/rainbow/check.cjs
node scripts/rainbow/build.cjs
./.venv-rainbow/Scripts/python scripts/rainbow/preview.py
./.venv-rainbow/Scripts/python scripts/rainbow/qa.py
./.venv-rainbow/Scripts/python scripts/rainbow/qa.py --links
npm install --prefix .rainbow-qa axe-core@4.13.0 --no-package-lock --ignore-scripts
./.venv-rainbow/Scripts/python scripts/rainbow/qa.py --accessibility
python scripts/build_catalog.py
python scripts/seo_check.py how-do-rainbows-work.html sensors-cameras-lidar-radar-imu-gps.html
python scripts/add_hub_breadcrumbs.py --check
python scripts/check_hubs.py
php -l category-map.php
```

The `.venv-rainbow/` and `.rainbow-qa/` directories are local, ignored development
artifacts. Production reads only the root HTML and the optimized landscape; the
social PNG and vector plate are separate share/download assets. Editing content
in the root HTML is supported: the builder replaces only the marked figure/app
slots, preserving prose and metadata. Do not edit generated SVG or embedded JS by
hand; edit `optics.js` or `app.js` and rebuild. After geometry changes regenerate
the preview too. No storage, external scripts, remote fonts or runtime solver are
used. Inputs live in one browser state object, and every page load starts in a
reproducible default state.

## Measured acceptance and limits

- `numerical-validation.json`: published benchmark, independent Bessel comparison, Airy value and multipole-tail checks passed. Geometry script passes 48 path cases plus cone, inversion, spectral-order and endpoint checks.
- `browser-validation.json`: Chrome 153.0.8010.48; 1440×1000, 375×812 light/dark, 1280×500 short viewport, and 640×400 reflow equivalent to 200% desktop zoom. No page overflow or out-of-bounds SVG text; visible scientific labels meet the 14px target. Keyboard, touch, three wavelength presets, all size presets, toggles, reset, empty observer state, reduced motion and no-JS static figures exercised. No application exceptions.
- The 200% check is a CSS-viewport/reflow equivalent, not an OS zoom automation claim. Browser QA initially used localhost; the reproducible script uses the standalone file directly and creates no persistent server. PHP routing is checked separately by the repository gate.
- `accessibility-validation.json`: no automated WCAG A/AA violations in light or dark. Axe leaves contrast review incomplete for SVG, MathML, the photographic background and off-screen scroll regions. Manual palette checks: ordinary ink on paper 14.14:1; muted ink on the bench 7.42:1; muted dark-mode ink on the bench 8.06:1; muted ink on the laboratory surface 6.51:1. Scientific line colors also have labels/pattern distinctions. This is not a claim of external accessibility certification or screen-reader user testing.
- Print: generated A4 PDF, inspected rendered signature plate, drop paths, wave plots and derivation. White surfaces, expanded derivation, visible model parameters, no landscape raster, no controls or sticky navigation. The long study version is 18 pages; tables repeat their headers and may continue across pages.
- Measured payload is recorded in the browser report: about 389 KB raw HTML, 145 KB gzip HTML plus 71 KB WebP, and 21 KB application JavaScript. All budgets pass: initial compressed estimate below 700 KB; complete page below 1.5 MB; hero below 250 KB; JS below 60 KB. Data JSON is not executable JS. Download/social assets are not initial requests.
- A representative local-file run recorded LCP 344 ms, CLS 0 and maximum observed event duration 96 ms. These are local lab measurements, not deployed Core Web Vitals or field INP. The browser report retains the latest run's actual values.
- Missing-image fallback remains readable; monochrome signature construction was reviewed before color/art. Five distinct compositions are present: panorama, ray sequence, linked spatial plate, angular plots/derivation, comparative sky slice and research notebook.
- Independent scientific editorial review checked the observer/D connection, primary/secondary angles, Airy sign and scaling, numerical example and Mie recurrences. It corrected “complementary” to “supplementary” and added local Airy-variable definitions. Comprehension checkpoints are editorial prompts; no real-reader study was conducted.

The host PHP CLI initially parsed its main `php.ini` twice, producing duplicate
extension warnings. For validation only, `PHP_INI_SCAN_DIR` was pointed to the empty
local `.rainbow-qa/php-empty` directory. The main configuration and its extensions
remain loaded once; no diagnostics or rules were disabled and no shared config
was modified. With that correction the page, reciprocal-link page and rendered
index/category SEO checks report zero failures; all 201 breadcrumbs, 15 category
hubs and category-map PHP lint pass.

Production deployment is intentionally separate and requires explicit approval.
