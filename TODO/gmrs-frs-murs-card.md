# Spec: GMRS, FRS & MURS — the channel and rules card

**Target file:** `gmrs-frs-murs-card.html`
**Batch:** [niche-utility-batch-2026-08.md](niche-utility-batch-2026-08.md) (sheet 1 of 10).

## Why this topic

The Radio category is this site's proven shape. `ham-radio-technician.html` converts at
**8.05% CTR**, `baofeng-uv5r-quick-ref.html` at **3.87%** on 1,860 impressions, and
"baofeng uv-5r programming cheat sheet" alone is 760 impressions per 90 days at position 6.5.
Those pages win because someone is holding the radio while reading them.

GMRS/FRS is the same person one step earlier: the blister-pack pair from the camping aisle, or
the Baofeng they just discovered transmits on channels they may not be licensed for. The
existing corpus never covers the unlicensed services at all — a reader who lands on the Baofeng
pages gets programming steps with no answer to "which of these channels am I allowed to use, at
what power, with what antenna?"

The market is full of charts and short of *rulings*. Manufacturer PDFs list 22 channels and
stop. What nobody publishes in one place: the channel table **plus** the FCC rule that governs
each row (power ceiling, bandwidth, antenna restriction, repeater eligibility), **plus** the
crosswalk that makes a programmable radio legal — because the single most common real question
is "I have a UV-5R and a GMRS licence, what may I actually put in memory?" The honest answer
involves Part 95 certification and is genuinely awkward; saying it plainly is the moat.

## Targeting

- **Primary query:** `gmrs frequencies chart`
- **Secondary:** `frs vs gmrs`, `gmrs channels and frequencies`, `murs frequencies`,
  `gmrs repeater channels`, `gmrs power limits by channel`, `do i need a license for gmrs`
