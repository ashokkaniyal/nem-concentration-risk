"""
Corporate event register: loaders, validators, filter helpers.

Layer B in the three-layer information taxonomy. These are events generated
by named private-sector actors (companies, funds, OEMs) rather than by
institutional policy actors. Examples: project FIDs, commissioning
announcements, M&A transactions, capital raises, strategy updates.

Important methodological distinction from policy events:

  - Policy events (Layer A) are exogenous: they are produced by
    institutional actors who are not themselves part of the investor
    herd. They go into Hawkes regressions as exogenous covariates.

  - Corporate events (Layer B) are endogenous: the firms producing them
    are part of the herd. They go into Hawkes regressions as the point
    process being modelled, with self-excitation parameters capturing
    the feedback structure.

Treating Layer B events as covariates would introduce endogeneity bias
and the framework would produce numbers but not meaning. Be disciplined
about which layer each event belongs to.

The corporate register joins to `data/actors.csv` on actor_id for the
actor's metadata (name, type, listed status, ticker, parent, etc.).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import pandas as pd

# Controlled vocabularies for corporate events. Different from policy events:
# these track corporate actions, not policy announcements.

VALID_EVENT_TYPES = {
    "fid",                        # final investment decision on a project
    "commissioning",              # project energisation
    "acquisition",                # M&A: acquiring an asset or company
    "divestment",                 # M&A: selling an asset
    "asset_purchase",             # buying specific assets (vs full company)
    "takeover",                   # full takeover of a listed company
    "delisting",                  # delisting from a stock exchange
    "capital_raise",              # equity or debt issuance
    "joint_venture",              # JV formation or restructure
    "pipeline_announcement",      # major project pipeline disclosure
    "project_announcement",       # specific project announcement
    "strategy_update",            # strategic direction announcement
    "quarterly_results",          # earnings / quarterly update
    "restructuring",              # corporate restructuring
    "access_rights_award",        # awarded REZ access rights
    "project_acceleration",       # acceleration of existing pipeline
    "capital_deployment",         # large-scale capital commitment
    "policy_environment_shift",   # non-corporate event affecting all actors
}

VALID_SOURCE_TYPES = {
    "asx_disclosure",       # ASX Markets Announcements Platform
    "media_release",        # company's own media/press page
    "trade_press",          # third-party trade press article
    "broker_note",          # equity research note (rare in free-sources mode)
    "linkedin",             # LinkedIn post by company or executive
    "conference_presentation",  # disclosed in conference materials
    "regulatory_filing",    # non-ASX regulatory filing (e.g. CCS, ACCC)
    "annual_report",        # company annual report
}

VALID_CONFIDENCE = {"verified", "needs_verify", "uncertain"}

VALID_TECHNOLOGIES = {
    "wind",
    "solar",
    "battery",
    "pumped_hydro",
    "hydro",
    "gas",
    "coal",
    "biomass",
    "solar+wind+storage",  # hybrid
    "solar+storage",
    "wind+storage",
    "",                    # not applicable / unknown
}


@dataclass(frozen=True)
class CorporateEvent:
    """A single corporate event."""
    event_id: str
    date: date
    actor_id: str
    actor_name: str
    actor_type: str
    event_type: str
    project_name: Optional[str]
    nem_region: Optional[str]
    rez: Optional[str]
    capacity_mw: Optional[float]
    technology: Optional[str]
    source_type: str
    description: str
    source_url: Optional[str]
    confidence: str
    notes: str
    date_is_partial: bool


def _parse_partial_date(date_str: str) -> tuple[date, bool]:
    """Same convention as in events.py: XX placeholders pin to mid-month / mid-year."""
    date_str = date_str.strip()
    is_partial = "XX" in date_str
    if is_partial:
        parts = date_str.split("-")
        year = int(parts[0])
        month = 7 if parts[1] == "XX" else int(parts[1])
        day = 15 if parts[2] == "XX" else int(parts[2])
        return date(year, month, day), True
    return datetime.strptime(date_str, "%Y-%m-%d").date(), False


def load_actors(
    path: Path | str = "data/actors.csv",
) -> pd.DataFrame:
    """Load the actors register."""
    df = pd.read_csv(path, dtype=str).fillna("")
    if df["actor_id"].duplicated().any():
        dupes = df[df["actor_id"].duplicated(keep=False)]["actor_id"].tolist()
        raise ValueError(f"Duplicate actor_ids: {dupes}")
    return df


def load_corporate_events(
    events_path: Path | str = "data/events/corporate_events.csv",
    actors_path: Path | str = "data/actors.csv",
    drop_partial_dates: bool = False,
    confidence_min: str = "needs_verify",
    join_actors: bool = True,
) -> pd.DataFrame:
    """
    Load the corporate event register with validation and optional actor join.

    Parameters
    ----------
    events_path : Path or str
        Path to the corporate events CSV.
    actors_path : Path or str
        Path to the actors register. Used for the actor metadata join.
    drop_partial_dates : bool
        If True, drop events where the original date had XX placeholders.
    confidence_min : str
        Minimum confidence level to include.
    join_actors : bool
        If True, join actor metadata onto each event row.

    Returns
    -------
    DataFrame with parsed dates, validated categoricals, optionally joined actors.
    """
    df = pd.read_csv(events_path, dtype=str).fillna("")

    parsed = df["date"].apply(_parse_partial_date)
    df["date"] = parsed.apply(lambda t: t[0])
    df["date_is_partial"] = parsed.apply(lambda t: t[1])

    # Capacity is numeric where present
    df["capacity_mw"] = pd.to_numeric(df["capacity_mw"], errors="coerce")

    # Validate controlled vocabs
    _validate_column(df, "event_type", VALID_EVENT_TYPES)
    _validate_column(df, "source_type", VALID_SOURCE_TYPES)
    _validate_column(df, "confidence", VALID_CONFIDENCE)
    _validate_column(df, "technology", VALID_TECHNOLOGIES)

    # Confidence filter
    confidence_order = ["verified", "needs_verify", "uncertain"]
    min_idx = confidence_order.index(confidence_min)
    allowed = set(confidence_order[: min_idx + 1])
    df = df[df["confidence"].isin(allowed)].copy()

    if drop_partial_dates:
        df = df[~df["date_is_partial"]].copy()

    if join_actors:
        actors = load_actors(actors_path)
        # Some rows (like c018 - policy environment shift) have no actor;
        # use left join and leave actor fields blank for those
        df = df.merge(
            actors[["actor_id", "actor_name", "actor_type", "listed",
                    "ticker", "parent", "jurisdiction_focus"]],
            on="actor_id",
            how="left",
        )

    return df.sort_values("date").reset_index(drop=True)


def _validate_column(df: pd.DataFrame, col: str, valid: set) -> None:
    bad = df[~df[col].isin(valid)]
    if len(bad) > 0:
        bad_values = bad[col].unique().tolist()
        raise ValueError(
            f"Column '{col}' contains invalid values: {bad_values}. "
            f"Valid values: {sorted(valid)}"
        )


# ----- Filter helpers ---------------------------------------------------------


def events_for_actor(events: pd.DataFrame, actor_id: str) -> pd.DataFrame:
    """All events for a specific actor."""
    return events[events["actor_id"] == actor_id].copy()


def events_for_actor_type(events: pd.DataFrame, actor_type: str) -> pd.DataFrame:
    """
    All events for actors of a given type (utility, developer, fund, etc.).
    Requires that actor metadata has been joined.
    """
    if "actor_type" not in events.columns:
        raise ValueError(
            "actor_type not in events columns. "
            "Did you load with join_actors=True?"
        )
    return events[events["actor_type"] == actor_type].copy()


def events_in_rez(events: pd.DataFrame, rez_code: str) -> pd.DataFrame:
    """
    Events tagged to a specific REZ. Note: an event can be tagged to
    multiple REZs (comma-separated in the rez column); this filter
    returns events that mention the REZ anywhere in that field.
    """
    return events[events["rez"].str.contains(rez_code, na=False)].copy()


def events_of_type(events: pd.DataFrame, event_type: str) -> pd.DataFrame:
    """Events of a specific type (fid, commissioning, acquisition, etc.)."""
    if event_type not in VALID_EVENT_TYPES:
        raise ValueError(
            f"event_type must be one of {sorted(VALID_EVENT_TYPES)}"
        )
    return events[events["event_type"] == event_type].copy()


def actor_lead_lag_pairs(
    events: pd.DataFrame,
    max_lag_days: int = 180,
) -> pd.DataFrame:
    """
    Identify pairs of (leader_actor, follower_actor) where the follower's
    event follows the leader's event within max_lag_days, for the same
    event_type and REZ.

    This is the primitive for the "who leads the herd?" analysis -
    actors who consistently appear as leaders (across many pairs) are
    candidates for the synchronisation-driver role.

    Returns DataFrame with columns:
        leader_id, follower_id, event_type, rez,
        leader_date, follower_date, lag_days

    Caveat: this gives you raw counts of lead-lag occurrences. To turn
    these into a statistical statement you need to compare against a null
    model (random pairing). Don't over-interpret the raw counts.
    """
    pairs = []
    grouped = events.groupby(["event_type", "rez"], dropna=False)
    for (event_type, rez), group in grouped:
        if not rez:  # skip events without REZ tags
            continue
        sorted_group = group.sort_values("date").reset_index(drop=True)
        for i, leader in sorted_group.iterrows():
            for j in range(i + 1, len(sorted_group)):
                follower = sorted_group.iloc[j]
                lag = (follower["date"] - leader["date"]).days
                if lag > max_lag_days:
                    break
                if leader["actor_id"] == follower["actor_id"]:
                    continue
                pairs.append({
                    "leader_id": leader["actor_id"],
                    "follower_id": follower["actor_id"],
                    "event_type": event_type,
                    "rez": rez,
                    "leader_date": leader["date"],
                    "follower_date": follower["date"],
                    "lag_days": lag,
                })
    return pd.DataFrame(pairs)


if __name__ == "__main__":
    import sys
    events_csv = sys.argv[1] if len(sys.argv) > 1 else "data/events/corporate_events.csv"
    actors_csv = sys.argv[2] if len(sys.argv) > 2 else "data/actors.csv"
    events = load_corporate_events(events_csv, actors_csv)
    print(f"Loaded {len(events)} corporate events from {events_csv}")
    print(f"Date range: {events['date'].min()} to {events['date'].max()}")
    print(f"Partial-date events: {events['date_is_partial'].sum()}")
    print(f"Verified events: {(events['confidence'] == 'verified').sum()}")
    print(f"\nBy event_type:")
    print(events["event_type"].value_counts().to_string())
    print(f"\nBy actor_type:")
    print(events["actor_type"].value_counts().to_string())
