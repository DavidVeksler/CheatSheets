# Deployment runbook — cheatsheets.davidveksler.com

**Production is the live site at `https://cheatsheets.davidveksler.com/`.** This is
a repo of standalone `.html` / `.php` / `.json` / image files served directly by
nginx — **there is no build step**. The files in the repo *are* the deployed site,
so a push to the `production` remote *is* the deploy.

Deploy is wrapped in a guarded script so a bare `git push production` can't ship a
dirty, divergent, or broken tree. Use it:

```bash
git push origin main     # GitHub is the source of truth — push there first
./deploy.sh              # guarded deploy (./deploy.ps1 on PowerShell)
```

`./deploy.sh` and `./deploy.ps1` are thin wrappers around
[`scripts/deploy.py`](../scripts/deploy.py) (stdlib-only Python — no venv needed).

## Repositories and remotes

- **GitHub source repo** (`origin`): `https://github.com/DavidVeksler/CheatSheets.git`
- **Production** (`production`): `johngalt@direct.vellum.capital:/var/www/cheatsheets.davidveksler.com/htdocs`
  — pushes straight into the live docroot (a checked-out repo; the push updates the
  working tree in place).
- Local deploy branch: `main`.

Invariant the pipeline enforces: **live never gets a commit GitHub doesn't have.**
Push `main` to `origin` first, then deploy. `production == origin == local main`.

## What `./deploy.sh` does

Five phases; it aborts at the first failure (see escape hatches below).

1. **Preflight**
   - On branch `main` (else abort, or `--force`).
   - Working tree is clean (you deploy commits, not uncommitted files).
   - `git fetch origin main`; local `main` is in sync with `origin/main` (else abort,
     or `--force`).
   - `git fetch production` to refresh the `production/main` tracking ref, so the
     changeset diff is accurate.
2. **Validate** (local — the robustness win). Scoped to files **changed vs
   production** by default; `--all` validates the whole repo.
   - **SEO gate:** runs [`scripts/seo_check.py`](../scripts/seo_check.py) on changed
     `.html` (title ≤ 60, meta description 150–200, canonical, valid JSON-LD).
   - **Internal link/asset integrity:** every local `href`/`src` in changed pages
     must resolve to a committed file. This is the check that catches a
     forgotten-`git add` image/script before it 404s in production.
   - **JSON:** every changed `.json` data file must parse.
   - **PHP:** `php -l` on changed `.php` — skipped cleanly if `php` isn't on PATH
     locally (it usually isn't on the dev box).
3. **Changeset preview:** prints `git diff --stat production/main..HEAD` — exactly
   what goes live.
4. **Confirm:** `[y/N]` prompt (skip with `--yes`).
5. **Deploy + verify:** `git push production main`, then curls the live site — the
   homepage (expect `200`), each changed page (expect `200` + `cache-control:
   max-age=1800`), and a known-bad URL (expect `404`). Prints a pass/fail table and
   exits non-zero if any live check fails (the push already landed — investigate the
   server, not the script).

Cloudflare cache purging is **not** done by this script — it happens server-side in
the repo's `post-receive` hook via [`purge-cache.py`](../purge-cache.py), which
purges the edge cache for the changed `.html`. So the deploy box doesn't need the
Cloudflare token.

## Flags

```
./deploy.sh                # full pipeline, interactive confirm
./deploy.sh --yes          # skip the confirm prompt
./deploy.sh --dry-run      # preflight + validate, then stop (no push)
./deploy.sh --check        # preflight + validate only (what the pre-push hook runs)
./deploy.sh --all          # validate every file, not just changed
```

Escape hatches — use sparingly, they exist so you're never truly stuck:

```
--force        allow a non-main branch / skip the origin-sync check
--skip-seo     skip the SEO gate
--skip-links   skip internal link/asset integrity
--skip-verify  skip the post-deploy live curl checks
```

## First-time setup in a fresh clone

The tracked pre-push hook lives in `.githooks/` and is **not** active until you
point git at it (this is local config, not committed):

```bash
git config core.hooksPath .githooks
```

With that set, even a raw `git push production` runs the preflight + validation
first (`scripts/deploy.py --check`) and is blocked if anything fails. Pushes to
`origin` are unaffected. `deploy.py` sets `CHEATSHEETS_DEPLOY=1` when it issues its
own push, so the hook no-ops and validation doesn't run twice.

Line endings: `.gitattributes` pins `*.sh`, `.githooks/*`, and `scripts/*.py` to LF
so the bash hook and wrappers don't break under Git Bash on Windows. If a hook ever
fails with `bad interpreter`, re-checkout: `rm .githooks/pre-push && git checkout --
.githooks/pre-push`.

## Manual fallback

If the wrapper can't run (no local Python, etc.), the raw deploy is still:

```bash
git push production main
```

The server-side `post-receive` hook and Cloudflare purge still fire. You lose the
local preflight/validate/verify, so run the checks under **Verification** by hand.

## Verification

The pipeline runs these automatically; to check by hand after any deploy:

```bash
# Homepage + a known 404 (server 404 routing)
curl -o /dev/null -w "%{http_code}\n" https://cheatsheets.davidveksler.com/                    # 200
curl -o /dev/null -w "%{http_code}\n" https://cheatsheets.davidveksler.com/no-such-page-xyz    # 404

# A page you just shipped: served + correct cache TTL
curl -sI https://cheatsheets.davidveksler.com/<page>.html | grep -i cache-control              # public, max-age=1800

# Confirm the live content is the new version (Cloudflare purged)
curl -s https://cheatsheets.davidveksler.com/<page>.html | grep -o "<title>[^<]*</title>"
```

Caching context (see AGENTS.md → *Server Configuration*): `.html` gets a 30-min TTL,
images/CSS/JS get a 7-day `immutable` TTL. Editing an existing `images/*.png` in
place can serve stale for up to a week — rename it or bump a query string.
