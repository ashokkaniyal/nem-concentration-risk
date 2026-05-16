#!/usr/bin/env python3
"""
Download historical AEMO NEM Generation Information releases.

The Generation Information page is updated quarterly (March, July, September,
November per the Generation Information Guidelines). This script pulls the
historical Excel releases into a local directory for analysis.

USAGE
-----
    python download_aemo_geninfo.py [--out DIR] [--start-year YEAR] [--end-year YEAR]

    Defaults:
      --out         ./data/projects/aemo_geninfo
      --start-year  2019
      --end-year    current year

NOTES
-----
The file naming convention on AEMO's CMS has varied slightly over years.
This script tries multiple naming patterns per (year, month) combination
and records which patterns succeeded.

If a release is missing from the current AEMO site, it may still be
available via the Wayback Machine. The script reports missing releases
at the end so you can hunt them down manually.

Run periodically to refresh (the script skips files already downloaded).

REQUIREMENTS
-----
    pip install requests

No other dependencies - deliberately uses only the standard library plus requests.
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterator

import requests

# AEMO publishes quarterly: March, July, September, November
QUARTERLY_MONTHS = [3, 7, 9, 11]

# Month name conventions used in AEMO URLs over the years
MONTH_NAMES = {
    1: "january", 2: "february", 3: "march", 4: "april",
    5: "may", 6: "june", 7: "july", 8: "august",
    9: "september", 10: "october", 11: "november", 12: "december",
}

# AEMO has used a few different URL patterns over the years.
# Each pattern is a template; we try them in order until one succeeds.
URL_PATTERNS = [
    # Standard 2020-present pattern (lowercase, hyphenated)
    "https://aemo.com.au/-/media/files/electricity/nem/planning_and_forecasting/generation_information/{year}/nem-generation-information-{month_name}-{year}.xlsx",
    # With trailing query string (newer pages append ?la=en)
    "https://aemo.com.au/-/media/files/electricity/nem/planning_and_forecasting/generation_information/{year}/nem-generation-information-{month_name}-{year}.xlsx?la=en",
    # Variant without 'nem-' prefix (some older releases)
    "https://aemo.com.au/-/media/files/electricity/nem/planning_and_forecasting/generation_information/{year}/generation-information-{month_name}-{year}.xlsx",
    # Capitalised path variant (very old releases pre-CMS migration)
    "https://aemo.com.au/-/media/Files/Electricity/NEM/Planning_and_Forecasting/Generation_Information/{year}/NEM-Generation-Information-{month_name_cap}-{year}.xlsx",
]

# Minimum size to consider a download valid (smaller = probably an error page)
MIN_FILE_SIZE_BYTES = 10_000


def candidate_urls(year: int, month: int) -> Iterator[str]:
    """Yield candidate URLs to try for a given (year, month) release."""
    month_name = MONTH_NAMES[month]
    month_name_cap = month_name.capitalize()
    for pattern in URL_PATTERNS:
        yield pattern.format(
            year=year,
            month_name=month_name,
            month_name_cap=month_name_cap,
        )


def is_xlsx_content(data: bytes) -> bool:
    """
    Check whether bytes look like an xlsx file.

    .xlsx files are zip archives, so they start with PK\\x03\\x04.
    AEMO sometimes returns HTML error pages with status 200, so we
    can't trust status alone.
    """
    return len(data) >= 4 and data[:2] == b"PK"


def download_release(
    year: int,
    month: int,
    out_dir: Path,
    session: requests.Session,
    timeout: int = 60,
) -> tuple[bool, str]:
    """
    Attempt to download the AEMO Generation Information release for (year, month).

    Returns (success, message) where message describes what happened.
    """
    out_filename = f"nem-gen-info-{year}-{month:02d}.xlsx"
    out_path = out_dir / out_filename

    if out_path.exists():
        size = out_path.stat().st_size
        return True, f"already have {out_filename} ({size:,} bytes)"

    last_status = None
    for url in candidate_urls(year, month):
        try:
            response = session.get(url, timeout=timeout)
        except requests.RequestException:
            continue

        last_status = response.status_code
        if response.status_code != 200:
            continue

        body = response.content
        if not is_xlsx_content(body):
            # AEMO returns HTML 200 for missing files sometimes
            continue
        if len(body) < MIN_FILE_SIZE_BYTES:
            # Suspiciously small - probably truncated or error
            continue

        # Looks like a real xlsx file - save it
        out_path.write_bytes(body)
        return True, f"downloaded {out_filename} ({len(body):,} bytes)"

    status_info = f" (last HTTP status: {last_status})" if last_status else ""
    return False, f"no working URL found for {year}-{month:02d}{status_info}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Download historical AEMO Generation Information releases.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("./data/projects/aemo_geninfo"),
        help="Output directory (default: ./data/projects/aemo_geninfo)",
    )
    parser.add_argument(
        "--start-year",
        type=int,
        default=2019,
        help="First year to attempt (default: 2019)",
    )
    parser.add_argument(
        "--end-year",
        type=int,
        default=datetime.now().year,
        help="Last year to attempt (default: current year)",
    )
    parser.add_argument(
        "--user-agent",
        default="nem-concentration-risk-research/0.1 (academic research)",
        help="User-Agent string for HTTP requests",
    )
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {args.out.resolve()}")
    print()

    session = requests.Session()
    session.headers.update({"User-Agent": args.user_agent})

    successes = []
    failures = []

    for year in range(args.start_year, args.end_year + 1):
        for month in QUARTERLY_MONTHS:
            # Skip future releases
            release_date = datetime(year, month, 1)
            if release_date > datetime.now():
                continue

            print(f"  {year}-{month:02d}  ", end="", flush=True)
            ok, msg = download_release(year, month, args.out, session)
            print(msg)
            if ok:
                successes.append((year, month, msg))
            else:
                failures.append((year, month, msg))

    print()
    print("=" * 70)
    print(f"Summary: {len(successes)} downloaded/cached, {len(failures)} missing")
    print("=" * 70)

    if failures:
        print()
        print("Missing releases (try Wayback Machine):")
        for year, month, _ in failures:
            print(f"  {year}-{month:02d}")
        print()
        print("Wayback Machine search:")
        print("  https://web.archive.org/web/*/aemo.com.au/*generation-information*")
        print()
        print("Tip: search for the specific filename pattern, e.g.")
        print("  https://web.archive.org/web/*/*nem-generation-information-july-2021*")

    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
