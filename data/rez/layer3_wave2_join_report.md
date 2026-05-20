# Layer 3 Wave 2 — spatial join report (Layer 1 + Wave 1 + Wave 2)

Region-aware join (`spatial_join_catchment.py`) on the corrected 591-coord `project_coordinates.csv`. Output: `spatial_join_v3_wave2.csv`. **Not committed.**

## Corrections applied first
1. **5 interstate conflicts dropped** (no coords written): Moah Creek, Halys BESS, Everleigh Solar (→QLD, out of non-QLD scope); Territory Battery, Williamsdale BESS (→ACT, load-area, left to Method 1). All 5 already had NaN coords — confirmed none leaked into the file.
2. **6 GEM-only coords verified:** Wimmera Plains WF, Campbells Forest SF, Uungula WF/BESS, Bundy Energy Hub A/B → second source confirmed within ~10 km, **upgraded low→medium**. Australia Plains SF → GEM coord disputed (~60 km too far east, near the Murray); **replaced** with Australia Plains locality (nr Eudunda/Robertstown), held at low.
3. **Palmerston Big Battery** confirmed at Poatina/Central Highlands (−41.79, 146.99), not Sheffield. No change needed.

## Cumulative coverage
| | n |
|---|---:|
| Projects with coords | 591 / 1,555 |
| **Spatially classified (real catchment)** | **577** |
| — Wave 2 contribution | 231 |
| — Wave 1 contribution | 73 |
| — Layer 1 (OSM) + spike | 273 |
| no_coordinate (→ Method 1 backstop) | 949 |
| excluded by name filter | 23 |
| Unclassified (>100 km, probable bad coord) | 6 |

**Of the 1,273 original Layer-1 misses, 304 are now classified** via Wave 1 (73) + Wave 2 (231) hand-compiled coords.

## Coverage lift from Wave 2 alone
Wave 2 added **231 new spatial classifications** (349 → 580 matched rows; 577 with real catchment). That roughly **doubles** the post-Wave-1 spatially-classified count.

## Cumulative by state
| State | classified |
|---|---:|
| NSW | 265 |
| VIC | 184 |
| SA | 94 |
| TAS | 29 |
| QLD (controls) | 5 |

## Cumulative by catchment
SW-NSW 80, MN 69, CWO 56, NEW 55, HCC 52, SW-VIC 50, CN-VIC 48, WV 40, TAS-NW 29, GIP 24, MR 22, ILW 21, SE-SA 16, EYR 9, (QLD controls: CQ 2, WD 2, SD 1), RIV 1.

## Distance distribution (all 583 matched)
| Stat | km |
|---|---:|
| median | **5.1** |
| 95th pct | 47.5 |
| max | 195.9 (Ceduna — genuinely remote) |

Median **improved** vs Wave 1 (6.6 km) — the AEMO KCI datafile street addresses geocoded precisely, pulling many matches under 5 km.

## Region mismatch log (unchanged: 1)
| Project | Panel | Matched | Nearest sub | Dist | In-region nearest | Catchment |
|---|---|---|---|---:|---:|---|
| Nonowie Wind Farm | NSW1 | SA | Whyalla (MN) | 12.6 km | 390.5 km | MN (review) |

No new region mismatches — the 5 interstate Wave-2 conflicts were dropped rather than coord-applied, so they fall to Method 1 instead of triggering fallback.

## Coords >100 km from any substation → Unclassified (6)
| Project | Nearest | Dist | Note |
|---|---|---:|---|
| Ceduna Solar Farm | Wudinna | 196 km | Real but far-west Eyre; lookup lacks Ceduna-area substation |
| Ceduna Wind Farm | Wudinna | 196 km | Same — coverage gap, not bad coord |
| Nyngan Solar Plant | Narromine | 133 km | Layer-1; real, sparse substation coverage |
| NSW Gas Peaker | Jemalong | 121 km | Wave-1 GEM approximate coord — genuinely dubious |
| EIWA Richmond Valley BESS | Tenterfield | 103 km | North Coast NSW, outside any REZ substation cluster |
| Musselroe Wind Farm | (TAS catch-all) | 102 km | Layer-1; NE Tas, far from lookup substations |

