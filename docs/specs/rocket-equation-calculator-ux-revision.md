# Rocket equation calculator: UX revision spec

Target: `rocket-equation-calculator.html`. Source: UX critique of 2026-11-14
(renders at 1440 and 375 px, both themes, all presets, both modes, error path).
Scope is presentation, interaction and copy. The physics, `solve()`, sources and
the honesty contract in [`../titan-crosspromo.md`](../titan-crosspromo.md) do not change.
Delete this file when the revision ships.

Goal: a first-time visitor understands "faster exhaust, less propellant, less
thrust" by moving one control within ten seconds, on a phone as well as a desk.

## Constraints that hold throughout

- `window.rocketCalculator.{solve,presets,getResult}` keeps its shape and results.
  `scripts/check_rocket_equation.py` numeric expectations (rel_tol 1e-10) must
  still pass; update the script only where this spec changes markup or units.
- Existing element ids stay (`mode`, `wet`, `final`, `dv`, `exhaust`, `constraint`,
  `thrust`, `power`, the `*-unit` selects, `error`, `share`, `reset`, `results`,
  `chart`, `primary`, `out-*`). New elements get new ids.
- Single self-contained file, no CDN, no new runtime dependency. All AGENTS.md
  tech invariants apply.
- No new facts without a primary source. Figures in this spec are anchors
  (TODO/README.md Rule 1); verify or omit.
- Fictional Titan values keep a design label wherever they appear as data. What
  goes is the repeated sentence-level caveat, not the label.

## Phase 1: correctness and legibility fixes

### 1.1 Worked case C formula mismatch
The formula line computes retained mass (6,065.31 t) while the answer shows
propellant (3,934.69 t). Change the formula to
`mₚ = 10,000 × (1 − e^(−100/200))` so the line above the answer produces the
answer. Body text keeps "6,065.31 t remains".

### 1.2 Raw floats in inputs
Programmatic writes to inputs (`loadPreset`, the mode, constraint and unit
handlers, shared-URL load) currently show values such as `6065.306597126334`.

- Add `setField(el, value)`: displays the value at 6 significant digits with
  trailing zeros trimmed, and stores the exact value in `el.dataset.exact`.
- `read()` uses `dataset.exact` when the visible value still equals the formatted
  one; any user `input` event on that field deletes `dataset.exact`.
- The share link serializes the exact value.
- Acceptance: after Long Passage then Mission mode, no visible input shows more
  than 7 significant digits, and `getResult()` is unchanged to 1e-10.

### 1.3 Presets carry their natural units
Add a `units` object per preset and apply it in `loadPreset` instead of forcing
t / Isp / kN:

| Preset | Mass | Exhaust | Thrust |
|---|---|---|---|
| chemical | t | Isp 350 s | 1 MN |
| ion | kg | Isp 3,000 s | 0.1 N |
| passage | t | 200 km/s | 63.7 kN |
| tug | t | Isp 2,500 s | 85 N |
| ascent | t | Isp 345 s | 221 kN |

Keep `resetUnits()` consistent with whatever units the preset applied. Update
the check script where it assumes the old forced units.

### 1.4 Output formatting
- No E notation anywhere in the UI. Replace `n()`'s scientific branch with
  `1.24 × 10⁷` style, and prefer scaled units first (days, t, GW).
- Replace the `#summary` line with one plain sentence built from the result:
  "Changing velocity by 7.90 km/s burns 90 t of this 100 t vehicle in 5 min 9 s
  of engine time." Mission-mode variant: "A 100 km/s mission that ends at
  6,065 t must start at 10,000 t." Keep "engine time is not trip time" only in
  the Gotchas section.
- `duration()` gains minutes and years: `5 min 9 s`, `681 days (1.86 y)`.

### 1.5 Glyphs and the headline number
- Replace every `ꜰ` (U+A730) with real markup: `m<sub>f</sub>`, and convert the
  other Unicode subscripts in visible formulas (`m₀`, `vₑ`, `Pⱼ`, `Pᵢₙ`) to `<sub>`
  so they share one font. Plain-text contexts (`<title>`, `aria-label`, meta)
  use `mf`, `m0`, `ve`.
- `.big-number`: remove the trailing space text node; the unit span gets
  `margin-inline-start: .2em`, `font-size: .32em`, baseline aligned. "10,000 t"
  and "7.9032 km/s" must read as one quantity.

