# Inside an AI Data Center: Blender model redesign (spec)

**Target:** `inside-ai-data-center.html`, its eight 3D views and the rack line-up.
**Status:** specification only (2026-11-14). Nothing built. Deploy needs David's go-ahead.
**Goal:** replace the eight box-primitive scenes with models authored in Blender so each view is more detailed, more realistic, easier to read, and teaches more.
**Builder:** an Opus or Sonnet sub-agent, one card at a time (§11). This spec is the contract.

Related documents:

| Document | Role after this spec |
|---|---|
| `TODO/inside-ai-data-center.md` | Original page spec. Still binding for content: §1 editorial contract, §3 staleness, §5 word budgets and anti-goals, §9 provenance. Superseded by this spec: §6 "flat-shaded low-poly, no PBR", §7 "procedural geometry only, no GLB models", §7 "no free orbit" (the page already ships orbit and zoom), §8 triangle and draw-call budgets. |
| `docs/inside-ai-data-center-production.md` | Geometry and numerical manifest. Every new dimension goes here with source, date and tier. |
| `scripts/check_inside_ai_dc.py`, `scripts/qa_inside_ai_dc.py`, `scripts/render_inside_ai_dc_social.py` | Existing gates and captures. Extended in §10, not replaced. |
| `~/Projects/concordia-racer-dock/docs/16_visual_architecture.md`, `scripts/assets/blender/*_lib.py`, `scripts/assets/process.ps1` | Working example of code-authored Blender kits exported to meshopt GLB. Copy the patterns, not the files. |

Numbers in this spec are plausibility anchors under `TODO/README.md` Rule 1. Verify each against a primary source before it shapes geometry or copy; an unverifiable dimension is drawn as illustrative and stamped so.

## 1. Current state

The scenes are built at runtime by eight builder functions (`campus`, `hall`, `row`, `rack`, `tray`, `superchip`, `gpu`, `hbm`) plus eight `DRESS` functions, all in the page's inline module. Geometry is `BoxGeometry`, `CylinderGeometry`, `TubeGeometry` and `InstancedMesh`, with `MeshStandardMaterial` colours, canvas-generated face textures, a hemisphere light and one shadow light.

| Problem | Where it shows |
|---|---|
| Parts are unrecognisable without their label. A cold plate, a power shelf, a CDU and a UPS are all tinted boxes. | Every stop |
| Each stop uses its own arbitrary unit scale and the page says "Schematic, not to scale". The scale lesson, the page's core claim, rests on text. | Stage label, stop stamps |
| The child object inside a parent is a different shape from the hero of the next stop (a rack is a plain box in the row, a banded cabinet at the rack stop). Containment is asserted, not shown. | Stops 0 to 6 transitions |
| The three spines that make a rack one computer (busbar, manifolds, NVLink cable cartridges) are thin bars at the back with no mating detail. Blind-mating, the reason a tray is a service unit, is invisible. | Stops 3, 4 |
| Package and memory internals have no cross-section. The layers that explain "a GPU is a package" and "HBM is a stack" sit on top of each other as slabs. | Stops 6, 7 |
| Flow paths are straight tubes that do not follow physical routes (overhead busway to tap box to whip to shelf; header to CDU to manifold to quick disconnect to plate). | All flow overlays |
| Geometry lives as coordinates in minified JS. Nobody can review or extend it, and it is not tied to the manifest dimensions. | `inside-ai-data-center.html` lines ~150 to 235 |

What already works and must survive unchanged: the eight-stop rail, breadcrumbs, numbered callouts adopted from static HTML, nameplate, flow toggles, Simulate fault, Separate trays / Lift cold plates, Compare racks and its table, the worked example at stop 0, orbit and zoom with Reset, render-on-demand, theme toggle, WebGL-failure message, `REFERENCE_BUILD`, and every existing part id (§6.2).

## 2. Decisions

