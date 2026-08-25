# Spec: Meshtastic field config — the settings that actually matter

**Target file:** `meshtastic-field-config.html`
**Batch:** [niche-utility-batch-2026-08.md](niche-utility-batch-2026-08.md) (sheet 2 of 10).

## Why this topic

Meshtastic is the fastest-growing thing in the hobby-radio adjacency and its documentation is a
wiki: correct, exhaustive, and organized by software subsystem rather than by the decision a
person is making with a node in their hand. The gap is not knowledge, it is **shape**. Someone
setting up two nodes needs six decisions in a fixed order — region, modem preset, channel and
key, role, hop limit, power — and every one of them has a range-versus-throughput-versus-battery
consequence that the docs describe in separate pages.

This is the purest form of the site's device-programming shape: a reader with hardware in front
of them, a phone in the other hand, and a specific settings screen open. The Radio cluster
already proves that shape converts here (`ham-radio-technician.html` 8.05% CTR,
`baofeng-uv5r-quick-ref.html` 3.87%).

Honest framing on targeting: unlike most of this batch, there is **no GSC evidence** for it — the
site has never surfaced on a Meshtastic query because it has no Meshtastic content. It is a
cluster bet, judged on its own launch baseline. Say so in the log rather than implying measured
demand.

## Targeting

- **Primary query:** `meshtastic settings`
- **Secondary:** `meshtastic modem preset comparison`, `meshtastic range`, `meshtastic channel
  setup`, `meshtastic hop limit`, `meshtastic router vs client role`, `meshtastic battery life`
- **Mode:** operational, hardware-in-hand. The reader is inside the app's settings screen right
  now; every section must name the setting exactly as the app labels it, not as the docs
  describe it conceptually.

## Draft title / H1 / meta

- `<title>`: `Meshtastic Setup Card: Regions, Presets and Channels` (52 chars)
- **H1:** `Meshtastic Field Config: The Settings That Matter`
- **Meta description (draft):**
  `Set up a Meshtastic node in the field: region and frequency slot, modem preset range-versus-speed tradeoffs, channel keys, node roles, hop limit, GPS and battery settings.` (169 chars)

## Reader outcome

The reader can configure a node from factory state to a working mesh in a known order, and can
say — for their own deployment — which preset they chose, what it cost them in throughput, how
many hops their traffic will survive, and how long the battery will last as configured.

## Success metric

Organic entries on the settings/preset query family and **return-direct traffic** (this is a page
people reopen every time they add a node). Secondary: AI-answer citation, since preset tradeoff
tables are exactly what assistants get vague about.

## Content approach

1. **Quick Reference: the six decisions, in order** (signature element) — a numbered decision
   strip: Region → Modem preset → Channel + PSK → Role → Hop limit → Power/GPS. Each box shows
   the default, the common mistake, and where the setting lives in the app. This is the artifact
   people screenshot.
2. **Region and frequency** — the region table (US, EU_868, EU_433, ANZ, JP, IN, and the rest)
   with the frequency range, the legal basis in one clause, duty-cycle limits where they apply,
   and the number of usable slots. Include the specific failure mode: mismatched region means two
   nodes on the same table never see each other and nothing reports an error.
3. **Modem presets: the tradeoff table** — one row per preset (LongFast, LongSlow/LongModerate,
   MediumFast, MediumSlow, ShortFast, ShortTurbo, and whatever the current firmware ships):
   spreading factor, bandwidth, coding rate, on-air data rate, approximate airtime for a standard
   text packet, relative range, and the practical channel-capacity ceiling (how many nodes before
   the mesh chokes). **Anchor numbers only — verify every one against current firmware.** The
   column that makes this page: "what this costs you", stated in nodes-per-mesh and battery.
4. **Channels, keys and privacy** — primary vs secondary channels, the default public key and
   what it does and does not protect, generating a real PSK, QR/URL sharing, and the distinction
   between channel name (routing) and encryption (privacy). Same correction pattern as the CTCSS
   "privacy code" myth in the GMRS card — link the two.
5. **Roles** — Client, Client Mute, Router, Router Client, Repeater, Tracker, Sensor: what each
   does to rebroadcast behaviour, when choosing Router actively harms a mesh, and the standard
   guidance that most nodes should stay Client. One row per role, with "choose this when".
6. **Hop limit and mesh behaviour** — what a hop costs in airtime, why raising the limit usually
   reduces delivery rather than extending reach, flood-routing basics, and how to read the
   telemetry that tells you which is happening.
