# Spec: Crypto compliance as architecture — KYT, Travel Rule, sanctions, IVMS101

**Target file:** `crypto-compliance-architecture.html`
**Batch:** [custody-engineering-batch-2026-08.md](custody-engineering-batch-2026-08.md) (sheet 4 of 9, P1).
Build after sheet 3 — this page is written as the compliance overlay on sheet 3's policy engine and
sheet 2's pipeline, and it should reference both rather than restating them.

## Why this topic

Every compliance page on this subject is a checklist written for a compliance officer. The engineer
who has to *build* it gets nothing, and the resulting systems are wrong in a specific, predictable
way: **screening runs too late.** Screening after broadcast is not a control, it is a report — the
transaction is irreversible and the only remaining action is a filing. Yet late screening is
extremely common, because a checklist says "screen transactions" and never says where in the call
graph.

The framing that makes this page different: **compliance controls are pipeline placement decisions,
not a checklist.** Every requirement in this domain resolves to a question about *where in the
request path* a gate sits and *what it blocks*. Screen the destination before signing, not after
broadcast. Screen the deposit before crediting, not after the customer withdraws. Rescreen on list
update, not only at onboarding. Put that spine through the page and the checklist content becomes
architecture.

The second gap is IVMS101. It is the data model the entire Travel Rule runs on, it is genuinely
fiddly (nested types, controlled vocabularies for identifier types, character-set constraints),
and there is no good public field reference with a real worked payload. That block alone justifies
the page.

## Targeting

- **Primary query:** `ivms101 data model`
- **Secondary:** `crypto travel rule threshold by country`, `kyt transaction monitoring crypto`,
  `ofac sanctions screening crypto addresses`, `travel rule unhosted wallet`, `trisa vs trp`,
  `fatf recommendation 16 crypto`, `mica travel rule requirements`
- **Mode:** operational, mid-build. The IVMS101 section will be entered directly and repeatedly by
  people mapping their own customer records into it, so field-level anchors are required.

## Draft title / H1 / meta

- `<title>`: `Crypto Compliance Architecture: KYT, Travel Rule, IVMS101` (56 chars)
- **H1:** `Compliance as Architecture: Where the Screening Gates Actually Go`
- **Meta description (draft):**
  `Screening placement in the transaction pipeline, KYT vendor exposure models, sanctions rescreening, per-jurisdiction Travel Rule thresholds, and an IVMS101 field reference with a worked payload.` (191 chars)

## Reader outcome

The reader can place every compliance gate at the correct point in a deposit and withdrawal
pipeline and say what each one blocks; map a customer record into a valid IVMS101 payload; state
the Travel Rule threshold and the unhosted-wallet treatment for the jurisdictions they operate in;
and execute the runbook when a sanctioned-source deposit lands. Acceptance test: given an
architecture diagram, they can point at the wrong place a screening call was made and say why.

## Success metric

Deep links to the IVMS101 field reference and the threshold table from implementation work.
Secondary: the pipeline-placement diagram being reused in design discussions. Not a traffic page.

## Content approach

The pipeline is the organising principle. Every subsequent section answers "what does this gate
check, and what does it do on a hit."

1. **Quick reference: the gate map** — the deposit path and the withdrawal path drawn end to end
   with every compliance gate marked, its input, its blocking behaviour, and the consequence of
   putting it one step later. Signature element, and the page's whole thesis in one image.
   Explicit callout: the gate that must precede **signing**, not broadcast, and why the difference
   is the entire control.
2. **The placement rules** — stated as rules before any vendor or regulation is named:
   screen before irreversibility; screen before crediting, not before withdrawing; rescreen on
   list change, because a clean address today is a hit tomorrow and the exposure is retroactive;
   fail closed on screening-provider outage (and the operational cost of that decision, honestly
   stated — this is the tradeoff that gets argued in every organisation); never let a screening
   result be advisory to an automated path.
