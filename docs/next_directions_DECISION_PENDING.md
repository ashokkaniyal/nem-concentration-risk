# Next directions — DECISION PENDING (holding document)

**This is a holding document, not a scope.** It records candidate next directions discussed at
the end of the notebook-07/08 work so they are not lost. **No direction is chosen.** A decision
should be made deliberately — rested, after review of the frozen results — **not by default** and
not tonight. Nothing here is a commitment.

---

## Where the work landed (factual summary)

- **Notebook 07** — announcement-stage, **catchment-level** concentration is **real and robust**:
  early-stage (Proposed/Anticipated) first-entries concentrate cross-catchmently within quarters
  (combined p ≈ 3.7e-18), surviving a permutation check. Five catchments carry the conditioned
  signal: **CWO, HCC, ILW, MN, NEW**. This is the cheap-signal, behavioural-precursor finding,
  with a documented **exposure-baseline circularity caveat** (the baseline is built from prior
  first-entries).
- **Notebook 08** — status-stratified (Committed / leak-corrected Existing / Withdrawn). The
  **corridor-level results are null or baseline artefact**: Committed-corridor is null (quarterly
  p = 0.40; pooled signal unstable/artefactual); Existing-corridor is significant only under the
  c2 catchment-count baseline (p = 0.0093) and **dissolves** under an activity-weighted baseline
  (p = 0.116, fails permutation). **One robust positive: SW-NSW energisation** — a *single
  catchment*, not a corridor, ambiguous mechanism (energisation is downstream of commitment, so
  may reflect construction/commissioning waves rather than decision herding). Documented the
  **c2 catchment-count baseline artefact** as a methodological finding.
- **Structural conclusion:** the **corridor** (SLD-topology grouping) is **not** the unit at which
  the phenomenon operates. The concentration that survives is **catchment-level** (nb07
  announcements; SW-NSW energisation).

---

## Candidate direction A — stop / consolidate

Treat notebooks 06/07/08 as a **closed, modest, honest body of work** and write it up as-is. No
new analysis. **Lowest effort; produces a defensible finished artefact.** The findings stand on
their own: a real catchment-level announcement-stage concentration signal, an honest set of nulls,
and a documented baseline-methodology contribution.

## Candidate direction B — thermal hosting-capacity tool

Generalise the prior **WA Pyomo dummy-generator hosting-capacity** work to the NEM:
dispatch-aware, **observed-bid-and-dispatch-conditioned**, **thermal constraints only**.
Explicitly bounded — **does NOT cover voltage, transient, oscillatory, or fault-level limits.**
Dissolves the baseline problem for the **thermal case** (gives a hosting-capacity baseline to
replace c2 / exposure for thermally-constrained corridors). **Buildable independently;
weeks-to-months.**
**Caveat:** must **not** claim to be a full hosting-capacity / PSS-E-equivalent tool.

## Candidate direction C — multi-layer hosting-capacity platform

Thermal + **voltage (AC OPF)** + **dynamic (transient / oscillatory / fault-level)**.
**Honest constraint:** the dynamic layer is **not an optimisation problem** and is **not
buildable in Pyomo** — it needs **time-domain dynamic simulation** and **confidential
dynamic-model data** (machine / inverter / controller parameters) that are **not publicly
available.** This is a **career-scale / institutional-home project with a hard data-access
dependency**, not an independent build.

---

## Shared open prerequisite (B and C)

The **RHS feasibility spike** (see `docs/test_5_prerequisites.md`). Its **first job** is to
**classify which NEM corridors are thermally constrained vs voltage/stability constrained**,
because the hosting-capacity framing is **well-posed only for thermally-constrained corridors.**

## Note on the curtailment/revenue analysis

The curtailment / revenue analysis discussed earlier is **subsumed** — it is the **economic layer**
that sits on top of whichever of B/C is pursued. It should **not** be scoped independently until
B or C is chosen.

---

## Status

**All directions undecided.** Decision to be made **deliberately, rested, against the frozen
results** — not by default, not tonight.
