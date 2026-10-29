# Living Particle Loom: warp and weft (redesign spec)

2026-10-29. Replaces the visual direction in [`living-particle-loom-visual-redesign.md`](living-particle-loom-visual-redesign.md) (2026-10-28). Page: `living-particle-loom.html` (live; keep the URL, byline and `datePublished` 2026-10-28). Build rules: `AGENTS.md`, `TODO/README.md` (Rules 1 to 6 are binding even though this spec lives in `docs/specs/`), `TODO/SPEC-AUDIT.md`.

## Why redesign

The original brief: native 3D motion that conveys the **interplay** of fermions and bosons, continuously moving, navigable to each family, very colorful, illustrations over text.

The shipped version promised "you recognize a particle by what it can do," then built the opposite:

- Shapes, sizes, motion and brightness encode nothing, so a five-point legend and an "Illustration · not to scale" chip have to say so.
- Connectors "show families, never forces." Bosons are boxes, never exchanged. Interactions hide behind a dropdown overlay.
- The Chart tab rearranges the same blobs into a grid; the chart does not come *from* the sculpture.
- Pastel-on-navy reads tasteful, not colorful. The 3D is projected but never navigated. The inspector is paragraphs.
- Masses, lifetimes and decays were "intentionally omitted," so the reference below the stage is not a terminal reference.

## Core concept

**Matter is the warp. Forces are the weft.**

- **Warp:** each fermion flavor is a lane of threads running along the time axis, streaming toward the camera forever. Twelve lanes (6 quarks, 6 leptons).
- **Weft:** bosons are the threads that cross between warp threads. Every crossing is a **knot**, and every knot is an allowed Standard Model vertex drawn in Feynman notation: wavy photon, curly gluon, zig-zag W and Z, dashed Higgs.
- **Shuttles:** each boson has a shuttle on a rack at the side of the loom; the shuttle flies across to lay its weft. The Bosons family view looks along this rack.
- **The chart is the loom seen end-on.** Lanes are laid out in cross-section exactly like the conventional chart: rows up-type quarks, down-type quarks, charged leptons, neutrinos; columns generations I, II, III; shuttle rack as the boson column. Swinging the camera to look down the time axis turns the threads into the 17-entry chart. Same data, same objects, no separate grid.
- **Identity by signature.** A particle's identity is the set of knots its thread accepts. With labels hidden, an up quark (gluon, photon, W, Z, Higgs), an electron (photon, W, Z, Higgs), and a neutrino (W and Z only, faint) are visibly different. That is the teaching idea, made literal.
- **The nesting shows itself.** Fermions = quarks + leptons. Threads that take gluon knots are quarks; threads that never do are leptons. Threads without photon knots are neutrinos. The page says this once, in the Families transition, while the camera regroups lanes by signature.

## Encoding contract (acceptance test 1)

Every visual property either encodes a stated quantity or is constant by design. No decorative variation that needs a disclaimer. This table ships on the page as the "How to read the loom" illustration (glyphs, not prose).

| Visual property | Encodes | Notes |
|---|---|---|
| Lane position (row, column) | Flavor: type row × generation column | Same layout as the conventional chart |
| Direction along the warp | Time (toward the viewer) | One line on the stage says so |
| Knot type (line style) | Vertex type (γ, g, W, Z, H, and boson-boson vertices) | Feynman notation, see vertex table |
| Which knots a thread accepts | Which interactions the particle takes part in | The signature; never violated |
| Thread length before it ends in a W knot | Lifetime, **log-scaled** | Order preserved, ratios compressed; mapping printed on the lifetime ladder figure |
| Quark thread hue | Current color charge (r, g, b; antiquarks cyan, magenta, yellow) | Changes at each gluon knot; every bundle sums to white |
| Higgs knot brightness | Higgs coupling, log scale (∝ mass for fermions) | Neutrinos get no Higgs knot (see open questions) |
| Cross-generation W knot frequency for quarks | Relative rate ∝ \|V_ij\|² (CKM) | b→u knots really are rare; inspector offers "show me one" |
| Arrow chevrons on a thread | Particle (with time) vs antiparticle (against time) | Feynman convention |
| Thread thickness, knot size, flow speed, generation | **Constant** | Heavier generations are not bigger or slower |
| Lepton thread finish | Constant chrome (charged) or glass (neutrino) | Colorless because leptons carry no color charge |

