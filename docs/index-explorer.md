# Index Explorer runbook

`index.php` is the Explorer: one page, one generated catalog, three lenses (Grid, Map, Paths) over every catalogued sheet.

## Data flow

```
*.html + category-map.php + paths.json + catalog-overrides.json (optional)
        │
        ▼
scripts/build_catalog.py   (BeautifulSoup parse, git dates, shape heuristics,
        │                    force-directed map layout, inputs_hash)
        ▼
catalog.json                (committed, ~350 KB)
        ├─► index.php        server-renders Grid + facet rail + Pulse + category hub pages
        │                    (/<slug>, copy from category-hubs.json; routed by
        │                    conf/nginx/category-hubs.conf, locally scripts/dev_router.php);
        │                    inlines "catalog-lite" JSON; lazy-fetches catalog.json on first
        │                    palette/map/drawer open
        ├─► scripts/render_og_map.py   Map lens screenshot → images/cheatsheets-og-portfolio.png
        └─► scripts/deploy.py --check  fails if catalog.json is stale (inputs_hash) or
                                        paths.json names a file not in the catalog

popularity.json (fetch-popularity.py, nightly, Cloudflare Analytics)
        └─► Pulse strip (site sparkline, trending) + drawer per-sheet sparkline
```

## On Cloudflare Workers (from cutover)

`index.php` is no longer run per request: `scripts/build_site.py` prerenders it with PHP CLI (default view, paths lens, each curated path, each hub) and the site Worker (`workers/site/index.js`) picks the document per URL, adds `noindex` for client-state params and the `?sheet=` head, and 301s `?cat=`/`?category=`/`?hub=`. Filters, sorts and the lens in a URL are applied by the page script on load. Time-relative bits (deep cut of the day, NEW badges) refresh with the daily popularity publish. The referrer history below needs origin logs and ends at cutover (D-2). Spec: [`specs/cloudflare-migration.md`](specs/cloudflare-migration.md).

## The catalog builder

`catalog.json` holds per sheet: title, description, keywords, image, category (`category-map.php`), section headings with anchor ids, outbound links to other sheets (graph edges), multi-valued `shape`, word/table/section counts, git `created`/`updated`, `reviewed` (from `refresh-status.json`), map `x`/`y`. Collection level: category counts, light/dark hue pairs, edge list, `stats`.

```bash
python3 scripts/build_catalog.py                # rebuild
python3 scripts/build_catalog.py --check        # freshness + paths.json gate, no write
python3 scripts/build_catalog.py --print-hues   # category hue table
```

Rebuilt by `.githooks/pre-commit` (see [`../deploy/DEPLOY.md`](../deploy/DEPLOY.md)) and nightly by `.github/workflows/update-popularity.yml`, so `reviewed`/`updated` stay current without commits.

**Shapes:** `comparison` (2+ tables or a 9+-row table), `procedure` (8+ checkboxes), `calculator`, `tracker`, `commands`, `device`, `essay` (2,900+ words, under 2 tables), `timeline`, `visual`; no match falls back to `reference`. Keep the `reference` share ≤ 10% (the builder warns on stderr); tune thresholds in `compute_shapes()` first.

**`catalog-overrides.json`** (optional, not present today): `{"file.html": {"shape": [...], "hide": true, "featured": true}}`. Only for a genuine one-off heuristic misfire.

## `paths.json`: adding a curated path

Hand-authored:

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

Every step's `file` must be a catalogued sheet (the build and `--check` fail with the path id and filename otherwise). Most sheets need no entry; add one only for a genuine ordered trail. Paths render only in the Paths lens (`?view=paths`): a trail is ~15 KB, too much for every page view. `?path=` is a real navigation (server-rendered stepper), not `pushState`.

## OG preview

`?og=1` render mode (Map lens, dark theme, no chrome, 1200x630 canvas, top 12 sheets labeled by popularity, live-count caption); never linked, always `noindex`. Commands in [`marketing.md`](marketing.md) > *Social preview image (OG)*.

## Per-sheet popularity history

`fetch-popularity.py` writes `popularity.json` `dailyHistory`: a 30-day rolling `{"<file>": {"<ISO date>": views}}` buffer, computed by `accumulate_daily_history()` (tested in `scripts/test_fetch_popularity.py`, no Cloudflare credentials needed). The drawer and `?sheet=` detail block show a 30-point sparkline only once a sheet has 7+ days of history, never a placeholder.

## Referrer history

Cloudflare Free has no referrers and logrotate keeps ~3 weeks of nginx logs, so `scripts/referrer_accumulate.py` runs nightly **on the server** (cron below) and folds every complete day still in the logs into `.referrers.json` in the docroot (gitignored; `^~ /.` 404s it over HTTP). Same human filter and channel rules as `scripts/referrer_report.py` (it imports `read_hits()`/`classify()`). Per day: landings per channel, top 50 sources and top 30 landing paths per channel; no IPs, no referrer paths, private-network hosts collapsed. A day is written once, so missed nights backfill on the next run; retention ~5 years (~40 KB/month). Tests: `python3 -m unittest scripts.test_referrer_accumulate`.

`popularity.php` > *Where readers come from* renders it: last-N vs prior-N channel mix (N = 30 days once the store holds 60), weekly referred-landing bars by channel (direct excluded), top sources with a `new` flag (first seen in 14 days), landing pages per channel. Search counts in the logs run above GSC clicks; take search volume from GSC.

Cron (johngalt, after `cheatsheets-pull.sh` at 04:00; server clock is UTC):

```
20 4 * * * cd /var/www/cheatsheets.davidveksler.com/htdocs && /usr/bin/python3 scripts/referrer_accumulate.py >> .git/referrers.log 2>&1
```

The store lives only on the server. Losing it loses history older than the logs; recover the last ~3 weeks by re-running the script.

## Standing design rules

- The index has no CDN dependency (no Bootstrap, no icon font); the "don't rewrite Bootstrap sheets" rule does not apply to it.
- Icons on all PHP pages come from `chrome_icon()` in `lib/chrome.php` (inline SVG, 16-grid, 1.5px stroke, `currentColor`); the drawer gets its few as a `#icons` JSON block. Cards carry no icons beyond the info button (every card byte is paid once per sheet).
- Microsoft Clarity tag stays (heatmaps of palette and map use).
- Category hub pages are indexable; see [`marketing.md`](marketing.md) > *Category hub pages*.
- Map hub labels use out-degree, not total degree (total degree would label most of the map).
- `catalog-lite` omits map `x`/`y` and titles (titles are read from rendered cards).
- The map/paths inline script is a plain `<script>` at the end of `<body>`; `defer` is ignored on inline scripts.
- Page budgets (targets): HTML ≤ 200 KB raw / 45 KB gzip, inline CSS ≤ 20 KB, inline JS ≤ 25 KB, `catalog.json` ≤ 350 KB, map redraw < 8 ms. At ship HTML/CSS/JS ran over and were accepted because Lighthouse mobile and Core Web Vitals passed; re-measure before quoting.
