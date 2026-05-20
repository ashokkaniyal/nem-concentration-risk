# v0.7.1 cleanup — audit trail

Companion to `v07_audit_report.md`. Four changes applied after the v0.7 audit.

## 1. Wantirna Mini Hydro dedup (audit findings #2 / #6)

**What:** dropped the spurious QLD-section row for "Wantirna Mini Hydro" from
`transmission_catchment_lookup.csv`; kept the VIC-section row.
**Why:** Wantirna is a Melbourne (VIC) project. It appeared twice in the
canonical — once inherited from the original QLD-canonical section (with QLD
metadata: `owner_tier=tier_3`, `phantom_risk=0`) and once from the non-QLD
section. Both were `Unclassified`, but the duplicate caused +18 join-row
inflation (18 panel rows × 2 lookup matches). The QLD-section row was the
mis-tag; the AEMO panel itself wrongly carries Wantirna under `QLD1` in some
releases.
**Test:** canonical row count 2110 → 2109; `site_name=="Wantirna Mini Hydro"`
now returns exactly 1 row (the VIC/non-QLD one). Re-running
`join_catchment(panel, lookup)` gives joined rows = panel rows = **28,626**
(inflation 0, was +18).

## 2. catchment_confidence casing normalise (audit finding #3)

**What:** standardised `catchment_confidence` to lowercase
(`high`/`medium`/`review`/`unresolved`).
**Why:** consistency for downstream exact-match filters; the schema/prose
referred to "Unresolved" while data stored "unresolved".
**Test:** the column was already consistently lowercase in the v0.7 canonical
(value set `{high, medium, review, unresolved}` before and after); the
`.str.lower()` pass is idempotent and confirms no stray `High`/`Medium`/`Review`
variants exist. The `n/a` value is added only at join time by `join_catchment`
for "Other NEM region" overwrites, not stored in the canonical.

## 3. Schema doc updates (audit findings #1 / #4 / #5)

**What:** in `catchment_lookup_schema.md` — added a "Catchment universe" section
(15 non-QLD + 8 QLD = 23 REZ catchments + Unclassified + unresolved), listing all
15 non-QLD by state and noting EYR was added mid-Phase-2 (ElectraNet topology
shows Eyre is electrically separate from MN); added a casing-convention note;
added a "Known data anomalies" section (Nonowie NSW1→MN, snapshot-vs-union
asymmetry, Wantirna resolution, casing); refreshed the downstream-code section to
reflect the now-generalised `join_catchment`.
**Why:** the v0.7 commit message undercounted catchments as "14" (omitted EYR);
the audit edge cases (Nonowie, snapshot asymmetry) needed a permanent home.
**Test:** doc now states 23 REZ catchments and lists EYR under SA (4 SA
catchments).

## 4. This document

`v07_cleanup.md` records the cleanup for the audit trail, alongside
`v07_audit_report.md` (the findings) and `catchment_lookup_schema.md` (the
canonical reference).

## Accepted as documented edge cases (no change)

- **Nonowie NSW1→MN** (audit #4): AEMO panel region error; region-aware spatial
  join assigns MN correctly. Documented in schema doc + wave2_concerns.md.
- **~41 QLD panel projects → Unclassified** (audit #5): lookup snapshot vs
  22-release panel union; expected asymmetry.
