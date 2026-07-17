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

## Measurement (pulled, not eyeballed)

- **Search Console** via the `search-console` MCP: `list_sites`, then
  `query_search_analytics` for impressions/clicks/position. Use it to refresh the
  striking-distance list before trusting numbers older than a few weeks.
- **Traffic** via the `cloudflare-stats` skill (this repo is the model for it) —
  visits, page views, and top pages for `cheatsheets.davidveksler.com`.

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

## Cross-linking

This site is the **firearms-bridge donor** (Phase 3) in the cross-domain plan: a
high-organic donor that deep-links **into** `coloradofirearmswatch.org` (CFW is
pseudonymous and only receives links — never link a personal identity from it).
The live link list and status are in
[`~/Projects/seo-crosslinking`](../../seo-crosslinking/README.md) and its
[`domains/cheatsheets.davidveksler.com/TODO.md`](../../seo-crosslinking/domains/cheatsheets.davidveksler.com/TODO.md).
Do not copy the plan here — read it there and follow the donor/receiver map and
per-domain constraints.
