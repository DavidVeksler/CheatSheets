# The Data Center Power Chain: Grid to GPU

Target file: `datacenter-power-chain.html`

## Why this topic

Power is now the binding constraint on AI buildout — interconnect queues, not chips, gate new capacity — yet there is no single-page reference explaining the chain from utility interconnect to GPU socket. The content is scattered across utility filings, EE textbooks, and vendor UPS marketing. Almost entirely STABLE physics and process content, giving this the best evergreen durability of the cluster. Strongest brand fit: infrastructure literacy for AI strategy conversations, exactly the analyst positioning the site is building.

## Targeting

- **Primary query:** how do data centers get power
- **Secondary queries:** data center power chain explained; grid interconnection queue data center; behind the meter power data center; data center ups and switchgear basics; why do data centers use diesel generators
- **Mode:** Research (learning intent; secondary audience: journalists and analysts needing accurate framing)
- **Title:** The Data Center Power Chain, Grid to GPU: How AI Facilities Get Power
- **H1:** The Power Chain: Grid to GPU
- **Meta description:** How power reaches an AI data center: interconnection queues, substations, switchgear, UPS, busways, and rack PDUs — plus behind-the-meter gas turbines and SMRs, explained end to end.
- **Reader outcome:** A technically literate reader can trace a watt from the transmission line to a GPU socket, explain where the losses and failure points are, and understand why interconnect queues and behind-the-meter generation dominate current siting decisions.
- **Success metric:** ≥200 organic sessions/month by month 6; cited/linked as the explainer by at least one external post or newsletter.
- **Volatile-facts register:**
  - Electrical architecture (voltage steps, UPS topologies, redundancy schemes N/N+1/2N, loss percentages): STABLE
  - Interconnect queue durations by region, typical MW of new campuses: SLOW-DRIFT (annual)
  - Named projects (specific behind-the-meter deployments, SMR announcements), pending legislation: VOLATILE — keep to a small clearly-dated sidebar, not load-bearing content
- **Index category:** [VERIFY against category-map.php]
- **Jurisdiction/geographic scope:** US-centric for grid/regulatory content (ISO/RTO structure), physics is global; state scope explicitly
- **Reading conditions:** Desktop long-read; diagram must survive mobile. Print: diagram + loss table.
- **Cross-link map:** Hub link to/from `ai-infrastructure-numbers.html`; from `datacenter-cooling-thresholds.html` (cooling as facility load); to `data-center-community-impact.html` (rate-design section is the technical backing for the civic page's bill claims). [VERIFY existing corpus.]

## Content approach

- **Quick-reference block (top):** The chain in one horizontal strip — Generation → Transmission (~115–500kV) → Substation → Medium voltage → Switchgear → UPS → PDU/busway → Rack → GPU — with typical voltage and loss at each hop.
- **Fundamentals:** Why a data center is a grid customer like no other (flat 24/7 load, MW scale, power quality sensitivity); what an interconnection request actually is and why queues take years.
- **Working knowledge:** Section per stage — substation and transformer basics, redundancy topologies (N, N+1, 2N, catcher blocks), UPS technologies (double-conversion vs line-interactive, battery vs flywheel), why AI halls are shifting 208V → 415/480V distribution, diesel generator sizing and why they exist.
- **Edge/advanced:** Behind-the-meter generation decision table (gas turbines, fuel cells, SMRs, solar+storage) — why 46 planned centers totaling ~56 GW plan to skip the grid entirely; load-shape problems AI training creates (rapid MW-scale swings, the ~1,500 MW disconnection event class NERC has flagged); rate design and large-load tariffs.
- **Major tables:**
  1. The chain (signature companion): ~9 rows, stage × voltage × function × typical loss × failure mode.
  2. Redundancy topologies: ~4 rows (N/N+1/2N/distributed-redundant × cost × availability × when used).
  3. Behind-the-meter options: ~5 rows (gas turbine, recip engines, fuel cell, SMR, solar+storage × MW scale × lead time × $/MW × regulatory posture).
- **Common mistakes:** Confusing backup (generators) with ride-through (UPS); assuming grid power is the only path; equating nameplate campus MW with actual draw; assuming interconnect approval means power delivery; treating diesel gensets as routine power sources rather than emergency assets.

## Research sources

- Primary: FERC/ISO interconnection process documentation (PJM, ERCOT), NERC reliability reports, LBNL interconnection-queue studies, Uptime Institute topology definitions, EPRI publications, utility integrated resource plans (Dominion) for queue/load figures, Cleanview or equivalent for behind-the-meter project counts.
- **Must not recall from memory:** queue durations, loss percentages, GW totals, project counts, tariff details, and any named-project facts. Verify the NERC large-load-loss event details from the primary report.

## Visual design

- **Palette/aesthetic:** Electrical-schematic identity — dark slate base, copper/gold conductor accent, thin schematic linework. Reads like a beautiful one-line diagram, not a marketing graphic.
- **Signature visual:** A stylized one-line power diagram spanning the page width: grid to GPU with voltage steps annotated and losses shown as small bleed-off indicators at each stage. Inline SVG; each stage anchors (links) to its section.
- **og:image:** 1200x630 crop of the one-line diagram with title.
- **Mobile:** diagram rotates to vertical flow below 768px (top = grid, bottom = GPU). **Print:** diagram + loss table on page one, grayscale-safe.
