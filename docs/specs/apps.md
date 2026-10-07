# Spec: hosting built apps (multi-file projects) on the cheatsheets site

Procedure: [`../apps.md`](../apps.md) (the runbook wins on steps; this file holds the design and rationale).

Status: implemented 2026-10-06. First app: `black-hole-flight-simulator` (source repo `m87-descent`, previously its own Worker at `m87.davidveksler.com`).

## Problem

Most sheets are one self-contained `.html` file with no build step. Some projects can't work that way: m87-descent is a TypeScript/Vite/WebGL2 app with its own tests, browser QA, a 3D renderer and audio files, about 780 KB once built. Inlining it into one file (base64 audio, a 300 KB script) would hurt caching and make the source unreadable. Keeping it in its own repo and on its own subdomain splits its SEO from the site and leaves it out of the Explorer, hubs, sitemap and popularity tracking.

## Decision

An **app** keeps its source, tests and QA in its own repo. CheatSheets keeps a **built copy**, split in two:

| Piece | Path in this repo | Public URL |
|---|---|---|
| Entry page (the built `index.html`) | `<slug>.html` (repo root, like every sheet) | `/<slug>.html` |
| Hashed JS/CSS, audio, data | `apps/<slug>/...` | `/apps/<slug>/...` |
| Provenance manifest | `apps/<slug>/app.json` | not linked |

The entry page sits at the root with the other sheets, so everything that finds sheets by the top-level `*.html` glob picks it up unchanged:

- `build_catalog.py`: Explorer card, map node, hub listing via `category-map.php`
- `sitemap.php`
- `fetch-popularity.py` (only counts top-level `.html`)
- `seo_check.py`
- the site Worker: `html_handling: "none"` serves `/<slug>.html` as is, so no Worker change and no `run_worker_first` entry

The app is built with Vite `base: '/apps/<slug>/'`, so the entry page refers to its assets with absolute `/apps/<slug>/...` URLs, which resolve from the root.

The built copy is committed (vendored). The deploy pipeline and the daily popularity Action then never need the app's repo or Node: `build_site.py` already copies `git ls-files` into `dist/`, and `apps/` isn't in `INTERNAL_DIRS`.

### Rejected

- **Inline into one file** (vite-plugin-singlefile): about 1 MB of HTML with base64 audio, nothing cached between visits, and the 30-minute `.html` cache would re-download it all.
- **Git submodule + build at deploy time**: puts Node, the app's npm tree and its test suite into every CheatSheets deploy and the popularity Action. That's fragile, and the build wouldn't be reproducible from this repo alone.
- **Keep the subdomain, link out**: the user chose to fold it in. It would also need new catalog code for entries that aren't files.
- **Serve the app at `/<slug>/`** (a directory index): with `html_handling: "none"`, `/m87-descent/` returns 404. It would need Worker routing and a new kind of catalog entry, and gain nothing.

## The sync script: `scripts/sync_app.py <slug>`

The only supported way to update an app (`--skip-qa`, `--no-commit` available). It reads `apps/<slug>/app.json`:

```json
{
  "slug": "black-hole-flight-simulator",
  "repo": "~/Projects/m87-descent",
  "github": "https://github.com/DavidVeksler/m87-descent",
  "commit": "<source sha, written by the script>",
  "built": "<date, written by the script>",
  "qa": ["check", "qa:build"],
  "drop": [],
  "runtime": ["blackbody.json", "audio/*.mp3", "audio/manifest.json"]
}
```

Fail closed, in order: source tree clean; no uncommitted changes to `<slug>.html` / `apps/<slug>/` here; each `qa` npm script in the source repo with `APP_BASE=/apps/<slug>/`; built page has the cheatsheets canonical and the base; replace `apps/<slug>/` (keeping `app.json`, skipping `drop`), write `dist/index.html` to `<slug>.html`, record commit and date; `check_apps.py`; commit `App sync: <slug> @ <sha>`. It never deploys.

The source repo must take its base from `APP_BASE` (Vite `base`) and build every runtime URL from `import.meta.env.BASE_URL`, never a root-absolute literal. Its QA must run under the base: Vite preview only serves the base path, so a stray `/foo.json` fails QA.

## Gate: `scripts/check_apps.py`

Add to `build_site.py` gates and to `deploy.py --check`. For every `apps/<slug>/app.json`:

- `<slug>.html` exists at the root, is in `category-map.php`, and carries the required metadata template (canonical `https://cheatsheets.davidveksler.com/<slug>.html`, OG/Twitter, JSON-LD).
- Every `src`/`href` in the entry page that points at `/apps/...` points inside `/apps/<slug>/` and to a file tracked in git.
- No root-absolute URL outside `/apps/<slug>/` other than the site's own pages. This catches a forgotten `fetch('/foo.json')` in the source.
- Nothing in `apps/<slug>/` is unreferenced except `app.json`. Built JS can fetch runtime files (audio, a lookup table), so the gate also accepts anything listed in a `runtime` array in `app.json`.
- `app.json` records a 40-hex source commit.

Other gates: `add_hub_breadcrumbs.py` skips app entry pages (the source page carries its own BreadcrumbList and hub link, and a sync would overwrite an injected block). `build_site.py` never publishes `apps/*/app.json`.

## Rules for an app's entry page (exceptions to the sheet invariants)

| Invariant | For apps |
|---|---|
| Single self-contained file | Waived: assets live under `apps/<slug>/`. |
| SRI on CDN assets | Still applies; vendored same-origin bundles need none. |
| Metadata template, SEO gate | Applies in full. The source repo's `index.html` carries the cheatsheets head (canonical, OG, Twitter, JSON-LD `author`/`creditText`). |
| `light-dark()`, accordions, `@layer` | Waived where the app's UI is immersive (a WebGL cockpit). Landmarks, focus-visible, reduced motion, contrast and keyboard access still apply. |
| `localStorage` | Keys namespaced by slug (m87 already uses `m87-*`), since all apps share one origin. |
| Core bar ("terminal reference") | An app is an interactive explainer. Its entry page should have some readable explanatory text (the m87 About panel) so it isn't an empty shell for crawlers. |

Headers: add `/apps/*/assets/*` → `Cache-Control: public, max-age=31536000, immutable` to `deploy/cloudflare/_headers` (Vite puts a content hash in those filenames). Unhashed runtime files (audio, LUT) get the default.

## First app: black-hole-flight-simulator (done 2026-10-06)

- m87-descent repo: `vite.config.ts` base from `APP_BASE`; LUT and audio fetches use `BASE_URL`; QA URL includes the base; head retargeted to `https://cheatsheets.davidveksler.com/black-hole-flight-simulator.html` (title, OG/Twitter, WebApplication + BreadcrumbList + FAQPage JSON-LD); keyword H1; sourced numbers and an FAQ in the About dialog; own Cloudflare deploy scripts now refuse; `verify-live.mjs` checks the CheatSheets URL.
- CheatSheets: `category-map.php` (Engineering & Science), `images/black-hole-flight-simulator.png`, links from `stellar-lifecycle.html`, the engineering-science hub intro, llms.txt / llms-full.txt.

**Subdomain retirement, pending David's go-ahead:** `m87.davidveksler.com/*` → 301 to the CheatSheets URL (zone Single Redirect rule), then delete Worker `m87-descent` and its custom domain. Until then the subdomain serves the last build, canonical to itself.
