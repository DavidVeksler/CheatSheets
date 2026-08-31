#!/usr/bin/env python3
"""Generate the nine standalone custody-engineering reference sheets.

The generated HTML is deliberately self-contained apart from pinned Bootstrap assets.
Content data remains here so the batch's repeated visual language and semantic scale do
not drift between pages.
"""

from __future__ import annotations

import html
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFIED = "2026-08-31"


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def table(title: str, columns: list[str], rows: list[list[str]], note: str = "") -> str:
    head = "".join(f"<th scope=\"col\">{esc(column)}</th>" for column in columns)
    body = "".join(
        "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    return f"""
    <section class="sheet-section" aria-labelledby="{slugify(title)}">
      <h2 id="{slugify(title)}">{esc(title)}</h2>
      {f'<p class="section-note">{note}</p>' if note else ''}
      <div class="table-wrap" role="region" aria-label="{esc(title)}" tabindex="0">
        <table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>
      </div>
    </section>"""


def cards(title: str, entries: list[tuple[str, str, str, str]], intro: str = "") -> str:
    rendered = []
    for name, definition, example, gotcha in entries:
        rendered.append(f"""
        <article class="entry">
          <h3>{esc(name)}</h3>
          <p>{definition}</p>
          <p class="example"><strong>Concrete use:</strong> {example}</p>
          <p class="gotcha"><strong>Failure mode:</strong> {gotcha}</p>
        </article>""")
    return f"""
    <section class="sheet-section" aria-labelledby="{slugify(title)}">
      <h2 id="{slugify(title)}">{esc(title)}</h2>
      {f'<p class="section-note">{intro}</p>' if intro else ''}
      <div class="entry-grid">{''.join(rendered)}</div>
    </section>"""


def checklist(title: str, items: list[str], intro: str = "") -> str:
    lis = "".join(f"<li><span aria-hidden=\"true\">□</span> {item}</li>" for item in items)
    return f"""
    <section class="sheet-section checklist" aria-labelledby="{slugify(title)}">
      <h2 id="{slugify(title)}">{esc(title)}</h2>
      {f'<p class="section-note">{intro}</p>' if intro else ''}
      <ol>{lis}</ol>
    </section>"""


def sources(items: list[tuple[str, str, str]]) -> str:
    rendered = "".join(
        f'<li><a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(label)}</a>'
        f'<span>{esc(note)}</span></li>'
        for label, url, note in items
    )
    return f"""
    <section class="sheet-section sources" aria-labelledby="sources">
      <h2 id="sources">Primary sources &amp; scope</h2>
      <p class="section-note">Operational and volatile claims were checked against these first-party documents on {VERIFIED}. Examples are illustrative controls, not legal, investment, or vendor-selection advice.</p>
      <ul>{rendered}</ul>
    </section>"""


def related(items: list[tuple[str, str]]) -> str:
    links = "".join(f'<a href="{esc(href)}">{esc(label)} <span aria-hidden="true">→</span></a>' for label, href in items)
    return f'<aside class="related" aria-labelledby="related"><h2 id="related">Related engineering sheets</h2><div>{links}</div></aside>'


def slugify(value: str) -> str:
    return "".join(ch.lower() if ch.isalnum() else "-" for ch in value).strip("-").replace("--", "-")


SHARED_RELATED = [
    ("MPC wallet architecture", "mpc-wallet-architecture.html"),
    ("Deposits & withdrawals", "blockchain-deposits-withdrawals.html"),
    ("Institutional custody", "institutional-crypto-custody.html"),
    ("Compliance architecture", "crypto-compliance-architecture.html"),
    ("Stablecoin infrastructure", "stablecoin-payment-infrastructure.html"),
    ("Provider integration", "custody-provider-integration.html"),
    ("Exchange architecture", "crypto-exchange-architecture.html"),
    ("Wallet recovery", "wallet-recovery-forensics.html"),
    ("Post-quantum migration", "post-quantum-custody-migration.html"),
]


CSS = r"""
@layer reset, tokens, base, layout, components, print;
@layer tokens {
  :root {
    color-scheme: light dark;
    --paper: light-dark(#faf9f7, #0f172a); --surface: light-dark(#ffffff, #182235);
    --surface-2: light-dark(#f4f1ed, #111c2e); --ink: light-dark(#172033, #e7edf6);
    --muted: light-dark(#586273, #a9b5c7); --line: light-dark(#d8d3cc, #334155);
    --accent: light-dark(#86198f, #e879f9); --accent-soft: light-dark(#fae8ff, #3b1641);
    --safe: light-dark(#166534, #86efac); --safe-bg: light-dark(#dcfce7, #12351f);
    --warn: light-dark(#92400e, #fcd34d); --warn-bg: light-dark(#fef3c7, #3b2a0d);
    --danger: light-dark(#991b1b, #fca5a5); --danger-bg: light-dark(#fee2e2, #401719);
    --sans: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    --mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  }
}
@layer reset { *,*::before,*::after{box-sizing:border-box} body,h1,h2,h3,p{margin:0} table{border-collapse:collapse} }
@layer base {
  body{background:var(--paper);color:var(--ink);font-family:var(--sans);line-height:1.55;text-wrap:pretty}
  a{color:var(--accent);font-weight:650;text-decoration-thickness:.08em;text-underline-offset:.18em}
  :focus-visible{outline:3px solid var(--accent);outline-offset:3px}
  code,.mono,td:nth-child(n+2){font-family:var(--mono);font-variant-numeric:tabular-nums}
  h1,h2,h3{text-wrap:balance;line-height:1.15} h1{font-size:clamp(2rem,6vw,4.25rem);letter-spacing:-.045em;max-width:18ch}
  h2{font-size:clamp(1.45rem,3vw,2.15rem);margin-bottom:1rem} h3{font-size:1.02rem;letter-spacing:.015em}
  p+p{margin-top:.72rem}
}
@layer layout {
  .shell{width:min(1180px,calc(100% - 2rem));margin-inline:auto}.masthead{padding:2.2rem 0 1.5rem;border-bottom:1px solid var(--line)}
  .eyebrow{color:var(--accent);font:700 .76rem/1 var(--mono);letter-spacing:.12em;text-transform:uppercase;margin-bottom:1rem}
  .dek{color:var(--muted);font-size:clamp(1rem,2vw,1.25rem);max-width:72ch;margin-top:1rem}
  .meta{display:flex;flex-wrap:wrap;gap:.6rem 1.25rem;margin-top:1.2rem;color:var(--muted);font:600 .78rem/1.4 var(--mono)}
  nav{position:sticky;top:0;z-index:5;background:color-mix(in srgb,var(--paper) 94%,transparent);border-bottom:1px solid var(--line)}
  nav .shell{display:flex;gap:.9rem;overflow-x:auto;padding:.65rem 0}nav a{white-space:nowrap;font-size:.82rem}
  main{padding:1.5rem 0 4rem}.sheet-section{margin-top:clamp(2.2rem,6vw,4.5rem);scroll-margin-top:4rem}
  .section-note{color:var(--muted);max-width:85ch;margin-bottom:1rem}.entry-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:.8rem}
}
@layer components {
  .signal{display:inline-flex;gap:.35rem;align-items:center;border-radius:999px;padding:.2rem .55rem;font:800 .72rem/1 var(--mono);white-space:nowrap}
  .signal.safe{color:var(--safe);background:var(--safe-bg)}.signal.warn{color:var(--warn);background:var(--warn-bg)}.signal.danger{color:var(--danger);background:var(--danger-bg)}
  .quick{background:var(--surface);border:1px solid var(--line);border-top:5px solid var(--accent);padding:clamp(1rem,3vw,2rem);box-shadow:0 16px 36px rgba(15,23,42,.08)}
  .quick h2{display:flex;align-items:center;gap:.6rem}.quick h2::before{content:"CONTROL REGISTER";font:800 .64rem/1 var(--mono);letter-spacing:.1em;color:var(--paper);background:var(--accent);padding:.38rem .5rem}
  .table-wrap{overflow-x:auto;border:1px solid var(--line);background:var(--surface)}table{width:100%;min-width:720px;font-size:.86rem}
  th,td{padding:.72rem .78rem;border-bottom:1px solid var(--line);vertical-align:top;text-align:left}th{position:sticky;top:0;background:var(--surface-2);font:800 .72rem/1.25 var(--sans);letter-spacing:.04em;text-transform:uppercase}
  tbody tr:hover{background:var(--accent-soft)}td:first-child{font-family:var(--sans);font-weight:760;min-width:12rem}tbody tr:last-child td{border-bottom:0}
  .entry{background:var(--surface);border:1px solid var(--line);padding:1rem;min-width:0}.entry h3{border-left:3px solid var(--accent);padding-left:.65rem;margin-bottom:.65rem}
  .entry p{font-size:.9rem}.example,.gotcha{padding:.65rem;border-left:2px solid var(--safe);background:var(--safe-bg)}.gotcha{border-color:var(--danger);background:var(--danger-bg)}
  .checklist ol{list-style:none;padding:0;display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,320px),1fr));gap:.5rem;counter-reset:steps}.checklist li{counter-increment:steps;background:var(--surface);border:1px solid var(--line);padding:.8rem}.checklist li::before{content:counter(steps,decimal-leading-zero);color:var(--accent);font:800 .7rem/1 var(--mono);margin-right:.55rem}
  .sources ul{list-style:none;padding:0;display:grid;gap:.5rem}.sources li{display:grid;grid-template-columns:minmax(16rem,1fr) 2fr;gap:1rem;border-top:1px solid var(--line);padding:.65rem 0}.sources span{color:var(--muted);font-size:.86rem}
  .related{margin-top:4rem;border:1px solid var(--line);padding:1rem;background:var(--surface-2)}.related h2{font-size:1rem}.related div{display:flex;flex-wrap:wrap;gap:.55rem 1rem}.related a{font-size:.84rem}
  .equation{font:800 clamp(1rem,3vw,1.55rem)/1.4 var(--mono);padding:1rem;border:1px dashed var(--accent);background:var(--accent-soft);overflow-wrap:anywhere}
  .flow{display:grid;grid-template-columns:repeat(auto-fit,minmax(145px,1fr));gap:.55rem}.flow div{position:relative;padding:1rem;background:var(--surface);border:1px solid var(--line);min-height:7rem}.flow b{display:block;color:var(--accent);font:800 .7rem/1 var(--mono);margin-bottom:.5rem}.flow p{font-size:.83rem}
  .callout{border-left:5px solid var(--warn);padding:1rem;background:var(--warn-bg);margin:1rem 0}.print-only{display:none}
}
@layer print {
  @media print{nav{display:none}.shell{width:100%}.sheet-section{break-inside:avoid;margin-top:1.3rem}.entry{break-inside:avoid}a{color:inherit}.print-only{display:block}.table-wrap{overflow:visible}table{min-width:0;font-size:7.7pt}th{position:static}}
  @media(max-width:600px){.shell{width:min(100% - 1rem,1180px)}.masthead{padding-top:1.2rem}.sources li{grid-template-columns:1fr}.quick{padding:.8rem}.table-wrap{margin-inline:-.5rem}.entry-grid{grid-template-columns:1fr}}
}
"""


def render(page: dict[str, object]) -> str:
    title = str(page["title"])
    description = str(page["description"])
    slug = str(page["slug"])
    sections = str(page["sections"])
    nav = "".join(f'<a href="#{slugify(label)}">{esc(label)}</a>' for label in page["nav"])
    schema = {
        "@context": "https://schema.org", "@type": "TechArticle", "headline": title,
        "description": description, "author": {"@type": "Person", "name": "David Veksler (AI Generated)"},
        "publisher": {"@type": "Organization", "name": "David Veksler Cheatsheets"},
        "datePublished": VERIFIED, "dateModified": VERIFIED, "keywords": page["keywords"],
    }
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(description)}"><meta name="keywords" content="{esc(page['keywords'])}">
<link rel="canonical" href="https://cheatsheets.davidveksler.com/{slug}.html">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:type" content="website"><meta property="og:url" content="https://cheatsheets.davidveksler.com/{slug}.html"><meta property="og:image" content="images/{slug}.png"><meta property="og:image:alt" content="{esc(page['image_alt'])}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="{esc(title)}"><meta name="twitter:description" content="{esc(description)}"><meta name="twitter:image" content="images/{slug}.png"><meta name="twitter:creator" content="@heroiclife">
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB" crossorigin="anonymous">
<link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/bootstrap-icons.min.css" rel="stylesheet" integrity="sha384-CK2SzKma4jA5H/MXDUU7i1TqZlCFaD4T01vtyDFvPlD97JQyS+IsSh1nI2EFbpyk" crossorigin="anonymous">
<script type="application/ld+json">{json.dumps(schema, separators=(',', ':'))}</script><style>{CSS}</style></head>
<body><header class="masthead"><div class="shell"><p class="eyebrow">Crypto custody &amp; compliance · engineering reference</p><h1>{esc(page['h1'])}</h1><p class="dek">{esc(page['dek'])}</p><div class="meta"><span>LAST VERIFIED: {VERIFIED}</span><span>VOLATILE CLAIMS: DATE-TAGGED</span><span>PRINT: LANDSCAPE TABLES</span></div></div></header>
<nav aria-label="Page sections"><div class="shell"><a href="#quick-reference">Quick reference</a>{nav}<a href="#sources">Sources</a></div></nav>
<main class="shell"><section class="quick" id="quick-reference" aria-labelledby="quick-title"><h2 id="quick-title">{esc(page['quick_title'])}</h2>{page['quick']}</section>{sections}{related([item for item in page['related'] if item[1] != slug + '.html'])}</main>
<footer class="shell meta"><p>Last verified: {VERIFIED} · Built as a standalone operational reference. Verify live policy, chain, and vendor state before production changes.</p></footer></body></html>"""


PAGES: list[dict[str, object]] = []


# 1. MPC wallet architecture -------------------------------------------------
mpc_protocols = [
    ["Lindell17", "ECDSA · 2-party", "Interactive online signing", "Paillier + ZK proofs", "Historical baseline; use only audited, patched implementations"],
    ["GG18", "ECDSA · t-of-n", "Offline presigning + online rounds", "Paillier MtA", "Influential; implementation proof validation is security-critical"],
    ["GG20", "ECDSA · t-of-n", "Adds identifiable abort", "Paillier MtA", "Blame does not remove malformed-proof risk"],
    ["CMP / CGGMP", "ECDSA · t-of-n", "Proactive refresh; non-interactive presigning", "Paillier + commitments", "Modern family; pin paper, code commit, and audit together"],
    ["DKLs", "ECDSA · 2-party / t-of-n variants", "OT-based multiplication", "Oblivious transfer", "Avoids Paillier; different implementation surface"],
    ["FROST (RFC 9591)", "Schnorr / EdDSA · t-of-n", "2 signing rounds", "Prime-order group + hash", "RFC is Informational; coordinator selection remains external"],
    ["MuSig2 (BIP 327)", "Schnorr · n-of-n", "2 communication rounds", "Key aggregation", "Not threshold: every signer is required"],
]
mpc_sections = (
    table("Protocol lineage", ["Family", "Output / quorum", "Rounds & preprocessing", "Core assumption", "Operational reading"], mpc_protocols,
          "Protocol names are not interchangeable. Record the exact paper revision, implementation commit, curve suite, and audit. RFC 9591 was checked August 2026.")
    + cards("Key lifecycle", [
        ("Distributed key generation", "Each party contributes entropy and proves consistency; no dealer ever possesses the aggregate private key.", "For a 2-of-3 wallet, retain the DKG transcript hash, participant identities, public key, and independently derived first address.", "Importing and splitting a pre-existing seed leaves a full-key compromise moment."),
        ("Signing", "Participants validate the same canonical payload, consume one presign package where applicable, and produce an ordinary chain signature.", "Bind request ID <code>wd_20260831_0042</code>, chain ID, nonce, asset, amount, destination, fee ceiling, and policy decision into the audit record.", "A quorum can correctly sign a malicious payload supplied by a compromised policy engine."),
        ("Proactive refresh", "Shares are re-randomized while the public key and address remain unchanged; old and new epoch shares cannot be combined.", "Refresh quarterly and after a suspected host compromise; prove completion on all three parties before deleting epoch N material.", "A configured job that has never completed a restore test is not a control."),
        ("Resharing", "A live quorum changes <code>t-of-n</code> or replaces participants without moving funds.", "Replace a departing 2-of-3 signer with a new HSM and verify the unchanged public key before revoking the old share.", "Below-threshold survivors cannot reshare; the address is permanently frozen."),
        ("Retirement", "Move remaining assets, destroy every live share and presign cache, and retain non-secret audit evidence.", "After a chain is delisted, sweep all derivation paths, reconcile zero balances, then obtain destruction attestations from each domain.", "Deleting the vendor workspace while dust or token contracts remain creates orphaned value."),
    ])
    + table("Share custody topology", ["Topology", "Correlated failure", "Liveness", "Recovery", "Collusion floor"], [
        ["3 VMs / one cloud account / one IAM role", '<span class="signal danger">BROKEN</span>', "Fast", "Easy", "One admin credential"],
        ["Separate cloud accounts, same provider", '<span class="signal warn">CONDITIONAL</span>', "High", "Moderate", "2 account compromises"],
        ["Two cloud providers + on-prem HSM", '<span class="signal safe">DIVERSE</span>', "Medium", "Harder", "2 trust domains"],
        ["Vendor 2 shares + customer HSM share", '<span class="signal warn">VERIFY</span>', "Vendor-dependent", "Exit package required", "Vendor + customer or vendor internal quorum"],
        ["Mobile approver + cloud + HSM", '<span class="signal warn">DEVICE RISK</span>', "High", "User lifecycle heavy", "2 device/domain compromises"],
    ], "Three hosts are not three trust domains. Model IAM, hypervisor, update channel, operator, region, and recovery authority.")
    + cards("What MPC does not protect", [
        ("Policy-engine compromise", "The signer sees an authorized request, so threshold secrecy provides no safety.", "Require an independently operated callback to compare the payload with ledger intent before any share acts.", "Putting policy and all shares under one admin collapses the architecture."),
        ("Blind signing", "Approvers who see only a digest cannot verify the human-readable destination or contract call.", "Decode EIP-712 or chain-native intent on a separate trusted display and bind it to the request.", "A green approval screen can describe different bytes than the signer receives."),
        ("Address substitution", "Malware changes a destination after business approval but before canonical serialization.", "Use allowlists with a 48-hour activation delay and out-of-band confirmation for additions.", "Clipboard checks and prefix/suffix matching are not authentication."),
        ("Threshold insider collusion", "Exactly <code>t</code> valid participants are sufficient by design.", "Set role separation so two approvers cannot also administer policy or signer infrastructure.", "2-of-3 is not two humans if automation controls both shares."),
        ("Missing attribution", "The chain records one aggregate signature, not which parties participated.", "Write append-only participant, policy, payload, and transcript hashes to an external audit store.", "On-chain indistinguishability trades away native signer attribution."),
        ("Supply-chain compromise", "A malicious library or signer image can bias nonces, leak shares, or rewrite payloads.", "Pin reproducible builds, SBOM, signatures, audit commit, and measured boot evidence.", "A mathematically proven protocol does not prove the deployed binary."),
    ])
    + table("Custody primitive decision matrix", ["Primitive", "On-chain footprint", "Quorum change", "Attribution", "Exit failure"], [
        ["Threshold MPC", "Ordinary single signature", "Same address via reshare", "Off-chain log only", "Need export/reshare package"],
        ["Native multisig", "Visible; chain-specific fee", "Usually new policy/address", "Often visible", "Independent signers can survive coordinator"],
        ["Smart-contract wallet", "Contract call + execution gas", "Upgradeable policy", "Event/log dependent", "Chain and contract governance remain"],
        ["Single-key HSM", "Ordinary signature", "Re-key requires move", "HSM audit log", "Backup/key ceremony determines survival"],
        ["Hybrid MPC hot + multisig cold", "Tier-dependent", "Independent paths", "Mixed", "Reduces common vendor failure"],
    ], "Use MPC for broad chain coverage and stable addresses; native multisig for independently verifiable cold quorums; hybrid tiering when correlated vendor risk dominates.")
    + checklist("Vendor due-diligence checklist", [
        "Name the protocol, revision, ciphersuite, implementation commit, and every production audit.",
        "Prove DKG was used; document any full-key import path and when it is allowed.",
        "Map shares to independent IAM, cloud, region, operator, HSM, backup, and update domains.",
        "Show completed refresh and resharing evidence, not configuration screenshots.",
        "Explain malformed-proof validation, nonce handling, presign reuse prevention, and identifiable abort.",
        "Separate policy administration from signer administration and require quorum for policy changes.",
        "Provide an export/exit package and execute a restore in an isolated environment.",
        "Measure signing availability for the chosen quorum; alert before survivors fall below threshold.",
        "Retain payload and participant attribution outside the vendor's trust domain.",
        "Test vendor disappearance, customer-share loss, cloud outage, and revoked operator scenarios."],
        "A protocol label is the start of diligence, not the result.")
    + cards("Common mistakes & anti-patterns", [
        ("Seed import called MPC", "Splitting a key after creation is secret sharing, not dealerless generation.", "Mark imported wallets as a distinct assurance class.", "Marketing vocabulary cannot erase the full-key event."),
        ("One-manager quorum", "Multiple accounts still share one coercion and employment boundary.", "Require independent reporting lines for high-value tiers.", "Org-chart correlation defeats technical separation."),
        ("ECDSA-only selection", "ECDSA threshold families do not sign Ed25519-native chains.", "Inventory chain signature schemes before procurement.", "Raw signing may bypass transaction parsing and policy."),
        ("No exit rehearsal", "Exportability exists only if a second implementation can restore and sign.", "Run an annual isolated restore using the contractual package.", "A PDF procedure is not evidence of recoverability."),
    ])
    + sources([
        ("RFC 9591 — FROST", "https://www.rfc-editor.org/rfc/rfc9591.html", "Two-round threshold Schnorr ciphersuites and security considerations."),
        ("NIST IR 8214", "https://csrc.nist.gov/pubs/ir/8214/final", "Threshold terminology, validation challenges, and implementation risk."),
        ("NIST Multi-Party Threshold Cryptography", "https://csrc.nist.gov/Projects/threshold-cryptography", "Current program state; IR 8214C final published January 2026."),
        ("BIP 327 — MuSig2", "https://github.com/bitcoin/bips/blob/master/bip-0327.mediawiki", "n-of-n Schnorr multisignature; not a threshold quorum."),
    ])
)
PAGES.append({"slug":"mpc-wallet-architecture","title":"MPC Wallet Architecture: Threshold Signing in Production","h1":"MPC wallet architecture","description":"Engineer and audit threshold-signing wallets: DKG, ECDSA and FROST protocol families, share topology, refresh, resharing, liveness, failure modes, and vendor diligence.","keywords":"MPC wallet architecture, threshold signatures, DKG, FROST, GG18, CMP, crypto custody","dek":"The useful question is not whether a wallet says “MPC.” It is which protocol, which trust domains, which lifecycle controls, and which failure leaves the address spendable.","image_alt":"Control-room matrix comparing MPC, multisig, smart-contract wallets, and HSM custody","quick_title":"The threshold guarantee — and its boundary","quick":table("Threshold signing model",["Term","Precise meaning","Production test"],[
    ["Share", "A secret contribution; never a standalone private key", "Exfiltrating one share cannot sign or reconstruct below threshold"],
    ["DKG", "Parties jointly create the key; no dealer knows it", "Transcript and independently derived public key agree"],
    ["t-of-n", "Any t participants can sign; fewer reveal nothing", "Exercise every authorized quorum and one below-threshold set"],
    ["Refresh", "New shares, same aggregate key and address", "Old epoch + new epoch shares do not form a valid quorum"],
    ["Reshare", "Change participants or quorum without moving funds", "Public key is byte-identical before and after"],
    ["Boundary", "MPC protects key use, not transaction intent", '<span class="signal danger">POLICY IS SEPARATE</span>'],
  ],"NIST calls out that real implementation security can diverge from the ideal primitive. Treat the signer, policy engine, callback, approver device, and audit store as separate trust surfaces."),"sections":mpc_sections,"nav":["Protocol lineage","Key lifecycle","Share custody topology","What MPC does not protect","Custody primitive decision matrix","Vendor due-diligence checklist","Common mistakes & anti-patterns"],"related":SHARED_RELATED + [("Bitcoin self-custody", "bitcoin-self-custody-guide.html"),("Post-quantum cryptography", "post-quantum-cryptography.html")]})


# 2. Blockchain deposits and withdrawals ------------------------------------
finality_rows = [
    ["Bitcoin", "PoW · probabilistic", "~10 min target", "mempool → block depth", "1 / 3 / 6 blocks by value", "No protocol-final state"],
    ["Ethereum", "PoS · economic finality", "12 s slot", "head → safe → finalized", "Use <code>safe</code> or <code>finalized</code>", "Finality normally spans epochs; query the node"],
    ["Solana", "PoS + Tower BFT", "~400 ms slot target", "processed → confirmed → finalized", "Use commitment parameter explicitly", "Finalized means max lockout / rooted"],
    ["Tron", "DPoS / SR", "~3 s", "latest → solidified", "Credit only solidified for withdrawal", "Resource and SR behavior differ from EVM"],
    ["BNB Smart Chain", "PoSA", "Network-upgrade dependent", "latest → finalized", "Use finality RPC where supported", "Never hard-code an old block interval"],
    ["Polygon PoS", "Heimdall/Bor + Ethereum checkpoints", "~2 s Bor", "Bor inclusion → checkpoint", "Separate fast credit from bridge exit", "PoS reorg and L1 checkpoint are different states"],
    ["Avalanche C-Chain", "Snowman · accepted finality", "Sub-second to seconds", "processing → accepted", "Require accepted", "Do not add Bitcoin-style confirmations mechanically"],
    ["Litecoin", "PoW · probabilistic", "~2.5 min target", "block depth", "Value-tiered depth", "Security budget differs from Bitcoin"],
    ["Dogecoin", "PoW · probabilistic", "~1 min target", "block depth", "Value-tiered depth", "Merged mining does not make depth policies identical"],
    ["Bitcoin Cash", "PoW · probabilistic", "~10 min target", "block depth", "Value-tiered depth", "Deep-reorg history requires incident override"],
    ["XRP Ledger", "Federated consensus", "~3–5 s ledger", "open → validated", "Credit validated ledger only", "Destination tag is part of deposit identity"],
    ["Stellar", "SCP · deterministic", "Usually seconds", "pending → successful ledger", "Successful ledger close", "Memo is part of deposit identity"],
    ["Cardano", "Ouroboros · probabilistic", "~20 s slot", "block depth", "Node/venue risk policy", "Settlement assurance grows with depth"],
    ["Cosmos SDK / CometBFT", "BFT · deterministic", "Chain configured", "commit", "Committed block", "Validator-set and chain halts dominate"],
    ["Tezos", "PoS with finality", "Protocol-version dependent", "head → finalized", "Use finalized level", "Upgrade can change timing parameters"],
    ["Aptos", "Jolteon/DiemBFT", "Sub-second target", "pending → executed", "Committed execution", "Expiration timestamp is operationally significant"],
    ["Sui", "Narwhal/Bullshark lineage", "Path dependent", "effects certified/checkpointed", "Checkpointed for external credit", "Fast-path and consensus-path semantics differ"],
    ["TON", "PoS sharded", "Shard/masterchain dependent", "included → masterchain confirmed", "Observe masterchain state", "Shard routing and memo identity matter"],
]
deposit_sections = (
    table("Finality register", ["Chain", "Consensus", "Cadence", "Native vocabulary", "Credit rule", "Critical caveat"], finality_rows,
          "Cadences are protocol targets or typical ranges, not SLAs. A production adapter must query live network state and carry an incident override. Last checked August 2026.")
    + cards("Finality vocabulary & Layer 2", [
        ("Probabilistic depth", "Each additional PoW block raises reversal cost but never creates a protocol-final flag.", "A venue may expose 1-block provisional credit while holding withdrawals until 6 blocks for a large BTC deposit.", "Applying the same count to Dogecoin and Bitcoin ignores security-budget differences."),
        ("Economic finality", "A PoS checkpoint becomes reversible only through exceptional consensus failure and slashable behavior.", "On Ethereum, request <code>safe</code> for lower latency or <code>finalized</code> for the strongest standard RPC state.", "The JSON-RPC <code>latest</code> tag is not a finality promise."),
        ("Optimistic rollup", "Sequencer receipt, L1 data publication, and challenge-window completion are three different moments.", "Credit a small Arbitrum deposit after L1 inclusion but gate bridge-dependent withdrawal until the relevant protocol state.", "An L2 cannot be more final than the L1 data and state it inherits."),
        ("ZK rollup", "Validity proof acceptance on L1 establishes state correctness; data availability and L1 finality remain separate.", "Track batch inclusion, proof verification, and L1 finalized block as independent fields.", "A sequencer UI saying final does not prove L1 settlement."),
    ])
    + cards("EVM nonce runbook", [
        ("Single-writer allocator", "One durable allocator leases sequential nonces per hot address; workers never poll independently for the next value.", "Lease nonce 418 for 60 seconds, persist request ID and fee fields, then mark broadcast by transaction hash.", "Two workers reading <code>pending</code> can assign the same nonce."),
        ("Gap handling", "A missing nonce blocks every later transaction from that address.", "If 418 is stuck and 419–425 are queued, replace 418 first; do not keep adding higher nonces.", "A gap can look like seven unrelated provider failures."),
        ("Replacement", "Resubmit the same nonce with the same intent and a sufficiently higher effective fee.", "Keep <code>maxPriorityFeePerGas</code> and <code>maxFeePerGas</code> under a policy ceiling, then reconcile whichever hash lands.", "A replacement creates multiple hashes for one withdrawal intent."),
        ("Throughput sharding", "Nonce serialization is per sender, so scale with multiple funded hot addresses.", "Route withdrawals deterministically across 8 addresses while retaining per-address single writers.", "Sharding multiplies gas, reconciliation, policy, and rebalancing surfaces."),
    ])
    + table("UTXO operations", ["Operation", "Control", "Worked value", "Do not"], [
        ["Coin selection", "Minimize input cost, change, and privacy leakage", "At 20 sat/vB, a 68-vB input costs ~1,360 sat to spend", "Select nominal value without effective value"],
        ["Batching", "One transaction, many outputs", "10 P2WPKH outputs avoid repeating 10 transaction overheads", "Mix incompatible urgency or screening states"],
        ["RBF", "Replace an opt-in unconfirmed transaction", "Same inputs; higher fee; preserve withdrawal identity", "Credit both hashes"],
        ["CPFP", "Spend a low-fee parent output with a high-fee child", "Package feerate must clear the target", "Assume every output is spendable"],
        ["Consolidation", "Merge small UTXOs during low-fee windows", "Only consolidate inputs whose future fee saving exceeds current cost", "Create one operationally catastrophic mega-UTXO"],
        ["Descriptor scan", "Derive monitored addresses with an explicit range", "Persist last-used index and scan beyond configured lookahead", "Rely on an implicit gap limit"],
    ], "Fee examples are arithmetic, not fee recommendations. Query a current node estimator and enforce a maximum policy.")
    + cards("Gas station & deposit hazards", [
        ("Token sweep funding", "A token-holding address also needs the chain's native asset to pay execution fees.", "Detect USDC, estimate sweep gas, fund only the bounded amount, then sweep and reconcile both transactions.", "Pre-funding every address strands native asset and expands attack value."),
        ("Contract identity", "Token contract and chain identify an asset; symbol and decimals are display metadata.", "Credit only the allowlisted Ethereum USDC contract and read its configured 6 decimals.", "A fake token can emit the same symbol and Transfer event."),
        ("Memo / destination tag", "Some chains multiplex users behind one address; the tag is part of the account key.", "Store <code>(chain,address,tag)</code> and hold unmatched XRP deposits for operations review.", "Address-only indexing miscredits or strands deposits."),
        ("Address poisoning", "Zero-value or dust transfers plant a lookalike address in history.", "Never populate destinations from recent on-chain counterparties; use authenticated address books.", "Prefix/suffix visual checks are weak against generated lookalikes."),
        ("Transfer semantics", "Fee-on-transfer, rebasing, and contract-originated moves break naive amount assumptions.", "Credit the observed balance delta after finality, not the requested calldata amount.", "Transaction success does not imply the expected token amount arrived."),
    ])
    + table("Reconciliation break taxonomy", ["Mismatch", "Detection", "Likely cause", "First response"], [
        ["On-chain, no ledger", "Finalized inbound absent internally", "Indexer/webhook loss", "Pause auto-sweep; backfill by block range"],
        ["Ledger, no chain", "Broadcast intent has no accepted hash", "Timeout/crash before broadcast", "Query provider by idempotency ID before retry"],
        ["Duplicate credit", "Same transfer identity posted twice", "At-least-once delivery", "Reverse duplicate journal entry; fix uniqueness key"],
        ["Orphaned credit", "Credited block no longer canonical", "Reorg", "Freeze derived availability; post compensating entry"],
        ["Amount mismatch", "Observed delta differs from ledger amount", "Decimals/fee-on-transfer", "Quarantine asset adapter"],
        ["Wrong network", "Supported address, unsupported chain", "User routing error", "Do not automate recovery; assess key/control path"],
        ["Fee drift", "On-chain fee ≠ booked expense", "Replacement or estimator error", "Attach all hashes to one intent and settle actual fee"],
        ["In-flight snapshot", "Invariant break clears next cycle", "Timing boundary", "Model in-flight account explicitly; do not use tolerance"],
    ], "Balance tolerance is zero. Timing differences belong in explicit in-flight accounts, not an unexplained reconciliation allowance.")
    + checklist("Common mistakes & incident checklist", [
        "Use an internal immutable transaction ID as the key; treat every chain hash as an output/version.",
        "Record requested, safe, and finalized block identifiers—not just a confirmation count.",
        "Centralize nonce allocation and expose lease, gap, replacement, and expiry telemetry.",
        "Check native-fee balance before token sweep and cap automated funding.",
        "Persist chain + contract + address + tag/memo + log index as deposit identity.",
        "Verify token contract and decimals; measure balance delta for unusual tokens.",
        "Make webhook consumers idempotent and back them with block-range polling.",
        "Raise confirmation policy during consensus incidents; never wait for a code deploy.",
        "Alert before descriptor/lookahead exhaustion and test skipped-address recovery.",
        "Reconcile more frequently than the shortest customer withdrawal SLA."], "Run this list before enabling a new chain or asset.")
    + table("Observed incident register", ["Network / date", "Observed event", "Evidence", "Engineering consequence"], [
        ["Bitcoin · 2013-03-11", "0.8/0.7 consensus split from Berkeley DB lock behavior", '<a href="https://bitcoin.org/bip/50/">BIP 50</a>: fork at height 225,430; experimental double-spend documented', "Suspend on node-version disagreement; height is not a unique ID"],
        ["Bitcoin · 2013-08-16", "Unpatched nodes forked at block 252,451", '<a href="https://bitcoin.org/bip/50/">BIP 50 resolution record</a>', "Track consensus alerts and client versions, not depth alone"],
        ["Ethereum Classic · 2020-07-31", "Successful 51% reorganization attack", '<a href="https://www.ethereumclassic.org/knowledge/history/">Project history</a>', "Static confirmation policy can become obsolete during attack"],
        ["Ethereum Classic · 2020-08-06", "Third successful 51% reorganization attack", '<a href="https://www.ethereumclassic.org/knowledge/history/">Repeated within one week</a>', "Pause can be safer than adding a few blocks"],
        ["Ethereum Classic · 2020-08-29", "Fourth successful 51% reorganization attack", '<a href="https://www.ethereumclassic.org/knowledge/history/">Repeated in same month</a>', "Security budget and incident state govern policy"],
    ], "Where a primary record does not establish a trustworthy depth, this register does not invent one. Absence of a number is safer than a false confirmation rule.")
    + table("Value-at-risk policy pattern", ["Tier", "Credit", "Withdrawal", "Incident overlay"], [
        ["Low", "Provisional at conservative safe level", "Hold until settled", "Raise or pause automatically"],
        ["Medium", "Chain-native safe/final state", "Additional risk/KYT hold", "Manual release during instability"],
        ["High", "Strongest final state + independent node agreement", "Human approval after reconciliation", "Pause on fork/finality alarm"],
    ], "Derive bands from loss tolerance and attack economics; never treat one universal confirmation count as an asset property.")
    + sources([
        ("Ethereum consensus and PoS finality", "https://ethereum.org/developers/docs/consensus-mechanisms/pos/", "Slots, epochs, justification and finalization."),
        ("Solana commitment", "https://solana.com/docs/rpc", "RPC commitment parameters and chain-native status vocabulary."),
        ("Bitcoin developer reference", "https://developer.bitcoin.org/reference/", "Transactions, blocks, mempool and wallet primitives."),
        ("Circle CCTP finality", "https://developers.circle.com/cctp/concepts/finality-and-block-confirmations", "Current cross-chain confirmed/finalized thresholds and timing."),
        ("EIP-1559", "https://eips.ethereum.org/EIPS/eip-1559", "Typed transaction fee fields and replacement context."),
    ])
)
PAGES.append({"slug":"blockchain-deposits-withdrawals","title":"Blockchain Deposits & Withdrawals: Finality and Operations","h1":"Blockchain deposits & withdrawals","description":"Production reference for chain finality, confirmation policy, EVM nonces, UTXO selection, gas stations, deposit identity, idempotency, and reconciliation failures.","keywords":"blockchain confirmations, finality, crypto deposits, withdrawals, nonce management, UTXO, reconciliation","dek":"A transaction hash is evidence, not identity. Credit policy begins with the chain’s native finality model and ends with an invariant that detects every missing, duplicated, or orphaned posting.","image_alt":"Per-chain finality and confirmation policy control register","quick_title":"Per-chain finality policy","quick":table("Value-tiered credit states",["State","Customer balance","Withdrawal","Required evidence"],[
    ["Observed", "Hidden / pending", "Blocked", "Transaction parsed; asset identity validated"],
    ["Provisional", "May display", "Blocked", "Canonical block at adapter-defined safe depth"],
    ["Credited", "Available by value tier", "Risk hold may remain", "Chain-native safe/final state"],
    ["Settled", "Available", "Allowed by policy", "Reconciled ledger posting + final chain evidence"],
    ["Orphaned", '<span class="signal danger">REVERSE</span>', "Freeze derived funds", "Previously observed block left canonical chain"],
  ],"Keep block hash, height/slot, status vocabulary, adapter version, and policy version with every decision. A bare integer confirmation count cannot be audited across chains."),"sections":deposit_sections,"nav":["Finality register","Finality vocabulary & Layer 2","EVM nonce runbook","UTXO operations","Gas station & deposit hazards","Reconciliation break taxonomy","Observed incident register","Value-at-risk policy pattern","Common mistakes & incident checklist"],"related":SHARED_RELATED + [("Bitcoin wallet", "bitcoin-wallet.html")]})


# 3. Institutional custody ---------------------------------------------------
ccss_rows = [
    ["1.01 Key/Seed Generation", "Approved entropy and controlled generation", "Stronger separation and validation", "Highest-assurance ceremony evidence", "DKG / ceremony script + entropy attestation"],
    ["1.02 Wallet Creation", "Correct, verified wallet construction", "Independent verification", "Comprehensive control evidence", "Two-device address derivation and sign/verify test"],
    ["1.03 Key/Seed Storage", "Protected storage", "Distributed, access-controlled storage", "Highest isolation and resilience", "Tier topology + geographic inventory"],
    ["1.04 Key/Seed Usage", "Controlled signing", "Stronger authorization and isolation", "Comprehensive transaction controls", "Policy engine + decoded intent + audit log"],
    ["1.05 Key Compromise Policy", "Documented response", "Tested and role-assigned response", "Mature evidence and exercise", "Freeze, rotate/reshare, investigate, notify"],
    ["1.06 Keyholder Grant/Revoke", "Controlled lifecycle", "Dual-control changes", "Auditable, rehearsed lifecycle", "Joiner/mover/leaver + quorum-change ceremony"],
    ["1.07 Log and Monitor", "Security-relevant records", "Monitoring and protected retention", "Comprehensive review and evidence", "External append-only signing and policy logs"],
    ["2.01 Third-Party Security Audits", "Independent review", "Broad scope and remediation", "Sustained assurance", "Audit exact signer/policy release + track closure"],
    ["2.02 Data Sanitization", "Secret-bearing media disposal", "Verified procedures", "Comprehensive evidence", "Crypto erase, device destruction, witness log"],
    ["2.03 Risk Management", "Threats and controls identified", "Periodic assessment", "Mature continuous treatment", "Threat model sets review and test cadence"],
]
custody_sections = (
    table("Custody tier register", ["Tier", "Purpose", "Typical latency", "Approval", "Network exposure", "Loss bound"], [
        ["Hot", "Automated withdrawals", "Seconds–minutes", "Policy + automated signer", "Online", "Strict balance and velocity cap"],
        ["Warm", "Human-gated replenishment", "Minutes–hours", "2-person quorum", "Connected only for workflow", "Per-transfer and daily cap"],
        ["Cold", "Reserve", "Hours–day", "Independent key holders", "Air-gapped ceremony", "Facility/quorum loss tolerance"],
        ["Deep cold", "Long-horizon reserve", "Days", "Geographic retrieval quorum", "Offline, distributed", "Catastrophic correlated-event bound"],
    ], "Percentages are outputs of demand and loss models, not universal best practices.")
    + cards("Tiering & float math", [
        ("Base-stock target", "Cover withdrawals during replenishment lead time at a chosen service level, then cap exposure above that target.", "Mean daily BTC demand $2.0M, one-day replenishment lead, 99th-percentile one-day demand $3.2M: set hot target S=$3.2M, not a portfolio percentage.", "Normal-distribution shortcuts understate fat-tail withdrawal runs."),
        ("Reorder point", "Trigger warm/cold replenishment before available hot inventory reaches expected lead-time demand.", "With $2.0M mean lead-time demand and $1.2M safety stock, reorder at s=$3.2M and replenish to a separately governed S.", "Counting pending deposits as available can postpone replenishment until failure."),
        ("Per-asset sizing", "Each asset has distinct demand, finality, fee, halt, and replenishment behavior.", "USDC payment float may turn daily while an illiquid governance token remains entirely cold.", "Portfolio-wide percentages hide the one chain that cannot replenish during an outage."),
        ("Loss/service cost", "Minimize expected compromise loss + delayed-withdrawal cost + ceremony cost.", "Compare $3.2M hot exposure with an estimated incident loss fraction against the measurable cost of one delayed day and each cold pull.", "False precision in compromise probability is worse than sensitivity ranges."),
    ], "Worked result: the stated profile produces a $3.2M hot target. Recompute from observed withdrawals, replenishment lead, and incident conditions.")
    + cards("Policy engine controls", [
        ("Ordered rules", "Rules match subject, source, destination, asset, amount, time, and action in a documented order.", "Deny unknown destinations first; allow routine USDC only after KYT and velocity gates; route $250k+ to 2-of-3 approval.", "A broad allow above a narrow deny turns rule order into a bypass."),
        ("Destination time lock", "A newly allowlisted destination cannot receive funds until an observation window passes.", "Require 48 hours plus out-of-band confirmation before first transfer; alert on creation and activation.", "Instant allowlisting makes a stolen admin session equivalent to key theft."),
        ("Rolling velocity", "Aggregate amount and count over overlapping windows by user, asset, destination, and risk domain.", "Cap $50k/hour and $200k/24h, with sub-$10k structuring still aggregating.", "Calendar-day resets invite an attacker to straddle midnight."),
        ("Policy-change quorum", "Changing authorization logic is itself a high-risk custody operation.", "Require two administrators from separate roles and a 24-hour delayed activation for production rule changes.", "A mutable policy controlled by one admin is decorative."),
        ("Break glass", "Emergency bypass is narrow, expiring, visible, and separately authorized.", "Open a 30-minute route for one predeclared destination with a maximum amount and after-action review.", "Permanent emergency roles become the normal attack path."),
    ])
    + checklist("Key ceremony script", [
        "Approve purpose, asset/scheme, quorum, participants, facilities, and abort criteria.", "Freeze software, firmware, device serials, hashes, SBOM, and build provenance.",
        "Rehearse the script with non-production material and record expected outputs.", "Sweep room, disable networks, inventory devices, and seal unrelated electronics.",
        "Verify participant identity and role; confirm no person holds conflicting quorum roles.", "Inspect tamper packaging and device provenance in view of independent witnesses.",
        "Collect independent entropy sources where the scheme requires them; log method, never secret value.", "Run DKG or generation; abort on any proof, display, or transcript mismatch.",
        "Derive the aggregate public key and first receive address independently on two implementations.", "Perform a funded canary receive and a complete sign/broadcast/confirm cycle before bulk funding.",
        "Create backups without reconstructing a full key; label scheme, path, epoch, and quorum metadata.", "Seal backups with unique IDs and record custody without photographing secrets.",
        "Distribute shares/backups across approved geographic and administrative domains.", "Sign the ceremony attestation and transcript hashes; note every deviation.",
        "Load policy default-deny, limits, allowlist delays, and audit destinations.", "Reconcile the public inventory against custody records before accepting customer funds.",
        "Schedule refresh/reshare, holder departure, compromise, and retirement ceremonies.", "Schedule an isolated restore drill; define RTO and RPO for signing, not merely the app.",
        "Store evidence outside signer and policy trust domains.", "Close with independent witness and auditor sign-off; destroy temporary secret-bearing media."],
        "A ceremony is executable procedure. If a step lacks owner, evidence, abort condition, and recovery, it is prose.")
    + table("CCSS v9.0 engineering crosswalk", ["Current aspect", "Level I intent", "Level II direction", "Level III direction", "Architecture evidence"], ccss_rows,
          "CCSS v9.0 was published December 17, 2024 and organizes ten aspects across two domains. This table is an engineering navigation aid, not normative requirement text; use C4's current standard for assessment.")
    + table("Assurance landscape", ["Framework / rule", "What it answers", "What it does not answer", "Current engineering hook"], [
        ["CCSS v9.0", "Crypto-system controls across 10 aspects", "Enterprise control completeness by itself", "Map every aspect to evidence"],
        ["SOC 2 Type II", "Control design + operation over a period", "Specific crypto key architecture", "Scope signer, policy, ledger, provider, DR"],
        ["ISO/IEC 27001", "Information-security management system", "Wallet correctness or asset existence", "Risk treatment, supplier and incident processes"],
        ["NIST SP 800-57", "Key-management lifecycle terminology", "Chain-specific custody design", "Generation, activation, rotation, revocation, destruction"],
        ["NYDFS custody guidance", "Segregation, separate accounting, limited use, disclosure", "A universal global custody rule", "Ledger/on-chain segregation and reconciliation"],
        ["MiCA Article 75", "EU CASP custody policy, register, statements, return and segregation", "Technical control implementation", "Client position register and operational segregation"],
    ], "Regulatory status changes. Links below point to primary text checked August 2026; obtain jurisdiction-specific counsel for applicability.")
    + cards("Common mistakes & anti-patterns", [
        ("Hot balance by intuition", "A round portfolio percentage ignores demand and replenishment lead time.", "Calculate per-asset base stock and sensitivity.", "Market moves can double fiat exposure without any operational change."),
        ("Allowlist without delay", "The attacker who controls admin can immediately cash out.", "Alert and hold new destinations 48 hours.", "Out-of-band checks after transfer are forensics, not prevention."),
        ("Untested backup", "Presence of sealed media says nothing about correctness or current metadata.", "Restore annually and verify the first address.", "Discovering a bad backup during disaster converts outage to permanent loss."),
        ("Assessment as outcome", "A level or report is evidence about scoped controls, not immunity from loss.", "Track scope, exclusions, period, tested version, and remediation.", "A vendor badge does not transfer your policy and ledger responsibilities."),
    ])
    + cards("Business continuity, dual control & insurance", [
        ("Signing RTO/RPO", "Recovery objectives apply to authorization and signing, not merely the web/API tier.", "Exercise loss of one site and one key holder; measure time to a valid canary signature and intact audit trail.", "A restored database with no quorum is still a custody outage."),
        ("Role separation", "Initiator, approver, policy admin, signer admin, key holder, and auditor are conflict domains.", "Prohibit one identity from changing a destination rule and satisfying its transfer quorum.", "Two accounts owned by one person do not create dual control."),
        ("Vendor/facility loss", "Exit must recreate shares, paths, addresses, policy, pending state and evidence.", "Restore in an isolated alternate site annually and reconcile a canary address.", "A share without derivation metadata may not restore the portfolio."),
        ("Insurance scope", "Crime, specie, and cyber policies contain peril, hot/cold, location, sublimit, exclusion, and allocation terms.", "Map each tier and subcontractor to the schedule and model loss above each sublimit.", "“Insured up to $X” rarely means every client receives X."),
    ])
    + sources([
        ("CCSS v9.0 details", "https://cryptoconsortium.org/cryptocurrency-security-standard-documentation/ccss-details-v9/", "Current aspect and control structure."),
        ("CCSS overview", "https://cryptoconsortium.org/cryptocurrency-security-standard-documentation/overview/", "Ten aspects, two domains, and level aggregation."),
        ("MiCA Article 75", "https://eur-lex.europa.eu/eli/reg/2023/1114/oj", "Custody agreements, register, policy, return and segregation."),
        ("NYDFS virtual-currency guidance", "https://www.dfs.ny.gov/virtual_currency_businesses", "Current guidance index; 2025 custody update supersedes 2023 guidance."),
        ("NIST SP 800-57 Part 1", "https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final", "General key-management lifecycle guidance."),
    ])
)
PAGES.append({"slug":"institutional-crypto-custody","title":"Institutional Crypto Custody: Tiers, Controls, and CCSS","h1":"Institutional crypto custody","description":"Design institutional digital-asset custody tiers, hot-wallet float, policy engines, dual control, key ceremonies, disaster recovery, and a CCSS v9.0 control crosswalk.","keywords":"institutional crypto custody, CCSS v9, hot warm cold wallet, key ceremony, policy engine","dek":"Custody is the control system around a signing primitive: asset float, policy, people, evidence, recovery, and a ledger that still balances when a facility or vendor disappears.","image_alt":"Institutional hot warm cold and deep-cold custody tier control register","quick_title":"Four tiers, four bounded failure domains","quick":table("Custody tier quick reference",["Tier","Automation","Target","Transfer gate","Verdict"],[
    ["Hot", "Continuous", "Lead-time withdrawal demand", "Default-deny policy + velocity", '<span class="signal danger">LIMIT EXPOSURE</span>'],
    ["Warm", "Workflow", "Replenishment buffer", "Human quorum + delayed destinations", '<span class="signal warn">CONDITIONAL</span>'],
    ["Cold", "Ceremony", "Reserve", "Offline independent key holders", '<span class="signal safe">ISOLATED</span>'],
    ["Deep cold", "Retrieval", "Long-horizon reserve", "Geographic quorum + multi-day process", '<span class="signal safe">DIVERSE</span>'],
  ],"The correct hot amount is a demand quantile over replenishment lead time, not “5% of AUC.” Every tier needs a documented loss bound and a tested way back."),"sections":custody_sections,"nav":["Custody tier register","Tiering & float math","Policy engine controls","Key ceremony script","CCSS v9.0 engineering crosswalk","Assurance landscape","Business continuity, dual control & insurance","Common mistakes & anti-patterns"],"related":SHARED_RELATED + [("Personal cybersecurity", "personal-cybersecurity.html")]})


# 4. Crypto compliance architecture -----------------------------------------
ivms_payload = """<section class="sheet-section" aria-labelledby="ivms101-payload"><h2 id="ivms101-payload">IVMS101.2023 worked payload</h2>
<p class="section-note">Illustrative transport envelope: validate against the counterparty network's current IVMS101.2023 schema and required jurisdictional fields. Names use structured identifiers; dates use ISO 8601.</p>
<pre><code>{
  "originator": {"originatorPersons": [{"naturalPerson": {
    "name": [{"nameIdentifier": [{"primaryIdentifier": "Rivera", "secondaryIdentifier": "Elena", "nameIdentifierType": "LEGL"}]}],
    "geographicAddress": [{"addressType": "HOME", "streetName": "740 Market Street", "townName": "Denver", "countrySubDivision": "CO", "postCode": "80202", "country": "US"}],
    "nationalIdentification": {"nationalIdentifier": "CUST-78421", "nationalIdentifierType": "CUST"},
    "customerIdentification": "cust_78421", "dateAndPlaceOfBirth": {"dateOfBirth": "1987-04-12", "placeOfBirth": "Santa Fe, US"}
  }}], "accountNumber": ["acct_78421"]},
  "beneficiary": {"beneficiaryPersons": [{"legalPerson": {
    "name": [{"nameIdentifier": [{"legalPersonName": "Northwind Components LLC", "legalPersonNameIdentifierType": "LEGL"}]}],
    "geographicAddress": [{"addressType": "BIZZ", "streetName": "1650 Blake Street", "townName": "Denver", "countrySubDivision": "CO", "postCode": "80202", "country": "US"}],
    "nationalIdentification": {"nationalIdentifier": "20261234567", "nationalIdentifierType": "RAID", "registrationAuthority": "RA000602"}
  }}], "accountNumber": ["0x2B7C...91E4"]},
  "originatingVASP": {"originatingVASP": {"legalPerson": {"name": [{"nameIdentifier": [{"legalPersonName": "Origin VASP Inc", "legalPersonNameIdentifierType": "LEGL"}]}]}}},
  "beneficiaryVASP": {"beneficiaryVASP": {"legalPerson": {"name": [{"nameIdentifier": [{"legalPersonName": "Destination VASP Ltd", "legalPersonNameIdentifierType": "LEGL"}]}]}}},
  "transferPath": {"transferPath": [{"sequence": 0, "account": "acct_78421"}, {"sequence": 1, "account": "0x2B7C...91E4"}]},
  "payloadMetadata": {"transliterationMethod": ["none"]}
}</code></pre><div class="callout"><strong>Do not copy identity values into production.</strong> Store consent/lawful-basis, schema version, counterparty identity, transport receipt, policy decision, and the minimum data actually required.</div></section>"""
compliance_sections = (
    cards("Gate placement rules", [
        ("Deposit observation", "Parse chain, contract, amount, source, destination, tag, and finality before any customer posting.", "Open a compliance case on a new USDC transfer while the balance remains pending.", "Screening after credit lets tainted value fund internal trades or withdrawals."),
        ("Pre-credit KYT", "Screen the actual transfer and counterparty exposure before making funds available.", "Persist provider, model/list version, score, categories, hop depth, and raw response hash.", "A naked score cannot be reproduced after the vendor model changes."),
        ("Pre-sign withdrawal gate", "All identity, Travel Rule, sanctions, destination, and business-policy checks must pass before irreversible signing.", "The signer callback verifies compliance case <code>case_20418=cleared</code> and exact destination bytes.", "Screening between signing and broadcast leaves a valid signed payload that can escape."),
        ("Rescreen on list update", "Addresses and persons previously clean can become blocked property when lists change.", "Subscribe to list changes, rescreen held positions and pending transfers, and open retroactive cases.", "A once-at-onboarding result silently expires."),
        ("Fail closed", "Provider outage blocks automated value movement while an explicit, dual-controlled manual route handles exceptions.", "After 60 seconds of KYT timeout, queue rather than sign; page operations before SLA breach.", "Fail-open turns the outage into an ideal attacker window."),
    ])
    + table("Compliance gate map", ["Path", "Gate", "Input", "On hit", "If placed later"], [
        ["Deposit", "Asset validation", "chain + contract + decimals", "Quarantine", "Fake token may be credited"],
        ["Deposit", "KYT exposure", "source + transfer graph", "Pending/manual review", "Funds become internally spendable"],
        ["Deposit", "Sanctions", "person + address + live list", "Block/segregate", "Blocked property may move"],
        ["Deposit", "Finality", "chain-native status", "Wait", "Reorg creates unbacked credit"],
        ["Withdrawal", "Customer/KYC state", "identity + account risk", "Reject/review", "Value enters signer path"],
        ["Withdrawal", "Travel Rule", "counterparty + threshold + IVMS payload", "Hold/send data", "Transfer may breach obligation"],
        ["Withdrawal", "Destination KYT", "address + asset + amount", "Reject/review", "Signed transaction exists"],
        ["Withdrawal", "Policy callback", "ledger intent + decoded payload", "Do not sign", "Broadcast control is too late"],
    ], "The control boundary is signing. A signed blockchain transaction is a bearer-like capability even if your broadcaster has not submitted it yet.")
    + table("Travel Rule implementation register", ["Regime", "Engineering baseline", "De minimis posture", "Unhosted-wallet concern", "Primary text"], [
        ["FATF R.16", "Originator/beneficiary information; VASP-to-VASP transmission", "Countries implement locally", "Risk-based treatment", '<a href="https://www.fatf-gafi.org/en/topics/fatf-recommendations.html">FATF</a>'],
        ["United States", "31 CFR / FinCEN funds-transfer rules and BSA records", "Thresholds depend on rule and transaction class", "Identify applicable counterparty/rule", '<a href="https://www.ecfr.gov/current/title-31/subtitle-B/chapter-X">eCFR Title 31</a>'],
        ["European Union", "Regulation 2023/1113 applies information duties to crypto transfers", "No general crypto de minimis", "Self-hosted interactions require risk controls", '<a href="https://eur-lex.europa.eu/eli/reg/2023/1113/oj">EUR-Lex</a>'],
        ["United Kingdom", "Money Laundering Regulations + FCA implementation", "Verify current UK requirements", "Risk-based evidence", '<a href="https://www.fca.org.uk/firms/financial-crime/cryptoassets-aml-ctf-regime">FCA</a>'],
        ["Switzerland", "AMLA/AMLO-FINMA implementation", "Verify current Swiss threshold", "Proof of control often material", '<a href="https://www.finma.ch/en/supervision/fintech/">FINMA</a>'],
        ["Singapore", "Payment Services Act / MAS notices", "Verify current notice and scope", "Counterparty due diligence", '<a href="https://www.mas.gov.sg/regulation/anti-money-laundering">MAS</a>'],
        ["Japan", "Act / JFSA and JVCEA implementation", "Verify current local rule", "Counterparty controls", '<a href="https://www.fsa.go.jp/en/">JFSA</a>'],
        ["Canada", "PCMLTFA / FINTRAC virtual-currency transfer records", "CAD threshold rules vary by duty", "Identity and records", '<a href="https://fintrac-canafe.canada.ca/guidance-directives/transaction-operation/vctr/vctr-eng">FINTRAC</a>'],
        ["Australia", "AML/CTF regime and AUSTRAC guidance", "Verify reforms and commencement", "Counterparty and ownership risk", '<a href="https://www.austrac.gov.au/business/core-guidance/amlctf-programs">AUSTRAC</a>'],
        ["Hong Kong", "AMLO VASP regime", "Verify current threshold and circulars", "Risk-based controls", '<a href="https://www.sfc.hk/en/Regulatory-functions/Intermediaries/Virtual-asset-trading-platforms-operators">SFC</a>'],
        ["UAE", "Federal plus competent-authority rule", "Depends on regulator/free zone", "Counterparty verification", '<a href="https://www.vara.ae/en/regulations/regulations/">VARA</a>'],
    ], "This is a routing register, not a legal threshold table. Thresholds and scope depend on entity, activity, corridor, and current local implementation; resolve them in maintained policy data before launch.")
    + table("IVMS101 field map", ["Object / field", "Cardinality / type", "Constraint", "Common rejection"], [
        ["originator / beneficiary", "1 object", "Person arrays + account number", "Flattening all persons into one name"],
        ["naturalPerson.name", "1..n", "Structured <code>nameIdentifier</code>", "Single free-text full name"],
        ["legalPerson.name", "1..n", "Legal-person identifier structure", "Using natural-person fields"],
        ["nameIdentifierType", "code", "Controlled vocabulary such as <code>LEGL</code>", "Unrecognized local code"],
        ["geographicAddress", "0..n", "Typed address + ISO country", "Country name instead of alpha-2 code"],
        ["addressType", "code", "Controlled vocabulary", "Billing/home/business semantics mixed"],
        ["nationalIdentification", "0..1", "Identifier + type; authority where required", "Sending raw document without type"],
        ["dateAndPlaceOfBirth", "0..1", "ISO date + place", "Locale-formatted date"],
        ["customerIdentification", "0..1", "VASP customer identifier", "Reusing government ID"],
        ["accountNumber", "0..n strings", "Chain/account or internal account", "Dropping memo/tag"],
        ["originatingVASP / beneficiaryVASP", "0..1", "Legal-person identity", "Trusting a domain name as identity"],
        ["transferPath", "0..1", "Ordered intermediaries", "Losing sequence"],
        ["payloadMetadata", "0..1", "Encoding/transliteration metadata", "No Latin/local script strategy"],
    ], "IVMS101 standardizes identity data; it does not standardize discovery, transport, certificate trust, or corridor policy.")
    + ivms_payload
    + cards("KYT, sanctions & data protection", [
        ("Hop depth", "Indirect exposure is a policy parameter; at enough hops almost every liquid address becomes connected.", "Store direct and 1-hop exposure separately and require a documented threshold by category.", "Treating graph distance as moral certainty creates unbounded false positives."),
        ("Vendor disagreement", "Attribution and clustering are models, not shared facts.", "Route a high-value disagreement to evidence review; retain each vendor's label version.", "Averaging opaque scores does not create truth."),
        ("Dynamic sanctions data", "Lists add and remove identifiers; application code must consume versioned authoritative data.", "Treat the OFAC SDN feed as an external signed/versioned input and rescreen on update.", "Hard-coded addresses become wrong in both directions."),
        ("Blocked-property response", "Freeze and segregate; route reporting, recordkeeping, and legal decisions to the applicable program.", "Open one case linking asset, list version, timestamps, owners, decisions, and reports.", "Automatically returning funds may itself be prohibited."),
        ("Data minimization", "Transmit required identity data only to an authenticated counterparty under a recorded lawful mechanism.", "Encrypt in transit and at rest, separate compliance payload from chain transaction, and expire unnecessary copies.", "The blockchain is not a place for Travel Rule personal data."),
    ])
    + checklist("Blocked-property and alert runbook", [
        "Atomically freeze availability and prevent signing; preserve the exact screening response.", "Identify governing entity, program, list entry, ownership/control basis, and transaction state.",
        "Segregate or label the position so routine sweeps and reconciler repairs cannot move it.", "Do not return, consolidate, or test-transfer value without authorized legal determination.",
        "Open a privileged case with timestamps, list version, assets, chain evidence, and decision owners.", "Evaluate required blocking/rejection reports and deadlines under the applicable program.",
        "Evaluate separate suspicious-activity reporting and anti-tipping-off constraints.", "Notify internal legal/compliance/security through the documented channel, not ordinary support notes.",
        "Rescreen related customers, addresses, counterparties, and pending transfers.", "Retain records and schedule ongoing/annual reporting where the applicable rule requires it.",
        "Test release/delisting path with dual control and complete audit evidence.", "After closure, repair the placement or data defect that allowed exposure."],
        "Deadlines are jurisdiction- and program-specific. The runbook must link to maintained legal policy, never freeze a number in application code.")
    + cards("Common mistakes & anti-patterns", [
        ("Screen after broadcast", "The irreversible action already happened.", "Gate before signing.", "A broadcaster hold does not neutralize signed bytes."),
        ("Hard-coded lists", "Sanctions state changes without software releases.", "Consume authoritative versioned feeds.", "Delisting is as important as designation."),
        ("Score as fact", "A vendor's risk score encodes taxonomy and model choices.", "Store evidence, category, distance, model and appeal path.", "Threshold tuning without false-positive measurement is guesswork."),
        ("Unauthenticated counterparty", "Correct IVMS data sent to the wrong VASP is a breach.", "Verify certificate/entity before payload transmission.", "Protocol membership is not universal identity assurance."),
    ])
    + table("KYT integration surfaces", ["Provider", "Documented surface", "Retain", "Do not infer"], [
        ["Chainalysis", "APIs and platform workflows", "category, exposure, score, evidence/version", "Cross-vendor score equivalence"],
        ["TRM Labs", "APIs and case workflows", "risk indicators, attribution, graph context", "Attribution immutability"],
        ["Elliptic", "Wallet/transaction screening APIs", "risk rule, category, path, timestamp", "Identical taxonomy"],
        ["Merkle Science", "Transaction-monitoring APIs", "rule hit, exposure, model state", "Score as legal conclusion"],
        ["Crystal", "Blockchain-analytics APIs", "entity/category and transaction evidence", "Universal chain/token coverage"],
    ], "Recheck each vendor's public documentation before procurement. This compares integration shape, not quality, experience, or rank.")
    + table("Travel Rule protocol interoperability", ["Protocol/network", "Transport/discovery", "Identity trust", "Payload", "Architecture implication"], [
        ["TRISA", "Certificate-backed directory/messaging", "VASP certificates", "IVMS101-compatible", "Operate certificate lifecycle and discovery"],
        ["TRP", "Open protocol specifications", "Implementation-dependent counterparty verification", "IVMS101 mapping", "No universal directory"],
        ["OpenVASP", "Open messaging/identity design", "Protocol-defined VASP identity", "Structured Travel Rule data", "Reach may require another network"],
        ["Commercial broker", "Vendor directory and routed transport", "Vendor onboarding model", "Often IVMS101", "Broker concentration and exit are controls"],
    ], "The payload is standardized more broadly than transport and discovery. Multi-network routing, receipts, retries, and counterparty identity are first-class state.")
    + sources([
        ("IVMS101.2023", "https://www.intervasp.org/", "Maintainer page and current data model download."),
        ("FATF virtual-asset guidance", "https://www.fatf-gafi.org/en/publications/Fatfrecommendations/Guidance-rba-virtual-assets-2021.html", "Recommendation 16 implementation context."),
        ("EU Regulation 2023/1113", "https://eur-lex.europa.eu/eli/reg/2023/1113/oj", "Information accompanying crypto-asset transfers."),
        ("OFAC sanctions data", "https://ofac.treasury.gov/sanctions-list-service", "Authoritative list service and digital-currency identifiers."),
        ("FinCEN regulations", "https://www.ecfr.gov/current/title-31/subtitle-B/chapter-X", "Current BSA regulatory text."),
    ])
)
PAGES.append({"slug":"crypto-compliance-architecture","title":"Crypto Compliance Architecture: KYT, Travel Rule, IVMS101","h1":"Crypto compliance architecture","description":"Place KYT, sanctions, Travel Rule, and policy gates correctly; implement an IVMS101 field map and payload; and handle alerts without signing irreversible transfers.","keywords":"crypto compliance architecture, KYT, Travel Rule, IVMS101, sanctions screening, VASP","dek":"Compliance is transaction architecture. The decisive question is whether a gate runs before credit and before signing, with enough versioned evidence to reproduce the decision months later.","image_alt":"Deposit and withdrawal compliance gate map showing controls before credit and signing","quick_title":"Gate before irreversibility","quick":'<div class="flow"><div><b>01 · OBSERVE</b><p>Parse chain, contract, transfer identity and finality.</p></div><div><b>02 · SCREEN</b><p>KYT + sanctions with model/list version.</p></div><div><b>03 · IDENTIFY</b><p>Customer, counterparty VASP, corridor, unhosted status.</p></div><div><b>04 · TRANSMIT</b><p>Minimum IVMS101 data to authenticated counterparty.</p></div><div><b>05 · AUTHORIZE</b><p>Ledger intent, policy, velocity, approvals.</p></div><div><b>06 · SIGN</b><p>Only the exact cleared payload.</p></div></div><p class="callout"><strong>Signing is the boundary.</strong> “Screen before broadcast” is too late if valid signed bytes already exist.</p>',"sections":compliance_sections,"nav":["Gate placement rules","Compliance gate map","Travel Rule implementation register","IVMS101 field map","IVMS101.2023 worked payload","KYT, sanctions & data protection","KYT integration surfaces","Travel Rule protocol interoperability","Blocked-property and alert runbook","Common mistakes & anti-patterns"],"related":SHARED_RELATED})


# 5. Stablecoin payment infrastructure --------------------------------------
stablecoin_sections = (
    table("Stablecoin operating register", ["Asset / model", "Issuer/control", "Reserve class", "Freeze surface", "Operator consequence"], [
        ["USDC · fiat-backed", "Circle", "Cash / short-duration liquid reserve per issuer reports", "Issuer-controlled addresses", "Native contract + chain + issuer redemption are separate risks"],
        ["USDT · fiat-backed", "Tether", "Issuer-reported reserve mix", "Issuer-controlled addresses", "Chain support and direct redemption terms differ"],
        ["PYUSD · fiat-backed", "Paxos", "Issuer-regulated reserve reporting", "Issuer-controlled addresses", "Contract admin and regulated issuer are dependencies"],
        ["EURC · fiat-backed", "Circle", "Euro-denominated issuer reserve", "Issuer-controlled addresses", "FX and banking-calendar exposure differ from USD rails"],
        ["DAI / USDS family · crypto/RWA-backed", "Protocol governance", "On-chain collateral + RWA structures", "Governance/module dependent", "Peg and governance risk differ from issuer token"],
        ["Synthetic / delta-neutral", "Protocol/operator", "Hedged derivatives + custody", "Protocol-specific", "Funding, exchange and liquidation risks replace reserve cash"],
    ], "Do not use supply figures or chain counts from this table: both drift quickly. Pull issuer APIs/reports at decision time and save the as-of snapshot.")
    + cards("Reserve, redemption & token controls", [
        ("Attestation ≠ audit", "An agreed-upon-procedures report tests specified assertions at a point/date; it does not opine on the whole business.", "Record report period, reporting accountant, procedures, reserve cutoff, and liabilities definition.", "A monthly PDF cannot prove intraday liquidity or future redemption."),
        ("Redemption right", "Token price converges to par only when eligible parties can redeem under workable limits and banking schedules.", "Model direct issuer redemption, exchange sale, and market-maker path separately for a $5M treasury exit.", "Retail token holders may not have the same direct claim or minimum."),
        ("Admin keys", "Pause, blacklist, mint, burn, and upgrade roles are operational dependencies.", "Inventory current contract proxy/admin addresses and alert on role or implementation changes.", "“On-chain” does not mean immutable or permissionless."),
        ("Native vs bridged", "Native issuance is an issuer liability on that chain; bridged representation adds bridge custody and message finality.", "Identify by chain + contract + issuance path; reject symbol-only asset configuration.", "A bridge failure can decouple a representation while native tokens remain sound."),
        ("Banking calendar", "Mint/redemption and fiat settlement may stop while tokens trade continuously.", "Hold weekend liquidity buffers sized to Monday settlement and expected redemption queue.", "24/7 chain settlement does not create 24/7 bank money."),
    ])
    + table("Movement rail comparison", ["Rail", "Finality dependency", "Trust added", "Best use", "Failure mode"], [
        ["Same-chain transfer", "Source chain", "Token admin", "Routine payment", "Reorg, pause/blacklist, gas"],
        ["Centralized exchange/book transfer", "Internal ledger", "Venue solvency/operations", "Liquidity conversion", "Withdrawal halt or account freeze"],
        ["Lock-and-mint bridge", "Both chains + bridge validators/contracts", "Bridge custody", "Unsupported native route", "Exploit or validator compromise"],
        ["Burn-and-mint (CCTP)", "Source finality + attestation + destination", "Issuer attestation service", "Native USDC cross-chain", "Attestation delay / destination submission"],
        ["Liquidity network", "Source payment + provider settlement", "LP/solver", "Fast UX", "Liquidity exhaustion / pricing"],
        ["Bank wire → mint", "Bank settlement + issuer processing", "Bank + issuer", "Treasury creation/redemption", "Cutoff, return, compliance hold"],
    ], "CCTP v2 encodes confirmed=1000 and finalized=2000 thresholds; integrators must still track source transaction, message, attestation, destination mint, and reconciliation as separate states.")
    + cards("Payment operations", [
        ("Invoice identity", "A payment intent fixes asset, chain, contract, amount, destination, expiry, and finality policy.", "Invoice <code>inv_9372</code> expects 1,250.00 USDC on Base contract X before 16:00Z.", "“Send USDC” without chain/contract is not a complete instruction."),
        ("Under/overpayment", "Match observed finalized balance delta to a tolerance and route exceptions.", "Accept $1,249.99 only if the merchant policy permits a one-cent fiat-equivalent tolerance; never hide the delta.", "Token decimals are not business-currency precision."),
        ("Refund", "A refund is a new screened, authorized withdrawal—not reversal of the inbound transaction.", "Link refund <code>rf_881</code> to invoice, verified destination, case, and payout hash.", "Sending to the source address can pay a custodial hot wallet or poisoned route."),
        ("Treasury concentration", "Set issuer, chain, bank, bridge, venue, and intraday-settlement limits.", "Cap any one issuer at a board-approved percentage and keep operational gas in each active chain.", "Diversifying contracts on the same issuer may not diversify credit risk."),
        ("Depeg runbook", "Predefine price source, duration, size, and operational triggers rather than improvising during panic.", "At 0.995 for 15 minutes, pause auto-conversion; at 0.98, require treasury quorum and evaluate redemption path.", "A single thin exchange price can trigger a false cascade."),
    ])
    + table("Finality versus freezability", ["Risk", "On-chain finality solves?", "Issuer/bridge solves?", "Required control"], [
        ["Source-chain reorg", '<span class="signal safe">YES, after finality</span>', "No", "Chain-native finality policy"],
        ["Issuer blacklist", "No", '<span class="signal danger">CONTROL SURFACE</span>', "Exposure limits + screening + legal runbook"],
        ["Bridge exploit", "No", '<span class="signal danger">BRIDGE DEPENDENCY</span>', "Prefer native; cap bridged inventory"],
        ["Bank failure/cutoff", "No", "Redemption path dependent", "Bank diversification + calendar buffer"],
        ["Attestation outage", "Source may be final", '<span class="signal warn">CCTP DELAY</span>', "State machine + retry + reconciler"],
        ["Wrong contract", "A fake transfer may be final", "No", "Allowlist chain + contract"],
    ], "A finalized token transfer may still be frozen, bridged, unreedeemable, or the wrong contract. Settlement assurance is multidimensional.")
    + checklist("Treasury and incident checklist", [
        "Identify chain + contract + issuance path; reject symbol-only configuration.", "Store issuer report period, reserve definition, redemption eligibility, minimum, cutoff, and bank calendar.",
        "Inventory pause/blacklist/mint/upgrade roles and monitor contract implementation changes.", "Track CCTP burn, message, attestation, receive, mint, and refund/re-attest as separate states.",
        "Set issuer, chain, bridge, venue, bank, and intraday settlement concentration limits.", "Maintain native gas buffers and a gas-station low-balance alert per chain.",
        "Price with multiple independent venues and a time-weighted depeg trigger.", "Exercise weekend redemption and bank-holiday liquidity scenarios.",
        "Treat refund as a new screened payout to an authenticated destination.", "Reconcile token balances, in-flight cross-chain messages, issuer receivables, and ledger liabilities to zero."],
        "Stablecoin operations fail at the boundaries between a 24/7 chain, an administered token, a bridge/attestation service, and banking hours.")
    + cards("Common mistakes & anti-patterns", [
        ("Symbol identity", "USDC exists in multiple native and bridged contracts.", "Key by chain + contract + issuance path.", "A fake symbol can produce a final transfer."),
        ("Attestation called audit", "The scope and assertion are narrower.", "Read the procedures and cutoff.", "Cadence does not equal continuous assurance."),
        ("Bridge balance called cash", "The representation adds bridge and destination dependencies.", "Cap and reconcile by route.", "Peg can fail locally while issuer remains solvent."),
        ("One depeg price", "Thin or stale markets can lie.", "Use multiple feeds, duration and size thresholds.", "Automation can sell into the very dislocation it creates."),
    ])
    + table("On-ramp and off-ramp mechanics", ["Rail", "Clock", "Reversal/failure", "Ledger representation", "Use when"], [
        ["Domestic wire", "Bank operating hours", "Return/compliance hold", "Fiat receivable → settled cash → mint", "High-value treasury movement"],
        ["ACH / local batch", "Batch days", "Return window", "Pending receivable distinct from settled", "Lower-cost non-urgent funding"],
        ["Issuer mint/redeem API", "Issuer + bank settlement", "Eligibility, cutoff, account hold", "Issuer receivable/payable + token mint/burn", "Direct eligible treasury operation"],
        ["Exchange conversion", "24/7 trading; fiat rail separate", "Venue withdrawal/counterparty risk", "Venue position + in-flight withdrawal", "Liquidity/asset conversion"],
        ["OTC / market maker", "Contracted settlement", "Counterparty and failed delivery", "Trade receivable/payable", "Large negotiated block"],
    ], "Do not mark tokens issued or redeemed because a bank instruction was submitted. Banking and token events have separate immutable states.")
    + table("Regulatory engineering overlay", ["Regime", "Current status checked", "System requirement shape", "Primary text"], [
        ["US GENIUS Act", "Public Law 119-27, approved 2025-07-18; 2026 implementation rulemaking", "Permitted issuer, reserve/redemption, BSA and lawful-order controls", '<a href="https://www.govinfo.gov/app/details/PLAW-119publ27">GovInfo</a>'],
        ["EU MiCA", "Regulation 2023/1114 in force", "Authorization, reserve segregation/liquidity, redemption and custody", '<a href="https://eur-lex.europa.eu/eli/reg/2023/1114/oj">EUR-Lex</a>'],
        ["EU 2025/1264", "Delegated liquidity/reserve rules published", "Intraday liquidity, emergency availability, custodian concentration", '<a href="https://eur-lex.europa.eu/eli/reg_del/2025/1264/oj">EUR-Lex</a>'],
    ], "Engineering routing map, not legal advice. Effective dates and implementing-rule status belong in maintained policy data.")
    + sources([
        ("Circle USDC transparency", "https://www.circle.com/transparency", "Issuer reserve and assurance materials."),
        ("Circle CCTP v2 technical guide", "https://developers.circle.com/cctp/references/technical-guide", "Burn/mint, nonces and finality thresholds."),
        ("Paxos transparency", "https://www.paxos.com/transparency", "Issuer reserve reporting for Paxos-issued assets."),
        ("Tether transparency", "https://tether.to/en/transparency/", "Issuer-published reserve and supply materials."),
        ("EU MiCA", "https://eur-lex.europa.eu/eli/reg/2023/1114/oj", "EU issuer and crypto-asset service framework."),
    ])
)
PAGES.append({"slug":"stablecoin-payment-infrastructure","title":"Stablecoin Payment Infrastructure: Issuers, Rails, Treasury","h1":"Stablecoin payment infrastructure","description":"Engineer stablecoin payments and treasury: issuer and reserve risk, native versus bridged assets, CCTP states, finality, refunds, depeg controls, and reconciliation.","keywords":"stablecoin payment infrastructure, USDC CCTP, stablecoin treasury, burn and mint, stablecoin reserves","dek":"Stablecoins join four systems with different clocks and failure modes: an issuer, a token contract, a chain or bridge, and banking settlement. Production design must name every dependency.","image_alt":"Stablecoin issuer transport finality and freezability comparison matrix","quick_title":"Finality is not redeemability","quick":table("Decision layers",["Layer","Question","Evidence","Bad shortcut"],[
    ["Asset", "Which chain, contract, and issuance path?", "Allowlisted contract + issuer registry", "Ticker symbol"],
    ["Reserve", "What backs the liability and at what cutoff?", "Issuer report + accountant procedures", "“Audited” badge"],
    ["Transfer", "When is this route final?", "Chain + bridge/attestation state", "Block count copied from another chain"],
    ["Control", "Who can pause, freeze, mint, or upgrade?", "Contract roles + issuer policy", "“Decentralized” label"],
    ["Redemption", "Who can exit at par, when, and how?", "Eligibility + minimum + banking cutoff", "Exchange spot price"],
  ],"A rail is production-ready only when every state has an immutable internal ID, a retry rule, and a reconciliation path."),"sections":stablecoin_sections,"nav":["Stablecoin operating register","Reserve, redemption & token controls","Movement rail comparison","Payment operations","Finality versus freezability","Treasury and incident checklist","On-ramp and off-ramp mechanics","Regulatory engineering overlay","Common mistakes & anti-patterns"],"related":SHARED_RELATED + [("Index investing", "index-investing-tax-advantaged.html")]})


# 6. Custody provider integration -------------------------------------------
provider_sections = (
    table("Generic provider object map", ["Generic concept", "Fireblocks", "BitGo", "Coinbase Prime", "Build invariant"], [
        ["Custody container", "Vault account / asset wallet", "Wallet / enterprise", "Portfolio / wallet / address group", "Your internal account ID remains authoritative"],
        ["Transfer intent", "Transaction + <code>externalTxId</code>", "Transfer / send request", "Onchain transaction", "Client idempotency ID before API call"],
        ["Policy", "Policies / TAP terminology", "Wallet/enterprise policy + webhook rule", "Portfolio/user controls", "Default deny in your domain too"],
        ["Signer hook", "API Co-Signer callback", "Webhook policy / signing architecture", "Platform-managed API flow", "Independent payload-vs-ledger validation"],
        ["Event", "Webhook v2 transaction events", "Wallet/transfer webhooks", "WebSocket/REST state", "Hint only; reconciler is truth"],
        ["Chain evidence", "<code>txHash</code> + status/subStatus", "Transfer hash/state", "Transaction state", "Many hashes may map to one intent"],
    ], "Vendor terminology is dated August 2026. Build an anti-corruption layer so your ledger and state machine do not inherit vendor names.")
    + cards("Authentication, idempotency & webhooks", [
        ("Separate credentials", "Read, create, approve/sign, policy-admin, and workspace-admin capabilities belong in different keys and stores.", "A reconciler key can list transactions but cannot create or approve one.", "One omnipotent key turns a reporting host into a withdrawal host."),
        ("Signed request", "Bind method, path, body hash, nonce/time, and short expiry to the caller identity.", "Hash raw JSON bytes, issue JWT <code>jti=req_8291</code>, and reject clock skew outside the documented window.", "Re-serializing JSON can change the signed bytes."),
        ("Idempotent create", "Generate and persist the client external ID before the first network attempt.", "Retry <code>wd_8291</code> after timeout and query by the same ID before any second create.", "A timeout has unknown outcome; blind retry can pay twice."),
        ("Raw-body verification", "Verify webhook signature and timestamp over exact received bytes before parsing.", "Queue the verified envelope, return 2xx quickly, then process asynchronously.", "Signing parsed JSON breaks when whitespace/key order changes."),
        ("At-least-once consumer", "Deduplicate event IDs, tolerate reordering, and compare polled authoritative state.", "A late <code>PENDING_SIGNATURE</code> event cannot regress a locally reconciled <code>COMPLETED</code> transaction.", "Webhook arrival order is not transaction order."),
        ("Silence alarm", "No events can mean no activity or a broken integration; only polling distinguishes them.", "Poll every 60 seconds and alert when webhook silence exceeds 5 minutes while state changes exist.", "A green HTTP endpoint does not prove events are arriving."),
    ])
    + table("Fireblocks transaction lifecycle", ["Status family", "Meaning", "Terminal?", "Ledger action", "Operator focus"], [
        ["SUBMITTED / PENDING_*", "Created; policy/approval/signing work remains", "No", "Reserve/hold only", "Read exact current status and subStatus"],
        ["QUEUED", "Waiting for processing/resource", "No", "Keep hold", "Queue age and dependency"],
        ["BROADCASTING", "Submission in progress", "No", "Keep hold; no settlement", "Unknown hash/outcome window"],
        ["CONFIRMING", "On chain, confirmation policy pending", "No", "Attach hash/version", "Reorg and replacement"],
        ["COMPLETED", "Provider completion criteria met", "Yes for provider flow", "Settle actual amount/fee after reconciliation", "Verify chain evidence"],
        ["BLOCKED", "Policy/compliance stopped", "Yes unless new intent", "Release/retain hold per case", "Rule number / sanctions context"],
        ["REJECTED", "User, AML, or workflow rejection", "Yes", "Release hold", "Sub-status is the explanation"],
        ["CANCELLED", "Cancelled before completion", "Yes", "Release only after chain query", "May have prior hash/state"],
        ["FAILED", "Provider/chain operation failed", "Yes for this attempt", "Reconcile; compensating entry", "Fee, nonce, connectivity, authorization"],
    ], "Fireblocks primary status and sub-status enums change. Parse unknown values safely, retain raw payload, and alert instead of crashing or treating unknown as success.")
    + table("Failure sub-status operations", ["Sub-status", "Likely domain", "Response"], [
        ["BLOCKED_BY_POLICY", "Policy order / sanctions", "Record rule, do not mutate policy to force retry"],
        ["AUTHORIZATION_FAILED", "API Co-Signer callback", "Check authentication and callback availability"],
        ["REJECTED_AML_SCREENING", "Compliance", "Freeze/route case; preserve provider evidence"],
        ["AUTO_FREEZE", "Transaction screening", "Treat as blocked-property workflow"],
        ["ADDRESS_WHITELISTING_SUSPENDED", "Destination activation", "Wait for configured activation; never bypass"],
        ["ACTUAL_FEE_TOO_HIGH", "Fee policy / market", "Re-estimate within ceiling; create linked attempt"],
        ["AMOUNT_TOO_SMALL", "Dust/minimum/net fee", "Reject before provider call using adapter limits"],
        ["3RD_PARTY_PROCESSING", "Exchange/network dependency", "Poll provider and third party; do not duplicate"],
        ["ON_PREMISE_CONNECTIVITY_ERROR", "Self-hosted component", "Fail closed and execute co-signer failover"],
    ], "These are documented Fireblocks examples as read August 2026. Always store unknown sub-status strings verbatim.")
    + cards("Policy callback & gas station", [
        ("Independent callback", "Your code compares decoded vendor request to the immutable ledger intent before allowing the co-signer share to act.", "Require exact chain, source, destination, asset, amount, fee ceiling, case ID, and policy version.", "If callback and transaction creator share one credential/host, the independence is cosmetic."),
        ("Critical-path availability", "Callback uptime becomes withdrawal signing uptime, so failure must be observable and closed.", "Deploy across two fault domains, use bounded timeouts, and test that timeout rejects rather than approves.", "A fail-open callback nullifies the strongest integration control."),
        ("Gas Station", "Fireblocks can auto-fuel EVM vault accounts so token sweeps have native gas.", "Enable <code>autoFuel</code> only on intended deposit vaults; monitor source balance and unexpected funding volume.", "The gas source can run dry exactly when sweep backlog peaks."),
        ("Exit package", "Provider disappearance is a designed failure, not a contract footnote.", "Restore keys/shares, derivation data, policies, address inventory, pending transactions, and audit evidence in isolation.", "Key export without path and address metadata may be unusable."),
    ])
    + table("Platform due-diligence register", ["Platform", "Public integration surface", "Custody/signing model to verify", "Policy/signer hook", "Exit question"], [
        ["Fireblocks", "REST/SDK + Webhooks v2", "MPC-CMP / workspace configuration", "Policies + API Co-Signer callback", "Can customer reshare/export each wallet class?"],
        ["BitGo", "REST SDK + webhooks", "Multisig/TSS by product", "Wallet policies + webhook policy", "Which keys and metadata remain customer-held?"],
        ["Coinbase Prime", "REST/FIX/WebSocket", "Qualified-custody/platform paths", "Portfolio/user controls", "How are wallets and transaction history exported?"],
        ["Copper", "Public docs/API where available", "MPC/custody product-specific", "Verify documented policy hook", "Independent recovery/export package?"],
        ["Anchorage Digital", "Public API/docs where available", "Institutional custodian", "Verify programmatic approval surface", "Asset return and history format?"],
        ["Dfns", "API + webhooks", "Wallet-as-a-service MPC", "Policy/approval surface", "Key export/reshare per network?"],
        ["Turnkey", "API + policy engine", "Secure enclave / sub-organization model", "Signed policy operations", "Root quorum and export path?"],
        ["Safe", "Smart-contract accounts + SDK", "On-chain owner threshold", "Modules/guards", "Can owners operate without hosted service?"],
        ["Self-build", "Your API", "Chosen open protocol + HSM/enclave", "Your policy/callback", "You own every audit and chain adapter"],
    ], "No ranking or pricing. Capabilities are product/configuration specific and must be reverified in public docs and contracts; absence from a public page is not evidence of absence.")
    + checklist("Go-live integration checklist", [
        "Persist client idempotency ID before every create call and enforce database uniqueness.", "Separate read, create, approve/sign, policy-admin, and workspace-admin credentials.",
        "Verify request/webhook signatures over exact bytes; enforce timestamp and replay window.", "Acknowledge events quickly, queue durably, deduplicate, and tolerate reordering.",
        "Poll authoritative transaction state and chain evidence on a fixed cadence.", "Handle unknown status/sub-status values without treating them as success.",
        "Default deny in provider policy and in your own pre-sign callback.", "Test callback timeout, authentication failure, regional outage, and failover.",
        "Alert on webhook silence, stuck state age, queue depth, gas-source balance, and reconciler lag.", "Execute a full export/exit restore, including paths, addresses, pending state and audit history.",
        "Reconcile provider balances, chain balances, in-flight transfers, fees and ledger liabilities to zero.", "Write stuck, rejected, replaced, reorged and provider-unavailable runbooks before customer funds."],
        "Buying signing infrastructure does not buy your ledger, reconciler, compliance placement, nonce allocator, support operation, or exit plan.")
    + cards("Common mistakes & anti-patterns", [
        ("Webhook as truth", "Delivery can duplicate, reorder, delay, or disappear.", "Poll and reconcile.", "Exactly-once is an application invariant, not a transport guarantee."),
        ("Parsed-body signature", "The verified bytes differ from received bytes.", "Capture raw body first.", "Framework middleware often destroys the evidence."),
        ("Status without sub-status", "The actionable reason is discarded.", "Persist and route both.", "“Failed” cannot tell fee from policy from co-signer outage."),
        ("Untested export", "Contractual capability may not restore a live wallet.", "Execute isolated exit annually.", "Vendor failure is the worst time to discover format gaps."),
    ])
    + sources([
        ("Fireblocks capabilities", "https://developers.fireblocks.com/docs/capabilities", "Vaults, policies, transactions and Gas Station."),
        ("Fireblocks transaction webhooks", "https://developers.fireblocks.com/reference/transaction-webhooks", "Current event fields and Webhooks v1 deprecation notice."),
        ("Fireblocks sub-statuses", "https://developers.fireblocks.com/reference/sub-statuses", "Operational error and policy taxonomy."),
        ("BitGo webhook policy", "https://developers.bitgo.com/docs/policies-webhook/", "Public transaction-policy callback behavior."),
        ("Coinbase Prime APIs", "https://docs.cdp.coinbase.com/prime/introduction/welcome", "Public REST, FIX, WebSocket, custody and transaction surface."),
    ])
)
PAGES.append({"slug":"custody-provider-integration","title":"Fireblocks & Custody Provider Integration Patterns","h1":"Custody provider integration","description":"Integrate Fireblocks and custody platforms safely: vault models, idempotent transaction APIs, co-signer callbacks, webhooks, status/sub-status handling, gas stations, and exit tests.","keywords":"Fireblocks integration, custody API, webhook idempotency, API Co-Signer, crypto custody provider","dek":"A provider should be mapped into your model—not allowed to become it. Your immutable transaction ID, policy decision, ledger, polling reconciler, and exit package remain authoritative.","image_alt":"Custody provider transaction lifecycle and webhook reconciliation state machine","quick_title":"Webhooks are hints; reconciliation is truth","quick":'<div class="flow"><div><b>01 · INTENT</b><p>Persist internal ID and ledger hold.</p></div><div><b>02 · CREATE</b><p>Send external/idempotency ID once.</p></div><div><b>03 · AUTHORIZE</b><p>Provider policy + independent callback.</p></div><div><b>04 · SIGN</b><p>Exact decoded payload only.</p></div><div><b>05 · OBSERVE</b><p>Webhook v2 into durable queue.</p></div><div><b>06 · RECONCILE</b><p>Poll provider + chain; settle actuals.</p></div></div><p class="equation">one internal intent → 0..n API attempts → 0..n chain hashes → exactly one final ledger outcome</p>',"sections":provider_sections,"nav":["Generic provider object map","Authentication, idempotency & webhooks","Fireblocks transaction lifecycle","Failure sub-status operations","Policy callback & gas station","Platform due-diligence register","Go-live integration checklist","Common mistakes & anti-patterns"],"related":SHARED_RELATED})


# 7. Crypto exchange architecture -------------------------------------------
exchange_sections = (
    cards("Matching engine", [
        ("Single-writer sequencer", "A total ordered command log makes execution deterministic and replayable.", "Sequence order <code>9,184,201</code> reserves balance, enters a BTC-USD limit order, and emits all resulting fills before <code>9,184,202</code>.", "Distributed writers create conflicting price-time order and irreproducible books."),
        ("Price-level book", "Ordered price map points to FIFO queues; add/cancel is near O(1) within a known level and best-price lookup follows the ordered structure.", "A post-only bid at $62,500 joins the tail of that price level unless it would cross.", "Floating-point price keys create equality and ordering defects."),
        ("Order semantics", "Limit, market, stop, IOC, FOK, post-only, and iceberg orders change when/how quantity enters the book.", "A 5 BTC FOK must fill completely immediately or cancel without partial execution.", "Implementing order labels without exact atomic behavior produces customer disputes."),
        ("Self-trade prevention", "Prevent related accounts from matching themselves under an explicit cancel-new/cancel-old/decrement policy.", "Apply the configured account-group rule before a fill enters the journal.", "Post-trade cleanup cannot undo misleading market data."),
        ("Recovery", "Snapshot + append-only journal restores state, then deterministic replay produces the identical book and sequence.", "Load snapshot at sequence 9,180,000, replay 4,201 commands, compare state hash before reopening.", "A database balance snapshot cannot reconstruct queue priority."),
    ])
    + table("Ledger design rules", ["Rule", "Concrete form", "Invariant", "Failure prevented"], [
        ["Double entry", "Every journal transaction sums debits and credits per asset", "Σ postings = 0", "Value creation/loss"],
        ["Integer minor units", "BTC satoshis; token base units; wide integer/decimal", "Exact arithmetic", "18-decimal rounding drift"],
        ["Immutable journal", "Corrections are compensating entries", "History never rewritten", "Untraceable balance edits"],
        ["Available vs total", "Holds reserve open orders/withdrawals", "available = total − holds", "Double-spend of customer liability"],
        ["Idempotent posting", "Unique business event + version", "One event, one journal result", "Duplicate webhook/fill credit"],
        ["Projection", "Balance is derived/cached with journal checkpoint", "Projection equals replay", "Authoritative mutable balance row"],
        ["Domain boundary", "Book and wallet only post through ledger API", "No direct chain/book coupling", "Hidden liability changes"],
    ], "Use explicit asset units and enforce per-asset zero-sum at the database boundary, not in application convention.")
    + table("Wallet-boundary crossings", ["Crossing", "Ordered sequence", "Ledger effect", "Chain effect", "Break signal"], [
        ["Deposit", "observe → validate → finality → screen → credit", "Liability increases", "External asset arrives", "On-chain asset without liability"],
        ["Trade/internal transfer", "reserve → match → settle journal", "Liabilities move between accounts", "None", "Any chain dependency"],
        ["Withdrawal", "hold/debit → screen → approve → sign → broadcast → settle", "Liability decreases / in-flight closes", "Asset leaves", "Broadcast before debit/hold"],
        ["Sweep", "detect → authorize → move → reconcile fee", "No customer-liability change; fee/asset location only", "Internal address movement", "Sweep booked as customer flow"],
        ["Rebalance", "policy → transfer between tiers → reconcile", "Asset-location accounts move", "Internal custody movement", "Reserve invariant changes"],
    ], "Most exchange transactions are ledger entries and never touch a chain. The wallet system never talks to the book; both talk to the ledger.")
    + table("Addressing model comparison", ["Model", "Attribution", "Sweep/gas", "Privacy", "Provability", "Operational risk"], [
        ["Omnibus address", "Memo/internal ledger", "Lowest", "Poor on-chain separation", "Aggregate only", "Tag mistakes; ledger critical"],
        ["Per-user deposit address → pool", "Address derivation", "High; gas station often needed", "Better inbound separation", "Address history visible", "Gap/lookahead and sweep backlog"],
        ["Segregated custody", "Address is position boundary", "Highest", "On-chain linkability varies", "Individual control easier to evidence", "Large key/policy/address surface"],
    ], "Legal and operational segregation are not identical. MiCA Article 75 and NYDFS guidance both make the internal position register and segregation design material.")
    + cards("Withdrawal pipeline at scale", [
        ("Reservation", "Place an immutable hold before any external action so available balance cannot be spent twice.", "A $25,000 USDC withdrawal moves available → withdrawal-hold in one serializable transaction.", "Debiting after broadcast allows concurrent spending."),
        ("Batching", "Combine compatible screened intents while retaining output-to-intent mapping.", "Ten Bitcoin P2WPKH withdrawals share one version/locktime/input set; each output maps to one internal ID.", "One tainted or urgent output can poison an entire batch."),
        ("Fee spike", "Queue policy distinguishes urgency, customer quote, ceiling, and replacement path.", "Hold low-priority withdrawals above 200 sat/vB while expiring quotes and showing queue state.", "Flat fees without cost accounting socialize extreme chain cost invisibly."),
        ("Outage drain", "Rate-limit release of backlog across policy, signer, chain, and support capacity.", "Drain 1,000 queued transfers in value tiers with fresh rescreening and nonce/UTXO allocation.", "Releasing all at once resembles an attack and exhausts hot float."),
    ])
    + table("Proof-of-reserves constructions", ["Construction", "Proves", "Does not prove", "Attack / control"], [
        ["Signed address message", "Control of listed keys at a time", "Ownership, unencumbered asset, completeness", "Borrowed assets; repeat unpredictably"],
        ["Asset self-transfer", "Ability to move listed asset", "No hidden lien/liability", "Snapshot gaming; combine with books"],
        ["Merkle liabilities", "A customer leaf is included in committed set", "No omitted users or negative balances by itself", "Omission/negative leaf; audit construction"],
        ["ZK liabilities", "Committed sum and constraints such as non-negative balances", "Off-balance-sheet claims unless included", "Circuit/scope audit"],
        ["Reserve oracle/feed", "Publisher's stated observation", "Independent solvency", "Staleness and publisher trust"],
    ], "Proof of reserves is not proof of solvency. A point-in-time assets proof says nothing about undisclosed liabilities or what happens immediately after the snapshot.")
    + cards("Risk, APIs & market data", [
        ("Margin boundary", "Cross margin shares collateral; isolated margin bounds a position's collateral and liquidation path.", "Journal collateral, unrealized PnL, fees, funding and liquidation as explicit accounts.", "Mixing risk-engine projections with settled ledger balances hides insolvency."),
        ("Mark price", "A robust index/mark drives margin and liquidation, not the venue's last thin trade.", "Use multiple spot sources, staleness guards and bounded deviation.", "A manipulable last price can trigger forced liquidation."),
        ("Snapshot + delta", "Clients load an order-book snapshot then apply contiguous sequence deltas.", "On gap 81,104 → 81,107, discard local book and resnapshot.", "Applying deltas through a gap creates a plausible but false book."),
        ("Client order ID", "Unique client identity makes order create safe to retry.", "Query <code>cli_20260831_771</code> after timeout before another create.", "Transport timeout is not evidence of rejection."),
    ])
    + checklist("Common mistakes & anti-patterns", [
        "Never use binary floating point for price, quantity, fee, balance, or PnL.", "Never let matching engine or risk engine read live chain state.",
        "Credit only after adapter-defined finality and compliance gates.", "Book sweeps/rebalances as asset-location changes, not liability changes.",
        "Hold/debit before signing or broadcast; release only after authoritative terminal reconciliation.", "Require zero unexplained balance tolerance; model in-flight explicitly.",
        "Scan HD addresses with persisted range/lookahead and alert before exhaustion.", "Do not publish assets-only proof as solvency.",
        "Resynchronize market data on any sequence gap.", "Reconcile customer liabilities + firm positions + fees against on-chain + in-flight + receivables continuously."],
        "The architecture cannot prevent an authorized operator from overriding controls; governance, segregation, and external assurance must make that override visible and costly.")
    + sources([
        ("MiCA Regulation 2023/1114", "https://eur-lex.europa.eu/eli/reg/2023/1114/oj", "Client position registers and custody segregation."),
        ("NYDFS virtual-currency guidance", "https://www.dfs.ny.gov/virtual_currency_businesses", "Current custody and customer-asset guidance index."),
        ("FIX Trading Community", "https://www.fixtrading.org/standards/", "Protocol standards for institutional order flow."),
        ("Bitcoin developer reference", "https://developer.bitcoin.org/reference/", "Chain transaction and wallet primitives."),
        ("How to Build a Bitcoin Exchange, Part 1", "https://freethepeople.org/how-to-build-a-bitcoin-exchange-part-1/", "David Veksler's 2017 design-goals article; this page is the engineering continuation."),
    ])
)
PAGES.append({"slug":"crypto-exchange-architecture","title":"Crypto Exchange Architecture: Ledger, Matching, Wallet Boundary","h1":"Crypto exchange architecture","description":"Design a crypto exchange around deterministic matching, a double-entry ledger, wallet-boundary invariants, deposit and withdrawal pipelines, reconciliation, and proof of reserves.","keywords":"crypto exchange architecture, matching engine, double entry ledger, wallet system, proof of reserves","dek":"The matching engine makes trades; the ledger makes them true; the wallet subsystem crosses into a chain. Most catastrophic defects live at the boundary between those statements.","image_alt":"Crypto exchange system map with a heavy wallet boundary and ledger invariant","quick_title":"The system map and hard invariant","quick":'<div class="flow"><div><b>CLIENT</b><p>REST · WebSocket · FIX</p></div><div><b>RISK</b><p>Balance holds · limits · STP</p></div><div><b>SEQUENCER</b><p>Total ordered commands</p></div><div><b>MATCHER</b><p>Deterministic in-memory book</p></div><div><b>LEDGER</b><p>Immutable double-entry truth</p></div><div><b>WALLET BOUNDARY</b><p>Deposit · withdrawal · sweep · rebalance</p></div></div><p class="equation">customer liabilities + fees + firm position = on-chain holdings + in-flight settlements + receivables</p><p class="callout"><strong>Continuous assertion:</strong> if the equation breaks, stop withdrawals before explaining the difference.</p>',"sections":exchange_sections,"nav":["Matching engine","Ledger design rules","Wallet-boundary crossings","Addressing model comparison","Withdrawal pipeline at scale","Proof-of-reserves constructions","Risk, APIs & market data","Common mistakes & anti-patterns"],"related":SHARED_RELATED + [("Bitcoin exchanges & cards", "bitcoin-exchanges-cards.html")]})


# 8. Wallet recovery forensics ----------------------------------------------
recovery_sections = (
    table("Recovery feasibility triage", ["Case", "Secret exposure", "Constraint", "First safe action", "Verdict"], [
        ["Valid seed, wrong path", "None", "Known wallet/era/address", "Offline path + script matrix scan", '<span class="signal safe">LIKELY</span>'],
        ["One missing 12-word position", "Seed candidates", "11 known words + checksum", "Enumerate 2,048 words; checksum prunes", '<span class="signal safe">TRACTABLE</span>'],
        ["One missing word, unknown position", "Seed candidates", "11 words + 12 positions", "Enumerate positions × wordlist; checksum", '<span class="signal safe">TRACTABLE</span>'],
        ["Two missing words", "Seed candidates", "10 known + positions", "Compute exact combinations before hardware", '<span class="signal warn">MEASURE</span>'],
        ["Remembered password structure", "Encrypted wallet copy", "Mask/token grammar", "Benchmark KDF on copy; checkpoint", '<span class="signal warn">DEPENDS</span>'],
        ["Unknown BIP39 passphrase", "Seed remains valid", "No length/word constraints", "Build honest candidate model", '<span class="signal danger">OFTEN INFEASIBLE</span>'],
        ["Lost seed + intact unlocked device", "Live device", "Export/transfer window", "Isolate and move using native UI", '<span class="signal warn">TIME CRITICAL</span>'],
        ["Lost seed + locked/wiped hardware", "Device", "PIN retry/chip model", "Stop attempts; document device/version", '<span class="signal danger">SPECIALIST / NO</span>'],
        ["Deleted wallet file", "Disk image", "Blocks not overwritten", "Power down; forensic image; carve copy", '<span class="signal warn">UNCERTAIN</span>'],
        ["No key, seed, file, device or constraints", "None", "Unconstrained key space", "Do not pay anyone", '<span class="signal danger">IMPOSSIBLE</span>'],
    ], "Never type a seed into a website. Work on copies, isolate secrets, record every transformation, and move recovered funds to a newly generated wallet after verification.")
    + cards("The wallet is often looking in the wrong place", [
        ("Derivation path", "The same seed creates different accounts under different purpose, coin, account, change, and index values.", "Scan <code>m/44'/0'/0'</code>, <code>m/49'/0'/0'</code>, <code>m/84'/0'/0'</code>, and <code>m/86'/0'/0'</code> only in an offline, systematic plan.", "Random path guessing loses coverage and evidence."),
        ("Script type", "Legacy, wrapped SegWit, native SegWit, and Taproot encode different output scripts and addresses.", "Match a known historical receive address before scanning balances.", "A valid seed can show zero when the wallet defaults to the wrong script family."),
        ("BIP39 passphrase", "Every passphrase—including empty—derives a valid but unrelated wallet.", "Test remembered spelling, normalization, spaces, case and language from a constrained list.", "There is no checksum that tells you the passphrase is “close.”"),
        ("Account/index range", "Funds can sit beyond a wallet's default account or lookahead range.", "Persist last-used indexes and scan beyond known activity only with a bounded range.", "An unused gap can make later addresses invisible."),
        ("Wrong chain/coin type", "Shared curve/address formats do not imply shared derivation or asset state.", "Identify wallet software/version and the actual chain transaction history first.", "Importing into a lookalike chain can expose keys without finding funds."),
    ])
    + table("BIP39 search-space math", ["Known information", "Raw candidates", "Checksum effect", "Operational reading"], [
        ["12 words, one unknown at known position", "2,048", "12-word checksum accepts ~1/16", "~128 valid mnemonics before address check"],
        ["12 words, one unknown position", "12 × 2,048 = 24,576", "Many duplicates/invalid; verify systematically", "Small"],
        ["12 words, two known positions missing", "2,048² = 4,194,304", "Checksum reduces valid mnemonics ~16×", "Benchmark; often tractable"],
        ["12 known words, order unknown", "12! = 479,001,600", "Checksum ~16× pruning", "Large but constrain with remembered positions"],
        ["24 words, one unknown at known position", "2,048", "24-word checksum accepts ~1/256", "~8 valid mnemonics before address check"],
        ["8-char lowercase password", "26⁸ = 208,827,064,576", "No mnemonic checksum", "KDF speed decides; don't assume feasible"],
        ["4 Diceware-like unknown words from 7,776 list", "7,776⁴ ≈ 3.66×10¹⁵", "No helpful checksum", "Infeasible at most wallet KDF rates"],
    ], "BIP39: entropy is 128–256 bits, words index a 2,048-word list, checksum length is ENT/32, and seed derivation uses PBKDF2-HMAC-SHA512 with 2,048 iterations. Checksum pruning is not password security.")
    + table("Format and tool register", ["Format/problem", "Cost function", "Tool class", "Required input", "Gotcha"], [
        ["BIP39 mnemonic/passphrase", "PBKDF2-HMAC-SHA512 × 2,048", "btcrecover / custom offline verifier", "Known address/xpub + constraints", "Every passphrase yields a wallet"],
        ["Bitcoin Core wallet encryption", "Version/wallet dependent", "bitcoin2john + hashcat/John; source-specific", "Copy of wallet file", "Do not benchmark an unknown format guess"],
        ["Ethereum keystore", "scrypt or PBKDF2 parameters embedded in JSON", "hashcat/John modes", "Keystore copy + exact KDF params", "Memory cost limits parallelism"],
        ["Browser-extension vault", "Version-dependent PBKDF2/other KDF", "Format extractor + cracker", "Vault + creating version", "Iteration counts change across versions"],
        ["Wrong HD path", "Derivation + address lookup", "Electrum/descriptor/xpub scanner", "Seed/xpub + known address", "Never upload xpub for sensitive wallet privacy"],
        ["Deleted file", "Storage forensics", "Read-only disk image + carving", "Image, filesystem, time line", "Continued use overwrites evidence"],
    ], "Benchmark your exact extracted hash/KDF on named hardware. The governing equation is candidates ÷ measured guesses/second = seconds; compare cost and time with value at stake.")
    + cards("Device, media & estate cases", [
        ("Dead hardware, known seed", "The seed/descriptor is the wallet; replace the device and verify derived address before moving.", "Restore on a trusted spare, confirm a historical receive address, then migrate to fresh backup material.", "Device brand does not bind funds if the interoperable backup is complete."),
        ("Unknown PIN, no seed", "Retry counters and secure elements can turn experimentation into permanent wipe.", "Stop, photograph model/firmware/condition, and obtain a specialist feasibility opinion before another attempt.", "Online videos for another revision can destroy the only remaining state."),
        ("Damaged backup", "BIP39 wordlist, prefix uniqueness, position and checksum provide reconstruction constraints.", "Transcribe every plausible character/word from high-resolution images of the copy, not the original under repeated handling.", "Cleaning chemicals and heat can erase remaining evidence."),
        ("Estate access", "Legal authority and technical key access are independent requirements.", "Keep a sealed locator/instruction record outside the will; use distributed key arrangements and annual restore drills.", "Publishing a seed in a probate document destroys secrecy."),
    ])
    + cards("Recovery scam red flags", [
        ("Unsolicited contact", "Reply bots and impersonators target public loss reports.", "Independently locate official contact channels; do not continue in direct messages.", "Claimed law-enforcement affiliation is not verification."),
        ("Upfront unlock/tax fee", "A fake platform displays a balance then demands payment to release it.", "Do not pay; preserve messages, wallet addresses, domains and transaction evidence for reporting.", "Additional payment compounds the loss and does not unlock a blockchain transfer."),
        ("Seed validator/sync site", "The tool exfiltrates the only secret required to steal funds.", "Use reviewed open-source tools offline on an isolated system and a copy.", "A professional-looking domain and TLS do not make seed entry safe."),
        ("Guaranteed recovery", "No one can recover a mathematically unconstrained private key.", "Require a written feasibility model: candidate count, measured rate, time, cost and stop condition.", "Confidence without constraints is sales fraud, not forensics."),
        ("Second-wave recovery", "Victim lists are resold; a new actor claims to recover the first loss.", "Assume anyone citing private details may have bought them; verify independently and report.", "Prior victimization increases targeting, not legitimacy."),
    ])
    + checklist("Safe recovery and prevention checklist", [
        "Stop using the only device/media; make verified read-only copies or a forensic image.", "Record wallet software, version, chain, script type, derivation path, known addresses, dates, and observed error.",
        "Scan path/script/account matrix before any cracking attempt.", "Compute candidate count and benchmark the exact KDF on named hardware before renting hardware.",
        "Run tools offline; never disclose seed, passphrase, private key, or unrestricted wallet file.", "Checkpoint long jobs and retain tested/excluded candidate sets.",
        "After recovery, move funds to a fresh wallet whose backup was independently verified.", "Store seed and passphrase in separate failure domains with durable, geographically redundant media.",
        "Record descriptor/path/software metadata alongside—not secret inside—the recovery instructions.", "Perform an annual restore to a spare device and verify a known first address."],
        "The annual restore drill is the only evidence that a backup, passphrase, derivation metadata, and procedure form a real recovery system.")
    + cards("Common mistakes & anti-patterns", [
        ("Only-copy experimentation", "A repair, parser or password attempt can corrupt the remaining evidence.", "Image first; hash source and working copy.", "Recovery cannot be repeated without provenance."),
        ("Cracking before scanning", "The seed may be correct under another path, script, account or passphrase state.", "Run the derivation matrix first.", "Hardware spend cannot fix a wrong model."),
        ("Seed entered online", "The attempt discloses spend authority.", "Use reviewed tools offline and move recovered funds.", "A checker can steal later, not immediately."),
        ("No stop condition", "Search expands indefinitely as memories become guesses.", "Precommit space, budget, benchmark and checkpoint.", "Sunk cost is not new evidence."),
    ])
    + sources([
        ("BIP 39", "https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki", "Mnemonic entropy, checksum, 2,048-word list and PBKDF2 parameters."),
        ("BIP 44", "https://github.com/bitcoin/bips/blob/master/bip-0044.mediawiki", "HD account hierarchy and gap-limit context."),
        ("btcrecover", "https://github.com/3rdIteration/btcrecover", "Open-source local recovery tooling and documentation."),
        ("FBI recovery-scam warning", "https://www.fbi.gov/contact-us/field-offices/elpaso/news/fbi-tech-tuesday-building-a-defense-against-cryptocurrency-recovery-scams", "Upfront-fee and impersonation warning signs."),
        ("FTC scam reporting", "https://reportfraud.ftc.gov/", "US consumer fraud reporting channel."),
    ])
)
PAGES.append({"slug":"wallet-recovery-forensics","title":"Wallet Recovery Forensics: Feasibility, Paths, and Search Math","h1":"Wallet recovery forensics","description":"Triage lost crypto wallets safely: derivation-path diagnosis, BIP39 checksum search spaces, KDF cost math, recovery tools, device/media forensics, scam detection, and prevention.","keywords":"wallet recovery, BIP39 missing word, derivation path, crypto recovery scam, btcrecover","dek":"Recovery is constraint engineering. First prove the wallet is not merely scanning the wrong path; then divide the remaining candidate space by a measured guess rate and accept the answer.","image_alt":"Wallet recovery feasibility matrix with candidate-space and KDF cost math","quick_title":"Feasibility before tools","quick":'<p class="equation">candidate space ÷ measured guesses per second = wall-clock seconds</p><div class="flow"><div><b>1 · PRESERVE</b><p>Work on verified copies; stop destructive retries.</p></div><div><b>2 · IDENTIFY</b><p>Format, wallet version, chain, script, path.</p></div><div><b>3 · SCAN</b><p>Rule out wrong path/account/passphrase state.</p></div><div><b>4 · CONSTRAIN</b><p>Write exact token/mask/position assumptions.</p></div><div><b>5 · BENCHMARK</b><p>Exact KDF on named hardware.</p></div><div><b>6 · STOP</b><p>Reject runs whose cost exceeds rational value.</p></div></div><p class="callout"><strong>No secret, no exploit, no recovery.</strong> Blockchain transparency does not let anyone derive an unconstrained private key.</p>',"sections":recovery_sections,"nav":["Recovery feasibility triage","The wallet is often looking in the wrong place","BIP39 search-space math","Format and tool register","Device, media & estate cases","Recovery scam red flags","Safe recovery and prevention checklist","Common mistakes & anti-patterns"],"related":SHARED_RELATED + [("Bitcoin self-custody", "bitcoin-self-custody-guide.html"),("Bitcoin wallet", "bitcoin-wallet.html"),("Personal cybersecurity", "personal-cybersecurity.html")]})


# 9. Post-quantum custody migration -----------------------------------------
pq_sections = (
    table("Quantum exposure inventory", ["Holding/output type", "What is published at rest", "Exposure moment", "Long-range verdict", "Action now"], [
        ["Bitcoin P2PK", "Raw public key", "Creation", '<span class="signal danger">EXPOSED</span>', "Inventory and plan migration"],
        ["Bitcoin P2PKH, never spent/reused", "Hash of public key", "Spend reveals key", '<span class="signal safe">HASH-SHIELDED</span>', "Do not reuse address"],
        ["Bitcoin P2PKH after spend + reused balance", "Public key in prior input", "First spend", '<span class="signal danger">EXPOSED</span>', "Sweep to fresh non-reused output"],
        ["Bitcoin P2WPKH, never spent/reused", "Witness program hash", "Spend reveals key", '<span class="signal safe">HASH-SHIELDED</span>', "Do not reuse address"],
        ["Bitcoin P2SH/P2WSH unspent", "Script hash", "Spend reveals script/keys", '<span class="signal warn">DEPENDS</span>', "Inspect revealed history and reuse"],
        ["Bitcoin P2TR", "Tweaked Schnorr public key", "Creation", '<span class="signal danger">EXPOSED AT REST</span>', "Include in exposed inventory"],
        ["Proposed P2MR / BIP 360", "Merkle root, no key path", "Script-path spend", '<span class="signal warn">DRAFT</span>', "Track; not deployable consensus today"],
        ["EVM account never sent", "Address hash; key not directly published", "First signature enables recovery", '<span class="signal safe">UNTIL SEND</span>', "Avoid reuse after outbound activity"],
        ["EVM account that sent", "Recoverable signer key from signature", "First outbound transaction", '<span class="signal danger">EXPOSED</span>', "Inventory and migration dependency"],
        ["Ed25519 account after signing", "Public key/signature visible by chain design", "Account/signature use", '<span class="signal danger">EXPOSED</span>', "Chain-specific inventory"],
        ["xpub / wallet descriptor leak", "Public derivation material", "Export/disclosure", '<span class="signal danger">MANY KEYS EXPOSED</span>', "Treat as sensitive; rotate where feasible"],
    ], "Exposure is not present-day compromise. It identifies which assets would offer a future cryptographically relevant quantum computer an unbounded attack window.")
    + table("Primitive impact", ["Primitive", "Role", "Quantum effect", "Operational consequence"], [
        ["ECDSA / secp256k1", "Bitcoin/EVM signatures", "Shor breaks discrete-log assumption", "Exposed public keys become key-recovery targets"],
        ["Schnorr / secp256k1", "Taproot signatures", "Same curve assumption", "Output key is exposed at rest"],
        ["Ed25519 / EdDSA", "Account/chain signatures", "Elliptic-curve discrete log", "Used accounts require chain migration"],
        ["SHA-256", "Hash commitments / PoW", "Grover gives quadratic generic search speedup", "256-bit hash retains large margin; signatures are priority"],
        ["RIPEMD-160 / HASH160", "Bitcoin key hash", "Generic search speedup", "Unspent hash-shielded outputs differ from raw-key outputs"],
        ["Merkle commitments", "Transaction/script/state commitments", "Hash security reduction, not Shor break", "Not the primary signing failure"],
    ], "“Quantum breaks Bitcoin mining” is the wrong operational model. The actionable custody inventory is signature schemes and public-key exposure.")
    + table("Post-quantum signature size register", ["Scheme / parameter", "Public key bytes", "Signature bytes", "Class", "Custody reading"], [
        ["ECDSA secp256k1 baseline", "33 compressed", "~71–73 DER", "Classical", "Compact; quantum-vulnerable"],
        ["Schnorr BIP340 baseline", "32", "64", "Classical", "Compact; quantum-vulnerable"],
        ["ML-DSA-44", "1,312", "2,420", "NIST FIPS 204", "~38× a 64-byte Schnorr signature"],
        ["ML-DSA-65", "1,952", "3,309", "NIST FIPS 204", "Higher category; larger witness"],
        ["ML-DSA-87", "2,592", "4,627", "NIST FIPS 204", "Largest ML-DSA standard set"],
        ["SLH-DSA-SHA2-128s", "32", "7,856", "NIST FIPS 205", "Small key; very large signature"],
        ["SLH-DSA-SHA2-128f", "32", "17,088", "NIST FIPS 205", "Faster family variant; larger signature"],
    ], "Parameters were checked against FIPS 204/205. On-chain cost depends on future serialization and consensus weight rules; multiplying raw bytes by today's witness fee formula would be illustrative, not a deployable quote.")
    + cards("Two attack windows", [
        ("Long-range", "An already published public key can be attacked for months or years without broadcasting anything.", "P2PK, P2TR, reused key-hash outputs, used accounts, and leaked xpubs enter the exposed inventory now.", "Waiting for a mempool anomaly misses the quiet attack window."),
        ("Short-range", "An attacker derives a key after spend broadcast and races a conflicting transaction before confirmation.", "Hash-shielded P2WPKH still needs a chain-level PQ signature path to close this window.", "Moving to a fresh key-hash output only addresses long exposure."),
        ("Present-day hygiene", "Reduce exposed reuse without claiming quantum safety.", "Stop address reuse, protect xpubs/descriptors, and sweep long-held reused balances through ordinary controlled ceremonies.", "A rushed migration can cause a certain operational loss to hedge an uncertain future threat."),
    ])
    + table("Threshold custody migration paths", ["Path", "Address continuity", "Threshold quality", "Chain dependency", "Primary failure"], [
        ["Classical threshold + separate PQ signature", "Contract/script dependent", "Hybrid, asymmetric", "Needs verification rule", "PQ key may reintroduce single point"],
        ["Upgradeable smart-contract/account wallet", "Can remain stable by contract design", "Policy-level multisig possible", "Chain VM + gas + governance", "Upgrade/admin compromise"],
        ["On-chain multisig of PQ keys", "New output/account", "Coarse m-of-n", "PQ opcode/account validation", "Large witness and visible policy"],
        ["Threshold ML-DSA research", "Potentially ordinary PQ signature", "Research / emerging", "Scheme support + mature implementation", "Rejection sampling/MPC complexity"],
        ["Stateful hash-based threshold", "Scheme dependent", "Operationally hazardous", "State tracking", "Backup rollback / one-time-key reuse"],
    ], "As of August 2026, NIST's MPTC program is actively collecting threshold schemes under IR 8214C. That is progress, not proof of mature interoperable custody deployments.")
    + cards("Chain dependency & governance", [
        ("BIP 360 / P2MR", "Draft Pay-to-Merkle-Root removes Taproot's exposed key path and targets long-exposure resistance while retaining script trees.", "Track status and wallet/test-vector work; do not label current holdings P2MR.", "A merged BIP document is not activated consensus."),
        ("BIP 361", "Draft informational migration/sunset framework discusses restricting legacy vulnerable outputs after a future PQ output exists.", "Use it to model governance choices and legacy-coin policy, not a schedule.", "Draft phase names and dates are not network commitments."),
        ("Account abstraction", "A contract/account validation layer can make signature verification upgradeable without changing the user-facing account.", "Inventory upgrade authority, fallback path, validation gas and chain support.", "Upgradability trades cryptographic rigidity for governance risk."),
        ("Legacy exposed coins", "Freeze, rescue/burn, and do-nothing positions allocate theft, property and consensus risk differently.", "Represent the debate in board risk planning; do not assume an outcome.", "Custodians cannot unilaterally choose chain consensus."),
    ])
    + table("Migration register", ["When", "Control", "Owner", "Evidence", "Blocked by"], [
        ["Now", "Inventory chain, scheme, output/account type, exposure, value and horizon", "Custody engineering", "Versioned cryptographic asset register", "Nothing"],
        ["Now", "Ban address reuse and protect xpub/descriptor exports", "Wallet platform", "Policy test + monitoring", "Nothing"],
        ["Now", "Sweep reused/exposed long-held outputs where ordinary risk permits", "Custody operations", "Approved migration/reconciliation", "Fees and operational risk"],
        ["Now", "Record software, path, scheme, signer, export and recovery metadata", "Platform + DR", "Restore-tested inventory", "Vendor access may limit"],
        ["Now", "Ask vendor for PQ roadmap and independent export/re-key path", "Risk/procurement", "Written response + exit test", "Vendor capability"],
        ["Next", "Make signature scheme and serialization explicit in internal interfaces", "Architecture", "Multi-scheme test harness", "Legacy assumptions"],
        ["Next", "Model byte/fee/capacity impact and migration batching", "Chain operations", "Scenario workbook", "Final chain rules unknown"],
        ["Next", "Monitor NIST MPTC and chain proposals by status", "Cryptography owner", "Quarterly review", "Standards/governance"],
        ["Later", "Deploy PQ or hybrid signing", "Chain + custodian", "Activated standard path + audited implementation", "Consensus and mature threshold support"],
    ], "Planning inequality: required secrecy lifetime + migration duration > uncertain time to capability means inventory and agility work starts now—even when scheme replacement is blocked.")
    + checklist("Common mistakes & anti-patterns", [
        "Do not claim 256-bit hash functions and proof-of-work fail the same way as elliptic-curve signatures.", "Do not classify every address equally; inspect output/account type and spend/reuse history.",
        "Do not treat a hardware wallet as a post-quantum control; it still emits the chain's signature scheme.", "Do not classify Taproot like an unspent P2WPKH output; P2TR publishes a key at creation.",
        "Do not assume an ECDSA threshold engine can swap in ML-DSA without a new protocol and chain rule.", "Do not plan migration the chain cannot validate or wallets cannot receive.",
        "Do not ignore public-key/signature bytes, block capacity, fee market, and consolidation scale.", "Do not buy unverifiable “quantum-safe” branding or deploy an unstandardized scheme into production custody.",
        "Do not put prediction-year precision into policy; use horizon + migration-duration scenarios.", "Do not create present operational loss through rushed sweeps; use ordinary custody controls and reconciliation."],
        "Calm inventory work is useful under every forecast. Panic procurement is useful under none.")
    + table("Timelines stated honestly", ["Timeline", "What is factual", "What remains uncertain", "Planning use"], [
        ["NIST transition", "IR 8547 initial public draft describes federal transition planning", "Draft may change; application guidance differs", "Track status and agency-specific mandates"],
        ["NIST standards", "FIPS 204/205 final since August 2024", "Blockchain consensus and threshold profiles", "Use parameters for size/testing, not deployment claims"],
        ["NIST threshold work", "IR 8214C final January 2026; submissions/workshops active", "Mature audited custody interoperability", "Review annually; prototype off production path"],
        ["Bitcoin proposals", "BIPs 360/361 are Draft as of August 2026", "Activation, signature choice, sunset policy, schedule", "Inventory dependencies; promise no date"],
        ["CRQC capability", "No public machine breaks production ECC today", "Whether/when capability exists", "Use scenario ranges, not a forecast year"],
    ], "Decision inequality: required security lifetime + credible migration duration versus an uncertain capability horizon. Uncertainty motivates reversible inventory work, not false precision.")
    + sources([
        ("NIST FIPS 204 — ML-DSA", "https://csrc.nist.gov/pubs/fips/204/final", "Standard parameter sets and byte encodings."),
        ("NIST FIPS 205 — SLH-DSA", "https://csrc.nist.gov/pubs/fips/205/final", "Stateless hash-based signature standard."),
        ("NIST IR 8547 draft", "https://csrc.nist.gov/pubs/ir/8547/ipd", "Federal transition planning; draft status is explicit."),
        ("NIST MPTC", "https://csrc.nist.gov/Projects/threshold-cryptography", "IR 8214C and current threshold-standardization program."),
        ("BIP 360 — P2MR", "https://github.com/bitcoin/bips/blob/master/bip-0360.mediawiki", "Draft long-exposure-resistant script-tree output."),
        ("BIP 361 — migration/sunset", "https://github.com/bitcoin/bips/blob/master/bip-0361.mediawiki", "Draft informational legacy-signature migration framework."),
    ])
)
PAGES.append({"slug":"post-quantum-custody-migration","title":"Post-Quantum Custody Migration: What Actually Breaks","h1":"Post-quantum migration for digital asset custody","description":"Classify quantum-exposed holdings, compare post-quantum signature sizes, understand threshold-custody barriers, track Bitcoin BIPs 360/361, and sequence migration work.","keywords":"post quantum crypto custody, Bitcoin quantum risk, BIP 360, BIP 361, ML-DSA blockchain, quantum exposed public key","dek":"Signatures break before hashes do. The useful work now is an exposure inventory, address hygiene, exportable metadata, and crypto-agile interfaces—not a confident prediction of “Q-day.”","image_alt":"Post-quantum custody exposure inventory by Bitcoin output and account type","quick_title":"Signatures break; hashes do not","quick":table("Primitive triage",["Question","If yes","Verdict"],[
    ["Is an elliptic-curve public key already visible?", "Long-range key-recovery target under a future CRQC", '<span class="signal danger">INVENTORY NOW</span>'],
    ["Is only a hash of the key/script visible and unused?", "Long exposure is reduced until spend reveals it", '<span class="signal safe">NO REUSE</span>'],
    ["Does the chain validate a standardized PQ signature today?", "Only then can a true scheme migration execute", '<span class="signal warn">CHAIN DEPENDENT</span>'],
    ["Does the custody quorum have a mature audited PQ threshold protocol?", "Only then can threshold semantics survive directly", '<span class="signal warn">EMERGING</span>'],
    ["Can keys, paths and policy be exported/re-keyed without the vendor?", "Migration remains operationally possible", '<span class="signal safe">TEST EXIT</span>'],
  ],"Exposure is a property of published keys and spend history. Capability timing is uncertain; inventory and hygiene are not."),"sections":pq_sections,"nav":["Quantum exposure inventory","Primitive impact","Post-quantum signature size register","Two attack windows","Threshold custody migration paths","Chain dependency & governance","Migration register","Timelines stated honestly","Common mistakes & anti-patterns"],"related":SHARED_RELATED + [("Post-quantum cryptography", "post-quantum-cryptography.html"),("Quantum physics vs hype", "quantum-physics-vs-quantum-bullshit.html"),("Bitcoin self-custody", "bitcoin-self-custody-guide.html")]})


def main() -> None:
    for page in PAGES:
        target = ROOT / f"{page['slug']}.html"
        target.write_text(render(page), encoding="utf-8")
        print(target.name)


if __name__ == "__main__":
    main()
