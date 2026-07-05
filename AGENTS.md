# AGENTS.md

Cross-agent guidance for this repository. Read by Claude Code, Codex, and Cursor. If a tool needs its own file, point it here (`CLAUDE.md` → this file; `.cursorrules` → this file) so the standard lives in one place.

## Project Overview

A collection of interactive, standalone HTML cheatsheets covering technology, finance, philosophy, AI safety, crypto, martial arts, and more. Each file is a self-contained reference guide.

The defining quality bar is **comprehensiveness plus accuracy**. A cheatsheet here is a *terminal reference*: a competent practitioner should be able to do real work from a single page for the topic's common cases without opening another tab. Density and correctness win over brevity. The Content Comprehensiveness Standard and the Accuracy & Freshness Protocol below are hard acceptance criteria, not style suggestions.

## Repository documents (what governs what)

This file owns the quality bar. The other Markdown docs divide the workflows — use the right one for the task:

| Document | Use it when |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | Entry point → this file; also holds the **precomputed SRI hash table** for pinned CDN assets. |
| [`TODO/README.md`](TODO/README.md) | **Building a cheatsheet from a spec** in `TODO/` — binding implementation rules (numbers-are-anchors, outline-first, definition of done, design execution). |
| `TODO/<topic>.md` | One spec per planned cheatsheet (content angle, sections, visual identity). Deleted after the build ships. |
| [`TODO/SPEC-AUDIT.md`](TODO/SPEC-AUDIT.md) | **Writing or reviewing a spec** — spec-completeness criteria (search targeting, reader outcome, staleness register, etc.). |
| [`TODO/CHEATSHEET-AUDIT.md`](TODO/CHEATSHEET-AUDIT.md) | **Reviewing an existing/shipped cheatsheet** — run this per-file conformance audit (metadata, SRI, content depth, site integration), with severity tiers, fix policy, and the corpus defect baseline. |
| [`weekly-freshness-update.md`](weekly-freshness-update.md) | The scheduled **fact-drift job** — worker instructions for refreshing one dated cheatsheet per run. Owns fact verification; the audit above only checks the freshness *machinery* exists. |
| [`Device Cheat Sheet Generator.md`](Device%20Cheat%20Sheet%20Generator.md) | Standalone generator prompt for hardware/device guides (radios, appliances, tools). Predates this file — where they conflict, this file wins. |
| [`README.md`](README.md) | Public repo readme (minimal). |
| [`.github/copilot-instructions.md`](.github/copilot-instructions.md) | GitHub Copilot's summary of this repo. Duplicates rather than points here, so it drifts (e.g. it still says Bootstrap 5.3.3) — treat this file as authoritative; sync that one when touching it. |

Non-Markdown but load-bearing: `SEO_PROMPT.txt` (footer cross-linking procedure), `PROMPT2.txt` (legacy generator prompt).

## Generation Protocol (read first)

1. **Effort = High** (the Opus 4.8 default). Comprehensiveness comes from the spec in this file, not the effort dial — do not rely on Extra/Max to add coverage the spec already mandates. If a draft is thin, apply the standard harder.
2. **Research before writing.** For any version-sensitive, fast-moving, or specific factual content, verify against primary sources via web search first (see Accuracy & Freshness). AI-generated cheatsheets are exactly where hallucinated specifics creep in — close that gap up front.
3. **Outline to three depths, then fill** (see Coverage Contract). No section ships hollow.
4. **Self-verify against the Testing Checklist** before finishing. The model is expected to run its own output through the checklist, not assume it passed.

Treat the Coverage Contract, Atomic Entry Rule, and Accuracy Protocol as binding acceptance criteria. A cheatsheet that violates them is not done, regardless of polish.

## Content Comprehensiveness Standard (REQUIRED)

### Coverage contract — three depths
Every cheatsheet MUST cover its topic at three depths:
1. **Fundamentals** — definitions, mental model, the 20% that explains 80%.
2. **Working knowledge** — the syntax, commands, patterns, and decisions a practitioner uses daily.
3. **Edge & advanced** — gotchas, failure modes, performance characteristics, the things that trip up experienced people.

