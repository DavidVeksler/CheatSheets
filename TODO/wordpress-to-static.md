# Spec: wordpress-to-static.html — Life After WordPress: the SSG fleet operator's guide

**Target file:** `wordpress-to-static.html`
**Index category:** `Software & DevOps` (existing label in `category-map.php`)
**Goal classification (Rule 0 honesty):** primarily a **personal-study / operator-reference page**
(David + his agents use it to work on his own five post-WordPress sites), with an **advocacy
layer** (the git-is-the-CMS argument from the 2026-07 LinkedIn post) and a **secondary SEO
layer** (SSG decision framework + migration playbook). Judge it by utility and use, not
traffic. The niche-utility shape it passes on: **comparison tables with exact specs** and an
**operator runbook you keep open while working in a repo** — not a broad "what is an SSG"
overview.

## Why this topic

David ran WordPress since b2/cafelog (~2001). Between 2026-07-09 and 2026-07-14 he cut over
three production sites from WordPress to static generators, and now operates **five no-CMS
sites** across three architectures (Astro, Eleventy, Next.js-prerendered-to-static). The
thesis, per the LinkedIn post: a CMS does three jobs — an editing workflow, a database, and a
theme — and with AI collaborators all three have better answers: **git is the editor, files
are the database, the model is the designer**. Page builders (Elementor) are hostile to
agents because layout lives as opaque DB blobs; plain files in a repo are the substrate
agents are good at.

