# -*- coding: utf-8 -*-
"""Insert a beginner 'Start here' primer into the 9 Crypto Custody & Compliance sheets.

Adds, per file:
  1. .primer / .pq / .primer-line CSS into @layer components (after the .callout rule)
  2. abbr.term CSS where the sheet does not already carry it
  3. a #start-here section immediately after <main id="main" class="shell">
  4. a 'Start here' link as the first item in the section nav
  5. .pq to the print break-inside:avoid list

Idempotent: re-running detects the existing block and rewrites it in place.
"""
import re
import sys
import pathlib

ROOT = pathlib.Path(r"C:\Users\veksl\Projects\CheatSheets")

PRIMERS = {
"mpc-wallet-architecture": {
 "lead": "A normal wallet has one private key, and whoever holds it can move the money. An MPC wallet never creates that key. Each participating machine generates a share, and signing is a short conversation between enough of those machines to meet a threshold. The chain receives one ordinary signature and cannot tell the difference.",
 "qs": [
  ("How is this different from multisig?",
   "Multisig puts several real keys on chain and the chain enforces the rule, so anyone can see which keys approved. MPC does the same job off chain and hands the chain a single ordinary signature. That is why MPC works on chains with no multisig support, and also why the chain records nothing about who signed."),
  ("If nobody holds a key, what can still go wrong?",
   "Threshold signing protects the key material, not the decision to sign. An attacker who takes over the system that requests signatures gets a valid signature from a perfectly healthy quorum. Every share behaved correctly, and the money is still gone."),
  ("Why does share refresh keep coming up?",
   "Refresh re-randomizes every share while the address stays the same, which makes all older shares useless. The realistic attack is not compromising three machines in one night, it is compromising one this quarter and another next year. Refresh puts a deadline on that."),
  ("How do you back up a key that does not exist?",
   "Carefully, because this is where the scheme quietly collapses back into single-key custody. If you can bring enough shares together in one place to restore, you have rebuilt the single key you were trying to avoid."),
 ],
 "line": "MPC protects the key. It does not protect the decision to sign. Spend your review time on the policy engine."
},

"blockchain-deposits-withdrawals": {
 "lead": "This sheet covers the two moments a business actually touches a blockchain: money arriving, and money leaving. Both are conversations with a system you do not control and cannot roll back, and every rule below follows from that.",
 "qs": [
  ("How many confirmations before I credit a deposit?",
   "There is no universal number, and six is a convention rather than a derivation. The real question is what an attacker would have to spend to reverse a block against what you just credited. A chain with a small security budget needs more confirmations than Bitcoin, not fewer because its blocks are fast."),
  ("Why do ten workers jam on one hot wallet?",
   "Account-model nonces are strictly sequential per address, so two workers that read the same next value both submit and one of them loses. You need a single writer handing out nonces, and you get throughput by sharding across several hot addresses rather than by parallelising one."),
  ("Why does sweeping a USDT deposit need ETH?",
   "Moving a token out of a deposit address is a transaction sent from that address, and it needs the chain's native coin for gas. Nobody sends you ETH when they send you USDT, so every token sweep is a funding problem with a transfer attached."),
  ("Can I guarantee a withdrawal sends exactly once?",
   "No. Exactly-once does not exist against a system you cannot transact with atomically. What you build instead is at-least-once delivery, an idempotency key so a retry returns the original transaction, and a reconciler that keeps comparing your ledger against the chain."),
 ],
 "line": "Record the intent before you sign it. A signed transaction your system has no record of is the worst state in the pipeline."
},

"crypto-exchange-architecture": {
 "lead": "An exchange looks like a blockchain product and is mostly a bookkeeping product. Most transactions never touch a chain at all: a trade between two customers is a pair of ledger entries, instant and free and final. The chain only appears at the edges.",
 "qs": [
  ("Where does the trading system end and the wallet system begin?",
   "At the ledger. The matching engine never talks to a chain, and the wallet system never talks to the order book. Only four things cross that boundary: deposits, withdrawals, sweeps, and rebalances."),
  ("Why is the internal ledger the system of record?",
   "Because you cannot rebuild it from chain state. Trades, fees, and internal transfers leave no on-chain trace, so a chain scan can tell you what you hold but never what you owe."),
  ("Why integers and never floating point?",
   "Token precision differs per asset: USDT is six decimals, most ERC-20s are eighteen. Floats drop the low digits silently, so balances are held as integer minor units with the per-asset precision recorded alongside them."),
  ("What does proof of reserves actually prove?",
   "That you controlled certain assets at one moment. Assets are the easy half. Liabilities are the hard half, and a naive customer-balance tree still allows omitted accounts and negative balances. It is not proof of solvency."),
 ],
 "line": "The ledger is the system of record. The chain is an external effect you reconcile against it."
},

"custody-provider-integration": {
 "lead": "A custody platform sells you signing, key storage, and chain coverage. It does not sell you a wallet system. This sheet is about the seam between their API and your ledger, which is where the integration bugs live.",
 "qs": [
  ("What does buying a custody platform actually remove?",
   "Threshold-signing implementation and its audit burden, HSM and enclave operations, and the pace of adding new chains. It removes approximately none of the ledger, deposit detection, reconciliation, nonce management, compliance placement, or the withdrawal pipeline."),
  ("What do integrators get wrong first?",
   "Trusting webhooks. They arrive at least once, out of order, and sometimes not at all. Treat a webhook as a hint that something changed, and let a polling reconciler be the thing that decides what is true."),
  ("Why does every page insist on an idempotency key?",
   "A create call that times out has an unknown outcome. It may already have been accepted. Without a key on the request, your retry is a second withdrawal."),
  ("What is a co-signer callback for?",
   "It is the one place your own code sits inside the signing path. It lets you check that the transaction being signed matches the intent your ledger recorded, which is the only real defence against a compromised caller holding valid credentials."),
 ],
 "line": "The webhook is a hint. The reconciler is the source of truth."
},

"crypto-compliance-architecture": {
 "lead": "Most compliance failures are not missing policies. They are gates placed at the wrong point in the call graph, where they can observe a problem but no longer stop it. This sheet is about placement.",
 "qs": [
  ("Where does sanctions screening belong?",
   "Before signing, never after broadcast. Screening a transaction you have already sent is not a control, it is a report, because the only action left is a filing."),
  ("What is the Travel Rule in one paragraph?",
   "It is the requirement that identifying information about the sender and the recipient travels alongside a transfer between regulated firms, above a threshold. IVMS101 is the shared data format that information is carried in."),
  ("If the format is standard, why is it hard?",
   "The payload is standardised and the network is not. The competing Travel Rule networks all carry IVMS101 but discover and authenticate counterparties differently, so you either join several of them or route through a broker."),
  ("Why rescreen addresses you already cleared?",
   "Sanctions lists move in both directions. An address that is clean today can be designated tomorrow, and the exposure applies to what you already did, so screening only at onboarding leaves a gap that grows every day."),
 ],
 "line": "Compliance controls are pipeline placement decisions, not a checklist. Screen before irreversibility."
},

"institutional-crypto-custody": {
 "lead": "Custody is not one vault. It is a set of tiers holding different balances at different speeds, wrapped in a control system: who may approve what, how the keys were created, who can change the rules, and what happens when a facility or a vendor disappears.",
 "qs": [
  ("How much should sit in the hot wallet?",
   "It is an inventory problem, not a security instinct. Model withdrawal demand over the time it takes to replenish from cold, then size the float against the tail of that distribution. Expected loss from a hot compromise scales with the balance, while delayed withdrawals and the cost of each cold retrieval push the other way."),
  ("What is a policy engine, and why is it the real control?",
   "It is the ordered rule set deciding which transactions are allowed and how many approvals each needs. Rules evaluate first-match, so an over-broad rule high in the list silently shadows everything below it, and a missing terminal default-deny rule turns the whole thing into a suggestion engine."),
  ("What actually happens in a key ceremony?",
   "Named roles, an offline room, verified devices, recorded video, and an independent witness who holds no key. The step people skip is verifying the address from the backup material and running a test recovery before any real funds arrive."),
  ("What is CCSS?",
   "The CryptoCurrency Security Standard: the crypto-specific control standard with a public levelled structure covering key generation, storage, usage, compromise policy, and audit logs. The crosswalk further down maps each requirement to an architectural decision."),
 ],
 "line": "A control the system does not enforce is not a control. If an administrator can quietly edit the policy, the policy is decorative."
},

"stablecoin-payment-infrastructure": {
 "lead": "A stablecoin payment depends on four systems running on different clocks: an issuer, a token contract, a chain or bridge, and a bank. Treating it as a single payment is how integrations break, because any one of the four can fail without the others noticing.",
 "qs": [
  ("Is a stablecoin just a dollar on a blockchain?",
   "Only as far as the issuer's balance sheet and redemption terms go. What you hold is a token whose contract has an owner, whose value depends on reserves you cannot inspect directly, and whose redemption runs on banking hours rather than block times."),
  ("The transfer is final. Why can it still fail?",
   "Chain finality and issuer control are independent axes. A finalized transfer can still sit in a frozen address, wait on a bridge attestation, or land on a contract that resembles the asset you wanted and is not it."),
  ("Why does native versus bridged matter so much?",
   "They are different tokens carrying different risk. Native is issued on that chain by the issuer. Bridged is a claim minted by a bridge against a balance locked elsewhere, so it inherits the bridge's failure modes and may not be redeemable at par."),
  ("What breaks first during a depeg?",
   "Not the chain. Redemption queues, banking cutoffs, and pricing sources are where a depeg turns into an operational incident, which is why the treasury controls on this page sit next to the contract details."),
 ],
 "line": "Settled on chain and redeemable at par are two separate guarantees. Never let one stand in for the other."
},

"post-quantum-custody-migration": {
 "lead": "Quantum risk in custody is a signature problem, not an encryption problem. A sufficiently large quantum computer would recover a private key from a published elliptic-curve public key, and that is what nearly every chain uses to authorize spending. Hash functions are far less affected.",
 "qs": [
  ("Is my Bitcoin at risk today?",
   "No existing machine is close, and the honest answer about timing is that nobody has a date. What is knowable today is exposure: which of your outputs have already published an elliptic-curve public key, because those are the ones a future machine would target."),
  ("Why does address reuse matter so much here?",
   "An unspent output that shows only a hash of the key is not yet a target. Spending reveals the public key, and that transition only runs one way. Not reusing addresses is the one control fully available right now."),
  ("If post-quantum signatures exist, why not switch now?",
   "Because a chain has to validate them first. The standardised schemes are also one to two orders of magnitude larger than the 64 to 72 bytes chains budget for today, which changes fees, block space, and every place a signature is stored."),
  ("What should we actually do this year?",
   "Build the exposure inventory, fix reuse policy, confirm keys and derivation paths can be exported without the vendor, and keep the signature scheme behind an interface. That work pays off whatever the timeline turns out to be."),
 ],
 "line": "Inventory and hygiene are available today. A confident Q-day prediction is not."
},

"wallet-recovery-forensics": {
 "lead": "Most lost wallets are not cryptographically lost. They are looking in the wrong place, or missing a piece the owner still half-remembers. This sheet is about working out which case you are in before spending money on cracking.",
 "qs": [
  ("My wallet shows a zero balance. Is the money gone?",
   "Usually not. A wallet derives its addresses from a path, and a different wallet or a different account setting derives different addresses from the same seed. Ruling out a wrong derivation path resolves a large share of cases before any cracking starts."),
  ("I forgot part of my seed phrase. Can it be brute forced?",
   "It depends entirely on how much you still know, and the range spans about twelve orders of magnitude. One missing word in a known position is a couple of thousand candidates. A forgotten passphrase of four random words is beyond any hardware. To the person asking, both feel like the same problem."),
  ("How do I know whether it is feasible at all?",
   "Arithmetic. Constrain the candidate space with everything you remember, benchmark real guesses per second on named hardware, and divide. If the answer is longer than a human lifetime, that is the answer, and no tool changes it."),
  ("Someone guarantees recovery for a fee. Is that real?",
   "No. Nobody can guarantee an outcome that depends on a search space they have not measured. Upfront fees, guarantees, and any request to send the wallet file or the seed phrase are the standard shape of the scam."),
 ],
 "line": "Do the feasibility arithmetic first. Preserve a verified copy of the media before anything is allowed to touch it."
},
}

