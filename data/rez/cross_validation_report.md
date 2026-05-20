# Method 1 (keyword) × Method 2 (spatial) cross-validation

Analysis only — no final lookup built. Inputs: `transmission_catchment_lookup_draft_v2.csv` (Method 1) × `spatial_join_v3_wave2.csv` (Method 2). Comparison: `method_1_vs_2_comparison.csv`.

## Headline
| | |
|---|---|
| Projects classified by both methods (intersection) | **582** |
| Agreement (same catchment) | **461 / 582 = 79.2%** |
| Genuine disagreements (both confident, materially different) | **1** (Nonowie, the known region conflict) |

## Disagreement-class breakdown
| Class | n | Severity | Reading |
|---|---:|---|---|
| boundary_swap | 56 | low | adjacent REZ corridors — expected at borders |
| excluded_method_1 | 51 | medium | M1 said Unclassified; **M2 adds a REZ** (coverage gain) |
| corridor_misread | 8 | high | same-state non-adjacent — M2 generally corrects an M1 keyword misread |
| excluded_method_2 | 5 | medium | M2 Unclassified (>100 km); **M1 better** (substation-coverage gaps) |
| genuine_disagreement | 1 | high | Nonowie (NSW1 panel vs SA location) |
| interconnector_artefact | 0 | — | none — the interconnector exclusion already did its job |

## Per-state agreement
| State | n | agree | % |
|---|---:|---:|---:|
| NSW | 267 | 200 | 74.9 |
| VIC | 184 | 144 | 78.3 |
| SA | 96 | 83 | 86.5 |
| TAS | 30 | 29 | 96.7 |
| QLD ctrl | 5 | 5 | 100.0 |

NSW lowest (74.9%) — most projects, most adjacent REZs (CWO/NEW/HCC cluster), most keyword ambiguity. TAS highest (96.7%, single catchment).

## Per-status agreement
| Status | n | % |
|---|---:|---:|
| Existing less Announced Withdrawal | 5 | 100.0 |
| Committed | 10 | 90.0 |
| Anticipated | 4 | 75.0 |
| Proposed | 288 | 74.7 |
| Withdrawn | 1 | 100.0 |
| Announced Withdrawal | 1 | 100.0 |

Established projects (Existing/Committed) agree ~90-100%; Proposed 74.7% (the speculative tail with weaker M1 keywords + more M2 locality proxies).

## Per Method-1-confidence agreement — the key signal
| M1 confidence | n | agree % |
|---|---:|---:|
| high | 117 | **98.3** |
| medium | 378 | **86.8** |
| review | 87 | **20.7** |

**This is the decisive result.** Where Method 1 was *high* confidence, the methods agree **98.3%** — the two independent methods strongly corroborate. Where Method 1 was *review* (ambiguous keyword), agreement collapses to **20.7%** — exactly the cases where Method 2 should override. The cross-validation cleanly separates trustworthy M1 calls from ones needing M2 correction.

## Per-MW-band agreement (Wave 3 relevance)
| MW band | n | agree % |
|---|---:|---:|
| <100 | 113 | 92.0 |
| 100-199 | 79 | 84.8 |
| 200-499 | 171 | 78.4 |
| >=500 | 49 | 69.4 |

Agreement *rises* as capacity falls (<100 MW: 92%, 100-199: 85%, 200-499: 78%, ≥500: 69%). The 100-199 band — Wave 3's target — already agrees 85%.

## High-severity disagreements (9 — all corridor_misread or genuine)
**None have both methods at high confidence** (the worst case the brief asked for does not occur). Every one has M1 at medium and M2 at medium/high — i.e. Method 2 is correcting a medium-confidence M1 keyword call.

| Project | M1 | M2 | Nearest sub | km | Class | M1c/M2c |
|---|---|---|---|---:|---|---|
| Belhaven Renewable Project | NEW | SW-NSW | Wagga | 2 | corridor_misread | medium/high |
| Jeremiah WF | NEW | SW-NSW | Blowering | 39 | corridor_misread | medium/medium |
| Kingswood BESS | SW-NSW | NEW | Tamworth | 5 | corridor_misread | medium/high |
| Nonowie Wind Farm | SW-NSW | MN | Whyalla | 13 | genuine_disagreement | medium/review |
| Strontian Solar BESS | NEW | SW-NSW | Lockhart | 14 | corridor_misread | medium/high |
| Wattle Creek Energy Hub - Battery Storage | CWO | ILW | Marulan | 1 | corridor_misread | medium/high |
| Wattle Creek Energy Hub - Solar / BESS | CWO | ILW | Marulan | 9 | corridor_misread | medium/high |
| Malunga Nine Mile BESS - KCI | MR | SW-VIC | Berrybank | 23 | corridor_misread | medium/medium |
| Quandong Solar Farm | MR | SW-VIC | Yaloak South | 26 | corridor_misread | medium/medium |

**Read:** Belhaven/Strontian/Jeremiah (M1 NEW → M2 SW-NSW, all Wagga/Riverina-area, M2 right); Kingswood BESS (M1 SW-NSW → M2 NEW Tamworth 4.9 km, M2 right); Wattle Creek ×2 (M1 CWO → M2 ILW Marulan, M2 right — Arthursleigh is Southern Tablelands); Malunga/Quandong (M1 MR → M2 SW-VIC, M2 right). 8 of 9 are **Method 2 correcting an M1 keyword misread**; the 9th is Nonowie (region data error).

