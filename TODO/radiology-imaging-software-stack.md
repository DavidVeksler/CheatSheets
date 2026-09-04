# Spec: Radiology imaging software stack — DICOM, PACS, viewers, build vs buy

**Target file:** `radiology-imaging-software-stack.html`
**Source manuscript:** `C:\Users\veksl\OneDrive\Desktop\complete-radiology-imaging-software-stack-guide.md`
(2,500-line working draft, "A Complete Guide to the Radiology Imaging Software Stack"). The
page is a *compression* of that manuscript into terminal-reference form, not a summary of it.

## Hard exclusion: internal material

The manuscript contains a section titled **"Internal Antech case-study sources"** (15 internal
documents, named authors, Teams threads, emails) plus scattered "Internal case study" and
"Case-study lesson" paragraphs that reference Antech, AIS, and named colleagues. **None of it
goes on the page.** Do not name Antech, AIS, any internal document, any person, or any internal
system. Where a case-study lesson is a general truth that public standards reasoning supports
(e.g. "a proprietary image-delivery contract blocks viewer replacement"), it may appear as an
unattributed entry in Anti-patterns or Red flags. Nothing else survives. Also drop Part XIX
(editorial plan), "Additional research still worth doing", and the "Final decision memo
template" prose; the memo's *headings* may be reused as the checklist skeleton in §22.

## Why this topic

The site has veterinary-diagnostics, medical-school-curriculum, microservices, API design and
observability sheets, and nothing connecting clinical imaging to software architecture. The web
has DICOM *tag* cheat sheets (dictionary lookups) and vendor whitepapers (PACS marketing), and
nothing that puts the DIMSE service table, the DICOMweb endpoint table, the IHE profile
maturity list, the FHIR imaging resource map, and a component-level build-vs-buy scorecard on
one page for the person who has to make a sourcing decision or design an integration.

**Niche utility test (README Rule 0):** the reader keeps this open *during* a vendor demo,
a conformance-statement review, an architecture review, or while drafting a procurement memo.
The value is the exact identifiers (service names, transfer-syntax UIDs, SOP class UIDs, tag
numbers, profile acronyms with maturity status) side by side, plus the questionnaire and red
flags they tick off live. An AI chat answer cannot replace a page you work *through*. Shape:
comparison tables with exact specs + procedure/checklist reference.

Differentiator: the manuscript's **evidence-label discipline**. Every strong claim on the
page carries a small badge (STANDARD, IHE PROFILE: FINAL TEXT, IHE PROFILE: TRIAL
IMPLEMENTATION, REGULATORY CONTEXT, PROFESSIONAL GUIDANCE, COMMON PRACTICE, ARCHITECTURE
PATTERN, RECOMMENDATION, EMERGING). No other imaging reference separates "the standard says"
from "vendors usually do" from "we think you should." That distinction *is* the page.

## Targeting

- **Primary query:** `PACS architecture`
- **Secondary:** `DICOMweb vs DIMSE`, `PACS vs VNA`, `DICOM conformance statement checklist`,
  `IHE radiology profiles list`, `PACS vendor evaluation checklist`, `build vs buy PACS`,
  `DICOM transfer syntax UID list`, `teleradiology platform architecture`, `veterinary PACS`
- **Mode:** research-then-return. First arrival is a search on one of the lookups; return
  visits are bookmarks during a procurement or integration project. Stable `id` anchors on every
  table and every scorecard row.

## Draft title / H1 / meta

- `<title>`: `Radiology Imaging Stack: DICOM, PACS, Viewers, Build vs Buy` (59 chars)
- **H1:** `The Radiology Imaging Software Stack: From Exposure to Answer`
- **Meta description (draft, verify 150–200 with `scripts/seo_check.py`):**
  `DICOM services, DICOMweb endpoints, transfer syntaxes, IHE radiology profiles, FHIR imaging resources, PACS vs VNA, viewer tiers, radiologist workflow, and a component build-vs-buy scorecard for human and veterinary imaging.`

## Reader outcome

