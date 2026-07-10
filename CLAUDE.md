See AGENTS.md

## SEO planning

Use [`TODO/seo-planning.md`](TODO/seo-planning.md) as the working doc for SEO strategy work
(Search Console baseline, striking-distance opportunities, open questions). Pull fresh data via
the `search-console` MCP tools rather than trusting stale numbers in that file.

## Cached CDN dependencies (SRI hashes)

Precomputed `integrity` values for the pinned CDN assets, so they don't have to be
recalculated each time. Computed from the real CDN bytes with
`curl -sL <url> | openssl dgst -sha384 -binary | openssl base64 -A`.
**If you bump a version, recompute the hash for that file and update this table.**

| Asset | Version | URL | integrity (sha384-…) |
|---|---|---|---|
| Bootstrap CSS | 5.3.8 | `https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/css/bootstrap.min.css` | `sha384-sRIl4kxILFvY47J16cr9ZwB07vP4J8+LH7qKQnuqkuIAvNWLzeN8tE5YBujZqJLB` |
| Bootstrap JS (bundle) | 5.3.8 | `https://cdn.jsdelivr.net/npm/bootstrap@5.3.8/dist/js/bootstrap.bundle.min.js` | `sha384-FKyoEForCGlyvwx9Hj09JcYn3nv7wiPVlz7YYwJrWVcXK/BmnVDxM+D2scQbITxI` |
| Bootstrap Icons CSS | 1.13.1 | `https://cdn.jsdelivr.net/npm/bootstrap-icons@1.13.1/font/bootstrap-icons.min.css` | `sha384-CK2SzKma4jA5H/MXDUU7i1TqZlCFaD4T01vtyDFvPlD97JQyS+IsSh1nI2EFbpyk` |

All `<link>`/`<script>` CDN tags must carry `integrity="sha384-…" crossorigin="anonymous"`; load JS with `defer`. (Hashes last computed 2026-06-24.)
