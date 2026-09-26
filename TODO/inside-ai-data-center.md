# Inside an AI Data Center (codename: AI Compute, Powers of Ten): implementation spec

**Target:** `inside-ai-data-center.html`
**Status:** specification only; not yet traffic-ranked.
**Purpose:** the site's first scroll-driven three.js page. It is a visual hub for the existing data center cluster and a showcase of what the pipeline can do with 3D. Implementation and deployment are separate work.

**Revision 2026-09-24 (David's review): no large blocks of text. The information content is built into the 3D space.** Every entry, figure, delta, blast radius, and correction is anchored to the physical part it describes, the way an exploded service-manual drawing carries its own callouts. The page does not have a prose column beside a canvas. §4-§8 and §10 below are written to that rule; where an older instinct ("put it in the panel") conflicts with it, the scene wins.

## 1. Editorial contract

The page is a continuous zoom through AI compute. It starts at a 1 GW campus and ends at one HBM memory stack. There are eight stops, each roughly one order of magnitude smaller in linear size than the last. At every stop the reader sees three things at once, **all in the scene**: the physical object, what it contains, and what it costs in watts, liters, dollars, and blast radius.

**Core sentence:** An AI data center is a power and cooling machine that happens to hold GPUs, and every level of it is shaped by moving three things: watts in, heat out, bytes between.

This is a design/showcase project under TODO/README.md Rule 0, the same as `how-do-rainbows-work.html`. It is not a broad informational SEO bet. Judge it by these criteria:
- whether a reader leaves with a correct mental model of scale;
- whether the 3D does work that a 2D diagram cannot;
- whether the reader can learn the page's facts **by looking at the scene, not by reading beside it**;
- whether it routes readers into the six existing data center sheets.

**Division of labour with existing pages.** `ai-datacenter-infrastructure.html` is the layer-by-layer reference, and `ai-infrastructure-numbers.html` holds the numbers. This page is the spatial and scale view. It does not reproduce their spec tables. It shows one headline figure per level and deep-links to the sheet that owns the detail. If a callout starts becoming a paragraph, cut it to a label, a value, and a link (README Rule 4).

**Why 3D earns its place here.** The content is nested physical packaging across six orders of magnitude, and 2D diagrams handle that badly. Each level of this subject is a box inside a box. The reader's misconception is about scale and containment, not about any single fact. Because the facts are properties of specific parts (the busbar carries the kW, the manifold carries the flow, the tray is the failure unit), the natural place for each fact is on its part. The 3D must serve that one job. It must not become a free-roaming toy (see §7).

## 2. Targeting and acceptance outcome

- **Primary query:** inside an AI data center.
- **Secondary queries:** what is inside an AI server rack; GB200 NVL72 rack explained; how big is an AI data center; how many GPUs in a 1 GW data center; how are AI data centers cooled.
- **Intent:** research and curiosity, low stress. Also shared on HN, Reddit, and LinkedIn as a visual. Audience: engineers, investors, journalists, and local residents following `data-center-community-impact.html`.
- **Title (≤60):** `Inside an AI Data Center: 3D Zoom From Campus to Chip`
- **H1:** `Inside an AI data center, from a gigawatt campus to one memory chip`
- **Deck:** `Eight stops, six orders of magnitude. Follow the watt, the liter, and the byte.`
- **Meta description draft (150-200):** `Zoom through an AI data center in 3D: campus, data hall, row, rack, tray, superchip, GPU package and HBM stack, with the power, cooling, cost and failure domain at every level.` Recount the length at build time.
- **Reader outcome:** the reader can do three things.
  - Estimate how many GPUs and racks fit in a campus of a given megawatt rating.
  - Name what physically sits between the utility substation and a GPU die.
  - Explain why a rack, not a server, is now the unit of AI compute.
- **Success metric:**
  - Primary: shares of the signature zoom, measured as referrers in Cloudflare stats, plus click-through from this page into the six cluster sheets.
  - Secondary: organic entries on the primary query in Search Console.
  - Do not add new tracking.
  - Before the build, pull Search Console queries for `ai-datacenter-infrastructure.html` and `ai-infrastructure-numbers.html`. If either already ranks on the primary query, shift this page's primary query to "what is inside an AI server rack" to avoid cannibalization. Record the decision in the production notes.
- **Category:** existing `Engineering & Science` in `category-map.php`.
- **Scope:** worldwide hardware; US grid context only where a figure requires a jurisdiction (utility interconnection is US-framed; say so once, on the substation callout).
- **Reading conditions:**
  - Desktop exploration and HN-driven phone traffic on mid-range Android over cellular.
  - The phone case sets the budgets: the page must be readable and useful before WebGL loads and if it never loads.
  - Classroom or meeting projection is plausible: callouts legible at 1080p from the back of a room.
  - Print is secondary; print the static per-level plates with their keyed callout lists.

## 3. Staleness register

Overall rating: **SLOW-DRIFT geometry, VOLATILE hardware generation.**

| Fact | Rot rate | Re-verification |
|---|---|---|
| Which rack-scale system is the reference build (GB200 NVL72 vs GB300 NVL72 vs Vera Rubin) | ~12 months | NVIDIA product pages and GTC keynotes; OEM shipping announcements |
| Rack power (kW), HBM capacity per GPU, GPU TDP | Per generation | NVIDIA datasheets |
| Rack price, $/MW capex | ~6 months, noisy | Primary reporting only (earnings calls, SEC filings, named-source reporting); omit if unsourced |
| Campus-scale figures (PUE range, GW-class campus count) | ~6 months | Same sources `ai-infrastructure-numbers.html` uses; reuse its verified values and dates |
| Facility geometry (hall and row layout) | Stable | Illustrative; labelled as representative |
| HBM stack height, die count per stack | Per HBM generation | JEDEC standard summaries, SK hynix / Samsung / Micron product pages |

The reference build is a **named constant block** at the top of the page script (§7), so a generation swap is a data edit plus geometry tweaks, not a rewrite. Tag every volatile figure inline with "as of Mon YYYY" (on the callout itself, in the muted ink).

## 4. The eight stops

Every number below is a **plausibility anchor** under README Rule 1. It must be verified or omitted. Levels 0-1 are **representative, labelled illustrative**; do not model or name a real campus. Levels 2-7 are **dimensioned from vendor or standards sources** and recorded in the geometry manifest (§9).

| # | Stop | Linear scale | Contains (anchor) | Headline figure (anchor) | Blast radius: what one failure here takes down | Deep link |
|---|---|---|---|---|---|---|
| 0 | Campus | ~10³ m | Several halls, substation, cooling plant, backup generation | 1 GW facility ≈ 830 MW IT at PUE 1.2 | Grid or substation event: everything; why interconnection is the binding constraint | `datacenter-power-chain.html`, `data-center-community-impact.html` |
| 1 | Data hall | ~10² m | Dozens of rows, CDUs, busway, containment | Tens of MW per hall | Cooling plant or UPS lineup: a hall; training jobs checkpoint and resume elsewhere | `datacenter-cooling-thresholds.html` |
| 2 | Row / pod | ~10¹ m | ~8 compute racks plus network and CDU racks | Scale-out fabric leaves the rack here (InfiniBand or Ethernet) | Row PDU or CDU: one pod | `ai-datacenter-infrastructure.html` |
| 3 | Rack (NVL72-class) | ~10⁰ m | 18 compute trays, 9 NVLink switch trays, power shelves, busbar, manifolds, copper NVLink spine | 72 GPUs in one NVLink domain; ~120-140 kW; ~1.3-1.4 t | NVLink domain: one tray down degrades a 72-GPU job | `ai-accelerator-comparison.html` |
| 4 | Compute tray | ~10⁻¹ m | 2 superchips, cold plates, NICs, DPU | 4 GPUs + 2 CPUs per 1U tray | Tray: 4 GPUs drained, rack keeps running degraded | `ai-accelerator-comparison.html` |
| 5 | Superchip | ~10⁻¹ m | 1 Grace CPU + 2 Blackwell-class GPU packages | CPU-GPU coherent link | Board: 2 GPUs | `ai-accelerator-comparison.html` |
| 6 | GPU package | ~10⁻² m | 2 reticle-sized compute dies + 8 HBM stacks on an interposer | ~208B transistors; ~8 TB/s memory bandwidth; ~1-1.2 kW | Package: 1 GPU; the unit of cloud rental | `semiconductor-manufacturing.html` |
| 7 | HBM stack | ~10⁻³ m | 8-12 DRAM dies bonded with through-silicon vias | Stack height held to a JEDEC limit under a millimetre | ECC and row remapping absorb most faults | `semiconductor-manufacturing.html` |

An eighth "below this" coda points to transistor scale (~10⁻⁸ m) and links `semiconductor-manufacturing.html`. It is not modelled; it is a single callout on the HBM die edge pointing "down".

### Where each kind of information lives in the scene

This table is the core of the revision. Each content type has one physical home and one visual grammar. Nothing below is a text panel.

| Content | In-scene form | Anchored to |
|---|---|---|
| Stop name, power of ten | Title block in the corner of the drawing sheet, like an engineering drawing's title block (≤8 words) | The drawing surface, bottom-right |
| "What you're looking at" | One caption line under the title block, ≤20 words | Same title block |
| Linear scale | A **dimension line** drawn on the object's longest edge ("2.24 m", tick marks, arrowheads), plus the scale bar bottom-left | The enclosing object's bounding edge |
| GPUs, IT power, mass, capex anchor (the old ledger) | A **nameplate**: a small engraved-style plate on the enclosing object, 4 rows, monospace, like the rating plate on real equipment | The enclosing object at this stop (campus gate, hall door, row end panel, rack side, tray faceplate, package substrate edge, HBM base die) |
| Coolant flow | Written **on the pipe** as a flow tag ("~200 L/min · ΔT 10 K") beside supply/return arrows | The manifold or loop segment at this stop |
| Power at this level | Written **on the conductor** ("~130 kW · 48 V busbar") | Busway, busbar, power shelf, VRM field |
| Bandwidth at this level | Written **on the link** ("NVLink · 130 TB/s domain") | Spine, fabric trunk, interposer |
| Ledger delta ("×18 trays = one rack") | A **multiplicity bracket**: one child instance outlined, a bracket spanning all siblings, and "×18" on the bracket | The repeated sibling instances |
| The four atomic entries per stop | **Numbered callouts** with leader lines to the specific part. Collapsed: label + value (≤8 words). Expanded on hover, focus, or tap: definition, value, gotcha (≤45 words) | The part the entry describes; an entry with no physical part is cut or reassigned |
| Blast radius | A **Fail** toggle per stop: the failure unit turns hatched red, every instance it takes down greys out, and a count tag reads the loss ("−4 GPUs · rack runs degraded") | The failure unit and its dependents |
| Illustrative-geometry notice | Muted "ILLUSTRATIVE" stamp in the title block at levels 0-1 and on any illustrative sub-part | Title block / part |
| Deep link | The **nameplate's last row** and the relevant callout's expanded card link out | Nameplate |
| Common Mistakes | **Correction tags** (§5) pinned where the misconception is visibly false | The frame that disproves it |

**Rule for the builder:** if you cannot name the part a fact is anchored to, the fact does not go on this page. Push it to the owning cluster sheet.

### Persistent ledger (the reader's running odometer)

The ledger is no longer a fixed strip of prose values. It is the **nameplate chain**:
- each stop's enclosing object carries its nameplate (GPUs contained, IT power, coolant flow, mass, capex anchor);
- on zoom-in, the parent's nameplate shrinks into a breadcrumb chip at the top edge of the drawing ("CAMPUS 1 GW › HALL ~80 MW › ROW ~1.1 MW › RACK 130 kW"), so the reader always sees the chain of containers they are inside;
- the breadcrumb chips are buttons on the level rail's behalf: clicking one zooms back out.

Coolant flow is **computed, not quoted**, from ṁ = P / (c_p · ΔT) with a stated loop ΔT. The formula appears once, as a small annotation on the rack manifold's flow tag (expand to see the arithmetic for that level), not as a disclosure paragraph.

### Scale referents

A 1.75 m human silhouette appears at levels 0-3, rendered as a flat billboard in the drawing style, with its own dimension line. At levels 4-7 the referent changes: a credit card at the tray and superchip levels, a fingernail at the package, a human hair cross-section at the HBM stack. Each referent carries a one-line dimension tag. Referent dimensions are standard figures; verify them anyway.

## 5. Content contract

AGENTS.md floor applies: 20+ substantive entries, Quick Reference near the top, a comparison table, a Common Mistakes section. **Minimum 32 entries:** four per stop, each following the atomic-entry rule (definition, concrete value, quantified metric, gotcha). The entries are the stop's numbered callouts (§4); the atomic-entry rule is met in the expanded state.

**Word budgets (machine-gated, §10):**

| Element | Max words |
|---|---|
| Title block caption | 20 |
| Collapsed callout | 8 |
| Expanded callout | 45 |
| Correction tag, expanded | 35 |
| Any `<p>` anywhere on the page | 60 |
| Intro above the scene (H1 + deck + one sentence) | 40 total |

A stop's scroll section contains **only** the title block text and its callouts' DOM (§7). There is no per-stop prose panel.

**Quick Reference (above the fold, static HTML):** a six-chip strip, each chip ≤12 words, each a link that zooms to the stop that proves it.
1. 1 GW ≈ ~6,000 NVL72-class racks ≈ ~430k GPUs.
2. A rack is ~130 kW and ~1.4 t.
3. 72 GPUs share one NVLink domain.
4. Most heat leaves through liquid.
5. A GPU is a package, not a chip.
6. The utility interconnect, not GPUs, is the usual bottleneck.

All six are anchors.

**Worked example, built into the campus scene (must reach a final answer):** "How many GPUs fit in a 1 GW campus?" It runs as a **four-step build-up at stop 0**, each step changing the scene and adding one dimension-style equation tag:
1. `1,000 MW ÷ PUE 1.2 = 830 MW IT`: the facility overhead share (cooling plant, losses) tints as its own volume; the IT share is what remains.
2. `830 MW ÷ ~140 kW per rack (incl. network + CDU racks) = ~6,000 racks`: racks instance into the halls until the count is reached.
3. `× 72 = ~430k GPUs`: the GPU count ticks on the campus nameplate.
4. `× rack capex = ~$20B IT capex`: the capex row fills.

Step buttons (Prev / Next) sit on the drawing, and the reduced-motion path jumps straight to each end state. The same four equation lines exist in the DOM as a short `<ol>` (SEO and screen readers): equations only, no connecting prose. Use verified inputs and units at every step. The anchors above are shapes, not values; the final numbers come from verified inputs.

**Optional campus calculator:** two inputs (campus MW, PUE) and a reference-build selector, rendered as input fields **on the campus nameplate itself**. Changing them re-runs the build-up instantly (rack instance count, GPU count, capex, coolant flow). It shares code with the nameplates. **Cut it if the JS budget is tight;** the worked example is mandatory, the calculator is not.

**Generations comparison: the line-up.** At stop 3, a "Line-up" toggle slides the reference rack sideways and places four rack silhouettes side by side at true relative scale on the same floor grid: HGX H100 (four air-cooled 8-GPU servers in a rack), GB200 NVL72, GB300 NVL72, and the next announced rack-scale system (Vera Rubin class; mark "announced" vs "shipping" per verified status at build time). Each rack wears its own nameplate: GPUs per NVLink domain, rack kW, cooling method, HBM per GPU, rack mass, first volume shipments. The NVLink domain is drawn as an outlined volume inside each rack, so the jump from an 8-GPU box to a 72-GPU rack is visible as geometry, and the cooling method shows as air arrows vs liquid manifolds. This is not a 3D bar chart: every mark is the physical object.

The same data is a real `<table>` in the DOM (anti-goal check: the AGENTS.md comparison table), visually hidden in the 3D view but kept in the accessibility tree and linked from the Line-up toggle as "View as table". Exemplar row at final depth: **HGX H100 | 8 | ~40 kW per rack (4 × ~10 kW servers) | air | 80 GB HBM3 | anchor, verify | 2023.** The one-sentence takeaway ("8 to 72 GPUs per domain; air to liquid") is the line-up's title block caption.

**Common Mistakes: correction tags.** Eight tags, each pinned in the frame that disproves it. A tag shows the misconception struck through, with the correction on flip (hover, focus, or tap), ≤35 words. A small counter in the title block ("2 corrections at this stop") makes them findable. The DOM also holds them as one `<ul id="common-mistakes">` in source order (required section), which remains available in the document for assistive technology.

| # | Misconception | Pinned at | What the frame shows |
|---|---|---|---|
| 1 | "An AI data center is a big room of GPUs." | Stop 0 | Cooling plant and substation volumes vs the halls, footprint shares labelled |
| 2 | "1 GW means 1 GW of GPUs." | Stop 0, worked example step 1 | The overhead volume carved out of the 1 GW |
| 3 | "A GPU is a chip." | Stop 6 | Dies and HBM stacks separated on the interposer |
| 4 | "The server is the unit of compute." | Stop 3 | NVLink domain outline spans the whole rack |
| 5 | "Liquid cooling means water on the chips." | Stop 3 or 4 | Facility water stops at the CDU; secondary loop and cold plate drawn with the boundary marked |
| 6 | "PUE measures compute efficiency." | Stop 0 | PUE tag sits on the facility overhead volume, not on the racks |
| 7 | "More GPUs = linear speedup." | Stop 2 | Bandwidth tags drop from the NVLink spine to the scale-out fabric at the rack boundary: the cliff, labelled |
| 8 | "Data centers are mostly AI." | Stop 0 | Tag links `data-center-myths.html` |

**Anti-goals:**
- **No text blocks.** No prose panel beside or below the canvas; no paragraph over 60 words anywhere.
- No vendor logos or wordmarks; product names are used factually.
- No named real campus.
- No financial or investment framing.
- No em dashes in page copy.
- No "Last verified" line.

## 6. Visual identity: exploded technical illustration at night

**Look:** isometric engineering illustration, flat-shaded low-poly, thin ink edges, drawn on a graphite drafting surface. Think exploded-view service manual, not game render: the callouts, dimension lines, nameplates, and title block **are** the text of the page. No PBR materials, no environment maps, no bloom, no glass.

**Palette:**

| Role | Hex |
|---|---|
| Surface, dark | `#12161C` |
| Surface, light mode | `#EEF1F4` |
| Ink | `#D8DEE6` (dark) / `#1B2430` (light) |
| Muted ink | `#8A96A6` |
| Structure (racks, trays, enclosures) | `#3A4452` / `#C9D1DB` |
| Power flow | `#F2A93B` |
| Coolant supply | `#3E9BE0` |
| Coolant return | `#E0574A` |
| Data flow | `#4CC38A` |
| Zoom-target highlight | `#F4F1E8` outline |
| Blast-radius hatch | Coolant-return red at 35% plus 45° hatch pattern |

Flow colours carry meaning and must be paired with line pattern for colour-blind readers:
- power: solid;
- coolant: dashed;
- data: dotted.

Test contrast of every callout, tag, and nameplate combination in both themes, including tags drawn over flow lines. Callouts get a surface-coloured backing pill so contrast never depends on what geometry is behind them.

**Typography:**
- Title block and H1: `system-ui` stack at heavy weight.
- Callouts, nameplates, dimension lines, flow tags: `ui-monospace, SFMono-Regular, Menlo, monospace`.
- No web fonts.

**Recurring grammar (in priority order):**
1. **Box in a box.** The next level down is always shown as a highlighted outline inside the current level before the zoom moves into it. It carries its own collapsed label ("RACK ▸ zoom"), and clicking it zooms. This is the page's single most important visual convention.
2. **Callouts are service-manual callouts.** Numbered circles on the part, leader lines out to label columns in the left and right gutters of the drawing, sorted by anchor height so leader lines never cross.
3. **Numbers live on their carriers.** kW on conductors, L/min on pipes, TB/s on links, counts on multiplicity brackets, totals on nameplates.
4. All text is HTML overlays (CSS2DRenderer), never text baked into textures.
5. The scale bar sits bottom-left at every level; the dimension line on the object repeats it in real units.

### Signature element: "Follow the watt, the liter, the byte"

The zoom itself plus three flow overlays, toggled by native checkboxes: Power, Cooling, Data. Each overlay traces its path continuously across levels **and carries its own quantities as tags along the path**, so the overlay is simultaneously the diagram and the numbers:
- **Power:** substation (MW, voltage) → hall busway → row PDU → rack busbar (kW, V) → power shelf → tray → package VRMs (W per GPU).
- **Cooling:** cooling plant → CDU (where facility water stops; boundary marked with a tag) → rack manifold (L/min, ΔT) → tray cold plate loop → package cold plate. Supply and return are colour-split.
- **Data:** scale-out fabric between rows (per-GPU Gb/s) → NVLink spine in the rack (TB/s) → switch tray → GPU.

When an overlay is on and the reader changes level, the flow line and its tags continue through the zoom without a visual break; the tag at the exit point of one level becomes the tag at the entry point of the next. That continuity is the shareable artifact.

Success test: a reader with the Cooling overlay on can point to where facility water stops and the secondary loop begins, and read the flow rate at that point, without reading anything outside the drawing. Build this first, in monochrome geometry, before any styling (§10).

## 7. Interaction and 3D implementation boundaries

### Camera

- Orthographic, fixed isometric pitch; the camera follows a scripted path between the eight stops.
- **No free orbit by default.** This follows the rainbow spec's reasoning: camera freedom creates occlusion, mislabelled surfaces, and interactions unrelated to the lesson. It also breaks callout layout, which is precomputed per camera state.
- At stops 3 and 4 only, an "Inspect" button enables bounded yaw (±45°) via drag or arrow keys, with a Reset button. Zoom and pan stay locked. During inspect, callouts whose anchor is occluded fade to their number only.
- **Focus framing:** focusing or expanding a callout eases the camera a small bounded amount (≤15% pan, no zoom change) to centre its part, and highlights the part. This is the only camera motion driven by content.

### Navigation

- Three equivalent inputs: normal document scroll, a level rail (eight buttons labelled with the power of ten and stop name), and the breadcrumb chips (zoom out). Keyboard users use the rail.
- The canvas is full-bleed and sticky. Each stop's DOM section (title block text + callout list) is one viewport tall of scroll; IntersectionObserver on each section drives the target level.
- **No scroll hijacking, no scroll-linked scrubbing, no pinning a stop for multiple screens.** One stop = one screen of scroll. Content density lives in the scene, not in scroll length.
- Within a stop, **Tab order = callout order.** Tabbing walks the numbered callouts, expanding each and framing its part; Escape collapses. Then the stop's toggles (Fail, Explode, Inspect, Line-up where present), then the next stop.
- On phones the drawing takes the full viewport under a compact top bar (rail chips + overlay toggles). There is no text column to scroll beneath it.

### Callout layout engine (~150 lines, write by hand)

- Each callout is authored in the DOM (§7 Single source of truth) with `data-anchor="<part id>"`. At init, JS adopts each element into a CSS2DObject attached to the anchor's world position.
- Because the camera is scripted, layout is solved per stop state (assembled, exploded, line-up, inspect-reset): project anchors, assign each callout to the left or right gutter by screen x, sort by screen y, space them at ≥ label height, draw leader lines as SVG or `THREE.Line` in screen space.
- Visible collapsed callouts per stop: ≤8 on desktop, ≤4 at 375 px. The rest collapse to numbered pins that expand on tap. Priority order is authored (`data-priority`).
- Expanded cards open toward the drawing's empty side and never cover their own anchor.
- A callout whose part is not on screen in the current state is hidden, not dangling.

### Explode

At stops 3 and 4, an "Explode" toggle separates components along their install axes. Offsets carry dimension tags where the install axis matters (e.g. tray pitch 1U). Default is assembled at stop 3 and exploded at stop 4. Callout layout re-solves on toggle.

### Fail (blast radius)

Every stop has a "Fail" toggle. On: the stop's failure unit is hatched, dependents grey out, and a loss tag appears on the nameplate ("−72 GPUs in job · 17 trays still serving"). Off restores. Reduced motion: instant state change.

### Motion

- Camera moves tween ≤800 ms.
- Under `prefers-reduced-motion`, cut directly between states with a 150 ms opacity crossfade. No camera travel, no focus-framing pan, no animated flow particles, no instance build-up in the worked example (jump to end state); flows render as static lines.
- Flow animation (moving dashes) is allowed only under `no-preference` and pauses when the canvas is off-screen.

### Scene management

- Only the active stop plus its parent and child proxies exist in the scene.
- Each stop is a builder function that returns a Group from **procedural geometry only**: boxes, cylinders, extrusions, instanced meshes. No GLB models, no textures except an optional 1-channel edge or AO bake. Every part that anchors a callout gets a stable id.
- Repeated parts (racks, trays, HBM stacks, cables) are InstancedMesh. Blast-radius greying uses per-instance colour, not new meshes.
- Dispose geometry and adopted CSS2D objects (returning their DOM elements to their section) on stop exit.

### Single source of truth

- **Numbers:** one `REFERENCE_BUILD` constant block holds every dimension, count, and figure, each with a `src` key pointing into the geometry manifest. Geometry, nameplates, flow tags, dimension lines, calculator, and Quick Reference read from it.
- **Words:** every callout, correction tag, and title block line is authored exactly once in the page's static HTML. The 3D layer adopts those elements; it never generates its own copy. Numbers inside static HTML are wrapped in `<data value="…" data-key="rack.kW">` so the assertion script (§10) can prove the static text matches `REFERENCE_BUILD`.

### Library

- Use three.js via import map at the **same pinned version as `machine-consensus.html` (0.185.1, jsdelivr)**. Do not introduce a third version; the skeleton page is on 0.164.1 via unpkg.
- Add the import map `integrity` field so the AGENTS.md SRI invariant holds in supporting browsers. Record browser support in the production notes.
- Use only core `three` plus `CSS2DRenderer` for callouts. No OrbitControls (write the bounded yaw by hand, ~40 lines), no postprocessing.
- Migrating the skeleton page to the shared version is out of scope; open a GitHub issue for it.

### Load strategy

- The 3D canvas is the primary visual; JavaScript and WebGL are required.
- Dynamically import three.js when the scene container nears the viewport or on first rail interaction.
- Render on demand: re-render only on camera, state, callout expand, or resize change, plus the flow animation loop when active and visible. No perpetual `requestAnimationFrame` on an idle scene.
- Cap `devicePixelRatio` at 2 on desktop and 1.5 on coarse-pointer devices.

### Runtime requirement

JavaScript and WebGL are required. The page shows a concise requirement message if the 3D scene cannot start or loses its context. There are no static drawings for the eight stops.

### Accessibility

- The canvas has `role="img"` with an `aria-label` updated per stop, describing what is shown.
- Callouts are native `<button aria-expanded>` elements with the expanded text in the accessibility tree; they are reachable in reading order without WebGL.
- The rail, toggles, breadcrumb chips, and worked-example step buttons are native buttons and checkboxes.
- The stop title and nameplate summary are announced via a polite live region on change, once, not on every frame.
- Flow meaning is never colour-only.
- At 200% browser zoom, callouts reflow into fewer visible labels (pins for the rest) rather than overlapping.

## 8. Responsive, print, and budgets

**At 375 px:**
- Full-viewport drawing under a compact top bar (rail chips, overlay toggles).
- Title block shrinks to stop name + caption; nameplate collapses to three rows (GPUs, kW, scale) with a tap to expand the rest.
- ≤4 collapsed callouts visible; the rest are numbered pins. An expanded card opens as a small anchored card, ≤45 words, never a bottom sheet of prose.
- All callout text ≥14 px rendered.
- Test stops 3 and 4 exploded, the line-up, and the worked example build-up at 375 px specifically.

**Social preview:** `scripts/render_inside_ai_dc_social.py` captures `images/inside-ai-data-center.png` at 1200×630 from the live 3D rack scene. It is a sharing preview, not page content.

**Print:** The interactive scene requires a browser with JavaScript and WebGL; no static print plate is provided.

**Budgets (planning targets; measured values go in the production notes; repo CWV gates are binding):**

| Budget | Target |
|---|---|
| Initial transfer before three.js import | ≤400 KB compressed |
| three.js module + page JS | ≤250 KB compressed combined |
| Page's own JS (incl. callout layout engine) | ≤70 KB uncompressed |
| Triangles on screen at any stop | ≤150k (line-up: four racks, instanced) |
| Draw calls | ≤120 |
| CSS2D elements live at once | ≤40 (callouts + tags + nameplate) |
| Frame rate during a transition | 60 fps on a mid-range 2023 Android; profile on a real device or throttled Chrome DevTools |
| Callout layout solve per state | ≤4 ms on the same profile |

## 9. Research and geometry provenance

Every dimension and count used to build geometry goes in a **geometry manifest** in `docs/inside-ai-data-center-production.md`:
- part (with its scene id, since callouts anchor to it);
- dimension or count;
- units;
- source URL;
- access date;
- "measured / vendor-stated / illustrative" tier.

Illustrative items (all of levels 0-1, cable routing, internal tray layout where vendors publish only renders) carry the ILLUSTRATIVE stamp in the scene (§4). The production notes also record:
- the cannibalization decision (§2);
- the reference-build choice and the date it was made;
- measured payload, fps, and callout layout solve time;
- import-map integrity browser support;
- the social preview render command.

| Claims needing verification | Source direction |
|---|---|
| Reference rack composition, power, mass, NVLink domain bandwidth, cooling split | NVIDIA product pages and datasheets for the chosen system; OCP / MGX rack specifications; OEM (Supermicro, Dell, HPE) spec sheets for physical dimensions |
| GPU package: dies, transistor count, HBM stacks and capacity, bandwidth, TDP | NVIDIA architecture whitepaper for the chosen generation |
| HBM stack height limit, die count, TSV structure | JEDEC HBM3E / HBM4 standard summaries; SK hynix, Samsung, Micron product pages |
| PUE ranges, campus-scale MW, GW-class campus context | Reuse the verified values and dates on `ai-infrastructure-numbers.html`; re-verify if older than 90 days |
| Rack and GPU capex | Earnings calls, SEC filings, named-source reporting; omit if not primary-sourced |
| Coolant ΔT and flow per rack | Vendor CDU and cooling-plant documentation; compute flow from verified kW and ΔT, never quote an unsourced flow number |
| Line-up racks (H100 HGX rack, GB300, next-gen) dimensions and mass | Same vendor and OEM sources; any rack without published dimensions is drawn from the NVL72 envelope and stamped ILLUSTRATIVE |
| Scale referent dimensions | Standard references (ISO/IEC 7810 ID-1 card; human hair diameter range) |

## 10. Build sequence and quality gates

1. **Plan (README Rule 2).**
   - Full outline to three depths.
   - **The callout map:** for each stop, the part list with scene ids, and for each of its four entries the anchor part, collapsed text, and expanded text. One fully populated exemplar callout at final depth. Any entry without an anchor part is cut here.
   - The correction-tag placement table (§5) confirmed against the frames.
   - The generations line-up row list plus exemplar.
   - The verification list mapped to sources.
   - The Search Console cannibalization check.
   - Choose and date the reference build.
2. **Verify numbers and fill `REFERENCE_BUILD` plus the manifest before any geometry.**
3. **Spike: stops 3 and 4 only, monochrome, with the Cooling overlay, its flow tags, the nameplate, and four live callouts through the layout engine.**
   - Measure triangles, draw calls, fps, and layout solve time on a throttled mobile profile; check callouts at 375 px.
   - **If this fails the budget or callouts cannot be laid out legibly at 375 px, stop and report** rather than simplifying silently (in particular, do not fall back to a text panel). That is a scope decision for David.
4. **Build all eight stops monochrome with the box-in-box highlight grammar, dimension lines, and the scripted camera.**
   - The zoom must explain containment with no colour and no callouts.
   - Capture desktop and 375 px screenshots.
5. **Add all three flow overlays with their tags and continuity across stop boundaries**, then the palette, nameplates and breadcrumb chain, callouts, multiplicity brackets, Fail, Explode, Inspect, and Line-up.
6. **Write the words into the DOM:** title block lines, callouts, correction tags, Quick Reference chips, worked example equations, line-up table. Then the worked-example build-up in the campus scene. Optionally the calculator.
7. **Render the social image; show a requirement message when WebGL fails.**
8. **QA** (checks below).
   - Integrate `category-map.php`, catalog, and footer cross-links per `SEO_PROMPT.txt`.
   - Add reciprocal links from `ai-datacenter-infrastructure.html` and `ai-infrastructure-numbers.html` (one natural sentence each).
   - Open the three.js version-consolidation issue.
9. **Commit implementation, social preview, script, and production notes.** Delete this spec when the page meets acceptance. Deploy only with David's go-ahead.

**Machine gates (scripts, not review prompts):**
- `scripts/check_inside_ai_dc.py` (or a Node twin) asserts:
  - every `<data data-key>` value in the HTML equals the matching `REFERENCE_BUILD` value;
  - counts multiply consistently down the zoom (trays × GPUs per tray = rack GPUs; racks × GPUs = campus GPUs within the worked example's rounding);
  - every flow tag's L/min equals ṁ = P/(c_p·ΔT) for its displayed inputs;
  - every callout has a `data-anchor` that exists in the part-id list exported from the builders;
  - word budgets (§5): no `<p>` over 60 words, collapsed callouts ≤8, expanded ≤45, correction tags ≤35, title captions ≤20.
- Wire it into the pre-push hook alongside the existing checks.

**Correctness checks:**
- Every rendered dimension traces to a manifest row.
- No calculator endpoint produces NaN, a negative value, or an overflowing nameplate row.

**Visual checks:**
- Desktop and 375 px at every stop, dark and light themes, 200% zoom.
- No crossing leader lines, no callout covering its own anchor, no dangling callout for an off-screen part, in every state (assembled, exploded, line-up, Fail, inspect at ±45°).
- Keyboard-only traversal: rail, callouts in order with focus framing, toggles, breadcrumb chips, worked-example steps.
- Reduced motion; WebGL disabled (Chrome flag); forced context loss; short viewport.
- No flow line or flow tag terminating mid-level, no z-fighting on exploded parts, no giant empty scroll regions.

**Comprehension checks (editorial review prompts; do not claim user-testing results):**
- Looking only at the stop 3 drawing, an everyday reader can say how many GPUs are in a rack and why liquid cooling is necessary.
- With overlays on, an engineer can trace the cooling loop boundary and the NVLink domain boundary and read the quantity at each.
- A reader of `data-center-community-impact.html` can estimate the GPU count behind a local "300 MW" announcement by stepping through the worked example.

**Showcase acceptance:**
- The flow-overlay zoom, with its tags, is the most polished artifact on the page.
- A reader can get every fact on the page from the scene without scrolling to a text block, because there isn't one.
- The page requires JavaScript and WebGL for its interactive drawings.
- The 3D demonstrably carries the containment and scale argument that a flat diagram would not.

**Failure modes that reject the build:**
- A text column or panel of prose beside, over, or under the canvas.
- A rotating hero model followed by a text essay.
- A free-orbit sandbox.
- 3D bar charts.
- Any number that appears only inside the canvas (every number is a DOM element, even when positioned in 3D).
- Callouts that collide, cross, or float detached from their parts.
