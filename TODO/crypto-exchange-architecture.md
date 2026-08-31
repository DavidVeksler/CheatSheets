# Spec: Crypto exchange architecture — matching, settlement, and the wallet boundary

**Target file:** `crypto-exchange-architecture.html`
**Batch:** [custody-engineering-batch-2026-08.md](custody-engineering-batch-2026-08.md) (sheet 7 of 9, P2).
Depends on sheet 2 (confirmation policy) and sheet 3 (custody tiering); build after both.

## Why this topic

This page has an unusual and strong hook: **it is the sequel to an article the author already
published and never continued.** "How to Build a Bitcoin Exchange, Part 1: Design Goals & Risk
Management" (freethepeople.org, David Veksler, 1 July 2017) laid out design goals, order types,
execution speed, security categories and market making — and closed by promising to elaborate in
future posts. Part 2 was never written. This sheet is that Part 2, rebuilt for 2026: the same
author, nine years of operating experience later, taking the piece that the 2017 article deferred.

That framing should be explicit on the page — a short note linking the 2017 article as the design-
goals half — because it does three things at once: it makes the page a genuine continuation rather
than a generic explainer, it gives an honest reason for the page to exist, and it creates a real
cross-domain link between two of the author's own properties.

The substantive gap is the boundary itself. Matching-engine content is written by trading-systems
engineers who treat settlement as someone else's problem, and custody content is written by
security engineers who treat the order book as someone else's problem. **The interesting
engineering is precisely at the seam**: where the ledger stops being an in-memory trading position
and becomes an on-chain liability, what invariant connects them, and what breaks when it does not
hold. That seam is also where every large exchange failure has happened — not in the matching
engine.

## Targeting

- **Primary query:** `crypto exchange architecture`
- **Secondary:** `how to build a crypto exchange`, `matching engine design`,
  `omnibus vs segregated wallet exchange`, `exchange ledger double entry crypto`,
  `proof of reserves merkle tree`, `internal transfer vs on chain settlement`,
  `crypto exchange hot wallet design`
- **Mode:** research mode, high intent. Someone designing, assessing or auditing an exchange, or
  writing about one. The 2017 article's residual readership is a secondary inbound path worth
  serving with a clear "this is the continuation" note near the top.

## Draft title / H1 / meta

- `<title>`: `Crypto Exchange Architecture: Matching, Ledger, Settlement` (57 chars)
- **H1:** `Crypto Exchange Architecture: Where the Order Book Ends and the Wallet Begins`
- **Meta description (draft):**
  `Matching engine design, the double-entry ledger invariant that ties trading to custody, internal transfers versus on-chain settlement, omnibus versus segregated addressing, and proof of reserves.` (192 chars)

## Reader outcome

The reader can draw the boundary between the trading system and the custody system, state the
invariant that must hold across it and how it is checked, decide omnibus versus segregated
addressing with the regulatory and operational consequences of each, and explain what a proof of
reserves does and does not prove. Acceptance test: given an exchange's published PoR attestation,
they can name what it fails to establish.

## Success metric

Deep links to the ledger-invariant and proof-of-reserves sections; referral traffic from the 2017
Free the People article once a "continued here" link is added there. The cross-property link is a
success metric in itself — it connects two of the author's domains on a topic where both have
standing.

## Content approach

Trading side, then the boundary, then the custody side — with the boundary as the longest and most
detailed part, because it is the page's reason to exist.

1. **Quick reference: the system map** — the whole exchange on one screen as a block diagram:
   client APIs, risk/pre-trade checks, sequencer, matching engine, market data, the ledger, and
   the wallet/settlement subsystem, with the **wallet boundary drawn as a heavy line** and every
   crossing of it labelled. Signature element. Above it, the short note placing the page as the
   continuation of the 2017 design-goals article, with the link.
2. **Matching engine** — the trading core, at working depth and no deeper (this page is not a
   trading-systems tutorial; sheet scope discipline per README Rule 4). Deterministic single-writer
   sequencing and why determinism is the whole design; the in-memory book structure (price levels
   with FIFO queues) and its complexity characteristics; order types (limit, market, stop, IOC,
   FOK, post-only, iceberg) with what each does at the book; price-time priority versus pro-rata;
   self-trade prevention and why it is not optional; sequence numbers on market data and the
   client's obligation to detect a gap and resynchronise; snapshot-plus-journal recovery and
   deterministic replay; and the latency budget stated honestly — microseconds in the engine,
   milliseconds end to end, and the fact that for most crypto venues the engine is not the
   bottleneck.
3. **The ledger** — the system of record, and the part the 2017 article's "atomic database
   operations" section pointed at. Double-entry structure with accounts and immutable journal
   entries; **integer minor units, never floating point**, with the per-asset precision problem
   (chains have different decimal counts, and a naive schema loses value at the eighteenth
   decimal); available versus total balance and the hold/reservation model that makes an order
   placement safe; idempotent posting; append-only with no updates or deletes, so the balance is a
   projection rather than a stored value; and the hard rule that follows — **the matching engine
   never talks to a chain, and the wallet system never talks to the book.** Both talk to the
   ledger.
