# index.php Redesign: From Directory to Explorer

## Target

- Existing page: `index.php` (https://cheatsheets.davidveksler.com/)
- Companions touched: `sitemap.php` (category URLs), `llms.txt` (catalog link), `docs/content.md` and `AGENTS.md` routing table (new build step), `deploy/DEPLOY.md` (new gate)
- New files: `scripts/build_catalog.py`, `catalog.json` (generated, committed), `paths.json` (hand-authored), optional `catalog-overrides.json`
- Change type: full front-end rewrite of the index plus a small data layer. Cheatsheets themselves are untouched.
- Content posture: the index gets richer by reading data that already exists in the repo. No new factual claims are written for it.

Read `AGENTS.md`, `TODO/README.md`, `TODO/SPEC-AUDIT.md`, and this file before implementation. If they disagree, the repository-wide instructions win. Per the global operating rules, Fable wrote this spec; Opus or Sonnet implements it (see Phasing for which).

## Why this redesign

The current index is a competent directory: 197 cards, a title/description filter, a category dropdown, six sort orders, a glass hero, an email form. It answers "what pages exist" and nothing else. The collection has outgrown that:

1. **It cannot see inside a page.** A reader who types "tap drill M6" gets nothing, because the filter only reads titles and 150-character descriptions. Yet the sheets carry `<section id>` anchors and H2 headings that could deep-link straight to the answer. The site's stated bar is "terminal reference"; the front door should search like one.
2. **It ignores the graph.** The sheets link to each other about 1,490 times (every sheet has at least one outbound link, the hubs have 15 to 22). Those edges encode which topics belong together, and the index shows none of it.
3. **It ignores the site's own telemetry.** `popularity.json` (30-day decayed scores, lifetime totals, 24 days of site-wide history), `refresh-status.json` (last-reviewed dates), and git history (first-commit, last change) are all on disk. They surface only on `popularity.php` and `history.php`, which almost nobody opens.
4. **It sells the pipeline before the content.** The hero and CTA are about governance and LinkedIn. That serves goal 2 and 3 (portfolio, case study), but a first-time visitor came for a reference. Lead with the content; let the pipeline show itself through a live "pulse" rather than a paragraph.
5. **It violates the repo's own invariants.** Every card uses `backdrop-filter` and the body has a fixed animated gradient, exactly what `AGENTS.md` bans for scroll performance. It is light-only while the sheets support dark mode. The `<title>` is 65 characters against a 60-character gate (`seo_check.py` only scans `*.html`, so this was never caught). It ships Bootstrap CSS, Bootstrap JS, and an icon font for what is, functionally, a filtered list.
6. **Category views have no URL of their own.** `?cat=Radio` is rewritten client-side; the server renders the same title and description for every category. Fifteen indexable landing pages are being left on the table.

## Concepts considered

Brainstormed and scored against the four site goals (study tool, portfolio, agentic case study, advocacy) and the reading conditions below.

| Concept | Verdict | Reason |
|---|---|---|
| **A. Command palette search that reads inside pages** (titles, keywords, headings, section anchors) | **Core** | The single feature that changes what the index *is*. Cheap to build once the catalog exists. Serves every goal. |
| **B. Constellation map** (force-laid graph of sheets, edges = cross-links, colour = category, size = popularity) | **Core, as a mode, not the default** | The graph is real data and the map is the shareable signature artifact. Force graphs are poor primary navigation, so Grid stays default; Map is one keystroke away. |
| **C. Facets beyond category** (shape: comparison / procedure / calculator / tracker / commands / essay; interactivity; freshness) | **Core** | Cheap heuristics at catalog-build time. Lets a reader ask "show me things I can *use*" rather than "show me a topic". |
| **D. Curated paths** (hand-written trails of 4 to 6 sheets with a one-line reason per step) | **Core, phase 2** | The only concept that adds editorial value a directory cannot derive. Also the clearest expression of goal 1 (this is how David actually uses the collection). |
| **E. Pulse strip** (live counts, last commit, sheets reviewed this week, site-traffic sparkline, trending) | **Core** | Turns the goal-3 pitch from a paragraph into evidence. Server-rendered, no JS needed. |
| **F. Detail drawer** ("what's inside" outline, neighbours in the graph, dates, review status, open/copy) | **Core** | Every other concept needs a place to land a click. Shareable via `?sheet=`. |
| **G. Serendipity** ("Surprise me", weighted toward the long tail; "Deep cut of the day") | **Include, small** | Two buttons. Surfaces goal-1 pages that will never rank. |
| **H. Server-rendered category landing pages** with their own title, description, canonical, JSON-LD, sitemap entries | **Include** | Pure SEO win, near-zero design cost. |
| I. Per-sheet inline preview on hover (render the sheet's Quick Reference block) | Defer | Needs per-sheet HTML extraction and a consistent Quick Reference markup that does not exist across 197 files. Revisit after the catalog exposes outlines. |
| J. Reader accounts, bookmarks synced, comments | Reject | No backend beyond PHP + flat files by design; localStorage covers "visited" and "path progress". |
| K. Timeline / "the collection over time" scrubber | Defer | History is already `history.php`; a scrubber is a toy. The Pulse strip's newest-three and sparkline cover the useful part. |
| L. AI chat over the collection | Reject | `llms.txt` and `llms-full.txt` already serve AI agents. An on-page chatbot adds a dependency, a cost, and a failure mode with no goal it serves better than the palette. |

## Recommended concept: the Explorer

One page, three lenses over the same catalog, one search box that reaches inside every sheet.

- **Search** (command palette, `Cmd/Ctrl+K` or `/`): instant, client-side, over title + keywords + description + headings. Results group by sheet and list matching sections as deep links (`file.html#section-id`).
- **Grid** (default lens): the card wall, with a facet rail (category, shape, interactivity, freshness) and sort. Server-rendered and fully usable without JavaScript.
- **Map** lens: the constellation. Precomputed layout, canvas render, hover shows neighbourhood, click opens the drawer.
- **Paths** lens: curated trails with progress.
- **Drawer**: the landing spot for any click. Outline, neighbours, metrics, open.
- **Pulse**: a thin strip under the hero with live facts about the collection.

Signature element: **the constellation map.** Build it best. It also becomes the social preview image (phase 3), so the map must look good static.

## Targeting and reader outcome

### Audiences and goals

| Visitor | Arrives via | Needs from the index | Site goal served |
|---|---|---|---|
| David, mid-task | Bookmark, `Cmd+K` muscle memory | Land on the right section of the right sheet in under 3 seconds | 1 |
| Practitioner who found one sheet | Sheet footer "All cheatsheets" link | Find the sibling sheets; understand what else is here | 1, 3 |
| Recruiter, peer, hiring manager | LinkedIn, `how-its-built.html` | Grasp scale and quality in 10 seconds; see it is alive | 2, 3 |
| AI crawler / answer engine | `llms.txt`, direct | A machine-readable catalog and clean per-category pages | 3 |

### Search intent

- Primary query for the index itself: `david veksler cheatsheets` (brand). The index is not a keyword page; the category landing pages are.
- Category landing page queries (examples): `baofeng cheatsheets`, `buddhism cheat sheet`, `crypto custody reference`, `ham radio quick reference`. Research mode.
- The palette is for **navigational** intent inside the collection, not organic search.

### Metadata contract (drafts, implementer verifies lengths with `seo_check.py` extended to `index.php` output)

- `<title>`: `Cheatsheets by David Veksler: Explore 190+ References` (53 chars; the count is a literal in the title and must be updated by the catalog builder or written as a round-down like "190+")
- H1: `Find the one page you'll keep open.`
- Lead: `197 dense, verified references across 15 fields, built by one person plus AI agents under a public, git-audited spec. Search inside every page, follow a path, or wander the map.` (counts are template variables, not literals)
- Meta description (150 to 200 chars): `Search inside 190+ interactive reference guides on AI, software, security, crypto custody, radio, health, philosophy and more. Built by a governed Claude Code pipeline with a public git audit trail.`
- Category page `<title>`: `{Category} Cheatsheets ({n}) | David Veksler`; description generated from the first three sheet titles in that category, clamped to 200 chars.

### Definition of working

After the redesign, a reader can type a term that appears only in a section heading of one of 197 sheets and open that exact section in under three seconds, without knowing which sheet it lives in.

### Success metrics

- Palette usage: `explorer_search` events per session and the share of sessions with a deep-link click.
- Index bounce rate down and pages-per-session up in GA4 (property `properties/543339529`), comparing 30 days before and after deploy.
- Category landing pages acquire impressions in Search Console within 60 days (currently zero because they do not exist as distinct documents).
- Lighthouse mobile performance stays at or above 95 with all 197 cards server-rendered.

### Reading conditions

- Primary: 1280 to 1920 px desktop, keyboard on, often with another window open. Frequent jumping, rarely scrolling the whole grid.
- Secondary: 375 to 430 px phone, thumb on the search box. Map is not the default here.
- Lighting: both themes first-class; dark mode is the norm for the software and AI audiences.
- Stress level: low, but impatience is high. Anything that animates before the reader can type is a defect.

## Data layer

### `scripts/build_catalog.py` (new; supersedes `generate-metadata.py`)

Runs in the repo root, scans every `*.html` not excluded, and writes `catalog.json`. `generate-metadata.py` and its workflow are retired or turned into a thin wrapper so two parsers cannot drift (automation ladder rule: one script owns extraction).

Per sheet it records:

| Field | Source | Notes |
|---|---|---|
| `file`, `url` | filename | canonical URL from `<link rel=canonical>` if present, else base + file |
| `title` | `<title>` | full, untruncated |
| `description` | `meta[name=description]`, fallback `og:description` | full, untruncated; index clamps via CSS |
| `keywords[]` | `meta[name=keywords]` split on commas | 183 of 197 sheets have this |
| `image` | `og:image` | resolved relative to site root |
| `category` | `category-map.php` | parsed by regex; unmapped falls to `Other` and the builder prints a warning |
| `headings[]` | `h2`; if a sheet has fewer than 3, descend to the first of `h3`, `h4`, `h5` that has 3 or more (`judo.html` uses only `h5`) | each entry `{text, id}` where `id` is the heading's own id or the enclosing `<section id>`; text is tag-stripped and entity-decoded; entries without an id are still searchable but not deep-linkable |
| `outlinks[]` | `href="*.html"` to other catalogued files | deduplicated; self-links dropped; these are the graph edges |
| `shape[]` | heuristics, see below | multi-valued |
| `interactive` | boolean | `localStorage` present or 3+ form inputs inside a `<script>`-bearing page |
| `words`, `tables`, `sections` | counts | drive shape heuristics and the drawer's "size" line |
| `created` | `git log --follow --diff-filter=A --format=%ct` | first commit; matches current `git_ctime` |
| `updated` | `git log -1 --format=%ct -- file` | last commit, not filesystem mtime (mtime is unreliable after a fresh clone or rsync) |
| `reviewed` | `refresh-status.json` | ISO date or null |
| `x`, `y` | precomputed layout | see Map layout |

Collection-level fields: `generated` (ISO timestamp), `count`, `categories[]` with per-category counts and hues, `edges[]` as `[fromIndex, toIndex]` pairs, and `stats` (total sections indexed, total edges).

Exclusions: the current `$excludedItems` list plus anything in `catalog-overrides.json` marked `"hide": true`. Candidates to review at implementation time: `command-deck.html`, `p-doom-test-harness.html`, `prompt-builder.html`, `how-its-built.html` (keep it, it belongs in AI & Safety per the map, but consider `featured`).

### Shape heuristics (multi-valued; a sheet with none gets `reference`)

| Shape | Rule (anchors, tune against the real corpus) |
|---|---|
| `comparison` | 3+ tables, or any table with 12+ rows |
| `procedure` | 3+ ordered lists, or a checklist (10+ checkboxes) |
| `calculator` | 3+ `input[type=number|range]` or `<output>`, plus script |
| `tracker` | `localStorage` plus 10+ checkboxes |
| `commands` | 10+ `<pre>`/`<code>`/`<kbd>` |
| `device` | title or keywords match a model-number pattern (`[A-Z]{1,4}-?\d{2,5}`) or contain "programming", "error codes" |
| `essay` | 4,000+ words and fewer than 2 tables |
| `timeline` | title or a heading contains "timeline", "history", "log" |
| `visual` | 3+ inline `<svg>` or a `<canvas>` |

`catalog-overrides.json` may set `shape`, `hide`, or `featured` per file when a heuristic misfires. Keep it small; fix heuristics first.

### Map layout (precomputed)

- Deterministic, seeded Fruchterman-Reingold in pure Python (no dependency). 197 nodes and ~1,490 edges converge in well under a second.
- Category gravity: each category's centroid is placed on a circle; nodes are pulled toward their centroid so clusters read as regions. Isolated nodes (degree 0 after filtering) sit at their category centroid with a small jitter.
- Output normalised to `[0,1]` in both axes. The renderer scales to the viewport.
- The layout is regenerated on every build; small drift between builds is acceptable, large drift is not. If two consecutive builds move the median node more than 5% of the canvas with no edge changes, the seed or cooling schedule is wrong.

### `paths.json` (hand-authored)

```json
{
  "paths": [
    {
      "id": "baofeng-weekend",
      "title": "Program a Baofeng this weekend",
      "promise": "From unboxing to a working GMRS and repeater setup, in the order you will actually need it.",
      "steps": [
        {"file": "baofeng-uv5r-quick-ref.html", "why": "Keypad sequences and screen icons first; nothing else makes sense until the menu is familiar."},
        {"file": "baofeng-uv5r-ham-guide.html", "why": "Repeaters, offsets, tones, and the legal lines."},
        {"file": "gmrs-frs-murs-card.html", "why": "The channels you can legally use without a ham ticket."},
        {"file": "emergency-radio-card.html", "why": "What to preload before you need it."},
        {"file": "ham-radio-technician.html", "why": "If the hobby stuck, the licence is a weekend of study."}
      ]
    }
  ]
}
```

The builder validates every `file` exists in the catalog and fails the build otherwise (a rename can no longer silently break a trail). Draft trails for David to edit, filenames verified at build time:

1. Program a Baofeng this weekend (above)
2. Harden a Linux box: `linux-server-hardening`, `ubuntu-linux-for-ai-developers`, `passkeys-yubikeys-hardware-auth`, `modern-devops-pipelines`, `observability-logs-metrics-traces-slos`
3. Crypto custody, decision by decision: `crypto-custody-index`, `bitcoin-self-custody-guide`, `mpc-wallet-architecture`, `institutional-crypto-custody`, `custody-provider-integration`, `post-quantum-custody-migration`
4. The AI landscape in one sitting: `ai-frontier`, `ai-models-compared`, `open-weight-ai-models`, `ai-model-api-pricing`, `ai-coding-agents-compared`, `ai-infrastructure-numbers`
5. Household preparedness, likely to rare: `actual-risk-dashboard`, `the-household-numbers`, `prepper-gear-audit`, `vehicle-emergency-kit`, `emergency-radio-card`, `nuclear-preparedness`
6. Protect a parent from scams: `scam-defense-for-parents`, `parents-threat-model`, `privacy-data-broker-opt-out`, `small-business-scams`, `debt-collection-defense`
7. Buddhist practice, principles to cushion: `buddhism-core-principles`, `anapanasati-mindfulness-of-breathing`, `satipatthana-four-foundations`, `five-hindrances-debugger`, `right-speech-modern-life`
8. Longevity, what the evidence supports: `longevity-what-actually-works`, `longevity-biomarkers`, `blood-tests-cbc-cmp-lipids-a1c-thyroid`, `longevity-supplements-evidence`, `sleep-optimization`, `strength-training`
9. Space hardware by the numbers: `orbital-rockets-comparison`, `rockets-and-spaceflight`, `starlink-satellite-anatomy`, `space-habitats-life-support`, `boom-supersonic`
10. Architecture for .NET teams: `clean-architecture-dotnet`, `dotnet-cheatsheet`, `microservices`, `api-design-rest-graphql-grpc-webhooks`, `sql-performance-tuning`, `postgresql`
11. Death, estate, and the paperwork: `estate-documents`, `death-logistics`, `insurance-worth-it`, `index-investing-tax-advantaged`

### Gates

- `scripts/deploy.py --check` gains a step: `catalog.json` must be newer than every catalogued `.html` and `category-map.php`, and `paths.json` must validate. Fail closed with the command to run.
- A tracked `.githooks/pre-commit` regenerates `catalog.json` when any `*.html`, `category-map.php`, `paths.json`, or `catalog-overrides.json` is staged, and stages the result. Document enabling it (`git config core.hooksPath .githooks`) next to the existing pre-push note.
- The nightly `update-popularity.yml` job also runs the builder so `reviewed` and `updated` stay current even when nobody commits.

## Page architecture

### Rendering layers

1. **Server (PHP)** reads `catalog.json`, `popularity.json`, `refresh-status.json`, `paths.json`, and one `git log -1` call. It renders the complete Grid (all cards), the facet rail as real links, the Pulse strip, the Paths lens as static lists, the JSON-LD, and, when `?sheet=` is present, that sheet's detail block inline near the top. Everything a no-JS reader needs is in the HTML.
2. **Inline JSON** (`<script type="application/json" id="catalog-lite">`): the compact fields needed for instant filtering and the palette's first keystroke: `file, title, category, shape, pop, x, y, keywords`. Target under 45 KB uncompressed.
3. **Lazy `catalog.json`** fetched on first palette open, first Map open, or first drawer open: adds `headings`, `outlinks`, `description`, `edges`. Cache-busted with `?v=<generated>` and served with a one-year cache.
4. **Inline JS** (single `<script defer>`, no framework, target under 25 KB): filtering, palette, drawer, map renderer, paths progress, theme toggle, URL state, analytics events.

If `catalog.json` is missing, the page renders a single plain banner saying so with the build command. No runtime HTML parsing fallback; the deploy gate guarantees the file.

### URL state (all `replaceState` except drawer, which uses `pushState`)

| Param | Meaning | Indexable? |
|---|---|---|
| `cat` | category filter; server-rendered title/description/canonical/JSON-LD | Yes, self-canonical, listed in `sitemap.php` |
| `shape`, `sort`, `view` (`grid|map|paths`), `q` | client state; server honours them on load | No (`noindex` when present) |
| `sheet` | open drawer for a file; server inlines the detail block | No (`noindex`); canonical points to the sheet itself |
| `path` | open a trail | No |

### Modes and keyboard map

| Key | Action |
|---|---|
| `Cmd/Ctrl+K`, `/` | Open palette (`/` only when focus is not in an input) |
| `Esc` | Close palette or drawer |
| `↑ ↓ Enter` | Move and open within palette results; `Enter` on a section row opens the deep link |
| `g` then `g` / `m` / `p` | Switch lens to Grid / Map / Paths (two-key chord, shown in the palette footer) |
| `t` | Toggle theme |
| `?` | Show the keyboard map |

## Feature specifications

### Search palette

- Opens as a `<dialog>` centred at the top third of the viewport. Input autofocused. Placeholder rotates through three real examples drawn from the catalog (for instance `torque`, `ukemi`, `ufw`) so the reader learns it searches inside pages. The builder verifies each example matches at least one heading.
- Index: built once from `catalog-lite`, upgraded when `catalog.json` arrives. Tokenise on non-alphanumerics; match on prefix per token. Field weights: title 5, keyword 3, heading 3, description 1. Add `log10(pop + 1) * 0.5` as a tie-breaker so the popular sheet wins a draw but never outranks a better text match.
- Results: up to 10 sheets. Each sheet row shows category dot, title, and up to 3 matching headings as sub-rows with a `#` glyph. Sub-rows without an id are shown but not linked. Below results, a "Commands" group: `Open map`, `Open paths`, `Surprise me`, `Toggle theme`, `Category: X` for the top 3 matching category names.
- Empty query: shows `Recent` (last 5 opened, localStorage), `Trending` (top 5 by score), and the commands.
- Latency: full re-rank under 20 ms for 197 sheets on a mid-range phone; no debounce.
- Live region announces "12 results" on each change.
- Analytics: `explorer_search {chars, results}` fired on `Enter` or a result click, not per keystroke.
- No-JS fallback: the hero search box is a plain `GET` form to `?q=`, filtered server-side over title, keywords, and description. The palette only exists with JS.

### Grid lens and facet rail

- Cards keep the current information (image, category badge, title, description, created/updated) and add: shape chips (max 3), a `reviewed` dot when `refresh-status.json` has a date within 90 days (title attribute carries the date; no visible "last verified" text, per `AGENTS.md`), and a visited state from localStorage.
- Card click anywhere opens the drawer; the title link and the "Open" button go straight to the sheet (middle-click and `Cmd+click` work as normal links). Rationale: the drawer is discovery, the link is intent; both must be one click.
- Facet rail (left on desktop, collapsible top bar on mobile): Category (15, with counts), Shape (with counts), Interactive (toggle), Freshness (`Reviewed in 90 days`, `Updated in 30 days`, `New in 30 days`). Facets AND across groups, OR within a group. Every facet is a real `<a href>` so no-JS works; JS intercepts for instant filtering.
- Sort: Newest, Recently updated, Most popular, Recently reviewed, Title. Default Newest (current behaviour).
- Result count and active facets appear as removable chips above the grid.
- `NEW` badge: created within 30 days (currently uses mtime; switch to git created).

### Map lens

- `<canvas>` sized to the viewport minus rail, device-pixel-ratio aware. Nodes: filled circles, radius `4 + 6 * sqrt(pop_norm)` CSS px, category hue, 1 px surface-coloured ring. Edges: 0.5 px lines at 12% opacity by default.
- Labels: always drawn for the top 25 by popularity and for every hub with degree 12+; others appear on hover and when zoom exceeds 1.6x. Labels use the on-surface text colour, never the category hue (contrast).
- Hover: node grows 1.5x, its edges rise to 60% opacity, neighbours highlight, everything else dims to 35%. A tooltip shows title, category, degree.
- Click: opens the drawer and centres the node.
- Pan: pointer drag. Zoom: wheel and pinch, 0.6x to 4x, around the pointer. Double-click resets.
- Legend: category dots with counts; clicking a legend entry dims all other categories (multi-select).
- The active facet filter applies to the map too: filtered-out nodes render at 15% opacity rather than disappearing, so the shape of the whole is never lost.
- Under 768 px: the Map lens renders the **ego graph** of the drawer's sheet (or of the most popular sheet when none is selected) as a radial layout, with a "show whole map" button that switches to pan/zoom mode.
- Accessibility: canvas has `role="img"` with an `aria-label` summarising node and edge counts. A "List this map" toggle renders the same data as nested lists (category, sheet, links to). The drawer's neighbour lists are the primary keyboard route.
- Reduced motion: no hover growth animation; state changes are instant.
- Performance: full redraw under 8 ms at 1440x900 on an integrated GPU; redraw only on interaction, never in a loop.

### Paths lens

- Each trail is a card with title, promise, step count, and progress (`2 of 5`, from localStorage `cs-explorer:v1:path:<id>`).
- Open trail: horizontal stepper on desktop, vertical on mobile. Each step: number, sheet title, the `why` line, a `Start`/`Continue`/`Done` state. Marking done happens when the sheet link is clicked (optimistic) with a manual toggle to undo.
- "Related paths" at the bottom: trails sharing at least one sheet.
- No-JS: trails render as ordered lists with links; progress simply does not persist.
- Analytics: `explorer_path_start {id}` and `explorer_path_step {id, step}`.

### Drawer

- Right-side `<aside>` on desktop (420 px), bottom sheet on mobile (85 vh, drag handle). Non-modal, but focus moves in on open and returns on close. `Esc` closes. Background gets `inert` while open on mobile only.
- Contents, top to bottom: preview image (fixed 40:21 box), category badge and shape chips, title (h2), description (full), **What's inside** (headings as a list; linked when they have ids; capped at 14 with "and 6 more" expander), **Neighbours** (Links to: n, Linked from: n; each a compact row that swaps the drawer content in place, with browser back restoring the previous sheet), **Facts** (created, updated, reviewed, size as `~n words · n tables · n sections`, popularity rank as `#12 of 197 this month`), and actions: `Open`, `Copy link`, `Show on map`.
- URL: `?sheet=file.html` via `pushState`; back button closes or returns to the previous drawer.
- Analytics: `explorer_drawer {file, from: grid|map|palette|path|neighbour}`.

### Pulse strip

Server-rendered, no JS. One line on desktop, two on mobile. Numerals in the monospace token with `font-variant-numeric: tabular-nums`.

- `{count} references · {categories} fields · {sections} sections indexed · {edges} cross-links` (all from catalog stats; today that is 197, 15, and about 1,490 edges; the section count is whatever the builder finds)
- `Last change: "{subject}" · {relative time}` linking to `history.php` (one `git log -1 --format=%s%n%ct` call; cached with the existing 300 s page cache)
- `Reviewed this week: {n}` (from `refresh-status.json`, count of `last_reviewed` within 7 days; omitted when zero)
- A 24-point inline SVG sparkline of `totalViewsHistory` with the last value labelled, linking to `popularity.php`
- `Trending:` three titles by score, filtered to catalogued files (this also fixes the junk paths like `404.html` that `popularity.json` currently carries)

If any data source is missing, that segment is omitted, never faked.

### Serendipity

- `Surprise me` (hero and palette command): picks uniformly from the bottom two-thirds by popularity, excluding the last 10 surprises (localStorage), and opens the drawer. `explorer_surprise {file}`.
- `Deep cut of the day`: one card pinned at the top of the Grid, chosen deterministically from `sha1(date + file)` over the same pool, server-rendered so it is stable for a full UTC day and cacheable.

### Category landing pages (`?cat=`)

- Server renders title, description, canonical (self), H1 (`{Category}`), a one-paragraph intro generated from counts and the three most popular titles (no prose claims), filtered JSON-LD `ItemList`, and the filtered grid. The facet rail pre-selects the category.
- `sitemap.php` lists the 15 category URLs with `changefreq weekly`.
- Unknown `cat` values return the unfiltered index with `noindex`.

### Email signup and pipeline CTA

- Keep the signup form exactly as it works today (same-origin `subscribe.php`, honeypot, JSON enhancement). Move it to a slim band above the footer.
- Replace the "How this collection is built" section with a two-sentence band under the Pulse strip linking to `how-its-built.html` and GitHub. The LinkedIn CTA moves to the footer. The Pulse strip is now the case-study argument.

### Theming and motion

- `color-scheme: light dark` and `light-dark()` tokens; `[data-theme]` toggle persisted to `cs-explorer:v1:theme`, applied before first paint via a two-line inline script in `<head>` to avoid a flash.
- Remove the animated body gradient, the cursor-following hero glow, and every `backdrop-filter`. Allowed motion, all gated behind `prefers-reduced-motion: no-preference`: card lift 2 px on hover (120 ms), drawer slide (200 ms), palette fade (120 ms), map hover growth (100 ms).

## Visual identity: Chart Room

The map is a chart, so the page borrows from navigational charts and library card catalogs: paper and ink, thin rules, small-caps section labels, monospace numerals, and colour used only to encode category. It must feel like an instrument, not a landing page.

### Palette (tokens, defined once on `:root` via `light-dark()`)

| Role | Light | Dark |
|---|---:|---:|
| Page | `#f6f6f2` | `#0e1013` |
| Surface | `#ffffff` | `#161a20` |
| Surface raised (drawer, palette) | `#ffffff` | `#1c2129` |
| Rule | `#d9d9d2` | `#2a3038` |
| Ink | `#16181d` | `#e8e9ec` |
| Ink muted | `#5b6068` | `#9aa1ab` |
| Accent (controls, focus, links) | `#4338ca` | `#a5b4fc` |
| Accent surface | `#e8e7fb` | `#26294a` |
| Success (reviewed dot) | `#15803d` | `#4ade80` |

The accent keeps continuity with the current indigo brand and with `how-its-built.html`.

### Category hues

Keep the existing 15 light hues from `$categoryStyles` for continuity with the sheets' badges. Define a dark-mode partner for each that meets 3:1 against the dark page for non-text use (nodes, badges, top rules). Category hue is never used for body text; badges use the hue as a border and tint with `Ink` text. The implementer records the final 15 pairs in a table in `index.php`'s CSS comment block and checks each with a contrast tool.

### Type

- Body: `system-ui, -apple-system, "Segoe UI", Roboto, sans-serif`
- Numerals and metadata: `ui-monospace, "SF Mono", Menlo, Consolas, monospace`, `font-variant-numeric: tabular-nums`
- Headings: `text-wrap: balance`; body: `text-wrap: pretty`
- Scale: 13 px metadata, 15 px body, 17 px card title, 22 px section heads, 34 to 44 px H1 (`clamp`)
- No web fonts.

### Layout

- Max content width 1440 px. Facet rail 240 px, sticky. Grid `repeat(auto-fill, minmax(300px, 1fr))`, gap 20 px. Container queries switch the card to a horizontal layout when the container is narrower than 340 px.
- Hero height under 40 vh on desktop, under 30 vh on mobile; the search box is the hero's focal element and sits above the fold on a 375x667 screen.
- Cards: flat surface, 1 px `Rule` border, 3 px category top rule (continuity with current cards), 8 px radius, no shadow at rest, 2 px lift and `Rule` to `Accent` border on hover.
- Print: Grid prints as a two-column list of title + URL + category; Map and Paths print their list equivalents.

## Budgets

| Budget | Target |
|---|---|
| HTML document, 197 cards, uncompressed | ≤ 200 KB (trim JSON-LD `ItemList` items to `name`, `url`, `genre` if needed) |
| HTML gzipped | ≤ 45 KB |
| Inline CSS | ≤ 20 KB |
| Inline JS | ≤ 25 KB |
| `catalog.json` (lazy) | ≤ 350 KB uncompressed |
| External requests before interaction | 0 scripts and 0 stylesheets beyond the existing Clarity tag (which David may drop, see Open decisions) |
| LCP | < 1.5 s on simulated 4G; LCP element is the H1 text |
| INP | < 100 ms; palette keystroke to paint < 50 ms |
| CLS | < 0.05; every image box has a fixed aspect ratio |
| Lighthouse mobile | Performance ≥ 95, Accessibility ≥ 95, SEO 100 |
| WCAG | 2.2 AA; contrast ≥ 4.5:1 text, ≥ 3:1 UI and nodes; every control reachable and operable by keyboard; `:focus-visible` rings 2 px `Accent` |

## SEO and analytics

- Index `<title>` ≤ 60 chars, description 150 to 200, canonical, `CollectionPage` + `ItemList` JSON-LD as today. Extend `scripts/seo_check.py` to validate the rendered output of `index.php` (run `php index.php` with a stub `$_SERVER` or curl the local server) so the gate covers the front door.
- Category pages as above; `sitemap.php` updated; `robots.txt` unchanged.
- `llms.txt` gains one line pointing at `catalog.json` as the machine-readable index. `llms-full.txt` unchanged.
- GA4 (injected by Cloudflare, not in the HTML) receives the `explorer_*` events via `gtag` when present. Keep the existing `linkedin_click` event.
- OG image: unchanged in phase 1; phase 3 replaces it with a rendered map.

## Scope boundaries

### Preserve exactly

- All sheet files, their content, and their URLs.
- `subscribe.php` contract and the signup form's fields, honeypot, and JSON response handling.
- `category-map.php` as the single source of category truth (the builder reads it; nothing else writes it).
- `popularity.json`, `refresh-status.json` formats and their writers.
- `history.php` and `popularity.php` (they remain the deep views; the Pulse strip links to them).
- The 300 s `Cache-Control` on the index.
- The `?q=`, `?cat=`, `?sort=` parameters and their meanings (existing shared links keep working).
- Page-title sync on category (`{Category} Cheatsheets | David Veksler`), now server-side.

### Out of scope

- Editing any cheatsheet's content, metadata, or cross-links (the graph is read, not shaped, in this pass).
- Server configuration, nginx rewrites, pretty URLs for categories (`?cat=` is fine; revisit if Search Console shows the pages indexing poorly).
- A CMS, database, login, or any write path other than `subscribe.php`.
- Deployment. Commit and push to `origin` under repository policy; production deploy needs David's explicit go-ahead.

### Anti-goals

- No framework, no icon font, no web fonts, no new CDN dependency (which also means no SRI to maintain on this page).
- No autoplaying or continuous animation anywhere.
- No `backdrop-filter`, no fixed animated backgrounds.
- No "AI recommends" or "personalised for you" language; recommendations are graph edges, popularity, and hand-written paths, and the UI says so.
- No infinite scroll; 197 cards render at once, filtered in place.
- Map is never the default lens, on any device.
- Nothing on the page states or implies a review date on a sheet's behalf beyond the `reviewed` dot backed by `refresh-status.json`.
- No em dashes in any copy on the page.

## Phasing

Each phase ships as its own commit set, pushed to `origin`, reviewed by David, deployed by David.

| Phase | Deliverable | Suggested model |
|---|---|---|
| 0. Data | `scripts/build_catalog.py` with unit tests on 5 representative sheets (`fastener-torque-tap-drill`, `ai-frontier`, `judo`, `linux-server-hardening`, `shabbat-services-cheatsheet`); `catalog.json`; `paths.json` with the 11 drafts; `catalog-overrides.json` if needed; `.githooks/pre-commit`; `deploy.py --check` gate; nightly workflow step; retire `generate-metadata.py`. Docs: `docs/content.md` step 6 "run the catalog builder (or let the hook)", `AGENTS.md` routing row, `deploy/DEPLOY.md` gate note. | Sonnet |
| 1. Explorer core | `index.php` rewrite: Chart Room identity, theming, Grid + facet rail, palette, drawer, Pulse, serendipity, category landing pages, `sitemap.php` category URLs, `seo_check.py` coverage of the index, signup/CTA moves. Bootstrap removed. | Opus |
| 2. Map and Paths | Layout precompute in the builder; canvas renderer; ego-graph mobile mode; list equivalent; Paths lens with progress. | Opus |
| 3. Polish | `scripts/render_og_map.py` (headless Chromium via the existing `scripts/shot.py` pattern) producing `images/cheatsheets-og-portfolio.png` from the map; `fetch-popularity.py` gains a 30-day per-file daily ring buffer so the drawer can show a per-sheet sparkline; `llms.txt` catalog line; screenshot-based visual regression of the three lenses at 375 and 1440 px. | Sonnet |

Implementer's outline-first rule (`TODO/README.md` Rule 2) applies: before writing `index.php`, produce the DOM outline, the token list, the URL-state table, and the event list, and check them against this spec.

## Definition of done

In addition to `AGENTS.md` and `TODO/README.md` Rule 3:

- Typing `torque` in the palette lists `Bolt Torque & Tap Drill Chart` with a section row that opens `fastener-torque-tap-drill.html#torque` directly (that sheet has 20 `<section id>` anchors and 11 `h2`s). Typing `ukemi` finds the judo sheet via its `Ukemi (Breakfalls) & Movement` heading even though the sheet has no `h2`, `h3`, or `h4`; the row is shown unlinked because that heading carries no id.
- With JavaScript disabled: the full grid renders, every facet link works, `?cat=Radio` shows only Radio sheets with a Radio-specific title and description, `?sheet=judo.html` shows the judo detail block, and the signup form posts.
- With `catalog.json` deleted: the page renders one plain banner naming the build command; no PHP warnings.
- `curl -s https://cheatsheets.davidveksler.com/?cat=Radio | grep '<title>'` returns `Radio Cheatsheets (5) | David Veksler` (count as of build).
- `php -l index.php` passes; `python scripts/deploy.py --check` passes including the new catalog-freshness gate; `python scripts/seo_check.py` passes on the rendered index and every category page.
- Lighthouse mobile on the live index: Performance ≥ 95, Accessibility ≥ 95, SEO 100; no `backdrop-filter` or infinite animation in the CSS (grep).
- Both themes render correctly at 375, 768, and 1440 px; the Map lens at 1440 px shows labels only for the top 25 and the hubs; hovering a node dims the rest; the mobile ego graph appears under 768 px.
- All 11 paths validate; marking a step done persists across reload; a broken filename in `paths.json` fails the build with the offending id.
- Every `explorer_*` event fires exactly once per action (verified in the GA4 DebugView or by stubbing `gtag`).
- No em dashes in the rendered page (grep for `—` and `&mdash;`).

## Volatile facts and staleness register

| Item | Rots when | Guard |
|---|---|---|
| Counts in title, lead, Pulse | Every new sheet | Template variables from the catalog; never literals except the title's "190+" style round-down, which the builder warns about when it becomes wrong |
| Path step filenames | Sheet renamed or removed | Build fails |
| Category hue table | New category added to `category-map.php` | Builder warns on a category with no hue; page falls back to `Other` hue |
| Shape heuristics | New sheet styles | Re-tune when more than 10% of sheets fall to plain `reference` |
| Map layout | Every build | Drift check in the builder (median move under 5% with unchanged edges) |
| Popularity junk paths | Continuously | Always filter scores through the catalog |
| Rating | SLOW-DRIFT | Data-driven page; the only hand-written volatile content is `paths.json` |

## Open decisions for David (each has a recommendation; implementation proceeds on the recommendation unless told otherwise)

1. **Drop Bootstrap and the icon font from the index?** Recommend yes. The index is not a sheet, so the "do not rewrite existing Bootstrap sheets" rule does not bind, and the payload cut is the cheapest LCP win available.
2. **Keep the Microsoft Clarity tag?** Recommend keep for the first 30 days after launch to watch palette and map usage as heatmaps, then decide.
3. **Make `?cat=` pages indexable?** Recommend yes, with self-canonical and sitemap entries.
4. **Which of the 11 draft paths ship, and in what wording?** Recommend shipping all 11 as drafted, then editing `paths.json` in place; it is a data file, not code.
5. **Title framing.** The current title leads with the pipeline ("Governed Agentic-AI Output at Scale"). The draft leads with the content and lets the Pulse strip make the case-study argument. Recommend the draft; the pipeline story keeps its own page.
