# Spec: refine `homelessness-externalized-costs.html` into a compelling, defensible argument

**Target file:** `homelessness-externalized-costs.html` (existing page; URL and slug stay).
**Kind:** revision of a shipped advocacy page, not a new sheet. Judged by the advocacy goal in `TODO/META-seo-planning.md`, not by traffic.
**Implementer:** Opus for the rewrite; Sonnet for the final style pass (§9). Read `AGENTS.md`, then this spec, then `TODO/README.md`. Rule 1 applies: every number below is an anchor to verify, not a fact to ship.
**Why this revision:** a 2026-09-10 critique found the page rigorous but self-defeating. The hero claims causation the body then disclaims forty times; three mechanisms are drawn as equals when the evidence supports one; the headline number is an amenity gap, not a regulatory cost; the care mechanism does not fit the free-market frame; and the page is two essays (externalized costs, then bottom rungs) stitched at a visible seam. This spec fixes the argument, not the evidence discipline, which stays.

---

## 1. The argument this page makes (the only thing the implementer must get exactly right)

State it once, in the hero and again in one paragraph under it, then never restate it.

> Where homelessness concentrates in the United States is explained by rents and vacancy, not by poverty, drug use, mental illness or weather. Rents are highest where rules constrain housing supply and where the cheapest legal housing forms have been abolished. So the cheapest intervention against homelessness is repeal, and repeal never appears in the budget debate, because it has no line item and the people it would help are not in the room. The full ledger has two columns, each with a hidden half: the costs of homelessness that land outside public accounts, and the costs of prevention that are political rather than fiscal. Count both, then compare reforms on outcomes and rights, not on appropriations.

Three confidence tiers, declared on the page and used consistently:

| Tier | Claim | Basis |
|---|---|---|
| **Established** | Rent and vacancy predict regional homelessness rates; individual risk factors predict who within a metro, not which metro. | Colburn & Aldern 2022 (cross-metro), consistent with Quigley, Raphael & Smolensky 2001 and Hanratty 2017. |
| **Established** | Land-use restriction raises land and housing prices in constrained metros. | Gyourko & Krimmel 2021; Glaeser & Gyourko 2018 JEP; Greenaway-McGrevy & Phillips 2023 (Auckland upzoning). |
| **Established** | The cheapest legal housing form (SRO, rooming house) was regulated out of existence and is hard to rebuild. | HUD 2018; NYC lost on the order of 175,000 SRO units 1955 to 1990s (anchor; verify via Furman or Coalition for the Homeless). |
| **Probable** | Minimum-wage increases raise homeless counts at the margin. | One peer-reviewed study (Hill 2025). Opposing literature must be cited (see §5). |
| **Probable** | Psychiatric capacity and financing restrictions shift care costs to families, ERs, jails and streets. | Bed counts plus displacement evidence; no causal conversion. |
| **Contested / rights question** | Whether commitment standards should change. | Not an economic question; handled in §6 as a tradeoff, not a mechanism. |

The page must never assign a tier higher than this table allows. It may lower one if verification disappoints.

**Reader outcome (definition of working):** a reader can explain, with three citations, why "which city" is a rent question and not a drug question, name the specific regulatory changes that would restore the cheapest housing form, and audit any local "cost of homelessness" figure for the four quadrants of the ledger.

---

## 2. Search targeting and naming

- **Primary query (research mode):** `why is homelessness higher in california than west virginia` and variants (`homelessness rent vs poverty`, `is homelessness a housing problem`).
- **Secondary:** `cost of homelessness per person`, `SRO housing why illegal`, `minimum wage homelessness study`, `hidden costs of homelessness`, `Bastiat seen unseen homelessness`.
- **`<title>`** (≤60): `Homelessness: The Costs We Hide and the Options We Banned` (57)
- **H1:** `Homelessness tracks rents. Rents track the rules.`
- **Deck:** "Across US metros, rent and vacancy explain where homelessness concentrates; poverty, drug use and mental illness do not. The rules that push rents up, and the cheap rooms they outlaw, never appear on the bill for managing the result."
- **Meta description (150–200):** draft: "Why homelessness follows rents rather than poverty or drugs, which rules push rents up, and what the budget debate leaves out on both sides of the ledger: hidden costs of homelessness and the political cost of repeal." (verify length at build).
- **Index category:** keep the page's current `category-map.php` assignment.
- **Cross-links:** outbound to `housing-comparison.html`, `economic-systems-compared.html`, `red-vs-blue-state-economies.html`; add a reciprocal link from `housing-comparison.html`. One line each, in a Related block near the footer.
- **Reading conditions:** desktop or tablet, unhurried, reader is arguing with someone (a council meeting, a comment thread). Optimize for quotable, sourced paragraphs and a printable ledger. Dark mode stays.

