# Cheatsheet Audit — per-file conformance procedure

Instruction set for **auditing one completed cheatsheet per run** against the repo's current
standards. Written to be executed systematically across all ~101 HTML files. Grounded in a
corpus scan on **2026-07-04** (see Appendix for the baseline findings and priority lists).

**Division of labor with the other repo docs:**
- `AGENTS.md` — owns the quality bar. This audit *applies* it retroactively; it never redefines it.
- `weekly-freshness-update.md` — owns **fact drift** (stale versions, prices, model names).
  This audit does NOT re-verify facts; it checks that the freshness *machinery* exists
  (stamps, dated volatile facts). If you find stale facts, note them for the freshness job.
- `TODO/SPEC-AUDIT.md` — spec completeness for *future* pages; not used here.

**Context that explains most defects:** the corpus spans several generations of the build
pipeline. Old pages predate the SRI mandate, JSON-LD requirement, `Last verified` line,
Bootstrap 5.3.8 pin, and no-web-fonts rule. The audit's job is to bring each page up to the
current standard *or* explicitly accept a legacy exception — never to silently skip.

---

## 1. Execution model

- **One file per run.** `FILE` = the cheatsheet path. Touch only `FILE` (plus `index.php`
  if adding a `$categoryMap` entry, and `images/` if generating a missing preview).
- **Audit → fix → report.** Run all checks first, classify findings by severity, apply the
  in-place fixes (§6), then report (§7). Don't fix as you go — a full defect picture first.
- **Surgical edits only.** Preserve structure, voice, layout, classes. If defects are
  structural (thin content, no real sections), recommend **REGENERATE** rather than patching.
- Commit per repo norm: one commit per audited file, explicit paths only, `Co-Authored-By`
  trailer. Message: `Audit fixes: <filename>`.

## 2. Severity tiers

| Tier | Meaning | Examples |
|---|---|---|
| **BLOCKER** | Visibly broken or lying to users/crawlers | placeholder URLs (`YOUR_IMAGE_URL_HERE`, `yourdomain.com`), broken internal links, JSON-LD describing content not on the page, `dateModified` bumped without review |
| **HIGH** | Violates a hard AGENTS.md requirement | missing JSON-LD, missing `Last verified`, CDN tags without SRI, unpinned/old Bootstrap, missing `$categoryMap` entry, missing preview image, missing `lang` attr |
| **MEDIUM** | Standard not met, degrades quality | web-font dependency (offline break), thin sections (<3 entries), no Quick Reference block, no Common Mistakes section, undated volatile facts, JS not deferred |
| **LOW** | Modernization / polish | Bootstrap collapse instead of native `<details name>`, no `light-dark()` theming, no container queries, missing `text-wrap` niceties |

LOW items are only worth fixing opportunistically while editing the file anyway, or during
a deliberate modernization pass — do not churn a healthy page for them.

## 3. Automated checks (run these verbatim)

All from repo root, with `FILE=<name>.html`:

```bash
BASE="${FILE%.html}"

# A. Metadata presence
grep -c 'application/ld+json' "$FILE"                      # expect ≥1
grep -ciE 'last verified|last updated' "$FILE"             # expect ≥1
grep -o 'rel="canonical" href="[^"]*"' "$FILE"             # expect .../$FILE exactly
head -3 "$FILE" | grep -io '<html[^>]*lang="[a-z-]*"'      # expect lang="en"
grep -c 'name="twitter:card"' "$FILE"                      # expect ≥1

# B. og:image — must point at images/$BASE.png and the file must exist
grep -oE '<meta[^>]*og:image[^>]*>' "$FILE" | head -2      # eyeball: real URL, right file
ls "images/$BASE.png"                                      # must exist
grep -inE 'YOUR_IMAGE|yourdomain|placeholder|example\.com|TODO|FIXME' "$FILE"  # expect none

# C. CDN hygiene — every CDN <link>/<script> needs SRI; Bootstrap pinned to 5.3.8
grep -cE 'cdn\.jsdelivr|cdnjs|unpkg' "$FILE"               # count CDN tags…
grep -c 'integrity="sha384' "$FILE"                        # …must EQUAL the CDN tag count
grep -o 'bootstrap@[0-9.]*' "$FILE" | sort -u              # expect only bootstrap@5.3.8
grep -o 'bootstrap-icons@[0-9.]*' "$FILE" | sort -u        # expect only @1.13.1
grep -cE 'fonts\.googleapis|fonts\.gstatic' "$FILE"        # 0 = clean; >0 = MEDIUM finding

# D. Internal links — every relative .html href must exist
grep -o 'href="[a-z0-9_-]*\.html"' "$FILE" | sed 's/href="//;s/"//' | sort -u \
  | while read t; do [ -f "$t" ] || echo "BROKEN: $t"; done

# E. Site integration
grep -c "'$FILE'" index.php                                # expect 1 ($categoryMap entry)

# F. JS delivery
grep -oE '<script[^>]*src=[^>]*>' "$FILE" | grep -v defer  # expect empty (all deferred)
```