7. **Power and battery** — a table of measured-anchor draw by state (transmit, receive, light
   sleep, deep sleep) and resulting runtime for common battery sizes, plus the settings that
   dominate battery life (GPS interval, screen timeout, telemetry interval, Bluetooth). Include
   solar sizing in two lines.
8. **Antennas and physical siting** — SMA versus RP-SMA (the connector that destroys radios),
   never transmit without an antenna, height beats gain, and a short table of realistic range by
   siting: handheld in a valley, handheld with line of sight, rooftop node, hilltop repeater.
9. **Field checklist** — a printable pre-deployment check: firmware version noted, region set,
   preset matched across all nodes, channel URL shared, roles assigned, GPS policy chosen,
   battery topped, node named, and a two-node comms test performed before leaving.
10. **Common mistakes** (mandatory): mismatched presets across nodes; everyone setting Router;
    raising hop limit to "fix" range; keeping the default PSK and assuming privacy; transmitting
    with no antenna; GPS at 30-second intervals killing a solar node; assuming a mesh works
    without a single node with height.
11. **Related sheets** footer per the cross-link map.

## Volatile-facts register

**Overall: VOLATILE — the most volatile page in this batch.** Meshtastic firmware changes preset
names, defaults, and role behaviour between releases.
- Pin a visible **"Verified against firmware x.y.z"** line at the top, not just `Last verified`.
- Preset parameter table, role list, and default settings: re-verify every release cycle.
- Region/frequency legal limits: slow-drift, annual.
- Hardware list (board names, battery draw): drifts as vendors ship new boards.
Put this page on the weekly freshness rotation from day one, with the firmware-version line as
the check target.

## Index category

`Radio`.

## Reading conditions

Two modes, both hands-busy: bench setup at a desk with a laptop and USB cable, and field setup
on a phone with the node in one hand and possibly no cell service — so the page must be useful
**offline once loaded** (no runtime fetches, nothing that fails without network) and legible in
sunlight (high-contrast light theme, not a dark-only design). Print: the six-decision strip plus
the preset tradeoff table on one sheet.

## Cross-link map

- **Internal outbound:** `gmrs-frs-murs-card.html` (the licensed/unlicensed neighbour, shipped in
  the same batch), `baofeng-uv5r-quick-ref.html`, `ham-radio-technician.html`,
  `emergency-radio-card.html`, `prepper-gear-audit.html` (where mesh sits on the probability
  ladder), `personal-cybersecurity.html` (for the key-management section).
- **Reciprocal inbound:** one line from `prepper-gear-audit.html` and `emergency-radio-card.html`.
- **External outbound:** the official Meshtastic docs for anything version-specific; link *to*
  the doc rather than restating a number that will rot.

## og:image / shareable artifact

The six-decision strip, dark theme, rendered as a horizontal flow at 1200×630. It is also the
screenshot-this artifact and the thing that must not look generic.

## Jurisdiction scope

Global by construction (region selection is the first decision), but the legal detail is stated
only for US ISM 915 MHz and EU 868 MHz duty cycle; everything else is named in the region table
with a "verify locally" note. Say once that region legality is the reader's responsibility.

## Density targets

Region table ≥ 10 rows; preset tradeoff table ≥ 6 rows × 8 columns; roles 7 rows; power/battery
table ≥ 8 rows; range-by-siting ≥ 6 rows; field checklist ≥ 9 items; common mistakes ≥ 7.

## Research sources (verify against these, per Rule 1)

Official Meshtastic documentation and firmware release notes (the only authority for preset
parameters, role semantics and defaults); the LoRa modulation math for airtime figures (Semtech
application notes); FCC Part 15 / ETSI EN 300 220 for regional limits; vendor datasheets for
board current draw. Never take a preset parameter from a forum post or from this spec.

## Visual design

**Identity: topographic field notebook.** Muted contour-line background motif baked into the
element background (never a fixed full-viewport layer — AGENTS.md scroll-performance rule), a
survey-orange accent, and a squared engineering-drawing grid behind the decision strip. Light
theme is the primary theme here (sunlight legibility), dark theme is the night-camp variant. The
preset tradeoff table uses a two-ended bar in each row — range one way, throughput the other —
so the tradeoff is visible before it is read. No JavaScript required; at most one CSS-only
detail/summary expansion per preset row.
