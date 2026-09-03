# -*- coding: utf-8 -*-
"""Wrap first-use jargon in <abbr class="term" title="..."> across the custody cluster.

Only touches visible text inside <main>...</main>, never markup, attributes,
or text already inside an <abbr>. First occurrence only, per term.
"""
import re
import pathlib

ROOT = pathlib.Path(r"C:\Users\veksl\Projects\CheatSheets")

TERMS = {
"blockchain-deposits-withdrawals": [
 ("reorg", "Reorganization: the chain discards blocks it previously accepted and replaces them with a different branch, so a transaction you already saw can become unconfirmed again."),
 ("nonce", "A per-address counter on account-model chains. Transactions from one address must be mined in strict nonce order, so a missing nonce stalls every later transaction from that address."),
 ("mempool", "The set of valid transactions a node has seen but that are not yet in a block. Each node keeps its own, so mempool contents differ between providers."),
 ("UTXO", "Unspent Transaction Output: on Bitcoin-style chains a balance is not a number, it is a set of discrete unspent outputs, and spending means selecting and consuming whole outputs."),
 ("finality", "The point at which reversing a transaction stops being economically or cryptographically feasible. It is defined per chain, and some chains only ever offer a probability."),
 ("RBF", "Replace-By-Fee: rebroadcasting a stuck transaction with the same inputs and a higher fee so miners prefer the replacement."),
 ("CPFP", "Child Pays For Parent: unsticking a low-fee transaction by spending its output in a new high-fee transaction, so miners must include both to collect the fee."),
 ("dust", "An output too small to be worth the fee required to spend it. Dust accumulates in deposit systems and can make a balance unspendable in practice."),
 ("idempotency", "A property where repeating the same request produces the same single effect. It is how a retry after a timeout avoids becoming a second withdrawal."),
 ("epoch", "On Ethereum, a fixed span of 32 slots used for attestation and finality accounting. Finalization takes roughly two epochs."),
],

"custody-provider-integration": [
 ("webhook", "An HTTP callback the provider sends when something changes on their side. Delivery is at least once, unordered, and not guaranteed, so a webhook is a hint rather than a fact."),
 ("idempotency key", "A caller-supplied identifier attached to a create request. The provider returns the original result instead of creating a second transaction when the same key arrives again."),
 ("co-signer", "A signing participant you host yourself. Because it sits inside the signing path, it is the one place your own code can check the transaction against the intent your ledger recorded."),
 ("HMAC", "Hash-based Message Authentication Code: a keyed signature over the raw request body used to prove a webhook really came from the provider. Verify before parsing, never after."),
 ("vault", "A provider-side container grouping addresses and balances under one policy scope. Vault structure is what your policy rules are written against, so it is hard to change later."),
 ("sub-status", "The provider's secondary failure field. The status says a transaction failed; the sub-status says why, which is the difference between an actionable alert and a shrug."),
 ("exponential backoff", "Retrying a failed call after progressively longer waits, so a struggling provider is not hit by a retry storm from every client at once."),
 ("gas station", "Automated funding that tops up an address with the chain's native coin so a token sweep can pay its own gas. It is a float, and it needs monitoring like any other float."),
 ("reconciler", "A process that repeatedly compares your ledger against provider and chain state and reports every difference. It is the correctness mechanism, not a cleanup job."),
],

"crypto-compliance-architecture": [
 ("VASP", "Virtual Asset Service Provider: FATF's term for a regulated firm that holds, exchanges, or transfers crypto on behalf of others. Travel Rule obligations attach to transfers between VASPs."),
 ("FATF", "Financial Action Task Force: the intergovernmental body whose recommendations national regulators implement. It writes no binding law itself; each jurisdiction transposes it differently."),
 ("IVMS101", "InterVASP Messaging Standard 101: the shared data model for the originator and beneficiary information carried alongside a Travel Rule transfer."),
 ("KYT", "Know Your Transaction: continuously screening on-chain activity for links to sanctioned, stolen, or high-risk addresses, as distinct from verifying the customer's identity once at onboarding."),
 ("sunrise", "The sunrise problem: a counterparty in a jurisdiction that has not yet implemented the Travel Rule cannot receive the payload, so you need a documented policy for transfers it affects."),
 ("unhosted", "A wallet the counterparty controls directly, with no regulated firm on the other end. There is nobody to exchange Travel Rule data with, so the requirement becomes a proof-of-control question."),
 ("de minimis", "A threshold below which an obligation does not apply. Travel Rule thresholds differ by jurisdiction and some regimes set none at all for crypto transfers."),
 ("OFAC", "The US Treasury's Office of Foreign Assets Control, which publishes the sanctions list most screening providers key against. Designations are added and removed, so a list is an input, never a constant in code."),
],

"institutional-crypto-custody": [
 ("HSM", "Hardware Security Module: a tamper-resistant device that performs signing operations internally so key material never appears in ordinary server memory."),
 ("quorum", "The minimum number of approvers or signers required for an action. It sets both the collusion floor and the availability floor, which is why raising it is never purely a security win."),
 ("dual control", "A rule that no single person can complete a sensitive action alone. It is a procedural control, so it is only real if the system enforces it rather than the policy document asserting it."),
 ("air-gapped", "Physically isolated from any network. Moving a transaction in or out requires a deliberate manual step, which is the point."),
 ("break-glass", "A pre-authorized emergency path that bypasses normal controls. It needs its own dual control and its own alarm, or it becomes the easiest way in."),
 ("CCSS", "CryptoCurrency Security Standard: the crypto-specific control standard with a public levelled structure covering key generation, storage, usage, compromise policy, and audit logs."),
 ("SOC 2", "An attestation report on a service organization's controls. It says an auditor tested the controls the organization defined, which is not the same as those controls being adequate for custody."),
 ("time lock", "A mandatory waiting period before a change takes effect. On whitelist additions it is the highest-value single control: an attacker with full API access still waits in public view."),
 ("key ceremony", "The scripted, witnessed procedure for generating and backing up keys. Its load-bearing step is verifying the address from the backup material and doing a test recovery before real funds arrive."),
],

"stablecoin-payment-infrastructure": [
 ("depeg", "The token trading away from its reference value. The chain keeps working, so a depeg shows up first in redemption queues, pricing sources, and banking cutoffs."),
 ("attestation", "A signed statement from an off-chain party that something happened, used by bridges to authorize a mint on the destination chain. Until it lands, the value is in flight and not spendable."),
 ("CCTP", "Cross-Chain Transfer Protocol: Circle's burn-and-mint route for moving native USDC between chains, so the token on the destination chain is issued rather than wrapped."),
 ("bridged", "A token minted by a bridge against a balance locked on another chain. It carries the bridge's failure modes and may not be redeemable at par with the issuer."),
 ("native", "Issued directly on that chain by the issuer, redeemable through the issuer. Native and bridged versions of the same ticker are different assets with different risk."),
 ("blacklist", "An issuer-controlled list of addresses whose balances cannot move. It is why a final on-chain transfer can still leave funds unusable."),
 ("at par", "Exchangeable one-for-one with the reference asset by the issuer. Trading near the peg on an exchange is not the same guarantee."),
 ("reserve", "The assets the issuer holds against outstanding tokens. What matters operationally is the composition, the reporting cutoff, and who can actually redeem, not the headline total."),
],

"post-quantum-custody-migration": [
 ("CRQC", "Cryptographically Relevant Quantum Computer: a machine large and stable enough to break deployed public-key cryptography. None exists, and no credible date for one exists either."),
 ("Shor", "Shor's algorithm: the quantum algorithm that would recover a private key from a published elliptic-curve public key. It is the reason custody's quantum risk is a signature problem."),
 ("Grover", "Grover's algorithm: gives a quadratic speedup against hash and symmetric primitives, which is why hashes are weakened rather than broken and doubling output length answers it."),
 ("xpub", "Extended public key: exporting one reveals every public key derivable beneath it, which turns a convenience feature into an exposure decision under a quantum threat model."),
 ("ML-DSA", "Module-Lattice Digital Signature Algorithm, standardised in NIST FIPS 204. Its signatures are far larger than the 64 to 72 bytes chains budget for today."),
 ("SLH-DSA", "Stateless Hash-based Digital Signature Algorithm, standardised in NIST FIPS 205. It rests only on hash security, at the cost of very large signatures."),
 ("crypto-agility", "Designing so the signature scheme can be swapped without rewriting everything around it. It is the part of migration you can build before any chain supports a new scheme."),
 ("address reuse", "Spending from, or receiving again at, an address whose public key is already published. It is the exposure decision fully under your control today."),
],

"wallet-recovery-forensics": [
 ("BIP39", "The standard that turns wallet entropy into a word list from a fixed 2,048-word vocabulary, with a checksum built in. It is why a mistyped word is usually detectable."),
 ("derivation path", "The index route a wallet walks to turn one seed into many addresses. Two wallets using different paths show different balances from the identical seed, which explains most apparently empty wallets."),
 ("passphrase", "An optional extra secret added to a seed phrase, sometimes called the 25th word. It creates an entirely separate wallet, and forgetting it is usually the difference between feasible and impossible."),
 ("KDF", "Key Derivation Function: the deliberately slow computation between a password and a key. Its cost per guess is the number that decides whether a search is feasible."),
 ("checksum", "Redundant bits that let a wallet detect a wrong word or a typo. A phrase that fails its checksum is invalid, which narrows a search rather than widening it."),
 ("keystore", "An encrypted JSON file holding one private key, protected by a password. Recovery is a password search, not a seed search, and the KDF parameters are in the file."),
 ("entropy", "The raw randomness a wallet was created from, measured in bits. It sets the size of the search space, and no amount of computing power shrinks it."),
 ("brain wallet", "A key derived from a memorised phrase. Anything memorable has been guessed already, so these are treated as compromised rather than recoverable."),
],

"mpc-wallet-architecture": [
 ("policy engine", "The rule set deciding which transactions are allowed and how many approvals each needs. It sits outside the threshold boundary, which is why compromising it defeats a healthy quorum."),
],

"crypto-exchange-architecture": [
 ("double-entry", "Bookkeeping where every movement is recorded as equal and opposite entries, so the books can be proved to balance rather than assumed to."),
 ("minor units", "Integer amounts in an asset's smallest unit, stored with that asset's decimal precision. Floating point drops the low digits silently, so balances never use it."),
 ("sweep", "Moving funds from many deposit addresses into a pooled wallet. It changes where money sits without changing what you owe, so booking it as anything else corrupts the ledger."),
],
}