SRI note: use the precomputed hashes in `AGENTS.md` (Tech Baseline → Cached CDN dependencies) for Bootstrap 5.3.8 / Icons 1.13.1.
For any *other* CDN asset, compute from real bytes
(`curl -sL <url> | openssl dgst -sha384 -binary | openssl base64 -A`) — never recall a hash.

## 4. Manual content checks (read the page)

Apply the AGENTS.md Testing Checklist's comprehensiveness half, as an auditor:

1. **Coverage contract** — fundamentals + working knowledge + edge/advanced all present?
   Any hollow section (heading with <3 substantive entries)?
2. **Atomic entry rule** — spot-check 5 entries: definition + concrete example + gotcha?
   Vague qualifiers ("fast", "expensive") where a number belongs?
3. **Quick Reference block** near the top? **Common Mistakes** section (mandatory for
   technical topics)?
4. **Self-containment test** — could a practitioner work from this page alone?
5. **JSON-LD truthfulness** — does the schema describe what's visibly on the page? Is
   `dateModified` plausible against `git log -1 --format=%cs -- "$FILE"`?
6. **Volatile facts dated?** Don't verify the facts (freshness job's work) — check they
   carry `as of <Mon YYYY>` tags so staleness is *visible*.
7. **Cross-links** — does the page link its cluster (per `SEO_PROMPT.txt` groupings), and
   do related pages link back?

**Word-count caution:** app-like pages (calculators, `human-skeleton.html`,
`command-deck.html`, `p-doom-*`) legitimately have little HTML text — their content lives in
JS data. Judge them by rendered output in a browser, not by markup volume. For article-style
pages, under ~1,500 words of body text is a thinness signal worth a closer look.

## 5. Browser checks (per AGENTS.md Build & Verify)

Serve locally (`python3 serve.py` or `nohup python3 -m http.server 8765 &`) and load the page:

- Console clean (favicon 404 is the only acceptable error). **If SRI was added/changed this
  run, this check is mandatory** — a wrong hash silently blocks the asset:
  `typeof window.bootstrap !== 'undefined'`.
- Interactive elements work: checkboxes persist to `localStorage`, copy buttons map to their
  blocks, sorting sorts.
- 375 px wide: no horizontal scroll, tables wrapped in `overflow-x: auto`.
- Both themes if the page has a toggle; `prefers-reduced-motion` honored.
- Print preview: sane output (mandatory-print pages must look deliberate).
- Works with JS disabled: content visible, native `<details>` still opens.

## 6. Fix policy

**Fix in place this run (BLOCKER + HIGH, and cheap MEDIUMs):**
- Placeholder/wrong og:image → point at `images/$BASE.png`; generate the image if missing
  (1200×630 per AGENTS.md; `generate-image-previews.py` is the batch fallback).
- Missing JSON-LD → add the standard `TechArticle` block, describing only what's on the page.
  Set `datePublished` from `git log --diff-filter=A --format=%cs -- "$FILE"`.
- Missing `Last verified` → add the footer line **only after actually reviewing the page this
  run** (which an audit does). Match the muted footer style.
- Bootstrap 5.3.2/5.3.3 → bump to 5.3.8 + Icons 1.13.1 with the AGENTS.md SRI hashes; add
  `defer`. Then run the browser check — old pages occasionally use removed/renamed behaviors.
- Missing SRI on existing CDN tags → add computed hashes + `crossorigin="anonymous"`.
- Broken internal links → remove the link or retarget to an existing page (do NOT create the
  missing page; note it as a possible spec candidate).
- Missing `$categoryMap` entry → add to `index.php`, reusing an existing category label.
- Missing `lang`, missing `defer`, missing twitter:card → add.

**Flag, don't fix (report for a separate decision):**
- Web-font removal on pages whose visual identity depends on the font — swapping to a system
  stack changes the design; batch this as its own pass per affected page.
- Thin content / missing sections / no Quick Reference → these need real research and
  writing. Verdict: **REGENERATE** (full rebuild against AGENTS.md) or **EXPAND** (targeted
  sections). A pre-SRI-era page failing multiple content checks is usually cheaper to
  regenerate than to patch.
- Stale facts → hand to the freshness job (`weekly-freshness-update.md`), don't duplicate it.
- LOW-tier modernization → note it; only do it if you're already editing nearby.

## 7. Report format

```
### <filename> — verdict: PASS | FIXED | FIXED+FLAGS | REGENERATE
**Blockers/High found:** bullets, each with the fix applied (old → new)
**Medium/Low found:** bullets, fixed or flagged
**Content assessment:** 2-3 sentences against §4 (coverage, density, self-containment)
**Flags for other jobs:** stale facts → freshness; font swap → design pass; missing page → spec idea
**Browser check:** clean console y/n, mobile y/n, no-JS y/n, print y/n
```

