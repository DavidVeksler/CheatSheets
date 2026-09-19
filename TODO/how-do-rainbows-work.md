# How do rainbows work? — implementation spec

**Target:** `how-do-rainbows-work.html`  
**Status:** specification only; not yet traffic-ranked.  
**Purpose:** an original HTML/CSS design showcase and progressive visual explanation, from a curious lay reader to research-level optics. Implementation and deployment are separate work.

## 1. Editorial contract

Make the explanation happen in the pictures. The page should feel like an illustrated scientific instrument that gradually becomes a research notebook. Its achievement is the continuity between a beautiful sky, a geometrically correct explanation, and a deeper mathematical model. A rainbow gradient behind ordinary cards does not satisfy this brief.

This is an explicitly requested design/personal-study project under TODO/README.md Rule 0, not a broad informational SEO traffic bet. Judge the showcase by explanatory clarity, visual originality, and whether its construction is reproducible. Do not claim the result is impossible to make by hand or proof of a model's superiority; the artifact must demonstrate its merit.

The motivating conversation supplies a progression, not publishable evidence. Exclude all population percentages, rankings of people's understanding, and historical superiority claims. Do not use the linked NSF survey to substantiate rainbow knowledge. Depth labels describe the material, never the reader's intelligence.

**Core sentence:** A rainbow is sunlight redirected by many droplets into particular viewing directions; its position depends on the observer.

The first screen earns curiosity; the first three chapters deliver a complete everyday explanation. Later chapters deepen and qualify that explanation without declaring the earlier one false. Research depth requires equations, defined assumptions, reproducible examples, and model limitations—not a list of advanced terminology.

## 2. Targeting and acceptance outcome

- **Primary query:** how do rainbows work.
- **Secondary queries:** why are rainbows curved; why is a rainbow 42 degrees; how do double rainbows form; rainbow refraction and reflection; rainbow Airy theory and Mie scattering.
- **Intent:** research/curiosity, low stress; useful to teachers, students, photographers, and optics readers.
- **Title:** `How Do Rainbows Work? From Sunlight to Wave Optics`.
- **H1:** `How do rainbows work?`
- **Deck:** `Follow the light. Change your point of view. Keep going until rays become waves.`
- **Meta description:** `Explore how rainbows work through original visual diagrams: follow sunlight through a raindrop, discover your viewing cone, and descend from everyday geometry into wave optics.`
- **Reader outcome:** predict where a rainbow can appear, trace its light path, explain why its arc belongs to the observer, and choose an appropriate ray or wave model for a specified phenomenon.
- **Success:** all comprehension checks below pass; shareable signature figure and usable deep links work. After release, compare signature-figure shares and return visits with the site's existing measurement capabilities; organic traffic is secondary. Do not add tracking infrastructure for this spec.
- **Category:** existing `Engineering & Science` in `category-map.php`.
- **Scope:** worldwide; no jurisdiction-dependent guidance.
- **Reading conditions:** leisurely phone reading outdoors or indoors, desktop exploration, classroom projection, and printed study. Large labels and short narrative units come before fine chart detail. Print preserves scientific diagrams and derivations while removing decorative raster imagery.
- **Staleness:** STABLE physics. Recheck source links at implementation and when broken. Refractive-index datasets, computational-library versions, image-generation model names, and browser support require verification when used; keep tool versions in production notes, not evergreen explanatory prose. Do not hand-edit `refresh-status.json`.
- **Cross-links:** outbound to `celestial-navigation.html` for angular observation, `sensors-cameras-lidar-radar-imu-gps.html` for polarization/imaging context where relevant, and `quantum-physics-vs-quantum-bullshit.html` for the distinction between models and claims. Consider one natural reciprocal link from the sensors page. Put a small process/provenance link to `how-its-built.html` in the byline; do not interrupt the science with AI marketing.

## 3. Visual identity: daylight becoming an optical bench