---

## 3. Structure and word budget

Target 6,000 to 6,800 words total, down from 10,162. Cuts come from the registers (§8), the negation tic (§9), and removing the duplicated thesis restatements. Order:

| # | Section | Anchor id (keep existing ids where they exist) | Words |
|---|---|---|---|
| 0 | Hero: H1, deck, three defensible numbers, tier legend | `main` | 250 |
| 1 | The argument in one paragraph, plus the confidence table from §1 | new `h-argument` | 350 |
| 2 | Signature figure: the weighted ladder (§10) | `lad-*` | 120 |
| 3 | Housing: the load-bearing mechanism | `h-housing-rung`, `housing-math` | 1,300 |
| 4 | Work: a secondary channel, both sides cited | `h-work-rung` | 600 |
| 5 | Care: financing and capacity (economic), then commitment (rights) | `h-capacity`, `h-care-rung` | 700 |
| 6 | Who is on the bottom rung (disability evidence, with its implication stated) | `h-non-investment` (rename to `h-bottom-rung`) | 450 |
| 7 | The two-column ledger and the sign inversion | `h-seen-unseen`, `h-hardening` | 700 |
| 8 | Objections, answered | new `h-objections` | 800 |
| 9 | Reform tests | `h-reform-test` | 400 |
| 10 | Evidence registers (condensed, collapsed by default) | `h-ledger`, `h-public-budget`, `h-public-space`, `h-avoidance`, `h-property-crime`, `h-sanitation`, `h-comparison` | 900 |
| 11 | Accounting mistakes (trim to 10 rows) | `h-limits` | 300 |
| 12 | Method note and byline | | 120 |

Every existing `id` that is dropped must get a same-page redirect target (a hidden anchor or a renamed heading keeping the old id) so inbound deep links from the index catalog and the SEO cross-linking repo do not break. Regenerate `catalog.json` after.

---

## 4. Hero numbers (replace the current three)

The current hero shows $9,360/year (an amenity gap), 2–3% (an elasticity), and 10.8 beds/100k (a stock). Replace with three numbers that each support a tiered claim and each convert to something a reader can picture.

1. **The geography number.** The Colburn & Aldern contrast: a high-poverty, low-rent state versus a low-poverty, high-rent metro. Anchor: West Virginia has among the highest poverty rates and among the lowest homelessness rates; San Francisco or Seattle the reverse. Present as two per-10,000 homelessness rates and two poverty rates from HUD PIT 2024 and Census ACS 2024, sourced, not from the book's paraphrase. Caption: "Poverty does not predict it. Rent does."
2. **The people number.** Hill's 2–3% converted to people: 2–3% of the 2024 PIT count (anchor: 771,480) is roughly 15,000 to 23,000 people per 10% real minimum-wage increase, if the estimate holds. Caption states "one study" and the tier.
3. **The abolished-stock number.** SRO units lost in one city over the period the form was regulated out (anchor: NYC ~175,000 units, 1955 to mid-1990s). Verify from a primary or Furman Center source; if only advocacy tallies exist, use HUD's national framing instead and say so. Caption: "The cheapest legal room, removed by code."

Below the numbers, one sentence: which tier each number belongs to. No further caveat paragraph in the hero; caveats live beside the numbers in their sections.

---

## 5. Section-level requirements

### 5.3 Housing (load-bearing)

Must contain, in this order:

