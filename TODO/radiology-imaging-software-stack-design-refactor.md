# Radiology Imaging Software Stack - Architecture Atlas Design Refactor

## Target

- Existing page: `radiology-imaging-software-stack.html`
- Existing preview: `images/radiology-imaging-software-stack.png`
- Change type: visual hierarchy, navigation, responsive tables, search UX, and evaluation-workspace refinement
- Index category: `Software & DevOps` (already registered in `category-map.php`)
- Content posture: preserve the shipped reference; this is not a research or prose-rewrite pass

Read `AGENTS.md`, `TODO/README.md`, `TODO/SPEC-AUDIT.md`, and this file before implementation. If they disagree, the repository-wide instructions win.

## Why this refactor

The page already succeeds as a dense practitioner reference and contains a strong signature artifact: the thirteen-stratum stack map. Its current presentation still behaves like one very long document. The reader encounters 29 sections, 36 tables, 28 navigation links, 116 evidence badges, 120 scorecard fields, and 76 checklist boxes through nearly identical section, card, and table treatments.

The refactor should make the page feel like an architecture atlas with an embedded procurement workspace. It must become easier to answer three questions quickly:

1. Where does this concept sit in the imaging stack?
2. What standard, workflow, or product boundary governs it?
3. What should I ask, compare, or decide next?

The design must improve orientation without reducing technical density or hiding reference content behind an application shell.

## Targeting and reader outcome

### Search intent

- Primary query: `radiology imaging software stack`
- Secondary queries:
  - `PACS architecture`
  - `DICOMweb vs DIMSE`
  - `PACS vs VNA`
  - `DICOM conformance statement checklist`
  - `build vs buy PACS`
- Search mode: research mode, often followed by active architecture planning or vendor evaluation

### Metadata contract

Preserve these values unless a separate SEO task authorizes a change:

- `<title>`: `Radiology Imaging Stack: DICOM, PACS, Viewers, Build vs Buy`
- H1: `The Radiology Imaging Software Stack: From Exposure to Answer`
- Meta description: `DICOM services and UIDs, DICOMweb endpoints, transfer syntaxes, IHE radiology profiles, FHIR imaging resources, PACS vs VNA, viewer tiers, and a component build-vs-buy scorecard.`

### Definition of working

After using the page, a product or architecture lead can locate a component in the imaging stack, follow its standards and workflow dependencies, and complete a defensible first-pass vendor or build-versus-buy evaluation without opening another guide.

### Success metric

Success is increased use of the stack map and evaluation tools, reflected by return-direct visits, print events, and popularity score growth without a decline in organic entries for the existing target queries.

### Reading conditions

- Primary: 1280-1920 px desktop monitor during architecture work or a vendor call, with frequent jumping rather than linear reading.
- Secondary: 375-768 px phone or tablet used for a quick UID, protocol, or terminology lookup.
- Meeting: printed scorecard or questionnaire in grayscale.
- Lighting: office light and reading-room dark conditions; both themes are first-class.
- Stress level: moderate. The reader may be diagnosing an integration failure or challenging a vendor claim, so location and evidence type must remain obvious.

## Scope boundaries

### Preserve exactly

- All 29 existing `<section>` IDs and every other deep-link target.
- The current order and meaning of technical content.
- Table row and column relationships.
- Evidence-label wording and semantic distinctions.
- Stack-map strata, strategic classifications, default verdicts, and link targets.
- All `[data-sc]` keys and their saved scorecard behavior.
- All `[data-q]` keys and their saved questionnaire behavior.
- The current `localStorage` keys.
- Metadata, canonical URL, JSON-LD, disclaimer, sources, and related-link destinations.
- Standalone single-file delivery, except for the existing preview PNG.

### Allowed content changes

- Navigation labels, search status text, button labels, help text, section-purpose labels, and other interface microcopy.
- A short chapter introduction or task-path label when it does not make a new factual claim.
- Replacement of empty dependency-based footer icons with inline SVG or text-only treatment.

### Out of scope

