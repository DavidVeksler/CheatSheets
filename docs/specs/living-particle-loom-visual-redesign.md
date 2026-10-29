# Living Particle Loom: visual design study

2026-10-28. Scope: visual design and interface behavior. Physics validation is deferred at David's request; the existing reference records and event explanations remain unvalidated in this pass.

## Direction

An editorial scientific instrument built around woven light. Midnight blue gives coral, amber, cyan, and violet filaments room to read. Serif display typography and quiet instrument labels frame the sculpture. The inspector uses an open margin rather than a stack of cards. Light mode uses warm paper around the same dark stage.

The central visual grammar is a set of procedural, three-dimensional filaments projected onto the stage. These are compositional graphics, not computed particle behavior. They do not encode physical size, shape, mass, speed, or a measured trajectory. The visible illustration legend explains this distinction.

## Implementation

- Standalone HTML with embedded CSS, JavaScript, and GLSL. No renderer library, external fonts, image textures, or build requirement.
- WebGL 2 instanced line strips and luminous point accents render the sculpture. CSS layers, container sizing, `light-dark()`, native disclosures, and `ResizeObserver` support the interface.
- Scene, family neighborhoods, generation alignment, and chart share particle records and interpolate from their current positions. A new navigation action redirects the running transition.
- The two up-quark scene instances converge on the up reference entry. The anonymous neutrino example fades independently rather than acquiring a flavor identity.
- Names, symbols, hit targets, search, breadcrumbs, inspector text, and navigation remain normal HTML. GPU loss leaves that interface usable.
- Pause freezes the animation clock. Reduced motion removes travel and ambient movement. Rendering stops while the stage is outside the viewport or the document is hidden.
- URL fragments restore view, family, selection, overlay, and generations. Pause, motion preference, and theme persist with a local-storage fallback.

## Visual and interface checks

Reviewed in the Codex in-app Chromium browser at its desktop viewport, 1280 × 960, and 390 × 844. These are responsive-layout checks, not mobile-device performance benchmarks.

Checked the opening sculpture, family transition, lepton neighborhood, all 17 chart entries, particle search including “muon neutrino,” interaction emphasis, pause, both themes, and phone overflow. Browser error and warning logs were empty during those checks. SEO and JavaScript syntax checks also pass.

The social preview is an actual capture of this design, encoded as lossless WebP. The existing scientific reference material remains available below the stage. Physics review and learner acceptance remain subsequent work. Deployment requires David's go-ahead.

The full repository publishing check passes catalog freshness, hubs, breadcrumbs, app integrity, JSON parsing, and PHP syntax. Its rendered front-door SEO checks are blocked by the local PHP runtime lacking `mbstring` (`mb_strtolower` is undefined). It also flags the existing `how-its-built.html` link to `popularity` as an uncommitted target. These checks were not bypassed; no deployment was performed.
