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
) -> pd.DataFrame:
    """One row per input project, with assignment and nearest-substation distance."""
    # Substations with coordinates only
    s_geo = subs.dropna(subset=["lat", "lon"]).copy()
    s_geo["lat"] = s_geo["lat"].astype(float)
    s_geo["lon"] = s_geo["lon"].astype(float)
    # Exclude interconnector terminals from the candidate set — a project near
    # Heywood/Murraylink/Basslink/Terranora should snap to the nearest *real*
    # generation substation, not the cross-region DC/AC link terminal.
    if "interconnector_terminal" in s_geo.columns:
        ic = s_geo["interconnector_terminal"].astype(str).str.lower().isin(["true", "1", "yes"])
        n_ic = int(ic.sum())
        if n_ic:
            print(f"Excluding {n_ic} interconnector-terminal substations from candidate set",
                  file=sys.stderr)
        s_geo = s_geo[~ic].copy()
    out_rows = []
    for _, p in projects.iterrows():
        site = p.get("site_name", "")
        # 1. Exclusion filter
        excl = excluded(site)
        if excl:
            out_rows.append({
                "site_name": site,
                "region": p.get("region", ""),
                "method": "spatial_join_excluded",
                "transmission_catchment": "Unclassified",
                "catchment_confidence": "excluded",
                "nearest_substation": "",
                "nearest_substation_rez": "",
                "distance_km": None,
                "exclusion_pattern_matched": excl,
                "project_lat": p.get("lat"),
                "project_lon": p.get("lon"),
                "project_coord_source": p.get("source", ""),
                "spike_class": p.get("spike_class", ""),
                "expected_catchment": p.get("expected_catchment", ""),
            })
            continue
        # 2. Coordinate check
        try:
            plat = float(p.get("lat"))
            plon = float(p.get("lon"))
            if math.isnan(plat) or math.isnan(plon):
                raise ValueError("nan")
        except (TypeError, ValueError):
            out_rows.append({
                "site_name": site,
                "region": p.get("region", ""),
                "method": "no_coordinate",
                "transmission_catchment": "Unclassified",
                "catchment_confidence": "no_coordinate",
                "nearest_substation": "",
                "nearest_substation_rez": "",
                "distance_km": None,
                "exclusion_pattern_matched": "",
                "project_lat": p.get("lat"),
                "project_lon": p.get("lon"),
                "project_coord_source": p.get("source", ""),
                "spike_class": p.get("spike_class", ""),
                "expected_catchment": p.get("expected_catchment", ""),
            })
            continue
        # 3. Spatial join — haversine to every geocoded substation
        dists = s_geo.apply(
            lambda r: haversine_km(plat, plon, r.lat, r.lon), axis=1
        )
        idx_min = dists.idxmin()
        d_min = float(dists.loc[idx_min])
        nearest = s_geo.loc[idx_min]
        out_rows.append({
            "site_name": site,
            "region": p.get("region", ""),
            "method": "spatial_join",
            "transmission_catchment": nearest["rez_code"] if d_min <= 100 else "Unclassified",
            "catchment_confidence": confidence_from_distance(d_min),
            "nearest_substation": nearest["substation"],
            "nearest_substation_rez": nearest["rez_code"],
            "distance_km": round(d_min, 2),
            "exclusion_pattern_matched": "",
            "project_lat": plat,
            "project_lon": plon,
            "project_coord_source": p.get("source", ""),
            "spike_class": p.get("spike_class", ""),
            "expected_catchment": p.get("expected_catchment", ""),
        })
    return pd.DataFrame(out_rows)


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
    result = spatial_match(projects, subs)
    result.to_csv(args.out, index=False)
    print(f"\nWrote {len(result)} rows to {args.out}", file=sys.stderr)
    print("\nMethod summary:", file=sys.stderr)
    print(result["method"].value_counts().to_string(), file=sys.stderr)
    print("\nConfidence summary:", file=sys.stderr)
    print(result["catchment_confidence"].value_counts().to_string(), file=sys.stderr)
    # Distance distribution for actually-matched rows
    matched = result[result["method"] == "spatial_join"]
    if len(matched):
        print("\nDistance distribution (km) for spatially-matched projects:", file=sys.stderr)
        print(matched["distance_km"].describe(percentiles=[0.5, 0.95]).to_string(), file=sys.stderr)


if __name__ == "__main__":
    main()
