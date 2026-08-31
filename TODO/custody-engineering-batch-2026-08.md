# Batch: Digital-asset custody engineering — 2026-08 (9 specs)

Specced 2026-08-31. A nine-sheet cluster covering how institutional crypto custody is actually
built: threshold signing, chain settlement, custody tiering, compliance placement, stablecoin
rails, custody-vendor integration, exchange internals, key-loss forensics, and post-quantum
migration.

| # | Spec | Target file | Shape | Priority |
|---|---|---|---|---|
| 1 | [mpc-wallet-architecture.md](mpc-wallet-architecture.md) | `mpc-wallet-architecture.html` | Architecture reference + comparison matrix | **P0 — flagship** |
| 2 | [blockchain-deposits-withdrawals.md](blockchain-deposits-withdrawals.md) | `blockchain-deposits-withdrawals.html` | Dense numeric table (per-chain finality) | **P0 — most differentiating** |
| 3 | [institutional-crypto-custody.md](institutional-crypto-custody.md) | `institutional-crypto-custody.html` | Control-mapping reference | **P0** |
| 4 | [crypto-compliance-architecture.md](crypto-compliance-architecture.md) | `crypto-compliance-architecture.html` | Schema + threshold reference | P1 |
| 5 | [stablecoin-payment-infrastructure.md](stablecoin-payment-infrastructure.md) | `stablecoin-payment-infrastructure.html` | Comparison tables + flow diagrams | P1 |
| 6 | [custody-provider-integration.md](custody-provider-integration.md) | `custody-provider-integration.html` | API/integration reference | P1 |
| 7 | [crypto-exchange-architecture.md](crypto-exchange-architecture.md) | `crypto-exchange-architecture.html` | Architecture reference | P2 |
| 8 | [wallet-recovery-forensics.md](wallet-recovery-forensics.md) | `wallet-recovery-forensics.html` | Field diagnostics + search-space math | P2 |
| 9 | [post-quantum-custody-migration.md](post-quantum-custody-migration.md) | `post-quantum-custody-migration.html` | Exposure inventory + timeline | P2 |

Build order is the priority column. 1, 2 and 3 are the cluster's spine; each of the others
depends on at least one of them for a cross-link and reads thinner if built first.

---

## Rule 0 disposition — read this before writing any of these pages

`README.md` Rule 0 rejects "broad informational topics" for the **goal-3 (agentic-automation
case study / traffic)** purpose. This batch is deliberately built for **goal 2 (professional
brand)** and **goal 1 (personal study)**, and per the site-goals rule in `seo-planning.md` it is
judged by those goals' criteria — depth, correctness, and whether a practitioner in the field
would cite it — **not** by impressions or CTR. Do not measure these pages against
`baofeng-uv5r-quick-ref.html`.

That said, five of the nine independently pass the Rule 0 niche-utility test in the
**"comparison tables with exact specs"** shape, and those are the ones to build first:

- **#2** — a per-chain confirmation/finality table with observed historical reorg depths. This
  artifact does not exist publicly in correct form. An engineer sets a confirmation policy with
  it open.
- **#3** — a CCSS control-by-control mapping. Read while filling in an assessment.
- **#4** — an IVMS101 field reference with a real payload and per-jurisdiction thresholds. Read
  while building a Travel Rule integration.
- **#6** — webhook/policy/status-lifecycle reference. Read while writing the integration.
- **#8** — recovery feasibility triage plus KDF cost math. Read while assessing a live case.

**#1, #5, #7 and #9 are architecture references**, not lookup cards. They earn their place on
goal-2 grounds and on the strength of a single hard artifact each (the MPC comparison matrix,
the finality-vs-freezability table, the ledger invariant, the exposed-pubkey inventory). Hold
them to that: if the signature artifact is not the best thing on the page, the page failed.

## Two batch-level decisions, made once here

### 1. New index category

These nine plus the four existing `Bitcoin & Finance` crypto pages form a cluster large enough
to warrant its own category rather than diluting a category that also holds
`index-investing-tax-advantaged.html` and `housing-comparison.html`.

Add to `$categoryStyles` in `index.php` and use in `category-map.php`:

```php
'Crypto Custody & Compliance' => ['color' => '#a21caf', 'bg' => '#fae8ff', 'icon' => 'bi-safe2-fill'],
```

All nine files go in this category. **Verify the hex visually before shipping sheet 1** — it sits
near `Philosophy & Religion` (`#6b21a8`) on the wheel; if the two chips are hard to tell apart in
the index grid, pick a different accent and record it here. Do not leave the batch split across
two categories.

`post-quantum-cryptography.html` stays in `Security & Privacy` (it is a general cryptography
page); sheet 9 is the custody-specific sibling and lives in the new category.

### 2. Sheet 6 is a patterns page, not a vendor page

The natural title for sheet 6 is a single vendor's name. **Do not build it that way.** A page
named after, and centred on, one company is the shape that already cost this repo a page after a
cease-and-desist. Sheet 6 ships as `custody-provider-integration.html`: an *integration-patterns*
reference in which several named platforms are compared factually from their own public
documentation, with the largest one carrying the most detail because it has the most public
documentation — not because it is being promoted. Concretely, the constraints are:

- No vendor logos, no vendor colour schemes, no brand-styled sections.
- Every vendor-specific claim carries an inline "as documented <Mon YYYY>" tag and links to that
  vendor's own public docs.
- No pricing claims unless publicly published by the vendor; commercial terms are private and
  guessing at them is both wrong and provocative.
- No comparative superlatives ("the best", "the industry standard"). State capabilities, cite the
  doc, let the table speak.
- Nothing sourced from a private account, dashboard, contract, or NDA'd material.

