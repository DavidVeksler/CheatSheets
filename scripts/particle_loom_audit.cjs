#!/usr/bin/env node
// Particle Loom weaver gate (docs/specs/living-particle-loom-warp-weft.md, rev. 2, Phase 1b).
// Pulls #sm-data, #lessons and #weaver out of the HTML and runs:
//   1. the socket derivation (three rules must reproduce the vertex table exactly),
//   2. sampled decay channels and CKM flavors against PDG weights,
//   3. every lesson script through the event audit (including tie/miss expectations),
//   4. the free loom on five seeds,
//   5. injected faults, each of which the checks above must catch.
// Usage: node scripts/particle_loom_audit.cjs [file.html] [events]
"use strict";
const fs = require("fs");
const file = process.argv[2] || "docs/prototypes/particle-loom/weaver-debug.html";
const events = +(process.argv[3] || 10000);
const html = fs.readFileSync(file, "utf8");
const block = id => html.match(new RegExp(`<script[^>]*id="${id}">([\\s\\S]*?)</script>`))[1];
const data = block("sm-data"), lessonsSrc = block("lessons"), code = block("weaver");
const load = (src = code) => { const m = { exports: {} }; new Function("module", src)(m); return m.exports; };
const fresh = () => JSON.parse(data);

// One full pass of checks 1 to 4; returns a list of failures.
function check(lib, SMfn = fresh, lessons = JSON.parse(lessonsSrc), n = events, seeds = [1, 2, 3, 7, 42], log = false) {
  const fails = [];
  const sock = lib.socketDerivation(SMfn());
  if (!sock.pass) fails.push(`socket rules: extra [${sock.extra}] missing [${sock.missing}]`);
  if (log) console.log(`socket rules: ${sock.pass ? "PASS" : "FAIL"} (${sock.derived} derived, ${sock.expected} in the vertex table)`);
  const samp = lib.samplingCheck(SMfn(), 20000);
  if (!samp.pass) fails.push(...samp.problems.map(p => "sampling: " + p));
  if (log) console.log(`sampling vs PDG and CKM: ${samp.pass ? "PASS" : "FAIL"}`);
  for (const L of lessons) {
    const r = lib.auditRun(SMfn(), { script: L.steps });
    if (!r.pass) fails.push(...r.errors.map(e => `lesson ${L.id}: ${e}`));
    if (log) console.log(`lesson ${L.id} (${L.title}): ${r.pass ? "PASS" : "FAIL"} (${r.events} events)`);
  }
  for (const seed of seeds) {
    const r = lib.auditRun(SMfn(), { seed, events: n });
    if (!r.pass) fails.push(...r.errors.map(e => `seed ${seed}: ${e}`));
    if (log) console.log(`free loom seed ${seed}: ${r.pass ? "PASS" : "FAIL"} (${r.events} events, ${r.warnings.length} warnings)`);
  }
  return fails;
}

let ok = true;
const base = check(load(), fresh, undefined, events, undefined, true);
base.slice(0, 10).forEach(f => console.log("  " + f));
ok = !base.length;

// Each fault must make the checks fail, or a PASS proves nothing.
const withData = edit => () => { const SM = fresh(); edit(SM); return SM; };
const faults = {
  "photon and Z knots ignore sockets": { code: c => c.replace("const cands = lv.filter(m => ties(key, m.f));", "const cands = lv;") },
  "Higgs knots on neutrinos": { code: c => c.replace('const cands = lv.filter(m => ties("H", m.f));', "const cands = lv;") },
  "neutrino given an electric-charge socket": { data: withData(SM => SM.fermions.find(f => f.id === "ne").sockets.push("Q")) },
  "vertex removed from the table": { data: withData(SM => { SM.vertices = SM.vertices.filter(v => v.id !== "WWZ"); }) },
  "gluon knot breaks color neutrality": { code: c => c.replace("setSeg(A, t, A.f, b); setSeg(B, t, B.f, a);", "setSeg(A, t, A.f, b);") },
  "lane change without a W": { code: c => c.replace('emit({ t, kind: "exchange", boson: key, legs: [legInfo(A), legInfo(B)] });', "if (A.f === 'e') setSeg(A, t, 'mu', null); emit({ t, kind: \"exchange\", boson: key, legs: [legInfo(A), legInfo(B)] });") },
  "W products with the wrong charge": { data: withData(SM => { SM.decays.mu.channels[0].W = ["e", "ne"]; }) },
  "lepton flavor violation": { data: withData(SM => { SM.decays.mu.channels[0].to = "ne"; }) },
  "keys always miss": { code: c => c.replace("const fits = ties(key, th.f);", "const fits = false;") },
  "lesson claims a photon ties into a neutrino": { lessons: () => { const L = JSON.parse(lessonsSrc); L[1].steps.find(s => s.try === "γ" && s.on === "n1").expect = "tie"; return L; } },
  "decay channels ignore branching fractions": { code: c => c.replace("for (let i = 0; i < n; i++) c[ch.indexOf(weighted(ch.map(x => [x, x.br])))]++;", "for (let i = 0; i < n; i++) c[ch.indexOf(weighted(ch.map(x => [x, 1])))]++;") },
  "unstable visitors drift out instead of decaying": { code: c => c.replace('if (tau) { g.role = "visitor"; g.leaveAt = Infinity; }', 'if (tau) { g.role = "product"; g.leaveAt = t + 0.5; }') },
  "W scatters back in the free loom": { code: c => c.replace("wScatters: false,", "wScatters: true,") },
  "H → γγ loop through a particle without a charge socket": { data: withData(SM => { SM.decays.H.channels.find(c => c.kind === "loop" && c.products[0] === "γ").via = "Z"; }) },
};
for (const [name, f] of Object.entries(faults)) {
  const src = f.code ? f.code(code) : code;
  if (f.code && src === code) { console.log(`fault "${name}": patch no longer applies; update this script`); ok = false; continue; }
  let fails;
  try { fails = check(load(src), f.data || fresh, f.lessons ? f.lessons() : undefined, 3000, [3]); }
  catch (e) { fails = [`crashed: ${e.message}`]; }
  console.log(`fault "${name}": ${fails.length ? "caught" : "MISSED"}`);
  ok = ok && fails.length > 0;
}
console.log(ok ? "PARTICLE LOOM AUDIT: PASS" : "PARTICLE LOOM AUDIT: FAIL");
process.exit(ok ? 0 : 1);
