// Every value the page shows, computed from the published BIP84 test mnemonic.
import { HDKey } from '@scure/bip32';
import { mnemonicToEntropy, mnemonicToSeedSync } from '@scure/bip39';
import { wordlist } from '@scure/bip39/wordlists/english.js';
import { p2wpkh } from '@scure/btc-signer';
import { sha256 } from '@noble/hashes/sha2.js';
import { ripemd160 } from '@noble/hashes/legacy.js';
import { bytesToHex } from '@noble/hashes/utils.js';

export const MNEMONIC = 'abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about';
export const PATH = "m/84'/0'/0'/0/0";

const bin = bytes => [...bytes].map(v => v.toString(2).padStart(8, '0')).join('');

export function exampleValues() {
  const words = MNEMONIC.split(' ');
  const entropy = mnemonicToEntropy(MNEMONIC, wordlist);
  const checksum = bin(sha256(entropy)).slice(0, 4);
  const bits = bin(entropy) + checksum;
  const indices = bits.match(/.{11}/g).map(b => parseInt(b, 2));
  const seed = mnemonicToSeedSync(MNEMONIC, '');
  const master = HDKey.fromMasterSeed(seed);
  const key = master.derive(PATH);
  const hash = ripemd160(sha256(key.publicKey));
  const address = i => p2wpkh(master.derive(`m/84'/0'/0'/0/${i}`).publicKey).address;
  return {
    words, indices, checksum, entropy: bytesToHex(entropy),
    seed: bytesToHex(seed),
    masterPrivate: bytesToHex(master.privateKey), masterChainCode: bytesToHex(master.chainCode),
    privateKey: bytesToHex(key.privateKey), publicKey: bytesToHex(key.publicKey),
    hash160: bytesToHex(hash),
    address: address(0), nextAddresses: [1, 2, 3].map(address),
    changeAddress: p2wpkh(master.derive("m/84'/0'/0'/1/0").publicKey).address
  };
}
