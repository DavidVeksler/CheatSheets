# Index Explorer — runbook

`index.php` is the Explorer: one page, one generated catalog, three lenses (Grid, Map,
Paths) over the same 197 sheets. This is the durable reference for how it is built and how
to extend it, written when `TODO/index-explorer-redesign.md` (the implementation spec) shipped
and was deleted per [`TODO/README.md`](../TODO/README.md)'s "a shipped spec is deleted" rule.

## Data flow

```
*.html + category-map.php + paths.json + catalog-overrides.json
        │
        ▼
scripts/build_catalog.py   (BeautifulSoup parse, git dates, shape heuristics,
        │                    force-directed map layout, inputs_hash)
        ▼
catalog.json                (committed; ~350 KB)
        │
        ├─► index.php        server-renders Grid + facet rail + Pulse + category
        │                    landing pages; inlines a "catalog-lite" JSON for instant
        │                    client-side filtering; lazy-fetches catalog.json itself
        │                    on first palette/map/drawer open for headings/outlinks/edges
        │
        ├─► scripts/render_og_map.py   headless-Chromium screenshot of the live
        │                              Map lens → images/cheatsheets-og-portfolio.png
        │
        └─► scripts/deploy.py --check  fails the deploy if catalog.json is stale
                                        (inputs_hash mismatch) or paths.json references
                                        a file not in the catalog

popularity.json (fetch-popularity.py, nightly, Cloudflare Analytics)
        │
        └─► index.php's Pulse strip (site-wide sparkline, trending) and the drawer's
            per-sheet sparkline (dailyHistory, a 30-day rolling ring buffer per file)
```

### The catalog builder (`scripts/build_catalog.py`)

Scans every catalogued `.html` file and writes `catalog.json`: title, description,
keywords, image, category (from `category-map.php`), section headings (with deep-link
anchor ids where the heading or its enclosing `<section>` has one), outbound links to
other catalogued sheets (the graph edges), a multi-valued `shape` (see below), word/table/
section counts, git-derived `created`/`updated` dates, `reviewed` (from
`refresh-status.json`), and a precomputed `x`/`y` map position. Collection-level: category
counts and light/dark hue pairs, the edge list, and `stats` (sections indexed, edge count).

Run it after any change to a catalogued `.html`, `category-map.php`, `paths.json`, or
`catalog-overrides.json`:

```bash
python3 scripts/build_catalog.py            # rebuild catalog.json
python3 scripts/build_catalog.py --check    # freshness + paths.json gate only, no write
python3 scripts/build_catalog.py --print-hues   # print the light/dark category hue table
```

`.githooks/pre-commit` runs the builder automatically when a staged change touches one of
those inputs, and stages the result — enable it once per clone with
`git config core.hooksPath .githooks`. `scripts/deploy.py --check` re-runs `--check` so a
commit made without the hook enabled still fails closed rather than shipping a stale
catalog. The nightly `update-popularity.yml` workflow also rebuilds it, so `reviewed` and
`updated` stay current even on nights nobody commits.

### Shape heuristics

