# Spec: Custody provider integration patterns — vaults, policy engines, webhooks, build vs buy

**Target file:** `custody-provider-integration.html`
**Batch:** [custody-engineering-batch-2026-08.md](custody-engineering-batch-2026-08.md) (sheet 6 of 9, P1).
**Read the batch file's "Sheet 6 names Fireblocks, and covers more than Fireblocks" section before
writing a line of this.** Fireblocks is named throughout, its terminology is used directly, and it
gets a section of its own; the accuracy and citation rules there are binding.

## Why this topic

Fireblocks' developer documentation is good and thorough, and it is also written from entirely
inside the Fireblocks model — as is every competitor's. Each assumes you have already chosen, and
none of them tells you which of its concepts are Fireblocks inventions and which are the shape that
every custody platform converges on. What does not exist is the **cross-vendor integration-patterns
reference**:
the handful of structures every custody platform converges on — an account/vault hierarchy, a
declarative transaction-authorisation policy, an out-of-band co-signer, a webhook stream with
at-least-once delivery, a transaction state machine, and an automated native-asset funding
mechanism — described once, generically, with each vendor's naming mapped onto it.

That page is useful in both directions. Choosing a platform: you can compare on the structures
rather than on the marketing. Integrating with one: you can predict which problems you are about
to have, because they are the same six problems on every platform. **Webhooks arrive at least
once, out of order, and sometimes not at all; therefore the webhook is a hint and the reconciler
is the source of truth** — that is the single most important sentence in this subject and no
vendor's quickstart says it.

The build-versus-buy frame closes it, and it is honest in a way vendor content cannot be: buying a
custody platform removes the signing problem and roughly none of the ledger, reconciliation,
deposit-detection or compliance problems. Sheets 2, 3 and 4 do not go away.

One thing this page must be straight about, because it is what makes it trustworthy: it compares
**documented capabilities**, not operating experience. The author has built and run provider
integrations of exactly this shape (see the research-sources note) but has not personally operated
every platform in the comparison table. State that once, plainly, in an "about this page" line —
it costs nothing, it is what an honest technical reference does, and a reader who spots an
unearned claim of experience discards the whole page.

## Targeting

- **Primary query:** `fireblocks integration`
- **Secondary:** `fireblocks transaction authorization policy`, `fireblocks webhook verification`,
  `fireblocks api co-signer`, `fireblocks vault account structure`, `fireblocks vs bitgo vs copper`,
  `custody platform integration patterns`, `custody build vs buy crypto`,
  `crypto custody api webhook verification`, `crypto gas station automation`
- **Note on the primary:** the vendor-shaped queries carry the volume and the intent — someone
  typing `fireblocks webhook verification` has a bug open right now. The generic queries carry the
  durability. The page serves both by using Fireblocks' own vocabulary in the headings and the
  generic model in the structure, so it ranks for the vendor terms without being obsolete when the
  vendor landscape shifts.
- **Mode:** operational, mid-integration or mid-evaluation. Entered at a specific section (webhooks,
  policy, statuses) from a specific problem.

## Draft title / H1 / meta

- `<title>`: `Fireblocks Integration Patterns: Vaults, TAP, Webhooks` (54 chars)
- **H1:** `Custody Provider Integration Patterns: Fireblocks and the Model Underneath It`
- **Meta description (draft):**
  `Fireblocks vault accounts, Transaction Authorization Policy, the API co-signer callback and webhook delivery semantics, mapped onto the generic model every custody platform shares. With build vs buy.` (198 chars)
- **Filename stays `custody-provider-integration.html`.** The title leads with the vendor because
  that is the query; the canonical URL stays generic because it is permanent and the page outlives
  any one platform. If the vendor terms clearly carry the page after six months of Search Console
  data, revisit — but a URL is the one thing that cannot be cheaply changed later.

## Reader outcome

