# Particle Loom prototype: weaver debug view (Phases 0 and 1)

**Spec rev. 2 (2026-10-29)** turns this engine into the backbone for a socket grammar, scripted Lessons and a predict-then-check Lab. Its Phase 1b table lists what changes here: fixed cast instead of random spawns and exits, equal knot cadence, real bosons as threads, sockets in `sm-data`, scripted event queues. `socket_check.py` is the enumeration showing the three socket rules reproduce the tree-level vertex list exactly; Phase 1b moves it into the audit gate.

Spec: [`docs/specs/living-particle-loom-warp-weft.md`](../../specs/living-particle-loom-warp-weft.md). Everything under `docs/` is internal and never deployed.

`weaver-debug.html` holds three blocks, each written to move into `living-particle-loom.html` unchanged:

| Block | What it is |
|---|---|
| `#sm-data` | Physics data: 12 fermions, 5 bosons, vertex table, CKM, lifetimes, decay channels. Every value has a `src` key into `sources`. |
| `#weaver` | Seeded event engine plus `auditRun`. No DOM, so it runs headless. |
| `#debug-view` | Flat canvas lane view (time left to right), signature table, event log, isolate-a-force, labels toggle, audit button. |

## Run it

- View: serve the repo root (`python -m http.server 8765`) and open `/docs/prototypes/particle-loom/weaver-debug.html`. Add `#audit` to run the audit on load (the tab title becomes `AUDIT PASS` or `AUDIT FAIL`).
- Gate: `node scripts/particle_loom_audit.cjs [file] [events]`. Runs five seeds × 10,000 events, then injects seven known faults (photon or Higgs knots on neutrinos, a broken color group, a lane change without a W, wrong W charge, lepton flavor violation, an edited vertex rule) and fails unless the audit catches every one. When the engine moves into `living-particle-loom.html`, point the script at that file and add it to the deploy gates.

## What the audit checks on every event

- Each knot is a vertex in `sm-data.vertices`: photons only on charged threads, gluons only on quarks of one color group, Higgs only on massive threads, W only between doublet partners (quarks across generations via CKM, leptons within one generation).
- W decays and annihilations produce a doublet pair carrying the W's charge.
- Lane changes happen only at W knots; color changes only at gluon knots.
- Every color group is neutral after every event; no lone quarks; top never sits in a hadron.
- Charge, baryon number and the three lepton numbers are conserved by every event except entering or leaving the frame.
- The observed signature per lane never includes a forbidden knot type.

## Data provenance

Verified 2026-10-29 against PDG *Review of Particle Physics* 2026: summary tables for quarks, leptons, gauge and Higgs bosons, mesons and baryons; CKM review (rev. March 2026, Eq. 12.27); physical constants (G_F for the Higgs vacuum value). The tree-level vertex list and the absent vertices come from Romao and Silva, arXiv:1209.6213. Derived values (top lifetime from Γ_t, hadronic remainders) are marked `src: derived` with a note.

Simplifications (all recorded in `sm-data` notes): hadronic W products are drawn as a single quark pair (d ū, u d̄, or c s̄); K⁻ 3-pion modes (7.34%) and the π⁰ Dalitz mode (1.17%) are not drawn; B → τ modes are folded into the hadronic remainder because PDG lists only exclusive τ modes; a color-connected heavy quark that is not in a listed hadron uses the lifetime of the matching listed meson (B⁻, D⁰, K⁻).

Changes from the spec's memory anchors under PDG 2026: s 92.9 MeV, c 1.2729 GeV, b 4.186 GeV, t 172.60 GeV, e 0.51099895069 MeV, W 80.3625 GeV, Z 91.1879 GeV, H 125.13 GeV, neutron 878.3 s, B± 1.637 ps, τ→eνν 17.85%, τ→μνν 17.37%, CKM fit updated, KATRIN limit m_ν < 0.45 eV now in the summary table.

Not yet in `sm-data` (Phase 4 reference work): discovery years. A first pass found them only in secondary sources (CERN, Fermilab, DESY, BNL, APS pages read as search summaries), so they need primary pages before they ship.

## Known gaps before Phase 2

- Top threads live about 0.4 s on screen, so most runs show few knots on the top lane. That is faithful (it decays before it can do much), but the 3D view needs a way to call one up.
- In the flat view, gluon knots between up and down lanes cross the charm and top lanes. The 3D loom groups bundles physically, so this goes away there.
