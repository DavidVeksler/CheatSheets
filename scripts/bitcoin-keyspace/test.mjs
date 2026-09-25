import test from 'node:test';
import assert from 'node:assert/strict';
import bip39 from 'bip39';
import { BIP32Factory } from 'bip32';
import * as ecc from 'tiny-secp256k1';
import * as bitcoin from 'bitcoinjs-lib';
import { exampleValues, MNEMONIC, PATH } from './values.js';

const v = exampleValues();

test('BIP39: zero-entropy phrase, word indices, checksum, empty-passphrase seed', () => {
  assert.equal(v.words.join(' '), MNEMONIC);
  assert.equal(v.entropy, '00000000000000000000000000000000');
  assert.deepEqual(v.indices, [0,0,0,0,0,0,0,0,0,0,0,3]);
  assert.equal(v.checksum, '0011');
  // BIP84 test vector seed (independent library)
  assert.equal(v.seed, bip39.mnemonicToSeedSync(MNEMONIC, '').toString('hex'));
});

test('BIP84 published vector: key, receive, next and change addresses', () => {
  assert.equal(v.publicKey, '0330d54fd0dd420a6e5f8d3624f5f3482cae350f79d5f0753bf5beef9c2d91af3c');
  assert.equal(v.address, 'bc1qcr8te4kr609gcawutmrza0j4xv80jy8z306fyu');
  assert.equal(v.nextAddresses[0], 'bc1qnjg0jd8228aq7egyzacy8cys3knf9xvrerkf9g');
  assert.equal(v.changeAddress, 'bc1q8c6fshw2dlwun7ekn9qwf37cu2rn755upcp6el');
});

test('every shown value cross-checks with bip32 + bitcoinjs-lib', () => {
  const root = BIP32Factory(ecc).fromSeed(bip39.mnemonicToSeedSync(MNEMONIC, ''));
  assert.equal(Buffer.from(root.privateKey).toString('hex'), v.masterPrivate);
  assert.equal(Buffer.from(root.chainCode).toString('hex'), v.masterChainCode);
  const key = root.derivePath(PATH);
  assert.equal(Buffer.from(key.privateKey).toString('hex'), v.privateKey);
  assert.equal(key.toWIF(), 'KyZpNDKnfs94vbrwhJneDi77V6jF64PWPF8x5cdJb8ifgg2DUc9d'); // BIP84 vector
  const pay = bitcoin.payments.p2wpkh({ pubkey: key.publicKey });
  assert.equal(Buffer.from(pay.hash).toString('hex'), v.hash160);
  assert.equal(pay.address, v.address);
  [1, 2, 3].forEach((i, n) => assert.equal(
    bitcoin.payments.p2wpkh({ pubkey: root.derivePath(`m/84'/0'/0'/0/${i}`).publicKey }).address, v.nextAddresses[n]));
});
