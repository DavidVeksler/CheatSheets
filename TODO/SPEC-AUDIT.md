# Spec Audit Guide — criteria every cheatsheet spec should address

A checklist for **writing or reviewing specs in this folder**, distilled from an audit of the
first 14 specs (2026-07-04). The existing template — target file, "why this topic," content
approach, research sources, visual design — is strong on *what goes on the page* and *what it
looks like*, and weak on *who arrives, via what query, and what they walk away able to do*.
This guide closes that loop. It is **not** a spec itself; when a spec and this guide conflict,
fix the spec.

Layering reminder: AGENTS.md owns the global quality bar (density floor, accuracy protocol,
metadata, a11y, print) and README.md here owns implementation rules. This guide owns **spec
completeness** — the decisions that belong at spec time because deferring them to build time
either loses information or makes the same collection-level call 14 separate times.

## Tier 1 — Required fields (add to every spec)

### 1. Search-intent targeting
Name the **primary query** the page competes for, 3–5 secondary queries, and whether the
searcher is in **crisis mode** (searches the symptom: "flight cancelled what to do") or
**research mode** (searches the topic: "amish technology"). Crisis-mode pages lead the title
and H1 with the crisis phrase; question-shaped H2s should match real queries.
*Model: the SEO note in `flight-disruption-playbook.md` — the only first-generation spec that
did this, and visibly the strongest spec because of it.*

### 2. Draft title / H1 / meta description
The name is a strategic decision, not an implementation detail. A great internal codename can
be a terrible search title ("Death Logistics" — nobody at a funeral home types that).
Deciding the title at spec time forces the search-intent thinking in §1. Include: `<title>`,
H1 (may differ), and a 150–200 char meta description draft.

### 3. Reader-outcome definition ("definition of working")
One sentence: what the reader should be **able to do** after the page that they couldn't
before. This is the acceptance test for *content*, complementing README Rule 3's definition
of *done* for structure. Examples: "take and reduce a real noon sight" (celestial), "decline
a voucher citing the DOT rule," "activate a rapid response team." If you can't state the
behavioral test, the page is probably a topic summary, not a cheatsheet.

### 4. Success metric
What does success look like for the *site*: organic entries on the target query, bookmark /
return-direct traffic ("save before your trip" pages), shares of the signature artifact,
print events, feeding popularity scores. One line is enough — it changes implementation
choices (e.g., a bookmark-first page invests in the printable card; a search-first page
invests in question H2s).

### 5. Volatile-facts register (staleness profile)
A short list: **which facts will rot, how fast, and what re-verification looks like** (e.g.,
FTC Funeral Rule status, federal estate exemption + sunset, DOT dashboard commitments, state
legality lists, IDB caps, SDR limits). This plugs directly into the weekly freshness-update
workflow instead of making each pass rediscover what's volatile. Rate the page overall:
STABLE (Amish, celestial, NNT) / SLOW-DRIFT (insurance, contractor) / VOLATILE (flight,
estate exemption sections).

### 6. Index category
Name the `$categoryMap` category in `index.php` the file belongs to — reuse an existing
label, or, if a batch of specs needs a new one (e.g., a "Life Admin" / "Consumer Defense"
category for the legal-consumer cluster), decide that **once at spec-batch time**, not
per-file at build time.

### 7. Reading-conditions statement
Device, stress level, lighting, age of the reader at the moment of use — because real
requirements fall out of it: "one-handed phone at 3 AM" ⇒ dark variant + big tap targets
(er-triage); "older readers under stress" ⇒ 18px+ base (hospital-stay); "printed in a ditch
bag" ⇒ print stylesheet mandatory (celestial, nuclear); "standing at gate B37 at 11 PM" ⇒
tel: links + single column (flight). Every page has an answer; state it and derive the
mobile/print/offline priorities explicitly.

## Tier 2 — Standardize (present in some specs; make consistent)

### 8. Cross-link map
List the spec's cluster: inbound and outbound links to existing and planned pages (medical
trio: er-triage ↔ hospital-stay ↔ nnt; legal-consumer: contract ↔ small-claims ↔ contractor ↔
estate ↔ death-logistics; prepper: celestial ↔ nuclear ↔ radio pages). README Rule 6 gives
examples; the spec should give *its own* map so the cluster ships coherent rather than being
retrofitted per SEO_PROMPT.txt.

### 9. og:image / shareable-artifact designation
Every spec names a signature element; also name **which element becomes the 1200×630 social
preview** and which block is the "screenshot this" artifact (they're often the same — the
Amish eight-questions block, the nuclear decay curve). AGENTS.md requires generating the
preview image anyway; deciding its subject at spec time keeps the signature element and the
share card aligned.

### 10. Geographic / jurisdiction scope
Declare it: US-only? State-variance handled how? What does a non-US reader get? (Flight
covers EU/UK/Canada explicitly; small-claims is implicitly US-only; death-logistics never
says.) One line prevents accidental half-coverage and sets the "verify for your state"
cadence per README Rule 4.

### 11. Quantified density targets
For each major table, the expected row count ("25–35 rows" — nnt; "4–5 case studies" —
amish). AGENTS.md sets the global floor (20+ entries); per-table numbers let README Rule 2's
outline review catch thinness at plan time instead of after a full build.

## Tier 3 — Already covered; don't duplicate into specs

- **Rationale / differentiation** — the "why this topic" paragraphs are consistently strong;
  keep that bar.
- **Unique visual pitch** — every spec names an aesthetic + signature element; the template's
  best feature.
- **Anti-goals & disclaimers** — README Rule 4 (global + per-domain).
- **Accuracy / verification protocol** — README Rule 1 + AGENTS.md accuracy gate.
- **Interactivity budget** — specs already cap this well ("one interactive element max").
- **Tech, a11y, print, metadata baselines** — AGENTS.md; never restate in a spec.

## How to use this guide

- **Writing a new spec:** include Tier 1 as explicit fields (a `## Targeting` block after
  "Why this topic" works well); fold Tier 2 into the content/design sections.
- **Auditing an existing spec:** score it against Tiers 1–2; anything missing is a spec
  defect to fix *before* the build starts — these decisions are cheap at spec time and
  expensive to retrofit.
- **At build time:** if a spec lacks a Tier 1 field, don't silently improvise it — derive it,
  write it back into the spec, and proceed. (Exception: specs are deleted when done per
  README; the derived targeting still governs the build.)