Sitting across from a PACS or cloud-DICOM vendor, the reader can ask for the conformance
statement and know which sections to open, tell a DIMSE-only archive from a DICOMweb one and
know when a gateway is needed, distinguish a Final Text IHE profile from a trial one, name the
FHIR resource that references a study without holding pixels, classify each of 15 stack
components as commodity / enabling / differentiating, and walk away with a filled-in
scorecard and a ticked questionnaire instead of a slide deck.

## Success metric

Organic entries on the secondary lookup queries (transfer syntax UIDs, IHE profile list,
DICOMweb vs DIMSE) that feed the page; **print events and return-direct traffic** on the
scorecard and questionnaire; deep-link traffic to table anchors. This is also a
personal-study page for David's day job, so accuracy over reach.

## Jurisdiction scope

Standards (DICOM, IHE, HL7 FHIR) are international. Regulatory rows are US-labeled: HIPAA
Security Rule (human health, covered entities and business associates), FDA SaMD / AI-enabled
device list. One line each for EU MDR and GDPR as "also applies, not covered here." State once,
prominently in the security section: **veterinary imaging generally falls outside HIPAA and
FDA medical-device scope; verify for your jurisdiction and for any human-health data your
system also touches.** Do not repeat per row.

## Reading conditions

Architect or product leader at a desk, dual monitor, often with a vendor call or a
conformance-statement PDF in the other window; sometimes printing the scorecard and
questionnaire for a meeting. Consequences: dense tables with sticky headers and zebra rows,
`overflow-x: auto` wrappers, monospace for every UID / tag / service name so they can be
copied exactly, and a **print stylesheet that gets the scorecard, questionnaire, red flags,
and the source-of-truth worksheet onto clean greyscale pages** with checkboxes rendered as
empty squares. Dark theme is the metaphor (below) but `prefers-color-scheme` rules.

## Visual identity

**Metaphor: the reading room.** Dark-first, near-black surfaces like a diagnostic display in a
dim room, greyscale-heavy, with two accent colors borrowed from viewer overlays: a cool cyan
for standards/normative content and an amber for recommendations and warnings. Light mode is
the "lightbox": pale grey film-viewer paper, same accents darkened for contrast. Section
headers carry a small monospace corner overlay in the style of a viewer's DICOM tag overlay
(e.g. `SERIES 04 / STANDARDS` top-left, `W:400 L:40` decoration top-right) — decorative,
`aria-hidden`, and removed in print. Fonts: system sans for body, system monospace
(`ui-monospace, "Cascadia Code", Consolas, Menlo, monospace`) for identifiers. No web fonts
required; if one is used, follow the crypto-exchange-architecture.html pattern.

**Evidence badges** are a first-class component: small uppercase monospace chips, one color
per label family (normative = cyan outline, IHE maturity = cyan filled with status text,
regulatory = neutral, guidance/common practice = grey, recommendation = amber). Every table
that mixes claim types has a badge column or an inline badge per row.

**Human / veterinary pairing:** wherever the manuscript pairs contexts, use a two-column
"🏥 Human | 🐾 Veterinary" callout with `aria-label`s, never emoji alone as the label.

### Signature element: the stack map

An inline SVG of the complete imaging stack as horizontal strata, read bottom-up like a
geological section: **Modalities → Edge gateway / uploader → Ingestion & orchestration →
Identity reconciliation → DICOM repository → DICOMweb / API layer → Workflow & case state →
Viewers (diagnostic / review / customer) → Radiologist workbench → Reporting → Delivery &
integration (EHR / PIMS) → Administration, support, observability (a vertical bar spanning all
layers) → Security & audit (second vertical bar).** Each stratum is tinted by strategic
character (commodity / enabling / differentiating, per manuscript §28) with a legend, and
carries a stamped default verdict from §33 (BUY / BUILD / BUY+CUSTOMIZE / OPEN SOURCE+EXTEND /
OUTSOURCE). Each stratum is an `<a href="#section">` so the map is the page's table of
contents. At 375 px it becomes a single vertical column of full-width strata (same SVG,
`viewBox` swap via a `<picture>`-style second SVG or CSS-hidden duplicate — implementer's
choice, but test it). Build this first and best. It is the og:image.

