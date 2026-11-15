// Post-process the raw Blender GLBs for inside-ai-data-center (spec 6.3): weld, local GPU instancing, quantize,
// meshopt. Writes models/inside-ai-data-center/<file>.glb and manifest.json.
//
// Run: node scripts/inside_ai_dc/post.mjs [s3-rack s4-tray ...]   (default: every raw GLB in build/inside_ai_dc/raw)
//
// Instancing is local: siblings named 'i.*' that share a mesh become one EXT_mesh_gpu_instancing node under the SAME
// parent, so instanced trays stay inside the rack hierarchy (gltf-transform's instance() would hoist them to the
// scene root). Named part nodes are never instanced or flattened.
import { createHash } from 'node:crypto';
import { execSync } from 'node:child_process';
import { existsSync, readdirSync, readFileSync, writeFileSync, mkdirSync } from 'node:fs';
import { gzipSync } from 'node:zlib';
import { dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS, EXTMeshGPUInstancing } from '@gltf-transform/extensions';
import { weld, quantize, meshopt, getBounds, prune } from '@gltf-transform/functions';
import { MeshoptEncoder, MeshoptDecoder } from 'meshoptimizer';

const ROOT = resolve(dirname(fileURLToPath(import.meta.url)), '..', '..');
const RAW = join(ROOT, 'build', 'inside_ai_dc', 'raw');
const OUT = join(ROOT, 'models', 'inside-ai-data-center');
const MANIFEST = join(OUT, 'manifest.json');
const BUDGET = { uniqueTriangles: 80000, renderedTriangles: 350000, drawCalls: 150, bytes: 700 * 1024, totalBytes: 5 * 1024 * 1024 };

await MeshoptEncoder.ready;
await MeshoptDecoder.ready;
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS)
  .registerDependencies({ 'meshopt.encoder': MeshoptEncoder, 'meshopt.decoder': MeshoptDecoder });

function instanceLocal(doc) {
  const ext = doc.createExtension(EXTMeshGPUInstancing);
  let batches = 0;
  const parents = [...doc.getRoot().listScenes(), ...doc.getRoot().listNodes()];
  for (const parent of parents) {
    const groups = new Map();
    for (const node of parent.listChildren()) {
      if (!node.getName().startsWith('i.') || !node.getMesh() || node.listChildren().length) continue;
      const mesh = node.getMesh();
      if (!groups.has(mesh)) groups.set(mesh, []);
      groups.get(mesh).push(node);
    }
    for (const [mesh, nodes] of groups) {
      if (nodes.length < 2) continue;
      const make = (type, n) => doc.createAccessor().setType(type).setArray(new Float32Array(nodes.length * n));
      const t = make('VEC3', 3), r = make('VEC4', 4), s = make('VEC3', 3);
      nodes.forEach((node, i) => { t.setElement(i, node.getTranslation()); r.setElement(i, node.getRotation()); s.setElement(i, node.getScale()); });
      const batch = ext.createInstancedMesh().setAttribute('TRANSLATION', t).setAttribute('ROTATION', r).setAttribute('SCALE', s);
      const kind = nodes[0].getExtras().kind || nodes[0].getName().split('.')[1];
      const bn = doc.createNode('i.' + kind).setMesh(mesh).setExtension('EXT_mesh_gpu_instancing', batch)
        .setExtras({ kind, count: nodes.length, tier: nodes[0].getExtras().tier || 'illustrative', ...('shadow' in nodes[0].getExtras() ? { shadow: nodes[0].getExtras().shadow } : {}) });
      parent.addChild(bn);
      nodes.forEach((node) => node.dispose());
      batches++;
    }
  }
  return batches;
}

