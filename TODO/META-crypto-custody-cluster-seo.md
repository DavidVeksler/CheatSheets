# SEO strategy — Crypto Custody & Compliance cluster

Durable working doc for the 9-sheet custody cluster. Sibling to `TODO/META-seo-planning.md`
(site-wide). Update in place.

Cluster URL (browse view): `https://cheatsheets.davidveksler.com/?cat=Crypto+Custody+%26+Compliance`
Category membership is defined in `category-map.php:85-94`.

## Situation as of 2026-09-02

All nine sheets were committed 2026-08-31 and are live (HTTP 200), in `sitemap.php` (196 URLs),
and listed under a `## Crypto Custody & Compliance` heading in both `llms.txt` and `llms-full.txt`.

**GSC: zero impressions across all nine pages** for 2026-06-04 → 2026-09-01. That is expected at
two days old, not a defect. It also means there is nothing to optimize yet — the first 60 days of
work is indexation and link equity, not on-page tuning.

Assets already in place (do not redo):

| Asset | State |
|---|---|
| Internal mesh | Near-complete: each sheet links to 8–10 siblings |
| Slug anchors | Present (`#recovery-feasibility-triage`, `#format-and-tool-register`, …) |
| JSON-LD | `TechArticle` + `Person` + `Organization` on all nine |
| OG images | All nine present in `images/` (200–330 KB) |
| Primary-source citations | NIST, FATF, EUR-Lex, NYDFS, CCSS/cryptoconsortium, intervasp.org, Fireblocks + Circle developer docs |
| Cross-domain inbound | walletrecovery.info deep-links `wallet-recovery-forensics.html` from 5+ posts, with working anchors |
| Cross-domain outbound | 24 links from the cluster to walletrecovery.info |
| Beginner on-ramp | `#start-here` primer on all nine (2026-09-03): plain-English framing, four question cards, one takeaway line. Filterable (`data-f`), so it hides with everything else on a no-match query |
| First-use glossary | 58 `abbr.term` tooltips added across the seven sheets that had none. Placement is first *body* use, never inside the primer, an SVG, or a link |

## Competitive reality — do not chase head terms

SERPs for `mpc wallet architecture`, `travel rule ivms101`, and neighbours are owned by funded
vendors publishing their own category-defining content: Fireblocks, BitGo, Cobo, Notabene,
Chainalysis, Alchemy, Blockdaemon, Silence Laboratories. They win on domain authority and on
brand-name demand ("fireblocks vault", "notabene travel rule") that this site cannot compete for.

What they systematically do **not** publish, because it undercuts a sales motion:

- Named failure modes and what breaks in production
- Exhaustive status/sub-status enumerations and what each one obliges the integrator to do
- Exit tests ("can you leave this vendor, and what does it cost")
- Refusal cases — when recovery is arithmetically impossible, when migration is premature
- Vendor-neutral crosswalks (CCSS v9.0 controls against an actual tier model)

That gap is the entire positioning. **The cluster's claim is: the vendor-neutral operator
reference an engineer opens while the vendor's doc is already in the other tab.** Every SEO
decision below follows from it.

## Target query shape (hypotheses — validate against GSC at day 30/60)

No third-party volume data backs this table; Semrush API units were exhausted on 2026-09-02.
These are intent hypotheses derived from what each sheet uniquely answers. Treat the day-60 GSC
query pull as the first real evidence and rewrite this table against it.

| Sheet | Intent to win | Shape of the query |
|---|---|---|
| `mpc-wallet-architecture` | Engineer evaluating or auditing TSS | `mpc vs multisig custody`, `dkg key refresh`, `frost vs ecdsa threshold` |
| `custody-provider-integration` | Integrator mid-build | `fireblocks webhook sub status`, `idempotent transaction api custody`, `co-signer callback` |
| `crypto-compliance-architecture` | Compliance engineer | `ivms101 field map`, `travel rule payload`, `kyt alert workflow` |
| `crypto-exchange-architecture` | Systems designer | `exchange double-entry ledger`, `wallet boundary invariant`, `proof of reserves design` |
| `blockchain-deposits-withdrawals` | On-call / ops | `stuck evm nonce withdrawal`, `deposit reconciliation mismatch`, `utxo selection gas funding` |
| `institutional-crypto-custody` | Risk / audit reader | `ccss v9 controls`, `hot wallet float policy`, `key ceremony procedure` |
| `stablecoin-payment-infrastructure` | Treasury / payments eng | `cctp stuck state`, `native vs bridged usdc`, `depeg controls` |
| `post-quantum-custody-migration` | Forward-planning security | `bip 360 361`, `quantum exposed utxo`, `pq signature size custody` |
| `wallet-recovery-forensics` | Owner of a lost wallet | `bip39 checksum search space`, `derivation path wrong addresses` — already fed by walletrecovery.info |

