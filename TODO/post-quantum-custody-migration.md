# Spec: Post-quantum migration for digital asset custody

**Target file:** `post-quantum-custody-migration.html`
**Batch:** [custody-engineering-batch-2026-08.md](custody-engineering-batch-2026-08.md) (sheet 9 of 9, P2).
**Companion to the existing** `post-quantum-cryptography.html`, which stays in `Security & Privacy`
and keeps the general-cryptography treatment. This sheet is the custody-specific sibling and must
not duplicate it — link across for algorithm internals, NIST process history and the general
migration picture, and spend the whole page on the part that is specific to holding digital assets.

## Why this topic

The general post-quantum story is well covered, including on this site. The custody-specific story
is not, and it is different in three ways that matter:

1. **The exposure is asymmetric and mostly already public.** Custody is not a "harvest now, decrypt
   later" problem — there is nothing encrypted to harvest. It is a **"the public key is already on
   the chain, forge later"** problem, and whether that applies to a given holding depends on the
   output type and the spend history, not on anything the holder does from here.
2. **You cannot migrate faster than the chain lets you.** In every other domain, migration is a
   decision the operator makes. Here the operator cannot deploy a post-quantum signature until the
   chain supports verifying one, which turns a security roadmap into a governance-dependency
   problem.
3. **Threshold protocols are the hard case, and this is the point almost nothing states.** The
   whole custody industry moved to threshold signing over the past decade, and the post-quantum
   signature standards do not have mature threshold constructions. The migration path that looks
   obvious — swap the signature scheme inside the MPC protocol — is not available, and the reasons
   are structural rather than a matter of waiting for an implementation.

Together those give the page an argument rather than a summary: **for a custodian, post-quantum
migration is an inventory-and-hygiene problem now and a scheme-replacement problem later, and the
work that pays off today is not the work that gets discussed.** That is a defensible, useful and
genuinely under-written position.

## Targeting

- **Primary query:** `quantum computing bitcoin custody risk`
- **Secondary:** `which bitcoin is quantum vulnerable`, `exposed public key quantum bitcoin`,
  `post quantum signature blockchain`, `threshold post quantum signature`,
  `ml-dsa signature size blockchain`, `taproot quantum vulnerability`,
  `crypto agility custody roadmap`
- **Mode:** research mode, professional, with a fair amount of arriving scepticism (the reader has
  seen a great deal of quantum hype). The page's tone must earn credibility by being *less* alarmed
  than the genre, not more.

## Draft title / H1 / meta

- `<title>`: `Post-Quantum Migration for Crypto Custody: What Actually Breaks` (62 chars — trim to
  ≤ 60 at build, e.g. `Post-Quantum Custody Migration: What Actually Breaks`)
- **H1:** `Post-Quantum Migration for Digital Asset Custody`
- **Meta description (draft):**
  `Which holdings are actually quantum-exposed and why it depends on output type and spend history, what post-quantum signatures cost in blockspace, and why threshold custody is the hardest case.` (190 chars)

## Reader outcome

The reader can classify their own holdings by quantum exposure using output type and spend history,
explain why a threshold-signed wallet cannot simply swap in a post-quantum scheme, state what
migration work is worth doing this year and what is not, and ask a custody vendor the two questions
that actually distinguish a real roadmap from a press release. Acceptance test: given an address
and its transaction history, they can say whether its public key is exposed and what that does and
does not imply.

## Success metric

Goal-2 signal above all: this is the "true expert" artifact, and its value is in being correct and
calm on a topic where most published material is neither. Watch for citation by people arguing
about the subject rather than for search volume. Secondary: it should raise the standing of the
existing `post-quantum-cryptography.html` through internal linking.

## Content approach

