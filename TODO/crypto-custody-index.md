# Spec: Crypto custody cluster hub — the decision-ownership map

**Target file:** `crypto-custody-index.html`
**Parent strategy:** [META-crypto-custody-cluster-seo.md](META-crypto-custody-cluster-seo.md), workstream 3.
Read that doc before this one; it owns the cluster's positioning, the "do not chase vendor
head terms" rule, and the day-30/60/90 measurement gates this page reports into.
**Cluster:** the nine sheets listed in `category-map.php:85-94`.

---

## Rule 0: does this page pass the niche-utility test?

`TODO/README.md` Rule 0 rejects "overview of X" outright, and a cluster index is the most
likely thing in the repo to become exactly that. So resolve it before anything else.

**The rejected shape.** A page whose body is nine blurbs — "MPC wallet architecture covers
threshold signing, DKG, and share topology…" — is a directory listing with a pretty grid. It
loses to the browse view it replaces, it duplicates `llms.txt`, and an AI chat answers
"what should I read about crypto custody" better than it ever will. **Do not build that page.**

**The shape that passes.** Rule 0's accepted list includes *comparison tables with exact specs*
— "where the value is the dense verified numbers side by side, not a narrative" — and *field
diagnostics*. This page passes on the first and carries a small instance of the second:

> The reader is scoping or reviewing a custody design and needs the **complete enumeration of
> operating decisions** their system must answer, marked with **who owns each one under the
> custody model they picked**. That grid is the artifact. It stays open in a second window
> while they write the design doc, fill the vendor questionnaire, or argue with an auditor
> about scope.

Three properties make it a tool rather than a summary:

1. **It is an enumeration, and enumerations are what chat is worst at.** A chat answer gives
   you the four decisions it thought of. The failure mode in custody is the decision nobody
   listed — the gas-funding problem nobody owned, the policy-change control nobody gated. The
   value is completeness against a fixed axis, checked in one glance.
2. **Every row carries a fact the sibling sheets do not state: who owns it, per model.** The
   nine sheets teach *how* each decision works. None of them says "under a qualified custodian
   this one is still yours." That crosswalk exists nowhere in this repo and, per the parent
   SEO doc, nowhere in vendor content either — because publishing "here is everything we do
   not do for you" undercuts a sales motion.
3. **It has a real second use: incident routing.** "A deposit did not credit" and "our seed
   phrase is incomplete" are symptom lookups, and the symptom router (§5) resolves each to one
   sheet and one anchor. That is the field-diagnostics shape, in a compact lane.

**Honest caveat.** This is the weakest Rule 0 pass in the cluster, and the failure mode is
gradual: a matrix cell grows a clause, the clause grows a sentence, and six commits later the
page is the rejected shape. So the spec sets a hard build gate, restated in the anti-goals:

> **No sentence on this page may teach a sibling sheet's content.** Strip every link out of the
> page and no cell should still explain how MPC refresh works, how IVMS101 is structured, or
> what a reorg is. If a cell survives that test as a mini-tutorial, it is a defect.

If a build cannot hold that line, the fallback is not "ship it anyway." It is: cut the page to
the matrix and the symptom router only — two tables, no prose sections — and ship that. Two
dense tables that pass Rule 0 beat nine sections that fail it.

---

## Why this page exists (site-side)

`?cat=Crypto+Custody+%26+Compliance` filters client-side and `index.php:310` emits a canonical
to the site root for every filtered view. The cluster therefore has **no indexable URL**:
nothing ranks for the category head terms, nothing concentrates the internal links the mesh
already builds, and an AI answer engine asked for "a crypto custody reference" has nine URLs
and no front door. This page is the front door, and it is the single target every external link
in workstream 2 of the parent SEO doc points at.

---

## Targeting

- **Primary query:** `crypto custody architecture`
- **Secondary:** `custody model comparison`, `self custody vs qualified custodian`,
  `digital asset custody responsibilities`, `mpc vs multisig vs custodian`,
  `crypto custody reference`, `what does a custodian actually do`
- **Mode:** research-then-return, with a crisis side door. First arrival is a research search
  ("we are choosing a custody model"); the return arrival is a bookmark opened mid-build. The
  crisis lane (§5) is a minority of arrivals but the highest-value ones, so it must be reachable
  in one tap from the top of the page on a phone.