The only on-stage text about representation: *"Time flows toward you. Each knot is an allowed Standard Model vertex in Feynman notation; lines are notation, not paths."* The strong-force card adds: *"Quark 'color' is a name for a kind of charge, not a hue."* No other disclaimers anywhere on the stage.

## The weaver (physics engine)

A deterministic, seeded CPU event scheduler emits events from the vertex table. The GPU only renders. Events:

1. **Exchange:** a boson weft connects two threads (photon between two charged threads, Z between any two fermions, gluon between two quarks in a bundle, W between two threads that both change identity, such as e⁻ u → ν_e d).
2. **Decay:** a thread ends at a W knot; the W lays two daughter threads (μ⁻ → ν_μ W⁻, W⁻ → e⁻ ν̄_e). Daughter antiparticles carry reversed chevrons.
3. **Gluon churn:** inside quark bundles, gluon knots swap color between threads continuously (r quark emits r-ḡ gluon and turns green; the absorber turns red). This is the main source of color and motion.

Rules the engine enforces at every event (and asserts in a self-check, see Gates):

- Charge, color neutrality per bundle, baryon number, and lepton number are conserved. Lepton flavor is conserved (flavor basis); oscillation is covered in the neutrino card, not animated.
- Quark threads exist only in color-neutral bundles: baryons (qqq) or mesons (q q̄). Exception: top threads end (t → b W⁺) before forming a bundle.
- Only W knots change a thread's lane. Z, photon, gluon and Higgs knots never change flavor (no tree-level flavor-changing neutral currents).
- Lanes replenish from the far end of the time axis so populations stay steady.
- Stable threads (e, u and d in a proton, neutrinos, the proton bundle) never end. Free neutron bundles (udd) end with the longest finite length on the loom.

## Vertex table (design spine)

This list is the page's core data and its biggest accuracy risk. Rows are textbook tree-level Standard Model vertices; the builder verifies each against the sources in Phase 0 before any rendering work.

| Vertex | Participants | Changes | Example on the loom |
|---|---|---|---|
| f f γ | Any electrically charged fermion | Nothing | e⁻ and u bundle exchange a photon |
| q q g | Any quark | Color only | Gluon churn in a proton bundle |
| g g g, g g g g | Gluons | Color | Gluon weft knots gluon weft (Strong view) |
| f f′ W | Left-handed doublet partners: u↔d-type (all generations via CKM), ℓ↔ν_ℓ (same generation) | Flavor, charge by ±1 | Muon decay, neutron β decay, b → c |
| f f Z | Every fermion, neutrinos included | Nothing | ν_μ e⁻ elastic scattering |
| W W γ, W W Z | W pair with photon or Z | Nothing | Shuttle-rack knots (Bosons view) |
| W W γ γ, W W Z Z, W W Z γ, W W W W | Quartic gauge | Nothing | Bosons view only |
| H f f | Massive fermions, coupling ∝ mass | Nothing | Top threads glow brightest |
| H W W, H Z Z, H H W W, H H Z Z | Higgs with W/Z | Nothing | Bosons view |
| H H H, H H H H | Higgs self-coupling | Nothing | Bosons view; trilinear coupling not yet measured |
| **Absent:** γγ, γZ, ZZZ, Hγγ, Hgg at tree level | | | Shown as "no knot" in the signature strip; H→γγ and gg→H happen through loops (top, W), drawn as a loop diagram in the Higgs card |

Sources: PDG *Review of Particle Physics* (2024 edition plus 2025 web update): "Electroweak model and constraints on new physics," "Quantum chromodynamics," "Higgs boson physics," "CKM quark-mixing matrix," particle listings. Cross-check: Griffiths, *Introduction to Elementary Particles* (2nd ed.), ch. 2 and 9 to 10; Peskin and Schroeder, Feynman rules appendix.

## Scene, camera and navigation