## Content approach

Every table gets an `id`. Numbers in this spec are anchors (README Rule 1): verify against the
current DICOM edition at dicomstandard.org/current, PS3.6 for tags and UIDs, profiles.ihe.net/RAD
for profile status, hl7.org/fhir for resources, and the ACR/NIST/FDA/HHS pages in the source
list. If a UID or status cannot be verified, omit the row.

1. **Quick Reference strip** (top, one screen): the DICOM information hierarchy with its UIDs
   (Patient → Study `(0020,000D)` → Series `(0020,000E)` → SOP Instance `(0008,0018)` → Frame);
   the DIMSE service table; the DICOMweb endpoint table; default ports (104 is the registered
   DICOM port; 11112 is the common unprivileged alternative — verify); AE Title = up to 16
   characters (verify PS3.5 AE VR); and the five-word vocabulary ladder (standards support →
   conformance → compatibility → interoperability → workflow fitness).

2. **Stack map** (signature element, above).

3. **Vocabulary that must not be confused.** Two tables from the manuscript's evidence policy:
   (a) the *prescriptive vocabulary* table (must/shall, is required by, conforms to, supports,
   should, commonly, can/may, we recommend, in this case study → when each is allowed);
   (b) the *evidence labels* legend that defines every badge used on the page. Plus a
   three-line "what DICOM does not provide" list drawn from §4 (no staffing model, no pricing,
   no customer onboarding, no finished viewer, no cloud architecture, no product analytics).

4. **DICOM parts table** — PS3.1 through PS3.22 (current edition, name the edition e.g.
   "2026a" — verify): part, title, what it governs, "open it when…". ≥ 20 rows. Badge: STANDARD.

5. **DIMSE services table** — C-ECHO, C-STORE, C-FIND (Q/R and Modality Worklist), C-MOVE,
   C-GET, N-ACTION / N-EVENT-REPORT (Storage Commitment), N-CREATE / N-SET (MPPS), plus the
   association concepts (AE Title, presentation context, abstract syntax, transfer syntax,
   SCU/SCP roles). Columns: service, SCU/SCP roles, what it does, the gotcha (C-MOVE requires
   the destination AE to be pre-configured on the SCP and opens a *new* inbound association —
   the firewall trap; C-GET returns on the same association; C-FIND has hierarchical vs
   relational query models). ≥ 10 rows.

6. **DICOMweb table** — QIDO-RS, WADO-RS (study / series / instance / frames / metadata /
   rendered / bulkdata), STOW-RS, WADO-URI, UPS-RS (worklist). Columns: service, HTTP method,
   URL template (`/studies/{study}/series/{series}/instances/{instance}/frames/{frames}`),
   media types (`application/dicom`, `application/dicom+json`, `multipart/related`), gotcha
   (rendered vs pixel data; frame numbering is 1-based; transfer-syntax negotiation via
   `Accept`). ≥ 8 rows.

7. **DIMSE vs DICOMweb comparison** — transport, auth model, firewall posture, who initiates,
   query model, retrieve semantics, partial/frame retrieval, rendered output, typical
   consumers (modalities vs browsers), when you need a gateway. Then the four product
   implications from §5 as a callout. Badge: ARCHITECTURE PATTERN.

8. **SOP classes beyond images** — table of commonly encountered SOP Classes with UID:
   CT Image, MR Image, US Image / US Multi-frame, DX (for presentation / processing), CR,
   Enhanced CT / MR, Secondary Capture, Basic Text SR, Comprehensive SR, Comprehensive 3D SR,
   Key Object Selection Document, Segmentation, Grayscale Softcopy Presentation State,
   Encapsulated PDF, X-Ray Radiation Dose SR, Parametric Map, Encapsulated STL (as an
   "also exists" line). UID root `1.2.840.10008.5.1.4.1.1.` — verify every suffix in PS3.6
   Annex A. Columns: object, UID, what it carries, why a product leader cares (e.g. GSPS is
   how annotations survive viewer replacement; KOS is how IOCM rejections are expressed).
   ≥ 14 rows. Badge: STANDARD.

