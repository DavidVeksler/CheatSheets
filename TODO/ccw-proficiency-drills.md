# Spec: CCW Proficiency — Drills, Par Times, and Scored Standards

**Target file:** `ccw-proficiency-drills.html`
**Status:** spec, not built. Delete this file when the page ships.
**Read first:** `AGENTS.md`, then `TODO/README.md` (Rules 0–6), then this spec.

---

## Why this topic

Searchers looking for concealed-carry information get buried in two things: **state law**
(thousands of pages, well covered, and a legal-liability minefield) and **gear reviews**
(affiliate content). The thing almost nobody publishes in usable form is the *practical
measurement layer*: **what a carrier should be able to do, expressed as a number, and the
exact courses of fire that produce that number.**

The material exists but is scattered — one drill per blog post, a PDF per instructor, a
forum thread per standard, each with its own target, scoring system, and gear assumptions
that make the numbers non-comparable. A shooter standing at a range bay with 100 rounds and
45 minutes has no single sheet that says: *shoot this cold, score it this way, here's what
your number means, here's what to fix.*

That is exactly the niche-utility shape (README Rule 0): a page kept open on a phone at the
range while performing a task, re-opened every practice session, printed for the ammo can.
An AI chat answer can describe the Bill Drill; it can't be the scorecard you're filling in
between strings with ear pro on.

**Explicit non-goal: legal content.** Permit process, reciprocity, use-of-force law, and
carry restrictions are covered elsewhere and are deliberately out of scope. The page carries
exactly one legal block, which points readers to
<https://coloradofirearmswatch.org/ccw/> for the Colorado permit process as the worked
example of "your state has a process, here is what one looks like," plus one line telling
readers to verify their own state. Do not expand this into a fifty-state table. (README
Rule 4: link the gap in one line and move on.)

---

## Targeting (Tier 1)

**Primary query:** `concealed carry drills` / `ccw drills` (research mode, repeat-use).

**Secondary queries** (all confirmed present in Google autocomplete, Sept 2026):
- `pistol drills pdf` · `pistol drills for the range` · `dry fire drills pistol`
- `good draw time from concealment` / `average draw time from concealment` / `good ccw draw time`
- `bill drill time standards` · `el presidente drill time standard` · `5x5 drill` · `mozambique drill time`
- `handgun qualification course` (informational half of the query, not the license half)
- `concealed carry drills at home` (the dry-fire section serves this)

**Mode:** research, not crisis — but with a strong *return-visit* profile. The page is
bookmarked and re-opened, not read once. That changes implementation priorities: the drill
library and scorecard matter more than narrative; the page must work with a cold cache and
no signal.

**Draft `<title>`:** `Concealed Carry Drills and Par Times: Scored Standards` (52 chars)
**Draft H1:** `CCW proficiency: the drills, the par times, the scorecard`
**Draft meta description** (177 chars):
`Timed handgun drills for concealed carriers: exact courses of fire, par times, targets and scoring for the FBI qual, Bill Drill, Wizard, FAST, Dot Torture and more, plus a practice program.`

Verify final title ≤65 chars and description 150–200 against `scripts/seo_check.py` before
commit. If the title changes, keep "drills" and "par times" in it — those are the query.

**Reader outcome ("definition of working"):** after this page, a carrier can walk into a
range bay, shoot a named cold assessment correctly (right target, right distance, right
start position, right par), score it by the drill's own rules, place that score on a
skill ladder, and leave with a specific next drill. Behavioral test: *they can run the
Wizard and tell you whether they passed and why not.*

**Success metric:** organic entries on the `concealed carry drills` / `pistol drills`
family; return-direct and print traffic (the range-card and log blocks); popularity-score
lift in the Firearms cluster. Secondary: the standards-ladder graphic being screenshotted.

**Index category:** `Firearms & Military` (existing label in `category-map.php`, alongside
`handgun-calibers.html`, `modern-firearms.html`, `operator-loadouts.html`).

**Geographic scope:** US-wide. Drills, standards and instructors named are US. No state
law content beyond the single pointer block described above. Non-US readers get everything
except the permit pointer, which is labeled as US/Colorado.

