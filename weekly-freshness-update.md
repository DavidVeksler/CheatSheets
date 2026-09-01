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
   single cheatsheet's dated content, then reports.

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
- **You never touch `refresh-status.json`.** Workers in the same batch run concurrently
  (§1); a shared JSON file edited by several parallel processes is exactly how updates get
  silently dropped. Recording the outcome is the Selector's job, done once, after every Worker
  in the run has reported back (§9). Your only obligation is to report accurately (§11).

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
5. **No visible date stamp, no JSON-LD `dateModified`, on the page — ever.** Cheatsheets used to
   carry a visible "Last verified: DATE" line and a matching JSON-LD field. That turned into
   makework: bumping a date is easy to do without actually checking anything, and the pages
   accumulated stamps nobody could vouch for. Freshness is now tracked externally in
   `refresh-status.json`, written once per run by the **Selector** (§9), never by a Worker. Do not
   add, edit, or bump any date/stamp in the page itself, and do not touch `refresh-status.json`.
6. **An unverified run reports as unverified — full stop.** If you could not reach a primary
   source for this file's volatile facts — the search budget ran out, the sources were
   unreachable, the tool errored — say so plainly in your report (§11). There is no page stamp to
   protect and nothing to leave alone; the only failure mode left is reporting a review that
   didn't happen.
7. **Never overwrite a real provenance note with a failure message.** If a file carries a
   standalone sentence recording what was checked and when (e.g. "Metadata, CDN dependencies, and
   internal links reviewed against repository audit standards."), and you could not verify it
   this run, leave the sentence alone. Put "could not verify" in your **report**, never in the
   page.

   This section used to be about protecting a page-visible date stamp from false bumps: on
   2026-07-26 the session's 200-call web-search budget was exhausted 9 batches in, and the
   remaining Workers kept "succeeding" while doing zero verification — five files had their
   stamps bumped with nothing checked behind them, two of which overwrote a genuine provenance
   note with "could not verify". The underlying lesson (silent false provenance is worse than an
   incomplete run) is why the stamp was removed from the page entirely rather than just patched:
   a claim that lives in the page is a claim a rushed run can fake, and the same makework pattern
   showed up week over week as the routine's only real output. `refresh-status.json`, written once
   by a single process after every report is in, closes that hole structurally instead of by
   discipline.

---

## 5. Procedure

1. **Read the entire `FILE` first.** Note what it covers and whether a prior run left partial
   edits.
2. **Make a volatile-fact list** using the checklist in §6. If, after reading, the page is
   essentially **evergreen** (see §7) with nothing materially stale, that's fine — say so in your
   report; there is no page stamp to update.
3. **Verify each volatile fact** with focused web searches against primary sources.
4. **Edit in place** with the `Edit` tool, matching the surrounding HTML/style exactly. Apply
   Golden Rules §4.1–§4.2 to every change.
5. **Run the self-check** in §10.
6. **Write the report** per §11.

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

Whole topics that are essentially evergreen (expect a "nothing material changed" report):
religion, philosophy, anatomy, martial-arts technique, cooking, historical timelines of the past,
the Bitcoin whitepaper.

---

## 8. No page stamps (read this if you're used to the old procedure)

Older revisions of this doc had a Worker add or bump a visible "Last verified" line and a JSON-LD
`dateModified` field on every run. That's gone. Cheatsheets carry no visible review-date stamp and
no `dateModified` at all now — freshness lives in `refresh-status.json`, updated once per run by
the Selector, never by a Worker (§2, §9).

If you happen to notice a leftover visible "Last verified" / "Last updated" line or a
`dateModified` field on the page you're editing (a straggler the migration missed), remove it as
part of your edit and note it in your report — but that's opportunistic cleanup, not your primary
job, and it's not something to go hunting for across the rest of the page if it isn't already
in your way.

---

## 9. Selector: which files to refresh, and recording the outcome

(Selector role — not the Worker. Included here so the spec is complete.)

### 9a. Picking the working set

Pick the working set by **staleness × volatility**:

- **Process** files whose topics drift (AI, software/versions, crypto, cloud, hardware/products,
  space, markets, defense, regulation) — prioritize those with the oldest recorded review.
- **Skip** evergreen topics (§7) except for an occasional light check-in.
- **Skip** anything reviewed in the last **~30 days** (already fresh).
- Rotate so every dated file is revisited within a few weeks rather than all at once.

**Do not maintain the dated set by hand. Compute it:**

```sh
python scripts/freshness_scan.py            # this run's batch, oldest-first
python scripts/freshness_scan.py --all      # full ranking, no batch cut
python scripts/freshness_scan.py --json     # machine-readable
```

The script is read-only: it never edits a file, never hits the network, and never bumps a date.
It ranks every root `*.html` by the age of its `refresh-status.json` `last_reviewed` entry
(falling back to the file's last git commit date for files with no entry yet), drops anything
refreshed inside `--min-age-days` (30 by default), holds back the §7 evergreen topics, and cuts
the result to a batch that fits the search budget.

### 9b. Recording the outcome (after every Worker in the run has reported)

For each file a Worker actually reviewed this run — i.e. its report's **Review status** (§11) is
`verified` or `partially verified`, not `unverified` — run:

```sh
python scripts/update_refresh_status.py FILE.html --date TODAY --note "<one-line summary>"
```

Take the note from the Worker's **Changes made** / **Verified still-current** summary. Run this
**once per file, from the Selector, after Workers have finished** — never dispatch it to a Worker
and never let two processes write `refresh-status.json` concurrently, since the whole point of
moving this out of the page was to make it a single-writer operation instead of a race. Do not
call it for files reported `unverified`; their existing `last_reviewed` date stands (an
unreviewed file staying visibly stale is correct — it's what makes the next Selector run pick it
up again).

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
- [ ] Edits are surgical; structure/tone/classes intact.
- [ ] You did not add, edit, or bump any visible date stamp or JSON-LD `dateModified` on the page.
- [ ] You did not touch `refresh-status.json`.
- [ ] Only `FILE` was modified.
- [ ] Your report's **Review status** (§11) honestly reflects whether you actually verified
      anything this run.

---

## 11. Report format (what the Worker returns)

Return tight Markdown — this is for the job log, not an end user:

```
### <filename>
**Review status:** verified | partially verified | unverified
**Changes made:** bullets, each `old → new` + source domain. ("None — content current" is valid.)
**Verified still-current:** notable facts checked that didn't need changing.
**Unverified / flagged:** anything you could not confirm (with why).
```

The Selector reads **Review status** to decide whether to call `update_refresh_status.py` for
this file (§9b) — `unverified` means don't.

---

## 12. Notes for whoever wires up the schedule

- This file is the **Worker prompt body**. Prepend the two inputs (§3) and the target file path.
- Keep batches ≤ 4 concurrent Workers; no sub-agent spawning (§1).
- After every Worker in the run reports back, the Selector updates `refresh-status.json` per §9b
  — that write is part of the Selector's job, not optional cleanup.
- Commit policy follows the repo norm: one logical commit, by explicit file path, never staging
  `.claude/` or unrelated changes (`refresh-status.json` is the one exception: it's the Selector's
  own bookkeeping and belongs in the same commit as the content edits it summarizes). Decide per
  your automation whether to auto-commit or open for review. Do not push unless intended.
- Last updated: 2026-09-01.
