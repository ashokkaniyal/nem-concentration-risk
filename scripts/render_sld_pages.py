"""Render AEMO SLD PDF pages to PNG for visual topology reading.

The SLD (data/rez/sources/aemo_sld_2022.pdf, content dated 2019-04-04) is a
vector schematic. Connectivity is graphical and not recoverable from the text
layer, so boundary-case REZ adjudication requires reading the rendered pages.

Uses pymupdf (pip, no system poppler needed). Output PNGs are gitignored
(derived artifacts) — regenerate on demand.

Usage:
    python scripts/render_sld_pages.py                 # render the boundary-case pages
    python scripts/render_sld_pages.py --all           # render all 40 pages
    python scripts/render_sld_pages.py --pages 24 22   # render specific 1-based pages
"""
from __future__ import annotations
import argparse
from pathlib import Path
import fitz  # pymupdf

REPO = Path(__file__).resolve().parents[1]
SLD = REPO / "data" / "rez" / "sources" / "aemo_sld_2022.pdf"
OUT = REPO / "data" / "rez" / "sld_pages"

# 1-based page -> friendly name. These are the boundary-case pages from
# sld_topology_adjudication.md.
BOUNDARY_PAGES = {
    24: "NSW-j_bayswater",
    22: "NSW-h_wollar",
    16: "NSW-b_hunter",
    11: "QLD-k_bullicreek",
    26: "VIC-a_mortlake",
    35: "SA-d_robertstown",
    31: "VIC-f_loyyang",
    27: "VIC-b_kerang",
}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--all", action="store_true", help="render all pages")
    ap.add_argument("--pages", nargs="+", type=int, help="specific 1-based page numbers")
    ap.add_argument("--zoom", type=float, default=3.0, help="render zoom factor")
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(str(SLD))
    if args.all:
        targets = {i + 1: f"page_{i+1:02d}" for i in range(len(doc))}
    elif args.pages:
        targets = {p: f"page_{p:02d}" for p in args.pages}
    else:
        targets = BOUNDARY_PAGES
    mat = fitz.Matrix(args.zoom, args.zoom)
    for pg1, name in targets.items():
        pix = doc[pg1 - 1].get_pixmap(matrix=mat)
        path = OUT / f"{name}.png"
        pix.save(str(path))
        print(f"  page {pg1} -> {path.relative_to(REPO)} ({pix.width}x{pix.height})")
    print(f"Rendered {len(targets)} pages to {OUT.relative_to(REPO)}")


if __name__ == "__main__":
    main()
