# Spec — System diagrams for `crypto-exchange-architecture.html`

**Type:** enhancement spec for a shipped sheet (not a new cheatsheet). Delete this file when
the three figures and two tables below are live and the QA gate at the bottom passes.

**Target file:** `crypto-exchange-architecture.html` (shipped 2026-08-31, `datePublished` stays).
Binding context: `AGENTS.md`, `TODO/README.md` Rules 1–6. This spec adds *only* the diagram
layer and the two tables that make the diagrams legible; it does not restructure the prose.

---

## 1. Why

The sheet currently explains the exchange in six well-written slabs of prose and one small
620×240 system map. A reader can follow any single subsystem and still not be able to answer
the two questions an engineer actually opens this page with:

1. **"What state is my order in, who put it there, and what did that do to my balance?"**
   The order lifecycle is described in five different places (risk holds, sequencer, order
   semantics, STP, client order ID) and drawn nowhere.
2. **"What do I actually store?"** The ledger rules table states seven invariants
   (`Σ postings = 0`, integers, immutable journal, available = total − holds, idempotent
   posting, projections, domain boundary) without ever showing the tables those invariants
   constrain. An invariant with no schema next to it reads as advice.

Both are diagram-shaped problems. This is also the page's weakest spot against the niche
utility test (README Rule 0): prose about matching engines is exactly what an AI chat answers
well; a state machine annotated with hold and ledger effects, and a schema plate you keep open
while writing migrations, is not.

### 1a. What to take from the 2013 source material, and what to reject

David's original design work (the `freethepeople.org` "How to Build a Bitcoin Exchange" series,
and the swimlane / ERD / EDMX diagrams behind it) is the ancestor of this page and is already
cited in Sources. Treat it as **historical input, not a template.** Use your own judgment; the
following calls have already been made:

**Keep (the ideas that aged well):**

- **Swimlanes by trust domain.** The original split UI / Trading Engine / Bitcoin API / Data
  Stores. That partition is still the right one and becomes Figure B's lanes.
- **Status as a first-class, named, published vocabulary.** The original annotated the flow with
  the customer-visible status at each step (`Validating`, `Accepted`, `Processing`, `Executing`,
  `Confirming`, `Complete`, `Cancelled`). Publishing an exact status vocabulary is still correct
  and becomes Figure A.
- **Standing orders / scheduled re-validation as a distinct actor.** Stops and take-profits are
  triggered by a clock-driven process, not by the order-entry path. Figure A keeps this as an
  explicit trigger transition.
- **The re-validate-before-execute step.** Re-checking balance and price between acceptance and
  execution is what stops a stale reservation from overdrawing an account.

**Reject (what 13 years changed):**

| 2013 shape | Why it is wrong now | What replaces it |
|---|---|---|
| `AssetBalance.Balance` / `FrozenBalance` as mutable authoritative rows | Directly violates this sheet's own ledger rules — "Projection: never an authoritative mutable balance row" and "Immutable journal" | Append-only journal + entries; balances are a rebuildable projection with a journal checkpoint |
| Per-order calls into a "Bitcoin API" to `Execute Buy/Sell Order` | Conflates broker/wallet with exchange. A trade between two customers touches no chain | Chain contact only at the five crossings already tabled on the page |
| `Pending (Suspended)` / `Pending Manual Validation` as normal-path order states | Manual approval per order was a 2013 volume and compliance artifact | Compliance screening is a gate inside accept and inside withdrawal, not an order state |
| `InsertDate` / `UpdateDate` / `SaveDate` on every table | Row-mutation timestamps as a substitute for event history | The journal *is* the history; operational tables carry the sequence number that produced them |
| Single-writer implied by a relational transaction | Says nothing about determinism or replay | Explicit sequencer lane and sequence numbers on the wire in Figure B |
| Book state living in SQL (an `OrderBook` table as truth) | Cannot deliver deterministic price-time priority or replay | In-memory book, journal-backed; the durable row is the *order*, not the book |

