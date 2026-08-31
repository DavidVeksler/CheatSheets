# Spec: Blockchain deposits & withdrawals — confirmations, reorgs, nonces, reconciliation

**Target file:** `blockchain-deposits-withdrawals.html`
**Batch:** [custody-engineering-batch-2026-08.md](custody-engineering-batch-2026-08.md) (sheet 2 of 9, **P0**).
**Build second**, after sheet 1 fixes the design language. This is the batch's densest data page
and the one most likely to be linked externally.

## Why this topic

The useful version of this page does not exist publicly. What exists: exchange help-centre pages
listing their own confirmation counts with no reasoning, chain documentation describing finality
for that one chain, and blog posts explaining reorgs in the abstract. Nobody has put a
**cross-chain finality table next to observed historical reorg depths next to a confirmation
policy derived from value at risk** — which is the artifact every payments or custody engineer
actually needs and currently assembles by hand, badly, from six tabs.

The second half is rarer still. Everything above the signing layer is well covered; the
operational layer beneath it — EVM nonce allocation under concurrency, UTXO coin selection and
consolidation timing, the gas-station problem for token sweeps, idempotency when the only
identifier you have is mutable, and a systematic taxonomy of ways the reconciler breaks — is
tribal knowledge that gets rebuilt from scratch at every company and is learned by losing money.

The framing that makes it defensible: **"finality" is not a property of a chain, it is a policy
you set against a threat model and a value at risk.** Bitcoin's six confirmations is a convention
from 2009, not a derivation. On optimistic rollups, finality is a claim that stays contestable for
the length of the challenge window regardless of how many blocks pass.

## Targeting

- **Primary query:** `blockchain confirmations by chain`
- **Secondary:** `ethereum safe vs finalized`, `solana confirmed vs finalized`,
  `how many confirmations for deposit`, `blockchain reorg history`, `evm nonce management`,
  `erc20 sweep gas station`, `utxo consolidation strategy`, `crypto deposit reconciliation`
- **Mode:** operational lookup, mid-build. The realistic use is a deep link to one anchor from a
  code review or a design doc. Every table and every chain row needs its own stable anchor, and
  the finality table must be usable as the only thing on screen.

## Draft title / H1 / meta

- `<title>`: `Crypto Deposits & Withdrawals: Confirmations, Reorgs, Nonces` (59 chars)
- **H1:** `Deposits and Withdrawals: Confirmations, Reorgs, Nonces, and Reconciliation`
- **Meta description (draft):**
  `Per-chain finality and confirmation policy set against observed reorg depths, plus EVM nonce management under concurrency, UTXO coin selection, token-sweep gas, and a reconciliation break taxonomy.` (194 chars)

## Reader outcome

The reader can set a defensible confirmation policy per chain and per value tier and explain the
derivation; build a withdrawal pipeline that does not double-send under retry, reorg or restart;
and, when the reconciler breaks at 2 AM, classify the break from a taxonomy instead of guessing.
Acceptance test: they can answer "why do you credit this chain at N confirmations and that one at
M" without appealing to convention.

## Success metric

Deep links to individual anchors — the finality table, the reorg register, the nonce section —
from engineering docs, Stack Exchange answers and repository READMEs. Anchor-level inbound links
are the metric; total impressions are not. Secondary: return-direct traffic (engineers bookmark
tables they use repeatedly).

## Content approach

Reference-first. The reader is looking something up; prose exists only to make the tables
correct.

1. **Quick reference: the finality table** — first screen, no preamble. Signature element.
   Columns per chain: consensus family, block time, finality *type* (probabilistic / economic /
   deterministic / L1-derived), the chain's own confirmation levels and their exact names,
   time-to-each-level, deepest reorg observed with a date, and a recommended credit threshold at
   three value tiers. Rows: Bitcoin, Ethereum, Solana, Tron, BNB Smart Chain, Polygon PoS,
   Avalanche C-Chain, Litecoin, Dogecoin, Bitcoin Cash, XRP Ledger, Stellar, Cardano, Cosmos-SDK
   chains, Tezos, Aptos, Sui, TON, and the L2 block (below). Every cell that is a number carries
   its source.
