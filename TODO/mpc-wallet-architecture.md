# Spec: MPC wallet architecture — threshold signing, key lifecycle, failure modes

**Target file:** `mpc-wallet-architecture.html`
**Batch:** [custody-engineering-batch-2026-08.md](custody-engineering-batch-2026-08.md) (sheet 1 of 9, **P0 — build first**).
**Sets the batch design language.** Sheet 1 fixes the palette, the three-colour semantic scale and
the table register that sheets 2–9 reuse. Get it right here or every later sheet re-litigates it.

## Why this topic

MPC custody content splits into two useless halves. Vendor marketing says "no single point of
failure" and stops. Academic papers give the protocol and assume you already know why anyone
wants it. Nothing in between explains what an engineer actually has to decide: which protocol
family, what quorum, where shares live, what happens at 3 AM when one share is unreachable, and
what the whole apparatus does *not* buy you.

That last part is the page's reason to exist. **A compromised policy engine produces perfectly
valid signatures.** Threshold signing protects the key material; it does not protect the decision
to sign. Most MPC content never says this because the people producing it are selling MPC. A page
that leads with the guarantee and then draws the boundary around it is more useful than either
half of the existing literature, and it is the honest version.

The second gap is the comparison. "MPC vs multisig" articles exist and are almost all wrong in the
same way: they compare on chain support and fees and skip the two axes that decide real
deployments — **signer attribution** (on-chain multisig tells you who signed; MPC does not, unless
you built the audit log yourself) and **address stability under quorum change** (MPC resharing
keeps the address; multisig does not).

## Targeting

- **Primary query:** `mpc wallet architecture`
- **Secondary:** `threshold signature scheme custody`, `mpc vs multisig`, `gg18 vs cggmp`,
  `distributed key generation wallet`, `proactive share refresh`, `threshold ecdsa explained`,
  `what mpc does not protect`
- **Mode:** research mode, professional. The reader is designing or assessing a signing stack, not
  in crisis. They arrive from a specific sub-question and need the surrounding map, so every
  section needs a stable anchor and the page must survive being entered at section 6.

## Draft title / H1 / meta

- `<title>`: `MPC Wallet Architecture: Threshold Signing & Failure Modes` (57 chars)
- **H1:** `MPC Wallet Architecture: Threshold Signing, Key Lifecycle, and What It Doesn't Protect`
- **Meta description (draft):**
  `How threshold-signature custody actually works: DKG, the GG18 to CGGMP protocol lineage, share refresh, quorum changes without address changes, and the failure modes MPC leaves wide open.` (186 chars)

## Reader outcome

After this page the reader can specify a threshold-signing deployment — protocol family, quorum,
share topology, refresh cadence, recovery path — defend each choice against the alternative, and
name the three attacks that the design does not stop. Acceptance test: they can look at a vendor's
architecture diagram and ask the two questions that matter (where do the shares actually run, and
what signs off on the payload before the shares see it).

## Success metric

Cited or linked by practitioners rather than clicked by searchers. Watch for inbound links from
engineering blogs, vendor comparison posts and security write-ups, and for the comparison matrix
being screenshotted. Search position on `mpc vs multisig` is a secondary indicator only.

## Content approach

Structure runs guarantee → lifecycle → limits → comparison. The limits section is the payload;
everything before it is the setup that makes the limits land.

1. **Quick reference: the one-screen model** — what a threshold signature is in four lines (n
   shares, t needed, no share ever combined, output is an ordinary on-chain signature
   indistinguishable from single-key), the vocabulary table (share vs key vs shard vs seed; DKG vs
   splitting; t-of-n vs n-of-n), and a jump index. Signature element lives here.
2. **DKG: why generation matters more than storage** — distributed key generation with no dealer
   versus splitting an existing key (Shamir over a seed). The point: if a full key ever existed on
   one machine, the entire security argument is about that one moment, not about the shares. Cover
   the verifiable-secret-sharing component, the public-key derivation, and how you verify a DKG
   actually happened as claimed (the audit question a customer should ask a vendor).
3. **Protocol lineage** — a table, not prose, tracking the ECDSA threshold line and the Schnorr
   line separately:
   - **ECDSA:** Lindell17 and the 2-party case; GG18 (Gennaro–Goldfeder) and its MtA-with-Paillier
     construction; GG20 adding identifiable abort; CGGMP/CMP (Canetti–Gennaro–Goldfeder–
     Makriyannis–Peled) with proactive refresh and non-interactive presigning; DKLs (Doerner–
     Kondi–Lee–shelat) taking the OT-based route and avoiding Paillier entirely.
   - **Schnorr/EdDSA:** FROST for threshold Ed25519 and Taproot key-path; MuSig2 as n-of-n
     aggregation (and why it is *not* a threshold scheme — a distinction routinely botched).
   Columns: round count, presigning support, identifiable abort, assumptions (Paillier / OT /
   DDH), curve support, maturity, and where it is deployed. Chain applicability is the practical
   punchline: Ed25519 chains cannot use the ECDSA line at all.
