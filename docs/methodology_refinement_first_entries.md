# Methodology refinement: first-entry events as the upstream herding signal

*Added 2026-05-18 after empirical observation. Author: Ashok Kaniyal with Claude.*

## Context

The framework's v0.5 specification treated **status transitions** (project moves from
one status bucket to another between two AEMO releases) as the unit of analysis for
the herding detection tests (Claims 1, 1b, 3).

This refinement documents why that was wrong, what the right unit is, and what changed
empirically when the test was re-run on the corrected unit.

## The observation

The April 2024 release window showed eight QLD projects transitioning together
(Borumba, Chinchilla BESS, Dulacca Wind, Munna Creek, Wambo Wind, Wandoan South Solar
Stage 1, Western Downs Battery, Woolooga Solar). At first sight this looks like a
coordinated herding event in April 2024.

But each of these projects' panel histories shows they first appeared in AEMO data
between February 2020 and January 2023 — a four-year spread. The April 2024
transitions are the *terminal* outputs of their respective 2-4 year development
pipelines, not a coordinated April 2024 decision.

## The implication

Australian project development pipelines typically run 4-7 years:

```
Announcement → Approvals → Connection studies → FID → Construction → Energisation
```

A policy event in 2021 cannot cause a Committed→Existing transition in 2021. It can
cause an *announcement* in 2021, which becomes Committed around 2023-2024 and Existing
around 2025-2026. Each project's status transitions are largely governed by its own
internal process clock, not by external coupling at the time of transition.

The herding decision — whether a developer commits speculative capital to a site in a
particular catchment — happens at the *announcement* stage. Status transitions in
later periods are lagged echoes of that earlier herding, smeared out by heterogeneous
development timelines.

Testing for herding at the transition stage measures the wrong thing. It measures
*coincident process-clock outputs*, not coupled decision-making. The signal exists but
it's noisier and weaker than it needs to be.

## The correct unit of analysis

**First-entry events.** For each project, the release window in which it first appears
in the AEMO Generation Information register. This is the earliest visible decision
signal — the moment a developer commits enough capital to a site that AEMO learns
about it and surveys it.

First-entry events at the Proposed or Anticipated status bucket are the primary
signal. (First-entries directly at Committed or Existing are rare and usually
artefacts of project re-classification or AEMO data backfill.)

This refinement requires:

1. Left-censoring: projects that first appear in the panel start window (2020-02 for
   this dataset) cannot have their first-entry observed — they existed before the
   panel began. Drop them from the test.
2. Status filtering: restrict to first-entries at Proposed or Anticipated to avoid
   contamination from late-pipeline re-classification events.

## Empirical comparison

Both tests run on QLD catchments, phantom-cleaned, with exposure as project count at
the prior release.

| Test | v0.5 (transitions) | refined (first-entries) |
|---|---|---|
| Sample size | 78 QLD events | 254 QLD events |
| WD Claim 1b p | 0.0075 | 0.0081 (stable) |
| WG Claim 1b p | 0.036 | **0.0023** |
| SD Claim 1b p | 0.527 (NS) | **0.00022** |
| CQ Claim 1b p | 0.482 (NS) | **<0.000001** |
| SEQ Claim 1b p | 0.0001 (suspect) | 0.00031 (corroborated) |
| Fisher's combined Claim 3 | p = 6×10⁻⁴ on 12 windows | **p = 7×10⁻⁸ on 15 windows** |

The qualitative narrative also clarified: significant clustering windows in the
first-entry data fall within 6-12 months of major policy events
(NSW Roadmap and first ISP → 2021-07 cluster; CIS design finalisation →
2023-05 cluster; CIS Tender 1 outcomes → 2024-04 cluster). That timing relationship
is consistent with policy-driven herding at the announcement stage with a typical
delay of 3-12 months — which is the right order of magnitude for the
land-option-and-feasibility-study process between a policy signal and an AEMO
registration.

## What this changes about the framework

1. **Claim 1 and Claim 3 should be run on first-entries.** Status transitions remain
   useful for project-level progress tracking and for Claim 4 (constraint emergence)
   but are not the right unit for the upstream herding test.

2. **Claim 2 (Layer A coupling) is back on the table.** The original specification
   tested "policy events excite next-quarter transitions" — implausible given
   development lags. The refined specification tests "policy events excite new
   project announcements at 3-12 month lags" — which is plausible and now
   empirically supported by the timing alignment in the first-entry windows.

3. **The "buildout pipeline" is the right intermediate concept.** A herding event at
   time T produces first-entries clustered around T+3 to T+12 months, then
   Anticipated transitions at T+1 to T+2 years, then Committed at T+2 to T+3 years,
   then Existing at T+3 to T+5 years. The framework needs to be clear about which
   stage of this lag chain each test is measuring.

## Limitations of the refinement

- **Phantom contamination is higher in first-entries.** Many shell developers register
  speculative projects with AEMO that never reach FID. These projects show up as
  first-entries but should not count as herding signal. The phantom-risk filter
  applied at the project level already mitigates this — phantoms classified as
  risk=2 are excluded from the headline analysis — but this is a more important
  decision than at the transition level. Some sensitivity analysis on the
  phantom-risk threshold would strengthen this.
- **AEMO registration lag is unknown.** A developer's "decision moment" precedes their
  AEMO registration by some unknown interval. If different developers have different
  lags between decision and registration, the first-entry timing is itself smeared.
  Probably a smaller effect than the project-status-clock smearing, but real.
- **Left-censoring reduces the panel start period.** Of 561 QLD projects in the
  current data, 154 are left-censored. This is a one-time cost of the panel
  start date, not an ongoing limitation.

## Next steps

1. Update the framework's Claim 1, 1b, 3 specifications in preregistration.md to
   identify first-entries as the primary unit, transitions as a secondary check.
2. Add a notebook `06_first_entry_tests.ipynb` that runs both unit-of-analysis
   choices side-by-side for the audit trail.
3. Refine Claim 2 to test policy-event coupling at the first-entry stage with
   3-12 month lags rather than transition-stage coupling at next-quarter lags.
4. Consider extending the test to other NEM states (NSW REZs especially) — given
   the increased sample size at first-entries, multi-state replication becomes more
   feasible.