- Fact refreshes, version changes, new product recommendations, or new medical/regulatory claims.
- Rewriting, condensing, or reordering the substantive reference prose.
- Adding clinical images or making the page resemble a diagnostic image viewer.
- Loading a framework, web font, icon library, analytics library, or other new CDN dependency.
- Converting the page into an SPA or requiring JavaScript to reach content.
- Changing the index category or cross-link destinations.
- Deployment. Implementation may be committed and pushed under repository policy, but production deployment still requires explicit approval.

## Design concept: Architecture Atlas

Retain the existing reading-room visual identity but make the hierarchy feel more like a well-labeled imaging study:

- Chapters are the study-level organization.
- Sections are series.
- Tables, diagrams, and worksheets are instances.
- Cyan identifies standards and navigation.
- Amber identifies recommendations and decisions.
- Red identifies failure, safety, and stop conditions.
- Neutral gray carries common practice, supporting information, and structure.

Do not use fake patient names, scan imagery, radiology annotations, or controls that imply clinical interpretation. The metaphor supports orientation only.

### Palette

Keep the current color family and formalize it as the design contract:

| Role | Light | Dark |
|---|---:|---:|
| Page | `#e9edef` | `#08090b` |
| Primary surface | `#ffffff` | `#101318` |
| Secondary surface | `#dde3e6` | `#171b21` |
| Primary cyan | `#0a6072` | `#7fd8ea` |
| Recommendation amber | `#7a4f04` | `#efba63` |
| Stop red | `#8f1f2c` | `#f79aa6` |
| Divider | `#c3ccd2` | `#262c34` |

The refactor may adjust derived `color-mix()` percentages for contrast, but it must not introduce additional categorical colors.

### Typography

- Keep the system sans and system monospace stacks.
- Reserve monospace for UIDs, protocol tokens, instrumentation, and compact interface metadata.
- Body text remains at least `1rem` with approximately `1.55-1.65` line height.
- Important interface text must be at least `0.75rem`.
- Evidence badges must be at least `0.6875rem` and remain legible at 200% zoom.
- H3 headings must be visibly subordinate to H2 but clearly larger or heavier than body copy.

## Information architecture

Group the existing section links into six chapters without changing content order:

1. **Orientation**
   - `quickref`
   - `stack-map`
   - `vocabulary`
2. **Protocols and exchange**
   - `dicom-parts`
   - `dimse`
   - `dicomweb`
   - `gateway`
   - `sop-classes`
   - `transfer-syntax`
   - `ihe`
   - `fhir`
3. **Product stack**
   - `identity`
   - `ingestion`
   - `repository`
   - `market`
   - `viewers`
   - `workbench`
   - `reports`
   - `ai`
4. **Assurance and change**
   - `security`
   - `change`
5. **Sourcing and evaluation**
   - `sourcing`
   - `scorecard`
   - `architectures`
   - `questionnaire`
   - `red-flags`
   - `anti-patterns`
6. **Reference**
   - `glossary`
   - `sources`

The current navigation omits `gateway`; the new grouped navigation must include it.

## Required layout

### Command bar

Use one sticky command bar rather than two competing sticky rows. It contains:

- Wordmark or compact page identifier.
- Search field with a visible clear control.
- Current chapter label.
- A `Sections` control at widths where the full navigator is unavailable.
- Theme and print controls.

The command bar must not exceed 56 px in its normal desktop state. At 375 px, controls may wrap into two rows, but the content viewport must retain at least 80% of the initial screen height after the user scrolls.

### Desktop navigator

At approximately 1200 px and wider, use a left section rail beside the main content:

- Six labeled chapter groups.
- All 29 section links.
- Active section state driven by `IntersectionObserver` with a no-JS fallback.
- Current chapter and active section must not rely on color alone.
- The rail may become sticky but must leave room for the command bar.
- Increase the outer shell only as needed, up to approximately 1480 px, so the content column remains useful for wide tables.

At narrower widths, collapse the rail into the `Sections` control. Do not retain a 29-item horizontal scroller.

### Hero launchpad

Keep the current H1, introduction, and version metadata. Add three compact task links immediately below them:

1. `Understand the stack` -> `#stack-map`
2. `Resolve a protocol boundary` -> `#dicom-parts`
3. `Evaluate a product or vendor` -> `#scorecard`

