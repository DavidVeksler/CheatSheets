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
   stamp to `TODAY` **because you actually reviewed the content this run**. Never bump the date
   without reviewing.
6. **A stamp is a claim about verification, so an unverified run must not stamp.** If you could
   not reach a primary source for this file's volatile facts — the search budget ran out, the
   sources were unreachable, the tool errored — then **leave every existing date exactly as you
   found it** and report the file as unverified. Do not bump `dateModified`, do not bump the
   visible "Last verified" line, and do not add one. A stale-but-honest date is recoverable; a
   fresh date on unverified content is a lie the next run will trust.
7. **Never overwrite a real provenance note with a failure message.** If a file carries a note
   recording what was checked and when, and you could not verify it this run, leave the note
   alone. Put "could not verify" in your **report**, never in the page.

   Rules 6 and 7 are not hypothetical. On 2026-07-26 the session's 200-call web-search budget was
   exhausted 9 batches in; the remaining Workers kept "succeeding" while doing zero verification,
   and five files had their stamps bumped with nothing checked behind them — two of which
   overwrote a genuine provenance note with "could not verify". All five had to be reverted.
   Silent false provenance is a worse outcome than an incomplete run, so when in doubt, stamp
   nothing and say so.

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

**Do not maintain the dated set by hand. Compute it:**

```sh
python scripts/freshness_scan.py            # this run's batch, oldest-first
python scripts/freshness_scan.py --all      # full ranking, no batch cut
python scripts/freshness_scan.py --json     # machine-readable
```

The script is read-only: it never edits a file, never hits the network, and never bumps a date.
It ranks every root `*.html` by the age of its in-file `dateModified` (falling back to a visible
"Last verified" line, then to the file's last git commit date), drops anything refreshed inside
`--min-age-days` (30 by default), holds back the §7 evergreen topics, and cuts the result to a
batch that fits the search budget.

**This replaced a hand-typed list, because the list drifted into being wrong.** It named ~43
files when the repo held 173, and it omitted the entire AI-models / AI-datacenter cluster — the
fastest-drifting content in the repo. A list of files living in prose is exactly the thing that
should be computed.

**The budget is a hard constraint, not a guideline.** At §2's ceiling of ~15 searches per Worker
against a 200-call session cap (`CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION`, shared across the
Selector *and* every Worker), only about **12 files** can be dispatched per run. The script
refuses to emit a larger plan rather than let the late Workers starve and stamp unverified files
(see §4.6). If a bigger batch is genuinely wanted, raise the cap first, then pass `--limit`.

**Known cadence problem, worth a decision:** as of 2026-08-08 the corpus sits in near-lockstep
around 25 days old, so once it crosses the 30-day threshold roughly 164 files become eligible
against a 12-file batch — about 14 weeks to complete a single pass. Either raise the search cap,
run the job more often than weekly, or accept that the selector is a staleness *triage* rather
than a full sweep. Do not "solve" it by dispatching more Workers than the budget supports.

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
