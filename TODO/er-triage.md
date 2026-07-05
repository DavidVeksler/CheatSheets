# Spec: "Is This an Emergency?" — ER, Urgent Care, or Wait

**Target file:** `er-triage.html`

**Why this topic:** The single highest-stakes piece of practitioner folklore — triage nurses carry precise escalation heuristics (which chest pains, which head bumps, which fevers) that exist only in nursing lore and clinical decision rules, never as a lay reference. Consumers face a 30x cost spread (telehealth ~$50 → urgent care ~$150–250 → ER $2,000+) and err in both directions: ER visits for ear infections, and "waiting out" strokes. Decision-support framing keeps it defensible.

## Targeting

- **Search intent: crisis mode.** The searcher has the symptom *now* and types the situation, not the topic. Primary query: **"should I go to the ER or urgent care."** Secondary: "when to go to the ER for chest pain," "baby fever when to go to ER," "does my cut need stitches," "hit head when to go to hospital," "urgent care vs emergency room cost." Symptom H2s should be question-shaped to match real queries ("Hit your head — ER or wait?"), not clinical labels ("Cranial trauma").
- **Title:** `ER or Urgent Care? When to Go, When It Can Wait` (47 chars). **H1:** "Is This an Emergency? ER, Urgent Care, or Wait" — leads with the crisis question. **Meta description:** "Symptom-by-symptom decision tables built from real triage rules (Ottawa ankle, PECARN, Canadian CT Head): when chest pain, head bumps, fevers, and cuts mean 911, urgent care today, or watch at home." (198 chars)
- **Reader outcome:** At 3 AM with a scary symptom, the reader can place it in the correct tier — 911/ER now, urgent care today, or watch at home — by checking the discriminating features on the matching card, and can say *why* ("fever plus stiff neck, not fever alone").
- **Success metric:** Organic entries on symptom + venue queries, with night-time mobile sessions as the tell that the page reaches its real moment of use; secondary, repeat-direct visits from households that bookmarked it.
- **Volatile-facts register:** Clinical decision rules (Canadian CT Head, Ottawa, PECARN, pediatric fever cutoffs) — STABLE published instruments; re-verify only on formal revision. Cost figures ($50 telehealth → $2,000+ ER) — SLOW-DRIFT; re-check yearly against FAIR Health / published claims averages, dated inline. Hotlines (911, 988, Poison Control 1-800-222-1222) and EMTALA — STABLE; confirm annually they still work as described. Freestanding-ER billing distinctions — SLOW-DRIFT (state legislation moves). **Overall: STABLE**, with one SLOW-DRIFT cost column.
- **Index category:** Health & Fitness.
- **Jurisdiction:** US-only for numbers, costs, and law (911, 988, Poison Control, EMTALA, freestanding-ER billing); the clinical red flags themselves are universal. One line up top tells non-US readers to substitute their emergency number and skip the billing content.
- **Reading conditions:** one-handed phone, 3 AM, dark bedroom or parked car, frightened parent or spouse, zero patience for prose. Derived priorities: the dark variant and big tap targets are load-bearing requirements, not polish; single column; 911 list above the fold; print is low priority; the symptom-picker index is the navigation because nobody scroll-hunts in a panic.
- **Cross-link map:** Outbound → `hospital-stay-survival.html` (companion: this page gets you to the hospital, that one gets you out intact), `nnt-medical-interventions.html` (for the non-emergent "is this treatment even worth it" question), `actual-risk-dashboard.html` (base-rate calibration for the chronic worrier). Inbound: reciprocal links from all three.

## Content approach

Framing is critical and must be exact: this page helps you choose the **level and speed of care**, never whether to seek care. Prominent standing rule at top: *when genuinely in doubt, call 911 or your nurse line — this page is for the 3 AM "how worried should I be" moment, not a diagnosis.* Also surface the two free expert resources people forget: 24/7 nurse lines (on the back of every insurance card) and Poison Control (1-800-222-1222).

Sections:

