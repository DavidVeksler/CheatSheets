# Spec: High Holiday services — Rosh Hashanah & Yom Kippur follow-along

**Target file:** `high-holiday-services-cheatsheet.html`
**Batch:** [niche-utility-batch-2026-08.md](niche-utility-batch-2026-08.md) (sheet 3 of 10).
**⚠️ Seasonal deadline: ship by 2026-09-01.** Rosh Hashanah 5787 begins at sundown on Friday
2026-09-11; Yom Kippur begins at sundown Sunday 2026-09-20. Published after the first week of
September, this page misses its entire annual demand window and waits until 2027.

## Why this topic

`shabbat-services-cheatsheet.html` is the proof: 2,762 words, 1,065 impressions, **2.63% CTR** —
one of the highest conversion rates on a site of 182 pages, because the reader is holding a
phone in a sanctuary trying to work out where everyone else is. High Holiday services are the
same task at ten times the difficulty and once a year: a different book (machzor, not siddur),
services that run four to six hours, an order most attendees only half-remember, and the largest
attendance of the Jewish year — including the people who attend *only* on these days and are
precisely the ones who cannot follow along.

Nothing in the corpus serves this. `judaism.html` is an overview; the Shabbat page covers Friday
evening only. The gap is the follow-along: what happens, in order, what it is called, when the
shofar sounds, what to do when you cannot read Hebrew, and how far through you actually are.

## Targeting

- **Primary query:** `rosh hashanah service order`
- **Secondary:** `yom kippur service order`, `what happens at rosh hashanah services`,
  `kol nidre service explained`, `when is the shofar blown`, `machzor explained`,
  `yizkor service`, `neilah`
- **Mode:** **crisis-mode, in-room.** The searcher is either about to walk in or already sitting
  down. Title and H1 lead with the follow-along promise, not with a topic label. Question-shaped
  H2s throughout.

## Draft title / H1 / meta

- `<title>`: `Rosh Hashanah & Yom Kippur Service Follow-Along Guide` (52 chars)
- **H1:** `High Holiday Services: What Happens and When`
- **Meta description (draft):**
  `Follow Rosh Hashanah and Yom Kippur services section by section: the order of each service, when the shofar sounds, what the machzor calls each part, and how long is left.` (169 chars)

## Reader outcome

A guest who cannot read Hebrew can sit through any High Holiday service, name the section
currently being chanted, know what is expected of them physically (stand, sit, bow, respond)
at each point, know when the shofar is coming, and estimate how much of the service remains.

## Success metric

Organic entries on the service-order family during the two-week seasonal window, and CTR at or
above the Shabbat page's 2.63%. Secondary and equally important: **return visits within the same
day** (someone reopening it between services) and print events. Judge this page in September, not
in April.

## Content approach

