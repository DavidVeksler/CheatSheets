# Weekly Cheatsheet Freshness Update: Agent Instructions

Procedure for the `cheatsheets-weekly-freshness` routine. Sections 2-8, 10, 11 are the **Worker prompt body**, handed to a light model (Claude Haiku) that updates **exactly one cheatsheet**. Quality bar: [`AGENTS.md`](AGENTS.md) > *Generation & quality protocol*; AGENTS.md wins on conflict. Section numbers are referenced by the routine and by scripts; keep them stable.

---

## 1. Roles

1. **Selector** (once per run): picks the files (§9), dispatches one Worker per file, records outcomes (§9b).
2. **Worker** (one per file, Haiku): refreshes one sheet's dated content and reports.

Dispatch Workers in batches of **≤ 4 concurrent**. Workers do their own research and **never spawn sub-agents** (fan-out trips API rate limits and leaves files half-edited).

## 2. Worker constraints

- Update ONE file (path given). Touch nothing else.
- Follow this checklist literally rather than reasoning open-endedly.
- Research with `WebSearch` / `WebFetch`; no Agent/Task tool. Tools: `Read`, `WebSearch`, `WebFetch`, `Edit`.
- Budget ~8-15 focused searches; stop when the volatile facts are checked.
- Never touch `refresh-status.json` (parallel writers drop updates; the Selector writes it once, §9b).

## 3. Inputs

- `FILE`: absolute path of the sheet.
- `TODAY`: `YYYY-MM-DD`; derive `MONTH YYYY` and `YEAR`. If not supplied, get the current date first.

## 4. Golden rules

1. **Verify, never recall.** Every changed version, price, date, model name, spec, benchmark, funding figure, count, or "latest" claim is confirmed against a primary source (vendor site, official docs, the spec, the org's newsroom). Assume training data is wrong about anything recent.
2. **Never fabricate.** Can't confirm? Keep the existing value if still plausible, else soften/remove it, and flag it in the report.
3. **Surgical.** Preserve structure, tone, layout, classes, formatting. Change only what is stale, wrong, or newly important. No rewrites or redesigns.
4. **One file only.**
5. **No page date stamps.** Never add, edit, or bump a visible date stamp or JSON-LD `dateModified`. Review status lives in `refresh-status.json`, written only by the Selector.
6. **Unverified runs report as unverified.** If primary sources were unreachable (budget exhausted, tool errors), say so in the report (§11).
7. **Never overwrite a real provenance note** (e.g. "Metadata, CDN dependencies, and internal links reviewed against repository audit standards.") with a failure message. "Could not verify" goes in the report, never the page.

## 5. Procedure

1. Read the whole `FILE`; note coverage and any partial edits from a prior run.
2. List volatile facts (§6). If the page is essentially evergreen (§7), say so in the report.
3. Verify each fact against primary sources.
4. Edit in place with `Edit`, matching surrounding HTML exactly, applying §4.1-§4.2.
5. Self-check (§10).
6. Report (§11).

## 6. Volatile-fact checklist

- **Software:** versions, "new in vX", current stable/LTS, EOL dates, deprecations, license changes.
- **AI models:** flagship names/versions, context windows, pricing, benchmarks, leaders.
- **Products & hardware:** lineup/trims, specs, MSRP, discontinued/successor models, shipping status.
- **Companies & people:** funding, valuations, leadership, mergers, shutdowns, renames.
- **Markets & rates:** prices, rates, market share, unit costs. Tag each with `as of MONTH YYYY` and a source. Never embed a volatile spot price (e.g. live BTC); make it relative or omit it.
- **Regulation/standards:** law status (proposed/in force/withdrawn), standard numbers and statuses, guidance dates.
- **Timelines:** lapsed predictions, "recent developments", latest timeline entry.
- Any **"latest / newest / current / as of"** phrase.

Confirmed change → edit to the verified value (+ `as of MONTH YYYY` where the page uses them). Unverifiable → leave/soften and flag.

## 7. Evergreen content: do not churn

Concepts, definitions, theory, history, technique, glossaries, OPSEC/safety principles, anatomy, religion, philosophy, mathematics, historical documents. Touch only a sheet's dated section. Essentially evergreen topics (expect "nothing material changed"): religion, philosophy, anatomy, martial-arts technique, cooking, past historical timelines, the Bitcoin whitepaper.

## 8. Leftover stamps

If the page you're editing still has a visible "Last verified" / "Last updated" line or a `dateModified` field, remove it and note it in the report. Don't go hunting beyond the edit.

## 9. Selector

### 9a. Picking the working set

The dated set is computed, never hand-listed:

```sh
python scripts/freshness_scan.py            # this run's batch, oldest-first
python scripts/freshness_scan.py --all      # full ranking, no batch cut
python scripts/freshness_scan.py --json     # machine-readable
python scripts/freshness_scan.py --limit N  # custom batch (refused if over budget)
```

Read-only (no edits, no network). Ranks root `*.html` by `refresh-status.json` `last_reviewed` (fallback: last git commit date), drops files reviewed within `--min-age-days` (default 30), holds back §7 topics, and cuts to a budget-sized batch.

**Budget is hard:** ~15 searches per Worker against the 200-call session cap (`CLAUDE_CODE_MAX_WEB_SEARCHES_PER_SESSION`, shared by Selector and Workers) allows about **12 files per run**. To go bigger, raise the cap first, then pass `--limit`. Never dispatch more Workers than the budget supports. Open issue: most of the corpus ages past 30 days at once, so a full pass takes many weeks at 12 files/run; the Selector is triage, not a full sweep.

### 9b. Recording the outcome (after all Workers report)

For each file whose **Review status** (§11) is `verified` or `partially verified`:

```sh
python scripts/update_refresh_status.py FILE.html --date TODAY --note "<one-line summary>"
```

Note comes from the Worker's **Changes made** / **Verified still-current**. Run once per file from the Selector only; never concurrently. Skip `unverified` files so their old date keeps them first in line next run.

## 10. Self-check

- [ ] Every changed fact confirmed against a primary source (or left + flagged).
- [ ] No fabricated specifics.
- [ ] Edits surgical; structure/tone/classes intact.
- [ ] No visible date stamp or JSON-LD `dateModified` added or bumped.
- [ ] `refresh-status.json` untouched.
- [ ] Only `FILE` modified.
- [ ] **Review status** honestly reflects what was verified.

## 11. Report format (Worker returns)

```
### <filename>
**Review status:** verified | partially verified | unverified
**Changes made:** bullets, each `old → new` + source domain. ("None — content current" is valid.)
**Verified still-current:** notable facts checked that didn't need changing.
**Unverified / flagged:** anything you could not confirm (with why).
```

The Selector calls `update_refresh_status.py` only for non-`unverified` reports (§9b).

## 12. Scheduling notes

- Prepend the §3 inputs and target path to the Worker prompt.
- Commit: one logical commit by explicit path, never `.claude/` or unrelated files. `refresh-status.json` goes in the same commit as the content edits it summarizes.
- Pushing to `origin` does not make changes live; deploy is David's gate (`./deploy.sh`).
