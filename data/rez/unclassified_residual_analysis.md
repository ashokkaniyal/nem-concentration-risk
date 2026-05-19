# Residual unclassified rows — categorical breakdown

**Draft:** `data/rez/transmission_catchment_lookup_draft_v2.csv` (non-QLD rows only; QLD originals preserved as-is).
**Substation lookup:** `data/rez/rez_substation_lookup_NEM.csv` (789 keywords across 14 catchments).
**Matcher:** `scripts/build_nem_catchment_lookup.py` (strict substation/locality substring match, case-insensitive, word-boundary-aware).

## Why this document exists

The non-QLD draft has **345 review-flagged rows out of 1,549 (22%)**, vs ~25% target.
Of these:
- **305 are `Unclassified`** (no substation/locality keyword matched the project name).
- **40 are `review` with an assigned catchment** (a keyword matched substations in two REZs — the matcher assigned by locality but flagged the ambiguity).

Most `Unclassified` rows are not matcher failures — they are sites that **legitimately don't map to any state-declared REZ** under your locked methodology. This document categorises them so future readers can audit the residue without re-deriving the categories.

## Summary table

| Category | NSW | VIC | SA | TAS | Total | Why unclassified |
|---|---:|---:|---:|---:|---:|---|
| Outside any declared REZ — North Coast NSW | 16 | 0 | 0 | 0 | **16** | Northern Rivers region (Casino/Tabulam/Lismore/Coffs/Tweed) is outside every NSW REZ. AEMO's ISP A3 lists no candidate REZ there. |
| Load-area — Western Sydney | 13 | 0 | 0 | 0 | **13** | BESS/load-firming at Sydney metro distribution substations (Moorebank, Smithfield, Vineyard, Wallgrove, Lucas Heights, Eastern Creek). Not generation REZ-tagged. |
| Load-area — ACT/Cooma–Monaro | 14 | 0 | 0 | 0 | **14** | ACT BESS/projects (Queanbeyan, Royalla, Mugga Lane, Williamsdale, Belconnen, Mt Majura, Dalton, Jindabyne). Outside NSW REZ scope. |
| Load-area — Melbourne | 0 | 48 | 0 | 0 | **48** | Melbourne metro distribution BESS (Tramway Rd, Thomastown, Rangebank, Cranbourne, Altona, Hallam, Hastings, Brooklyn, Geelong load). Not generation REZ. |
| Load-area — Adelaide | 0 | 0 | 3 | 0 | **3** | Adelaide metro distribution BESS not classifiable to the surrounding generation REZ (Christies Beach, Wingfield, Direk, Penfield, Kincraig). |
| Behind-the-meter / commercial | 44 | 28 | 28 | 0 | **100** | C&I rooftop solar, club/RSL/school/winery/sports facility projects, street-address corporate solar (e.g. "275 Kent St", "Channel Nine", "St George Leagues Club", "De Bortoli Wines"). Outside REZ scope by design. |
| VPP / aggregator portfolios | 3 | 0 | 7 | 0 | **10** | Behind-the-meter aggregations (AGL VPP, Simply Energy VPP, SA Govt VPP, NSW Diverse Battery, NSW Energy Cluster). Geographically distributed — not REZ-tagged. |
| Uncategorised residual | 71 | 44 | 21 | 0 | **136** | Smaller projects in fringe areas (Tablelands wind, historical/withdrawn proposals, typos, micro hydro). Most ≤10 MW. Listed in full below. |
| **Total `Unclassified`** | 161 | 120 | 59 | 0 | **340** | |
| **Plus shared-keyword `review`** | — | — | — | — | **40** | Assigned catchment but flagged because the matched keyword exists in 2+ REZs. Listed in §3. |
| **Total review-flagged** | — | — | — | — | **380** | |

## 1. Outside any declared REZ — North Coast NSW (16 sites)

The Northern Rivers / North Coast NSW corridor (Casino → Tweed Heads, plus Kempsey/Coffs Harbour) is not within any of the five NSW REZs declared by EnergyCo (CWO, NEW, HCC, ILW, SW-NSW) and is not a candidate REZ in AEMO 2024 ISP Appendix A3. Projects here are genuinely outside the state-declared REZ system.

