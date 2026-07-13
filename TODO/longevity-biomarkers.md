# Spec: longevity-biomarkers.html

**Target file:** `longevity-biomarkers.html`
**Cluster:** Longevity (spoke page; pillar is `longevity-what-actually-works.html`, sibling spoke is
`longevity-supplements-evidence.html`).

## Why this topic

Millions of people now own the raw data — an Apple Watch VO2 max estimate, a resting heart rate
trend, a cholesterol panel, a $25 grip dynamometer, a "biological age" test they paid for — and have
no honest reference for what any of it *predicts*. The pages that rank for `VO2 max longevity`,
`grip strength mortality`, `biological age test`, and `biomarkers of aging` are mostly selling the
test, the wearable, or the clinic that "optimizes" the number for you. So the numbers with the
strongest mortality evidence and the ones that are pure marketing get presented with equal
confidence, and the reader can't tell that VO2 max and grip strength out-predict most of what a $500
longevity panel measures.

**David sells no tests, no wearables, no clinic membership, no coaching** (excluded from the Phase-2
affiliate list). That makes this the honest reference the funnel pages can't be: for each biomarker,
*how strongly it actually predicts mortality*, *how to measure it (ideally free/at-home)*, *your
target band by age and sex*, and *whether it's worth paying for at all*. It's the measurement
companion to the pillar's "what to do" and the supplements page's "what to take."

This is the **most niche-utility page of the three** — the clearest pass of the "keep it open while
doing a task an AI answer can't replace" test. The reader literally holds their wearable or lab
report next to it and reads their own number against the evidence-based bands. The value is the
dense, exact, side-by-side reference (hazard ratio per unit, target by age/sex, how to measure) —
not a narrative. An interactive "enter your numbers" scorecard makes it a tool, not an article.

## Targeting

- **Primary query:** `VO2 max longevity` / `biomarkers that predict lifespan`
- **Secondary queries:**
  - `grip strength mortality` / `grip strength longevity`
  - `biological age test` / `epigenetic clock accuracy`
  - `resting heart rate longevity` / `VO2 max by age chart`
  - `gait speed mortality` / `walking speed longevity`
  - `what biomarkers should I track for longevity` / `longevity biomarkers at home`
  - `ApoB vs LDL` (routes toward blood-tests page for interpretation)
- **Search mode:** research mode, high **self-quantification intent** — the reader already has a
  number in hand and wants to know if it's good. Lead H2s with the metric name + "what it predicts"
  and "your target by age," matching real queries ("What's a good VO2 max for my age?",
  "Does grip strength really predict mortality?").
- **Draft title (≤60 char):** `Longevity Biomarkers: The Numbers That Predict Lifespan`
- **Draft H1:** `The Numbers That Predict How Long You'll Live`
  (dek: *VO2 max, grip strength, gait speed, resting heart rate and more — how strongly each predicts
  mortality, your target by age, and how to measure it free. No test to sell you.*)
- **Meta description (150–200):** `The biomarkers that actually predict how long you'll live —
  VO2 max, grip strength, gait speed, resting heart rate, waist-to-height, ApoB, biological-age
  clocks — ranked by evidence, with target bands by age and sex and how to measure each at home.`
- **Reader outcome:** After this page a reader can take their own measurable numbers (VO2 max, grip,
  resting HR, waist-to-height, gait speed, and the key labs), place each in an evidence-based band
  for their age and sex, identify which of their numbers is the worst relative to target, and know
  which "longevity tests" are worth paying for and which aren't.
- **Success metric:** organic entries on `VO2 max longevity` / `grip strength mortality` (high-volume,
  clear intent); return/bookmark traffic (people re-check as their numbers change — the interactive
  scorecard invests in this); shares of the scorecard. Goal-3 (niche-utility case study) + goal-1
  (study). **Note (2026-07-12 GSC):** greenfield — no current longevity footprint; demand-creation
  bet judged on the niche-utility + brand goals, not on existing rankings.
- **Index category:** `Health & Fitness`.
- **Jurisdiction/scope:** universal biology. Target bands are age- and sex-specific and
  population-derived — cite the reference population per metric; note where norms differ by sex.
  Decision-support only, not diagnosis (one prominent disclaimer per README Rule 4).

## Volatile-facts register (staleness profile)

Overall rating: **SLOW-DRIFT.** The mortality associations are stable; normative bands and the
biological-age-clock landscape drift.

