# Spec: Eid prayer — the follow-along card

**Target file:** `eid-prayer-cheatsheet.html`
**Batch:** [niche-utility-batch-2026-08.md](niche-utility-batch-2026-08.md) (sheet 4 of 10).
**Seasonal:** Eid al-Fitr and Eid al-Adha are the demand spikes; Ramadan 1448 begins ≈ February
2027. Ship by January 2027 at the latest, earlier if the queue allows — the page also earns
steadily from the "how do I pray Eid" evergreen.

## Why this topic

Measured, unclaimed demand: **`"eid cheat sheet"` earned 317 impressions in 90 days at position
8.7 with zero clicks**, landing on `islam.html` — a broad overview that mentions holy days and
never tells anyone how the prayer runs. Google has already decided this site is relevant to the
query; the site simply has nothing that answers it.

The competitive field is charity-organization blog posts: readable, well-intentioned, and almost
all of them silently pick one madhab's takbirat count and present it as *the* count. A reader
standing in an unfamiliar musalla, following an imam who does it differently, is left thinking
they got it wrong. **The differentiator is the comparison table** — Hanafi, Shafi'i, Maliki and
Hanbali side by side, with the count, the placement, and what to do when the imam's practice
differs from yours (follow the imam). That is the dense-verified-comparison shape the site is
built for, applied to a ritual follow-along — the same combination that makes
`shabbat-services-cheatsheet.html` the site's CTR benchmark at 2.63%.

## Targeting

- **Primary query:** `how to pray eid prayer`
- **Secondary:** `eid prayer takbir count`, `eid salah steps`, `eid prayer time`,
  `eid al adha prayer`, `takbir eid text`, `zakat al fitr amount`, `eid cheat sheet`
- **Mode:** **crisis-mode, minutes before.** Lead with the step order, not with the theology.
  Question-shaped H2s matching the queries above.

## Draft title / H1 / meta

- `<title>`: `Eid Prayer Cheat Sheet: Takbirat, Timing and Khutbah` (52 chars)
- **H1:** `Eid Prayer: Step Order and Takbirat by Madhab`
- **Meta description (draft):**
  `How Eid al-Fitr and al-Adha prayer runs rak'ah by rak'ah, with takbirat counts for the Hanafi, Shafi'i, Maliki and Hanbali schools, timing windows and the takbir text.` (166 chars)

## Reader outcome

