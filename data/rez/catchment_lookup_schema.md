# Catchment lookup schema & provenance guide

How to read `transmission_catchment_lookup.csv` (canonical, NEM-wide as of v0.7,
deduped in v0.7.1) and its cross-validation working file
`transmission_catchment_lookup_draft_v5.csv`. Written for a panel reviewer or
future-self auditing how each project got its catchment.

## Catchment universe

**23 REZ catchments** (15 non-QLD + 8 QLD) plus `Unclassified` and `unresolved`.

| State | n | Catchments |
|---|---:|---|
| NSW | 5 | CWO, HCC, NEW, SW-NSW, ILW |
| VIC | 5 | CN-VIC, MR, WV, GIP, SW-VIC |
| SA | **4** | MN, SE-SA, RIV, **EYR** |
| TAS | 1 | TAS-NW |
| QLD | 8 | WD, SD, DD, TG, WG, FNQ, CQ, SEQ |

**Note on the count:** the v0.7 commit message (6ca5632) said "14 NSW/VIC/SA/TAS
catchments" — that undercounted. The correct non-QLD total is **15**. **EYR**
(Eyre Peninsula) is the 4th SA catchment, added mid-Phase-2 when ElectraNet
transmission topology showed the Eyre Peninsula is electrically separate from
Mid-North (MN) — it connects via Cultana/Davenport on the Upper Spencer Gulf,
not into the Mid-North 275 kV corridor. EYR is legitimate (24 rows).

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

**Casing convention (v0.7.1):** `catchment_confidence` is **lowercase**:
`high` / `medium` / `review` / `unresolved`. At join time, `join_catchment`
adds `n/a` for rows overwritten to "Other NEM region" under a region filter.

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

## Downstream code status

`src/nem_herding/projects.py::join_catchment` was **generalised** (signature
`join_catchment(panel, lookup_path, regions=None, region=None)`): the default
`regions=None` applies no region filter and preserves every project's catchment
NEM-wide; it reads the final `catchment`/`catchment_confidence` columns; the old
`region="QLD1"` keyword still works but emits a `DeprecationWarning`.

**Remaining Turn-2 work (notebooks):** `03_western_downs_eda`,
`04_framework_tests`, and `06_first_entry_tests` still hard-code
`QLD_CATCHMENTS = ['WD','SD','DD','TG','WG','FNQ','CQ','SEQ']` and per-state
grouping. With the generalised `join_catchment`, a bare call is now NEM-wide, so
these notebooks need their hard-coded QLD lists replaced (and to pass
`regions=["QLD1"]` explicitly if QLD-only behaviour is intended) before they
analyse the full 23-catchment NEM set.

## Known data anomalies (accepted edge cases)

Documented in `v07_audit_report.md` and accepted (no fix required):

1. **Nonowie Wind Farm — region/catchment mismatch.** AEMO tags it region
   `NSW1`, but the project is physically near Whyalla, South Australia. The
   region-aware spatial join correctly fell back across regions and assigned
   catchment **MN** (`merge_rule_applied = nonowie_manual`). This is an AEMO
   panel data error, not a lookup error. A `regions=["NSW1"]`-filtered NSW
   analysis will therefore contain one MN-catchment project — expected.

2. **Lookup is a snapshot; panel is a 22-release union.** The canonical was
   built from a point-in-time project set. The panel
   (`load_all_releases`) is the union across all 22 AEMO releases, so it
   contains projects (withdrawn, renamed, or backfilled) that have no lookup
   row. ~41 of 601 QLD panel projects (~7%) resolve to `Unclassified` on join
   for this reason. Expected and accepted — not a coverage gap in the
   methodology.

3. **Wantirna Mini Hydro (resolved in v0.7.1).** Previously appeared twice in
   the canonical (a spurious QLD-section row inherited from draft_v2 plus the
   correct VIC row), both `Unclassified`, causing +18 join-row inflation. The
   spurious QLD-section row was dropped in v0.7.1; the canonical now has one
   Wantirna row. Note the AEMO *panel* still tags Wantirna under both `QLD1`
   and `VIC1` across releases (an AEMO error) — but with a single lookup row
   the join no longer inflates.

4. **Casing.** `catchment_confidence` normalised to lowercase in v0.7.1.