2. **The vocabulary problem** — a short, high-value section, because half the field's confusion is
   terminological. Ethereum's `head`/`safe`/`justified`/`finalized`, Solana's
   `processed`/`confirmed`/`finalized`, Tron's SR confirmations, Cosmos's single-block finality,
   Bitcoin's absence of any finality concept. State plainly which of these are the *same idea*
   and which are not, and give the exact RPC parameter that requests each level — that is the
   detail an implementer needs and the one every explainer omits.
3. **Layer 2: where finality is a lie** — separate treatment because L2s break the table's
   assumptions. Three distinct moments for an optimistic rollup — sequencer soft confirmation
   (fast, trust the sequencer, no cryptographic guarantee), batch posted to L1 (data available,
   still challengeable), challenge window elapsed (final) — and the fact that the middle state is
   what most integrations mistakenly treat as final. Then ZK rollups, where finality arrives with
   the validity proof's L1 inclusion and inherits L1 finality. Then the dependency that catches
   everyone: **an L2 cannot be more final than the L1 it settles to**, so an L1 non-finality
   incident propagates. Include the forced-inclusion / escape-hatch mechanism, because it is the
   answer to "what if the sequencer stops".
4. **Reorg register** — a dated table of observed reorganisations with depth, chain, cause and
   consequence. Include the deep 51%-attack reorgs on smaller proof-of-work chains (which are the
   evidence that confirmation policy must scale with a chain's security budget, not just its
   block time), the notable Bitcoin chain split, Ethereum's shallow reorgs and its
   non-finality incidents, and the deep reorg on a large PoS sidechain. Each row cites a primary
   source. This table is the empirical basis for §5 and is why the page can claim to be derived
   rather than conventional.
5. **Confirmation policy as a function of value at risk** — the derivation. Frame it as cost of
   attack versus value of reversal: for a proof-of-work chain, the rentable-hashpower cost to
   produce a reorg of depth d, against the amount you would credit; for proof-of-stake, the
   slashable stake at risk. Produce a tiered policy table (value bands × chain × confirmations)
   with the reasoning shown for at least two chains in full, plus the operational overlays: credit
   below threshold with a hold on withdrawal, different thresholds for internal versus external
   destinations, and raising thresholds during a known network incident.
6. **EVM nonce management under concurrency** — the section engineers arrive for. Sequential
   per-account nonces; `pending` versus `latest` and why polling the node for the next nonce is a
   race; the gapped-nonce stall (one missing nonce blocks every later transaction); a
   single-writer allocator design with leases and timeouts; replacement transactions and the
   minimum fee bump the client will accept; cancellation by self-send at the same nonce; what a
   reorg does to a nonce you thought was consumed; EIP-1559 fee fields and the underpriced-during-
   spike failure; chain-ID replay protection; and the real answer to throughput — **nonces are
   per-address, so concurrency comes from sharding across hot addresses, not from cleverness at
   one address.** Include the stuck-transaction runbook as a numbered procedure.
7. **UTXO operations** — coin selection objectives and the algorithms in use (branch-and-bound for
   changeless matches, knapsack fallback), effective value and when an input costs more to spend
   than it holds, dust thresholds, change management and the privacy leak of naive selection,
   consolidation strategy and timing it to low-fee windows, fee estimation and its failure modes,
   RBF and CPFP as the two unstick mechanisms with when each applies, batching withdrawals into
   one multi-output transaction and the fee arithmetic that justifies it, and deposit detection by
   descriptor/xpub scan with the gap limit that silently loses deposits when exceeded.
8. **The gas-station problem** — sweeping a token requires the native asset at the address that
   holds it, and that address is a per-user deposit address with a zero native balance. The
   options as a comparison table: pre-funding every deposit address (simple, leaks value,
   scales badly), a funding transaction immediately before each sweep (two transactions, race
   conditions), `CREATE2` counterfactual deposit contracts deployed at sweep time, permit /
   meta-transaction flows where the token supports them, and account abstraction with a paymaster.
   Then the chains where the economics differ structurally: the resource-staking model on Tron
   (bandwidth and energy rather than per-transaction fees) and the rent-exemption and associated-
   token-account creation cost on Solana. Give the cost-per-sweep arithmetic for each.
