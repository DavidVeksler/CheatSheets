# Cheatsheet Audit: per-file conformance procedure

Audit **one shipped cheatsheet per run** against current standards; bring it up to standard or explicitly accept a legacy exception, never silently skip.

- `AGENTS.md` owns the quality bar; this audit applies it, never redefines it.
- `weekly-freshness-update.md` owns fact drift and `refresh-status.json`. This audit does not re-verify facts or touch that file; it only checks volatile facts are dated inline. Hand stale facts to the freshness job.
- `TODO/SPEC-AUDIT.md` is for future-page specs; not used here.

---

## 1. Execution model

- **One file per run.** `FILE` = the cheatsheet path. Touch only `FILE` (plus `category-map.php`
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
| **BLOCKER** | Visibly broken or lying to users/crawlers | placeholder URLs (`YOUR_IMAGE_URL_HERE`, `yourdomain.com`), broken internal links, JSON-LD describing content not on the page |
| **HIGH** | Violates a hard AGENTS.md requirement | missing JSON-LD, a visible "Last verified" line or JSON-LD `dateModified` (remove, never add), CDN tags without SRI, unpinned/old Bootstrap, missing `$categoryMap` entry, missing preview image, missing `lang` attr |
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
grep -ciE 'last verified|last updated|dateModified' "$FILE"  # expect 0
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
grep -c "'$FILE'" category-map.php                         # expect 1 ($categoryMap entry)

# F. JS delivery
grep -oE '<script[^>]*src=[^>]*>' "$FILE" | grep -v defer  # expect empty (all deferred)
```

SRI note: `<link rel="preconnect">` needs no SRI. Use the precomputed hashes in `AGENTS.md` (*Tech baseline*) for Bootstrap 5.3.8 / Icons 1.13.1.
For any *other* CDN asset, compute from real bytes
(`curl -sL <url> | openssl dgst -sha384 -binary | openssl base64 -A`) — never recall a hash.

## 4. Manual content checks (read the page)

Apply AGENTS.md > *Generation & quality protocol* as an auditor:

1. **Coverage contract** — fundamentals + working knowledge + edge/advanced all present?
   Any hollow section (heading with <3 substantive entries)?
2. **Atomic entry rule** — spot-check 5 entries: definition + concrete example + gotcha?
   Vague qualifiers ("fast", "expensive") where a number belongs?
3. **Quick Reference block** near the top? **Common Mistakes** section (mandatory for
   technical topics)?
4. **Self-containment test** — could a practitioner work from this page alone?
5. **JSON-LD truthfulness** — does the schema describe what's visibly on the page? No
   `dateModified` field at all.
6. **Volatile facts dated?** Don't verify the facts (freshness job's work) — check they
   carry `as of <Mon YYYY>` tags so staleness is *visible*.
7. **Cross-links** — does the page link its cluster (per `SEO_PROMPT.txt` groupings), and
   do related pages link back?

**Word-count caution:** app-like pages (calculators, `human-skeleton.html`,
`command-deck.html`, `p-doom-*`) legitimately have little HTML text — their content lives in
JS data. Judge them by rendered output in a browser, not by markup volume. For article-style
pages, under ~1,500 words of body text is a thinness signal worth a closer look.

## 5. Browser checks (see `docs/content.md` > *Local QA*)

Serve locally (`python3 -m http.server 8765`) and load the page:

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
- Missing JSON-LD → add the standard `TechArticle` block (no `dateModified` field), describing
  only what's on the page. Set `datePublished` from `git log --diff-filter=A --format=%cs -- "$FILE"`.
- Visible "Last verified" line or JSON-LD `dateModified` → **remove it** (delete a
  self-contained stamp element outright; if it's one clause among others, drop just the clause
  and fix the surrounding punctuation).
- Bootstrap 5.3.2/5.3.3 → bump to 5.3.8 + Icons 1.13.1 with the AGENTS.md SRI hashes; add
  `defer`. Then run the browser check — old pages occasionally use removed/renamed behaviors.
- Missing SRI on existing CDN tags → add computed hashes + `crossorigin="anonymous"`.
- Broken internal links → remove the link or retarget to an existing page (do NOT create the
  missing page; note it as a possible spec candidate).
- Missing `$categoryMap` entry → add to `category-map.php`, reusing an existing category label.
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

## Appendix: corpus baseline, 2026-09-22 (204 root `.html`)

Re-derive with the §3 commands before trusting; the repo moves.

- **Clean corpus-wide:** JSON-LD present, no "Last verified" stamps, no JSON-LD `dateModified` (one prose mention in `how-its-built.html` is not a field), all Bootstrap tags at 5.3.8, every file in `$categoryMap`, every file has `images/<name>.png`, `lang` set, no placeholder og:images, no broken relative `.html` links. Canonical and viewport were already clean.
- **CDN without SRI (HIGH):** `human-evolution.html` (Leaflet 1.9.4 CSS + JS from unpkg), `weightloss-cheatsheet.html` (`leader-line-new@1.1.9`).
- **Web-font dependency (MEDIUM, 41 files):** flag per §6; batch swaps as a design pass.
