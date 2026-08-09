# Batch note — economics & liberty comparison cluster (2026-08)

Not a spec. Batch-level decisions for the four specs below, kept in one place so
they aren't repeated per-file. Delete when the last spec in the batch ships.

## Origin and evidence

These specs execute **Phase 2 of `~/Projects/freecapitalists.org/docs/specs/off-site-content.md` § 4c**:
cheatsheets.davidveksler.com takes "comparisons and explainers" on economics and
liberty subjects, with candidates drawn from the measured comparison bucket in
the mises.org GSC export — not from imagination.

Source data: `freecapitalists.org/data/gsc/mises-org-live_queries_Apr-6-2025-Jul-31-2026.json`
(third-party GSC export, 2025-04-06 → 2026-07-31, imported 2026-08-08). The
comparison bucket is exactly 10 queries, 40,837 impressions, 3.67% CTR at
weighted position 3.3. Full bucket and routing:

| Query | Impr. | Their pos | Their CTR | Disposition |
| --- | ---: | ---: | ---: | --- |
| mercantilism vs capitalism | 16,847 | 4.3 | 1.28% | **Spec: `economic-systems-compared.md`** |
| red states vs blue states economy | 5,843 | 1.5 | 2.70% | **Spec: `red-vs-blue-state-economies.md`** |
| mississippi gdp per capita vs uk | 5,028 | 4.3 | 1.89% | **Spec: `us-states-vs-countries-gdp.md`** |
| the man versus the state | 2,648 | 2.8 | 5.85% | Declined — it's a book (Spencer); primary-text demand belongs to the archive, not here |
| total gdp of red vs blue states | 2,411 | 1.6 | 5.85% | Folded into `red-vs-blue-state-economies.md` |
| dave smith vs douglas murray | 2,013 | 3.6 | 7.45% | Declined — ephemeral debate-event query; commentary is declined fleet-wide (off-site-content § 6) |
| douglas murray vs dave smith | 1,678 | 3.5 | 6.32% | Declined — same |
| neoliberalismo vs liberalismo | 1,594 | 2.4 | 11.10% | Evidence for `political-ideologies-compared.md` (we don't ship Spanish pages; the confusion it evidences is real and language-independent) |
| realism vs liberalism vs constructivism | 1,412 | 1.7 | 8.85% | Declined — IR theory is off the economics-and-liberty brief, demand is small, and the incumbent already converts at 8.85%. Watchlist only. |
| liberalismo vs neoliberalismo | 1,363 | 1.9 | 12.91% | Same as neoliberalismo row |

Rule 1 reminder applies to *content* numbers inside the specs; the GSC figures
above are measured, not anchors.

## Batch decisions (SPEC-AUDIT § 6, decided once here)

- **Index category: new label `Economics & Politics`.** Nothing existing fits —
  `Bitcoin & Finance` is personal finance/crypto, `Philosophy & Religion` is
  contemplative/doctrinal. Add the label to `category-map.php` and a style entry
  in `index.php` `$categoryStyles` when the first sheet ships. Optionally move
  `capitalism.html` into it at the same time (builder's call).
- **Niche-utility framing (TODO/README Rule 0):** every sheet in this batch is
  the "comparison tables with exact specs" passing shape. Dense verified numbers
  side by side are the product; narrative is scaffolding. A draft that reads as
  an essay has failed the batch's premise.
- **Archive deep links:** each sheet should deep-link into
  freecapitalists.org / wiki.freecapitalists.org primary texts and concept pages
  where a citation is natural (off-site-content § 5), **subject to
  `~/Projects/seo-crosslinking/`** — check the donor/receiver map before adding
  any cross-domain link.
- **Build order** (cheapest signal first, per off-site-content § 7 Phase 2):
  1. `economic-systems-compared.md` — biggest demand, weakest incumbent CTR, STABLE facts.
  2. `us-states-vs-countries-gdp.md` — distinctive angle, beatable incumbent position.
  3. `red-vs-blue-state-economies.md` — best-proven demand but incumbent at position 1.5.
  4. `political-ideologies-compared.md` — weakest measured anchor; cheap, STABLE.
