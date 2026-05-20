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


MIN_OSM_TOKEN_LEN = 4  # OSM names shorter than this after normalisation are too generic to match safely


def is_safe_osm_name(norm: str) -> bool:
    """Reject names that would substring-match too liberally.

    Filters out short/generic names like "A", "Bay", "Power", numeric-only
    designations, and single-letter substation labels. These produce
    false-positive matches against our lookup substations.
    """
    if not norm or len(norm) < MIN_OSM_TOKEN_LEN:
        return False
    # Single-token generic names
    GENERIC = {"power", "bay", "main", "north", "south", "east", "west", "central",
               "switch", "yard", "kv", "hv", "lv"}
    tokens = norm.split()
    if len(tokens) == 1 and tokens[0] in GENERIC:
        return False
    return True


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
            norm = normalise(name)
            if not is_safe_osm_name(norm):
                continue  # skip too-generic OSM names that would match many lookup rows
            records.append({
                "name": name, "norm": norm,
                "lat": coord[0], "lon": coord[1], "id": el_id(e),
                "voltage": (e.get("tags") or {}).get("voltage", ""),
            })
        osm_subs_by_state[st] = pd.DataFrame(
            records, columns=["name", "norm", "lat", "lon", "id", "voltage"]
        )
        print(f"  {st}/substation: {len(records)} OSM records (after generic-name filter)", file=sys.stderr)

    n_subs = len(subs)
    matched = 0
    progress_every = max(100, n_subs // 20)
    for counter, (i, row) in enumerate(subs.iterrows(), start=1):
        if counter % progress_every == 0:
            print(f"    substation match progress: {counter}/{n_subs} (matched so far: {matched})", file=sys.stderr)
        if pd.notna(row.get("lat")) and pd.notna(row.get("lon")):
            continue  # already geocoded
        st = row["state"]
        if st not in osm_subs_by_state or len(osm_subs_by_state[st]) == 0:
            continue
        target = row["substation"]
        ntarget = normalise(target)
        if len(ntarget) < 3:
            continue
        # Match priorities (most specific to least):
        # 1. Exact normalised equality (best)
        # 2. Target name fully contains OSM name (OSM name appears as a complete
        #    token sequence in target — e.g. lookup "Bayswater" inside OSM "Bayswater Substation")
        # 3. OSM name contains target as a complete word boundary (e.g. lookup "Wollar"
        #    inside OSM "Wollar Substation" after normalisation)
        # We DO NOT do generic substring matching anymore — it false-positives.
        osm_df = osm_subs_by_state[st]
        # Word-boundary regex: \b around the target on both sides
        wb = r"(?:^|\s)" + re.escape(ntarget) + r"(?:\s|$)"
        cands = osm_df[osm_df.norm.str.contains(wb, regex=True, na=False)]
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
    """Try to match each spike project to an OSM power=plant in the same state.

    Per-state, pre-compile a single alternation regex over all eligible OSM
    plant names (length ≥ 6) once, then run one regex.search per project
    instead of N regex compilations per project. This is the difference
    between O(projects × OSM_names) regex ops and O(projects) at scale.
    """
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
        # Filter plants the same way to be safe
        records = [r for r in records if is_safe_osm_name(r["norm"])]
        osm_plants_by_state[st] = pd.DataFrame(
            records, columns=["name", "norm", "lat", "lon", "id", "source"]
        )
        print(f"  {st}/plant: {len(records)} OSM records (after generic-name filter)", file=sys.stderr)

    # Pre-compile per-state alternation regex over OSM names (length ≥ 6).
    # One compiled regex per state -> O(1) search per project.
    osm_alt_re = {}
    for st, df in osm_plants_by_state.items():
        if len(df) == 0:
            osm_alt_re[st] = None
            continue
        long_names = df[df.norm.str.len() >= 6].copy()
        if len(long_names) == 0:
            osm_alt_re[st] = None
            continue
        # Dedup on norm — multiple OSM features can share the same normalised
        # name (e.g. several "Tamworth ..." substations); keep the first.
        long_names = long_names.drop_duplicates(subset=["norm"])
        # Sort by descending length so longer/more-specific match first in regex alternation
        long_names = (long_names.assign(_len=long_names.norm.str.len())
                                .sort_values("_len", ascending=False)
                                .drop(columns=["_len"]))
        names_sorted = long_names.norm.tolist()
        alt = "|".join(re.escape(n) for n in names_sorted)
        pat = re.compile(r"(?:^|\s)(" + alt + r")(?:\s|$)")
        osm_alt_re[st] = (pat, long_names.set_index("norm")[["lat", "lon", "id"]].to_dict("index"))

    n_projects = len(proj)
    matched = 0
    progress_every = max(100, n_projects // 20)
    for counter, (i, row) in enumerate(proj.iterrows(), start=1):
        if counter % progress_every == 0:
            print(f"    project match progress: {counter}/{n_projects} (matched so far: {matched})", file=sys.stderr)
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
        df = osm_plants_by_state[st]
        # Forward match: project's normalised name appears as a token sequence in any OSM name
        wb_target = r"(?:^|\s)" + re.escape(ntarget) + r"(?:\s|$)"
        cands_a = df[df.norm.str.contains(wb_target, regex=True, na=False)]
        # Reverse match: precompiled alternation finds the FIRST OSM long-name embedded in target
        cands_b_records = []
        pair = osm_alt_re.get(st)
        if pair:
            pat, lookup = pair
            mm = pat.search(ntarget)
            if mm:
                osm_norm = mm.group(1)
                hit = lookup.get(osm_norm)
                if hit:
                    cands_b_records.append({"norm": osm_norm, **hit})
        cands_b = pd.DataFrame(cands_b_records)
        cands = pd.concat([cands_a, cands_b], ignore_index=True).drop_duplicates(subset=["id"])
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
    print(f"  Matched {matched} of {n_projects} project rows to OSM plants", file=sys.stderr)
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
