# Agentic AI — The Practitioner's Field Guide (pillar page)

Target file: `agentic-ai.html`

## Why this topic

"Agentic AI" is ultra-saturated with vendor fluff and recycled listicles — which is exactly
the opportunity: almost none of it is written by someone who ships agents and can link the
receipts. This page's angle is **authority through artifacts**. David has: a 150+ page site
built by a governed multi-agent pipeline (`how-its-built.html`), a published governance
framework (`governing-agentic-ai.html`), a founding-an-AI-delivery-function case study at a
regulated lender (davidveksler.com/david/ai-strategy.html), and public tooling
(skill-lint, agent-skills, CodeContext). No competing "what is agentic AI" page can say
"here is the pipeline, the framework, the case study, and the linter — click them."

This is the **pillar/hub page for the AI cluster**, the same role
`software-development-guides.html` plays for the dev cluster (see the July 2026
"developer pillar and spoke backlinks" pattern). It routes readers to the existing spokes
instead of duplicating them.

**Goal declaration (per TODO/README.md Rule 0):** this is a goal-2 (brand/authority) +
goal-1 (study) page, explicitly NOT judged by goal-3 traffic criteria. The head term is
unwinnable and that's fine. It still needs niche-utility hooks — the decision tables and
failure-mode taxonomy are the "keep this open while designing your agent" elements.

**Differentiation from existing pages (do not duplicate):**
- `governing-agentic-ai.html` = org-level governance (Golden Rule, four invariants, maturity path)
- `ai-coding-agents-compared.html` = product comparison with pricing/benchmarks
- `how-its-built.html` = this-site case study
- `agentic-ai.html` (this page) = **how agents actually work and fail**: architecture
  patterns, the autonomy ladder, context engineering, failure modes, security model —
  vendor-neutral, with one-line links into the spokes wherever depth already exists.

## Targeting

- **Primary query:** `agentic ai cheatsheet`
- **Secondary queries:** `ai agent architecture patterns` · `agent vs workflow when to use
  which` · `ai agent failure modes` · `context engineering cheat sheet` · `building ai
  agents field guide`