### 1.6 Controls
- Remove the visible Calculate button (results are live). Keep the submit
  handler for Enter.
- Action row: "Copy link" as the single outlined primary; Reset and Print as
  quiet text buttons.
- Presets become two labelled groups: **Teaching** (Chemical, Ion) and
  **Titan 2100 · fictional** (Long Passage, Cargo tug, Ascent). Drop the
  asterisks.
- After a manual edit the description reads "Edited from Long Passage." (or the
  relevant preset name) and no preset shows a pressed or outlined state once
  focus leaves it.

### 1.7 Caveat budget
One caveat per context, stated once. Edits:

| Location | Action |
|---|---|
| Masthead aside `<small>` | Delete. On mobile show the formula and its one-sentence gloss instead of hiding them. |
| Preset descriptions | Delete "this is not a named vehicle", "*Titan presets are fictional designs", "not a flight specification", "not a qualified Hall-thruster system". State inputs only. |
| `custom()` text | "Edited from <preset>." Nothing about feasibility. |
| `.small` under fields | Keep the post-burn mass definition; move the jet power definition to a field hint (4.1). |
| `.note` under the tool | One line: "Ideal model: constant exhaust velocity, no gravity, drag or steering losses. Equations and limits ↓" |
| Chart figcaption | Numbers only; drop "does not assume..." and "held outside this comparison". |
| Comparison table | Remove the "Small-spacecraft survey." prefix from seven rows (the caption says it). Keep the design tags on the last three rows. |
| Worked cases A and B | Drop "not a named rocket" and "illustrative electric spacecraft" sentences. |
| Titan section | Keep the single `.design` tag. Delete "not evidence of an available engine". |

Gate (add to the check script, counting visible body text): "fictional" ≤ 4,
"not a " ≤ 3 outside the Gotchas section, "ideal" ≤ 8.

## Phase 2: the chart becomes the interaction

### 2.1 Replace the dual-axis chart
Two stacked panels sharing one log x-axis (exhaust velocity, 1 to 1,000 km/s):

- **Top, "Propellant share of launch mass"**: linear 0 to 100%, the current
  `1 − e^(−Δv/vₑ)` curve, area-filled in the accent colour.
- **Bottom, "Thrust at this jet power"**: log y with ticks on round decades
  (1 N, 1 kN, 1 MN as applicable), violet line.

No shared plot area, so no line crossing. The "left linear, right logarithmic"
sentence goes away. Title stays "Faster exhaust. Less mass. Less push."

### 2.2 Engine-class bands
A strip between the panels and the x-axis marks where engine families sit,
derived only from rows already sourced in the comparison table (Isp × g₀):
hydrazine monopropellant, the 350 s chemical teaching point, gridded ion, Hall,
nuclear thermal (≈900 s), Direct Fusion Drive (56.5 km/s, tagged "proposed"),
Long Passage (200 km/s, tagged "Titan design"). Ranges render as bars, single
design points as ticks. Labels collapse to Chemical / Electric / Nuclear thermal
/ Fusion below 600 px.

### 2.3 What-if scrubbing
- Pointer drag, tap, and arrow keys on the chart (`role="slider"`, labelled
  "What-if exhaust velocity") move a second marker. The current-configuration
  marker stays.
- The scrub holds the chart's stated conditions fixed: same Δv, same post-burn
  mass, same jet power. It does not mutate the form.
- A readout beside the chart (below it on mobile) shows, for the what-if point:
  exhaust velocity and Isp, propellant %, launch mass, thrust, engine time, each
  with the change from the current configuration ("−62 t", "÷ 4.1 thrust").
- The mass bar in the results panel shows a ghost outline of the what-if split
  while scrubbing.
- A button "Use this exhaust velocity" commits: sets mode to Mission, constraint
  to jet power, writes the exhaust value, runs `update()`.
- A matching `<input type="range">` (log-mapped) under the chart drives the same
  state for users who do not discover the drag.

### 2.4 No horizontal scroll
The chart redraws to its container width (ResizeObserver; recompute tick set:
1, 10, 100, 1,000 below 500 px). Remove `.chart-scroll` overflow. Both panels,
both markers and all axis labels are visible at 320 px.

## Phase 3: phone layout (≤ 760 px)

