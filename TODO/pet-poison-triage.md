# Spec: Pet poison triage — what dose is actually dangerous

**Target file:** `pet-poison-triage.html`
**Batch:** [niche-utility-batch-2026-08.md](niche-utility-batch-2026-08.md) (sheet 5 of 10).

## Why this topic

`veterinary-diagnostics.html` is one of the site's best-converting pages by CTR class (306
impressions, 2.61%, and 9.24% in an earlier window) on a topic almost nobody writes densely. It
serves the calm mode: understanding a test result. The crisis-mode sibling is missing entirely,
and crisis mode is where the volume is — the searcher whose dog just ate something and who is
deciding, right now, whether this is a 2 a.m. emergency-vet drive or a night of watching.

The field is saturated with **single-toxin chocolate calculators** — a dozen of them, all doing
the same theobromine arithmetic. What none of them do is the thing the panicking owner actually
needs: **one page covering the toxins that are actually eaten, ranked by how fast they kill,
with the threshold expressed per kilogram of the animal in front of them, and an explicit
ER-or-not verdict per row.** Xylitol and lilies matter far more than chocolate and get a
fraction of the coverage, because chocolate gets the search traffic. Ranking by danger rather
than by search volume is the page's whole claim.

This must be built as **decision support that routes to a professional**, never as treatment
advice — see the anti-goals below, which are unusually strict for this page.

## Targeting

- **Primary query:** `my dog ate chocolate how much is too much`
- **Secondary:** `xylitol dog toxic dose`, `how many grapes are toxic to dogs`,
  `cat ate lily what to do`, `ibuprofen toxic dose dog`, `is my dog poisoned`,
  `pet poison helpline`, `dog ate weed edible`
- **Mode:** **pure crisis.** Two-thirds of arrivals are on a phone, at night, one-handed, scared.
  The first screen must resolve the emergency question before any explanation. Title and H1 lead
  with the crisis phrase.

## Draft title / H1 / meta

- `<title>`: `Pet Poison Triage: Toxic Doses by Weight, ER or Not` (50 chars)
- **H1:** `Pet Poison Triage: What Dose Is Actually Dangerous`
- **Meta description (draft):**
  `Dog and cat poisoning thresholds by body weight: chocolate, xylitol, grapes, ibuprofen, lilies, rodenticide, antifreeze and THC, and the dose that makes it an emergency.` (167 chars)

## Reader outcome

Within sixty seconds of landing, the reader can state: the substance, the amount relative to
their animal's weight, which of four bands that falls in (watch / call / go now / already an
emergency regardless of dose), and the phone number they should be dialling — and they know
whether inducing vomiting would help or kill.

## Success metric

Organic entries on the crisis-query family, and **time-to-first-interaction**, not time on page:
success is a reader who gets an answer and leaves to phone a vet. Secondary: this is the site's
strongest candidate for AI-answer citation, because the per-kilogram thresholds are exactly what
assistants hedge on — track crawler fetches on this URL as a KPI alongside clicks.

## Content approach

**The disclaimer appears exactly once, prominently, above the fold** — "this page helps you
decide how urgently to call; it does not replace the call" — with the poison-control and
emergency numbers in the same block. Not repeated per section (README Rule 4).

1. **The 60-second triage block** (signature element, above everything) — three inputs stated in
   plain text (species, weight, what they ate), then the four-band verdict scale rendered as a
   single vertical stack: **CALL NOW REGARDLESS** / **CALL, HAVE THE NUMBERS READY** / **WATCH,
   WITH THESE SIGNS** / **LOW RISK AT THIS DOSE**. Tap-through anchors straight to the substance
   rows. The helpline numbers are a tel: link at the top of this block, not buried in a footer.
2. **The "call now regardless of dose" list** — the substances where dose arithmetic wastes time:
   lilies in cats (any part, including pollen and vase water), antifreeze/ethylene glycol,
   anticoagulant and bromethalin rodenticides, xylitol, permethrin in cats, amphetamine and ADHD
   medications, ivermectin in herding breeds. Short, unmissable, first.
