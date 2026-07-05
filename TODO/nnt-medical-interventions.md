# Spec: NNT — What Medical Interventions Actually Do

**Target file:** `nnt-medical-interventions.html`

**Why this topic:** Doctors communicate in relative risk ("reduces heart attacks 30%!") but decisions require absolute numbers (Number Needed to Treat). The NNT data exists in Cochrane reviews and thennt.com but is scattered and never presented as a unified lay reference. Pure aggregation + base-rate-correction leverage — and the numbers are structurally stable, so low staleness risk.

## Targeting

- **Search intent: research mode.** The searcher types the topic, calmly — after an appointment, a prescription, or a scary headline. Primary query: **"number needed to treat examples"** (the list-seeking variant; the bare head term "number needed to treat" is definitional and belongs to the mental-model section). Secondary: "NNT statins primary prevention," "relative risk vs absolute risk example," "number needed to screen mammogram," "NNT and NNH list of common drugs," "does the flu shot actually work statistics." Sections 3–4 get question-shaped H2s ("Why is screening different?", "What do I ask my doctor?").
- **Title:** `Number Needed to Treat: What Common Treatments Actually Do` (59 chars — spell out NNT in the title; the abbreviation can carry the H1). **H1:** "NNT: What Medical Interventions Actually Do." **Meta description:** "NNT and NNH for 30+ common interventions — statins, aspirin, SSRIs, antibiotics, mammography — sourced from Cochrane and theNNT.com, with an icon array showing your absolute odds of benefit." (190 chars)
- **Reader outcome:** The reader can convert any relative-risk claim into absolute terms ("out of 100 people like me…") and walk into an appointment able to ask for the NNT, NNH, and timeframe of a proposed treatment at their age and baseline risk.
- **Success metric:** Organic entries on NNT/absolute-risk queries (search-first page → invest in question H2s and clean table extractability for answer engines); secondary, shares of the icon array as a citation in online arguments.
- **Volatile-facts register:** NNT/NNH values — STABLE; they move only when a Cochrane review updates. Annual pass against thennt.com/Cochrane per cited entry, re-date the page. USPSTF grades and screening age bands (mammography decades, PSA) — SLOW-DRIFT; revised on ~5-year cycles, check uspreventiveservicestaskforce.org. Guideline reversals of the aspirin-primary-prevention type — SLOW-DRIFT, and the reversal itself is teaching material, not just rot. Flu-vaccine NNT — per-season by nature; tag the season inline, never present as a constant. **Overall: STABLE** (this is the batch's lowest-maintenance page, per the topic-selection rationale above).
- **Index category:** Health & Fitness.
- **Jurisdiction:** The evidence base is international (Cochrane); the screening recommendations cited are US bodies (USPSTF) — flag once that non-US guidelines differ on screening ages/intervals while the arithmetic is universal. No state variance to handle.
- **Reading conditions:** desktop or tablet, evening, unhurried; readers 40–70 weighing their own prescriptions. Derived priorities: density and legibility over speed — tabular-nums, generous row height; the big table gets an `overflow-x` wrapper and the icon array must render honestly at 375 px; a printed big table is a plausible bring-to-the-appointment artifact, so print gets medium priority; standard dark-mode toggle suffices.
- **Cross-link map:** Outbound → `actual-risk-dashboard.html` (sister risk-literacy page: that page is hazard-side base rates, this one is treatment-side), `er-triage.html` (when the real question is urgency, not efficacy), `hospital-stay-survival.html` (its four medication questions pair with this page's doctor's-office script), `weight-loss-levers.html` (effect-size honesty for lifestyle interventions, where natural). Inbound: reciprocal from er-triage, hospital-stay-survival, and actual-risk-dashboard.

## Content approach

Framing is everything: this page is **decision support, not medical advice** — state that clearly once, prominently, then get on with the data. Not anti-medicine: include the spectacular winners (NNT 1–10) alongside the marginal ones, so the page reads as calibration, not contrarianism.

Sections:

1. **The mental model.** NNT = 1/ARR, explained with one worked example (statins primary prevention: ~1–2% absolute risk reduction over 5 yrs → NNT ~50–100, yet marketed as "~30% relative reduction"). Also define NNH (number needed to harm) — every entry below gets both. And the icon-array intuition: "out of 100 people like you taking this for 5 years…"
2. **Quick reference: the big table.** Columns: intervention, condition/population, NNT (benefit + what the benefit is), NNH (harm + what the harm is), timeframe, evidence grade, source. Populate ~25–35 rows from thennt.com / Cochrane — roughly 8–12 per band below, so no band reads as token:
   - **Winners:** antibiotics for confirmed bacterial meningitis, epinephrine in anaphylaxis, ORT for cholera, appendectomy, H. pylori eradication for ulcers, smoking cessation (any method), vaccines (measles, flu in elderly — per season).
   - **Solid but smaller than assumed:** statins secondary vs. primary prevention (the contrast is the lesson), BP meds by baseline risk, aspirin secondary (and the reversal on primary), SSRIs for severe vs. mild depression, metformin.
   - **Marginal/contested:** annual physicals, PSA screening, mammography by decade of age (NNS ~1,000+ to prevent one death; overdiagnosis numbers), arthroscopic knee surgery for degenerative tears, oseltamivir, glucosamine, most multivitamins.
3. **Screening is different.** Three concepts — Number Needed to Screen, lead-time bias, overdiagnosis — each explained with the worked mammography/PSA numbers from the big table, not fresh abstractions. This section prevents the most common misreading of the table.
4. **How to use this at the doctor's office.** 5–6 literal questions: "What's my absolute risk with and without this?", "What's the NNT for someone my age/risk?", "What happens if we wait a month?", "What's the NNH?", "Is this treating a number or a symptom?" Plus how to read a study headline (relative vs. absolute spotting drill with 2 real examples).
5. **Common mistakes** (5–7 entries): relative-risk seduction, assuming NNT of 50 means "won't work for me" (it's population math + tail insurance), comparing NNTs across different timeframes, ignoring baseline risk (same drug, NNT 20 vs. 200 depending on who you are), surrogate endpoints vs. outcomes that matter.

Research: thennt.com (primary aggregator, cite per-entry), Cochrane summaries, USPSTF grades. Every row must carry its timeframe — an NNT without a timeframe is meaningless.

## Visual design

**Icon-array-driven** — the signature visual of risk communication, and no other page on the site uses it.

- **Hero: an interactive icon array.** A 10×10 grid of 100 person-glyphs (CSS/SVG). A dropdown selects an intervention from the table → glyphs recolor: helped (green), harmed (orange), unaffected (gray — the visually dominant mass, which is the point). One line of caption text updates: "Statins, 5 yrs, primary prevention: 2 helped, 1 harmed (muscle symptoms), 97 unaffected."
- **Big table** with NNT rendered as a small horizontal dot-scale (log-ish: 1–10 / 10–100 / 100–1000+ bands) so magnitude is scannable without reading numbers; color-code evidence grade.
- Clinical-clean light theme: white, one medical teal accent, strong tabular typography (tabular-nums), generous row height. Feels like a well-designed lab report, not a blog.
- Each "big table" row expandable (details/summary) for the two-sentence context + citation, keeping the table dense by default.
- **Share card & screenshot artifact:** the icon array with the statins-primary-prevention example pre-selected, caption included — that exact frame is both the 1200×630 og:image and the "screenshot this" artifact. Two green, one orange, ninety-seven gray is the whole argument in one image.