TAG = re.compile(r"<[^>]*>")


def eligible_spans(body):
    """Yield (start, end) offsets of body text that may be wrapped.

    Excludes markup itself, plus anything inside an <abbr> (already glossed),
    an <svg> (abbr is not valid SVG content), an <a> (a tooltip fights the
    link), or the Start-here primer (deliberately plain English, so the first
    body use is the one that needs glossing).
    """
    spans, depth, last = [], 0, 0
    for m in TAG.finditer(body):
        if depth == 0 and m.start() > last:
            spans.append((last, m.start()))
        low = m.group(0).lower()
        if low.startswith("<!--start-here"):
            depth += 1
        elif low.startswith("<!--/start-here"):
            depth = max(0, depth - 1)
        else:
            for name in ("abbr", "svg", "a"):
                if low.startswith("<" + name + ">") or low.startswith("<" + name + " "):
                    depth += 1
                    break
                if low.startswith("</" + name + ">"):
                    depth = max(0, depth - 1)
                    break
        last = m.end()
    if depth == 0 and last < len(body):
        spans.append((last, len(body)))
    return spans


def wrap(path, terms):
    src = path.read_text(encoding="utf-8")
    i = src.index('<main id="main"')
    j = src.index("</main>")
    head, body, tail = src[:i], src[i:j], src[j:]

    applied = []
    for term, title in terms:
        esc_title = title.replace('"', "&quot;")
        # Idempotent: a term already glossed on this page is left alone, so a
        # re-run never plants a second tooltip on the next occurrence.
        if 'title="%s"' % esc_title in body:
            applied.append(term)
            continue
        pat = re.compile(r"(?<![\w-])" + re.escape(term) + r"(?![\w-])", re.I)
        # Re-tokenize each pass so a term can never match inside a title
        # attribute an earlier term just inserted.
        for a, b in eligible_spans(body):
            m = pat.search(body, a, b)
            if not m:
                continue
            rep = '<abbr class="term" title="%s">%s</abbr>' % (esc_title, m.group(0))
            body = body[: m.start()] + rep + body[m.end() :]
            applied.append(term)
            break

    out = head + body + tail
    if out != src:
        path.write_text(out, encoding="utf-8")
    missing = [t for t, _ in terms if t not in applied]
    return applied, missing


if __name__ == "__main__":
    for slug, terms in TERMS.items():
        applied, missing = wrap(ROOT / (slug + ".html"), terms)
        print("%-38s +%d%s" % (slug, len(applied), ("  MISSING: " + ", ".join(missing)) if missing else ""))