## 20 most informative resolutions (Method 2 corrects/adds vs Method 1)
Mix of corridor_misread corrections + high-confidence excluded_method_1 additions — the Bayswater/Wollar-style insight at scale:

| Project | M1 | M2 | Nearest sub | km | Insight |
|---|---|---|---|---:|---|
| Belhaven Renewable Project | NEW | SW-NSW | Wagga | 2.0 | M2 corrects keyword misread |
| Jeremiah WF | NEW | SW-NSW | Blowering | 38.7 | M2 corrects keyword misread |
| Kingswood BESS | SW-NSW | NEW | Tamworth | 4.9 | M2 corrects keyword misread |
| Strontian Solar BESS | NEW | SW-NSW | Lockhart | 13.8 | M2 corrects keyword misread |
| Wattle Creek Energy Hub - Battery Storage | CWO | ILW | Marulan | 1.5 | M2 corrects keyword misread |
| Wattle Creek Energy Hub - Solar / BESS | CWO | ILW | Marulan | 8.8 | M2 corrects keyword misread |
| Malunga Nine Mile BESS - KCI | MR | SW-VIC | Berrybank | 22.6 | M2 corrects keyword misread |
| Quandong Solar Farm | MR | SW-VIC | Yaloak South | 26.4 | M2 corrects keyword misread |
| Acacia SF | Unclassified | NEW | Central Hub (Hub 5) | 9.2 | M2 adds REZ M1 missed |
| Arundel BESS | Unclassified | SW-NSW | Wagga | 7.2 | M2 adds REZ M1 missed |
| Bells Mountain | Unclassified | HCC | Muswellbrook | 2.7 | M2 adds REZ M1 missed |
| Bells Mountain Pumped Hydro | Unclassified | HCC | Muswellbrook | 6.9 | M2 adds REZ M1 missed |
| Biala Wind Farm | Unclassified | SW-NSW | Gullen Range | 9.9 | M2 adds REZ M1 missed |
| Galore Energy Project - Solar And BESS - KCI | Unclassified | SW-NSW | Lockhart | 4.7 | M2 adds REZ M1 missed |
| Holbrook SF | Unclassified | SW-NSW | Uranquinty | 11.3 | M2 adds REZ M1 missed |
| Middlebrook SF & BESS | Unclassified | NEW | Central Hub (Hub 5) | 17.2 | M2 adds REZ M1 missed |
| Quorn Park Solar Farm | Unclassified | CWO | Parkes | 3.0 | M2 adds REZ M1 missed |
| Royalla Solar Farm | Unclassified | ILW | Williamsdale | 10.7 | M2 adds REZ M1 missed |
| South Keswick Solar Farm | Unclassified | CWO | Dubbo | 2.8 | M2 adds REZ M1 missed |
| Summerhill | Unclassified | HCC | Waratah | 6.1 | M2 adds REZ M1 missed |

## Pattern analysis
- **Concentration by M1 confidence, not MW band or proponent:** disagreements are overwhelmingly in M1 `review` (79% of review rows disagree) and M1 `Unclassified` (the 51 excluded_method_1). M1 `high` is near-perfect (98.3%).
- **By catchment:** disagreements cluster in the NSW CWO/NEW/HCC corridor (boundary swaps) and in NSW `Unclassified`→REZ additions. SA/TAS/VIC are cleaner.
- **By state:** NSW carries 67 of the 121 disagreements (NSW 67/267; VIC 40/184; SA 13/96; TAS 1/30). NSW's dense adjacent-REZ geography drives most boundary swaps.
- **excluded_method_2 (5)** are all substation-coverage gaps (Ceduna ×2, Nyngan, Musselroe, NSW Gas Peaker) — here **Method 1 keyword is the better source**; the final lookup should prefer M1 for these.

## Wave 3 decision: SKIP recommended
Wave 3 (100-199 MW hand-compile) **would not resolve the disagreements**, because:
1. The 100-199 MW band already agrees **84.8%** — higher than the 200-499 band Wave 2 covered. More coords there yields diminishing returns.
2. Disagreements are driven by **Method 1 keyword misreads** (corridor_misread) and **M1 Unclassified gaps** (excluded_method_1) — both are fixed by *adopting Method 2's assignment in the final lookup*, not by compiling more coordinates.
3. The 1 genuine disagreement is a region data error (Nonowie), unaffected by coverage.
4. The 5 excluded_method_2 are substation-lookup gaps, fixed by adding far-west-Eyre / NE-Tas substations, not project coords.

**Recommendation:** skip Wave 3; proceed to build the final cross-validated lookup (next session) with the merge rule below.

## Suggested merge rule for the final lookup (next session)
- M1 high **and** agree → accept (highest confidence).
- Agree (any confidence) → accept.
- boundary_swap → accept Method 2 (topology beats keyword at borders), confidence medium, flag.
- corridor_misread → accept Method 2 (it corrects the keyword), flag for one-line eyeball.
- excluded_method_1 → accept Method 2 (coverage gain), confidence per distance band.
- excluded_method_2 → accept Method 1 (M2 has no nearby substation), flag coverage gap.
- genuine_disagreement (Nonowie) → manual (MN per region-aware join).
- M1-only (no coord; 949 no_coordinate) → keep Method 1 keyword assignment as backstop.