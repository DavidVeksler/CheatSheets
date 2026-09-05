# Content quick path — add / edit / publish a cheatsheet

Front-to-back index for producing content. This is a thin router: the binding
rules live in [`../AGENTS.md`](../AGENTS.md) and [`../TODO/README.md`](../TODO/README.md).
Where this file and AGENTS.md disagree, AGENTS.md wins.

## Where content lives

- **Cheatsheets** are standalone `.html` files in the **repo root** (lowercase, hyphens,
  e.g. `linux-server-hardening.html`). Each is fully self-contained (embedded CSS/JS).
- **Specs** for planned pages live one-per-file in [`../TODO/`](../TODO) as `<topic>.md`,
  deleted after the build ships.
- `index.php` (gallery) and `sitemap.php` auto-discover root `.html`; `images/{filename}.png`
  holds the 1200x630 preview. There is **no build step**.

## Create a cheatsheet (summary — full steps in AGENTS.md)

1. **Research first**, then outline to three depths, then fill to the density floor
   (Generation Protocol + Content Comprehensiveness Standard in AGENTS.md).
2. Write `topic-subtopic.html` in root using the Modern Platform Baseline and **all**
   metadata blocks (title, meta description, canonical, OG/X, TechArticle JSON-LD).
   JSON-LD must match visible content — do not add a `dateModified` field or a visible
   "Last verified" line (review status lives in `refresh-status.json`, not the page).
3. Add the file to the `$categoryMap` array in `category-map.php`, or it lands under "Other"
   (AGENTS.md > *Adding New Cheatsheets*).
4. Regenerate `catalog.json`: run `python3 scripts/build_catalog.py`, or let the tracked
   `.githooks/pre-commit` hook do it for you and stage the result automatically. Enable
   the hook once per clone with `git config core.hooksPath .githooks` (see *The gate
   that must pass* below). `catalog.json` is the data layer behind the index's search,
   map, and facets; a commit that adds a new `.html` or an entry to `category-map.php`
   without also updating `catalog.json` fails the deploy gate (`scripts/deploy.py --check`).
5. Generate + optimize the `images/{filename}.png` preview.
6. Commit the `.html` + its `images/*.png` + `catalog.json` by explicit path. One
   cheatsheet per commit.

Reviewing an existing page: run [`../TODO/CHEATSHEET-AUDIT.md`](../TODO/CHEATSHEET-AUDIT.md).
Writing/reviewing a spec: [`../TODO/SPEC-AUDIT.md`](../TODO/SPEC-AUDIT.md).

## Build + QA locally

No build step — serve the static files and verify in a real browser
(AGENTS.md > *Build & Verify Workflow*):

```bash
python3 -m http.server 8765     # then load http://127.0.0.1:8765/<file>.html
```

Assert: console clean (a `favicon.ico` 404 is the only allowed error), any CDN
framework loaded (e.g. for Bootstrap, `typeof window.bootstrap !== 'undefined'` so
a bad SRI hash can't pass silently), interactive bits work, light + dark themes
both render. (Design approach is a free choice now — see AGENTS.md > *Design
approach*; Bootstrap is one option, not a requirement.)

For the annually refreshed economics comparison batch, run
`python scripts/build_economics_batch.py`; source vintages and fallback behavior are
documented in [`economics-data-refresh.md`](economics-data-refresh.md).

## The gate that must pass

- **SEO gate** — `scripts/seo_check.py` on changed `.html`: title <= 60 chars, meta
  description 150-200, canonical present, valid JSON-LD.
- **Link/asset integrity, JSON parse, `php -l`** — also run by the deploy validator.
- **Catalog freshness**: `python scripts/build_catalog.py --check` fails if `catalog.json`
  is older than any catalogued `.html`, `category-map.php`, `paths.json`, or
  `catalog-overrides.json`, or if a `paths.json` step points at a file that no longer
  exists. Part of `scripts/deploy.py --check`.
- **`.githooks/pre-push`** guards the `production` remote only (it runs
  `python scripts/deploy.py --check`). Pushes to `origin` are **not** blocked.
- **`.githooks/pre-commit`** regenerates `catalog.json` (and stages it) whenever a staged
  change touches a catalogued `.html`, `category-map.php`, `paths.json`, or
  `catalog-overrides.json`, so the freshness gate above almost never fires locally.
- Enable both hooks once per clone with `git config core.hooksPath .githooks`.

## Who deploys

- **You**: commit and push to `origin` without asking (commits are the backup).
- **David deploys.** Deploy is the guarded pipeline `./deploy.sh` (`./deploy.ps1` on
  PowerShell), which pushes `main` to the `production` remote (`git push production main`).
  Never run a deploy script, push to `production`, or purge caches without his go-ahead.
  Full runbook: [`../deploy/DEPLOY.md`](../deploy/DEPLOY.md).
