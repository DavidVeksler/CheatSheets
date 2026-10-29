# Living Particle Loom: warp and weft (redesign spec, rev. 2)

Rev. 2, 2026-10-29. Rev. 1 (same day, in git history) built the loom as the lesson; rev. 2 makes it the place where lessons happen. Replaces the visual direction in [`living-particle-loom-visual-redesign.md`](living-particle-loom-visual-redesign.md) (2026-10-28). Page: `living-particle-loom.html` (live; keep the URL, byline and `datePublished` 2026-10-28). Build rules: `AGENTS.md`, `TODO/README.md` (Rules 1 to 6 are binding even though this spec lives in `docs/specs/`), `TODO/SPEC-AUDIT.md`. Prototype and data: [`docs/prototypes/particle-loom/`](../prototypes/particle-loom/README.md).

## Why redesign

The original brief: native 3D motion that conveys the **interplay** of fermions and bosons, continuously moving, navigable to each family, very colorful, illustrations over text.

The 2026-10-28 build promised "you recognize a particle by what it can do," then encoded nothing (shapes, sizes and motion were decorative, so a legend had to say so), drew no forces ("connectors show families, never forces"), produced the chart as a separate grid, and left masses, lifetimes and decays out of the reference.

## What rev. 2 changes, and why

Rev. 1 fixed the encoding but would still not have taught. Its critique:

- **It showed outcomes and hid causes.** A neutrino never took a photon knot, but nothing on screen said why (no electric charge). Learners would memorize a pattern instead of a rule.
- **The signature only existed statistically.** Telling a muon from an electron meant counting knot types on one thread over minutes. In the debug view the *table* taught, not the weave.
- **A passive, random stream is a weak teacher.** Animations rarely beat equivalent static graphics (Tversky, Morrison and Bétrancourt, "Animation: can it facilitate?", 2002), each knot is gone before it can be studied, and the process the learner needs may not happen while they watch. Nothing invited a prediction.
- **The encoding contract cheated.** Knot rates were arbitrary yet read as strength (Z exchange as common as photon exchange). Threads left the frame about as often as they decayed, so length did not read as lifetime. The cast (B mesons beside protons beside top pairs) was a composed scene, which the old page at least admitted.
- **Lanes by flavor fought bundles.** In the flat debug view a proton's gluon knots crossed the charm and top lanes. (In the 3D cross-section u and d are neighbors; see Atlas.)
- **Time toward the viewer aimed the camera at the past.** New knots formed far away and small.
- **Bosons were second-class.** A real W from a top decay looked like a virtual exchange; a learner could conclude bosons are not particles.

Rev. 2 answers each: a **socket grammar** that makes the cause visible, **three layers** (Atlas, Lessons, Lab) so the learner predicts and checks instead of watching, an encoding contract with no arbitrary rates, a fixed cast whose threads end only by decaying, real bosons as threads, and the present placed nearest the camera.

## Learning goals

The relationships the page must teach, in order:

1. **Family tree:** fermions are quarks and leptons; bosons carry forces; leptons are fermions, not a third category.
2. **Charges decide forces:** each force acts on exactly one kind of charge (photon: electric; gluon: color; W and Z: weak; Higgs: mass coupling).
3. **Who feels what follows from (2).**
4. **Partners:** a W turns a fermion into its doublet partner (u ↔ d-type across generations via CKM; e ↔ νₑ within a generation).
5. **Generations:** three copies of one pattern; heavier copies decay down through W knots.
6. **Confinement:** quarks appear only in color-neutral groups; gluons carry color themselves.
7. **Conservation:** charge, color, baryon and lepton number limit what can become what.

**Reader outcome (acceptance test for content):** given any Standard Model particle and any boson, the reader predicts whether they couple and names the charge that decides it; draws a valid W decay for a muon, a neutron and a top quark; and names an unlabeled thread from its knots.

## Core concept

**Matter is the warp. Forces are the weft. Charges are the sockets the weft ties into.**

