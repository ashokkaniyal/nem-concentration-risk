# v0.7 canonical lookup & join_catchment audit

Pre-Turn-2 audit of `transmission_catchment_lookup.csv` (v0.7, NEM-wide) and the
generalised `join_catchment` output. No fixes applied.

## 1. Catchment count discrepancy — RESOLVED (commit text undercounted)

The v0.7 commit message says "14 NSW/VIC/SA/TAS REZ catchments". The canonical
holds **15**. All 15 are legitimate Phase-2 catchments — none spurious.

| State | n | Catchments (row counts) |
|---|---:|---|
| NSW | 5 | SW-NSW (184), NEW (137), CWO (122), HCC (76), ILW (37) |
| VIC | 5 | CN-VIC (108), SW-VIC (89), WV (77), GIP (70), MR (42) |
| SA | **4** | MN (151), SE-SA (37), EYR (24), RIV (9) |
| TAS | 1 | TAS-NW (96) |
| **Non-QLD total** | **15** | |
| QLD | 8 | CQ (166), FNQ (73), SEQ (69), WD (53), WG (46), SD (33), DD (26), TG (11) |

Plus `Unclassified` (373) and `unresolved` (1, Quandong).

**The discrepancy is in SA: 4 catchments, not 3.** EYR (Eyre Peninsula) was added
mid-Phase-2 as the 4th SA catchment (your explicit request when ElectraNet's 10
candidate REZs showed Eyre Peninsula is electrically separate from Mid-North).
The "14" in the commit message simply predates/omits EYR in the headcount.
**EYR is legitimate (24 rows, all in SA1).** No spurious catchment exists.
→ Recommended action: correct the count in documentation to **15**; no data change.

## 2. Other data anomalies

- **Duplicate site_names: 1** — `Wantirna Mini Hydro` (2 rows, both `Unclassified`).
  Inherited from draft_v2 (present in both the QLD-canonical and non-QLD sections).
  Catchment-neutral (both Unclassified) but inflates joins (see §3).
- **Catchment typos / unknown values: 0.** Every catchment value is in the known
  universe (15 non-QLD + 8 QLD + Unclassified + unresolved).
- **Casing:** the unresolved row is stored lowercase `unresolved` (1 row). The
  schema doc / spec prose refers to "Unresolved" (capital) — cosmetic only; the
  data is lowercase. No "Unresolved" capitalised value exists.

## 3. Panel row-count reconciliation

Panel = **28,626 rows**, sums correctly across regions. All 5 regions span **22
releases**.

| Region | Panel rows | Unique projects | Unique releases |
|---|---:|---:|---:|
| NSW1 | 8,488 | 692 | 22 |
| QLD1 | 7,360 | 601 | 22 |
| VIC1 | 6,633 | 486 | 22 |
| SA1  | 4,462 | 276 | 22 |
| TAS1 | 1,683 | 96  | 22 |
| **Sum** | **28,626** | 2,151 | |

Volume ordering: **NSW > QLD > VIC > SA > TAS** — sensible (your expected
NSW>VIC>SA>TAS holds for the non-QLD set; QLD slots between NSW and VIC).

Note: QLD1 has **601 unique panel projects** but the canonical QLD section has
560 rows — so ~41 QLD panel projects (appearing in some releases, e.g. withdrawn
or renamed) have no lookup row and resolve to `Unclassified` on join. Expected,
not an anomaly (the QLD lookup was a snapshot; the panel is the full 22-release
union).

Join inflation: joined output = 28,644 (+18). **Single root cause: Wantirna Mini
Hydro.** It appears 18× in the panel (VIC1 ×10 + QLD1 ×8 — AEMO itself tags this
Melbourne project under QLD1 in some releases) and matches 2 lookup rows → +18.
Catchment-neutral (both Unclassified).

## 4. Cross-region catchment anomalies

After `join_catchment(panel, lookup)` with no region filter, exactly **1**
project resolves to a catchment outside its panel region's state:

| Project | Panel region | Catchment | Catchment state |
|---|---|---|---|
| Nonowie Wind Farm | NSW1 | MN | SA |

(7 joined rows = Nonowie across 7 release windows.) This is the documented region
data error (AEMO tags it NSW1; it is physically near Whyalla SA; the region-aware
spatial join assigned MN). **No other cross-region cases.** Per-region catchment
states: NSW1 → {NSW, SA(Nonowie)}; VIC1 → {VIC}; SA1 → {SA}; TAS1 → {TAS};
QLD1 → {QLD}. All clean except the one known Nonowie case.

## 5. Duplicate summary (for the fix decision)

Only **one** duplicate across the whole canonical: `Wantirna Mini Hydro` (2 rows,
both `Unclassified`, one in the QLD section + one in the non-QLD section). No
other duplicates found in §2. A 1-line dedupe (drop the spurious QLD row, since
Wantirna is a VIC suburb) removes the +18 join inflation.

## Decisions needed

| # | Finding | Recommended action |
|---|---|---|
| 1 | Commit message says "14" catchments; actual is **15** (EYR is the 4th SA catchment, legitimate) | **Fix in documentation** — note 15 in future text; no data change. EYR accepted as legitimate. |
| 2 | `Wantirna Mini Hydro` duplicated (2 rows, both Unclassified; QLD + non-QLD sections) | **Fix in canonical** — drop the spurious QLD-section row (Wantirna is VIC). 1-line dedupe; removes +18 join inflation. Bundled for your approval. |
| 3 | `unresolved` stored lowercase vs "Unresolved" in prose | **Accept as documented edge case** — or normalise casing if you prefer "Unresolved" for display. Cosmetic; no functional impact. |
| 4 | Nonowie: NSW1 panel → MN (SA) catchment | **Accept as documented edge case** — region data error already flagged in wave2_concerns.md and the merge (nonowie_manual rule). A `regions=["NSW1"]` NSW analysis will contain this 1 MN project. |
| 5 | ~41 QLD panel projects not in the 560-row QLD lookup → Unclassified on join | **Accept** — expected (lookup snapshot vs 22-release panel union); not an anomaly. |
| 6 | Join inflation +18 from Wantirna | **Resolved by Decision 2** — dedupe fixes it. |

No other anomalies. Canonical is sound apart from the single Wantirna duplicate
(Decision 2) and the documentation count (Decision 1).
