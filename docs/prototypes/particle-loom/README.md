# Particle Loom prototype: weaver debug view (Phases 0, 1 and 1b)

Spec: [`docs/specs/living-particle-loom-warp-weft.md`](../../specs/living-particle-loom-warp-weft.md) (rev. 2). Everything under `docs/` is internal and never deployed.

`weaver-debug.html` holds four blocks, each written to move into `living-particle-loom.html` unchanged:

| Block | What it is |
|---|---|
| `#sm-data` | Physics data: 12 fermions and 5 bosons with sockets (Q, C, I, M), keys, the three socket rules, the vertex table with machine-readable `instances`, couplings at the Z mass, CKM, lifetimes, decay channels for hadrons, leptons, top, W, Z and H. Every value has a `src` key into `sources`. |
| `#lessons` | Scripts for the 8 Lessons: spawns, key tries with `expect: tie/miss`, forced decays, gluon knots, and the text shown at each step. |
| `#weaver` | Seeded event engine, `auditRun`, `socketDerivation`, `samplingCheck`. No DOM, so it runs headless. |
| `#debug-view` | Flat canvas lane view (time left to right) with socket glyphs, tie and miss knots, coupling brightness, boson lanes, a lesson player (mode menu, Next step), signature table, event log, isolate-a-force, labels toggle, audit button. |

## Run it

- View: serve the repo root (`python -m http.server 8765`) and open `/docs/prototypes/particle-loom/weaver-debug.html`. `#audit` runs every check on load (tab title becomes `AUDIT PASS` or `AUDIT FAIL`); `#lesson=N` opens a lesson.
- Gate: `node scripts/particle_loom_audit.cjs [file] [events]`, about 2 s. It runs the socket derivation, PDG and CKM sampling, all 8 lesson scripts, the free loom on five seeds × 10,000 events, then 13 injected faults that must all be caught. When the engine moves into `living-particle-loom.html`, point the script at that file and add it to the deploy gates (the build's gate runner is Python, so wrap it).

## How the engine behaves (rev. 2)

- **Cast:** residents stay for the whole visit (2 protons, 1 neutron, 2 electrons, one neutrino of each flavor). Visitors (μ±, τ±, π±, π⁰, K±, D⁰, B⁻, t t̄, W±, Z, H) only ever end by decaying. Stable decay products (e, ν, γ, gluon pairs from H → gg) drift out after a few seconds; nothing unstable ever leaves.
- **Knots:** every key (γ, g, W, Z, H) fires at the same cadence, 0.6 per second; strength is shown by brightness on one log scale of couplings at the Z mass. A key only ties into a matching socket, so photons and Z bosons tie into W threads (W W γ, W W Z), Higgs knots tie into W, Z and H threads, and nothing ties into a photon thread.
- **Real bosons are threads:** t → b W⁺ makes a W thread that then decays; W, Z and H visitors decay through their PDG channels; H → γγ and H → gg are loop events through a W or top.
- **Scripts:** lesson mode turns off random knots, spawns and natural decays; only the scripted steps happen, and each passes the same audit.

## What the checks cover

- **Socket derivation:** the three rules, applied to the sockets in `sm-data`, reproduce the vertex `instances` exactly (28 classes, none extra, none missing).
- **Every event:** keys only tie into matching sockets; a shown miss really lacks the socket; lesson `expect` values match; W hops only between doublet partners; W, Z and H decays and the π⁰ → γγ annihilation form valid vertices; loops run through a particle that has both the Higgs socket and the product's socket; lane changes only at W knots; color changes only at gluon knots; every color group neutral; no lone quarks; top never in a hadron; charge, baryon number and the three lepton numbers conserved except when a product drifts out; residents and visitors never drift out.
- **Sampling:** 20,000 draws per decaying state match the PDG branching fractions, and quark flavor choices match \|V\|², within 4.5 σ.
- **Faults caught:** knots ignoring sockets, Higgs knots on neutrinos, a neutrino given a charge socket, a vertex removed from the table, broken color neutrality, a lane change without a W, wrong W charge, lepton flavor violation, keys that always miss, a lesson claiming a photon ties into a neutrino, decays ignoring branching fractions, visitors drifting out, and an H → γγ loop through a particle without a charge socket.

## Data provenance

PDG *Review of Particle Physics* 2026: summary tables (quarks, leptons, gauge and Higgs bosons, mesons, baryons), CKM review (rev. March 2026), Higgs review (rev. Aug 2025, Table 11.2), physical constants (G_F, sin²θ_W(M_Z), α_s(M_Z), ħ). Vertex list: Romao and Silva, arXiv:1209.6213. Derived values carry `src: derived` with their inputs and formula: couplings at the Z mass (tree-level relations: g = 2 m_W / v, e = g sin θ_W, g_s = √(4π α_s)), boson and top lifetimes from widths, hadronic remainders, the Z → q q̄ split from PDG's (uū+cc̄)/2 and (dd̄+ss̄+bb̄)/3 averages, and the invisible width split over three neutrinos.

Simplifications, all noted in `sm-data`: hadronic W products are one quark pair; K⁻ 3-pion modes (7.34%), the π⁰ Dalitz mode, H → Zγ and rare Z modes are not drawn; B → τ modes fold into the hadronic remainder; H → WW and ZZ draw both bosons as threads though one is off-shell; gluons from H → gg drift out (their jets are not drawn); a color-connected heavy quark outside a listed hadron uses the matching listed meson's lifetime.

Not yet in `sm-data`: discovery years (need primary sources before Phase R).

## Open questions for David

- **W exchanges in the free loom.** With equal cadence, electron capture and neutrino absorption happen as often as photon exchange, so residents flip between proton and neutron and the W zig-zags dominate the flat view. The contract makes this honest (cadence is presence only), but it may teach "weak interactions are everywhere." Options: keep it; count decays toward the W cadence and add scatters only to make up the difference; or leave scatters out of the free loom and show them only in a lesson.
- **Top lane.** A top lives 0.4 s on screen, so it rarely shows knots in the free loom. Lesson 7 covers it.
