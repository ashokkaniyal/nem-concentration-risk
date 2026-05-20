"""Method 2 — spatial join project → nearest substation → REZ catchment.

Reads project coordinates from data/rez/project_coordinates.csv (schema: region,
site_name, lat, lon, source, source_url_or_ref, confidence) and substation
coordinates from data/rez/rez_substation_lookup_NEM.csv (which must have lat,
lon columns appended).

For each project:
  1. Apply non-generation name exclusion filter. Projects matching the filter
     return catchment='Unclassified' confidence='excluded' regardless of
     spatial proximity. Filter applied BEFORE spatial match.
  2. Haversine distance from project lat/lon to every substation with
     coordinates.
  3. Assign REZ = nearest substation's REZ.
  4. Confidence band:
       distance ≤ 20 km  → high
       20-50 km          → medium
       50-100 km         → review
       > 100 km          → Unclassified

Projects without coordinates fall through to catchment='Unclassified'
confidence='no_coordinate' so they remain visible for follow-up.

Usage:
    python scripts/spatial_join_catchment.py \
        --projects-csv data/rez/project_coordinates.csv \
        --substations-csv data/rez/rez_substation_lookup_NEM.csv \
        --out data/rez/spike_spatial_results.csv

The same script scales to all 1,549 non-QLD projects in Phase 2 — just point
--projects-csv at a wider file.
"""
from __future__ import annotations

import argparse
import math
import re
import sys
from pathlib import Path
from typing import Optional

import pandas as pd

# Non-generation exclusion patterns. Applied to site_name (case-insensitive,
# regex). Matching projects are returned as Unclassified/excluded regardless
# of spatial proximity.
EXCLUSION_PATTERNS = [
    r"\bpumping station\b",
    r"pipeline.*\bps\b",
    r"\bps\b.*pipeline",
    r"\bgas utilisation\b",
    r"\blandfill\b",
    r"\bwaste to energy\b",
    r"\bcogeneration\b",
    r"\bco-?gen\b",
    r"\bwinery\b",
    r"\bdata centre\b",
    r"\bdata center\b",
    r"\bwastewater\b",
    r"\bdesalination\b",
    r"\bwater filtration\b",
    r"\bbioreactor\b",
]
EXCLUSION_RE = re.compile("|".join(EXCLUSION_PATTERNS), re.IGNORECASE)


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    R = 6371.0088
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlmb / 2) ** 2
    return 2 * R * math.asin(math.sqrt(a))


def confidence_from_distance(d_km: float) -> str:
    if d_km <= 20:
        return "high"
    if d_km <= 50:
        return "medium"
    if d_km <= 100:
        return "review"
    return "Unclassified"


def excluded(site_name: str) -> Optional[str]:
    """Return the matched exclusion pattern, or None."""
    if pd.isna(site_name):
        return None
    m = EXCLUSION_RE.search(str(site_name))
    return m.group(0) if m else None


