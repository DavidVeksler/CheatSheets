# Spec: Wallet recovery forensics — how keys are lost and how they are recovered

**Target file:** `wallet-recovery-forensics.html`
**Batch:** [custody-engineering-batch-2026-08.md](custody-engineering-batch-2026-08.md) (sheet 8 of 9, P2).
**Read the batch file's public-repo constraints before writing.** This is the one sheet with a real
confidentiality surface, and the rules there are binding: no client, case or engagement detail;
every example a composite or a publicly-reported incident with a citation.

## Why this topic

The rest of the batch describes how keys are held. This one reads the same subject backwards —
through how they are lost — and it is the sheet nobody else in the field can write, because
writing it credibly requires having actually done recoveries.

The public literature is in bad shape in a specific way. Recovery content splits into tool READMEs
(here is how to run this script), forum threads (my exact situation, one anecdote), and **scam
sites** — which are the majority of what a desperate person finds, because "bitcoin recovery
service" is one of the most aggressively targeted phrases on the internet. There is no honest,
quantified triage reference: *given what you still have, is this recoverable, and roughly what
would it cost to try?*

That is the page. Its differentiating artifact is **search-space and cost arithmetic**: the actual
size of the candidate space for each partial-information case, and the actual guess rate against
each wallet format's key-derivation function. Those two numbers together decide every case, and
they are the numbers nobody publishes. They also produce the page's most valuable honest
conclusion — a BIP39 passphrase you have genuinely forgotten with no constraints is not
recoverable, and the correct advice is to stop paying people who say otherwise.

The scam section is a public good and the strongest trust artifact on the site. It is also what
makes the page defensible as a professional credential rather than an advertisement: the page's
loudest advice is *don't hire anyone yet, here is how to tell whether you need to.*

## Targeting

- **Primary query:** `bitcoin wallet recovery`
- **Secondary:** `forgot bip39 passphrase`, `recover seed phrase missing words`,
  `wrong derivation path funds missing`, `wallet.dat password recovery`,
  `crypto recovery service scam`, `btcrecover how long`, `lost hardware wallet seed`,
  `inherited crypto wallet access`
- **Mode:** **crisis mode.** This is the only crisis-mode page in the batch and it changes
  everything about the design. The reader has lost money, is frightened, is possibly being actively
  defrauded right now, and is reading on a phone. The title and H1 lead with the crisis phrase;
  H2s are question-shaped and match how the situation is described rather than how it is
  classified; the triage table is the first thing on the page and the scam warning is reachable
  within one screen.

## Draft title / H1 / meta

- `<title>`: `Crypto Wallet Recovery: What's Recoverable and What Isn't` (56 chars)
- **H1:** `Lost Access to a Crypto Wallet? Start Here`
- **Meta description (draft):**
  `An honest triage of crypto wallet recovery: which losses are recoverable, the real search-space and cracking-cost math for partial seeds and passwords, and how to identify a recovery scam.` (186 chars)

## Reader outcome

Within two minutes the reader can classify their own loss as recoverable, possibly recoverable or
not recoverable, and knows the next concrete step. Within twenty minutes they can estimate the
work involved, identify the tool that applies, and recognise the scam pattern being run on them.
Acceptance test: someone who has lost a wallet can decide — correctly — whether to spend money on
this, and never has to reveal a seed phrase to anyone to make that decision.

## Success metric

Two distinct ones. Search: organic entries on the loss-scenario queries, which are high-intent and
persistently in demand. Trust: the scam section being cited and linked by others, and the page
serving as the credibility artifact that connects the author's recovery practice to the rest of
this custody cluster. Return-direct traffic matters here (people come back to the triage table).

## Content approach

Triage first, safety second, math third, procedure fourth. A frightened reader must hit the
classification and the scam warning before any technical content.

1. **First: do these three things now** — a short, prominent block at the very top. Stop and make
   a forensic copy of any wallet file, keystore or device backup before touching anything (working
   on the only copy destroys cases). Write down everything you remember while you remember it,
   including wrong guesses, because the constraint set *is* the recovery. **Do not give your seed
   phrase to anyone, ever, including anyone who says they will recover your wallet** — a
   legitimate engagement works from an encrypted file or a constraint list, never from a seed.
   Three items, unmissable, above the fold.