| Fact class | Rating | Re-verify against |
|---|---|---|
| VO2 max ↔ all-cause mortality (Cleveland Clinic, n≈122k) | STABLE | JAMA Netw Open 2018 (Mandsager) |
| Grip strength ↔ mortality (~16% ↑ per 5kg drop) | STABLE | PURE study (Leong 2015, *Lancet*); meta-analyses |
| Gait speed ↔ survival (≥1.0 m/s threshold) | STABLE | Studenski 2011 *JAMA* pooled analysis |
| Resting HR / HRV ↔ mortality | STABLE | large cohort meta-analyses |
| VO2 max / grip normative bands by age & sex | SLOW-DRIFT | ACSM / Cooper Institute norms; national reference data |
| ApoB vs LDL as the better risk marker | SLOW-DRIFT | current lipidology consensus; defer interpretation to blood-tests page |
| Biological-age / epigenetic clocks (DunedinPACE etc.) predictive value | VOLATILE | 2025 BASE-II biomarker comparison (medRxiv) + newer validations |

Every band and hazard ratio is an **anchor, not a fact.** Verify each normative band against a named
reference (ACSM/Cooper/PURE/national data) at build; if a band can't be sourced, present the metric
qualitatively (direction of risk) rather than shipping an unverified cutoff.

## Cross-link map

- **Inbound:** from the pillar's VO2/fitness rows and "measure what matters" section; from the
  supplements page where a marker tempts a supplement.
