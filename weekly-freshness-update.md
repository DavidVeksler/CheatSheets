# Weekly Cheatsheet Freshness Update — Agent Instructions

This document is the **worker-agent instruction set** for the recurring job that keeps the
time-sensitive cheatsheets in this repo accurate. It is written to be handed, verbatim, to a
**light model (Claude Haiku)** that updates **exactly one cheatsheet per run**.

The authoritative quality bar for the repo lives in [`AGENTS.md`](AGENTS.md) (see the
*Accuracy & Freshness Protocol*). This document is the operational procedure that enforces it
on a schedule. If the two ever conflict, `AGENTS.md` wins.

---

## 1. How the weekly job is structured

There are two roles. Keep them separate.

1. **Selector (runs once per week).** Decides *which* files to refresh this week (see §9), then
   dispatches one **Worker** per file.
2. **Worker (one per file, this is the Haiku agent these instructions are for).** Refreshes a
   single cheatsheet's dated content and freshness stamps, then reports.

**Concurrency rule (learned the hard way):** dispatch Workers in **small batches (≤ 4 at a time)**.
Each Worker must do its **own** web research and **must NOT spawn sub-agents** — fanning out
dozens of agents that each spawn their own helpers will trip API rate limits and leave files
half-edited.

---

## 2. Worker role, model, and execution constraints

- **You update ONE file.** You are given its path. Do not touch any other file.
- **Model:** Claude Haiku (light). Favor following this checklist literally over open-ended
  reasoning.
- **Do your own research** with `WebSearch` / `WebFetch`. **Do NOT** use the Agent/Task tool or
  spawn sub-agents.
- **Budget:** aim for **~8–15 focused web searches**. Stop when the volatile facts are checked.
- **Tools you use:** `Read`, `WebSearch`, `WebFetch`, `Edit`. Nothing else is required.

---

## 3. Inputs

- `FILE` — absolute path to the one cheatsheet to update.
- `TODAY` — today's date in `YYYY-MM-DD` (e.g. `2026-06-21`). Also derive `MONTH YYYY`
  (e.g. `June 2026`) and `YEAR` (e.g. `2026`) from it.

If `TODAY` is not supplied, get the current date before doing anything else.

---

## 4. Golden rules (do not violate)

