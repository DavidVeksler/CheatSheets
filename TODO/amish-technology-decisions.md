# Spec: The Amish Technology Decision Framework

**Target file:** `amish-technology-decisions.html`

**Why this topic:** The Amish are the only society running a deliberate, 300-year evaluation process for technology adoption — and almost everything written about them is either tourist mythology ("they reject technology") or academic prose nobody reads. The real system (community trials, reversibility, asking "what does this do to us?" before "what does this do for me?") is a portable decision framework arriving at exactly the right cultural moment (smartphones, AI). Extraction-without-tribal-membership is pure LLM leverage, and the knowledge is stable — near-zero staleness risk.

## Targeting

- **Primary query:** *"amish technology"* — **research mode.** The searcher is curious, not in crisis; they arrive with the misconception ("they reject technology") that section 1 exists to demolish. No crisis phrase needed in the H1; the hook is the correction itself. Question-shaped H2s should still match the real secondary queries below.
- **Secondary queries:** "why do amish not use technology," "do amish use electricity," "amish cell phone rules," "amish rules on technology / Ordnung rules," "how do amish decide what technology to use."
- **Title:** `Amish Technology: How They Actually Decide What to Adopt` (57 chars). **H1:** "The Amish Technology Decision Framework — They Don't Reject Technology; They Filter It." **Meta description:** "The Amish don't reject technology — they filter it: community trials, reversibility, phone shanties. How the 300-year evaluation process works, plus eight questions to run on your own next adoption." (~198 chars)
- **Reader outcome:** the reader can run the eight-questions trial on a live decision of their own — e.g., decide *where* a kid's smartphone lives (the shanty move) before deciding *whether* to buy it, or set a trial-and-revoke period for an LLM assistant.
- **Success metric:** search-first — organic entries on the primary/secondary queries — plus screenshots/shares of the eight-questions block. Implementation follows: invest in question-matching H2s and FAQ JSON-LD, and make the eight-questions block the most polished thing on the page.
- **Volatile-facts register — overall: STABLE** (near the most stable page in the collection):
  - Population count and ~20-year doubling time, retention ~85–90% — drift slowly (annual) → refresh against the Young Center's annual census; date the figures inline.
  - Affiliation-spectrum specifics (which affiliation permits what) — slow drift as districts vote → spot-check against Kraybill/Young Center on freshness passes; no inline dating needed beyond the page's `Last verified:` line.
  - Everything else — the Ordnung mechanism, the 1920s tractor reversal, *Wisconsin v. Yoder* (1972), the framework itself — inert.
- **Index category:** Philosophy & Religion (existing category).
- **Reading conditions:** relaxed rabbit-hole reading — desktop or phone, daytime, zero stress, likely arriving from a search or a share. No offline/print urgency, no crisis affordances; this frees the design to be what the spec asks for: serif-forward, larger base size, stillness. Sane print defaults suffice.
- **Scope:** descriptive content covers North American Old Order settlements (where essentially all Amish live); the extracted framework is jurisdiction-free. No "verify for your state" cadence applies to this page.
- **Cross-link map:** no sibling in this TODO batch — a standalone entry in the deliberate-living cluster. Outbound: `living-richly-guide.html`, `conscious-leadership-contexts.html`, `buddhism.html`; the LLM-assistant case study (section 5) links `ai-frontier.html` or `governing-agentic-ai.html` naturally — pick whichever fits the sentence. Inbound: add reciprocal links from those existing pages where a natural anchor exists.

## Content approach

Two-layer structure: (1) accurately describe how the system actually works — myth-busting via mechanism; (2) extract it as a general-purpose framework any person, family, or team can run. The page earns the second half by being rigorous in the first.

Sections:

1. **The core misconception.** They don't reject technology; they filter it slowly, communally, and by criteria other than utility. Lead with the killer examples: solar panels widely accepted, grid electricity refused (dependence/connection to the outside, not electrons); phone shanties at the end of the lane but not in the house (tool vs. tether — placement as policy); riding in cars vs. owning them; diesel-powered pneumatic ("Amish electricity") workshops; propane fridges. Each example states the *principle* it reveals. Density: 6–8 example pairs (the six above are the floor).
2. **How the decision process actually works.** The Ordnung (living, unwritten-ish rulebook, revisited semi-annually), the bishop and district autonomy (why adoption varies wildly between districts — natural experiments), the trial pattern: one member gets informal permission → community observes effects for months/years → keep or revoke. Key properties to name explicitly: default-no with burden of proof on the technology, small-scale trials, **reversibility** (they actually un-adopt; cite the tractor reversal of the 1920s), evaluation criterion = effect on community/family cohesion, not individual convenience.
3. **The affiliation spectrum table.** Swartzentruber → Andy Weaver → Old Order → New Order → Beachy/Amish-Mennonite, as columns/rows vs. technologies (grid power, tractors in field, cell phones, computers in business, cars). Density: 5 affiliations × 8–10 technologies. Shows it's a dial, not a switch — and functions as a comparison table of policy strictness.
4. **The extracted framework: eight questions to ask before adopting any technology.** The portable payoff. Roughly: What does it do to the texture of the day? Does it make me more dependent on distant systems? Who benefits from my adoption? Is it reversible — what's the exit cost? What did the trial reveal (run one!)? Does it replace something communal with something individual? Tool or tether (can I put it in a "shanty")? What's the second-order effect at full saturation? Each question: one line of Amish origin + one line of modern application.
5. **Case studies: the framework applied to modern choices.** 4–5 worked examples in identical format (question grid → verdict): smartphone for a 12-year-old (the shanty solution: shared family phone in the kitchen), social media for an adult, LLM assistants for a knowledge worker, smart-home devices, video games. Verdicts should be nuanced (adopt-with-placement-rules, trial-then-decide), not luddite.
6. **What the data says.** Brief honest section (6–8 dated data points): Amish population doubling every ~20 years, retention rates ~85–90% post-Rumspringa (myth-check Rumspringa while there), reported life-satisfaction findings, and the honest costs — education ceiling (8th grade, Wisconsin v. Yoder), genetic founder effects, constraints on individual autonomy, gender roles. No romanticizing; the framework is separable from the theology.
7. **Common mistakes** applying this (4–6 entries; the four below are the floor): confusing aesthetic minimalism with structural filtering, individual willpower vs. community enforcement (the mechanism IS the community; solo adaptations: precommitment devices, family media agreements), rejecting tools instead of placing them, one-way-door adoptions with no trial period.

Research: Kraybill (*The Riddle of Amish Culture*), Wetmore's engineering-ethics papers on Amish tech, Kevin Kelly's *What Technology Wants* Amish chapters, Young Center (Elizabethtown) population data.

## Visual design

**Handcraft aesthetic — the page itself should feel deliberately made.** Distinct from everything else on the site: no dark mode, no dashboard chrome.

- Palette and texture drawn from Amish quilts and barn wood: deep indigo, barn red, mustard, cream — flat solid color blocks with strong geometry (quilt-block motifs as section dividers, pure CSS).
- **Section 1 examples as "split cards":** left half ADOPTED (indigo), right half REFUSED (red) with the principle across the bottom seam — e.g., "solar panel | grid line → autonomy over convenience."
- **The affiliation spectrum as a horizontal gradient table** — strictest (darkest) to most permissive (lightest), one row per technology, filled/empty quilt-diamond glyphs as the yes/no marks.
- **The eight questions as a numbered woodcut-style list** — large drop numerals, generous spacing; this block designed to be screenshot-able as the page's shareable artifact, and it is also the **og:image**: render the 1200×630 social preview from it so the share card and the signature element are the same artifact.
- Case studies in identical bordered "trial record" cards — mimicking the community-trial idea: Proposed / Trial observations / Verdict rows.
- Serif-forward typography (something with warmth), slightly larger base size than site norm; restrained or zero JS — stillness as a design statement consistent with the subject.