- **AEO target:** be the URL an answer engine cites for "crypto custody reference" and for
  "what stays your responsibility with a custodian." The `ItemList` and the refusals table
  (§7) are the two blocks written to be quotable.
- **Explicitly not targeted:** any vendor-brand query. Per the parent doc's "Do not" list.

## Draft title / H1 / meta

- `<title>`: `Crypto Custody Architecture: Who Owns Which Decision` (52 chars)
- **H1:** `Crypto custody: which decisions stay yours`
- **Eyebrow:** `Crypto custody & compliance · cluster index` (the nine sheets read
  `… · engineering reference`; the differing final word is the only chrome difference)
- **Dek:** `Nine reference sheets, one question first: which of the operating decisions
  below does your custody model hand to a vendor, and which stay yours no matter what you buy.`
- **Meta description (draft, 184 chars):**
  `A vendor-neutral map of digital-asset custody: 34 operating decisions crossed against five custody models, what breaks when nobody owns one, and the reference sheet that resolves each.`

Title and description are derived from the routing angle, not from the category label. Nothing
here says "a collection of guides about crypto custody."

## Reader outcome ("definition of working")

After this page a reader can **name every operating decision their custody design must answer,
say which ones their chosen model hands to a vendor and which stay theirs regardless, and open
exactly one sheet — at the right anchor — for each decision they still owe.** If they arrived
with a symptom instead of a design, they leave with one sheet, one anchor, and one thing not
to do first.

## Success metric

Organic entries on the `crypto custody architecture` family, and — the real test — the hub
becoming the cluster's **top entry page** in GSC while the nine gain entries via internal
links from it. Secondary: the hub URL appearing in AI-answer visibility checks for cluster
queries (parent doc, workstream 4). Report both into the day-60 and day-90 pulls in
`docs/seo-progress.md`. Zero impressions at day 60 on a page with this many inbound links is
a crawl or a canonical problem, not a content problem.

---

## The routing model

Four axes are available — **custody model** (who holds key material), **tier** (hot / warm /
cold / deep cold), **control** (policy, quorum, evidence), and **lifecycle stage** (choose →
build → operate → prove → exit → recover). Offering all four is how a hub becomes a maze.

**Primary axis: custody model.** It is chosen first, it is the most expensive to reverse, and
it is the only axis that partitions the entire cluster — every one of the nine changes meaning
depending on it. Tier and control are *inside* the model (they are what
`institutional-crypto-custody` covers, and the hub must not re-teach them). Lifecycle is an
**ordering**, not a router: it decides the sequence of the matrix bands, and gets one compact
section (§6), but the reader never picks a lifecycle stage to find a sheet.

**The crisis lane is the exception, and it is deliberately not an axis.** Someone whose deposit
did not credit has no interest in custody models. They get a flat symptom → sheet#anchor table
(§5) placed high, linked from the primer, and reachable in one tap. It routes on symptom
strings, nothing else.

So a reader lands in exactly one of two lanes:

| Arrival | Lane | Resolves to |
|---|---|---|
| "We hold customer funds and are choosing a custody model" | Model chooser (§3) → matrix (§4) | One model row, then one sheet per unowned decision |
| "A deposit did not credit" | Symptom router (§5) | `blockchain-deposits-withdrawals.html#reconciliation-break-taxonomy` |
| "Our seed phrase is incomplete" | Symptom router (§5) | `wallet-recovery-forensics.html#recovery-feasibility-triage` |

