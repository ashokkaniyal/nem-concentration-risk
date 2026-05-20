"""
AEMO Generation Information parser and panel builder.

Loads quarterly Generation Information xlsx files, normalises the schema across
years (column-name whitespace drift handled), joins the transmission-catchment
lookup, and detects project status transitions across consecutive releases.

The catchment tag is a professional-judgement proxy for shared transmission
topology — *not* a formal REZ membership. The grid is meshed: power flows
across REZ polygon boundaries via shared substations and transmission corridors,
which is precisely why crowding around a corridor matters analytically.
"""
from __future__ import annotations

import re
import warnings
from datetime import datetime
from pathlib import Path
from typing import Optional

import pandas as pd

# Sheet that contains the project register. The exact name varies slightly across
# releases — AEMO used 'ExistingGen&NewDevs' in the 2022-05 release before reverting
# to 'ExistingGeneration&NewDevs'. We probe both.
PROJECT_SHEET_CANDIDATES = (
    "ExistingGeneration&NewDevs",
    "ExistingGen&NewDevs",
)

# AEMO uses slightly different column names across years (whitespace mostly).
# Normalise everything to snake_case canonical names.
COLUMN_ALIASES = {
    # canonical: [variants seen across releases]
    "region": ["Region"],
    "asset_type": ["Asset Type"],
    "site_name": ["Site Name"],
    "owner": ["Owner"],
    "technology_type": ["Technology Type"],
    "fuel_type": ["Fuel Type"],
    "duid": ["DUID"],
    "num_units": ["Number of Units"],
    "lower_nameplate_mw": ["Lower Nameplate Capacity (MW)"],
    "upper_nameplate_mw": ["Upper Nameplate Capacity (MW)"],
    "agg_lower_nameplate_mw": ["Aggregated Lower Nameplate Capacity (MW)"],
    "agg_upper_nameplate_mw": ["Aggregated Upper Nameplate Capacity (MW)"],
    "nameplate_mw": ["Nameplate Capacity (MW)"],
    "storage_mwh": ["Storage Capacity (MWh)"],
    "unit_status": ["Unit Status"],
    "dispatch_type": ["Dispatch Type"],
    "full_commercial_use_date": ["Full Commercial Use Date"],
    "expected_closure_year": ["Expected Closure Year"],
    "closure_date": ["Closure Date"],
    "status_bucket": ["Status Bucket Summary", "StatusBucketSummary"],
    "fuel_bucket": ["Fuel Bucket Summary", "FuelBucketSummary"],
    "survey_id": ["SurveyId"],
    "kci_id": ["AEMO KCI Id"],
    "survey_last_requested": ["Survey Last Requested"],
    "survey_version_datetime": [
        "Survey Version DateTime",
        "SurveyVersionDateTime",
        "SurveyEffectiveDate",
    ],
}

# Inverse: each variant -> canonical name
_VARIANT_TO_CANON = {v: canon for canon, vs in COLUMN_ALIASES.items() for v in vs}


def parse_release_date_from_filename(path: Path) -> Optional[datetime]:
    """Extract YYYY-MM from filenames like 'nem-gen-info-2024-07.xlsx'."""
    m = re.search(r"(\d{4})-(\d{2})", str(path.name))
    if not m:
        return None
    year, month = int(m.group(1)), int(m.group(2))
    return datetime(year, month, 1)