Keep a running log (append per file) so the systematic pass has a paper trail of what's done.

---

## Appendix — corpus baseline, 2026-07-04 (101 files)

Re-derive with the §3 commands before trusting these lists — the repo moves. Counts and
lists below are the audit-priority queue as of the scan date.

**Placeholder/broken og:image (BLOCKER):** `bitcoin-whitepaper.html`
(`YOUR_IMAGE_URL_HERE/...`), `compression-algorithms.html` (`yourdomain.com/...`),
`etz-chaim-tree-of-life.html` (`etz-chaim-placeholder.png`). Several others point at
non-convention filenames (e.g. `brazilian-jiu-jitsu.html` → a `.jpg` header image,
`git-scm.html`/`versioncontrol.html` → `-preview.png` names) — verify each target exists;
non-existent target = BLOCKER, existing-but-nonstandard = LOW.

**Broken internal links (BLOCKER):** `automotive-innovation-timeline.html` and
`engineering-metals-selection.html` both link `anduril-products.html`, which does not exist.

**Missing JSON-LD (HIGH, 32 files):** ai-progress-dashboard, airisk, aisafety,
anapanasati-mindfulness-of-breathing, ashihara-karate, bitcoin-exchanges-cards,
bitcoin-self-custody-guide, bitcoin-wallet, bitcoin-whitepaper, brazilian-jiu-jitsu,
compression-algorithms, conscious-leadership-contexts, cooking-guide, currency-timeline,
databases, emergency-radio-card, human-evolution, human-skeleton, judo, leadership,
living-richly-guide, medical-school-curriculum, modern-devops-pipelines, objectivism,
p-doom-test-harness, post-quantum-cryptography, postgresql, scrum,
shabbat-services-cheatsheet, versioncontrol, weightloss-cheatsheet,
yudkowsky-rationality-ai-cheatsheet.

**Missing `Last verified`/`last updated` (HIGH, 33 files):** anapanasati, art-of-war-sun-tzu,
ashihara-karate, bitcoin-whitepaper, brazilian-jiu-jitsu, buddhism, capitalism, command-deck,
conscious-leadership-contexts, cooking-guide, currency-timeline, cycling,
emergency-radio-card, global_cuisine_guide, hot-tub-treatment, human-evolution,
human-skeleton, islam, israel-history, judaism, judo, leadership, living-richly-guide,
martial-arts-cheatsheet, medical-school-curriculum, military-aphorisms, objectivism,
p-doom-test-harness, running, scrum, shabbat-services-cheatsheet, weightloss-cheatsheet,
yudkowsky-rationality-ai-cheatsheet. (Mostly evergreen topics — the stamp still belongs;
see freshness doc §7–8.)

**CDN without any SRI (HIGH, 30 files):** ai-risk-timeline, anapanasati, aws-vs-azure,
bitcoin-whitepaper, capitalism, command-deck, currency-timeline, cycling,
emergency-radio-card, global_cuisine_guide, google-ai-studio-guide, hot-tub-treatment,
human-skeleton, humanoid-robots, islam, judaism, living-richly-guide,
martial-arts-cheatsheet, medical-school-curriculum, military-aphorisms, operator-loadouts,
p-doom-test-harness, postgresql, privacy-data-broker-opt-out, running, scrum,
shabbat-services-cheatsheet, tesla-products, weightloss-cheatsheet,
yudkowsky-rationality-ai-cheatsheet. Additional files have *partial* SRI (some tags hashed,
some not) — the §3C count comparison catches them.

**Bootstrap version spread (HIGH where old):** 5.3.8 (current pin), 5.3.3 (~69 tag
references across older files), 5.3.2 (4 references). Any non-5.3.8 file gets the bump+SRI
treatment in §6.

**Missing from `$categoryMap` (HIGH, 8):** anatta-not-self, buddhist-work-leadership,
craving-desire-habit-loops, data-center-myths, five-hindrances-debugger,
right-speech-modern-life, satipatthana-four-foundations, stellar-lifecycle. (The Buddhism
cluster suggests adding one category label once, not eight ad-hoc decisions.)

**Missing preview image (HIGH, 5):** buddhist-work-leadership, craving-desire-habit-loops,
five-hindrances-debugger, right-speech-modern-life, satipatthana-four-foundations — the
recent uncommitted batch; generate at 1200×630 before their commits.

**Web-font dependency (MEDIUM, 38 files):** flag per §6; batch the swaps as a design pass.

**Missing `lang` (HIGH, 1):** martial-arts-cheatsheet.

**Clean across the corpus:** every file has a correct canonical URL and a viewport meta —
no action needed on those dimensions.