The same rule applies more loosely to sheets 4 and 5, which also name commercial vendors: name
them in a table, cite public documentation, do not rank them editorially.

## Prior work by the author that these sheets draw on

Two of the nine have a real body of the author's own work behind them, and the specs point at it.
Using it is what makes the batch credible; **how** it is used is constrained.

- **`Paytech-Labs/paytech-platform`** (private, .NET 9, built 2024) — a crypto payments platform:
  crypto payment invoices behind a swappable provider abstraction, provider webhook controllers,
  background invoice-monitor jobs that poll for state the webhooks were supposed to deliver, KYC
  verification with a vendor webhook, cash payouts, and a PostgreSQL transaction schema. That is a
  working instance of most of sheet 6's generic model, sheet 2's deposit-detection and
  reconciliation loop, sheet 4's KYC placement, and sheet 5's payment operations. Read it for
  **which problems are real and in what order they bite** — that is what turns these sheets from
  literature reviews into engineering references.
- **`~/Projects/WalletRecovery.info`** (local) — the recovery practice behind sheet 8, including its
  own research and content directories.

**Constraint, binding on both:** these are sources of *judgement*, not of *content*. Nothing
proprietary reaches a published page — no code, no schema, no entity or table names, no
configuration, no vendor commercial terms, no customer or client detail, no incident specific
enough to identify a party, and no material from a repository that is not public. PayTech Labs has
other shareholders and a board; WalletRecovery has clients. Every fact on every page must be
independently verifiable by a reader from the public sources named in that spec. If a genuinely
useful pattern can only be stated by revealing something non-public, state it generically or cut
it.

## Also worth doing, outside this repo

Sheet 7 continues an article the author published in 2017 and never followed up
(freethepeople.org, "How to Build a Bitcoin Exchange, Part 1"). If edit access to that article
still exists, add a "continued here" link to it once sheet 7 ships. Record in the build report
whether that was done — it is the batch's one genuine external backlink opportunity from a
property the author controls.

## Public-repo constraints for this batch

This repository is public. Three things must not appear in any of these specs or pages:

- **No individuals, employers, job descriptions, or hiring context.** The professional motivation
  behind the batch is real and is why goal 2 governs, but it stays out of the committed files.
  Write for "an engineer building or assessing a custody stack", never for a named reader.
- **No client, case, or engagement detail in sheet 8.** Every example is a composite or a
  publicly-reported incident with a citation. Nothing traceable to a real recovery client, no
  matter how anonymised it feels.
- **No operational detail of the author's own holdings, wallets, or key material** anywhere in
  the batch. The pages describe how custody is built; they never describe a specific deployment.
- **Nothing from a private repository**, including the author's own — see the prior-work
  constraint above.

## Shared design language

The batch is a set and should read as one. Fix these once, in sheet 1, and reuse:

**Identity: the control-room / assurance-report register.** Not "crypto" styling — no neon, no
gradients, no coin iconography. The reference points are an audit workpaper and a systems
runbook: a restrained near-monochrome ground (deep slate `#0f172a` dark / warm paper `#faf9f7`
light), one signal accent for the category (`#a21caf`), and a strict **three-colour semantic
scale used identically on every sheet** — a green for "safe/finalised/passes", an amber for
"conditional/degraded/manual review", a red for "unsafe/broken/blocked". Once a reader learns
the scale on sheet 2's finality table, it must mean the same thing on sheet 3's CCSS grid and
sheet 9's exposure inventory. Colour is never the only carrier: every cell also carries a glyph
or a word.

Typography: a system UI stack for prose, a monospace stack for every value that is a number, a
path, a field name, an address, or a status. Tabular figures on all numeric columns.

Per-sheet variation comes from the **signature element**, not from re-theming. Each spec names
one; build it first and best.

## Cluster cross-link map

The nine link densely to each other; that internal graph is most of the point. The spine:

- **1 ↔ 3** — MPC is a signing primitive; custody tiering is what wraps it. Sheet 1's "what MPC
  does not protect" section hands directly to sheet 3's policy engine.
- **2 ↔ 5** — CCTP latency is a function of source-chain finality; sheet 5 links into sheet 2's
  finality table rather than restating it.
- **2 ↔ 7** — the confirmation policy is where the exchange ledger and the chain meet.
- **3 ↔ 4** — compliance controls are custody controls; screening placement is a policy-engine
  question.
- **1 ↔ 9** — threshold protocols are the hard case for PQ migration.
- **1, 3, 6 ↔ 8** — everything about how keys are held, read backwards through how they are lost.
- **6 ↔ 1, 3** — build-vs-buy only makes sense against the two sheets that describe what you'd be
  building.

External to the batch: `bitcoin-self-custody-guide.html`, `bitcoin-wallet.html`,
`bitcoin-exchanges-cards.html`, `post-quantum-cryptography.html`, `personal-cybersecurity.html`.
Add one reciprocal inbound line to each of those four from the relevant new sheet — that is what
makes the cluster visible to the index and to crawlers.

## Accuracy protocol reminder (Rule 1 applies with unusual force here)

Every version number, threshold, date, byte count, iteration count, block count, dollar figure
and protocol name in these nine specs is an **anchor from the spec author's memory, not a fact**.
This subject matter drifts fast (MiCA phase-ins, the GENIUS Act, CCSS versioning, NIST PQC
document numbers, vendor APIs, L2 finality parameters) and several of the anchors here are
recalled to an order of magnitude rather than a digit.

Verify every one against the primary source named in the spec. If verification disagrees with the
anchor, the verified number wins with no discussion. **If a number cannot be verified, cut the
entry — do not ship the anchor.** A wrong confirmation count or a wrong Travel Rule threshold on
a page written for practitioners is worse than an absent one; these are pages people would act
from.