def load_release(path: Path, release_date: Optional[datetime] = None) -> pd.DataFrame:
    """Load one AEMO Generation Information xlsx into a normalised DataFrame.

    Header is on row 2 (1-indexed); data starts row 3.
    Region values for some rows are footnote text ('Battery of the Nation -...'); these are dropped.
    """
    path = Path(path)
    if release_date is None:
        release_date = parse_release_date_from_filename(path)
        if release_date is None:
            raise ValueError(
                f"Cannot infer release_date from {path.name}; pass it explicitly"
            )

    raw = pd.read_excel(path, sheet_name=None, header=1, engine="openpyxl")
    # raw is dict of sheet_name -> DataFrame; pick the first candidate that exists
    sheet_df = None
    for cand in PROJECT_SHEET_CANDIDATES:
        if cand in raw:
            sheet_df = raw[cand]
            break
    if sheet_df is None:
        raise ValueError(
            f"{path.name}: none of expected sheets {PROJECT_SHEET_CANDIDATES} found. "
            f"Available sheets: {list(raw.keys())}"
        )

    # Rename to canonical snake_case where we know the alias; drop unknown columns
    rename = {c: _VARIANT_TO_CANON[c] for c in sheet_df.columns if c in _VARIANT_TO_CANON}
    df = sheet_df.rename(columns=rename)
    df = df[[c for c in df.columns if c in _VARIANT_TO_CANON.values()]]
    # Some releases have multiple Survey* columns that canonicalise to the same name.
    # Keep first occurrence of each canonical column.
    df = df.loc[:, ~df.columns.duplicated()]

    # Filter to real region rows (drop the footnote rows AEMO sticks at the bottom)
    real_regions = {"NSW1", "QLD1", "SA1", "TAS1", "VIC1"}
    df = df[df["region"].isin(real_regions)].copy()

    # Drop rows with no site name
    df = df[df["site_name"].notna()].copy()
    df["site_name"] = df["site_name"].astype(str).str.strip()

    # Coerce capacity to numeric
    for c in [
        "lower_nameplate_mw", "upper_nameplate_mw",
        "agg_lower_nameplate_mw", "agg_upper_nameplate_mw",
        "nameplate_mw", "storage_mwh", "num_units",
    ]:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")

    # Add release_date column
    df["release_date"] = release_date

    return df.reset_index(drop=True)


def load_all_releases(directory: Path) -> pd.DataFrame:
    """Load every xlsx in `directory` matching the AEMO filename pattern.

    Returns a long-format panel: one row per (project, release_date).
    """
    directory = Path(directory)
    files = sorted(directory.glob("nem-gen-info-*.xlsx"))
    if not files:
        raise FileNotFoundError(f"No nem-gen-info-*.xlsx files in {directory}")
    frames = [load_release(f) for f in files]
    panel = pd.concat(frames, ignore_index=True)
    return panel