1. **Quick Reference: "where are we?"** (signature element) — a vertical service-progress rail
   for each of the five services (Erev Rosh Hashanah / Rosh Hashanah morning / Kol Nidre / Yom
   Kippur morning / Ne'ilah), each stop showing: Hebrew name, transliteration, English gloss,
   typical duration, what the congregation does, and an approximate "% through" marker. This is
   the artifact — a reader should be able to glance at their phone and find their place in under
   ten seconds.
2. **The five services, in order, one section each** — full flow at the level of named liturgical
   units: Ma'ariv/Shacharit/Musaf structure, the Amidah and its High Holiday insertions, Avinu
   Malkeinu, Unetaneh Tokef, the Torah and Haftarah readings for each day (name the actual
   readings), Tashlich, Kol Nidre's three repetitions, Yizkor, the Avodah service, Selichot and
   the Thirteen Attributes, Ne'ilah and the closing shofar blast.
3. **The shofar section** — the four sounds (tekiah, shevarim, teruah, tekiah gedolah) with what
   each sounds like, the standard sequence and total count, when in the service it happens, and
   the rule about Shabbat. **Note for 2026: the first day of Rosh Hashanah falls on Shabbat, so
   the shofar is not sounded that day** — verify this against a calendar before publishing, and
   write the page so the rule is stated generally with the current year's application dated.
4. **Denominational variance table** — Orthodox / Conservative / Reform / Reconstructionist /
   Chabad, columns for: which machzor is typical, service length, how much is in English, whether
   there is instrumental music, seating, whether the second day is observed, Musaf treatment. One
   honest row per movement; no editorializing about which is correct.
5. **What to do with your body** — standing, sitting, bowing, the full prostration in Aleinu and
   the Avodah, when to respond aloud, when the ark is open, and the "follow the row in front of
   you" fallback. This is the section guests actually need and nobody writes.
6. **Hebrew you will hear, with transliteration** — the responses and refrains a guest can join:
   Shema, Barchu, Kedushah responses, Avinu Malkeinu refrain, the Al Chet confession structure,
   L'shana tovah greeting forms. Hebrew, transliteration, translation, three columns.
7. **Fasting and practicalities (Yom Kippur)** — the fast window (sundown to nightfall, ~25
   hours), who is exempt under standard practice, the pre-fast and break-fast meals, medication
   guidance stated as "ask your rabbi and your doctor" once, and the leather-shoe and washing
   customs. **Decision-support framing only** — no medical advice, per README Rule 4.
8. **Machzor navigation** — how the common machzorim are laid out (Artscroll, Lev Shalem, Mishkan
   HaNefesh, Koren), page-number conventions, what the italic instructions mean, and how to find
   your place when the announced page number does not match your book.
9. **The calendar** — dates for the current and next several years, with the standard sundown-to-
   nightfall convention stated once. Table with a visible "generated on" date.
10. **Common mistakes / guest questions** (mandatory): arriving on time for a service that
    started an hour earlier; expecting Rosh Hashanah morning to end before mid-afternoon; missing
    Tashlich because it is not in the building; assuming Kol Nidre is the whole evening; leaving
    before Ne'ilah, which is the point; treating Yizkor as optional to sit through when family
    custom says otherwise.
11. **Related sheets** footer per the cross-link map.

## Volatile-facts register

**Overall: STABLE liturgy, VOLATILE calendar.**
- Dates: recompute annually. The dated calendar table and any "this year" statement (including
  the 2026 shofar-on-Shabbat note) are the freshness targets.
- Liturgy, service order, shofar sequence, denominational patterns: stable for generations.
- Machzor editions: slow-drift; new editions appear every decade or so.
Freshness routine: one check each August, before the season.

## Index category

`Philosophy & Religion`.

## Reading conditions

**Phone, in a sanctuary, screen dimmed, possibly self-conscious about using it at all.** Every
design consequence flows from that: a **dark theme by default is wrong** (a bright screen in a
dim room is the conspicuous failure) — ship a low-luminance, low-contrast-glare variant and
respect `prefers-color-scheme`; no animation; no sound; nothing that could autoplay. Large tap
targets for one-handed scrolling. A **print stylesheet is mandatory** for observant readers who
will not carry a phone on the day: the progress rail plus the Hebrew/transliteration responses
must print to two clean sheets. Say plainly near the top that the page prints, and why.

## Cross-link map

- **Internal outbound:** `shabbat-services-cheatsheet.html` (the weekly sibling — link both
  ways), `judaism.html` (the background overview), `etz-chaim-tree-of-life.html`,
  `comparative-religion-map.html`.
- **Reciprocal inbound:** a seasonal line in `shabbat-services-cheatsheet.html` and `judaism.html`.
- **Cross-domain:** check `~/Projects/seo-crosslinking/` before adding any external deep link.
- **External outbound:** Sefaria for liturgical texts; Hebcal for dates. Nothing commercial.

## og:image / shareable artifact

The service-progress rail for Yom Kippur morning — the longest and most disorienting service,
and the most useful screenshot. 1200×630, light variant.

## Jurisdiction scope

Not jurisdictional but **denominational**: state once, near the top, that the page describes the
common North American pattern across the four major movements and that any individual
congregation varies — with the "follow your congregation's machzor and announcements" line stated
once, not per section.

## Density targets

Progress rail: 5 services × ≥ 8 stops each (≥ 40 stops). Denominational table 5 rows × 7 columns.
Hebrew/transliteration table ≥ 12 responses. Shofar sequence ≥ 4 sounds with counts. Calendar
≥ 5 years. Guest questions ≥ 8. Torah/Haftarah readings named for all five services.

## Research sources (verify against these, per Rule 1)

Sefaria (liturgical text and readings); Hebcal (dates, and whether the shofar is sounded in a
given year); the published machzorim themselves for page-layout conventions (Artscroll, Mahzor
Lev Shalem, Mishkan HaNefesh, Koren); movement bodies — OU, USCJ, URJ, Reconstructing Judaism —
for denominational practice statements rather than a third-party summary. Where movements
genuinely differ, cite each one's own source.

## Visual design

**Identity: the machzor itself.** Cream page stock, a warm ink-brown text colour, a single
pomegranate-red accent used only for the shofar markers, generous margins, and a serif face with
real Hebrew support for the Hebrew column (system Hebrew stack; no web font). The progress rail
is drawn as a ruled margin column, echoing a printed prayer book's structural marks, with the
shofar stops marked by a small filled glyph. Restraint is the design: this page must look like it
belongs in the room. Zero JavaScript, zero animation. The one interactive element permitted is a
CSS-only `<details name="service">` accordion so only one service is expanded at a time — which
is also the correct behaviour for someone scrolling one-handed.
