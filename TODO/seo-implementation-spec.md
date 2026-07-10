# SEO implementation spec — metadata pass

**Derived from:** [`seo-audit-2026-07-09.md`](seo-audit-2026-07-09.md) · **Created:** 2026-07-09
**Status:** ready to execute · **Scope:** work packages WP1–WP6 below.

This spec is binding. Where it conflicts with habit, follow the spec. Where it conflicts with
[`AGENTS.md`](../AGENTS.md), stop and ask.

---

## Hard rules (read before touching a file)

1. **Metadata only.** Do not change visible body content, CSS, JS, or layout. The one exception is
   WP5 (`<h1>` fixes), which is explicitly scoped.
2. **Preserve the existing attribute order.** These files use `content="…" name="description"`
   (reversed). Match the file's local style; do not "normalise" it. A find-and-replace that assumes
   `name=` comes first will silently miss the tag.
3. **JSON-LD must match visible content** (`AGENTS.md`, Accuracy Protocol). If you change a page's
   description, update JSON-LD `description` to match. Never let them drift.

   > **Corrected 2026-07-09.** This rule originally said `headline` must equal the `<title>`. That is
   > wrong. `headline` is the *article's* headline and should track the page's visible `<h1>`;
   > `<title>` is the *SERP listing* and is legitimately shorter and more keyword-led. Forcing them
   > equal would have made ~9 pages' `headline` diverge from their own visible `<h1>` — the exact
   > thing the Accuracy Protocol forbids. **Standard: `headline` ≈ visible `<h1>`; leave it alone when
   > it already does.**
4. **Never invent dates.** For `datePublished` / `dateModified`, derive from git:
   ```bash
   git log --diff-filter=A --format=%ad --date=short -- <file> | tail -1   # datePublished
   git log -1 --format=%ad --date=short -- <file>                          # dateModified
   ```
5. **Do not touch** `index.php`, `sitemap.php`, `robots.txt`, `.htaccess`, or any server config.
6. **Character budgets are hard limits**, not targets. Titles **≤ 60**. Descriptions **150–200**
   (the band `AGENTS.md` specifies). When *writing a new* description, aim for 150–160; when a
   description already sits anywhere in 150–200, **leave it alone** — it conforms.
   Verify with the script in "Acceptance gate" below — do not eyeball them.

   > **Corrected 2026-07-09.** An earlier revision of this spec set a 150–160 hard band, which
   > contradicts `AGENTS.md` and would have flagged ~65 conforming files as failures. The gate script
   > below now enforces 150–200.

7. **Never assert a fact about a page you have not read.** Titles and descriptions are content
   claims, and `AGENTS.md`'s Accuracy Protocol governs them: no fabricated counts, no naming an
   entity the page doesn't cover. If proposed text names "68 throws", "20+ styles", or a specific
   technology, **verify it against the page body first**. If it's wrong, reject the text and report
   it — do not ship it, and do not quietly invent a replacement claim either.
7. **Commit per work package**, not per file. Message format: `SEO: <what> (WP<n>)`, ending with the
   `Co-Authored-By` trailer. **Do not push.** Do not stage `.claude/` or unrelated changes.
8. If a page's proposed title would lose a term it currently ranks for, **stop and flag it** rather
   than shipping the change.

---

## Status (updated 2026-07-09)

