# Layer 3 Wave 2 — coordinate hand-compile report

**Scope:** 200-499 MW band from `layer3_scope.csv`, onshore only, excluding projects already coord'd in Waves 1/Layer 1. Coordinates appended to `project_coordinates.csv` (Phase 1 schema). **Not committed** — for your review.

## Counts
| | n |
|---|---:|
| Wave 2 set (200-499 MW, onshore, not already done) | 272 |
| Resolved & integrated (in-bbox coord) | **234** |
| Unresolved (no citable coord) | 37 |
| Held out — out-of-state coord (concerns) | 1 (Moah Creek = QLD) |

Resolution rate: **234/272 = 86%**. Two projects (Euston WF, Wee Jasper WF) were resolved by an agent but initially missed in transcription — added on reconciliation. `project_coordinates.csv` now holds **591/1,555** coords (Layer 1 + Wave 1 + Wave 2).

## Per-status coverage (resolved)
| Status | resolved | unresolved |
|---|---:|---:|
| Proposed | 218 | 37 |
| Committed | 8 | 0 |
| Anticipated | 4 | 0 |
| Existing | 3 | 0 |
| Announced Withdrawal | 1 | 0 |

## Per-state coverage (resolved)
| State | resolved |
|---|---:|
| NSW | 101 |
| VIC | 80 |
| SA | 48 |
| TAS | 5 |

## Per-source breakdown
| Source | n |
|---|---:|
| proponent_site | 63 |
| locality_proxy | 54 |
| aemo_filing (AEMO KCI datafile addresses) | 44 |
| wikipedia / GEM | 28 |
| aremi (Rosetta Network Map Renewables) | 15 |
| osm_substation | 14 |
| state_portal (NSW Planning / PlanSA / IPC) | 16 |
| osm_plant | 2 |

A notable Wave-2 discovery: agents found the **AEMO KCI datafile** (`kci-datafile-compiled-nem.xlsx`) carries authoritative "Site Location Description" text (often full street addresses) even though it has no lat/lon columns — geocoding those addresses via OSM was the workhorse for ~44 NSW/SA projects. This is a better Phase-2-style source than we had in Wave 1.

## Per-confidence breakdown
| Confidence | n | Meaning |
|---|---:|---|
| high | 7 | filed doc / authoritative station or terminal-station coord |
| medium | 78 | proponent map, AEMO-KCI street address, or terminal-station connection point |
| low | 149 | locality/town proxy |

**64% are low-confidence locality proxies** — higher than Wave 1 (28%). The 200-499 MW band is more speculative/early-stage, so fewer have filed connection coords. Per the Wave-1 logic already in the spatial join, locality_proxy+low coords are capped at `medium` confidence downstream.

## Unresolved (37) — `wave2_unresolved.csv`
All 37 are Proposed. Dominant patterns: generic placeholders (Sturt Solar, Green Hydrogen Power Station, NSW/SA-region VPP names, "Melbourne Solar Farm", "South East BESS"), KCI/proponent-suffix names with no findable site, and same-name ambiguity (multiple "Armidale BESS", "Wellington BESS 2", "Little River Solar"). Notable: **Juno BESS, Vineyard BESS, Boulka Park BESS, Ballarat North BESS, Riverside BESS, Moonah Solar, Lambing Gully WF** — no citable site found.

## Concerns (41) — `wave2_concerns.csv`
Categories: 23 suspected duplicates, 6 GEM-only coords, 5 suspected co-located, 2 name/site mismatches, 1 out-of-state (Moah Creek), 1 attribution-uncertain, 1 status-questionable, 1 geocode-check, 1 hint-correction. **Key region/data flags:**
- **Interstate region conflicts (held, no coord written):** Moah Creek Solar (NSW1 panel → QLD), Halys BESS (VIC1 → QLD), Everleigh Solar (VIC1 → QLD), Territory Battery (NSW1 → ACT), Williamsdale BESS (NSW1 → ACT). These mirror the Wave-1 Nonowie pattern — likely AEMO region mislabels. Held out per the strict Wave-2 bbox gate; your call whether to apply like Nonowie.
- **GEM-only coords (low conf, verify):** Wimmera Plains WF, Campbells Forest SF, Australia Plains SF, Uungula WF/BESS, Bundy Energy Hub A/B.
- **Name/site mismatches:** Kyabram WF (site is Koyuga-Nanneella), Cranbourne BESS (Maoneng project is Mornington/Tyabb).
- **Status-questionable:** Kanmantoo PHES (AGL terminated; mine resumed).
- **Hint correction:** Palmerston Big Battery is near Poatina/Central Highlands, NOT Sheffield (my batch hint was wrong; agent corrected).
- **23 suspected duplicate/co-located pairs** (mostly base-vs-KCI twins and shared-substation clusters) — these will get identical spatial-join assignments, which is correct, but flags real project-count inflation in the AEMO panel for your dedupe review.

## Execution & time
**~55 minutes wall-clock** via **9 parallel research subagents** (3 NSW, 3 VIC, 2 SA, 1 TAS). Per-batch coverage: NSW1 38/39 resolved, NSW2 ~36/38, NSW3 ~28/38, VIC1 28/32, VIC2 23/33, VIC3 26/31, SA1 24/26, SA2 23/26, TAS 5/6. Cumulative agent runtime ~3.5 hours but parallel. Agents independently discovered the AEMO KCI datafile and the Rosetta Network Map CSV as coordinate sources.

## Honest assessment: did Proposed-first hold?
**Yes — cleanly, with no squeeze-out.** All 16 non-Proposed projects (8 Committed, 4 Anticipated, 3 Existing, 1 Announced-Withdrawal) resolved, because they are established/named assets (Snowy 2.0, Tallawarra B, Hunter PS, Wooreen ESS, Mortlake Battery, Victorian Big Battery, HBESS, etc.) that geocode trivially. The 37 unresolved are ALL Proposed — the genuinely-speculative tail with no filed location. So the priority ordering was effectively costless here: the speculative pipeline got full attention and the only failures were projects with no locatable site by any method.

## Not done (per brief)
- Spatial join NOT re-run (Wave 2 output is coords only).
- `draft_v3.csv` NOT written. `draft_v2`/canonical untouched.
- Nothing committed.

## Suggested next step
Re-run the region-aware spatial join on the now-591-coord `project_coordinates.csv` to measure cumulative coverage lift, then decide: Wave 3 (≥100 MW band, ~268 remaining) vs proceed to Method 1 × Method 2 cross-validation.