- **Mode:** research mode (engineer/EM/architect evaluating or designing agent systems;
  also the LinkedIn-share audience checking whether David knows what he's talking about).
- **Title:** `Agentic AI Cheatsheet: Patterns, Failure Modes & the Autonomy Ladder`
- **H1:** `Agentic AI: A Practitioner's Field Guide`
- **Meta description (150–200 chars):** `A field guide to agentic AI from a practitioner
  who ships it: architecture patterns, the autonomy ladder, context engineering, failure
  modes, security, and governance — with receipts.`
- **Reader outcome:** the reader can (a) decide whether their problem needs an agent, a
  workflow, or a script, using the decision table; (b) place a proposed system on the
  autonomy ladder and name the guardrails that rung requires; (c) name the top failure
  modes and the mitigation for each before writing code.
- **Success metric (brand goal):** LinkedIn shares of the autonomy-ladder artifact;
  referral clicks out to `ai-strategy.html?ref=cheatsheets` and the GitHub repos; becomes
  the most-linked internal hub of the AI cluster. Not judged on organic entries.
- **Index category:** `AI & Safety` (matches the whole existing cluster).
- **Jurisdiction:** global; no geographic variance.
- **Reading conditions:** desktop at work while designing/evaluating (primary); mobile
  first-read from a LinkedIn share (secondary — hero + ladder must land at 375 px). Print
  low priority; sane defaults suffice.

## Volatile-facts register

Design decision: keep volatile specifics OUT of this page — link the spokes that already
manage drift (`ai-model-picker.html`, `ai-model-api-pricing.html`,
`ai-coding-agents-compared.html`, `open-weight-ai-models.html`) instead of restating
model names, context-window sizes, prices, or SWE-bench numbers here.

- STABLE: agent loop anatomy, architecture patterns (Anthropic's five workflow/agent
  patterns), failure-mode taxonomy, security principles (lethal trifecta, least privilege,
  drafts-only default), autonomy-ladder rungs.
- SLOW-DRIFT: framework/protocol landscape (MCP, skills, computer use, the major
  orchestration frameworks) — name them with "as of <Mon YYYY>" tags, no version numbers
  beyond what's needed.
- VOLATILE: anything with a number attached to a vendor — quarantine to the spokes.
- **Overall rating: SLOW-DRIFT** if the quarantine rule is followed.

## Content approach

Quick-reference block near top, then ~10 sections. Interactivity budget: one interactive
element max (the autonomy-ladder self-assessment — click a rung, see its guardrail
checklist — is enough; everything else is static).

1. **Quick Reference — the vocabulary decoder** (table, 15–20 rows): agent, workflow,
   harness, tool/function calling, MCP, skill, subagent, orchestrator, context window,
   compaction, memory, eval, trace, HITL, guardrail, sandbox, system of record. One-line
   definition + the practical gotcha each term hides. Exemplar row:
   `MCP | Open protocol for connecting tools/data to any agent (as of 2026: the de facto
   standard) | A connector is a capability grant — treat every MCP server as part of your
   attack surface.`
2. **The agent loop** — gather context → plan → act (tools) → verify → iterate; what
   breaks at each stage (annotated diagram, 5 stages × failure + mitigation).
3. **The Autonomy Ladder** (SIGNATURE — see Visual design): L0 script → L1 LLM-in-the-loop
   → L2 tool-calling agent → L3 multi-step with verification → L4 orchestrated
   subagents/fleets → L5 unattended standing automations. Per rung: what capability
   unlocks it, dominant failure mode, guardrails required before you're allowed to climb.
   6 rungs, fully populated.
4. **Do you even need an agent?** — decision table (8–10 rows): task shape → script /
   workflow / single agent / multi-agent, with cost & reliability rationale. Include the
   five canonical patterns (prompt chaining, routing, parallelization,
   orchestrator-workers, evaluator-optimizer) — verify names/definitions against the
   Anthropic "Building Effective Agents" source, don't recall.
5. **Context engineering** (10+ entries): context budget as the scarce resource,
   retrieval vs stuffing, compaction, structured notes/memory, subagent isolation,
   just-in-time tool schemas. Link `prompt-builder.html` for the prompt-level layer.
6. **Tools & integration layer**: tool-design rules (fewest tools that cover the job,
   typed outputs, idempotency, error messages written for the model), MCP vs bespoke
   function calling vs skills-as-files. Link CodeContext and agent-skills repos as
   worked examples.
7. **Failure-mode taxonomy** (10–14 specimen cards — the second shareable artifact):
   hallucinated success, silent failure swallowed by a fallback, runaway loop / cost
   blowup, context rot, lost-in-the-middle, prompt injection, confused deputy /
   over-privileged connector, cross-agent contamination, eval overfitting, automation
   bias. Each card: definition, real-world sighting, detection signal, mitigation.
8. **Security & governance in one screen**: the lethal trifecta (private data + untrusted
   content + exfiltration channel — verify against Willison's canonical post), least
   privilege, drafts-only default, human-in-the-loop as architecture, the system of
   record always wins. This section is a *summary that links out* — one line each into
   `governing-agentic-ai.html` (four invariants, maturity path) and the lender case study
   (`ai-strategy.html?ref=cheatsheets`) as the "this is deployed in a regulated
   environment" receipt.
9. **Evals & observability — minimum viable rig** (6–8 entries): trace every run, eval
   sets before autonomy, canary tasks, cost/latency budgets, regression on prompt change,
   the two jobs of observability (debugging vs adoption measurement — from the case study).
10. **Common mistakes / anti-patterns** (MANDATORY, 8+): building an agent where a cron
    job wins; demo-driven autonomy (L4 demo, L1 reliability); "the framework will handle
    it"; unbounded tool permissions; treating evals as a launch gate instead of a
    regression suite; multi-agent as a status symbol; ignoring token economics; shipping
    without a kill switch.
11. **Field notes — the receipts** (authority section, framed as case studies with
    lessons, NOT a bio): (a) this site — 150+ pages from a governed pipeline, link
    `how-its-built.html`; (b) the regulated-lender platform — 10-plugin marketplace,
    ~30 skills, drafts-only architecture, link the case study; (c) public tooling —
    skill-lint, agent-skills, CodeContext, each with a one-line lesson it encodes.
    End with a byline linking the portfolio site (davidveksler.com), LinkedIn, and GitHub.

**Own-resource link map (the point of the page — implement ALL of these):**
- On-site spokes: `governing-agentic-ai.html`, `how-its-built.html`,
  `ai-coding-agents-compared.html`, `ai-model-picker.html`, `ai-model-api-pricing.html`,
  `open-weight-ai-models.html`, `prompt-builder.html`, `aisafety.html` /
  `ai-safety-existential-risk.html` (risk framing), `software-development-guides.html`
  (sibling pillar).
- Off-site — REQUIRED, per David (do not drop these two even if trimming links):
  `https://davidveksler.com/david/ai-strategy.html?ref=cheatsheets` (the lender case
  study — the primary receipt, linked from the security/governance section AND the
  field-notes section) and `https://davidveksler.com/?ref=cheatsheets` (portfolio site —
  linked from the field-notes section byline, e.g. "More of David's work →").
- Off-site (verify each is live at build time before linking):
  `https://github.com/DavidVeksler/skill-lint`,
  `https://github.com/DavidVeksler/agent-skills`,
  `https://github.com/DavidVeksler/CodeContext`,
  `https://github.com/DavidVeksler/CheatSheets`,
  `https://www.linkedin.com/in/davidveksler/`. Do NOT link richagent.ai unless verified
  live and presentable.
- Reciprocal links (parent-agent edits): add "part of the agentic AI field guide" links
  back from `governing-agentic-ai.html`, `how-its-built.html`, and
  `ai-coding-agents-compared.html` Related sections; consider one from
  `software-development-guides.html` (pillar-to-pillar).

## Research sources (verify, don't recall)

- Anthropic, "Building Effective Agents" + the context-engineering and multi-agent
  engineering posts (anthropic.com/engineering) — pattern names and definitions.
- modelcontextprotocol.io — MCP status/adoption claims.
- OpenAI "A Practical Guide to Building Agents" — cross-check pattern vocabulary.
- Simon Willison, "The Lethal Trifecta" (simonwillison.net) — exact formulation.
- David's own pages/repos above — quote the real numbers from them (150+ pages, ~30
  skills, 9 departments) rather than inventing new ones; re-verify against the live pages.
- Must NOT be recalled from memory: any benchmark score, any model context-window size,
  any vendor pricing (quarantine rule), the five pattern names, the trifecta wording.

## Visual design

- **Aesthetic: naturalist's field guide** — cream paper texture, ink-line illustrations,
  specimen-label typography (small caps, figure numbers, "Plate I" captions) for the
  light theme; dark theme keeps the ink-on-slate feel. Distinct from the engineering
  exhibit of `how-its-built.html` and the civic tone of `governing-agentic-ai.html`.
  Commit fully: failure modes as pinned-specimen cards with Latin-style binomials
  (e.g. *Successus hallucinatus*), the ladder as an engraved plate.
- **Signature element / og:image / shareable artifact: the Autonomy Ladder** — a single
  1200×630-friendly plate, L0→L5 with one-line guardrail per rung. Build it first and
  best; it must read at 375 px (rungs stack vertically on mobile).
- Interactive element (one, optional-JS): clicking a ladder rung reveals its guardrail
  checklist via native `<details name="ladder">`. Works without JS as stacked details.
- Wide tables get `overflow-x: auto` wrappers; specimen cards go single-column at 375 px.
- Print: sane defaults; details print expanded where feasible.
