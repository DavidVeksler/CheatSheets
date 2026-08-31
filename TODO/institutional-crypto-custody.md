# Spec: Institutional custody architecture — hot/warm/cold, policy engines, dual control

**Target file:** `institutional-crypto-custody.html`
**Batch:** [custody-engineering-batch-2026-08.md](custody-engineering-batch-2026-08.md) (sheet 3 of 9, **P0**).
**Pair:** build after [mpc-wallet-architecture.md](mpc-wallet-architecture.md); this page is where
sheet 1's "what MPC does not protect" section lands, and it should be written as the answer to it.

## Why this topic

Custody writing is either marketing ("bank-grade, insured, multi-layered") or standards text (the
control list without the engineering). The missing artifact is the one an engineer or an assessor
actually needs: **the architecture, with the numbers, mapped control by control to the standard
they will be assessed against.**

CCSS is the natural spine because it is the only crypto-specific control standard with a public,
levelled structure, and because a control-by-control mapping is a genuinely reusable working
document rather than an essay. That mapping — every aspect, what Level I/II/III each require, and
the concrete architectural decision that satisfies it — is the page, and it does not exist
publicly in usable form.

The second differentiator is the float math. Every custody page says "keep most funds in cold
storage." None of them show the arithmetic that sets the hot-wallet target: it is an inventory
problem with a known shape (a base-stock policy against a withdrawal demand distribution), the
cost of being wrong in one direction is a delayed withdrawal and in the other is a larger loss
given a hot-wallet compromise, and it is entirely computable. Show the computation with a worked
example that arrives at a real dollar number.

## Targeting

- **Primary query:** `institutional crypto custody architecture`
- **Secondary:** `ccss level 3 requirements`, `hot warm cold wallet architecture`,
  `crypto key ceremony procedure`, `transaction policy engine crypto`, `dual control crypto custody`,
  `hot wallet float calculation`, `qualified custodian crypto`
- **Mode:** research mode, professional, with a real deliverable in hand — an assessment, a design
  review, or a board memo. The CCSS mapping will be entered at directly from a search for a
  specific control, so every aspect needs its own anchor.

## Draft title / H1 / meta

- `<title>`: `Institutional Crypto Custody: Tiering, Policy Engines, CCSS` (58 chars)
- **H1:** `Institutional Custody Architecture: Hot, Warm, Cold, and the Controls That Hold Them Together`
- **Meta description (draft):**
  `Custody tiering with the float arithmetic behind it, approval quorums, velocity limits, time-locked whitelists, key ceremony and DR procedure, mapped control by control to CCSS Levels I, II and III.` (196 chars)

## Reader outcome

The reader can size the hot tier from their own withdrawal distribution and defend the number;
specify a policy engine's rule set; run or audit a key ceremony from the written procedure; and
walk a CCSS aspect from requirement to the specific architectural control that satisfies it at
each level. Acceptance test: they can take an existing custody design and produce a gap list
against Level II.

## Success metric

Cited in assessment and design work; linked from compliance and security-engineering discussions.
The CCSS mapping table getting deep-linked is the specific signal. Print events matter unusually
much here — the ceremony script and the mapping are working documents.

## Content approach

Architecture first, then controls, then the standard mapping that ties them together. The mapping
comes last deliberately: it is a lookup table that only makes sense once the architecture it maps
to has been described.

1. **Quick reference: the tier card** — the three (or four) tiers on one screen with, per tier:
   what fraction of assets, what signing latency, what approval quorum, what key material and
   where, what network exposure, what it is *for*, and the loss it is designed to bound. Signature
   element. A reader who only sees this block should still leave with the model.
2. **Tiering and float math** — the section with the arithmetic. Define the tiers precisely
   (hot = automated signing, online; warm = human-in-the-loop, network-connected but
   policy-gated; cold = air-gapped, ceremony to move; deep cold = geographically distributed,
   multi-day retrieval). Then the sizing:
   - Model withdrawal demand: mean, variance, and the fat right tail that actually sets the number.
   - Target hot balance to cover demand over the cold-to-hot replenishment lead time at a chosen
     service level, with the (s, S) reorder structure named for what it is.
   - The cost function on both sides: expected loss from hot compromise versus the operational and
     reputational cost of a delayed withdrawal, plus the per-pull cost of a cold retrieval.
   - **A fully worked example** that arrives at a real dollar figure for a stated volume profile,
     per README Rule 3 — no "and so on".
   - Sweep-up thresholds and the reverse flow; per-asset rather than per-portfolio targets;
     why the correct hot fraction differs by an order of magnitude between a payments processor
     and a long-horizon custodian.
