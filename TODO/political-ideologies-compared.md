# Spec: Political Ideologies Compared — Liberal, Libertarian, Neoliberal, Decoded

**Target file:** `political-ideologies-compared.html`
**Batch:** see `economics-batch-2026-08.md` (sheet 4 of 4 in build order — weakest measured anchor, cheapest build, STABLE facts).

## Why this topic

The measured anchor is indirect but real: the comparison bucket's
`neoliberalismo vs liberalismo` pair carries **2,957 impressions converting at
11–13% CTR** — searchers in Spanish are actively confused about the liberalism
word-family, and that confusion is language-independent (in English it's worse:
"liberal" means near-opposite things in the US, Europe, and Latin America).
Adjacent evidence from the same export cluster: fee.org's definitional bucket
runs 635k impressions at 0.3% CTR, with `what is a libertarian` alone at
150,910 impressions. The *definitions* are routed to wiki.freecapitalists.org
(off-site-content § 4a) — this page deliberately does not compete for them.
What the wiki cannot do, and this site's format does, is the **comparison
matrix**: eight ideologies × concrete positions, plus the lineage map showing
how one 18th-century word split into enemies.

Honest confidence note: this is the batch's lowest-confidence page — no single
high-volume English query is measured for it. It's included because it is the
cheapest build (all-STABLE facts, zero data maintenance), the natural sibling
of `economic-systems-compared.html`, and the comparative-query long tail
("libertarian vs liberal", "classical liberalism vs libertarianism") is
plausibly large but sits below both exports' 1,000-row caps. Treat it as the
experiment it is.

## Targeting

- **Primary query:** `liberal vs libertarian` (unmeasured — below export caps;
  chosen as the highest-plausibility English head term for the confusion the
  Spanish queries measure)
- **Secondary:** `classical liberalism vs libertarianism`,
  `neoliberalism vs liberalism`, `what's the difference between liberal and leftist`,
  `conservatism vs libertarianism`, `types of political ideologies chart`
