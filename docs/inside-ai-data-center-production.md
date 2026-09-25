# Inside an AI Data Center: production notes

## Plan and source decision

Reference build selected 2026-09-24: **NVIDIA DGX GB200 NVL72**. NVIDIA's hardware and SuperPOD guides publish the rack, tray, and link composition. This page uses a documented reference system for the physical zoom, not a claim about a typical 2026 deployment. GB300 and Vera Rubin belong in the comparison line-up with their distinct dates and specifications.

Search Console, 2026-06-24 to 2026-09-21: filtered `inside` queries for `ai-datacenter-infrastructure.html` and `ai-infrastructure-numbers.html` returned zero rows each. Keep `inside an AI data center` as the primary query. This is a narrow query check, not a claim of zero page traffic.

### Outline to three depths

1. Campus: utility boundary, overhead versus IT, halls, cooling plant; 1 GW arithmetic in four steps.
2. Hall: busway, rows, CDUs, containment; representative placement and hall failure unit.
3. Row: rack instances, CDU, scale-out fabric, PDU; NVLink ends at rack boundary.
4. Rack: 18 compute trays, 9 switch trays, power shelves/busbar, supply and return manifolds; explode, fail, inspect, and four-generation line-up.
5. Tray: two superchips, cold plates, NICs, front service boundary; exploded default.
6. Superchip: Grace CPU, two Blackwell packages, coherent CPU-GPU links, substrate.
7. GPU package: two compute dies, eight HBM stacks, interposer, power delivery.
8. HBM: stacked DRAM dies, TSVs, base die, package edge; transistor-scale coda.

Each stop has four numbered callouts anchored to these parts, a nameplate, dimension and scale, flow tags, a failure state, and a child outline leading to the next stop. The correction tags follow the eight placements in the specification. The generation line-up rows are HGX H100, GB200 NVL72, GB300 NVL72, and Vera Rubin NVL72. GB200 is the fully populated reference row; omit a field on other rows where a primary source does not publish it.

### Geometry and numerical manifest

| Part ID / figure | Value | Tier | Primary source, accessed 2026-09-24 |
|---|---:|---|---|
| `campus` envelope / facility power | 1,000 MW and a representative 1 km envelope | illustrative | Scenario, not a real campus. PUE 1.2 is an explicit scenario assumption. |
| `hall` and `row` envelopes | 100 m hall, 10 m row, eight compute racks per row | illustrative | Representative drawing, not an operator plan. |
| `rack` system | 72 GPUs, 36 Grace CPUs, 18 1RU compute trays, nine 1RU switch trays | vendor-stated | [NVIDIA hardware guide](https://docs.nvidia.com/dgx/dgxgb200-user-guide/hardware.html) |
| `rack` power | approximately 120 kW | vendor-stated | [NVIDIA hardware guide](https://docs.nvidia.com/dgx/dgxgb200-user-guide/hardware.html) |
| `rack` mass and cooling split | approximately 2,900 lb, 85% liquid / 15% air | vendor-stated | [NVIDIA partition guide](https://docs.nvidia.com/multi-node-nvlink-systems/partition-guide-v1-2.pdf) |
| `rack` outer drawing envelope | 0.706 m wide, 2.054 m high, 1.219 m deep | illustrative proxy | [OCP ORv3 base rack](https://www.opencompute.org/documents/google-implementation-orv3-spec-1-pdf). GB200-specific outer dimensions not implied. |
| `tray` contents | two superchips, four Blackwell GPUs, two Grace CPUs, four 400 Gb/s ConnectX-7 NICs | vendor-stated | [NVIDIA SuperPOD components](https://docs.nvidia.com/dgx-superpod/reference-architecture-scalable-infrastructure-gb200/latest/dgx-superpod-components.html) |
| `rack` tray order | power shelves, 10 compute trays, 9 switch trays, 8 compute trays, power shelves | illustrative | Commonly published NVL72 layout; NVIDIA's hardware guide gives counts only. Drawn at schematic pitch. |
| `rack` HBM | 13.4 TB HBM3E per rack, 372 GB per superchip (186 GB per GPU) | vendor-stated | [NVIDIA GB200 NVL72](https://www.nvidia.com/en-us/data-center/gb200-nvl72/), accessed 2026-09-24. Line-up row corrected from 180 GB. |
| `person` scale referent | 1.75 m, drawn at the 2.054 m ORv3 proxy scale | illustrative | Standard adult height referent. |
| `superchip` contents | two Blackwell GPUs, one Grace CPU, 900 GB/s NVLink-C2C | vendor-stated | [NVIDIA tuning guide](https://docs.nvidia.com/multi-node-nvlink-systems/multi-node-tuning-guide/overview.html) |
| `gpu` contents | two compute dies, 208 billion transistors | vendor-stated | [NVIDIA Blackwell architecture](https://www.nvidia.com/en-us/data-center/technologies/blackwell-architecture/) |
| `nvlink-spine` domain bandwidth | 130 TB/s for NVL72 | vendor-stated | [NVIDIA Blackwell architecture](https://www.nvidia.com/en-us/data-center/technologies/blackwell-architecture/) |
| `hbm` stack and GPU bandwidth | eight HBM stacks per Blackwell GPU; up to 8 TB/s per GPU | vendor-stated | [NVIDIA Blackwell Ultra technical article](https://developer.nvidia.com/blog/?p=104887). GB200 capacity differs; do not transfer Blackwell Ultra capacity into GB200. |
| `manifold` calculated flow | about 146 L/min for 102 kW liquid at assumed 10 K delta | derived | `102 kJ/s ÷ (4.186 kJ/kg/K × 10 K) × 60 s/min`, water density approximated 1 kg/L. The 10 K is an illustration, not a vendor setting. |

No rack price or campus capex is shown until a primary source supplies a defensible figure. The worked example therefore ends at the GPU count and labels the capex row `not published` rather than inventing a dollar amount.

## Measurement and QA

Layout QA: `python scripts/qa_inside_ai_dc.py [out_dir]` screenshots every stop plus explode, line-up, and fail at 1280x800 and 375x812, and fails on any desktop overlay overlap, page error, or page wider than the viewport. Posters and social image: `python scripts/render_powers_of_ten_posters.py`.

Measured 2026-09-24 (headless Chromium, SwiftShader, desktop): 11 to 74 draw calls per state (line-up 51), at most 4,740 triangles, callout layout solve at most 2.2 ms. Posters 22 to 37 KB WebP each. Frame rate on a real mid-range Android is not yet measured.

Known gap: at 375 px, collapsed callouts sit over the drawing and can cover another pin; the QA script reports these without failing.
