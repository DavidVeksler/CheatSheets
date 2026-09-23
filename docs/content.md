# Content quick path: add / edit / publish a cheatsheet

Thin router. Binding rules: [`../AGENTS.md`](../AGENTS.md) (quality protocol, invariants, metadata template) and [`../TODO/README.md`](../TODO/README.md) (specs). AGENTS.md wins on conflict.

## Where content lives

- Sheets: standalone `.html` in the repo root (lowercase, hyphens, e.g. `linux-server-hardening.html`).
- Specs: one `TODO/<topic>.md` per planned sheet, deleted after it ships.
- Preview image: `images/<filename>.png`, 1200x630.
- `index.php` renders from `catalog.json`; `sitemap.php` auto-discovers root `.html`. No build step.

## Create a sheet

1. Research, outline to three depths, fill to the density floor (AGENTS.md > *Generation & quality protocol*).
2. Write `topic-subtopic.html` in root per AGENTS.md > *Tech baseline* with the full *Required metadata template*. JSON-LD must match visible content; no `dateModified`, no "Last verified" line.
3. Add it to `$categoryMap` in `category-map.php` (else it lands under "Other"). Then run `python3 scripts/add_hub_breadcrumbs.py` so it links back to its hub (gated at deploy).
4. Regenerate `catalog.json` (`python3 scripts/build_catalog.py`, or let `.githooks/pre-commit` do it).
5. Generate and optimize `images/<filename>.png` (`generate-image-previews.py --apply` is the batch fallback).
6. Commit the `.html`, its image, and `catalog.json` by explicit path; one sheet per commit.
7. Optional: add a `paths.json` step only if the sheet belongs in a curated multi-step trail ([`index-explorer.md`](index-explorer.md)).

Review an existing page: [`../TODO/CHEATSHEET-AUDIT.md`](../TODO/CHEATSHEET-AUDIT.md). Write/review a spec: [`../TODO/SPEC-AUDIT.md`](../TODO/SPEC-AUDIT.md). Economics batch: `python scripts/build_economics_batch.py`, see [`economics-data-refresh.md`](economics-data-refresh.md).

## Local QA

```bash
python3 -m http.server 8765                     # static .html: http://127.0.0.1:8765/<file>.html
php -S 127.0.0.1:8000 scripts/dev_router.php    # index.php, hub slugs, other PHP pages
```

Assert in a real browser: console clean (only a `favicon.ico` 404 allowed); any CDN framework actually loaded (e.g. `typeof window.bootstrap !== 'undefined'`, so a bad SRI hash can't pass silently); interactive bits work; light and dark both render.

## Gates

`./deploy.sh --check` runs everything the deploy runs (SEO gate, link/asset integrity, JSON, `php -l`, catalog freshness, hubs, breadcrumbs). Details and hook setup: [`../deploy/DEPLOY.md`](../deploy/DEPLOY.md). Deploy only with David's go-ahead.