**Reading conditions:** phone held one-handed in an outdoor bay in direct sun, hearing
protection on, hands dirty, timer in the other hand, frequently **no cell signal**. Derived
requirements: no runtime network dependency of any kind (no CDN, no fonts, no analytics
call the page waits on); high-contrast light theme that survives sunlight *and* a dark
theme for indoor bays; tap targets ≥44 px; the drill cards must be readable at arm's length
(≥16 px body, ≥18 px in the drill cards); a print stylesheet that emits a **two-page range
card** (drill library + blank score log) on US Letter portrait.

**Volatile-facts register:** overall rating **SLOW-DRIFT**.

| Fact class | Rots how fast | Re-verification |
|---|---|---|
| FBI qualification course version (Jan 2019 is current) | Years | FBI/agency publications; note the 2013 predecessor exists |
| IDPA classifier tables, division names, rulebook revision | ~1–2 years | idpa.com current rulebook |
| USPSA classification percentages / division list | ~1–2 years | uspsa.org rules |
| Gabe White pin times, Rangemaster test versions | Rare but real | Instructor's own current page |
| Ammunition cost per round, range fees, gear prices | **Fast — 6–12 months** | Quote as ranges with an inline "as of Sep 2026" tag; prefer $/100 rounds |
| Dry-fire tool product landscape (laser cartridges, SIRT, Mantis) | ~1 year | Manufacturer pages; keep to categories + capability, not model numbers |
| Incident-statistics citations (Givens dataset, NRA Armed Citizen, LEOKA) | Slow; datasets grow | Cite dataset + year explicitly |
| Drill provenance and course of fire | Stable | KR Training compendium + originator page |

---

## Content approach

### Global rules for this page

- **Every drill entry is a complete, runnable specification.** Distance, round count,
  target, start position (including whether the gun is concealed), string-by-string course
  of fire, par time(s), scoring method, and pass standard. A drill row that omits the start
  position or the target is a defect — those are exactly what makes published times
  non-comparable.
- **Attribute every drill to its originator by name** and link the originator's page or the
  best canonical write-up. Several of these are living people whose standards are their
  professional work.
