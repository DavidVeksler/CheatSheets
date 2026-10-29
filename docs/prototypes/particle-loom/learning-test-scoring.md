# Particle Loom learning test (Phase 1c): running and scoring

Gate for all 3D work (spec [`living-particle-loom-warp-weft.md`](../../specs/living-particle-loom-warp-weft.md), Phase 1c, Acceptance 3 and 4). Page: [`learning-test.html`](learning-test.html).

## Run a session

1. **Testers:** at least three adults who did not build the page and know no particle physics beyond school. Someone who already knows the Standard Model will score high before the lessons, so their gain cannot reach 3 (see Pass criteria).
2. **Give each one a code** (T1, T2, T3...). No names go into the page or the results.
3. **Send the file.** `learning-test.html` is self-contained: it opens from disk in a current Chrome, Edge, Firefox or Safari, with no server and no WebGPU. A laptop is best; phones work.
4. **Don't help.** No hints, no answering questions mid-session, no looking things up. If you had to step in, note what you said in the sheet.
5. **Collect the results.** The last screen has Copy and Download buttons; the tester sends you the JSON. If a tester closes the tab mid-session, the same browser offers "Resume".

Preview without saving anything: `learning-test.html#jump=practice:0` (practice items 0 to 11), `#jump=post`. `#audit` runs the answer-key and replay checks in the page.

## What the tester does (about 25 minutes)

| Part | Content |
|---|---|
| Before | Questions 1 to 6 (a to f below), no feedback |
| Practice | Lessons 1 to 3, each followed by one check; the "Bosons are threads too" card; Lab 1 to 5 (predict, then the loom plays the answer and names the socket or conservation law that decided it) |
| After | Questions 1 to 6 again, then the labels-off questions 7 and 8, then an optional comment |

## Rubric

Questions b, c, f, g and h are auto-scored (the `auto` block in the results). The choice in a is auto-scored; you mark its reason. You mark d and e by hand. One point each; no half points (note half answers in the sheet, they help the redesign).

| Q | Correct | Point only if |
|---|---|---|
| a | No | "No" **and** the reason says the neutrino has no electric charge (or photons interact only with electric charge). "Too small", "too fast" or no reason scores 0. |
| b | Gluon only | Exactly "Gluon". |
| c | Muon neutrino only | Exactly "A muon neutrino". |
| d | The W is charged, the Z is not | Says the W has electric charge and the Z does not, or that photons couple to charge. Mass, lifetime or "the Z is like a heavy photon" scores 0. |
| e | Photons have no Higgs coupling; the decay goes through a loop | **Both:** (1) photons are massless, have no Higgs coupling or no mass socket, and (2) the decay goes through a loop of W bosons or top quarks, or through heavy charged particles. Either part alone scores 0. |
| f | Muon | "A muon". |
| g (labels off) | Thread B | Electron vs neutrino from knots alone. |
| h (labels off) | Thread D | Quark vs lepton from knots alone. |

## Score sheet

| Tester | Before (a to f) | After (a to f) | Gain | Labels off (g, h) | Hard practice items | Notes |
|---|---|---|---|---|---|---|
| T1 | /6 | /6 | | /2 | | |
| T2 | /6 | /6 | | /2 | | |
| T3 | /6 | /6 | | /2 | | |

"Hard practice items" are the `practice` entries with `"correct": false`.

## Pass criteria

- **Acceptance 3:** at least two of three testers score 5 or 6 out of 6 after, and each gains at least 3. A tester who scored 4 or more before cannot gain 3; report them separately and recruit another tester.
- **Acceptance 4:** testers get g and h right (electron vs neutrino, quark vs lepton from knots alone).
- **If the target is missed:** revise the socket grammar or the lessons before any 3D work. Which questions failed points at the cause: a and b mean sockets are not read; c and f mean partners are not read; d and e mean boson sockets are not landing; g and h mean knots are not linked to sockets.

## Design notes for the reviewer

- **Every answer key is derived.** The keys are hand-written in `#items`, and `#lab-check` re-derives each from `#sm-data` and the socket rules. The gate (`node scripts/particle_loom_audit.cjs`) fails on any mismatch, on drift between this page's shared blocks and `weaver-debug.html`, and if a Lab replay breaks the event audit.
- **Additions to the spec:** the "Bosons are threads too" card. Lessons 1 to 3 never show boson sockets, and questions b, d and e depend on them. Also: questions use "interact directly" rather than "tie", so the before-test needs no page vocabulary.
- **Leak checks:** labels-off and hidden threads are drawn in one neutral color, figure lanes keep question order (not chart order), Lab scenes show only pre-answer lanes, and correct answers sit in different positions.
- Lab items avoid repeating the test items, but they practice the same ideas: Z partners (vs gluon in b), naming a hidden W (vs a muon in f), H γ γ as the impossible vertex (feeds e).
