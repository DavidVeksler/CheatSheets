# Marketing campaign — execution plan

Implemented in-repo 2026-07-14. Companion to [`seo-planning.md`](seo-planning.md), which owns
organic-search measurement. This document now contains the remaining human publishing queue and the
ready-to-use campaign assets; completed prerequisites are recorded as evidence, not left as TODOs.

## Positioning

The flagship story is the system, not any single page:

> One person plus AI agents build and maintain 160+ standalone reference pages through written specs,
> primary-source research, browser QA, deployment gates, and a public git audit trail.

Individual cheatsheets are proof that the process repeatedly produces useful artifacts. Use separate
mini-campaigns for separate audiences; do not market the whole 13-category collection as one product.

## Implemented owned-media foundation

Verified 2026-07-14:

- The public [`how-its-built.html`](../how-its-built.html) case study explains the pipeline, governance,
  tradeoffs, live collection size, and audit trail.
- [`README.md`](../README.md) now gives the public repository a useful landing page and links to the
  live site, case study, and change history.
- The homepage now leads with the 160+ page agentic-pipeline story and links directly to GitHub.
- Every root cheatsheet carries a concise pipeline proof block linking to the case study and public
  source repository.
- Every root cheatsheet participates in a reciprocal, category-local discovery ring. The link audit
  reports 0 orphan pages and a minimum of 4 inbound links per page.
- Email capture is already implemented on the homepage and build-story page through `subscribe.php`;
  no new provider or tracking dependency is needed.
- The initial campaign pages below have valid local OG assets at 1200×630 or the exact 2× equivalent,
  and their metadata points at those assets.

## Initial campaign pages

| Audience | Lead asset | Supporting proof | Share angle |
|---|---|---|---|
| AI / developer | `how-its-built.html` | `ai-frontier.html`, `ai-model-api-pricing.html`, `ai-coding-agents-compared.html` | A governed one-person agentic publishing pipeline, with inspectable source and output |
| Ham radio | `baofeng-uv5r-quick-ref.html` | `baofeng-uv5r-ham-guide.html`, `ham-radio-technician.html` | A keep-open programming and field reference, shared as “I made this” |
| Martial arts | `judo.html` | `brazilian-jiu-jitsu.html`, `ashihara-karate.html` | Dense training reference; ask practitioners what is missing rather than claiming authority |
| Space / engineering | `orbital-rockets-comparison.html` | `space-habitats-life-support.html`, `boom-supersonic.html` | Exact side-by-side engineering comparisons |
| Advocacy | `objectivism.html` | — | Reach within existing relevant communities; keep separate from the developer campaign |

Do not promote the Anduril topic. The removed page and 404 decision remain settled.

## Tracking convention

Use one canonical UTM shape on every manually shared link:

```text
https://cheatsheets.davidveksler.com/<page>.html?utm_source=<channel>&utm_medium=social&utm_campaign=agentic_cheatsheets_2026&utm_content=<post_slug>
```

Examples:

```text
https://cheatsheets.davidveksler.com/how-its-built.html?utm_source=linkedin&utm_medium=social&utm_campaign=agentic_cheatsheets_2026&utm_content=build_story
https://cheatsheets.davidveksler.com/baofeng-uv5r-quick-ref.html?utm_source=reddit&utm_medium=social&utm_campaign=agentic_cheatsheets_2026&utm_content=baofeng_quick_ref
```

Keep `utm_campaign` stable so GA4 groups the launch. Change `utm_source` and `utm_content` per post.
Do not put UTMs in internal links, canonical tags, `llms.txt`, or the sitemap.

## Ready-to-publish copy

### LinkedIn — flagship

> I built a 160+ page reference site with AI agents. The pages are useful, but the more interesting
> artifact is the system behind them: written specs, primary-source fact checks, accessibility and
> metadata gates, real browser QA, preview generation, git history, and a human-controlled deploy.
>
> The full pipeline and tradeoffs are here: [UTM link to `how-its-built.html`]
>
> The source is public too: https://github.com/DavidVeksler/CheatSheets

### Hacker News

Suggested title:

```text
Show HN: A 160+ page reference site built with a governed AI-agent pipeline
```

Suggested first comment:

> I built this to test whether agentic content production can be made repeatable rather than lucky.
> The repository has one binding quality standard, topic specs, primary-source verification rules,
> browser checks, social-preview generation, and a separate human deploy gate. The case-study page
> explains what worked, what is deliberately simple, and what still requires judgment. I would value
> criticism of the governance model and the actual page quality more than the raw page count.

### Niche community template

> I made a free, keep-open reference for [specific task]: [one-sentence utility]. I would appreciate
> corrections from people who do this regularly: [UTM link].

Before posting, replace the bracketed text, read that community's current self-promotion rules, and
answer comments from the same account. One honest post per community is the default.

### Newsletter / podcast pitch

Subject:

```text
Story idea: the governance system behind a 160+ page AI-built reference site
```

Body:

> I maintain a public 160+ page cheatsheet collection with AI agents, but the useful story is the
> production system: a binding cross-agent spec, verified volatile facts, deterministic acceptance
> checks, browser QA, a public commit trail, and a human deployment gate. The engineering case study
> and source are public. If you cover practical agentic workflows, I can share the failure modes,
> economics, and what still does not automate cleanly.

## Human publishing queue

These actions affect external accounts or community reputation and therefore remain intentionally
unexecuted in the repository:

- [ ] Publish the LinkedIn flagship post with the tracked build-story URL.
- [ ] Make one quiet niche share, starting with the Baofeng quick reference; record the post URL and
  7-day outcome below before choosing the next community.
- [ ] Decide whether the quality of discussion from the first two posts justifies the one-shot Show HN
  launch.
- [ ] If the HN launch earns sustained interest, pitch no more than three relevant AI-builder
  newsletters or podcasts using the draft above.

## Measurement log

Judge each audience by its actual goal:

- Professional brand: profile views and recruiter or peer conversations.
- Agentic case study: tracked referral sessions, GitHub stars, substantive discussion, and earned
  newsletter or podcast pickup.
- Advocacy: reach and engagement inside the intended community.
- Niche references: useful corrections, saves/bookmarks where visible, and qualified referral traffic.

Do not set a site-wide traffic target. Record each post date, final URL, UTM content slug, 7-day
referral sessions, and qualitative outcome here before repeating a channel.

| Date | Channel | Asset | Post URL | 7-day result | Decision |
|---|---|---|---|---|---|
| — | — | — | — | — | — |

## Guardrails

- Never commit personal data, subscriber addresses, or private analytics exports.
- No astroturfing, sockpuppets, paid amplification, or fabricated social proof.
- Check community rules at posting time; they are not stable repo facts.
- Prefer write-once assets that compound: the case study, README, public source, and durable links.
- External sending and posting require the account owner's explicit action; this repository contains
  the copy and measurement contract, not authorization to publish.
