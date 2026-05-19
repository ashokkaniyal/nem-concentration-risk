"""Build the draft NEM-wide transmission_catchment lookup for non-QLD regions.

Strategy mirrors the existing QLD lookup pattern:
  - case-insensitive substring match of substation/region names against site_name
  - high confidence on substation hit, medium on region/town hit
  - 'review' when no match or multiple ambiguous matches
  - matched_keyword captures the hit; rationale describes the corridor

QLD rows (catchments built from Powerlink TAPR) are preserved as-is. Non-QLD rows
are appended, with phantom_risk and owner_tier left blank (separate manual review).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "src"))
from nem_herding.projects import load_release  # noqa: E402

DATA = REPO / "data"
REZ = DATA / "rez"
PANEL_DIR = DATA / "projects" / "aemo_geninfo"

QLD_LOOKUP = REZ / "transmission_catchment_lookup.csv"
SUB_LOOKUP = REZ / "rez_substation_lookup_NEM.csv"
OUT = REZ / "transmission_catchment_lookup_draft_v2.csv"

# Map user-specified catchment codes to a human-readable rationale prefix.
RATIONALE_BY_REZ = {
    "CWO": "Central-West Orana REZ corridor (Elong Elong/Merotherie/Wollar)",
    "NEW": "New England REZ corridor (Armidale/Tamworth/Dumaresq)",
    "HCC": "Hunter-Central Coast REZ corridor (Bayswater/Eraring/Singleton)",
    "ILW": "Illawarra REZ corridor (Dapto/Avon/Wollongong)",
    "SW-NSW": "South-West NSW REZ corridor (Buronga/Dinawan/Wagga/PEC)",
    "CN-VIC": "Central North Victoria REZ corridor (Bendigo/Shepparton)",
    "MR": "Murray River REZ corridor (Kerang/Red Cliffs/PEC western feed)",
    "WV": "Western Victoria REZ corridor (Bulgana/Ararat/WRL)",
    "GIP": "Gippsland REZ corridor (Latrobe Valley 500 kV)",
    "SW-VIC": "South-West Victoria REZ corridor (Mortlake/Moorabool/Heywood)",
    "MN": "Mid-North SA REZ corridor (Robertstown/Davenport/Cultana)",
    "SE-SA": "South-East SA REZ corridor (Tailem Bend/Tungkillo/Heywood interconnector)",
    "RIV": "Riverland REZ corridor (Renmark/Berri/Loxton)",
    "TAS-NW": "Tasmania single catchment (NW Transmission Devs + Central Highlands hydro)",
}

# REZ priority for tie-breaking when a substation name appears in multiple REZs
# (e.g. Bayswater is named in both HCC and NEW; geographically in HCC).
# Lower number = higher priority.
PRIORITY = {
    "CWO": 1, "NEW": 1, "HCC": 1, "ILW": 1, "SW-NSW": 1,
    "WV": 1, "GIP": 1, "SW-VIC": 1, "MR": 1, "CN-VIC": 1,
    "MN": 1, "SE-SA": 1, "RIV": 1, "TAS-NW": 1,
}

REGION_TO_STATE = {"NSW1": "NSW", "VIC1": "VIC", "SA1": "SA", "TAS1": "TAS"}


def load_substation_index() -> pd.DataFrame:
    sub = pd.read_csv(SUB_LOOKUP)
    # Normalise for matching
    sub["substation_norm"] = sub["substation"].str.lower().str.strip()
    return sub


def collect_unique_site_names() -> pd.DataFrame:
    """Pool unique (region, site_name) pairs across all releases."""
    files = sorted(PANEL_DIR.glob("nem-gen-info-*.xlsx"))
    frames = []
    for f in files:
        try:
            frames.append(load_release(f)[["region", "site_name"]])
        except Exception as e:
            print(f"  skip {f.name}: {e}", file=sys.stderr)
    panel = pd.concat(frames, ignore_index=True).drop_duplicates(["region", "site_name"])
    panel = panel[panel["region"].isin(REGION_TO_STATE)]
    panel["site_name"] = panel["site_name"].astype(str).str.strip()
    return panel.reset_index(drop=True)


def match_site(site_name: str, state: str, sub_state: pd.DataFrame) -> dict:
    """Match one site against substation list for its state.

    Returns dict with catchment, confidence, matched_keyword, rationale.
    """
    s = site_name.lower()
    hits = []
    for _, row in sub_state.iterrows():
        kw = row["substation_norm"]
        if not kw:
            continue
        # Substring match using word-boundary-aware check (avoid 'Hay' matching 'Haywarra')
        # Simple rule: surround with non-letter sentinels.
        padded = f" {s} "
        if f" {kw} " in padded or padded.startswith(f"{kw} ") or padded.endswith(f" {kw}"):
            hits.append(row)
        elif kw in s and (len(kw) >= 6 or " " in kw):
            # Allow substring match for longer/multi-word substation names
            hits.append(row)

    if not hits:
        return {
            "catchment": "Unclassified",
            "confidence": "review",
            "matched_keyword": "",
            "rationale": "No rule matched — manual review needed",
        }

    # If multiple REZ hits, pick the highest-priority one; if same priority, prefer 'high' over 'medium'
    def sort_key(r):
        return (
            PRIORITY.get(r["rez_code"], 99),
            0 if r["confidence_default"] == "high" else 1,
            -len(r["substation_norm"]),  # prefer longer/more specific
        )

    hits_sorted = sorted(hits, key=sort_key)
    best = hits_sorted[0]
    distinct_rez = {h["rez_code"] for h in hits}

    confidence = best["confidence_default"]
    if len(distinct_rez) > 1:
        # Genuine cross-REZ ambiguity → demote
        confidence = "review" if confidence == "medium" else "medium"
        rationale = (
            f"{RATIONALE_BY_REZ.get(best['rez_code'], best['rez_code'])} — "
            f"shared keyword across REZs: {sorted(distinct_rez)}; "
            f"primary assignment based on substation locality"
        )
    else:
        rationale = RATIONALE_BY_REZ.get(best["rez_code"], best["rez_code"])

    return {
        "catchment": best["rez_code"],
        "confidence": confidence,
        "matched_keyword": best["substation"],
        "rationale": rationale,
    }


def main():
    sub = load_substation_index()
    panel = collect_unique_site_names()

    # Pull the most recent release for capacity / tech metadata
    latest_file = sorted(PANEL_DIR.glob("nem-gen-info-*.xlsx"))[-1]
    print(f"Using latest release for metadata: {latest_file.name}", file=sys.stderr)
    latest = load_release(latest_file)

    # Pick best capacity (max of available capacity cols) per site_name
    cap_cols = [
        "upper_nameplate_mw", "agg_upper_nameplate_mw",
        "nameplate_mw", "lower_nameplate_mw",
    ]
    cap_cols = [c for c in cap_cols if c in latest.columns]
    latest["best_cap"] = latest[cap_cols].max(axis=1, skipna=True)
    site_meta = (
        latest.groupby("site_name")
        .agg(best_capacity_mw=("best_cap", "max"),
             technology=("technology_type", "first"),
             fuel=("fuel_type", "first"),
             owner=("owner", "first"))
        .reset_index()
    )

    rows = []
    for _, p in panel.iterrows():
        state = REGION_TO_STATE[p["region"]]
        if state == "QLD":  # not reached, but guard
            continue
        # User-specified single TAS catchment: blanket-tag every TAS1 site
        if state == "TAS":
            m = {
                "catchment": "TAS-NW",
                "confidence": "high",
                "matched_keyword": "(TAS region)",
                "rationale": RATIONALE_BY_REZ["TAS-NW"]
                + " — single user-specified catchment covers all TAS1 sites",
            }
        else:
            sub_state = sub[sub["state"] == state]
            m = match_site(p["site_name"], state, sub_state)
        rows.append({
            "site_name": p["site_name"],
            "transmission_catchment": m["catchment"],
            "catchment_confidence": m["confidence"],
            "rationale": m["rationale"],
            "matched_keyword": m["matched_keyword"],
            "_state": state,
        })
    nonqld = pd.DataFrame(rows)
    nonqld = nonqld.merge(site_meta, on="site_name", how="left")

    # Schema alignment to QLD lookup
    qld = pd.read_csv(QLD_LOOKUP)
    schema_cols = list(qld.columns)
    for c in schema_cols:
        if c not in nonqld.columns:
            nonqld[c] = ""
    # Per instructions: leave phantom_risk + owner_tier blank for non-QLD
    nonqld["phantom_risk"] = ""
    nonqld["phantom_flags"] = ""
    nonqld["owner_tier"] = ""
    nonqld = nonqld[schema_cols]  # column order

    out = pd.concat([qld, nonqld], ignore_index=True)
    out.to_csv(OUT, index=False)

    # Summary
    print(f"\nWrote {OUT.relative_to(REPO)} — {len(out)} rows ({len(qld)} QLD preserved + {len(nonqld)} non-QLD).", file=sys.stderr)
    nonqld_with_state = nonqld.copy()
    nonqld_with_state["_state"] = [r["_state"] for r in rows]
    print("\nPer-state classification counts:", file=sys.stderr)
    print(nonqld_with_state.groupby("_state").size().to_string(), file=sys.stderr)

    print("\nPer-catchment breakdown (non-QLD):", file=sys.stderr)
    print(nonqld_with_state.groupby(["_state", "transmission_catchment"]).size().to_string(), file=sys.stderr)

    print("\nConfidence breakdown (non-QLD):", file=sys.stderr)
    print(nonqld_with_state.groupby(["_state", "catchment_confidence"]).size().to_string(), file=sys.stderr)


if __name__ == "__main__":
    main()
