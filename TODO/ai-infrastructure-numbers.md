# AI Infrastructure Numbers Everyone Should Know

Target file: `ai-infrastructure-numbers.html`

## Why this topic

The "Latency Numbers Every Programmer Should Know" format (Jeff Dean / Peter Norvig) is one of the most-shared engineering artifacts ever created, and no one has built the AI-datacenter equivalent. The space is vendor whitepapers and paywalled SemiAnalysis deep-dives; a neutral, single-page, order-of-magnitude reference has no occupant. HN-native format, LinkedIn-shareable, and directly supports the site's AI-governance positioning: infrastructure literacy for people making AI strategy decisions.

## Targeting

- **Primary query:** ai infrastructure numbers every engineer should know
- **Secondary queries:** how much power does an ai data center use; gpu power consumption per rack; data center pue benchmarks; cost to build ai data center per megawatt; how many gpus per megawatt
- **Mode:** Research (reference/bookmark intent, not crisis)
- **Title:** AI Infrastructure Numbers Everyone Should Know (2026)
- **H1:** AI Infrastructure Numbers Everyone Should Know
- **Meta description (150–200 chars):** The essential order-of-magnitude numbers for AI data centers: kW per rack, watts per GPU, PUE and WUE bands, MW per 10K GPUs, capex per megawatt, and time from permit to power-on.
- **Reader outcome:** An engineer, architect, or technically literate exec can sanity-check any AI infrastructure claim (vendor pitch, news article, internal proposal) against order-of-magnitude reality within 60 seconds.
- **Success metric:** HN front page or ≥500 organic sessions/month within 6 months; becomes the top-cited cross-link source for the datacenter cluster.
- **Volatile-facts register:**
  - Physics constants (heat capacity ratios, thermodynamic limits): STABLE
  - PUE/WUE benchmark bands, cooling thresholds, capex $/MW, construction timelines: SLOW-DRIFT (re-verify every 6–12 months)
  - Per-chip wattage, GPUs-per-rack, current-generation specs: VOLATILE (12–18 month churn; isolate in one clearly-dated table)
- **Index category:** [VERIFY against category-map.php — likely AI/Cloud or Infrastructure]
- **Jurisdiction/geographic scope:** Global, with US-market cost figures noted as such
- **Reading conditions:** Desktop bookmark + mobile quick-lookup. Mobile: tables must reflow or scroll horizontally without breaking; print: single-page-friendly condensed layout is a first-class goal (this is a print-and-pin artifact).
- **Cross-link map:** Forward-links to `datacenter-cooling-thresholds.html`, `datacenter-power-chain.html`, `ai-accelerator-comparison.html` (this page is the hub). Reciprocal links from all three when they ship. [VERIFY existing corpus for natural reciprocal candidates — any cloud/Azure/SQL pages.]

## Content approach

- **Quick-reference block (top):** The signature table itself — ~20 rows of "number, unit, meaning, source" in latency-numbers style. The page leads with the artifact.
- **Fundamentals:** What each metric means (PUE, WUE, ERE, rack density, IT load vs facility load) in one tight glossary table.
- **Working knowledge:** Sections expanding each number cluster — power (chip → rack → hall → campus), cooling (thresholds and why), water, cost, time. Each section is 2–4 paragraphs plus a small table.
- **Edge/advanced:** Behind-the-meter generation ratios, interconnect queue times by ISO/RTO, why nameplate ≠ actual draw (40–60% enterprise, 70–90% AI training utilization).
- **Major tables:**
  1. The Numbers (signature): ~20 rows — e.g., W per flagship GPU, kW per AI rack, MW per 10K-GPU cluster, PUE band by cooling type, gallons/day per 100MW, $/MW capex, months permit-to-power.
  2. Metric glossary: ~8 rows (PUE, WUE, ERE, CUE, rack density, IT load, critical load, nameplate).
  3. Scale ladder: ~7 rows (single GPU → server → rack → row → hall → campus → gigawatt cluster) with power, rough cost, and real-world analogy per rung.
- **Common mistakes:** Confusing IT load with facility load; using nameplate ratings; comparing PUE across climate zones; assuming training and inference facilities have the same profile; treating vendor peak specs as sustained draw.

## Research sources

- Primary: Uptime Institute annual survey (PUE benchmarks), IEA data centre energy reports, NVIDIA/AMD official spec sheets (TDP), Lawrence Berkeley National Lab / NREL publications (WUE, cooling), EIA (US power data), hyperscaler engineering blogs (Meta OCP publications, Microsoft, Google) for rack density claims.
- **Must not recall from memory:** every wattage, dollar figure, PUE value, water figure, and timeline. All ~20 signature-table rows require a cited primary source. Sources conflict (air-cooling limit quoted 20–50 kW/rack across vendors) — where ranges conflict, present the range with attribution rather than a false point value.

## Visual design

- **Palette/aesthetic:** Dark terminal aesthetic consistent with latency-numbers homage — monospace numerals, high-contrast single accent color (electric amber or cyan) on near-black. Deliberately austere; the numbers are the design.
- **Signature visual:** The Numbers table itself, styled as a monospace card that screenshots cleanly. Secondary: a log-scale horizontal bar strip showing the power ladder (GPU → campus) — 700W to 1GW spans 6 orders of magnitude, which is the "wow" image.
- **og:image:** 1200x630 screenshot of the top ~10 rows of the signature table with the title.
- **Mobile:** signature table becomes stacked cards (number huge, label small) below 576px. **Print:** one-page condensed table, ink-friendly light theme via print stylesheet.
