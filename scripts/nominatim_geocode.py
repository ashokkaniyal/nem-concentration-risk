"""Layer 2 test-sample geocoder via OSM Nominatim.

Throttled to 1 req/sec, caches every response to data/rez/nominatim_cache.json
keyed by query string (never re-queries). Three query forms with fallback;
acceptance classification per the Phase 2 spec.

Usage:
    python scripts/nominatim_geocode.py --in /tmp/nominatim_sample.csv \
        --out data/rez/nominatim_sample_results.csv
"""
from __future__ import annotations
import argparse, json, time, sys
import urllib.request, urllib.parse, urllib.error
from pathlib import Path
import pandas as pd

REPO = Path(__file__).resolve().parents[1]
CACHE = REPO / "data" / "rez" / "nominatim_cache.json"
UA = "nem-concentration-risk/0.1 (ashok.kaniyal@gmail.com)"
ENDPOINT = "https://nominatim.openstreetmap.org/search"

STATE_NAME = {"NSW1": "New South Wales", "VIC1": "Victoria",
              "SA1": "South Australia", "TAS1": "Tasmania"}
STATE_BBOX = {  # south, west, north, east
    "NSW1": (-37.6, 140.8, -28.1, 153.7),
    "VIC1": (-39.2, 140.8, -33.9, 150.1),
    "SA1":  (-38.2, 128.8, -25.9, 141.1),
    "TAS1": (-43.7, 144.5, -39.5, 148.5),
}
STATE_CENTRE = {"NSW1": (-32.8, 147.2), "VIC1": (-36.8, 144.5),
                "SA1": (-32.7, 135.5), "TAS1": (-41.8, 146.5)}

ACCEPT_TYPES = {"administrative", "industrial", "power_station", "power_plant",
                "substation", "power", "plant"}
TOWN_TYPES = {"town", "village", "hamlet", "locality", "suburb", "city"}

SUFFIXES = [" wind farm", " solar farm", " bess", " battery", " project",
            " stage 2", " stage 1", " - kci", " power station", " energy hub",
            " solar", " wind", " pumped hydro", " energy storage system"]


def load_cache() -> dict:
    if CACHE.exists():
        try:
            return json.load(open(CACHE))
        except Exception:
            return {}
    return {}


def save_cache(cache: dict):
    CACHE.write_text(json.dumps(cache, indent=2))


def strip_suffix(name: str) -> str:
    n = name.lower()
    for s in SUFFIXES:
        n = n.replace(s, "")
    return n.strip()


def haversine_km(a, b):
    import math
    R = 6371.0
    lat1, lon1 = a; lat2, lon2 = b
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1); dl = math.radians(lon2 - lon1)
    h = math.sin(dp/2)**2 + math.cos(p1)*math.cos(p2)*math.sin(dl/2)**2
    return 2*R*math.asin(math.sqrt(h))


def query_nominatim(q: str, cache: dict) -> list:
    if q in cache:
        return cache[q]
    params = urllib.parse.urlencode({"q": q, "format": "jsonv2", "limit": 3,
                                     "addressdetails": 1, "extratags": 1})
    url = f"{ENDPOINT}?{params}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read())
    except Exception as e:
        print(f"    query error for {q!r}: {e}", file=sys.stderr)
        data = []
    cache[q] = data
    save_cache(cache)
    time.sleep(1.1)  # politeness: <1 req/sec
    return data


def classify(result: dict, region: str) -> tuple[str, dict]:
    """Return (classification, info)."""
    try:
        lat = float(result["lat"]); lon = float(result["lon"])
    except (KeyError, ValueError):
        return "unresolved", {}
    s, w, n, e = STATE_BBOX[region]
    in_bbox = (s <= lat <= n) and (w <= lon <= e)
    typ = result.get("type", "")
    cls = result.get("class", "")
    cat = result.get("category", cls)
    dist_centre = haversine_km((lat, lon), STATE_CENTRE[region])
    info = {"lat": lat, "lon": lon, "type": typ, "class": cls, "category": cat,
            "display_name": result.get("display_name", ""), "dist_centre_km": round(dist_centre, 1)}
    if not in_bbox:
        return "wrong_state", info
    if typ in ACCEPT_TYPES or cls in ("power", "industrial") or cat in ("power", "industrial"):
        return "acceptable", info
    if typ in TOWN_TYPES:
        return "ambiguous_town", info
    if typ == "natural" or cls == "natural":
        return "unresolved", info
    if dist_centre > 600:  # >200km from centre is normal for large states; use 600 as outlier guard
        return "unresolved", info
    # administrative boundary or other -> treat admin as acceptable, else ambiguous
    if typ == "administrative" or cls == "boundary":
        return "acceptable", info
    return "ambiguous_town", info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="infile", required=True, type=Path)
    ap.add_argument("--out", required=True, type=Path)
    args = ap.parse_args()
    cache = load_cache()
    sample = pd.read_csv(args.infile)
    rows = []
    for i, p in sample.iterrows():
        region = p.region
        sname = STATE_NAME[region]
        forms = [
            f"{p.site_name}, {sname}, Australia",
            f"{p.site_name}, Australia",
            f"{strip_suffix(p.site_name)}, {sname}, Australia",
        ]
        result_row = {"region": region, "site_name": p.site_name,
                      "status_bucket": p.get("status_bucket", ""), "stratum": p.get("stratum", ""),
                      "classification": "unresolved", "query_used": "", "lat": None, "lon": None,
                      "osm_type": "", "osm_class": "", "display_name": "", "dist_centre_km": None}
        print(f"  [{i+1}/{len(sample)}] {p.site_name} ({region})", file=sys.stderr)
        for qi, q in enumerate(forms):
            data = query_nominatim(q, cache)
            if not data:
                continue
            cls, info = classify(data[0], region)
            if cls == "wrong_state" and qi < len(forms) - 1:
                continue  # try next form
            result_row.update({"classification": cls, "query_used": q,
                               "lat": info.get("lat"), "lon": info.get("lon"),
                               "osm_type": info.get("type", ""), "osm_class": info.get("class", ""),
                               "display_name": info.get("display_name", ""),
                               "dist_centre_km": info.get("dist_centre_km")})
            if cls in ("acceptable", "ambiguous_town"):
                break
        rows.append(result_row)
    out = pd.DataFrame(rows)
    out.to_csv(args.out, index=False)
    print(f"\nWrote {args.out} ({len(out)} rows)", file=sys.stderr)
    # Summary
    print("\n=== Classification counts ===", file=sys.stderr)
    print(out.classification.value_counts().to_string(), file=sys.stderr)


if __name__ == "__main__":
    main()
