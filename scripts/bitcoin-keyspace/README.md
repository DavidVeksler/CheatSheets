# How 12 Words Become a Bitcoin Address: source

`../../bitcoin-key-derivation-bips.html` is generated. Spec: [`TODO/bitcoin-keyspace-spec.md`](../../TODO/bitcoin-keyspace-spec.md). Edit `page.template.html` (copy) or `values.js` (the example), then:

```powershell
npm ci
npm test        # values vs published BIP39/BIP84 vectors + independent bip32/bitcoinjs-lib
npm run build   # fills {{PLACEHOLDERS}} in the template, writes the sheet
python preview.py   # redraws images/bitcoin-key-derivation-bips.png
```

The page is static HTML with no runtime JavaScript. Every value it shows comes from `values.js` at build time, derived from the public BIP84 test phrase (`abandon` ×11 `about`, no passphrase, path `m/84'/0'/0'/0/0`).

| Value | Provenance |
| --- | --- |
| Phrase, entropy, checksum | [BIP39](https://github.com/bitcoin/bips/blob/master/bip-0039.mediawiki) zero-entropy vector |
| Seed, master key, chain code | Cross-checked with `bip39` + `bip32` (test-only deps) |
| Private key (WIF), public key, addresses 0/1, change 0 | [BIP84 test vectors](https://github.com/bitcoin/bips/blob/master/bip-0084.mediawiki) |
| Addresses 2 and 3, HASH160 | Cross-checked with `bitcoinjs-lib` |
