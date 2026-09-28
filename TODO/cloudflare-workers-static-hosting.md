# Spec: `cloudflare-workers-static-hosting.html`

**Type:** new cheatsheet. Binding context: `AGENTS.md`, `TODO/README.md` Rules 0 to 6, `TODO/SPEC-AUDIT.md`. Delete this file when the page ships.

**One line:** the operator's reference for serving static sites from Cloudflare Workers static assets, drawn from a real 12-site move off a self-hosted nginx server on 2026-09-27/28: how the request actually flows, every config key, what nginx did that you must port, the guarded deploy and rollback, forms Workers, and the dated incident log.

---

## 1. Why this topic

Cloudflare's docs describe each piece on its own page: routes, static assets, `_redirects`, `_headers`, `html_handling`, `run_worker_first`, versions, preview URLs, Single Redirects, D1, Turnstile. They do not show how the pieces combine for someone running real sites, and they say nothing about leaving nginx. This fleet moved 12 production sites in two days, ranging from a 6-page portfolio to a 20,000-file archive with 4,329 legacy redirects. Along the way it hit the edges the docs don't cover together: Page Rules stop firing once a Worker route exists, `html_handling` answers 307 where nginx answered 301, assets-only Workers cannot send 410, and security headers nginx added server-wide silently disappeared.

**Niche utility test (README Rule 0): passes.** It is a procedure and exact-limits reference. An operator keeps it open beside a terminal during a migration or cutover. A chat answer will give plausible `wrangler` flags, but it will not give the ordering of zone rules against routes, the verified limit table, or a rollback that has actually been run.

**Angle / search hook:** "the nginx exit". Most Workers content is greenfield (`npm create cloudflare`). This page is for people who already have an origin, a redirect map, and SEO equity to protect.

**Relationship to `wordpress-to-static.html`:** that page covers choosing and building a generator. This page covers everything after `dist/` exists. Do not re-explain generators; link to it.

---

## 2. Targeting (SPEC-AUDIT Tier 1)

- **Primary query:** `cloudflare workers static assets`. Research mode.
- **Secondary queries:** `host static site on cloudflare workers`, `cloudflare pages vs workers`, `migrate nginx to cloudflare workers`, `cloudflare workers _redirects limit`, `wrangler versions upload preview url`, `cloudflare worker route vs custom domain`, `run_worker_first`.
  - Semrush had no API units on 2026-09-28, so these volumes are unverified. Check them in GSC after launch.
  - Question-shaped H2s should use the secondary phrasing.
- **Draft `<title>` (59 chars):** `Cloudflare Workers Static Assets: 12-Site Migration Runbook`
- **H1:** `Hosting static sites on Cloudflare Workers`
- **Meta description draft (verify 150 to 200 chars with the SEO gate):** `How 12 static sites moved off nginx onto Cloudflare Workers static assets: wrangler config, _redirects and _headers limits, preview-parity-promote deploys, forms Workers with D1, rollback.`
- **Reader outcome (definition of working):** A reader with an nginx-hosted static site can:
  - write the `wrangler.jsonc`;
  - port every redirect and header;
  - pick route vs custom domain;
  - cut over with zero DNS change;
  - prove parity before promoting;
  - roll back in one command;
  - all without opening a second tab.
- **Success metric:** organic entries on the primary/secondary cluster, plus citations in AI answer engines for "Workers static assets limits" and "nginx to Workers" questions. Secondary: clicks from `wordpress-to-static.html`.
- **Volatile-facts register (page rating: VOLATILE):**
  - **Fast rot (re-verify quarterly):**
    - static-assets limits: files per version on Free vs Paid, per-file size, `_redirects` 2,000 static + 100 dynamic, `_headers` 100 rules, `run_worker_first` entry limits;
    - Workers Paid price;
    - Free-plan request quota;
    - wrangler major version and command status (`wrangler triggers deploy` printed "experimental" on 4.142.0, 2026-09-28);
    - `versions secret put` syntax;
    - Cloudflare's current Pages-vs-Workers recommendation;
    - D1 and R2 free-tier limits;
    - Resend/Mailgun free tiers if named.
  - **Slow drift:**
    - rule execution order (the Traffic Sequence);
    - `html_handling` modes and the 307 behavior;
    - Page Rules deprecation status.
  - **Stable:** the incident log (dated history), the nginx-to-Workers mapping concepts, the pipeline shape.
  - Every volatile number carries "as of Mon YYYY" or a wrangler version tag inline.
