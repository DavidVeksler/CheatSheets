# Spec: cheatsheets.davidveksler.com from the droplet to Cloudflare Workers

Status: **draft for implementation, 2026-09-28.** Wave 4 (the last site) of `~/Projects/server-mirror/docs/cloudflare-migration.md`. Procedure: `~/Projects/cf-static-kit/docs/runbook.md` (governing; this spec only adds what is specific to this site). Decisions cited as **D-n** are David's, 2026-09-27 (plan §5 and §7).

Scope: build, preview and parity until PASS on branch `cloudflare-workers`. Cutover (routes), cron removal and decommission stay David's gate.

## 1. Current behaviour (inventory, verified 2026-09-28)

The droplet docroot `/var/www/cheatsheets.davidveksler.com/htdocs` is a git checkout of `main` (at `455f434`, same as `origin/main`). Everything under it is served unless an nginx rule says otherwise.

### 1.1 PHP routes

| URL | File | Behaviour |
| --- | --- | --- |
| `/`, `/index.php` | `index.php` | Explorer. Server-renders every card from `catalog.json`, the facet rail, Pulse strip, deep cut of the day (UTC day), Map and Paths lenses. Runs `git log -1` per request. `Cache-Control: public, max-age=300`. |
| `/?cat=`, `/?category=`, `/?hub=`, `/index.php?hub=` | `index.php` | 301 to `/<slug>`, other params kept. `?hub=<sheet>` 301s to `/<sheet>.html`; unknown `?hub=` is a 404 page. |
| `/?q= &shape= &fresh= &interactive= &sort=` | `index.php` | Same document with cards hidden/sorted server-side; `<meta name="robots" content="noindex, follow">`. Client JS already mirrors this state (it filters in place with `history.replaceState`). |
| `/?view=map` / `/?view=paths` / `/?path=<id>` | `index.php` | Lens on `<body data-view>`; the paths lens (and the `?path=` stepper) is only rendered in that view. noindex. |
| `/?sheet=<file>` | `index.php` | Detail block server-rendered, title = sheet title, canonical = sheet URL; JS opens the drawer. noindex. |
| `/?og=1` | `index.php` | Chrome-less map render for `scripts/render_og_map.py` (local tool). noindex. |
| `/<slug>` (15 hubs) | `index.php?hub=` | Category hub, indexable, `category-hubs.json` copy, JSON-LD. |
| `/history.php[?commit=&file=&q=&page=]` | `history.php` | Git history browser (plumbing per request). |
| `/popularity.php` | `popularity.php` | Renders `popularity.json`, `refresh-status.json`, and "Where readers come from" from `.referrers.json`. `max-age=3600`. |
| `/sitemap.php` | `sitemap.php` | XML sitemap: every root `.html` (lastmod = file mtime), 15 hubs, `/`. `text/xml`, `max-age=3600`. Named in `robots.txt`. |
| `/subscribe.php` (POST) | `subscribe.php` | Newsletter intake: validate, honeypot `website`, append `.subscribers.jsonl`, HMAC confirm link, Resend send, owner notice via PHP `mail()`. JSON or no-JS HTML page. GET is 405. |
| `/confirm.php?p=&s=` | `confirm.php` | Verify token (7-day TTL), append `.confirmed.jsonl` once, HTML page. 400 on missing/invalid. |
| `/category-map.php` | data include | Executes, 200 with an empty body. Never linked. |
| `/check-category-map.php`, `/lib/*.php` | | 404 (internal-paths.conf). |

### 1.2 nginx rules (vhost + `conf/nginx/*.conf`)

| Rule | Effect |
| --- | --- |
| `category-hubs.conf` | `^/([a-z0-9][a-z0-9-]*)$` not a file → `index.php?hub=$1`; `^/(slug)/$` → 301 `/$1` for **any** single segment. |
| `redirects.conf` | `/anduril-products.html`, `/defense-autonomy-platforms.html` → 301 `/autonomous-defense-systems.html`. |
| `internal-paths.conf` | 404 for `/docs/ /marketing/ /TODO/ /scripts/ /deploy/ /conf/ /lib/`, `/newsletter/` except `YYYY-MM.html`, root dotfiles, `*.md|py|ps1`, `AGENTS.md`, `SEO_PROMPT.txt`, `requirements.txt`, `check-category-map.php`. Two public exceptions served as `text/plain; charset=utf-8`: `/docs/how-do-rainbows-work-production.md`, `/scripts/grass_green/build_spectra.py`. |
| `facet-trap.conf` | 302 to the clean path for filter URLs requested with our own Referer and no `cs_js` cookie (scraper trap). |
| `php-routing.conf` | `try_files $uri $uri/ =404` (no front controller). |
| `cache-control.conf` | `*.html` → `public, max-age=1800`. |
| `ssl.conf` | TLS, HTTP/3, `X-protocol` header. Cloudflare-terminated; nothing to port. |
| vhost | `.glb` → `model/gltf-binary`; `if ($bad_bot) return 429`. |
| WordOps `locations-wo.conf` | CORS `*` + far-future cache on images/json/css/js; 403 on `*.sh`, `README.*`, backups; `/favicon.ico` falls back to a 1x1 GIF; server-wide `X-Frame-Options`, `X-Content-Type-Options`, `Referrer-Policy`. |

