# Spec: hosting built apps (multi-file projects) on the cheatsheets site

Status: proposed 2026-10-06. First app: `m87-descent` (today a separate Worker at `m87.davidveksler.com`).

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

The only supported way to update an app. It runs from CheatSheets and reads `apps/<slug>/app.json` to find the source repo:

```json
{
  "slug": "m87-descent",
  "repo": "~/Projects/m87-descent",
  "github": "https://github.com/DavidVeksler/m87-descent",
  "commit": "<source sha the copy was built from>",
  "built": "2026-10-06",
  "drop": ["robots.txt", "sitemap.xml", "llms.txt"]
}
```

Steps (fail closed at every step):

1. Source repo tree is clean. Note its HEAD sha.
2. In the source repo, run `npm run check` with the base set (`APP_BASE=/apps/<slug>/`).
3. Clear `apps/<slug>/` except `app.json`, then copy `dist/` into it, leaving out the `drop` files (the site has its own robots, sitemap and llms). Move `dist/index.html` to `<slug>.html` at the root.
4. Update `commit` and `built` in `app.json`.
5. Run `scripts/check_apps.py`, then `build_catalog.py`.
6. Commit as `App sync: <slug> @ <short sha>`.

It doesn't deploy. Deploying is still `scripts/deploy-cloudflare.sh` with David's go-ahead.

## Gate: `scripts/check_apps.py`

Add to `build_site.py` gates and to `deploy.py --check`. For every `apps/<slug>/app.json`:

- `<slug>.html` exists at the root, is in `category-map.php`, and carries the required metadata template (canonical `https://cheatsheets.davidveksler.com/<slug>.html`, OG/Twitter, JSON-LD).
- Every `src`/`href` in the entry page that points at `/apps/...` points inside `/apps/<slug>/` and to a file tracked in git.
- No root-absolute URL outside `/apps/<slug>/` other than the site's own pages. This catches a forgotten `fetch('/foo.json')` in the source.
- Nothing in `apps/<slug>/` is unreferenced except `app.json`. Built JS can fetch runtime files (audio, a lookup table), so the gate also accepts anything listed in a `runtime` array in `app.json`.

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

## m87-descent migration

In the **m87-descent repo**:

1. `vite.config.ts` with `base: process.env.APP_BASE ?? '/'`. Replace the two root-absolute fetches with `import.meta.env.BASE_URL`: `src/main.ts:48` (`/blackbody.json`) and `src/audio/soundscape.ts:46` (`/audio/<name>.mp3`).
2. `index.html` head: canonical and JSON-LD URL become `https://cheatsheets.davidveksler.com/m87-descent.html`. Add OG/Twitter tags, `og:image` = `images/m87-descent.png`, and `creditText` per the AGENTS.md template.
3. `scripts/qa-server.ts`: when `APP_BASE` is set, set `QA_URL` to the base path (Vite preview serves under `base`).
4. Retire its own Cloudflare deploy: `docs/deployment.md` points to `sync_app.py`, and `scripts/deploy-cloudflare.*` is removed or made to refuse. Drop `public/robots.txt`, `public/sitemap.xml` and `public/llms.txt`, or leave them to the `drop` list.

In **CheatSheets**:

5. `scripts/sync_app.py`, `scripts/check_apps.py`, `apps/m87-descent/app.json`, and the `_headers` rule.
6. `category-map.php`: `'m87-descent.html' => 'Engineering & Science'`.
7. `images/m87-descent.png`: a 1200x630 crop of a reviewed golden view (`m87-descent/tests/golden/`).
8. Contextual links: `stellar-lifecycle.html` black hole section ("Fly into one"), plus llms.txt / llms-full.txt entries.
9. `catalog-overrides.json` shape `["visual", "calculator"]` if the heuristics misfire (likely, since the page has few tables or words).

**Subdomain retirement** (deployment-gated; do after the CheatSheets deploy is live):

10. `m87.davidveksler.com/*` → 301 to `https://cheatsheets.davidveksler.com/m87-descent.html` as a zone Single Redirect rule (the house pattern for aliases). Then delete the `m87-descent` Worker and its custom-domain DNS record. It launched on 2026-10-06, so it has almost no link equity to lose.
11. Remove it from `deploy-sites.json` and `cf-static-kit/sites.json` if listed. Note it in `docs/seo-progress.md` of both repos.

## Open questions

- Slug/URL: `m87-descent.html` (matches the repo) vs a search-led name like `black-hole-flight-simulator.html`. The title already carries the keywords, and renaming later costs a redirect.