The reader can integrate with a custody platform without the four mistakes that cost everyone a
week (trusting webhook ordering, no signature verification, no reconciliation loop, no idempotency
key), read any vendor's API documentation by mapping it onto the generic model, and make a
build-versus-buy decision on the axes that actually differ rather than on price alone. Acceptance
test: they can describe what their system does when a webhook for a completed withdrawal never
arrives — and the answer is a procedure, not a shrug.

## Success metric

Deep links to the webhook-semantics and state-machine sections from integration work; reuse of the
build-vs-buy scorecard in evaluation documents. Goal-2 signal: demonstrates fluency in the
operational reality of these platforms. Not a traffic page.

## Content approach

Generic model first, vendor mapping second, decision frame last. **The generic model is the
skeleton; Fireblocks' vocabulary is the flesh.** Use Fireblocks' actual terms in the prose and
headings — a reader searching `transaction authorization policy` should land on a heading that says
it — while the section structure stays generic so the page survives an API revision and so a Copper
or BitGo reader can still use it. Every Fireblocks-specific assertion is dated and cited to the
developer docs.

1. **Quick reference: the six structures** — the concepts every platform implements, each in one
   line, with a cross-vendor naming table beneath. **Fireblocks is the leftmost vendor column and
   the anchor vocabulary**, because it is the one most readers arrive already using: vault account,
   vault asset wallet, internal/external/contract wallet, Transaction Authorization Policy, API
   co-signer, Gas Station. The other columns say what each platform calls the same thing. Signature
   element, and the page's most reusable object — it is what makes any vendor's documentation
   readable once you know one vendor's.
2. **Account and address hierarchy** — the tree (organisation → account/vault → per-asset wallet →
   address) and the decisions it forces: one vault per customer versus an omnibus vault with an
   internal ledger, and the scaling wall the per-customer model hits; permanent versus one-time
   deposit addresses; the distinction between addresses the platform signs for and external
   destinations it merely knows about; and the address-management burden on chains with account
   models versus UTXO models. Cross-reference sheet 7's omnibus-versus-segregated treatment rather
   than duplicating it.
3. **Transaction authorization policy (Fireblocks TAP, and its equivalents)** — the declarative
   rule layer as a generic model: an
   ordered rule list, each rule matching on initiator, source, destination, asset and amount, and
   resolving to allow / block / require-N-approvals. Then the properties that matter and that
   engineers get wrong: **first-match ordering makes rule order a security property**; a
   default-deny terminal rule is mandatory and its absence is the most common misconfiguration;
   changes to the policy must themselves be quorum-gated or the policy is decorative; and the
   policy is only as good as the identity of the initiator, which is an API-key management
   question. Give a worked example policy for a realistic organisation — tiered amounts,
   allowlisted destinations, a break-glass rule — expressed in TAP's actual rule vocabulary
   (initiator, designated signer, source, destination, asset, amount, action) so it is directly
   usable, with a note on which parts of that vocabulary are Fireblocks-specific and which have
   equivalents elsewhere. Then walk an attack through it to show which rule stops it.
   Cross-reference sheet 3, which owns the control design; this section owns the *encoding* of it.
4. **The API co-signer and the callback handler** — the architectural hook that most integrations
   never discover and that is the most interesting thing on the page. Deploying your own co-signer
   with a callback handler means
   a signing request passes through **your** code before the shares act, so you can enforce policy
   the vendor's engine cannot express — business-rule checks, your own risk score, a
   cross-reference against your ledger, a rate limit, a sanity check that the payload matches the
   intent your system recorded. That is the mitigation for sheet 1's "the policy engine is outside
   the MPC boundary" problem, and it belongs here. Cover the deployment models, the availability
   requirement it creates (your callback is now on the critical path for every withdrawal, so its
   uptime is your withdrawal uptime), the fail-open versus fail-closed decision, and the
   attestation/enclave models vendors use to protect the signing environment — for Fireblocks, the
   enclave-based co-signer and the choice between a hosted and a self-deployed co-signer, described
   from the documented architecture and dated. Name the equivalent hook on the other platforms
   where one exists, and say plainly where one does not, because its absence is a real
   differentiator that no comparison table usually captures.
