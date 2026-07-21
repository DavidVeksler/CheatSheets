# Dev-spoke content plan — prepared work, execute after 2026-08-06

Prep for the Software & DevOps striking-distance work flagged in
[`seo-planning.md`](seo-planning.md). **Do not execute before the 2026-08-06 checkpoint** — the
title/consolidation freeze holds until then, and even the content-only items below are held so the
August pull reads clean. This doc is the diagnosis + ready-to-execute plan so the work can start the
moment the freeze lifts.

## Method and baseline

Data: Search Console, 90-day window **2026-04-22 → 2026-07-20**, pulled 2026-07-21, dimensions
`page` × `query`. Positions/impressions below are from that pull — re-pull before executing so lift
is measured against a fresh baseline, not this snapshot.

**Headline finding:** every target page already has its head keyword in its title and H1. They rank
at **position 40–87 for their exact "[topic] cheat sheet" head terms** anyway. So this is an
**authority/depth problem, not a listing problem** — the lever is on-page content depth and internal
authority, and mostly *not* title rewrites. That matters because it means most of this work is
content addition, which does not touch the frozen title/consolidation surface.

Cross-check against the site-goals ground rule: these are goal-3 (agentic case study — organic
traffic is the KPI) pages, so judging them on search performance is legitimate. None are proposed
for pruning.

## Tier 1 — thin page + clear query gap + existing authority (highest ROI)

### azure-devops.html
- **Diagnosis:** thinnest page in the cluster (**2,784 words**, no "best practices" section) yet it
  **wins "azure devops cheat sheet" at position 2.1 (22.7% CTR)**. Authority is proven; the page is
  simply underbuilt. It fails the Coverage Contract's density floor for a topic this large.
- **Query gap (90d):** `azure devops best practices` 162 impr @ pos 52.2; `best practices for azure
  devops` 93 impr @ pos 43.8 (255 impr combined, page 5). `azure devops boards repos pipelines test
  plans …` 71 impr @ **pos 9.4** (already page 1, close).
- **Action (content-only, no title change):** add a substantive **"Azure DevOps best practices"**
  section (branching policy, pipeline security, environments/approvals, work-item hygiene, IaC gates)
  and expand thin sections toward the density floor (~20+ substantive entries). Every claim verified
  against Microsoft Learn; keep the visible `Last verified` current.
- **Acceptance:** passes `scripts/seo_check.py`; title unchanged; `dateModified` = real edit date.
- **Success metric:** `azure devops best practices` family moves off page 5 toward page 1–2 at
  roughly constant position on the head term (guard-rail: do not lose the pos-2 "azure devops cheat
  sheet" ranking).

### dotnet-cheatsheet.html
- **Diagnosis:** 5,341 words but **no C# keywords reference** (2 incidental "keyword" mentions). The
  single biggest impression pool in the cluster is a query it barely serves.
- **Query gap (90d):** `c# keywords cheat sheet` **408 impr @ pos 28.2**; `c# cheat sheet` 53 impr @
  pos 43.7; `c sharp cheat sheet` / `csharp cheat sheet` ~pos 43. `dotnet cheat sheet` already pos 8.7.
- **Action (content-only):** add a dedicated **"C# keywords cheat sheet"** reference — a scannable
  table of the C# keyword set (contextual keywords noted), grouped (types, modifiers, control flow,
  query, async, pattern) with a one-line purpose each. This directly answers the 408-impr query and
  deepens the page.
- **Success metric:** `c# keywords cheat sheet` moves from pos 28 toward page 1–2.

## Tier 2 — moderate depth, competitive terms (targeted enrichment)

### clean-architecture-dotnet.html
- **Diagnosis:** the "cheat sheet" framing already ranks (`clean architecture cheat sheet` **pos
  6.0**), but the higher-volume bare-topic queries do not: `.net clean architecture` 201 impr @ pos
  40.9; `clean architecture in .net` 184 impr @ pos 41.6 (385 impr combined, page 5).
- **Action (content-only):** strengthen the canonical ".NET clean architecture" explanation (layer
  dependency rules, a concrete solution/project layout, where EF Core/CQRS/MediatR sit) so the page
  competes for the bare topic terms, not only the "cheat sheet" modifier. Verify against Microsoft's
  reference architecture guidance.
- **Success metric:** `.net clean architecture` / `clean architecture in .net` move up from pos ~41.

### databases.html
- **Diagnosis:** 9,025 words. `database comparison` 27 impr @ pos 65.6; `database comparison chart`
  20 impr @ pos 34.9; `database management system cheat sheet` 73 impr @ pos 39.5. Competitive terms,
  ranking deep.
- **Action (content-only):** elevate an explicit **"database comparison chart"** artifact (a
  single scannable SQL-vs-NoSQL-vs-graph-vs-vector matrix with the decision criteria) near the top,
  which matches the `database comparison chart` intent and is the kind of self-contained artifact
  answer engines extract. Lower confidence than Tier 1; competitive SERP.

## Tier 3 — do NOT add content (wrong lever) / defer

- **postgresql.html — already deep and fresh; do NOT add content.** 18,397 words, verified
  2026-07-04, and it *still* sits at **pos 44–47 across the entire `postgresql`/`psql cheat sheet`
  query family** (~150+ impr combined, tightly clustered on page 5). On-page depth is not the
  constraint — this is off-page authority in a crowded SERP (postgresqltutorial, cheat-sheets.org,
  etc.). Right lever: internal-link support from higher-authority pages (the dev pillar, related
  spokes) and time, not more words. Re-evaluate after the pillar backlinks age.
- **aws-vs-azure.html — defer.** 1,498 impr but positions 67–87 on brutally competitive terms
  (`aws vs azure services` pos 67, 200 impr). Cloud-vendor and big-media pages own this SERP; on-page
  work is low ROI. Leave as a reference page (serves the case-study goal regardless of rank).
- **git-scm.html — mostly won its winnable niche.** Ranks `git cheat sheet interactive` pos 9.2 and
  `interactive git cheat sheet` pos 16.8. `git commands` (231 impr) sits at pos 62 — a head term
  owned by git-scm.com/atlassian; not worth chasing on-page.
- **javascript-for-architects.html — intent mismatch, revisit as a title question post-freeze.** Its
  478 impr are almost all accidental long-tail code-error matches (astro eslint, rxjs) at pos 4–8,
  not "javascript architecture" intent. That is a positioning/title question (frozen), not a content
  add. Flag for a title/scope review after 2026-08-06, not for enrichment now.
- **python-for-architects.html — low volume.** `python for architects` 20 impr @ pos 22.5. Minor;
  fold into a general depth pass only if convenient.

## Execution checklist (per page, after 2026-08-06)

1. Re-pull the page's query family (fresh baseline) before editing.
2. Make the content-only change above; **do not** rewrite titles during the same window as the WP1
   title measurement unless a page is explicitly cleared.
3. Run `scripts/seo_check.py` (0 failures) and the accuracy protocol on every new number.
4. Update the visible `Last verified` date and JSON-LD `dateModified`.
5. Commit one page per commit; each page starts its own before/after measurement at roughly constant
   head-term position (guard-rail: never trade a won head-term ranking for long-tail gains).