3. **The policy engine** — the control plane that sheet 1 identified as MPC's blind spot. Rule
   anatomy (subject, source, destination, asset, amount, time, action), ordered first-match
   evaluation and why rule order is a security property, and then each control in turn with its
   real parameters and its bypass: approval quorums tiered by amount; velocity limits over rolling
   windows (and the structuring attack that defeats a naive one); destination allowlists with a
   mandatory **time lock on additions** (the single highest-value control on the page — an
   attacker with full API access still waits 24–48 hours in public view); per-asset and
   per-destination limits; travel-rule and screening gates as policy conditions (hand-off to
   sheet 4); break-glass and its own dual control; and the meta-control that most deployments
   forget — **changing the policy must itself require a quorum, or the policy is decorative.**
4. **Dual control and separation of duties** — the human layer, stated as roles and prohibited
   combinations rather than platitudes. Initiator ≠ approver; approver ≠ policy administrator;
   key holder ≠ policy administrator; nobody holds a quorum's worth of anything. The collusion
   floor as an explicit number. Out-of-band verification for destination changes. Vacation/
   rotation coverage without weakening the floor, and the specific way that gets weakened in
   practice (temporary approvals that never get revoked).
5. **Key ceremony** — a written procedure, not a description. Participants and roles (ceremony
   administrator, key holders, independent witness, auditor, videographer); pre-ceremony
   preparation and the read-through rehearsal; the room (no network, no phones, recorded);
   entropy sourcing and verification; device provenance and tamper-evident packaging; the
   generation itself; **address verification before any funds move** (the step whose omission has
   destroyed real ceremonies); backup material creation, sealing, and geographic distribution;
   the signed attestation and the artifacts retained. Then the ceremonies people forget to plan:
   quorum change, key-holder departure, and the annual restore drill. Present as a numbered,
   printable script with a checklist column.
6. **Disaster recovery and business continuity** — key-holder unavailability and reconstitution;
   loss of a facility; loss of the vendor (the exit-package question from sheet 1, made concrete);
   RTO and RPO for *signing* as distinct from for the application; the tested-restore requirement
   and the cadence; and the honest observation that the most common custody disaster is not a
   breach, it is an unrehearsed recovery discovering that a backup was never valid.
7. **CCSS control mapping** — the page's signature artifact and the reason it exists. A table with
   one row per CCSS aspect across both domains — key/seed generation, wallet creation, key
   storage, key usage, key compromise policy, keyholder grant/revoke, security tests and audits,
   data sanitisation, proof of reserve, and audit logs — and columns for what Level I, Level II
   and Level III each require, plus a fourth column: **the specific architectural control on this
   page that satisfies it**, linked to the relevant section anchor. That last column is what makes
   this a working document rather than a restatement of the standard.
   **Verification is critical here:** CCSS has been restructured, and the aspect numbering, level
   definitions and the certification body's role have all changed across versions. Verify the
   current version's structure directly from the standard before writing a single row, state the
   version and date visibly above the table, and do not paraphrase requirement text in a way that
   could be mistaken for the normative wording — describe, cite, and link.
8. **The wider assurance landscape** — one compact table so the reader can place CCSS: SOC 2
   Type II (what it does and does not say about key management), ISO 27001, penetration testing
   cadence, and the regulatory regimes that impose custody requirements directly — the New York
   DFS virtual currency regime, the SEC qualified-custodian question for advisers, state trust
   charters and federal charters, and MiCA's segregation and safekeeping obligations. One or two
   lines each, all dated, all linked to the primary text. **This section must not become a legal
   guide** — its job is to tell an engineer which document to go read, then stop.
9. **Proof of reserves and asset verification** — brief here, because sheet 7 owns it. What a
   custodian can attest, why proof of liabilities is the hard half, and a link.
10. **Insurance** — what crime and specie policies actually cover, the hot/cold coverage split,
    sub-limits, the difference between the custodian's policy and the client's exposure, and the
    "insured up to $X" claim's usual meaning. Short, factual, no vendor names.
11. **Common mistakes** (mandatory) — a hot wallet sized by intuition; whitelists without a time
    lock; velocity limits that reset on a boundary an attacker can wait for; a policy engine an
    administrator can silently edit; a ceremony with no independent witness; backups never
    restore-tested; cold storage whose retrieval procedure exists only in one person's head; dual
    control satisfied by two accounts belonging to one person; treating an assessment level as a
    security outcome.
12. **Related sheets** footer per the cross-link map.

## Volatile-facts register

**Overall: SLOW-DRIFT, with two VOLATILE sections.**
- **§7 CCSS mapping: VOLATILE.** Versioned standard under active revision; aspect numbering and
  level requirements have changed and will again. Re-verify at every freshness pass, and carry a
  visible version + date line. If the standard has moved, the whole table is re-derived, not
  patched.
- **§8 regulatory landscape: VOLATILE.** The qualified-custodian rules, MiCA implementation and
  state/federal charter positions all move. Keep the entries to one line each precisely so that
  updating them is cheap; date each.