- **Outbound:** to `blood-tests-cbc-cmp-lipids-a1c-thyroid.html` for interpreting the *lab* markers
  (lipids, A1c, ApoB — that page owns "is my result normal?"; this page owns "what does it predict
  and what's my target"); to `strength-training.html` (raise grip/strength), `running.html` /
  `cycling.html` (raise VO2 max), `sleep-optimization.html` (lower resting HR / raise HRV);
  to the pillar for "now what do I do about it."
- **Reciprocal:** add a link from `blood-tests-…html` ("for what these numbers predict about
  longevity, see…") and from `running.html`/`cycling.html` (VO2 max payoff).

## Content approach

### Quick-reference block (top): the Biomarker Scorecard
The signature artifact + the one interactive element. A table/grid of biomarkers, each row: the
metric, how strongly it predicts mortality (an evidence-strength chip), your **target band**, and an
input where the reader types their own number and the row lights green/amber/red against their
age/sex band. This is the "cheat-within-the-cheat" and the reason to keep the page open.

Core rows (target **12–16 biomarkers**):
- **VO2 max** — strongest single predictor; band by age/sex; measure via watch estimate, Cooper
  12-min run, or lab. (Every 1 MET ≈ 3.5 ml/kg/min ↑ ≈ 10–15% ↓ mortality — verify.)
- **Grip strength** — dynamometer (<$30); ~16% ↑ mortality per 5 kg drop (PURE); band by age/sex.
- **Gait / walking speed** — ≥1.0 m/s = better-than-expected survival (Studenski); measure with a
  tape + stopwatch.
- **Resting heart rate** — wearable; higher RHR ↔ higher mortality; target band.
- **HRV** — wearable; trend, not a hard cutoff; caveats.
- **Waist-to-height ratio** — tape measure; <0.5 target; out-predicts BMI for visceral risk.
- **Blood pressure** — cuff; targets; → NNT/blood-tests for treatment.
- **ApoB (or non-HDL)** — blood; the better lipid risk marker; → blood-tests page to interpret.
- **HbA1c / fasting glucose** — blood; metabolic aging; → blood-tests page.
- **hs-CRP** — inflammation marker; caveats.
- **Number of push-ups / sit-to-stand** — free functional proxies with cohort data (e.g., push-up
  capacity ↔ CV events; sit-to-stand ↔ mortality).
- **Biological-age / epigenetic clocks (DunedinPACE, etc.)** — the "should you pay for this?" row:
  what they measure, current predictive value, why the pace-of-aging clocks beat the first-gen ones,
  and the honest verdict on the consumer tests.

### Fundamentals — "How to read a biomarker's mortality claim"
- Predictive (associated with dying sooner) vs modifiable vs causal — a marker can predict without
  being worth "optimizing" directly.
- Hazard ratio per unit; what "predicts mortality" means; regression to function.
- Reverse causation again (low grip because already sick).
- Free/functional measures vs paid panels — the honest-broker throughline.
- Define the evidence-strength chip scale used across the scorecard.

### Working knowledge — per-biomarker atomic entries
For **each** biomarker: precise mortality association + source/population, evidence-strength chip,
**how to measure it (prefer free/at-home)**, the target band by age & sex, one concrete example,
and "how to move it" → link to the relevant how-to page. Quantify every band (real numbers, dated).

### Edge & advanced
- Which numbers to prioritize if you can only track a few (VO2 max, grip, waist, BP, ApoB).
- Consumer wearable accuracy caveats (watch VO2 max estimate error; optical HR limits).
- The biological-age-clock market: what's validated vs what's a $300 novelty; test-retest noise.
- When a "bad" number is reverse causation vs a real target to chase.

### Common Mistakes / Anti-Patterns (required)
- Paying for exotic panels while never measuring the free giants (VO2 max, grip, waist).
- Optimizing a marker that's predictive but not modifiable/causal.
- Trusting a single wearable reading over a trend.
- Treating a consumer epigenetic-age result as a precise verdict.
- Chasing a lab number while ignoring the functional tests that out-predict it.

## Research sources (verify at build — do NOT recall)
- VO2 max & mortality: Mandsager et al., *JAMA Netw Open* 2018 (Cleveland Clinic, n≈122,007).
- Grip strength: Leong et al., PURE study, *The Lancet* 2015; grip-strength meta-analyses.
- Gait speed: Studenski et al., *JAMA* 2011 (pooled cohort).
- Push-up capacity: Yang et al., *JAMA Netw Open* 2019 (male firefighters, CV events).
- Sit-to-stand: Brito et al. (musculoskeletal fitness & mortality).
- Resting HR / HRV: cohort meta-analyses (e.g., Zhang et al. RHR & mortality).
- Waist-to-height: meta-analyses vs BMI for mortality/visceral fat.
- VO2 max & grip **normative bands**: ACSM Guidelines / Cooper Institute norms; national reference data.
- Biological-age clocks: BASE-II 14-biomarker comparison (medRxiv 2025); DunedinPACE validation papers.
- ApoB vs LDL: current lipidology consensus (defer numeric interpretation to blood-tests page).

## Visual design

- **Aesthetic:** "instrument panel / diagnostic dashboard," distinct from the pillar's peer-review
  desk and the supplements ledger. Dark charcoal base (echoing `actual-risk-dashboard.html`'s
  authority but with its own palette), gauge-style accents. Zone ramp: green `#16a34a` (in target) →
  amber `#d97706` (borderline) → red `#dc2626` (elevated risk), with cyan `#06b6d4` as the neutral
  UI accent. Tabular/monospace numerals for readings; humanist sans for labels. Honor
  `light-dark()` with a clean light variant.
- **Signature visual element — the interactive Biomarker Scorecard:** the reader enters their own
  numbers and each row's gauge fills into the green/amber/red band for their age & sex. This is BOTH
  the signature artifact and the single interactive element — build it first and best. Pure JS +
  `localStorage` (persist the reader's numbers, like the site's saved-progress pattern); feature-
  detect and fail soft; gate any animation behind `prefers-reduced-motion`. No framework, no chart lib.
- **Interactivity budget:** the scorecard is the one element. Do not add a second.
- **og:image (1200×630):** the Scorecard populated with an exemplar set of numbers, dark theme,
  gauges lit — the "screenshot this" artifact.
- **Mobile:** scorecard rows → single-column cards, each with its input + gauge; ≥44px tap targets;
  numeric inputs use `inputmode="decimal"`. Test the gauge and input at 375px specifically.
- **Print:** sane defaults; ensure bands read in greyscale (label the zone in words, not color only),
  and that the scorecard prints with the reader's entered values.

## Density / acceptance
- ≥12 biomarker entries + literacy layer + edge section = past the 20-entry floor with the sub-entries.
- Every band/hazard ratio dated + sourced inline; one prominent "not diagnosis" disclaimer; visible
  `Last verified`; real `dateModified`.
- `TechArticle` JSON-LD only; no FAQ/HowTo schema despite question-shaped H2s.
- Interactive scorecard works without breaking the page when JS is off (bands still visible as a
  static reference table).
- Self-containment test: a reader can score their own numbers and find their worst metric from this
  page alone.