The recovery sheet is the outlier: walletrecovery.info's own GSC shows live demand in this
space (`wallet.dat` 612 impressions, `bitcoin core wallet recovery` 259, `wallet recovery` 602).
It should be first to earn impressions, because it inherits an already-ranking neighbour.

## Workstreams

### 1. Indexation (weeks 0–4) — the only thing that matters right now

- [ ] Confirm all nine are in GSC's index (URL Inspection, or a day-30 impressions pull — a page
      with zero impressions at day 30 is a crawl problem, not a ranking problem).
- [ ] Re-submit `sitemap.php` in GSC so the 2026-08-31 batch is picked up on a fresh crawl.
- [ ] Ship the inbound links in workstream 2 — for a new URL on a mid-authority domain, an
      inbound link from an already-crawled page is a faster discovery path than the sitemap.

### 2. Link equity — the highest-leverage fix

This site's authority sits in `ai-frontier.html` (157K impressions/90d) and other topically
unrelated pages. Passing it to custody pages is not available. The equity that *is* available is
topical and cross-domain, and one link is worth more than all the rest:

- [ ] **`davidveksler.com/work/crypto-custody-and-recovery/` currently links to cheatsheets only
      for agentic AI.** That page carries the Celsius / Vellum / $4M-recovered credentials — it is
      the strongest E-E-A-T signal in the fleet for exactly this topic, and it points nowhere near
      the cluster. Add deep links from it to `institutional-crypto-custody`,
      `custody-provider-integration`, and `wallet-recovery-forensics`. **Do this first.**
- [ ] Add reciprocal cluster links from `vellum.capital`'s custody-options post (already linked
      from bitcoin-exchanges-cards; the return path is missing).
- [ ] Extend walletrecovery.info's existing deep-link pattern beyond the forensics sheet:
      `post-quantum-custody-migration` and `institutional-crypto-custody` both answer questions
      its readers ask.
- [ ] Link into the cluster from the older, already-indexed Bitcoin sheets. Present today:
      `bitcoin-exchanges-cards` → exchange-architecture, `bitcoin-wallet` → pq-custody,
      `bitcoin-self-custody-guide` → wallet-recovery-forensics. Missing and worth adding:
      `bitcoin-wallet` → `mpc-wallet-architecture`, `bitcoin-self-custody-guide` →
      `institutional-crypto-custody`, `personal-cybersecurity` → `wallet-recovery-forensics`.
- [ ] **Record every one of these in `~/Projects/seo-crosslinking/crosslinks.tsv`.** The 24
      existing cluster → walletrecovery.info links and the 5+ inbound deep links are not tracked
      there; the register is already behind reality.

### 3. Build an indexable hub page

`?cat=Crypto+Custody+%26+Compliance` filters client-side and `index.php:310` emits a canonical to
the site root for every filtered view. So the cluster has **no indexable landing page**: nothing
can rank for the category head terms, nothing concentrates the internal links, and nothing gives
an AI answer engine a single URL to cite for "crypto custody reference".

Build `crypto-custody-index.html` as a real sheet, not a directory listing: a decision surface
that routes a reader to the right sibling (custody model → tier → control → the sheet that covers
it), with a `CollectionPage` + `ItemList` JSON-LD block enumerating the nine. It becomes the hub
every external link in workstream 2 points at, and it inherits the mesh already built.

### 4. AEO / citation surface

The cluster is unusually well-suited to AI answer engines: dense tables, primary-source citations,
explicit refusal cases. Two cheap additions:

- [ ] Add `FAQPage` JSON-LD to the four sheets with genuine operator questions
      (compliance-architecture, custody-provider-integration, blockchain-deposits-withdrawals,
      wallet-recovery-forensics). Only questions the sheet actually answers — no invented FAQs.
- [ ] Track AI-answer visibility for 3–4 cluster queries on the same schedule as the site-wide
      check (per global marketing standards, AI visibility is a KPI, not a bonus).

### 5. Measurement

- Day 30 (2026-10-01): impressions-only pull. Success = any impressions at all. Zero = crawl
  problem; escalate to workstream 1.
- Day 60 (2026-11-01): first query-dimension pull. Rewrite the hypothesis table above against
  real queries. Success = 3+ sheets with impressions, any position.
- Day 90 (2026-12-01): striking-distance analysis (position 11–30) and first CTR/title work.
  Do not touch titles before this date — there is no data to tune against.
- Append each pull to `docs/seo-progress.md`.

## Do not

- Do not chase vendor-brand queries (`fireblocks pricing`, `bitgo vs anchorage`). Unwinnable, and
  it would trade the vendor-neutral positioning for nothing.
- Do not add "as of" freshness churn to these sheets to look updated. Per
  `weekly-freshness-update.md`, review status belongs in `refresh-status.json`.
- Do not rewrite titles or descriptions before day 90. They are well-formed and there is no CTR
  data to improve them against.
- Do not add more sheets to the cluster until the existing nine have impressions. Nine
  zero-traffic pages is a link-equity dilution problem, not a coverage problem.
