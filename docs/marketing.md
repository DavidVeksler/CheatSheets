# Marketing quick path — SEO, promotion, measurement

Thin router for growth work. The durable SEO working doc is
[`../TODO/seo-planning.md`](../TODO/seo-planning.md); the campaign assets and
publishing queue are in [`../TODO/marketing-campaign-plan.md`](../TODO/marketing-campaign-plan.md).
Discoverability rules live in [`../AGENTS.md`](../AGENTS.md) (> *Discoverability*).

## SEO standards

- **Per-page SEO gate** — `scripts/seo_check.py`: title <= 60, meta description
  150-200, canonical, valid JSON-LD. Every page also carries OG/X tags, keywords,
  descriptive image alt text, and `TechArticle` JSON-LD that matches visible content.
- **Do not** add `FAQPage`/`HowTo` schema to chase rich results (deprecated for SERP
  features); the lever is genuinely good, self-contained content under clear headings.
- **Repo-level discovery files that exist:** [`../llms.txt`](../llms.txt) (curated +
  full category index for LLM crawlers), `../sitemap.php` (category-priority sitemap),
  and `../robots.txt` (points at the sitemap). There is no `llms-full.txt`.
- The site is verified in Google Search Console (see `seo-planning.md` for the baseline).
- **Category hub pages are indexable URLs at `/<slug>`** (`/ai-safety`, `/radio`, all
  15 listed in `llms.txt` and `sitemap.php`), server-rendered by `index.php` with a
  hand-written title, description, H1, intro and "start here" list from
  [`../category-hubs.json`](../category-hubs.json), plus `CollectionPage`/`ItemList`
  (with item names) and `BreadcrumbList` JSON-LD. nginx hands `/<slug>` to
  `index.php?hub=<slug>` via [`../conf/nginx/category-hubs.conf`](../conf/nginx/category-hubs.conf);
  `?cat=<Category>`, the old `?category=`, and `/<slug>/` all 301 to the slug so Search
  Console sees one URL per hub. Every sheet links back to its hub from a footer
  breadcrumb (`scripts/add_hub_breadcrumbs.py`, gated by `deploy.py --check`), which is
  what gives the hubs inbound links; before 2026-09 they had none and did not rank.
  Hub titles target the two-word "cheat sheets" query family Search Console actually
  shows ("git cheat sheet", "ham radio cheat sheet"), not the category name. Every
  other Explorer query parameter (`q`, `sort`, `shape`, `view`, `sheet`, `path`,
  `fresh`, `interactive`) expresses client state, not a document, and is `noindex`.
- **To add or rename a category**: add the sheets to `category-map.php`, add the hub
  entry (slug, title <= 60, description 150-200, h1, intro, start_here) to
  `category-hubs.json`, rebuild the catalog, run `python3 scripts/add_hub_breadcrumbs.py`,
  and if a slug changed add a `location = /old-slug { return 301 /new-slug; }` to
  `conf/nginx/redirects.conf`. No nginx change is needed for a new slug.

## Social preview image (OG)

`images/cheatsheets-og-portfolio.png` is the constellation map from the Explorer's
Map lens, not a hand-designed graphic: `scripts/render_og_map.py` drives headless
Chromium (Playwright, from `.venv`) against a local `php -S` server, loads
`index.php`'s `?view=map&og=1` render mode (added purely for this script — forces
dark theme and the map lens, hides all chrome, fixes the canvas at 1200x630, and
draws a caption with the live `{count} references · {edges} cross-links`), and
screenshots the result.

Re-run it manually whenever the map's shape has moved enough to be worth a new
preview (a batch of new sheets, a big cross-linking pass) — it is **not** wired into
any git hook or CI workflow, because a Chromium launch is too slow for pre-commit
and not worth an extra job on every push:

```bash
.venv/bin/python scripts/render_og_map.py          # renders + optipng, prints the byte size
.venv/bin/python scripts/render_og_map.py --check   # verifies the committed PNG is 1200x630, no render
```

Commit the regenerated PNG by explicit path. `scripts/deploy.py --check` does not
gate this file — a stale-but-present OG image is not a build failure, just worth
refreshing periodically. If a Chromium GitHub Action step ever becomes trivial to
add to `.github/workflows/update-popularity.yml`, wire it there as a commented-out
optional step next to the popularity fetch; until then this stays a manual step.

## Measurement (pulled, not eyeballed)

- **Search Console** via the `search-console` MCP: `list_sites`, then
  `query_search_analytics` for impressions/clicks/position. Use it to refresh the
  striking-distance list before trusting numbers older than a few weeks.
- **Traffic** via the `cloudflare-stats` skill (this repo is the model for it) —
  visits, page views, and top pages for `cheatsheets.davidveksler.com`.
- **Explorer usage (GA4 DebugView or reports)**: `index.php`'s inline JS fires
  `explorer_search {chars, results}`, `explorer_drawer {file, from}`,
  `explorer_view {view}`, `explorer_surprise {file}`, `explorer_theme {theme}`,
  `explorer_path_start {id}`, and `explorer_path_step {id, step}` via `gtag` when
  present (GA4 property `properties/543339529`, tag injected by Cloudflare, not in
  the HTML). Palette-usage share (`explorer_search` events per session) and the
  category-landing-page impression count in Search Console are the two KPIs the
  redesign spec ties success to; pull both before/after a deploy the same way as the
  existing traffic pull, not eyeballed.

## Promotion channels

Positioning (from `marketing-campaign-plan.md`): lead with the **system** — one person
plus AI agents maintaining 160+ governed, git-audited reference pages — not any single
page. Run separate mini-campaigns per audience:

- AI / developer -> `how-its-built.html`
- Ham radio -> `baofeng-uv5r-quick-ref.html`
- Martial arts -> `judo.html`
- Space / engineering -> `orbital-rockets-comparison.html`
- Advocacy -> `objectivism.html` (kept separate from the developer campaign)

Tag every manually shared link with the canonical UTM shape
(`utm_campaign=agentic_cheatsheets_2026`) documented in the campaign plan.

**Reddit (daily, draft-tier):** the [`reddit-daily-drafts`](reddit-daily-drafts.md) runbook
drives a routine that scans niche subreddits for threads a cheatsheet genuinely answers and
stages ready-to-paste comment/post drafts for review. The subreddit→cheatsheet map is
[`../marketing/reddit-subreddit-map.json`](../marketing/reddit-subreddit-map.json); the
read-only scanner is [`../scripts/reddit_scan.py`](../scripts/reddit_scan.py). It never posts —
David posts from his own account, then logs the result in the campaign measurement log.

## Newsletter

Not live. [`newsletter.md`](newsletter.md) is the spec: Resend-backed monthly digest built
from git history + `popularity.json`, double opt-in intake, draft-tier routine, David sends.
Its KPI table (confirm/open/click/complaint rates) appends to `seo-progress.md` alongside the
GSC and Cloudflare pull once it ships.

## Cross-linking

This site is the **firearms-bridge donor** (Phase 3) in the cross-domain plan: a
high-organic donor that deep-links **into** `coloradofirearmswatch.org` (CFW is
pseudonymous and only receives links — never link a personal identity from it).
The live link list and status are in
[`~/Projects/seo-crosslinking`](../../seo-crosslinking/README.md) and its
[`domains/cheatsheets.davidveksler.com/TODO.md`](../../seo-crosslinking/domains/cheatsheets.davidveksler.com/TODO.md).
Do not copy the plan here — read it there and follow the donor/receiver map and
per-domain constraints.
