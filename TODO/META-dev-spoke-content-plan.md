# Dev-spoke content plan (Software & DevOps striking distance)

Diagnosis from a 90-day page×query GSC pull (2026-04-22 → 2026-07-20): every target page already had its head keyword in title and H1 yet ranked 40-87 for its "[topic] cheat sheet" head term. **Authority/depth problem, not a listing problem**; the lever is content depth and internal links, not titles. These are case-study-goal pages, so search is the right yardstick; none are pruned.

## Shipped (2026-07-21): measure lift at the next pull

| Page | Commit | Change | Target queries (baseline) | Guard-rail |
|---|---|---|---|---|
| `azure-devops.html` | `4870e04` | Azure DevOps best-practices section | "azure devops best practices" 162 impr @ 52.2; "best practices for azure devops" 93 @ 43.8 | keep "azure devops cheat sheet" at ~pos 2 |
| `dotnet-cheatsheet.html` | `4870e04` | C# keywords table | "c# keywords cheat sheet" 408 @ 28.2 | "dotnet cheat sheet" pos 8.7 |
| `clean-architecture-dotnet.html` | `8cbc056` | canonical .NET clean architecture explanation | ".net clean architecture" 201 @ 40.9; "clean architecture in .net" 184 @ 41.6 | "clean architecture cheat sheet" pos 6.0 |
| `databases.html` | `f33bb0a` | database comparison chart near top | "database comparison chart" 20 @ 34.9; "database management system cheat sheet" 73 @ 39.5 | |

## Do not add content (wrong lever)

- `postgresql.html`: 18k words, still pos 44-47 on the whole psql family; off-page authority problem. Lever is internal links from the dev pillar and time.
- `aws-vs-azure.html`: pos 67-87 on terms owned by vendors and big media; leave as a reference page.
- `git-scm.html`: niche won ("interactive git cheat sheet" pos 9-17); "git commands" belongs to git-scm.com/atlassian.
- `python-for-architects.html`: ~20 impr; fold into a general depth pass only if convenient.

## Open

- `javascript-for-architects.html`: its impressions are accidental long-tail code-error matches (astro eslint, rxjs), not architecture intent. Needs a title/scope review (freeze has lifted).

## Per-page execution rules

1. Re-pull the page's query family before editing.
2. Content changes and title changes go in separate measurement windows.
3. `scripts/seo_check.py` clean; verify every new number against a primary source.
4. One page per commit; never trade a won head-term ranking for long-tail gains.
