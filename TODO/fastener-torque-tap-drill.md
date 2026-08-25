# Spec: Fastener bench card — tap drills, grades and torque

**Target file:** `fastener-torque-tap-drill.html`
**Batch:** [niche-utility-batch-2026-08.md](niche-utility-batch-2026-08.md) (sheet 6 of 10).
**Pair:** build back-to-back with [connector-pinouts.md](connector-pinouts.md); they share a
design language and a reader.

## Why this topic

This is the archetype of the shape `TODO/README.md` Rule 0 protects: a dense numeric table a
person keeps open — or tapes to a wall — *while their hands are busy*. Nobody asks an AI chat
"what drill for a 3/8-16 tap" twice; they look it up on the same page every time, because the
answer is a lookup, not an explanation, and because a wrong answer wastes a part.

The site has no shop reference at all, despite `engineering-metals-selection.html`,
`auto-repair-decoder.html`, `hiring-a-contractor.html` and `home-maintenance-guide.html` all
sending readers toward exactly this lookup and dropping them. The existing web coverage is
manufacturer PDFs (accurate, unreadable on a phone, un-linkable to a specific row) and chart
farms (readable, unsourced, frequently wrong about grade markings).

The differentiator: **one page that answers the whole sequence** — what thread is this, what
drill do I need to tap it, what clearance hole for the through-piece, what grade is this bolt
from its head marking, what torque does that grade take in this material, and what changes when
it is lubricated. Every existing resource covers one link in that chain.

## Targeting

- **Primary query:** `tap drill chart`
- **Secondary:** `bolt torque chart`, `metric tap drill size`, `bolt grade markings`,
  `clearance hole size chart`, `thread pitch chart`, `torque specs by bolt size`,
  `dry vs lubricated torque`
- **Mode:** research-then-return. First arrival is a search; every subsequent arrival is a
  bookmark or a print. Optimize the *return* experience: stable anchors per table, printable,
  fast.

## Draft title / H1 / meta

- `<title>`: `Bolt Torque & Tap Drill Chart: Threads, Grades, Sizes` (53 chars)
- **H1:** `Fastener Bench Card: Tap Drills, Grades and Torque`
- **Meta description (draft):**
  `Tap drill sizes, thread pitch, clearance holes, bolt grade markings and torque specs for inch and metric fasteners, plus lubrication factors and thread-locker rules.` (164 chars)

## Reader outcome

Standing at a bench with an unknown bolt and a hole to make, the reader can identify the thread,
pick the correct tap drill and clearance drill, read the grade off the head, and apply a defensible
torque figure — including the correction for lubrication, which is where most amateur fastener
failures actually come from.

## Success metric

Organic entries on the chart query family, plus **print events and return-direct traffic** — this
page's success looks like a taped-up printout. Secondary: deep-link traffic to specific table
anchors (a sign other sites and forum posts are citing individual rows).

## Content approach

1. **Quick Reference: the eight highest-frequency lookups** — the rows people actually need:
   1/4-20, 5/16-18, 3/8-16, 1/2-13, M6×1.0, M8×1.25, M10×1.5, M12×1.75 — each with tap drill,
   clearance drill, and Grade 5 / class 8.8 dry torque. One screen, before anything else.
2. **The master inch table** (signature element) — every common UNC and UNF size from #4 to 1",
   columns: nominal size, threads per inch, major diameter, tap drill (75% thread), tap drill
   (50% thread, for hard materials), decimal equivalent, close-fit clearance drill, free-fit
   clearance drill. Number-and-letter drills spelled out with decimals — the whole point is not
   having to cross-reference a second chart.
3. **The master metric table** — M2 through M24, coarse and fine pitch rows separated, same
   column structure, with the standard "tap drill = major diameter − pitch" rule stated once and
   the sizes where it fails called out.
4. **Grade identification** — head markings rendered as small drawn diagrams, not described in
   prose: SAE Grade 2/5/8, ASTM A325/A490, metric class 4.6/8.8/10.9/12.9, stainless A2/A4 and
   why stainless is *weaker*, not stronger, than a Grade 8. Columns: marking, proof strength,
   tensile strength, typical use, and the "do not substitute" note.
5. **The torque tables** — separate tables for inch and metric, rows by size, columns by grade,
   with **three torque columns: dry, lubricated, and zinc-plated**, plus the lubrication
   correction factor stated as a rule (anchor: lubricated ≈ 25–30% below dry — verify). State the
   basis: torque is a proxy for clamp load, K-factor assumptions, and why the same bolt in
   aluminium gets a different number.
6. **Threads in soft materials** — minimum thread engagement by material (steel, cast iron,
   aluminium, plastic), when to use a threaded insert (helicoil-type) instead, and torque
   reduction in aluminium and plastic.
7. **Thread lockers, anti-seize and sealants** — the colour-strength convention, cure time and
   temperature, removal torque, when anti-seize *invalidates* a published torque figure (it makes
   the joint lubricated — this is the single most common professional mistake), and the
   galvanic-corrosion cases where it is mandatory.
