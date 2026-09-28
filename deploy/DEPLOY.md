# Deployment runbook: cheatsheets.davidveksler.com

Served by Cloudflare Workers since the 2026-09-28 cutover (soak ends 2026-10-05): Worker `cheatsheets-davidveksler-com`, route `cheatsheets.davidveksler.com/*` over the existing proxied DNS record. Governing procedure: `~/Projects/cf-static-kit/docs/runbook.md`. Site design and decisions: [`../docs/specs/cloudflare-migration.md`](../docs/specs/cloudflare-migration.md).

Always go through the guarded script, only with David's go-ahead:

```bash
git push origin main                    # GitHub first
bash scripts/deploy-cloudflare.sh       # scripts/deploy-cloudflare.ps1 [-Yes] on PowerShell (wraps the .sh via Git Bash)
```

Registered as `cheatsheets` in `~/Projects/deploy-sites.json` (`scripts/deploy-cloudflare.ps1 -Yes`).

## Pipeline (aborts at the first failure)

1. **Preflight:** clean tree; `cf-static-kit` present (parity checker); `npm ci` if wrangler is missing. If HEAD is already the active version at 100% and the live page answers, it stops here: nothing to deploy (`--redeploy` / `-Redeploy` runs everything anyway, e.g. to refresh the Explorer's build-time "updated N hours ago" text).
2. **Build + gates:** `python3 scripts/build_site.py` (needs `php` 8.1+ and git). Gates: `build_catalog.py --check`, `check_hubs.py`, `add_hub_breadcrumbs.py --check`, `check_cluster_hub.py`. Then copies the public files from `git ls-files` into `dist/` (internal dirs and files excluded, mirroring the old nginx `internal-paths.conf`) and prerenders `index.php`, `popularity.php`, `sitemap.php` with PHP CLI into `dist/_x/`. After adding a hub: `--write-worker-first`.
3. **Preview:** uploads a version (not public) and runs the parity check against production (smoke; `--full-parity` for the full set).
4. **Confirm** `[y/N]` (skip with `--yes` / `-Yes`).
5. **Promote:** `wrangler versions deploy <version>@100%`, `wrangler triggers deploy`, then purges this host's edge cache (`cf-static-kit/scripts/purge_host.py`; a failed purge only warns).
6. **Verify live:** fetches `/` and greps for a distinctive string. On failure after promotion: `npx wrangler rollback`.

Flags: `--yes`, `--preview-only`, `--full-parity`, `--skip-parity`, `--redeploy` (PowerShell: `-Yes`, `-PreviewOnly`, `-FullParity`, `-SkipParity`, `-Redeploy`).

The build runs only the four gates above. The SEO gate (`scripts/seo_check.py`), link/asset integrity, JSON parse and `php -l` live in `scripts/deploy.py --check` (`./deploy.sh --check`, see *Legacy droplet deploy*).

## Pieces

| Piece | Where |
|---|---|
| Site Worker `cheatsheets-davidveksler-com` | `wrangler.jsonc`, `workers/site/index.js` (hub URLs, `?cat=`/`?hub=` redirects, prerendered Explorer states, `history.php` 301 to GitHub, newsletter endpoints forwarded to the forms Worker); assets from `dist/` |
| Forms Worker `cheatsheets-davidveksler-com-forms` (subscribe/confirm, D1) | `workers/forms/`; deploy `scripts/deploy-forms-cloudflare.sh`; tests `npm run test:forms`. Reached through the `FORMS` service binding, no route of its own |
| D1 `cheatsheets-davidveksler-com-forms` (0907d9a3-a6de-4458-9cdf-ba19eee2eca0) | subscriber addresses: count, never print. `scripts/newsletter_d1.py`, `scripts/import_subscribers.py` |
| Retired-URL redirects (also renamed hub slugs) | `deploy/cloudflare/redirects.txt` (was `conf/nginx/redirects.conf`) |
| Headers, 404 | `deploy/cloudflare/_headers`, `deploy/cloudflare/404.html`; headers on Worker-built responses are set in `workers/site/index.js` |
| Parity probes / allow rules | `deploy/parity-paths.txt`, `deploy/parity-allow.txt` |
| Daily popularity publish | `.github/workflows/popularity-cloudflare.yml` (02:30 UTC) → `scripts/popularity-publish-cloudflare.sh` |

Caching: `.html` `max-age=1800` (`_headers`); Explorer and hubs `max-age=300`, popularity/sitemap `3600` (set in the Worker).

Public URLs carry no `.php` (since 2026-09-28): `/`, `/popularity`, `/sitemap.xml`, `/subscribe`, `/confirm`. The PHP files stay as build-time templates. `/index.php`, `/popularity.php`, `/sitemap.php` and `/confirm.php` 301 to the clean URL (query kept); `/subscribe.php` is still forwarded to the forms Worker so a cached form keeps posting. Mapping: `LEGACY` in `workers/site/index.js`; the parity gates translate production's old links with `scripts/url_rename.py`.

## Daily popularity publish (pre-authorized)

The GitHub Action refreshes `popularity.json` + `catalog.json`, commits and pushes them, then builds and deploys the Worker with the Workers-only secret `CLOUDFLARE_WORKERS_TOKEN`. It publishes only when everything between the live Worker's commit and `HEAD` is those two files or unserved paths (`docs/`, `marketing/`, `TODO/`, root `*.md`, ...). Any other change is reported as DRIFT and waits for `scripts/deploy-cloudflare.sh`. A manual run defaults to a dry run.

## Hooks (once per clone: `git config core.hooksPath .githooks`)

- **pre-commit:** regenerates and stages `catalog.json` when a commit touches a catalogued `.html`, `category-map.php`, `paths.json`, or `catalog-overrides.json`. Needs `beautifulsoup4` (`requirements.txt`, see `activate-venv.sh`) importable by the `python`/`python3` on PATH.
- **pre-push:** runs `scripts/deploy.py --check` only on pushes to the droplet `production` remote; `origin` pushes are untouched.
- `.gitattributes` pins `*.sh`, `.githooks/*`, `scripts/*.py` to LF. On `bad interpreter`: `rm .githooks/pre-push && git checkout -- .githooks/pre-push`.

## Rollback

- Bad deploy: `npx wrangler rollback`.
- Back to the droplet (soak only): comment out `routes` in `wrangler.jsonc`, `npx wrangler triggers deploy --config wrangler.jsonc`. The droplet copy is no longer updated and its crons are gone (spec §6).

## Cutover log

- 2026-09-28: route live (`0ec7fc1`); popularity schedule enabled and `update-popularity.yml` deleted (`047ad9d`); droplet crons `cheatsheets-pull.sh` (04:00) and the referrer accumulator (04:20) removed; referrer feature deleted (`2c5e781`), live as version `246de019` (per `~/Projects/server-mirror/docs/cloudflare-migration.md`, which also lists David's one real newsletter sign-up test as pending).

Decommission after the soak: runbook §7, plus the list in the spec §6.

## Legacy droplet deploy

`./deploy.sh` / `./deploy.ps1` wrap `scripts/deploy.py`, a guarded `git push production main` to `johngalt@direct.vellum.capital:/var/www/cheatsheets.davidveksler.com/htdocs` (post-receive hook + `purge-cache.py`; nginx drop-ins in `conf/nginx/`). Still present until the droplet copy is decommissioned after the soak (ends 2026-10-05); it no longer changes the live site. `./deploy.sh --check` still runs the full validation set (SEO gate, links, JSON, `php -l`, catalog, hubs, breadcrumbs) without pushing; it diffs against the droplet's `production/main`.
