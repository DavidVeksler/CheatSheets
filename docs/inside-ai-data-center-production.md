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

Each stop has four numbered callouts anchored to these parts, a nameplate, flow tags, a failure state, and a child outline leading to the next stop. Campus, hall, and row dimensions are example extents; the rack height uses the ORv3 proxy. The tray and smaller views are not to scale. The correction tags follow the eight placements in the specification. The generation line-up rows are four DGX H100 servers, GB200 NVL72, GB300 NVL72, and Vera Rubin NVL72. GB200 is the fully populated reference row; omit a field on other rows where a primary source does not publish it.

### Geometry and numerical manifest

| Part ID / figure | Value | Tier | Primary source, accessed 2026-09-24 |
|---|---:|---|---|
| `campus` envelope / facility power | 1,000 MW and a representative 1 km envelope | illustrative | Scenario, not a real campus. PUE 1.2 is an explicit scenario assumption. |
| `hall` and `row` envelopes | 100 m hall, 10 m row, eight compute racks per row | illustrative | Representative drawing, not an operator plan. |
| `rack` system | 72 GPUs, 36 Grace CPUs, 18 1RU compute trays, nine 1RU switch trays, eight power shelves, two management TOR switches | vendor-stated | [NVIDIA hardware guide](https://docs.nvidia.com/dgx/dgxgb200-user-guide/hardware.html) |
| `rack` power | approximately 120 kW | vendor-stated | [NVIDIA hardware guide](https://docs.nvidia.com/dgx/dgxgb200-user-guide/hardware.html) |
| `rack` mass and cooling split | approximately 2,900 lb, 85% liquid / 15% air | vendor-stated | [NVIDIA partition guide](https://docs.nvidia.com/multi-node-nvlink-systems/partition-guide-v1-2.pdf) |
| `rack` outer drawing envelope | 0.706 m wide, 2.054 m high, 1.219 m deep | illustrative proxy | [OCP ORv3 base rack](https://www.opencompute.org/documents/google-implementation-orv3-spec-1-pdf). GB200-specific outer dimensions not implied. |
| `tray` contents | two superchips, four Blackwell GPUs, two Grace CPUs, four 400 Gb/s ConnectX-7 NICs | vendor-stated | [NVIDIA SuperPOD components](https://docs.nvidia.com/dgx-superpod/reference-architecture-scalable-infrastructure-gb200/latest/dgx-superpod-components.html) |
| `rack` tray order | four power shelves, 10 compute trays, 9 switch trays, 8 compute trays, four power shelves | illustrative | NVIDIA's hardware guide gives counts, not this exact vertical order. Drawn at schematic pitch. |
| `rack` HBM | 13.4 TB HBM3E per rack, 372 GB per superchip (186 GB per GPU) | vendor-stated | [NVIDIA GB200 NVL72](https://www.nvidia.com/en-us/data-center/gb200-nvl72/), accessed 2026-09-24. Line-up row corrected from 180 GB. |
| `person` scale referent | 1.75 m, drawn at the 2.054 m ORv3 proxy scale | illustrative | Standard adult height referent. |
| `superchip` contents | two Blackwell GPUs, one Grace CPU, 900 GB/s NVLink-C2C | vendor-stated | [NVIDIA tuning guide](https://docs.nvidia.com/multi-node-nvlink-systems/multi-node-tuning-guide/overview.html) |
| `gpu` contents | two compute dies, 208 billion transistors | vendor-stated | [NVIDIA Blackwell architecture](https://www.nvidia.com/en-us/data-center/technologies/blackwell-architecture/) |
| `nvlink-spine` domain bandwidth | 130 TB/s for NVL72 | vendor-stated | [NVIDIA Blackwell architecture](https://www.nvidia.com/en-us/data-center/technologies/blackwell-architecture/) |
| `hbm` stack and GPU bandwidth | eight HBM stacks per Blackwell GPU; up to 8 TB/s per GPU | vendor-stated | [NVIDIA Blackwell Ultra technical article](https://developer.nvidia.com/blog/?p=104887). GB200 capacity differs; do not transfer Blackwell Ultra capacity into GB200. |
| `manifold` calculated flow | about 146 L/min for 102 kW liquid at assumed 10 K delta | derived | `102 kJ/s ÷ (4.186 kJ/kg/K × 10 K) × 60 s/min`, water density approximated 1 kg/L. The 10 K is an illustration, not a vendor setting. |
| `power shelf` | eight shelves per rack, each six 5.5 kW PSUs, 33 kW input per shelf, N+N; 50 to 51 V DC output to the bus bar | vendor-stated | [NVIDIA hardware guide](https://docs.nvidia.com/dgx/dgxgb200-user-guide/hardware.html), accessed 2026-11-14 |
| `tray storage and DPUs` | per compute tray: two BlueField-3 DPUs, four 3.84 TB E1.S NVMe data drives, one 1.92 TB M.2 boot drive | vendor-stated | [NVIDIA hardware guide](https://docs.nvidia.com/dgx/dgxgb200-user-guide/hardware.html), accessed 2026-11-14. The Blender spec's "8 drives" anchor was wrong; four E1.S drives are modelled. |
| `rack rear spines` | rear carries the power bus bar, liquid manifolds running the rack height, and a passive copper NVLink cable-cartridge backplane | vendor-stated (existence); geometry illustrative | [NVIDIA hardware guide](https://docs.nvidia.com/dgx/dgxgb200-user-guide/hardware.html), accessed 2026-11-14. No cable count, cartridge count or quick-disconnect count is published there; the model draws four cartridges and one supply plus one return quick disconnect per tray, stamped illustrative. The spec anchor "more than 5,000 cables" is not used. |
| `rack unit` | 1RU = 44.45 mm (1.75 in) | derived | EIA-310 rack unit, standard figure. Compute trays and switch trays are 1RU per the NVIDIA hardware guide. |
| `rack frame layout` | 0.12 m base (casters, levelling feet, base frame); two management TOR switches drawn at the top; 37RU of equipment from the top of the base frame | illustrative | No GB200 rack drawing is used. TOR position is not published. |
| `compute tray envelope` | 0.56 m wide, 43.2 mm high, 0.86 m deep; internal layout (board placement, plate shapes, tube routes, fan count) | illustrative | Proportioned from public photographs, no vendor drawing. 43.2 mm leaves a 1.25 mm gap in each 44.45 mm slot. |
| `ID-1 card referent` | 85.60 × 53.98 × 0.76 mm | derived | ISO/IEC 7810 ID-1 format, standard figure. |
| `hbm stack height` | eight DRAM dies per stack in the reference build | illustrative, unverified | Spec anchor only. Verify against a primary source before stop 7 geometry (card 3). |

No rack price or campus capex is shown: no primary source supplies a defensible figure, so the nameplate has no capex row and the worked example ends at the GPU count (three steps). Re-add both only with a primary source.

## Measurement and QA

Layout QA: `python scripts/qa_inside_ai_dc.py [out_dir]` screenshots every stop plus explode, line-up, and fail at 1280x800 and 375x812, and fails on any desktop overlay overlap, page error, or page wider than the viewport. Social preview: `python scripts/render_inside_ai_dc_social.py`.

Measured 2026-09-25 (headless Chromium, SwiftShader, desktop): 44 to 98 draw calls per state (rack 98, line-up 69), at most 3,900 triangles. These are diagnostic frame samples, not a device frame-rate claim. Frame rate on a real mid-range Android is not yet measured.

Visual model: rack panels use generated vent, port, and PSU textures; hall cabinets, rack rails, rear manifolds, tray cold plates, board packages, and HBM layers have distinct geometry. Their appearance follows NVIDIA's [rack hardware guide](https://docs.nvidia.com/dgx/dgxgb200-user-guide/hardware.html) and [SuperPOD component guide](https://docs.nvidia.com/dgx-superpod/reference-architecture-scalable-infrastructure-gb200/latest/dgx-superpod-components.html), but dimensions, exact placement, and colors remain schematic.

Fail shows the blast radius per stop: the failure unit is red, only its dependents grey out (for example one tray and its 4 GPUs at the rack; the served rows at the hall), and the loss tag sits on the unit.

At 375 px, part callouts collapse to tappable numbered pins. Expanded text opens in place. The QA script reports intentional pin/button overlap without failing; red correction and failure tags can still cross a pin in some states.

## Blender model redesign (docs/specs/inside-ai-data-center-blender-models.md)

Numeric source: `scripts/inside_ai_dc/reference_build.json`. `check_inside_ai_dc.py` fails if the page's inline `REFERENCE_BUILD` differs from its `page` block, or if `rackOrder` disagrees with `counts`.

### Card 0 baseline (2026-11-14, procedural builders)

`python scripts/qa_inside_ai_dc.py build/inside_ai_dc/baseline` (headless Chromium, SwiftShader). Draw calls include the shadow pass. The 2026-09-25 figures above (98 draw calls at the rack) no longer match the shipped page.

| State | Draw calls | Triangles |
|---|---:|---:|
| 0 campus | 233 | 19,606 |
| 1 hall | 386 | 9,350 |
| 2 row | 228 | 17,966 |
| 3 rack (default, separated, fault) | 354 | 10,168 |
| 3 line-up | 307 | 8,682 |
| 4 tray (default, plates lifted) | 180 | 4,700 |
| 4 tray fault | 316 | 6,552 |
| 5 superchip | 134 | 2,978 |
| 6 GPU package | 184 | 10,754 |
| 7 HBM | 163 | 5,154 |

The baseline QA run already exits 1: desktop overlaps at stop 0 (zoom button over the worked example) and the line-up (three flow tags overlap each other). Both predate this work.

Unlabelled part test, baseline (overlays and pins hidden, `scripts/inside_ai_dc/unlabelled.py`, judged by the builder agent looking at the captures, not user testing):

- Stop 3. Named correctly: server rack, person, stacked 1U equipment. Not nameable: compute tray versus switch tray (a darker band in the middle reads as different, not as switches), power shelves, busbar (an orange stripe), manifolds (blue and red stripes read as "pipes or cables", not as supply and return manifolds), NVLink spine (not visible), NVLink domain (dashed line with no meaning). At 375 px the rack reads as a rack; no internal part is identifiable.
- Stop 4. Named correctly: a flat server tray, add-in cards (the green NIC boards, as "cards"), pipes. Partly: the striped plates read as heat sinks because pipes run to them, but they float; the dark slabs with blue blocks read as "chips on a board", not as two superchips each with one CPU and two GPUs. Not nameable: power contact, rear connectors, the sealed loop (the pipes end in mid-air).

Loading path proof: a one-cube GLB exported by Blender 4.5.10 (`export_scene.gltf` with `export_format='GLB', export_apply=True, export_extras=True, export_yup=True, export_vertex_color='ACTIVE', export_all_vertex_colors=False, export_image_format='NONE', export_gpu_instances=True`; options confirmed by listing the operator's RNA properties in 4.5.10), compressed by gltf-transform 4.5.1 (weld, quantize, meshopt), loaded in the page through `GLTFLoader` with `meshopt_decoder.module.js`. Node extras, scene extras (`metresPerUnit`), the `anchor:` child empty and the material name all arrive. The meshopt decoder carries its WASM inline, so no request leaves the import map; replacing its integrity hash with a wrong value blocks the import. GLTFLoader strips `:` from node names, so the runtime reads `userData.name`. The import map now also pins `three.core.js`, which `three.module.js` imports and which had no integrity entry.

### Cards 1 and 2: pipeline and the rack and tray spike (2026-11-15)

Build: `scripts/inside_ai_dc/build-models.sh [3|4|all]` (PowerShell twin `build-models.ps1`): Blender 4.5 composes and validates each stop (`blender/build.py`, `lib.validate`), exports a raw GLB to `build/inside_ai_dc/raw/`, `post.mjs` welds, instances (locally, under the same parent), quantizes and meshopt-compresses into `models/inside-ai-data-center/` and writes `manifest.json`, then `check_inside_ai_dc.py` runs. The page loads `s3-rack.glb` and `s4-tray.glb`; `?models=procedural` keeps the old builders.

Measured with `scripts/inside_ai_dc/measure.py` (headless Chromium, SwiftShader software WebGL; mobile = 375 px, 4x CPU throttle, 150 ms RTT, 1.6 Mbit/s). Draw calls and triangles are `renderer.info` and include the shadow pass. Frame rates under SwiftShader are CPU-bound and only compare old against new; no real device was measured.

| Stop 3 rack | Procedural | GLB |
|---|---:|---:|
| Unique triangles (GLB) | n/a | 18,600 |
| Triangles per frame, GLB alone / renderer incl. shadow | 10,168 | 33,148 / 37,086 |
| Draw calls per frame | 354 | 52 |
| GLB bytes (raw / gzip -9) | 0 | 238,968 / 37,685 |
| Stop change to model on screen, cold, mobile profile | 177 ms | 2,145 ms |
| Same, model in memory, mobile / desktop | 46 ms | 72 / 18 ms |
| Orbit fps, mobile profile, environment map on / off | 31 / 34 | 11 / 25 |

| Stop 4 tray | Procedural | GLB |
|---|---:|---:|
| Unique triangles (GLB) | n/a | 9,180 |
| Triangles per frame, GLB alone / renderer incl. shadow | 4,700 | 9,796 / 17,362 |
| Draw calls per frame | 180 | 103 |
| GLB bytes (raw / gzip -9) | 0 | 148,112 / 39,884 |
| Stop change to model on screen, cold, mobile profile | 348 ms | 1,806 ms |
| Same, model in memory, mobile / desktop | 30 ms | 54 / 100 ms |
| Orbit fps, mobile profile, environment map on / off | 51 / 56 | 16 / 50 |

Budget status (spec section 9): triangles, draw calls, bytes and the cold (2.5 s) and cached (150 ms) load targets pass. Orbit at 30 fps on the mobile profile fails at both stops with the `RoomEnvironment` reflections on; with them off, stop 4 passes and stop 3 reaches 25 fps. The procedural rack was itself near the line (31 to 34 fps) in this profile. Not decided here: drop the environment map on coarse-pointer devices, or measure on a real mid-range Android before deciding.

Unlabelled part test on the GLB stops (same method as the baseline):

- Stop 3. Named correctly: server rack with casters and an open frame, person, stacked 1U trays; the compute trays (drive and port blocks on the face) now read differently from the switch band (plain perforated faces) and from the power shelves (six light module faces each). Still not nameable from the default camera: the bus bar, manifolds and NVLink cartridges sit at the rear and show only as coloured edges; rotated to the rear they read as two pipes, a copper bar pair and four cable cartridges.
- Stop 4. Named correctly: server tray, two motherboards, a fan row, front drive carriers and network cards, cold plates lifted off the chips, the cut plate's fins, hoses running from two rear couplings through a small block to the plates, cables to rear connector blocks, a card beside the tray. Not nameable: the power distribution board and bus bar clip read as "some board and a copper block".

Deviations and limits recorded for this spike:

- The Separate trays and Lift cold plates buttons cycle through the model's steps (0, 1, 2, back to 0). Stop 4: 0 lid on, 1 lid lifted, 2 lid removed and plates lifted (the default). The lid is hidden at step 2 rather than set aside, so the interior stays in frame.
- On the GLB stops a flow toggle swaps the carrier between its flow colour and its neutral material instead of hiding it, so the carriers stay readable with colours off (spec carrier test). The return manifold and return hoses carry `flow: hot` and follow the Cooling toggle.
- Vertex-colour ambient occlusion is per object (self-occlusion only), because instances share one mesh.
- Palette materials are not theme-dependent; neither were the procedural materials.
- The stop 4 camera sits higher (about 44 degrees) so the true-scale 43 mm tray stays legible at 375 px. Its stamp reads "Drawn to scale"; its scale bar is 10 cm. The intro sentence "Views are not to scale" is unchanged and is now only true for stops 0 to 2 and 5 to 7.
- Superchip boards in the tray are a low-detail proxy (card 3 builds them). The rack's tray proxy shares the tray's front and rear geometry, but its interior is an empty pan with the runtime GPU blocks.