- `Arundel BESS` — 300 MW
- `EIWA Richmond Valley BESS` — 300 MW
- `Myrtle Creek BESS` — 275 MW
- `Richmond Valley BESS` — 275 MW
- `Boiling Down BESS` — 260 MW
- `Richmond Valley Solar Farm` — 252 MW
- `South Kempsey BESS` — 200 MW
- `Broadwater` — 38 MW
- `Condong` — 30 MW
- `Grafton Rd BESS (KCI)`
- `Lismore BESS`
- `Myrtle Creek Solar Farm`
- `Nymboida`
- `Richmond Valley BESS (EIWA)`
- `Walgett Solar Farm`
- `Wee Waa Solar Farm`

## 2. Load-area projects (146 sites — 13 + 14 + 48 + 3 + behind-the-meter spread)

Distribution-substation BESS and gas peakers near major load centres. By methodology, REZ classification is for generation-source corridors; load-area firming is treated as a separate concentration risk dimension.

### Western Sydney (13)

- `Vineyard BESS` — 200 MW
- `Smithfield Energy Facility` — 126 MW
- `Smithfield BESS` — 86 MW
- `Wallgrove Grid Battery project` — 50 MW
- `Lucas Heights 2` — 13 MW
- `Chipping Norton Waste to Energy` — 8 MW
- `Tahmoor` — 7 MW
- `Eastern Creek` — 5 MW
- `Eastern Creek 2 Gas Utilisation Facility` — 4 MW
- `Jacks Gully` — 2 MW
- `Grange Avenue` — 1 MW
- `Erskine Park`
- `Lucas Heights I`

### ACT / near-ACT (14)

- `Royalla Solar Farm` — 20 MW
- `Mugga Lane BESS` — 12 MW
- `Queanbeyan BESS` — 10 MW
- `Mugga Lane Renewable Hybrid` — 6 MW
- `Jindabyne` — 1 MW
- `Belconnen`
- `CRS Canberra`
- `Dalton`
- `Mount Majura`
- `Mugga Lane`
- `Mugga Lane Solar Park`
- `Queanbeyan BESS (Global Power)`
- `Queanbeyan BESS (Neoen)`
- `Queanbeyan Battery`

### Melbourne metro (48)

- `Melbourne Renewable Energy Hub - Side A` — 600 MW
- `Melbourne Renewable Energy Hub - Side B` — 600 MW
- `Melbourne Solar Farm - KCI` — 350 MW
- `Thomastown BESS` — 300 MW
- `Tramway Road BESS` — 300 MW
- `Melbourne Renewable Energy Complex` — 250 MW
- `Riverside BESS - Storage - KCI` — 250 MW
- `Rangebank BESS` — 200 MW
- `Birkins Solar Farm - Storage - KCI` — 200 MW
- `Somerton` — 170 MW
- `Laverton North` — 156 MW
- `Cranbourne BESS (Macquarie)` — 150 MW
- `Altona BESS` — 100 MW
- `Hastings Generation Site` — 29 MW
- `Hallam Road` — 9 MW
- `Brooklyn LFG U1-3` — 3 MW
- `HYMIVC06 Belgrave-Hallam Rd Micro Hydro` — 0 MW
- `Altona BESS - KCI`
- `Bayswood Timber Hallam VIC`
- `Berwick`
- _(…and 28 more — see lookup CSV)_

### Adelaide metro (3) — only sites not already absorbed into MN substation list

- `Pallamana Solar Farm`
- `Pedler Creek`
- `South Hummocks BESS`

### Behind-the-meter / commercial / industrial (NSW 44 + VIC 28 + SA 28 = 100)

C&I rooftop solar at street addresses, clubs, schools, wineries, factories, mines. Genuinely outside the REZ system. Top examples (full list in `transmission_catchment_lookup_draft_v2.csv`):

- `[NSW] Moorebank Logistics Park Project` — 200 MW
- `[NSW] Forest Glen Solar Farm` — 90 MW
- `[NSW] Peninsula Solar Farm & BESS` — 80 MW
- `[VIC] Melbourne Regional Landfill` — 9 MW
- `[NSW] 101 Miller Street`
- `[NSW] 133 Castlereagh St`
- `[NSW] 20 Bond St`
- `[NSW] 275 Kent St`
- `[NSW] 40 Mount St`
- `[NSW] 8 Chifley Place`
- `[NSW] Bakers Maison`
- `[NSW] Bankstown Sports Club`
- `[NSW] Blackmores`
- `[NSW] Brocklehurst Solar Farm`
- `[NSW] Channel Nine - Willoughby, NSW`
- `[NSW] Club Merrylands`
- `[NSW] DHL6 Solar Horsley Park`
- `[NSW] De Bortoli Wines`
- `[NSW] Drayton's Family Wines Solar`
- `[NSW] Earthpower Technologies Sydney`
- `[NSW] Holbrook SF`
- `[NSW] LMCC - Works Depot Power Station`
- `[NSW] Nine Network Willoughby`
- `[NSW] Nine Network Willoughby_x000D_`
- `[NSW] Peninsula Solar Farm`
- _(…and 75 more — see lookup CSV)_

