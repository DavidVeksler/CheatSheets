# Spec: AI model release log — dated, chronological, maintained

**Target file:** `ai-model-release-log.html`
**Batch:** [niche-utility-batch-2026-08.md](niche-utility-batch-2026-08.md) (sheet 10 of 10).

## Why this topic

This is the **largest single pool of unclaimed demand on the site.** Across the 90 days to
2026-08-22, month-stamped release queries produced roughly 2,400 impressions at positions 5–12
with **zero clicks**:

| Query | Impressions | Position |
|---|---|---|
| ai frontier models developments last 24 hours | 1,054 | 12.4 |
| frontier ai model releases july 2026 | 347 | 8.2 |
| latest frontier ai models june 2026 | 215 | 8.5 |
| frontier ai models 2026 | 202 | 12.1 |
| top frontier ai models july 2026 | 159 | 9.1 |
| latest frontier ai models july 2026 | 149 | 6.3 |
| current frontier ai models july 2026 | 132 | 5.3 |
| frontier ai model releases june 2026 | 111 | 10.7 |

Plus a long tail of date-literal queries (`"august 15, 2026" "ai model" release`,
`"august 9, 2026" ai model release`) that are unmistakably people — and, from their phrasing,
automated research agents — asking **what shipped on a specific date**. `ai-frontier.html` absorbs
these because it is the site's AI authority, and it disappoints them because it is a landscape of
labs, not a timeline.

There is a second argument, and it is the one that makes this page worth maintaining. **A dated
release log is the single content type an AI assistant cannot answer from its own weights.** Every
model has a cutoff; every model is asked "what came out last month"; and the failure is invisible
to the user. This is the inverse of the AI-Overview problem that flattens the rest of this site's
traffic — here, the AI systems that consume this site heavily (ChatGPT-User alone fetches
`ai-frontier.html` ~1,600 times a week) have a structural reason to fetch this page specifically.

It also fits the house doctrine: the page is a **register a scheduled routine maintains**, which
makes it a working demonstration of the agentic-automation thesis rather than another artifact
that rots.

## Targeting

- **Primary query:** `latest ai model releases [month] [year]`
- **Secondary:** `frontier ai model releases 2026`, `ai model release timeline`,
  `what ai models came out this month`, `gpt/claude/gemini release dates`,
  `ai model release history`
- **Mode:** research, recurring, increasingly **agent-mediated** — a meaningful share of these
  queries are issued by research agents, not humans, which is an explicit design input (see
  Content approach §1).
- **Scope diff against `ai-frontier.html` — binding.** `ai-frontier` owns
  `frontier ai labs / companies / models / providers / list` (positions 2–6; do not touch). This
  page owns **dated release events**: any query containing a month, a year, "release", "launch",
  "shipped", "timeline" or "history". The title, H1 and description must not contain the phrase
  "frontier AI labs" or read as a list of companies. Before shipping, diff the two pages' query
  families in GSC and re-word on any overlap, per the standing rule in `seo-planning.md`.

## Draft title / H1 / meta

- `<title>`: `AI Model Release Log 2026: Dated Frontier Launches` (49 chars)
- **H1:** `AI Model Releases, Dated: The 2026 Log`
- **Meta description (draft):**
  `Every notable AI model release of 2026 with its exact ship date, context window, pricing, weights status and official announcement, newest first and updated weekly.` (162 chars)

## Reader outcome

The reader can answer "what shipped, and when" for any month of the covered period — naming the
model, the date, what changed relative to its predecessor, and the primary announcement — without
trusting a chat answer whose training cutoff they cannot see.

## Success metric

Organic entries on month-stamped release queries — measured as **the number of distinct dated
queries landing on this URL**, which is the honest metric for a portfolio page. Two secondary
KPIs, both of which matter more here than on any other page:

1. **AI crawler fetch rate on this URL specifically** (Cloudflare, same method as the
   `seo-planning.md` baseline). If the citability thesis is right anywhere, it is right here.
2. **Freshness lag** — days between a major release and its appearance on the page. Target ≤ 7
   days. A release log that lags is worse than no release log, and this metric is the page's own
   quality gate.

## Content approach

**Inclusion rule, stated on the page** (this is what keeps it from becoming a second labs list):
a row exists only for a **dated, publicly announced model release or major version** from a lab
that trains its own frontier or near-frontier models, with a primary-source announcement URL.
Not included: pricing changes, product features, funding, benchmark results without a model, or
rumours. Say the rule out loud; it is the page's editorial spine and its defence against drift.

1. **Quick Reference: the last 90 days** (signature element) — a reverse-chronological strip of
   recent releases, each as a dated card: date, lab, model, one-line "what changed". Above it, a
   single visible line: **"Last updated: YYYY-MM-DD · covering releases through YYYY-MM-DD"** —
   two distinct dates, because a stale-but-honest log is usable and a stale log claiming freshness
   is not. Designed to be readable by an agent as well as a human: real dates in `<time datetime>`
   attributes, no information carried only by styling.