9. **Idempotency and identity** — exactly-once delivery does not exist, so the design is
   at-least-once plus deduplication. A client-supplied idempotency key on withdrawal submission,
   an internal transaction ID that is the system of record, and the rule that **the on-chain
   transaction hash is an output, never a key**. The double-broadcast case, the crash-between-sign-
   and-broadcast case, the reorg-then-rebroadcast case, and the specific handling per chain family
   (Bitcoin malleability before and after segwit, deterministic EVM hashes, Solana signatures and
   blockhash expiry, and the memo/tag chains).
10. **Deposit crediting hazards** — the operational list: destination-tag and memo chains as the
    single largest source of lost deposits; verifying the token contract rather than the symbol
    (fake tokens with real symbols); fee-on-transfer and rebasing tokens breaking amount
    accounting; contract-originated transfers that do not appear in a naive transaction list;
    decimals mismatches; wrong-network deposits to an address that is valid on several chains;
    zero-value transfers used for address poisoning; and deposits from sanctioned or mixer-adjacent
    sources, which is a hand-off to sheet 4.
11. **Break taxonomy for the reconciler** — the closing artifact and the second-most-shareable
    block. Every class of mismatch, with detection signal, likely cause, and remedy:
    on-chain-not-in-ledger; ledger-not-on-chain; amount mismatch; duplicate credit; reorg-orphaned
    credit; wrong-chain deposit; unsupported asset to a supported address; dust; internal transfer
    double-count; fee accounting drift; in-flight at snapshot time. Plus the design questions
    that precede it: reconciliation cadence, what tolerance (if any) is acceptable and why the
    correct answer for balances is zero, and the invariant to assert continuously.
12. **Common mistakes** (mandatory) — using the transaction hash as a primary key; crediting on
    `latest` instead of a finality level; a fixed confirmation count applied across chains of wildly
    different security budgets; polling for the next nonce from more than one worker; sweeping
    without checking the native balance first; exceeding the xpub gap limit; treating an L2
    sequencer receipt as final; reconciling on a schedule that is longer than the withdrawal SLA.
13. **Related sheets** footer per the cross-link map.

## Volatile-facts register

**Overall: VOLATILE — the most perishable page in the batch.**
- **Finality table: VOLATILE.** Block times, finality parameters and confirmation levels change
  with protocol upgrades; L2 challenge windows and the set of live L2s change fastest of all.
  Re-verify every row against chain documentation at least twice a year; date the table inline
  with a single visible "table verified" line rather than per-row dates.
- **Reorg register: APPEND-ONLY.** Never rots, only becomes incomplete. Add incidents as they
  occur; each new deep reorg strengthens §5.
- **Gas-station mechanics and Tron/Solana resource economics: VOLATILE** — fee-model parameters
  are governance-adjustable. Date the arithmetic.
- **Nonce management, UTXO selection, idempotency, break taxonomy: STABLE.** These are properties
  of the problem, not of any release.
Named as a semi-annual target in the weekly-freshness rotation, with the finality table and the L2
section as the check targets.

## Index category

`Crypto Custody & Compliance`.

## Reading conditions

**Two monitors, an IDE open, mid-implementation.** The reader is looking up one number or one
procedure and will leave. Consequences: the finality table must be reachable in one scroll and
readable without horizontal scrolling on a laptop; every chain row and every subsection needs a
copy-able anchor link (a visible `#` on hover); code and RPC parameter names must be selectable
monospace, never images. Mobile is a genuine secondary case (on-call, phone, reading the break
taxonomy) so the taxonomy and the stuck-transaction runbook specifically must be excellent at
375 px — those two collapse to single-column cards. Print: the finality table on one landscape
page is a legitimate wall artifact; make it work.

## Cross-link map

- **Internal outbound:** `crypto-exchange-architecture.html` (sheet 7 — where the ledger meets
  this pipeline), `stablecoin-payment-infrastructure.html` (sheet 5 — CCTP latency is downstream
  of this table), `institutional-crypto-custody.html` (sheet 3 — withdrawal policy),
  `crypto-compliance-architecture.html` (sheet 4 — screening placement in this same pipeline),
  `bitcoin-self-custody-guide.html`.