The problem this page solves: five repos × three generators × two deploy patterns is too much
to hold in one head. Every "how does vellum deploy again?" or "which site uses
`markdownTemplateEngine: false` and why?" costs a repo-spelunking session. This page is the
**fleet control board**: the mental model of each generator, the exact content model, build
command, deploy path, and the sharp edges of each site — plus the general decision framework
so the next migration (or the reader's first one) doesn't re-derive it.

Differentiation vs. the internet: "Astro vs Eleventy" listicles compare feature matrixes in
the abstract. This page compares them **as operated in production by one person**, with the
real migration scars: WordPress XML imports, `wp-content` passthrough, nginx redirect maps,
Turnstile-guarded form replacements, and the agent-workflow angle nobody else covers.

## Targeting

- **Primary query:** `wordpress to static site` (research mode)
- **Secondary queries:** `astro vs eleventy`, `static site generator comparison`, `leaving
  wordpress for static site`, `git as a cms`, `migrate wordpress to eleventy`
- **Mode:** research mode, not crisis. Title/H1 lead with the transformation, question-shaped
  H2s match real queries ("Which static site generator should I use?", "How do you replace
  WordPress forms/search/RSS?").
- **Draft `<title>`:** `WordPress to Static Site: Astro, Eleventy, Agent-Built HTML` (59 chars)
- **Draft H1:** `Life After WordPress: Running Five Sites With No CMS`
- **Draft meta description (150–200):** `A CMS is an editor, a database, and a theme engine.
  Git, plain files, and AI agents now do all three jobs better. The decision framework,
  Astro vs Eleventy vs Next.js comparison, and migration playbook from five production
  WordPress exits.` (~250 → trim at build to 150–200; keep "editor/database/theme" hook first.)

## Reader outcome ("definition of working")

Two readers, two tests:

1. **David or an agent** opens any of the five repos cold and can, from this page alone:
   name the generator + content model, run the right build command, know where content lives,
   and execute the correct deploy path without re-reading the repo's AGENTS.md.
2. **A stranger with a WordPress site** can decide whether an SSG fits their site, pick
   between Astro/Eleventy/Next.js/raw HTML using the decision table, and enumerate the
   migration workstreams (content export, media, redirects, forms, RSS, SEO gates) without
   missing one.

## Success metric

Primary: **use as fleet onboarding** — the page gets linked from the five repos' AGENTS.md
files as shared context and actually shortens agent onboarding (qualitative). Secondary:
long-tail organic entries on `astro vs eleventy` / `wordpress to static` families, and
shares of the CMS-teardown diagram as the LinkedIn-post-companion artifact.

## Reading conditions

Desktop, second monitor, terminal open in one of the repos; unhurried but task-focused.
Agents also consume it via clean semantic HTML. Implications: wide tables are fine (with
`overflow-x: auto` wrappers for the 375 px case), code/command blocks must be copy-paste
exact, dark theme is the natural default for the audience, print is low priority (sane
defaults suffice).

## Geographic scope

None — global technical content. No jurisdiction caveats needed.

## Content approach

Hybrid structure, two parts. Part A is the search-facing general framework; Part B is the
fleet operator's reference. Quick Reference block at the very top serves both.

### Quick Reference (top of page)

Two artifacts side by side:
- **"Should this site be static?" decision table** (~8 rows): content changes per day,
  editors who need a GUI, per-request personalization, auth/user accounts, forms, search,
  comments, e-commerce — each row: "static works because…" vs "you still want a CMS/app
  because…".
- **Fleet at-a-glance strip**: 5 sites × (generator, deploy pattern) in one scannable line
  each — the page's own table of contents into Part B.

### Part A — The framework (general, search-facing)

1. **The CMS teardown** (signature element, see Design): the three jobs and their
   replacements. Editor → git (review, diffs, rollback, audit trail = commits and PRs).
   Database → files in the repo (markdown, JSON, versioned data — diffable, greppable,
   portable). Theme → the model (designs from scratch, iterates, QAs in a real browser).
   Plus the forcing function: page builders store layout as opaque DB blobs an agent cannot
   diff or review; plain files are the substrate agents are good at. ~6–8 atomic entries,
   each with a concrete example from the fleet (e.g. "the database": CFW's versioned firearms
   list JSON — `list-2026-05-15.json` → `list-2026-07-30.json`, 872 entries, fix = PR not
   phpMyAdmin).

2. **Generator decision table** (the load-bearing comparison, 5 columns × ~12 criteria
   rows): **Astro / Eleventy / Next.js (prerendered) / raw agent-written HTML / stay on
   WordPress**. Criteria rows: mental model, templating, content formats supported,
   data-driven page generation (build 900 pages from JSON), client JS shipped by default,
   component islands/interactivity story, build speed at this fleet's scale, config surface,
   learning curve, agent-friendliness (can a model own the whole file?), ecosystem risk,
   best-fit site shape. Every cell concrete — versions and real behaviors, not adjectives.
   Follow with explicit **"use X when…" decision guidance** (~5 entries), each justified by
   which fleet site proves it (e.g. "Eleventy when content is a pile of WP-exported
   markdown/HTML and you want templating OFF the content path — walletrecovery,
   vellum.capital"; "Astro when pages are generated from structured data at build time —
   CFW's 913 firearm + 64 county pages"; "Next.js only when you might grow into an app —
   whopaysforai, and note its Drizzle schema is still `export {}`").

3. **WordPress migration playbook** (~10-step ordered checklist, each step: what, the fleet
   example, the gotcha):
   - Export: WP XML (`vellumcapital.WordPress.2026-07-10.xml` retained in-repo) + import
     script (`import:wordpress`).
   - Media: download + passthrough the whole `wp-content` tree so URLs survive
     (vellum.capital) vs re-hosting and rewriting (walletrecovery `download_media.py`,
     `optimize_images.py`, WebP `<picture>` transform).
   - **URL preservation is the whole SEO game:** permalink rules centralized in code
     (walletrecovery `src/lib/routing.js`), `legacyRoutes.json` + nginx redirect map
     (vellum), `redirects.map` + `check_redirects.py` (walletrecovery).
   - Templating off the content path: WP-exported bodies contain raw braces/HTML —
     `markdownTemplateEngine: false` (walletrecovery), both engines false (vellum). This is
     the #1 non-obvious Eleventy migration setting.
   - Dates: coercing WP `YYYY-MM-DD HH:mm:ss` strings into real UTC dates (custom YAML
     parser).
   - Rebuild the dynamic bits (cross-ref section A4).
   - RSS, sitemap, robots as templates you own (hand-built njk vs `@11ty/eleventy-plugin-rss`
     vs `@astrojs/sitemap` — all three approaches exist in the fleet).
   - SEO/quality gates in the build (`lint-claims.mjs` + `seo-check.mjs` wired into
     `npm run build` on davidveksler.com; `seo_check.mjs` in whopaysforai's build).
   - Cut-over: DNS already behind Cloudflare, swap origin vhost, verify, keep WP export
     archived.
   - Decommission: what you stop paying/patching (PHP, MySQL, plugin updates, admin login
     attack surface).

4. **Rebuilding the "dynamic" 10% without a CMS** (~6 entries, each: need → static-era
   answer → fleet example): contact/lead forms (PHP endpoint or Cloudflare Worker +
   Turnstile — walletrecovery `api/contact.php`, vellum `workers/investor-inquiry`), search
   (client-side Fuse.js — CFW lookup), newsletters (Buttondown dispatch via GitHub Action on
   merge — CFW alerts), scheduled data freshness (cron GitHub Actions watchers diffing
   sources and opening PRs — CFW's 6 workflows), comments (verdict: drop them / outsource),
   AI-agent discoverability (`llms.txt` as a first-class route — walletrecovery, vellum).

### Part B — The fleet (operator's reference)

5. **Fleet dashboard** (the second signature artifact; 5 rows × ~9 columns): site / URL /
   generator + pinned version / content model (formats + where) / scale (pages, posts,
   data records) / build command / quality gates + CI / deploy pattern / companion Workers.
   All values from the repos as of 2026-08-14 (see volatile register — re-read the repos at
   build time).

6. **Per-site operator cards** (5 cards, ~6 entries each — the densest section). Each card:
   one-line identity, mental model, content model ("to add a post, touch…"), build/dev/test
   commands, deploy path + approval gate, and 2–3 site-specific gotchas. Anchor facts
   (verified from repos 2026-08-14):
   - **coloradofirearmswatch.org** — Astro ^7.1.0 + React islands + Fuse.js. One markdown
     collection (`updates`); the real content is versioned JSON under `data/` (SSF lists
     with 872 entries, counties, litigation, training). Vitest suite; CI asserts ≥64 county
     + ≥100 firearm pages so a silent data-loader regression fails the build. Deploy:
     `scripts/deploy.sh` rsync → origin, Cloudflare purge, verify. Gotchas: a stale
     `astro.config.mjs` comment claims Cloudflare Pages deploys it (it doesn't — rsync is
     real); 6 scheduled GitHub Actions (PDF diff watcher, county recheck, CPW watcher,
     litigation poller, alert dispatch) write data via PRs — content changes arrive as PRs,
     not human edits.
   - **davidveksler.com** — Astro ^5.2.0. Collections: `work` (7 case studies) + `pages`
     (6); every claim on the site must reference a record in `src/data/evidence.json`
     (46 records) with a status enum enforced by `lint-claims.mjs`, which runs **inside**
     `npm run build` alongside the SEO gate. Deploy: rsync `--delete` → origin. Gotchas:
     build fails on an uncited claim (feature, not bug); `/david/ai-strategy.html`
     deliberately excluded from sitemap.
   - **WalletRecovery.info** — Eleventy ^3.1.6, CommonJS config. 29 pages + 50 posts,
     markdown + YAML frontmatter; `markdownTemplateEngine: false` on purpose; permalinks
     centralized in `src/lib/routing.js`. Deploy: `git push production` (GitHub + server
     trigger repo; `post-receive` rebuilds), `scripts/deploy.sh` is the preflight wrapper.
     Gotchas: branch is `master` not `main`; Python link/redirect checkers are the test
     suite; contact form is PHP + Turnstile (one PHP file survives the WordPress exit).
   - **vellum.capital** — Eleventy ^3.1.2, ESM config. 49 posts as **WordPress-exported
     HTML** (both template engines off), 15 njk page templates; `wp-content` passthrough
     preserves all media URLs. Deploy: `git push production main` → `post-receive` runs
     `npm ci && build && check`. Gotchas: the `workers/investor-inquiry` Worker must deploy
     **before** the site and is its own approval gate; `legacyRoutes.json` + nginx redirect
     conf are load-bearing for the WP-era URLs.
   - **whopaysforai.org** — Next.js 16.3.0 via `vinext` (Vite + App Router), React 19.
     Content is **TypeScript modules, not markdown** (`app/lib/content.ts`, generated
     `news-data.ts` from a 6,000-line JSONL corpus with a triage pipeline + twice-daily
     ingest cron that never publishes without human review). Deploy: build → `vinext start`
     → **crawl the route list into flat HTML** → tar/rsync → byte-compare live homepage so
     a stale Cloudflare response fails closed. Gotchas: Drizzle/D1/R2 are starter
     scaffolding, intentionally unused (`db/schema.ts` is `export {}`); never hand-edit
     generated `news-data.ts`.

7. **Shared infrastructure & the two deploy patterns** (~5 entries): all five sites → one
   self-hosted nginx (WordOps) origin behind Cloudflare — none uses Pages/Vercel/Netlify
   (deliberate: same box that ran the WordPress sites, zero platform lock-in). Pattern 1:
   **rsync-from-local** (CFW, davidveksler, whopaysforai) — build on the workstation, push
   artifacts. Pattern 2: **`git push production`** (walletrecovery, vellum) — server
   `post-receive` hook rebuilds from source. Compare honestly: rsync = workstation is the
   build env (fast, but "works on my machine" risk); push-to-build = reproducible server
   build (slower, needs node on the origin). Every repo: AGENTS.md canonical + CLAUDE.md
   pointer; deploy always behind explicit human approval — the one gate that never
   automates.

8. **Common Mistakes / Anti-Patterns** (mandatory, ~8 entries): leaving template engines on
   over third-party/WP-exported content (build-time injection + brace explosions); dropping
   WP URLs without a redirect map (the SEO extinction event); trusting config comments over
   deploy scripts (the CFW Cloudflare Pages comment); hand-editing generated files;
   publishing origin infrastructure details on a Cloudflare-fronted site (see anti-goals);
   assuming starter scaffolding is live (the empty Drizzle schema); skipping the
   worker-before-site deploy ordering; treating "static" as "no moving parts" (the fleet
   runs 8+ scheduled Actions — the motion moved from request time to build/cron time).

### Density targets

Decision table ≥12 criteria rows × 5 columns; migration playbook ≥10 steps; dynamic-bits
≥6 entries; fleet dashboard exactly 5 × ~9; each operator card ≥6 entries; mistakes ≥8.
Total well past the 20+ floor.

## Volatile-facts register

**Overall rating: SLOW-DRIFT.** Verification source for nearly everything = **the five repos
themselves** (read `package.json`, configs, deploy scripts at build time; the recon numbers
in this spec were read from the repos on 2026-08-14 but are anchors per Rule 1).

- Package versions (Astro 7.x/5.x, Eleventy 3.1.x, Next 16.x): drift monthly via
  dependabot. Tag inline "as of <Mon YYYY>"; freshness pass = re-read five `package.json`.
- Content counts (pages/posts/records/firearm-list entries): drift weekly-to-monthly. Use
  "~" and date them, or phrase as orders of magnitude.
- Deploy patterns and gates: stable but repo-authoritative; re-check deploy scripts.
- Fleet composition itself: David ships new sites; the dashboard needs a row added when the
  next one lands. Note this in the page's freshness comment.

## Cross-link map

- **Internal (this repo):** `how-its-built.html` (the sibling agent-pipeline architecture —
  strongest reciprocal link; this page is "the other sites", that page is "this site"),
  `versioncontrol.html` + `git-scm.html` (git-as-editor claim), `javascript-for-architects.html`
  (Astro/framework context), `governing-agentic-ai.html` (agent governance angle),
  `linux-server-hardening.html` (the origin box). Add reciprocal links from
  `how-its-built.html` and `versioncontrol.html` at minimum.
- **Cross-domain:** deep links to all five subject sites are inherently natural here —
  follow `~/Projects/seo-crosslinking/` (donor/receiver map + per-domain constraints) and
  record additions there.

## Visual identity

**Design language: "the decommissioning."** A two-era page: WordPress-admin visual DNA
(the wp-admin dark sidebar `#23282d`, its blue `#0073aa`) appearing only as the *struck-
through past* — and a clean files-and-terminal aesthetic (repo tree, diff green/red,
monospace data) as the present. Vanilla + modern CSS platform (the recommended default —
no framework), dark-first with `light-dark()`.

- **Signature element (build first, best, and it's the og:image): the CMS teardown
  diagram** — three labeled slabs (EDITOR / DATABASE / THEME) each visually "unplugging"
  from a WordPress block and re-plugging into its replacement (git commit graph / file tree
  with JSON+md files / a model glyph sketching a layout). Pure inline SVG, no JS, reads at
  1200×630. This is the LinkedIn-post thesis as one image.
- Second artifact: the **fleet dashboard** styled as a physical control board / rack-tag
  strip — each site row gets a status-tag look (generator badge, deploy-pattern glyph).
- Per-site operator cards: native `<details name="fleet">` exclusive accordions, styled as
  server rack tags with the site's own accent hue.
- One interactive element max: none required; if any, a copy button on command blocks
  (reuse the existing `.cmd` pattern) — no decision-wizard JS, the tables do that job.
- 375 px: dashboard + decision table in `overflow-x: auto` wrappers; teardown SVG stacks
  vertically via viewBox swap or acceptable horizontal scroll.

## Anti-goals

- **Do NOT publish origin infrastructure details:** no origin IP, no SSH usernames/hosts,
  no Cloudflare zone IDs, no Turnstile site keys, no server paths beyond generic
  `/var/www/<site>/htdocs`-style illustration. The sites are Cloudflare-fronted; leaking
  the origin defeats that. Say "a self-hosted nginx origin behind Cloudflare."
- No SSG-war flaming: WordPress is presented as the right tool for 2001–2026 and still
  right for sites with many GUI editors — the page argues fit, not superiority.
- No re-listing every SSG (Hugo, Jekyll, Gatsby get one comparative sentence in the
  decision-table intro at most; the table compares only the stacks actually operated).
- Don't duplicate `how-its-built.html`: this repo's PHP+static pipeline gets a one-line
  link, not a sixth operator card (per the user's scope call: SSG sites + whopaysforai).