### 1.3 Crons, hooks, routines, consumers

| Item | What it does |
| --- | --- |
| cron 04:00 `~/scripts/cheatsheets-pull.sh` | ff-only pull of `origin/main` + Cloudflare purge. The only way the daily `popularity.json` commit (GitHub Action `update-popularity.yml`, 02:30 UTC) goes live. It also publishes **any** commit on `origin/main` within 24 h. |
| cron 04:20 `scripts/referrer_accumulate.py` | Folds nginx access logs into `.referrers.json`. **Not broken** (the audit was wrong): it ran today and the store holds 14+ days since the peer session "Cheatsheets popularity referrers and caching" shipped it on 2026-09-27 (`890af8e`). |
| `post-receive` hook | Logs the deploy, purges changed HTML from Cloudflare (`purge-cache.py`). |
| `deploy.sh`/`deploy.ps1` → `scripts/deploy.py` | Guarded `git push production main`. |
| `scripts/newsletter_sync.py` | SSH-pulls `.confirmed.jsonl` into Resend (monthly newsletter routine, project skill `cheatsheets-newsletter-monthly`). |
| `scripts/referrer_report.py` | Ad-hoc ssh report over nginx logs. |
| routine `cheatsheets-weekly-freshness` | Pushes to `origin/main`; its footer says updates go live only after `git push production`. |
| routine `cheatsheets-reddit-daily-drafts` | Commits drafts only; no droplet contact. |
| `~/Projects/deploy-sites.json` `cheatsheets` | `deploy.ps1 --yes --skip-seo`. |
| Server-only files | `.newsletter.env` (4 keys), `.subscribers.jsonl` (5 rows), `.confirmed.jsonl` (1 row), `.referrers.json`, `.cloudflare.env`, `.metadata-cache.json`. |

`www.cheatsheets.davidveksler.com` has no DNS record: no alias to redirect.

## 2. Target design

One site Worker `cheatsheets-davidveksler-com` (static assets + a small script) and one forms Worker `cheatsheets-davidveksler-com-forms` (D1 `cheatsheets-davidveksler-com-forms`), both unrouted until cutover.

### 2.1 Build (`scripts/build_site.py`, output `dist/`, gitignored)