Use a continuous progression from luminous atmospheric space to precise scientific drawing. Early sections have generous, panoramic compositions. Middle sections resemble a clean optical bench. Late sections grow denser, with aligned equations and plots. Maintain the same type family and annotation grammar throughout.

**Palette:** daylight paper `#F7F4EC`, ink `#142538`, muted ink `#46566B`, storm `#182B43`, dark surface `#0D1726`, pale line `#C8D5DE`. Spectral accents: red `#D94B54`, orange `#E58A37`, gold `#E8BE49`, green `#4AAB82`, blue `#478ED1`, violet `#8A6BD1`. These are design colors, not a calibrated wavelength-to-RGB model. Use dark ink for labels on light surfaces; test actual combinations. Never use yellow body text on white.

**Typography:** `Georgia, 'Times New Roman', serif` for large editorial headings; `system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif` for explanation and labels; `ui-monospace, SFMono-Regular, Menlo, monospace` for measured values. Use native MathML for equations with an adjacent verbal reading. No font download is necessary.

**Recurring grammar:** a small numbered observer glyph; solid arrows for propagation; dashed lines for sightlines/extensions; normal vectors in neutral gray; named angles with arc marks; wavelength labels alongside color. Separate axes, ray paths, and decorative spectrum ribbons visually. Each figure states its frame: observer view, side section, drop section, or angular plot.

The spectrum appears in a narrow chapter rail, light paths, plot legends, and transitions between surfaces. Body text stays neutral. Avoid repeating rainbow borders, card grids, glowing glass panels, seven equal hard color stripes, or continuous animated backgrounds.

### Signature element: “Your rainbow”

A three-view plate joins **what you see**, **where you stand**, and **one droplet**. On desktop, the main perspective construction occupies roughly two-thirds of the plate, with the sky view and drop section stacked beside it. Labels bridge the views by shared identifiers, not long crossing leader lines.

The main view shows an observer at the cone apex, the antisolar axis, a translucent wireframe viewing cone, a rain volume, a horizon, and a few sampled contributing drops at different distances. The cone is a set of sight directions, not a physical luminous shell. Do not draw a single flat curtain of drops as the universal location of a rainbow.

One observer-position control moves between A and B within an illustrative rain field. Recompute which sampled drops can send the selected color toward that observer; update the sky inset and emphasized rays. Some contributing regions may overlap: do not claim neighboring observers can never receive light from any common drop. Keep sunlight effectively parallel, and label the scene's distances as illustrative rather than measured.

The image is successful only if the reader can infer: “I have changed which light reaches my eye,” without first reading a paragraph. The observer glyph must be visually dominant enough to prevent a droplet-centered cone interpretation.

## 4. Image generation, SVG, and 3D: capability allocation

Use OpenAI image generation for one original atmospheric plate, with an optional second crop/variant only if needed for the mobile composition. Use calculated SVG for every explanatory diagram. Raster art cannot be the only evidence for a scientific claim.

| Asset | Production method | Contract |
|---|---|---|
| Opening rain landscape | OpenAI-generated raster | Broad rain curtain and directional light, low horizon, quiet space for type; no rainbow, labels, Sun disk, diagram, or prominent person baked in. Add the bow as a separate controlled layer. |
| Hero bow | SVG arcs with soft, restrained compositing | Correct primary color order; intended observer-centered composition. Mark the combined scene as an illustration. Its color/intensity rendering is illustrative. |
| Observer cone | Analytically constructed 3D points projected into SVG | Known camera, explicit coordinates, depth ordering, horizon, axis and angle annotations. No guessed perspective paths. |
| Droplet cutaway and ray bundles | SVG generated from ray intersections/refraction | Exact common geometry reused in all chapters; no image model draws rays or normals. |
| Caustic and wave plots | SVG from computed arrays | Labeled units and conventions; retain generating code and inputs. No decorative curves presented as data. |
| Section transitions | CSS surfaces, clipping, restrained gradients | Explain continuity without full-screen filters or texture downloads. |
| Social preview | Rendered composition of finished assets | Exactly 1200×630 at `images/how-do-rainbows-work.png`; title plus observer/cone/arc, legible at thumbnail size. |