| # | Decision | Reason |
|---|---|---|
| D1 | **Models are code-authored in Blender** (headless `bpy` scripts, Blender 4.5 LTS at `C:\Program Files\Blender Foundation\Blender 4.5\blender.exe`). No hand-modelled `.blend` is a source of truth. | Reviewable diffs, dimensions read from one JSON, regenerable when the reference generation changes, and agents can build and validate without a GUI. |
| D2 | **Models ship as meshopt-compressed GLB files in `models/inside-ai-data-center/`,** loaded on demand by the existing page. The page stays one hand-authored `.html`; it does not become an `apps/<slug>/` app. | `docs/apps.md` is for bundled projects whose entry HTML is generated. Here the words, numbers and gates live in the hand-edited sheet. Precedent for a sheet with a binary model: `human-skeleton.html` + `human_skeleton.glb`. This is a recorded exception to the "single self-contained file" invariant, limited to model binaries. |
| D3 | **Look: a physical cutaway teaching model,** the kind a museum or a vendor training lab would build. Neutral, believable materials on everything; the four flow colours stay reserved for power, coolant supply, coolant return and data. | "More realistic" must not cost legibility. Realism goes into shape, proportion and material; meaning stays in the colour code and the labels. |
| D4 | **Every stop is authored at true scale in metres** from the manifest. Where true scale would be unreadable (HBM stack height, TSV diameter), the exaggeration factor is a named constant, exported in the GLB and printed on the drawing. | Replaces "not to scale" with a real scale bar and makes the scale claim visible. |
| D5 | **One shared part library, two levels of detail.** The rack that appears eight times in the row is the low-detail export of the same Blender builder that makes the rack hero. Same for tray, superchip, GPU package, HBM stack. | Containment becomes literal: what you click in the parent is what you arrive inside. |
| D6 | **No Draco, no KTX2.** Meshopt only; colour comes from named materials and vertex-colour ambient occlusion. At most one shared WebP detail atlas (§5.4). | Both decoders fetch WASM at runtime outside the import-map SRI; `meshopt_decoder.module.js` is a single ES module that the import map can pin. Verify that claim against three 0.185.1 before relying on it. |
| D7 | **Migration is per stop behind a flag.** `?models=procedural` keeps the old builder for that stop until its GLB passes acceptance, then the builder and its `DRESS` function are deleted. No permanent dual path. | Before/after captures need both; long-term there is one geometry source. |
| D8 | **Phase A changes models only.** The 32 callouts, eight correction tags, nameplate values and all copy stay as they are. New callouts for newly visible parts are Phase B (§8) and go through the content rules. | Keeps the model work reviewable by eye and keeps fact verification out of the modelling cards. |

Open for David (§13): confirm D3 against the original "ink illustration" identity, confirm the D2 exception, choose whether the hero stays GB200, and approve Phase B.

## 3. Modelling principles

These are the rules a builder applies when the per-stop tables in §4 leave a choice open.