function stats(doc) {
  let unique = 0, rendered = 0, draws = 0;
  const seen = new Set();
  const tris = (mesh) => mesh.listPrimitives().reduce((a, p) => a + (p.getIndices() ? p.getIndices().getCount() : p.getAttribute('POSITION').getCount()) / 3, 0);
  for (const node of doc.getRoot().listNodes()) {
    const mesh = node.getMesh();
    if (!mesh) continue;
    const inst = node.getExtension('EXT_mesh_gpu_instancing');
    const n = inst ? inst.getAttribute('TRANSLATION').getCount() : 1;
    const t = tris(mesh);
    if (!seen.has(mesh)) { seen.add(mesh); unique += t; }
    rendered += t * n;
    draws += mesh.listPrimitives().length;
  }
  return { uniqueTriangles: Math.round(unique), renderedTriangles: Math.round(rendered), drawCallEstimate: draws, nodes: doc.getRoot().listNodes().length };
}

const ids = process.argv.slice(2).length ? process.argv.slice(2) : readdirSync(RAW).filter((f) => f.endsWith('.glb')).map((f) => f.replace('.glb', ''));
mkdirSync(OUT, { recursive: true });
const manifest = existsSync(MANIFEST) ? JSON.parse(readFileSync(MANIFEST, 'utf8')) : { files: {} };
let commit = 'unknown';
try { commit = execSync('git rev-parse --short HEAD', { cwd: ROOT }).toString().trim(); } catch { /* not a checkout */ }
const failures = [];
for (const id of ids) {
  const meta = JSON.parse(readFileSync(join(RAW, id + '.meta.json'), 'utf8'));
  const doc = await io.read(join(RAW, id + '.glb'));
  await doc.transform(weld());
  const batches = instanceLocal(doc);
  await doc.transform(prune({ keepLeaves: true, keepExtras: true }), quantize({ quantizeNormal: 10, quantizeColor: 8 }), meshopt({ encoder: MeshoptEncoder, level: 'high' }));
  const s = stats(doc);
  const scene = doc.getRoot().getDefaultScene() || doc.getRoot().listScenes()[0];
  const b = getBounds(scene);
  const out = join(OUT, id + '.glb');
  await io.write(out, doc);
  const bytes = readFileSync(out);
  const entry = {
    stop: meta.stop, bytes: bytes.length, gzipBytes: gzipSync(bytes, { level: 9 }).length,
    sha256: createHash('sha256').update(bytes).digest('hex'), ...s, instancedBatches: batches,
    parts: meta.parts, anchors: meta.anchors, tiers: meta.tiers,
    bounds: { min: b.min.map((v) => +v.toFixed(4)), max: b.max.map((v) => +v.toFixed(4)) },
    metresPerUnit: meta.metresPerUnit, exaggeration: meta.exaggeration || {}, sourceCommit: commit,
  };
  manifest.files[id + '.glb'] = entry;
  for (const k of ['uniqueTriangles', 'renderedTriangles']) if (s[k] > BUDGET[k]) failures.push(`${id}: ${k} ${s[k]} > ${BUDGET[k]}`);
  if (s.drawCallEstimate > BUDGET.drawCalls) failures.push(`${id}: draw calls ${s.drawCallEstimate} > ${BUDGET.drawCalls}`);
  if (bytes.length > BUDGET.bytes) failures.push(`${id}: ${bytes.length} bytes > ${BUDGET.bytes}`);
  console.log(`${id}.glb: ${bytes.length} B (gzip ${entry.gzipBytes}), ${s.uniqueTriangles} unique / ${s.renderedTriangles} rendered tris, ~${s.drawCallEstimate} draws, ${batches} instanced batches`);
}
const total = Object.values(manifest.files).reduce((a, f) => a + f.bytes, 0);
if (total > BUDGET.totalBytes) failures.push(`all GLBs ${total} > ${BUDGET.totalBytes}`);
manifest.budget = BUDGET;
writeFileSync(MANIFEST, JSON.stringify(manifest, null, 1) + '\n');
if (failures.length) { failures.forEach((f) => console.error('BUDGET FAIL:', f)); process.exit(1); }