1. **Quick reference: the venue table.** ER vs. urgent care vs. primary care vs. telehealth vs. self-care (5 venues × ~6 decision columns) — columns: typical cost (insured/uninsured), wait, capabilities (imaging? sutures? IV? cardiac workup?), and the one-line "go here when." Include the folklore facts: urgent care can do X-rays and stitches but not CT/appendicitis workups; freestanding ERs bill like hospital ERs despite looking like urgent cares (name-check how to tell them apart — "Emergency" in the name = ER billing).
2. **Call 911 NOW list.** The unambiguous list (expect 8–10 entries), each with its reason: FAST-plus stroke signs (face droop, arm drift, speech, time — plus sudden worst headache, sudden vision loss), chest pain with pressure/radiation/sweating/shortness of breath, anaphylaxis signs, major bleeding that soaks through pressure, blue lips/struggling to breathe, suicidal intent with plan (988 + 911 guidance), seizure >5 min or first-ever, signs of sepsis (fever + confusion + rapid breathing). Why 911 beats driving for cardiac/stroke: treatment starts in the ambulance and ERs fast-track EMS arrivals.
3. **The symptom decision tables — the core of the page.** One compact decision block per common presentation — the 12 cards below, each structured as ER now / urgent care today / watch and wait, with the discriminating features drawn from real clinical decision rules (cite them). Expect 8–15 discriminating features per card across its three tiers; a card with 4 total lines is under-researched:
   - **Chest pain** (features that matter vs. reproducible-by-touch/positional)
   - **Head injury** (Canadian CT Head Rule distilled: LOC, repeated vomiting, age >65, anticoagulants, worsening headache; kids: PECARN highlights)
   - **Abdominal pain** (RLQ migration, rigidity, pain-out-of-proportion; the appendicitis timeline)
   - **Fever by age** (the hard cutoffs: <3 months ≥100.4°F = ER, period; adult thresholds + red flags: stiff neck, rash that doesn't blanch, confusion)
   - **Cuts** (need stitches? gaping, depth, location, the 6–12 hr closure window; tendon/nerve checks: can you move/feel below it)
   - **Sprains/possible fractures** (Ottawa ankle rules distilled: can you bear weight for 4 steps + bony tenderness points)
   - **Back pain** (red flags: saddle numbness, bladder/bowel changes = ER for cauda equina; otherwise almost never an emergency)
   - **Headache** (thunderclap, worst-ever, with fever/stiff neck, after age 50 new-onset vs. the migraine pattern)
   - **Allergic reactions** (skin-only vs. two-system involvement)
   - **Vomiting/diarrhea** (dehydration signs by age, blood, the bilious/green rule in infants)
   - **Eye problems** (sudden vision loss/curtain/flashes-and-floaters surge = same-day ophtho or ER; red eye discriminators)
   - **Kids' breathing** (retractions, grunting, nostril flaring — the visual signs parents miss)
4. **What the triage nurse is actually assessing.** Brief demystifier: the ESI 1–5 scale, why the quiet gray sweaty person goes first and the screaming ankle waits, why "chest pain" gets you an EKG in 10 minutes regardless of the waiting room. Payoff: how to describe symptoms so triage understands — onset, severity movement, associated symptoms; never minimize ("it's probably nothing, but…" buries the signal).
5. **Common mistakes** (6–8 entries): driving yourself during a possible heart attack, sleeping off a head injury on blood thinners, urgent care for abdominal pain that needs a CT (double-billing round trip), ER for medication refills, ignoring symptom *combinations* (fever alone vs. fever+stiff neck), and cost-fear delay for the genuinely emergent (EMTALA: ERs must screen and stabilize regardless of ability to pay).

Research: cite the actual decision instruments (Canadian CT Head, Ottawa ankle, PECARN, ESI handbook, ACEP/CDC patient guidance). Every threshold number must come from the published rule, not vibes. Standard medical disclaimer per site norms.

## Visual design

**Triage-tag aesthetic** — the page borrows the visual language of START triage tags and ED signage: content is literally color-sorted the way triage sorts patients.

- Three-color system used with total consistency: **red (ER/911) / amber (urgent care today) / green (watch at home)** — every entry in every table carries its color as a left-edge band; the decision blocks are physically grouped in that order.
- Light clinical background, but the section headers styled as **hospital wayfinding signage**: bold condensed type on solid color bars with arrow chevrons (→ EMERGENCY, → URGENT CARE).
- **Each symptom block is a "triage card":** perforation-dot border and a corner hole + string illustration echoing a paper triage tag; discriminating features as checkbox lines.
- The 911 list on a solid red band with white text — visually impossible to miss, placed above the fold.
- One interactive element: a symptom-picker index (click "head injury" → jump + highlight the card). No calculators — false precision is dangerous here.
- **Share card & screenshot artifact:** the og:image (1200×630) is a fanned red/amber/green triage-card trio with the H1 — the three-color sort IS the page's identity. The "screenshot this" block is the solid-red Call 911 NOW band, which must render complete within one phone screen.
- Mobile-first ruthlessness: this page's real usage is one-handed at 3 AM — single column, big tap targets, dark-mode media query supported (a genuinely dim night variant, not just inverted).
