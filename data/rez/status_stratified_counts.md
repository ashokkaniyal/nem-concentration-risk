# Status-stratified concentration — Phase 1 counts (cluster level)

*Phase 1 of the status-stratified within-window concentration analysis. **Counts only — no
test has been run.** Reports event counts, distributions, and cluster×quarter matrices for
the three lifecycle statuses, then a per-status power verdict. Built 2026-05-22. Awaiting
review before Phase 2.*

## Method recap (settled design)

- **Panel / censoring:** same as notebook 07 — phantom-cleaned panel (`phantom_risk < 2`),
  21 post-censoring release windows (2020-11 … 2025-07; the 2020-02 cohort is left-censored).
- **Events (first-appearance, ≤ 1 per project per status, after the censoring boundary):**
  - **Committed** = first release at `Committed`.
  - **Existing** = first release at `Existing less Announced Withdrawal`.
  - **Withdrawn** = first release at `Withdrawn` *or* `Announced Withdrawal`, whichever is earlier.
  - (Status read verbatim from the AEMO `Status Bucket Summary` column; whitespace-normalised,
    which folds in the 1 stray `" Existing less Announced Withdrawal"` row.)
- **Resolution:** the 5 multi-catchment clusters (Central-Northern NSW [3 catchments], Southern
  QLD [5], Eastern SA [2], Western Victoria [2], Northern Victoria [2]). Singletons excluded
  from the cluster test; reported descriptively here.
- **c2 baseline (for Phase 2; shown here as context):** expected cluster share =
  (n catchments in cluster) / 14. → CN-NSW 0.214, S-QLD 0.357, E-SA/W-VIC/N-VIC 0.143 each.
  Flat-across-catchments; no project counts, no capacity → no circularity, no stage mismatch.
- **`phantom_risk` note:** the `<2` filter removes **zero** events from all three series
  (phantom-flagged projects never reach Committed/Existing/Withdrawn) — counts are identical
  with or without it. So the filter does not thin the Withdrawn (failure) series.

---

## Committed

- **Total post-censoring first-appearance events: 133.** In the 5 clusters: **75**.
  Singletons/Unclassified: 58.

| Cluster | observed | obs share | c2 share |
|---|---:|---:|---:|
| Central-Northern NSW | 21 | 0.28 | 0.214 |
| Eastern SA | 19 | 0.25 | 0.143 |
| Southern QLD | 14 | 0.19 | 0.357 |
| Western Victoria | 13 | 0.17 | 0.143 |
| Northern Victoria | 8 | 0.11 | 0.143 |

- **Singletons carrying events (excluded from test):** SW-NSW 24, CQ 7, GIP 6, SEQ 5, SE-SA 5,
  FNQ 3, ILW 2. **Unclassified:** 6. *(SW-NSW alone carries 24 — more than any cluster's
  in-test total except CN-NSW; the cluster test discards it as a singleton.)*
- **Quarters populated (clustered events):** 17 of 21.
- **Cluster×quarter matrix:** 105 cells — **57 zero (54%)**, **97 < 3 (92%)**. Per-window
  clustered n hits ≥3 in ~12 windows (peaks: 24-04 = 12, 20-11 = 9, 21-07 = 8, 23-07 = 8).