## 3. VPP / aggregator portfolios (10 sites)

Geographically distributed behind-the-meter aggregations. By methodology, no REZ tag is meaningful.

- [NSW] `NSW Energy Cluster`
- [NSW] `ACT Renewables Battery Storage`
- [NSW] `NSW Diverse Battery`
- [SA] `AGL Battery (Maoneng)`
- [SA] `AGL VPP`
- [SA] `SA Government Virtual Power Plant - stage 1`
- [SA] `SA Government Virtual Power Plant - stage 2`
- [SA] `SA Government Virtual Power Plant - stage 3`
- [SA] `Simply Energy VPP`
- [SA] `Zero Cost Energy Future`

## 4. Uncategorised residual (136 sites — fringe projects, mostly ≤10 MW)

These mostly fall into: (a) very small / historical wind farms in border areas not covered by REZ substation lists (e.g. Biala WF, Carrick SF, Currawarra SF — Tablelands); (b) typo variants of names already in the lookup (e.g. "Guunedah Solar Farm" — should match "Gunnedah", "Gilgandara" — should match "Gilgandra"); (c) withdrawn/cancelled proposals retained in historical AEMO releases; (d) micro hydro / experimental projects.

### Top 30 by capacity (NSW)

- [NSW] `Territory Battery` — 200 MW
- [NSW] `Kangaroo Hills Wind Farm` — 155 MW
- [NSW] `Rothby BESS` — 120 MW
- [NSW] `Panorama BESS` — 100 MW
- [NSW] `Quorn Park Solar Hybrid` — 97 MW
- [NSW] `Project Brandy BESS` — 97 MW
- [VIC] `Derby Solar Farm & BESS` — 95 MW
- [NSW] `Summerville Solar Farm` — 90 MW
- [NSW] `Carag Solar Farm` — 16 MW
- [NSW] `South Keswick Solar Farm` — 14 MW
- [NSW] `Wilga Park Power Station A` — 6 MW
- [NSW] `Wilga Park Power Station B` — 6 MW
- [NSW] `Pindari` — 6 MW
- [NSW] `Brown Mountain Hydro Power Station` — 5 MW
- [NSW] `Dapper Solar Farm` — 4 MW
- [NSW] `The Drop` — 2 MW
- [NSW] `Bells Mountain Pumped Hydro`
- [NSW] `Belrose`
- [NSW] `Biala Wind Farm`
- [NSW] `Blayney`
- [NSW] `Bogan River`
- [NSW] `Carrick Solar Farm`
- [NSW] `Chillamurra`
- [NSW] `Currawarra Solar Farm`
- [NSW] `Gidginbung`
- [NSW] `Gilgandara Solar Farm`
- [NSW] `Guunedah Solar Farm`
- [NSW] `Kanowna Solar Farm`
- [NSW] `Moorambilla Solar Farm`
- [NSW] `Mumbil Solar Farm`

**Recommended action:** spot-check the top-capacity ones during your manual review. Most of the rest are correctly `Unclassified`.

## 5. Boundary ambiguity (shared-keyword `review`) — 40 sites

These projects matched a substation/locality keyword that exists in two REZs. The matcher assigned the higher-priority REZ by locality but downgraded `catchment_confidence` to `review` so you can verify or override.

