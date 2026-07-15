# AI Accelerator Comparison: GPUs, TPUs, and Custom Silicon

Target file: `ai-accelerator-comparison.html`

## Why this topic

Highest search volume in the cluster ("H100 vs B200", "MI300X specs", "GPU comparison for AI") but the weakest strategic case as a standalone: fully VOLATILE facts register and a semi-saturated SERP of spec aggregators. It earns its slot as the completion of the cluster — the compute layer under the power and cooling pages — and as a maintenance-honest alternative to aggregators: fewer chips, verified numbers, and the derived columns aggregators don't compute (memory bandwidth per watt, interconnect domain size, rack-level power). **Build decision:** ship last, and only if the first three pages show cluster traction; otherwise fold the table into `ai-infrastructure-numbers.html` and delete this spec.

## Targeting

- **Primary query:** ai accelerator comparison
- **Secondary queries:** h100 vs b200 specs; nvidia vs amd ai gpu comparison; tpu vs gpu for training; mi300x vs h100; gpu memory bandwidth comparison
- **Mode:** Research with purchase/architecture intent
- **Title:** AI Accelerator Comparison: NVIDIA, AMD, Google, AWS Silicon Side by Side
- **H1:** AI Accelerator Comparison Table
- **Meta description:** Current AI accelerators compared: compute, memory capacity and bandwidth, interconnect, TDP, and rack-level power for NVIDIA, AMD, Google TPU, and AWS Trainium — with derived efficiency columns.
- **Reader outcome:** An architect can compare current-generation accelerators on the axes that actually drive cluster design — memory bandwidth, interconnect domain, watts — not just headline FLOPS.
- **Success metric:** ≥400 organic sessions/month within 6 months; if it can't hold top-10 for two secondary queries by month 6, fold into the numbers page.
- **Volatile-facts register:**
  - Comparison axes and why they matter (memory-bound vs compute-bound workloads): STABLE
  - Which chips are "current generation": VOLATILE (12–18 month full churn)
  - Every spec value: VOLATILE — entire main table carries a visible verified-as-of date; this page needs re-verification on every major silicon launch, not a calendar cadence
- **Index category:** [VERIFY against category-map.php]
- **Jurisdiction/geographic scope:** Global; note export-control variants (China-market SKUs) exist without detailing them
- **Reading conditions:** Desktop comparison session dominant; mobile must handle a wide table gracefully. Print: main table on one landscape page.
- **Cross-link map:** To `ai-infrastructure-numbers.html` (power context), `datacenter-cooling-thresholds.html` (what these TDPs force). Inbound from both. [VERIFY existing corpus.]

## Content approach

- **Quick-reference block (top):** The main comparison table, immediately.
- **Fundamentals:** Why FLOPS marketing misleads — precision games (FP8 vs FP16 vs sparsity-inflated numbers), memory-bound reality of inference, why interconnect domain size matters more than single-chip specs for training.
- **Working knowledge:** Per-vendor section (NVIDIA, AMD, Google TPU, AWS) — architecture philosophy, software ecosystem maturity (CUDA moat vs ROCm vs JAX/XLA), availability/access model (buy vs cloud-only).
- **Edge/advanced:** Derived metrics table (bandwidth per watt, HBM capacity per dollar where pricing is public); scale-up vs scale-out boundary per platform (NVLink domain vs pod vs UltraCluster); how spec sheets differ from sustained real-world utilization (MFU ranges).
- **Major tables:**
  1. Main comparison (signature): ~8 rows (current flagship + prior gen per vendor) × (compute by precision, HBM capacity, bandwidth, interconnect, TDP, form factor, access model). Every cell sourced; sparsity-inflated figures footnoted.
  2. Derived efficiency: ~8 rows (bandwidth/W, memory/W, chips per rack, kW per rack as-deployed).
  3. Ecosystem: ~4 rows (vendor × software stack × framework support × lock-in profile).
- **Common mistakes:** Comparing sparse to dense FLOPS; comparing across precisions; ignoring memory bandwidth for inference workloads; treating TDP as constant real draw; assuming spec-sheet FLOPS translate to model FLOPS (MFU is 30–60%, not 100%).

## Research sources

- Primary: vendor spec sheets only for specs (NVIDIA, AMD, Google Cloud, AWS official pages) — never third-party aggregators as source of record; MLPerf results for any performance claims; vendor architecture whitepapers for interconnect domains.
- **Must not recall from memory:** every spec value, every precision figure, every TDP, current product naming and availability status. Model knowledge of chip specs is presumptively stale; verify all of it.

## Visual design

- **Palette/aesthetic:** Silicon-die aesthetic — dark base with vendor-coded accent chips (muted, not logo-derived) and a subtle die-shot texture in the header only.
- **Signature visual:** The main comparison table with a toggle to re-sort by any column and a highlight mode that colors the winning cell per row — the interactive sort is the differentiator over static aggregator tables.
- **og:image:** 1200x630 of the main table, flagship rows.
- **Mobile:** column-picker pattern — user selects 2 chips to compare side by side below 768px. **Print:** full table landscape, one page, footnotes below.
