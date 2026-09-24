# Marketing quick path: SEO, promotion, measurement

Thin router. SEO working doc: [`../TODO/META-seo-planning.md`](../TODO/META-seo-planning.md). Campaign assets, UTM shape, publishing queue, and promotion log: [`../TODO/marketing-campaign-plan.md`](../TODO/marketing-campaign-plan.md). Metadata rules: [`../AGENTS.md`](../AGENTS.md) > *Required metadata template*.

## SEO standards

- Per-page gate `scripts/seo_check.py` (title ≤ 60, description 150-200, canonical, valid JSON-LD) plus OG/X tags, keywords, image alt text, and `TechArticle` JSON-LD matching visible content.
- Discovery files: [`../llms.txt`](../llms.txt), [`../llms-full.txt`](../llms-full.txt), `../sitemap.php` (category-priority), `../robots.txt` (points at the sitemap). Verified in Google Search Console.

## Category hub pages

- Indexable URLs at `/<slug>` (e.g. `/ai-safety`, `/radio`), all listed in `llms.txt` and `sitemap.php`. Server-rendered by `index.php` from [`../category-hubs.json`](../category-hubs.json) (title, description, H1, intro, start-here list) with `CollectionPage`/`ItemList` and `BreadcrumbList` JSON-LD.
- nginx routes `/<slug>` → `index.php?hub=<slug>` via [`../conf/nginx/category-hubs.conf`](../conf/nginx/category-hubs.conf). `?cat=<Category>`, `?category=`, and `/<slug>/` 301 to the slug.
- Every sheet links back to its hub from a footer breadcrumb (`scripts/add_hub_breadcrumbs.py`, gated at deploy); these are the hubs' only inbound links.
- Hub titles target the "<topic> cheat sheet" query family seen in Search Console, not the category name.
- All other Explorer query params (`q`, `sort`, `shape`, `view`, `sheet`, `path`, `fresh`, `interactive`) are client state and `noindex`.
- **Add or rename a category:** add sheets to `category-map.php`; add the hub entry (slug, title ≤ 60, description 150-200, h1, intro, start_here) to `category-hubs.json`; rebuild the catalog; run `python3 scripts/add_hub_breadcrumbs.py`; on a slug rename add `location = /old-slug { return 301 /new-slug; }` to `conf/nginx/redirects.conf` and ship it per [`../deploy/DEPLOY.md`](../deploy/DEPLOY.md). A new slug needs no nginx change.

## Social preview image (OG)

`images/cheatsheets-og-portfolio.png` is a headless-Chromium screenshot of the Explorer's Map lens (`index.php?view=map&og=1`). Manual, not in any hook or CI (Chromium is too slow; a commented-out step sits in `.github/workflows/update-popularity.yml`). Re-run after a batch of new sheets or a big cross-linking pass, then commit the PNG by path. Not deploy-gated.

```bash
.venv/bin/python scripts/render_og_map.py           # render + optipng, prints byte size
.venv/bin/python scripts/render_og_map.py --check   # verify committed PNG is 1200x630
```

## Measurement (pulled, not eyeballed)

- Search Console: `search-console` MCP (`list_sites`, `query_search_analytics`). Refresh striking-distance data before trusting numbers older than a few weeks.
- Traffic: `cloudflare-stats` skill for `cheatsheets.davidveksler.com`.
- Referral channels (search / AI assistants / Reddit / social): `ssh johngalt@198.211.102.9 'python3 - --md' < scripts/referrer_report.py`. Origin logs keep ~3 weeks; Cloudflare free has no referrers; GA4 has data only for 2026-06-25 → 07-03. Google counts in the logs run ~4x GSC clicks, so take search volume from GSC.
- Explorer usage (GA4 `properties/543339529`, tag injected by Cloudflare, not in the HTML): `index.php` fires `explorer_search {chars, results}`, `explorer_drawer {file, from}`, `explorer_view {view}`, `explorer_surprise {file}`, `explorer_theme {theme}`, `explorer_path_start {id}`, `explorer_path_step {id, step}`. Explorer KPIs: `explorer_search` events per session, and category hub impressions in Search Console.
- Log results in [`seo-progress.md`](seo-progress.md).

## Promotion

Lead with the system (one person plus AI agents maintaining a governed, git-audited reference corpus), with separate mini-campaigns per audience: AI/dev → `how-its-built.html`; ham radio → `baofeng-uv5r-quick-ref.html`; martial arts → `judo.html`; space/engineering → `orbital-rockets-comparison.html`; advocacy → `objectivism.html` (kept separate from the developer campaign). Every shared link uses `utm_campaign=agentic_cheatsheets_2026` (full shape in the campaign plan).

- **Reddit (daily, draft tier):** [`reddit-daily-drafts.md`](reddit-daily-drafts.md); map [`../marketing/reddit-subreddit-map.json`](../marketing/reddit-subreddit-map.json); scanner [`../scripts/reddit_scan.py`](../scripts/reddit_scan.py). Never posts; David posts and logs the result in the campaign plan.
- **Cold email (draft tier):** [`cold-outreach.md`](cold-outreach.md); focus pages [`../marketing/cold-outreach/pages.json`](../marketing/cold-outreach/pages.json); gate/renderer [`../scripts/cold_outreach.py`](../scripts/cold_outreach.py). One pillar or spoke per email, drafted only when the address scores > 0.5. Prospect data stays in the private `cheatsheets-outreach` repo.
- **Newsletter:** not sending yet; spec and status in [`newsletter.md`](newsletter.md). Its KPIs go in `seo-progress.md` once it ships.

## Cross-linking

This site is the **firearms-bridge donor** (Phase 3) of the cross-domain plan: it deep-links into `coloradofirearmswatch.org` (CFW is pseudonymous and only receives links; never link a personal identity from it). Follow [`~/Projects/seo-crosslinking`](../../seo-crosslinking/README.md) and its [`domains/cheatsheets.davidveksler.com/TODO.md`](../../seo-crosslinking/domains/cheatsheets.davidveksler.com/TODO.md); don't copy the plan here.