1. **Gates** (the always-run subset of `deploy.py --check`): `build_catalog.py --check`, `check_hubs.py`, `add_hub_breadcrumbs.py --check`, `check_cluster_hub.py`.
2. **Copy public files** from `git ls-files` (never the working tree's untracked files) through one allowlist function that mirrors nginx: root `*.html`, root data/asset files (`.json .js .glb .txt LICENSE`), `images/`, `newsletter/YYYY-MM.html`, the two provenance files. Everything nginx 404s or 403s is left out, so it 404s on Workers. `*.php` sources are never copied.
3. **Prerender with PHP CLI** (`scripts/prerender.php`, same `index.php`/`popularity.php`/`sitemap.php`, `HTTP_HOST=cheatsheets.davidveksler.com`, `HTTPS=on`, `TZ=UTC`) into `dist/_x/`: Explorer default view, paths lens, one page per curated path (11), one page per hub (15), popularity, sitemap. PHP stays the template engine, so the prerendered HTML is the droplet's HTML for the same state, and local dev (`serve.py`, `render_og_map.py`) keeps working.
4. **Generate** `dist/_redirects` (per root sheet: `/<name> → /<name>.html 301` and `/<name>/ → /<name> 301`, reproducing the hub rule's two hops; the two retired-URL redirects), copy `deploy/cloudflare/_headers` and `deploy/cloudflare/404.html` (noindex).
5. **Write** `build/site-routes.json` (gitignored) for the site Worker: hub slug ↔ category, sheet titles for `?sheet=`, curated path ids. Fail if `wrangler.jsonc` `run_worker_first` does not list every hub (`--write-worker-first` rewrites the block).

Reproducibility: `TZ=UTC`, LF checkout (`* text=auto eol=lf`), `dist/` cleared first. `sitemap.php` lastmod comes from `git log -1` per file instead of mtime (a CI checkout has meaningless mtimes). The Explorer's time-relative bits (deep cut of the day, NEW badges, "Last change … ago", "Reviewed this week") are frozen at build time; the daily popularity publish (§2.5) rebuilds every day, and "Last change … ago" is re-computed client-side from a timestamp so it never goes stale between builds.

### 2.2 Explorer: prerendered + client-side facets (D-2)

`index.php` changes (all small, all in the one file):

- On load, when the URL carries `q`, `shape`, `fresh`, `interactive` or `sort`, the grid JS runs its existing `apply()` (it already parses these from `location.search`); the hero search box is filled from `q`.
- On load, `?view=map|paths` selects the lens from the URL. When the paths lens is not in the document (hub pages), it navigates to `./?view=paths` once, never to the same URL (no loop).
- The `cs_js` cookie line goes with the facet trap.
- "Change history" links point to `https://github.com/DavidVeksler/CheatSheets/commits/main/` (D-2), here and in `lib/chrome.php`.
- "Last change … ago" carries `data-ts` and is refreshed by the page script.

Site Worker (`workers/site/index.js`), `run_worker_first` on `/`, `/index.php`, `/*.php`, `/_x/*`, the 15 hub slugs and their `/<slug>/` forms, `/favicon.ico` and the two provenance files:

| Request | Response |
| --- | --- |
| `/?cat=<Category>` / `?category=` / `?hub=<slug>` (on `/` or `/index.php`) | 301 `/<slug>` + remaining params (droplet's `http_build_query` form). `?hub=<sheet>` → 301 `/<sheet>.html`; unknown `?hub=` → 404 page. |
| `/?path=<id>` (valid) | `_x/path/<id>.html` |
| `/?view=paths` | `_x/paths.html` |
| anything else on `/`, `/index.php` | `_x/index.html` |
| `/<slug>` | `_x/hub/<slug>.html`; `/<slug>/` → 301 `/<slug>` |
| `?sheet=<file>` on the index | HTMLRewriter sets `<title>`, `og:title`, `twitter:title` to the sheet title (58-char clamp, as PHP), and canonical/`og:url` to the sheet URL; the drawer opens client-side (existing code). The server-rendered detail block is dropped (no-JS readers get the grid). |
| any client-state param (`q sort shape view sheet path fresh interactive og`, unknown `cat`) | HTMLRewriter inserts `<meta name="robots" content="noindex, follow">` exactly where PHP did. |
| `/_x/*` directly | 404 (internal). |
| responses | `Cache-Control` as the droplet sent (`max-age=300` Explorer/hubs, `3600` popularity/sitemap/redirects), plus the three WordOps security headers (`_headers` does not apply to Worker-built responses). |

The facet crawl trap disappears: facet URLs now cost one cached static asset, not a PHP render, so there is nothing to trap (D-2). `robots.txt` keeps its `Disallow` lines and noindex stays on every state URL.

### 2.3 History (D-2)

`history.php` is not built. The site Worker answers every `/history.php` URL with 301 (cached 1 h):

| Old URL | New URL |
| --- | --- |
| `/history.php` (also `?q=`, `?page=`) | `https://github.com/DavidVeksler/CheatSheets/commits/main/` |
| `/history.php?file=<path>` | `https://github.com/DavidVeksler/CheatSheets/commits/main/<path>` (each segment URL-encoded; invalid path → the list) |
| `/history.php?commit=<hash>` | `https://github.com/DavidVeksler/CheatSheets/commit/<hash>` (hash validated `^[0-9a-f]{4,40}$`) |

Three sheets link to `history.php` (`how-its-built.html` ×5, `machine-consensus.html`, `wordpress-to-static.html`): their hrefs change to the GitHub URL. Their prose is left alone (the how-its-built exhibit is dated July 2026; flagged for David).

### 2.4 Newsletter forms Worker (`workers/forms/`)

From the kit's `contact-worker` shape (D1, health, per-IP rate limit, JSON vs no-JS responses), with two handlers instead of contact/event:

- `POST /subscribe.php`: PHP contract exactly: field `email` (trimmed, ≤ 254, FILTER_VALIDATE_EMAIL-equivalent), honeypot `website` (silent success, nothing stored), same messages and status codes (405, 503 fail-closed without secret/key, 422, 502, 200), JSON when `Accept: application/json` or any `X-Requested-With`, otherwise the same Bootstrap no-JS page. Intake row → D1 `subscribers(email, ts, src)` (ts in PHP `gmdate('c')` form, src = Referer ≤ 200). Token `base64url(email).unix_ts`, `base64url(HMAC-SHA256(payload, NEWSLETTER_TOKEN_SECRET))`, link `https://<host>/confirm.php?p=…&s=…`, same email HTML/text, subject, From/Reply-To via Resend with `RESEND_SENDING_KEY`. Owner notice to `CHEATSHEET_NOTIFY_EMAIL`: PHP used the droplet's `mail()`; the Worker sends the same text through Resend from the sending domain (the only change in the contract, forced by the platform).
- `GET /confirm.php`: same checks, TTL 7 days, constant-time compare, same pages and 200/400. Confirmed row → D1 `confirmed` (unique on `email COLLATE NOCASE`, `INSERT OR IGNORE`): re-confirming stays a silent no-op. Links minted by the droplet verify unchanged because the secret moves as is.
- `GET /subscribe.php?health=1`: 200 when D1, token secret and sending key are present, 503 otherwise (a new endpoint; GET without it stays 405).
- Rate limit: 10 subscribe POSTs per hashed IP per hour (fails open). New, to stop the endpoint being used to mail-bomb third parties.

Routing: the site Worker forwards `/subscribe.php` and `/confirm.php` to the forms Worker through a **service binding** (`FORMS`), so the preview works end to end and cutover needs one route (`cheatsheets.davidveksler.com/*`), not two.

Secrets: `NEWSLETTER_TOKEN_SECRET`, `RESEND_SENDING_KEY`, `CHEATSHEET_NOTIFY_EMAIL` piped from the droplet's `.newsletter.env` (`sudo -n cat` over ssh) into `wrangler secret put` by `scripts/newsletter_secrets_to_worker.py`; values are never printed or written to disk. `RESEND_SEGMENT_ID` is not a Worker secret (only `newsletter_sync.py` uses it, from `~/Projects/.resend.env`).

Import: `scripts/import_subscribers.py` reads both `.jsonl` files over ssh, and inserts rows missing from D1 (multiset on `(email, ts, src)` for intake, email for confirmed). Dry run by default, `--apply` writes, prints counts only, never an address. Run once now and again right after the route goes live.

Consumers: `scripts/newsletter_sync.py` gets `--source d1` (default) reading `confirmed` with the D1 token; `--source droplet` keeps the ssh path until decommission.

### 2.5 Daily popularity publish (D-5, pre-authorized; built disabled)

New workflow `.github/workflows/popularity-cloudflare.yml`, `workflow_dispatch` only, `dry_run` input defaulting to `true`; its `schedule` is commented out. It runs `scripts/popularity-publish-cloudflare.sh`:

1. `fetch-popularity.py` + `build_catalog.py` (same as today), commit `popularity.json` + `catalog.json` and push (skipped on dry run).
2. **Publish guard** (model: objectivismonline-seo `refresh-homepage-cloudflare.sh`): read the live version's `workers/tag` (the commit it was built from). Publish only if every file changed between that commit and `HEAD` is `popularity.json` or `catalog.json` (an empty diff also publishes, which refreshes the date-dependent Explorer bits). Anything else is DRIFT: publish nothing, warn, exit 0, and wait for `scripts/deploy-cloudflare.sh` and David.
3. Build, `wrangler versions upload --tag <sha>`, `versions deploy @100%`, verify `/popularity.php` shows the new generation stamp.

At cutover this workflow gets its schedule (02:30 UTC) and `update-popularity.yml` is deleted in the same commit, and the droplet crons are removed in the same session. Secret `CLOUDFLARE_WORKERS_TOKEN` (Workers Scripts Edit on the account only), minted by David; the existing `CLOUDFLARE_API_TOKEN` secret stays the Analytics token.

Behaviour change to note: today any commit on `origin/main` goes live by 04:00 via the cron pull. After cutover only popularity-driven changes auto-publish; everything else needs `scripts/deploy-cloudflare.sh` (the stated deploy gate).

### 2.6 Headers, caching, misc

| Droplet | Workers |
| --- | --- |
| WordOps security headers on every response | `_headers` `/*`; the site Worker adds them to its own responses. |
| `.html` `public, max-age=1800` | `_headers` `/*.html` if Workers accepts an infix splat; otherwise the Workers default (ETag revalidation) with an allow rule. The 30-min TTL existed to shield PHP/nginx; nothing to shield now. |
| CORS `*` on `.json` | `_headers` `/*.json` (public datasets; catalog.json is advertised as machine-readable). |
| `.glb` `model/gltf-binary` | Workers MIME table; verified by parity. |
| `/favicon.ico` → 1x1 GIF | Site Worker returns the same 43-byte GIF. |
| `bad_bot` 429 | Dropped (plan §4, as davidveksler.com); zone WAF/Bot rules still apply. |
| Cloudflare purge after deploy | Not needed: Workers deploys are atomic. `purge-cache.py` retires at decommission. |

## 3. What is dropped and why

| Dropped | Why |
| --- | --- |
| `history.php` git browser | D-2: link to GitHub, 301 old URLs. |
| Referrer history (`.referrers.json`, 04:20 cron, "Where readers come from") | D-2. Also forced: no nginx access logs exist once Workers serves the site. The prerender has no store, so `popularity.php` renders without that section. The scripts stay in the repo until David confirms deletion (they are the peer session's recent work, `890af8e`). |
| Facet trap (`facet-trap.conf`, `cs_js` cookie) | D-2: filtering is client-side over a static page. |
| Server-rendered filtered grids and the `?sheet=` detail block for no-JS readers | D-2. Every state URL still returns the full grid, noindex, and JS applies the state. |
| `?og=1` render mode in production | Only `scripts/render_og_map.py` uses it, locally via PHP. `/?og=1` serves the Explorer, noindex. |
| `/category-map.php` 200-empty | Data include, never linked; now 404. |
| `bad_bot` 429, `X-protocol`, `Alt-Svc` | Origin-only concerns. |
| `.sh`/`README.md` 403 | Become 404 (assets-only Workers cannot send 403). |
| Unknown `/<x>/` → 301 `/<x>` then 404 | Unknown paths 404 directly. Known sheets and hubs keep both hops. |
| Droplet deploy path (`deploy.sh`/`.ps1`, `deploy.py` push, post-receive, 04:00 pull, `purge-cache.py`, `conf/nginx/`) | Replaced by `scripts/deploy-cloudflare.*` at decommission (kept until then for rollback). |

## 4. URL and redirect table (parity probes in `deploy/parity-paths.txt`)

| URL | Droplet | Workers |
| --- | --- | --- |
| every sitemap URL (206 sheets, 15 hubs, `/`) | 200 | 200, same bytes for sheets |
| `/<sheet>` | 301 `/<sheet>.html` | same (`_redirects`) |
| `/<sheet>/` | 301 `/<sheet>` | same |
| `/<slug>/` | 301 `/<slug>` | same (Worker) |
| `/?cat=Radio`, `/?category=Radio`, `/?hub=radio`, `/index.php?hub=radio` | 301 `/radio` | same |
| `/?hub=dotnet-cheatsheet` | 301 `/dotnet-cheatsheet.html` | same |
| `/anduril-products.html`, `/defense-autonomy-platforms.html` | 301 `/autonomous-defense-systems.html` | same |
| `/history.php…` | 200 | 301 GitHub (allow rule) |
| facet URLs (`?shape= ?fresh= ?sort= ?q= ?interactive=1 ?view=map ?view=paths ?path= ?sheet=`) | 200 | 200, body differs (allow rule, verified by `scripts/compare_explorer.py`) |
| internal paths (`/docs/…`, `/scripts/…`, `*.md`, dotfiles, …) | 404 | 404 |
| provenance files | 200 text/plain | 200 text/plain |
| `/subscribe.php` GET, `/confirm.php` GET | 405, 400 | same |
| `/index.html`, `/foo` | 404 | 404 |

## 5. Parity strategy

1. **Full `cf_parity.py`** against the droplet from the scaffolded deploy script: both sitemaps, every file live in the droplet docroot (`origin_paths.sh`, internal paths included on purpose so their 404 is checked; `ORIGIN_EXCLUDE` empty), `deploy/parity-paths.txt` (redirects, hubs ± slash, extensionless sheets, facet/state URLs, history URLs, forms GETs, internal-path probes), URL-variant probes, random 404.
2. **Explorer equivalence** (`scripts/compare_explorer.py`), because the Explorer HTML legitimately differs (build time vs request time, changed links, no cookie line). It fetches the same URL from both sides and compares extracted content, not bytes: `<title>`, meta description, robots, canonical, OG/Twitter tags, JSON-LD (parsed), H1 and hub intro/start-here, the ordered card list (file, title, category, description, shape chips, dates, NEW badge), facet rail entries and counts, sort links, stats line, trails, `catalog-lite` and `daily-history` JSON. Pages: `/`, `/index.php`, every hub, `/?view=paths`, every `/?path=<id>`, `/popularity.php` (tables and ranks), `/sitemap.php` (URL set). Known differences are enumerated in the script (history links, relative-time text, referrer section) and anything else fails.
3. Allow rules only for the differences above, each with its reason, scoped to the paths concerned.
4. Forms: local contract suite under `wrangler dev` (no email leaves the machine; Resend is faked), including a droplet-minted token (PHP `newsletter_mint_token`) verified by the Worker; preview `?health=1`; D1 counts after import.

## 6. Cutover (David's go-ahead) and rollback

Cutover checklist in the PR and `deploy/DEPLOY.md`:

1. Merge the PR. Re-run `python scripts/import_subscribers.py --apply` (catches sign-ups since the first import).
2. `python scripts/newsletter_secrets_to_worker.py --check` (secret names present on the forms Worker).
3. `python ~/Projects/cf-static-kit/scripts/enable_routes.py`, commit, `bash scripts/deploy-cloudflare.sh --full-parity` (one route `cheatsheets.davidveksler.com/*`; forms reached through the service binding, so no forms route).
4. Immediately after the route is live: `import_subscribers.py --apply` again; one real sign-up by David (confirmation email arrives, confirm link works, row in D1).
5. Mint `CLOUDFLARE_WORKERS_TOKEN`, add it as a repo secret; enable the schedule in `popularity-cloudflare.yml` and delete `update-popularity.yml` (one commit); in the same session remove both droplet crons (`cheatsheets-pull.sh`, `referrer_accumulate.py`).
6. Routines: `cheatsheets-weekly-freshness` footer (live only after `scripts/deploy-cloudflare.sh`); project skill `cheatsheets-newsletter-monthly` (sync reads D1; archive deploy via `scripts/deploy-cloudflare.sh`).
7. `~/Projects/deploy-sites.json` `cheatsheets` → `scripts/deploy-cloudflare.ps1 -Yes`; `cf-static-kit/sites.json` entry; log version ids in `deploy/DEPLOY.md`.

Rollback: comment out `routes`, `npx wrangler triggers deploy`: the droplet answers again immediately (its crons must be back if removed: keep `crontab -l` output in the cutover log). Subscriptions taken on Workers during a rollback window live in D1 only; `import_subscribers.py` is one-way, so note the window and replay by hand if needed.

Decommission after the 7-day soak (runbook §7): vhost, htdocs (including `.newsletter.env`, `.jsonl` stores), post-receive hook, `production` remote, `deploy.sh/.ps1/deploy.py`, `purge-cache.py`, `conf/nginx/`, `lib/env.php`, `subscribe.php`, `confirm.php`, `history.php`, referrer scripts (if David agrees), rename `deploy-cloudflare.*` to `deploy.*`, docs.

## 7. Risks

| Risk | Mitigation |
| --- | --- |
| Explorer regressions hidden by a body allow rule | `compare_explorer.py` gates the content; allow rules name paths, not `.*`. |
| Stale time-relative Explorer content if the daily publish stops | Publish guard runs daily after cutover; relative "Last change" is computed client-side; fleet health notices a stale `generated` stamp. |
| Daily publish shipping unreviewed work | Guard publishes only `popularity.json`/`catalog.json` diffs against the live commit. |
| Confirm links minted before cutover failing | Same secret and algorithm; tested with a PHP-minted token. |
| Subscriber PII leaking into logs or git | Importer and secret helper print counts/names only; SQL temp file lives in a private temp dir and is deleted; `.jsonl` never copied locally to disk. |
| Hub added without updating `run_worker_first` | Build fails and names the missing slug; `--write-worker-first` fixes it. |
| Owner notice through Resend counts against the free tier (100/day) | One extra email per sign-up; volume is single digits. |
| Workers MIME/Content-Type differences (`.glb`, `LICENSE`, `.txt`) | Parity checks every droplet file's content type. |