Any section in the outline MUST be fully populated. No placeholder stubs, no "TODO," no "see the docs." If a section can't be filled, cut or merge it.

### Atomic entry rule
Every entry (concept, command, pattern, term, technique) MUST include:
- A precise one-line definition or statement of purpose.
- At least one **concrete** example with realistic values — never `foo`/`bar` when a real value teaches more.
- Where applicable, a gotcha, pitfall, or explicit "when NOT to use this."

**Quantify everything quantifiable.** "Fast" → "~O(log n), sub-ms for n < 10⁶." "Expensive" → the actual price/token figure. "Large" → the actual cutoff. Real defaults, thresholds, limits, versions, complexity, latencies, rates.

### Breadth requirements (include when the topic supports them)
- **Comparison table** whenever 2+ alternatives exist — alternatives × decision criteria.
- **Explicit decision guidance** — "use X when…, use Y when…."
- **Common Mistakes / Anti-Patterns section** — MANDATORY for any technical topic.
- **Quick Reference block** near the top — the highest-frequency lookups in one scannable table (the cheat-within-the-cheat).
- Copy-paste-ready snippets, CLI flags, config keys with defaults, shortcuts where relevant.

### Density floor
Err toward over-inclusion: when uncertain whether an item belongs, include it. A finished cheatsheet should typically carry **20+ distinct substantive entries** and read as exhaustive for its scope. Any section with fewer than ~3 entries is either not a real section (fold it) or under-developed (expand it). **Thinness is a defect, not an aesthetic choice.**

### Self-containment test (run before finishing)
*"Could a competent practitioner do real work from this page alone for the common cases?"* If not, close the gap before shipping.

## Accuracy & Freshness Protocol (REQUIRED)

These cheatsheets are AI-generated and increasingly AI-consumed, so wrong specifics propagate. Hold the line:

- **Verify, don't recall.** Any version number, price, API signature, default, limit, benchmark, or date MUST be checked against a primary source (official docs, the spec, the vendor) before it goes in. If you can't verify it, omit it or flag the uncertainty explicitly — never fabricate a plausible-looking number.
- **Date volatile facts.** Tag anything that drifts with "as of <Mon YYYY>" or a version tag inline, so staleness is visible rather than silent.
- **Show freshness.** Include a visible `Last verified: YYYY-MM-DD` line in the page footer/header, and set `dateModified` in JSON-LD to the real edit date.
- **Structured data must match visible content** — never describe in schema what isn't on the page.
- **Prefer primary sources** over aggregators, SEO blogs, and forum posts.

## Tech Baseline

### Framework
- **Bootstrap 5.3.x — pin the current stable (5.3.8 as of 2026-06).** Bootstrap 6 is not yet stable; do not target it. Bootstrap is retained for visual consistency across the 47+ existing files — do not rip it out wholesale.
- Add **Subresource Integrity (`integrity` + `crossorigin`)** to all CDN `<link>`/`<script>` tags. Load JS with `defer`.
- Bootstrap Icons via CDN, pinned.

### Modern Platform Baseline (prefer these — all Baseline-supported in 2026)
Use native platform features over Bootstrap's JS wherever they're strictly better. Highest-value swaps:
- **Exclusive accordions: native `<details name="group">` + `<summary>`.** Zero JS, prints fully expanded-capable, works without JS, accessible by default. This replaces Bootstrap collapse for the core collapsible pattern — and satisfies the "works without JS" requirement for free.
- **Theming: `color-scheme` + the `light-dark()` CSS function**, honoring `prefers-color-scheme` automatically. Offer an optional manual override via `[data-theme]` (a tiny JS shim or `:has()`), not a hand-rolled dual stylesheet.
- **Layout: CSS Grid + container queries** for the card grid, so cards respond to their container, not just the viewport.
- **Specificity: wrap custom CSS in `@layer`** so it sits cleanly above Bootstrap without `!important` wars.
- **`:has()`** for state-driven styling without JS.
- **Typography: `text-wrap: balance`** on headings, `text-wrap: pretty` on body copy.
- **Motion: gate all animations and any View Transitions behind `@media (prefers-reduced-motion: no-preference)`.**
- **Persistence:** `localStorage` for checkbox/progress state (existing pattern) — feature-detect and fail soft.

