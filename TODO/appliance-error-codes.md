# Spec: Appliance error codes — the cross-brand decoder

**Target file:** `appliance-error-codes.html`
**Batch:** [niche-utility-batch-2026-08.md](niche-utility-batch-2026-08.md) (sheet 8 of 10).

## Why this topic

The site already has direct evidence that appliance-manual queries rank here trivially:
`"samsung bespoke oven microwave combo instructions"` sits at **position 1.2** on 188 impressions
per 90 days, from a single-model page (`samsung-bespoke-oven-guide.html`) that David built for his
own kitchen. Position 1.2, zero clicks — a SERP feature is eating it, but the *ranking* proves the
category is winnable with a fraction of the effort a competitive topic takes.

The generalization is obvious and unbuilt: the moment an appliance shows `4C` or `LE` or `E24`, the
owner's actual question is not "what does this code mean" (a dozen sites answer that) but **"is
this a fix-it-myself or a call-the-tech, and what does it cost either way"** — and, crucially,
whether the same three-letter code means the same thing on their brand as on the one the search
result was written for. It does not. Cross-brand collision is the reason this page exists: a
single decoder that resolves a code *within its brand* and says plainly when a code is
manufacturer-specific.

The incumbents are repair-parts retailers whose entire business model is selling you the part,
and content farms that copy each other's code lists without checking. An independent page that
says "this code is usually not a failed part, check the filter first" has an angle neither can
take.

## Targeting

- **Primary query:** `[brand] washer error code [code]` — the long-tail head of a very large family
- **Secondary:** `samsung washer 4c error`, `lg washer le code`, `whirlpool dishwasher error
  codes`, `bosch dishwasher e24`, `ge refrigerator error codes`, `dryer error codes`
- **Mode:** **crisis-adjacent**: standing in a laundry room with a beeping machine. The searcher
  arrives on a specific code, so the page must land them on that row, not on an introduction —
  every code is a stable `#anchor`.

## Draft title / H1 / meta

- `<title>`: `Appliance Error Codes: Samsung, LG, Whirlpool, Bosch` (51 chars)
- **H1:** `Appliance Error Codes and What They Actually Mean`
- **Meta description (draft):**
  `Washer, dryer, dishwasher, fridge and oven fault codes for Samsung, LG, Whirlpool, GE and Bosch, with the failure each code points at and what to check before calling.` (166 chars)

## Reader outcome

Given a code on a display, the reader can name the subsystem it implicates, perform the two or
three checks that resolve the majority of instances of that code, and — if those fail — decide
between a service call and replacement with an actual cost range in hand, rather than a guess.

## Success metric

Organic entries across many long-tail code queries rather than one head term (this page is a
portfolio, like the pinout card). The KPI is **breadth of ranking codes**, measured as the number
of distinct queries in GSC that land on this URL, not the clicks on any one. Secondary: anchor-
level deep links.

## Content approach

**Scope decision, stated on the page:** five brands — Samsung, LG, Whirlpool, GE, Bosch — across
five appliance types. Naming the scope beats a thin pretence of covering everything, and the
brands are chosen for US market share plus code-system distinctiveness.

1. **Quick Reference: type your code** (signature element) — a code-lookup block: a static,
   alphabetically-ordered index of every code on the page, grouped by brand, each linking to its
   row. If (and only if) it can be done in plain CSS-and-a-tiny-inline-script with a working
   no-JS fallback to the full index, a filter box on top; the index must work with JavaScript
   disabled.
2. **The master code table** — the page's core, one row per code: brand, appliance type, code as
   displayed, what the machine is actually reporting, the most common cause, the first check,
   the second check, "DIY or tech" verdict, and typical part cost range. Grouped by brand, then by
   appliance. Target ~120 rows.
3. **The collision table** — codes that mean different things on different brands (the reason
   generic code lists mislead). One row per colliding code with each brand's meaning side by side.
   This is the page's differentiator and should sit high, right after the master table's intro.
4. **The five checks that resolve most codes** — before any code-specific advice: power-cycle and
   how long to hold it by brand, water supply and inlet screens, drain filter and pump, door/lid
   switch and latch, and levelling. With the honest note that a large share of "error" calls are
   resolved by one of these.
5. **Per-appliance failure primers** — five short sections (washer, dryer, dishwasher,
   refrigerator, oven) each explaining what the machine's sensors actually measure, so a code
   becomes interpretable rather than memorized: pressure switch versus flow meter, thermistor
   versus thermal fuse, turbidity sensor, defrost cycle, and oven temperature probe drift.
6. **Diagnostic/test modes** — how to enter service or test mode per brand, what it displays, and
   the caution that some test modes will run components dry. Include how to read a stored fault
   history where the brand supports it.
