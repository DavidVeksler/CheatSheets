# Deployment runbook: cheatsheets.davidveksler.com

> **Moving to Cloudflare Workers** (branch `cloudflare-workers`, spec [`../docs/specs/cloudflare-migration.md`](../docs/specs/cloudflare-migration.md)). Until cutover the droplet path below is the live one. The Workers path is described in *Cloudflare Workers* at the end, with the cutover checklist.


No build step: the repo files are the site, so pushing to the `production` remote is the deploy. Always go through the guarded script:

```bash
git push origin main     # GitHub first: live never gets a commit origin lacks
./deploy.sh              # ./deploy.ps1 on PowerShell; both wrap scripts/deploy.py (stdlib only, no venv)
```

## Remotes

| Remote | URL |
|---|---|
| `origin` | `https://github.com/DavidVeksler/CheatSheets.git` |
| `production` | `johngalt@direct.vellum.capital:/var/www/cheatsheets.davidveksler.com/htdocs` (checked-out repo; a push updates the live docroot in place) |

Deploy branch: `main`. Invariant: `production == origin == local main`.

## Pipeline (aborts at the first failure)

1. **Preflight:** on `main`; clean tree; `main` in sync with `origin/main`; `git fetch production` so the diff is accurate.
2. **Validate** (files changed vs `production/main`; `--all` for everything):
   - SEO gate `scripts/seo_check.py` on changed `.html` (title ≤ 60, description 150-200, canonical, valid JSON-LD).
   - Every local `href`/`src` in changed pages resolves to a committed file (catches a forgotten `git add` image).
   - Changed `.json` parses; `php -l` on changed `.php` (skipped if `php` is not on PATH).
   - Always, repo-wide: `scripts/build_catalog.py --check` fails if `catalog.json` is stale vs any catalogued `.html`, `category-map.php`, `paths.json`, `catalog-overrides.json`, or a `paths.json` step names a missing file. Fix: `python3 scripts/build_catalog.py`.
   - Always: `scripts/check_hubs.py` (`category-hubs.json`), `scripts/add_hub_breadcrumbs.py --check` (every sheet's hub breadcrumb), and `scripts/check_cluster_hub.py` (crypto custody hub parity and anchors).
3. **Preview:** `git diff --stat production/main..HEAD`.
4. **Confirm** `[y/N]` (skip with `--yes`).
5. **Push + verify:** `git push production main`, then curl homepage (200), each changed page (200 + `cache-control: max-age=1800`), and a known-bad URL (404). Non-zero exit if a live check fails (the push already landed; investigate the server).

Cloudflare purge runs server-side in the `post-receive` hook via `purge-cache.py`, so the deploy box needs no Cloudflare token.

## Flags

```
--yes          skip confirm            --dry-run   preflight + validate, no push
--check        preflight + validate only (what pre-push runs)
--all          validate every file, not just changed
--force        allow non-main branch / skip origin-sync check
--skip-seo | --skip-links | --skip-verify    escape hatches, use sparingly
```

## Hooks (once per clone: `git config core.hooksPath .githooks`)

- **pre-push:** pushes to `production` run `scripts/deploy.py --check` and are blocked on failure; `origin` pushes are untouched. `deploy.py` sets `CHEATSHEETS_DEPLOY=1` on its own push so validation doesn't run twice.
- **pre-commit:** regenerates and stages `catalog.json` when a commit touches a catalogued `.html`, `category-map.php`, `paths.json`, or `catalog-overrides.json`. Needs `beautifulsoup4` (`requirements.txt`, see `activate-venv.sh`) importable by the `python`/`python3` on PATH.
- `.gitattributes` pins `*.sh`, `.githooks/*`, `scripts/*.py` to LF. On `bad interpreter`: `rm .githooks/pre-push && git checkout -- .githooks/pre-push`.

## nginx drop-ins (not deployed by `git push`)

`conf/nginx/*.conf` are copied by hand into the vhost include dir; the server has no other backup of them.

The target dir is owned by `www-data`, so `johngalt` can't `scp` into it directly; stage in `/tmp` and `sudo install`:

```bash
scp conf/nginx/<name>.conf johngalt@198.211.102.9:/tmp/
ssh johngalt@198.211.102.9 'sudo install -o root -g root -m 644 /tmp/<name>.conf /var/www/cheatsheets.davidveksler.com/conf/nginx/ && rm /tmp/<name>.conf && sudo nginx -t && sudo systemctl reload nginx'
```

- `category-hubs.conf`: `/<slug>` → `index.php?hub=<slug>`, `/<slug>/` 301 → `/<slug>`. Must be live before a deploy that ships slug links, or every breadcrumb 404s.
- `redirects.conf`: permanent redirects for retired URLs.
- `internal-paths.conf`: 404 for repo internals the checkout puts in the docroot (`docs/`, `marketing/`, `TODO/`, `scripts/`, `deploy/`, `conf/`, `lib/`, non-archive `newsletter/` files, root dotfiles, every `.md`/`.py`/`.ps1`, `AGENTS.md`). Two provenance files linked from sheets are exempt by exact match; add another exemption there before linking a sheet to any internal file. Verify: `python3 scripts/check_internal_paths.py`.
- `facet-trap.conf`: 302 to the clean path for explorer filter/sort/view URLs requested with our own Referer and no `cs_js` cookie (scraper traversal of the combinatorial facet links). Needs the `index.php` that sets `cs_js` live first, or JS users reloading a filtered view lose their filters. Verify: `curl -s -o /dev/null -w "%{http_code}\n" -H "Referer: https://cheatsheets.davidveksler.com/" "https://cheatsheets.davidveksler.com/?shape=reference"` → 302; same URL without the Referer → 200.
- `php-routing.conf`, `cache-control.conf`, `ssl.conf` exist on the server only.

Verify after reload: `curl -o /dev/null -w "%{http_code}\n" https://cheatsheets.davidveksler.com/radio` → 200; `curl -o /dev/null -w "%{http_code} %{redirect_url}\n" "https://cheatsheets.davidveksler.com/?cat=Radio"` → 301 to `/radio`.

## Server cron (not deployed by `git push`)

None. `johngalt`'s crontab held `cheatsheets-pull.sh` at 04:00 (ff-only pull of `origin/main`, a second deploy path) and a referrer-log accumulator at 04:20; both were removed at the Workers cutover (2026-09-28), and the referrer feature was dropped.

## Manual fallback and hand verification

If the wrapper can't run: `git push production main` (post-receive + purge still fire), then check by hand:

```bash
curl -o /dev/null -w "%{http_code}\n" https://cheatsheets.davidveksler.com/                  # 200
curl -o /dev/null -w "%{http_code}\n" https://cheatsheets.davidveksler.com/no-such-page-xyz  # 404
curl -sI https://cheatsheets.davidveksler.com/<page>.html | grep -i cache-control            # public, max-age=1800
curl -s https://cheatsheets.davidveksler.com/<page>.html | grep -o "<title>[^<]*</title>"   # new version live
```

Caching: `.html` 30-min TTL; images/CSS/JS 7-day `immutable`. Editing an `images/*.png` in place can serve stale for a week, so rename it or bump a query string.

## Cloudflare Workers (preview; cutover pending)

Governing procedure: `~/Projects/cf-static-kit/docs/runbook.md`. Design and decisions: [`../docs/specs/cloudflare-migration.md`](../docs/specs/cloudflare-migration.md).

| Piece | Where |
|---|---|
| Site Worker `cheatsheets-davidveksler-com` | `wrangler.jsonc`, `workers/site/index.js`; assets from `dist/` |
| Build (gates + prerender) | `python3 scripts/build_site.py` (needs `php` 8.1+ and git); `--write-worker-first` after adding a hub |
| Deploy | `scripts/deploy-cloudflare.sh` / `.ps1` (preview + full parity + `parity_body_recheck.py` + `compare_explorer.py` before cutover) |
| Forms Worker `cheatsheets-davidveksler-com-forms` (subscribe/confirm, D1) | `workers/forms/`; `scripts/deploy-forms-cloudflare.sh`; tests `npm run test:forms` |
| D1 `cheatsheets-davidveksler-com-forms` (0907d9a3-a6de-4458-9cdf-ba19eee2eca0) | subscriber addresses: count, never print. `scripts/newsletter_d1.py`, `scripts/import_subscribers.py` |
| Retired-URL redirects | `deploy/cloudflare/redirects.txt` (was `conf/nginx/redirects.conf`) |
| Headers, 404 | `deploy/cloudflare/_headers`, `deploy/cloudflare/404.html` |
| Parity probes / allow rules | `deploy/parity-paths.txt`, `deploy/parity-allow.txt` |
| Daily popularity publish | `.github/workflows/popularity-cloudflare.yml` → `scripts/popularity-publish-cloudflare.sh` (manual, dry run, until cutover) |

Deploys are atomic: no cache purge. Rollback after cutover: `npx wrangler rollback`; back to the droplet: comment out `routes`, `npx wrangler triggers deploy`.

### Cutover checklist (David's go-ahead)

1. Merge the PR into `main`; `git pull` the main checkout.
2. `python3 scripts/import_subscribers.py --apply` (sign-ups since the last import), then `python3 scripts/newsletter_secrets_to_worker.py --check`.
3. `bash scripts/deploy-forms-cloudflare.sh` (contract suite + preview health).
4. `python ~/Projects/cf-static-kit/scripts/enable_routes.py`, commit, then `bash scripts/deploy-cloudflare.sh --full-parity` (one route, `cheatsheets.davidveksler.com/*`; the forms Worker is reached through the service binding, no route of its own).
5. Right after the route is live: `import_subscribers.py --apply` once more; `curl https://cheatsheets.davidveksler.com/subscribe.php?health=1`; one real sign-up by David (email arrives, confirm link works, `SELECT COUNT(*) FROM confirmed` goes up).
6. Mint the GitHub secret `CLOUDFLARE_WORKERS_TOKEN` (Workers Scripts Edit, this account only). In one commit: uncomment `schedule` in `popularity-cloudflare.yml` and delete `update-popularity.yml`. Same session: remove both droplet crons (`crontab -l` saved to the cutover log first).
7. Routines: `cheatsheets-weekly-freshness` footer (live only after `scripts/deploy-cloudflare.sh`); `.claude/skills/cheatsheets-newsletter-monthly` (sync reads D1; archive deploy via `scripts/deploy-cloudflare.sh`).
8. `~/Projects/deploy-sites.json` `cheatsheets` → `scripts/deploy-cloudflare.ps1 -Yes`; add the site to `cf-static-kit/sites.json`; log the cutover (date, version ids) here.

Decommission after the 7-day soak: runbook §7, plus the list in the spec §6.
