#!/usr/bin/env node
// Particle Loom weaver gate (docs/specs/living-particle-loom-warp-weft.md, Phase 1).
// Pulls #sm-data and #weaver out of the HTML, runs the audit over several seeds, then
// injects known faults and requires the audit to catch every one.
// Usage: node scripts/particle_loom_audit.cjs [file.html] [events]
"use strict";
const fs = require("fs");
const file = process.argv[2] || "docs/prototypes/particle-loom/weaver-debug.html";
const events = +(process.argv[3] || 10000);
const html = fs.readFileSync(file, "utf8");
const data = html.match(/<script type="application\/json" id="sm-data">([\s\S]*?)<\/script>/)[1];
const code = html.match(/<script id="weaver">([\s\S]*?)<\/script>/)[1];
const load = (src = code) => { const m = { exports: {} }; new Function("module", src)(m); return m.exports; };

let ok = true;
const { auditRun } = load();
for (const seed of [1, 2, 3, 7, 42]) {
  const r = auditRun(JSON.parse(data), { seed, events });
  ok = ok && r.pass;
  console.log(`audit seed ${seed}: ${r.pass ? "PASS" : "FAIL"} (${r.events} events, ${r.errors.length} errors, ${r.warnings.length} warnings)`);
  r.errors.slice(0, 5).forEach(e => console.log("  " + e));
}

// Each fault must make the audit fail, or a PASS proves nothing.
const faults = {
  "photon knots on neutrinos": [c => c.replace("const charged = live.filter(m => F[m.f].q3 !== 0);", "const charged = live;")],
  "photon rule edited in the vertex table": [null, SM => { SM.vertices.find(v => v.id === "ffA").requires = "quark"; }],
  "Higgs knots on neutrinos": [c => c.replace("const massive = live.filter(m => F[m.f].massive);", "const massive = live;")
                                     .replace("F[A.f].massMeV / (SM.v.value * 1e3)", "Math.max(1e-9, F[A.f].massMeV) / (SM.v.value * 1e3)")],
  "gluon knot breaks color neutrality": [c => c.replace("setSeg(A, t, A.f, b); setSeg(B, t, B.f, a);", "setSeg(A, t, A.f, b);")],
  "lane change without a W": [c => c.replace('emit({ t, kind: "exchange", boson: "Z"', "if (A.f === 'e') setSeg(A, t, 'mu', null); emit({ t, kind: \"exchange\", boson: \"Z\"")],
  "W products with the wrong charge": [null, SM => { SM.decays.mu.channels[0].W = ["e", "ne"]; }],
  "lepton flavor violation": [null, SM => { SM.decays.mu.channels[0].to = "ne"; }],
};
for (const [name, [patchCode, patchData]] of Object.entries(faults)) {
  const src = patchCode ? patchCode(code) : code;
  if (patchCode && src === code) { console.log(`fault "${name}": patch no longer applies; update this script`); ok = false; continue; }
  const SM = JSON.parse(data); if (patchData) patchData(SM);
  let r; try { r = load(src).auditRun(SM, { seed: 3, events: 4000 }); } catch (e) { console.log(`fault "${name}": crashed (${e.message})`); ok = false; continue; }
  console.log(`fault "${name}": ${r.pass ? "MISSED" : "caught"}`);
  ok = ok && !r.pass;
}
console.log(ok ? "PARTICLE LOOM AUDIT: PASS" : "PARTICLE LOOM AUDIT: FAIL");
process.exit(ok ? 0 : 1);
