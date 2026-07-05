# TODO/ — Implementation guidance for all specs in this folder

Each `.md` file here is a spec for one cheatsheet. Specs cover the topic: content angle,
section structure, and a page-specific visual identity. Everything else — quality bar,
density floor, atomic entry rule, accuracy protocol, testing checklist — lives in
`AGENTS.md` and is binding. Read AGENTS.md first, then the spec, then this file's rules.
When done, delete the spec file. When **writing or reviewing** a spec, also check it
against `SPEC-AUDIT.md` (spec-completeness criteria: search targeting, reader outcome,
staleness register, etc.). For auditing **already-shipped** cheatsheets, use
`CHEATSHEET-AUDIT.md` (per-file conformance procedure + corpus defect baseline).

## Rule 1: Numbers in specs are anchors, not facts

Every figure in a spec (prices, NNTs, protection factors, micromort values, legal
thresholds, state counts) is a **plausibility anchor from the spec author's memory** —
it tells you the expected order of magnitude and what kind of number belongs there.
It is NOT a verified fact. Verify every number against the primary sources named in
the spec before it goes on the page. If your verified number disagrees with the spec's
anchor, the verified number wins, no discussion needed. If you can't verify a spec
number, omit that entry rather than shipping the anchor.

## Rule 2: Outline first, then build

Before writing any HTML, produce and review your own plan:

1. Full section outline to three depths (per AGENTS.md coverage contract).
2. For every major table: the complete **row list** (not the cell contents — just what
   the rows will be) plus **one fully-populated exemplar row** at final depth.
3. The list of facts requiring primary-source verification, mapped to the source you'll use.

Check that plan against the spec and AGENTS.md's density floor. A thin outline caught
here costs minutes; a thin finished page costs a full regeneration. Only then research
and build.

## Rule 3: Definition of done (applies to every spec)

A page is done when all of these hold, in addition to the AGENTS.md testing checklist:

- Every section named in the spec exists and is fully populated; every major table meets
  or exceeds the row coverage the spec describes.
- Every worked example arrives at an actual final answer (a real latitude, a real dollar
  gap, a real NNT) — never "…and so on."
- Every volatile fact carries an inline date or version tag; the page has a visible
  `Last verified:` line.
- The spec's **signature visual element** (see Rule 5) is implemented and is the most
  polished thing on the page.
- The page renders correctly at 375 px wide and prints sanely (the celestial and nuclear
  pages REQUIRE a deliberate print stylesheet; for the rest, sane defaults suffice).

## Rule 4: Anti-goals — what NOT to include

Global: no affiliate framing, no product/brand recommendations beyond what the spec
explicitly names as an example, no filler prose restating the obvious, no hedging
boilerplate repeated per-section (one clear disclaimer where the spec says so, then
get on with it).

Per-domain:
- **Medical pages (NNT, risk dashboard):** decision-support framing only. No dosing
  advice, no treatment recommendations, no "ask your doctor" padding beyond the single
  prominent disclaimer.
- **Legal/consumer pages (death logistics, insurance, small claims):** state law varies —
  say so once per section where it matters, with "verify for your state," not per-sentence.
- **Nuclear page:** preparedness only. No weapons-design or weapons-effects detail beyond
  what shelter decisions require.
- **All pages:** if a subtopic tempts you to write a second cheatsheet inside this one,
  link the gap in one line and move on.

## Rule 5: Design execution

Each spec defines a unique visual identity so the collection doesn't converge on one
aesthetic. To keep that intent through implementation:

- Each spec names (explicitly or implicitly) one **signature element** — the icon array,
  the rubber-stamp verdicts, the decay curve, the noon-sight worksheet. Build that first
  and best; it's the page's shareable artifact and the thing that must not be generic.
- Derive a concrete palette (real hex values) and font stack from the spec's design
  language before writing CSS, and use them consistently. When a spec references a style
  ("chart paper," "civil-defense," "financial ledger"), commit to it fully — a
  half-applied theme reads as default AI styling.
- Signature layouts must degrade gracefully on mobile: timelines collapse to
  single-column, wide tables get `overflow-x: auto` in a wrapper, decorative backgrounds
  never cost readability. Test the signature element at 375 px specifically.
- System font stacks are fine; if a spec's identity truly needs a distinctive face,
  prefer a locally-tolerable fallback stack over loading web fonts.

## Rule 6: Interlinking and SEO

- Add "Related" links to the existing pages in this repo that share the cluster
  (e.g., celestial navigation and nuclear preparedness ↔ `baofeng-uv5r-quick-ref.html`,
  `ham-radio-technician.html`, `emergency-radio-card.html`; insurance ↔
  `index-investing-tax-advantaged.html`; death logistics ↔ estate/aging content as it
  lands). Where natural, add a reciprocal link from the existing page.
- Follow `SEO_PROMPT.txt` for metadata. Derive the `<title>` and meta description from
  the spec's "why this topic" paragraph — the unique angle IS the search hook (e.g., the
  honest-pricing angle, the fatalism-correction angle), so lead with it rather than a
  generic topic label.
- JSON-LD must describe only what's actually on the page (per AGENTS.md).