**Verdict: INFERENTIAL (moderate power).** ~12 windows clear the n≥3 per-window threshold the
test needs (cf. 18 in notebook 07's §2). The within-window multinomial test conditions on each
window's total, so the 92%-of-cells-<3 sparsity is expected and not disqualifying; power is
moderate, not strong. Caveat: only 75/133 events (56%) are in-cluster.

---

## Existing

- **Total post-censoring first-appearance events: 166.** In the 5 clusters: **77**.
  Singletons/Unclassified: 89.

| Cluster | observed | obs share | c2 share |
|---|---:|---:|---:|
| Eastern SA | 18 | 0.23 | 0.143 |
| Western Victoria | 18 | 0.23 | 0.143 |
| Central-Northern NSW | 14 | 0.18 | 0.214 |
| Southern QLD | 14 | 0.18 | 0.357 |
| Northern Victoria | 13 | 0.17 | 0.143 |

- **Singletons:** SW-NSW 26, SE-SA 8, SEQ 8, CQ 7, TAS-NW 7, FNQ 6, ILW 3, GIP 3, EYR 3.
  **Unclassified:** 18. *(54% of Existing events fall outside the 5 clusters; SW-NSW again largest.)*
- **Quarters populated:** 15 of 21.
- **Cluster×quarter matrix:** 105 cells — **58 zero (55%)**, **97 < 3 (92%)**. ~13 windows
  clear n≥3 (peak 24-04 = 10).

**Verdict: INFERENTIAL (moderate power) — with a definitional caveat.** Raw power is comparable
to Committed (~13 testable windows). **But the back-loading concern is *not* what limits it,
and for an unexpected reason:** Existing first-appearances are *not* back-loaded (early windows
carry 7 each in 20-11/21-01/21-05). That is because "first appearance at Existing" captures both
(a) genuine within-window Committed→Existing energisations *and* (b) projects first listed in the
panel already operational (no observed Committed phase). Early-window Existing events are mostly
(b). **Flag for Phase 2:** if the Existing series is meant to represent *energisation*, consider
restricting it to projects with a prior observed `Committed` status; as currently defined it
conflates energisation with mid-panel listing of existing plant. The concentration test itself is
still runnable, but the interpretation must reflect this.

---

## Withdrawn

- **Total post-censoring first-appearance events: 21.** In the 5 clusters: **7**.
  Singletons/Unclassified: 14.

| Cluster | observed | c2 share |
|---|---:|---:|
| Central-Northern NSW | 2 | 0.214 |
| Eastern SA | 2 | 0.143 |
| Southern QLD | 1 | 0.357 |
| Western Victoria | 1 | 0.143 |
| Northern Victoria | 1 | 0.143 |

- **Singletons:** CQ 3, SEQ 1, EYR 1, SE-SA 1, GIP 1. **Unclassified:** 7.
- **Quarters populated:** 7 of 21 — and **each populated window has exactly 1 clustered event.**
- **Cluster×quarter matrix:** 105 cells — **98 zero (93%)**, **105 < 3 (100%)** — every cell is
  0 or 1; the maximum cell count is 1.

**Verdict: DESCRIPTIVE-ONLY (underpowered — cannot run the test).** Only 7 clustered events, and
**no window reaches the n≥3 per-window threshold** (every populated window has n=1), so the
within-window test would have *zero* testable windows. Even pooled, 7 events across 5 clusters
and 7 quarters cannot support an inferential concentration test. Report descriptively in Phase 2;
do not test. *(This matches the design's stated worry that withdrawals within 2020–2025 would be
too few.)*

---

## Cross-cutting observations

1. **A large share of events fall in singletons, which the cluster test discards:** Committed
   56% in-cluster (44% discarded), Existing 46% in-cluster (54% discarded), Withdrawn 33%
   in-cluster. **SW-NSW** — a strong herding catchment in notebook 07 — is a singleton and
   carries the most events of any single unit (Committed 24, Existing 26), yet is excluded from
   the cluster test. The cluster-resolution test therefore speaks to a minority of events.
2. **Unclassified events** (panel projects with no lookup row; the snapshot-vs-union issue):
   Committed 6, Existing 18, Withdrawn 7 — also excluded.
3. **c2 vs observed, descriptively (not a test):** Eastern SA looks over-represented for both
   Committed (0.25 vs 0.14) and Existing (0.23 vs 0.14); Southern QLD looks under-represented
   (0.18–0.19 vs 0.36). Whether these are significant against the multinomial null is the Phase 2
   question — not assessed here.

## Summary of verdicts

| Status | Total events | In-cluster | Testable windows (n≥3) | Verdict |
|---|---:|---:|---:|---|
| Committed | 133 | 75 | ~12 | **Inferential** (moderate power) |
| Existing | 166 | 77 | ~13 | **Inferential** (moderate; definitional caveat — energisation vs mid-panel listing) |
| Withdrawn | 21 | 7 | 0 | **Descriptive-only** (underpowered) |

**Stopping here per the two-phase plan.** No test run, no notebook 08, nothing committed.
Phase 2 (Committed + Existing inferential tests with the c2 baseline and a permutation check;
Withdrawn descriptive) only after your review of these counts — and a decision on the Existing
definitional caveat.

---

# Phase 1 addendum (2026-05-22) — leak-fixed Existing + coverage quantification

## 1. Corrected Existing (genuine Committed→Existing energisation)

**Corrected definition:** first appearance at `Existing less Announced Withdrawal`, **restricted
to projects with a prior observed `Committed` release** (`committed_first < existing_first`),
post-censoring. Projects appearing already-Existing with no observed Committed phase are dropped.

- **Total: 107** (was 166 leaky — **59 catalogue-listings removed**). In the 5 clusters: **59**
  (was 77).

| Cluster | corrected obs | obs share | c2 share |
|---|---:|---:|---:|
| Eastern SA | 15 | 0.25 | 0.143 |
| Western Victoria | 14 | 0.24 | 0.143 |
| Central-Northern NSW | 11 | 0.19 | 0.214 |
| Northern Victoria | 11 | 0.19 | 0.143 |
| Southern QLD | 8 | 0.14 | 0.357 |

- **Singletons:** SW-NSW 22, CQ 5, SE-SA 5, FNQ 4, SEQ 3, ILW 2, TAS-NW 2, GIP 1, EYR 1.
  **Unclassified:** 3.
- **Quarters populated (clustered):** 15 of 21. Per-quarter clustered counts: 20-11:6, 21-01:6,
  21-05:2, 21-07:3, 22-01:2, 22-05:5, 22-10:4, 23-01:4, 23-05:6, 23-07:1, 24-04:8, 24-10:5,
  25-01:2, 25-04:4, 25-07:1.
- **Testable windows (clustered n≥3): 10** (was ~13 leaky).

**Back-loading: NO — and that is expected, not a problem.** The corrected series is *not*
strongly back-loaded; early windows remain populated (20-11:6, 21-01:6). These are **genuine
energisations** — projects already `Committed` at or before the 2020-02 boundary that reached
`Existing` in 2020–2022 (the commitment is observed in-panel, even if at the censored boundary;
the *transition* occurs within the window). A substantial committed pipeline existed at panel
start and matured across the whole period, so energisations are spread, not late-clustered. The
leak fix removed the 59 already-operational catalogue-listings without gutting the early windows.

**Re-assessment: INFERENTIAL but borderline.** 59 in-cluster events across 10 testable windows
(vs Committed's 75 / 12, and notebook 07 §2's 18). Clean now (genuine transitions), but power is
the weakest of the inferential candidates — flag for Phase 2 that the corrected-Existing result
will be the most fragile and most permutation-sensitive.

## 2. Coverage quantification

| | Committed | Corrected Existing |
|---|---|---|
| total events | 133 | 107 |
| **in 5 clusters** | 75 (**56%**) | 59 (**55%**) |
| in singletons | 52 (39%) | 45 (42%) |
| Unclassified | 6 (5%) | 3 (3%) |

The cluster test sees ~55% of events for both statuses; ~40% sit in singletons (excluded).

**Per-singleton counts and catchment-level (n≥10) viability:**

| Singleton | Committed n | Corrected-Existing n | Clears n≥10? |
|---|---:|---:|---|
| **SW-NSW** | **24** | **22** | **Yes — both statuses** |
| CQ | 7 | 5 | Committed borderline (7), Existing no |
| GIP | 6 | 1 | No |
| SE-SA | 5 | 5 | No |
| SEQ | 5 | 3 | No |
| FNQ | 3 | 4 | No |
| ILW | 2 | 2 | No |
| TAS-NW | 0 | 2 | No |
| EYR | 0 | 1 | No |

**Decision input for A / B / C:**
- **Only SW-NSW** clears an n≥10 catchment-level threshold (Committed 24, Existing 22). CQ is
  borderline for Committed only (7). Every other singleton is too sparse for an inferential
  catchment-level test under either status.
- So **option (B)** (catchment-level for high-n singletons) effectively rescues **one unit —
  SW-NSW** (optionally CQ-Committed as a borderline second). It does **not** broadly recover the
  discarded ~40%; the other 7–8 singletons stay descriptive regardless.
- The choice is therefore essentially: **(C)** 5-cluster test + all singletons descriptive
  (~55% coverage), versus **(C)+SW-NSW** — i.e. the 5 clusters *plus* SW-NSW as a single
  catchment-level inferential addendum (the one materially herding singleton from notebook 07).
  **(A)** (re-clustering singletons) remains the corridor-logic-corrupting option you flagged.

**Stopping here. No test, no notebook 08, nothing committed. Awaiting your A/B/C decision and
confirmation to scope Phase 2.**