3. **KYT and transaction monitoring** — what these systems actually compute. Address attribution
   and clustering; direct versus indirect exposure and the hop-depth parameter (with the point
   that indirect exposure at sufficient depth converges on everything, so depth is a policy
   choice, not a fact); category taxonomies (darknet, mixer, sanctioned entity, ransomware, high-
   risk exchange, gambling, scam) and the fact that they are **vendor-specific and not
   interchangeable**; risk-scoring models and their opacity; the false-positive burden and how
   alert volume scales with thresholds. A vendor table — the major screening and analytics
   providers — with coverage, model type and integration surface, sourced from public
   documentation, **not ranked** (see the batch rule). Then the operational problems nobody
   documents: two vendors disagreeing on the same address, the appeal path when an attribution is
   wrong, and the design decision of whether a score gates automatically or opens a case.
4. **Sanctions screening** — distinct from KYT and often wrongly merged with it. The OFAC SDN list
   including its digital-currency address identifiers; EU, UK and UN lists; the difference between
   screening a *person* at onboarding and screening an *address* at transaction time; name
   matching and its fuzzy-matching failure modes; rescreening cadence on list publication; and
   the **retroactive hit** problem — you screened clean, the list changed, you now hold blocked
   property. Include the well-documented case of a mixing-protocol designation that was later
   challenged in court and subsequently delisted, as the worked example of why a hard-coded
   address list in application code is an architectural defect: the list is an input, it changes
   in both directions, and it must be sourced live. Verify the full procedural history of that
   example carefully before writing it; it is the section most likely to be recalled wrong.
5. **The blocked-property runbook** — a numbered procedure for when a screening gate fires on real
   funds: freeze and segregate; do not return the funds (returning them is itself a prohibited
   transaction); the reporting obligation and its deadline; the annual report; the suspicious-
   activity filing and its separate timeline; the prohibition on tipping off; and record
   retention. Every deadline verified against the regulation text and cited. This is a printable
   block.
6. **Travel Rule** — the requirement, then the implementation. FATF Recommendation 16 and the
   VASP-to-VASP obligation; the **per-jurisdiction threshold table**, which is the section's
   working artifact: jurisdiction, threshold amount and currency, whether there is a de minimis at
   all, what data is required above and below it, the unhosted-wallet treatment, and the in-force
   date. Cover at minimum the US, EU, UK, Switzerland, Singapore, Japan, Canada, Australia, Hong
   Kong and UAE. Flag the two structural traps: the EU regime's absence of a de minimis threshold
   for crypto transfers, and the fact that the originator's and beneficiary's jurisdictions can
   impose different requirements on the same transfer. Then the sunrise problem — counterparties
   not yet subject to the rule — and the unhosted-wallet ownership-proof approaches with an honest
   assessment of each (message signing, micro-deposit, declaration) including which ones prove
   control rather than ownership.
7. **IVMS101 field reference** — the page's deep artifact. The data model as a structured table:
   `originator` / `beneficiary` / `originatingVASP` / `beneficiaryVASP` / `transferPath` /
   `payloadMetadata`; within each, `naturalPerson` versus `legalPerson` and the fields that differ;
   `nameIdentifier` with its identifier-type vocabulary; `geographicAddress` with its address-type
   vocabulary; `nationalIdentification` with its identifier-type vocabulary and the
   registration-authority field; `dateAndPlaceOfBirth`; `customerIdentification`; `accountNumber`.
   For every field: cardinality, type, constraint, controlled vocabulary values, and the mistake
   people make with it. Then **a complete, valid worked payload** for a realistic natural-person-
   to-legal-person transfer, in a copyable code block, annotated — this is the single most useful
   block on the page and the reason it will be linked. Close with the encoding and character-set
   constraints and the local-versus-Latin name representation problem, which is the most common
   source of rejected payloads.
   Verify the field names, the vocabulary code values and the current version of the standard
   directly against the published data model; do **not** ship any code value from this spec
   unverified, and state the version and date above the table.