7. **Repair-or-replace** (mandatory decision guidance) — a table by appliance type: typical repair
   cost, typical replacement cost, remaining-life expectation by age, and the standard rule of
   thumb with its failure cases (the rule breaks for high-end built-ins and for compressors under
   sealed-system warranty). Include the "second failure within a year" heuristic.
8. **What to have ready when you call** — model and serial location by appliance type (with where
   the sticker actually is: door jamb, under the lid, behind the kickplate), the code, what you
   already checked, and purchase date. Screenshot-sized block.
9. **Warranty and parts reality** — sealed-system and compressor warranties that outlive the
   general warranty, why the first-line phone diagnosis is often "descale it", the OEM-versus-
   aftermarket part question stated factually, and the recall lookup step (CPSC / manufacturer)
   that costs nothing and occasionally makes the repair free.
10. **Common mistakes** (mandatory): replacing a pump because of a drain code when the filter was
    clogged; assuming a shared code means the same thing across brands; running a diagnostic mode
    without water supply; ignoring an intermittent code until it becomes a flood; buying a control
    board first (the most expensive and least often faulty part); not clearing the code and
    assuming the repair failed.
11. **Related sheets** footer per the cross-link map.

## Anti-goals

No part-number recommendations, no retailer links, no affiliate framing — the page's entire
credibility rests on not being a parts funnel. No live-electrical repair procedure: where a step
requires opening a powered cabinet, the page says "this is a tech job" and stops. No brand
editorializing ("brand X is junk").

## Volatile-facts register

**Overall: SLOW-DRIFT with one fast-moving column.**
- Code meanings: stable per platform, but manufacturers introduce new code systems with new
  product generations. State the model-year/platform range each brand's table covers.
- **Part and repair cost ranges: VOLATILE — annual re-verification, and every figure dated
  inline.** This is the page's primary freshness target.
- Diagnostic-mode entry sequences: stable per platform, change across generations.
- Recall status: check the CPSC link works; do not enumerate live recalls (they rot immediately).

## Index category

`Home & Lifestyle`.

## Reading conditions

**Laundry room or kitchen floor, phone in one hand, often kneeling, machine beeping, sometimes
water on the floor.** Consequences: land-on-anchor navigation must work (a reader arriving from
Google on `#lg-le` sees that row immediately, with a visible "back to index" control), large text,
high contrast in bright kitchen light, and no interstitials. Print stylesheet: the five checks
plus the "what to have ready" block on one sheet for the utility-room wall.

## Cross-link map

- **Internal outbound:** `samsung-bespoke-oven-guide.html` (the single-model proof-of-concept —
  link both ways), `home-maintenance-guide.html`, `home-electrical-basics.html`,
  `hiring-a-contractor.html` (the service-call negotiation), `air-water-filtration.html` (water
  hardness as a root cause of dishwasher and washer faults), `contract-red-flags.html` (extended
  warranty contracts).
- **Reciprocal inbound:** a line from `samsung-bespoke-oven-guide.html` and
  `home-maintenance-guide.html`.
- **External outbound:** manufacturer support pages and CPSC recall search only.

## og:image / shareable artifact

The collision table — the same code meaning three different things on three brands — at 1200×630.
It is the most distinctive claim on the page and the reason to link it.

## Jurisdiction scope

**US market appliances**, stated once: model lines, code systems and cost ranges are US. Note that
European variants of the same brands (particularly Bosch and Samsung) use different code systems
and that this page covers the US-market platform, so a reader in the EU knows to check their own
manual.

## Density targets

Master table ≥ 100 code rows × 9 columns across 5 brands × 5 appliance types (minimum 15 codes
per brand); collision table ≥ 8 codes; five-checks section 5 items with per-brand variations;
per-appliance primers 5 × ≥ 4 sensor explanations; diagnostic-mode entries 5 brands × appliance
types where documented; repair-or-replace table ≥ 5 rows; common mistakes ≥ 6.

## Research sources (verify against these, per Rule 1)

Manufacturer service manuals and official support documentation for each brand — the only
acceptable source for a code meaning. Cost ranges from published industry survey data with the
survey and year named, never from a repair blog's guess. CPSC for recall procedure. Where a code's
meaning cannot be confirmed in a manufacturer document, **omit the row** rather than repeat what
the content farms say — the collision table exists precisely because those sources are unreliable.

## Visual design

**Identity: appliance control panel.** Seven-segment display treatment for the code itself — each
code rendered in a small LED-style plate (drawn with CSS, not an image font), against brushed-
steel-grey panel surfaces with a single amber fault accent. Light mode is a white enamel panel;
dark mode is the machine at night with the display lit. Rows are grouped in "panel" cards per
brand with the brand as a moulded label. The verdict column uses a two-state chip — *you* or
*tech* — in words plus shape, never colour alone. The code index at the top is the signature
element and must feel like a lookup instrument. JavaScript budget: one optional filter input with
a full no-JS fallback, nothing else.
