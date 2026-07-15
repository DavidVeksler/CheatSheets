# Marketing campaign — high-level brainstorm

Working doc for promoting cheatsheets.davidveksler.com beyond passive SEO. First pass
2026-07-14; brainstorm only, no committed budget/calendar yet. Companion to
[`seo-planning.md`](seo-planning.md) (organic search is covered there — this doc is about
everything else).

## What we're marketing

~160 standalone, no-framework HTML cheatsheets spanning AI/dev tools, martial arts, Buddhism,
ham radio, personal finance/legal defense, prepping, religion, engineering. Site goals (per
`cheatsheets-site-goals` memory) shape the campaign — we are NOT just chasing traffic:

1. **Personal study tool** — not marketed.
2. **Personal brand / portfolio** — marketed to recruiters, peers, hiring managers.
3. **Agentic-automation case study** — marketed to the AI/dev community; traffic = proof.
4. **Advocacy pages** — marketed for reach in relevant communities.

Implication: run **per-audience mini-campaigns**, not one site-wide campaign.

## The core story (the thing actually worth promoting)

The single most differentiated asset isn't any one cheatsheet — it's the **meta-story**:
*"One person + Claude Code built and maintains a 160-page reference site: specs, QA audits,
SEO, deploys — all agentic."* That's a story the AI/dev community shares organically; individual
cheatsheets are the supporting evidence. Goal-3 marketing should lead with the process, not
the pages.

## Campaign ideas by audience

### A. AI / dev community (goal 3 — the flagship campaign)

- **"How this site is built" write-up** — a public post (blog or a cheatsheet-style page on the
  site itself) documenting the pipeline: TODO specs → generation → QA audits → popularity
  scoring → deploy. Include real numbers (pages, commits, GSC clicks). This is the launchable
  asset everything else links back to.
- **Show HN / Hacker News launch** of that write-up (not the raw site). One shot; timing and
  title matter. Lobsters, r/ClaudeAI, r/LocalLLaMA as secondary.
- **The repo is public — use it.** Add a strong README with the meta-story, link it from every
  page footer ("built with agents — see how"). GitHub stars are a distribution channel.
- **Individual high-value dev pages as standalone posts**: ai-frontier, ai-model-api-pricing,
  ai-coding-agents-compared are natural fits for r/artificial, X/Twitter threads, and
  newsletters (Ben's Bites, TLDR AI accept submissions).
- **X/Twitter thread series**: "I asked Claude to build me a cheatsheet on X" — screenshot the
  page, link it. Cheap, repeatable, compounds with the meta-story.

### B. Niche hobby communities (traffic + proof, low effort)

Each strong niche page has a home community where a genuinely useful reference is welcome
(not spam) if shared honestly as "I made this":

- **Ham radio**: baofeng-uv5r pages → r/amateurradio, r/Baofeng, QRZ forums. Already the #2
  organic performer — the audience demonstrably wants it.
- **Martial arts**: bjj / judo / ashihara-karate → r/bjj, r/judo, martial arts Discords.
- **Prepping/emergency**: emergency-radio-card, air-water-filtration → r/preparedness.
- **Buddhism/meditation**: the Buddhism cluster → r/Buddhism, r/Meditation (mind the
  self-promo norms; these subs are strict).
- **Space**: orbital-rockets-comparison → r/space, r/SpaceXLounge.
- Rule of thumb: one post per community, ever, unless it lands well. Reputation > reach.

### C. Recruiters & professional peers (goal 2)

- **LinkedIn**: the agentic-automation case study as a LinkedIn article/post — this audience
  rewards "how I use AI at scale" content heavily right now.
- Link the site prominently from davidveksler.com, LinkedIn profile, GitHub profile, resume.
- Cross-link with resumeforge.davidveksler.com if that's public-facing.

### D. Advocacy pages (goal 4)

- Share capitalism/objectivism-adjacent pages through existing channels (freecapitalists.org
  audience, relevant subreddits/groups). Measured on reach, kept separate from the dev-brand
  campaign — don't mix the two audiences.

## Channel inventory (owned / earned / paid)

- **Owned**: the site itself, public GitHub repo, davidveksler.com, freecapitalists.org,
  LinkedIn, X/Twitter, email (Mailgun is already wired up — a "new cheatsheet of the month"
  digest is possible later; needs a signup form first).
- **Earned**: HN, Reddit niches, newsletters, podcasts (AI-builder podcasts love the
  one-person-agentic-site story), backlinks from "awesome-cheatsheets"-style lists.
- **Paid**: probably not worth it — no monetization, so CAC has nothing to amortize against.
  Skip unless testing a specific hypothesis.

## Site-side prerequisites (do before driving traffic)

- [ ] Fix striking-distance metadata first (already specced in
      [`seo-implementation-spec.md`](seo-implementation-spec.md)) — don't send traffic to
      pages with truncated titles.
- [ ] "How this site is built" page — the campaign centerpiece.
- [ ] Footer/homepage link to the GitHub repo + meta-story blurb on every page.
- [ ] OG images verified on the pages we'll share (social cards are the ad creative).
- [ ] Decide: email capture or not (adds maintenance; defer unless HN launch pops).

## Measurement

- GSC + Cloudflare edge analytics + GA4 (Cloudflare-injected) already in place — enough.
- Per-campaign: UTM-tag shared links so referral spikes are attributable.
- Success metrics by goal: goal 2 = profile views / recruiter contacts (anecdotal is fine);
  goal 3 = referral traffic, GitHub stars, HN/newsletter pickup; goal 4 = reach on advocacy
  pages. No site-wide traffic target.

## Constraints / guardrails

- Public repo, personal site: no personal data, ever (per standing rule).
- One-person operation: prefer campaigns that are **write once, compound forever** (the
  write-up, the README, footer links) over ones needing sustained posting cadence.
- Don't astroturf niche communities — one honest "I made this" per community.
- Never touch the Anduril topic (C&D on record).

## Open questions for David

1. Is the meta-story write-up something you'd want on the site itself, on davidveksler.com,
   or as a LinkedIn article first?
2. Appetite for an HN launch (it invites scrutiny of every page)?
3. Email digest: worth the maintenance, or skip?
4. Any communities above you're already active in (posting lands much better from an
   established account)?

## Rough sequencing (if/when this becomes a plan)

1. Prerequisites (metadata fixes, build-story page, repo README, footer links).
2. Quiet niche shares (B) to validate pages land well.
3. LinkedIn post (C) — low risk, on-brand.
4. HN/newsletter launch of the meta-story (A) — the big swing.
5. Evaluate → decide on email digest / repeatable X cadence.