These are navigation aids, not promotional CTA cards. They must look useful in print and remain plain anchor links without JavaScript.

### Chapter dividers and section headers

- Add a distinct chapter divider before the first section in each chapter.
- Give each section a persistent visual number or series label plus one purpose tag: `Lookup`, `Compare`, `Trace`, `Decide`, or `Execute`.
- Keep the existing section note directly under the H2.
- Reduce decorative overlay text that does not improve orientation.
- Use whitespace and surface changes before adding more borders.

## Signature stack map

The stack map remains the most polished and shareable element on the page.

### Desktop map

- Retain all eleven horizontal stack strata and the two cross-cutting capabilities.
- Add a clear lifecycle cue: `Exposure -> Ingest -> Store -> Read -> Report -> Deliver`.
- Render Administration and Security with horizontal text. They may remain in a side rail, but their spanning relationship to every layer must remain explicit through a bracket, rail, or shared background.
- Give every linked stratum an obvious hover, focus, and pointer affordance.
- Distinguish strategic character from sourcing verdict through position and label, not color alone.
- Keep verdict stamps aligned in one consistent column.
- Preserve the bottom-up concept and state it once in the visual.

### Mobile map

- Do not scale the desktop SVG down until its text becomes unreadable.
- Render strata as a single vertical sequence of tappable cards.
- Place the two cross-cutting capabilities in a separate, clearly labeled block.
- Keep all thirteen labels, summaries, verdicts, and destinations.

### Preview image

Regenerate `images/radiology-imaging-software-stack.png` at exactly 1200 x 630 from the finished desktop map. At a displayed width of 600 px, every stratum title and verdict must remain legible. The image contains the map only, not the navigation chrome.

## Table system

Do not apply one automatic mobile transformation to all 36 tables. Classify tables by reading behavior:

1. **Comparison matrix:** preserve rows and columns; use horizontal scrolling, sticky first column, sticky header, and an overflow cue.
2. **Lookup table:** may become labeled row cards below a container-query threshold if every header relationship remains visible.
3. **Worksheet:** preserve the grid, use sticky component names, and provide an explicit horizontal-scroll cue.

Requirements for every table wrapper:

- The page itself never overflows horizontally.
- A shadow or fade indicates additional off-screen columns and disappears at the scroll boundary.
- Keyboard users can focus and scroll the wrapper.
- The table has an accessible label or caption.
- Sticky cells remain opaque in both themes.
- Hover is supplemental; row identity remains clear without it.
- Print removes scrolling and repeats table headers where supported.

## Evidence system

Preserve every evidence label and its meaning. Simplify only the visual family:

- Standards lifecycle: cyan family.
- Regulation and professional guidance: high-contrast neutral family.
- Common practice and architecture patterns: muted neutral family.
- Recommendations and emerging material: amber family.
- Stop or safety conditions: red remains reserved for actual hazards and rejection states.

Add a compact evidence legend near the beginning of the page and a link back to `#evidence-labels`. Exact badge text remains visible; tooltips cannot be the only explanation. Badges must use border style, label, or icon in addition to color.

## Search and find behavior

Replace the current row-only filter behavior with contextual page finding:

- Search headings, section notes, body text, table rows, cards, drawer summaries, checklist labels, UIDs, and code tokens.
- Report both matches and sections, for example `12 matches in 4 sections`.
- Keep the matching section heading and enough surrounding context visible.
- Highlight visible matches with semantic `<mark>` elements or an equivalent accessible treatment.
- Provide next and previous match controls when there is more than one match.
- `/` focuses search only when focus is not already in an editable control.
- `Escape` clears search and restores the previous reading position.
- A visible clear button is available to pointer and touch users.
- Search remains an enhancement. All content is visible and navigable when JavaScript is disabled.

Do not build fuzzy search, indexing, query persistence, or an autocomplete library.

## Evaluation workspace

Treat the scorecard and questionnaire as one coherent evaluation workflow while keeping their existing sections and data models.