Say none of this on the page as history. The page shows the current design; the contrast above
is build guidance only.

---

## 2. Targeting (SPEC-AUDIT Tier 1)

- **Search intent.** Secondary-intent capture on an existing URL, not a new page. Target
  phrasings the current page cannot rank for: *crypto exchange order lifecycle*, *exchange order
  status flow diagram*, *order state machine trading*, *exchange ledger schema*, *crypto exchange
  database design*, *double entry ledger schema crypto*, *matching engine data model*.
- **Title / H1 / meta.** Unchanged. The existing `<title>` and description still describe the
  page accurately. Do **not** rewrite metadata for this change. Optionally extend
  `<meta name="keywords">` with `order lifecycle, exchange data model` — nothing else.
- **Reader outcome ("definition of working").** A backend engineer can (a) name every state their
  order system needs, who owns each transition, and the exact hold and ledger effect of each, and
  (b) sketch the table set with correct grain and mutability class, without opening another tab.
  Both diagrams should be screenshot-able straight into a design doc.
- **Success metric.** Figure A becomes the page's shareable artifact (see §7 og:image).
  Secondary: scroll depth past the matching-engine section; the sheet is currently front-loaded.
- **Volatile-facts register.** Low volatility overall. Two things drift: exchange REST status
  vocabularies (Binance / Coinbase / Kraken names) and FIX `OrdStatus` enumerations across FIX
  versions. Date-tag both inline. The state machine's *structure* is not volatile and gets no
  date tag.
- **Index category.** Unchanged — Crypto custody & compliance, engineering reference.
- **Reading conditions.** At a desk, during design or code review, mid-task and scanning. Both
  figures must be readable at a glance without the surrounding prose.

---

## 3. Placement

Three figures. One replaces an existing one; two are new sections. Nav entries and `#anchor` ids
must be added to `nav.sections`.

| # | Where | Action |
|---|---|---|
| **B** | Existing section `#system-map-figure` ("Where the exchange stops being reversible") | **Replace** the current 620×240 SVG with the swimlane plate. It subsumes the existing map — same wallet-boundary point, far more information. Keep the `<h2>` and section note; rewrite the figcaption to match the new content. Do not ship two system maps. |
| **A** | New section `#order-lifecycle`, inserted **after** `#matching-engine`, before `#ledger-design-rules` | Figure A plate + Table A. This is the page's new signature element. |
| **C** | New section `#data-model`, inserted **after** `#ledger-design-rules`, before `#wallet-boundary-crossings` | Figure C plate + Table C. Sits directly under the invariants it gives a schema to. |

Nav order becomes: Quick reference · Matching engine · **Order lifecycle** · Ledger design rules ·
**Data model** · Wallet-boundary crossings · Addressing · Withdrawal pipeline · Proof of reserves ·
Risk/APIs · Mistakes · Sources.

---

## 4. Figure A — Order lifecycle state machine (SIGNATURE ELEMENT)

Build this one first and best (README Rule 5). It is the artifact people screenshot.

**Section H2:** `Order lifecycle` — heading text: *"Every state, and what it does to the money"*.

**Section note (write to this substance):** an order status is a promise to three audiences at
once — the customer reading it in the UI, the API client automating against it, and the ledger
that has to have already moved the corresponding hold. Statuses that mean different things to
those three are where disputes come from. Each transition below names its owner and its exact
balance effect.

### 4a. States (nodes)

Terminal states get `.dg-node.end`, the resting/working states get `.dg-node.on`, transient
in-flight states get plain `.dg-node`, the reject/STP node gets `.dg-node.hot`.