**Image prompt direction:** panoramic editorial landscape after a rain shower; dark distant rain against a luminous clearing; subtle terrain; low horizon; natural light and restrained detail; no rainbow, no text, no diagrams, no lens flare; leave generous quiet sky for composited graphics. Request a separate portrait composition if cropping destroys the mobile scene. This is art direction, not a promise of generation fidelity.

Use the imagegen skill when producing those assets during implementation. Record tool/model identifier if exposed, prompt, edits, output provenance, and final crop in `docs/how-do-rainbows-work-production.md`. Review the generated background for conflicting light direction and distracting artifacts before compositing. Never ask it to fabricate a scientifically authoritative diagram. If a generation fails, revise the art direction; a CSS-only temporary background is acceptable during development, but the final showcase includes the requested original generated imagery.

Save optimized artwork under `images/how-do-rainbows-work/`. The HTML has embedded CSS/JS and inline scientific SVG; local raster illustrations are the explicit asset dependency. No runtime image API, secrets, bundler, external rendering engine, or live model inference. A development-only Python geometry/plot generator is allowed; its output must be committed and the page must run without it.

**Why not a freely orbiting 3D scene?** Camera freedom creates occlusion, labels on the wrong surfaces, and interactions unrelated to the lesson. Use a fixed oblique projection plus orthographic insets. A projection helper and depth-sorted SVG give inspectable geometry and sharp printing at much lower complexity. A transition between frames uses a dissolve and shared highlights; do not suggest that a perspective scene literally morphs into its cross-section.

## 5. Progressive storyboard and content contract

Minimum **32 substantive entries** across eight chapters, at least four per chapter. Each entry supplies purpose, a concrete case, an appropriate quantitative anchor, and a limitation/mistake; do not turn them all into cards. Numerical anchors below require verification before publication. Keep the common story visible; optional native disclosures hold algebra expansions and methods, not missing core explanations.

Near the opening, add a compact quick-reference strip: Sun behind you; rain in the viewing direction; primary bow near 42° from the antisolar direction; one internal reflection for the primary. Link each item to the figure explaining it. Include a “Choose your depth” anchor rail: See → Trace → Locate → Derive → Compare → Resolve → Calculate → Investigate.

| Chapter / depth | Four required entries | Dominant composition and reader checkpoint |
|---|---|---|
| 1. What are you actually seeing? / fundamentals | Sun–rain–eye relationship; white light and continuous spectrum; angular appearance versus physical object; seeing part of a circle | Panoramic generated scene with controlled bow and four short anchored observations. Check: identify the direction opposite the Sun. |
| 2. What happens inside one drop? / fundamentals | Entry refraction; wavelength-dependent bending; internal reflection; exit refraction toward an eye | Large circle sliced across the page, then a three-step ray sequence sharing its coordinates. Check: put the three events in order. Explicitly distinguish partial reflection from total internal reflection. |
| 3. Why a circle—and why your circle? / working knowledge | Antisolar point; constant-angle cone; horizon clipping and Sun elevation; changed observer and contributing drops | Signature three-view plate. Include ground and elevated-observer cases. Check: explain why walking toward a bow cannot reach its “end.” |
| 4. Why approximately 42°? / working knowledge | Snell's law with angle conventions; impact parameter and incidence; deflection minimum; concentration of neighboring rays | A ray-bundle fan beside a deflection curve with a linked selected ray. Follow with a compact worked derivation. Check: distinguish an individual exit ray from the caustic direction. |
| 5. What makes the second bow? / working knowledge | Two internal reflections; reversed color order; primary/secondary angular regions; Alexander's dark band | Two drop paths paired with a radial sky cross-section and one comparison table. Check: predict order of colors and which gap is comparatively dark; do not draw it as zero light. |
| 6. Where do rays stop being enough? / advanced | Geometric caustic singularity; finite wave pattern/Airy approximation; supernumeraries and size dependence; polarization | A ray-density plot gives way to a wave-intensity plot on a clearly declared angular convention. Add paired polarization curves. Check: identify which observed structure ray optics cannot predict. |
| 7. How would you calculate a real bow? / graduate/research | Size parameter and refractive index; Lorenz–Mie amplitudes and intensity; Debye separation and ray-family correspondence; source spectrum, solar disk and size-distribution averaging | Aligned model ledger, reproducible input/output example, and honest model-comparison plot. Check: choose inputs needed for a stated scattering calculation and say which averaging removes fine structure. |
| 8. What breaks the ideal picture? / research frontier | Nonspherical drops; higher orders and sunward geometry; stationary phase/fold-caustic route to Airy behavior; limits and convergence of numerical approximations | Research notebook with a derivation ladder, three parameterized investigation briefs, and sources tied to claims. Check: distinguish established theory from an approximation and a still-uncomputed case. |