def spatial_match(
    projects: pd.DataFrame, subs: pd.DataFrame
):
    """One row per input project, with assignment and nearest-substation distance.

    Region-aware: matches against substations in the project's panel-tagged
    region first. If the nearest in-region substation is >300 km away (or the
    region has no geocoded substations), falls back to all-region candidates,
    flags the row as a region mismatch (confidence=review), and records it for
    region_mismatches.csv.

    Confidence cap: a project whose coord came from a low-confidence locality
    proxy can never be labelled 'high' even if it lands within 20 km of a
    substation — capped at 'medium'.

    Returns (results_df, region_mismatches_df).
    """
    REGION_TO_STATE = {"NSW1": "NSW", "VIC1": "VIC", "SA1": "SA", "TAS1": "TAS", "QLD1": "QLD"}
    REGION_FALLBACK_KM = 300.0

    # Substations with coordinates only
    s_geo = subs.dropna(subset=["lat", "lon"]).copy()
    s_geo["lat"] = s_geo["lat"].astype(float)
    s_geo["lon"] = s_geo["lon"].astype(float)
    # Exclude interconnector terminals from the candidate set.
    if "interconnector_terminal" in s_geo.columns:
        ic = s_geo["interconnector_terminal"].astype(str).str.lower().isin(["true", "1", "yes"])
        n_ic = int(ic.sum())
        if n_ic:
            print(f"Excluding {n_ic} interconnector-terminal substations from candidate set",
                  file=sys.stderr)
        s_geo = s_geo[~ic].copy()

    def cap_conf(conf: str, source: str, src_conf: str) -> str:
        """Cap 'high' to 'medium' for low-confidence locality proxies."""
        if (str(source) == "locality_proxy" and str(src_conf) == "low"
                and conf == "high"):
            return "medium"
        return conf

    out_rows = []
    mismatches = []
    for _, p in projects.iterrows():
        site = p.get("site_name", "")
        region = p.get("region", "")
        src = p.get("source", "")
        src_conf = p.get("confidence", "")
        base = {
            "site_name": site, "region": region,
            "project_lat": p.get("lat"), "project_lon": p.get("lon"),
            "project_coord_source": src,
            "spike_class": p.get("spike_class", ""),
            "expected_catchment": p.get("expected_catchment", ""),
        }
        # 1. Exclusion filter
        excl = excluded(site)
        if excl:
            out_rows.append({**base, "method": "spatial_join_excluded",
                             "transmission_catchment": "Unclassified", "catchment_confidence": "excluded",
                             "nearest_substation": "", "nearest_substation_rez": "", "distance_km": None,
                             "exclusion_pattern_matched": excl, "region_mismatch": False})
            continue
        # 2. Coordinate check
        try:
            plat = float(p.get("lat")); plon = float(p.get("lon"))
            if math.isnan(plat) or math.isnan(plon):
                raise ValueError("nan")
        except (TypeError, ValueError):
            out_rows.append({**base, "method": "no_coordinate",
                             "transmission_catchment": "Unclassified", "catchment_confidence": "no_coordinate",
                             "nearest_substation": "", "nearest_substation_rez": "", "distance_km": None,
                             "exclusion_pattern_matched": "", "region_mismatch": False})
            continue
        # 3. Region-aware spatial join
        state = REGION_TO_STATE.get(region)
        in_region = s_geo[s_geo["state"] == state] if state else s_geo.iloc[0:0]
        region_mismatch = False
        cand = in_region
        if len(in_region):
            dists = in_region.apply(lambda r: haversine_km(plat, plon, r.lat, r.lon), axis=1)
            d_in = float(dists.min())
        else:
            d_in = float("inf")
        # Fallback: no in-region substations, or nearest in-region is implausibly far
        if d_in > REGION_FALLBACK_KM:
            cand = s_geo  # all regions
            region_mismatch = True
        dists = cand.apply(lambda r: haversine_km(plat, plon, r.lat, r.lon), axis=1)
        idx_min = dists.idxmin()
        d_min = float(dists.loc[idx_min])
        nearest = cand.loc[idx_min]
        conf = confidence_from_distance(d_min)
        if region_mismatch:
            conf = "review"  # cross-region match is inherently uncertain
        conf = cap_conf(conf, src, src_conf)
        catchment = nearest["rez_code"] if d_min <= 100 else "Unclassified"
        notes = ""
        if region_mismatch:
            notes = f"panel region {region} conflicts with location; matched substation in {nearest['state']}"
            mismatches.append({
                "site_name": site, "panel_region": region,
                "matched_state": nearest["state"], "nearest_substation": nearest["substation"],
                "nearest_substation_rez": nearest["rez_code"], "distance_km": round(d_min, 2),
                "in_region_nearest_km": round(d_in, 1) if d_in != float("inf") else None,
                "assigned_catchment": catchment,
            })
        out_rows.append({**base, "method": "spatial_join",
                         "transmission_catchment": catchment, "catchment_confidence": conf,
                         "nearest_substation": nearest["substation"], "nearest_substation_rez": nearest["rez_code"],
                         "distance_km": round(d_min, 2), "exclusion_pattern_matched": "",
                         "region_mismatch": region_mismatch, "notes": notes})
    return pd.DataFrame(out_rows), pd.DataFrame(mismatches)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--projects-csv", required=True, type=Path)
    ap.add_argument("--substations-csv", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()

    projects = pd.read_csv(args.projects_csv)
    subs = pd.read_csv(args.substations_csv)
    print(f"Loaded {len(projects)} projects from {args.projects_csv}", file=sys.stderr)
    print(f"Loaded {len(subs)} substation rows; "
          f"{subs.dropna(subset=['lat','lon']).shape[0]} have coordinates",
          file=sys.stderr)
    result, mismatches = spatial_match(projects, subs)
    result.to_csv(args.out, index=False)
    print(f"\nWrote {len(result)} rows to {args.out}", file=sys.stderr)
    # Region mismatches side-file
    mm_path = args.out.parent / "region_mismatches.csv"
    mismatches.to_csv(mm_path, index=False)
    print(f"Wrote {len(mismatches)} region mismatches to {mm_path}", file=sys.stderr)
    print("\nMethod summary:", file=sys.stderr)
    print(result["method"].value_counts().to_string(), file=sys.stderr)
    print("\nConfidence summary:", file=sys.stderr)
    print(result["catchment_confidence"].value_counts().to_string(), file=sys.stderr)
    matched = result[result["method"] == "spatial_join"]
    if len(matched):
        print("\nDistance distribution (km) for spatially-matched projects:", file=sys.stderr)
        print(matched["distance_km"].describe(percentiles=[0.5, 0.95]).to_string(), file=sys.stderr)


if __name__ == "__main__":
    main()