| State | Camera | What the learner sees |
|---|---|---|
| Loom (opening) | Three-quarter view, slow orbit drift, time streaming toward viewer | Whole loom; the gluon-braided quark bundles in the foreground give the og image |
| Quarks | Dolly into the two quark rows | Bundles, color churn, W knots hopping threads between up and down rows |
| Leptons | Dolly to the two lepton rows | Chrome charged-lepton threads with photon, W, Z, Higgs knots; glass neutrino threads with only W and Z |
| Fermions | Pull back so both lanes fill the frame; shuttle rack dims | Lanes regroup by signature: the quark/lepton split happens on screen |
| Bosons | Turn 90° to look along the shuttle rack | Shuttles and boson-boson knots; Higgs field as a faint iridescent medium filling the loom |
| Generations | Lanes slide apart by column | Three copies of one pattern; II and III threads visibly shorter (they decay) |
| Chart (end-on) | Swing to look straight down the time axis | Threads resolve into the 4×3 grid plus boson column; weft keeps flickering as arcs between cells |
| Isolate a force | Any state; one force's knots stay lit | "Who feels this": gluon isolates the quark rows, photon lights everything except neutrinos |

- Camera moves on splines and can be interrupted; a new action redirects the move in flight.
- Family navigation: a pill bar (All, Fermions, Quarks, Leptons, Bosons, Generations, Chart) plus search. Arrow keys walk lanes, Enter inspects, Space pauses, Esc steps back.
- URL fragment restores state, selection, isolated force and pause.

## Interactions

- **Hover/focus a thread:** a label pill tracks it and shows the **signature strip** (five knot glyphs, lit or unlit).
- **Select a thread:** inspector card, mostly illustration: signature strip, a mini Feynman diagram of its main decay (or "stable"), position on the lifetime ladder, mass on a log ruler, and a fact block of charge, spin, color, generation and discovery (year, lab). Text is capped at about two sentences.
- **Select a knot:** the loom freezes and the knot lifts into a 2D Feynman diagram card (SVG, morphed with the View Transitions API) with the process name and real numbers, for example "μ⁻ → e⁻ ν̄_e ν_μ · τ = 2.197 μs." Resume restores the stream.
- **Guess the thread:** labels off, one thread highlighted, four choices. The reveal explains the answer by its signature ("no photon knots, so neutral; no gluon knots, so a lepton: a neutrino"). Streak stored in localStorage with a soft fallback. This is the reader-outcome test, playable.
- **Show me a rare knot:** from a b-quark card, forces a b→u W knot and states its relative rate.

## Visual identity

The stage stays dark in both themes (bloom needs it); the page around it follows `light-dark()` as before.

| Role | Hex | Line style |
|---|---|---|
| Stage background | `#07061A` with a deep violet radial lift `#140F33` | none |
| Color charge red / green / blue | `#FF3B4E` / `#2EE88A` / `#3D7BFF` | quark threads |
| Anticolor cyan / magenta / yellow | `#19E6E6` / `#FF3DF0` / `#FFD23D` | antiquark threads; gluons are twisted two-tone ribbons (color + anticolor) |
| Photon | `#FFE7A8` warm white-gold | wavy |
| W± | `#FF6A3D` coral-orange, chevron shows charge flow | zig-zag |
| Z | `#9D7BFF` ultraviolet | zig-zag |
| Higgs | pearl `#F4F1FF` with thin-film iridescence by view angle | dashed |
| Charged leptons | chrome `#C9D6E8` with teal rim light `#5FE3D9` | solid |
| Neutrinos | glass `#7FA3B8` at about 35% opacity | solid, faint |

Signature element: the gluon-braided quark bundle churning color in the foreground of the Loom view. Build it first and best. The og image (1200×630, lossless WebP) is the Loom state with a proton bundle front and center; the second share artifact is the vertex table.

Typography: keep the current serif display and mono instrument labels. Glyphs and diagrams over prose: every card leads with an illustration.

## Technology

