# Rocket equation calculator: implementation outline

User authorized proceeding with a provisional concept on 2026-11-04; keyword
volume remains unverified. Research and rationale:
`docs/research/2026-11-04-titan-concept.md`. Ship locally and push; no deployment.

Title: Rocket Equation Calculator: Chemical, Ion & Fusion (50 characters).
H1: Rocket equation calculator. Meta description: Calculate delta-v, propellant
mass and burn time. Compare chemical, ion, nuclear thermal and fusion propulsion,
with sourced examples and Titan's fictional fleet. Category Engineering & Science,
hub `/engineering-science`. Global audience; preliminary spacecraft design at a
desk or on a phone. Readable at 375 px and in print. Search success and freshness
requirements remain in the research brief.

## Outline review before HTML

1. Fundamentals: quick reference with eight formulas and units; final mass includes
   payload and reserves; Isp uses standard gravity, not destination gravity.
2. Working knowledge: one calculator with vehicle/mission modes and thrust/jet
   power constraint; presets for chemical, ion and three Titan designs; live
   propellant versus exhaust-velocity plot plus fixed-jet-power thrust comparison;
   three fully worked examples; eight propulsion categories in a reference table.
3. Edge/advanced: pressure thrust and axial-jet model limits, low-thrust trajectory
   mismatch, staging, power source efficiency and waste heat, changing mass and
   acceleration, safe input bounds, delta-v versus speed and flight time.
4. Common mistakes: at least eight concrete corrections. Related sheets and a
   primary-source register. Titan Explore block is clearly a fictional design
   study set in 2100. Contextual UTM links point into fleet, fusion and chemistry.

Signature: responsive SVG chart with separate, clearly labelled axes for
propellant fraction and thrust at fixed directed jet power. Numeric accessible
summary updates with it. A 1200x630 crop of the calculator/chart is the OG image.

Complete table rows: cold gas; hydrazine monopropellant; solid; electrothermal;
electrospray; gridded ion; Hall effect; hydrogen nuclear thermal; DFD fusion study;
Titan Long Passage. The first seven take **small-spacecraft survey** values from
NASA Table 4-1, not universal limits. Nuclear thermal uses NASA 20150021872 (a
design capability, not a flown engine). DFD uses Razin 2014's explicit design
56.5 km/s; do not equate its source power with directed jet power. Titan's
200 km/s is a separate fiction/challenge value.

Fully populated exemplar: Cold gas | pressure energy | Isp 40–110 s | 10 μN–3.6 N
| selected small-spacecraft systems, NASA Table 4-1, accessed 2026-11-04. Use for
small impulses; low Isp costs propellant on large delta-v jobs. Derived exhaust
speed is 0.392–1.079 km/s using 9.80665 m/s²; no manufacturer claim inferred.

Three worked examples: 100 t to 10 t at 350 s, 1 MN chosen thrust; 1.2 t to 1 t
at 3,000 s and 0.1 N (illustrative ion model); Long Passage 10,000 t, 100 km/s,
200 km/s exhaust, 63.7 kN chosen in Titan. Compute exact outputs in the page and
independently in QA. At least 20 substantive entries across the sheet.

Primary-source mapping: NASA Glenn rocket equation and specific impulse pages
for formulas and pressure thrust; BIPM VIM 2.12 for standard gravity; NASA
19760011112 for jet power; NASA small-spacecraft Table 4-1 for surveyed ranges;
NASA NTRS 20150021872 for nuclear thermal; Razin 2014 Princeton publication for
DFD. Titan generated vehicle JSON for fictional inputs. Accessed 2026-11-04.

QA: independent numerical acceptance values, inverse modes, constant-power
coupling, unit conversion, presets, invalid/zero/extreme inputs, shared URL
round-trip, local clipboard failure fallback, light/dark mobile/desktop overflow,
keyboard labels/focus, axe serious/critical, print, no console errors, SEO,
catalog, discovery and repository deploy preflight without deployment.