## Required Metadata Standards

Every cheatsheet must include all blocks below. JSON-LD MUST match the visible content.

#### Essential SEO Tags
```html
<title>Topic: Descriptive Subtitle</title>
<meta name="description" content="150-200 char comprehensive description"/>
<meta name="keywords" content="primary topic, technology stack, related concepts"/>
<link rel="canonical" href="https://cheatsheets.davidveksler.com/filename.html"/>
```

#### Open Graph + Twitter/X Card
```html
<meta property="og:title" content="Title"/>
<meta property="og:description" content="Description"/>
<meta property="og:type" content="website"/>
<meta property="og:url" content="https://cheatsheets.davidveksler.com/filename.html"/>
<meta property="og:image" content="images/filename.png"/>
<meta property="og:image:alt" content="Descriptive alt text"/>
<meta name="twitter:card" content="summary_large_image"/>
<meta name="twitter:title" content="Title"/>
<meta name="twitter:description" content="Description"/>
<meta name="twitter:image" content="images/filename.png"/>
<meta name="twitter:creator" content="@heroiclife"/>
```

#### JSON-LD Structured Data (Required)
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "TechArticle",
  "headline": "Title with Version",
  "description": "Detailed description",
  "author": {"@type": "Person", "name": "David Veksler (AI Generated)"},
  "publisher": {"@type": "Organization", "name": "David Veksler Cheatsheets"},
  "datePublished": "YYYY-MM-DD",
  "dateModified": "YYYY-MM-DD",
  "keywords": "keyword list"
}
</script>
```

## Discoverability: Search + AI Answer Engines

The consumption model has shifted. Optimize for both classic search and AI answer engines (Claude, ChatGPT, Perplexity, Gemini) that read structured data and clean semantics when indexing.

- **Keep `TechArticle` JSON-LD.** It is valid, machine-readable, and consumed by AI crawlers.
- **Do NOT add `FAQPage` or `HowTo` schema to chase rich results.** FAQ rich results were deprecated in Google Search on 2026-05-07 (tooling removed June–Aug 2026); HowTo since 2023. Both remain valid schema.org types but earn no SERP feature. Only include `FAQPage` if it mirrors a real, visible Q&A section on the page.
- **There is no special schema that buys AI Overview / AI Mode inclusion.** The lever is genuinely good, accurate, self-contained content under clear headings — which is exactly what the Comprehensiveness Standard already enforces. Write answers that stand alone under a heading and are scannable; that is what answer engines extract.
- Keep meta description (150–200 chars), canonical, keywords, OG/X tags, and descriptive image alt text.
- **Repo-level (optional):** add `/llms.txt` summarizing the cheatsheet index for LLM crawlers.

## Architecture

- **Standalone HTML files** — each cheatsheet self-contained (embedded CSS/JS).
- **`index.php`** — portfolio gallery; scans root for `.html`, extracts metadata (title/description/og:image/mtime), and assigns each file a category from the `$categoryMap` array (filename → category; unmapped files fall back to `'Other'`). Cards show an "Updated" date from `filemtime()`, default-sort newest-first, and support client-side category + text filtering.
- **`sitemap.php`** — SEO sitemap with category-based priorities.
- **`generate-image-previews.py`** — Playwright screenshot generation + metadata backfill; outputs `images/{filename}.png`.
- **`how-its-built.html`** — the "How this site is built" engineering exhibit. Describes this very pipeline (spec, generation, self-verification gate, governance, tech choices) from real repo facts; cross-links `governing-agentic-ai.html` and `history.php`. Keep it in sync if the pipeline materially changes.
- No build step. Static-hosting friendly. 47+ cheatsheets; recent additions include `lifestyle-calculator.html`, `clean-architecture-dotnet.html`.

## Server Configuration (nginx)

The site is plain PHP + static HTML with **no client-side routing and no pretty-URL rewriting** — every real route is a literal file (`index.php`, `history.php`, `popularity.php`, `sitemap.php`, `subscribe.php`, `robots.txt`, or a `topic.html` cheatsheet). There is no legitimate reason for the server to fall back to `index.php` for a request that doesn't match a real file.

**Known misconfiguration to check for:** requests for nonexistent paths (including `/robots.txt` before it existed as a real file) were observed returning `HTTP 200` with the homepage HTML instead of a `404`. This is almost always one of:
- an overly broad `try_files $uri $uri/ /index.php;` fallback (correct for SPA/front-controller frameworks, wrong here — nothing needs a catch-all front controller), or
- an `error_page 404 = /index.php;` directive rewriting 404s into 200s.

**Fix** — in the nginx server block for `cheatsheets.davidveksler.com` (Plesk: Hosting Settings → Apache & nginx Settings → Additional nginx directives; otherwise the vhost file directly):

```nginx
location / {
    try_files $uri $uri/ =404;
}
```

Remove any `error_page 404 = /index.php;` (or similar) override. PHP files still route through the existing `location ~ \.php$ { ... }` fastcgi block — this only changes what happens when `$uri` matches no real file or directory.

**Verify after reloading** (`nginx -t && systemctl reload nginx`):
```bash
curl -o /dev/null -w "%{http_code}\n" https://cheatsheets.davidveksler.com/robots.txt        # expect 200, text/plain
curl -o /dev/null -w "%{http_code}\n" https://cheatsheets.davidveksler.com/no-such-page-xyz   # expect 404
```

`robots.txt` is a real static file at the repo root (`Allow: /` + a `Sitemap:` pointer to `sitemap.php`) — no server rule is needed to generate it, only to stop swallowing its request into the PHP fallback.

### Caching headers for static files

The dynamic PHP endpoints (`index.php`, `sitemap.php`, `popularity.php`, `history.php`) send their own `Cache-Control` via `header()` in source. But every cheatsheet is a **literal static `.html` file** served directly by nginx, plus the `images/*.png` previews and any CSS/JS — none of those get a `Cache-Control` header from PHP, so as observed they were going out with only `Last-Modified` and `cf-cache-status: DYNAMIC`. Add explicit caching in the nginx server block (same location as the 404 fix above):

```nginx
location ~* \.(html)$ {
    add_header Cache-Control "public, max-age=1800";
}
location ~* \.(png|jpe?g|gif|webp|svg|ico|css|js)$ {
    add_header Cache-Control "public, max-age=604800, immutable";
}
```

- Cheatsheet HTML gets a 30-minute TTL — edits land within a reasonable window without every page-load hitting the origin.
- Images/CSS/JS get a 7-day `immutable` TTL — filenames don't change on edit (see [[public-repo-no-personal-data]]-adjacent note: there's no cache-busting query string in this repo), so if you edit an existing `images/{filename}.png` in place, force a refresh by renaming or bumping a query string, or accept a stale image for up to a week.

**Verify after reloading:**
```bash
curl -sI https://cheatsheets.davidveksler.com/microservices.html | grep -i cache-control   # expect public, max-age=1800
curl -sI https://cheatsheets.davidveksler.com/images/ai-frontier.png | grep -i cache-control  # expect public, max-age=604800, immutable
```

## Email signup endpoint

The homepage (`index.php`) and `how-its-built.html` carry a lightweight, privacy-respecting email signup (one field + submit, no tracking scripts, no cookies, no third-party services). Both forms POST to **`subscribe.php`**, a same-origin native-PHP handler.

**How it works** (`subscribe.php`):
- Validates the address (`FILTER_VALIDATE_EMAIL`), rejects a tripped honeypot (`website` field), then **appends the address to `.subscribers.jsonl`** (the source of truth) and **emails a notification** to the owner via PHP `mail()`.
- Responds with JSON (`{ok, message|error}`) to `fetch` requests, or a small self-contained confirmation page to a plain no-JS form POST. So it degrades gracefully: without JavaScript the native POST still records the signup and shows a confirmation; with JS it confirms inline.

**Configuration (one env var):**
- Set **`CHEATSHEET_NOTIFY_EMAIL`** in the server environment to the address that should receive new-signup notifications (e.g. in the vhost/`php-fpm` pool config, `.htaccess` `SetEnv`, or the hosting panel's env settings). **Do not hard-code the address in source** — this is a public repo. If it's unset, signups are still recorded to `.subscribers.jsonl`; only the notification email is skipped.
- `.subscribers.jsonl` is **gitignored** — subscriber addresses must never be committed (public repo; see [[public-repo-no-personal-data]]).
- Requires a working `mail()` (sendmail/Postfix or the host's mail relay). If `mail()` is unavailable or you outgrow a flat-file list, swap the notify/record block in `subscribe.php` for a provider API (Kit, Buttondown, MailerLite, or a WordPress newsletter plugin on `davidveksler.com`) — the form contract (`POST` with an `email` field, JSON or HTML response) stays the same.
- Spam protection is intentionally minimal (honeypot + email validation). Add rate-limiting or a CAPTCHA if abuse appears.

## Phase 2 — Affiliate links (planned, NOT yet implemented)

Deferred. Do **not** add affiliate links in the current pass. When implemented, apply this pattern to the ~6–8 commercial-intent sheets only: `bitcoin-exchanges-cards.html`, `bitcoin-wallet.html`, `baofeng-uv5r-ham-guide.html`, `baofeng-uv5r-quick-ref.html`, `modern-firearms.html`, `operator-loadouts.html`, `hot-tub-treatment.html`, `samsung-bespoke-oven-guide.html`.

- **Disclose** every affiliate relationship with a clear, visible FTC-compliant disclosure on the page (not buried).
- **No fabricated IDs.** Affiliate/tracking IDs come from a single config source (a PHP config var or documented placeholder), never invented or guessed — same discipline as the email endpoint and SRI hashes.
- Keep links `rel="sponsored nofollow noopener"` and only on genuinely commercial-intent pages; do not retrofit informational/reference sheets.

## Adding New Cheatsheets

1. Run the **Generation Protocol** (research → outline to three depths → fill to density floor → self-verify).
2. Create `topic-subtopic.html` (lowercase, hyphens) in root, following the established pattern + Modern Platform Baseline.
3. Include ALL metadata blocks; ensure JSON-LD matches visible content; set a real `Last verified` date.
4. `index.php` and `sitemap.php` auto-discover the `.html` file — but **add the new file to the `$categoryMap` array in `index.php`** (`'topic-subtopic.html' => 'Category'`), or it shows up under "Other". Reuse an existing category label; only add a new one if nothing fits.
5. Generate the preview image → `images/{filename}.png` (see **Build & Verify Workflow**).
6. **Auto-commit when done.** Once the cheatsheet is written, verified in a browser, and its preview image exists, commit it to `main` directly — this repo ships cheatsheets straight to `main` (linear history, no PR/branch per file). One cheatsheet per commit, bundling the `.html` and its `images/*.png`. Message: `Add <topic> cheatsheet`, ending with the `Co-Authored-By` trailer. Do **not** push unless asked, and never stage `.claude/` or other unrelated working-tree changes — commit only the cheatsheet files by explicit path.

## Build & Verify Workflow

Concrete steps from past builds that make a cheatsheet correct on the first pass — do these before claiming "done":

- **Compute SRI hashes from the real files — never recall them or trust a summarizer/WebFetch.** Pin the current Bootstrap (**5.3.8**) and Icons (**1.13.1**), then hash the actual CDN bytes:
  ```bash
  curl -sL https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css | openssl dgst -sha384 -binary | openssl base64 -A
  ```
  Add `integrity="sha384-…" crossorigin="anonymous"` to every CDN `<link>`/`<script>`. A wrong hash silently blocks the asset — which is why you verify load (below).
- **Verify in a real browser, don't just eyeball the markup.** `file://` is blocked by the Playwright MCP, so serve locally first:
  ```bash
  nohup python3 -m http.server 8765 >/tmp/serve.log 2>&1 &   # a `(cmd &)` subshell can fail to bind; use nohup
  ```
  Load `http://127.0.0.1:8765/<file>.html` and assert: console is clean (a `favicon.ico` 404 is the only acceptable error); Bootstrap actually loaded (`typeof window.bootstrap !== 'undefined'`) so a bad SRI hash can't pass silently; CSS custom props resolve.
- **Exercise the interactive bits.** For checklist/progress pages, toggle checkboxes via `dispatchEvent(new Event('change'))` and confirm the progress count + `localStorage` keys update; confirm copy buttons map 1:1 to command blocks. Check both light and dark themes.
- **Generate the preview image yourself at 1200×630** (matches `og:image`/`twitter:image`): resize viewport to 1200×630, pick the theme that flatters the topic (dark for tech), hide floating controls (e.g. `themeToggle`, `backTop`), scroll to top, screenshot to `images/{filename}.png`. `generate-image-previews.py` remains the batch fallback.
- **Clean up** stray screenshots and kill the `http.server` before committing.

### Reusable interactive patterns
- **Saved-progress checklist** (the recurring "hook"): native `<details>` task cards, each with a `.task-check` checkbox + a `data-task` id; persist state to `localStorage` under a per-page prefix; a sticky Bootstrap progress bar reads done/total; a Reset button clears the keys. `stopPropagation` on the checkbox so ticking it doesn't toggle the `<details>`. Reference: `linux-server-hardening.html`, `privacy-data-broker-opt-out.html`.
- **Paste-ready command blocks:** a `.cmd` wrapper with an optional `.cmd-label`, a `<pre><code>`, and a copy button using the Clipboard API with an `execCommand('copy')` fallback; flash a checkmark on success. Reference: `linux-server-hardening.html`.

## Theme & Styling

- Clean, modern, responsive. Color theming suited to subject (dark for tech, light for academic).
- Dark/light via `color-scheme` + `light-dark()`; respect `prefers-color-scheme`, optional manual toggle.
- Custom CSS variables under `@layer`; consistent Bootstrap components for shared chrome.
- Hover/animation effects gated behind `prefers-reduced-motion`.

## Accessibility (target WCAG 2.2 AA)

- Semantic landmarks (`<main>`, `<nav>`, `<section>` with headings in order).
- Visible focus (`:focus-visible`), full keyboard operability.
- Contrast ≥ 4.5:1 for body text, 3:1 for large text/UI.
- Native `<details>`/`<summary>` for collapsibles (a11y built in).
- All images have meaningful `alt`; decorative images `alt=""`.
- Honor `prefers-reduced-motion`.

## Performance (Core Web Vitals)

- Targets: **LCP < 2.5s, INP < 200ms** (INP replaced FID in 2024), **CLS < 0.1**.
- `defer` all JS; lazy-load non-critical images; keep CDN payload minimal (only the Bootstrap JS components actually used).
- Inline critical CSS is acceptable given the standalone model.

## Testing Checklist

Comprehensiveness & accuracy:
- [ ] Coverage contract met: fundamentals + working knowledge + edge/advanced
- [ ] Atomic entry rule: every entry has definition + concrete example + gotcha where applicable
- [ ] Quantified: vague qualifiers replaced with real numbers/defaults/complexity
- [ ] Breadth: comparison tables, decision guidance, Common Mistakes section where supported
- [ ] Quick Reference block present near top
- [ ] Density floor: 20+ substantive entries; no section under ~3 entries
- [ ] Self-containment test passed
- [ ] **Accuracy gate: every version/price/limit/benchmark verified against a primary source; no fabricated specifics**
- [ ] Volatile facts dated; visible `Last verified` line; `dateModified` is real

Platform & delivery:
- [ ] Bootstrap pinned to current 5.3.x with SRI; JS deferred
- [ ] Collapsibles use native `<details name>`; theming via `light-dark()`
- [ ] All metadata blocks present and valid; JSON-LD matches visible content
- [ ] No FAQ/HowTo schema added for rich-result purposes
- [ ] Responsive (mobile/tablet/desktop) incl. container-query behavior
- [ ] Print styles correct
- [ ] Works without JS (native details, content visible)
- [ ] WCAG 2.2 AA: landmarks, focus-visible, contrast, reduced-motion
- [ ] Core Web Vitals targets plausibly met (LCP/INP/CLS)
- [ ] Social previews render; image generated in `/images/`