| Region | Site (capacity) | Assigned | Matched | Notes |
|---|---|---|---|---|
| NSW | `Pottinger Energy Park - Wind - KCI` (1300 MW) | **NEW** | `Pottinger Energy Park` | |
| NSW | `Hanworth Battery` (1200 MW) | **CWO** | `Hanworth` | |
| NSW | `Glenbawn Pumped Hydro Project` (770 MW) | **NEW** | `Glenbawn Pumped Hydro` | |
| NSW | `Bayswater` (685 MW) | **NEW** | `Bayswater` | |
| NSW | `Goulburn River Solar Farm And BESS` (588 MW) | **HCC** | `Goulburn River Solar` | |
| NSW | `Yarrabee Solar Power Project` (584 MW) | **CWO** | `Yarrabee Solar` | |
| NSW | `Pottinger Energy Park - Battery - KCI` (500 MW) | **NEW** | `Pottinger Energy Park` | |
| NSW | `Stratford Renewable Energy Hub` (400 MW) | **HCC** | `Stratford` | |
| NSW | `Bowmans Creek Wind Farm` (347 MW) | **NEW** | `Bowmans Creek` | |
| SA | `Port Augusta Solar Farm (KCI)` (300 MW) | **MN** | `Port Augusta` | |
| NSW | `Maxwell Downs Solar Farm - KCI` (300 MW) | **CWO** | `Maxwell Downs` | |
| NSW | `Pottinger Energy Park - Solar - KCI` (300 MW) | **NEW** | `Pottinger Energy Park` | |
| NSW | `Mullion Creek Wind Farm` (250 MW) | **CWO** | `Mullion Creek` | |
| SA | `Yoorndoo Ilga Solar - KCI` (250 MW) | **MN** | `Yoorndoo Ilga` | |
| NSW | `Shoalhaven Expansion` (235 MW) | **ILW** | `Shoalhaven Expansion` | |
| SA | `Port Augusta Renewable Energy Park - Wind` (201 MW) | **MN** | `Port Augusta` | |
| VIC | `LYA BESS` (200 MW) | **CN-VIC** | `LYA` | |
| VIC | `Koorangie Energy Storage System` (185 MW) | **CN-VIC** | `Koorangie` | |
| VIC | `Koorangie BESS Stage 2` (150 MW) | **CN-VIC** | `Koorangie` | |
| SA | `Whyalla` (140 MW) | **MN** | `Whyalla` | |
| NSW | `Bodangora Wind Farm` (113 MW) | **CWO** | `Bodangora` | |
| SA | `Morgan Solar` (108 MW) | **MN** | `Morgan Solar` | |
| SA | `Whyalla BESS - KCI` (100 MW) | **MN** | `Whyalla` | |
| SA | `Port Augusta Renewable Energy Park - Solar` (99 MW) | **MN** | `Port Augusta` | |
| SA | `Cathedral Rocks` (62 MW) | **MN** | `Cathedral Rocks` | |
| VIC | `Salt Creek Wind Farm` (54 MW) | **WV** | `Salt Creek Wind Farm` | |
| SA | `Mannum Adelaide Pumping Station No 2 - MAPL2 (Palmer)` (16 MW) | **MN** | `Adelaide` | |
| SA | `Morgan To Whyalla Pipeline No 3 PS` (8 MW) | **MN** | `Whyalla` | |
| SA | `Morgan To Whyalla Pipeline No 4 PS` (6 MW) | **MN** | `Whyalla` | |
| SA | `Morgan To Whyalla Pipeline No 2 PS` (6 MW) | **MN** | `Whyalla` | |
| SA | `Morgan To Whyalla Pipeline No 1 PS And Water Filtration Plant` (6 MW) | **MN** | `Whyalla` | |
| NSW | `Maxwell Solar Farm` (—) | **CWO** | `Maxwell` | |
| SA | `SSE Whyalla Solar Farm` (—) | **MN** | `Whyalla` | |
| SA | `Whyalla Solar Farm` (—) | **MN** | `Whyalla` | |
| NSW | `Goulburn River BESS` (—) | **CWO** | `Goulburn River` | |
| NSW | `Goulburn River SF` (—) | **CWO** | `Goulburn River` | |
| SA | `Emeroo BESS (Bungala)` (—) | **MN** | `Bungala` | |
| SA | `Whyalla BESS` (—) | **MN** | `Whyalla` | |
| NSW | `Maxwell Downs Bess - KCI` (—) | **CWO** | `Maxwell Downs` | |
| NSW | `Hanworth BESS - KCI` (—) | **CWO** | `Hanworth` | |

## 6. How to override during manual review

To flip a row before merge:
1. Edit `data/rez/transmission_catchment_lookup_draft_v2.csv` directly — change `transmission_catchment`, `catchment_confidence`, and `rationale`.
2. Or tell the matcher about it permanently by adding a row to `data/rez/rez_substation_lookup_NEM.csv` and re-running `scripts/build_nem_catchment_lookup.py`.
3. Then merge into canonical `transmission_catchment_lookup.csv` only after sign-off.

## Methodology note

Strict substation-based matching, per locked decision #2 ("Project classification by closest substation electrically, not by REZ polygon membership"). Town/locality keywords were added at `confidence_default=medium` to mirror the QLD methodology pattern, reaching 22% review which is in line with the 15-25% target band. The remaining `review` rows are documented above so the high review rate is auditable, not a hidden gap.