9. **Transfer syntaxes and compression** — table: name, UID (`1.2.840.10008.1.2`, `.1`, `.2`
   retired big-endian, `.4.50` JPEG baseline, `.4.51`, `.4.57`, `.4.70` JPEG lossless SV1,
   `.4.80/.81` JPEG-LS, `.4.90/.91` JPEG 2000, `.4.201/.202/.203` HTJ2K, `.5` RLE, MPEG-4
   variants, Deflated Explicit VR LE `.1.99`) — verify all; lossy or lossless; typical use;
   browser-decodable natively or via WASM. ≥ 12 rows. Then the lossy-compression rules:
   Lossy Image Compression `(0028,2110)`, ratio `(0028,2112)`, method `(0028,2114)`, and
   Derivation Description; the ACR–AAM–SIIM electronic-practice standard's position on
   irreversible compression as PROFESSIONAL GUIDANCE (quote its actual stance after reading
   it; do not invent a ratio). Manuscript §13 validation layers: automated validity → decoder
   matrix across viewers → clinical quality review → downstream AI behavior. Two-line
   🏥/🐾 callout: mammography constraints vs veterinary practice. Anti-pattern: "one ratio is
   universally safe."

10. **IHE Radiology profiles** — table: acronym, full name, problem solved, maturity status
    as published at profiles.ihe.net/RAD (Final Text / Trial Implementation / retired), badge
    per row. Rows: SWF, SWF.b, PIR, CPI, PGP, ARI, KIN, RWF, ED, PDI, REM, XDS-I.b, XCA-I,
    IOCM, BIR, WIA, WIC, IID, IMR, IRA, plus MRRT (Management of Radiology Report Templates)
    and any others you verify. ≥ 18 rows. IMR and IRA must carry the "not yet recommended for
    production use" note from their published pages. Then the maturity ladder as a four-step
    strip (Public Comment → Trial Implementation → Final Text → Deprecated).

11. **FHIR imaging resources** — table: resource, role, DICOM mapping where it exists
    (ImagingStudy.identifier ↔ Study Instance UID as `urn:oid:`, `series.uid`, `instance.uid`,
    `series.modality`, `numberOfSeries/Instances`, `endpoint` → WADO-RS), what it does *not*
    hold. Rows: Patient, Practitioner, Organization, Encounter, ServiceRequest, ImagingStudy,
    DiagnosticReport, Observation, Task, DocumentReference, ImagingSelection (R5), Endpoint.
    ≥ 11 rows. State FHIR version (R5 current normative content; R6 status — verify). Callout:
    HL7's own statement that DICOM instances are not stored in ImagingStudy and a WADO-RS
    server is still required. One line on HL7 v2 (ORM/OMI orders, ORU^R01 results) because
    real sites still run it.

12. **Identity and source of truth** — the manuscript §53 worksheet, filled in with DICOM
    tags rather than blanks: entity, stable identifier, DICOM representation (Patient Name
    `(0010,0010)`, Patient ID `(0010,0020)`, Issuer of Patient ID `(0010,0021)`, Accession
    Number `(0008,0050)`, Referring Physician `(0008,0090)`, Institution Name `(0008,0080)`,
    Study Instance UID, Requested Procedure ID `(0040,1001)`), FHIR representation, typical
    update owner (RIS/EHR/PIMS vs PACS), correction workflow. Veterinary rows use the
    veterinary tags: Responsible Person `(0010,2297)`, Responsible Person Role `(0010,2298)`,
    Patient Species Description `(0010,2201)`, Patient Breed Description `(0010,2292)`,
    Patient Sex Neutered `(0010,2203)` — verify each in PS3.6. ≥ 10 rows. Then the three
    reconciliation flows as short numbered lists: MWL-matched, unscheduled/emergency
    (PIR), and wrong-patient correction after read (IOCM + report addendum). Badge the
    "AE Title is not a user credential" line as RECOMMENDATION and put it here *and* in §18.