3. **The threshold table** (the page's core) — one row per toxin, ~25 rows, columns: substance,
   species affected, the toxic dose **per kg body weight** with the concentration assumption
   stated, what that means in everyday units (squares of baking chocolate, pieces of gum,
   200 mg tablets), onset time, first signs, and the verdict band. *All figures are anchors —
   verify every one against the sources below.* Anchor examples the build must confirm:
   theobromine mild effects ≈ 20 mg/kg, cardiac ≈ 40–60 mg/kg, seizures ≈ 60+ mg/kg; xylitol
   hypoglycaemia ≈ 0.1 g/kg and hepatic failure ≈ 0.5 g/kg; ibuprofen GI ≈ 50 mg/kg upward;
   acetaminophen in cats dangerous at very low doses; grapes/raisins idiosyncratic with no
   established safe dose.
4. **Chocolate, done properly** — the theobromine-per-gram table by chocolate type (white, milk,
   semi-sweet, dark by cocoa percentage, baking, cocoa powder, cocoa mulch) and a worked example
   that arrives at a real number for a real dog ("a 12 kg beagle, 100 g of 70% dark") and lands in
   a band. **A worked example, not a JavaScript calculator** — the interactivity budget goes to
   one optional client-side calculator at most, and it must degrade to the table with JS off.
5. **The idiosyncratic ones** — grapes and raisins (tartaric acid hypothesis, no dose-response),
   macadamias, onions and garlic by weight percentage, and why "no established safe dose" is a
   reason to call rather than a reason to relax.
6. **Cannabis and edibles** — THC dose bands, the chocolate-plus-THC compound case, why owners
   under-report and why the vet does not care about legality. Explicit and non-judgmental; this
   is a rising fraction of real cases.
7. **Human medications** — the top offenders by call volume with their thresholds: NSAIDs,
   acetaminophen, ADHD stimulants, antidepressants (SSRI and the serotonin-syndrome picture),
   sleep aids, blood-pressure medications. One table.
8. **Household and garden** — rodenticides by active ingredient (the class determines the
   treatment and the timeline, so name them), antifreeze, batteries, silica gel versus desiccant
   confusion, compost/mycotoxins, and a short high-risk plant list for cats and dogs separately.
9. **What NOT to do** (mandatory, and the most valuable section) — when inducing vomiting is
   actively harmful (caustics, petroleum distillates, already symptomatic, brachycephalic
   breeds); hydrogen peroxide dosing myths; never induce vomiting in a cat at home; milk, bread,
   and activated-charcoal folklore; "wait and see" with xylitol and antifreeze, where the delay
   is the cause of death.
10. **What the vet will ask** — the checklist to have ready before dialling: species, breed,
    weight, exact product and packaging, estimated amount, time since ingestion, current signs,
    existing conditions and medications. Screenshot-sized.
11. **Cost and access reality** — one honest paragraph: what poison-control consultation fees and
    emergency visits typically run, that the helpline case number saves duplicated work at the
    clinic, and that cost anxiety is the main reason owners wait too long.
12. **Related sheets** footer per the cross-link map.

## Anti-goals (per README Rule 4, medical domain)

Decision-support framing only. **No treatment protocols, no home antidotes, no at-home dosing of
anything** — including the peroxide dose that other sites publish; state that it is a veterinary
decision and why. No brand recommendations. No "consult your vet" padding beyond the single
prominent disclaimer. No fear-marketing of pet insurance.

## Volatile-facts register

**Overall: SLOW-DRIFT.**
- Toxic thresholds and toxicology: very stable — these are the durable core.
- Helpline phone numbers and consultation fees: verify annually; a dead number on a crisis page
  is the worst possible defect. **This is the page's primary freshness target.**
- Rodenticide active ingredients available at retail: shifts with regulation (the EPA
  second-generation anticoagulant restrictions changed what is on shelves) — verify annually.
- Cannabis prevalence framing: drifts with legalization.

## Index category

`Health & Fitness` (same as `veterinary-diagnostics.html`).

## Reading conditions

**2 a.m., phone, one hand, animal in the other, adrenaline, possibly crying.** This drives
everything: the verdict block above the fold with nothing before it, `tel:` links that dial
directly, minimum 18 px base text, very large touch targets, dark-mode-first for a dark house but
correct in both, no modal, no cookie banner, no newsletter interruption of any kind on this page.
It must render usefully on a slow connection — the triage block must be in the first paint. Print
stylesheet: the "have this ready for the vet" checklist and the helpline numbers on one sheet
someone can stick inside a cupboard door before they ever need it.

## Cross-link map

- **Internal outbound:** `veterinary-diagnostics.html` (the calm-mode sibling — link both ways),
  `er-triage.html` (the human analogue, same design problem solved for people),
  `actual-risk-dashboard.html`, `home-maintenance-guide.html` (where the household chemicals live).
- **Reciprocal inbound:** a prominent crisis link from `veterinary-diagnostics.html`.
- **External outbound:** ASPCA Animal Poison Control and Pet Poison Helpline (numbers, and their
  toxin pages), Merck Veterinary Manual. No retailer or insurance links.

## og:image / shareable artifact

The four-band verdict scale with two or three example rows, dark theme, 1200×630. It is also the
screenshot-this artifact — and the thing most likely to be shared into a group chat at the moment
it is needed.

## Jurisdiction scope

US-first for the helpline numbers and retail product landscape, stated once, with a short block
of equivalent national poison lines for Canada, UK and Australia so a non-US reader is not left
dialling a number that will not answer. Toxicology itself is universal.

## Density targets

Threshold table ≥ 25 substances × 7 columns; chocolate-type table ≥ 8 rows; human-medication table
≥ 10 rows; rodenticide classes ≥ 4; plant list ≥ 15 (split by species); "what not to do" ≥ 8
items; vet-call checklist ≥ 8 fields. One fully worked chocolate example ending in a real verdict.

## Research sources (verify against these, per Rule 1)

Merck Veterinary Manual (toxicology sections) as the spine; ASPCA APCC and Pet Poison Helpline
toxin monographs; peer-reviewed veterinary toxicology literature for the per-kg thresholds
(especially the grape/raisin tartaric-acid work and xylitol hepatotoxicity); EPA rodenticide
registration documents for what is actually on retail shelves; FDA CVM advisories. Never take a
threshold from a calculator site or from this spec — every number in the table is verified against
a veterinary-toxicology primary source or it does not ship.

## Visual design

**Identity: emergency-department triage tag.** The physical paper triage tag: heavy card stock
texture baked into the block backgrounds, a serial-numbered header strip, and the four bands
rendered as tear-off tag colours — but with the site's honesty constraint: bands are labelled in
words first and colour second, so the page works for colour-blind readers and in greyscale print.
Palette: near-black ground, bone-white card, one alarm-amber and one clinical-blue accent; a
condensed grotesque for band labels, tabular figures for every dose. The triage block is built
first and best: it is the page. Everything below it is quieter — plain tables, no ornament.
Motion gated behind `prefers-reduced-motion`, and in practice there should be none.