1. **Verify, never recall.** Every version number, price, date, model name, spec, benchmark,
   funding figure, count, or "latest/current" claim you change MUST be confirmed against a
   **primary source** (official vendor site, official docs, the spec, the org's own newsroom).
   Your training data is stale — assume it is wrong about anything recent.
2. **Never fabricate.** If you cannot confirm a specific from a primary source: **leave the
   existing value if it's still plausible, or soften/remove it — and flag it in your report.**
   A plausible-looking but unverified number is worse than no number.
3. **Be surgical and conservative.** Preserve the page's structure, tone, voice, layout, HTML
   classes, and formatting. Change only what is genuinely stale, wrong, or newly important.
   Do **not** rewrite sections, restructure, or redesign.
4. **One file only.** Never create or modify any other file.
5. **Structured data must match visible content.** Only set a `dateModified` / "Last verified"
   stamp to `TODAY` **because you actually reviewed the content this run** (which you always do).
   Never bump the date without reviewing.

---

## 5. Procedure

1. **Read the entire `FILE` first.** Note what it covers and whether a prior run left partial
   edits (see §8).
2. **Make a volatile-fact list** using the checklist in §6. If, after reading, the page is
   essentially **evergreen** (see §7) with nothing materially stale, that's fine — make only the
   freshness-stamp update (§8) and say so in your report.
3. **Verify each volatile fact** with focused web searches against primary sources.
4. **Edit in place** with the `Edit` tool, matching the surrounding HTML/style exactly. Apply
   Golden Rules §4.1–§4.2 to every change.
5. **Update freshness stamps** per §8.
6. **Run the self-check** in §10.
7. **Write the report** per §11.

---

## 6. Volatile-fact checklist (what to hunt for)

Look for, and verify, any of these:

- **Software/versions:** language/runtime/framework/library versions, "new in vX", current
  stable/LTS, EOL dates, deprecations, licensing changes (e.g. open-source → commercial).
- **AI models:** current flagship model names & versions, context windows, pricing, benchmark
  scores, who leads on what.
- **Products & hardware:** current lineup/trims, specs, MSRP/prices, discontinued models,
  successor models, shipping status.
- **Companies & people:** funding rounds, valuations, leadership/role changes, mergers,
  shutdowns, renames.
- **Markets & rates:** prices, interest/mortgage rates, market-share figures, cost-per-unit.
  Tag every such figure with `as of MONTH YYYY` and a source. Do **not** embed a volatile spot
  price (e.g. live BTC price) — make it relative or omit it.
- **Regulation/standards:** law/rule status (proposed/in-force/withdrawn), standards bodies'
  document numbers and statuses, official guidance dates.
- **Timelines:** predictions whose dates have lapsed; "recent developments" sections; the most
  recent entry in any timeline.
- **"Latest / newest / current / as of <date>" phrases** anywhere on the page.

For each: confirm → if changed, edit to the verified current value + (where the page uses them)
an `as of MONTH YYYY` tag; if unverifiable, leave/soften and flag.

---

## 7. Evergreen content — do NOT churn

Concepts, definitions, theory, history, step-by-step technique, glossaries, OPSEC/safety
principles, anatomy, religion, philosophy, mathematics, and historical documents are **timeless**.
Don't reword them. A cheatsheet can be 90% evergreen with a small dated section — touch only the
dated section.

Whole topics that are essentially evergreen (expect a freshness-stamp-only update): religion,
philosophy, anatomy, martial-arts technique, cooking, historical timelines of the past, the
Bitcoin whitepaper.

---

## 8. Freshness-stamp procedure (always do this)

Update whichever of these **exist** in the file; **add only the visible "Last verified" line** if
missing. Different files use different mechanisms — check for each:

- **Visible title/subtitle/header date** (e.g. `Updated May 2026`, `(May 2026 Update)`,
  `2025 edition`) → `MONTH YYYY`.
- **`<meta name="description">`, `keywords`, `og:*`, `twitter:*`** date mentions → `MONTH YYYY`.
- **JSON-LD** `"dateModified"` (inside a `<script type="application/ld+json">` block) →
  `TODAY`. **Leave `datePublished` unchanged.**
- **Microdata** `<meta itemprop="dateModified" ...>` → `TODAY`.
- **`<meta property="article:modified_time" ...>`** → `TODAY` (ISO).
- **Visible footer "Last verified:" line** → `Last verified: TODAY`. **If there is none, add one**
  in the footer, matching the site's small/muted footer style, e.g.:
  `<p class="mb-2"><strong>Last verified: TODAY.</strong> <short note on what was checked.></p>`
- **Footer copyright** `© <year>` → `© YEAR`.

**Idempotency / partial-edit handling:** a prior run may have already changed some of these. After
editing, ensure there is **exactly one** "Last verified" line and **exactly one** `dateModified`
value. Do not duplicate the footer line. If you find a `dateModified` already set to `TODAY` but the
content was never reviewed, review it now so the stamp is truthful.

---

## 9. Selector: which files to refresh each week

(Selector role — not the Worker. Included here so the spec is complete.)

Pick the working set by **staleness × volatility**:

- **Process** files whose topics drift (AI, software/versions, crypto, cloud, hardware/products,
  space, markets, defense, regulation) — prioritize those with the oldest `dateModified`.
- **Skip** evergreen topics (§7) except for an occasional light freshness-stamp pass.
- **Skip** anything updated in the last **~30 days** (already fresh).
- Rotate so every dated file is revisited within a few weeks rather than all at once.

**Known dated set in this repo** (verify against current files; the repo grows):

> AI/ML: `ai-frontier`, `ai-progress-dashboard`, `ai-risk-timeline`, `agi-development-guide`,
> `airisk`, `aisafety`, `p-doom-calculator`, `prompt-builder`, `google-ai-studio-guide`,
> `humanoid-robots`.
> Tech/software: `dotnet-cheatsheet`, `clean-architecture-dotnet`, `postgresql`, `databases`,
> `azure-devops`, `aws-vs-azure`, `modern-devops-pipelines`, `python-for-architects`,
> `javascript-for-architects`, `post-quantum-cryptography`, `git-scm`, `versioncontrol`,
> `compression-algorithms`.
> Products/hardware/markets: `tesla-products`, `orbital-rockets-comparison`, `boom-supersonic`,
> `automotive-innovation-timeline`, `bitcoin-exchanges-cards`, `bitcoin-self-custody-guide`,
> `bitcoin-wallet`, `modern-firearms`, `operator-loadouts`, `future-of-warfare-technology`,
> `engineering-materials-future`, `geoengineering-approaches`, `housing-comparison`,
> `home-maintenance-guide`, `handgun-calibers`, `engineering-metals-selection`,
> `ham-radio-technician`, `veterinary-diagnostics`, `privacy-data-broker-opt-out`,
> `lifestyle-calculator`.

A robust automated selector can rank by `dateModified` age: `git log -1 --format=%cs -- <file>`
or the in-file `dateModified`, oldest first.

---

## 10. Self-check before finishing

- [ ] Every changed fact was confirmed against a primary source (or left + flagged).
- [ ] No fabricated specifics.
- [ ] Edits are surgical; structure/tone/classes intact;
- [ ] Exactly one "Last verified" line (= `TODAY`); exactly one `dateModified` (= `TODAY`);
      `datePublished` untouched; copyright = `YEAR`.
- [ ] Only `FILE` was modified.
- [ ] The page's structured-data date now truthfully matches reviewed content.

---

## 11. Report format (what the Worker returns)

Return tight Markdown — this is for the job log, not an end user:

```
### <filename>
**Changes made:** bullets, each `old → new` + source domain. ("None — content current" is valid.)
**Verified still-current:** notable facts checked that didn't need changing.
**Unverified / flagged:** anything you could not confirm (with why).
**Freshness stamps:** which stamps you updated.
```

---

## 12. Notes for whoever wires up the schedule

- This file is the **Worker prompt body**. Prepend the two inputs (§3) and the target file path.
- Keep batches ≤ 4 concurrent Workers; no sub-agent spawning (§1).
- Commit policy follows the repo norm: one logical commit, by explicit file path, never staging
  `.claude/` or unrelated changes. Decide per your automation whether to auto-commit or open for
  review. Do not push unless intended.
- Last updated: 2026-06-21.