- Float math, policy-engine design, dual control, ceremony procedure, DR: **STABLE.** These are
  operations-research and security-engineering fundamentals.
- Insurance market terms: SLOW-DRIFT, and stated generically enough not to rot.
Named as a semi-annual freshness target, with §7 as the primary check.

## Index category

`Crypto Custody & Compliance`.

## Reading conditions

**Desk, working session, likely with a spreadsheet or an assessment template open alongside.** The
reader is producing a deliverable and taking pieces of this page into it. Consequences: the
ceremony script and the CCSS mapping must **print cleanly on their own** — a deliberate print
stylesheet is required for this page (the ceremony script as a numbered checklist with tick boxes
and a signature block; the mapping as a landscape table), which puts it in the same category as
the celestial and nuclear sheets. On screen, the mapping table needs sticky headers and per-row
anchors. Mobile is a low-priority read case here but must not be broken: the mapping degrades to
per-aspect cards.

## Cross-link map

- **Internal outbound:** `mpc-wallet-architecture.html` (sheet 1 — the signing primitive this
  wraps, and the source of §3's framing), `crypto-compliance-architecture.html` (sheet 4 —
  screening as a policy-engine gate), `custody-provider-integration.html` (sheet 6 — buying this
  instead of building it), `crypto-exchange-architecture.html` (sheet 7 — proof of reserves),
  `blockchain-deposits-withdrawals.html` (sheet 2 — the withdrawal pipeline the policy engine
  gates), `bitcoin-self-custody-guide.html` (the individual-scale analogue).
- **Reciprocal inbound:** one line from sheet 1's §8 and one from `bitcoin-self-custody-guide.html`
  ("what the institutional version of this looks like").
- **External outbound:** the CCSS standard itself, NYDFS regulation text, MiCA text, SEC rule
  text, NIST SP 800-57 for key-management lifecycle vocabulary. Primary documents only.

## og:image / shareable artifact

The **tier card** from §1 at 1200×630 — four tiers, with the fraction, latency, quorum and key
location per tier, in the semantic colour scale. It is the page's one-glance idea. The CCSS
mapping is the deep artifact but is unreadable at social-card size; it is the screenshot-this
block, not the og:image.

## Jurisdiction scope

**Primarily US, explicitly stated once**, with the EU treated in §8 at one-line depth and the
engineering content (tiers, float, policy, ceremony, DR) being jurisdiction-neutral throughout.
State the scope in a single line at the top of §8 rather than hedging per sentence, per README
Rule 4. CCSS itself is jurisdiction-neutral, which is worth one sentence — it is part of why the
mapping is the durable half of the page.

## Density targets

Tier card 4 tiers × 7 attributes. Float section: ≥ 1 fully worked example ending in a real number,
plus a sensitivity table of ≥ 4 scenarios. Policy controls ≥ 8, each with parameters and its
bypass. Ceremony script ≥ 20 numbered steps with a checklist column. DR scenarios ≥ 6.
CCSS mapping: every aspect in the current standard, no omissions, × 4 columns. Assurance landscape
≥ 6 regimes. Common mistakes ≥ 9.

## Research sources (verify against these, per Rule 1)

The CCSS standard as published by its steering body — read the current version directly; do not
reconstruct the aspect list from memory or from secondary summaries, and do not carry over the
numbering in this spec without checking it. NYDFS 23 NYCRR Part 200 and the associated guidance;
the SEC custody/safeguarding rule text and its current status; MiCA (Regulation 2023/1114) Title V
for CASP safekeeping obligations; AICPA SOC 2 trust services criteria; ISO 27001; NIST SP 800-57
Part 1 for key lifecycle terminology and SP 800-34 for contingency planning structure. For float
math, standard inventory-theory treatment of base-stock policies — cite the method, not a crypto
blog.

## Visual design

**Identity: the batch register at its most document-like** — this is the sheet that most resembles
an audit workpaper, and it should lean into that. Warm paper ground in light mode, ruled tables,
a title-block header on the ceremony script, and the shared semantic scale used on the CCSS
mapping (green = satisfied by the described architecture, amber = requires an explicit
organisational decision, red = commonly missing in practice). Monospace for every control
identifier and parameter.

**Signature element: the tier diagram with the policy gate drawn in.** One inline SVG showing the
four tiers as concentric or stacked bands with the value fraction and latency labelled, and — the
part that makes it more than a stock diagram — the **withdrawal path drawn crossing every gate**:
request, screening, policy evaluation, quorum approval, time-lock hold, signing, broadcast. Each
gate on the path is a link to its section. This is the page's map and its most reusable image.
Draw it at 375 px first; on narrow viewports the path runs vertically with the tiers as a legend.

Print stylesheet is **mandatory** (see reading conditions). No JavaScript; the mapping table is a
plain table with sticky headers via CSS only.