- **Warp:** each fermion flavor is a lane of threads along the time axis.
- **Weft:** bosons cross between threads. Every crossing is a **knot**, and every knot is an allowed Standard Model vertex in Feynman notation (wavy photon, curly gluon, zig-zag W and Z, dashed Higgs).
- **Sockets:** every thread carries small glyphs for the charges it has. A boson's weft can only tie into its matching socket. The knot happens *because* the socket is there, and the learner can see it.
- **The chart is the loom seen end-on.** The lane cross-section is the conventional chart (rows up-type, down-type, charged leptons, neutrinos; columns generations I to III; boson column at the side).

Three layers share one engine, one data block and one 3D scene:

| Layer | Role | The learner |
|---|---|---|
| **Atlas** (the loom) | Ambient, explorable, beautiful; the home screen and og image | Browses families, orbits, isolates a force, opens any thread or knot |
| **Lessons** (8 chapters) | Scripted, learner-paced, replayable sequences that each teach one relationship | Steps forward and back; the loom slows to a single thread or knot |
| **Lab** (predict, then check) | Questions generated from the vertex rules; the loom plays the answer | Commits to a prediction before seeing the result |

## The socket grammar

### Sockets and keys

| Socket | Glyph | Fermions that carry it | Bosons that carry it |
|---|---|---|---|
| **Q** electric charge | Gold notched ring; notch count = \|Q\| in thirds (1, 2 or 3); notches lean forward for +, back for − | Quarks, charged leptons | W± |
| **C** color | Tri-segment ring lit in the thread's current color (antiquarks: anticolor) | Quarks | Gluons (color + anticolor) |
| **I** weak | Half-clasp that points toward the thread's doublet partner lane | All fermions | W± |
| **M** mass (Higgs coupling) | Pearl ring, brightness = coupling on the shared log scale | Massive fermions | W±, Z, H |

| Key (boson) | Ties into | Rule |
|---|---|---|
| γ | Q | |
| g | C | |
| W± | I | Turns the thread into its partner; carries charge ±1 |
| Z | I | Never changes flavor |
| H | M | |

Neutrinos show an **empty, dashed M socket**: their mass is known to be nonzero (oscillation; KATRIN m_ν < 0.45 eV) but the Standard Model as written gives them no Higgs coupling. The open question becomes a visible object.

### Three rules

1. A key ties only into its matching socket.
2. A fermion line takes one key at a time. A boson pair takes one or two keys; two only if both are gauge keys (γ, g, W, Z) or both are Higgs keys.
3. Charge is conserved at every knot (so one W key on a W pair is forbidden, and a W key changes a fermion line to its partner).

**These rules reproduce the complete tree-level vertex list exactly.** Checked 2026-10-29 by enumeration over the five fermion and boson classes: 28 vertex classes derived, 28 in Romao and Silva (arXiv:1209.6213), no extras, none missing, including every absence (no γγγ, γγZ, γZZ, ZZZ, Hγγ, Hgg, HγZ, HHZ, HWZ). Phase 1b makes this a permanent gate (see Gates).

What the learner can now *explain*, not just observe:

- Neutrinos ignore photons and gluons: they have only the weak socket.
- Gluons tie into each other (g g g) but photons never do: gluons carry color; photons carry no electric charge.
- A photon ties into a W (W W γ) but not a Z: the W is charged; the Z is not.
- The Higgs does not touch photons or gluons directly: neither has a mass socket. H → γγ happens through a loop of W or top threads, which *do* have sockets (Lesson 7 draws it).
- Z Z Z does not exist: the Z has no weak socket of its own.

**Honesty notes (one line each, placed in the lesson that needs them, never on the stage):** sockets are a picture of real charges (quantum numbers); the rules are a compact way to state the tree-level couplings, not a mechanism. The W ties only to the left-handed part of a fermion, and the Z's coupling also depends on electric charge; both live in an "advanced" toggle on the weak lesson and in the reference.

## Atlas: the loom

### Layout: lanes and bundles

- Lanes sit in the chart's 4 × 3 cross-section, so u and d (row 1 and row 2, column I) are neighbors. A proton's three threads run side by side in two adjacent lanes.
- Each hadron is wrapped in a **harness**: a translucent sleeve around its member threads. Gluon knots live on the inner surface of the harness and never cross other lanes. Mesons that span columns (B⁻ = b ū) stretch their harness diagonally; this is the visual cue that heavy-flavor hadrons are short-lived.
- The flat debug view unrolls the grid into 12 rows; its lane crossings are an artifact of that view, not of the loom.