13. **Ingestion & failure scenarios** — table from §9: scenario (duplicate SOP Instance UID
    with different bytes, partial study / late series, unknown calling AE Title, unsupported
    transfer syntax, unscheduled study with no order, off-hours retransmit storm, clock skew
    between modality and server, wrong character set `(0008,0005)`, oversized multi-frame,
    private tags stripped by a middlebox), detection signal, correct handling, product
    surface it needs (admin tool). ≥ 10 rows. Badge: COMMON PRACTICE / ARCHITECTURE PATTERN.

14. **Repository, storage lifecycle, scale** — (a) logical responsibilities of the repository
    (§11) as a checklist; (b) typical study size by modality table (CR/DX, CT, MR, US incl.
    cine, mammography incl. tomosynthesis, PET-CT, dental, veterinary DR) — anchors only, give
    a range and cite where it came from or drop the row; (c) storage tier decision table
    (hot / cool / archive: latency, retrieval cost model, where it is *not* allowed = the
    synchronous clinical path); (d) the **exit test** from §11 as a five-item box (bulk
    export of original objects + metadata + presentation states + reports + audit, at what
    throughput). Anti-pattern: object storage ≠ archive; capacity price ≠ total cost.

15. **PACS, VNA, and the market categories** — one comparison table from §38–46: Full PACS,
    Managed cloud DICOM service, DICOM server / archive software, VNA, Viewer categories
    (diagnostic workstation / zero-footprint diagnostic / clinical review / patient-customer /
    SDK / rendering library), Radiologist workflow & reporting platform, Image exchange &
    sharing, Teleradiology service. Columns: what it typically includes, what it should *not*
    be assumed to include, the one question that exposes the boundary. Then a focused
    **PACS vs VNA** row-pair from §14. Named open-source examples allowed as *examples* only
    (Orthanc, dcm4chee, DCMTK, pydicom, fo-dicom, OHIF, Cornerstone3D, Weasis) with license
    and current major version dated — no commercial vendor names, no rankings.

16. **Viewer tiers and evaluation** — (a) three-tier table (diagnostic / clinical review /
    customer-or-patient): intended user, regulatory posture (diagnostic use may be a
    regulated device claim — REGULATORY CONTEXT, US), display requirement (PS3.14 GSDF
    calibration for diagnostic; ACR–AAPM display standard as PROFESSIONAL GUIDANCE), must-have
    tools. (b) architecture choices: thick client, server-side rendered zero-footprint,
    browser-side decode over DICOMweb (WASM/WebGL), hybrid — pros, cons, bandwidth, offline.
    (c) **evaluation matrix** ≥ 15 criteria: GSPS read *and* write persistence, hanging
    protocols, priors auto-fetch, MPR/MIP/3D, measurement calibration (Pixel Spacing vs Imager
    Pixel Spacing gotcha), cine, window/level presets, multi-monitor, embedding/iframe and
    auth handoff, keyboard accessibility, transfer-syntax decoder coverage, annotation
    storage location, audit of who viewed, print/export, mobile. 🐾 callout: veterinary
    measurements (vertebral heart score, TPLO tibial plateau angle, Norberg angle) are
    absent from general-purpose viewers — verify each measurement name. Anti-pattern:
    "selecting a viewer from screenshots."

17. **The radiologist workbench** — §17 as a state table: intake → readiness (all series
    present, priors fetched, order matched) → assignment (rules, credentials, region,
    subspecialty, load) → interpretation → reporting → QA/peer review. Columns: state,
    entry condition, exit condition, metric (turnaround, time-in-state, reassignment rate),
    failure mode. Then the reporting sub-table: structured vs free text, templates (MRRT),
    speech, critical-results communication per ACR communication parameter
    (PROFESSIONAL GUIDANCE), addendum vs amendment. ≥ 8 states.

18. **Reports and delivery** — report status lifecycle (preliminary / final / addendum /
    corrected) and the delivery-channel table: HL7 v2 ORU^R01, FHIR DiagnosticReport, DICOM
    Basic Text / Comprehensive SR, Encapsulated PDF, portal, email link, fax (still real).
    Columns: channel, what it carries, image linkage, correction propagation.