- **Sticky result strip.** While the form is on screen and `#results` is not,
  a strip pinned to the bottom of the `.tool` section shows the primary value,
  propellant %, and a thin mass bar. Tapping it scrolls to `#results`. Use
  `position: sticky` inside the section and an IntersectionObserver; solid
  background, no blur.
- **Comparison table** becomes stacked rows: mechanism as the row heading, Isp
  and thrust on one line, the decision sentence below. No horizontal scroll.
- **Touch targets** ≥ 44 px high: TOC links (currently 15 px), preset buttons
  (38 px), action buttons (40 px).
- **Engine constraint** select takes a full row so its value is not truncated.
- Quick-reference grid: one column below 420 px so formulas do not wrap mid-term.
- Target page length at 375 px: ≤ 12 screens (currently 16).

## Phase 4: comprehension and structure

### 4.1 Field hints
One short line under each label that needs it, always visible, ≤ 12 words:
- Post-burn mass: "Everything still aboard after the burn: structure, payload, reserves."
- Engine constraint: "Fix the push (thrust) or fix the power in the exhaust."
- Directed jet power: "Kinetic power in the exhaust, before engine losses."
- Required ideal delta-v: "Total velocity change the mission needs."

### 4.2 Delta-v anchors
In Mission mode, a chip row under the delta-v field fills in common budgets and
names them, for example surface to low Earth orbit, low Earth orbit to trans-lunar
injection, low Earth orbit to Mars transfer. Each value needs a primary source
added to the Sources list with its basis (ideal or including losses) in the chip
title. Omit any that cannot be verified. In Vehicle mode the result panel shows
the nearest anchor at or below the computed delta-v ("enough for ...") when one
applies.

### 4.3 Result hierarchy
Under the headline number and mass bar, three stats at a larger size:
propellant consumed, engine-on time, and whichever of thrust or jet power is
derived. The remaining seven stay in the two-column grid at the current size
under a "Details" label.

### 4.4 Section order
Calculator → quick reference → propulsion comparison → worked cases →
**Titan** → equations → gotchas → sources → related. Worked case C hands off
directly to the Titan section. Renumber the TOC and kickers.

### 4.5 Titan section
The ship illustration spans the full panel width with its four labels attached
to the parts they name (leader lines on desktop, the existing caption grid on
mobile). Text and the three links sit below it in two columns.

### 4.6 Comparison table thrust column
Add a small inline log-scale bar per row (1 μN to 100 kN) under the thrust text,
drawn from the same values, so ten orders of magnitude are visible at a glance.
"Design dependent" rows show no bar.

### 4.7 Type floor
Anything that is a sentence (field labels, hints, notes, captions, stat labels,
table cells) is at least 0.875 rem. 0.8 rem is reserved for uppercase kickers
and badges.

## Acceptance

1. `python scripts/check_rocket_equation.py --base <url> --render-og` passes with
   updated assertions: the caveat gate (1.7), no input over 7 significant digits
   after any preset or mode change (1.2), no `E` exponent in visible text (1.4),
   no `ꜰ` in the document (1.5), `scrollWidth ≤ clientWidth` for the chart and
   comparison containers at 360 and 375 px (2.4, Phase 3), every visible
   interactive element ≥ 44 px high at 375 px (Phase 3).
2. Scrub test: with the chemical preset, moving the what-if marker to 30 km/s
   shows a propellant share matching `1 − e^(−Δv/30000)` to 4 digits and leaves
   every form input unchanged; "Use this exhaust velocity" then makes
   `getResult().ve === 30000`.
3. Worked case C: the formula line evaluates to the displayed answer.
4. Screenshots at 1440 and 375 px in both themes reviewed for the headline
   number, chart panels and sticky strip.
5. OG image re-rendered; the transient CSS in the check script is updated for
   the new chart markup.
6. `docs/titan-crosspromo.md` § Basis and scope: replace the dual-axis plot
   description with the two-panel and what-if description.
7. Repo gates in `docs/content.md` pass. No deploy without David's go-ahead.

## Implementation notes

Build in phase order; each phase is one commit and leaves the page shippable.
Phase 1 is mechanical and suits a Sonnet sub-agent. Phases 2 and 3 are the
design-heavy part and suit Opus with the `frontend-design` skill. Phase 4.2
needs source research before any markup.