1. **One lesson per stop.** Each stop names a single thing the reader should be able to say after looking at it with labels hidden (§4). Geometry that does not serve the lesson or the recognisability of a named part is context and gets the low-detail treatment.
2. **Three detail tiers.**
   - *Teaching parts:* have a part id, a callout or a flow role. Modelled to be recognised unlabelled: correct silhouette, mating features, fasteners only where they explain service (a tray's ejector handles, a quick disconnect collar).
   - *Context parts:* frame, floor, walls, neighbours. Correct proportion, bevelled edges, no small features.
   - *Surface detail:* vents, port rows, fins, bump arrays. Instanced geometry or the shared atlas, never unique triangles per instance.
3. **Cut, do not ghost.** Show interiors with section cuts (a wall removed, a quarter cut out of a mould cap) and with the existing Separate / Lift states. A cut face gets the `section` material (flat, hatched in the atlas) so the reader can tell a cut from a real surface. Transparent shells are limited to the NVLink domain volume and the campus facility-overhead volume.
4. **Carriers look like carriers.** A busbar is a copper bar with a clip, a coolant line is a hose or pipe with a collar at each connection, a data link is a cable bundle or a routed trace. A reader should identify which of the three flows a part carries with the overlay colours off, from shape alone; the colour then confirms it.
5. **Physical routes.** Every flow path runs where the real carrier runs and ends on a mating feature of the next level. No path ends in mid-air or passes through a solid.
6. **Scale referents are objects, not billboards.** The 1.75 m person (stops 0 to 3), an ID-1 card (stops 4, 5; 85.60 × 53.98 × 0.76 mm, ISO/IEC 7810), a fingertip (stop 6) and a hair cross-section (stop 7) are modelled at true size in the neutral `referent` material and stand next to the part they measure.
7. **Honest geometry.** Vendor-published counts and dimensions are exact. Everything else (internal tray layout, board component placement, rack rear mechanics) is drawn plausibly from public photographs and stamped illustrative per part (§6.3). Do not reproduce a vendor's industrial design, bezel styling, logo or wordmark; no text is modelled or textured anywhere. Rating plates are blank plates.
8. **Nothing implies a named real campus.** Stops 0 to 2 stay a representative layout.

## 4. Per-stop model specification

Existing part ids are in `code`; they keep their names. "New named parts" get ids for selection outlines and Phase B callouts. Budgets are in §9.

### Stop 0: Campus (1 km example)

**Lesson:** most of the site is power and heat-rejection equipment; the halls are the smaller part.

| Part | Model |
|---|---|
| `substation` | Fenced yard: two transmission towers with conductors entering, dead-end gantry, breakers, three or four main transformers with radiator banks and bushings, control house. |
| `campus-hall` ×4 | Long single-storey halls with parapet, loading dock, rooftop or side-yard heat-rejection units. **One hall has a roof section cut away** showing rows of rack proxies, so the next stop is visible inside this one. |
| `backup-generation` | Generator yard per hall: rows of containerised gensets with exhaust stacks and belly fuel tanks, step-up transformers. |
| `cooling-plant` | Chiller or dry-cooler yard with fan arrays, pump house, supply and return headers on a pipe bridge to each hall. |
| New: `mv-yard`, `water-tank`, `network-building`, `gate` | Medium-voltage switchgear and transformer pads along each hall; a storage tank; a small fibre building with duct bank to the halls; security gate with cars and a truck as secondary referents. |
| `facility-overhead`, `rack-instances` | Kept as runtime objects for the worked example. The GLB provides the rack placement grid as instance transforms inside the halls. |
| Site | Ring road, lawn (keep the existing procedural lawn and clouds; they are runtime effects, not model work), pads, fencing. |

Flows: power from the transmission line through the substation, underground duct bank to each hall's MV yard. Cooling headers on the pipe bridge. Data from the network building.

### Stop 1: Data hall (100 m example)

**Lesson:** three distribution systems cross the hall to every row: power overhead, liquid in pipes, air in the aisles.

| Part | Model |
|---|---|
| Shell | Two walls and the roof removed with section faces; columns and roof trusses kept on the remaining sides; slab floor. |
| `hall-rows` | Paired rows as hot-aisle containment pods (end doors, roof panels) built from rack proxies. |
| `hall-busway` | Overhead busway runs with tap-off boxes above each row. |
| `hall-cdu` | Row-end coolant distribution units on facility supply and return headers; the header-to-CDU connection is the visible facility-water boundary. |
| `hall-ups` | Electrical room behind a partition: UPS cabinets, battery cabinets, switchgear lineup. |
| New: `fan-wall`, `fiber-tray`, `hall-headers` | Air handlers for the air-cooled share; overhead fibre runner; the facility water headers as their own part. |
| Referent | Person at a row end. |

### Stop 2: Row / pod (10 m example)

**Lesson:** the rack is where the fast in-rack network ends; a pod is compute racks plus the network, power and cooling racks that serve them.

| Part | Model |
|---|---|
| `row-racks` ×8 | Rack low-detail export: frame, tray banding, front ports, rear spines visible from the hot aisle. |
| `row-fabric` | Network rack with switch chassis and fibre trunks rising to the overhead tray, one bundle dropping to each compute rack. |
| `row-pdu`, `row-power` | Busway segment, one tap-off box and whip per rack, landing on that rack's power shelves. |
| `row-cdu`, `row-cool` | In-row CDU with a door cut away: plate heat exchanger, pump pair, facility side and secondary side piping in different pipe finishes; secondary manifold along the row with a hose pair to each rack. |
| `row-data` | The fibre path in the overhead tray. |
| New: `containment` | Hot-aisle door and roof panel, cut on the near side. |

### Stop 3: Rack (GB200 NVL72 contents in an ORv3 proxy envelope)

**Lesson:** the rack is one 72-GPU computer because every tray blind-mates into three shared spines at the rear: busbar, liquid manifolds, NVLink cable cartridges.

| Part | Model |
|---|---|
| `rack` | Frame with posts, top and base, casters and levelling feet; near side panel removed. Envelope from the manifest (0.706 × 2.054 × 1.219 m proxy). |
| Power shelves ×8 | Each with six PSU module faces and a rear busbar clip (anchor: 33 kW shelf, 6 × 5.5 kW; verify). |
| `compute-tray` ×18 | Tray low-detail export: front face with ejector handles, drive bays, network cages; rear with busbar clip, two liquid quick disconnects, NVLink connector blocks. |
| `switch-tray` ×9 | Distinct front face and rear connector field so the reader can tell switch from compute by shape. |
| `busbar` | Vertical copper bar pair with a moulded shroud, full height. |
| `manifold`, `return` | Vertical supply and return manifolds with one quick-disconnect port per tray position. |
| `nvlink-spine` | Four cable cartridges with dense copper bundles between tray positions (anchor: more than 5,000 cables; verify). |
| `domain` | Existing dashed outline volume. |
| `rack-gpus` | Runtime `InstancedMesh` kept for the per-tray fault state; the GLB supplies four GPU slot transforms per tray. |
| `person` | Modelled referent at true scale. |

States: **Separate trays** becomes two steps. Step 1 slides one compute tray forward on its rails far enough to show the rear connectors leaving the three spines. Step 2 moves the spines rearward as a group. The tray vertical order stays as recorded in the manifest (illustrative).

Line-up (`lineup.glb`): an air-cooled 8-GPU server chassis (fan wall, eight heatsink towers under a cut lid) stacked four high in the same frame, next to the NVL72 rack. GB300 and Vera Rubin reuse the NVL72 model unless a published dimension differs, and carry the illustrative stamp.

### Stop 4: Compute tray (1RU)

**Lesson:** a 1RU tray is mostly cold plate and power delivery, and coolant reaches four GPUs through a sealed loop that starts and ends at two rear quick disconnects.

| Part | Model |
|---|---|
| `tray` | Sheet-metal chassis with rails; lid as a separate liftable part. |
| `superchip-a`, `superchip-b` | Superchip low-detail export. |
| `cold-plate` | Plate assembly per superchip with inlet and outlet barbs; **one plate is cut to show the microchannel fins** over the package. |
| `tray-supply`, `tray-return` | Tubing from the rear quick disconnects through a small distribution manifold to each plate and back, routed around components. |
| `nic` ×4 | Network cages on the front face with their boards. |
| `power-contact` | Rear busbar clip and the power distribution board behind it. |
| New: `quick-disconnect`, `nvlink-connector`, `dpu`, `ssd-bank`, `tray-fans` | Rear liquid couplings; rear NVLink connector blocks; data processing units; drive bank; the small fans for the air-cooled components (anchors: 2 DPUs, 8 drives; verify). |
| Referent | ID-1 card on the bench beside the tray. |

States: **Lift cold plates** keeps its meaning; add the lid as the first step.

### Stop 5: Superchip

**Lesson:** one CPU and two GPU packages share a board, and most of the board area around them is power conversion.

| Part | Model |
|---|---|
| `superchip` | PCB with visible layer edge, mounting posts for the cold plate. |
| `grace-cpu` | Lidded CPU package with its memory modules alongside (anchor: soldered LPDDR5X; verify). |
| `gpu-left`, `gpu-right` | GPU package low-detail export: substrate, stiffener ring, die area. |
| `power-delivery` | Rows of inductors and power stages on both sides of each package, bulk capacitors, the input connector. |
| `c2c-link`, `c2c-link-two` | Routed differential-pair trace bundles on the board surface between CPU and each GPU. |
| `superchip-cool` | The plate footprint outline and coolant direction over the packages. |
| Referent | ID-1 card. |

### Stop 6: GPU package

**Lesson:** "one GPU" is two logic dies and eight memory stacks on an interposer; the package is a layered sandwich.

| Part | Model |
|---|---|
| `substrate` | Organic substrate with a ball grid on the underside and decoupling capacitors on top. |
| `interposer` | Interposer slab under the dies. |
| `compute-die-a`, `compute-die-b` | Two dies inside the reticle limit (26 × 33 mm maximum field, standard figure; die size itself illustrative unless sourced). |
| `hbm-array` ×8 | HBM stack low-detail export, four per long side. |
| `die-link` | The die-to-die interconnect region between the two compute dies. |
| `gpu-power` | Power path from the ball grid up through the substrate. |
| New: `stiffener`, `cold-plate-lifted`, `section` | Stiffener ring; the cold plate lifted clear; **a "Slice" state** that cuts the package on its short axis and shows, top to bottom: cold plate, thermal interface, die, microbumps, interposer, bumps, substrate, solder balls, board. Vertical exaggeration is a named constant shown on the drawing. |
| Referent | Fingertip at true scale. |

### Stop 7: HBM stack

**Lesson:** the memory is eight thinned DRAM dies and a base die joined vertically by through-silicon vias, and the whole stack is about as thick as a bank card.

| Part | Model |
|---|---|
| `base-die` | Base logic die with the bump array to the interposer underneath. |
| `dram-layers` ×8 | Eight core dies with microbump layers between them; count from the manifest (eight-high for the reference build). |
| `tsv` | Via array in the central band of each die, continuous through the stack, visible in a quarter cut. |
| `die-edge` | Kept as the anchor for the transistor-scale coda. |
| New: `mold`, `hair` | Mould compound shell with one quarter cut away; a hair cross-section referent (anchor: ~70 µm; verify). An ID-1 card edge at 0.76 mm stands beside the stack for the thickness comparison (anchor: HBM3E stack height ~0.72 mm per JEDEC; verify). |

Exaggeration: stack height and via diameter are both scaled for visibility. The factors are constants in `reference_build.json`, exported as GLB extras, and the stage label reads them ("height ×N, vias ×M"); the existing callout sentence about enlarged vias stays true.

## 5. Look and materials

### 5.1 Lighting

Keep the hemisphere and shadow light. Add image-based reflections from three's `RoomEnvironment` through `PMREMGenerator` (no HDR download) so metals read as metal. Ambient occlusion is baked per vertex in Blender, not computed at runtime. No post-processing passes.

### 5.2 Material palette

Blender materials are named from a fixed palette; the GLB carries names, base colour and roughness/metalness factors only. At load, the runtime replaces each by name with its theme-aware `MeshStandardMaterial`, so light and dark themes, fault greying and flow toggles keep working through the existing code paths.

| Name | Use |
|---|---|
| `steel-painted`, `steel-bare`, `aluminium`, `sheet-dark` | Enclosures, frames, chassis |
| `copper` | Busbars, cold plate bases, bumps, traces |
| `pcb`, `substrate`, `silicon`, `dram`, `mold` | Electronics |
| `concrete`, `asphalt`, `roof`, `glass` | Site and building |
| `hose`, `pipe-facility`, `pipe-secondary` | Coolant carriers under the flow colours |
| `cable` | Data and power cable jackets under the flow colours |
| `section` | Cut faces |
| `referent` | Person, card, fingertip, hair |
| `flow-power`, `flow-cool`, `flow-hot`, `flow-data` | Flow overlays; values stay `#F2A93B`, `#3E9BE0`, `#E0574A`, `#4CC38A` |

The Blender validator fails the build on any material outside this list.

### 5.3 Edges

Hard edges get a small bevel (true-scale radius chosen per stop) so highlights define form. The existing ink `outline()` boxes are removed per stop as its model lands; the selection outline stays.

### 5.4 Textures

Default is none. If port rows, vent perforation and section hatching cannot be done within the triangle budget as instanced geometry, one shared greyscale WebP atlas (≤1024 px, ≤150 KB) may be added and referenced by all stops. It contains patterns only, never text or marks.

## 6. Asset pipeline

### 6.1 Layout

```
scripts/inside_ai_dc/
  reference_build.json      # numbers: the page's REFERENCE_BUILD plus model dimensions, each with a manifest key
  build-models.ps1 / .sh    # blender -b -P blender/build.py -- --stop <n|all|lineup>, then post.mjs, then the gates
  post.mjs                  # gltf-transform: weld, instance, quantize, meshopt; writes manifest.json
  blender/
    lib.py                  # scene reset, palette, bevel and AO helpers, naming, export, validate
    parts/                  # one builder per physical object: rack.py, tray.py, superchip.py, gpu_package.py, hbm.py, cdu.py, ...
    stops/                  # s0_campus.py ... s7_hbm.py, lineup.py: compose parts, place flows, anchors, referents
    sheet.py                # renders a contact sheet per stop for review (workbench or EEVEE, fixed cameras)
models/inside-ai-data-center/
  s0-campus.glb ... s7-hbm.glb, lineup.glb
  manifest.json             # per file: bytes, sha256, unique and rendered triangles, draw-call estimate, part ids, anchors, bounds in metres, exaggeration factors, source commit
```

`.blend` files and renders are build outputs under a git-ignored `build/inside_ai_dc/`. The GLBs and `manifest.json` are committed (the site has no asset build step). `scripts/build_site.py` publishes every git-tracked file that `is_public()` accepts, so tracked files under `models/` ship without a build change; confirm `models` is not in `INTERNAL_DIRS` and that `scripts/inside_ai_dc/` stays unpublished (`scripts` is internal). Add a long-cache `_headers` rule for `/models/*` only if the GLB filenames carry a content hash; otherwise leave default caching.

`reference_build.json` becomes the single numeric source. The page keeps its inline `REFERENCE_BUILD` (no extra request); `check_inside_ai_dc.py` asserts the inline block equals the JSON's page subset.

### 6.2 Node contract

Each part builder takes `lod` (`hero` or `proxy`) and returns objects named by this contract. The runtime depends on it; the validator enforces it.

| In Blender | Exported as | Runtime use |
|---|---|---|
| Object named with a part id (`compute-tray`, `manifold`, ...) | Node name | `parts[id]` for selection, fault unit, zoom target |
| Empty `anchor:<part id>` parented to the part | Node | Callout pin position; replaces `ANCHOR_MODE` and its hard-coded vectors |
| Custom property `tier` = `vendor` / `derived` / `illustrative` | `extras.tier` | Stamp text and the provenance gate |
| `explode` (vector, metres) and `explodeStep` (int) | `extras` | Separate / Lift states; replaces `userData.explode` literals |
| `down` (bool or group name) | `extras` | Fault state: what greys out with the failure unit |
| `flow` = `power` / `cool` / `hot` / `data` on a tube mesh with U along its length | `extras.flow` | Flow toggles; the U coordinate is there for direction marks |
| `slots` (list of transforms) | `extras` | Runtime instancing that needs per-instance state (`rack-gpus`, `rack-instances`) |
| `next` = true on the child proxy that leads to the next stop | `extras.next` | Zoom target and highlight; replaces the id table in `navigate()` |
| Scene properties `metresPerUnit`, `exaggeration` | Scene `extras` | Scale bar, dimension labels, stage stamp |

All 40-odd ids the page and `check_inside_ai_dc.py` use today must exist in the matching GLB. Repeated context geometry is exported with `EXT_mesh_gpu_instancing`; everything non-selectable is joined per material.

### 6.3 Export and optimisation

- Blender glTF exporter, GLB, +Y up, modifiers applied, custom properties as extras, vertex colours on, GPU instancing on. Confirm the exact operator arguments against the Blender 4.5 manual before writing `lib.py`.
- `post.mjs`: `@gltf-transform/cli` or its API as a dev dependency. Weld, dedupe, quantize, meshopt. Keep the scene graph for named nodes (no flatten of parts).
- Vertex-colour AO: bake with Cycles or compute by ray cast per vertex; either way the result must be deterministic for a fixed seed. If a GPU is used, follow the device order in `~/AGENTS.md` (R9700 first).
- Builds must be reproducible at the manifest level: same inputs give the same part list, triangle counts and bounds. Byte-identical GLBs are not required.

### 6.4 Blender-side validation (`lib.validate`, fails the build)

- Every id required for the stop is present, with an anchor empty.
- Counts equal `reference_build.json`: 18 compute trays, 9 switch trays, 8 power shelves, 4 GPU slots per tray, 2 superchips per tray, 2 compute dies and 8 HBM stacks per package, 8 DRAM dies per stack.
- Bounding dimensions of manifest-backed parts equal the manifest within 0.5%.
- Every part has a `tier`; a part with tier `vendor` has a manifest key.
- No material outside the palette, no image textures except the shared atlas, no text objects.
- Transforms applied, normals consistent, no zero-area faces, no flow tube ending more than a tolerance away from a mating part.
- Unique-triangle and node budgets (§9).

## 7. Runtime integration

Changes to `inside-ai-data-center.html`, kept small:

1. **Import map:** add `GLTFLoader`, its dependencies, `meshopt_decoder.module.js` and `RoomEnvironment` from the same pinned three 0.185.1 jsdelivr paths, each with an `integrity` entry.
2. **Loader:** `loadStop(n)` fetches `models/inside-ai-data-center/s<n>-*.glb`, caches the parsed scene, and prefetches `n±1` when idle. `build(n)` becomes async around it. While a model loads, show the stop's bounding box from `manifest.json` and a status line; on failure, show the existing requirement-style message for that stop.
3. **Adoption pass:** walk the loaded scene once: fill `parts` from node names, read `extras` into `userData`, swap materials by name, create runtime instanced meshes from `slots`, register flow meshes, collect anchors.
4. **Deletions per migrated stop:** its builder, its `DRESS` function, `outline()` calls, canvas face textures, `ANCHOR_MODE` entries, and the hard-coded next-part id.
5. **Scale:** `fit()` keeps framing by bounds. The stage label and `addDimension()` read `metresPerUnit` and real bounds, so each stop shows a true scale bar; "not to scale" copy is removed where it stops being true and replaced by the exaggeration note on stops 6 and 7.
6. **Dispose** geometries of the outgoing stop unless cached; cap the cache at three stops on coarse-pointer devices.
7. **Unchanged:** callout adoption from static HTML, inspector, flow tag text, fault tag text, worked example, line-up table, theme, context-loss handling, `window.__dcMetrics`.

Optional last card: because parent and child now share geometry, the stop transition can dolly into the `next` proxy and cross-fade to the hero at matching screen size. Build it only after all eight stops pass acceptance.

## 8. Phase B: new callouts (separate go-ahead)

Up to two extra callouts per stop for newly modelled parts, each written to the atomic-entry rule and the word budgets in the original spec §5, each with a sourced figure in the production manifest. Candidates: MV yard and network building (0); fan wall and facility headers (1); containment and tap-off whip (2); power shelf and NVLink cartridge (3); quick disconnect and DPU (4); VRM field and CPU memory (5); stiffener and the slice layers (6); mould cap and microbumps (7). Anything unverifiable stays an unlabelled illustrative part.

## 9. Budgets

Planning targets; measured values go in the production notes. Repo Core Web Vitals gates stay binding.

| Budget | Target |
|---|---|
| Unique triangles per stop GLB | ≤80k |
| Rendered triangles per stop (after instancing) | ≤350k desktop |
| Draw calls per stop | ≤150 |
| GLB transfer size per stop | ≤700 KB; stop 0 (first view) ≤500 KB |
| All nine GLBs | ≤5 MB |
| Added JS (loader, adoption pass) minus deleted builders | net ≤ 0 KB uncompressed |
| Time from stop change to model on screen, cached / cold on throttled 4G | ≤150 ms / ≤2.5 s |
| Idle frame cost | zero (render on demand unchanged) |
| Orbit frame rate, mid-range 2023 Android profile | ≥30 fps at every stop |

If a stop cannot meet its lesson inside the budget, cut context detail first, then surface detail, never a teaching part. If it still does not fit, stop and report; do not raise a budget silently.

## 10. Gates and QA

**Machine gates** (wired into `build-models.*` and the existing pre-push check path):

- Blender validation (§6.4) per stop.
- `scripts/check_inside_ai_dc.py` extended: every `data-anchor` and every id in its `part_ids` table exists in that stop's `manifest.json`; inline `REFERENCE_BUILD` equals the JSON; manifest budgets hold; every committed GLB's sha256 matches the manifest; no GLB contains an image other than the atlas.
- `scripts/qa_inside_ai_dc.py` extended (Playwright, per the repo memory on screenshots): every stop at desktop and 375 px, both themes, default / separated / fault / slice states; no console errors; every model request returns 200; `window.__dcMetrics` within budget; every callout pin projects inside the viewport and onto its part's screen bounds.

**Review artifacts** (committed under `docs/` only as a dated contact sheet if David asks; otherwise build output):

- `sheet.py` Blender contact sheet per stop: three fixed views plus each state.
- Before/after sheet per stop from `?models=procedural` against the new model, same camera.

**Comprehension checks** (editorial prompts; do not report them as user testing):

- *Unlabelled part test:* give a vision model a screenshot of each stop with all overlays and pins hidden and ask it to name the parts. Each teaching part should be named correctly or by an equivalent term. Record the transcript in the production notes. Run it on the procedural version first to set the baseline.
- *Lesson test:* with labels on, a reader can state each stop's lesson sentence (§4) from the picture.
- *Carrier test:* with flow colours off, a reader can point to the power, liquid and data carriers at stops 2, 3 and 4.
- *Containment test:* the object clicked in a parent is recognisably the same object as the next stop's hero.

**Rejects the build:**

- A part that is more detailed but less identifiable than the box it replaced.
- Realistic detail on a part with no source and no illustrative stamp.
- Any logo, wordmark, modelled or textured text, or a recognisable copy of a vendor's bezel design.
- A flow path that floats, clips through solids, or ends away from a mating feature.
- A regression in any existing interaction, callout position, word budget gate or the WebGL-failure path.
- A transparent shell used where a section cut would show the same thing.

## 11. Build sequence

Each card ends with its gates green, a contact sheet, and a commit. Push per card; no deploy.

| Card | Work | Stop condition |
|---|---|---|
| 0 | Baseline: capture all stops and states from the current page; run the unlabelled part test; record numbers in the production notes. Move numbers into `reference_build.json` with the equality gate. Confirm D6 (meshopt module, import-map integrity) and the exporter arguments with a one-cube GLB loaded in the page. | If meshopt cannot be loaded under SRI, report options before going on. |
| 1 | `lib.py`, palette, validator, `post.mjs`, `build-models.*`, manifest writer, loader and adoption pass behind `?models=`. | |
| 2 | **Spike: rack (stop 3) and tray (stop 4)** including the tray proxy inside the rack, two-step separate, flows on physical routes, anchors, fault state. Measure against §9 on the mobile profile. | If budgets or 375 px legibility fail, stop and report with numbers. This is the scope decision point for David. |
| 3 | Superchip, GPU package with Slice, HBM stack with exaggeration constants (stops 5 to 7) and their proxies back-filled into stops 4 to 6. | |
| 4 | Row and hall (stops 2, 1) from rack proxies, CDU, busway, containment. | |
| 5 | Campus (stop 0) with the cut-roof hall, worked-example slots, existing lawn and clouds kept. | |
| 6 | Line-up model. Delete all procedural builders and the `?models=` flag. Lighting pass, theme check, true scale bars, copy edits where "schematic" stops being true. | |
| 7 | Full QA matrix, comprehension checks, production notes (manifest rows, measured budgets, sheets), re-render `images/inside-ai-data-center.png` with `scripts/render_inside_ai_dc_social.py`. | |
| 8 (optional) | Continuous zoom transition (§7). | |
| B (separate go-ahead) | Phase B callouts (§8). | |

## 12. Out of scope

- New facts, figures or copy (Phase B only).
- Changing the reference generation. Part builders take counts and dimensions from `reference_build.json` so a later swap is data plus targeted geometry.
- Animation beyond the existing states, clouds and flow marks.
- Photoreal rendering, HDR environments, post-processing, baked lightmaps.
- Converting the page to an `apps/` project or adding a bundler.
- Other sheets' models, and the three.js version consolidation.

## 13. Open decisions for David

1. **Look (D3).** The original spec chose an ink-illustration identity with no PBR; the shipped page already moved toward lit materials. This spec commits to a physical cutaway model. Confirm, or ask for a stylised variant (same models, flat shading and ink edges) to compare at the card 2 spike.
2. **Model files beside the sheet (D2).** Confirms a standing exception to the single-file rule for model binaries under `models/<slug>/`.
3. **Reference build.** The hero stays GB200 NVL72 because it is the system with published composition in the manifest. Vera Rubin NVL72 is listed as shipping from fall 2026 in the page's own table; switching the hero is a content project, not part of this redesign.
4. **Phase B.** Whether to add callouts for the new parts after the models land.