def join_catchment(
    panel: pd.DataFrame,
    lookup_path: Path,
    regions: Optional[list[str]] = None,
    region: Optional[str] = None,
) -> pd.DataFrame:
    """Left-join the NEM-wide cross-validated catchment lookup onto a panel.

    Reads the v0.7 canonical schema's final ``catchment`` and
    ``catchment_confidence`` columns (NOT the legacy ``transmission_catchment``
    column, which is preserved in the lookup only for traceability). The joined
    panel exposes the final value under both ``catchment`` and
    ``transmission_catchment`` (the latter as a backward-compatible alias for
    downstream code such as ``detect_status_transitions`` and notebook 06).

    Args:
        panel: long-format project panel (must have ``region`` and ``site_name``).
        lookup_path: path to ``transmission_catchment_lookup.csv`` (v0.7+).
        regions: list of AEMO region codes to keep classified, e.g.
            ``["NSW1", "VIC1"]``. Rows outside the list are overwritten to
            "Other NEM region" / confidence "n/a". ``None`` (default) applies no
            region filter — every project keeps its lookup catchment (NEM-wide).
        region: DEPRECATED single-region string (e.g. "QLD1"). If given, it is
            treated as ``regions=[region]`` and emits a DeprecationWarning.

    Unmatched rows (in `regions` but absent from the lookup) → catchment
    "Unclassified", confidence "review". Lookup rows already tagged "unresolved"
    (the Quandong case) pass through verbatim.
    """
    if region is not None:
        warnings.warn(
            "'region' is deprecated, use 'regions=[...]' for explicit region filtering",
            DeprecationWarning,
            stacklevel=2,
        )
        if regions is None:
            regions = [region]

    lookup = pd.read_csv(lookup_path)

    # Schema validation — require the v0.7 final columns.
    if "catchment" not in lookup.columns or "catchment_confidence" not in lookup.columns:
        legacy = "transmission_catchment" in lookup.columns
        raise ValueError(
            f"{lookup_path} is missing the v0.7 final columns "
            f"('catchment', 'catchment_confidence'). "
            + (
                "This looks like a pre-v0.7 lookup with only the legacy "
                "'transmission_catchment' column. "
                if legacy else ""
            )
            + "Use the NEM-wide cross-validated lookup committed in v0.7 "
            "(commit 6ca5632); see data/rez/catchment_lookup_schema.md."
        )

    joined = panel.merge(
        lookup[["site_name", "catchment", "catchment_confidence"]],
        on="site_name", how="left",
    )

    # Region filter (only when `regions` given): rows outside the listed regions
    # are tagged out-of-scope so they don't masquerade as classified.
    if regions is not None:
        mask_other = ~joined["region"].isin(regions)
        joined.loc[mask_other, "catchment"] = "Other NEM region"
        joined.loc[mask_other, "catchment_confidence"] = "n/a"

    # In-scope rows with no lookup match -> Unclassified.
    joined["catchment"] = joined["catchment"].fillna("Unclassified")
    joined["catchment_confidence"] = joined["catchment_confidence"].fillna("review")

    # Backward-compatible alias for downstream code that reads transmission_catchment.
    joined["transmission_catchment"] = joined["catchment"]
    return joined


def detect_status_transitions(panel: pd.DataFrame) -> pd.DataFrame:
    """Detect status_bucket changes between consecutive releases for each project.

    A 'project' is identified by site_name + dispatch_type + fuel_type (handles
    cases where one site has multiple units/stages with different trajectories).
    Returns event log with: project_key, site_name, technology, capacity_mw,
    transmission_catchment, from_release, to_release, from_status, to_status.
    """
    p = panel.copy()
    # Project key: site_name|fuel_type|dispatch_type captures most uniqueness;
    # fall back gracefully if columns missing
    p["project_key"] = (
        p["site_name"].fillna("")
        + "|" + p.get("fuel_type", pd.Series([""] * len(p))).fillna("").astype(str)
        + "|" + p.get("dispatch_type", pd.Series([""] * len(p))).fillna("").astype(str)
    )
    p = p.sort_values(["project_key", "release_date"]).reset_index(drop=True)

    # Lag status_bucket within each project_key
    p["prev_status"] = p.groupby("project_key")["status_bucket"].shift(1)
    p["prev_release"] = p.groupby("project_key")["release_date"].shift(1)

    # Transitions: status_bucket different from prev_status (and prev_status not null)
    transitions = p[
        p["prev_status"].notna() & (p["status_bucket"] != p["prev_status"])
    ].copy()

    out_cols = [
        "project_key", "site_name", "region", "technology_type", "fuel_type",
        "transmission_catchment", "catchment_confidence",
        "prev_release", "release_date", "prev_status", "status_bucket",
        "nameplate_mw", "agg_upper_nameplate_mw", "owner", "duid",
    ]
    out_cols = [c for c in out_cols if c in transitions.columns]
    transitions = transitions[out_cols].rename(columns={
        "prev_release": "from_release",
        "release_date": "to_release",
        "prev_status": "from_status",
        "status_bucket": "to_status",
    })
    return transitions.reset_index(drop=True)


def latest_project_snapshot(panel: pd.DataFrame) -> pd.DataFrame:
    """Return the most recent release-snapshot of each project."""
    p = panel.sort_values("release_date")
    return p.groupby(["site_name", "fuel_type"], dropna=False).tail(1).reset_index(drop=True)