**The five custody models** (the matrix's columns, and the only place the hub takes a position):

| # | Model | One-line identity |
|---|---|---|
| 1 | Self-custody, single key | One org, one signing key, no quorum |
| 2 | Self-custody, on-chain multisig | Several real keys, the chain enforces the rule |
| 3 | Self-run threshold / MPC | You own the shares and run the signer nodes |
| 4 | Custody platform | Vendor tech and vendor operations; you hold a share or a callback |
| 5 | Qualified / third-party custodian | The vendor holds the keys and the regulatory position |

Five columns is the maximum the matrix can carry at 375 px under the degradation plan below.
Do not add a sixth (no "hybrid" column — hybrids are read as two columns at once, and the
matrix legend says so in one line).

---

## Signature visual element (Rule 5)

**The custody responsibility matrix.** 34 decision rows × 5 model columns, banded into 8
lifecycle groups, every cell a four-state token, every row a deep link, plus one column that
carries the page's only original content: what breaks when nobody owns that decision.

- **Tokens:** `YOU` (danger), `SHARED` (warn), `VENDOR` (safe), `N/A` (muted). Reuse the
  existing `.signal safe|warn|danger` classes from the cluster CSS — do not invent new colors.
  The token set is the visual signature: a reader scanning the "qualified custodian" column
  sees a wall of red where they expected green, and that is the page's argument made visually.
- **The headline number is computed from the matrix, never asserted:** the count of rows that
  are `YOU` or `SHARED` in *every* column. State it in the quick-reference strip and in the
  matrix caption. If the built matrix yields a different number than this spec's anchor of 17,
  the built number wins (README Rule 1 applies to the page's own arithmetic too).
- **Band headers** are full-width `<th colspan>` rows inside the table, sticky under the
  column header.
- **Palette and chrome:** lift the cluster's existing tokens verbatim from
  `institutional-crypto-custody.html` (`--accent: light-dark(#0d6357, #43d1b6)`, `--ink`,
  `--muted`, `--line`, `--safe`/`--warn`/`--danger` and their `-bg` pairs, the mono/serif
  stacks, the `.utility` bar, the `.instrument` strip, `.plate` figures). The hub is the front
  door of a set; it must look like the set. Differentiation comes from the matrix being the
  only full-bleed element on the page, not from a new theme.

### Mobile degradation at 375 px

The matrix is 7 columns wide. `overflow-x: auto` alone is not an acceptable answer for the
page's signature element, so build a CSS-only column switch:

- Five radio inputs above the table, styled as a segmented control ("Which model are you
  evaluating?"), labelled with the model names. No JavaScript.
- Below `640px`: all model columns hidden except the checked one, via
  `#m-mpc:checked ~ .matrix td.c-mpc, … {display:table-cell}` with a `display:none` default on
  `.matrix td[class^="c-"]`. Above `640px` the radios are visually hidden (still focusable is
  unnecessary — hide with `display:none` at that width) and every column shows.
- Below `640px` the "what breaks if unowned" cell reflows to a second line under the decision
  name (`.cell-note`, `display:block`), so a phone reader sees decision → owner token →
  failure with **no horizontal scroll at all**.
- First column (`Decision`) is `position: sticky; left: 0` at all widths, on a solid
  background, for the desktop scroll case.
- Keep the `.table-wrap` `overflow-x:auto` wrapper with `role="region" tabindex="0"` as the
  progressive-enhancement floor: with CSS partially applied the table still scrolls.
- **Print:** the matrix prints as the full grid, landscape, radios hidden, `.cell-note`
  inline. It must fit one landscape page; if it does not, break at a band boundary, never
  mid-band.
- **Acceptance test at 375 px:** switch to "Qualified custodian," scroll the full matrix, and
  read every row's decision, token, and failure line without a horizontal scrollbar appearing.

### og:image / shareable artifact

`images/crypto-custody-index.png`, 1200×630, subject = the matrix cropped to roughly ten rows
across all five model columns, chosen so the token pattern (the red column under "Qualified
custodian") is legible at thumbnail size. Alt: `Custody responsibility matrix showing which
operating decisions stay with the operator under five custody models`. Generate with
`scripts/shot.py` per the existing cluster images.

---

## Section outline

### 1 · Start here (primer) — `#start-here`

Matches the cluster's 2026-09-03 primer convention exactly: `.primer-lead`, four `.pq` question
cards, one `.primer-line` takeaway, all `data-f` filterable. This primer is about **the
cluster**, not about custody — the nine already explain custody, and repeating them here is a
duplicated-content defect.

- Lead: what this page is (a decision map, not a reading list) and how to use it in one move.
- Card 1 — **"Which of these nine sheets do I actually need?"** → answer is the matrix: you
  need the sheets covering the decisions your model leaves with you.
- Card 2 — **"What does buying custody actually remove?"** → it removes the signing primitive
  and its audit burden; it removes approximately none of ledger, deposits, reconciliation,
  compliance placement, or the withdrawal pipeline. (This is the hub's thesis. It echoes the
  `custody-provider-integration` primer's framing at cluster scale — one sentence, no expansion.)
- Card 3 — **"Why is 'who owns this' the first question?"** → because the decisions nobody
  assigned are the ones that cause incidents, and vendor documentation is structured around
  what the vendor does, not around what is left over.
- Card 4 — **"I have an incident, not an architecture question."** → jump link to §5, plus the
  universal first move: record what you know before touching anything.
- Takeaway line: **"A custody model decides who signs. It never decides who is responsible."**

### 2 · Quick reference strip — `#quick-reference`

The cluster's `.instrument` component, six cells, all computed from the page:
`9` sheets · `5` custody models · `34` decisions · `17` yours in every model (anchor — recount
at build) · `8` lifecycle bands · `16` symptom entries. Section note: one line stating that
every figure is a count of this page's own rows, so nothing here needs re-verification.

### 3 · Custody model chooser — `#custody-model-chooser`

**5 rows** (the five models), one screen, placed before the matrix so the reader picks a column
first. Columns:

`Model` · `Who holds signing material` · `What the chain sees` · `The failure you keep` ·
`What you cannot outsource here` · `Start at`

Row list: single key · on-chain multisig · self-run threshold/MPC · custody platform ·
qualified custodian.

Exemplar row at final depth (custody platform):

> **Custody platform** | Vendor infrastructure; you hold a share or a co-signer callback |
> One ordinary signature; the chain records nothing about the arrangement |
> A compromised caller with valid credentials getting a legitimate signature |
> Intent verification in the callback, and the exit package |
> `custody-provider-integration.html#policy-callback--gas-station`

Each `Start at` cell is a deep link to a sibling anchor, not a bare filename.

### 4 · The custody responsibility matrix — `#responsibility-matrix` (signature element)

**34 rows in 8 bands.** Columns: `Decision` · `Single key` · `Multisig` · `Self-run MPC` ·
`Platform` · `Custodian` · `If nobody owns it`. Every decision name links to the sibling
anchor that resolves it.

Row list, by band:

**A · Key material (6)**
1. Key or share generation ceremony and its evidence → `institutional-crypto-custody.html#key-ceremony-script`
2. Signing primitive selection (single key / multisig / threshold) → `mpc-wallet-architecture.html#custody-primitive-decision-matrix`
3. Share topology and quorum choice → `mpc-wallet-architecture.html#share-custody-topology`
4. Share refresh and resharing cadence → `mpc-wallet-architecture.html#key-lifecycle`
5. Backup material and a *tested* restore → `institutional-crypto-custody.html#business-continuity-dual-control--insurance`
6. Signer and approver device integrity → `mpc-wallet-architecture.html#what-mpc-does-not-protect`

**B · Authorization (5)**
7. Transaction policy rule set and terminal default-deny → `institutional-crypto-custody.html#policy-engine-controls`
8. Human approval quorum per value band → `institutional-crypto-custody.html#policy-engine-controls`
9. Policy-change control (who may edit the rules, and after how long) → `institutional-crypto-custody.html#policy-engine-controls`
10. Independent intent verification in the signing path → `custody-provider-integration.html#policy-callback--gas-station`
11. Destination allow-listing and new-address delay → `institutional-crypto-custody.html#custody-tier-register`

**C · Tiering and float (3)**
12. Tier structure and hot-float sizing → `institutional-crypto-custody.html#tiering--float-math`
13. Sweep and rebalance scheduling across the wallet boundary → `crypto-exchange-architecture.html#wallet-boundary-crossings`
14. Velocity limits and value-at-risk policy → `blockchain-deposits-withdrawals.html#value-at-risk-policy-pattern`

**D · Ledger and accounting (4)**
15. Internal ledger as the system of record → `crypto-exchange-architecture.html#ledger-design-rules`
16. Balance representation and per-asset precision → `crypto-exchange-architecture.html#ledger-design-rules`
17. The wallet-boundary invariant, asserted continuously → `crypto-exchange-architecture.html#wallet-boundary-crossings`
18. Proof-of-reserves construction and its liability half → `crypto-exchange-architecture.html#proof-of-reserves-constructions`

**E · Chain operations (7)**
19. Deposit detection and address attribution → `blockchain-deposits-withdrawals.html#deposit-pipeline-figure`
20. Confirmation and finality policy per chain → `blockchain-deposits-withdrawals.html#finality-register`
21. Nonce sequencing and hot-address sharding → `blockchain-deposits-withdrawals.html#evm-nonce-runbook`
22. UTXO selection and change management → `blockchain-deposits-withdrawals.html#utxo-operations`
23. Gas funding for token sweeps → `blockchain-deposits-withdrawals.html#gas-station--deposit-hazards`
24. Withdrawal idempotency and retry semantics → `custody-provider-integration.html#authentication-idempotency--webhooks`
25. Reconciliation and break taxonomy → `blockchain-deposits-withdrawals.html#reconciliation-break-taxonomy`

**F · Compliance (4)**
26. Gate placement relative to signing → `crypto-compliance-architecture.html#gate-placement-rules`
27. Travel Rule transmission and the IVMS101 payload → `crypto-compliance-architecture.html#ivms101-field-map`
28. Ongoing rescreening of already-cleared addresses → `crypto-compliance-architecture.html#kyt-sanctions--data-protection`
29. Blocked-property handling and filings → `crypto-compliance-architecture.html#blocked-property-and-alert-runbook`

**G · Assets held (3)**
30. Issuer, reserve and freeze-authority exposure → `stablecoin-payment-infrastructure.html#reserve-redemption--token-controls`
31. Native versus bridged asset selection → `stablecoin-payment-infrastructure.html#movement-rail-comparison`
32. Depeg and redemption-queue response → `stablecoin-payment-infrastructure.html#treasury-and-incident-checklist`

**H · Assurance, exit and long horizon (2 + the two that follow)**
33. Control evidence and attestation scope (CCSS / SOC) → `institutional-crypto-custody.html#ccss-v9-0-engineering-crosswalk`
34. Vendor exit test and key-export package → `custody-provider-integration.html#platform-due-diligence-register`

*(Band H additionally absorbs, if the build's recount leaves room without breaking the 34-row
target: address-reuse policy and exposure inventory →
`post-quantum-custody-migration.html#quantum-exposure-inventory`, and signature-scheme agility
behind an interface → `post-quantum-custody-migration.html#migration-register`. If the count
exceeds 34, merge rows 8 and 9 rather than dropping a sheet from the matrix — **every one of
the nine must own at least two rows**, or the matrix has stopped being a router for the
cluster.)*

Exemplar row at final depth (row 23):

> **[Gas funding for token sweeps](blockchain-deposits-withdrawals.html#gas-station--deposit-hazards)**
> | `YOU` | `YOU` | `YOU` | `SHARED` | `VENDOR` |
> *Token deposits accumulate in addresses that cannot pay to move them.*

Note the shape: the failure cell is ≤ 12 words, states an outcome, and teaches nothing about
how gas works. That is the density and the discipline for all 34.

Caption under the matrix carries the computed headline number and one line: hybrid designs
read as two columns at once.

### 5 · Symptom router — `#symptom-router` (crisis lane)

**16 rows.** Columns: `Symptom` · `First thing to check` · `Do not do this first` · `Go to`.
Symptom strings are written the way a person types them at 2 a.m., not the way an architect
names them.

Row list: deposit did not credit · deposit credited twice · withdrawal stuck pending ·
withdrawal sent twice · nonce gap blocking every later withdrawal · token stuck in a deposit
address with no gas · balances disagree with the chain · reorg reversed a credited deposit ·
transfer landed in a frozen address · bridged asset will not redeem at par · stablecoin off
peg during a payment run · sanctioned address surfaced after we already sent · Travel Rule
counterparty unreachable · seed phrase incomplete · wallet shows a zero balance · a signer
device or share holder is gone.

Exemplar row at final depth:

> **A deposit did not credit** | Whether the chain shows it confirmed to an address your
> attribution actually owns | Do not re-send, and do not credit manually before the break is
> classified | [Reconciliation break taxonomy](blockchain-deposits-withdrawals.html#reconciliation-break-taxonomy)

Placement: immediately after the quick-reference strip on mobile, so the crisis reader reaches
it in one tap from the primer's card 4. On desktop it may sit after the matrix; use source
order plus the nav bar, not a reordering hack.

### 6 · Lifecycle order of operations — `#lifecycle-order`

**8 rows**, one per matrix band, in build order. Columns: `Stage` · `The band it covers` ·
`The gate that ends it` · `Sheet that governs`. This is an *ordering*, not a second router —
its job is to tell a reader building from zero which band to resolve before which. Keep every
cell to a clause. No prose introduction beyond one section note.

Exemplar gate: *Authorization is done when a test transaction to an unlisted destination is
refused by the policy engine and not by a person.*

### 7 · What this cluster refuses to answer — `#refusals`

**6 rows**, and the single most citable block on the page. Columns: `Question` ·
`Why there is no answer here` · `What you get instead`.

Row list: "which custody vendor is best" · "what does custody cost" · "is our setup compliant
in jurisdiction X" · "when is Q-day" · "can you guarantee my wallet is recoverable" · "is a
proof of reserves proof of solvency."

Exemplar row:

> **"When is Q-day?"** | Nobody has a date, and a page that gave one would be inventing it |
> An exposure inventory you can build this quarter →
> [`quantum-exposure-inventory`](post-quantum-custody-migration.html#quantum-exposure-inventory)

This is the vendor-neutral positioning from the parent SEO doc, stated as content rather than
as a claim. It is also the block most likely to be quoted by an answer engine, so every row
must stand alone out of context.

### 8 · The nine sheets — `#the-nine`

**9 rows**, and deliberately the thinnest section on the page. Columns: `Sheet` ·
`The one question it answers` · `Land here first`. Nothing else — no summaries, no topic
lists, no "covers X, Y and Z." The question column is one interrogative sentence; the landing
anchor is the sibling's most useful entry point, which for a first-time reader is usually its
`#start-here` and for a returning engineer is its densest register.

This section exists so the `ItemList` JSON-LD describes something actually on the page. It is
the section most at risk of drifting into the rejected shape; hold it to three cells per row.

### 9 · Sources — `#sources`

Short by design. The hub's own claims are counts of its own rows. Cite only: the standards it
names by version (CCSS v9.0, FATF Recommendation 16, NIST post-quantum standards) and the nine
sheets, each of which carries its own sourced register. Do not re-cite the siblings' primary
sources — that is duplicated content with extra steps.

### 10 · Related — `.related`

The cluster's standard `.related` block, listing all nine.

---

## Metadata and structured data

Standard AGENTS.md block (title, description, keywords, canonical, OG, Twitter, `og:image` +
alt), with these page-specific decisions:

- **Keywords:** `crypto custody architecture, custody model comparison, digital asset custody,
  MPC vs multisig, qualified custodian, custody responsibilities, crypto custody reference`
- **JSON-LD block 1 — `CollectionPage` with `mainEntity` = `ItemList`:**
  - `CollectionPage`: `name`, `description`, `url` (canonical), `author` (Person, David Veksler
    (AI Generated)), `publisher` (Organization), `datePublished`. **No `dateModified`** — repo
    rule; review status lives in `refresh-status.json`.
  - `ItemList`: `numberOfItems: 9`, `itemListOrder:
    "https://schema.org/ItemListUnordered"`, nine `ListItem`s with `position`, `url`, `name`,
    `description`.
  - **Single-source the nine `name`/`description` values from `llms.txt:114-122`** — those are
    the sheets' exact `<title>` and meta description strings. Copying them by hand from the
    HTML is how the two drift.
- **JSON-LD block 2 — one `BreadcrumbList`** (Home → Crypto Custody & Compliance → this page).
  Optional; skip it rather than fake a hierarchy the site does not have.
- **No `FAQPage`.** The parent SEO doc reserves `FAQPage` for four sibling sheets with genuine
  operator questions. The hub's cards are routing prompts, not answers, and inventing FAQ
  entries to farm a rich result is an explicit anti-goal.
- `scripts/seo_check.py` enforces title ≤ 65, description 150–200, canonical present, every
  `ld+json` block parseable. The drafts above are inside those bounds; recount after any edit.

---

## Internal-link plan

The hub is worth building only if links point at it. Specify both directions.

### Inbound — in this repo (do these in the build commit or the one after)

| Source | Change |
|---|---|
| All nine sheets, `.related` block | Add **"Custody cluster index"** → `crypto-custody-index.html` as the **first** entry |
| `scripts/generate_custody_batch.py:115` (`SHARED_RELATED`) | Add the same entry so the generator matches the files |
| `category-map.php` | Add `'crypto-custody-index.html' => 'Crypto Custody & Compliance',` in alphabetical position (after `crypto-compliance-architecture`, before `crypto-exchange-architecture`) |
| `llms.txt` + `llms-full.txt` | List the hub **first** under `## Crypto Custody & Compliance`, with a line naming it the cluster entry point |
| `bitcoin-wallet.html`, `bitcoin-self-custody-guide.html`, `bitcoin-exchanges-cards.html`, `personal-cybersecurity.html` | One contextual link each into the hub (these already link into individual cluster sheets; the hub is the better target for a general "custody" mention) |

> ⚠️ **Do not regenerate the nine by re-running `scripts/generate_custody_batch.py`.**
> `crypto-exchange-architecture.html` currently carries ~194 lines of hand-authored diagram
> work (per `TODO/crypto-exchange-architecture-diagrams.md`) that a regeneration would
> destroy, and the primers and `abbr.term` glossary added 2026-09-03 may be in the same
> position. Edit the nine HTML files' `.related` blocks directly **and** update
> `SHARED_RELATED` so the generator does not reintroduce the drift later.

`index.php` and `sitemap.php` discover files with `scandir`, so no registration is needed
beyond `category-map.php`. Clear `.metadata-cache.json` if the card does not appear.

### Inbound — cross-domain (parent SEO doc, workstream 2; separate session)

| Source | Target | Priority |
|---|---|---|
| `davidveksler.com/work/crypto-custody-and-recovery/` | The hub, plus the existing three deep links | **First.** Strongest topical E-E-A-T signal in the fleet |
| `vellum.capital` custody-options post | The hub (the missing return path) | High |
| `walletrecovery.info` | The hub, alongside its existing `wallet-recovery-forensics` deep links | Medium |

**Record every one of these in `~/Projects/seo-crosslinking/crosslinks.tsv`** — the register is
already behind reality for this cluster (24 untracked outbound links), and adding a hub without
tracking it makes that worse.

### Outbound from the hub

- ~34 matrix rows + 5 chooser rows + 16 symptom rows + 6 refusal rows + 9 roster rows, all
  deep links to sibling anchors. Repetition of targets across tables is expected and fine.
- **Cross-domain: at most one**, in the refusals row about recovery guarantees. The hub's job
  is to push equity *into* the nine, not out of the site.
- Every link must be a real anchor that exists on the target. The anchors named in this spec
  were read off the shipped files on 2026-09-03; re-verify each at build (`grep -o 'id="…"'`)
  because a future regeneration renames slugs.

---

## Anti-goals

Global anti-goals from `TODO/README.md` Rule 4 apply. Page-specific, and each is a build gate:

1. **No summaries of the nine.** The Rule 0 test above is the acceptance criterion: strip the
   links, and no cell should still teach a sibling's content. The hub routes; it does not
   explain. Violating this is the single failure mode that makes this page worthless.
2. **No vendor recommendations, rankings, or pricing.** No "best custody provider" table, no
   Fireblocks-vs-BitGo cell, no cost figures. A vendor name may appear only where a sibling
   already uses it as the canonical example of a pattern (the Fireblocks co-signer callback),
   never in a comparative position.
3. **No invented FAQ and no `FAQPage` JSON-LD.**
4. **No new verifiable facts.** Every number on the page is either a count of the page's own
   rows or a version tag already carried and sourced on a sibling. The hub must not become a
   thing that needs re-verification; that is what the nine are for.
5. **No legal, compliance, or investment advice.** Regime names appear as routing labels
   ("regulatory posture"), never as instructions. One disclaimer line in the refusals section,
   not per-section hedging.
6. **No visible "Last verified" line and no `dateModified`** (repo-wide rule).
7. **No duplicated primer.** The hub's `#start-here` is about the cluster. If a card could be
   pasted into `institutional-crypto-custody.html` unchanged, rewrite it.
8. **No sixth custody-model column** and no second router. One primary axis, one crisis lane.

---

## Volatile-facts register

**Overall: STABLE, with roster drift as the only real risk.** By design the page carries almost
no rotting facts — it holds counts of its own rows and links to sheets that hold the facts.

| Fact | Rots when | Re-verification |
|---|---|---|
| The nine-sheet roster (matrix rows, `ItemList`, §8, `.related`) | A sheet is added to or removed from the cluster | Parity check, below — this must not be a human's job |
| Sibling anchor slugs | A sheet is regenerated or restructured | `grep` every `href="*.html#*"` target against the target file's `id=` set |
| Sibling `<title>` / meta description strings in the `ItemList` | A sibling's metadata is edited | Re-copy from `llms.txt` |
| `CCSS v9.0` version reference | CCSS publishes a new version | Same cadence as `institutional-crypto-custody` |
| Regime names in the chooser's "regulatory posture" cell (MiCA, NYDFS, FATF R.16) | Slowly; names outlive rules | Annual |
| The computed headline number ("17 of 34") | Any matrix edit | Recount; never hand-edit |

**Build the machine gate** (global CLAUDE.md automation ladder, rung 4): a check that asserts
cluster membership parity across four places — `category-map.php`, the `## Crypto Custody &
Compliance` block in `llms.txt`, the hub's `ItemList`, and the hub's matrix row targets — and
additionally that every `href="*.html#anchor"` on the hub resolves to a real `id` in the target
file. Fold it into `scripts/seo_check.py` or add `scripts/check_cluster_hub.py` and wire it into
the deploy pipeline's validate step and `.githooks/pre-push`. Without this, the hub silently
rots the first time the cluster changes.

---

## Index category

`Crypto Custody & Compliance` (existing label; no new category).

## Geographic / jurisdiction scope

Global and deliberately jurisdiction-light. Regulatory regimes appear only as *labels* in one
chooser column and one refusal row; the hub never states an obligation. The sheets that do
carry jurisdiction detail (`crypto-compliance-architecture`,
`stablecoin-payment-infrastructure`) own it, and the refusals table says so out loud.

## Reading conditions

**Two audiences, both on a laptop, both with a second window open.**

1. *The engineer scoping or reviewing a design* — desktop, two windows, mid-build, working
   through the matrix while writing a design doc or a vendor questionnaire. Consequences:
   desktop-first dense grid, sticky first column and header, keyboard-navigable table region,
   no information conveyed by hover, stable anchors so individual rows can be cited in a doc,
   and a print stylesheet good enough to bring the matrix into a review meeting.
2. *The on-call engineer at 2 a.m.* — phone, one hand, stressed, arriving from a search on a
   symptom string. Consequences: the symptom router reachable in one tap from the top, tap
   targets ≥ 44 px, no horizontal scroll anywhere at 375 px (hence the column-switch plan),
   and dark theme respected on first paint.

The theme toggle, filter box and utility bar come from the cluster chrome and behave
identically to the nine — a reader arriving from a sibling should not have to relearn the
furniture.

## Density targets

| Table | Rows |
|---|---|
| Custody model chooser | 5 |
| **Responsibility matrix (signature)** | **34, in 8 bands, every sheet owning ≥ 2** |
| Symptom router | 16 |
| Lifecycle order of operations | 8 |
| Refusals | 6 |
| The nine sheets | 9 |

78 substantive rows against a 20-entry floor. If the build comes in materially under these
counts, the page has drifted toward a listing and should be reviewed against Rule 0 again
before it ships.

## Definition of done (additions to README Rule 3)

- The Rule 0 strip-the-links test passes on every cell.
- The headline number in the quick-reference strip was **recounted from the built matrix**, not
  copied from this spec.
- Every `href` to a sibling anchor resolves to a real `id` in the target file.
- The 375 px acceptance test in the degradation plan passes for all five model selections.
- The matrix prints on one landscape page, or breaks at a band boundary.
- `python scripts/seo_check.py crypto-custody-index.html` returns 0 failures.
- The nine sheets' `.related` blocks and `SHARED_RELATED` link back, edited **without**
  regenerating the batch.
- The parity check exists and passes.
