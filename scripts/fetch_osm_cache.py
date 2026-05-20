"""Fetch OSM power=substation and power=plant features per NEM state into
data/rez/osm_cache/ as JSON. Robust to hung mirrors via 120s urllib timeout
and rotation across three Overpass endpoints.

Usage:
    python scripts/fetch_osm_cache.py                 # all 5 states, both kinds
    python scripts/fetch_osm_cache.py --states NSW    # subset
    python scripts/fetch_osm_cache.py --kinds plant   # only plants
    python scripts/fetch_osm_cache.py --force         # re-fetch even if cached

The harvester (harvest_osm_coords.py) reads cache only and does not fetch.
"""
from __future__ import annotations
import argparse, json, os, socket, sys, time
import urllib.request, urllib.parse, urllib.error
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT_DIR = REPO / "data" / "rez" / "osm_cache"

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120.0 Safari/537.36 "
    "nem-concentration-risk-research/0.2 (academic; contact via repo)"
)

MIRRORS = [
    "https://overpass.private.coffee/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass-api.de/api/interpreter",
]

# bbox: (south, west, north, east)
BBOXES = {
    "NSW": (-37.6, 140.8, -28.1, 153.7),
    "VIC": (-39.2, 140.8, -33.9, 150.1),
    "SA":  (-38.2, 128.8, -25.9, 141.1),
    "TAS": (-43.7, 144.5, -39.5, 148.5),
    "QLD": (-29.2, 138.0, -10.5, 153.6),
}


def build_query(kind: str, bbox: tuple[float, float, float, float]) -> str:
    s, w, n, e = bbox
    if kind == "substation":
        return (
            f'[out:json][timeout:180];'
            f'(node["power"="substation"]["name"]({s},{w},{n},{e});'
            f'way["power"="substation"]["name"]({s},{w},{n},{e}););'
            f'out center;'
        )
    if kind == "plant":
        return (
            f'[out:json][timeout:180];'
            f'(node["power"="plant"]["name"]({s},{w},{n},{e});'
            f'way["power"="plant"]["name"]({s},{w},{n},{e});'
            f'relation["power"="plant"]["name"]({s},{w},{n},{e}););'
            f'out center;'
        )
    raise ValueError(f"unknown kind: {kind}")


def fetch_one(state: str, kind: str, *, force: bool = False, timeout: int = 120) -> tuple[bool, str]:
    """Fetch one (state, kind) bundle. Returns (success, message)."""
    fn = OUT_DIR / f"{state}_{kind}.json"
    if fn.exists() and fn.stat().st_size > 500 and not force:
        try:
            n = len(json.load(open(fn)).get("elements", []))
            return True, f"cached: {fn.name} ({fn.stat().st_size:,} bytes, {n} elements)"
        except Exception:
            print(f"  {fn.name}: cached file corrupt, will re-fetch", file=sys.stderr)
            fn.unlink()
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    query = build_query(kind, BBOXES[state])
    data = urllib.parse.urlencode({"data": query}).encode()
    for mirror_idx, m in enumerate(MIRRORS):
        host = m.split("//")[1].split("/")[0]
        print(f"  {state}/{kind}: fetching from {host} (try {mirror_idx+1}/{len(MIRRORS)}, timeout={timeout}s)...",
              file=sys.stderr, flush=True)
        req = urllib.request.Request(m, data=data,
                                     headers={"User-Agent": UA, "Accept": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                code = r.status
                body = r.read()
        except socket.timeout as ex:
            print(f"    {host}: TIMEOUT after {timeout}s — rotating", file=sys.stderr, flush=True)
            time.sleep(5)
            continue
        except urllib.error.HTTPError as ex:
            print(f"    {host}: HTTP {ex.code} — rotating", file=sys.stderr, flush=True)
            time.sleep(5)
            continue
        except urllib.error.URLError as ex:
            print(f"    {host}: URLError {ex.reason} — rotating", file=sys.stderr, flush=True)
            time.sleep(5)
            continue
        except Exception as ex:
            print(f"    {host}: {type(ex).__name__}: {ex} — rotating", file=sys.stderr, flush=True)
            time.sleep(5)
            continue
        try:
            parsed = json.loads(body)
        except Exception as ex:
            print(f"    {host}: returned non-JSON — rotating", file=sys.stderr, flush=True)
            continue
        n_els = len(parsed.get("elements", []))
        # Write atomically
        tmp = fn.with_suffix(fn.suffix + ".tmp")
        tmp.write_bytes(body)
        tmp.replace(fn)
        msg = f"got {code}, N={n_els} elements, {len(body)/1024:.1f} KB"
        print(f"    {host}: {msg}", file=sys.stderr, flush=True)
        return True, msg
    return False, f"ALL {len(MIRRORS)} mirrors failed after rotation"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--states", nargs="+", default=list(BBOXES.keys()),
                    choices=list(BBOXES.keys()))
    ap.add_argument("--kinds", nargs="+", default=["substation", "plant"],
                    choices=["substation", "plant"])
    ap.add_argument("--timeout", type=int, default=120, help="per-request seconds")
    ap.add_argument("--force", action="store_true", help="re-fetch even if cached")
    args = ap.parse_args()
    summary = []
    for state in args.states:
        print(f"--- {state} ---", file=sys.stderr, flush=True)
        for kind in args.kinds:
            ok, msg = fetch_one(state, kind, force=args.force, timeout=args.timeout)
            summary.append((state, kind, ok, msg))
            time.sleep(3)  # be polite between requests
    print("\n=== Summary ===", file=sys.stderr)
    for state, kind, ok, msg in summary:
        marker = "✓" if ok else "✗"
        print(f"  {marker} {state}/{kind}: {msg}", file=sys.stderr)
    n_ok = sum(1 for *_, ok, _ in summary if ok)
    print(f"\n{n_ok}/{len(summary)} successful", file=sys.stderr)
    sys.exit(0 if n_ok == len(summary) else 1)


if __name__ == "__main__":
    main()
