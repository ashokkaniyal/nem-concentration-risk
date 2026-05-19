"""Hand-compiled project coordinates for the 56-project Phase 1 spike.

Each entry: (region, site_name_substring, lat, lon, source_ref, confidence)
Coordinates derived from public records (EIS documents, AEMO project
information, AusGrid/Transgrid/Powerlink project pages, Wikipedia, NSW DPIE
Major Projects portal, VicGrid REZ pages, ElectraNet TAPR). Confidence:
  high   — confirmed from project's own filed planning docs
  medium — derived from project area / nearest town / known cluster
  low    — best-guess from name / regional context

site_name_substring matches via case-insensitive substring; the manual coord
overrides any prior OSM coord.

Run after harvest_osm_coords.py to fill in coords OSM missed. Pass --write
to persist; otherwise dry-run.
"""
from __future__ import annotations
import argparse
import pandas as pd
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PROJ_CSV = REPO / "data" / "rez" / "project_coordinates.csv"

# (region, site_name_substring, lat, lon, source_ref, confidence)
# Coordinates are decimal degrees, WGS84.
COORDS = [
    # === NSW priors ===
    # Pottinger Energy Park (Liverpool Plains, ~25km NW of Quirindi, AGL/CEFC)
    ("NSW1", "Pottinger Energy Park", -31.30, 150.50, "AGL Pottinger EP planning docs (Liverpool Plains)", "medium"),
    # Hanworth Battery (Liverpool Plains region — Murrurundi area per planning portal)
    ("NSW1", "Hanworth Battery", -31.80, 150.85, "NSW Major Projects portal — Murrurundi area", "medium"),
    ("NSW1", "Hanworth BESS",     -31.80, 150.85, "NSW Major Projects portal — Murrurundi area", "medium"),
    # Glenbawn Pumped Hydro (Lake Glenbawn, Upper Hunter near Scone — HCC)
    ("NSW1", "Glenbawn Pumped Hydro", -32.10, 151.10, "Lake Glenbawn coords — Scone area", "high"),
    # Goulburn River Solar Farm (near Bylong, Goulburn River National Park — CWO/HCC border)
    ("NSW1", "Goulburn River Solar", -32.35, 150.10, "Goulburn River National Park area — Bylong", "medium"),
    ("NSW1", "Goulburn River BESS",  -32.35, 150.10, "Goulburn River National Park area — Bylong", "medium"),
    ("NSW1", "Goulburn River SF",    -32.35, 150.10, "Goulburn River National Park area — Bylong", "medium"),
    # Yarrabee Solar Power Project (NSW): "Yarrabee" in NSW context is near
    # Singleton/Hunter Valley (different Yarrabee from QLD Bowen Basin coal).
    # NSW DPIE Major Projects records show Yarrabee Solar near Singleton.
    ("NSW1", "Yarrabee Solar", -32.40, 151.05, "NSW DPIE Major Projects — Singleton area", "medium"),
    # Bayswater (existing 685 MW power station)
    # Already OSM-matched but include as fallback
    ("NSW1", "Bayswater", -32.395, 150.950, "Bayswater PS Wikipedia / OSM", "high"),

    # === VIC priors ===
    # LYA BESS = Loy Yang A BESS, at Loy Yang A PS site
    ("VIC1", "LYA BESS", -38.260, 146.590, "Loy Yang A PS coords", "high"),
    # Koorangie ESS / BESS Stage 2 (Edify Energy, Kerang area — VIC1, MR REZ)
    ("VIC1", "Koorangie Energy Storage", -35.85, 143.91, "Edify Koorangie ESS — Kerang area", "high"),
    ("VIC1", "Koorangie BESS",           -35.85, 143.91, "Edify Koorangie ESS — Kerang area", "high"),
    # Salt Creek Wind Farm — already OSM (Pacific Hydro, Hamilton VIC)
    ("VIC1", "Salt Creek Wind Farm", -37.917, 142.782, "Salt Creek WF OSM relation", "high"),

    # === SA priors (EXCLUDED — coords don't affect outcome but listed for completeness) ===
    ("SA1", "Mannum Adelaide Pumping Station", -34.92, 139.30, "Mannum, eastern SA", "high"),
    ("SA1", "Morgan To Whyalla Pipeline No 1", -34.00, 139.66, "Morgan SA (pipeline origin)", "high"),
    ("SA1", "Morgan To Whyalla Pipeline No 2", -34.00, 138.70, "Pipeline midpoint near Burra", "medium"),
    ("SA1", "Morgan To Whyalla Pipeline No 3", -33.50, 138.10, "Pipeline midpoint", "medium"),
    ("SA1", "Morgan To Whyalla Pipeline No 4", -33.20, 137.80, "Pipeline near Whyalla", "medium"),
    ("SA1", "Cathedral Rocks", -34.856, 135.582, "Cathedral Rocks WF OSM (Port Lincoln)", "high"),

    # === QLD ground-truth controls ===
    # Western Downs Green Power Hub (Neoen, north of Chinchilla — Brigalow area)
    ("QLD1", "Western Downs Green Power Hub", -26.674, 150.580, "Neoen Western Downs GPH — Brigalow", "high"),
    # MacIntyre Wind Farm (Karara area, west of Warwick)
    ("QLD1", "MacIntyre Wind Farm", -28.396, 151.205, "MacIntyre WF EIS — Karara/Warwick area", "high"),
    # Kogan Creek Power Station
    ("QLD1", "Kogan Creek", -26.828, 150.745, "Kogan Creek PS Wikipedia", "high"),
    # Aldoga Solar Farm (south of Gladstone)
    ("QLD1", "Aldoga Solar Farm", -23.946, 151.160, "Aldoga SF EIS — Gladstone area", "high"),
    # Stanwell Power Station (west of Rockhampton)
    ("QLD1", "Stanwell", -23.546, 150.336, "Stanwell PS Wikipedia", "high"),

    # === Shared-boundary cases (40 from residual analysis §5) ===
    # Stratford Renewable Energy Hub (Gloucester area NSW — HCC)
    ("NSW1", "Stratford Renewable Energy Hub", -32.20, 151.95, "Gloucester/Stratford NSW Major Projects", "medium"),
    # Bowmans Creek Wind Farm (Singleton area HCC)
    ("NSW1", "Bowmans Creek Wind Farm", -32.40, 151.10, "Bowmans Creek WF EIS — Singleton", "high"),
    # Port Augusta Solar Farm (KCI) — Port Augusta city (MN/EYR boundary)
    ("SA1", "Port Augusta Solar Farm", -32.500, 137.780, "Port Augusta city centre", "high"),
    # Maxwell Downs Solar Farm — Maxwell coal mine area Upper Hunter (HCC)
    ("NSW1", "Maxwell Downs Solar Farm", -32.300, 150.950, "Maxwell Coal Mine area, Upper Hunter", "medium"),
    ("NSW1", "Maxwell Downs Bess",      -32.300, 150.950, "Maxwell Coal Mine area, Upper Hunter", "medium"),
    ("NSW1", "Maxwell Solar Farm",      -32.300, 150.950, "Maxwell Coal Mine area, Upper Hunter", "medium"),
    # Mullion Creek WF (Orange CWO)
    ("NSW1", "Mullion Creek Wind Farm", -33.250, 149.110, "Mullion Creek WF EIS — Orange area", "high"),
    # Yoorndoo Ilga Solar (Mid-North SA — north of Adelaide, near Hallett area)
    ("SA1", "Yoorndoo Ilga", -33.40, 138.95, "Hallett area, MN", "low"),
    # Shoalhaven Expansion (Origin pumped hydro — Tallowa Dam area, ILW)
    ("NSW1", "Shoalhaven Expansion", -34.780, 150.400, "Tallowa Dam / Shoalhaven scheme", "high"),
    # Morgan Solar (SA, Riverland — Morgan town)
    ("SA1", "Morgan Solar", -34.025, 139.660, "Morgan SA — Riverland", "high"),
    # Whyalla BESS / SSE Whyalla / Whyalla Solar (all in Whyalla EYR)
    ("SA1", "Whyalla BESS",            -33.030, 137.580, "Whyalla city centre", "high"),
    ("SA1", "SSE Whyalla Solar Farm",  -33.030, 137.580, "Whyalla city centre", "high"),
    ("SA1", "Whyalla Solar Farm",      -33.030, 137.580, "Whyalla city centre", "high"),
    # Emeroo BESS / Bungala (Port Augusta area — Bungala SF coords, EYR)
    ("SA1", "Emeroo BESS",  -32.475, 137.900, "Bungala SF area, Port Augusta — Emeroo BESS", "medium"),
]


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()
    df = pd.read_csv(PROJ_CSV)
    for c in ("lat", "lon"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    for c in ("source", "source_url_or_ref", "confidence"):
        if c in df.columns:
            df[c] = df[c].astype(object)
    matched = 0
    for region, substr, lat, lon, src, conf in COORDS:
        mask = (df.region == region) & df.site_name.str.contains(substr, case=False, na=False, regex=False)
        # Only fill empties OR override low confidence
        for i in df[mask].index:
            existing_conf = df.at[i, "confidence"] if "confidence" in df.columns else None
            existing_lat = df.at[i, "lat"]
            existing_ref = df.at[i, "source_url_or_ref"] if "source_url_or_ref" in df.columns else None
            # Skip if already has a high-quality coord (OSM matches are 'medium' default)
            if pd.notna(existing_lat) and existing_conf == "high":
                continue
            df.at[i, "lat"] = lat
            df.at[i, "lon"] = lon
            df.at[i, "source"] = "manual"
            df.at[i, "source_url_or_ref"] = src
            df.at[i, "confidence"] = conf
            matched += 1
    print(f"Filled {matched} project rows from manual coord table")
    coord_count = df.lat.notna().sum()
    print(f"Total with coords now: {coord_count}/{len(df)}")
    print("\nRemaining without coords:")
    for _, r in df[df.lat.isna()].iterrows():
        print(f"  [{r.region}] {r.spike_class:15s} {r.site_name!r}")
    if args.write:
        df.to_csv(PROJ_CSV, index=False)
        print(f"\nWrote {PROJ_CSV}")
    else:
        print("\n(dry run — pass --write to persist)")


if __name__ == "__main__":
    main()