- **WP1 — done**, commit `4a8383b`. 15 of 16 files changed. **5 of the 16 proposed descriptions were
  rejected as factually wrong against the page body** and reverted by the implementer (see the
  post-mortem note under WP1's table). `judo.html` and `databases.html` titles were subsequently
  rewritten by hand in `51abbba`.
- **WP2 — done**, commit `04252ad`. 70 files (the spec's "66" was arithmetic error; real overlap with
  WP1 was 12, not 16).
- **WP3 — done**, commit `42727af`. 55 files.
- **WP4, WP5, WP6 — not started.**
- `autonomous-defense-systems.html` was added by a concurrent session *after* the audit snapshot and is
  **outside this spec's 151-file corpus**. Do not touch it. It currently has a 75-char title and a
  214-char description; fold it into a later pass.

## WP1 — Rewrite titles + descriptions for the 16 highest-impression pages

These 16 pages carry ~85% of site impressions. Each rewrite below is **grounded in that page's actual
Search Console queries** (180-day window). Apply verbatim — the character counts are pre-validated.

For each file, update **four** places so they stay consistent:
- `<title>`
- `<meta name="description">`
- `<meta property="og:title">` and `<meta name="twitter:title">` → set to the new `<title>`
- `<meta property="og:description">` and `<meta name="twitter:description">` → set to the new description
- JSON-LD `headline` → new title; JSON-LD `description` → new description; `dateModified` → today (`2026-07-09`)

> `og:title` may keep a longer, more expressive variant if one already exists **only** where the
> existing one is clearly better for social sharing. When in doubt, mirror the `<title>`.

| File | New `<title>` (≤60) | New `<meta description>` (150–160) |
|---|---|---|
| `ai-frontier.html` | `Frontier AI Companies & Labs: Complete List of Models (2026)` | `Every frontier AI lab and model as of 2026: OpenAI, Anthropic, Google DeepMind, xAI, Meta, Mistral, DeepSeek. Philosophy, funding, products, and AGI goals.` |
| `orbital-rockets-comparison.html` | `Rocket Size Comparison: Starship, New Glenn, Falcon Heavy` | `Compare Starship, New Glenn, Falcon Heavy, Falcon 9, Ariane 6, Vulcan and Long March 5 side by side: payload to LEO, height, thrust, reuse, cost and status.` |
| `humanoid-robots.html` | `Humanoid Robots 2026: Every Company, Robot and Spec Compared` | `Optimus, Figure 03, Atlas, Digit, Unitree and more: height, payload, battery, actuators, price and ship date for every humanoid robot program, updated 2026.` |
| `tesla-products.html` | `Tesla Products & Specs: Every Model, Battery and Platform` | `Full Tesla lineup specs: Model 3, Y, S, X, Cybertruck, Semi, Roadster and Optimus. Battery chemistry, range, drivetrain, platform and pricing in one table.` |
| `judo.html` | `Judo Guide: All Throws, Groundwork and Core Principles` | `A complete judo reference: all 68 Kodokan throws by group, pins, chokes, armlocks, kuzushi and tactics, with belt-rank syllabus and common beginner mistakes.` |
| `ashihara-karate.html` | `Ashihara Karate: Sabaki, Strikes and Kata Cheatsheet` | `Ashihara karate reference: the sabaki circular-movement system, strikes, blocks, kicks, and all kata by belt rank, with drills and a trackable syllabus.` |
| `operator-loadouts.html` | `Special Forces Loadouts & EDC Gear: SWAT, Operators, Medics` | `Real loadouts by role: SWAT entry, special forces, paramedic and EDC. Plate carriers, optics, rifles, medical kits and weights, itemised with tradeoffs.` |
| `google-ai-studio-guide.html` | `Google AI Studio Settings: Temperature, Top-P & Advanced` | `Every Google AI Studio setting explained: temperature, top-p, top-k, stop sequences, safety filters, system instructions, and when to change each default.` |
| `martial-arts-cheatsheet.html` | `Martial Arts Cheatsheet: Styles, Techniques and Comparison` | `Compare 20+ martial arts: striking, grappling, weapons and hybrid styles. Origins, ruleset, signature techniques, and which one to train for your goal.` |
| `postgresql.html` | `PostgreSQL Cheat Sheet: Commands, Tuning and Advanced SQL` | `PostgreSQL reference for DBAs and developers: psql commands, indexing, EXPLAIN plans, vacuum, replication, window functions, JSONB and performance tuning.` |
| `javascript-for-architects.html` | `JavaScript for Architects: Modern JS, React & Ecosystem` | `Modern JavaScript for architects: ES2026 syntax, async patterns, React and framework tradeoffs, bundlers, testing, and the decisions that outlive frameworks.` |
| `clean-architecture-dotnet.html` | `.NET Clean Architecture: Layered Web API Cheat Sheet` | `Clean Architecture in .NET Web API: domain, application, infrastructure and API layers, dependency rules, CQRS, EF Core placement and testing strategy.` |
| `compression-algorithms.html` | `Compression Algorithms Compared: Codecs, Ratios, Tradeoffs` | `Compare gzip, zstd, brotli, LZ4, xz, AV1 and more: compression ratio, speed, memory, and when each codec wins. Lossless and lossy, with real benchmarks.` |
| `bitcoin-whitepaper.html` | `Bitcoin Whitepaper Explained: A Plain-English Guide` | `Satoshi's Bitcoin whitepaper section by section: transactions, proof-of-work, SPV, incentives and privacy, with plain-English notes and modern protocol context.` |
| `anapanasati-mindfulness-of-breathing.html` | `Anapanasati: The 16 Steps of Mindfulness of Breathing` | `The Anapanasati Sutta's 16 steps across its four tetrads, with posture, practice instructions, common obstacles, and how each step maps to the four jhanas.` |
| `databases.html` | `Database Comparison: SQL vs NoSQL vs NewSQL Cheat Sheet` | `Compare relational, document, key-value, graph, column and vector databases: consistency, scaling, query model, and which workload each one actually fits.` |

> **Rationale, so you can sanity-check each edit:** every new title front-loads the exact noun phrase
> users type. `ai-frontier` gains *companies / labs / list*; `judo` gains *guide*;
> `operator-loadouts` gains *special forces*; `google-ai-studio-guide` gains *settings* and drops the
> meaningless *Enhanced*; `orbital-rockets-comparison` gains *size* and the *vs* pairings.

`databases.html` and `bitcoin-whitepaper.html` also appear in later work packages — do WP1's rewrite
first, then let WP4 read the *new* title when it generates JSON-LD.

### ⚠️ Post-mortem: 5 of the 16 rows above were factually wrong

The table was written from the Search Console query data **without reading the page bodies**. Five
proposed descriptions asserted things the pages do not contain. The implementing agent verified each
against the source and **correctly refused all five**:

| File | Fabricated claim | Reality |
|---|---|---|
| `judo.html` | "all 68 Kodokan throws" | Page presents a *selection* from the Gokyo no Waza (~17 throws) and explicitly says "Many more exist." |
| `databases.html` | "NewSQL" | No NewSQL section; taxonomy is SQL / NoSQL & Search / Modern Engines. |
| `martial-arts-cheatsheet.html` | "Compare 20+ martial arts" | Page covers **9** styles; its own JSON-LD already said so. |
| `compression-algorithms.html` | names "LZ4" | LZ4 appears nowhere on the page. |
| `anapanasati-mindfulness-of-breathing.html` | "how each step maps to the four jhanas" | Jhāna is mentioned only in passing; no step-to-jhāna mapping exists. |

All five were verified independently against the source afterwards — every rejection was correct.

**The lesson, which now lives in Hard Rule 7:** a `<title>` and a `meta description` are content
claims and fall under `AGENTS.md`'s Accuracy Protocol ("never fabricate a plausible-looking number";
"structured data must match visible content"). Search-intent data tells you *which words to rank for*,
never *what the page says*. Read the page before you describe it. An agent that ships spec text
verbatim without checking it against the body is doing the wrong job.

