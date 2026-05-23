# Test 5 — Prerequisites checklist

*Companion document to `preregistration.md` Test 5 (synchronisation onset precedes
constraint emergence; Claim 4 / Option C). Lists the data and code artifacts that
must exist before the Test 5 pipeline is run. Each item is a tracked deliverable;
Test 5 is gated on all six being present and committed.*

Status legend: **[ ]** not started, **[~]** in progress, **[x]** complete.

---

## 1. Transmission-element-to-catchment lookup **[ ]**

**Deliverable.** A new hand-curated CSV at `data/rez/constraint_element_catchment_lookup.csv`.

**Schema.**

| column | type | notes |
|---|---|---|
| `constraint_element` | string | AEMO transmission element identifier (line, transformer, bus). Matches the LHS variable string in AEMO constraint equations. |
| `transmission_catchment` | string | One of the eight QLD catchment codes (`WD`, `SD`, `DD`, `TG`, `WG`, `FNQ`, `CQ`, `SEQ`) or a comma-separated list if multi-catchment. |
| `affects_generation` | bool | Whether binding of this element materially restricts generation in the listed catchment(s), as opposed to passively involving the element in an equation. |
| `confidence` | enum | `high` / `medium` / `review` — same convention as `transmission_catchment_lookup.csv`. |
| `notes` | string | Free-text: rationale, network diagram reference, ambiguity flags. |

**Source materials.** AEMO constraint equation metadata (extractable from
`nem-constraints`), AEMO network diagrams for QLD, the existing
`data/rez/transmission_catchment_lookup.csv` for site-to-catchment alignment.

**Open questions to resolve during construction.**

- How to handle elements that affect multiple catchments (e.g., the southern
  QLD backbone). Current proposal: list all affected catchments; Test 5
  pipeline counts the binding event against each.
- How to distinguish "binding because the element is the actual bottleneck"
  from "binding because the element appears in an equation whose binding
  origin is elsewhere on the network." The `affects_generation` flag is
  intended to capture this but requires judgement.
- Whether to include elements outside QLD that bind on QLD generation
  (interconnector limits). Default: include, tag as `SEQ` (interconnector
  flows land at SEQ).

**Acceptance criterion.** All `confidence in {high, medium}` rows reviewed by
the author and spot-checked against AEMO constraint equation text. `review`
rows are excluded from the headline Test 5 analysis and form a sensitivity
subset.

---

## 2. `nem-constraints` schema confirmation **[ ]**

**Deliverable.** A short note in this file (Section 2 below this line) recording
the verified schema of the relevant `nem-constraints` DuckDB tables on the GCP
VM. The GitHub repo state of `nem-constraints` may not match the VM state
(see `[[ref-nem-constraints]]`); confirmation comes from the VM, not GitHub.

**What needs to be verified.**

- **Constraint equation table.** Columns identifying each equation (id,
  description, when introduced, when retired if applicable), and whether the
  RHS variables are stored alongside or in a separate equation-component table.
- **Binding flag time series.** Columns: equation id, dispatch interval
  timestamp, binding flag (or LHS value vs RHS for derived binding). Storage
  granularity (5-min dispatch vs aggregated).
- **Generator-to-equation mapping.** How generators are linked to the
  equations that constrain them (LHS variable string, dedicated mapping
  table, or both).
- **Time coverage.** Earliest and latest dispatch interval available on the
  VM; whether coverage is continuous or has gaps.

**Confirmed schema:** *(to be filled in by the author after VM query; leave
blank until verified.)*

```
-- placeholder; replace with actual confirmed DDL
```

---

## 3. First-entry onsets frozen as CSV **[ ]**

**Deliverable.** `data/derived/first_entry_onsets.csv`.

**Source.** Output of `notebooks/06_first_entry_tests.ipynb`, Section 4
(per-window concentration p-values) and Section 1 (per-window catchment
counts and rate ratios).

**Schema.**

| column | type | notes |
|---|---|---|
| `transmission_catchment` | string | One of the eight QLD catchments. |
| `onset_window` | date | First release window satisfying the onset definition (per-window chi-square p<0.05 AND catchment rate-ratio ≥ 2.0), or null if no qualifying window. |
| `onset_rate_ratio` | float | The catchment's first-entry rate ratio at `onset_window`. |
| `onset_window_pvalue` | float | The per-window concentration chi-square p-value at `onset_window`. |
| `censored` | bool | True if no qualifying window exists in the panel. |
| `source_notebook_commit` | string | Git short hash of the `06_first_entry_tests.ipynb` revision that produced this row. |

