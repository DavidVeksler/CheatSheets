# Externalized costs of homelessness: implementation and evidence notes

## Scope and outline

Implement the supplied twelve-plate ledger as `homelessness-externalized-costs.html`.
No policy-prescription plate or companion-sheet crosslinks. The spec's explicit
"cross-link nothing yet" takes precedence over its proposed research-directory link.
Use engraved account-book styling: cream paper, charcoal ink, oxide headings,
green measured stamps, amber estimated stamps, outlined gap stamps; system serif
and monospace typography. The central ledger is the signature element.

Each plate moves from definition to evidence to accounting limits. Planned rows:

1. Ledger: public budget; property crime; public-space exclusion; business flight;
   sanitation; victimization; supplementary security.
2. Seen/unseen: displaced spending; foregone capacity; transferred public-order costs.
3. Public budgets: historical NYC cohort; Denver randomized outcomes; Denver costs
   and offsets; limits on extrapolating to the general population.
4. Crime: Boulder proximity; Denver displacement study; retailer closure reports;
   theft/burglary/arson attribution gaps.
5. Public space: Seattle hedonic estimates; Los Angeles working paper; transit,
   parks and libraries; explicit valuation method and overlap risks.
6. Business: SF, LA, Portland, Denver and a comparison market; vacancies versus
   attribution; BID revenue versus business losses.
7. Sanitation: San Diego outbreak burden and response; SF cleanup; needle-cost gap.
8. Violence: survey victimization; outward violence; non-comparable denominators.
9. Security: Denver BID spending; allocation to homelessness; private-spend gaps.
10. Non-investment: historical public psychiatric capacity; contemporary national
    and Colorado beds; SRO restrictions; unpriced counterfactual.
11. Comparison: street status quo; enforcement plus treatment; Denver Housing First;
    Houston coordination; LA capital costs; Denver All In Mile High expenses.
    Add a sensitivity worksheet with user assumptions, no invented empirical range.
12. Limits: causation; stock/flow; overlap; population/time/geography; missing totals.

Exemplar ledger row: private security | commercial owners/tenants | measured
spending, gap in attribution | Denver BID Security & Safety $1,056,568 in 2024 |
2024 BID annual report, p. 10 | supplementary service spending, not all attributable
to homelessness and not proof of police withdrawal.

## Source decisions

Primary research and original budgets govern figures. Tags mean measured
(recorded observation or spending), estimated (statistical/valuation calculation),
or gap (no defensible applicable figure in this review). Measured does not imply
causal. Dates are source vintages, not page-wide verification claims.

Corrections to the supplied anchors: Culhane is a historical selected cohort;
Denver SIB does not establish a literal top-decile cutoff; hedonic studies exist;
neither a national externality multiplier nor public-space cost rank is established;
victimization cannot be compared to perpetration without matched denominators;
capital development cost is not annual cost; security spending is not automatically
all homelessness-related. Preserve favorable Housing First evidence.

Source URLs, populations, dates and limitations are recorded directly beside the
page's figures. The sensitivity worksheet is a declared hypothetical calculation,
not a city estimate or confidence interval. No assumptions are persisted.

## Evidence review, September 9, 2026

- Use the August 2026 International Review of Finance publication for Seattle:
  the published estimate differs from the preliminary 2024 working paper.
- Culhane table 17 reports $40,451 while the abstract reports $40,449; the page
  identifies the table value. The abstract's net cost is $995 per unit-year.
- The Denver BID report's financial table is on PDF page 10. Its security expense
  is an all-cause category, not a homelessness attribution estimate.
- San Diego's county after-action report (page 6) gives approximately $12.5 million
  through April 2018. The later surveillance update supplies the final case series
  used here; do not present it as a count confined to calendar 2017.
- Use Cushman & Wakefield's common Q4 2024 national table for vacancy snapshots;
  retain each market boundary and distinguish LA CBD from market-wide figures.
- All In Mile High is separate from Denver SIB. The March 2026 city audit records
  cumulative reconstructed expenses, not the spec's suggested annual spending.

## Validation

Focused SEO, unique IDs, all local links/fragments, twelve plates and seven ledger
categories passed. Chromium checks passed at 1440, 768 and 375 pixels with no
document overflow; wide tables scroll. Light/dark/system themes and persistence,
reduced motion, no-JavaScript reading, and console checks passed. Calculator checks
covered defaults, reset, missing/negative/oversized inputs, reversed bounds, ties
and an alternative already cheaper before external costs. Print output has no
blank pages; preview is a rendered 1200 by 630 PNG.

Separate HTTP audit checked 29 source URLs: 22 returned 200, six restricted
automated requests with 403, and HUD returned a 202 challenge. No 404s. Restricted
links were retained; source retrieval used the research tool where available.
PHP is unavailable locally, so PHP lint and rendered PHP index/category checks
are skipped, not passed. Production deployment was not authorized.

The initial clean-clone gate exposed a pre-existing raw-byte catalog fingerprint:
Git's Windows CRLF conversion changed the hash without changing parsed content.
The catalog builder now normalizes line endings, matching its text reader. A
regression test checks cross-platform equivalence while retaining detection of
substantive content changes. No validation flags or deployment guards were bypassed.

After the fix, all 51 catalog unit tests passed. The committed snapshot passed
`python scripts/deploy.py --check --all` in a clean local clone: SEO and internal
links/assets for 201 HTML files, parsing of 15 JSON files, custody-cluster parity,
and catalog/path freshness. The validator's generic SEO success message mentions
the rendered index, but PHP was unavailable; rendered PHP checks and lint of the
8 PHP files remain explicitly skipped. Neither GitHub push nor deployment ran.