| State | Class | Meaning in one line |
|---|---|---|
| `received` | plain | Accepted at the edge, deduped on client order ID, not yet risk-checked |
| `rejected` | hot/end | Failed validation, risk, or STP. Never entered the book, never took a sequence number on it |
| `pending_new` | plain | Sequenced, hold placed, awaiting matcher acknowledgement |
| `working` | on | Resting on the book with a price-time queue position |
| `partially_filled` | on | Some quantity executed, remainder still resting and still held |
| `filled` | end | Fully executed. Hold released, journal posted |
| `cancelled` | end | Customer or system cancelled the remainder. Residual hold released |
| `expired` | end | Time-in-force elapsed (GTD/DAY) or an IOC/FOK remainder killed on arrival |
| `pending_cancel` | plain | Cancel accepted at the edge, not yet acknowledged by the matcher |
| `untriggered` | plain | Stop / take-profit held off-book until the trigger condition fires |

Ten states. Do not add more: if a candidate state does not change the hold, the ledger, or what
the client may do next, it is a field, not a state.

### 4b. Transitions (edges) — every edge labelled with **owner** and **effect**

Draw the labels. An unlabelled arrow is the exact failure this figure exists to prevent.
Minimum edge set:

- `received → rejected` — owner: risk/compliance — effect: **no hold, no journal**
- `received → pending_new` — owner: risk — effect: **hold placed (available decreases)**
- `pending_new → working` — owner: sequencer/matcher — effect: none (hold already placed)
- `pending_new → rejected` — owner: matcher — effect: **hold released** (post-only would cross; STP)
- `working → partially_filled` — owner: matcher — effect: **journal posting per fill; hold reduced by the filled quantity**
- `working → filled` / `partially_filled → filled` — owner: matcher — effect: **final posting, hold zeroed**
- `working | partially_filled → pending_cancel → cancelled` — owner: customer, then matcher — effect: **residual hold released on the matcher's acknowledgement, not on the request**
- `working → expired` — owner: TIF clock / scheduled task — effect: **residual hold released**
- `untriggered → pending_new` — owner: trigger evaluator (mark price) — effect: **hold placed at trigger time, not at submission**
- `partially_filled → cancelled` — owner: customer — effect: **filled quantity stays filled; only the remainder is released**

Three annotations placed as `.dg-no` / `.dg-acc` text, not as nodes:

1. On the cancel path: **"cancel is a request, not a result"** — the race against an incoming fill
   is resolved by the sequencer, and the customer may get a fill after they hit cancel.
2. On the reject path: **"reject before the sequence number, or you have printed a trade you
   cannot recall"** (ties to the existing STP entry).
3. Under `untriggered`: **"a stop is not on the book; it holds nothing until it triggers"** — the
   reason a stop can fail on insufficient funds at the worst possible moment.

### 4c. Geometry and rendering

- `viewBox="0 0 900 430"`, `role="img"`, `aria-labelledby` pointing at a `<title>` / `<desc>` pair
  with unique ids (`ol-t` / `ol-d`) — match the existing `ex-t` / `ex-d` convention.
- Reuse the existing `@layer diagram` classes verbatim (`.dg-node`, `.on`, `.end`, `.hot`,
  `.dg-flow`, `.dg-cap`, `.dg-lbl`, `.dg-ok`, `.dg-no`, `.dg-acc`). **Add no new color tokens.**
  One new class allowed: `.dg-edge{font:500 8px var(--mono);fill:var(--faint)}` for edge labels,
  declared inside `@layer diagram`.
- Marker: define a new arrowhead id (`arOL`). Do not reuse `ar` across figures in one document.
- Left-to-right main spine (`received → pending_new → working → filled`), rejects dropping below
  the spine, cancels and expiries rising above it, `untriggered` entering from the lower left.
- This plate is wider than the existing 44rem cap. Add `figure.plate.wide svg{max-width:60rem}`
  and wrap the SVG in `.plate-scroll{overflow-x:auto}` so 375px gets a horizontal scroll rather
  than 6px type. Give the scroll container `role="region" tabindex="0"` and an `aria-label`,
  matching how `.table-wrap` is already handled.
- `<desc>` must carry the full state list and the three annotations in prose. Table A is the real
  fallback, but the desc has to stand on its own.