### Time and viewpoint

- **Now is the bright fell edge nearest the camera.** New knots form large in the foreground; woven history recedes into depth and fades at about 30 s.
- On-stage line (the only one): *"Now is the bright edge nearest you. Each knot is a Standard Model vertex in Feynman notation."*

### Cast

- **Residents** stay for the whole visit: two protons, one neutron, two electrons, one neutrino of each flavor.
- **Visitors** are unstable particles that enter at the fell edge and **always leave by decaying**: μ±, τ±, π±, π⁰, K±, D⁰, B⁻, t t̄. A visitor never fades out.
- **Stable decay products** (electrons, neutrinos, photons) drift out of the loom sideways and fade. So: *ends at a knot* = decayed or annihilated; *fades sideways* = left the loom. The two never overlap.
- The "How to read" illustration carries one line: *"The loom gathers particles that rarely meet in one place, so you can compare them side by side."*

### Real bosons are threads

A real (on-shell) W, Z or H, such as the W in t → b W⁺, is drawn as **its own short thread with its own sockets**, in the boson column's lane, ending in its decay. Virtual exchanges stay weft. The Bosons view puts the five bosons side by side as threads with sockets. Bosons are particles too; the page shows it.

### Camera states

| State | Camera | What the learner sees |
|---|---|---|
| Loom (opening) | Three-quarter view from the fell edge, slow drift | Proton harness in the foreground churning color; the og image |
| Quarks / Leptons / Fermions | Dolly to the rows | Sockets come forward; the quark/lepton split is the color socket |
| Bosons | Turn to the boson column | Five boson threads with their sockets; boson-boson knots |
| Generations | Columns slide apart | Three copies; visitors in II and III end sooner |
| Chart (end-on) | Look straight down the time axis | Threads resolve into the 17-entry chart; sockets become the chart's charge annotations |
| Isolate a force | Any state | Only that key's sockets glow; every thread that lacks the socket dims |

Camera moves on interruptible splines. Pill bar (All, Fermions, Quarks, Leptons, Bosons, Generations, Chart) plus search; arrow keys walk lanes, Enter inspects, Space pauses, Esc steps back. URL fragment restores state.

## Encoding contract (acceptance test 1)

Every visual property encodes a stated quantity or is constant by design. Ships on the page as the "How to read the loom" illustration (glyphs, not prose).

| Visual property | Encodes | Notes |
|---|---|---|
| Lane position | Flavor (chart row × generation column) | |
| Depth | Time; now is nearest | |
| Sockets on a thread | The charges the particle carries | Q, C, I, M; empty dashed M for neutrinos |
| Knot type (line style) | Vertex type | Feynman notation |
| Knot brightness | Coupling constant at the Z mass, one shared log scale | g_s ≈ 1.2, g ≈ 0.65, e ≈ 0.31, Yukawa y = √2 m / v (top ≈ 1, electron ≈ 3 × 10⁻⁶). Anchors; verify in Phase 1b |
| Knot cadence | **Constant** for every allowed vertex type | Presence only; brightness carries strength |
| Visitor thread length | Lifetime, log-scaled, with a lifetime ruler alongside | Visitors always end at a knot |
| Fading sideways | Stable product leaving the loom | Never a decay |
| Quark hue | Current color charge; antiquarks carry anticolor | Changes only at gluon knots; every harness sums to white |
| Harness | A hadron (color-neutral group) | |
| Chevrons | Particle (with time) vs antiparticle (against time) | |
| Thread thickness, speed, generation | **Constant** | Heavier is not bigger |
| Lepton finish | Chrome (charged) or glass (neutrino) | No color socket, no hue |

The brightness rule has a lesson in it: at the Z mass the weak coupling is *larger* than the electromagnetic one. The weak force is weak at everyday energies because the W and Z are heavy, not because the coupling is small (Lesson 2).

## Lessons

Eight learner-paced chapters. Each is a scripted event queue run by the same weaver (so the audit covers it), with step, back and replay, one idea per chapter, and at most two sentences of text per step. Every chapter ends with one Lab question.