PRIMER_CSS = """
  /* Beginner on-ramp: plain-English framing above the dense reference. */
  .primer{margin-top:1.6rem;background:var(--surface-2);border:1px solid var(--line);
    border-left:5px solid var(--accent);padding:1.1rem 1.2rem;scroll-margin-top:6rem}
  .primer h2{font-size:clamp(1.15rem,2.6vw,1.5rem)}
  .primer-lead{color:var(--muted);max-width:78ch;margin:.5rem 0 1rem;font-size:.95rem}
  .primer-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,250px),1fr));gap:.65rem}
  .pq{background:var(--surface);border:1px solid var(--line);padding:.75rem .85rem}
  .pq h3{font-family:var(--display);font-size:.94rem;font-weight:600;letter-spacing:-.01em;margin:0 0 .3rem}
  .pq p{margin:0;font-size:.88rem;line-height:1.55}
  .primer-line{margin:1rem 0 0;padding-top:.8rem;border-top:1px solid var(--line);font-size:.95rem}
  .primer-line b{display:block;font:600 .66rem/1.3 var(--mono);letter-spacing:.08em;
    text-transform:uppercase;color:var(--accent);margin-bottom:.25rem}"""

ABBR_CSS = "\n  abbr.term{text-decoration:none;border-bottom:1px dotted var(--accent);cursor:help}"