- **Renderer:** vanilla WebGPU (WGSL) only, targeting current browser versions; no library, single self-contained file as the repo requires. Instanced ribbon segments for threads and weft, HDR `rgba16float` target with dual-filter bloom, thin-film shader for the Higgs. Use compute shaders where they simplify the work (ribbon geometry expansion, bloom), not for show.
- **Fallbacks are deferred (David, 2026-10-29).** No WebGL 2 path, no SVG stage substitute, no device-loss recovery until David signs off on the design. Minimum until then: if `navigator.gpu` or an adapter is missing, the stage shows one line ("This view needs WebGPU") and the HTML navigation, inspector and reference stay usable. Do not structure the code around a future fallback.
- **Labels and hit targets are HTML**, positioned from projected 3D each frame (`transform: translate3d`). Thread pills are real buttons.
- **Platform features worth showcasing:** WebGPU, the View Transitions API (knot to card), the Popover API (knot cards, guess-the-thread), CSS anchor positioning (card callouts to pills), scroll-driven animations for the reference section (inside `prefers-reduced-motion: no-preference`), `details name=` accordions.
- **Budgets:** 60 fps on an integrated GPU at 1080p; at most about 4,000 live segments (about 1,500 below 600 px wide); DPR capped at 2. Render loop stops off-screen (IntersectionObserver) and when the document is hidden. The canvas initializes after first paint so the HTML hero is the LCP. CLS 0. INP under 200 ms.
- **Reduced motion:** the stream stops on a static woven frame with all knot types visible; camera moves become crossfades.
- **Accessibility:** canvas `aria-hidden`; every thread, knot card and camera state is reachable by keyboard and announced via a polite live region; guess-the-thread is fully keyboard and screen-reader playable; contrast ≥ 4.5:1 for all HTML labels over the stage.
- **Data:** one `<script type="application/json" id="sm-data">` block holds particles, vertices, CKM magnitudes and lifetimes, each record with a `source` field. Renderer, inspector, reference tables and the checker all read it.

## Reference below the stage (terminal reference)

Rebuild the reference with numbers. Density targets:

| Section | Rows / items | Exemplar row |
|---|---|---|
| Particle table | 17 + antiparticle note | Muon · μ⁻ · 105.66 MeV · −1 · ½ · no color · T₃ −½ (left) · 2.197 μs · e⁻ ν̄_e ν_μ (≈100%) · 1936, Anderson and Neddermeyer |
| Vertex table | ≈18 incl. "absent" row | as above |
| Forces compared | 4 (strong, EM, weak, Higgs interaction) + gravity row marked "not in the Standard Model" | Mediator, mediator mass, range, acts on, what it can change |
| Lifetime ladder (SVG, log scale) | ≈12 rungs | Free neutron 878.4 s; π± 26.0 ns; K± 12.4 ns; muon 2.197 μs; τ 290 fs; B⁰ 1.52 ps; D⁰ 0.41 ps (charm hadrons decay faster than b hadrons, because b decays need the small \|V_cb\|); top ≈ 5 × 10⁻²⁵ s (from Γ_t ≈ 1.4 GeV); W, Z, H from widths |
| Worked decays (each a Feynman card + numbers) | 6 | Neutron β decay (d → u W⁻, W⁻ → e⁻ ν̄_e); muon decay; τ⁻ hadronic vs leptonic; t → b W⁺; H → b b̄ (largest branching fraction) and H → γγ via loops; Z → invisible counts 3 light neutrinos (LEP N_ν ≈ 2.98) |
| Conservation checklist | 6 | Charge, color, baryon number, lepton number, lepton flavor (SM only; oscillation breaks it), what only the W can change |
| Common mistakes | ≥ 8 | "Leptons are a third category beside fermions and bosons" (no: leptons are fermions); "The Higgs gives the proton its mass" (about 1%; the rest is QCD binding energy); "Photons couple to the Higgs" (not at tree level; H → γγ goes through loops); "Gluons are neutral like photons" (gluons carry color and self-interact); "The Z can change flavor"; "Neutrinos are massless" (oscillation proves mass; the SM as written gives none); "Heavier generation = bigger particle"; "Color charge is visible color" |
| Open questions | 5, one line each | Neutrino mass origin; dark matter; matter-antimatter asymmetry; gravity outside the SM; Higgs self-coupling not yet measured |

All numbers above are Rule 1 anchors. Verify against PDG before shipping; date volatile ones inline ("PDG 2024").

## Targeting