A reader can pray Eid in congregation without hesitating: they know the two-rak'ah structure,
how many extra takbirat their own school prescribes and where they fall, what to do when the
imam follows a different school, when the khutbah comes relative to the prayer (the opposite of
Jumu'ah), and what the sunnah acts before leaving the house are.

## Success metric

Organic entries on the "how to pray eid" family and recovery of the already-ranking
`"eid cheat sheet"` query at a real CTR. Watch the two seasonal spikes specifically; a flat
annual average will hide the result. Secondary: AI-answer citation of the madhab table, which is
the one part of this topic assistants habitually flatten.

## Content approach

1. **Quick Reference: the prayer in one screen** (signature element) — a two-column rak'ah map:
   left column rak'ah 1, right column rak'ah 2, each step in order (opening takbir → extra
   takbirat → Fatihah → surah → ruku' → sujud → …), with the extra-takbirat cells rendered as
   counted marks so the number is visible before it is read. A madhab selector is **not** needed:
   show all four counts in the same cell, colour-coded to a legend.
2. **The madhab comparison table** — four schools × columns: extra takbirat in rak'ah 1, extra
   takbirat in rak'ah 2, placement relative to the opening supplication and Fatihah, whether
   hands are raised each time, what is recited between takbirat, and the ruling when the imam
   differs. Every row cited to that school's own recognized manual, not to a summary site.
3. **Timing** — when the window opens (after sunrise plus the standard interval) and closes
   (before zenith), why Eid al-Adha prayer is prayed earlier and Eid al-Fitr later, what happens
   if you miss the congregation, and the make-up rulings. Give the interval in both the classical
   formulation and clock minutes, with the caveat that local mosques set an announced time.
4. **The takbirat text** — the takbir of Eid in Arabic, transliteration, and translation, plus the
   distinction between the general takbir (recited on the way, both Eids) and the takbir at-
   tashriq (tied to the days of Tashriq for al-Adha), with the days it applies. Three columns.
5. **Before you leave the house** — the sunnah sequence: ghusl, best clothes, perfume (with the
   note for men and women), eating an odd number of dates before al-Fitr and *not* eating before
   al-Adha, taking a different route home, walking if able, and paying zakat al-fitr **before**
   the prayer. One line each, in the order they occur.
6. **Zakat al-fitr** — what it is, the classical measure (a sa' of staple food), how that is
   converted to a local cash figure and who publishes that figure, the deadline relative to the
   prayer, and who it is due for. State the measure and the conversion method; **do not publish a
   dollar figure**, which rots annually and varies by locality — point to the reader's local
   mosque or a named national body instead.
7. **Eid al-Adha specifics** — the relationship to Hajj days, the udhiyah/qurbani window and its
   deadline, the standard thirds division of the meat, and the practical route for someone in a
   country where they cannot slaughter locally.
8. **The khutbah** — that it follows the prayer (unlike Jumu'ah), that it is sunnah rather than
   obligatory to remain, the two-part structure with takbirat, and the practical note that
   leaving early is common and what the scholarly view of it is.
9. **Women, children and first-timers** — attendance rulings across the schools stated neutrally,
   what to expect physically in a crowded musalla or field prayer, prayer during menstruation
   (attending without praying), and childcare reality. Descriptive, not prescriptive.
10. **Common mistakes** (mandatory): raising hands at the wrong takbirat and correcting audibly;
    praying nafl before or after when the congregation does not; assuming the imam follows your
    school; paying zakat al-fitr after the prayer; leaving before the khutbah in a community where
    that is discourteous; arriving at the announced time rather than early enough to get a place.
11. **Related sheets** footer per the cross-link map.

## Volatile-facts register

**Overall: STABLE ritual, VOLATILE dates and amounts.**
- Eid dates: lunar and locally determined — **never publish a fixed future date without the
  sighting caveat.** Give the astronomical estimate with an explicit "confirm with your local
  authority" and date the estimate.
- Zakat al-fitr cash equivalents: annual, local. Deliberately not published (see §6).
- Fiqh positions, takbirat counts, prayer structure: stable for centuries.
Freshness routine: one check each January, before Ramadan.

## Index category

`Philosophy & Religion`.

## Reading conditions

**Phone, standing, in a crowd, often outdoors in a field or parking lot in bright morning sun,
minutes before the prayer starts.** Consequences: high-contrast light theme is the primary design
(sunlight, not a dim sanctuary — the opposite of the High Holiday page), very large tap targets,
the rak'ah map must fit one 375 px screen without scrolling, and the page must be fully usable
after loading with no network. Print stylesheet: the rak'ah map and madhab table on one sheet.

## Cross-link map

- **Internal outbound:** `islam.html` (the overview this page drills out of — link both ways;
  `islam.html` currently absorbs the query and must hand it off), `comparative-religion-map.html`,
  `shabbat-services-cheatsheet.html` and `high-holiday-services-cheatsheet.html` (the
  ritual-follow-along cluster this establishes).
- **Reciprocal inbound:** a prominent contextual link from the Holy Days section of `islam.html`,
  since that is the page currently ranking for the target query.
- **External outbound:** recognized school manuals and major fiqh councils for rulings. No
  charity fundraising pages, per the anti-affiliate rule.

## og:image / shareable artifact

The two-column rak'ah map with the takbirat counts visible, light theme, 1200×630. Same artifact
as the screenshot-this block.

## Jurisdiction scope

Global, Sunni-majority practice as the page's declared scope, stated once at the top with the
Shia difference acknowledged in a single honest paragraph and a pointer, rather than covered
badly. Local variation in timing and zakat amounts is handled by pointing to local authority
rather than by listing countries.

## Density targets

Rak'ah map ≥ 14 steps across two rak'ah. Madhab table 4 rows × 6 columns. Takbirat text block
3 columns × ≥ 3 formulations. Sunnah pre-prayer list ≥ 8 items. Zakat al-fitr ≥ 5 decision rows.
Al-Adha section ≥ 6 entries. Common mistakes ≥ 7. Every Arabic term given in Arabic script,
transliteration and English.

## Research sources (verify against these, per Rule 1)

Primary fiqh manuals or their recognized translations for each of the four schools (the takbirat
table is the page's credibility and cannot rest on secondary summaries); Sunnah.com for hadith
references with grading noted; major fiqh councils (AMJA, European Council for Fatwa and
Research, and the equivalent regional bodies) for contemporary rulings; an astronomical source
for date estimates. Where the schools genuinely differ, cite each separately — never average them.

## Visual design

**Identity: geometric tilework, restrained.** A single Islamic geometric motif (an eight-point
girih star grid) used *only* as a light watermark baked into element backgrounds — never as a
fixed viewport layer, per the AGENTS.md scroll-performance rule. Palette: warm white ground,
deep teal-green ink, brass accent used exclusively for takbirat counts. Arabic set in a system
Arabic stack at a larger optical size than the Latin text, right-aligned in its own column, never
as an image. The rak'ah map is drawn as two facing panels joined by a thin rule, echoing a
manuscript spread. No animation, no audio, no JavaScript; the one interactive element is a
CSS-only highlight tying a madhab legend colour to its cells.
