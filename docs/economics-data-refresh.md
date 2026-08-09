# Economics comparison data refresh

`scripts/build_economics_batch.py` rebuilds the four comparison sheets introduced
in August 2026:

- `economic-systems-compared.html`
- `political-ideologies-compared.html`
- `us-states-vs-countries-gdp.html`
- `red-vs-blue-state-economies.html`

Run it from the repository root:

```powershell
python scripts/build_economics_batch.py
python scripts/seo_check.py economic-systems-compared.html political-ideologies-compared.html us-states-vs-countries-gdp.html red-vs-blue-state-economies.html
```

## Data contract

The generator downloads BEA state GDP and regional price parity ZIP files,
Census ACS ranking workbooks and population estimates, World Bank country GDP,
population, PPP, and exchange-rate series, and the Tax Foundation burden table.
It fails closed when the state or country row counts are implausible.

Two slow-release series are pinned in the script with visible vintage labels:

- 2024 BLS annual-average state unemployment, because automated requests to the
  BLS public-data endpoint are intermittently blocked.
- FFY 2023 Rockefeller Institute federal balance of payments per resident,
  transcribed from Table 6 of the 2025 report.

Before changing either pinned series, verify every value against the named
primary report and update the page's visible data-year block. Never silently mix
monthly unemployment with the annual-average comparison.

## Refresh cadence

Rebuild after the annual BEA RPP and Census ACS releases, then review the World
Bank country vintage for a common comparison year. After the November 2028 U.S.
election, replace the red/blue classification and its sensitivity set before
publishing any new state comparison.

After each refresh, serve the pages locally at desktop and 375-pixel widths,
check horizontal table scrolling and print styles, regenerate all four 1200x630
preview images, run the SEO gate, and commit the refreshed outputs.
