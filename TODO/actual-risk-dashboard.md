# Spec: The Actual Risk Dashboard (micromorts)

**Target file:** `actual-risk-dashboard.html`

**Why this topic:** Humans systematically misjudge what kills them — media salience inverts actuarial reality (shark attacks vs. falls, terrorism vs. driving). No individual holds the aggregate statistics; an LLM can compile CDC/actuarial data into one bias-correcting page. Nothing like it exists in cheatsheet form, and dense data-dashboard pages are this site's top traffic performers.

## Targeting

- **Primary query:** "micromort" (definition + chart intent — modest volume, low competition, durable) — research mode: curiosity and argument-settling, often arriving from a share to resolve a "which is more dangerous" dispute. Secondary: "odds of dying by activity", "leading causes of death by age group", "skydiving vs driving risk", "what actually kills people vs what we fear", "microlife smoking per cigarette".
- **Title:** `The Actual Risk Dashboard: What Kills People, in Micromorts` (60 chars). **H1:** "The Actual Risk Dashboard — Everyday Risk in Micromorts". **Meta description:** "Everyday risk in micromorts on one dashboard: driving, skydiving, childbirth, anesthesia — plus what actually kills people at every age, and the gap between real risks and the ones in headlines." (~195 chars)
- **Reader outcome:** rank any two activities by actual mortality risk in seconds, and name the dominant controllable risk for their own age bracket (after 65 the answer is falls, not anything on the news).
- **Success metric:** the site's dashboard pages are its top performers — organic entries on the micromort long-tails, bookmark/return-direct traffic, shares of the log-scale bar chart; a strong popularity-score feeder.
- **Volatile-facts register — overall STABLE.** Micromort magnitudes barely move year to year; the register is "as of" hygiene (every figure already carries a year tag per the Research note): (a) CDC WISQARS / NSC Injury Facts — annual releases, refresh year tags once a year; (b) the fastest movers in the cause-of-death tables — drug poisoning and heat deaths — check direction each pass; (c) the alcohol J-curve dispute — literature drift, re-check the framing yearly; (d) the media-coverage study citations (Shen et al. / OWID) — static.
- **Index category:** Risk & Preparedness (new category, decided at spec-batch time; the builder adds it to index.php's `$categoryMap`).
- **Jurisdiction:** US mortality data (CDC/NSC) — state once; the *ratios* between activities generalize across rich countries, the absolute rates don't.
- **Reading conditions:** phone or desktop, zero stress, exploratory scrolling. Derived: the dark dashboard aesthetic is the native mode; the sortable table and heatmap must survive 375 px via overflow-x wrappers; print irrelevant (sane defaults suffice).
- **Cross-link map:** risk-literacy spine — outbound → `security-theater-audit.html` (its house-symbols entry cites this page's perception-gap section), `insurance-worth-it.html` (micromorts price fear; insurance prices it in dollars), `nnt-medical-interventions.html` (microlives are the NNT's chronic-risk sibling). Inbound ← the medical trio — `er-triage.html`, `hospital-stay-survival.html`, `nnt-medical-interventions.html` — plus `security-theater-audit.html`.

## Content approach

Core unit: the **micromort** (1-in-a-million chance of death) and its sibling the **microlife** (30 minutes of life expectancy gained/lost). Define both up front with a one-paragraph mental model.

Sections:

1. **Quick reference: everyday activities in micromorts.** One big sortable table (25–35 rows; the ~20 activities below are the floor) — activity, micromorts per unit (per day / per event / per 1000 miles), source year. Include: driving, motorcycling, cycling, walking, commercial flight, general aviation, skydiving, scuba, base jumping, marathon running, skiing, horse riding (compare with ecstasy use — the famous Nutt comparison), childbirth, general anesthesia, living (baseline ~22 micromorts/day for a middle-aged adult).
2. **What actually kills people, by age bracket.** For each decade of life (0–10 through 80+), the top 5 causes of death from CDC WISQARS/NCHS data (9 brackets × top-5 ≈ 45 populated cells). The punchline pattern: accidents → suicide/overdose → heart disease/cancer, and falls after 65.
3. **Perception vs. reality gap.** Table (10–14 paired causes): cause of death, annual US deaths, share of media coverage / Google search volume (cite the Shen et al. / Our World in Data media-coverage study). Sharks, terrorism, plane crashes, kidnapping on one side; falls, drug poisoning, heat, drowning in pools on the other.
4. **Chronic risks in microlives** (12–15 entries across harms and gains)**.** Smoking (per cigarette), alcohol (per drink, note the J-curve is now disputed), sedentary hours, red/processed meat, air pollution (PM2.5 per µg/m³), obesity per BMI point, loneliness. Include the positive side: exercise, sleep 7–8h, statins for high-risk groups.
5. **The levers ranked.** A "what should you actually do" decision list (8–12 ranked levers) ordered by expected micromorts saved: don't ride motorcycles, mind ladders and bathtubs after 60, drive less / drive bigger-newer, fix sleep apnea, etc. This is the editorial payoff — explicitly contrast with what people worry about.
6. **Common mistakes** section: relative vs. absolute risk headlines, base-rate neglect, dread risk vs. chronic risk, per-trip vs. per-mile framing tricks.

Research sources: CDC WISQARS, NSC Injury Facts, David Spiegelhalter's micromort/microlife papers, Our World in Data. All figures need year tags — most of this data is structurally stable but should carry "as of" years.

## Visual design

Dashboard aesthetic, distinct from the site's article-style pages: dark background, data-viz forward.

- **Hero element:** a horizontal **log-scale micromort bar chart** (pure CSS/inline SVG, no chart libraries) — activities plotted from 0.1 to 10,000 micromorts. Log scale is the whole point; label the axis honestly. **og:image / shareable artifact:** this chart, rendered as the 1200×630 social card, is also the page's "screenshot this" block.
- **Age-bracket section as a heatmap grid:** rows = causes, columns = age decades, cell color intensity = rank/rate. Reads like a "risk timeline of your life."
- **Perception-gap section as paired diverging bars:** deaths share (left, e.g. teal) vs. coverage share (right, e.g. red) per cause — the visual asymmetry IS the argument.
- Micromort values rendered in a monospace font with a small "µ☠" or similar unit badge for scannability.
- Keep interactivity light: table sorting and an optional age-selector that highlights the relevant column in the heatmap. No frameworks.
