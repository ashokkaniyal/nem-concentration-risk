#!/usr/bin/env python3
"""
Download missing AEMO Generation Information releases from the Wayback Machine.

WHY THIS EXISTS
---------------
AEMO publishes Generation Information files irregularly (not strict quarterly).
The current AEMO site only hosts the most recent ~7 releases reliably; older
files return 403 or 404. The Wayback Machine has captured most of them.

This script:
  1. Queries the Wayback CDX API for all snapshots of AEMO's Generation
     Information URL prefix
  2. Filters to .xlsx mimetype + status 200
  3. Deduplicates to one snapshot per (year, month) using the FIRST snapshot
     in that month (closest to AEMO's actual publication date)
  4. Downloads each via the `id_` direct-content URL (raw file, not wrapped HTML)
  5. Skips releases you already have locally
  6. Validates each download via xlsx magic bytes

USAGE
-----
    python download_aemo_geninfo_wayback.py [--out DIR] [--from YYYYMMDD]
                                            [--to YYYYMMDD] [--dry-run]

    Defaults:
      --out   ./data/projects/aemo_geninfo
      --from  20190101
      --to    today

DEPENDENCIES
------------
    pip install requests

NOTES
-----
- The Wayback CDX API is rate-limited; the script paces requests with a
  small delay between snapshot downloads.
- If the CDX API returns nothing, that probably means the URL prefix has
  changed on AEMO's side over the years; check the AEMO_URL_PREFIXES list
  below and try alternative prefixes.
- Some captured snapshots are HTML error pages cached by Wayback rather
  than the actual xlsx; the magic-bytes check filters these out.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

# Wayback CDX API endpoint
CDX_API = "https://web.archive.org/cdx/search/cdx"

# AEMO has used a few URL prefixes for Generation Information over the years.
# The CDX API matchType=prefix returns anything beginning with these.
AEMO_URL_PREFIXES = [
    "aemo.com.au/-/media/files/electricity/nem/planning_and_forecasting/generation_information/",
    "aemo.com.au/-/media/Files/Electricity/NEM/Planning_and_Forecasting/Generation_Information/",
    "www.aemo.com.au/-/media/files/electricity/nem/planning_and_forecasting/generation_information/",
]

# Pattern that should appear in any Gen Info xlsx URL
GENINFO_FILE_PATTERN = re.compile(
    r"(nem-)?generation[-_]information[-_]([a-z]+)[-_](\d{4})\.xlsx",
    re.IGNORECASE,
)

# .xlsx files start with PK\x03\x04 (they're zip archives)
XLSX_MAGIC = b"PK\x03\x04"

# Pace requests to be polite to Wayback infrastructure
REQUEST_DELAY_SECONDS = 1.5


def query_cdx_for_prefix(
    session: requests.Session,
    prefix: str,
    from_date: str,
    to_date: str,
) -> list[dict]:
    """Query CDX API for all snapshots matching a URL prefix.

    Returns parsed records as list of dicts with keys: timestamp, original, mimetype, statuscode.
    """
    params = {
        "url": prefix,
        "matchType": "prefix",
        "output": "json",
        "filter": ["statuscode:200"],
        "from": from_date,
        "to": to_date,
        "limit": 5000,
    }
    print(f"  Querying CDX for prefix: {prefix}")
    try:
        r = session.get(CDX_API, params=params, timeout=60)
    except requests.RequestException as e:
        print(f"    CDX request failed: {e}")
        return []
    if r.status_code != 200:
        print(f"    CDX returned status {r.status_code}: {r.text[:200]}")
        return []
    try:
        rows = r.json()
    except json.JSONDecodeError:
        print(f"    CDX response not JSON: {r.text[:200]}")
        return []
    if not rows or len(rows) < 2:
        print(f"    No CDX results for this prefix")
        return []
    # First row is the header
    header, *data = rows
    return [dict(zip(header, row)) for row in data]


def parse_year_month_from_url(url: str) -> tuple[int, int] | None:
    """Extract (year, month) from a Gen Info URL.

    AEMO files are named like:
      .../generation_information/2024/nem-generation-information-july-2024.xlsx
    """
    m = GENINFO_FILE_PATTERN.search(url)
    if not m:
        return None
    month_name = m.group(2).lower()
    year = int(m.group(3))
    months = {
        "january": 1, "february": 2, "march": 3, "april": 4,
        "may": 5, "june": 6, "july": 7, "august": 8,
        "september": 9, "october": 10, "november": 11, "december": 12,
    }
    if month_name not in months:
        return None
    return year, months[month_name]


def is_xlsx_content(data: bytes) -> bool:
    return len(data) >= 4 and data[:4] == XLSX_MAGIC


def wayback_direct_url(timestamp: str, original_url: str) -> str:
    """Build a Wayback URL that returns the raw original file (no HTML wrapper).

    The `id_` modifier on the timestamp tells Wayback to serve the captured
    file as-is, without rewriting links or adding navigation.
    """
    # Ensure original starts with scheme; CDX 'original' is usually full http(s) URL
    if not original_url.startswith(("http://", "https://")):
        original_url = "https://" + original_url
    return f"https://web.archive.org/web/{timestamp}id_/{original_url}"


def download_snapshot(
    session: requests.Session,
    timestamp: str,
    original_url: str,
    out_path: Path,
    min_size_bytes: int = 50_000,
    max_size_bytes: int = 10_000_000,
    timeout: int = 90,
) -> tuple[bool, str]:
    """Download one Wayback snapshot to out_path.

    Returns (success, message).
    """
    url = wayback_direct_url(timestamp, original_url)
    try:
        r = session.get(url, timeout=timeout)
    except requests.RequestException as e:
        return False, f"download failed: {e}"

    if r.status_code != 200:
        return False, f"HTTP {r.status_code}"

    body = r.content
    if not is_xlsx_content(body):
        return False, f"not xlsx (first 4 bytes: {body[:4].hex()})"
    if len(body) < min_size_bytes:
        return False, f"too small ({len(body):,} bytes)"
    if len(body) > max_size_bytes:
        return False, f"too large ({len(body):,} bytes - probably wrong file)"

    out_path.write_bytes(body)
    return True, f"saved {len(body):,} bytes"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Fetch missing AEMO Generation Information releases from Wayback Machine.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--out", type=Path,
        default=Path("./data/projects/aemo_geninfo"),
        help="Output directory (default: ./data/projects/aemo_geninfo)",
    )
    parser.add_argument(
        "--from", dest="from_date", default="20190101",
        help="Earliest snapshot date YYYYMMDD (default: 20190101)",
    )
    parser.add_argument(
        "--to", dest="to_date",
        default=datetime.now().strftime("%Y%m%d"),
        help="Latest snapshot date YYYYMMDD (default: today)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="List candidate snapshots without downloading",
    )
    parser.add_argument(
        "--force", action="store_true",
        help="Re-download even if file already exists locally",
    )
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {args.out.resolve()}\n")

    session = requests.Session()
    session.headers.update({
        "User-Agent": "nem-concentration-risk-research/0.1 (academic research; "
                      "contact: ashok.kaniyal@gmail.com)",
    })

    # Step 1: query CDX for all snapshots across all known URL prefixes
    print("Step 1: querying Wayback CDX API")
    all_records = []
    for prefix in AEMO_URL_PREFIXES:
        records = query_cdx_for_prefix(session, prefix, args.from_date, args.to_date)
        print(f"    -> {len(records)} records")
        all_records.extend(records)
        time.sleep(REQUEST_DELAY_SECONDS)

    if not all_records:
        print("\nNo records found across any prefix. Possible causes:")
        print("  - CDX API rate-limited (try again in a few minutes)")
        print("  - URL prefix has changed (inspect AEMO_URL_PREFIXES in this script)")
        print("  - Network/firewall issue")
        return 1

    print(f"\n  Total raw CDX records: {len(all_records)}")

    # Step 2: filter to xlsx files matching Gen Info filename pattern
    print("\nStep 2: filtering to Gen Info xlsx snapshots")
    candidates = []
    for rec in all_records:
        original = rec.get("original", "")
        if not original.lower().endswith(".xlsx"):
            continue
        ym = parse_year_month_from_url(original)
        if ym is None:
            continue
        year, month = ym
        timestamp = rec.get("timestamp", "")
        candidates.append({
            "year": year, "month": month,
            "timestamp": timestamp,
            "snapshot_date": (
                datetime.strptime(timestamp[:8], "%Y%m%d")
                if len(timestamp) >= 8 else None
            ),
            "original": original,
            "mimetype": rec.get("mimetype", ""),
            "digest": rec.get("digest", ""),
        })
    print(f"  Candidate xlsx Gen Info snapshots: {len(candidates)}")

    if not candidates:
        print("\nFound CDX records but none matched the Gen Info xlsx pattern.")
        print("Sample of what CDX returned (first 5):")
        for rec in all_records[:5]:
            print(f"  {rec.get('timestamp')}  {rec.get('original')}")
        return 1

    # Step 3: dedupe — keep the earliest snapshot per (year, month) of file
    # The earliest snapshot is closest to AEMO's actual publication date.
    print("\nStep 3: deduplicating to earliest snapshot per (year, month)")
    by_release = {}
    for c in candidates:
        key = (c["year"], c["month"])
        if key not in by_release:
            by_release[key] = c
        else:
            if c["timestamp"] < by_release[key]["timestamp"]:
                by_release[key] = c
    print(f"  Unique (year, month) releases: {len(by_release)}")

    # Step 4: download what we don't already have
    print("\nStep 4: downloading missing releases")
    print(f"{'Release':10}  {'Wayback date':12}  Status")
    print("-" * 80)

    successes = []
    failures = []
    skipped = []

    for (year, month), c in sorted(by_release.items()):
        release_id = f"{year}-{month:02d}"
        out_filename = f"nem-gen-info-{release_id}.xlsx"
        out_path = args.out / out_filename
        wb_date = c["snapshot_date"].strftime("%Y-%m-%d") if c["snapshot_date"] else "?"

        if out_path.exists() and not args.force:
            print(f"{release_id:10}  {wb_date:12}  already have ({out_path.stat().st_size:,} bytes)")
            skipped.append(release_id)
            continue

        if args.dry_run:
            print(f"{release_id:10}  {wb_date:12}  [dry-run] {c['original']}")
            continue

        ok, msg = download_snapshot(session, c["timestamp"], c["original"], out_path)
        print(f"{release_id:10}  {wb_date:12}  {msg}")
        if ok:
            successes.append(release_id)
        else:
            failures.append((release_id, msg))
        time.sleep(REQUEST_DELAY_SECONDS)

    # Summary
    print("\n" + "=" * 80)
    print(f"Summary:")
    print(f"  Already had:    {len(skipped)}")
    print(f"  Downloaded:     {len(successes)}")
    print(f"  Failed:         {len(failures)}")
    print("=" * 80)

    if failures:
        print("\nFailures (consider running again later — Wayback can be flaky):")
        for r, msg in failures:
            print(f"  {r}: {msg}")

    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
