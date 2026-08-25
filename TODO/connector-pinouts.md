# Spec: Connector pinout card — the connectors you actually wire

**Target file:** `connector-pinouts.html`
**Batch:** [niche-utility-batch-2026-08.md](niche-utility-batch-2026-08.md) (sheet 7 of 10).
**Pair:** build back-to-back with [fastener-torque-tap-drill.md](fastener-torque-tap-drill.md);
shared design language, shared reader, shared print discipline.

## Why this topic

Same shape as the fastener card and the same argument: a lookup performed with both hands busy,
where getting it wrong costs a part or a cable. "Which pair goes in position 1 of a T568B jack"
is asked by the same person every time they crimp, and no amount of AI answering removes the need
for the diagram in front of them while they hold the connector.

There is a second, sharper reason this one belongs on *this* site. The dev cluster here ranks
badly for a diagnosed reason — authority, not content (`dev-spoke-content-plan.md`). A pinout card
does not compete on tutorial authority; it competes on **table density and diagram quality**, where
a single well-built page can win against wiki pages and forum screenshots. It is the one
dev-adjacent build in this batch that is not fighting the site's weak spot.

The existing field is fragmented by design: RJ45 charts live on cabling sites, OBD-II pinouts on
car forums, GPIO on the Pi foundation's own docs, XLR on audio blogs. Nobody has a reason to put
them on one page — except a cheatsheet site whose entire premise is that one page beats six tabs.

## Targeting

- **Primary query:** `rj45 pinout`
- **Secondary:** `t568a vs t568b`, `usb c pinout`, `obd2 connector pinout`, `xlr pinout`,
  `raspberry pi gpio pinout`, `db9 serial pinout`, `barrel jack polarity`
- **Mode:** operational lookup, hardware in hand, mid-task. Every section must be reachable by a
  stable anchor because the realistic use is a deep link from a forum answer or a bookmark to one
  connector.

## Draft title / H1 / meta

- `<title>`: `Connector Pinout Card: RJ45, USB-C, OBD-II, XLR, GPIO` (53 chars)
- **H1:** `Pinout Reference: The Connectors You Actually Wire`
- **Meta description (draft):**
  `Pin-by-pin wiring for RJ45 T568A and T568B, USB-C, OBD-II, XLR, DB9 serial, automotive relays, Pi GPIO and barrel jacks, with the polarity mistakes that kill hardware.` (166 chars)

## Reader outcome

With an unfamiliar connector in hand, the reader can identify it, orient it correctly (the pin-1
question, which is where most errors start), wire or verify every pin, and know the one failure
mode that connector is known for — before applying power.

## Success metric

Organic entries across several connector families rather than one head term (the page is a
portfolio of small queries, which is also its defence against any single SERP feature), plus
**anchor-level inbound links** and print/return traffic. Track which anchors get external links;
that tells the next build which connector deserves its own page.

## Content approach

Each connector gets an identical block structure — **diagram, pin table, orientation note, common
failure** — so the page is scannable across sections. Consistency is the design.

1. **Quick Reference: identify the connector** — a visual index of every connector on the page at
   thumbnail size with its name and jump link, so a reader who does not know what they are holding
   can start from the shape. This is the entry point and the signature element.
2. **Ethernet: RJ45** — T568A and T568B pin/pair/colour tables side by side, the straight-through
   versus crossover rule and why auto-MDI-X made it mostly moot, which pins 100BASE-TX actually
   uses versus 1000BASE-T, PoE modes A and B and the pins each energizes, and the shielded/ground
   note. Include the "pick one standard per building" rule and the RJ45-versus-8P8C naming
   correction.
3. **USB** — USB-C receptacle and plug pinout with the CC lines explained (which resistor value
   signals which current), USB-A and micro-B for legacy, the power-delivery levels table, and the
   distinctions that matter when a cable "doesn't work": charge-only cables, USB 2.0-only C
   cables, and Thunderbolt/USB4 marking.
4. **Automotive: OBD-II** — the 16-pin connector with the pins that are constant across all
   vehicles (power, ground, the CAN pair) versus the protocol-dependent pins, a protocol table
   (CAN, ISO 9141-2, J1850 PWM/VPW, KWP2000) with the pins each uses and the model years each was
   common, and the safety note on pin 16 being permanently live.
5. **Audio: XLR, TRS, TS, speakON** — XLR pin 1/2/3 (ground, hot, cold) and the pin-2-hot
   convention, balanced versus unbalanced, TRS as balanced mono versus unbalanced stereo (the
   ambiguity that causes the most confusion), insert cables, and the phantom-power caution.
6. **Serial: DB9 / RS-232, RS-485, TTL UART** — DB9 DTE and DCE pinouts, the null-modem
   crossover, the voltage-level difference between RS-232 and TTL UART that destroys
   microcontrollers, and RS-485 A/B polarity and termination.
7. **Single-board computers: Raspberry Pi GPIO** — the 40-pin header with both numbering schemes
   (physical versus BCM — the single largest source of wiring errors), the power and ground pins,
   the pins with special functions (I2C, SPI, UART, PWM), the pins that are pulled up at boot, and
   the 3.3 V-not-5 V warning with the current limits per pin and in total.