8. **Travel Rule protocols and interoperability** — TRISA, TRP/OpenVASP and the commercial
   networks, compared on: transport, discovery mechanism (how you find your counterparty and
   verify they are who they claim), identity/certificate model, IVMS101 as the shared payload,
   and the interoperability position. The real architectural point: **the payload is standardised,
   the network is not**, so a VASP either joins several networks or uses a broker, and that
   decision belongs in the design, not in procurement.
9. **The regulatory frame, briefly** — the GENIUS Act's obligations on permitted stablecoin
   issuers including the technical freeze/seize capability requirement (hand-off to sheet 5), MiCA
   CASP authorisation and its phase-in dates, and the EU AML package's forthcoming restrictions on
   anonymity-enhancing assets and anonymous accounts. One short paragraph each, every date
   verified and inline, every claim linked to the primary text. **Not a legal guide** — the job is
   to tell an engineer which obligations become system requirements, then stop.
10. **Data protection tension** — one honest section that most compliance content skips: the
    Travel Rule requires transmitting personal data to a counterparty who may be in another
    jurisdiction, and GDPR requires a lawful basis, minimisation and a transfer mechanism for
    exactly that. Name the tension, name the mechanisms in use, and do not pretend it is settled.
11. **Common mistakes** (mandatory) — screening after broadcast; screening the customer but not
    the counterparty address; a hard-coded sanctions list in application code; no rescreening on
    list update; treating a KYT risk score as a fact rather than a vendor opinion; returning
    blocked funds; mapping a full name into a single IVMS101 name field; assuming a de minimis
    threshold that does not exist in the counterparty's jurisdiction; sending IVMS101 data before
    verifying the counterparty VASP's identity; storing screening results without the list version
    that produced them.
12. **Related sheets** footer per the cross-link map.

## Volatile-facts register

**Overall: VOLATILE — with sheet 2, the most perishable page in the batch.**
- **§6 threshold table: VOLATILE.** Thresholds, in-force dates and unhosted-wallet treatment
  change per jurisdiction on their own schedules. Re-verify every row at each freshness pass; a
  visible per-row "as of" date, not a single page-level date, because rows will drift
  independently.
- **§4 sanctions and §9 regulatory frame: VOLATILE.** Designations, delistings and litigation
  outcomes change month to month. Date every claim inline.
- **§7 IVMS101: SLOW-DRIFT.** The model is versioned and has been revised; the field structure is
  stable enough to be useful but the version must be stated. Annual check against the published
  model.
- **§3 vendor table: SLOW-DRIFT.** Products and coverage change; keep entries thin and dated.
- **§2 placement rules, §5 runbook structure, §8 interoperability problem, §10 tension: STABLE.**
Named as a quarterly freshness target — the shortest interval in the batch — with §6 and §4 as the
check targets.

## Index category

`Crypto Custody & Compliance`.

## Reading conditions

**Desk, mid-implementation, mapping a schema or writing a design doc.** The IVMS101 payload will be
copied. Consequences: code blocks must be selectable text with a copy affordance, never images,
and must be correct JSON that validates. The threshold table needs per-row anchors and per-row
dates. The blocked-property runbook is the one block that will be printed and put in a folder —
give it a clean print rendering with numbered steps and deadline callouts. Mobile: the threshold
table degrades to per-jurisdiction cards; the IVMS101 reference stays a table with a scroll wrapper
because a field reference is useless when reflowed.

## Cross-link map

- **Internal outbound:** `institutional-crypto-custody.html` (sheet 3 — the policy engine these
  gates run inside), `blockchain-deposits-withdrawals.html` (sheet 2 — the pipeline being gated,
  and the deposit-hazard hand-off), `stablecoin-payment-infrastructure.html` (sheet 5 — issuer
  freeze capability and the GENIUS Act), `crypto-exchange-architecture.html` (sheet 7),
  `bitcoin-exchanges-cards.html`.