- **Index category:** `Software & DevOps` (hub `software-devops`). Add to `category-map.php`, then run `scripts/add_hub_breadcrumbs.py`.
- **Reading conditions:**
  - Desktop, a second monitor next to a terminal, often mid-cutover and alert but under time pressure.
  - Wide tables are fine, in `overflow-x: auto` wrappers. Commands need copy buttons.
  - Dark theme must be first-class, because the reader's terminal is dark.
  - Print is not required. Mobile must be readable (375 px) but is not the design target.
- **Geographic scope:** none. The platform is global; prices are USD.

---

## 3. Public-repo and page safety (hard rule)

This repo and page are public, and the page's own Common Mistakes section warns against exactly this leak. Never put any of the following in the spec, the page, JSON-LD, or image alt text:

- account, zone, D1, KV or R2 ids;
- API tokens or their permission lists tied to real token names;
- origin IP addresses;
- SSH users or hosts;
- real server filesystem paths;
- the dashboard host's internals;
- which DNS records still leak the origin.

Public site hostnames and public GitHub repo paths are fine. Say "the account id is pinned in `wrangler.jsonc`", not the id itself. Describe the droplet as "the previous nginx origin".

---

## 4. Sections (build to three depths; densities are minimums)

### 00 · Quick reference (top of page)

Build two blocks.

**Limits card (10 to 14 rows, each verified and dated):**
- files per version (Free / Paid);
- max file size;
- `_redirects` static and dynamic caps;
- `_headers` rule cap;
- `run_worker_first` entry count and length;
- Free-plan Worker requests/day;
- Workers Paid monthly price;
- preview URL behavior (always noindex);
- D1 and R2 free-tier headline limits.

