# David Veksler's Cheatsheets

[Browse the live collection](https://cheatsheets.davidveksler.com/) ·
[See how the pipeline works](https://cheatsheets.davidveksler.com/how-its-built.html) ·
[View the public change history](https://cheatsheets.davidveksler.com/history.php)

One person plus AI agents build and maintain this collection of 160+ standalone,
interactive reference pages. The interesting artifact is not one lucky generation: it is
the governed pipeline that repeatedly turns a written spec into a researched page, runs a
self-verification gate, creates its social preview, and records every change in git.

## What makes this repository different

- **Terminal references, not summaries.** Each page aims to cover fundamentals, daily working
  knowledge, and edge cases without sending the reader elsewhere for common tasks.
- **Accuracy before prose.** Version numbers, prices, limits, defaults, and dates must be checked
  against primary sources; volatile facts are visibly dated.
- **A binding quality gate.** [`AGENTS.md`](AGENTS.md) defines the coverage, accessibility,
  metadata, freshness, and browser-verification standards used by every coding agent.
- **Auditable agentic work.** Specs, fixes, preview images, and workflow changes are committed,
  while deployment remains a separate human-approved gate.
- **Portable output.** Every cheatsheet is a self-contained HTML file with embedded CSS and JS.
  There is no framework build or client-side router.

The collection spans AI and software, security, risk and preparedness, finance, martial arts,
radio, health, philosophy and religion, engineering, home systems, and consumer defense.

## The Explorer

[`index.php`](https://cheatsheets.davidveksler.com/) is not a card grid over a folder listing.
It reads a generated catalog of every sheet's title, description, keywords, and section
headings, so its search box can find a page by a term that appears only in one of its
headings and deep-link straight there, not just match a title. A Map lens draws the 197
sheets and their ~1,500 cross-links as a constellation, clustered by category. A Paths lens
holds hand-curated trails through 4-6 sheets at a time for a given task (harden a Linux box,
plan crypto custody, program a radio). The data behind all three lenses is
[`catalog.json`](https://cheatsheets.davidveksler.com/catalog.json), built by
[`scripts/build_catalog.py`](scripts/build_catalog.py) and regenerated on every commit that
touches a cheatsheet.

## Repository map

- `*.html` — standalone cheatsheets
- `images/*.png` — 1200×630 social and gallery previews
- `index.php` — the Explorer: search, category/shape/freshness facets, a constellation map,
  and curated paths, built from `catalog.json`
- `catalog.json` — generated data layer behind the Explorer (see `scripts/build_catalog.py`)
- `paths.json` — hand-curated trails for the Paths lens
- `category-map.php` — filename-to-category source of truth
- `sitemap.php` and `llms.txt` — search and AI discovery surfaces
- `TODO/` — queued page specs plus durable SEO and audit workflows
- `how-its-built.html` — the public engineering case study for this pipeline

## Run locally

```bash
python3 -m http.server 8765 --directory .
```

Then open <http://127.0.0.1:8765/>. PHP-backed gallery pages require a local PHP server; individual
cheatsheets work through the static server above.

## Working on the collection

Read [`AGENTS.md`](AGENTS.md) first. New-page builds also follow
[`TODO/README.md`](TODO/README.md); shipped-page reviews use
[`TODO/CHEATSHEET-AUDIT.md`](TODO/CHEATSHEET-AUDIT.md). The standards are intentionally strict:
comprehensiveness, factual verification, accessible interaction, valid structured data, and a real
browser check are acceptance criteria.