4. **The wallet boundary** — the page's core. State the invariant explicitly and give it a box:
   *the sum of all customer liabilities, plus fees and the exchange's own position, equals
   on-chain holdings plus in-flight settlements plus receivables.* Then work through each crossing
   of the boundary in turn:
   - **Deposit:** detection, confirmation policy (link to sheet 2, do not restate), credit as a
     ledger entry, and the hold that may still apply after crediting.
   - **Internal transfer / trade settlement:** a ledger entry and nothing else. No chain, no fee,
     instant, final. State this plainly because it is the single most under-appreciated fact about
     exchanges: **the overwhelming majority of "transactions" on an exchange never touch a
     blockchain**, which is what makes them fast and what makes the ledger, not the chain, the
     thing that must be right.
   - **Withdrawal:** debit and hold, risk and compliance gates (sheet 4), policy and quorum
     (sheet 3), signing, broadcast, confirmation, settlement of the hold. The ordering matters —
     debit before broadcast, or a double-spend of the customer's balance is possible.
   - **Sweeps and rebalances:** internal movements that change on-chain location without changing
     any liability, and the accounting mistake of booking them as anything else.
   Close with the reconciliation loop that continuously asserts the invariant, its cadence, and
   what happens on a break — hand off to sheet 2's break taxonomy.
5. **Omnibus versus segregated addressing** — the models: a single pooled hot address with all
   attribution in the ledger; per-user deposit addresses derived from an HD tree and swept into a
   pool; and genuinely segregated per-user custody where the address *is* the account. Compare on:
   operational cost, sweep complexity and gas cost, deposit attribution reliability, privacy,
   on-chain provability of individual holdings, and the regulatory position on commingling. Then
   the regulatory overlay in one compact block — customer-asset segregation obligations, the
   prohibition on using customer assets for the firm's own account, and the fact that the largest
   failures in this industry were **not** technical failures of any of the systems above but
   violations of exactly this boundary. Say that plainly and without editorialising: the
   architecture cannot enforce a rule that the operator overrides.
6. **Withdrawal pipeline at scale** — batching multiple withdrawals into a single transaction and
   the fee arithmetic that justifies it; the per-chain batching limits; fee policy (who pays, and
   the flat-fee-versus-cost decision); queue behaviour under a fee spike or a chain halt; the
   whitelist time-lock (sheet 3); and the drain-the-queue-after-an-outage problem, where the
   backlog releases at once into a policy engine sized for normal volume.
7. **Proof of reserves** — the section with the most substance and the most common
   misunderstanding. Assets side: proving control of addresses (a signed message, or a
   self-transfer of a challenge value) and its limitations, including borrowed-assets-at-snapshot
   gaming. Liabilities side, which is the hard half: a Merkle tree over customer balances with the
   leaf construction that lets a customer verify their own inclusion without learning others'
   balances, the **omitted-liability and negative-balance attacks** that a naive tree permits, and
   the zero-knowledge constructions that close them by proving the sum is correct and every
   balance non-negative without revealing the set. Then the honest conclusion, stated once and
   clearly: **proof of reserves is not proof of solvency** — it says nothing about off-balance-
   sheet liabilities, and a point-in-time snapshot says nothing about the moment after. Include the
   reserve-oracle approach for on-chain consumers of a reserve attestation, and what an
   attestation feed actually asserts. Cross-reference sheet 3.
8. **Risk and derivatives, briefly** — a compact section because it is a sheet of its own and
   should not swallow this one: cross versus isolated margin, the liquidation engine, the insurance
   fund and auto-deleveraging as the loss-socialisation backstop, funding rates on perpetuals, and
   mark price versus index price with the oracle-manipulation attack that has repeatedly emptied
   venues that used a thin spot market as their mark. Three to five entries, then a one-line "this
   deserves its own page" per README Rule 4.
9. **APIs and market data** — REST versus WebSocket versus FIX and what each is actually for; rate
   limiting and the weight model; the snapshot-plus-delta order book and the **resynchronise on
   sequence gap** rule that most client implementations get wrong; idempotent order placement with
   client order IDs; and the ordering guarantee between the private and public streams.
10. **Common mistakes** (mandatory) — floating-point balances; the matching engine reading chain
    state; crediting before the confirmation policy is met; booking a sweep as a liability change;
    withdrawal debit after broadcast; reconciliation with a nonzero tolerance on balances; per-user
    addresses without a gap-limit-aware scanner; a proof of reserves without a liabilities proof;
    a liquidation engine marking against a manipulable spot price; treating the ledger as
    reconstructible from the chain.
11. **Related sheets** footer per the cross-link map, plus the external link back to the 2017 Part 1.

## Volatile-facts register

**Overall: STABLE — the most durable page in the batch.**
- Matching-engine design, ledger structure, the boundary invariant, addressing models, PoR
  constructions and their attacks: **STABLE.** These are systems-engineering fundamentals and will
  read correctly in ten years.
- **§5 regulatory overlay: SLOW-DRIFT** — segregation obligations evolve; keep it to a few lines
  with dated citations so updating is cheap.