- **Mechanism paragraph** (existing text is fine).
- **The geography evidence**, as a small table: metro or state, homelessness per 10k, median rent, poverty rate, for 6 to 8 places spanning the range (anchors: SF, Seattle, LA, NYC, Boston vs. Detroit, Houston, Charleston WV, Little Rock). All four columns from primary series (HUD PIT 2024 CoC file, Zillow ZORI or HUD FMR, ACS). This table replaces the current prose citation of Colburn & Aldern and is the page's best evidence; give it room.
- **The rules evidence**: Gyourko & Krimmel zoning-tax rows (existing), plus Glaeser & Gyourko 2018 JEP framing, plus the Wharton Residential Land Use Regulatory Index as the standard measure. Keep the NAHB row with its advocacy-source label.
- **The rung-restored evidence** (new, mandatory; this is what makes the argument compelling rather than theoretical):
  - Auckland 2016 Unitary Plan upzoning: construction response and rent effect versus counterfactual (Greenaway-McGrevy & Phillips 2023; anchor: rents roughly 4–5% below trend after several years).
  - Minneapolis 2040 plan and parking-minimum repeal: rent growth versus the rest of Minnesota 2017–2023 (Pew 2024 analysis; anchor: Minneapolis rents about flat while state rents rose ~14%).
  - Houston: minimal zoning, minimum-lot-size reform 1998 and 2013, and its 60%+ decline in homelessness since 2011 alongside Housing First. State plainly that Houston is a joint treatment (cheap supply plus coordinated housing) and cannot separate the two.
  - Tokyo as the international reference for permissive national zoning and flat real rents (anchor only; include if a primary source is found, otherwise omit).
- **The Furman/HUD SRO model, reframed.** Keep the calculation but retitle it "What the outlawed unit looks like." The $780/month and 125-unit figures are the difference between two building formats, and the caption must say the regulatory component is the fraction of that gap that exists because the smaller unit is illegal, which the model does not isolate. It is no longer a hero number. Keep the 2018 date visible.
- **Free-market response** paragraph (existing).

### 5.4 Work (secondary, both sides)

- Keep Hill 2025 as the lead estimate with the people conversion from §4.
- Add the opposing estimates a hostile reader will cite: Cengiz, Dube, Lindner & Zipperer 2019 QJE (bunching estimator; near-zero employment effects up to the studied wage levels) and Dube's 2019 UK review. One row each, tier-labeled, with the honest sentence: the disemployment channel Hill relies on is exactly the effect this literature finds small in aggregate; Hill's argument is that it concentrates on the least employable, which aggregate studies would not detect. That is a testable claim, not a settled one.
- Licensing and entry-barrier row stays as a gap.
- Delete the sentence "Evidence for the broad claim that all marginal work has been outlawed is not established here" and any similar strawman-then-disclaim pattern.

### 5.5 Care (split in two)

- **Economic half:** IMD exclusion, Section 1115 waivers, state-hospital census (existing rows). Add one displacement row with a number: share of jail or ER population with serious mental illness (anchors: roughly 15–20% of jail inmates with SMI per Steadman et al. 2009; verify). Tier: probable.
- **Rights half:** O'Connor v. Donaldson stays. State the tradeoff plainly: the free-market case is for voluntary exchange and against coercion; expanding involuntary commitment is a rights cost that must be argued on its own terms, and this page does not resolve it. Then stop. No further hedging sentences.
- Drop the 1955 "340 beds per 100,000" comparator from the table. If historical context is wanted, one sentence noting the deinstitutionalization series exists and why it is not comparable (different patient population) is enough.

### 5.6 Who is on the bottom rung

Retitle from "The connection between work and care." Keep the three prevalence cards and the definitions table. Replace the three generic sub-headed paragraphs with one paragraph that states the implication the current page avoids:

> If about half of people experiencing homelessness carry a brain-injury history and about a quarter show measurable cognitive impairment, then "a cheap room and a job" is the complete fix for some and not for others. The housing mechanism still governs where homelessness concentrates, because rent determines who falls off the bottom of a local market; but the reform package must include care capacity, or deregulation alone will leave the most impaired share exactly where it found them. This is the strongest argument on the page for treating care as a mechanism at all.