### 4d. Table A — state contract (row list)

Immediately under the figure, inside `.table-wrap` with `role="region" tabindex="0"`. Every
`<tr>` carries `data-f` so the page filter works.

Columns: **State · Set by · Hold effect · Journal effect · Client may · FIX `OrdStatus` (39)**

Rows: one per state in 4a, in the same order (10 rows).

Fully-populated exemplar row (final depth — this is the bar for the other nine):

> **`partially_filled`** · Set by: matcher, on each execution · Hold effect: hold reduced by the
> executed quantity; the unfilled remainder stays held · Journal effect: one balanced posting per
> fill — buyer's quote liability down, base liability up, taker fee to the fee account, all inside
> the same transaction · Client may: cancel the remainder; may **not** assume the remainder is safe
> from a further fill in the same instant · FIX `OrdStatus`: `1` (Partially filled) *[VERIFY]*

### 4e. Explicitly out of scope for Figure A

No margin or liquidation state machine — positions are a different lifecycle; one line pointing at
the existing Risk section, then move on (README Rule 4). No withdrawal state machine — that is
Figure B's lower half plus the existing withdrawal-pipeline section.

---

## 5. Figure B — End-to-end swimlane (replaces the current system map)

**Purpose:** one plate showing all three flows the exchange runs, so the reader sees that two of
them never touch a chain and one of them is irreversible.

**Lanes (rows), top to bottom:**

1. **Client** — REST · WS · FIX
2. **Risk & compliance** — holds, limits, STP, screening
3. **Sequencer & matcher** — the single writer
4. **Ledger** — the only authority on customer liability
5. **Wallet & signing** — policy, approval, key material
6. **Chain** — below the heavy boundary line

**Flows (paths across the lanes), left to right:**

- **Deposit:** chain → wallet observes → finality policy → compliance screen → ledger credit →
  client sees balance. The client lane is the *last* thing to happen, not the first.
- **Trade:** client → risk hold → sequencer → matcher → ledger settle → client. **No lane 5 or 6
  contact at all.** Make this visually obvious — it is the single most important thing the figure
  teaches.
- **Withdrawal:** client → risk/compliance → ledger hold + debit → wallet approval → signer →
  broadcast → chain → ledger closes the in-flight entry. Crosses the boundary once, downward.

**The boundary:** keep the heavy `.dg-cross` rule and the label
`WALLET BOUNDARY · the only crossing onto a chain`, now sitting between lanes 5 and 6. Keep the
existing red annotation about halting withdrawals before explaining the difference.

**Geometry:** `viewBox="0 0 900 460"`. Lane labels in a left gutter (~110px) set horizontally
inside a `.dg-field` band. Same `.plate.wide` + `.plate-scroll` treatment as Figure A. New
arrowhead ids (`arDep`, `arTrd`, `arWdr`) — reusing `ar` becomes a document-level id collision
once three figures share the page.

**Distinguishing the three flows without new colors:** vary stroke treatment, not hue — deposit
`.dg-flow` plain, trade `.dg-flow` at heavier stroke-width, withdrawal `.dg-flow` plus
`stroke-dasharray`. Add a small inline key. This stays legible in both themes and in print and
stays inside the existing token set.

**Figcaption:** rewrite. Substance: a trade is two ledger rows; a withdrawal is a broadcast nobody
can take back; the wallet boundary is where "correct it with another row" stops being an option.

---

## 6. Figure C — Data model plate + Table C

**Section H2:** `Data model` — heading text: *"What you actually store"*.

**Section note (substance):** the invariants above are only real if the schema can enforce them.
Four mutability classes, and nothing may sit in the wrong one: **append-only** (the journal),
**derived** (projections, always rebuildable), **operational** (mutable working state that is never
a source of truth about money), **reference** (slow-moving lookups).

### 6a. The plate