- **Reciprocal inbound:** one line from sheet 2's deposit-hazards section and one from sheet 3's
  policy-engine section, both pointing at the gate map.
- **External outbound:** primary texts only — FATF Recommendation 16 and its interpretive note,
  the OFAC sanctions programme pages and the SDN list documentation, the FinCEN rule text, the EU
  Transfer of Funds Regulation and MiCA, the published IVMS101 data model, and each Travel Rule
  protocol's own specification. Vendor documentation only for claims about that vendor's product.

## og:image / shareable artifact

The **gate map** at 1200×630 — the deposit and withdrawal paths with the gates marked and the
"before signing, not after broadcast" boundary highlighted. It carries the page's thesis in one
image. The IVMS101 worked payload is the screenshot-this block but is unreadable at card size.

## Jurisdiction scope

**Explicitly multi-jurisdictional, and that is the point of §6.** Declare in one line at the top of
the regulatory sections: the engineering content is universal; the thresholds and obligations are
per-jurisdiction and are tabulated rather than narrated; nothing on the page is legal advice and
the primary texts are linked for every claim. One disclaimer, placed once, per README Rule 4 — not
repeated per section.

## Density targets

Gate map ≥ 8 gates across two paths. Placement rules ≥ 5. KYT vendor table ≥ 5 providers × 4
attributes. Sanctions section ≥ 4 list regimes plus 1 fully worked designation/delisting example.
Blocked-property runbook ≥ 8 numbered steps with deadlines. Threshold table ≥ 10 jurisdictions × 6
columns. IVMS101 reference ≥ 25 fields with cardinality, type and constraint, plus ≥ 3 controlled
vocabularies enumerated in full, plus 1 complete valid payload. Protocol comparison ≥ 4 protocols
× 5 columns. Common mistakes ≥ 10.

## Research sources (verify against these, per Rule 1)

FATF Recommendation 16, its interpretive note and the FATF targeted-update reports on virtual
assets. The published IVMS101 data model from its maintaining body — read the schema itself, and
do not carry any field name or code value from this spec unverified. OFAC's own sanctions
programme and SDN documentation, plus the court record for the designation example in §4. FinCEN
rule text at the CFR citation. EU Regulation 2023/1113 (transfers of funds) and Regulation
2023/1114 (MiCA), read directly. National regulator publications for each row of the threshold
table — the regulator's own page, never a vendor's summary of it. TRISA and TRP specifications
from their own repositories. GENIUS Act text for §9.

Experience source, not a citable source: `Paytech-Labs/paytech-platform` implements KYC
verification through a vendor webhook in the customer onboarding path — a concrete instance of
the placement question in §1 and §2. Use it to sanity-check where the gates actually sit in a
real request path. Per the batch constraint, nothing proprietary appears on the page.

## Visual design

**Identity: the batch register, in its most schematic form** — this page is mostly flow and
structure, so it leans on diagrams and field tables rather than the prose blocks of sheets 1 and 3.
Shared semantic scale applied to gate outcomes (green = pass, amber = manual review/case, red =
block/freeze), and applied consistently in the threshold table to mark "no de minimis" as the
attention state.

**Signature element: the gate map.** One wide inline SVG: two horizontal lanes (deposit, withdrawal)
running left to right through the same system, with each compliance gate drawn as a labelled valve
on the lane, the irreversibility boundary drawn as a heavy vertical rule, and every gate that must
sit left of that boundary visually distinguished from the ones that may sit right of it. Annotate
the one gate whose misplacement is the page's central error. Each valve links to its section. This
must be drawn for 375 px first — on narrow viewports the lanes stack and run vertically, with the
irreversibility boundary as a horizontal rule; it must not become a shrunken wide diagram.

The IVMS101 payload block gets real syntax highlighting done with static markup (no highlighting
library, no JavaScript) and must validate as JSON. No JavaScript anywhere on the page.