---

## WP2 — Trim the remaining 66 over-long titles to ≤60 characters

**Target:** every one of the 82 files whose `<head>` `<title>` exceeds 60 chars, **minus** the 16
handled in WP1. Get the live list by running the audit script in "Acceptance gate".

**Method — delete filler, never delete the topic.** Remove, in this order, until ≤60:

1. Trailing brand: `| David Veksler Cheatsheets`, `| git-scm`
2. Parenthetical process notes: `(Printable & Trackable)`, `(Detailed & …)`, `(List & Map)`
3. Empty intensifiers: `Ultimate Guide to`, `The Complete`, `Comprehensive`, `Enhanced`,
   `A Guide to`, `Interactive` (**only** when the interactivity isn't the page's actual hook)
4. Redundant `Cheatsheet` / `Cheat Sheet` when the title already says `Guide`, `Reference`, or `Compared`
5. The least-searched trailing clause after the final `&` or `,`

**Never remove:** the primary topic noun, a version/year that users search (`2026`), a
disambiguating qualifier (`.NET`, `UV-5R`, `Technician`), or a term the page currently ranks for.

Worked examples:

| File | Before (len) | After (len) |
|---|---|---|
| `databases.html` | `Database Comparison Cheatsheet: Interactive Guide to SQL, NoSQL, Modern…` (99) | *(handled in WP1)* |
| `hot-tub-treatment.html` | `Hot Tub Treatment: Water Chemistry, Sanitizer Strategy, and Pseudomonas…` (83) | `Hot Tub Water Chemistry: Sanitizers & Pseudomonas` (48) |
| `versioncontrol.html` | `Interactive Cheatsheet: Modern Version Control (Git, Mercurial) & Hosting…` (83) | `Modern Version Control: Git, Mercurial & Hosting` (47) |
| `dotnet-cheatsheet.html` | `.NET and C# Cheatsheet: SDK, ASP.NET Core, EF Core, MAUI, Aspire and A…` (81) | `.NET & C# Cheatsheet: SDK, ASP.NET Core, EF Core, MAUI` (53) |
| `linux-server-hardening.html` | `Linux Server Hardening & Sysadmin: Interactive Checklist + Paste-R…` (79) | `Linux Server Hardening: Checklist & Paste-Ready Commands` (55) |
| `leadership.html` | `The 15 Commitments of Conscious Leadership Cheatsheet (Detailed & …)` (77) | `The 15 Commitments of Conscious Leadership` (41) |