| # | Chapter | What happens | The one idea |
|---|---|---|---|
| 1 | What a particle carries | Electron, neutrino and up quark threads side by side; sockets light one by one | A particle is its set of charges |
| 2 | Forces are keys | A photon, gluon, Z and Higgs each try all three threads; ties and misses | Each force ties into one charge. Advanced: weak is strong at 91 GeV; heavy W and Z make it short-ranged |
| 3 | Partners | A muon reaches a W knot and becomes a muon neutrino; the W lays e⁻ and ν̄ₑ | The W swaps a fermion for its partner and conserves charge |
| 4 | Inside a proton | Harness opens; colors swap at gluon knots; gluons tie into gluons | Color stays neutral; gluons carry color. One line: three valence quarks summarize a proton that also holds a sea of gluons and quark pairs |
| 5 | Neutron decay | d → u W⁻, W⁻ → e⁻ ν̄ₑ; the harness becomes a proton | Beta decay is one W knot |
| 6 | Generations | B⁻ → D⁰ → K⁻ → π⁻ cascade beside a long-lived muon, on the lifetime ruler | Three copies; heavier ones fall down the ladder; charm hadrons decay faster than b hadrons because b needs the small \|V_cb\| |
| 7 | Mass and the Higgs | M sockets glow by coupling; top brightest; neutrino socket empty with "?"; H → γγ drawn as a top or W loop | The Higgs couples to mass; photons get there only through loops; neutrino mass is open |
| 8 | The chart | Camera swings end-on; the loom becomes the 17-entry chart with sockets as annotations | The chart is a cross-section of everything above |

## Lab: predict, then check

Questions are generated from `sm-data` (vertex rules, decays), so every answer is checkable by the audit. The learner commits before the loom plays the result. Feedback always names the socket or conservation law that decided it.

| Question type | Example | Direction |
|---|---|---|
| Will it tie? | "Will this photon tie into the νμ thread?" | Charges to knots |
| What can it become? | "At a W knot, what can this muon turn into?" (pick a lane) | Partners |
| Balance the decay | "t → b W⁺, then W⁺ → ? ?" (pick products; charge and lepton number shown as meters) | Conservation |
| Which boson? | "Which bosons can tie into a gluon?" | Boson sockets |
| Name the thread | Labels and sockets hidden; knots play; four choices | Knots to charges (inference) |
| Spot the impossible | Three knots, one forbidden (e.g. H γ γ) | Absences |

Progress and streaks in localStorage with a soft fallback. Wrong answers queue the matching Lesson.

## The weaver (physics engine)

Built in Phase 1 (`docs/prototypes/particle-loom/weaver-debug.html`, block `#weaver`). A seeded CPU event engine emits only allowed vertices; the GPU only renders. It already enforces: color neutrality per harness, conservation of charge, baryon number and the three lepton numbers, lane changes only at W knots, no tree-level flavor-changing neutral currents, top never in a hadron, PDG 2026 branching fractions with CKM-weighted flavor choice.

**Changes required in Phase 1b:**

| Phase 1 behavior | Rev. 2 |
|---|---|
| Random spawns from a weighted cast; any entity fades out after about 22 s | Residents fixed; visitors only end by decaying; stable products drift out sideways |
| Knot rates differ by type (gluon 0.7, photon 0.45, Z 0.3, Higgs 0.5 per second) | One cadence for every allowed vertex type; strength moves to brightness |
| Real W in top decay drawn as weft | Real W, Z, H become short threads with sockets |
| No sockets in `sm-data` | Q, C, I, M per particle; key per boson; the three rules |
| Audit checks knots against `requires` fields | Audit also enumerates the socket rules and requires an exact match with the vertex list |
| Free-running stream only | Scripted event queues for the 8 Lessons and Lab replays, run through the same audit |
| No coupling constants | g_s, g, e at the Z mass and Yukawa couplings, verified against PDG 2026 |

## Vertex table

