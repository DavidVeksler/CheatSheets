# AGENTS.md

Authoritative cross-agent guidance (Claude Code, Codex, Cursor). `CLAUDE.md` and `.cursorrules` point here.

## Project Overview

A collection of standalone, interactive HTML cheatsheets covering technology, finance, philosophy, AI safety, crypto, martial arts, and more.
**Core bar:** *Terminal reference* — high density, comprehensive coverage across edge cases, and zero factual fabrication. A competent practitioner must be able to perform real work from a single sheet without opening another tab.

## Repository Governance

| Document | Purpose / Workflow |
|---|---|
| [`docs/content.md`](docs/content.md) | **Content workflow** — Quick path to add/edit/publish, local build/QA, SEO gate. |
| [`docs/marketing.md`](docs/marketing.md) | **SEO & Promotion** — Discovery files, GSC/Cloudflare analytics, cross-linking. |
| [`docs/economics-data-refresh.md`](docs/economics-data-refresh.md) | **Economics data** — Generator command, data vintages, pinned series, QA. |
| [`docs/newsletter.md`](docs/newsletter.md) | **Newsletter spec** — Resend double opt-in, key-split security, digest routine. |
| [`docs/seo-progress.md`](docs/seo-progress.md) | **SEO log** — Append-only KPI and traffic measurement history. |
| [`CLAUDE.md`](CLAUDE.md) | Pointer only (`@AGENTS.md`). |
| [`TODO/README.md`](TODO/README.md) | **Implementation spec rules** — Anchors, outline-first, definition of done. |
| `TODO/<topic>.md` | One spec per planned cheatsheet (deleted after shipping). |
| [`TODO/SPEC-AUDIT.md`](TODO/SPEC-AUDIT.md) | **Spec audit** — Search targeting, outcome, staleness register criteria. |
| [`TODO/CHEATSHEET-AUDIT.md`](TODO/CHEATSHEET-AUDIT.md) | **Sheet audit** — Conformance audit, SRI checks, defect baseline. |
| [`TODO/seo-planning.md`](TODO/seo-planning.md) | **SEO planning** — GSC baselines and striking-distance opportunities. |
| [`deploy/DEPLOY.md`](deploy/DEPLOY.md) | **Deployment runbook** — `./deploy.sh` pipeline (preflight, validate, push, verify). |
| [`weekly-freshness-update.md`](weekly-freshness-update.md) | Scheduled fact-drift refresh routine. |
| [`README.md`](README.md) | Public repository readme. |
| [`.github/copilot-instructions.md`](.github/copilot-instructions.md) | GitHub Copilot summary (sync when editing this file). |
| `SEO_PROMPT.txt` | Footer cross-linking procedure. |

---

## Generation & Quality Protocol

1. **Effort = High** (Opus 4.8 default).
2. **Research primary sources first:** Verify every version, API signature, default, benchmark, limit, date, and price. Never fabricate or guess numbers.
3. **Coverage contract (3 Depths):**
   - **Fundamentals:** Mental models, core definitions (the 20% explaining 80%).
   - **Working knowledge:** Syntax, commands, daily production patterns, decisions.
   - **Edge & advanced:** Gotchas, failure modes, performance, internals.
   - *No placeholders or TODOs.* Every outlined section must be fully populated (≥3 substantive entries per section).
4. **Atomic entry rule:** Every entry must have:
   - Precise 1-line definition/purpose.
   - Concrete example with real-world values (no `foo`/`bar`).
   - Quantified metrics (e.g., "~O(log n), sub-ms for n < 10⁶", explicit token prices, exact cutoffs/defaults).
   - Gotcha, pitfall, or explicit "when NOT to use".
5. **Breadth requirements:**
   - Comparison table (criteria × alternatives) when 2+ options exist.
   - Decision guidance ("Use X when...; Use Y when...").
   - Common Mistakes / Anti-Patterns section (MANDATORY for technical sheets).
   - Quick Reference block near top (high-frequency lookups).
   - Density floor: 20+ substantive entries per sheet.
