# Spec: longevity-supplements-evidence.html

**Target file:** `longevity-supplements-evidence.html`
**Cluster:** Longevity (spoke page; pillar is `longevity-what-actually-works.html`, sibling spoke is
`longevity-biomarkers.html`).

## Why this topic

"Longevity supplements" is where the money and the misinformation are most concentrated. Every page
that ranks for `NMN`, `does resveratrol work`, `rapamycin longevity`, or `best longevity supplements`
is published by someone who sells the pills, sells the test that "proves" you need them, or runs the
newsletter that sells the ads. The result is a market where a compound with three human RCTs and a
compound with one leaky mouse study get the same glossy "clinically studied" treatment.

**David sells no supplements and takes no affiliate commission** (this file is explicitly excluded
from the Phase-2 affiliate list). That is the entire value proposition: a single scored ledger that
grades every popular longevity compound by the *quality of its human evidence*, not by how well it
sells — and says "save your money" out loud when that's the honest answer. This is the supplements
analogue of `nnt-medical-interventions.html`: same "here is the real number, nobody is upselling
you" discipline, applied to the supplement aisle instead of the pharmacy.

This is a **lookup tool**, not an overview — the niche-utility shape the site now prioritizes: the
reader keeps it open while standing in a store or looking at an influencer's stack, checks the
compound, reads the grade and the one-line verdict, and moves on. It passes the "would you keep this
open while doing a task an AI answer can't replace?" test because the value is the *dense, graded,
side-by-side verdicts with exact evidence tiers* — a comparison table with specs, not a narrative.

## Targeting

- **Primary query:** `longevity supplements evidence` / `do longevity supplements work`
- **Secondary queries:**
  - `best longevity supplements` (they searched to buy; we reframe to evidence)
  - `NMN vs NR` / `does NMN work` / `NAD supplements evidence`
  - `does resveratrol actually work`
  - `rapamycin longevity` / `metformin longevity` (drugs-off-label section)
  - `creatine longevity` / `omega 3 longevity` (the *proven*, boring winners)
  - `longevity supplements that actually work`
- **Search mode:** research mode, with strong **buyer intent** — the reader is often mid-purchase.
  Lead the title/H1 with "ranked by evidence" so the honest-broker reframe is the hook. Question H2s
  matching the per-compound queries ("Does NMN actually work?", "Is rapamycin worth it?").
- **Draft title (≤60 char):** `Longevity Supplements Ranked by Evidence (Not Hype)`
- **Draft H1:** `Longevity Supplements & Drugs, Ranked by Evidence`
  (dek: *What has real human trial data, what's mouse-only hype, and what to skip — graded by
  someone with nothing to sell you.*)
- **Meta description (150–200):** `Every popular longevity supplement and off-label drug graded by
  the quality of its HUMAN evidence — creatine and omega-3 vs NMN, resveratrol, rapamycin, metformin,
  fisetin, spermidine. An honest evidence tier list from someone selling no supplements.`
- **Reader outcome:** After this page a reader can place any popular longevity compound into the
  correct evidence tier (Proven human RCT / Emerging human data / Mechanism-only or mouse-only /
  Debunked-or-harmful), state the realistic dose and the single strongest study for the proven ones,
  and walk out of a supplement store having bought only what the evidence supports (often: little).
- **Success metric:** organic entries on the high-volume compound queries (`NMN`, `resveratrol`,
  `rapamycin longevity`); shares of the tier-list artifact; it's the cluster's likeliest
  link-magnet because the honest tier list is contrarian to the funnel content. Goal-4 (advocacy) +
  goal-1 (study). **Note (2026-07-12 GSC):** the site has zero current longevity footprint — this is
  demand-creation, not striking-distance capture; judge on brand/advocacy/shares, not on rescuing an
  existing ranking.
