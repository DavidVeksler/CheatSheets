# Spec: longevity-what-actually-works.html

**Target file:** `longevity-what-actually-works.html`
**Cluster:** Longevity (pillar page — 3-page cluster; the other two are
`longevity-supplements-evidence.html` and `longevity-biomarkers.html`, specced alongside this).

## Why this topic

Longevity is one of the most searched, most monetized health topics on the internet — and almost
every source ranking for it is selling something: a supplement stack (NOVOS, Purovitalis, Clariti),
a clinic membership (Valley Healthspan, DexaFit), a $200 book (*Outlive*, *Lifespan*), a testing
subscription, or a newsletter funnel. That commercial incentive systematically inflates the exotic
(rapamycin, NAD boosters, cold plunges, epigenetic clocks) and buries the boring interventions that
actually carry the evidence, because you can't sell someone "walk more and stop smoking."

**The site's angle — and the only reason to build this — is that David sells none of it.** No
supplements, no book, no seminar, no clinic, no affiliate links (this page is explicitly excluded
from the Phase-2 affiliate list). That makes it possible to do the one thing the funnel pages
can't: rank every popular longevity intervention *honestly by effect size × evidence quality*, and
name the myths as myths. This is the same honest-broker franchise the site already runs with
`nnt-medical-interventions.html` ("what treatments actually do"), `actual-risk-dashboard.html`
("what actually kills people"), and `reassurance-tables.html` — longevity is the natural next
member of that family, and it's a conspicuous gap in the Health & Fitness cluster (which has the
*how-to* pages — strength, running, cycling, sleep — but no *what-matters-most* decision layer).

The page is a **decision layer, not a how-to.** It does not re-teach how to lift or how to sleep —
it ranks *which* interventions move all-cause mortality most, with the real numbers, and links out
to the existing how-to pages for execution. Its job is to reset the reader's priorities: the person
who arrives worried about resveratrol dosing should leave understanding that their VO2 max, their
cigarettes, and their strength training dwarf every pill on the market.

## Targeting

- **Primary query:** `what actually extends life` / `what actually works for longevity`
- **Secondary queries:**
  - `longevity myths` / `longevity myths debunked`
  - `does resveratrol actually work` / `do longevity supplements work` (routes deeper to the
    supplements spoke, but the myth framing lives here)
  - `how to live longer evidence based`
  - `blue zones debunked` / `are blue zones real`
  - `biggest factors in living longer` / `what has the biggest effect on lifespan`
- **Search mode:** **research mode** (topic-searched, not crisis). Title/H1 lead with the
  evidence-vs-myth hook, not a symptom. Use question-shaped H2s that match real queries
  ("Do longevity supplements actually work?", "Is the metabolism-slows-after-30 thing true?",
  "Are blue zones real?").
- **Draft title (≤60 char):** `What Actually Extends Life: Longevity Evidence vs. Myths`
- **Draft H1:** `What Actually Extends Human Life`
  (dek beneath: *Every popular longevity intervention, ranked by real effect size and evidence
  quality — by someone selling you nothing.*)
- **Meta description (150–200):** `A no-hype longevity guide: every intervention ranked by its real
  effect on all-cause mortality and evidence quality, plus the myths (blue zones, antioxidants,
  metabolism-after-30, most supplements) debunked. No products, no book, no supplements to sell.`
- **Reader outcome ("definition of working"):** After this page a reader can correctly rank the
  top ~15 longevity interventions by evidence-backed effect size, state which of their own habits
  is the highest-leverage change available to them, and recognize the five or six most common
  longevity myths on sight — without buying anything.
- **Success metric:** organic entries on the `longevity myths` / `what actually works` query
  family; shares of the "Leverage Ladder" artifact; time-on-page and click-through into the two
  spoke pages and the existing how-to pages (internal-link depth for the cluster). Primarily a
  goal-4 (advocacy / brand-as-honest-broker) + goal-1 (study) page, with goal-3 (case-study) upside.
  **Note (2026-07-12 GSC):** the site has zero current longevity/healthspan search footprint (the
  health pages that exist rank at position 40–70) — so this cluster is a *demand-creation* bet, not
  a striking-distance capture. Judge it on brand/advocacy value and shares, and give it 3–6 months
  before reading its search performance; do not judge it against the site's established AI-topic
  traffic.
- **Index category:** `Health & Fitness` (add all three cluster files to `category-map.php`).
- **Jurisdiction/geographic scope:** universal biology; no jurisdictional content. Effect sizes are
  from international cohorts/meta-analyses — note population where a figure is population-specific.

## Volatile-facts register (staleness profile)

Overall rating: **SLOW-DRIFT.** The core effect sizes are stable (decades of cohort data); the
research-frontier items and the "myth status" of specific compounds drift.

