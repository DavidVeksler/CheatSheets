# Spec: Stablecoin payment & treasury infrastructure

**Target file:** `stablecoin-payment-infrastructure.html`
**Batch:** [custody-engineering-batch-2026-08.md](custody-engineering-batch-2026-08.md) (sheet 5 of 9, P1).
Depends on sheet 2 for finality — do not restate the finality table here, link into it.

## Why this topic

Stablecoin content is split between market commentary (supply charts, issuer market share) and
crypto-native explainers (how a peg works). The operational layer — what a company building
payments or treasury on stablecoins actually has to decide — is missing, and the gap has a sharp
edge: **a stablecoin payment can be technically final and still reversible**, because the issuer
holds a freeze function on the token contract. Chain finality is not payment finality when a
centralised issuer can blacklist an address after settlement. That single distinction reorganises
the whole subject and almost nothing written for a general audience states it.

The second missing piece is fragmentation. "USDC" is not one asset; it is native issuance on a
dozen chains plus bridged representations that are different assets with different risk, and the
bridge-hack record is the evidence. A treasury operator's actual daily problem is inventory across
that fragmented surface: where the balances are, what it costs and how long it takes to move them,
and what the rebalance is worth against the cost of idle float.

Third: the reversibility asymmetry at the ramps. Fiat rails can be reversed for weeks after the
fact; the crypto leg cannot be reversed at all. Every on-ramp fraud loss lives in that gap, and it
is an architectural constraint, not a fraud-team problem.

## Targeting

- **Primary query:** `stablecoin payment infrastructure`
- **Secondary:** `cctp cross chain transfer protocol`, `native vs bridged usdc`,
  `stablecoin settlement finality`, `usdc vs usdt reserves`, `stablecoin treasury management`,
  `stablecoin depeg history`, `genius act stablecoin requirements`, `stablecoin vs card fees`
- **Mode:** research mode with a build behind it — a payments or treasury engineer, or someone
  writing the memo that decides whether to do this at all.

## Draft title / H1 / meta

- `<title>`: `Stablecoin Payment & Treasury Infrastructure: How It Works` (57 chars)
- **H1:** `Stablecoin Payment and Treasury Infrastructure`
- **Meta description (draft):**
  `Issuer reserve models and depeg history, native versus bridged supply, CCTP burn-and-mint, ramp mechanics, and why settlement finality and payment finality are different things for a freezable token.` (198 chars)

## Reader outcome

The reader can choose an issuer and a chain for a given payment flow and defend both; design a
multi-chain treasury with inventory targets and rebalance triggers; and state exactly when a
payment received in stablecoin is safe to treat as settled — including the conditions under which
it never fully is. Acceptance test: they can price the same $100,000 transfer three ways (card
rail, wire, stablecoin) end to end, including float cost and reversal risk, and say which wins for
their flow.

## Success metric

Linked from payments-engineering and treasury discussions; the finality-versus-freezability table
and the fee comparison reused. Signals "understands the operating model", which is the goal-2
purpose. Not a traffic page.

## Content approach

Issuer → transport → ramps → finality → treasury. The finality section is the hinge; everything
before it is inputs and everything after is consequences.

1. **Quick reference: the issuer card** — the major fiat-backed stablecoins on one screen with
   issuer, jurisdiction and regulatory status, reserve composition class, attestation type and
   cadence, freeze/blacklist capability, chains with native issuance, and approximate supply with
   its as-of date. Signature element. Include at least one non-fiat-backed entry (crypto-
   collateralised, and a synthetic/delta-neutral design) explicitly marked as a **different risk
   class**, because treating them as interchangeable is the most expensive category error in the
   subject.
2. **Reserve models and what an attestation is** — the taxonomy: fiat-and-equivalents backed,
   over-collateralised crypto-backed, RWA-backed, synthetic/delta-neutral, and algorithmic (with
   the failed case named and dated as the reason the category is treated as it is). Then the
   distinction that matters and is routinely blurred: **an attestation is not an audit** — what an
   agreed-upon-procedures report actually asserts, at what point in time, and what it does not
   cover. Reserve composition risk (bank deposit concentration, commercial paper versus T-bills,
   repo, and the maturity/liquidity profile under a redemption run), and the redemption right
   itself: who can actually redeem at par, at what minimum, on what schedule — because for most
   holders the answer is "not you, via the secondary market", and that is why pegs break.
