"""
Policy event register: loaders, validators, and filter helpers.

The event register is the canonical record of NEM-relevant policy announcements
that could plausibly synchronise investor behaviour. Each event has:

- A stable event_id for cross-referencing
- A date (with partial-date conventions for events whose exact date is unverified)
- A jurisdiction and scope
- A pre-registered category and coupling_layer (these encode hypothesis predictions)
- A confidence flag indicating verification status

The categorisation columns (category, coupling_layer, information_unification)
encode hypotheses about how the event should affect synchronisation. Once an
event is categorised, it should NOT be re-categorised after looking at the data.
Doing so collapses the falsifiability of the framework.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Optional

import pandas as pd

# Controlled vocabularies. Keep these tight - if you find yourself wanting to
# add a new value, that's a signal to think about whether the new event type
# belongs in an existing category or genuinely needs a new one.

VALID_CATEGORIES = {"commitment", "information", "competitive", "adverse"}

VALID_COUPLING_LAYERS = {
    "direct",         # Layer 1: investors observing each other's actions
    "informational",  # Layer 2: shared information substrate
    "both",           # event affects both layers
}

VALID_CONFIDENCE = {"verified", "needs_verify", "uncertain"}

VALID_JURISDICTIONS = {
    "NSW", "QLD", "VIC", "SA", "TAS",
    "FED", "AEMO", "AEMC",
    "FED/NSW/VIC", "FED/NSW/SA",  # multi-jurisdiction events
}

VALID_SCOPES = {"federal", "state", "rez", "corridor", "nem-wide"}


@dataclass(frozen=True)
class PolicyEvent:
    """A single policy event in the register."""
    event_id: str
    date: date
    jurisdiction: str
    event_type: str
    category: str
    coupling_layer: str
    information_unification: int  # 1-3 scale
    scope: str
    rez: Optional[str]
    description: str
    source_url: Optional[str]
    confidence: str
    notes: str
    date_is_partial: bool  # True if original CSV had XX in date


def _parse_partial_date(date_str: str) -> tuple[date, bool]:
    """
    Parse dates that may have XX placeholders for unknown month/day.

    Returns the parsed date and a flag indicating whether the original
    was partial. Partial dates are pinned to the 15th of the month, or
    1 July if month is also unknown, so they sort correctly but can be
    filtered out for precise analyses.
    """
    date_str = date_str.strip()
    is_partial = "XX" in date_str

    if is_partial:
        # Handle YYYY-XX-XX (year only) and YYYY-MM-XX (year and month)
        parts = date_str.split("-")
        year = int(parts[0])
        month = 7 if parts[1] == "XX" else int(parts[1])
        day = 15 if parts[2] == "XX" else int(parts[2])
        return date(year, month, day), True

    return datetime.strptime(date_str, "%Y-%m-%d").date(), False


def load_events(
    path: Path | str = "data/events/policy_events.csv",
    drop_partial_dates: bool = False,
    confidence_min: str = "needs_verify",
) -> pd.DataFrame:
    """
    Load the policy event register from CSV with validation.

    Parameters
    ----------
    path : Path or str
        Path to the event register CSV.
    drop_partial_dates : bool
        If True, drop events where the original date had XX placeholders.
        Use this for analyses where event timing precision matters.
    confidence_min : str
        Minimum confidence level to include. One of "verified", "needs_verify",
        "uncertain". Default "needs_verify" includes verified + needs_verify
        but drops "uncertain" events.

    Returns
    -------
    DataFrame with parsed dates, validated categorical columns, and a
    `date_is_partial` boolean column.

    Raises
    ------
    ValueError if any row has invalid values in controlled-vocabulary columns.
    """
    df = pd.read_csv(path, dtype=str).fillna("")

    # Parse dates, flagging partial ones
    parsed = df["date"].apply(_parse_partial_date)
    df["date"] = parsed.apply(lambda t: t[0])
    df["date_is_partial"] = parsed.apply(lambda t: t[1])

    # Integer column
    df["information_unification"] = df["information_unification"].astype(int)

    # Validate controlled vocabularies
    _validate_column(df, "category", VALID_CATEGORIES)
    _validate_column(df, "coupling_layer", VALID_COUPLING_LAYERS)
    _validate_column(df, "confidence", VALID_CONFIDENCE)
    _validate_column(df, "jurisdiction", VALID_JURISDICTIONS)
    _validate_column(df, "scope", VALID_SCOPES)

    # Information unification must be 1, 2, or 3
    if not df["information_unification"].isin({1, 2, 3}).all():
        bad = df[~df["information_unification"].isin({1, 2, 3})]
        raise ValueError(
            f"information_unification must be 1, 2, or 3. Bad rows:\n{bad}"
        )

    # Apply confidence filter
    confidence_order = ["verified", "needs_verify", "uncertain"]
    min_idx = confidence_order.index(confidence_min)
    allowed = set(confidence_order[: min_idx + 1])
    df = df[df["confidence"].isin(allowed)].copy()

    # Optionally drop partial dates
    if drop_partial_dates:
        df = df[~df["date_is_partial"]].copy()

    return df.sort_values("date").reset_index(drop=True)


def _validate_column(df: pd.DataFrame, col: str, valid: set) -> None:
    """Raise ValueError if column contains values outside the valid set."""
    bad = df[~df[col].isin(valid)]
    if len(bad) > 0:
        bad_values = bad[col].unique().tolist()
        raise ValueError(
            f"Column '{col}' contains invalid values: {bad_values}. "
            f"Valid values: {sorted(valid)}"
        )


# ----- Filter helpers ---------------------------------------------------------
#
# These exist to make notebook code readable. Filter by REZ, by category, by
# date window. They all return DataFrames so they chain naturally.


def events_in_window(
    events: pd.DataFrame,
    start: date | str,
    end: date | str,
) -> pd.DataFrame:
    """Events with date in [start, end] inclusive."""
    if isinstance(start, str):
        start = datetime.strptime(start, "%Y-%m-%d").date()
    if isinstance(end, str):
        end = datetime.strptime(end, "%Y-%m-%d").date()
    return events[(events["date"] >= start) & (events["date"] <= end)].copy()


def events_for_rez(
    events: pd.DataFrame,
    rez_code: str,
    include_nem_wide: bool = True,
) -> pd.DataFrame:
    """
    Events affecting a specific REZ.

    Includes events where rez == rez_code, plus state-wide and NEM-wide
    events if include_nem_wide=True (these affect all REZs in scope).
    """
    rez_specific = events["rez"] == rez_code
    if not include_nem_wide:
        return events[rez_specific].copy()
    nem_wide = events["scope"].isin({"federal", "state", "nem-wide"})
    return events[rez_specific | nem_wide].copy()


def events_of_category(
    events: pd.DataFrame,
    category: str,
) -> pd.DataFrame:
    """Events in a given pre-registered category."""
    if category not in VALID_CATEGORIES:
        raise ValueError(f"category must be one of {VALID_CATEGORIES}")
    return events[events["category"] == category].copy()


def events_of_coupling_layer(
    events: pd.DataFrame,
    coupling_layer: str,
) -> pd.DataFrame:
    """
    Events that affect a particular coupling layer.

    'direct' returns Layer 1 events only. 'informational' returns Layer 2 only.
    'both' returns events flagged as affecting both layers.

    To get all events that affect Layer 1 (including 'both' events), pass
    'direct_or_both' as a convenience.
    """
    if coupling_layer == "direct_or_both":
        return events[events["coupling_layer"].isin({"direct", "both"})].copy()
    if coupling_layer == "informational_or_both":
        return events[events["coupling_layer"].isin({"informational", "both"})].copy()
    if coupling_layer not in VALID_COUPLING_LAYERS:
        raise ValueError(
            f"coupling_layer must be one of {VALID_COUPLING_LAYERS} "
            f"or 'direct_or_both' / 'informational_or_both'"
        )
    return events[events["coupling_layer"] == coupling_layer].copy()


def register_summary(events: pd.DataFrame) -> pd.DataFrame:
    """
    Quick summary of the register: counts by category, jurisdiction,
    confidence. Useful for sanity-checking after edits.
    """
    summaries = []
    for col in ["category", "jurisdiction", "scope", "coupling_layer", "confidence"]:
        s = events[col].value_counts().rename("count")
        s.index.name = "value"
        s = s.reset_index()
        s.insert(0, "field", col)
        summaries.append(s)
    return pd.concat(summaries, ignore_index=True)


if __name__ == "__main__":
    # Quick smoke test when run as a script
    import sys

    csv_path = sys.argv[1] if len(sys.argv) > 1 else "data/events/policy_events.csv"
    events = load_events(csv_path)
    print(f"Loaded {len(events)} events from {csv_path}")
    print(f"Date range: {events['date'].min()} to {events['date'].max()}")
    print(f"\nPartial-date events: {events['date_is_partial'].sum()}")
    print(f"Verified events: {(events['confidence'] == 'verified').sum()}")
    print(f"\nSummary:")
    print(register_summary(events).to_string(index=False))
