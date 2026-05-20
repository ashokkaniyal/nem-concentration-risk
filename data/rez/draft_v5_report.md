# draft_v5 — cross-validated NEM-wide catchment lookup

`transmission_catchment_lookup_draft_v5.csv` — Method 1 (keyword) × Method 2 (spatial) merged under the locked rule. **Not merged to canonical; not committed.**

## Final classification counts
- **Total rows: 2110** (QLD canonical 561 + non-QLD 1549)

### By state
| State | n |
|---|---:|
| NSW | 692 |
| QLD | 561 |
| VIC | 485 |
| SA | 276 |
| TAS | 96 |

### By confidence
| Confidence | n |
|---|---:|
| high | 998 |
| medium | 713 |
| review | 398 |
| unresolved | 1 |

### By final catchment
| Catchment | n |
|---|---:|
| Unclassified | 373 |
| SW-NSW | 184 |
| CQ | 166 |
| MN | 151 |
| NEW | 137 |
| CWO | 122 |
| CN-VIC | 108 |
| TAS-NW | 96 |
| SW-VIC | 89 |
| WV | 77 |
| HCC | 76 |
| FNQ | 73 |
| GIP | 70 |
| SEQ | 69 |
| WD | 53 |
| WG | 46 |
| MR | 42 |
| ILW | 37 |
| SE-SA | 37 |
| SD | 33 |
| DD | 26 |
| EYR | 24 |
| TG | 11 |
| RIV | 9 |
| unresolved | 1 |

## Merge-rule application
| Rule | n |
|---|---:|
| no_coord_m1_backstop | 1533 |
| agree | 456 |
| excluded_m1 | 51 |
| boundary_swap_m1_med_close | 21 |
| boundary_swap_m1_review | 18 |
| boundary_swap_m1_med_far | 16 |
| corridor_misread_m2 | 7 |
| excluded_m2 | 5 |
| boundary_swap_m1_high | 1 |
| nonowie_manual | 1 |
| corridor_misread_unresolved | 1 |

## Change vs draft_v2 (final catchment ≠ Method 1)
**115 projects changed catchment** under cross-validation:

| Rule | n | Direction |
|---|---:|---|
| excluded_m1 | 51 | M1 Unclassified → M2 REZ (coverage gain) |
| boundary_swap_m1_med_close | 21 | M1 medium → M2 (substation ≤20 km) |
| boundary_swap_m1_review | 18 | M1 weak keyword → M2 |
| boundary_swap_m1_med_far | 16 | M1 medium → M2 (>20 km, review-flagged) |
| corridor_misread_m2 | 7 | M1 keyword misread → M2 |
| nonowie_manual | 1 | region data error → MN |
| corridor_misread_unresolved | 1 | Quandong → unresolved |

The other 1,995 rows kept their Method 1 catchment (agree, M1-high boundary, excluded_m2, or no-coord backstop).

## Unresolved set (1)
- **Quandong Solar Farm** (VIC1) — catchment=`unresolved`. 350 MW; locality_proxy coord unconfirmed; neither M1 (MR) nor M2 (SW-VIC) substantiated.

## Review-flagged set (398)
- 377 `no_coord_m1_backstop` rows that were already M1 `review` (keyword "Unclassified/judgement" cases with no coord — unchanged status).
- 16 `boundary_swap_m1_med_far` (M2 adopted but >20 km — flagged).
- 4 `excluded_m1` where M2 was itself review-grade (>50 km).
- 1 `nonowie_manual`.
- Wattle Creek ×2 resolved to **ILW** (Marulan is ILW-coded), confidence medium with boundary note — not in the review set.

## Validation
- Rows with null/blank catchment: **0** (target 0). ✓
- Every row has a catchment value or the explicit `unresolved` sentinel (1 row).
- merge_rule_applied populated on all 2110 rows. ✓

## Top-20 sanity check
| Project | State | M1 | M2 | Rule | Final | Conf |
|---|---|---|---|---|---|---|
| Bayswater | NSW | NEW | HCC | boundary_swap_m1_review | **HCC** | high |
| Mortlake BESS | VIC | SW-VIC | SW-VIC | agree | **SW-VIC** | high |
| Kingswood BESS | NSW | SW-NSW | NEW | corridor_misread_m2 | **NEW** | high |
| Belhaven Renewable Project | NSW | NEW | SW-NSW | corridor_misread_m2 | **SW-NSW** | high |
| Wattle Creek Energy Hub - Battery  | NSW | CWO | ILW | corridor_misread_m2 | **ILW** | high |
| Quandong Solar Farm | VIC | MR | SW-VIC | corridor_misread_unresolved | **unresolved** | unresolved |
| Riverland Solar Storage - Solar | SA | RIV | MN | boundary_swap_m1_high | **RIV** | high |
| Nonowie Wind Farm | NSW | SW-NSW | MN | nonowie_manual | **MN** | review |
| Goat Hill Pumped Hydro | SA | MN | EYR | boundary_swap_m1_med_close | **EYR** | medium |
| LYA BESS | VIC | CN-VIC | GIP | boundary_swap_m1_review | **GIP** | high |
| Koorangie Energy Storage System | VIC | CN-VIC | MR | boundary_swap_m1_review | **MR** | high |
| Cathedral Rocks | SA | MN | EYR | boundary_swap_m1_review | **EYR** | medium |
| Snowy 2.0 | NSW | SW-NSW | SW-NSW | agree | **SW-NSW** | high |
| Western Downs Green Power Hub | QLD | WD | — | no_coord_m1_backstop | **WD** | high |
| Eraring Big Battery – Stage 1 | NSW | HCC | HCC | agree | **HCC** | high |
| Lovely Banks Renewable Energy Hub | VIC | WV | SW-VIC | boundary_swap_m1_med_close | **SW-VIC** | medium |
| McCullys Gap BESS | NSW | NEW | HCC | boundary_swap_m1_med_close | **HCC** | medium |
| Ceduna Solar Farm | SA | EYR | Unclassified | excluded_m2 | **EYR** | medium |
| NSW Gas Peaker | NSW | SW-NSW | Unclassified | excluded_m2 | **SW-NSW** | medium |

## Next (after your top-20 review)
Merge draft_v5 → canonical `transmission_catchment_lookup.csv`, commit as **v0.7**, then re-run `notebooks/06_first_entry_tests.ipynb` NEM-wide — the framework payoff.