- Show a compact saved-progress summary when the reader enters the Sourcing and evaluation chapter.
- Distinguish `Print blank worksheet` from `Print completed assessment`.
- Keep the existing blank-print use case.
- Style destructive clear controls separately from ordinary actions and require an explicit second action before erasing saved work.
- On narrow screens, keep the active component or questionnaire group visible while editing.
- Do not add accounts, synchronization, server storage, export formats, or data transmission.

## Footer cleanup

- Remove Bootstrap utility and icon classes that have no loaded dependency.
- Use text links or small inline SVG icons.
- Present related links as a compact cluster rather than one undifferentiated run of links.
- Preserve every existing destination and the build-note text.

## Responsive behavior

### 1200 px and wider

- Sticky command bar plus left section rail.
- Main content remains at least approximately 900 px wide where the viewport permits.
- Tables use their full comparison layout.

### 768-1199 px

- No permanent left rail.
- Command bar exposes the current chapter and `Sections` control.
- Task launchpad may use three columns when space permits.
- Table wrappers make overflow explicit.

### 375-767 px

- Single-column reading flow.
- Minimum 44 x 44 px touch targets for interactive controls.
- No clipped headings, badges, selects, or map labels.
- Task links stack vertically.
- Lookup tables may use their approved card treatment.
- Horizontal scrolling is confined to comparison and worksheet wrappers.

Use container queries for component-level changes where practical. Media queries remain appropriate for the page shell and navigation mode.

## Print behavior

The full reference and both worksheet states must print deliberately:

- Full-page Print prints the reference with current scorecard and questionnaire values.
- Print blank worksheet prints the relevant worksheet without saved values.
- Print completed assessment prints the scorecard and questionnaire with their current values.
- Hide command bar, section rail, search UI, task launchpad, and nonessential navigation.
- Open all architecture drawers for full-reference printing.
- Preserve chapter titles, section titles, evidence labels, table headers, and URLs where the current stylesheet emits them.
- Avoid blank pages caused by oversized `break-inside: avoid` blocks.
- Keep scorecard, questionnaire, red flags, and identity worksheet usable in grayscale.

## Accessibility and progressive enhancement

- Preserve the skip link and semantic landmarks.
- Navigation controls use correct expanded and current-state attributes.
- Active navigation uses `aria-current="location"`.
- The mobile section control returns focus correctly when dismissed.
- No hover-only information or color-only distinctions.
- Search updates use one restrained live region; do not announce every keystroke as a long message.
- Existing checkboxes and selects retain programmatic labels.
- All content, anchors, tables, and native drawers remain usable with JavaScript disabled.
- Motion stays behind `prefers-reduced-motion: no-preference`.

## Volatile-facts register

Overall staleness profile: **SLOW-DRIFT**, with localized volatile tables.

The design pass does not re-verify these facts, but it must preserve their inline version/date context:

| Area | Drift risk | Re-verification route |
|---|---|---|
| DICOM edition and service definitions | Periodic | Current DICOM standard and edition metadata |
| IHE Radiology profile status | Highest on page | Current IHE RAD Technical Framework and profile status pages |
| FHIR resource/version boundaries | Periodic | Current HL7 FHIR release documentation |
| Open-source component versions | Frequent | Primary project release pages |
| US regulatory and professional guidance | Periodic | FDA, HHS, NIST, and ACR primary sources |

`refresh-status.json` remains owned by the freshness routine and must not be edited during this refactor.

## Cross-link and share contract

- Preserve all current outbound related links.
- Do not add reciprocal links as part of this design-only pass.
- The stack map remains both the screenshot-this artifact and the `og:image` subject.
- Preserve the canonical URL and current social metadata paths.

## Implementation sequence

### Phase 1: Structure and orientation

1. Record the baseline section IDs, table count, `[data-sc]` keys, `[data-q]` keys, and map destinations.
2. Add chapter wrappers or markers without moving substantive section content out of order.
3. Replace the horizontal section scroller with the unified command bar and responsive grouped navigator.
4. Add the hero task links, chapter dividers, section-purpose labels, and active-section behavior.
5. Verify all deep links and no-JS access before continuing.

### Phase 2: Component system