- **Reciprocal inbound:** one line from sheet 5's CCTP section and one from sheet 7's settlement
  section, both pointing at the finality-table anchor.
- **External outbound:** chain documentation only for chain parameters (Bitcoin Core, Ethereum
  consensus specs, Solana docs, Tron docs, each L2's own docs), EIPs by number for nonce/fee
  behaviour, BIPs for descriptors and coin selection, and primary incident reports or post-mortems
  for every reorg row. No exchange help-centre pages as authority for anything except that
  exchange's own policy.

## og:image / shareable artifact

The **finality table**, cropped to the eight best-known chains and the three columns that carry
the idea (finality type, time to final, deepest observed reorg), at 1200×630 with the semantic
colour scale. This is the block the page will be linked for. The break taxonomy is the second
screenshot-this artifact.

## Jurisdiction scope

None — this is protocol behaviour, which is global. The only jurisdictional content on the page is
the single line in §10 handing sanctioned-source deposits to sheet 4. Keep it to one line.

## Density targets

Finality table ≥ 18 chains plus ≥ 6 L2s, × 8 columns. Reorg register ≥ 12 dated incidents.
Confirmation-policy table ≥ 3 value tiers × ≥ 10 chains, with 2 derivations shown in full.
Nonce section ≥ 8 failure modes plus a numbered runbook. UTXO section ≥ 6 selection/consolidation
topics. Gas-station comparison ≥ 5 approaches with per-sweep cost arithmetic. Break taxonomy ≥ 11
classes × 3 columns. Deposit hazards ≥ 8. Common mistakes ≥ 8.

## Research sources (verify against these, per Rule 1)

Chain documentation and consensus specifications first, always: the Ethereum consensus specs for
`safe`/`finalized` semantics, Solana's commitment-level documentation, the Bitcoin developer
documentation, Tron, Cosmos SDK, and each L2's own published finality and challenge-window
parameters. EIPs by number (1559, 155, and the nonce-relevant transaction-type EIPs). BIPs for
descriptors, gap limits and coin selection. For the reorg register: block explorers plus the
original post-mortem or research write-up for each incident — never a secondary news article as
the sole source. For attack-cost arithmetic in §5: publish the method and the hashrate/stake
inputs with their date, so a reader can redo it rather than trusting a stale number.

Experience source, not a citable source: `Paytech-Labs/paytech-platform` implements deposit
detection as a provider webhook plus a background invoice-monitor job that polls for the state
the webhook was supposed to deliver — which is §9 and §11 of this spec as built code. Use it to
check that the break taxonomy is complete and ordered by real frequency. Per the batch
constraint, nothing from it appears on the page: no schema, no entity names, no configuration.

## Visual design

**Identity: the batch's assurance register, pushed toward a monitoring console** — this is the
data-densest sheet and should look it. Deep slate ground, tabular monospace numerals throughout,
the shared three-colour semantic scale doing heavy work in the finality table (green = deterministic
or economically final, amber = probabilistic or challengeable, red = trust-the-sequencer / no
guarantee). Every coloured cell also carries a word, so the table is readable in greyscale and by
a colour-blind reader — this is non-negotiable given the table is the whole page.

**Signature element: the finality timeline.** For each of six representative chains, a horizontal
inline-SVG track with markers at each confirmation level, drawn to a shared logarithmic time axis
so a reader sees at a glance that Bitcoin's six confirmations and Solana's finalisation are three
orders of magnitude apart, and that an optimistic rollup's real finality marker sits a week to the
right of everything else. The log axis is the entire point — a linear axis renders the comparison
useless. Label every marker in text; the drawing carries the shape, the adjacent table carries the
numbers. On narrow viewports the tracks stack and keep the shared axis.

No JavaScript. Wide tables get `overflow-x: auto` wrappers with a visible scroll affordance.
Resist building a filterable chain selector — it would hide exactly the cross-chain comparison the
page exists to provide.
