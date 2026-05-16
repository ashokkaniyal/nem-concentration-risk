"""
Information environment: Layer C in the three-layer taxonomy.

Where Layers A (policy events) and B (corporate events) are discrete
shocks at specific dates, Layer C captures the continuous(-ish) texture
of the information substrate that couples investors together.

In Kuramoto terms, Layer C corresponds to the time-varying coupling
strength K(t) - the density of information flowing between investors
at a given point in time. High K(t) means everyone is reading the same
ISP, attending the same conferences, hearing the same broker views.
Low K(t) means the substrate is fragmented and investors are weakly
coupled to each other's information.

Practical measurement: we proxy K(t) by counting outputs in each REZ-
relevant information channel per month or quarter. Trade press article
counts, conference session counts, AEMO publication frequency. Each
channel is a partial proxy; the composite is the Layer C intensity.

Honest caveat: this layer is the hardest to measure rigorously from
free sources. The proxies are noisy and the historical reconstruction
involves judgement calls. Treat Layer C results as suggestive rather
than definitive in v1.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

import pandas as pd

VALID_OUTLETS = {
    "RenewEconomy",
    "EcoGeneration",
    "Energy Magazine",
    "PV Magazine Australia",
    "One Step Off the Grid",
    "AFR",
    "AEMO Publications",
    "AEMC Determinations",
}

VALID_REZS = {
    "CWO", "NER", "SWN", "HCC", "ILW",
    "QLD_NORTH", "QLD_CENTRAL", "QLD_SOUTH",
}


def load_trade_press_counts(
    path: Path | str = "data/info_environment/trade_press_quarterly.csv",
) -> pd.DataFrame:
    """
    Load monthly/quarterly trade press article counts by outlet and REZ.

    Each row is one outlet's article count for one REZ for one
    year-month. Empty article_count means not yet collected.

    Returns DataFrame with parsed period (start of month) and dropped
    rows where article_count is blank.
    """
    df = pd.read_csv(path, dtype=str).fillna("")
    df["article_count"] = pd.to_numeric(df["article_count"], errors="coerce")
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["month"] = pd.to_numeric(df["month"], errors="coerce").astype("Int64")
    df = df.dropna(subset=["year", "month"])
    df["period"] = pd.to_datetime(
        df["year"].astype(str) + "-" + df["month"].astype(str).str.zfill(2) + "-01"
    )
    return df


def load_conferences(
    path: Path | str = "data/info_environment/conferences.csv",
) -> pd.DataFrame:
    """
    Load conference programme session counts by year, conference, and REZ.

    Each row is one conference's REZ-tagged session count for one year.
    """
    df = pd.read_csv(path, dtype=str).fillna("")
    df["session_count"] = pd.to_numeric(df["session_count"], errors="coerce")
    df["total_energy_sessions"] = pd.to_numeric(
        df["total_energy_sessions"], errors="coerce"
    )
    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    return df


def info_intensity_by_rez(
    trade_press: pd.DataFrame,
    rez: str,
    aggregation: Literal["monthly", "quarterly", "yearly"] = "quarterly",
) -> pd.Series:
    """
    Compute time series of information intensity for a single REZ,
    summed across all outlets.

    This is the simplest Layer C measure: how much was each REZ being
    talked about, period by period?

    For sophisticated analysis, you'd want to weight outlets by audience
    or differentiate Layer 1 (trade press read by developers) from
    Layer 2 (AFR read by capital). For v1, an unweighted sum is fine.
    """
    if rez not in VALID_REZS:
        raise ValueError(f"rez must be one of {sorted(VALID_REZS)}")

    rez_data = trade_press[trade_press["rez"] == rez].copy()
    rez_data = rez_data.dropna(subset=["article_count"])

    if len(rez_data) == 0:
        return pd.Series(dtype=float)

    rez_data = rez_data.set_index("period")

    # Sum across outlets within each period
    period_totals = rez_data.groupby("period")["article_count"].sum()

    if aggregation == "monthly":
        return period_totals
    elif aggregation == "quarterly":
        return period_totals.resample("Q").sum()
    elif aggregation == "yearly":
        return period_totals.resample("Y").sum()
    else:
        raise ValueError("aggregation must be monthly, quarterly, or yearly")


def info_intensity_comparison(
    trade_press: pd.DataFrame,
    rezs: list[str] | None = None,
    aggregation: Literal["monthly", "quarterly", "yearly"] = "quarterly",
) -> pd.DataFrame:
    """
    Compute information intensity time series for multiple REZs side by side.
    Useful for visualising how attention shifts between REZs over time.
    """
    if rezs is None:
        rezs = sorted(VALID_REZS)

    series_dict = {}
    for rez in rezs:
        s = info_intensity_by_rez(trade_press, rez, aggregation)
        if len(s) > 0:
            series_dict[rez] = s

    if not series_dict:
        return pd.DataFrame()

    return pd.DataFrame(series_dict).fillna(0)


if __name__ == "__main__":
    import sys
    path = sys.argv[1] if len(sys.argv) > 1 else "data/info_environment/trade_press_quarterly.csv"
    tp = load_trade_press_counts(path)
    print(f"Loaded {len(tp)} trade press rows")
    if "article_count" in tp.columns:
        populated = tp["article_count"].notna().sum()
        print(f"  Of which populated with counts: {populated}")
    print(f"\nFirst few rows:")
    print(tp.head().to_string(index=False))