2. **The master release table** — the core, reverse chronological, one row per release: date
   (ISO), lab, model name and version, modality, context window, weights status (closed /
   open-weight with licence named), API availability, headline price per million tokens in and
   out, the one-line change from its predecessor, and a link to the **official announcement**
   (never a news article). Target ≥ 60 rows for 2026 to date.
3. **Month sections with anchors** — the table grouped under `#2026-08`-style anchors with a
   two-sentence month summary each, because the queries are month-shaped and the searcher's
   destination should be their month, not the top of a long table.
4. **Timeline visual** — a horizontal year timeline with a lane per lab and a marker per release,
   so the cadence and the clustering (the pattern where three labs ship within a fortnight) is
   visible at a glance. Inline SVG, labelled in text, degrading to the table on narrow screens.
5. **Version-lineage blocks** — per major family, the ordered chain of versions with dates and the
   deprecation/retirement dates where the lab has published them. Retirement dates are genuinely
   hard to find in one place and are the most useful thing here for anyone maintaining code.
6. **What "release" means** — a short, honest section on the ambiguity the table has to resolve:
   preview versus GA, staged rollouts, API-before-app, region-limited launches, and silent model
   swaps behind the same name. Name the convention this page uses and apply it consistently.
7. **What changed, in aggregate** — a small set of derived views over the same data: releases per
   quarter, the open-weight share over time, context-window growth, and price-per-token
   trajectory. This is the synthesizing content that keeps the page from being a bare list (and
   from a thin-content classification), and none of it requires an opinion.
8. **Coverage and method** — which labs are tracked and why, how a release qualifies, how often the
   page is updated, and how to report a missing release (link to a GitHub issue on the repo, per
   the house issues-as-intake practice).
9. **Related sheets** footer per the cross-link map.

## Maintenance — the page ships with its routine

This page is **not done when it is published.** Build the maintenance routine in the same session,
per the automation ladder:

- **Routine name:** `cheatsheets-ai-release-log-weekly` (naming convention: `<domain>-<action>-
  <cadence>`), scheduled overnight, staggered against the existing fleet.
- **Autonomy tier: draft.** It appends verified rows and opens a PR or commits to `main`; it never
  deploys. The deploy gate stays human, per the house rule.
- **Untrusted input model:** announcement pages, news posts and social posts are *claims to judge*.
  A row ships only with a primary-source URL from the lab itself. If the routine finds
  agent-directed instructions in a fetched page, it reports and moves on.
- **Hard limits:** never edit existing rows' dates without a source diff; cap at N new rows per
  run; on any anomaly, change nothing and report.
- **Quiet success, loud failure:** "0 releases this week" is a valid report.
- The runbook is the spec of record; the SKILL.md summarizes it and defers to it.

## Volatile-facts register

**Overall: VOLATILE by construction — this page is a freshness mechanism, not a victim of one.**
- Every row: pricing, context window and availability change after release. Date each row's
  verification, not just the page.
- Deprecation/retirement dates: published late and changed often.
- The `Last updated` / `covering through` pair is the page's most important fact and must never be
  written by hand — the routine sets it.
- Failure mode to design against: a log that silently stops updating. Consider a visible staleness
  banner when `covering through` is more than 21 days old, computed at build time.

## Index category

`AI & Safety`.

## Reading conditions

**Desk, laptop, research mode — plus a genuinely non-human reader.** Consequences: fast-loading
static HTML with the table in the initial paint (agents do not run JavaScript reliably), semantic
`<table>` markup with proper headers rather than a div grid, `<time datetime>` on every date, and
`llms.txt` registration on day one. For humans: sticky table headers, month anchors in the URL, and
a table that survives 375 px via an `overflow-x: auto` wrapper with the date and model columns
visually pinned.

## Cross-link map

- **Internal outbound:** `ai-frontier.html` (the labs landscape — link both ways; this page must
  hand off "who are the labs" and receive "when did it ship"), `ai-models-compared.html` (the
  which-model-for-which-job hub), `ai-model-api-pricing.html`, `open-weight-ai-models.html`,
  `ai-progress-dashboard.html` (benchmarks over time — the natural sibling view),
  `ai-coding-agents-compared.html`.
- **Reciprocal inbound:** a contextual line from `ai-frontier.html` and `ai-models-compared.html`.
  `ai-frontier` is the strongest page on the site; the inbound link there is this page's fastest
  route to being indexed and fetched.
- **Registration:** `category-map.php`, `llms.txt` (both the curated strongest-pages section once
  it earns it, and the AI category index immediately) — the 2026-07-21 finding was that new pillar
  pages were silently missing from `llms.txt`; do not repeat it.