1. Refine type scale, spacing, surfaces, and evidence families.
2. Classify all tables as comparison, lookup, or worksheet.
3. Implement sticky columns, overflow cues, and approved mobile treatments.
4. Refine evaluation controls and print actions without changing storage keys.
5. Clean up the footer dependency remnants.

### Phase 3: Signature map and search

1. Rework the desktop and mobile stack maps.
2. Implement contextual search, match navigation, highlighting, and keyboard behavior.
3. Regenerate the 1200 x 630 preview from the finished map.

### Phase 4: Verification

Run the complete acceptance checklist below. Fix failures before committing the implementation. Delete this spec only after the refactor is complete and verified.

## Acceptance checklist

### Preservation

- [ ] The same 29 existing section IDs exist exactly once.
- [ ] All existing non-navigation deep-link targets remain valid.
- [ ] All stack-map destinations are unchanged.
- [ ] All 120 `[data-sc]` fields and keys are unchanged.
- [ ] All 76 `[data-q]` fields and keys are unchanged.
- [ ] Existing saved scorecard and questionnaire data still loads after the refactor.
- [ ] Substantive headings, paragraphs, table cells, checklist labels, select options, disclaimer, and sources are unchanged except for an explicit allowlist of interface microcopy.
- [ ] Metadata, JSON-LD, canonical URL, and related-link destinations are unchanged.

### Navigation and search

- [ ] All six chapter groups and all 29 section links are present.
- [ ] `gateway` is included in the navigator.
- [ ] Active-section state updates correctly in both scroll directions.
- [ ] Deep-link arrival is not obscured by the sticky command bar.
- [ ] Search finds representative prose, UID, table-row, checklist, and drawer-summary matches.
- [ ] Match counts report matches and sections accurately.
- [ ] Search clear restores content and reading position.
- [ ] The page remains fully navigable with JavaScript disabled.

### Visual and responsive

- [ ] Both themes pass WCAG 2.2 AA contrast for text and controls.
- [ ] Important interface text is at least `0.75rem`; evidence text is at least `0.6875rem`.
- [ ] No page-level horizontal overflow at 375, 768, 1024, 1280, 1440, or 1920 px.
- [ ] Table overflow is confined to its wrapper and visibly signaled.
- [ ] Sticky headers and first columns work in both themes without transparency artifacts.
- [ ] The desktop and mobile maps contain all thirteen layers and readable verdicts.
- [ ] Keyboard focus remains visible throughout navigation, tables, map links, search, scorecard, and questionnaire.
- [ ] At 200% zoom, controls and labels do not overlap or become unreachable.

### Evaluation and persistence

- [ ] Scorecard and questionnaire progress counts are accurate.
- [ ] Blank and completed print actions produce the stated state.
- [ ] Clear controls cannot erase saved work through a single accidental click.
- [ ] No interaction transmits or stores data outside the browser.

### Print and preview

- [ ] Full reference print is readable in grayscale and does not omit drawer content.
- [ ] Blank worksheet print is actually blank.
- [ ] Completed assessment print includes current values.
- [ ] No avoidable blank pages or clipped tables appear in print preview.
- [ ] `images/radiology-imaging-software-stack.png` is exactly 1200 x 630.
- [ ] Preview labels remain legible at 600 px displayed width.

### Repository gates

- [ ] `python scripts/seo_check.py radiology-imaging-software-stack.html` passes.
- [ ] The repository's focused HTML/link/asset checks pass for the page.
- [ ] Browser console is clean except for an accepted favicon miss, if present.
- [ ] Theme, navigation, search, persistence, map links, print, and no-JS behavior receive manual browser QA.
- [ ] Only the HTML file and regenerated preview image are changed by implementation, plus deletion of this completed spec.

## Definition of done

The refactor is complete when a first-time desktop reader can identify the current chapter and section at any scroll position, a mobile reader can reach any section without traversing a 29-link scroller, a vendor-call user can find a protocol or UID with surrounding context, and an evaluator can safely resume, print, or clear locally saved work. All preservation and repository gates must pass, and the redesigned stack map must remain the page's clearest and most polished artifact.