**Decision strip (5 to 6 rows, "Use X when…"):**
- assets-only vs script Worker;
- route vs custom domain;
- `html_handling` mode picker keyed to your canonical URL shape (`/a/`, `/a`, `/a.html`);
- `_redirects` vs zone Single Redirect vs Worker code;
- Workers vs Pages for a new static site (state Cloudflare's current guidance with date);
- stay on the origin (dynamic apps).

### 01 · How a request flows (the signature element; see §5)

This is prose plus the interactive trace. Cover:
- the proxied DNS record;
- zone-level rules (Single Redirects, WAF/Bot Fight Mode, the Traffic Sequence order);
- route matching, where the most specific pattern wins (`host/api/*` beats `host/*`);
- the Worker (`run_worker_first` globs → script, else assets);
- assets resolution: `_redirects` runs before asset matching, then `html_handling`, then `not_found_handling`;
- `_headers` applied to asset responses only, not Worker-built responses;
- service bindings, D1, R2.

Call out that **Page Rules run after Worker routes**, so a forwarding Page Rule on a routed host silently stops firing at cutover. Verify this against the Traffic Sequence docs.

### 02 · `wrangler.jsonc`, key by key (table, 12 to 16 rows)

- **Columns:** key · value this fleet uses · why · gotcha.
- **Rows:** `name`, `account_id` (pin it when a token sees several accounts), `compatibility_date`, `assets.directory`, `assets.html_handling` (all four modes), `assets.not_found_handling` (`404-page` vs `single-page-application` vs `none`; `none` returns an empty body that browsers render blank), `assets.binding`, `assets.run_worker_first`, `main`, `workers_dev: false`, `preview_urls: true`, `routes` with `zone_name`, `observability`, `services` (service binding), `d1_databases`, `vars` vs secrets.
- **Exemplar row at final depth:**
  - key: `assets.html_handling`
  - value: `auto-trailing-slash` (default) or `none` for sites whose canonical URLs end in `.html`
  - why: must match your canonical URLs or every internal link gets a redirect
  - gotcha: normalizing redirects are **307**, not 301; with `none`, `/` no longer finds `index.html`, so add `/ /index.html 200` or handle it in the Worker
- Include one complete annotated `wrangler.jsonc` for an assets-only site and one for a script Worker with `run_worker_first` and a service binding. Build these from the fleet's real configs with ids stripped.
- Note that a root `wrangler.jsonc` is auto-loaded by the Cloudflare Vite plugin. whopaysforai names its config `wrangler.static.jsonc` for that reason.

### 03 · Porting nginx (the conversion table, 16 to 22 rows)

- **Columns:** nginx construct · what it did · Workers static-assets equivalent · gotcha / what cannot be ported.
- **Rows:**
  - `return 301`;
  - `map $uri $redirect_uri` (exact-path maps);
  - `location =`;
  - `location ^~` prefix;
  - regex `location ~`, where precedence matters, so over the `_redirects` caps use a script Worker that reproduces nginx order (freecapitalists.org: exact → longest prefix → regex in file order);
  - `try_files $uri $uri.html`;
  - `index index.xml` feeds (`/feed/ /feed/index.xml 200`);
  - `rewrite … last`;
  - `add_header` security headers inherited server-wide (X-Frame-Options, nosniff, Referrer-Policy);
  - `add_header Access-Control-Allow-Origin` on public JSON;
  - `expires` / Cache-Control;
  - gzip/brotli (automatic);
  - `error_page 404`;
  - `return 410` / `deny` (assets-only cannot emit 410 or 403, so they become 404);
  - PHP includes (prerender at build, as the CheatSheets Explorer does);
  - access logs (Cloudflare analytics, D1 event rows);
  - non-ASCII paths (Workers match the percent-encoded path, nginx matched decoded);
  - slashless 301s (write them explicitly or `html_handling` answers 307);
  - digit-only placeholders (not supported, so enumerate them);
  - splat ordering (splats count as dynamic and go last).
- **Worked example:** an actual 6-line nginx `map` block from WalletRecovery's `deploy/redirects.map` (public repo? verify; else synthesize a realistic one), then the `_redirects` lines `scripts/build_cloudflare_rules.py` emits for it, including a percent-encoded source.

### 04 · The guarded deploy pipeline (step ladder, 8 steps + flags table)

- **Steps:**
  1. preflight (clean tree, Node ≥ 22, token source, kit present, routed detection);
  2. build + gates, where the build must not modify tracked files;
  3. `wrangler versions upload --preview-alias c<sha> --tag <sha>`;
  4. parity check against production;
  5. stop here if unrouted or `--preview-only`;
  6. confirm;
  7. `wrangler versions deploy <id>@100%`, then `wrangler triggers deploy`, then optional host cache purge;
  8. live verify: distinctive string + body hash vs the preview + deployment status.
- **Flags table:** `--yes`, `--preview-only`, `--full-parity`, `--skip-parity`, PowerShell twin (`-Yes` etc.).
- **Parity sub-block (8 to 12 entries):**
  - what is compared: status, `Location`, content type, 11 headers, normalized body SHA-256;
  - probe sources: both sitemaps, paths files, `/`, `/robots.txt`, a random 404, slash / `.html` / `index.html` variants of 40 random pages;
  - the normalizers every Cloudflare zone needs: challenge script, `/cdn-cgi/`, Web Analytics beacon, email obfuscation, Cloudflare Fonts, Automatic HTTPS Rewrites, inter-tag whitespace;
  - allow-file syntax `<path-regex> <field>  # reason`;
  - exit codes 0/1/2;
  - "baseline parity" against a preview of the commit the old origin runs, used when the origin is behind the repo.
- **Callout:** Git-connected builds are deliberately not used, so that the deploy stays a human approval gate.

### 05 · Cutover, soak, rollback, decommission (checklist runbook)

- **Pre-cutover checklist (10 to 14 items):**
  - full parity passes;
  - security headers present;
  - HTML 404 page exists;
  - forwarding Page Rules recreated as Single Redirects;
  - forms Worker deployed unrouted and tested on its preview (health + one real submission);
  - secrets set (bootstrap `wrangler deploy` first, then `versions secret put` for uploaded-only versions);
  - `.gitattributes` `* text=auto eol=lf`, so Windows and Linux builds produce identical bytes;
  - `TZ=UTC` for date-rendering builds;
  - alias hosts have zone redirects;
  - analytics replacement ready.
- **Cutover:** uncomment `routes`, commit, deploy with `--full-parity`. DNS does not change.
- **Soak:** 7 days, with the old origin copy untouched; `soak_check` compares the Worker with the origin, pinned by host resolution.
- **Rollback, two ways, with when to use each:**
  - `npx wrangler rollback` for a bad version;
  - remove `routes` + `npx wrangler triggers deploy` to hand traffic back to the origin, which then serves its last origin deploy (stale).
- **Decommission steps.**

### 06 · Forms and beacons without a server (anatomy + table)

- Present the contact-Worker handler order as a numbered pipeline:
  1. method;
  2. honeypot (silent success);
  3. per-IP fixed-window rate limit on a salted, truncated IP hash in D1, failing open on D1 error;
  4. field validation;
  5. Turnstile siteverify with `remoteip`;
  6. mail send;
  7. D1 log row after the send.
- Response rules: JSON for `fetch()` callers, 303 for plain form posts. `GET ?health=1` returns 503 when D1, the secret or mail is unconfigured, so the form fails closed.
- **Variants table (4 rows):**
  - WalletRecovery forms: legacy `.php` paths kept, beacon slug allowlist, 200-byte cap;
  - CheatSheets newsletter: double opt-in, HMAC token, 7-day TTL, constant-time compare, reached by service binding with no route;
  - vellum investor inquiry: KV audit trail, origin check;
  - freecapitalists contact.
- Include the D1 schema (`inquiries`, `events`, `hits`) as a code block, with no PII in logged rows.
- **Deploy-order rule:** a forms Worker on its own route must be live before HTML that posts to it, or submissions 404. A service-bound forms Worker that answers both old and new paths removes the ordering constraint.

### 07 · What stays off Workers (decision table, 6 to 8 rows)

- Rows: WordPress, MediaWiki, Discourse, helpdesk, a dashboard that reads server logs, webhook receivers with local state, the WordPress admin.
- Columns: why it stays · what it would take to move · verdict.
- Name the hostnames only generically ("the fleet's WordPress blogs"). Do not list the droplet's full vhost inventory.

### 08 · Operating the fleet (6 to 10 entries)

- `fleet_check.py`: routes point at the expected Worker, DNS proxied, every 3xx line exact, alias 301s keep the path, listed 200s and 404s, security headers, forms health, `--crawl` link integrity including the R2 host. State its first full run's numbers as dated anchors (verify).
- **Scheduled CI publish:**
  - a GitHub Action with a **Workers-only token** that publishes only when the diff since the live version's tag is data-only;
  - anything else is reported as DRIFT and publishes nothing;
  - it verifies the published artifact by sha256.
- **Token scoping:** separate tokens for deploy, analytics read, and D1. Describe the principle only (see §3).
- **Analytics after leaving nginx logs:** Cloudflare Analytics GraphQL for popularity, D1 rows for form/beacon events. Name what was lost (the nginx referrer parsing).
- **R2 for bulk media:** move files out of `dist/` to stay under the per-version file cap (freecapitalists.org library, about 7,600 images). Include the custom-domain setup note.
- **Cache:** assets revalidate by ETag. Name the case where purge still matters: zone edge cache holding long max-age copies of old origin responses (verify against CheatSheets `/images/`).

### 09 · Incident log (the page's highest-value table, 10 to 12 rows, dated)

- **Columns:** date · symptom · root cause · fix · the general rule.
- **Rows (anchors from the migration; verify each against `cf-static-kit` and `server-mirror` git history before publishing):**
  - **2026-09-27:** a `/whitepaper` redirect was lost at cutover. Page Rules run after Worker routes; the fix moved it to a Single Redirect.
  - **2026-09-27:** parity false positives from Cloudflare-injected markup (beacon newlines, Fonts, HTTPS rewrites, email obfuscation). Fixed with normalizers.
  - **2026-09-27:** four sites shipped different bytes from Windows builds (CRLF). Fixed with `.gitattributes eol=lf`.
  - **2026-09-27:** Eleventy dates rendered in local time zone. Fixed with `TZ=UTC`.
  - **2026-09-28:** six sites were missing security headers and four served empty 404 bodies. Parity only started comparing headers after the early cutovers; `soak_check` found it and `fleet_check` now enforces it.
  - **2026-09-28:** the fleet check counted `<image:loc>` R2 URLs as page paths (175 bogus URLs).
  - **2026-09-28:** live checks failed on large pages. **Headline lesson:** it was read as 6 to 15 minute edge lag and led to longer timeouts and a purge step. The real cause was `echo "$BODY" | grep -q` under `pipefail`: SIGPIPE exit 141 on any page over the 64 KB pipe buffer. The fix was a here-string. Rule: prove the verifier on a known-good page before blaming the platform.
  - **2026-09-28:** the scheduled publish exited 22: `curl -f` inside `$(...)` under `set -e`, plus a Bot Fight Mode challenge on the CI runner.
  - **2026-09-28:** the forms deploy reported "preview only" after it had gone live. A JSONC "routed" regex bug.
  - wrangler crashed with EISDIR on a directory named `_redirects/`.
  - HSTS: the zone setting was on with `max_age 0`, so no policy was sent. Surfaced by parity.

### 10 · Common mistakes (8 to 10, mandatory)

- Leaving forwarding Page Rules on a routed host.
- Trusting `html_handling` for legacy 301s.
- Assuming `_headers` applies to Worker-generated responses.
- `not_found_handling: none` blank 404s.
- Deploying HTML before its form Worker.
- Setting secrets on a Worker whose newer version is only uploaded.
- Connecting Git builds and losing the approval gate.
- Publishing origin details.
- Believing parity passed when most paths were challenged. The checker marks runs untrusted above max(5, 10%) challenged.
- Blaming propagation before testing the checker.

### 11 · Sources

- Primary Cloudflare docs, one line each on what they establish: static assets overview, routing and `html_handling`, `_redirects`, `_headers`, `run_worker_first`, limits, pricing, versions and deployments, preview URLs, routes vs custom domains, Traffic Sequence / rules order, Single Redirects, Page Rules migration, service bindings, D1 limits, R2 custom domains, Turnstile siteverify, wrangler command reference, and the Pages-to-Workers migration guide.
- Plus public repo links where they exist: `DavidVeksler/CheatSheets` for `wrangler.jsonc`, `workers/site`, `workers/forms` and `scripts/deploy-cloudflare.sh`. Check whether the other fleet repos are public before linking any. Private repos are cited as "fleet repository" without links.

---

## 5. Design

- **Visual identity: "packet trace".**
  - A network-engineer's trace printout on a dark console: monospace hop labels, thin hairline rules, hop numbers down the left margin, status codes as colored stamps (2xx green, 3xx amber, 4xx red, 5xx magenta).
  - Palette: derive real hex values at build (README Rule 5), e.g. ink `#0f1419`, panel `#161d24`, hairline `#2a3440`, amber `#f2a33a` (primary accent), trace-green `#5fd08a`, stamp-red `#ef6b6b`, dim text `#8b9aa8`, plus a light variant via `light-dark()`.
  - Avoid Cloudflare's brand orange and logo. This is not a Cloudflare page (impersonation rule).
  - Fonts: system UI sans for prose, `ui-monospace` stack for hops and code.
- **Signature element: the request tracer (one interactive element; the page's budget).**
  - A vertical hop diagram: DNS (proxied) → zone rules → route match → Worker (`run_worker_first`?) → `_redirects` → asset lookup / `html_handling` → `not_found_handling` → `_headers` → response.
  - A select or button row of 7 to 9 real sample requests from the fleet. Each lights the hops it passes and dims the rest, prints the final status stamp and `Location`, and shows one line of "why":
    - `www.vellum.capital/` → zone rule 301;
    - `vellum.capital/whitepaper` → Single Redirect (the Page-Rule lesson);
    - `walletrecovery.info/api/contact.php` → more-specific route → forms Worker;
    - `walletrecovery.info/<legacy-wordpress-slug>/` → `_redirects` 301;
    - `vellum.capital/feed/` → 200 rewrite to `index.xml`;
    - `whopaysforai.org/about` → 200 rewrite ported from `try_files`;
    - `cheatsheets.davidveksler.com/software-devops` → `run_worker_first` → prerendered hub;
    - `…/page.html` on an `auto-trailing-slash` site → **307** (the gotcha);
    - a missing path → `404-page`.
  - Verify every sample live with `curl -sI` at build time and use the real status and `Location`. If a sample's behavior differs, the live behavior wins.
  - Without JS it must render as a static annotated trace of all samples (a table), so the content is never locked behind interaction.
  - At 375 px the hop column stays vertical and samples become a native `<select>`.
- **Shareable artifact / og:image:** the tracer mid-trace on the `/whitepaper` Page Rule case (hops lit, the Page Rule hop crossed out, amber 301 stamp), rendered to `images/cloudflare-workers-static-hosting.png` at 1200×630.
- **Secondary visuals:** the pipeline ladder in §04 as a horizontal step rail (vertical on mobile), with the approval gate drawn as a physical break in the rail. Nothing else gets custom art.

---

## 6. Cross-link map

- **Outbound:**
  - `wordpress-to-static.html` (building `dist/`);
  - `linux-server-hardening.html` (the origin that remains for dynamic sites);
  - `modern-devops-pipelines.html` (CI/CD context);
  - `observability-logs-metrics-traces-slos.html` (analytics after logs);
  - `api-design-rest-graphql-grpc-webhooks.html` (forms endpoints);
  - `how-its-built.html` (this collection runs on the architecture);
  - `aws-vs-azure.html` (hosting alternatives).
- **Inbound (add reciprocal links when shipping):**
  - `wordpress-to-static.html` section 07 "Shared infrastructure" intro and its Related block;
  - `how-its-built.html` hosting mention, if present;
  - `modern-devops-pipelines.html` Related.
- Footer cross-links per `SEO_PROMPT.txt`.

---

## 7. Anti-goals

- Not a Workers programming tutorial. No Durable Objects, Queues, AI, or framework adapters, beyond one line saying where the fleet chose not to use them.
- No Pages tutorial. Pages appears only in the Workers-vs-Pages decision row.
- No product comparisons with Vercel or Netlify beyond one row in the decision strip.
- No pricing advocacy.
- No internal fleet inventory beyond public hostnames. §3 governs.

---

## 8. Known drift in the source repos (resolve at build; scripts win over docs)

These disagreements existed on 2026-09-28. Do not copy either side to the page without checking the executable source:

1. **Cache purge after promote.** Several docs say no purge is needed. The kit template and some site scripts purge; others don't yet. The purge was added during the SIGPIPE misdiagnosis, so decide from Cloudflare's docs on Workers static-assets caching whether it is ever needed, and state the rule, not the history.
2. **Live-check windows** differ per repo (60 s, 3 min, 15 min). Template comments still attribute the 15-minute window to propagation. Present the check's logic, not a window number.
3. **Deployment status.** The runbook says the check confirms "100%"; the script only greps for the version id.
4. **Rate-limit storage.** The migration plan says KV; the template uses D1; vellum's Worker uses KV without Turnstile. The page describes the template.
5. **coloradofirearmswatch trailing-slash mode.** The plan says `force-trailing-slash`; the config says `auto-trailing-slash`. The config wins.
6. **CheatSheets entry in `cf-static-kit/sites.json`.** It still expects `/popularity.php` and `/sitemap.php` to return 200 after they became 301s (`098cc28`). Flag this to David; do not describe it on the page.
7. **Forms Workers** deploy with plain `wrangler deploy` (no preview-then-promote). State this honestly as a difference from site deploys.

---

## 9. Build notes

- Facts come from `~/Projects/cf-static-kit` (`docs/runbook.md`, `templates/`, `scripts/`), `~/Projects/server-mirror/docs/cloudflare-migration.md`, and each fleet repo's `wrangler*.jsonc`, deploy scripts and `workers/`. Read them in a subagent and bring back conclusions.
- Every number in this spec is an anchor (README Rule 1): re-verify it or drop it.
- `datePublished` = ship date. No visible "Last verified" line and no `dateModified`.
- The page is served by the architecture it describes. One sentence in the intro may say so; no more.