6. **Freshness & Provenance:**
   - Date volatile facts inline ("as of <Mon YYYY>" or version tag).
   - Include visible `Last verified: YYYY-MM-DD` in header/footer (dates the *topic content*, never internal tooling/Bootstrap versions/SRI hashes).
   - Set JSON-LD `dateModified` to match visible verification date.

---

## Change Management & Deployment

- **Commit unconditionally:** Commit all work (including WIP, docs, scripts) per logical batch. Quality gates deployment, not commits.
- **Never push unprompted:** Ask for user approval after committing before deploying.
- **Deploy via pipeline:** Push `main` to `origin`, then run `./deploy.sh` (or `./deploy.ps1`). Pipeline runs preflight, local validation (SEO gate, links/assets, JSON, `php -l`), confirmation, push to `production`, and live `curl` verification. See [`deploy/DEPLOY.md`](deploy/DEPLOY.md).

---

## Tech Baseline & Invariant Layer

### Design Approaches (Pick per Topic)
- **Vanilla + Modern CSS Platform** (*Recommended for new sheets*): Lightest payload, full visual identity.
- **Bootstrap 5.3.x**: Incumbent standard for dense card/table references. Do not rewrite existing sheets.
- **Utility / Tailwind**: Rapid custom layouts via prebuilt sheet or CDN.
- **Classless (Pico / Simple.css / Water.css)**: Semantic, clean text/essay references (philosophy, finance).
- **Bespoke Themed**: Strong metaphors (terminal/CRT for security/CLI, blueprint for architecture). Use `frontend-design` skill for direction.

### Non-Negotiable Technical Invariants
- **Standalone HTML:** Single self-contained file (embedded CSS/JS), zero build step.
- **SRI on CDN Assets:** Every `<link>`/`<script>` must include `integrity="sha384-..." crossorigin="anonymous"`. Load JS with `defer`.
- **Modern CSS Baseline:**
  - Accordions: Native `<details name="group">` + `<summary>` (no JS required, a11y & print native).
  - Theming: `color-scheme` + `light-dark()` honoring `prefers-color-scheme`; optional `[data-theme]` toggle.
  - Layout & Specificity: CSS Grid, container queries, custom CSS inside `@layer`.
  - Typography: `text-wrap: balance` (headings), `text-wrap: pretty` (body).
  - Motion: Gate animations behind `@media (prefers-reduced-motion: no-preference)`.
  - Scroll Performance: Avoid fixed full-viewport `mix-blend-mode` or `backdrop-filter` (causes scroll compositing stalls; bake textures into element `background`).
  - State: Native `localStorage` with feature-detection and soft fallback.
- **Accessibility (WCAG 2.2 AA):** Semantic landmarks (`<main>`, `<nav>`, `<section>`), `:focus-visible`, contrast ≥4.5:1 (3:1 large UI), explicit `alt` text.
- **Core Web Vitals:** LCP < 2.5s, INP < 200ms, CLS < 0.1.

### Cached CDN Dependencies (SRI Hashes)
Compute new hashes via `curl -sL <url> | openssl dgst -sha384 -binary | openssl base64 -A`.

| Asset | Version | URL | integrity (sha384-…) |
|---|---|---|---|
| Bootstrap CSS | 5.3.8 | `https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css` | `sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB` |
| Bootstrap JS | 5.3.8 | `https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js` | `sha384-FKyoEForCGlyvwx9Hj09JcYn3nv7wiPVlz7YYwJrWVcXK/BmnVDxM+D2scQbITxI` |
| Bootstrap Icons | 1.13.1 | `https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/bootstrap-icons.min.css` | `sha384-CK2SzKma4jA5H/MXDUU7i1TqZlCFaD4T01vtyDFvPlD97JQyS+IsSh1nI2EFbpyk` |

---

## Required Metadata & Discoverability

### HTML Metadata Template
```html
<title>Topic: Descriptive Subtitle</title>
<meta name="description" content="150-200 char comprehensive description"/>
<meta name="keywords" content="primary topic, technology stack, related concepts"/>
<link rel="canonical" href="https://cheatsheets.davidveksler.com/filename.html"/>

<!-- Open Graph & X Cards -->
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

<!-- JSON-LD -->
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