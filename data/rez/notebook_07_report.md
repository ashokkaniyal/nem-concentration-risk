# NEM-wide first-entry concentration — finding (notebook 07, v0.7.3)

Companion summary to `notebooks/07_nem_first_entry_tests.ipynb` (v0.7.3,
verified + confound-corrected). Built 2026-05-22 against the v0.7.1 NEM-wide canonical
(2,109 projects; 1,023 high+medium REZ first-entry events post left-censoring).

> **v0.7.3 changes.** (1) Foregrounds the within-window concentration test as the headline
> (it survives the verification permutation test). (2) Replaces the per-catchment temporal test
> with a **window-total-conditioned** version that removes a national-trend confound the
> verification caught. (3) Bootstrap **B = 100,000** (floor 1e-5) for genuine point estimates.
> Full verification: `data/rez/v072_verification_report.md`.

---

## Headline

**Renewable-generation first-entries concentrate cross-catchmently within specific release
windows — a NEM-wide, policy-aligned herding signature.**

In **10 of 18** independent release windows, new early-stage projects pile into particular
transmission catchments far beyond their exposure baseline; combined across the windows,
**p ≈ 3.7e-18** (parametric multinomial bootstrap, B = 100,000; no window at the floor). The
most concentrated windows — **2023-05, 2021-05, 2025-04, 2024-04, 2022-06** — align with major
policy events (AEMO ISP / NSW Roadmap, CIS design, CIS tenders). Each window is a disjoint set
of projects, so combining across windows is a legitimate independent combination, and the
result **survives a permutation test**: shuffling catchment labels by exposure destroys the
concentration.

---

## §2 — Within-window concentration (the headline test)

| | Primary (high+medium) | Robustness (+review) |
|---|---|---|
| Windows tested | 18 | 18 |
| Windows individually significant @0.05 | **10** | 12 |
| Combined p (independent windows) | **3.7e-18** | 1.5e-19 |
| Windows at bootstrap floor | 0 | 0 |
| Permutation check | concentration collapses to null | — |

This is the direct herding test (developers crowding the same catchment in the same window).
It conditions on the window total by construction, so it is immune to the national-trend
confound described below.

## §3–§5 — Conditioned temporal concentration (supporting)

*Which* units concentrate, after removing the national surge (expected[X,W] =
n_W × exposure_share_W[X]):

| Resolution | Conditioned significant (primary) | +review | Permutation collapse |
|---|---|---|---|
| **Catchment** | **5/21**: CWO, HCC, ILW, MN, NEW | identical 5 | 0.0 (was ~7.7 unconditioned) |
| **Cluster** | **4/5**: Central-Northern NSW, Eastern SA, Southern QLD, Western Victoria | identical 4 | 0.05 |
| **State** | **4/4**: NSW, VIC, SA, QLD | identical 4 | 0.0 |

Notable: **SW-NSW (n=116, the largest catchment) is not significant** under the conditioned
test (p≈0.47) — it grew with the market rather than herding. The significant sets are identical
across confidence tiers.

---

## The confound correction (v0.7.2 → v0.7.3) — audit trail

The v0.7.2 verification permutation test found that the old per-catchment temporal test
(constant mean rate) conflated a **national surge** (the whole NEM busy in a window) with
**catchment-specific** concentration: under a permutation that destroys catchment-specific
structure but preserves window totals, the old test still flagged ~7.7 of 12 catchments. So
"12 of 21 individually significant" (the v0.7.2 number) **overstated** unit-specific herding.

v0.7.3 conditions each window on its national total, so a unit riding the surge contributes ~0.
The conditioned test then **collapses to ~0 under the same permutation** (catchment 0.0,
cluster 0.05, state 0.0), confirming the confound is removed. The defensible
catchment count is therefore **5, not 12**. The headline §2 within-window test already
conditioned on window totals by construction, which is why it was correct throughout.

---

## Headline narrative (for panel / Akaysha communication)

**Renewable-generation first-entries concentrate cross-catchmently within specific release
windows — a NEM-wide, policy-aligned herding signature.** In 10 of 18 independent release
windows, new early-stage projects pile into particular transmission catchments far beyond what
each catchment's existing pipeline (exposure) would predict; combined across the windows the
effect is overwhelming (p ≈ 3.7e-18). The most concentrated windows line up with the major
policy events of the period (AEMO ISP / NSW Roadmap, the Capacity Investment Scheme design and
its tenders). Because each window is a separate set of projects, this is a genuine independent
combination, and it survives a permutation test — so the result is real spatial structure, not
a statistical artefact.

**Which catchments and regions herd — honestly stated.** A naive "is this catchment bursty
over time" test would credit a dozen catchments, but verification showed most of that was a
national surge rather than catchment-specific behaviour. After conditioning each window on its
national total, **5 catchments** (Central-West Orana, Hunter–Central Coast, Illawarra, SA
Mid-North, New England), **4 of 5 corridors**, and **all 4 mainland states** concentrate beyond
their exposure share — on disjoint project sets, so the cross-state agreement is independent
replication. Notably the single largest catchment (South-West NSW) is *not* a herding hotspot
once you account for how busy the market was.

**Status.** This establishes the herding *pattern* (Test 4). It does not establish that herding
*causes* subsequent transmission constraint — that is the separate pre-registered Test 5
(Claim 4). The analysis has passed a synthetic-null calibration check, an independent manual
re-derivation, and a permutation test.

---

## Methodology (short)

- **Headline test (§2):** per-window cross-catchment concentration vs exposure-share baseline,
  multinomial-bootstrap calibrated (B = 100,000); combined across disjoint windows.
- **Supporting test (§3–§5):** window-total-conditioned per-unit concentration
  (expected = n_W × share_W[X]); removes the national-trend confound; multinomial-bootstrap.
- **Unit:** first-entry events (earliest release at Proposed/Anticipated; nb06's v0.6
  refinement), phantom-cleaned, left-censored at 2020-02. n ≥ 10 per unit; Bonferroni per
  resolution. Catchments from the v0.7.1 lookup; 5 clusters from `cluster_definitions_proposal.md`.

## QLD baseline replication (§1)

Asymptotic, by design: QLD n=254, within-window Fisher's combined 7.04e-8, matching notebook 06
(7e-8). Pipeline verified.

## Key caveats (full set in notebook §10)

1. The v0.7.2 §2–§4 temporal test conflated national trend with catchment herding; v0.7.3
   conditions on window totals to separate them (permutation-confirmed).
2. Small expected counts → all tests bootstrap-calibrated (asymptotic anti-conservative).
3. B=100,000 floor 1e-5; no §2 window floored.
4. Cross-resolution results are not independent (same events re-cut); the independent
   comparisons are across windows (§2) and across states (§5, disjoint projects).
5. Establishes clustering/herding (Test 4), not the causal herding → constraint link
   (Test 5 / Claim 4).