If you cannot get a title under 60 without losing the topic, **leave it and list it in the summary**
rather than mangling it.

Keep `og:title` / `twitter:title` / JSON-LD `headline` in sync (rule 3).

---

## WP3 — Trim 52 over-long descriptions to 150–160 characters

**Target:** every file whose `meta description` exceeds 200 chars. Live list from the audit script.

**Method:** the first sentence states what the page *is* and carries the primary keyword. The second
gives a concrete reason to click — name the specific things covered (real entity names, real numbers),
not adjectives. Cut trailing throat-clearing (`Updated July 2026.`, `Learn everything about…`).

Also fix the **10 descriptions under 150 chars** by extending them with specifics the page genuinely
covers — do not pad with adjectives, and do not describe content that isn't on the page (rule 3).

Sync `og:description` / `twitter:description` / JSON-LD `description`.

---

## WP4 — Add `TechArticle` JSON-LD to the 21 pages missing it

Exact list (verified 2026-07-09):

```
ai-progress-dashboard.html      airisk.html                     aisafety.html
bitcoin-exchanges-cards.html    bitcoin-self-custody-guide.html conscious-leadership-contexts.html
cooking-guide.html              currency-timeline.html          databases.html
emergency-radio-card.html       human-evolution.html            human-skeleton.html
living-richly-guide.html        medical-school-curriculum.html  modern-devops-pipelines.html
objectivism.html                p-doom-test-harness.html        post-quantum-cryptography.html
scrum.html                      versioncontrol.html             weightloss-cheatsheet.html
```