## og:image / shareable artifact

The timeline visual — lab lanes with release markers across the year — at 1200×630. It is the one
view of this data nobody else publishes, and the screenshot-this artifact.

## Jurisdiction scope

Global. One stated scope decision instead: **which labs are tracked** (the frontier and
near-frontier trainers, named explicitly, matching `ai-frontier.html`'s roster plus open-weight
trainers), and an honest line that the page tracks *announced* releases, so labs that ship without
announcement are structurally under-represented.

## Density targets

Master table ≥ 60 rows × 11 columns for 2026 to date; month sections ≥ 8; lineage blocks ≥ 8
families; derived views ≥ 4 charts or tables; the last-90-days strip ≥ 10 cards. Every row carries
a primary-source link — a row without one does not ship.

## Research sources (verify against these, per Rule 1)

**Primary announcements only:** OpenAI, Anthropic, Google DeepMind, Meta, Mistral, xAI, DeepSeek,
Alibaba/Qwen, Cohere, AI21 and equivalent lab blogs, model cards, and official pricing and
deprecation pages. Model cards and API documentation for context windows and pricing. Hugging Face
model pages for open-weight licence terms. **Never** a news aggregator, a benchmark leaderboard, or
another tracker site as the source of record — those are leads for the routine to verify, not
citations. Where a date is disputed (preview versus GA), record both and say which convention the
row uses.

## Visual design

**Identity: flight-recorder / ship's log.** Monospaced entry lines on a dark instrument ground,
each entry stamped with an ISO date in a boxed field, lab names as fixed-width call signs — the
aesthetic of a log that a machine writes and a human reads. Light mode is the paper logbook: ruled
lines, ink-blue entries, a red stamp for the `Last updated` block. The timeline is the one place
colour does work (a hue per lab), always with the lab name printed on the marker as well. Deliberate
contrast with `ai-frontier.html`'s design so the two pages read as siblings, not duplicates. No
JavaScript required; the derived views are static SVG generated at build time by the same script
that maintains the table.

**Palette and type tokens — binding.** Dark instrument mode: recorder black `#0A0F14`, panel
`#121B24`, phosphor text `#D7E1E8`, cyan trace `#43B7D6`, warning amber `#E3A83B`, update-stamp
red `#D55252`. Light logbook mode: paper `#F3EBD8`, ink `#17324D`, rule `#9AA9B2`, stamp
`#B23A48`. Use a system monospace for dates, model IDs and measurements; use a compact grotesque
system stack for summaries and headings. Lab colours are data-series colours confined to the
timeline and derived charts — they are not decorative section accents.

**Composition contract — this must not become a long card feed.** Use the recent pages as a bar
for visual explanation — the shared time axis in `blockchain-deposits-withdrawals.html`, the
labelled inline-SVG plates in `mpc-wallet-architecture.html`, and the strong changes in scale in
`post-quantum-cryptography.html` — without copying the custody batch's shell. The page must use at
least these six distinct information shapes:

1. **Instrument-status masthead:** a compact two-column header, title and inclusion rule on the
   left; `LAST UPDATED`, `COVERING THROUGH`, row count and freshness state on a hard-edged recorder
   panel on the right. This is operational status, not four generic statistic cards.
2. **Ninety-day event tape:** a full-width vertical date rail on phones and a horizontal strip on
   desktop. Release entries attach directly to the rail like flight-recorder events; alternating
   sides or lab colours must never scramble chronology.
3. **Master logbook:** the release table is an uninterrupted ruled register with month dividers
   spanning all columns, pinned date/model columns and stamped source links. Do not wrap each row
   in a card.
4. **Lab-lane timeline:** one wide, quiet SVG plate using a shared month axis, collision-aware
   labels and explicit lab lane names. At 375 px it becomes stacked quarterly panels with the
   same axis, not a uniformly shrunken desktop graphic.
5. **Lineage schematics:** model families render as compact branching transit lines with version
   nodes, preview/GA/deprecation glyphs and dates. They must look categorically different from the
   master table and remain understandable without colour.
6. **Derived small multiples:** releases per quarter as bars, open-weight share as a 100% stack,
   context growth as a step plot and price movement as an indexed slope chart. Keep one chart
   grammar per question; do not repeat four doughnuts or four identically framed cards.

**Page rhythm and anti-patterns.** Alternate dense register sections with one wide explanatory
graphic, then a compact two-up comparison, then dense register again. Hard corners, rules, stamps
and datum ticks carry the identity; avoid floating rounded cards, glass effects, decorative
gradients, icon clouds, oversized empty hero space and a repeated three-column card grid. The
1200×630 preview must crop the lab-lane timeline plus the live coverage stamp, not merely the H1.
