# Layer 3 Wave 1 — coordinate hand-compile report

**Scope:** Wave 1 = projects ≥500 MW (or ≥500 MWh BESS) from `layer3_scope.csv`, onshore only (offshore excluded). Coordinates appended to `project_coordinates.csv` (same schema as the Phase 1 spike). **Not committed** — for your review.

## Counts

| | n |
|---|---:|
| ≥500 MW total | 106 |
| Offshore excluded | 22 |
| **Wave 1 onshore** | **84** |
| Resolved (coord written) | **74** |
| Unresolved (flagged) | **10** |

Resolution rate: **74/84 = 88%**. All 74 coords validated inside their state bounding box.

## Per-source breakdown

| Source | n | Typical confidence |
|---|---:|---|
| wikipedia | 32 | {'medium': 25, 'high': 5, 'low': 2} |
| locality_proxy | 15 | {'low': 15} |
| proponent_site | 11 | {'medium': 8, 'low': 3} |
| osm_plant | 11 | {'medium': 11} |
| osm_substation | 5 | {'medium': 3, 'low': 1, 'high': 1} |

## Per-confidence breakdown

| Confidence | n | Meaning |
|---|---:|---|
| high | 6 | filed planning doc / authoritative station coord |
| medium | 47 | proponent or portal map, or host-station coord |
| low | 21 | locality proxy (named town/suburb centroid) |

## Per-state coverage (resolved)

| State | resolved | unresolved |
|---|---:|---:|
| NSW | 41 | 7 |
| VIC | 26 | 3 |
| SA | 6 | 0 |
| TAS | 1 | 0 |

## Per-status coverage (resolved)

| Status bucket | resolved |
|---|---:|
| Proposed | 69 |
| Existing less Announced Withdrawal | 2 |
| Committed | 2 |
| Withdrawn | 1 |

## Unresolved (10) — see `wave1_unresolved.csv`

| Region | Project | Reason |
|---|---|---|
| NSW | Nonowie Wind Farm | Project resolves to South Australia (~10km W of Whyalla) despite NSW1 region tag — region conflict; not placed in NSW box |
| NSW | Combined Cycle Gas | Generic placeholder name; no proponent/site identifier; no citable location |
| NSW | Mt View Wind Farm (KCI) | No citable NSW location found (Cessnock-area Mount View suspected but unconfirmed); KCI placeholder |
| NSW | Wandoona Solar Farm | No NSW project found; only Wandoan QLD matches (wrong state/name) |
| NSW | Deargee | Does not resolve to a verifiable NSW locality or documented project |
| NSW | Rosedale SF | Ambiguous "Rosedale" in NSW (multiple candidates); no unique 500MW project located |
| NSW | NSW Energy Cluster | Generic placeholder name; no proponent/site/coordinate |
| VIC | Seymour Wind Farm - KCI | Diffuse multi-parcel site NE of Seymour; no published centroid; township proxy would mislead |
| VIC | Coonawarren BESS - KCI | "Coonawarren" not a verifiable VIC locality; no project source found |
| VIC | Doreen BESS | Could not tie 800MW project to a Doreen-located source; locality proxy risks wrong placement |

## Data-quality flags for your review

1. **Armidale Pumped Hydro = Oven Mountain Pumped Storage coord** (both -30.809, 152.202). The agent treated them as the same Walcha-area PHES project. They are two distinct AEMO panel entries — confirm whether they are the same physical project or a genuine duplicate before the join.
2. **21 low-confidence locality proxies** (Kurri Kurri, Merriwa ×2, Marulan, Bannaby ×2, Maison Dieu, Bells Mountain, Great Western, NSW Gas Peaker, Aquila, Goorambat, Nowingi, Wollert ×2, Navarre, Malunga ×2, Kiewa Valley, Meering). These are town/suburb centroids — fine for coarse REZ assignment (REZs are large) but the nearest-substation distance band will read artificially long. Treat their spatial-join confidence as capped at "medium" downstream.
3. **Nonowie Wind Farm** is tagged NSW1 in AEMO but the agent located it in SA near Whyalla — a likely AEMO region mislabel or a name collision. Left unresolved rather than forced into NSW.
4. **GEM coordinate errors caught**: agents rejected erroneous Global Energy Monitor coords for Merriwa Energy Hub (placed near Cobar, ~400km off) and Navarre (placed near Bacchus Marsh), substituting verified township coords. Good catches — but signals GEM coords need spot-checking.
5. **Bells Mountain → Muswellbrook PHES upper reservoir** — the agent inferred Bells Mountain is the upper reservoir of the Muswellbrook pumped hydro scheme. Plausible but unverified; confidence low.

## Time spent (honest tally)

**~50 minutes wall-clock**, not the 5-8h manual estimate — by running the 84-project research as **4 parallel general-purpose subagents** (one per region batch). Cumulative agent runtime was ~54 min (A 10m, B 6m, C 33m, D 4m) but parallel, so ~33 min wall for research + ~15 min for my batch prep, coord validation, bbox check, and file assembly. The manual spike-style approach the brief budgeted for would indeed have taken multiple hours; parallelising the web research collapsed it. Trade-off: agent-sourced coords carry more variance than hand-verified ones — hence the data-quality flags above and the in-box validation gate.

## Not done (per brief)
- Spatial join NOT re-run (Wave 1 output is the coord file only).
- `draft_v3.csv` NOT written. `draft_v2.csv` / canonical untouched.
- Nothing committed — awaiting your review of the Wave 1 coord additions.