After chapter 3, provide a quiet “You can now explain the everyday rainbow” recap with a link onward. Do not hide the advanced chapters behind a quiz or an unlock interaction. Deeper readers can enter directly at a chapter anchor with enough local definitions to orient themselves.

### Advanced depth must be earned

Chapter 4 includes a completed worked example using a clearly stated constant refractive index (candidate `n = 4/3` as an idealization), solving the stationary deflection condition and converting scattering/deflection angle to angular radius. Do not substitute the approximate 42° headline for the calculation.

Chapter 6 includes an actual evaluated Airy-profile example with its scaled coordinate and mapping explained. A generic sine wave or hand-shaped SVG path is not a diffraction simulation. Clearly separate monochromatic intensity from a displayed full-color spectrum.

Chapter 7 defines the sphere/plane-wave assumptions, size parameter, scattering amplitudes, polarization convention, and Debye indexing convention. Include at least one fully specified monochromatic spherical-drop case with verified numerical output and a reproducible method. A live Mie solver is not required: use a verified development-time implementation and commit sampled output. Any color rendering requires a declared illuminant, wavelength sampling, observer/color-matching data, normalization, and gamut treatment; otherwise show monochromatic curves only.

Chapter 8 gives a compact, mathematically meaningful chain from a scattering integral through coalescing stationary points to the cubic-phase/Airy form, defining symbols and the domain of validity. It need not derive all of Maxwell theory. Investigation briefs must have an input change, predicted observable, suitable method, and failure criterion. Examples: broaden the drop-size distribution; compare primary and secondary approximation error; perturb a spherical drop into an oblate model. The final example requires a nonspherical method—do not pretend spherical Mie code performs that calculation.

## 6. Tables and compact reference material

Only two major tables. Their density provides lookup utility late in the page; the opening remains visual.

**Bow comparison:** 6 rows, columns phenomenon / optical mechanism / viewing region and color behavior / diagnostic feature / limitation. Rows: primary, secondary, supernumerary, fogbow, higher-order bows, glory as a contrasting phenomenon. Exemplar at the intended final depth: **Primary | refraction → one internal reflection → refraction | near 42° from the antisolar direction, red outside violet (approximate; wavelength/index dependent) | usually brighter than the secondary under comparable viewing conditions | the angle alone does not predict brightness, fringe structure, or visibility.** Verify the anchor and qualify against the selected sources before shipping.

**Model selection:** 5 rows, columns model / inputs / predicts / cannot predict / use when. Rows: geometric ray tracing, Airy approximation, Lorenz–Mie sphere solution, Debye decomposition, nonspherical numerical scattering. Exemplar: **Geometric ray tracing | spherical drop, refractive index and incident direction; `n = 4/3` for the worked idealization | paths and stationary deflection | wave fringes and finite intensity at the caustic | locating the primary ray-family concentration; switch models for supernumeraries.** Debye decomposition must be described as a way of separating contributions, not an unrelated competing physical theory.