MARK_OPEN = "<!--START-HERE-->"
MARK_CLOSE = "<!--/START-HERE-->"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build_section(d):
    cards = "".join(
        '<div class="pq" data-f><h3>%s</h3><p>%s</p></div>' % (esc(q), esc(a))
        for q, a in d["qs"]
    )
    return (
        MARK_OPEN
        + '<section class="sheet-section primer" id="start-here" aria-labelledby="start-here-title">'
        + '<h2 id="start-here-title">Start here if this is new</h2>'
        + '<p class="primer-lead">%s</p>' % esc(d["lead"])
        + '<div class="primer-grid">%s</div>' % cards
        + '<p class="primer-line"><b>If you remember one line</b>%s</p>' % esc(d["line"])
        + "</section>"
        + MARK_CLOSE
    )


def process(slug, d):
    path = ROOT / (slug + ".html")
    src = path.read_text(encoding="utf-8")
    orig = src

    # 1 + 2. CSS, anchored on the .callout rule inside @layer components.
    if ".primer{" not in src:
        m = re.search(r"^(  \.callout\{[^\n]*\n)", src, re.M)
        if not m:
            raise SystemExit("%s: no .callout anchor" % slug)
        block = PRIMER_CSS
        if "abbr.term{" not in src:
            block += ABBR_CSS
        src = src[: m.end(1)] + block.lstrip("\n") + "\n" + src[m.end(1) :]

    # 5. Print: keep a card intact across page breaks.
    src = src.replace(
        ".entry,.checklist li,figure.plate,details.drawer{break-inside:avoid}",
        ".entry,.pq,.checklist li,figure.plate,details.drawer{break-inside:avoid}",
    )

    # 3. The section itself, right after <main>.
    section = build_section(d)
    if MARK_OPEN in src:
        src = re.sub(
            re.escape(MARK_OPEN) + ".*?" + re.escape(MARK_CLOSE), lambda _: section, src, flags=re.S
        )
    else:
        anchor = '<main id="main" class="shell">'
        if anchor not in src:
            raise SystemExit("%s: no <main> anchor" % slug)
        src = src.replace(anchor, anchor + "\n" + section, 1)

    # 4. Nav link, first position.
    if '#start-here"' not in src.split("<main")[0]:
        nm = re.search(r'(<nav class="sections"[^>]*><div class="shell">)', src)
        if not nm:
            raise SystemExit("%s: no nav anchor" % slug)
        src = src[: nm.end(1)] + '<a href="#start-here">Start here</a>' + src[nm.end(1) :]

    if src != orig:
        path.write_text(src, encoding="utf-8")
        return True
    return False


if __name__ == "__main__":
    for slug, d in PRIMERS.items():
        blob = repr(d)
        for bad in ("\u2014", "\u2013"):
            assert bad not in blob, "%s contains a dash character" % slug
        changed = process(slug, d)
        print(("updated " if changed else "no-change ") + slug)