**Why frozen.** Onset windows are inputs to Test 5's lead-lag computation. If
notebook 06 is later edited, the frozen CSV ensures the published Test 5
result remains reproducible against the same upstream definition that was
pre-registered. Subsequent changes to notebook 06 require a new
`first_entry_onsets_vN.csv` and a documented revision of Test 5's input.

---

## 4. Pipeline code **[ ]**

**Deliverable.** `src/nem_herding/constraint_emergence.py`.

**Required functions.**

- `load_binding_events(con, start_date, end_date, catchment_lookup) -> pd.DataFrame`
  — Pulls binding events from the `nem-constraints` DuckDB connection, joins
  to the transmission-element-to-catchment lookup, returns a long DataFrame
  of (catchment, dispatch_interval, binding_count, total_intervals).
- `compute_binding_onset(binding_df, threshold=0.05, window_days=90) -> pd.DataFrame`
  — Computes m*(z) per catchment under a configurable
  threshold-of-intervals × rolling-window-days rule. Default is the
  pre-registered 5%/90-day headline. Must support the full 12-point
  robustness grid {2%, 5%, 10%} × {30, 60, 90, 180}.
- `compute_lead_lag(onsets_df, binding_df) -> pd.DataFrame`
  — Joins first-entry onsets to binding onsets per catchment, computes
  Δ(z), handles censoring on either side.
- `sign_test_lead_lag(lead_lag_df) -> dict`
  — One-sided sign test for Δ > 0 across uncensored catchments; bootstrap CI
  on median Δ with B=5000.
- `permutation_placebo(onsets_df, binding_df, n=1000, seed) -> np.ndarray`
  — Permutes catchment labels on first-entries, recomputes median Δ,
  returns the null distribution.

**Testing.** Unit tests with synthetic fixtures in `tests/test_constraint_emergence.py`.
Synthetic fixtures should include: (a) a clean lead case, (b) a clean
non-lead case, (c) one censored catchment, (d) one multi-catchment binding
event.

---

## 5. Analysis notebook **[ ]**

**Deliverable.** `notebooks/07_test_5_lead_lag.ipynb`.

**Required sections.**

1. Load first-entry onsets (frozen CSV) and the `nem-constraints` DuckDB
   connection.
2. Compute per-catchment Δ(z) under the 5%/90-day headline.
3. Headline statistics: median Δ, sign-test p-value, bootstrap CI, per-catchment
   table.
4. 12-point robustness grid {2%, 5%, 10%} × {30, 60, 90, 180}-day. Output
   median Δ at each grid point.
5. Permutation placebo: 1000 catchment-label permutations; report the
   percentile rank of the observed median Δ in the null distribution.
6. Onset-definition sensitivity: re-run under the two alternative onset
   definitions and the v0.5 transition-based definition (for the
   methodological comparison row).
7. Phantom-risk sensitivity: re-run at phantom-risk thresholds {1, 2, 3}.
8. Censoring robustness: rate-ratio-magnitude vs probability-of-binding-by-2025-07
   correlation.

**Runtime target.** Less than 5 minutes on a laptop, with the DuckDB query as
the dominant cost. The 12-point grid and permutation placebo should be cheap
once the binding event table is in memory.

---

## 6. Reproducibility hooks **[ ]**

**Deliverable.** A small `scripts/run_test_5.py` that runs the full
pipeline end-to-end from a single config, plus a `configs/test_5.yaml`
holding the pre-registered parameter choices.

**Why.** When the headline result is reported, a single
`python scripts/run_test_5.py --config configs/test_5.yaml` should
regenerate every number in the write-up. This guards against silent
parameter drift between the notebook (used for development) and the
published claims.

---

## Order of work

Roughly:

1. **Section 2** (schema confirmation) — depends only on VM access. Do first;
   it shapes everything downstream.
2. **Section 1** (catchment lookup) — depends on Section 2 to know what
   elements exist.
3. **Section 3** (frozen onsets CSV) — independent of 1 and 2; can be done in
   parallel.