2. **Triage table** — the signature element and the reason to bookmark. Rows are loss scenarios
   phrased the way people describe them ("I have the seed but the wallet shows zero", "I have the
   file but not the password", "I remember most of the password", "I have 11 of 12 words", "the
   device is broken", "the exchange closed my account", "the person who held it died", "I sent it
   to the wrong network"). Columns: what you must still have for this to be possible, feasibility
   (recoverable / constrained-search / not recoverable), the mechanism, the rough effort class, and
   a jump link to the section. The table must include the honest **not recoverable** rows and state
   them without softening: if the keys were never yours, this is not a recovery problem; if the
   entropy is genuinely unconstrained, no amount of money changes the answer.
3. **The most common case is not a lost key** — the section that resolves a large share of real
   cases and that no scam site will tell you, because there is no fee in it. **The seed is fine and
   the wallet is looking in the wrong place.** Cover: derivation-path mismatches across the
   standard account structures and the specific well-known deviations between wallet vendors;
   script-type mismatch (legacy, wrapped-segwit, native segwit, taproot) producing entirely
   different addresses from the same seed; a passphrase applied or not applied (the "25th word"
   creating a completely separate wallet, which is the single most common "my funds vanished"
   report); wrong coin type; account index; and the gap limit hiding funds beyond an unscanned
   index. Give the **systematic scan procedure**: derive the extended public key, scan the standard
   path and script-type matrix, check balances, and only then conclude the seed is wrong. This
   section should come before anything about cracking, because running it costs nothing and closes
   many cases.
4. **Search-space math** — the page's differentiating artifact, part one. A table of partial-
   information cases with the actual candidate-space size: one unknown seed word at a known
   position; one unknown word at an unknown position; two unknown words; a known word set in
   unknown order; a transcription error of a known class; a password with a remembered structure
   expressed as a mask; a passphrase drawn from a candidate list; unknown passphrase with no
   constraints. Show the arithmetic, not just the result, and use the seed checksum as the
   worked example of why constraints collapse a space (the checksum eliminates the overwhelming
   majority of candidates for free, which is why one missing word is trivial and four is not).
   End each row with the honest verdict: minutes, hours, GPU-months, or never.
5. **Cracking-cost math** — the differentiating artifact, part two, and the number that actually
   decides feasibility. A table of wallet formats against their key-derivation function and its
   cost: the seed-to-master-key derivation's iteration count (deliberately cheap, which is why
   constrained seed searches are viable), the reference client's wallet-file encryption (tuned to a
   target time per guess, which is why it is slow but not hopeless), memory-hard keystore
   derivation (the reason those files resist large-scale search), and browser-extension vault
   formats whose iteration counts increased substantially across versions (so the *version* that
   created the file changes the feasibility, which is a genuinely useful and rarely-stated fact).
   For each: guesses per second on a stated commodity GPU, and therefore the wall-clock and cloud
   cost to exhaust a space of a given size. **Combine §4 and §5 into a single decision rule** and
   state it explicitly: candidate space ÷ guess rate = time; if that exceeds the value at stake,
   stop. That rule is the page's thesis.
   Verify every iteration count and every benchmark against the format's source and current tool
   documentation, and state the hardware and date beside every rate — a benchmark without hardware
   and a date is worthless.
6. **Tools and what each is for** — the open-source recovery tools by name, with what class of
   problem each solves, what input each requires, and their limitations; the password-cracking
   suites and the specific modes for each wallet format; extended-key scanners for §3. Emphasise
   throughout that these are free, run locally, and never require sending a seed anywhere. Include
   the practical operational notes: work on the copy, checkpoint long runs, and how to express
   constraints as a token or mask file, since expressing the constraint correctly is most of the
   skill.
7. **Device and media forensics** — hardware wallet with a known seed but a dead device (trivial —
   the seed is the wallet, and this is worth stating because many people do not know it); device
   with an unknown PIN and no seed (the retry counter and wipe threshold make this a different and
   usually hopeless problem); a deleted or corrupted wallet file and file-carving recovery from a
   disk image; damaged physical backups and partial reconstruction; and paper/metal backups with
   illegible characters, where the checksum again does the work. Be clear about which of these are
   engineering and which are chip-level work outside most readers' reach.