| Vertex | Participants | Changes | Socket reason |
|---|---|---|---|
| f f γ | Electrically charged fermions | Nothing | γ → Q |
| q q g | Quarks | Color only | g → C |
| g g g, g g g g | Gluons | Color | Gluons carry C |
| f f′ W | Doublet partners: up ↔ down-type (all generations via CKM), ℓ ↔ ν_ℓ (same generation) | Flavor; charge by ±1 | W → I |
| f f Z | Every fermion, neutrinos included | Nothing | Z → I |
| W W γ, W W Z | W pair with γ or Z | Nothing | W carries Q and I |
| W W γ γ, W W Z Z, W W Z γ, W W W W | Quartic gauge | Nothing | Two gauge keys on a W pair |
| H f f | Massive fermions, coupling ∝ mass | Nothing | H → M |
| H W W, H Z Z, H H W W, H H Z Z | Higgs with W/Z | Nothing | W, Z carry M |
| H H H, H H H H | Higgs self-coupling | Nothing | H carries M; trilinear not yet measured |
| **Absent at tree level:** γγγ, γγZ, γZZ, ZZZ, Hγγ, Hgg, HγZ | | | No matching socket; Hγγ, Hgg, HγZ arise only through loops |

Sources: PDG *Review of Particle Physics* 2026 (F. Takahashi et al., Int. J. Mod. Phys. A 41, 2630011), verified 2026-10-29 and stored in `sm-data`; complete tree-level rule set: Romao and Silva, arXiv:1209.6213. Cross-check: Griffiths, *Introduction to Elementary Particles* (2nd ed.), ch. 2 and 9 to 10.

## Visual identity

The stage stays dark in both themes (bloom needs it); the page around it follows `light-dark()`.

| Role | Hex | Form |
|---|---|---|
| Stage background | `#07061A`, radial lift `#140F33` | |
| Color charge r / g / b | `#FF3B4E` / `#2EE88A` / `#3D7BFF` | Quark threads; C socket segments |
| Anticolor c / m / y | `#19E6E6` / `#FF3DF0` / `#FFD23D` | Antiquarks; gluons are two-tone twisted ribbons |
| Photon key, Q socket | `#FFE7A8` warm gold | Wavy weft; notched ring |
| W key | `#FF6A3D` coral, chevron shows charge flow | Zig-zag weft |
| Z key | `#9D7BFF` ultraviolet | Zig-zag weft |
| I socket | Silver clasp `#C9D6E8`, tinted by the key that ties in | Half-clasp |
| Higgs key, M socket | Pearl `#F4F1FF`, thin-film iridescence | Dashed weft; ring |
| Charged leptons | Chrome `#C9D6E8`, teal rim `#5FE3D9` | |
| Neutrinos | Glass `#7FA3B8` at about 35% opacity | |
| Harness | White at 6 to 10% opacity, color-tinted at gluon knots | Sleeve |

Signature element: the proton harness in the foreground, colors swapping at gluon knots, sockets catching the light. Build it first and best. og image (1200 × 630, lossless WebP): that shot. Second share artifact: the socket table (sockets and keys).

Typography: keep the current serif display and mono instrument labels. Every card and lesson step leads with an illustration.

## Technology

- **Renderer:** vanilla WebGPU (WGSL) only, current browsers; no library; single self-contained file. Instanced ribbon segments (threads, weft, harness), instanced socket glyphs, HDR `rgba16float` target with dual-filter bloom, thin-film shader for M sockets and the Higgs. Compute shaders where they simplify (ribbon expansion, bloom).
- **Fallbacks deferred (David, 2026-10-29)** until design sign-off. Minimum: without WebGPU the stage shows "This view needs WebGPU"; Lessons, Lab and reference keep working in HTML and SVG (Lab questions and Feynman cards are SVG, not canvas).
- **HTML for everything readable:** labels, hit targets, lesson text, Lab choices. View Transitions (knot to Feynman card, lesson steps), Popover (Lab, knot cards), anchor positioning (callouts to sockets), scroll-driven animation for the reference (reduced-motion guarded), `details name=` accordions.
- **Budgets:** 60 fps on an integrated GPU at 1080p; about 4,000 live segments (1,500 below 600 px); DPR ≤ 2; render loop stops off-screen and when hidden; HTML hero is the LCP; CLS 0; INP < 200 ms.
- **Reduced motion:** the Atlas stops on a woven frame; Lessons advance by step only; camera moves crossfade.
- **Accessibility:** canvas `aria-hidden`; every thread, socket, knot, lesson step and Lab question is reachable by keyboard and announced in a polite live region; Lab is fully playable with a screen reader; contrast ≥ 4.5:1 for HTML over the stage.
- **Data:** one `<script type="application/json" id="sm-data">` block; every value carries `src`.