- **Mode:** research (students, the politically curious, people who just got
  called a neoliberal and want to know if it's an insult). Question H2s:
  "What's the difference between a liberal and a libertarian?", "Why does
  'liberal' mean opposite things in the US and Europe?"

## Draft title / H1 / meta

- `<title>`: `Liberal, Libertarian, Neoliberal: Political Labels Decoded` (58 chars)
- **H1:** `Political Ideologies, Compared`
- **Meta description (draft):**
  `What classical liberal, liberal, libertarian, neoliberal, conservative, and socialist actually mean — one comparison matrix, a lineage map, and why 'liberal' flips meaning across the Atlantic.`

## Reader outcome

The reader can place any of the eight covered ideologies on concrete positions
(state's economic role, civil liberties, redistribution, trade, source of
authority), trace which historical branch it came from, and correctly translate
"liberal" between American, European, and Latin American usage.

## Success metric

AI answer-engine citation is the primary KPI here (comparison matrices are the
most-extracted shape), with organic long-tail entries second. Low bar, low
cost: this page earns its keep if it ranks for any 2–3 of the secondary
queries within a quarter.

## Content approach

1. **Quick Reference: the translation table** (first screen, the hook) — the
   word "liberal" (and friends) across US / UK / Continental Europe / Latin
   America / academic usage: ~6 rows × 5 columns, each cell naming what a
   self-described "liberal" there actually believes and one named example
   (party or figure). This is the un-Googleable cell-by-cell artifact and the
   direct answer to what the Spanish queries evidence.
2. **The lineage map** (signature element): classical liberalism (Locke 1689,
   Smith 1776, Mill 1859) branching through the 19th–20th centuries into
   modern American liberalism (the New Deal capture of the word),
   libertarianism (the word's 1955 reclamation — Dean Russell essay),
   neoliberalism (1938 Colloque Walter Lippmann coinage vs its 1980s+
   pejorative usage), conservatism's fusion with free-market liberalism
   (fusionism, Meyer), and social democracy. Every node carries a date and a
   named text. Rendered as a static SVG family tree, mobile-degrading to an
   indented list.
3. **The master matrix:** 8 ideologies (classical liberalism, modern US
   liberalism, libertarianism, neoliberalism-as-program, conservatism,
   social democracy, democratic socialism, national conservatism/populism) ×
   ~10 concrete criteria: state's role in the economy; taxation/redistribution
   stance; civil liberties; trade; immigration; source of political authority;
   canonical thinker + text + year; flagship policy example; nearest party
   examples (US + Europe); most-confused-with. Every cell specific — a named
   policy or thinker, never "moderate".
4. **Head-to-head: liberal vs libertarian** — the primary query answered under
   its own H2: shared ancestry, the three questions that split them (scope of
   the state beyond rights-protection, redistribution, and positive vs
   negative liberty — Berlin 1958), with a liftable 3–4 sentence answer.
5. **"Neoliberal" — the word vs the program** — short section: the term's
   three distinct uses (historical coinage, the Washington-Consensus policy
   package with its actual 10 planks (Williamson 1989), and the modern
   epithet), so the reader can tell which one a given writer means.
6. **Common mistakes** (mandatory, ≥ 6): liberal ≠ leftist; libertarian ≠
   conservative; neoliberal ≠ new liberal; classical liberalism ≠ conservatism;
   social democracy ≠ democratic socialism (ownership vs redistribution);
   fascism was not "right-wing capitalism" (link the economic-systems sheet's
   corporatism column); the left–right single axis compresses two axes (one
   honest paragraph on two-axis models and their limits — no political-compass
   meme chart).
7. **Related sheets + archive/wiki links** footer per cross-link map.

## Volatile-facts register

**Overall: STABLE** — doctrines, dates, and texts don't move. The only
slow-drift cells are "nearest party examples" (parties rebrand, split, or
drift; re-check at freshness passes, tag "as of <Mon YYYY>") and the populism
row generally. No data-year maintenance at all — the batch's cheapest page to
keep true.

## Index category

`Economics & Politics` (batch decision).

## Reading conditions

Phone, calm-to-mildly-annoyed (often arriving mid-argument from social media).
Translation table must fit a phone screen with horizontal scroll; lineage map
must degrade to a list at 375 px. Print: matrix + lineage on separate pages,
both legible in grayscale.

## Cross-link map

- **Internal outbound:** `economic-systems-compared.html` (batch sibling — the
  one-line division of labor: "systems are about who owns capital; ideologies
  are about what the state should do"; link both ways), `capitalism.html`,
  `objectivism.html` (Rand's relation to libertarianism is a famous
  matrix-footnote — she rejected the label; one line + link),
  `stoicism-practice-texts-misreadings.html` only if a natural "misreadings"
  parallel presents itself — do not force it.
- **External outbound (subject to `~/Projects/seo-crosslinking/`):**
  wiki.freecapitalists.org concept pages (Libertarianism, Laissez faire,
  Individualism — all confirmed live per off-site-content § 4a) instead of
  duplicating definitions here; archive full-text deep links for held primary
  texts named in the lineage (e.g., On Liberty, Wealth of Nations — verify
  holdings before linking).

## og:image / shareable artifact

The lineage map, dark theme — it is the page's most distinctive and most
shareable artifact. The translation table is the secondary screenshot target.

## Jurisdiction scope

Explicitly transatlantic + Latin America — the US/Europe/LatAm split *is* the
content. Party examples labeled by country. No claim to cover non-Western
ideological families; one line saying so.

## Density targets

Translation table ~30 cells; lineage map ≥ 12 dated nodes; master matrix 8 ×
10 ≈ 80 filled cells; neoliberalism section ≥ 10 entries (3 uses + 10 planks
condensed); common mistakes ≥ 6. Past the floor with room.

## Research sources (verify against these, per Rule 1)

Primary texts and their real dates (Locke, Smith, Mill, Berlin, Hayek, Mises,
Rothbard, Rawls); Dean Russell, "Who Is a Libertarian?" (The Freeman, 1955);
Williamson's 1989 Washington Consensus paper for the actual planks; Stanford
Encyclopedia of Philosophy for doctrine summaries; party platforms/official
sites for current party examples. No opinion journalism as a source for what
an ideology holds.

## Visual design

**Identity: annotated intellectual-history chart** — parchment-neutral field,
single ink color per branch family, engraved-map typography (small-caps
labels, hairline connectors), like a plate from a history-of-ideas atlas. Dark
theme: midnight chart-room. Signature element built first: the lineage SVG —
it must not look like a generic flowchart; nodes are small "title-page" cards
(work, author, year). One interactive element max: CSS-only branch
highlighting on hover via `:has()`, reduced-motion gated, fully readable
without it.