19. **AI orchestration** — use-case table (triage/prioritization, detection, quantification,
    quality/protocoling, worklist routing, report drafting); platform capability checklist
    from §19 (routing, versioning, provenance, feedback, monitoring); **result encoding**
    table (DICOM SR TID 1500 measurement report, SEG, Parametric Map, Secondary Capture,
    FHIR Observation) with the rule that every result references source SOP Instance UIDs
    and a model version; FDA AI-enabled devices context as REGULATORY CONTEXT (US, human
    health) with a dated count only if you fetch it. Anti-pattern: "AI output as
    unversioned JSON disconnected from source images."

20. **Security, privacy, clinical safety** — (a) NIST SP 1800-24 control areas as a
    checklist (asset inventory, segmentation, access control, TLS for DICOM, audit, backup,
    vendor remote access); (b) DICOM PS3.15 profiles: Basic TLS Secure Transport, Audit
    Trail (ATNA), Basic Application Level Confidentiality (de-identification) with its
    option names (Clean Pixel Data, Retain Longitudinal Temporal Information, Retain Patient
    Characteristics, etc. — verify names); (c) **where identifying information hides** table
    from §24: tags, private tags, burned-in pixels `(0028,0301)`, overlays, structured
    reports, encapsulated documents, file names, audit logs, thumbnails, AI outputs;
    (d) HIPAA Security Rule scope line + the veterinary-scope line (jurisdiction section
    above); (e) clinical safety as a system property (§25): wrong-patient, wrong-side,
    missing series, stale prior, lossy artifact, display miscalibration → detection control.

21. **Change, correction, migration** — (a) IOCM change scenarios (rejected for quality,
    rejected for patient safety, incorrect modality worklist entry, data retention expired)
    expressed as KOS with rejection reason codes — verify codes; (b) correction propagation
    matrix: what must update where when patient identity changes after read (archive,
    viewer cache, worklist, report, EHR/PIMS, AI results, audit); (c) **migration validation
    ladder** from §27: byte count → instance count per study → SOP Instance UID set
    equality → header hash → viewer-open sample → clinical sample review → dual-run
    monitoring → exit criteria. Anti-pattern: "validated with byte counts alone."

22. **Sourcing decisions** — (a) the §28 commodity / enabling / differentiating table
    (13 rows) with badge RECOMMENDATION on the strategy column; (b) buy / build / hybrid /
    outsource as a four-column "favored when" matrix (§29–32); (c) the **component
    scorecard** (§33): 15 component rows × 7 criteria columns (strategic value, market
    maturity, customization need, clinical risk, integration difficulty, operating burden,
    portability risk) rendered as a fillable grid — each cell a `<select>` or a three-state
    Low/Med/High toggle, plus a strategy column with the seven allowed values; **state
    persists in `localStorage` with feature detection**; a "print blank" affordance prints
    empty cells; a filled default row set is *not* shipped (the reader fills it) but the
    stamped verdicts in the stack map show the manuscript's default lean per layer,
    labeled RECOMMENDATION; (d) reference strategies A–E (§34) as a five-column table:
    advantages, disadvantages, best fit, exit risk.

23. **Reference architectures** — five cards (§47–51: small clinic, hospital/referral
    center, teleradiology platform, multi-tenant cloud product, hybrid legacy
    modernization), each a numbered component list + "decision emphasis" list. Compact.

24. **Vendor questionnaire, PoC plan, red flags** — the §35 questionnaire (≥ 40 items across
    standards, archive & portability, viewer, workflow & reporting, security & operations,
    commercial & roadmap) as real `<input type="checkbox">` items with `localStorage`
    persistence and a "clear" control; the §36 PoC plan (data set, workflow tests, viewer
    tests, operational tests, clinical validation) as a checklist; the **14 red flags** (§37)
    styled as IOCM-style "rejection notes" — the page's second most shareable block.

25. **Common mistakes / anti-patterns** (mandatory) — the manuscript's 15-item list, each
    expanded to one line of consequence and one line of fix.

26. **Glossary** — ≥ 30 terms (manuscript glossary plus UPS, MPPS, ATNA, KOS, HTJ2K, GSDF,
    SCU/SCP, MRRT, TID 1500).