8. **Washers, torque-to-yield and reuse** — flat versus lock washers and the evidence on split
   washers, wedge-lock washers, what torque-to-yield means, and the flat rule that TTY bolts are
   single-use. Include the torque-angle method in three lines.
9. **Wrench and socket reference** — head size across the flats by bolt size for both systems, the
   metric/imperial near-misses that round fasteners (13 mm vs 1/2", 19 mm vs 3/4"), and
   6-point-versus-12-point guidance.
10. **Drill and tap technique, briefly** — tap drill for cutting versus forming taps, back-off
    intervals, cutting fluid by material, and the two failure modes (broken tap, stripped thread)
    with what causes each. Kept short: this is a numbers page, not a machining tutorial.
11. **Common mistakes** (mandatory): torquing a lubricated bolt to a dry spec; substituting a
    stainless bolt for a Grade 8; reusing TTY bolts; using a 75% tap drill in hardened steel;
    trusting a torque wrench that has never been calibrated or that was stored loaded; measuring
    thread pitch by eye instead of with a gauge; the 13 mm/half-inch socket habit.
12. **Related sheets** footer per the cross-link map.

## Volatile-facts register

**Overall: STABLE — the most stable page in the batch.** Thread standards and torque relations
have not moved in decades.
- ISO 68-1/261/262 (metric), ASME B1.1 (unified), SAE J429, ASTM A325/A490: revisions are rare
  and never change common values.
- The only genuine drift: available fastener classes at retail, and thread-locker product lines.
Annual freshness check is generous. Note the standard revision year each table is drawn from.

## Index category

`Engineering & Science`.

## Reading conditions

**Garage or shop: standing, dirty hands, phone propped or a printed sheet on a pegboard, often
poor light, sometimes a tablet at arm's length.** Consequences: tabular figures at a large optical
size, high contrast in both themes, zebra-striped rows (row-tracking across eight columns is the
real usability problem here), sticky table headers so scrolling deep into the metric table still
shows the column names, and wide tables wrapped in `overflow-x: auto` with the size column
visually pinned. **Print stylesheet is mandatory and is a first-class deliverable**: the inch
table, metric table and torque tables must each print to a single clean page, greyscale-safe.

## Cross-link map

- **Internal outbound:** `engineering-metals-selection.html` (material strength — link both
  ways), `auto-repair-decoder.html`, `home-electrical-basics.html`,
  `home-maintenance-guide.html`, `hiring-a-contractor.html`, `connector-pinouts.html` (the batch
  sibling and the other half of the bench pair).
- **Reciprocal inbound:** one line each from `engineering-metals-selection.html` and
  `auto-repair-decoder.html`.
- **External outbound:** standards bodies only (ISO, ASME, SAE, ASTM listing pages). No supplier
  or affiliate links, per README Rule 4.

## og:image / shareable artifact

The grade-marking diagram row — the drawn bolt heads with their strengths — at 1200×630. It is
the most visually distinctive block and the one people screenshot; the tables are the utility, but
the markings are the share.

## Jurisdiction scope

Not jurisdictional, but **dual-system by construction**: inch and metric are given equal weight
throughout, never converted from one to the other. Torque given in both lb-ft and N·m in every
cell. State once that fastener standards are international and that the divergence is regional
practice, not law.

## Density targets

Inch table ≥ 30 rows × 8 columns; metric table ≥ 24 rows (coarse + fine) × 8 columns; grade table
≥ 10 rows; torque tables ≥ 20 rows × 3 torque columns each system; thread-engagement table ≥ 4
materials; thread-locker table ≥ 6 rows; wrench-size table ≥ 20 rows; common mistakes ≥ 7. This
page should be among the densest on the site.

## Research sources (verify against these, per Rule 1)

ASME B1.1 (unified inch threads), ISO 68-1 / 261 / 262 / 965 (metric threads and tolerances),
SAE J429 and ASTM A325/A490/F3125 (grades and proof loads), ISO 898-1 (metric property classes),
Machinery's Handbook for tap drill and clearance conventions, and manufacturer engineering data
(Loctite/Henkel technical data sheets) for thread-locker figures only. Every torque value must be
traceable to a published clamp-load calculation or a standard's table — never to a chart site, and
never to the anchors in this spec.

## Visual design

**Identity: blueprint / shop drawing.** Cyanotype-blue ground with white rule lines and drafting
annotations in dark mode; in light mode, white drafting vellum with blue-grey rules and a red
correction-pencil accent used only for the "do not do this" callouts. A single condensed
engineering face with true tabular figures throughout. The grade-marking block is drawn as inline
SVG bolt heads in the drawing style — this is the signature element and must be genuinely drawn,
not iconographic clip art. Tables are styled as drawing-sheet schedules with a title block above
each (standard, revision year, units). Zero JavaScript; sticky headers and row highlighting are
pure CSS.