8. **Recovery scams** — the public-good section, written to be linked on its own. The taxonomy:
   the upfront-fee model; unsolicited "we found your funds" contact; fake trading platforms that
   show a recovered balance and demand a withdrawal fee; reply-bots on any public post mentioning a
   loss; fake seed "validators" and "sync" tools that exfiltrate the phrase; impersonation of
   wallet support; and the second-wave scam that targets people who were already defrauded once.
   Then a red-flag checklist and, as the contrast that makes it useful, **what a legitimate
   engagement actually looks like**: no seed disclosure ever, work performed on an encrypted file
   or a constraint list, a contingency or escrowed fee rather than a large upfront payment, a real
   identity and a written agreement, and an honest feasibility opinion up front — including "this
   is not recoverable", which is the answer a scammer never gives. Cite the law-enforcement
   advisories on recovery fraud and give the reporting channels. **No self-promotion in this
   section** — the criteria are stated generically and the reader applies them to whoever
   contacted them, including to the author.
9. **Inherited and estate access** — the case that grows every year. What heirs actually need (not
   a seed in a will, which becomes a public record in probate); the practical designs that work —
   distributed backup schemes, a multi-key arrangement with an independent party, sealed
   instructions that locate the keys without containing them; the legal-access-versus-technical-
   access distinction, where an executor's authority is worthless without the key material; and the
   honest observation that most inherited crypto is permanently lost because the deceased optimised
   entirely for secrecy. Cross-link to the estate/life-admin content in this repo.
10. **Prevention** — the closing turn, written as the thing the reader should do for their *other*
    wallets tonight. Redundancy times geography; durable media; recording the wallet software, its
    version, the script type and the full derivation path alongside the seed (the single highest-
    value habit on this page, because §3 exists entirely because people do not do it); passphrase
    handling and the fact that an undocumented passphrase converts a backup into a puzzle; and the
    **annual restore drill** — restoring to a spare device and confirming the first address
    matches, which is the only test that proves a backup is real.
11. **Common mistakes** (mandatory) — working on the only copy; typing a seed into any website;
    paying an upfront fee; concluding the seed is wrong before scanning the path/script matrix;
    forgetting a passphrase was ever set; buying hardware to brute-force a space that the math says
    is hopeless; discarding a "wrong" guess list (it is the constraint set); storing the seed and a
    passphrase together; a backup never restore-tested.
12. **Related sheets** footer per the cross-link map.

## Volatile-facts register

**Overall: SLOW-DRIFT with one VOLATILE section.**
- **§5 cracking-cost math: VOLATILE** in its benchmarks, stable in its structure. GPU throughput
  improves and wallet formats raise iteration counts. Every rate carries hardware and date;
  re-verify annually and update the derived cost figures with it.
- **§6 tools: SLOW-DRIFT** — tools are renamed, abandoned or forked, and format support changes.
  Annual check that every named tool is still maintained; drop dead ones rather than leaving them.
- **§8 scam taxonomy: SLOW-DRIFT** — the underlying patterns are durable, the delivery channels
  rotate. Refresh the channel examples annually; keep the red-flag criteria as they are.
- **§3 derivation-path deviations: SLOW-DRIFT** — new wallets introduce new quirks.
- **§4 search-space math, §9 estate, §10 prevention: STABLE.**
Annual freshness target, §5 and §6 as the check targets.

## Index category

`Crypto Custody & Compliance`.

## Reading conditions

**Phone, at night, distressed, possibly mid-scam.** This is the batch's only crisis-mode page and
it must be designed for that reader first and the desk reader second — the inverse of every other
sheet here. Consequences, all mandatory: a comfortable base size (18 px minimum) because stressed
readers on phones do not zoom; the three-item safety block and the triage table both above the
fold at 375 px; large tap targets on the triage jump links; the scam section reachable from the top
without scrolling past technical content; no dark patterns, no urgency framing, no scarcity
language of any kind — the page must not resemble the thing it is warning about. Print is
irrelevant here. The dense math sections (§4, §5) are the desk-reader half and may be tables with
scroll wrappers, but they must not be what a phone reader hits first.

## Cross-link map

