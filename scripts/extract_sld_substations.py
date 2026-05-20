"""Extract the substation universe from the AEMO Main System Diagram PDF.

The SLD is a vector schematic. Text extraction recovers substation NAMES (CAPS
labels) and bracketed CODES (QLD/VIC use (T##)/(H##)/etc.; NSW/SA/TAS codes are
rendered graphically and do NOT survive text extraction). Connectivity is drawn
as graphical line segments and is NOT recoverable from the text layer — the
connected_substations column is left blank here and is populated only for the
boundary-case pages we read visually (see sld_topology_adjudication.md).

Output: data/rez/sld_substations.csv
  schema: state, sld_page, substation_name, substation_code, voltage_levels,
          connected_substations, generators_attached, notes
"""
from __future__ import annotations
import re
from pathlib import Path
import pandas as pd
from pypdf import PdfReader

REPO = Path(__file__).resolve().parents[1]
SLD = REPO / "data" / "rez" / "sources" / "aemo_sld_2022.pdf"
OUT = REPO / "data" / "rez" / "sld_substations.csv"

# Noise tokens to drop — boilerplate, legend, symbols, generic words
NOISE = {
    "AUSTRALIAN ENERGY MARKET OPERATOR", "HIGH VOLTAGE NETWORK", "MAIN SYSTEM DIAGRAM",
    "NEW SOUTH WALES", "SOUTH AUSTRALIA", "QUEENSLAND", "VICTORIA", "TASMANIA",
    "DATE", "AEMO", "GENMAIN", "MAIN", "MAI N", "GENERATOR", "WIND FARM", "SOLAR FARM",
    "ENERGY STORAGE SYSTEM", "STATIC VAR COMPENSATOR", "SYNCHRONOUS CONDENSOR",
    "CIRCUIT BREAKER", "ISOLATOR", "CAPACITOR BANK", "REACTOR", "SERIES REACTOR",
    "AUTO TRANSFORMER", "SVC", "SVCSVC", "S/C", "S/CS/C", "PS", "BESS",
    "WEST", "EAST", "NORTH", "SOUTH", "POINT", "LAKE", "VALLEY", "TOWN", "LANE",
    "MILL", "HILL", "PARK", "CREEK", "B A A B", "A B", "B A", "SC", "TIE1", "TIE2",
    "COPYRIGHT", "ALL RIGHTS RESERVED",
}
NOISE_PREFIXES = ("OR", "TIE", "WB", "GR", "GT", "B1", "A1")
# Bracketed code: QLD T-numbers, VIC codes, also (H##)(S##)(MOPS)(HYTS) styles
CODE_RE = re.compile(r"\(([A-Z]{1,4}\d{1,3}[A-Z]?|[A-Z]{2,6})\)")
VOLT_RE = re.compile(r"\b(500|330|275|220|132|110|66|33|22)\s*kV", re.IGNORECASE)


def page_label(text: str, page_idx: int) -> tuple[str, str]:
    m = re.search(r"MAIN SYSTEM DIAGRAM\s*\n?\s*([A-Z ]+) - ([a-z])", text)
    if m:
        region = m.group(1).strip()
        sub = m.group(2)
        state_map = {"QUEENSLAND": "QLD", "NEW SOUTH WALES": "NSW",
                     "VICTORIA": "VIC", "SOUTH AUSTRALIA": "SA", "TASMANIA": "TAS"}
        return state_map.get(region, region), f"{state_map.get(region, region)}-{sub}"
    return "?", f"p{page_idx+1}"


def clean_name(tok: str) -> str | None:
    tok = re.sub(r"\s+", " ", tok).strip()
    # strip trailing standalone voltages / digits
    tok = re.sub(r"\s+\d{2,4}$", "", tok).strip()
    if tok in NOISE:
        return None
    if len(tok) < 3:
        return None
    if any(tok.startswith(p) and tok[len(p):].isdigit() for p in NOISE_PREFIXES):
        return None
    # mostly-digit tokens are circuit ids
    letters = sum(c.isalpha() for c in tok)
    if letters < 3:
        return None
    return tok


def main():
    r = PdfReader(str(SLD))
    rows = []
    for i, pg in enumerate(r.pages):
        text = pg.extract_text() or ""
        state, label = page_label(text, i)
        # Bracketed codes on this page (name→code association is unreliable from
        # flat text, so we store the page's code set separately and best-effort
        # attach by adjacency in the raw string)
        codes_on_page = CODE_RE.findall(text)
        volts = sorted(set(VOLT_RE.findall(text)), key=lambda v: -int(v))
        # CAPS name candidates
        caps = re.findall(r"\b[A-Z][A-Z0-9&/ ]{2,}[A-Z0-9]\b", text)
        seen = []
        for c in caps:
            name = clean_name(c)
            if name and name not in seen:
                seen.append(name)
        # Try to attach a bracket code that immediately follows a name in raw text
        for name in seen:
            # look for "NAME (CODE)" or "NAME\n(CODE)"
            mcode = re.search(re.escape(name) + r"\s*\n?\s*\(([A-Z]{1,4}\d{0,3}[A-Z]?)\)", text)
            code = mcode.group(1) if mcode else ""
            rows.append({
                "state": state,
                "sld_page": label,
                "substation_name": name,
                "substation_code": code,
                "voltage_levels": ";".join(f"{v}kV" for v in volts),  # page-level voltage set
                "connected_substations": "",  # graphical — not extractable from text
                "generators_attached": "",     # graphical — not reliably extractable
                "notes": "voltage_levels is page-level set, not per-substation; connectivity not extracted from text layer",
            })
    df = pd.DataFrame(rows).drop_duplicates(["state", "substation_name"]).reset_index(drop=True)
    df.to_csv(OUT, index=False)
    print(f"Wrote {OUT.relative_to(REPO)}: {len(df)} unique (state, substation_name) rows")
    print("\nPer-state counts:")
    print(df.groupby("state").size().to_string())
    print(f"\nWith bracket code: {(df.substation_code != '').sum()}")


if __name__ == "__main__":
    main()
