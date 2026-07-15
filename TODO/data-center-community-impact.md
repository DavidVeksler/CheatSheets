# A Data Center Is Coming to Your Town: Claim vs. Evidence

Target file: `data-center-community-impact.html`

## Why this topic

Highest raw search demand in the cluster: 71% of Americans oppose a local data center (Gallup, March 2026), 14 states are considering bans or pauses, and residents/officials/journalists are searching question-shaped queries with terrible answer quality — advocacy content in both directions, syndicated MSP listicles, no neutral scannable reference. The claim-vs-evidence format differentiates from every competitor and fits the site's evidence-graded analyst brand. Ranked fourth because audience overlap with the rest of the corpus is weakest and maintenance burden is highest; ship after the engineering cluster establishes the hub.

## Targeting

- **Primary query:** do data centers raise electricity bills
- **Secondary queries:** how many jobs does a data center create; data center water usage per day; how loud is a data center; data center tax revenue local community; data center pros and cons
- **Mode:** Crisis-adjacent (active local controversy; reader may be preparing for a county meeting tonight)
- **Title:** Data Center Coming to Your Town? Every Claim, Graded Against the Evidence
- **H1:** A Data Center Is Coming to Your Town: The Fact Sheet
- **Meta description:** Do data centers raise electric bills? How many jobs do they really create? Every common claim from boosters and opponents, graded against published evidence — with sources.
- **Reader outcome:** A resident or local official can walk into a zoning meeting able to separate evidenced claims from rhetoric on both sides, and knows which questions to ask the developer (rate class, water source, community benefits agreement, noise study).
- **Success metric:** ≥1,000 organic sessions/month within 9 months (demand supports it); at least one citation from local journalism.
- **Volatile-facts register:**
  - Physical basics (why cooling uses water, why load affects rates): STABLE
  - Job counts per facility class, water gallons/year ranges, noise dB measurements, tax revenue mechanics: SLOW-DRIFT (6-month re-verify)
  - Poll numbers, rate projections, state legislation status, named-project outcomes: VOLATILE — this page carries the heaviest register in the cluster; commit to a 6-month verification cadence or don't ship it
- **Index category:** [VERIFY against category-map.php — may need a civic/consumer category]
- **Jurisdiction/geographic scope:** US only; state-level variance (rate regulation, water law) flagged throughout
- **Reading conditions:** Mobile-first — readers arrive from local Facebook groups and news links on phones. Print is a first-class deliverable: people bring printouts to public meetings. Both must be excellent.
- **Cross-link map:** To `datacenter-power-chain.html` (rate-design deep dive), `ai-infrastructure-numbers.html` (scale numbers). Inbound from both. [VERIFY existing corpus.]

## Content approach

- **Quick-reference block (top):** The scorecard — ~10 claims, each with a one-line evidence grade (Supported / Mixed / Depends on rate design / Unsupported) and the key number.
- **Fundamentals:** How a hyperscale facility actually interacts with a community: construction phase vs operations phase, who the utility customer classes are, how costs get socialized.
- **Working knowledge:** One section per claim domain — electricity bills (the honest answer: panel data through 2024 shows ~$2/month effects, but AI-scale load and $4.3B in socialized 2024 connection costs point the other direction; rate design is the variable), jobs (20–150 permanent vs thousands construction), water (110M gal/yr medium facility; two-thirds of post-2022 builds in water-stressed areas), noise (40–59 dB measured at residences vs 92–96 dB at source), taxes and abatements, property values.
- **Edge/advanced:** What actually protects residents — large-load tariffs and separate rate classes, "pay your way" interconnection cost allocation, community benefits agreements, NDA limits, water-use disclosure. The "questions to ask the developer" checklist.
- **Major tables:**
  1. Claim scorecard (signature): ~10 rows — claim, who makes it, evidence grade, key figure, source.
  2. Impact-by-domain: ~6 rows (bills, jobs, water, noise, land, taxes × construction-phase vs operating-phase effect).
  3. Resident's question checklist: ~8 rows (question, why it matters, what a good answer looks like).
- **Common mistakes:** Attributing all bill increases to the local facility (grid costs are regional); comparing construction jobs to permanent jobs; assuming tax revenue is net of abatements; both-sides fallacy — some claims really are better evidenced than others, and the page must say so.

## Research sources

- Primary: Gallup March 2026 poll, Rutgers NJ State Policy Lab panel study, Union of Concerned Scientists connection-cost report, Virginia JLARC 2024 report, Ceres water analyses, Brookings rate analysis, EESI, NCSL legislation tracker, Consumer Reports investigation. Where advocacy sources are used (either direction), label them as such in the page.
- **Must not recall from memory:** every poll number, dollar figure, gallon figure, dB measurement, job count, and legislative status. This page lives or dies on citation density; every scorecard row links its source.

## Visual design

- **Palette/aesthetic:** Civic-neutral — warm paper/off-white base (departure from the engineering cluster's dark theme, signaling different audience), navy + evidence-grade color coding (green/amber/gray/red) used only in the scorecard.
- **Signature visual:** The claim-vs-evidence scorecard styled as a report card — claim on the left, grade chip, key number, source link. Designed to screenshot as a single legible card.
- **og:image:** 1200x630 screenshot of the top 6 scorecard rows.
- **Mobile:** scorecard rows become stacked cards; checklist collapsible via native details elements. **Print:** scorecard + checklist fit two pages, grade chips grayscale-distinguishable (shape + letter, not color alone).