- **Mode:** **crisis-adjacent operational** — the reader is standing in a parking lot, at a
  trailhead, or at the kitchen table before a trip, with the radio in hand. Question-shaped H2s
  matching real queries ("Which channels can I use without a license?", "How far will these
  actually reach?").

## Draft title / H1 / meta

- `<title>`: `GMRS, FRS & MURS Channel Chart: Frequencies and Rules` (53 chars)
- **H1:** `GMRS, FRS & MURS: The Channel and Rules Card`
- **Meta description (draft):**
  `Every FRS, GMRS and MURS channel with its frequency, power ceiling, bandwidth and license rule, plus repeater pairs, CTCSS and DCS tones, and realistic range by terrain.` (167 chars)

## Reader outcome

The reader can pick a channel for a specific task — a hiking group, a convoy, a neighborhood
net, a job site — and state, without looking anything else up, the frequency, the legal power
ceiling on that channel, whether a licence is required, whether their antenna is allowed, and
roughly how far it will carry in their terrain.

## Success metric

Organic entries on the primary query family, plus **print and return-direct traffic** — this is
a card people laminate. Watch the ratio of direct/returning hits on this URL against
`baofeng-uv5r-quick-ref.html`, which is the site's benchmark for the same behaviour.

## Content approach

1. **Quick Reference: the one-screen verdict** (top of page) — five rows: *No licence, 0.5 W,
   fixed antenna* → FRS 8–14; *No licence, 2 W* → FRS 1–7 / 15–22; *$35 licence, up to 50 W,
   repeaters* → GMRS; *No licence, VHF, 2 W* → MURS; *Licence + exam* → amateur, link out to
   `ham-radio-technician.html`. Each row ends with "use this when…".
2. **The master channel table** (signature element) — one row per channel, ~46 rows: channel
   number, frequency (MHz), service(s) sharing it, FRS power ceiling, GMRS power ceiling,
   authorized bandwidth, repeater input if any, and a plain-language "what it's for" column
   (interstitial channels, the de-facto calling channels, the channels bubble-pack radios label
   as "privacy"). Anchor-linked rows so a specific channel is a shareable URL.
3. **The rule column explained** — short, per-service: licence scope (GMRS licences cover the
   whole family, no exam, ten-year term — verify), antenna restrictions on FRS, why channels
   8–14 are capped so low, MURS bandwidth and antenna-height rules, and the prohibited uses
   every service shares.
4. **CTCSS / DCS: the "privacy code" lie** — the standard tone table (~38 CTCSS, ~100+ DCS)
   plus the correction that matters: tones are squelch, not privacy or channel separation;
   two groups on the same channel with different tones still collide.
5. **Repeaters** — the eight GMRS repeater pairs, the +5 MHz offset convention, how to find and
   ask permission to use a local machine, and what "open" vs "closed" means in practice.
6. **The programmable-radio crosswalk** (the hard-honesty section) — what Part 95 certification
   means, why most Part 90 handhelds are not certified for FRS/GMRS, what that does and does not
   change for an individual operator, and how the enforcement reality actually looks. State the
   rule, then state what is disputed, and cite the FCC text for both. No winking.
7. **Realistic range** — a table of expected distance by pairing and terrain: handheld to
   handheld in open ground, in suburbs, in forest, in a building, with a repeater. Include the
   antenna-height math in one line and kill the "35-mile range" packaging claim with it.
8. **Programming crosswalk to the site's radios** — the memory-channel values for a UV-5R style
   radio in a table the reader can type from, linking to `baofeng-uv5r-quick-ref.html` for the
   keypad sequence rather than repeating it.
9. **Common mistakes** (mandatory): assuming "privacy codes" mean privacy; buying a repeater-
   capable radio and never programming the offset; keying up on channel 20 during an actual
   emergency instead of the local calling channel; using a high-gain antenna on FRS; assuming
   the family licence covers a business; expecting simplex range from marketing numbers.
10. **Related sheets** footer per the cross-link map.

## Volatile-facts register

**Overall: SLOW-DRIFT.** The channel plan itself is stable for decades; the rules around it move
occasionally:
- FCC Part 95 subpart B (GMRS) / subpart E (FRS) / subpart J (MURS) — re-verify power ceilings,
  bandwidths and antenna rules against the current CFR text each pass, not against a blog.
- GMRS licence fee and term (anchor: $35, ten years) — fee changes have happened; verify.
- Any FCC action on Part 90 handhelds being marketed for FRS/GMRS — this is the live area.
Date the licence-fee line and the certification section inline. Annual freshness rotation is
enough.

## Index category

`Radio`.

## Reading conditions

Phone, outdoors, one hand, possibly gloves, sometimes cold and in a hurry; and a second mode —
laptop at the kitchen table the night before a trip, programming radios. Consequences: the
channel table must be readable at 375 px without horizontal panning of the *first three columns*
(freeze the channel/frequency/power columns visually; the rest scroll in an
`overflow-x: auto` wrapper), tap targets sized for gloves, and a **print stylesheet is
mandatory** — this page's best outcome is a laminated card in a go-bag, so the print layout must
put the master table plus the tone table on one sheet, front and back.

## Cross-link map

- **Internal outbound:** `baofeng-uv5r-quick-ref.html` and `baofeng-uv5r-ham-guide.html`
  (programming), `ham-radio-technician.html` (the licensed next step),
  `emergency-radio-card.html` (the panic-moment card), `prepper-gear-audit.html` and
  `vehicle-emergency-kit.html` (why a radio is in the kit at all).
- **Reciprocal inbound:** add a one-line "unlicensed options" link from
  `baofeng-uv5r-quick-ref.html`, `emergency-radio-card.html` and `prepper-gear-audit.html`.
- **External outbound:** FCC rule pages only. No retailer links, no affiliate framing.

## og:image / shareable artifact

The master channel table, dark theme, cropped to the FRS/GMRS shared rows so the power-ceiling
columns are legible at card size. Same artifact as the "screenshot this" block.

## Jurisdiction scope

**US (FCC) only, stated once at the top.** Add a single short table mapping the nearest
equivalents elsewhere — Canada (GMRS/FRS harmonization), UK/EU PMR446, Australia UHF CB — with
one line each and no channel detail, so an international reader knows in ten seconds that this
page is not for them and where to look.

## Density targets

Master channel table ~46 rows × 8 columns; CTCSS tone table ~38 rows; DCS list ~100 codes
(compact grid); repeater pairs 8 rows; range table ≥ 12 pairings; comparison of services 5 rows;
common mistakes ≥ 6. Comfortably past the floor.

## Research sources (verify against these, per Rule 1)

47 CFR Part 95 (subparts B, E, J) via eCFR; FCC GMRS/FRS/MURS licensing pages; FCC Universal
Licensing System for fee and term; the ARRL band plan for the amateur boundary; manufacturer
manuals only for tone-table conventions, never for rules. Every power, bandwidth and antenna
figure comes from the CFR text — not from a chart site, and not from this spec.

## Visual design

**Identity: FCC field card / radio faceplate.** Not the CRT-terminal look already used elsewhere
in the corpus — this is a printed government reference card: warm off-white stock in light mode,
deep charcoal with an amber channel-readout accent in dark mode, one condensed tabular-figures
face for every number. The master table is styled as a faceplate readout: channel number in a
boxed numeral, frequency in tabular mono, and the power ceiling as a small filled bar (0.5 W /
2 W / 5 W / 50 W) so the reader sees the ceiling before reading it. Licence-required rows carry
a thin left rule in a single accent colour; no red/green traffic lights, since "requires a
licence" is not a warning. Build the master table first and best. Zero JavaScript required; the
only interactive element is a CSS-only row highlight.

**Palette and type tokens — binding.** Field-card mode: stock `#EFE7D3`, ink `#1B2A34`, rule
`#82929A`, FCC blue `#356B78`, receiver amber `#C87928`. Night-radio mode: chassis `#11171B`,
recess `#192228`, warm legend `#F1E6CF`, LCD amber `#FFB347`, dial teal `#63B3B1`. Use a condensed
system sans for labels, a seven-segment-like system-monospace treatment for channel/frequency
readouts, and tabular numerals everywhere. Amber means active/readout, not danger.

**Composition contract — every section should resemble a different part of a radio kit.** Borrow
the recent pages' clarity of shared axes, inline SVG and semantic labels, but do not reuse their
dark dotted shell, status pills or generic table-plus-card cadence:

1. **Radio-face masthead:** a compact front-panel silhouette with the title engraved into the
   chassis and one useful LCD example showing service, channel, frequency and legal power. The
   scope line `US · FCC PART 95` reads like a faceplate legend, not a badge.
2. **Five-position service selector:** the quick-reference verdict is a large labelled rotary or
   stepped selector — FRS low power, FRS shared, GMRS, MURS, Amateur — with `USE THIS WHEN…` copy
   attached to each stop. A plain adjacent list carries the same content for accessibility.
3. **Channel faceplate table:** keep the dense master table, but vary row anatomy with boxed
   channel numerals, frequency readouts, proportional power bars and a thin repeater-pair rail.
   The first three fields form one fixed visual cluster while secondary rules scroll.
4. **Spectrum ruler:** show FRS/GMRS/MURS allocations on a full-width frequency ruler, including
   shared and interstitial regions. Labels and hatching carry service identity; colour alone does
   not. This is a spectrum diagram, not another table.
5. **Repeater duplex rails:** render the eight GMRS pairs as parallel receive/transmit tracks with
   the +5 MHz bridge drawn between them. On phones, each pair becomes a short two-line ladder.
6. **Tone codebook:** CTCSS is a ruled frequency ledger and DCS is a perforated compact code grid,
   separated by a large `SQUELCH, NOT PRIVACY` correction strip. Do not make 138 tiny cards.
7. **Terrain range profiles:** four labelled side-elevation silhouettes — open ground, forest,
   suburb and repeater — place radios and obstructions on a horizon line with range anchors. Pair
   with the numeric table; never imply a precise guarantee from the drawing.
8. **Programming worksheet:** the UV-5R crosswalk looks like a writable memory-bank sheet with
   numbered slots and an annotated keypad path, giving the bottom of the page a lighter paper
   texture than the chassis sections.

**Page rhythm and anti-patterns.** Sequence faceplate → selector → dense channel table → open
spectrum diagram → compact rules → duplex rails → codebook → terrain profiles → worksheet. Avoid
generic rounded cards, traffic-light verdict chips, signal-wave wallpaper, faux knobs that imply
clickability and a repeated three-column grid. The 1200×630 preview should combine the LCD identity
with a legible crop of the shared FRS/GMRS channel rows and their power bars.