| Fact class | Rating | Re-verify against |
|---|---|---|
| Mortality hazard ratios / MET-hour dose-response for activity | STABLE | PLOS Med pooled analysis, 2018 NEJM smoking papers, Cochrane |
| Smoking cessation years-of-life-gained (≈10y if quit by 35–44) | STABLE | NEJM (Jha 2013 / EVIDoa2300272) |
| Metabolism-stable-20-to-60 (Pontzer) | STABLE | *Science* 2021 (Pontzer et al.) |
| Blue-zones data-quality critique | SLOW-DRIFT | Newman 2024 (bioRxiv/Ig Nobel); note the ongoing rebuttal |
| Which supplements/drugs are "proven vs hype" | VOLATILE → lives in the **supplements spoke**; this page only summarizes | see that spec |
| Strength-training dose sweet spot (~30–60 / 60–120 min/wk) | SLOW-DRIFT | 2022 BJSM meta-analysis; 2025 cohort updates |

Every numeric effect size is an **anchor, not a fact** (README Rule 1). Verify each against the
primary source named above at build time; if a figure can't be verified, omit the row rather than
shipping the anchor.

## Cross-link map

- **Outbound (spoke pages, this cluster):** `longevity-supplements-evidence.html` (from the
  supplements row + the "do supplements work?" myth), `longevity-biomarkers.html` (from the "measure
  what matters" section + the VO2/grip rows).
- **Outbound (existing how-to pages — execution layer):** `strength-training.html`,
  `running.html`, `cycling.html`, `sleep-optimization.html`, `weight-loss-levers.html`,
  `blood-tests-cbc-cmp-lipids-a1c-thyroid.html`.
- **Outbound (existing decision-layer siblings):** `nnt-medical-interventions.html` (statins/aspirin
  effect sizes belong there), `actual-risk-dashboard.html` (micromort framing of what kills people),
  `reassurance-tables.html`.
- **Reciprocal inbound (add one natural link back):** from `strength-training.html` and
  `sleep-optimization.html` intro/CTA, and from `nnt-medical-interventions.html` ("for lifestyle
  interventions, see…").

## Content approach

### Quick-reference block (top of page): "The Leverage Ladder"
The signature artifact (see Visual design). A single ranked list/bar array of interventions by
approximate effect on all-cause mortality, each tagged with an evidence grade (A–D). This is the
"cheat-within-the-cheat": the whole thesis visible in one screen. Rows ordered roughly:

1. Don't smoke / quit smoking — up to ~10 yrs life expectancy if quit by 35–44 (Grade A)
2. Cardiorespiratory fitness (VO2 max — low→high fitness ≈ up to 5× mortality difference) (Grade A)
3. Any regular physical activity vs sedentary (≈14–25% mortality reduction, dose-response) (Grade A)
4. Strength/resistance training (~10–20% lower all-cause mortality at 30–60 min/wk) (Grade A/B)
5. Not being obese / metabolic health (waist, A1c, BP) (Grade A)
6. Blood pressure control (Grade A)
7. Sleep 7–9h, consistent (U-shaped risk) (Grade B)
8. Diet quality (Mediterranean-pattern, fiber, less ultra-processed) (Grade B)
9. Social connection / not being lonely (Grade B)
10. Moderate/less alcohol (the "moderate drinking is protective" claim has weakened) (Grade B/C)
11. Statins / aspirin etc. → pointer to NNT page (Grade A for secondary prevention) (Grade A)
12. **Below the line:** most supplements, antioxidants, "detox," cold plunge, resveratrol,
    NAD boosters → pointer to supplements spoke (Grade C/D / unproven)

### Fundamentals — "How to read a longevity claim" (the literacy layer)
- All-cause mortality vs disease-specific vs surrogate markers — why only all-cause counts.
- Relative vs absolute risk; hazard ratios; what "20% lower risk" does and doesn't mean.
- Mouse lifespan ≠ human lifespan; healthspan vs lifespan.
- The evidence hierarchy: RCT > large prospective cohort > case-control > mechanistic/animal >
  anecdote/influencer. Define the A–D grade scale used on the page.
- Confounding & reverse causation (sick-quitter effect, "healthy user" bias).

### Working knowledge — the ranked interventions, each as an atomic entry
For **each** intervention in the ladder, a card/row with: precise effect size + population/source,
evidence grade, the realistic dose/threshold, one concrete number, and a "when this matters most /
who benefits most" line, plus a link to the how-to page where relevant. Target **15–20 intervention
entries.**

### Edge & advanced — "Myths, half-truths, and honest uncertainty"
The myth-busting section — MANDATORY, and a core reason the page exists. Each myth as an atomic
entry: the claim, the reality, the source, and the grade of the debunk. Target **10–14 myths.**
Candidate list (verify each):
- **Blue zones** are validated longevity hotspots → data-quality critique (Newman 2024: missing
  birth certificates, pension fraud, age-heaping on multiples of 5). Handle fairly: note the
  rebuttal; the *habits* (move, eat plants, connection) are fine even if the *demographics* are shaky.
- Metabolism crashes after 30 → Pontzer 2021: stable 20–60, declines ~0.7%/yr only after 60.
- Antioxidant supplements slow aging → RCTs show no benefit, some harm (↑ certain cancers).
- "Detox"/cleanses remove toxins → physiology myth; kidneys/liver already do it.
- You must drink 8 glasses of water/day → no evidence basis (1945 misread; food counts).
- Resveratrol is a proven longevity drug → SIRT1 assay artifact; failed mouse lifespan; Sinclair
  caveat (routes to supplements spoke).
- Lifting heavy is dangerous as you age → progressed resistance training *reduces* fall/fracture risk.
- Stretching/"toxins" cause soreness; "no pain no gain"; running ruins your knees (link running page).
- More exercise is always better / marathons are optimal → dose-response plateaus; U-shape debated.
- Genetics decide your lifespan → heritability of longevity is modest (~20–30%); behavior dominates
  the modifiable range.
- Expensive biomarker panels/epigenetic clocks tell you your "true age" → routes to biomarkers spoke.
- Moderate drinking is heart-healthy → the protective-J-curve has largely collapsed under
  Mendelian-randomization / abstainer-bias correction.

### Common Mistakes / Anti-Patterns (required)
- Optimizing the exotic (supplements, cold plunge) while ignoring the boring giants (fitness, smoking).
- Chasing surrogate markers instead of function/mortality.
- Trusting mouse studies and influencer stacks.
- Treating a single cohort headline as settled science.

## Research sources (verify at build — do NOT recall numbers from memory)
- Physical-activity dose-response: PLOS Medicine pooled cohort (Arem/Moore 2015); BJSM/2022 meta.
- Smoking cessation: NEJM (Jha et al. 2013; NEJM Evidence 2024, EVIDoa2300272).
- VO2 max / cardiorespiratory fitness & mortality: JAMA Netw Open (Mandsager/Cleveland Clinic 2018,
  n≈122,007). (Deep VO2 numbers live on the biomarkers spoke; summarize here.)
- Strength training & mortality: 2022 BJSM systematic review/meta-analysis; large cohort updates.
- Metabolism stability: Pontzer et al., *Science* 2021.
- Blue-zones critique: Newman S.J., bioRxiv 2019/2024 preprint + 2024 Ig Nobel coverage; include a
  Blue Zones / Buettner rebuttal link for fairness.
- Antioxidants: Cochrane reviews (Bjelakovic) on antioxidant supplementation and mortality.
- Alcohol J-curve collapse: recent Mendelian-randomization and meta-analyses (e.g., 2023 JAMA Netw
  Open Zhao et al.).
- Statins/aspirin: defer to `theNNT.com` / existing NNT page rather than re-deriving.

## Visual design

- **Aesthetic:** clinical-evidence / "peer-review desk," distinct from the two spokes. Deep teal-green
  base consistent with the Health category (`#065f46`), on near-white paper for the light theme and a
  slate-charcoal dark theme via `light-dark()`. One restrained accent scale carries the whole page:
  the **evidence-grade color ramp** — A `#15803d` (green), B `#2563eb` (blue), C `#d97706` (amber),
  D `#6b7280` (grey), MYTH `#dc2626` (red). Grade chips reuse this ramp everywhere so the page reads
  as one graded system. Clean humanist sans for body; a heavier/condensed face (system stack) for
  ladder labels and grades.
- **Signature visual element — "The Leverage Ladder":** a horizontal ranked bar array of
  interventions, bar length ∝ approximate effect on all-cause mortality (label the axis honestly as
  a rough composite, not false precision), each bar colored by its evidence grade, with the myths
  shown *below the zero line / greyed with a red "MYTH" stamp* to make the hierarchy visceral. Build
  this first and best; it is the shareable artifact. Pure CSS/SVG, no chart library. Must collapse to
  single-column stacked bars at 375px with labels above bars.
- **Signature secondary element — "MYTHBUSTED" stamps:** rubber-stamp-style verdict badges on each
  myth card (echoing the NNT page's verdict language), in the MYTH-red.
- **Interactivity budget:** one element max — a **grade filter** (show All / A–B only / Myths only)
  toggling the ladder + cards, using `:has()`/native controls, no framework. Optional: none beyond this.
- **og:image (1200×630) target:** the Leverage Ladder at the top of the page, dark theme, floating
  controls hidden. It IS the "screenshot this" artifact.
- **Mobile:** ladder → single column; grade chips stay legible; tap targets ≥44px.
- **Print:** sane defaults suffice (no mandatory print stylesheet); ensure the ladder and grade
  colors survive greyscale by keeping the grade letter visible, not color-only.

## Density / acceptance
- ≥15 intervention entries + ≥10 myth entries + literacy layer = comfortably past the 20-entry floor.
- Every effect size dated/sourced inline; visible `Last verified: YYYY-MM-DD`; `dateModified` real.
- `TechArticle` JSON-LD only; no FAQ/HowTo schema (per AGENTS.md) even though H2s are question-shaped.
- Self-containment test: a reader can rank their own highest-leverage change from this page alone.