5. **Authentication and request semantics** — API key classes (signing versus read-only versus
   admin) and why they must be separate credentials with separate storage; request signing
   patterns (a signed token over a hash of the request body with a nonce and a short expiry) and
   the clock-skew failure that follows from a short expiry; rate limits and how to be a good
   client; and **idempotency**: a client-supplied external identifier on every transaction
   creation, so a retry after a timeout returns the original transaction rather than creating a
   second one. State the rule plainly: a create call that times out has an unknown outcome, and
   only an idempotency key makes the retry safe.
6. **Webhook delivery semantics** — the section engineers arrive for, and the one that should be
   the most quotable on the page. The guarantees are: **at least once, not exactly once; no
   ordering guarantee; and delivery can fail entirely.** Therefore the consumer must be idempotent,
   must tolerate a status regressing in arrival order (handle by comparing against your own
   recorded state and ignoring stale transitions, not by assuming monotonicity), and must be
   backed by a polling reconciler that is the actual source of truth. Then: signature verification
   over the **raw request body** — verify before parsing, never after, and never trust an event
   because it arrived at your URL; retry and backoff behaviour; the endpoint's latency budget
   (acknowledge fast, process asynchronously); replay protection; and the runbook for a webhook
   outage. Include a short, correct verification snippet in pseudocode that shows the raw-body
   requirement, since that is the detail most implementations get wrong.
7. **Transaction state machine** — the lifecycle as a diagram plus a table, using Fireblocks'
   documented status names as the reference vocabulary because they are the most widely encountered:
   submitted, pending authorisation, queued, pending signature, broadcasting, confirming, completed,
   and the terminal failure states (rejected by policy, blocked by compliance, cancelled, failed on
   chain). Verify the exact status strings against the current API reference — they are enum values
   and getting one wrong makes the table actively harmful. For each
   state: who can move it, whether it is terminal, whether funds are committed, and what your
   ledger should do on entry. Then the sub-status taxonomy that carries the actual reason for a
   failure, and the operational point: **the interesting information is in the sub-status, and
   most integrations only read the status.** Fireblocks' sub-status taxonomy is the worked example
   here and is worth enumerating properly, since it is the part of the API that turns "the
   withdrawal failed" into something actionable. Map the states onto the vendor naming table
   from §1.
8. **Gas stations and sweeping** — the platform-side answer to sheet 2's gas-station problem.
   Fireblocks Gas Station is the named example: automated native-asset funding of vault deposit
   addresses with a configured threshold and cap, the documented chain coverage and its limits, and
   the
   failure modes (the gas station itself running dry at the worst moment, funding races, and the
   cost of funding addresses that never get swept). Sweeping configuration and the interaction
   with the address model from §2. Link to sheet 2 for the underlying problem rather than
   restating it.
9. **Platform comparison** — a factual table, built under the batch rule: no ranking, no
   superlatives, no pricing, every claim dated and cited to that vendor's public documentation.
   Rows named explicitly: **Fireblocks**, Copper, BitGo, Anchorage, Coinbase Prime/Custody, Zodia,
   Cobo, Dfns, Turnkey, Privy, Safe as the smart-contract-wallet option, and the open-source
   threshold-signing libraries as the self-build row. Verify each is still operating and still
   publishing docs before including it. Columns: custody model
   (who holds what), signing scheme family, self-hosted co-signer available, policy expressiveness,
   webhook and API surface, chain coverage approach, regulatory posture (charter/licence type,
   stated as fact), **key exportability and exit package**, and integration effort class. The
   exportability column is the one nobody publishes and the one that matters most in five years.