Every sheet gets zero or more of: `comparison`, `procedure`, `calculator`, `tracker`,
`commands`, `device`, `essay`, `timeline`, `visual`. A sheet matching none of these falls
back to plain `reference`. The spec set a 10% ceiling on that fallback share; corpus tuning
in Phase 3 (inspecting the 36/197 sheets that fell to `reference` at launch) lowered three
thresholds — comparison now fires on 2+ tables or a 9+-row table (was 3 tables / 12 rows),
procedure on 8+ checkboxes (was 10), essay on 2,900+ words with under 2 tables (was 4,000 —
see the dated comments in `compute_shapes()` in `build_catalog.py` for the corpus evidence
behind each number. Re-tune again if a future corpus pushes the `reference` share back over
10% (the builder prints a warning to stderr when it does); `catalog-overrides.json` can also
set `shape` per file for a genuine heuristic misfire without touching the general rule.

### `catalog-overrides.json`

Optional, per-file: `{"file.html": {"shape": [...], "hide": true, "featured": true}}`.
Used sparingly — fix the heuristic first, override only for a genuine one-off.

### `paths.json` — adding a curated path

Hand-authored, not generated. Format:

```json
{
  "paths": [
    {
      "id": "harden-a-linux-box",
      "title": "Harden a Linux box",
      "promise": "A fresh server to a monitored, key-only, patched box, in the order that keeps you from locking yourself out.",
      "steps": [
        {"file": "linux-server-hardening.html", "why": "SSH keys and the firewall before anything else touches the network."},
        {"file": "ubuntu-linux-for-ai-developers.html", "why": "The daily commands and package setup once the box is locked down."}
      ]
    }
  ]
}
```

Every step's `file` must be a catalogued sheet; the builder validates this on every run
(`--check` and a full build) and fails with the offending path id and filename if not — a
sheet rename can no longer silently break a trail. Most new sheets need no path entry at
all (see `docs/content.md`'s create-a-cheatsheet steps); add one only when the sheet is
part of a genuine multi-step trail a reader would follow in order. `index.php` renders
paths only inside the Paths lens (`?view=paths`), not on Grid or Map, because each trail's
full step list is too much markup (~15 KB) to pay for on every page view.

### OG social preview (`scripts/render_og_map.py`)

`images/cheatsheets-og-portfolio.png` is a live screenshot of the Map lens, not a static
graphic — see `docs/marketing.md` > "Social preview image (OG)" for the regeneration
command and when to re-run it. It works by adding a minimal `?og=1` render mode to
`index.php` (forces the Map lens and dark theme, hides all chrome, fixes the canvas at
1200x630, labels only the top 12 sheets by popularity, and overlays a caption with the
live counts) that a real visitor never sees a link to and that is always `noindex`.

### Per-sheet popularity history

`fetch-popularity.py`'s nightly run writes `popularity.json`'s `dailyHistory` key — a
30-day rolling `{"<file>": {"<ISO date>": views}}` ring buffer per catalogued `.html` file,
pure-computed by `accumulate_daily_history()` (unit-tested in
`scripts/test_fetch_popularity.py` with synthetic counts; it needs no Cloudflare
credentials to test). `index.php` renders a 30-point sparkline from it in the drawer and
the server-rendered `?sheet=` detail block, but only once a sheet has 7+ days of recorded
history — never a placeholder for a thinner history. The structure is seeded from the
`dailyViews` snapshot that already existed in `popularity.json` on this feature's first
run, so the sparkline is not empty for a full 30 days after shipping.

## Open decisions (from the implementation spec) — all recommendations taken

1. **Drop Bootstrap and the icon font from the index?** Yes. The index carries no CDN
   dependency; the "do not rewrite existing Bootstrap sheets" rule in `AGENTS.md` never
   applied to it (it isn't a cheatsheet).
2. **Keep the Microsoft Clarity tag?** Kept, unchanged, for heatmap visibility into palette
   and map usage.
3. **Make `?cat=` pages indexable?** Yes — self-canonical, own title/description/JSON-LD,
   listed in `sitemap.php` and `llms.txt`.
4. **Which of the 11 draft paths ship?** All 11, as drafted; `paths.json` is a data file
   David can edit directly without a code change.
5. **Title framing.** The content-first draft shipped (`Cheatsheets by David Veksler:
   Explore 190+ References`), not the pipeline-first original; the Pulse strip carries the
   case-study argument instead.

## Measured budgets (Phases 1-2, at ship)

| Budget | Target | Measured |
|---|---|---|
| HTML document, uncompressed | ≤ 200 KB | 218 KB |
| HTML gzipped | ≤ 45 KB | 54 KB |
| Inline CSS | ≤ 20 KB | 24.8 KB |
| Inline JS (two blocks) | ≤ 25 KB | 42.7 KB |
| `catalog.json` (lazy) | ≤ 350 KB | 348 KB |
| Map redraw | < 8 ms at 1440x900 | 0.5 ms |

The HTML/CSS/JS numbers ran over their original per-budget-line targets; they were
accepted at ship because the numbers that actually gate a release — Lighthouse mobile
Performance/Accessibility/SEO and Core Web Vitals — passed. Phase 3 added a small amount to
both JS blocks (the `?og=1` label-count branch, the drawer sparkline) and a `daily-history`
inline JSON block that costs about 2 bytes today (`{}`) and grows as `popularity.json`
accumulates history; re-measure before treating these numbers as current.

## Recorded deviations from the original spec

- **Map hub labels use out-degree, not total degree.** 144/197 sheets have total degree
  12+ (one node has 177); the spec's literal per-degree rule would have labeled three
  quarters of the map. Out-degree gives 13 hubs, matching the spec's own prose ("the hubs
  have 15 to 22").
- **`?path=` is a real navigation, not a `pushState`.** The server already renders the
  opened stepper, so the client never needs to fetch `paths.json`, and Back works for free.
- **Paths render only inside the Paths lens**, not appended under Grid/Map — a trail's full
  step list is ~15 KB, too much to pay on every page view.
- **The map/paths inline script block is a plain `<script>`, not `<script defer>`** at the
  end of `<body>`: HTML ignores `defer` on an inline classic script, so the ordering the
  split buys (after the main block, after the DOM) is what actually matters, not the
  attribute.
- **`catalog-lite` (the inline JSON every page load pays for) omits `x`/`y` map
  coordinates and titles.** Titles are read off the already-rendered cards instead of
  duplicated (~11 KB saved); coordinates are only needed once the Map lens's `edges` are
  loaded anyway, so adding 197 coordinate pairs to every page load bought nothing.