8. **DC power: barrel jacks and automotive** — barrel-jack sizes and the centre-positive
   convention with the note that centre-negative exists and is not marked consistently, ATX
   motherboard and peripheral connector pinouts, automotive relay terminals (30/85/86/87/87a) with
   a wiring example, and blade-fuse ratings by colour.
9. **Orientation: finding pin 1** — a short, high-value section: the conventions across connector
   families (the notch, the arrow, the square pad on a PCB, the tab on a ribbon cable, the moulded
   triangle) and how to verify rather than assume. This is the section that prevents the errors
   the rest of the page documents.
10. **Test-before-power checklist** — continuity, polarity, short-to-ground, and the one-minute
    routine that catches most of the failures listed above.
11. **Common mistakes** (mandatory): mixing T568A and T568B ends without meaning to; splitting a
    twisted pair across positions; assuming BCM numbering when the code uses physical; 5 V logic
    on a 3.3 V pin; reversed barrel-jack polarity; assuming pin 2 hot on vintage audio gear;
    plugging TTL serial into an RS-232 port; trusting cable colour rather than continuity.
12. **Related sheets** footer per the cross-link map.

## Volatile-facts register

**Overall: STABLE, with two moving parts.**
- RJ45/T568, XLR, DB9, OBD-II, relay terminals, barrel jacks: fixed standards, effectively frozen.
- **USB-C and Power Delivery: SLOW-DRIFT** — PD revisions add power levels; re-verify the PD table
  and the marking rules annually and date that section inline.
- **Raspberry Pi GPIO: SLOW-DRIFT** — the 40-pin header is stable across models, but new boards
  add function assignments; state which board generations the table covers.
Annual freshness rotation, with the USB-PD and GPIO sections as the named check targets.

## Index category

`Engineering & Science`.

## Reading conditions

**Bench or crawl space: phone or laptop propped at an angle, hands holding a connector or a crimp
tool, frequently poor light, sometimes upside down under a desk.** Consequences: diagrams must be
legible at 375 px without pinch-zoom (draw them at that size first, then scale up — not the other
way round), every diagram must state its orientation in words as well as showing it, colour must
never be the only carrier of information (the T568 tables must be readable in greyscale and by a
colour-blind reader — label every colour in text, e.g. "white/orange", never a swatch alone), and
the print stylesheet must render each connector block on a single page.

## Cross-link map

- **Internal outbound:** `fastener-torque-tap-drill.html` (batch sibling),
  `home-electrical-basics.html`, `auto-repair-decoder.html` (OBD-II adjacency),
  `sensors-cameras-lidar-radar-imu-gps.html`, `ubuntu-linux-for-ai-developers.html` (serial
  console adjacency), `personal-cybersecurity.html` (the "found a USB cable" caution, one line).
- **Reciprocal inbound:** one line each from `home-electrical-basics.html` and
  `auto-repair-decoder.html`.
- **External outbound:** standards and vendor documentation only — TIA-568, USB-IF, SAE J1962,
  Raspberry Pi documentation.

## og:image / shareable artifact

The T568A/T568B side-by-side diagram — the single most-looked-up thing on the page — rendered at
1200×630 with the colour names printed on the conductors. Also the screenshot-this artifact.

## Jurisdiction scope

Global standards throughout. Two regional notes stated once: mains-side wiring colours are
deliberately **out of scope** (they are jurisdictional and dangerous to half-cover — point to
`home-electrical-basics.html` instead), and automotive OBD-II is legally mandated in the US from
1996 and the EU from 2001 for petrol, with the equivalents named.

## Density targets

≥ 10 connector families; RJ45 tables 8 rows × 2 standards; USB-C 24 pins; OBD-II 16 pins; DB9
9 pins × 2 roles; GPIO 40 pins with dual numbering; relay 5 terminals; PD levels ≥ 5; pin-1
conventions ≥ 6; common mistakes ≥ 8. Every family carries a drawn diagram — a family without a
diagram does not ship.

## Research sources (verify against these, per Rule 1)

ANSI/TIA-568 (Ethernet pin/pair assignment), IEEE 802.3 (PoE modes), USB-IF specifications
(USB-C and PD), SAE J1962 and ISO 15765 (OBD-II), AES14/IEC 61938 (XLR and phantom power),
TIA-232-F (serial), official Raspberry Pi documentation (GPIO), and manufacturer datasheets for
barrel jacks and relays. Diagrams must be drawn from the standard, not traced from another site's
image.

## Visual design

**Identity: the same blueprint/shop-drawing language as the fastener card**, deliberately — the
two pages are a matched pair and should be recognizable as a set. Where the fastener page uses
schedules and title blocks, this one uses **exploded-view drawings**: each connector rendered as
inline SVG in the drafting line style, pins numbered in drawing callouts with leader lines to the
table rows beside it. Cyanotype blue in dark mode, drafting vellum in light. Every diagram is
inline SVG with a `<title>` and `<desc>` for screen readers (and note, per the metadata sweep
warning in `seo-planning.md`, that SVG `<title>` elements must not collide with the document
title). No JavaScript; hovering a table row highlights its pin in the diagram via pure CSS
sibling selectors if it can be done without script, and is dropped entirely if it cannot.