27. **Sources** — public authoritative sources only, from the manuscript's list: DICOM
    current edition and PS3.2/PS3.6/PS3.15/PS3.18, IHE profiles pages, IHE RAD framework,
    IHE IMR/IRA pages, HL7 FHIR ImagingStudy / DiagnosticReport / ImagingSelection, ACR
    practice parameters (electronic practice, display, communication), NIST SP 1800-24,
    HHS HIPAA Security Rule, FDA AI SaMD pages, DICOM de-identification guidance. Each with
    "accessed <Mon YYYY>".

28. **Related sheets footer** per the cross-link map, using the `data-seo-related-links`
    block pattern from existing pages.

## Interactivity budget

Two stateful elements only: the component scorecard (§22c) and the questionnaire/PoC
checklists (§24). Both `localStorage` with feature detection and graceful fallback. The stack
map is anchor links + `:hover`/`:focus-visible` highlight, no JS required. Native
`<details name="…">` for the reference-architecture cards and the glossary if collapsed.

## Volatile-facts register

**Overall: SLOW-DRIFT.**
- DICOM edition label (several releases per year, e.g. 2026a/b/c): date the edition inline;
  UIDs and tags themselves are stable.
- IHE profile maturity statuses (IMR, IRA, WIA, WIC, IID may move TI → Final Text): re-check
  profiles.ihe.net/RAD quarterly; this is the most likely thing to rot.
- FHIR version status (R5 vs R6 ballot/normative): annual.
- FDA AI-enabled device list count: quarterly; only present if fetched with date.
- Open-source project versions and licenses (OHIF, Cornerstone3D, Orthanc, dcm4chee, Weasis):
  semi-annual.
- HTJ2K adoption in browsers/viewers: EMERGING badge; re-check annually.
- ACR practice parameter revision years: check on each freshness pass.

## Index category

`Software & DevOps` (architecture readers). Add to `$categoryMap` in `category-map.php`.

## Cross-link map

- **Internal outbound:** `veterinary-diagnostics.html` (imaging section — link both ways),
  `medical-school-curriculum.html`, `microservices.html`, `api-design-rest-graphql-grpc-webhooks.html`,
  `observability-logs-metrics-traces-slos.html`, `databases.html`, `compression-algorithms.html`
  (lossless/lossy background — link both ways), `linux-server-hardening.html`,
  `aws-vs-azure.html`.
- **Reciprocal inbound:** one line each from `veterinary-diagnostics.html` and
  `compression-algorithms.html`.
- **External outbound:** standards bodies and regulators only (dicomstandard.org, nema.org
  PS3 pages, ihe.net / profiles.ihe.net, hl7.org/fhir, acr.org, nist.gov, hhs.gov, fda.gov).
  Open-source project home pages allowed for the named examples. No vendor links.

## og:image / shareable artifact

The stack map (§2) at 1200×630, dark theme, verdict stamps visible. Second artifact: the red
flags block (§24), which should screenshot cleanly as a standalone card.

## Density targets

DICOM parts ≥ 20 rows; DIMSE ≥ 10; DICOMweb ≥ 8; SOP classes ≥ 14; transfer syntaxes ≥ 12;
IHE profiles ≥ 18; FHIR resources ≥ 11; identity worksheet ≥ 10; ingestion failures ≥ 10;
market categories 8; viewer evaluation ≥ 15 criteria; workbench states ≥ 8; scorecard 15 × 7;
questionnaire ≥ 40 items; red flags 14; anti-patterns 15; glossary ≥ 30. Total substantive
entries well above the 20-entry floor; expect a 600–900 line HTML file in the style of
`crypto-exchange-architecture.html`.

## Anti-goals

No commercial PACS vendor names, no product rankings, no pricing, no affiliate framing. No
clinical interpretation guidance (this is a systems page, not a radiology page). No internal
material of any kind (see the exclusion block at the top). No visible "Last verified" line
and no JSON-LD `dateModified`. Do not restate AGENTS.md invariants; they apply.
