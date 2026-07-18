# machine-consensus refinement spec (round 2)

Target files: `machine-consensus.html`, `machine-consensus-terrain.js`. No other files.
Design intent reference: the page's job is (in priority order) the 15-second test, the RLHF share test, the credibility test. Every change below serves one of those. Keep the existing aesthetic exactly: no new colors, no new fonts, no layout rework. Match existing code style (compact, no comments unless stating a non-obvious constraint).

## 1. Attract-mode auto demo (15-second test) — HIGHEST PRIORITY

Today the terrain sits inert until a prompt button is clicked. A first-time visitor must see the ball roll to the most common answer region without reading or clicking.

- In `machine-consensus.html`, after `ensureTerrain()` resolves with a live api (webgl mode, not fallback, not mobile, not reducedMotion), schedule an automatic `api.dropPrompt('safe')` roughly 1.2s later.
- Suppress the auto-drop if the user has already interacted (clicked any prompt button, moved temperature, toggled RLHF, or scrolled past the hero). One `userInteracted` flag set by those handlers is enough.
- The auto demo must NOT mark the `safe` prompt button `.active` deceptively wrong — it is fine (and preferred) to highlight it, since that is what actually ran. Use the normal `selectPrompt` path.
- State readout during the auto demo: `Demo drop: watch it roll to the most common answer` (then the normal settled text takes over).
- Do not auto-drop more than once per page load.

## 2. Settled particle must re-roll on morph (share test) — CRITICAL BUG FIX

In `machine-consensus-terrain.js`:

- Bug: `updateParticle` returns early unless phase is `dropping`/`descending`, so a settled particle keeps its old y while the terrain morphs under it (floats or gets buried). On morph completion `settleAtNearest()` only updates the label — the ball never visibly moves. The copy promises "It re-settles on the new field."
- Fix: in `startMorph`, if `phase === 'settled'` and the particle is visible, re-enter descent: `setPhase('descending', …)` with `phaseTime = 0`, a small random nudge velocity (magnitude ~0.02–0.04), and keep the trail. Because `heightAt` already reads the live `morph` value, the ball will follow the interpolated slope and visibly roll into the reshaped field. State text while this happens: `The terrain is moving under a settled answer…`.
- Also, whenever the particle is visible and phase is `settled` (e.g. no morph in progress but debug sliders moved terrain), glue its y to the surface each frame: in `animate` or `updateParticle`, recompute `y = heightAt(x,z) - 2.4 + .23` for settled particles so it can never float/bury.
- Make the morph feel like earthmoving, not a blink: raise morph tween duration from 1.5 to 2.6 seconds. Do not add camera moves.

## 3. Absolute social image URLs

In the `<head>`: `og:image` and `twitter:image` must be `https://cheatsheets.davidveksler.com/images/machine-consensus.png` (absolute). Leave everything else in head untouched.

## 4. Limits-section discoverability (credibility test)

Add one quiet link above the fold. In the hero, immediately after the `.hero-cta` "Drop a prompt" link, add a second inline link styled as plain text (small, `--muted` color, underlined) reading `Where this map lies →` with `href="#limits"`. One short CSS rule is fine; reuse existing tokens. Do not add a nav item or banner.

## 5. Dead "Continue" buttons

The `hold-safe`, `hold-steelman`, `hold-rlhf` steps have `.motion-next` buttons whose `data-run` values are no-ops in `runAction`. Remove those three buttons from the HTML (the hold steps are narrative; in reduced-motion mode a button that does nothing erodes trust). Keep the buttons on steps that actually run something.

## 6. Headless QA step hook

Animation is driven by `renderer.setAnimationLoop`, which never fires when the tab is hidden — this made headless QA impossible. Add to the returned api in `createTerrain`:

- `step(ms = 16.7)`: runs exactly one frame of the internal update (same body as `animate`, using a synthetic clock advanced by `ms`), independent of rAF. It must work while the loop is paused and must not double-advance time when the real loop is running (simplest: `step` calls the shared frame body with its own accumulated synthetic timestamp; guard it to only be usable when `paused` or the loop is inactive).
- Expose nothing else new. `window.__terrainQA` in the HTML already exposes the api getter; no HTML change needed for this item.

## Verification (required before finishing)

Use the running static server at http://localhost:8765/machine-consensus.html (Browser pane tab `seed`). The pane may be hidden, so rAF may not fire — that is exactly what the new `step()` hook is for. Verify via `javascript_tool`:

1. `ensureTerrain()` → mode `webgl`.
2. Drive `api.step(33)` in a loop (e.g. 400 steps) after the auto-drop timer fires (you can call `dropPrompt('safe')` directly) → phase reaches `settled`, callout label is `Mainstream view`.
3. `dropPrompt('steelman')`, step to settled → basin label is NOT `Mainstream view` (run up to 3 rerolls if needed; report which basin it lands in).
4. With a settled particle, `setMorph(1)`, then step through ≥ 3.5 simulated seconds → phase passed through `descending` and re-settled; particle y equals `heightAt(x,z) - 2.4 + .23` within 0.05 at the end.
5. Reload with `?fallback=1` → static mode still activates, no console errors.
6. Reload plain → confirm auto-drop schedules (phase leaves `idle` without any click, after stepping/waiting), and that setting the userInteracted flag first suppresses it.
7. Run `python scripts/seo_check.py` (or however the repo invokes it — check the script's usage) on the page and confirm it passes.

Report results as plain facts, including any check that failed. Do not commit; the parent session handles git.
