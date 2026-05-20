# Wave 1 corrections applied

Three user-confirmed dedupe/data-error fixes applied to `project_coordinates.csv` before re-running the spatial join. Output: `spatial_join_v3_wave1.csv`.

## 1. Armidale Pumped Hydro = Oven Mountain Pumped Storage (dedupe)
Two AEMO panel entries, one physical Walcha-area PHES project. Both `project_coordinates.csv` rows now point to the Oven Mountain coord (-30.8087, 152.2017) so both panel entries get the correct REZ via the join (rather than one falling through to the Layer-4 keyword backstop). Note added: "dedupe: same project as Oven Mountain Pumped Storage (user-confirmed)". Both resolve to **NEW** (nearest substation Metz, ~47 km — sparse New England coverage).

## 2. Bells Mountain = Muswellbrook PHES (dedupe)
Two AEMO panel entries, one project (Bells Mountain is the upper reservoir of the Muswellbrook pumped-hydro scheme). Both rows point to the Muswellbrook PHES coord (-32.2454, 150.9344). Confidence upgraded **low → medium** (relationship now user-confirmed). Note added flagging the dedupe.

## 3. Nonowie Wind Farm (region data error)
AEMO panel tags it NSW1 but the project is in SA near Whyalla. Per instruction: kept the SA coord (-33.05, 137.45) and left the panel region as NSW1 (don't fight the panel). The spatial join's new region-aware logic detected the conflict: nearest NSW substation was 390.5 km away (>300 km threshold), so it fell back to all-region candidates, matched **Whyalla (MN)** at 12.6 km, assigned **MN** with `catchment_confidence=review`, and logged the case to `region_mismatches.csv`.

## Spatial-join logic changes
1. **Region-aware matching with fallback**: match within the project's panel-region substations first; if nearest in-region substation is >300 km (coord likely in wrong region) or the region has no geocoded substations, fall back to all regions, flag `region_mismatch=True`, set confidence=review, and log to `region_mismatches.csv`.
2. **Locality-proxy confidence cap**: any project with `source=locality_proxy` AND input `confidence=low` has its output `catchment_confidence` capped at **medium** — a town-centroid coord can't be labelled high just because it lands within 20 km of a substation.