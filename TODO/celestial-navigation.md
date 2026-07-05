# Spec: Celestial Navigation on One Page

**Target file:** `celestial-navigation.html`

**Why this topic:** The complete skill lives in out-of-print Bowditch editions, WWII air-navigation manuals, and dying yacht-club oral tradition — Google surfaces only fragments and forum arguments. It's the purest "resurrect offline knowledge" play on the list, it slots directly into the site's ham-radio/prepper/emergency cluster (GPS-denied navigation is the prepper hook; WWV time signals are the ham hook), and "outmoded but fascinating" is a house category. A competent reader should finish able to take and reduce a real noon sight.

## Targeting

- **Primary query:** "celestial navigation" — research mode; nobody learns the sextant mid-crisis. This page is studied ashore and printed for the ditch bag. Secondary: "how to use a sextant", "noon sight latitude calculation", "how to navigate without GPS", "sight reduction tables explained", "find longitude with a watch".
- **Title:** `Celestial Navigation: Find Your Position Without GPS` (53 chars). **H1:** "Celestial Navigation on One Page". **Meta description:** "Find your position with a sextant, a watch, and a book — no electronics. Noon-sight worksheet, sextant corrections, sight reduction, dead reckoning, and no-instrument emergency methods on one page." (~197 chars)
- **Reader outcome:** take and reduce a real noon sight to an actual latitude — and a rough longitude from noon timing — using only the worksheet on this page. (Restates the sentence above; it is the page's acceptance test.)
- **Success metric:** bookmark/print-first page — print events and return-direct visits matter more than raw organic entries; secondary: organic entries on the "noon sight" / "sight reduction" long-tails and shares of the worked worksheet.
- **Volatile-facts register — overall STABLE.** The geometry never rots. Watch items: (a) worked-example almanac values — verify once against the stated date's Nautical Almanac, then frozen; (b) free-download URLs for HO-249 / Bowditch / the NA sight-reduction pages — link-rot check yearly; (c) WWV/WWVH/CHU status — frequencies are decades-stable but WWV defunding proposals recur, confirm still broadcasting each freshness pass; (d) sextant prices (Davis Mark 15 ~$60, Astra IIIb) — re-check yearly.
- **Index category:** Risk & Preparedness (new category, decided at spec-batch time; the builder adds it to index.php's `$categoryMap`).
- **Jurisdiction:** none — the geometry and the almanac are global; the only US-flavored details are the free NGA/USNO source downloads, which anyone can use.
- **Reading conditions:** studied calm at a desk; *used* on a moving deck in glare or at night, likely from a printed copy in a ditch bag. Derived priorities: the print stylesheet is mandatory and first-class (README Rule 3) — the worksheet must survive grayscale Letter/A4; total offline self-containment beats dark mode; mobile is a study surface, not the use surface.
- **Cross-link map:** outbound → `nuclear-preparedness.html` (prepper-cluster sibling), `baofeng-uv5r-quick-ref.html`, `ham-radio-technician.html`, `emergency-radio-card.html` (the WWV time-signal segue in section 4 is the natural anchor). Inbound ← `nuclear-preparedness.html`, plus reciprocal links added to the three radio pages.

## Content approach

Promise of the page: **find your position on Earth with a sextant, a watch, and a book — no electronics.** Structure it as theory → the one easy method (noon sight) → the general method (sight reduction) → no-instrument fallbacks.

Sections:

1. **The mental model.** Every celestial body is directly over exactly one point on Earth right now (its Geographic Position, tabulated in the Nautical Almanac). Measuring the body's altitude tells you your distance from that point — putting you on a circle of position. Two circles (or one circle + a compass bearing or DR estimate) = a fix. State this in ~4 sentences with a simple diagram; everything else is bookkeeping.
2. **Quick reference block.** The full noon-sight worksheet (fill-in-the-blank format, ~12–15 lines), the sextant correction stack in order (6 layers), the 7 key almanac quantities defined (GHA, LHA, declination, Hs/Ha/Ho, azimuth), and "accuracy you can expect" table (4–6 rows): noon sight ±1–2 nm latitude, timed sights ±2–5 nm, no-instrument methods ±30–60 nm.
3. **The sextant.** Parts diagram, how to bring a body to the horizon, rocking the sextant, reading the arc + micrometer. The correction stack with real numbers: index error (how to measure it against the horizon), dip (height of eye — table, 8–10 rows: e.g. 2 m → −2.5′), refraction, semidiameter, parallax. One fully worked correction: Hs → Ho with actual values. Buying note: a $60 Davis Mark 15 plastic sextant vs. a metal Astra IIIb — plastic is genuinely adequate to ±2–3 nm.
4. **The noon sight — latitude the easy way.** The method that needs almost no math: track the sun's maximum altitude at local apparent noon; Latitude = 90° − Ho ± declination (sign rules spelled out with all three cases). Full worked example with real date, real almanac declination, real numbers to a final latitude. Then **longitude from noon timing**: local apparent noon UTC vs. Greenwich + equation of time → longitude at 15°/hour (4 min = 1°). Why an accurate watch matters: 4 seconds of clock error = 1 nm of longitude — segue to time sources: WWV/WWVH frequencies (2.5/5/10/15/20 MHz), CHU, and quartz-watch drift-rate logging (calibrate before you need it).
5. **General sight reduction (any body, any time).** Honest framing: this is table lookup, not math. The intercept method (Marcq St. Hilaire) as a recipe: assume a position → compute what the altitude *should* be (Ho-249/Ho-229 or NASR tables) → compare with observed → the difference in minutes-of-arc is nautical miles toward/away from the body's azimuth → plot the LOP. One compressed worked example. Where to get the tables free: HO-249 and the Nautical Almanac's own NASR pages are public-domain downloads; list them. Star selection: the ~8 workhorse navigational stars + Polaris latitude shortcut (Ho of Polaris ≈ latitude, ±1° correction table exists).
6. **Dead reckoning — the connective tissue.** Log/speed × time × course; keeping a DR plot between fixes; set and drift (current) correction with the vector triangle; the 60 D=ST mental-math forms; why celestial fixes exist to *correct* DR, not replace it. Include the 6-minute rule (distance in 6 min = speed ÷ 10).
7. **No-sextant emergency methods** (expect 8–10 distinct methods, each with an honest error bar)**.** Kamal (knotted string + card — include the make-it-yourself dimensions), fingers/fist as degree measures (calibration: fist ≈ 10°, finger ≈ 2°), latitude from Polaris by eye, latitude from day length, direction: shadow-stick method, watch method (with its real error bars), star-rise bearings, ocean swell consistency. Frame with real precedents (Polynesian navigation, Shackleton's Worsley, WWII life-raft kits).
8. **Common mistakes** (the six here are the floor; 6–8 entries)**:** confusing true/magnetic/compass bearings (TVMDC), wrong sign on index correction, using zone time instead of UTC in the almanac, upper vs. lower limb mix-ups, rounding the assumed position wrong for the tables, trusting a noon sight for longitude without knowing the equation of time.

Research: Bowditch (*American Practical Navigator*, free from NGA — cite chapter numbers), the current Nautical Almanac's sight-reduction pages, HO-249 tables, Mary Blewitt's *Celestial Navigation for Yachtsmen* for pedagogy cues.

## Visual design

**Nautical chart aesthetic** — the page dressed as a plotting sheet. Distinct from every other page: no cards, no dashboard.

- Background: pale chart-paper cream with a faint compass rose watermark and fine lat/long graticule lines (pure CSS background, subtle enough to keep text AAA-readable).
- Typography: engraved-chart feel — a slab/DIN-style face for headings reminiscent of chart lettering, small-caps section labels ("SECTION 4 — MERIDIAN PASSAGE").
- **The noon-sight worksheet as the hero element:** rendered like a paper form with ruled fill-in lines and a completed example in a handwriting-style font overlaying it (side-by-side: blank | worked).
- **og:image / shareable artifact:** the *worked* side of the noon-sight worksheet, rendered as the 1200×630 social card — signature element and share card are the same artifact by design, and the worksheet is also the page's "screenshot this" block.
- **Correction stack as a vertical "stack diagram":** Hs at top, each correction as a labeled +/− layer, Ho at the bottom — like a receipt.
- Diagrams as inline SVG in chart-style line art (one color + black): celestial sphere/GP diagram, sextant parts, the intercept/LOP plot, the set-and-drift vector triangle.
- Optional single interactive: a "clock error → position error" slider (seconds of error → nm at your latitude). Nothing else; the page should feel like an artifact, and print beautifully (include a print stylesheet — this is a page people will genuinely print for a ditch bag).