3. **Depeg register** — a dated table of significant depeg events: asset, date, depth, duration,
   proximate cause, and how it resolved. The banking-exposure depeg, the algorithmic collapse, the
   collateral-crisis events, and the smaller ones. Each row cited. This is the empirical backing
   for §2's risk framing and the reason the page can make claims rather than assertions.
4. **Multi-chain supply fragmentation** — native issuance versus bridged representation as
   different assets with different failure modes; canonical bridges versus third-party; the
   lock-and-mint model's structural weakness (the lock contract is a single honeypot) and the
   **bridge-hack register** — dated, with amounts and root causes — as its evidence; the
   liquidity-fragmentation consequence for a payments operator (your customer sends the bridged
   variant to your native-only address, or vice versa, and the deposit is unrecoverable or
   requires a swap); and the accounting question of whether a bridged variant is the same asset in
   your ledger. Practical guidance: accept which variants, on which chains, and how to detect the
   wrong one at deposit time (hand-off to sheet 2's token-verification hazard).
5. **CCTP and native cross-chain transfer** — burn-and-mint as a structurally different design
   from lock-and-mint: no wrapped asset, no bridge honeypot, the issuer's attestation service as
   the trust anchor and the availability dependency that creates. Cover the message flow
   (burn → attestation → mint), the domain model, and the **latency, which is a function of source-
   chain finality — link into sheet 2's table rather than duplicating it**, because that
   dependency is the whole reason the two pages sit next to each other. Then the fast-transfer
   variant and what its speed actually costs (who takes the finality risk, and for what fee).
   Compare against the general token-portability designs — the omnichain-token and cross-chain-
   messaging standards — on trust model, latency and asset fungibility, without ranking them.
6. **On- and off-ramp mechanics** — the three routes (direct mint/redeem with the issuer, an OTC
   or liquidity provider, a public exchange) with their minimums, KYC requirements, cut-off times,
   banking-hours dependency and cost. Then the fiat rails table: ACH, same-day ACH, wire, RTP and
   FedNow, SEPA and SEPA Instant, Faster Payments, SWIFT — with settlement time, operating hours,
   cost, and **reversibility window**, which is the column that matters. State the asymmetry
   plainly: a consumer ACH debit can be returned as unauthorised long after the crypto leg is
   irreversible, so the ramp's fraud exposure is set by the fiat rail's return window, not by
   anything on-chain. Give the controls that follow (hold periods matched to the return window,
   rail selection by risk tier, prefunding).
7. **Settlement finality versus payment finality** — the page's hinge and its sharpest section.
   Three distinct notions: technical finality (the chain — link to sheet 2), legal settlement
   finality (the payment-system law concepts and why they mostly do not attach to a public chain),
   and **practical finality, which for a centralised stablecoin is bounded by the issuer's freeze
   capability.** Document the freeze mechanism concretely: it is a function on the token contract,
   who is authorised to call it, what it does to a balance, whether it can be reversed, and the
   fact that it has been used at scale in response to law enforcement and to hacks. Then the
   consequence table — for each stablecoin class, "when is a received payment safe to treat as
   settled", with the honest answer for freezable tokens being *never unconditionally*, and the
   risk-management response (know your payer, size your exposure, and understand that freeze risk
   is counterparty risk with a different name). Close with the mirror image: the freeze function
   is also the reason recovery is sometimes possible, and the GENIUS Act's requirement that
   permitted issuers *have* such a capability — link to sheet 4.
8. **Treasury float and rebalancing** — the daily operating problem. Inventory targets per chain
   and per venue driven by observed demand; the cost of a rebalance decomposed (transfer fee,
   finality delay, slippage or spread, and the opportunity cost of the in-flight balance);
   rebalance triggers as thresholds rather than schedules; netting before moving; prefunding
   versus just-in-time and the working-capital difference; yield on idle reserves via short-
   duration instruments and tokenised money-market funds, with the honest note that the yield is
   small relative to a single mispriced bridge decision. Include **one worked example** that
   arrives at a real number: a stated daily flow profile across three chains, the resulting
   inventory targets, and the monthly cost of the rebalancing policy versus the cost of the float
   it saves.
9. **Payment operations** — the flows that differ from card payments: refunds (there is no
   reversal, only a new payment, which changes the accounting and the fraud surface);
   over- and under-payment; invoice expiry and the price-window problem when the payer sends a
   non-stable asset; wrong-chain and wrong-variant receipts; and the merchant economics table
   comparing card interchange, wire, and stablecoin rails at several transaction sizes — the
   comparison that actually motivates the whole category, and where the small-ticket answer is
   frequently *not* stablecoins once ramp costs are included. Be honest about that.
10. **Regulatory shape, briefly** — the US permitted-issuer framework and its reserve, redemption
    and AML obligations; MiCA's e-money-token and asset-referenced-token regimes with their
    distinct requirements; and the practical consequence for an operator (which tokens are usable
    in which markets). One short paragraph each, dated, linked to primary text, hand-off to sheet 4
    for the compliance implementation. Not a legal guide.
11. **Common mistakes** (mandatory) — treating a bridged variant as the native asset; treating a
    synthetic or crypto-collateralised token as a fiat-backed one; assuming chain finality equals
    payment finality; sizing hold periods to the chain rather than to the fiat rail's return
    window; a single-issuer treasury; ignoring the attestation/audit distinction; rebalancing on a
    schedule instead of a threshold; quoting a stablecoin rail's cost without the ramp legs;
    building a refund flow that assumes reversal exists.
12. **Related sheets** footer per the cross-link map.

## Volatile-facts register

**Overall: VOLATILE.**
- **§1 issuer card: VOLATILE.** Supply figures, attestation providers, chain coverage and
  regulatory status all move. Supply numbers carry an explicit as-of date, or state them as
  magnitude bands rather than precise figures so they age gracefully — prefer the band.
- **§10 regulatory shape and §7's statutory reference: VOLATILE.** Phase-in dates and issuer
  authorisations change. Date every claim.
- **§5 CCTP: SLOW-DRIFT** — supported domains and protocol versions change; date the section and
  link to the issuer's own documentation for the live domain list rather than enumerating it in a
  way that will rot.
- **§6 fiat rails: SLOW-DRIFT** — instant-payment scheme coverage and limits change; return
  windows are stable.
- **§3 depeg register and §4 bridge-hack register: APPEND-ONLY.** They never rot.
- **§2 reserve taxonomy, §7 finality argument, §8 treasury method, §9 payment ops: STABLE.**
Semi-annual freshness target, with §1 and §10 as the check targets.

## Index category

`Crypto Custody & Compliance`.

## Reading conditions

**Desk, building a business case or a design.** Numbers will be lifted into a spreadsheet.
Consequences: every table must be copyable text with consistent units and explicit as-of dates,
the worked examples must show their inputs so the reader can substitute their own, and the fee
comparison must state every assumption inline rather than in a footnote. Mobile is a real
secondary case for the issuer card and the depeg register (both read like reference cards) — those
two must be excellent at 375 px. Print: the issuer card and the finality/freezability table on one
page each.

## Cross-link map

- **Internal outbound:** `blockchain-deposits-withdrawals.html` (sheet 2 — finality, referenced
  not restated, and the token-verification hazard), `crypto-compliance-architecture.html`
  (sheet 4 — issuer freeze obligations and the statutory frame),
  `institutional-crypto-custody.html` (sheet 3 — treasury float shares the inventory math with the
  hot-wallet float; make the connection explicit, it is a genuine insight),
  `crypto-exchange-architecture.html` (sheet 7), `bitcoin-exchanges-cards.html`,
  `currency-timeline.html` (the monetary-history adjacency, one line).
- **Reciprocal inbound:** one line from sheet 2's finality table ("what this means for a stablecoin
  transfer") and one from `bitcoin-exchanges-cards.html`.
- **External outbound:** issuer documentation and published attestation reports for reserve
  claims; the issuer's own protocol documentation for burn-and-mint mechanics; central-bank and
  scheme operator documentation for the fiat rails; primary statutory and regulatory text for §10;
  incident post-mortems for every bridge-hack and depeg row. No market-data aggregator as the sole
  source for a supply figure — cite the issuer's own transparency page.

## og:image / shareable artifact

The **finality-versus-freezability table** at 1200×630: stablecoin class down the side, and across
the top — chain finality, issuer freeze capability, redemption right, and "when is it settled" —
with the semantic scale. It carries the page's one non-obvious idea. The issuer card is the
screenshot-this block.

## Jurisdiction scope

**Global with a US and EU focus, stated once.** Issuer regulatory status is inherently
jurisdictional and is handled in the §1 card's status column plus §10; the rest of the page is
mechanics and is universal. One disclaimer, once: nothing here is legal or investment advice, and
issuer risk statements are descriptions of publicly documented mechanisms, not assessments of any
issuer's solvency. Per README Rule 4, say it once and move on — and per the batch rule, name
issuers factually and do not rank them.

## Density targets

Issuer card ≥ 8 stablecoins × 8 attributes. Depeg register ≥ 8 dated events. Bridge-hack register
≥ 6 dated incidents with amounts and root causes. Cross-chain transport comparison ≥ 4 designs × 5
columns. Fiat rails table ≥ 7 rails × 5 columns including the reversibility window. Finality/
freezability table ≥ 5 classes × 4 columns. Treasury section: 1 fully worked example ending in a
real monthly number, plus ≥ 4 rebalance-trigger scenarios. Merchant fee comparison ≥ 3 rails × 3
transaction sizes with all assumptions stated. Common mistakes ≥ 9.

## Research sources (verify against these, per Rule 1)

Issuer transparency pages and the actual published attestation reports — read the report, not the
summary of it, and note the exact scope language. The issuer's own protocol documentation for
cross-chain transfer mechanics and supported domains. Primary statutory text for the US stablecoin
framework and MiCA Titles III and IV. Central bank and payment scheme documentation for rail
settlement times and return windows (NACHA rules for ACH returns, the relevant scheme rulebooks
for instant payments). Incident post-mortems and, where available, the chain analysis published at
the time for each bridge hack and depeg. Token contract source for freeze-function claims — read
the contract, because that is the only authoritative statement of who can freeze what.

Experience source, not a citable source: `Paytech-Labs/paytech-platform` implements crypto
payment invoices, multiple payment providers behind one abstraction, and fiat cash payouts —
which is §9's payment operations and §6's ramp mechanics as built code, including the invoice
expiry and price-window problem. Use it to keep §9 honest about what actually breaks in a
payment flow. Per the batch constraint, nothing proprietary appears on the page.

## Visual design

**Identity: the batch register with a treasury-statement inflection** — ruled tables, tabular
figures, and a restrained use of the shared semantic scale (green = final and unfreezable, amber =
final on chain but issuer-freezable, red = not yet final or reversible off-chain). The scale is
doing something genuinely new here — marking *reversibility* rather than safety — so label the
legend explicitly rather than relying on the reader's memory from sheets 2 and 3.

**Signature element: the payment lifecycle bar.** A single inline SVG showing one payment's journey
as a horizontal bar segmented by state — initiated, broadcast, chain-final, issuer-freeze-window,
fiat-return-window closed, economically final — drawn to a real time axis, with the crucial visual
being that the **fiat return window extends far past chain finality**, and that for a freezable
token there is no point at which the bar turns fully green. Overlay three variants (card payment,
wire, stablecoin) on the same axis so the comparison is immediate. This drawing is the page's
argument; it must be the most polished element and must stack cleanly at 375 px with the shared
axis preserved.

No JavaScript. All figures carry as-of dates in the markup adjacent to the number, not only in a
page header, so a screenshotted table is still self-dating.