**Common mistakes:** an eight-entry illustrated correction list: rainbow as an object; one drop sending the whole visible bow to one eye; refraction alone; total internal reflection as the primary mechanism; exactly seven discrete colors; 42° measured from the Sun; darkness meaning no scattered light; spherical Mie theory explaining arbitrary drop shapes. Use small figure fragments, not another table.

## 7. Interaction and implementation boundaries

Use one reusable optical apparatus with three local control panels, not a collection of unrelated widgets:

1. **Observer panel (chapter 3):** A/B observer control and Sun-elevation range. Show numeric output and reset. Update axis, horizon clipping, and contributor selection consistently.
2. **Ray panel (chapter 4):** impact-parameter range and a small set of wavelength presets with sourced refractive indices. Show the selected path and its point on the deflection graph. Provide “show neighboring rays” as a native checkbox.
3. **Wave panel (chapters 6–7):** three validated drop-size presets and model visibility toggles using committed computed arrays. Display selected parameters, units, and model scope. No continuous control that merely stretches a static curve and calls it a new calculation.

Controls are enhancements. Initial inline SVG contains a fully labeled, useful static state. With JavaScript disabled, all arguments and completed examples remain, and inactive controls are hidden. Use HTML buttons/ranges with keyboard operation; never require dragging directly on SVG or hovering. Announce a compact value summary after changes without flooding a live region.

Scrolling changes composition and emphasis, not access to information. Optional sticky figure behavior is confined to its chapter on wide displays with adequate viewport height. Ordinary scrolling always works; no scroll hijacking, forced timing, autoplay ray particles, or pinning a chapter for multiple screens. Reduced motion uses direct state changes. Support light/dark system preferences without making the scientific color code change meaning.

Use a shared pure geometry layer: ray–sphere intersections, surface normals, Snell refraction, reflection, angle conversion, and fixed-camera projection. Keep model coordinates separate from SVG screen coordinates. Changing a control updates geometry and labels from one state object. Clip rays deliberately; never draw a plausible-looking path by eye. The illustration uses normalized distances unless stated otherwise.

## 8. Responsive, print, and asset budgets

At 375 px, stack the signature plate as sky view → observer section → drop detail, each with its own short caption. Replace a wide perspective construction with a legible side section if labels cannot fit; preserve the full construction as a separate optional enlarged view. Keep controls under the figure they affect. No core scientific annotation below a 14 px rendered design target. Wide late-stage tables may scroll inside labeled wrappers; narrative and figures must not cause page overflow.

Print uses white surfaces and dark labels, expands derivations, substitutes representative states for controls, repeats parameter captions, and keeps figure/caption blocks together. Include the signature construction, both drop paths, and advanced plots. Remove the landscape art and sticky navigation.

Planning budgets, not measured results: initial transfer at most 700 KB compressed, complete page plus illustrations at most 1.5 MB, embedded application JS at most 60 KB uncompressed, hero raster at most 250 KB. Reserve hero dimensions and prioritize it; defer below-fold rasters. Prefer a few dozen useful rays to thousands of DOM nodes. Profile before adding blur or SVG filters. Record actual payload and measured rendering results in the production notes; repo performance gates remain binding.

## 9. Research and figure provenance

Research the exact assumptions and plot conventions before implementing each scientific figure. The current source reconnaissance establishes useful starting points, not blanket verification of this spec. Every numeric anchor is subject to TODO/README.md Rule 1.