Exposure inventory first (concrete, checkable, and the reader's own situation), then cost, then the
threshold problem, then the timeline, then the plan. Lead with what is true and checkable so the
speculative sections are read by someone who already trusts the page.

1. **Quick reference: what breaks and what does not** — the first screen, and the correction to the
   genre's central error. **Signature schemes break; hash functions do not.** Elliptic-curve
   signatures fall to a period-finding quantum algorithm; hash functions lose roughly half their
   effective security to a search speedup, which leaves 256-bit hashes comfortably intact.
   Therefore: mining and hash-based commitments survive, proof-of-work is not the vulnerability,
   and the exposure is entirely on the signing side. Give the one-table version — primitive, role
   in the system, quantum impact, practical consequence — and note the corollary that an unspent
   output protected only by a *hash* of a public key is in a materially better position than one
   that publishes the key.
2. **Exposure inventory: which holdings are actually at risk** — the page's signature element and
   its most useful content, because it is checkable against a real address today. Work through the
   Bitcoin output types in order: outputs that publish a raw public key (permanently exposed, and
   the class that includes a large tranche of the earliest coins); pay-to-public-key-hash that has
   **never been spent from** (the key is behind a hash — this is the protected case); the same
   address **after** a spend, where the signature reveals the key and every remaining balance at
   that address is exposed (which is the concrete, unglamorous reason address reuse is a
   quantum problem and not merely a privacy one); script-hash outputs before and after reveal; and
   Taproot, where the tweaked output key is an actual public key sitting on-chain from the moment
   the output is created — meaning **Taproot outputs are exposed at rest**, an underappreciated
   point that should be stated plainly and carefully.
   Then account-model chains, where the situation is worse and simpler: because a public key is
   recoverable from any signature, **every account that has ever sent a transaction has an exposed
   key**, and only never-used addresses are protected. Then the Ed25519 chains. Close with the
   estimate of how much value sits in exposed-key outputs, stated as a magnitude with its
   methodology and date, or omitted entirely if it cannot be verified — this is exactly the number
   that circulates in wrong forms and it must not be repeated on this page unsourced.
3. **Two attack windows, not one** — the distinction that governs urgency. **Long-range:** an
   exposed public key can be attacked at leisure, for years, with no time pressure; this is the
   real threat and it applies to the outputs identified in §2. **Short-range:** stealing a
   transaction between broadcast and confirmation requires breaking the key within a block
   interval, which is a vastly harder engineering requirement, and it is the scenario most articles
   describe while implying the timeline of the first. State the difference, state which one drives
   policy (the long-range one), and note the consequence: **the defensive action available today is
   moving exposed-key holdings into unexposed outputs, which requires no new cryptography and no
   protocol change.** That is the page's most actionable sentence and it belongs early.
4. **The post-quantum signature standards and what they cost on-chain** — brief on the algorithms
   themselves (link to `post-quantum-cryptography.html` for internals) and detailed on the thing
   that page does not cover: **size**. A table of the standardised lattice and hash-based signature
   schemes plus a compact alternative, with public key size, signature size, and the multiple
   versus an elliptic-curve signature — which runs from roughly an order of magnitude to two orders
   of magnitude. Then translate that into custody economics: transaction weight, the resulting fee
   at a stated fee level, the block-capacity consequence if a meaningful share of transactions
   became post-quantum, and the UTXO-consolidation cost of migrating a large set of outputs. This
   is the section that makes the problem concrete for an operator, because the cost of migrating is
   a budget line and nobody has written it down. Verify every byte count against the published
   standards; these are exactly the numbers that get misquoted.
5. **Why threshold custody is the hard case** — the page's strongest section and its
   differentiator. The argument, in order: threshold signing for the classical schemes is mature
   and deployed (link to sheet 1); threshold constructions for the standardised lattice signature
   are research-grade, and the structural reason is that the scheme's rejection-sampling step is
   awkward to perform inside a multi-party computation without leaking or aborting; the hash-based
   stateless standard is enormous and equally awkward to threshold; and the stateful hash-based
   schemes carry a failure mode that is disqualifying in a distributed setting — **reusing a
   one-time state destroys the key's security, and maintaining that state consistently across n
   independently-operated shares, through crashes, restores from backup and quorum changes, is
   exactly the kind of coordination problem that distributed systems get wrong.** A backup restore
   that rewinds the state is a catastrophic key compromise. Say that clearly; it is the sharpest
   technical point on the page.
   Then the practical near-term paths, compared honestly: hybrid signing where a classical
   threshold signature and a post-quantum signature from a non-threshold key are both required;
   moving the policy and verification logic into a smart-contract or account-abstraction wallet
   where the verification scheme is upgradeable without changing the address (**the strongest
   structural answer available today**, and a genuine argument for that architecture that has
   nothing to do with the reasons usually given for it); and multi-signature over distinct
   post-quantum keys as a coarse substitute for a threshold scheme. Note the standards work in
   progress on threshold cryptography rather than implying nothing is happening.
6. **The chain dependency** — migration is gated by protocol governance, not by the custodian. What
   a chain has to do to support post-quantum signatures (a new output/verification type, activated
   by whatever that chain's upgrade process is), the live proposals for quantum-resistant output
   types on Bitcoin, the account-abstraction path on account-model chains, and the genuinely
   contested question that a custodian should understand because it affects long-horizon holdings:
   **what happens to coins in exposed-key outputs whose owners never move them** — the freeze,
   burn, and do-nothing positions, each with its argument. Present the debate; do not take a side;
   this is a governance question with real disagreement among serious people and the page's
   credibility depends on representing it fairly.
7. **Timelines, stated honestly** — the section that most determines whether a technical reader
   trusts the page. Give the published transition guidance from the standards bodies (the
   deprecate-by and disallow-by dates for classical public-key cryptography) as the *policy*
   timeline, which is a fact. Give the capability timeline as a range with its uncertainty
   acknowledged, sourced to expert-survey work rather than to any single prediction, and say
   plainly that confident single-year predictions in either direction are not credible. Then give
   the reader the tool rather than the answer: the standard planning inequality — *how long your
   assets must stay secure, plus how long your migration takes, versus how long until the
   capability exists* — which converts an unknowable date into a decision you can actually make.
   For custody the first term is unusually long, and that, not any particular forecast, is the
   argument for starting the inventory work now.
8. **The migration plan** — what to do, sequenced, with the near-term items honestly labelled as
   cheap and useful and the far-term ones as blocked on other people. **Now:** a
   cryptographic-asset inventory (which chains, which signature schemes, which key material,
   where, and which are exportable); address hygiene as policy — no reuse, ever, enforced in code
   rather than in a document; sweeping long-held exposed-key outputs into unexposed ones; recording
   the scheme and path metadata that a future migration will need (which is the same discipline
   sheet 8 asks for, for an entirely different reason); and adding two questions to vendor
   diligence — *what is your post-quantum roadmap, and can I export and re-key without you?*
   **Next:** crypto-agility in the internal signing abstraction so the scheme is a parameter rather
   than an assumption; monitoring the chain-level proposals that gate everything else.
   **Later, blocked:** actual scheme replacement. Be explicit that the middle column is where most
   published advice sits and the left column is where the value is.
9. **What not to do** — a short, valuable section given the genre. Do not buy a "quantum-safe"
   product whose claim is unverifiable; do not adopt a non-standardised signature scheme to get
   ahead; do not treat proof-of-work as the vulnerability; do not panic-move holdings in a way that
   creates a real, present operational risk to hedge a speculative future one — the migration
   transaction itself has a failure mode and it is not hypothetical.
10. **Common mistakes** (mandatory) — assuming hash functions are broken; assuming every address is
    equally exposed; assuming a hardware wallet's security model addresses this; treating Taproot
    as equivalent to unspent pay-to-hash outputs; assuming a threshold scheme can swap its
    signature algorithm; planning a migration that the chain cannot execute; ignoring signature
    size in fee and capacity planning; reusing addresses.
11. **Related sheets** footer per the cross-link map.

## Volatile-facts register

**Overall: VOLATILE on timelines and proposals, STABLE on the exposure analysis.**
- **§7 timelines: VOLATILE.** Both the policy dates and the capability estimates move, and this is
  the section a reader will check first for staleness. Date it prominently; re-verify at every
  freshness pass; never state a capability date as a fact.
- **§6 chain proposals: VOLATILE.** Proposals advance, stall and get renumbered. Cite by identifier
  and status with a date, and prefer describing the design question over tracking a specific
  proposal's progress.
- **§4 algorithm parameters: SLOW-DRIFT.** Standardised parameter sets are stable; additional
  standards are still arriving. Annual check.
- **§5 threshold state of the art: SLOW-DRIFT** — this is active research and the "not yet mature"
  claim must be re-checked annually rather than assumed to remain true. If a mature threshold
  construction is standardised, §5's argument changes and the section is rewritten, not patched.
- **§2 exposure inventory and §3 attack windows: STABLE.** These follow from the output types and
  will not change.
- Any figure for value-at-risk in exposed outputs: **VOLATILE**, and per §2, omit rather than
  guess.
Semi-annual freshness target, §5 and §7 as the check targets.

## Index category

`Crypto Custody & Compliance`. (The existing `post-quantum-cryptography.html` stays in
`Security & Privacy` — the split is deliberate and both pages should link across it.)

## Reading conditions

**Desk, sceptical reader, reading to evaluate whether the author knows what they are talking
about.** Consequences: precision over emphasis throughout; no alarm styling; every claim that could
be mistaken for hype carries its citation adjacent to it rather than in a footnote; the honest
uncertainty in §7 is stated in the body text, not hedged in a disclaimer at the bottom. The
exposure table in §2 is the block a reader will check against something they know, so it must be
exactly right. Mobile is a secondary case; the exposure table degrades to per-output-type cards.
Print is not a priority.

## Cross-link map

- **Internal outbound:** `post-quantum-cryptography.html` (the companion — link prominently and
  early, for algorithm internals, the standardisation history and the general migration picture;
  this page should read as its custody-specific continuation), `mpc-wallet-architecture.html`
  (sheet 1 — §5 depends on it entirely), `institutional-crypto-custody.html` (sheet 3 — key
  lifecycle and the inventory discipline §8 asks for),
  `custody-provider-integration.html` (sheet 6 — the vendor diligence questions),
  `bitcoin-self-custody-guide.html` and `bitcoin-wallet.html` (address hygiene at individual
  scale), `quantum-physics-vs-quantum-bullshit.html` (the hype-correction adjacency — a genuinely
  apt link and worth making explicit in §9).
- **Reciprocal inbound:** a line from `post-quantum-cryptography.html` pointing here for the
  custody case (**this is the most important reciprocal link in the batch** — it connects the new
  cluster to an established page), plus one from sheet 1's §5 and one from
  `quantum-physics-vs-quantum-bullshit.html`.
- **External outbound:** the NIST post-quantum standards by their FIPS numbers, the NIST migration
  guidance document, the NIST threshold-cryptography project, the relevant chain improvement
  proposals by identifier, and published expert-survey work for §7's capability estimates. Primary
  documents throughout; **no vendor "quantum-safe" marketing as a source for anything**, which is
  also the point of §9.

## og:image / shareable artifact

The **exposure inventory** at 1200×630 — output type down the side, and across the top: is the
public key on chain, when does it become exposed, and the verdict on the shared semantic scale.
It is the page's one genuinely novel and checkable object, and it is the thing most likely to be
screenshotted into an argument. The §1 "signatures break, hashes do not" table is the second
artifact.

## Jurisdiction scope

Global and technical. The only jurisdictional content is §7's policy timelines, which are drawn
from US federal standards guidance and should be labelled as such in one line, with a note that
other national schemes publish their own transition dates. No legal content.

## Density targets

Primitive-impact table ≥ 6 primitives. Exposure inventory ≥ 8 output/account types × 4 columns,
covering both UTXO and account models and both curve families. Signature-size table ≥ 5 schemes ×
4 columns plus the on-chain cost translation worked to a real fee figure at a stated fee level.
Threshold section ≥ 3 scheme families assessed plus ≥ 3 practical paths compared. Chain-dependency
section ≥ 3 proposals or approaches plus the 3 positions in the frozen-coins debate. Migration plan
≥ 6 "now" items, ≥ 2 "next", ≥ 1 "blocked". What-not-to-do ≥ 4. Common mistakes ≥ 8.

## Research sources (verify against these, per Rule 1)

The NIST post-quantum standards themselves for every parameter and byte count — read the FIPS
documents, do not carry a size from memory or from a blog. NIST's transition guidance for the
policy timeline, cited by document number with its status. The NIST multi-party threshold
cryptography project materials for §5's state of the art, plus current academic work on threshold
lattice signatures — and if that literature has moved past "research-grade", §5 must say so. Chain
improvement proposals read in their own repositories, cited by identifier and current status.
Published expert-survey work for capability estimates in §7, cited with its date and sample.
Bitcoin developer documentation for output-type semantics in §2, and the account-model chains' own
documentation for key-recovery behaviour. **Verify the existing** `post-quantum-cryptography.html`
**before linking to it** — if it has drifted, note the discrepancy in the build report rather than
propagating it.

## Visual design

**Identity: the batch register, at its most restrained.** This is the sheet most at risk of reading
as hype, so the design does the opposite: no dramatic colour, no countdown motifs, no quantum
imagery of any kind. Plain tables, generous whitespace, citations set close to their claims. The
shared semantic scale is used only in the exposure inventory, where green = key not on chain,
amber = exposed on spend, red = exposed at rest — and that is the one place on the page where
colour carries an argument, so it should be the only place colour appears at all.

**Signature element: the exposure inventory table**, built as a first-class object rather than an
ordinary table: output type, an inline miniature diagram of what that output actually publishes
(the key, or a hash of it), the moment of exposure on a small timeline, and the verdict. The
miniature diagrams are what make it more than a list and what make the claim checkable — a reader
should be able to see, not just read, why an unspent pay-to-hash output is in a different position
from a Taproot output. Inline SVG, drawn for 375 px first, with `<title>`/`<desc>` and the same
information in the adjacent text.

No JavaScript. No animation.
