# Layer 3 manual hand-compile — scope report

**Source:** the 1,273 non-QLD Layer-1 (OSM `power=plant`) misses in `project_coordinates.csv`. **Selection:** nameplate ≥ 100 MW, or storage ≥ 100 MWh for BESS-only projects with no nameplate MW.

**This is a scope report only — no hand-compiling has been done.** It exists so you can pick a threshold before committing the manual effort.

## Headline

- **540 projects** qualify (≥100 MW / ≥100 MWh) out of the 1,273 Layer-1 misses.
- **506 are Proposed** (priority 1) — the speculative end where the herding signal lives.
- Region split: NSW 242, VIC 184, SA 91, TAS 23.
- **18 are offshore wind** projects — large (1.5-3.1 GW) but their "location" is a marine zone; geocode to the declared offshore-wind-zone centroid or onshore connection point, not a substation. Flag separately.

## Breakdown by status bucket (priority order)

| Priority | Status bucket | Count |
|---:|---|---:|
| 1 | Proposed | 506 — _Proposed (506)_ |
| 2 | Anticipated | 11 — _Anticipated (11)_ |
| 3 | Committed | 13 — _Committed (13)_ |
| 4 | Existing/Operational | 7 — _Existing less Announced Withdrawal (7)_ |
| 5 | Announced/Withdrawn/Other | 3 — _Withdrawn (2), Announced Withdrawal (1)_ |

## Threshold cuts & effort estimate

Assuming **3-5 min/project** (search project EIS → NSW DPIE Major Projects / VIC Engage / SA PlanSA → AREMI/NationalMap → Wikipedia → OSM).

| Threshold | Projects | Effort @3min | Effort @5min |
|---|---:|---:|---:|
| ≥100 MW/MWh | 540 | 27.0 h | 45.0 h |
| ≥200 MW/MWh | 378 | 18.9 h | 31.5 h |
| ≥500 MW/MWh | 106 | 5.3 h | 8.8 h |

- **≥100 MW (540 projects):** ~27-45 hours — multi-day, best done in waves.
- **≥200 MW (378 projects):** ~19-32 hours — ~2-4 focused days.
- **≥500 MW (106 projects):** ~5-9 hours — ~1 day; captures the GW-scale pipeline.

## Hard-to-geocode names

**152/540 (28%)** carry KCI suffixes, proponent/trust legal names, "Stage N", or bracketed qualifiers (e.g. "- KCI", "Pty Ltd as trustee for...", "(Submitted via...)"). These need the project EIS or planning-portal record to locate — the name alone won't geocode. Budget toward the 5-min end for these.

## Top 20 by capacity

| Capacity | Status | Region | Project |
|---:|---|---|---|
| 3100 | Proposed | VIC | Acacia Offshore Wind Farm - KCI |
| 2700 | Proposed | VIC | Gippsland C - Wind - KCI |
| 2700 | Proposed | VIC | Gippsland A&B - Wind - KCI |
| 2508 | Proposed | VIC | Great Eastern Offshore Wind - KCI |
| 2000 | Proposed | NSW | Eden Offshore Wind Farm |
| 2000 | Proposed | NSW | Illawarra Offshore Wind Farm |
| 2000 | Proposed | NSW | Novocastrian Offshore Wind Farm |
| 2000 | Proposed | NSW | Ulladulla Offshore Wind Farm |
| 2000 | Proposed | VIC | Star of The South |
| 1995 | Proposed | VIC | Cape Winds Offshore Wind Farm |
| 1819 | Proposed | VIC | Blue Mackerel North Off Shore Wind Farm |
| 1800 | Proposed | SA | Cultana Pumped Hydro Energy Storage |
| 1600 | Proposed | NSW | Wollongong Offshore Wind |
| 1500 | Proposed | VIC | Meering Wind Farm |
| 1500 | Proposed | VIC | Seadragon offshore wind project |
| 1500 | Proposed | VIC | Seadragon project |
| 1500 | Proposed | VIC | Greater Southern Offshore Wind - KCI |
| 1500 | Proposed | VIC | Gippsland offshore wind farm |
| 1500 | Proposed | VIC | Greater Southern Offshore Wind |
| 1400 | Proposed | NSW | Eraring Big Battery – Stage 3 |

## Observations for threshold choice

1. **Offshore wind dominates the top end** (18 projects, mostly 1.5-3.1 GW, all Proposed). These are cheap to locate (declared offshore zones: Gippsland, Illawarra, Hunter, Southern Ocean) but resolve to marine zones — handle as a batch with zone-centroid coords, not substation snapping.
2. **506 of 540 are Proposed** — exactly the speculative pipeline the herding framework targets. A capacity threshold barely changes the status mix; it only changes volume.
3. **≥500 MW (106 projects, ~1 day)** is the highest-leverage first wave: GW-scale projects, minus the offshore batch (~25), leaves ~80 onshore projects to hand-compile.
4. **≥200 MW (378 projects)** roughly doubles coverage of committed capacity for ~3x the effort.
5. Recommend **wave structure**: Wave 1 = ≥500 MW onshore (~80, ~5h) + offshore batch (~25, fast). Re-run spatial join, assess coverage lift, then decide on Wave 2 (200-500 MW band).

## Files
- `data/rez/layer3_scope.csv` — all 540 qualifying projects, sorted by priority then capacity.
- `data/rez/layer3_scope_summary.md` — this report.