- **§7 zk-PoR constructions: SLOW-DRIFT** — implementations improve; describe the construction
  class rather than any one venue's implementation, and the section stops rotting.
- Any named venue or incident: cite and date, and prefer describing the failure class over
  narrating a company.
Annual freshness rotation, low priority within the batch.

## Index category

`Crypto Custody & Compliance`.

## Reading conditions

**Desk, long read, likely in one sitting.** This is the batch's most architectural page and the
least lookup-shaped; the reader is building a mental model, not fetching a value. Consequences:
invest in the system map and the boundary diagram over table density; keep prose sections tight
but allow them; a sticky section index matters because the page is long. The invariant statement
in §4 should be visually set apart as the page's one memorable box. Mobile: the system map must
degrade to a vertical stack that preserves the boundary line, which is the one thing the diagram
must never lose.

## Cross-link map

- **Internal outbound:** `blockchain-deposits-withdrawals.html` (sheet 2 — confirmation policy,
  batching, break taxonomy), `institutional-crypto-custody.html` (sheet 3 — tiering, policy
  engine, PoR), `crypto-compliance-architecture.html` (sheet 4 — the withdrawal gates),
  `custody-provider-integration.html` (sheet 6 — what a platform does and does not replace),
  `stablecoin-payment-infrastructure.html` (sheet 5), `bitcoin-exchanges-cards.html` (the
  consumer-facing counterpart — a genuine complement: that page is how to *choose* an exchange,
  this one is how one is *built*).
- **Reciprocal inbound:** one line from `bitcoin-exchanges-cards.html` and one from sheet 2's
  settlement section.
- **External cross-property:** link to
  `https://freethepeople.org/how-to-build-a-bitcoin-exchange-part-1-design-goals-risk-management/`
  from the top note as "Part 1: design goals and risk management (2017)". **Also add a reciprocal
  "continued here" link on the Free the People article if the author still has edit access** —
  that is a separate action outside this repo, worth doing, and worth noting in the build report
  rather than silently skipping.
- **External outbound:** primary papers and specifications for the PoR constructions, FIX protocol
  documentation, and post-mortems or regulatory findings for any incident referenced. No exchange
  marketing pages.

## og:image / shareable artifact

The **system map with the wallet boundary** at 1200×630 — the whole exchange with the heavy line
through it and the four labelled crossings. It is the page's title in picture form. The invariant
box is the screenshot-this text artifact.

## Jurisdiction scope

Technical and global. §5's regulatory overlay is US and EU at a few lines' depth with citations,
stated once as scope-limited and handing off to sheets 3 and 4 for anything deeper. No legal
advice; no commentary on any specific firm's conduct beyond citing published findings.

## Density targets

System map ≥ 8 components with ≥ 4 labelled boundary crossings. Order types ≥ 7. Ledger section
≥ 6 design rules. Boundary section: 1 stated invariant plus 4 crossings each worked in full
sequence. Addressing comparison 3 models × ≥ 6 criteria. Withdrawal pipeline ≥ 6 stages plus the
batching arithmetic worked to a real number. PoR ≥ 4 constructions plus ≥ 3 named attacks on naive
schemes. Risk section 3–5 entries. API section ≥ 5 rules. Common mistakes ≥ 10.

## Research sources (verify against these, per Rule 1)

For the trading core: published exchange engineering write-ups and the standard literature on
deterministic single-writer sequencing; FIX protocol specifications. For PoR: the original Merkle-
tree-of-liabilities proposals and the published zero-knowledge proof-of-solvency papers — read the
papers, and be precise about what each construction proves. For the regulatory overlay: primary
regulatory text and published enforcement findings only. For the 2017 continuation note: the Free
the People article itself, cited with its own publication date. Chain and node documentation for
anything about deposits or broadcasting — but prefer linking sheet 2 to restating it.

Experience source, not a citable source: `Paytech-Labs/paytech-platform` implements a
transaction and invoice ledger in PostgreSQL alongside crypto payment and fiat payout rails —
a smaller instance of §3's ledger and §4's boundary. Use it to check that the invariant in §4 is
stated in a form that a real schema could assert. Per the batch constraint, no schema, entity
names or code reach the page.

## Visual design

**Identity: the batch register in its systems-documentation mode** — closest in feel to sheet 6,
but with more diagram and less table. The shared semantic scale is used sparingly here (it fits the
PoR section's "what this proves / does not prove" columns and the addressing comparison), because
this page's information is structural rather than categorical.

**Signature element: the wallet-boundary system map.** One large inline SVG: the exchange drawn as
labelled blocks with data flows, and a single heavy vertical rule running through it separating the
trading domain from the custody domain. Every arrow that crosses the rule is numbered and links to
its subsection in §4; every arrow that does *not* cross it is drawn plainly, so the reader sees at a
glance how few flows actually cross — which is the page's thesis. The invariant is printed along
the boundary line itself. Draw the 375 px version first: the rule becomes horizontal, the domains
stack, and the numbered crossings remain the visual focus.

No JavaScript. The 2017-continuation note is a small, plainly-styled callout at the top — a link
and one sentence, not a banner.