Insert immediately before `</head>`, using the template from `AGENTS.md`:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "TechArticle",
  "headline": "<the page's final <title>, after WP1/WP2>",
  "description": "<the page's final meta description>",
  "author": {"@type": "Person", "name": "David Veksler (AI Generated)"},
  "publisher": {"@type": "Organization", "name": "David Veksler Cheatsheets"},
  "datePublished": "<git first-commit date>",
  "dateModified": "<git last-commit date, or 2026-07-09 if you edited it this pass>",
  "keywords": "<reuse the page's existing meta keywords verbatim>"
}
</script>
```

- `headline` and `description` **must** match the final visible title/description. Run WP4 **after**
  WP1 and WP2 so you copy the settled values.
- Do **not** add `FAQPage` or `HowTo` schema (`AGENTS.md`, Discoverability).
- Three of these pages (`ai-progress-dashboard`, `emergency-radio-card`, `p-doom-test-harness`) have
  **no meta description at all**. Write one (150–160 chars) describing what's actually on the page,
  add it as a `meta description` too, then use it in the JSON-LD.

---

## WP5 — Fix `<h1>` defects (3 files)

- `aisafety.html` — no `<h1>`. Promote the existing top-level visible heading to `<h1>`, or add one
  matching the page title. Do not add a heading that isn't visually present.
- `human-skeleton.html` — no `<h1>`. Same treatment.
- `javascript-for-architects.html` — **two** `<h1>` elements. Keep the first; demote the second to
  `<h2>`. Verify the heading order stays sequential (no `h2 → h4` jumps introduced).

This is the only WP permitted to touch body markup, and only these three files.

---

## WP6 — Add `/llms.txt`

Create `llms.txt` at the repo root. `AGENTS.md` lists this as optional; the audit found substantial
AI-crawler-shaped traffic, so it's worth having.

Format: a short site summary, then a flat list of the cheatsheets grouped by the categories already
defined in `index.php`'s `$categoryMap`, each as `- [Title](https://cheatsheets.davidveksler.com/file.html): one-line description`.

Generate it **from the files** (read each page's final `<title>` and `meta description`) — do not
hand-write entries from memory. A small Python script that walks `*.html` and reads `category-map.php`
is the right approach; leave the script out of the commit unless it's genuinely reusable.

---

## Acceptance gate — run this before committing anything

Save as `/tmp/seo_check.py` (do not commit it) and run from the repo root. **All checks must pass**
except the explicitly-allowed exceptions you list in your summary.

```python
from html.parser import HTMLParser
import glob, json, sys

class Head(HTMLParser):
    """Parse only the document <title>/meta/link inside <head>.
    Scoped to <head> because inline SVG <title> elements otherwise pollute the result."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.inhead = self.done = self._intitle = False
        self.title = None; self._t = []
        self.meta = {}; self.prop = {}; self.canon = None
    def handle_starttag(self, tag, attrs):
        if self.done: return
        a = dict(attrs)
        if tag == 'head': self.inhead = True
        elif tag == 'body': self.inhead = False; self.done = True
        elif not self.inhead: return
        elif tag == 'title' and self.title is None: self._intitle = True; self._t = []
        elif tag == 'meta':
            if a.get('name'): self.meta.setdefault(a['name'].lower(), a.get('content', ''))
            if a.get('property'): self.prop.setdefault(a['property'].lower(), a.get('content', ''))
        elif tag == 'link':
            r = a.get('rel'); r = ' '.join(r) if isinstance(r, list) else (r or '')
            if r.lower() == 'canonical' and not self.canon: self.canon = a.get('href', '')
    def handle_endtag(self, tag):
        if tag == 'title' and self._intitle:
            self._intitle = False; self.title = ' '.join(''.join(self._t).split())
        if tag == 'head': self.inhead = False; self.done = True
    def handle_data(self, d):
        if self._intitle: self._t.append(d)

fails = []
for f in sorted(glob.glob('*.html')):
    src = open(f, encoding='utf-8', errors='replace').read()
    p = Head(); p.feed(src)
    t = p.title or ''; d = p.meta.get('description', '')
    if len(t) > 60:            fails.append(f'{f}: title {len(t)} chars > 60')
    if not d:                  fails.append(f'{f}: no meta description')
    elif not 150 <= len(d) <= 200: fails.append(f'{f}: description {len(d)} chars, want 150-200')
    if not p.canon:            fails.append(f'{f}: no canonical')
    if 'application/ld+json' not in src: fails.append(f'{f}: no JSON-LD')
    # each ld+json block must parse INDEPENDENTLY (pages legitimately have 2-3 blocks)
    import re
    for i, b in enumerate(re.findall(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', src, re.S | re.I)):
        try: json.loads(b)
        except Exception as e: fails.append(f'{f}: ld+json block {i} invalid: {e}')

print(f'{len(fails)} failures')
for x in fails: print('  ', x)
sys.exit(1 if fails else 0)
```

Two subtleties this script encodes, both of which produced **false positives** on the first audit
pass — do not "simplify" them away:

- The parser is **scoped to `<head>`**, because inline SVG `<title>` elements otherwise get captured.
- Each `ld+json` block is validated **separately**; several pages legitimately carry two or three.

After the gate passes, spot-check three files by eye (`ai-frontier.html`, `judo.html`, one WP2 file)
to confirm `og:`/`twitter:`/JSON-LD really did stay in sync. The script does not check that.

---

## Out of scope — do not do these

- Server config (`410 Gone` for `anduril-products.html`) — awaiting David's decision.
- Contextual internal-linking pass — deferred to a second pass, after this one is measured.
- Cannibalization consolidation (`versioncontrol.html` vs `git-scm.html`, the buddhism trio, etc.) —
  requires per-goal judgment; **never** delete or merge a page in this pass.
- Any body-content edit outside WP5.
- `git push` / deploy.

---

## Deliverable

A short written summary containing:
1. Per-WP: files changed, and the acceptance-gate result.
2. Any title you could **not** get under 60 chars without losing meaning, and why.
3. Any page where the spec's proposed text looked wrong against the page's real content — flag it,
   don't silently "fix" it.
4. The commit SHAs (one per WP). **Not pushed.**