- **Index category:** `Health & Fitness`.
- **Jurisdiction/scope:** universal; note that supplements are unregulated for purity in the US
  (FDA doesn't pre-approve) — a key honest-broker point. Off-label drugs (rapamycin, metformin)
  require a prescription; frame as "what the evidence says," never as dosing advice (README Rule 4:
  medical pages are decision-support only — no dosing, no "ask your doctor" padding beyond one
  prominent disclaimer).

## Volatile-facts register (staleness profile)

Overall rating: **VOLATILE** — this is the fastest-drifting page in the cluster; new trials and new
hype cycles land constantly. This is the page the weekly-freshness job should visit most.

| Fact class | Rating | Re-verify against |
|---|---|---|
| Which compounds have human RCT data (tier assignments) | VOLATILE | PubMed/Cochrane; ClinicalTrials.gov; ITP (Interventions Testing Program) results |
| Rapamycin/metformin off-label longevity trial status (e.g., TAME, PEARL) | VOLATILE | trial registries + published readouts |
| Creatine, omega-3, vitamin D, magnesium proven benefits | STABLE | Cochrane / large meta-analyses |
| Resveratrol SIRT1-assay-artifact debunk | STABLE | published 2005+ reanalyses |
| Supplement purity/label-accuracy problem | SLOW-DRIFT | independent testing (e.g., ConsumerLab / USP-verification landscape) |

Every dose and effect size is an **anchor, not a fact.** Verify per-compound at build; if a
compound's human evidence can't be verified, place it explicitly in the mechanism/mouse-only tier
rather than guessing an effect size.

## Cross-link map

- **Inbound:** from the pillar (`longevity-what-actually-works.html`) supplements row + "do
  supplements work?" myth; from `longevity-biomarkers.html` where a biomarker tempts a supplement fix.
- **Outbound:** back to pillar; to `nnt-medical-interventions.html` for the *prescription* drugs with
  hard outcome data (statins etc. — those live there, not here); to
  `blood-tests-cbc-cmp-lipids-a1c-thyroid.html` for "test before you supplement" (vitamin D, B12).
- **Reciprocal:** add one link from the pillar's supplements section (same cluster ships coherent).

## Content approach

### Quick-reference block (top): the Evidence Tier List
The signature artifact. Every compound on one screen, grouped into tiers with a color-coded grade
stamp. This is the "cheat-within-the-cheat." Tiers:

- **Tier 1 — Proven (human RCT, real benefit):** creatine, omega-3 (EPA/DHA), vitamin D
  (deficiency-correction only), magnesium, protein/fiber adequacy. The boring, cheap winners.
- **Tier 2 — Emerging (human data, endpoints early):** NMN / NR (NAD+ elevation confirmed,
  functional endpoints early), GlyNAC (glycine + NAC; 3 small RCTs), berberine (metabolic),
  taurine, glycine, urolithin A, fisetin (senolytic, cleanest human biomarker trial so far).
- **Tier 3 — Mechanism-only / mouse-only / unproven in humans:** resveratrol, spermidine,
  most senolytics, CoQ10 (outside statin-myopathy), collagen-for-longevity, NR-vs-NMN marketing
  claims beyond NAD+.
- **Tier 4 — Debunked, useless, or potentially harmful:** high-dose antioxidant stacks
  (β-carotene/vitamin E — ↑ mortality signals), most multivitamins for longevity in
  well-nourished people, "detox" products, mega-dose anything.
- **Off-label drugs (own row, prescription):** rapamycin (strong animal data, human longevity RCTs
  ongoing — PEARL etc.), metformin (TAME trial framing; the "does it blunt exercise gains?"
  caveat), acarbose. Decision-support framing only.

### Fundamentals — "How to grade a supplement claim"
- Human RCT vs cohort vs mechanism vs mouse — and why mouse lifespan ≠ human lifespan.
- Surrogate marker (NAD+ went up) vs outcome (you lived longer / functioned better).
- The regulation gap: US supplements aren't pre-approved for purity/potency; "the brand matters more
  than the molecule." Third-party testing (USP/NSF) as the only real signal.
- Absence of evidence vs evidence of absence; publication bias; industry-funded study caveat.
- Define the 4-tier grade scale used across the page.

### Working knowledge — per-compound atomic entries
For **each** compound (target **20–28 entries**): tier stamp, mechanism in one line, the **best
single human study / strongest evidence** (or "no human outcome data"), realistic dose *as reported
in trials* (not a recommendation), cost order-of-magnitude, known risks/interactions, and a
one-line **verdict** ("Proven and cheap — take it if deficient" / "Save your money" / "Interesting,
unproven — not worth the price yet" / "Avoid").

### Edge & advanced
- Stacks & interactions (e.g., NAC + nitrates; berberine + antidiabetics; antioxidants blunting
  exercise adaptation).
- The "influencer stack" teardown: why Sinclair's and other public stacks aren't evidence.
- When a supplement is genuinely correcting a deficiency (D, B12, iron, magnesium) — test first,
  link blood-tests page.

### Common Mistakes / Anti-Patterns (required)
- Buying the exotic Tier-2/3 compound while skipping the proven Tier-1 basics.
- Treating "clinically studied" on a label as "proven to extend life."
- Ignoring third-party purity testing.
- Stacking a dozen compounds with no idea which (if any) does anything.
- Supplementing a nutrient you're not deficient in.

## Research sources (verify at build — do NOT recall)
- Cochrane reviews: antioxidant supplements & mortality (Bjelakovic); vitamin D; omega-3.
- Creatine: recent human RCT/meta-analyses (muscle, cognition, safety).
- NAD+/NMN/NR: published human RCTs (NAD+ elevation) + ITP mouse results.
- GlyNAC: the Baylor RCT series (Sekhar et al.).
- Resveratrol: SIRT1 assay-artifact reanalyses; ITP null lifespan.
- Rapamycin/metformin: ITP (rapamycin lifespan in mice); TAME (metformin) design; PEARL (rapamycin)
  readout status; the metformin-blunts-exercise-adaptation trial.
- Fisetin/senolytics: Mayo Clinic senolytic human biomarker trials.
- Purity/label problem: independent testing landscape (ConsumerLab / USP-verified program facts).
- NIH Office of Dietary Supplements fact sheets for baseline dose/safety.

## Visual design

- **Aesthetic:** "apothecary ledger / lab report," deliberately distinct from the pillar's
  peer-review-desk and the biomarkers dashboard. Warm off-white "prescription pad" paper in light
  mode; deep ink-navy dark mode via `light-dark()`. A **tier color system** carries it: Tier 1
  `#15803d` green, Tier 2 `#2563eb` blue, Tier 3 `#d97706` amber, Tier 4 `#dc2626` red, Drugs
  `#7c3aed` violet. Monospace for dose/cost figures (ledger feel); humanist sans for verdicts.
- **Signature visual element — the tier "grade stamp" scorecard:** each compound row carries a bold,
  rubber-stamp-style tier badge (PROVEN / EMERGING / UNPROVEN / AVOID / Rx) in the tier color — the
  scannable artifact you photograph and send to a friend about to buy NMN. Build this first and best.
- **Interactivity budget:** one element — a **tier filter + text search** over the compound list
  ("show only Proven", type "resveratrol"), native `<input>`/`:has()`, no framework. Cap here.
- **og:image (1200×630):** the Evidence Tier List grid, dark theme, controls hidden. The "screenshot
  this" artifact.
- **Mobile:** tier grid → single column stacked by tier; grade stamps stay legible; the dense
  per-compound table gets `overflow-x:auto` in a wrapper. Test at 375px.
- **Print:** sane defaults; ensure tier is conveyed by the stamp *word*, not color alone (greyscale).

## Density / acceptance
- ≥20 compound entries across the 4 tiers + the off-label drugs row + literacy layer.
- Every dose/effect/study dated + sourced inline; one prominent "not medical advice, not dosing
  guidance" disclaimer (README Rule 4 — no per-section hedging); visible `Last verified`;
  real `dateModified`.
- `TechArticle` JSON-LD only; no FAQ/HowTo schema despite question H2s.
- Self-containment test: a reader can correctly tier any popular compound and decide buy/skip from
  this page alone.
