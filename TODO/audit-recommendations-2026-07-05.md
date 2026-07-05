# Cheatsheet Audit — Recommendations (top 30 by popularity)

**Date:** 2026-07-05 · **Method:** `TODO/CHEATSHEET-AUDIT.md` §3 automated checks (scripted, verified against the filesystem) + §4 manual content checks. **No files were edited** — this is an audit-only pass; apply fixes per file in separate runs (`Audit fixes: <filename>` commits, per §1).

**Ordering:** descending `scores` from `popularity.json` (lastUpdated 2026-07-05). Ranks 31+ are the remaining queue (list at bottom).

**Browser checks (§5) were NOT run** — nothing was changed this pass. They become **mandatory** in the fix runs for any file where SRI or Bootstrap versions change (a wrong hash silently blocks the asset — check `typeof window.bootstrap !== 'undefined'`).

**Facts were NOT verified** (freshness job's territory). Items marked *→ freshness* go to `weekly-freshness-update.md`.

---

## Cross-cutting fixes (batch these — same edit shape everywhere)

1. **Bootstrap 5.3.3 → 5.3.8 + Icons 1.11.3 → 1.13.1 + SRI + `defer`** (CLAUDE.md has precomputed hashes). Files, by rank: bitcoin-whitepaper, shabbat-services-cheatsheet, boom-supersonic (icons only; BS is 5.3.3 *with* old SRI — bump both), tesla-products, humanoid-robots, privacy-data-broker-opt-out, google-ai-studio-guide, postgresql, yudkowsky-rationality-ai-cheatsheet, ashihara-karate, global_cuisine_guide, operator-loadouts, judo, aws-vs-azure, leadership, martial-arts-cheatsheet. Also icons-only bumps on otherwise-current pages: **ai-frontier**, **anapanasati** (icons 1.11.3, no SRI).
2. **Non-Bootstrap CDN assets needing computed SRI** (compute from real bytes, never recall):
   - `unpkg.com/aos@2.3.4` css+js — ashihara-karate, judo, leadership, martial-arts-cheatsheet
   - `tsparticles@2.12.0` — tesla-products
   - `leader-line-new@1.1.9` + Prism 1.29.0 (theme css, core, autoloader) — javascript-for-architects
3. **Missing JSON-LD (HIGH), add `TechArticle`, `datePublished` from `git log --diff-filter=A`:** compression-algorithms, bitcoin-whitepaper, shabbat-services-cheatsheet, bitcoin-wallet, postgresql, yudkowsky, anapanasati, ashihara-karate, judo, leadership.
4. **Missing `Last verified` footer (HIGH; add only after the fix-run review):** bitcoin-whitepaper, shabbat-services-cheatsheet, yudkowsky, anapanasati, ashihara-karate, global_cuisine_guide, judo, leadership, art-of-war-sun-tzu, martial-arts-cheatsheet.
5. **Web-font design pass (MEDIUM — flag, don't fix inline; visual identity at stake):** bitcoin-whitepaper (Fira Code/Inter/Roboto Cond), shabbat (Lato/Merriweather/Noto Serif Hebrew — Hebrew font may be load-bearing), boom-supersonic (Chakra Petch/Inter), tesla-products (Inter), bitcoin-wallet (Fira Code/Inter/Orbitron), google-ai-studio (Google Sans/Roboto), yudkowsky (Fira Code/Inter), ashihara + judo (Oswald/Roboto), global_cuisine (Inter/Montserrat/Oswald), leadership (Lato/Poppins), art-of-war (Noto Serif SC — likely needed for Chinese glyph coverage; check system fallbacks first), martial-arts (Anton/Cinzel/Noto Sans JP/Oswald/Roboto — Anton/Cinzel are brand identity).
6. **Cross-link clusters** — recurring gap; cheap wins:
   - Radio: baofeng-uv5r-quick-ref ↔ baofeng-uv5r-ham-guide ↔ ham-radio-technician ↔ emergency-radio-card (quick-ref currently links none).
   - Bitcoin: bitcoin-wallet → bitcoin-self-custody-guide, bitcoin-exchanges-cards (currently none).
   - Buddhism: anapanasati → satipatthana-four-foundations, anatta-not-self, five-hindrances-debugger, craving-desire-habit-loops.
   - Martial arts: ashihara-karate footer only links judo — add brazilian-jiu-jitsu + martial-arts-cheatsheet; reciprocate.
   - Databases: postgresql ↔ databases.html.
7. **`anduril-products.html` does not exist yet ranks #32 in traffic** (64.1 score — people are hitting a 404). Linked from engineering-metals-selection (top-30 BLOCKER, below) and automotive-innovation-timeline. Strong spec candidate for `TODO/`; until then, remove/retarget the two links.

**Corrections to the corpus baseline (Appendix of CHEATSHEET-AUDIT.md):** the "placeholder og:image" BLOCKERs on bitcoin-whitepaper and compression-algorithms are **commented-out leftovers** — the live og:image tags are correct and the PNGs exist. Downgrade to LOW (delete the commented lines). All 30 canonicals are correct. `images/tesla-products.png` and `images/humanoid-robots-social.png` both exist.

---

## Per-file recommendations (descending popularity)

### 1. ai-frontier.html (score 1326) — verdict: FIXED-candidate (minor)
- **HIGH:** Icons 1.11.3 without SRI → 1.13.1 + hash (only CDN tag of 3 missing SRI).
- **LOW:** og:image points at `images/ai-frontiers.png` (exists) while `images/ai-frontier.png` also exists — pick the convention name, delete or stop referencing the other.
- **Content:** OK — comprehensive 7-lab coverage, dated volatile facts ("as of July 2026", Series-H valuation, release dates), truthful JSON-LD (dateModified 2026-07-04 = git). No changes needed.

### 2. compression-algorithms.html (386) — verdict: FIXED+FLAGS
- **HIGH:** Missing JSON-LD → add TechArticle.
- **MEDIUM:** No Common Mistakes section (technical topic — mandatory). Suggested entries: recompressing already-compressed data, lossy-vs-lossless confusion, ignoring CPU/memory cost vs ratio, incompressible data expansion.
- **LOW:** Delete commented-out `yourdomain.com` meta tags (lines ~20, 27) — cosmetic, but they trip placeholder scans.
- **Content:** Strong — 27-algorithm quick-ref table, atomic entries (Zstd/Deflate/FLAC spot-checked), dated context (PEP 784, XZ CVE-2024-3094). Has Last verified 2026-07-04.

### 3. orbital-rockets-comparison.html (366) — verdict: PASS
- No metadata, CDN, or content defects. App-like density is in the table/cards; volatile facts explicitly dated (New Glenn LC-36 explosion May 28 2026, recovery window 2027–28); JSON-LD truthful. Leave alone.

### 4. bitcoin-whitepaper.html (311) — verdict: FIXED+FLAGS
- **HIGH:** Missing JSON-LD. Missing Last verified. SRI 0/3. Bootstrap 5.3.3 + Icons 1.11.3 → bump + hashes. Bootstrap JS not deferred.
- **MEDIUM:** Web fonts ×3 (design pass). Footer says "Last updated: 2025" (copyright-style) while git says 2026-06-25 — reconcile when adding the real stamp.
- **LOW:** Delete commented `YOUR_IMAGE_URL_HERE` meta lines (~18, 25).
- **Content:** Exemplary (difficulty-adjustment formulas, halving code, Poisson double-spend analysis, P2SH/SegWit/Taproot timeline; links bitcoin cluster). Content untouched — metadata batch only.

### 5. modern-firearms.html (290) — verdict: PASS (verify one section)
- Metadata/CDN clean; JSON-LD truthful; "Last updated: July 2026" + Last verified present.
- **Verify in fix run:** confirm a Safety Rules / Common Mistakes section exists in the lower half (auditor's read was truncated; header suggests Four Rules present). If absent → add Common Mistakes (MEDIUM).

### 6. shabbat-services-cheatsheet.html (254) — verdict: FIXED+FLAGS (app-like)
- **HIGH:** Missing JSON-LD. Missing Last verified. SRI 0/3. Bootstrap 5.3.3 → 5.3.8. JS not deferred.
- **MEDIUM:** Content lives in `reform/conservative/orthodox/emanuel_transcript.json` — **all four exist**, page is functional (an auditor's contrary claim was wrong). But there's no `<noscript>`/static fallback: with JS off the page is ~300 words. Add a noscript note or minimal static outline (AGENTS.md no-JS check).
- **LOW:** og:image `images/shabbat-preview.png` exists but is nonstandard naming.
- **Content:** Fine for its purpose once JSON loads; entries are narrative (liturgy, appropriately so). Cross-links etz-chaim + anapanasati already.

### 7. boom-supersonic.html (245) — verdict: FIXED-candidate
- **HIGH:** Icons 1.11.3 lacks SRI; Bootstrap is 5.3.3 (with old SRI) → bump both to pins + new hashes; add `defer` to the bundle script.
- **MEDIUM:** Web font (design pass).
- **Content:** OK — quantified specs (Mach 1.7, 201 ft, ICAO Ch.14), regulatory timeline dated (June 2025 EO, March 2026 SAM Act), JSON-LD truthful, Last verified 2026-07-04. Consider footer cross-links (orbital-rockets, tesla) — currently isolated.

### 8. baofeng-uv5r-quick-ref.html (231) — verdict: PASS
- Metadata fully clean (5.3.8 + SRI, JSON-LD, Last verified July 4 2026). Content excellent (menu dictionary ×40, both programming methods, troubleshooting).
- **LOW:** Zero internal cross-links — add radio cluster (ham-guide, ham-radio-technician, emergency-radio-card).

### 9. tesla-products.html (228) — verdict: FIXED-candidate
- **HIGH:** SRI 0/4 (Bootstrap css/js 5.3.3, Icons 1.11.3, tsparticles 2.12.0) → bump pins, add hashes (compute tsparticles), defer both scripts.
- **MEDIUM:** Web font (design pass).
- **Content:** OK — exceptional density and dating (Cybertruck AWD $71,985 Feb 2026, Semi Megacharging 1.2 MW, detailed Last-verified footer enumerating what was checked on 2026-07-04). JSON-LD truthful. og:image exists (an auditor's contrary claim was wrong).

### 10. humanoid-robots.html (214) — verdict: FIXED-candidate
- **HIGH:** SRI 0/3; Bootstrap 5.3.3 + Icons 1.11.3 → bump + hashes; defer.
- **LOW:** og:image `images/humanoid-robots-social.png` exists — nonstandard name only.
- **Content:** OK — 11 companies, milestones dated throughout (Figure 03 Oct 2025, CES 2026 Atlas, Optimus Gen 3 March 2026), JSON-LD truthful, Last verified present. Consider cross-link to ai-frontier.

### 11. bitcoin-wallet.html (194) — verdict: FIXED+FLAGS
- **HIGH:** Missing JSON-LD → add TechArticle (dateModified 2026-07-04).
- **MEDIUM:** Hardware-wallet product mentions (Trezor/Coldcard/Ledger) undated — add "as of Jul 2026" tags *→ freshness*. No cross-links to bitcoin cluster → add.
- **LOW:** og:image `images/bitcoin-og.png` nonstandard name (exists).
- **Content:** Solid — seed-phrase rules, fees in sat/vB, multisig/PSBT/passphrase coverage; Bootstrap 5.3.8+SRI already correct.

### 12. privacy-data-broker-opt-out.html (168) — verdict: FIXED-candidate
- **HIGH:** SRI 0/3; Bootstrap 5.3.3 → 5.3.8 + hashes; defer.
- **Content:** PASS — model volatile-topic hygiene (18 broker tasks with URLs/steps/gotchas; "as of July 2026, 21 states"; CFPB rule withdrawal dated May 15 2025; JSON-LD truthful). Broker URLs/procedures *→ freshness* on schedule.

### 13. google-ai-studio-guide.html (163) — verdict: FIXED+FLAGS
- **BLOCKER:** JSON-LD is **FAQPage with no visible Q&A section** — schema misrepresents the page to crawlers. Replace with TechArticle.
- **HIGH:** SRI 0/3; Bootstrap 5.3.3 → 5.3.8 + hashes; defer.
- **MEDIUM:** Model lineup / UI settings undated ("Gemini 3.5 Flash", temperature ranges) — add "as of Jul 2026" tags; confirm the footer freshness stamp wording *→ freshness* (fast-moving product). Web fonts incl. Google Sans (design pass).
- **Content:** Good — parameter entries are atomic (Temperature/Top-P with ranges, use-cases, failure modes); links prompt-builder + yudkowsky.

### 14. postgresql.html (158) — verdict: FIXED+FLAGS
- **HIGH:** Missing JSON-LD. SRI 0/3; Bootstrap 5.3.3 → 5.3.8 + hashes; defer.
- **MEDIUM:** No Quick Reference block at top of a 16k-word page — add (e.g., "most-used commands / config defaults" card). Gotchas are distributed but no dedicated Common Mistakes/anti-patterns section — consolidate one. Version-sensitive defaults (`shared_buffers` guidance etc.) undated *→ freshness*.
- **LOW:** Cross-link databases.html.
- **Content:** Excellent depth (MVCC/xmin/xmax, VACUUM/wraparound, index-type matrix); worth the metadata investment given rank.

### 15. yudkowsky-rationality-ai-cheatsheet.html (144) — verdict: FIXED-candidate
- **HIGH:** Missing JSON-LD. Missing Last verified. SRI 0/3; Bootstrap 5.3.3 → 5.3.8; defer.
- **MEDIUM:** Web fonts (design pass).
- **Content:** OK — concepts (orthogonality, instrumental convergence, Sequences structure) are evergreen and well-structured; already cross-links airisk + google-ai-studio. Metadata-only fix.

### 16. baofeng-uv5r-ham-guide.html (136) — verdict: PASS (flags)
- Metadata clean (JSON-LD truthful, dateModified = git).
- **MEDIUM:** Colorado repeater entries (SkyHub 449.450 etc.) are volatile and undated — add "as of" tags *→ freshness*.
- **LOW:** Cross-link baofeng-uv5r-quick-ref + ham-radio-technician.

### 17. anapanasati-mindfulness-of-breathing.html (134) — verdict: FIXED+FLAGS
- **HIGH:** Missing JSON-LD (add Article/TechArticle, datePublished from git-add, dateModified 2026-06-25). Missing Last verified. Icons 1.11.3 CDN tag without SRI (sole CDN tag).
- **MEDIUM:** Cross-link the Buddhism cluster (satipatthana, anatta, five-hindrances, craving-desire) — currently only buddhism.html + shabbat. A "foundations" pointer card for beginners would close the only self-containment gap.
- **Content:** Excellent (16 steps by tetrad, pacer, troubleshooting-equivalent pitfalls). Metadata/link fixes only.

### 18. strength-training.html (133) — verdict: PASS
- Only finding: JSON-LD `dateModified` 2026-06-24 vs git 2026-07-01 (LOW — correct when next touched). Otherwise the corpus gold standard: Quick Ref grid, dedicated Common Mistakes, quantified everything (RIR table, MV/MEV/MAV/MRV, 1.6–2.2 g/kg).

### 19. veterinary-diagnostics.html (129) — verdict: PASS (verify two details)
- Metadata present and current (dateModified 2026-07-04 = git).
- **Verify in fix run:** (a) JSON-LD `image` URL — schema shows `.../vet_diagnostics_og_image.png` without the `images/` path segment the real file has; (b) schema `author` is Organization — convention elsewhere is Person "David Veksler (AI Generated)".
- **MEDIUM:** No unified Quick Reference (common panels by species/complaint would fit). Reference-interval guidance undated *→ freshness*.
- **LOW:** og:image nonstandard name (`vet_diagnostics_og_image.png`, exists); no vet/medical cross-links (medical-school-curriculum is the nearest sibling).

### 20. ashihara-karate.html (128) — verdict: FIXED+FLAGS (oldest top-20 page, 2025-12-21)
- **HIGH:** Missing JSON-LD. Missing Last verified. SRI missing on 3/5 CDN tags (Icons 1.11.3, AOS css+js); Bootstrap 5.3.3 → 5.3.8; defer ×2.
- **MEDIUM:** Web fonts (design pass). Cross-links: only judo — add brazilian-jiu-jitsu + martial-arts-cheatsheet.
- **Content:** OK — thorough Sabaki-centered coverage with progress checkboxes; "Tips for Progress" covers the pitfalls role.

### 21. global_cuisine_guide.html (101) — verdict: FIXED+FLAGS
- **HIGH:** Missing Last verified. SRI 0/3; Bootstrap 5.3.3 → 5.3.8; defer. JSON-LD `dateModified` 2024-05-21 is stale vs git 2025-12-21 — fix.
- **MEDIUM:** Web fonts (design pass). Entries are survey-level (few gotchas/proportions) — acceptable as a breadth page; only EXPAND if you want it to be a working cooking reference (cooking-guide.html already covers technique).
- **Content:** Broad 12+12 cuisines, links cooking-guide + home-maintenance.

### 22. operator-loadouts.html (98) — verdict: FIXED-candidate
- **HIGH:** SRI 0/3; Bootstrap 5.3.3 → 5.3.8 + hashes; defer.
- **LOW:** `lang="en-US"` (spec expects `en` — harmless, normalize opportunistically). No Quick Ref (a by-scenario kit summary card would fit). No cross-links (modern-firearms, emergency-radio-card are natural).
- **Content:** OK — excellent atomic entries (Laerdal LCSU 4, CAT Gen 7, retention-holster gotcha), JSON-LD truthful.

### 23. engineering-metals-selection.html (95) — verdict: FIXED (one blocker)
- **BLOCKER:** Broken link → `anduril-products.html` (does not exist). Remove or retarget (engineering-materials-future.html is in-page and live). Note the traffic demand for that page (see cross-cutting §7).
- **Content:** OK otherwise — quantified properties (A36 250 MPa yield, sensitization/embrittlement gotchas), selection matrix, current JSON-LD. Metadata clean.

### 24. azure-devops.html (94) — verdict: PASS
- Metadata clean; JSON-LD truthful; volatile items dated ("as of June 2026" CodeQL, June-2026 GitHub-migration note). Opinionated, atomic entries.
- **LOW:** No Quick Ref (a YAML pipeline scaffold block would fit). Consider consolidating the scattered "biggest mistake" callouts into a Common Mistakes section.

### 25. judo.html (90) — verdict: FIXED+FLAGS
- **HIGH:** Missing JSON-LD (dateModified 2025-12-21). Missing Last verified. SRI missing on Icons + AOS css/js; Bootstrap 5.3.3 → 5.3.8; defer ×2.
- **MEDIUM:** Web fonts (design pass).
- **LOW:** Quick Ref idea: condensed Gokyo no Waza table. Cross-links exist (bjj, ashihara).
- **Content:** OK — good three-tier coverage; partial self-containment is inherent to the medium (needs mats and a partner, not more HTML).

### 26. aws-vs-azure.html (89) — verdict: FIXED+FLAGS
- **HIGH:** SRI 0/3 (verified — zero `integrity` attributes in file); Bootstrap 5.3.3 → 5.3.8 + hashes; defer.
- **MEDIUM:** No Common Mistakes section (technical topic): vendor lock-in, RI over-commitment, egress-cost surprises. Service/pricing facts undated — add "as of Jul 2026" on the volatile ones *→ freshness*.
- **Content:** OK — 13 categories, concrete service pairs with trade-offs; JSON-LD (BreadcrumbList + TechArticle) truthful.

### 27. leadership.html (84) — verdict: FIXED+FLAGS
- **HIGH:** Missing JSON-LD. Missing Last verified. SRI missing on Icons + AOS; Bootstrap 5.3.3 → 5.3.8; defer ×2.
- **MEDIUM:** Web fonts (design pass). Quick Ref idea: 15-commitments-at-a-glance grid.
- **Content:** OK — deep, sourced (Gottman 5:1, Sedona, Byron Katie), evergreen; links conscious-leadership-contexts.

### 28. art-of-war-sun-tzu.html (84) — verdict: PASS (flags) — app-like dual-language reader
- **HIGH:** Missing Last verified (evergreen text, stamp still required per freshness doc §7–8).
- **MEDIUM:** JSON-LD (WebPage/Book) lacks datePublished/dateModified — add. Noto Serif SC web font: check CJK system-font fallback before removing (glyph coverage is load-bearing here — design pass, careful).
- **Content:** OK — both data JSONs exist and match (13 chapters verified); fetch error-handling present. Browser check in fix run: toggle, chapter nav, 375 px.

### 29. javascript-for-architects.html (73) — verdict: FIXED+FLAGS
- **HIGH:** SRI missing on 4/7 CDN tags (leader-line-new 1.1.9, Prism theme/core/autoloader — compute hashes); 5 scripts undeferred (Prism autoloader ordering matters — test after adding defer).
- **MEDIUM:** No Common Mistakes section (tree-shaking, mixed async patterns, memoization misuse). Framework/tool versions undated — "as of Jul 2026" tags *→ freshness*. Confirm a visible Last-verified footer exists (auto-scan found a match; auditor's read of the truncated file did not).
- **Content:** OK — broad and deep (core JS → frameworks → tooling → architecture), truthful JSON-LD, Bootstrap already 5.3.8+SRI.

### 30. martial-arts-cheatsheet.html (69) — verdict: FIXED+FLAGS (most structurally defective in top 30)
- **HIGH:** File begins at `<head>` — **no `<!DOCTYPE html>` and no `<html lang="en">` at all** (the corpus's one missing-lang file). Add both. Missing Last verified. SRI 0/5 (verified — zero integrity attributes); Bootstrap 5.3.3 → 5.3.8, Icons → 1.13.1, AOS hashes; defer ×2. JSON-LD (Article) lacks datePublished/dateModified — add (git: 2026-06-25).
- **MEDIUM:** Web fonts ×5 (design pass — Anton/Cinzel are identity fonts, batch carefully). Quick Ref idea: 9-arts comparison grid (striking/grappling/sport/self-defense).
- **Content:** OK — 9 arts × 3 cards, concrete techniques and key figures; inline cross-links to ashihara/bjj/judo already present.

---

## Remaining queue (ranks 31+, not audited this pass)

engineering-materials-future (68), data-center-myths (64), databases (57), brazilian-jiu-jitsu (51), dotnet-cheatsheet (49), etz-chaim-tree-of-life (46 — baseline flags a placeholder og:image, check first), lifestyle-calculator (45), samsung-bespoke-oven-guide (45), python-for-architects (44), ai-model-picker (43), judaism (43), how-its-built (41), medical-school-curriculum (41), sleep-optimization (38), human-evolution (36), ai-coding-agents-compared (35), objectivism (34), index-investing-tax-advantaged (34), … (per popularity.json `scores`).

Also in the baseline but outside the traffic top-30: `automotive-innovation-timeline.html` shares the broken `anduril-products.html` link — fix it whenever the engineering-metals fix lands.