10. **Build versus buy** — the decision frame, stated honestly in both directions. What buying
    removes: threshold-signing implementation and its audit burden, chain integration velocity,
    HSM/enclave operations, some insurance and regulatory posture. What buying does **not**
    remove: the ledger, deposit detection, the reconciler, nonce and UTXO management, compliance
    screening placement, the withdrawal pipeline, and support operations — that is, most of
    sheets 2, 3, 4 and 7. Then the cost model shape (per-asset-under-custody versus per-transaction
    versus platform fee, and how each behaves as you scale — without quoting numbers), the
    lock-in analysis driven by §9's exportability column, the latency question, and the concrete
    decision guidance: buy when…, build when…, hybrid when… — where the hybrid (buy the hot tier,
    self-custody the cold tier) is the answer for more institutions than either pure position.
11. **Integration checklist** — printable. The things that must exist before go-live: idempotency
    keys, raw-body signature verification, an out-of-order-tolerant consumer, a polling reconciler
    with a defined cadence, separate key classes, a default-deny policy rule, a tested co-signer
    failover, an alert on webhook silence, a tested exit/export, and a runbook for a stuck
    transaction.
12. **Common mistakes** (mandatory) — trusting webhook order; verifying a signature over the parsed
    body; no idempotency key on create; treating webhooks as the source of truth; a policy without
    a terminal deny rule; one API key for everything; reading status without sub-status; a
    co-signer callback that fails open; never testing the export; assuming the platform reconciles
    for you.
13. **Related sheets** footer per the cross-link map.

## Volatile-facts register

**Overall: VOLATILE on the vendor-specific layer, STABLE underneath — and the page is deliberately
structured so those two layers can be updated independently.**
- **§1 naming table, §3 TAP vocabulary, §7 status and sub-status enums, §8 Gas Station chain
  coverage, §9 comparison: VOLATILE.** APIs, product names, enum values and feature matrices change
  on vendor release schedules, and Fireblocks ships frequently. Every vendor-specific cell carries
  an inline "as documented <Mon YYYY>" tag. **The status and sub-status enums in §7 are the single
  highest-risk content on the page** — a stale enum value silently breaks a reader's integration —
  so re-verify those against the current API reference at every freshness pass, not just annually.
  If a vendor's documentation is no longer public, remove the row rather than carrying stale
  claims.
- **§9 regulatory posture column: VOLATILE.** Charters and licences change.
- **§2–§8 generic models, §10 decision frame, §11 checklist, §12 mistakes: STABLE.** These are
  properties of the problem and will outlive every API on the page — which is why they are written
  vendor-neutrally.
Semi-annual freshness target, §9 as the check target. **Never let a vendor row assert a capability
without a dated citation**; that is the whole basis on which this page is defensible.

## Index category

`Crypto Custody & Compliance`.

## Reading conditions

**Second monitor, vendor documentation open on the first, code in an editor.** The reader is
translating between this page's generic model and a specific API. Consequences: the §1 naming table
is the most important element for that use and must be readable without scrolling horizontally on
a laptop; every section needs an anchor because this page will be linked at section granularity in
code review; pseudocode must be selectable monospace. The integration checklist prints. Mobile is
low priority but the checklist and the common-mistakes list must work at 375 px, because those are
what get read on a phone before a meeting.

## Cross-link map

- **Internal outbound:** `mpc-wallet-architecture.html` (sheet 1 — the signing primitive these
  platforms implement, and the trust-boundary problem §4 answers),
  `institutional-crypto-custody.html` (sheet 3 — the control design §3 encodes),
  `blockchain-deposits-withdrawals.html` (sheet 2 — the gas station and reconciliation problems
  §8 and §6 reference), `crypto-compliance-architecture.html` (sheet 4 — the screening gate inside
  the policy), `crypto-exchange-architecture.html` (sheet 7 — the ledger that buying does not
  replace).
- **Reciprocal inbound:** one line from sheet 1's due-diligence checklist and one from sheet 3's
  DR section (vendor-failure exit).