**Recommendation:** all 6 correctly Unclassified by the >100 km rule. Ceduna ×2 and Musselroe are real projects exposing **substation-lookup coverage gaps** (far-west Eyre, NE Tas), not coord errors — worth adding those substations later. NSW Gas Peaker is the one genuinely bad coord.

## 15 random Wave 2 spot-checks
| Project | REZ | Nearest sub | Dist | Conf | Source |
|---|---|---|---:|---|---|
| Glenrowan BESS - Storage - KCI | CN-VIC | Glenrowan | 0.1 | high | osm_substation |
| Mandurama Wind Farm | CWO | Orange | 42.0 | medium | locality_proxy |
| Kanmantoo | SE-SA | Mobilong | 24.0 | medium | wikipedia |
| Stonehaven Gas Turbines - KCI | SW-VIC | Geelong | 10.9 | medium | locality_proxy |
| Buronga BESS - Storage - KCI | SW-NSW | Buronga | 10.3 | high | aemo_filing |
| Jeeralang Battery | GIP | Jeeralang | 0.0 | high | proponent_site |
| Wallerawang 9 BESS | CWO | Wallerawang | 0.5 | high | proponent_site |
| Hills of Gold Wind Farm | NEW | Central South Hub | 9.9 | high | aremi |
| Merriwa SF | HCC | Merriwa | 0.8 | medium | locality_proxy |
| Mt Doran BESS | WV | Elaine | 6.1 | high | proponent_site |
| Woodland BESS | SW-NSW | Griffith | 22.3 | medium | state_portal |
| Glenellen Solar Farm | SW-NSW | Jindera | 1.7 | high | state_portal |
| Dalvui BESS | SW-VIC | Terang | 0.0 | high | proponent_site |
| Tchelery BESS | SW-NSW | Balranald | 58.3 | review | aemo_filing |
| Learmonth BESS | WV | Waubra | 12.5 | high | proponent_site |

## Honest read: Wave 2 vs Wave 1 quality

**The lower-confidence input distribution is NOT producing visible noise — the locality_proxy cap is doing its job.**

- Classified-confidence split is actually *similar*: Wave 1 = 42 high / 31 medium / 0 review (58% high); Wave 2 = 142 high / 80 medium / 9 review (61% high).
- Despite Wave 2 having 64% low-confidence *input* coords, output high-confidence is comparable because the **AEMO KCI street addresses (`aemo_filing`)** geocoded precisely (<20 km), earning legitimate high.
- The **cap is visibly working** in the spot-checks: Merriwa SF (0.8 km) and Stonehaven (10.9 km) would normally be high but are correctly held at medium because their input was a low-confidence locality proxy. So a town-centroid coord landing near a substation does NOT get over-credited.
- The 9 Wave-2 `review` rows are genuine long-distance matches (e.g. Tchelery 58 km — sparse far-west substation coverage), correctly flagged.
- Median match distance improved (6.6 → 5.1 km), so Wave 2 did not degrade spatial precision.

**Residual risk:** the ~54 pure locality_proxy coords are town centroids — fine for coarse REZ assignment (REZ regions are tens of km wide) but capped at medium so they cannot masquerade as precise. The honest weak spot is not noise but **coverage gaps** (Ceduna, Musselroe) where the substation lookup, not the project coords, is thin.

## Not done / next
- `draft_v3.csv` not written; `draft_v2`/canonical untouched; nothing committed.
- Next: Wave 3 (≥100 MW, ~268 remaining) **or** proceed to Method 1 × Method 2 cross-validation. Recommendation: with 304 of the speculative pipeline now spatially placed and median 5 km precision, this is a reasonable point to **start the cross-validation** and treat Wave 3 as optional fill-in.