`viewBox="0 0 900 420"`. Four labelled bands using `.dg-field`, one per mutability class, with
entity boxes inside. **Not** a classical crow's-foot ERD: the mutability class carries more design
weight than the cardinality, and crow's feet do not survive 375px. Draw relationships as plain
`.dg-flow` lines with a `1` / `n` label only where the cardinality is load-bearing.

**Append-only band:** `journal_transaction` (id, sequence, business event, idempotency key) →
`journal_entry` (transaction id, account id, asset, signed integer amount in minor units).
Annotate with `Σ amount = 0 per transaction per asset` as `.dg-ok`.

**Derived band:** `account_balance_projection` (account, asset, total, held, journal checkpoint).
Annotate as `.dg-acc`: **"rebuildable from the journal — if it disagrees, the journal wins"**.

**Operational band:** `order` (durable order record, current state, client order ID unique per
account), `fill`, `hold`, `withdrawal_request`, `deposit_observation`, `chain_transaction`,
`outbox`. Annotate: **the book itself is not here** — it lives in memory and is rebuilt from the
command log; the durable artifact is the order, not the book.

**Reference band:** `account` (chart of accounts: customer liability, firm position, fee income,
in-flight, asset location per wallet tier), `asset` (decimals, minor unit), `market` (tick size,
lot size, minimum notional).

Two annotations, both `.dg-no`:

1. Across the operational → derived edge: **"no service writes a balance; services post
   transactions"**.
2. Under `outbox`: **"the ledger commit and the outbox row are one transaction, or the chain and
   the books will disagree at exactly the wrong moment"**.

### 6b. Table C — table contract (row list)

Columns: **Table · Grain (one row per…) · Mutability · Written by · Invariant it carries**

Rows (13, in band order): `journal_transaction`, `journal_entry`, `account`, `asset`, `market`,
`account_balance_projection`, `order`, `fill`, `hold`, `deposit_observation`, `withdrawal_request`,
`chain_transaction`, `outbox`.

Fully-populated exemplar row:

> **`hold`** · Grain: one row per reservation against one account and asset, keyed to the order or
> withdrawal that caused it · Mutability: operational — the amount decreases on partial fill and
> the row closes on release; never deleted · Written by: risk engine on placement, matcher on fill
> or cancel, withdrawal service on approval · Invariant: `available = total − Σ open holds`, and a
> hold may only be released by the subsystem that placed it.

### 6c. Explicitly out of scope

No DDL, no index strategy, no partitioning, no vendor ("use Postgres", "use TigerBeetle"). Types
only where the type *is* the invariant (signed integer minor units). No API schema.

---

## 7. Supporting changes

- **`nav.sections`:** add `#order-lifecycle` and `#data-model` links in the positions in §3.
- **Quick-reference instrument panel:** the `Stages` tile currently reads `6 · client → wallet
  boundary`. Add one tile: `States · 10 · published vocabulary`. Do not exceed 7 tiles — the grid
  degrades past that.
- **og:image:** `images/crypto-exchange-architecture.png` should be regenerated from **Figure A**
  once built (it becomes the shareable artifact). The existing `og:image:alt` describes the old
  system map and must be updated to match. If the image cannot be regenerated in this pass, leave
  both alone rather than shipping a mismatched alt.
- **Cross-links:** Figure B's withdrawal path gets one inline link to
  `blockchain-deposits-withdrawals.html`; Figure C's chain and deposit entities get one to the
  same. No new entries in the Related aside — it is already at nine.
- **CSS additions (all inside the existing `@layer diagram`, no new tokens):**
  `.plate-scroll{overflow-x:auto}`, `figure.plate.wide svg{max-width:60rem}`,
  `.dg-edge{font:500 8px var(--mono);fill:var(--faint)}`.
- **Print (`@layer print`):** the two wide plates must not clip. Either let them shrink to page
  width or set `break-inside:avoid` and render the scroll container at full width. Check a print
  preview; a clipped state machine is worse than no state machine.