4. **Section 4** (pipeline code) — depends on 1, 2, 3.
5. **Section 5** (notebook) — depends on 4.
6. **Section 6** (reproducibility hooks) — final wrapper; depends on 4 and 5.

Test 5 itself does not run until all six items are at **[x]**.

---

# Forward-work additions (recorded 2026-05-22, v0.7.3 era)

*Sections 1–6 above were scoped for the QLD-only Test 5. The NEM-wide extension
(v0.7.3 Test 4) and the causal framing add the items below. The **RHS-change
feasibility spike** is the next major piece of work after the v0.7.3 external review.*

## RHS-change feasibility spike (Test 5 prerequisite) **[ ]**

**Status:** Not started. Next major piece of work after the v0.7.3 external review.

**Why it gates Test 5.** Test 5's causal claim (herding → constraint emergence) is
mediated by network build. A herded corridor only binds when generation growth
(constraint **LHS**) outpaces transfer-limit growth (constraint **RHS**). Test 5
cannot be pre-registered until we know whether the RHS / network-build side is
observable. The spike determines which version of Test 5 is feasible:

- **If legible → strong Test 5:** "binding emerges where LHS herding growth outran
  RHS build growth."
- **If not legible → weak Test 5:** "herded corridors bind more often, augmentation
  unmodelled" (more confounded).

**The idea.** Rather than reconstructing the network-build timeline by scraping TAPRs,
AEMO augmentation announcements, ISP actionable-project updates, and the Open
Infrastructure database — a miserable, error-prone data-archaeology job — read network
changes off the **constraint equations themselves**. MMSDM holds constraint equation
definitions and RHS values, versioned and effective-dated. Network augmentation
propagates into constraint equations as: RHS step changes, new constraint equation IDs
appearing, old IDs retiring, and LHS coefficient (PTDF) shifts.

**The known trap.** RHS values change for many reasons that are **not** network build —
ambient/dynamic line ratings, plant availability, seasonal re-rating, constraint
formulation revisions, outage-specific constraints. A naive "RHS changed → augmentation"
rule would be swamped by false positives. Genuine build is distinguished by:
**permanence** (a level shift in the floor/typical RHS, not a transient excursion),
**structural change** (new equation IDs / LHS coefficient changes, not just a different
number), **correlation with major constraint-set version changes**, and
**corroboration** against known augmentation events.

**Spike scope (when started).**

- Pick 2–3 corridors with known, well-dated augmentation history — Western Downs area,
  a NSW corridor (CWO / Wollar–Bayswater area), optionally an SA corridor.
- Pull constraint equation definitions and RHS history for those corridors' binding
  constraints from MMSDM.
- Plot RHS over time; track when constraint IDs appear and retire; inspect whether
  structural changes are legible against seasonal/ambient noise.
- Validate candidate network-change events against the handful of known augmentations.
- Deliver a **yellow/green/red feasibility verdict** — explicitly time-boxed, a
  feasibility look, **not** the start of building a full RHS-change detector.

**Sequencing.** Self-contained; does **not** depend on the v0.7.3 Test 4 result being
blessed. Intended to run in parallel with the external review of v0.7.3 (which has
latency). Requires the `nemc-pipeline` GCP VM restarted (~$55/mo; currently terminated).

## Full prerequisite stack (one-place overview)

The complete set of gates before Test 5 can run, consolidating Sections 1–6 above with
the v0.7.3-era additions:

| Prerequisite | Status | Where |
|---|---|---|
| v0.7.3 Test 4 result through external statistical review | **[~]** in progress | `notebook_07_*`, `notebook_07_brief.md` |
| Transmission-element-to-catchment lookup (constraint-side analogue of the project-to-catchment lookup; **needs NEM-wide extension** — Section 1 is QLD-only) | **[ ]** | Section 1 |
| MMSDM / `nem-constraints` constraint schema confirmation (which tables carry constraint definitions, RHS values, effective dates, binding events) | **[ ]** | Section 2 |
| First-entry herding onsets frozen as a versioned CSV (fixed Test 5 input) | **[ ]** | Section 3 |
| **RHS-change feasibility spike** (this section) | **[ ]** not started | this section |
| GCP VM `nemc-pipeline` restart (~$55/mo; currently terminated) | **[ ]** terminated | infra |

*(Pipeline code (Section 4), analysis notebook (Section 5), and reproducibility hooks
(Section 6) follow once the data-side gates above are met.)*
