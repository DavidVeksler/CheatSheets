// Fill page.template.html with values computed by values.js and write the delivered sheet.
import { readFile, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import path from 'node:path';
import { exampleValues } from './values.js';

const dir = path.dirname(fileURLToPath(import.meta.url));
const v = exampleValues();
const words = v.words.map((w, i) => `<li>${w}<small>#${v.indices[i]}</small></li>`).join('');
const row = (p, a, here) => `<tr${here ? ' class="here"' : ''}><td><code>${p}</code></td><td class="addr mono">${a}</td></tr>`;
const rows = [row("m/84'/0'/0'/0/0", v.address, true),
  ...v.nextAddresses.map((a, i) => row(`m/84'/0'/0'/0/${i + 1}`, a)),
  row("m/84'/0'/0'/1/0", v.changeAddress)].join('\n');
const fill = { WORDS: words, SEED: v.seed, MASTER_PRIV: v.masterPrivate, MASTER_CC: v.masterChainCode,
  PRIV: v.privateKey, PUB: v.publicKey, HASH160: v.hash160, ADDRESS: v.address, ADDR_ROWS: rows };
let html = await readFile(path.join(dir, 'page.template.html'), 'utf8');
for (const [k, val] of Object.entries(fill)) html = html.replaceAll(`{{${k}}}`, () => val);
const left = html.match(/\{\{\w+\}\}/);
if (left) throw new Error(`Unfilled placeholder ${left[0]}`);
await writeFile(path.resolve(dir, '../../bitcoin-key-derivation-bips.html'), html);
console.log(`Wrote bitcoin-key-derivation-bips.html (${Buffer.byteLength(html)} bytes)`);