- **External outbound:** each vendor's own public developer documentation, cited per claim and
  dated. Standards where relevant (webhook signature practice, JWT). **No vendor blog posts,
  comparison pages published by vendors, or analyst reports** — the first two are marketing and
  the third is usually paywalled and unverifiable.

## og:image / shareable artifact

The **six structures** table from §1 at 1200×630 — the generic concept in the left column,
Fireblocks' vocabulary in the anchor column, and the other platforms across the top. It is the
page's most reusable object and reads at card size.
The webhook-semantics block ("at least once, out of order, sometimes never") is the
screenshot-this text artifact.

## Jurisdiction scope

Technical and global. The only jurisdictional content is §9's regulatory-posture column, which
states facts about vendors' licences and charters with citations and dates, and makes no assessment
of what a reader's own obligations are — that is sheets 3 and 4. One line saying so.

## Density targets

Naming table ≥ 6 concepts × ≥ 5 platforms. Policy section: 1 worked policy of ≥ 6 rules plus ≥ 3
attacks walked through it. Webhook section ≥ 8 semantics/failure points plus 1 verification
snippet. State machine ≥ 10 states × 4 attributes, plus ≥ 8 failure sub-statuses. Platform
comparison ≥ 8 platforms × 9 columns, every cell dated and cited. Build-vs-buy: ≥ 6 "removed" items
and ≥ 7 "not removed" items, plus 3 decision rules. Integration checklist ≥ 10 items. Common
mistakes ≥ 10.

## Research sources (verify against these, per Rule 1)

The Fireblocks developer portal and API reference first and in the most depth — read the current
docs directly for vault structure, TAP rule grammar, co-signer deployment models, webhook event
types and signature verification, Gas Station configuration, and the full transaction status and
sub-status enumerations. Then each other platform's own public developer documentation and public
API reference, read directly and cited per claim with the date read. Public regulatory registers for the charter/licence column
(the regulator's register, not the vendor's about page). Open-source threshold-signing repositories
for the self-build row. RFC 7519 and current practice guidance for request-signing patterns.
**Nothing sourced from a private account, a dashboard, a sales conversation, a contract, or any
material under NDA** — the page must be reproducible by any reader from public documents, which is
both the accuracy standard and the legal one.

Experience source, not a citable source: `Paytech-Labs/paytech-platform` implements a swappable
payment-provider abstraction over several third-party providers, each with its own webhook
controller and its own background monitor job that polls for state the webhooks did not reliably
deliver. That is §1's generic-model-plus-vendor-mapping argument and §6's
"webhooks are a hint, the reconciler is the source of truth" rule, independently arrived at in
production. It is the strongest evidence behind this page and it must stay evidence: per the
batch constraint, no code, no interface names, no configuration, and no vendor commercial terms
reach the published page. Every claim on the page still has to be verifiable from that vendor's
public documentation.

## Visual design

**Identity: the batch register at its most technical** — this is the sheet that most resembles API
documentation, and it should read that way: heavy monospace, code blocks, state diagrams, sparse
prose. Deliberately the plainest page in the batch. Vendors are named freely in headings, prose and tables — that
is what makes the page findable and usable — but with **no vendor logos, no vendor brand colours
and no brand-styled section headers**: the batch has one visual identity and vendor branding would
wreck it. Fireblocks' terms are set in the same monospace as every other API identifier on the
page, which is exactly the right register for them.

**Signature element: the transaction state machine.** One inline SVG state diagram with the states
as nodes and the transitions labelled with what causes them, drawn in a plain systems-documentation
style, with the terminal failure states grouped and colour-coded on the shared semantic scale, and
— the detail that makes it more than a stock diagram — **each transition annotated with what your
ledger must do when it fires.** That annotation layer turns a diagram into a specification. It must
remain legible at 375 px, which means designing it as a vertical flow with branch-offs rather than
a wide graph; draw the narrow version first.

No JavaScript. The comparison table gets an `overflow-x: auto` wrapper and sticky first column.