## Reference below the stage (terminal reference)

This is where the page earns search traffic; it is no longer last in the build order (see Phases).

| Section | Rows / items | Exemplar |
|---|---|---|
| Particle table | 17 + antiparticle note | Muon · μ⁻ · 105.66 MeV · −1 · ½ · sockets Q I M · 2.197 μs · e⁻ ν̄ₑ νμ (≈100%) · discovery (primary source required) |
| Sockets and keys | 4 sockets × 17 particles, plus the three rules | The socket table above, as a matrix |
| Vertex table | 19 rows + absent row | As above, with the socket reason |
| Couplings | 4 rows (strong, EM, weak, Higgs) at the Z mass + one line on running | g_s, e, g with PDG 2026 values; why weak is weak at low energy |
| Forces compared | 4 + gravity row marked "not in the Standard Model" | Mediator, mass, range, socket, what it can change |
| Lifetime ladder (SVG, log scale) | ≈ 12 rungs | From `sm-data.lifetimes_s` (PDG 2026) |
| Worked decays (Feynman card + numbers) | 6 | Neutron β; muon; τ hadronic vs leptonic; t → b W⁺; H → b b̄ and H → γγ via loops; Z → invisible counts 3 light neutrinos (PDG 2026 fit N_ν = 2.996 ± 0.007, anchor) |
| Conservation checklist | 6 | Charge, color, baryon number, lepton number, lepton flavor (SM only; oscillation breaks it), what only the W changes |
| Common mistakes | ≥ 8 | Leptons as a third category; Higgs gives the proton its mass (about 1%); photons couple to the Higgs; gluons are neutral; the Z changes flavor; neutrinos are massless; heavier generation = bigger; color charge is a visible color |
| Open questions | 5 | Neutrino mass origin; dark matter; matter-antimatter asymmetry; gravity; Higgs self-coupling |

Numbers not already in `sm-data` are Rule 1 anchors until verified.

## Targeting

- **Mode:** research and study. **Primary query:** "standard model particles interactive"; head term "standard model of particle physics" (owned by Wikipedia and CERN). **Secondary (keep-open angle):** "allowed feynman vertices list," "which particles feel which forces," "why don't neutrinos interact electromagnetically," "why do gluons interact with each other," "particle lifetimes table." Question-shaped H2s match these.
- **Niche utility test:** a physics student drawing Feynman diagrams keeps the socket table, vertex table and decay cards open while working.
- **Draft `<title>` (59 chars):** `The Particle Loom: Standard Model Forces & Feynman Vertices`
- **H1:** The Living Particle Loom
- **Draft meta description (verify length with `scripts/seo_check.py`):** "See why each Standard Model particle feels the forces it does: charges as sockets, forces as keys, every Feynman vertex, with masses, lifetimes and decays to test yourself on."
- **Reader outcome:** see Learning goals.
- **Success metric:** learning test gain (Acceptance 3); GSC impressions and clicks on the vertex and "why" queries at day 60; og shares; popularity rank in Engineering & Science.
- **Volatile-facts register (STABLE core, SLOW-DRIFT numbers):** W, top and Higgs masses; couplings at the Z mass; neutrino mass limits (KATRIN, cosmology); CKM; Higgs branching fractions and self-coupling status; neutron lifetime (beam vs bottle). Re-verify each PDG release (2026 edition in use); add to the freshness routine's notes.
- **Index category:** Engineering & Science (hub `engineering-science`).
- **Reading conditions:** laptop or desktop, calm, studying; phones from social shares. Phone: stage 70svh, Lessons and Lab as bottom sheets, one-handed Lab. Print: end-on chart SVG plus reference.
- **Jurisdiction:** N/A. Units: masses in eV/c² multiples, lifetimes in seconds.
- **Cross-links:** `quantum-physics-vs-quantum-bullshit.html` (both ways); `nuclear-power-reactor-types.html` (beta decay, both ways); `nuclear-preparedness.html` (beta radiation, outbound if it fits); hub `engineering-science`; `llms.txt` and catalog description.

## Remove from the current page

The "Illustration · not to scale" chip, the five-point "Reading the loom" legend, the Scene/Families/Chart tab bar, the Interactions dropdown, the "separate examples" captions, the "quantitative values intentionally omitted" note, the proton/electron/neutrino blob scene.