- **Copyright discipline.** Courses of fire are procedures, not prose — express them in this
  page's own tabular structure and wording. Do **not** copy paragraphs from
  KR Training's compendium, instructor sites, or magazine articles, and do **not** reproduce
  copyrighted targets (Dot Torture's target, B-8 repair centers, IDPA/USPSA targets). Link
  to where the reader downloads them.
- **Gear normalization is a first-class fact.** Any time quoted must say whether it assumes
  concealment, open carry, or duty gear, because the published bonuses/penalties (e.g. Gabe
  White's 0.25 s concealment allowance, FAST's 0.5 s retention-holster adjustment) are the
  difference between a pass and a fail.
- **No brand shopping.** Gear sections describe *attributes that change measured
  performance* (holster rigidity, belt stiffness, sight type) with named examples only where
  a category is meaningless without one. No affiliate framing, no "best X" lists.
- **One prominent safety block, then get on with it.** Dry-fire safety protocol is a real
  section because it is procedural and people are injured by getting it wrong; it is not
  repeated as boilerplate elsewhere.

### Section outline (three depths per AGENTS.md coverage contract)

**1. Cold-start card (Quick Reference, above the fold)**
The five-minute version: five benchmark numbers a carrier can check today, each linking to
its full drill entry. Suggested: draw to first hit at 5 yd from concealment; the Wizard;
5 Yard Roundup; Bill Drill; Dot Torture. Each shown as `standard → what it proves`. This
block is the "screenshot this" artifact candidate #2.

**2. What the standards are calibrated against**
Why 3–7 yards, ~3 rounds, ~3 seconds dominates every defensive standard. Ground it in named
datasets with their limits stated honestly: Tom Givens' student-involved-incident dataset
(distances clustered ~3–5 yd, low round counts, very short durations — cite the dataset and
its selection bias: these are trained students, not a random sample), NRA Armed Citizen
compilations, FBI LEOKA (law-enforcement, different population — say so). Then the
inference: standards are built for a short, close, fast problem, which is why a 25-yard
bullseye score does not predict CCW competence, and why par time is scored at all.
*Anti-goal: no "statistics prove you need X" gear argument.*

**3. The measurement toolkit** (table, 10–14 rows)
Targets and scoring systems, because a "time" means nothing without them.
Rows: B-8 repair center (ring diameters), IDPA target (-0/-1/-3 zones, 4″ head circle),
USPSA/IPSC metric (A/C/D), QIT-99 / RFTS-Q bottle, IALEFI-Q, 3×5 index card, 8″ circle,
FAST target, paper plate as the field-expedient standard. For each: dimensions, what it
measures, which drills use it, where to get it.
Then scoring systems as their own sub-table: **par-time pass/fail**, **Vickers count**
(time + 0.5 s per point down), **Comstock / hit factor** (points ÷ time), **points-down
with time added**, **ring scoring out of 100**, **"par factor"** as a cross-drill
difficulty comparator. Give one worked scoring example end-to-end with real numbers — a
real run, real points down, a real final score. (README Rule 3: arrive at an actual answer.)
Also: shot timer basics — random start delay, par beep, why the timer's first beep is the
only honest start signal, what "split" and "draw" mean, and the phone-app caveat (indoor
bay echo and gunfire above the mic's dynamic range cause missed/false shot detection; par
mode is reliable, shot detection is not).

**4. The drill library** — the page's core. **28–36 drills.**
Structure as grouped cards or a grouped dense table (see Design). Groups and mandatory
members (add others as research supports; every one below is documented in the sources):

- *Cold assessments / minimum competency:* Hackathorn's **The Wizard**; **5 Yard Roundup**
  (Justin Dyal); Rangemaster **Baseline Skills Assessment**; **Ed Head's CHL practice drill**;
  KR Training **Three Seconds or Less**; Claude Werner's **Basic Self Defense Handgun Skills Test**.
- *Accuracy under a clock:* **Dot Torture** (Dave Blinder); **The Test** (Hackathorn/Vickers,
  both scoring variants); **Super Test** and Advanced/Langdon-timed variants (Dobbs & Bolke);
  **5×5 / 5^5** (Gila Hayes, extended by Claude Werner); **The 99 Drill**.
- *Speed and recoil control:* **Bill Drill** (Bill Wilson) with the competing published
  standards stated as competing (Wilson's, Enos's, KR Training's — they differ, say so);
  **El Presidente** (Cooper) plus the modern hit-factor benchmark; **Failure Drill /
  Mozambique**; **Gabe White Technical Skills Test** with the Turbo/Light/Dark pin times.
- *Manipulation:* **F.A.S.T.** (Todd Louis Green) with its rating tiers and gear
  adjustments; reload standards (slide-lock vs retention); **malfunction clearance** drills
  (ball-and-dummy induced, Type 1/2/3 with what each actually is).
- *One-handed and injured shooter:* strong-hand-only and weak-hand-only standards;
  one-handed manipulation (belt/heel racking); **Handgun Disability Course**.
- *Movement, multiple targets, decision:* stepping off the X on the draw; target
  transitions; shoot/no-shoot with a discriminator; **Farnam drill**; **3M test**.
- *Qualifications as benchmarks:* **FBI Pistol Qualification (Jan 2019)** — full 50-round
  course of fire with per-string par times, and note it replaced the 2013 60-round version;
  **Rangemaster Handgun Core Skills Test** (Comstock); a representative **state CCW
  qualification** shown as a *floor*, with the explicit point that passing a state qual is
  the legal minimum and not a proficiency standard. **BATFE handgun qualification** optional.
- *Carry-specific hardware:* **snub / 5-shot revolver** standards (Snub Super Test, Snub
  Assessment Drill); pocket-carry start position; **Spencer Keepers' test**; back-up-gun
  standards.
- *Low light:* Three Seconds or Less low-light variant; handheld vs weapon-light technique
  and what each costs in time.

**Columns for each drill:** name · originator · distance · rounds · target · start position
(concealed?) · course of fire (string by string) · par / standard · scoring · what it
measures · gear caveat · source link.

**5. The standards ladder — SIGNATURE ELEMENT** (10–14 benchmark rows × 4–5 tiers)
The visual answer to "what's a good draw time?" A banded chart mapping named benchmarks to
skill tiers. Tiers (name them plainly, no invented belt system): *state-qual floor →
competent carrier → skilled → high performer → competition-class*. Rows: draw to first hit
at 7 yd (concealed); draw to first hit at 5 yd; splits at 7 yd on an A-zone; Bill Drill
total; FAST total (with its published rating tiers); the Wizard (pass/fail, so shown as a
gate); 5 Yard Roundup score; Dot Torture (distance achieved clean); Super Test percentage;
reload (slide-lock) time; IDPA 5×5 classifier total mapped to IDPA classifications; USPSA
classification cross-reference.
Every cell must be a **sourced published standard, not an invented number.** Where no
published tier exists, leave the cell empty rather than inventing one — the empty cells are
themselves informative. State the gear assumption for the whole chart in the caption
(concealment, carry gear, no competition rig).
**This chart is the og:image subject.**

**6. Diagnostics — reading your own target and timer** (12–16 rows)
- Explicitly debunk the **"shooting correction wheel"** (the pie chart of "heeling /
  jerking / thumbing" pasted in every range) — it is not diagnostic for a shooter whose
  errors are unknown, it produces confident wrong answers, and instructors have criticized
  it for decades. Say this plainly with a citation, because the page will be read by people
  who have that chart on their wall.
- What actually diagnoses: **ball-and-dummy** (dummy round randomly loaded — reveals
  anticipation, and it is the only reliable self-test), **wall drill**, group size at 3 yd
  vs 25 yd slow fire, one-handed vs two-handed group comparison, the timer's own numbers
  (slow draw vs slow first shot vs wide splits each point at a different cause), grip
  pressure test, target-focus vs sight-focus test with a red dot.
- Map: *symptom → most likely cause → the test that confirms it → the drill that fixes it.*
  This map is a table and is one of the highest-value blocks on the page.

**7. The practice program** (8–12 rows + a worked annual budget)
Periodized and honest about cost. Dry fire 10–15 min, 3–4×/week (published minimums
converge here) with per-session rep budgets and the diminishing-returns point; live fire
1–2×/month with a round-count allocation table (how many of 100 rounds go to what); a
**quarterly cold test** (shoot a named assessment first, cold, no warm-up, and log it —
this is the single highest-signal practice habit on the page); annual formal instruction.
Include a real annual budget arithmetic: rounds/year × $/round (dated) + range fees +
one class + targets = a real dollar figure, plus a low-budget variant that is mostly dry
fire. Arrive at actual numbers.

**8. Dry-fire safety protocol** (procedural block, 8–10 rules)
Separate room; **no live ammunition in the room, period**; magazines and carry ammo
physically elsewhere; safe backstop direction (interior wall is not a backstop — name what
is); verbal or written session-end ritual and the "one more rep after you reload" failure
mode that causes most negligent discharges in dry practice; visual + physical chamber check
sequence; reholstering slowly with eyes on the holster; nothing in the holster (garment,
drawcord) — this is the AIWB injury mechanism; blue gun / barrel block / laser cartridge as
risk reduction. Then tools: laser cartridge, SIRT-type pistol, dedicated shot timer, phone
par-timer app, tracking systems — what each measures, what it can't, rough cost band.

**9. Gear that changes the number** (12–18 rows)
Only through the lens of measured performance. Holster (rigidity, mouth stays open,
retention level, ride height/cant, AIWB vs strong-side and the draw-time difference each
produces); belt stiffness as the most under-rated variable; concealment garment type and
the clearing technique each demands; sights — irons vs red dot with the honest tradeoffs
(dot presentation learning curve and the "finding the dot" failure, astigmatism, battery
life, lens obstruction in rain, and the measured advantage at distance); trigger; grip
texture; magazines and how many; ammunition — carry load vs practice load and why the
**last drill of the session should be fired with carry ammo** (point of impact shift,
recoil difference, feed reliability confirmation).

**10. Proficiency that isn't marksmanship** (10–14 entries)
The part of "CCW proficiency" that gun-drill content skips:
carry-position consistency (same place, every day — draw stroke is trained to one
position); reholstering discipline; garment management and printing; retention and
entangled-distance skills, and why standing-square-at-7-yards drills don't cover the most
common civilian distance problem; verbal commands and the pre-draw decision; movement to
cover and backdrop awareness; the legal-aftermath actions (one line, deferred);
**post-shooting medical**: tourniquet, pressure dressing, chest seal, and the honest point
that a carrier is far more likely to use medical gear than a gun — carrying a TQ without
training on it is gear cosplay. Rough time-to-competence for each. Link the medical gap in
one line rather than writing a second cheatsheet inside this one.

**11. Common mistakes and anti-patterns** (12–15 entries, MANDATORY per AGENTS.md)
Candidates: never drawing from concealment; only shooting warm; scoring hits but not time
(or time but not hits); practicing exclusively at 3 yd; the "range rig" that isn't the carry
rig; buying gear instead of reps; treating the state qualification as a proficiency
standard; no written log, so no trend; comparing your time to a YouTube time shot with a
competition holster; never practicing one-handed; never practicing a reload under a clock;
"tactical" theater drills that are unmeasurable; dry-fire without a par timer (all speed
work, no calibration); and the reholstering rush.

**12. The log** (schema + printable blank)
Columns: date · cold or warm · drill · gun/gear config · raw time(s) · points down · final
score · tier · one-line note on the limiting factor. Explain how to compute the trend and
what a plateau means. This block prints as page 2 of the range card.

**13. Legal, training and jurisdiction — one block only**
One short block: this page is about skill, not law; permit requirements, reciprocity, and
use-of-force rules are state-specific and change; verify for your state. Point to
<https://coloradofirearmswatch.org/ccw/> as the model of what a state's permit process
actually involves (Colorado CHP: training hours with live fire, sheriff application, fee,
decision window, renewal) — descriptive, linked, one paragraph, no numbers we haven't
verified against that page at build time. Also recommend formal instruction as the thing
this page cannot substitute for.

**14. Sources** (20–30 entries)
Named, linked, with what each was used for.

---

## Research sources (verify every number against these)

Primary/near-primary:
- KR Training / John Daub, *Drills, Qualifications, Standards, & Tests* (free PDF compendium,
  rev. 2022-05) — <https://krtraining.com/Drills-Qualifications-Standards-and-Tests-2022-05.pdf>
  — the best single cross-check for courses of fire and provenance. **Reference and cite;
  do not copy its prose.**
- pistol-training.com — F.A.S.T. (<https://pistol-training.com/drills/the-fast>) and
  Dot Torture (<https://pistol-training.com/shooting-drills/dot-torture/>).
- Gabe White Training, Technical Skills Tests — <https://www.gabewhitetraining.com/technical-skills-tests/>
  (pin times, gear adjustments, 4-of-8 attempts rule).
- Rangemaster (Tom Givens) — core skills test, baseline assessment, newsletters
  (<https://www.rangemaster.com/>).
- Active Response Training (Greg Ellifritz) — Wizard drill and 5×5 write-ups.
- Lucky Gunner Lounge "Start Shooting Better" series — FBI qual, 5 Yard Roundup, 5×5, with
  demonstrated times.
- IDPA current rulebook (classifier tables, target zones) — <https://www.idpa.com>.
- USPSA rules and classification system — <https://uspsa.org>.
- FBI / agency publications for the Jan 2019 qualification course of fire; corroborate the
  string list across at least two independent write-ups before publishing it.
- SWAT Magazine / Justin Dyal for 5 Yard Roundup; Shooting Illustrated for Ed Head's drill.
- Ben Stoeger / published dry-fire programs for session structure and rep budgets.
- Manufacturer/vendor spec pages for target dimensions (B-8 ring diameters, IDPA/USPSA
  zone sizes).

For the "shooting correction wheel" debunk, cite an instructor-side critique rather than a
forum post.

**Verification rule (README Rule 1):** every par time, distance, round count, ring diameter,
scoring constant, tier threshold and dollar figure in this spec is an **anchor from the spec
author's reading, not a verified fact.** Confirm each against the originator's page or the
compendium above. Where two credible sources disagree (the Bill Drill par time genuinely
does), publish both, attributed — the disagreement is useful content. Where you cannot
verify, cut the entry.

---

## Visual design

**Aesthetic: the range scorecard + shot timer.** Two materials in one page:

1. **Scorecard paper** — the light surface: an off-white card stock with a faint grid, thin
   rules, and tabular monospaced numerals. This is what carries the drill library and the
   log. It should look like something you'd clip to a board and write on.
2. **Timer LED** — the accent: a seven-segment-flavored numeric display treatment (dark
   panel, amber/red glow) for par times, benchmark numbers, and the live timer. Numbers on
   this page are the content, so they get the loudest typographic treatment.

Palette direction (derive real hex values before writing CSS): card stock
`#f5f2ea`-ish light / bay-charcoal `#16181c`-ish dark; timer amber `#ffb02e`; a single
safety-red `#c8342b` for fail states, safety rules and misses; a muted green for pass. Honor
`prefers-color-scheme` with `light-dark()`, and offer an explicit `[data-theme]` toggle,
because the outdoor-sun and indoor-bay cases genuinely differ.

Typography: condensed sans for headings, tabular-numeral monospace for every time/score.
No web fonts (offline requirement) — system stacks only.

**Signature element (build first and best): the standards ladder.** A CSS-grid / inline-SVG
banded chart, benchmarks on the y-axis, time or score on the x-axis, tier bands as colored
regions, with the reader's own result marker-able. Must collapse to a readable
single-column stacked form at 375 px — test that specifically. It is also the og:image.

**Interactivity budget: ONE component — the par timer / scorecard.**
- Random start delay (1.5–4 s), start beep, one or more par beeps, using WebAudio generated
  tones (no audio files, no network).
- A drill picker that loads the selected drill's strings and par times into the timer.
- Optional score entry (points down / hits) that computes the drill's own score and places
  it on the ladder.
- Session log persisted with `localStorage`, feature-detected, with a graceful "not saved"
  state; an export/copy-to-clipboard so the log survives a cleared browser.
- **Must degrade completely without JS:** every drill's parameters are in the static HTML;
  the timer is progressive enhancement only. Never hide content behind the widget.
- Volume/beep must be usable through hearing protection — offer a visual flash cue as well,
  and respect `prefers-reduced-motion` for the flash.
Do not add a second interactive toy (no ballistics calculator, no target generator).

Print: `@page` US Letter portrait; the print stylesheet emits **page 1 = drill library
range card**, **page 2 = blank score log**, everything else suppressed. The timer widget,
nav and related links do not print.

---

## Cross-link map

Outbound from this page:
- `handgun-calibers.html` — terminal performance and ammo selection.
- `modern-firearms.html` — platform reference.
- `operator-loadouts.html` — gear context.
- `prepper-gear-audit.html` and `vehicle-emergency-kit.html` — the medical/preparedness
  adjacency (the TQ point in §10).
- External: <https://coloradofirearmswatch.org/ccw/> (permit process, §13). Use a
  descriptive anchor, not "click here."

Reciprocal links to add in the same commit:
- `handgun-calibers.html` → this page ("what to do with the gun once you've chosen it").
- `modern-firearms.html` → this page.

Also: add the file to `category-map.php` under `Firearms & Military`, and let
`.githooks/pre-commit` regenerate `catalog.json`. No `paths.json` entry required.

---

## Density targets

| Block | Target |
|---|---|
| Drill library | 28–36 drills, each fully specified |
| Standards ladder | 10–14 benchmark rows × 4–5 tiers |
| Targets & scoring systems | 10–14 rows + 1 worked scoring example |
| Diagnostics map | 12–16 symptom→cause→test→fix rows |
| Practice program | 8–12 rows + a worked annual budget in dollars |
| Dry-fire safety | 8–10 rules + 5–8 tool rows |
| Gear that changes the number | 12–18 rows |
| Non-marksmanship proficiency | 10–14 entries |
| Common mistakes | 12–15 entries |
| Sources | 20–30 |

---

## Definition of done (this page, in addition to README Rule 3)

- Every drill row states its start position and target; none is missing a par or an explicit
  "no time limit."
- Every ladder cell is sourced or empty; no invented tier numbers.
- The worked scoring example and the annual budget both end in a real number.
- The par timer works offline, degrades without JS, and its beep is audible through ear pro
  (with a visual cue).
- Print output is exactly two pages and is legible in a range bag.
- 375 px render of the standards ladder verified.
- SEO gate, `php -l`, link/asset check and catalog build all pass; og:image rendered to
  `images/ccw-proficiency-drills.png`.
