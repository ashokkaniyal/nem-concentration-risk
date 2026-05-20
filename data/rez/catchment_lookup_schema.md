# Catchment lookup schema & provenance guide

How to read `transmission_catchment_lookup.csv` (canonical, NEM-wide as of v0.7)
and its cross-validation working file `transmission_catchment_lookup_draft_v5.csv`.
Written for a panel reviewer or future-self auditing how each project got its catchment.

## Columns

| Column | Meaning |
|---|---|
| `site_name` | AEMO Generation Information project name (join key) |
| `catchment` | **Final adjudicated REZ catchment** (or `Unclassified` / `unresolved`) |
| `catchment_confidence` | final confidence tier (see below) |
| `merge_rule_applied` | which of the 11 rules decided this row (see below) |
| `method_1_catchment` | what Method 1 (keyword) said — preserved for traceability |
| `method_1_confidence` | Method 1's own confidence (high/medium/review) |
| `method_2_catchment` | what Method 2 (spatial) said — blank if no coordinate |
| `method_2_confidence` | Method 2's distance-band confidence — blank if no coordinate |
| `transmission_catchment` | legacy column = Method 1 catchment (kept for backward compat) |
| `rationale`, `matched_keyword` | Method 1 audit fields |
| `best_capacity_mw`, `technology`, `fuel`, `owner`, `owner_tier`, `phantom_risk`, `phantom_flags` | project metadata (QLD rows carry the original phantom-review fields) |
| `notes` | row-specific adjudication notes |

## catchment_confidence tiers

| Tier | Meaning |
|---|---|
| **high** | Both methods agree, OR one method high-confidence (substation ≤20 km / filed planning coord / authoritative keyword) |
| **medium** | Single-method or moderate-distance (20-50 km) evidence; locality-proxy coords capped here |
| **review** | Weak/ambiguous: keyword "judgement call" with no coord, spatial match >50 km, boundary swap with a far coord, or manual region fix |
| **unresolved** | Neither method substantiated a catchment (1 row: Quandong Solar Farm) |

## The 11 merge_rule_applied values

| Rule | n (v0.7) | What it means | Final catchment from |
|---|---:|---|---|
| `agree` | 456 | M1 and M2 assigned the same catchment | either (identical) |
| `no_coord_m1_backstop` | 1,533 | No Method 2 coordinate (all 560 QLD + non-QLD projects without coords) | Method 1 keyword |
| `excluded_m1` | 51 | M1 said Unclassified; M2 found a REZ (coverage gain) | Method 2 |
| `excluded_m2` | 5 | M2 Unclassified (>100 km from any substation — coverage gap); M1 had a keyword | Method 1 |
| `boundary_swap_m1_high` | 1 | Adjacent-REZ disagreement, M1 high-confidence keyword wins over a distant M2 | Method 1 |
| `boundary_swap_m1_med_close` | 21 | Adjacent-REZ, M1 medium, M2 substation ≤20 km — topology wins | Method 2 |
| `boundary_swap_m1_med_far` | 16 | Adjacent-REZ, M1 medium, M2 >20 km — M2 adopted but flagged `review` | Method 2 |
| `boundary_swap_m1_review` | 18 | Adjacent-REZ, M1 weak keyword — M2 wins | Method 2 |
| `corridor_misread_m2` | 7 | Non-adjacent same-state disagreement; M2 corrects an M1 keyword misread | Method 2 |
| `corridor_misread_unresolved` | 1 | Corridor disagreement neither method substantiated (Quandong) | unresolved |
| `nonowie_manual` | 1 | Region data error (panel NSW1, actual SA) — manual call | MN (region-aware join) |

## Provenance trail — how to audit any single row

1. Read `merge_rule_applied` — tells you which method decided the catchment.
2. Compare `method_1_catchment` vs `method_2_catchment` — see what each method independently said.
3. For disagreements, the named adjudication docs hold the reasoning:
   - **Boundary swaps** (`boundary_swap_*`): `boundary_swap_breakdown.md` — the M1-confidence split and the per-case tie-break logic.
   - **Corridor misreads** (`corridor_misread_*`): `corridor_misread_adjudication.md` — 8 named cases with location checks and SLD-topology reads.
   - **Topology calls** (Bayswater/Wollar/Mortlake/Heywood/Bundey etc.): `sld_topology_adjudication.md` — connectivity-based REZ assignment from the 2019 AEMO SLD.
   - **Coordinate provenance** (Method 2): `project_coordinates.csv` (per-project lat/lon, `source`, `source_url_or_ref`, `confidence`) + `layer3_wave1_report.md`, `layer3_wave2_report.md`, `wave1_corrections.md`, `wave2_corrections.md`.
   - **Aggregate cross-validation**: `cross_validation_report.md` — agreement rates by state/status/confidence, disagreement-class breakdown.
4. For Method 2 spatial assignments, `nearest_substation` + `distance_km` (in `spatial_join_v3_wave2.csv`) show which substation anchored the catchment and how far the project sits from it.

## Method summary

- **Method 1 (keyword):** substring match of substation/locality names against `site_name`. Built in `scripts/build_nem_catchment_lookup.py` + `scripts/expand_rez_substation_lookup.py`. Output: `transmission_catchment_lookup_draft_v2.csv`.
- **Method 2 (spatial):** project lat/lon → haversine → nearest substation (region-aware, interconnector-excluded, locality-proxy-capped) → that substation's REZ. Built in `scripts/spatial_join_catchment.py`. Coordinates from `project_coordinates.csv` (590 projects: OSM `power=plant` + hand-compiled Waves 1-2 ≥200 MW). Output: `spatial_join_v3_wave2.csv`.
- **Cross-validation:** `method_1_vs_2_comparison.csv` (582 intersection) → 11-rule merge → `transmission_catchment_lookup_draft_v5.csv` → canonical.

## Known limitation for downstream code (flagged, not yet fixed)

`src/nem_herding/projects.py::join_catchment(panel, lookup_path, region="QLD1")`
**defaults to region="QLD1" and tags every non-QLD row as "Other NEM region"**,
discarding NSW/VIC/SA/TAS catchments. The notebooks
(`03_western_downs_eda`, `04_framework_tests`, `06_first_entry_tests`) all call it
with the default. **With the now-NEM-wide canonical, these notebooks will still
only classify QLD until `join_catchment` is generalised** (e.g. `region=None` to
join all regions). This is the first task of the next session (re-running
`06_first_entry_tests.ipynb` NEM-wide).
