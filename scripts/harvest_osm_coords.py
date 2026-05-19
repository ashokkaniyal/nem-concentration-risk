"""Harvest coordinates from OSM cache into substation and project lookups.

Inputs:
  data/rez/osm_cache/{NSW,VIC,SA,TAS,QLD}_{substation,plant}.json — bulk OSM
    queries fetched per NEM state for power=substation and power=plant tagged
    elements with name=*.

Outputs:
  - Adds/updates lat, lon columns in data/rez/rez_substation_lookup_NEM.csv
    where the substation name matches an OSM substation name (case-insensitive
    substring) within the same state's bbox.
  - Fills lat, lon, source, confidence columns in data/rez/project_coordinates.csv
    where the project name matches an OSM plant name (case-insensitive substring).

Matching is conservative: substring match against the OSM "name" tag, with
length≥4 keys to avoid spurious hits. Records the OSM element ID as
source_url_or_ref so a reviewer can verify in OSM directly.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
OSM_DIR = REPO / "data" / "rez" / "osm_cache"
SUB_CSV = REPO / "data" / "rez" / "rez_substation_lookup_NEM.csv"
PROJ_CSV = REPO / "data" / "rez" / "project_coordinates.csv"

STATE_TO_REGION = {"NSW": "NSW1", "VIC": "VIC1", "SA": "SA1", "TAS": "TAS1", "QLD": "QLD1"}
REGION_TO_STATE = {v: k for k, v in STATE_TO_REGION.items()}


def load_osm(state: str, kind: str) -> list[dict]:
    fn = OSM_DIR / f"{state}_{kind}.json"
    if not fn.exists():
        return []
    try:
        d = json.load(open(fn))
        return d.get("elements", [])
    except Exception as e:
        print(f"  load_osm({state},{kind}) error: {e}", file=sys.stderr)
        return []


def el_coord(e: dict):
    lat = e.get("lat") or e.get("center", {}).get("lat")
    lon = e.get("lon") or e.get("center", {}).get("lon")
    if lat is None or lon is None:
        return None
    return float(lat), float(lon)


def el_name(e: dict) -> str:
    return (e.get("tags") or {}).get("name", "") or ""


def el_id(e: dict) -> str:
    return f"OSM:{e.get('type','?')}/{e.get('id','?')}"


def normalise(s: str) -> str:
    s = re.sub(r"\b(substation|switching station|terminal station|switchyard|sts|zone substation|ts|sts)\b",
               "", s, flags=re.IGNORECASE)
    s = re.sub(r"[^a-z0-9 ]+", " ", s.lower())
    s = re.sub(r"\s+", " ", s).strip()
    return s


def match_substations(states: list[str]) -> pd.DataFrame:
    """Try to match each lookup substation to an OSM substation in the same state."""
    subs = pd.read_csv(SUB_CSV)
    if "lat" not in subs.columns:
        subs["lat"] = pd.NA
    if "lon" not in subs.columns:
        subs["lon"] = pd.NA
    if "coord_source" not in subs.columns:
        subs["coord_source"] = ""
    if "coord_source_ref" not in subs.columns:
        subs["coord_source_ref"] = ""
    for c in ("coord_source", "coord_source_ref"):
        subs[c] = subs[c].astype(object)
    for c in ("lat", "lon"):
        subs[c] = pd.to_numeric(subs[c], errors="coerce")

    # Build per-state OSM substation index
    osm_subs_by_state = {}
    for st in states:
        els = load_osm(st, "substation")
        records = []
        for e in els:
            name = el_name(e)
            if not name:
                continue
            coord = el_coord(e)
            if coord is None:
                continue
            records.append({
                "name": name, "norm": normalise(name),
                "lat": coord[0], "lon": coord[1], "id": el_id(e),
                "voltage": (e.get("tags") or {}).get("voltage", ""),
            })
        osm_subs_by_state[st] = pd.DataFrame(
            records, columns=["name", "norm", "lat", "lon", "id", "voltage"]
        )
        print(f"  {st}/substation: {len(records)} OSM records", file=sys.stderr)

    matched = 0
    for i, row in subs.iterrows():
        if pd.notna(row.get("lat")) and pd.notna(row.get("lon")):
            continue  # already geocoded
        st = row["state"]
        if st not in osm_subs_by_state or len(osm_subs_by_state[st]) == 0:
            continue
        target = row["substation"]
        ntarget = normalise(target)
        if len(ntarget) < 3:
            continue
        # Substring match either way (OSM name often "Wollar Substation"; lookup says "Wollar")
        cands = osm_subs_by_state[st][
            osm_subs_by_state[st].norm.str.contains(re.escape(ntarget), regex=True, na=False)
            | osm_subs_by_state[st].norm.apply(lambda n: n in ntarget if n else False)
        ]
        if len(cands) == 0:
            continue
        # Prefer the highest-voltage match (typically the real transmission substation)
        cands = cands.copy()
        def vmax(v):
            try: return max(int(x) for x in re.findall(r"\d+", str(v))) if v else 0
            except: return 0
        cands["_vmax"] = cands["voltage"].apply(vmax)
        cands = cands.sort_values("_vmax", ascending=False)
        best = cands.iloc[0]
        subs.at[i, "lat"] = best["lat"]
        subs.at[i, "lon"] = best["lon"]
        subs.at[i, "coord_source"] = "OSM"
        subs.at[i, "coord_source_ref"] = best["id"]
        matched += 1
    print(f"\n  Matched {matched} of {len(subs)} lookup rows to OSM substations", file=sys.stderr)
    return subs


def match_projects(states: list[str]) -> pd.DataFrame:
    """Try to match each spike project to an OSM power=plant in the same state."""
    proj = pd.read_csv(PROJ_CSV)
    if "lat" not in proj.columns:
        proj["lat"] = pd.NA
    if "lon" not in proj.columns:
        proj["lon"] = pd.NA
    # Coerce string-typed bookkeeping columns to object so we can write text
    for c in ("source", "source_url_or_ref", "confidence"):
        if c in proj.columns:
            proj[c] = proj[c].astype(object)
    # Numeric coord columns
    for c in ("lat", "lon"):
        proj[c] = pd.to_numeric(proj[c], errors="coerce")

    osm_plants_by_state = {}
    for st in states:
        els = load_osm(st, "plant")
        records = []
        for e in els:
            name = el_name(e)
            if not name:
                continue
            coord = el_coord(e)
            if coord is None:
                continue
            records.append({
                "name": name, "norm": normalise(name),
                "lat": coord[0], "lon": coord[1], "id": el_id(e),
                "source": (e.get("tags") or {}).get("plant:source", "")
                          or (e.get("tags") or {}).get("power:source", ""),
            })
        osm_plants_by_state[st] = pd.DataFrame(
            records, columns=["name", "norm", "lat", "lon", "id", "source"]
        )
        print(f"  {st}/plant: {len(records)} OSM records", file=sys.stderr)

    matched = 0
    for i, row in proj.iterrows():
        if pd.notna(row.get("lat")) and pd.notna(row.get("lon")) and str(row.get("lat")).strip():
            continue
        region = row["region"]
        st = REGION_TO_STATE.get(region)
        if st is None or st not in osm_plants_by_state or len(osm_plants_by_state[st]) == 0:
            continue
        target = row["site_name"]
        ntarget = normalise(target)
        if len(ntarget) < 4:
            continue
        # Try substring both ways; prefer longest OSM match
        df = osm_plants_by_state[st]
        # Direct: target name appears in OSM name
        cands_a = df[df.norm.apply(lambda n: ntarget in n if n else False)]
        # Inverse: OSM name appears in target (catches "Bayswater Power Station" matching "Bayswater")
        cands_b = df[df.norm.apply(lambda n: bool(n) and len(n) >= 5 and n in ntarget)]
        cands = pd.concat([cands_a, cands_b]).drop_duplicates(subset=["id"])
        if len(cands) == 0:
            continue
        cands = cands.copy()
        cands["_score"] = cands["norm"].str.len()
        best = cands.sort_values("_score", ascending=False).iloc[0]
        proj.at[i, "lat"] = best["lat"]
        proj.at[i, "lon"] = best["lon"]
        proj.at[i, "source"] = "OSM_plant"
        proj.at[i, "source_url_or_ref"] = best["id"]
        proj.at[i, "confidence"] = "medium"  # name-substring match; needs sanity check
        matched += 1
    print(f"  Matched {matched} of {len(proj)} project rows to OSM plants", file=sys.stderr)
    return proj


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="Persist results back to CSVs")
    ap.add_argument("--states", nargs="+", default=["NSW", "VIC", "SA", "TAS", "QLD"])
    args = ap.parse_args()

    print("--- Substations ---", file=sys.stderr)
    subs = match_substations(args.states)
    print("\n--- Projects ---", file=sys.stderr)
    proj = match_projects(args.states)
    if args.write:
        subs.to_csv(SUB_CSV, index=False)
        proj.to_csv(PROJ_CSV, index=False)
        print(f"\nWrote {SUB_CSV.relative_to(REPO)} ({len(subs)} rows)", file=sys.stderr)
        print(f"Wrote {PROJ_CSV.relative_to(REPO)} ({len(proj)} rows)", file=sys.stderr)
    else:
        print("\n(dry run — pass --write to persist)", file=sys.stderr)


if __name__ == "__main__":
    main()