### 5.7 The ledger and the sign inversion

Keep the four-quadrant table, the political-ownership asymmetry paragraph, and the hardening section's sign-inversion argument. These are the page's original contributions and should be the second most polished thing on it. Merge "The seen" and "A different broken window" cards into one short paragraph. Move the "unseen side of each decision" table into the registers.

### 5.8 Objections, answered (new, mandatory)

Eight objections, each: the objection in one sentence in the reader's voice, the best evidence for it, the answer, and the residual the answer does not cover. No objection gets a strawman phrasing.

1. "It's drugs and fentanyl, not rent." Answer: cross-metro variation; overdose rates are high in low-homelessness states (anchor: West Virginia leads the nation in overdose deaths and is near the bottom in homelessness). Residual: drugs affect who within a metro, and unsheltered severity.
2. "SROs vanished because land got valuable, not because of code." Answer: HUD documents both; the test is whether new SROs can be built today under current code, and in most large cities they cannot. Residual: some conversion was market-driven.
3. "Minimum-wage effects are near zero in the best studies." Answer as in §5.4.
4. "Housing First has failed on the West Coast." Answer: distinguish the intervention (housing plus services for high utilizers, RCT evidence from Denver, and Finland's national decline) from the supply constraint (housing first cannot house people into units that do not exist). Anchors: Finland long-term homelessness fell by roughly two-thirds 2008–2023; verify.
5. "Deregulation just builds luxury units." Answer: filtering evidence (Mast 2023 on migration chains; anchor: 100 new market-rate units free up roughly 70 units in below-median-income tracts within a few years).
6. "The costs you list are already priced into property values, so you are double counting." Answer: agreed, and the ledger says which rows overlap; the point is direction and ownership, not a total.
7. "You have no total, so you have no argument." Answer: the argument is about which column the debate ignores, and every sourced row is a lower bound on a category the budget treats as zero.
8. "Camping bans work." Answer: Grants Pass removed a legal constraint; Denver displacement evidence shows local, short-lived, mixed effects; enforcement without shelter moves the cost, and the ledger shows where.

### 5.9 Reform tests

Keep the three cards. Tighten each to: change, what to measure, what to count against it. Add a fourth card: **Care capacity**, separate from commitment, so the reform package matches §5.6.

### 5.10 Evidence registers (condense)

Keep, collapsed: the ledger table, public-budget, public-space, hardening (now merged with §5.7 prose, table only here), avoidance and the commute worksheet, property crime, sanitation, cost-per-person comparison.

Merge: "Violence, both directions" becomes two rows inside the crime register. "Private security substitution" becomes one row inside the ledger table. "Business and tax-base flight" becomes one row inside the ledger table with the SF vacancy figure and the attribution gap; the six-city vacancy table is deleted (it establishes nothing the argument uses).

The commute worksheet stays as is. The sensitivity worksheet must not display a computed dollar range on page load. Seed the public baseline with the Denver participant-year program cost (2021) and leave the external-cost fields blank; render the result only once all four fields have values. The "coincidence of arithmetic" paragraph is deleted.

### 5.11 Accounting mistakes

Trim from 13 rows to the 10 that a reader will actually encounter. Drop "Removing the bench saved money" (now argued in §5.7), "Prevention costs are just the program budget" (same), and "One less expense means one more dollar of social benefit" (fold into the fixed-budget row).

---

## 6. Facts requiring primary-source verification

Every row below must be verified before it ships; if unverifiable, omit the entry.

| Fact | Source to use |
|---|---|
| Per-10k homelessness rates by CoC/state, 2024 | HUD 2024 AHAR Part 1 and CoC PIT file |
| Poverty rates by state/metro | Census ACS 2024 1-year |
| Rent levels by metro | Zillow ZORI or HUD FMR, same year as PIT |
| Overdose death rates by state | CDC WONDER / NCHS provisional 2024 |
| NYC SRO units lost | Furman Center; HUD 2018; NYC Council reports |
| Auckland upzoning rent effect | Greenaway-McGrevy & Phillips, Journal of Urban Economics 2023 |
| Minneapolis rent growth vs Minnesota | Pew Charitable Trusts 2024 |
| Houston minimum-lot-size reforms | Gray & Millsap, or Houston Planning Dept |
| Cengiz et al. 2019 | QJE 134(3) |
| Mast filtering chain | Mast, Journal of Urban Economics 2023 |
| Finland long-term homelessness series | ARA (Housing Finance and Development Centre of Finland) annual report |
| Jail SMI prevalence | Steadman et al. 2009, Psychiatric Services |
| Hill people conversion | HUD 2024 PIT total × 0.02 and × 0.03 |
| Everything already cited on the page | keep existing links; re-check any DOI that was 403 at review (Hill; Kallberg & Shimizu) resolves |

---

## 7. Volatile-facts register

**Rating: SLOW-DRIFT.** Annual updates: HUD PIT (December), ACS (September), NAHB study (irregular), TAC bed census (irregular), AAA driving costs (September), Cushman office vacancy (quarterly, now only one row). Legal: any Supreme Court or CMS action on IMD waivers or camping enforcement. Freshness routine should re-verify the geography table and the people conversion once a year and leave the rest alone unless a cited study is retracted or superseded.

---

## 8. Anti-goals

- No total cost of homelessness, national or local. The page's credibility rests on this.
- No claim that repeal alone ends homelessness. §5.6 forbids it.
- No involuntary-commitment advocacy. The rights question is stated as a tradeoff and left open.
- No strawman-then-disclaim sentences ("evidence for the broad claim that X is not established here" where nobody claimed X).
- No second essay. If a register tempts a full section, it stays a table.
- No visible "Last verified" or `dateModified`.

---

## 9. Style pass (Sonnet, after Opus finishes)

- **Zero em dashes**, glyph or entity. Rewrite with a period, colon or comma. Current count: 11 glyphs.
- **Negation budget:** at most one "X is not Y" construction per section. The current page has dozens ("not a rate," "not proof," "not permission," "not the same as zero"). Replace with what the thing is.
- **Delete the word "plate"** everywhere; use "section."
- **Delete interaction instructions from body prose** ("Hover or focus a row to see…"). Put affordances in `aria-label` or a `<figcaption>` that reads correctly without the interaction.
- **Caveat placement:** one caveat sentence adjacent to the number it qualifies. No standalone caveat paragraphs. No caveat that repeats one already stated in the same section.
- **House voice:** David-voice per global rules; no unverifiable claims; every volatile number dated inline.
- Run the three greps from `cheatsheets-build-qa-checks` memory and `scripts/seo_check.py` before commit.

---

## 10. Design

The existing warm-paper identity, type stack, ledger tables and dark mode stay. Two changes:

- **Signature element: the weighted ladder.** Redraw the current SVG so rung thickness encodes the confidence tier from §1: housing thick and solid, work medium and dashed, care thin with two segments (financing solid, commitment dotted). Label each rung with its tier word. The figure below the lowest rung stays. Test at 375 px; the ladder stacks above the list on mobile. This is also the **og:image** subject, rendered via `scripts/shot.py` with the `data-og-capture` attribute on the hero-plus-ladder block.
- **Hero numbers** get the tier word as a small mono caption, in the same style as the current "measured / estimated / gap" tags, so the legend is learned once.

---

## 11. Definition of done (in addition to README Rule 3 and AGENTS.md)

- The §1 paragraph appears once in the hero and once in section 1 and nowhere else.
- The geography table exists with at least six rows and four sourced columns.
- The rung-restored block cites at least two natural experiments with primary sources.
- Objections section has all eight entries with a residual line each.
- The sensitivity worksheet renders no dollar figure until inputs are complete.
- Word count between 6,000 and 6,800 (measure with tags stripped).
- Em-dash grep returns zero; "plate" grep returns zero; `seo_check.py` passes; `catalog.json` regenerated; all previously existing `id`s still resolve.
- Screenshots at 1440 and 375 px in both themes reviewed; ladder legible at 375.
- `refresh-status.json` untouched; no "Last verified" stamp anywhere.
- Delete this spec file after shipping; note the revision in `docs/seo-progress.md` only if the title changes, since that resets GSC history for the query.