| Claims/data needing verification | Source and implementation action |
|---|---|
| Wave scattering, finite-source and size-distribution averaging, polarization, reproducible sphere examples | Philip Laven, [Simulation of rainbows, coronas, and glories by use of Mie theory](https://www.philiplaven.com/Publications/AO-42-03-p436.pdf), Applied Optics 42 (2003). Read relevant equations/figure parameters, then reproduce a chosen case; do not copy its figures as original artwork. |
| Ray families, model boundaries, Debye analysis | Author's [Optics of a water drop](https://www.philiplaven.com/index1.html) and [publication list](https://www.philiplaven.com/Publications.html). Follow to the original paper for any advanced quantitative claim. |
| Observer geometry and pedagogical cross-check | Les Cowley's [Primary Rainbow Cone](https://www.atoptics.org.uk/rainbows/primcone.htm) and [Rays through a large raindrop](https://www.atoptics.org.uk/rainbows/primrays.htm). Expert explanatory references; independently derive geometry and use primary literature for numeric claims. |
| Water dispersion/temperature and wavelength presets | Locate and verify the applicable IAPWS refractive-index release or an original measured-data paper. Record temperature, wavelength units, environmental assumptions and validity range before setting presets. |
| Airy scaling, stationary-phase derivation, approximation error | Select original rainbow asymptotics literature through the cited papers' references. Record the exact equation and coordinate/sign convention; verify against independent computed values. |
| Nonspherical drops and higher-order visibility | Select original papers from the author's publication index, including the higher-order visibility research. Verify which conclusions depend on ideal spheres and viewing conditions. |

Build a figure manifest in the production notes: figure ID, source equation/data, author-created geometry or generated art, parameters, units, angular convention, reproduction command, validation result, and approximations. A scientist should be able to audit the plotted quantities without reverse-engineering SVG. Treat decorative spectrum colors as schematic; never imply colorimetric accuracy without the required computation.

## 10. Build sequence and quality gates

1. Finalize the three-depth outline and the table rows/exemplars against current repository guidance. Resolve source/equation choices and complete the primary numerical example before artwork.
2. Build the signature plate in monochrome first. Verify observer/cone geometry and drop paths. Capture desktop and 375 px states; the concept must explain itself without gradients.
3. Build the shared ray calculations and static ray/deflection diagrams. Verify angle conventions against the independent analytic example. Then add the controls.
4. Produce and inspect original atmospheric art with OpenAI image generation; composite the opening and apply the palette/type system. Match lighting and avoid stretching raster images into scientific annotations.
5. Finish the eight chapters, independently validated wave data, model ledger and research derivation. Give every equation nearby variable definitions and every plot a verbal conclusion.
6. Perform browser, accessibility, numerical, print, no-JS, and content QA below. Produce the social image from the finished figure; integrate category, catalog and natural cross-links through the documented workflow.
7. Commit the implementation and validation artifacts. Delete this spec only after the complete page satisfies its acceptance criteria. Deployment still requires explicit user authorization under AGENTS.md.

**Scientific checks:** ray intersections lie on the drop boundary; incidence/refraction satisfy the chosen index ratio; reflection respects the surface normal; incoming/outgoing vectors use consistent directions; the computed stationary deflection agrees with the independent derivation; primary and secondary order/position are correct; the observer is the viewing-cone apex; wave curves reproduce the selected reference case within a stated tolerance appropriate to its precision. Test finite values at control endpoints. No numerical tolerance may be invented merely to pass a test.

**Visual checks:** desktop and 375 px screenshot review; dark/light mode; 200% zoom; keyboard and touch; reduced motion; short viewport; print preview; no-JS; missing-image state. No clipped labels, unlabeled color-only distinctions, giant empty scroll regions, rays passing through captions, or text on busy sky. The advanced chapter plots must be readable at their actual rendered size.

**Comprehension checks:** an everyday reader can explain the three optical events and locate the antisolar point using the figures; an intermediate reader can explain the cone and stationary deflection; a technical reader can reproduce one numerical result and state why the next model is necessary. Use these as editorial review prompts; do not claim user-testing results unless real readers were tested.

**Showcase acceptance:** the signature plate is the most polished artifact; at least five distinct compositions are visible across the page (panorama, ray sequence, linked spatial plate, plot/derivation, comparative sky slice, research notebook); generated art and vector explanation share a coherent composition; every promised scientific interaction has an honest model behind it. A stack of cards, decorative diagrams without explanatory force, or a beautiful hero followed by a text essay fails this brief.