- **Mode:** research mode. **Primary query:** "standard model particles interactive" (realistic) with "standard model of particle physics" as the head term Wikipedia and CERN own. **Secondary (niche utility, the keep-open angle):** "allowed feynman vertices list," "which particles feel which forces," "standard model vertices cheat sheet," "particle lifetimes table," "why don't neutrinos interact electromagnetically." Question-shaped H2s in the reference should match these.
- **Niche utility test:** a physics student drawing Feynman diagrams for homework keeps the vertex table, lifetimes and decay cards open while working. That is the reason the reference exists.
- **Draft `<title>` (59 chars):** `The Particle Loom: Standard Model Forces & Feynman Vertices`
- **H1:** The Living Particle Loom
- **Draft meta description (check length with `scripts/seo_check.py`):** "Watch the Standard Model weave itself: 12 matter threads, 5 force carriers, every allowed Feynman vertex. Identify any particle by what it feels, with masses, lifetimes and decays."
- **Reader outcome:** given any Standard Model particle, the reader can name the forces that act on it, draw its allowed vertices and main decay, and identify an unlabeled particle from its weave.
- **Success metric:** GSC impressions and clicks on the vertex and "which forces" queries at day 60; og-image shares; popularity score rank inside Engineering & Science.
- **Volatile-facts register (page rating: STABLE core, SLOW-DRIFT numbers):** top, W and Higgs masses (PDG updates yearly; W mass has the CDF 2022 outlier vs later ATLAS/CMS/LHCb results); neutrino mass upper bound (KATRIN, cosmology); CKM magnitudes; Higgs branching fractions and self-coupling status; neutron lifetime (beam vs bottle discrepancy). Re-verify each PDG release; add these to the freshness routine's notes for this sheet.
- **Index category:** Engineering & Science (unchanged in `category-map.php`; hub `engineering-science`).
- **Reading conditions:** laptop or desktop, calm, curious or studying; phones arrive from social shares. Phone: stage 70svh, simplified segment budget, inspector becomes a bottom sheet, guess-the-thread works one-handed. Print: the stage prints as the end-on chart SVG; reference tables print in full.
- **Jurisdiction scope:** N/A. Units: masses in eV/c² multiples, lifetimes in SI seconds.
- **Cross-links:** `quantum-physics-vs-quantum-bullshit.html` (both directions); `nuclear-power-reactor-types.html` (beta decay and the weak force, both directions); `nuclear-preparedness.html` (beta radiation entry, outbound only if it fits); hub `engineering-science`. Update `llms.txt` and the catalog description.

## Remove from the current page

The "Illustration · not to scale" chip, the five-point "Reading the loom" legend, the Scene/Families/Chart tab bar, the Interactions dropdown, the "separate examples" captions, the "quantitative values intentionally omitted" note, and the proton/electron/neutrino blob scene.

## Anti-goals

No graviton or gravity thread; no string-theory imagery; no "molasses" or "crowd at a party" Higgs analogy; no atoms, orbits or nuclei drawn as solar systems; no size or speed encoding of mass; no particles beyond the Standard Model except one-line open questions; no sound.

## Build phases and gates

0. **Physics data (gate).** Build `sm-data` from PDG with a `source` on every record. Verify every vertex row against two of the named sources. Nothing renders until this passes. If a value cannot be verified, omit it.
1. **Weaver plus a flat debug view.** Seeded engine, 2D top-down lane view, and an `#audit` fragment that generates 10,000 events and asserts the rules (no photon knot on a neutrino, no gluon knot on a lepton, no lane change except at W knots, every bundle color-neutral, conservation laws hold, top never bundles). **David reviews the debug view before Phase 2**; this is where the concept proves itself or dies cheaply.
2. **Renderer and camera states.** WebGPU renderer, bloom, all camera states, reduced motion. **David's design sign-off follows this phase**; fallbacks (WebGL 2, no-GPU SVG stage, device-loss recovery) become a separate phase only after it.
3. **Interactions.** Signature strips, inspector cards, knot-to-Feynman-card morph, isolate-a-force, guess-the-thread, search, keyboard, URL state.
4. **Reference, SEO, og.** Reference tables from `sm-data`, metadata, og capture, cross-links, `llms.txt`, catalog rebuild.

Optional machine gate (automation ladder rule 4): `scripts/check_particle_loom.py` parses `sm-data` and checks it against an independent vertex-rule list and conservation table; wire it into the pre-push hook if it earns its keep.

## Acceptance tests

1. **Encoding contract:** every visual property is in the contract table; nothing varies decoratively.
2. **Signature test:** with labels hidden, a viewer can tell electron from neutrino and quark from lepton by the weave alone. Test on at least two people who did not build it.
3. Audit fragment passes 10,000 events with zero violations.
4. End-on chart view matches the conventional 17-entry layout cell for cell.
5. Every number on the page traces to a `source` in `sm-data`.
6. Performance budgets met; console clean in current Chrome, Edge, Firefox and Safari; 375 px renders without horizontal scroll; reduced motion honored; WCAG 2.2 AA for the HTML interface.
7. The site gates pass (`scripts/seo_check.py`, catalog freshness, hubs). Deployment only with David's go-ahead.