- **Filter compatibility:** the page filter hides any `.sheet-section` whose `[data-f]` units are
  all hidden. Figures carry no `data-f`, so put `data-f` on table rows only and confirm a query
  matching nothing in the new sections hides them cleanly rather than leaving an orphaned figure.

---

## 8. Facts to verify before building (README Rule 1 — everything below is an anchor, not a fact)

| Claim | Verify against |
|---|---|
| FIX `OrdStatus` (tag 39) values used in Table A — `0` New, `1` Partially filled, `2` Filled, `4` Canceled, `6` Pending Cancel, `8` Rejected, `9` Suspended, `A` Pending New, `C` Expired | FIX Trading Community standards (already in Sources). Cite the FIX version explicitly; values differ across versions |
| That major venues publish these state names — Binance (`NEW`, `PARTIALLY_FILLED`, `FILLED`, `CANCELED`, `PENDING_CANCEL`, `REJECTED`, `EXPIRED`, `EXPIRED_IN_MATCH`), Coinbase Advanced Trade, Kraken | Each venue's current first-party API docs. Date-tag as "as of <Mon YYYY>". If a name cannot be confirmed first-party, drop that venue rather than approximating |
| Two-phase / pending-transfer semantics behind the `hold` design (reserve → post or void, with timeout) | TigerBeetle two-phase transfer docs, or the equivalent primitive in another first-party ledger reference. Describe the *pattern*; name no vendor on the page |
| Time-in-force behaviours mapped to `expired` (GTC, GTD, DAY, IOC, FOK) | FIX `TimeInForce` (tag 59) plus one venue's docs |
| Any decimal / minor-unit claim (BTC 8, ETH 18) | The page already asserts these; re-confirm, do not re-derive |

If a FIX value cannot be confirmed, ship Table A without the FIX column rather than guessing. The
column is a nice-to-have; the hold and journal columns are the point.

---

## 9. Anti-goals

- No JavaScript in any figure. No pan/zoom widget, no clickable state machine, no tooltips beyond
  the existing `abbr.term` pattern used in prose. The page's interactivity budget is already spent
  on the filter and the theme toggle.
- No new color tokens, no new fonts, no gradients or drop shadows on the plates. The sheet's
  identity is flat technical plate; three figures in three styles would wreck it.
- No mermaid, no external diagram library, no build step (AGENTS.md: standalone single file).
- No history lesson on the page about the 2013 design — §1a is build guidance only.
- No vendor names, no "we recommend X".
- Do not restate in the new sections what the existing tables already say. Figure C is a schema for
  the ledger rules table; it must not re-explain the rules.

---

## 10. Definition of done

In addition to `AGENTS.md`'s checklist and README Rule 3:

- [ ] Three figures live: A (new, signature), B (replacing the old system map — the old 620×240
      SVG is **gone**, not kept alongside), C (new).
- [ ] Every one of Figure A's ten states appears in both the plate and Table A under the same name,
      and every transition in 4b is drawn with an owner and an effect label.
- [ ] Table A and Table C each meet the exemplar-row depth given above for **every** row — no
      thinned rows below the fold.
- [ ] Figure C's four mutability bands are all populated, and every entity in Table C appears in
      the plate.
- [ ] Unique SVG marker / `title` / `desc` ids across all three figures — no collisions with the
      existing `ar` / `ex-t` / `ex-d`.
- [ ] Both wide plates scroll horizontally at 375px with legible type; nothing overflows `body`.
- [ ] Print preview: no clipped figure.
- [ ] `nav.sections` updated; both new anchors scroll correctly under the sticky offset.
- [ ] Page filter: a term hitting only the new tables hides the other sections and leaves no
      orphaned figure.
- [ ] Light and dark themes both checked, including annotation text colors.
- [ ] The repo SEO/validation gate passes; `datePublished` unchanged; no visible "Last verified"
      line introduced.
- [ ] `refresh-status.json` untouched by hand.