4. **Known breaks in deployed implementations** — the section that separates this page from vendor
   material. The 2023 class of disclosures against production TSS implementations (the
   zero-value / malformed-proof family against GG18 and GG20 deployments, and the parallel
   findings against Lindell17-derived 2-party code) illustrate the real lesson: **the protocol
   being proven secure says nothing about the implementation being secure**, and several of these
   allowed full key extraction over a sequence of signing sessions. Present as: what the flaw
   class was, what an attacker needed, what the fix was, and the question it generates for a
   vendor ("which audits, of which code, at which version"). Verify every specific before shipping
   and prefer naming the flaw class over naming a company.
5. **Key lifecycle** — the operational spine, section per phase: generation ceremony; share
   distribution and the topology question; signing; **proactive share refresh** (why a mobile
   adversary who compromises shares slowly across a year gets nothing if refresh is faster than
   they are — with the actual re-randomisation model and a cadence recommendation);
   **resharing / quorum change** (t-of-n → t'-of-n', same public key, same address, no funds
   movement — and why this is MPC's single strongest operational advantage over multisig);
   revocation of a compromised share; retirement.
6. **Share custody topology** — a table of real topologies and their actual security: shares
   across separate cloud accounts, separate cloud *providers*, on-prem HSM plus cloud, customer-
   held share plus vendor shares, mobile device share. Each row scores: correlated-failure risk,
   liveness, latency, recovery difficulty, insider-collusion floor. Include the anti-pattern
   explicitly — **three shares on three VMs in one cloud account under one IAM role is a single
   point of failure wearing a costume.**
7. **Liveness vs safety** — the availability arithmetic. With t-of-n, losing (n − t + 1) shares
   means funds are safe and permanently unspendable. Give the table: quorum choices against
   per-share availability, resulting signing availability, and the number of losses tolerated.
   Cover the operational cases: a share is offline (degraded, still signing), a share is
   destroyed (reshare from remaining), too few shares (frozen — and what a recovery package would
   have to have contained to prevent it). Name the tension in one line: every share you add for
   liveness lowers the collusion floor.
8. **What MPC does not protect** — the reason the page exists. Each item: the attack, why
   threshold signing is irrelevant to it, and the control that actually addresses it.
   - A compromised policy engine signs valid transactions. The shares behave correctly.
   - Blind signing: the quorum signs a payload it did not parse. Approvers approve a hash.
   - Address substitution between intent and payload (malware, compromised front-end,
     clipboard, a poisoned address book).
   - Compromise of the approving human's device or session, or of the API key that initiates.
   - Insider collusion at exactly the threshold — the quorum is the security boundary, and it is
     a *people* boundary.
   - Correlated infrastructure compromise (see §6).
   - No native signer attribution: the chain records one signature. If you did not build the
     off-chain audit log, you cannot prove who authorised.
   - Supply-chain compromise of the MPC library or the co-signer image.
9. **Comparison matrix** — the shareable artifact. Rows: threshold MPC, on-chain multisig
   (Bitcoin `OP_CHECKMULTISIG`/Taproot, Safe on EVM), smart-contract wallet / account
   abstraction, single-key HSM, passkey-based. Columns: on-chain footprint and fee, chain
   coverage, address stability under quorum change, signer attribution, policy privacy, recovery
   model, certification path (FIPS/CC), protocol maturity, vendor lock-in / exportability,
   failure mode when the vendor disappears. Follow with explicit decision guidance — use MPC
   when…, use multisig when…, use both when… — because the correct answer for many institutions
   is a hybrid (MPC for the hot tier, multisig for the cold tier) and no vendor page will say so.
10. **Vendor due-diligence checklist** — the questions that flow from §4–§8, as a printable list.
    Which protocol and version; which audits at which commit; DKG or import; refresh cadence and
    is it actually run; share topology and provider diversity; is the policy engine in the same
    trust domain as the shares; what does the exit package contain and has a restore been tested.
11. **Common mistakes** (mandatory) — importing an existing seed and calling it MPC; a quorum
    whose members all report to one manager; refresh configured but never exercised; no tested
    export; treating the policy engine as in-scope of the MPC guarantee; picking an ECDSA-only
    protocol then needing Solana; equating "2-of-3" with "two humans".
12. **Related sheets** footer per the cross-link map.

## Volatile-facts register

**Overall: SLOW-DRIFT, with one VOLATILE section.**
- Protocol lineage, DKG, refresh/reshare semantics, the liveness arithmetic, the comparison
  axes: **STABLE.** Mathematics does not rot.
- **§4 implementation breaks: VOLATILE** — new disclosures land regularly. Re-verify annually;
  date the section inline; never let it imply "these were the vulnerabilities" rather than "these
  were the ones public at the time of writing".
- **§3 protocol maturity column and §9 certification column: SLOW-DRIFT** — new schemes and new
  FIPS validations appear. Annual check.
- Named vendor products in §9/§10: SLOW-DRIFT, and per the batch rule, minimal and dated.
Annual freshness rotation with §4 as the named check target.

## Index category

`Crypto Custody & Compliance` (new — see the batch file).

## Reading conditions

**Desk, laptop, focused, two hours.** An engineer or an assessor reading deliberately, likely with
a vendor's documentation open in another tab and a decision to make this week. Consequences: dense
is correct, long is correct, but the page must be *navigable* — a sticky section index, stable
anchors on every subsection, and tables that survive being read out of order. Print matters more
than usual for this batch: the comparison matrix and the due-diligence checklist will be printed
and taken into a meeting, so both must fall on single pages. Mobile is a secondary but real case
(reading on a phone before a call): tables get `overflow-x: auto` wrappers and the matrix
degrades to stacked per-option cards rather than a shrunken grid.

## Cross-link map

- **Internal outbound:** `institutional-crypto-custody.html` (sheet 3 — the policy engine that
  §8 hands off to), `custody-provider-integration.html` (sheet 6 — who implements this),
  `post-quantum-custody-migration.html` (sheet 9 — why thresholds are the hard PQ case),
  `wallet-recovery-forensics.html` (sheet 8 — the frozen-quorum case), `bitcoin-wallet.html`,
  `bitcoin-self-custody-guide.html`.
- **Reciprocal inbound:** one line from `bitcoin-self-custody-guide.html` and one from
  `bitcoin-wallet.html` pointing at the comparison matrix anchor.
- **External outbound:** the original papers by name (GG18, GG20, CGGMP, DKLs, FROST, Lindell17),
  the FROST RFC, NIST's multi-party threshold cryptography project, and public audit reports.
  Papers and standards only — no vendor blogs as authority for how a protocol works.

## og:image / shareable artifact

The **comparison matrix** at 1200×630 — MPC / multisig / smart-contract wallet / HSM against the
five axes that fit legibly, with the semantic colour scale. It is also the screenshot-this block.
Second candidate if the matrix will not compress: the §8 "what MPC does not protect" list, which
is the page's most quotable idea.

## Jurisdiction scope

Global and technical. No regulatory content on this sheet at all — that is sheets 3 and 4, and
splitting it cleanly is what keeps both pages sharp. One line in §9's certification column
pointing at sheet 3 is the whole treatment.

## Density targets

Protocol lineage table ≥ 8 protocols × 8 columns. Topology table ≥ 6 topologies × 5 scores.
Liveness table ≥ 8 quorum configurations. Comparison matrix 5 options × ≥ 10 axes.
"Does not protect" ≥ 8 items, each with attack / why-irrelevant / actual-control.
Due-diligence checklist ≥ 12 questions. Common mistakes ≥ 8. Lifecycle phases ≥ 6, each with a
concrete operational procedure rather than a definition.

## Research sources (verify against these, per Rule 1)

Original papers: Gennaro–Goldfeder 2018 and 2020, Canetti–Gennaro–Goldfeder–Makriyannis–Peled
(CGGMP/CMP), Doerner–Kondi–Lee–shelat (DKLs), Lindell 2017, Komlo–Goldberg (FROST) and the FROST
RFC, Nick–Ruffing–Seurin (MuSig2). NIST IR 8214 series for threshold cryptography terminology.
Published third-party audit reports and the original disclosure write-ups for §4 — cite the
researchers' own publication, not a news summary. Chain documentation for curve/scheme support.
Vendor documentation only for claims about that vendor's own product.

## Visual design

**Identity: the assurance-report register defined in the batch file, in its first and most
complete expression.** Near-monochrome slate/paper ground, one fuchsia accent, the three-colour
semantic scale (safe / conditional / unsafe) that every later sheet inherits. Monospace for every
protocol name, parameter and quorum expression.

**Signature element: the trust-boundary diagram.** One inline SVG, drawn in the flat schematic
style of a security architecture review, showing the request path — initiator → API → policy
engine → co-signers → shares → chain — with a heavy boundary drawn around *only* the share layer
and everything outside it shaded as out-of-scope. Section 8's list attaches to the parts outside
the boundary with leader lines. This single drawing is the page's argument; it must be the most
polished thing on it and must remain legible at 375 px (stack the path vertically on narrow
viewports rather than scaling the whole diagram down). `<title>` and `<desc>` on the SVG, and the
same information available in the adjacent text so the diagram is never load-bearing alone.

No JavaScript. No animation. The comparison matrix is a plain `<table>` with a scroll wrapper —
resist the urge to build a filterable widget; it would be the least useful interactive element on
the site and would break print.