## Anti-goals

No graviton or gravity thread; no string-theory imagery; no "molasses" or "crowd at a party" Higgs analogy; no solar-system atoms; no size or speed encoding of mass; nothing beyond the Standard Model except one-line open questions; no sound; **the random stream is never the lesson**.

## Build phases and gates

**Status 2026-10-29:** Phases 0 and 1 done (`docs/prototypes/particle-loom/`; gate `node scripts/particle_loom_audit.cjs`). Rev. 2 adds 1b and 1c and splits Phase 2 so the cheap, risky questions are answered first.

0. **Physics data.** Done: PDG 2026, `src` on every value.
1. **Weaver, flat debug view, audit.** Done.
1b. **Engine and data for rev. 2.** Sockets and keys in `sm-data`; couplings at the Z mass (PDG 2026); resident/visitor cast; constant cadence; real bosons as threads; scripted event queues for Lessons and Lab. Gate additions: socket rules must reproduce the vertex list exactly; every Lesson and Lab replay passes the event audit; sampled decay frequencies match branching fractions within statistical tolerance.
1c. **Learning test on a flat prototype (gate).** A 2D page (SVG, no WebGPU) with sockets on threads, Lessons 1 to 3 and the Lab. Test with at least three people who did not build it: the six-question pre/post test (Acceptance 3) and the labels-off naming test. If the target is missed, revise the grammar before any 3D work. David recruits testers; the agent builds the page and the scoring sheet.
2a. **WebGPU sketch (gate).** Cross-section lanes, fell-edge viewpoint, harness sleeves, socket legibility at 1440 and 375 px; no bloom or polish. David signs off on viewpoint and legibility.
2b. **Renderer polish and camera states.** Bloom, iridescence, all Atlas states, reduced motion. **David's design sign-off**; fallbacks become their own phase only after it.
3. **Lessons and Lab in 3D**, inspector cards, knot-to-Feynman morph, search, keyboard, URL state.
R. **Reference** from `sm-data`. Can run in parallel from now on; it does not depend on the renderer.
4. **SEO, og, catalog, `llms.txt`, cross-links.** Deploy only with David's go-ahead.

## Acceptance tests

1. **Encoding contract:** every visual property is in the contract; nothing varies decoratively; knot cadence is equal across vertex types.
2. **Socket derivation:** the three rules reproduce the tree-level vertex list exactly (gate).
3. **Learning test:** six questions before and after one session (Lessons 1 to 3 plus Lab), at least three testers. Target: at least two of three score ≥ 5/6 after, each gaining ≥ 3. Questions: (a) Does a photon interact with a neutrino, and why? (b) Which bosons tie into a gluon? (c) What can a muon become at a W knot? (d) Why does a photon tie into a W but not a Z? (e) Why does the Higgs not couple directly to photons, and how does H → γγ happen? (f) Name an unlabeled thread from its knots.
4. **Labels-off test:** testers name electron vs neutrino and quark vs lepton from knots alone.
5. Event audit passes on five seeds × 10,000 events and on every scripted Lesson and Lab replay; all injected faults caught.
6. End-on chart matches the conventional 17-entry layout cell for cell.
7. Every number on the page traces to a `src` in `sm-data`.
8. Performance budgets; clean console in current Chrome, Edge, Firefox, Safari; no horizontal scroll at 375 px; reduced motion honored; WCAG 2.2 AA for the HTML.
9. Site gates pass (`scripts/seo_check.py`, catalog freshness, hubs).

## Decisions taken in rev. 2 (David can overrule)

- Socket grammar as the core teaching device, with the three rules stated as a mnemonic for real couplings.
- Knot strength shown by brightness on one log scale of couplings at the Z mass; cadence equal.
- Present nearest the camera (reverses rev. 1's "time flows toward you").
- Fixed resident cast plus decaying visitors; stable products leave sideways; the composed cast is named in one line.
- Real W, Z, H drawn as threads.
- Chirality kept out of the main grammar (advanced toggle and reference only).
- Branching fractions from PDG 2026 drive decays; CKM picks the quark flavor (rev. 1 said frequency ∝ \|V\|² only).
- A human learning test (1c) gates all 3D work; the reference moves into a parallel track.