- **Internal outbound:** `bitcoin-self-custody-guide.html` and `bitcoin-wallet.html` (the
  prevention side — and §10 should hand off to them rather than duplicating them),
  `mpc-wallet-architecture.html` (sheet 1 — the institutional frozen-quorum analogue of the same
  problem), `institutional-crypto-custody.html` (sheet 3 — key ceremony and tested restores as the
  professional version of §10), `personal-cybersecurity.html` (the scam and device-hygiene
  adjacency), and the estate/life-admin content in this repo for §9.
- **Reciprocal inbound:** one line each from `bitcoin-self-custody-guide.html` and
  `bitcoin-wallet.html` ("if you have already lost access, start here") — these two are the
  highest-value reciprocal links in the batch because they reach the right reader at the right
  moment.
- **External cross-property:** a single, plain link to the author's recovery practice, placed in
  the page's footer or an "about this page" note — **not in the scam section and not in the
  triage table**, per §8's no-self-promotion rule. One link, clearly labelled as the author's own,
  is honest disclosure; anything more turns the page into the advertisement it is warning about
  and destroys its value. This constraint is the point of the whole design.
- **External outbound:** BIPs by number for the seed, derivation and descriptor standards; the
  tools' own repositories; law-enforcement advisories on recovery fraud (the national cybercrime
  reporting bodies' own publications) for §8.

## og:image / shareable artifact

The **triage table** at 1200×630, cropped to the six most common scenarios with the feasibility
column colour-coded on the shared semantic scale. It is what people will screenshot for someone
else who has just lost a wallet. The red-flag checklist from §8 is the second shareable artifact
and should be built to stand alone as an image too.

## Jurisdiction scope

Technical content is global. §8's reporting channels and §9's estate content are **US-centric and
must say so once**, with one line naming the equivalent reporting bodies elsewhere. §9 carries the
single legal disclaimer for the page — estate law varies by jurisdiction, verify locally — stated
once per README Rule 4, not per paragraph.

## Density targets

Triage table ≥ 12 scenarios × 5 columns, including ≥ 3 honest "not recoverable" rows. Derivation
matrix ≥ 5 script types × ≥ 6 wallet vendors/path conventions. Search-space table ≥ 8 partial-
information cases with arithmetic shown. Cracking-cost table ≥ 6 wallet formats with KDF, guess
rate, hardware and date. Tools ≥ 6 with input requirements and limitations. Device/media cases
≥ 6. Scam taxonomy ≥ 8 patterns plus a red-flag checklist of ≥ 8 items plus ≥ 5 legitimate-
engagement criteria. Prevention ≥ 7 practices. Common mistakes ≥ 9.

## Research sources (verify against these, per Rule 1)

BIP-32, BIP-39, BIP-43/44/49/84/86 and the descriptor BIPs, read directly, for path and checksum
claims. Wallet software source or documentation for each vendor-specific derivation deviation —
this is the section where secondary sources are most often wrong, so verify against the wallet's
own code or docs. Format specifications and source for every KDF parameter in §5, plus the current
documentation of the cracking tools for mode support and benchmark methodology; run or cite a
dated benchmark rather than reusing a figure of unknown provenance. Law-enforcement and regulator
advisories for §8, cited to the issuing body. **No recovery-service marketing material as a source
for anything**, including for scam patterns — use the advisories.

## Visual design

**Identity: the batch register, deliberately softened.** Every other sheet in this batch is
designed for a professional at a desk; this one is designed for a frightened person on a phone, and
it should feel calmer and plainer than its siblings — larger type, more whitespace, shorter
lines, fewer simultaneous colours. It keeps the batch's palette and the three-colour semantic scale
(here: green = recoverable, amber = constrained search, red = not recoverable) so it still belongs
to the set, but it drops the dense-console register entirely. **No urgency styling, no countdowns,
no red banners beyond the semantic scale's ordinary use** — the page must look unlike a scam site,
and that is a design requirement, not an aesthetic preference.

**Signature element: the triage decision table**, built as the page's first and best object — a
scenario-first table a panicking reader can find themselves in within seconds, with the feasibility
verdict as a plain word plus colour plus glyph, and a large tap target jumping to the relevant
section. At 375 px it becomes stacked cards, one scenario per card, verdict at the top of each
card. Design the 375 px card version first and derive the desktop table from it — the reverse of
the usual order, and correct here because the phone reader is the primary reader.

No JavaScript. No forms, no input fields of any kind anywhere on the page — a page about not
entering your seed anywhere must not contain a single text input, even an innocuous one.
