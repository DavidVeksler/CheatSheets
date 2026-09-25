# How 12 Words Become a Bitcoin Address: spec

Status: rewritten 24 Sep 2026 after the first build (a 9-section, 8-BIP explorer with a 3D tree) read as a jumble. This version teaches **one concept** to a beginner.
Target: https://cheatsheets.davidveksler.com/bitcoin-key-derivation-bips.html (filename kept; existing links point here).

## The one concept

Your recovery words are not a password to an account. They are a number, and every key and address in your wallet is computed from that number by a fixed recipe. Follow one example through the recipe, front to back, and the reader understands why the words alone restore the wallet.

Success: a beginner can retell the chain **words → seed → master key → path → private key → public key → address** and say which links must stay secret.

## Flow (one example, one direction, no branching)

Example: the published BIP84 test phrase `abandon ×11 about`, no passphrase, path `m/84'/0'/0'/0/0`, address `bc1qcr8te4kr609gcawutmrza0j4xv80jy8z306fyu`. Every value shown is computed at build time by `scripts/bitcoin-keyspace/values.js` and tested against the published BIP39/BIP84 vectors and an independent library.

| Step | Plain question | Shows | Secret? |
|---|---|---|---|
| 1 Words | What is actually written on my backup? | 12 words as numbers 0-2047; 128 random bits + 4 checksum bits | Secret |
| 2 Seed | What does the wallet do with the words? | One-way scramble (PBKDF2, 2,048 rounds) to a 64-byte seed; one sentence on passphrases | Secret |
| 3 Master key | How does a seed become a key? | Seed hashed, split into master private key + chain code | Secret |
| 4 Path | How does one master key become many keys? | `m/84'/0'/0'/0/0` read left to right, one plain row per number | Secret |
| 5 Public key | What can I show people? | Private key → public key, one-way | Shareable (privacy-sensitive) |
| 6 Address | Where does the address come from? | Hash of the public key, Bech32-encoded to `bc1q...` | Shareable |
| Payoff | Why can the wallet make endless addresses? | Change the last number: addresses 0-3 and change address 0 | |

Then: "What this means for you" (5-6 practical consequences: words are the wallet, passphrase makes a different wallet, a wrong path shows an empty wallet, addresses are safe to share, words never go into a website) and a short "Go deeper" link list.

## Deliberately out of scope

Other address types (BIP44/49/86) beyond one sentence, xpubs and watch-only wallets, hardened-derivation math, SLIP-132 prefixes, BIP85, 3D visualisation, in-browser crypto, controls. Link out to the self-custody and wallet-recovery sheets instead.

## Build

Static HTML, no runtime JS required. `npm test` checks values against vectors; `npm run build` fills `page.template.html`. Standard site metadata, breadcrumb, byline.
