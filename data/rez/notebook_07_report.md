# NEM-wide first-entry concentration — multi-resolution finding (notebook 07, v0.7.2)

Companion summary to `notebooks/07_nem_first_entry_tests.ipynb` (v0.7.2,
bootstrap-calibrated). Built 2026-05-21 against the v0.7.1 NEM-wide canonical
(`transmission_catchment_lookup.csv`, 2,109 projects; 1,023 high+medium REZ
first-entry events post left-censoring).

> **v0.7.2 note.** All per-unit p-values are **parametric-bootstrap calibrated**
> (B = 10,000), not asymptotic chi-square — the asymptotic test is anti-conservative
> here because expected per-window counts are small (often <1). Magnitudes are more
> modest than the v0.7 chi-square version; the qualitative finding is unchanged.
> Bootstrap floor = 1/(B+1) ≈ 1.0e-4 (a unit "at the floor" has true p < 1e-4).

---

## Headline

**The QLD herding mechanism replicates independently across the NEM, and the
herding-specific signature is present directly.** Two complementary findings, both
calibrated and both positive:

- **(a) Temporal burstiness within units** — first-entries swing between windows
  more than exposure predicts. Replicates on **disjoint project sets**: NSW, VIC, SA
  and QLD each significant (bootstrap p < 1e-4 each).
- **(b) Cross-catchment concentration within windows** — the *direct* herding test.
  In **10 of 18** windows, first-entries pile into particular catchments beyond the
  exposure baseline (calibrated multinomial bootstrap; combined **p ≈ 1.4e-17**).

---

## Finding (a) — within-unit temporal dispersion (§2–§4)

| Resolution | Units tested | # significant (Bonferroni, bootstrap) | # at floor | Best p (corrected) | Robustness |
|---|---:|---:|---:|---:|---|
| **State** (4, disjoint sets) | 4 | **4** | 4 | 4.0e-4 | identical at +review |
| **Cluster** (5 corridors) | 5 | **5** | 5 | 5.0e-4 | identical at +review |
| **Catchment** (23 REZ) | 21 | **12** | 7 | 2.1e-3 | identical set at +review |

Significant catchments (12, identical under both confidence tiers): CN-VIC, CQ, GIP,
MN, NEW, SD, SEQ, SW-NSW, SW-VIC, TAS-NW, WG, WV. **CWO** is *not* significant under
the bootstrap (its asymptotic p of 2.3e-3 was a small-cell artifact); FNQ was never
significant. All 5 corridors and all 4 states sit at the bootstrap floor (true p < 1e-4).

*TAS-NW: descriptive only (single-catchment state) — Fano 2.57, CI (1.16, 4.10).*

## Finding (b) — within-window cross-catchment concentration (§5, the direct herding test)

For each release window, the observed cross-catchment count vector is compared against
the exposure-share baseline, calibrated by a **multinomial bootstrap**. Because each
window's first-entries are a **disjoint** set of projects, combining the per-window
p-values via Fisher's method is legitimately independent — so this combined figure is a
genuine probability (floor-limited), not just an evidence index.

- **10 of 18** windows individually significant (calibrated, p < 0.05).
- Combined across windows: **p ≈ 1.4e-17** (1 window at the 1e-4 floor).
- Most-concentrated windows — **2021-05, 2022-06, 2023-05, 2024-04, 2025-04** — align
  with the major policy events in notebook 06's timing analysis (ISP/Roadmap, CIS design,
  CIS tenders).
- Asymptotic version (anti-conservative, for reference): 7.97e-37.

This is the herding-specific result: not merely that catchments are busy at different
times, but that developers crowd the *same* catchments at the *same* moments.

---

## Headline narrative (for panel / Akaysha communication)

**The QLD herding mechanism replicates independently across the NEM, and the
herding-specific signature is present directly.** Two things are true and they reinforce
each other. First, early-stage first-entries are **temporally bursty within transmission
units**, and this replicates on *disjoint project sets*: New South Wales, Victoria and
South Australia each contain entirely different projects from Queensland and from each
other, yet all four states independently show significant clustering (parametric-bootstrap
p < 1e-4 each, after Bonferroni). Three independent jurisdictions reproducing a fourth's
signal is replication in the strict sense.

Second — and more directly to the point of *herding* — in specific release windows,
first-entries concentrate into particular catchments far beyond the exposure baseline
(10 of 18 windows significant; calibrated combined p ≈ 1.4e-17). It is not merely that
catchments are busy at different times; developers crowd the *same* catchments at the
*same* moments, and those moments line up with major policy events. The signal is a
corridor-level phenomenon: aggregating catchments into the five *a priori* transmission
corridors, all five are significant at the bootstrap floor, because pooling along a shared
backbone concentrates rather than dilutes the bursts.

**Statistical honesty.** These conclusions use parametric/multinomial bootstraps rather
than the asymptotic chi-square, because expected per-window counts are small (often <1),
which makes asymptotic p-values unreliable and too small. The calibrated magnitudes are
more modest than a naive chi-square, but the qualitative finding is unchanged and now
defensible. What this establishes is the **clustering/herding pattern** (Test 4 territory);
it does **not** by itself establish that clustering *causes* subsequent transmission
constraint — that causal link is the separate, pre-registered **Test 5 (Claim 4)**.

---

## Methodology (short)

- **Unit of analysis:** project first-entry events (earliest AEMO release at
  Proposed/Anticipated; nb06's v0.6 refinement), phantom-cleaned, left-censored at the
  2020-02 panel start.
- **Two tests:** (a) within-unit temporal dispersion vs the unit's own exposure-scaled
  rate (parametric Poisson bootstrap, B = 10,000); (b) within-window cross-catchment
  concentration vs exposure shares (multinomial bootstrap, B = 10,000).
- **Resolutions:** catchment (23 REZ), cluster (5 corridors from
  `cluster_definitions_proposal.md`, fixed before testing), state (NSW/VIC/SA/QLD; TAS
  descriptive). n ≥ 10 per unit for formal testing.
- **Confidence:** primary `{high, medium}`; robustness adds `review` (§8).
- **Multiple comparisons:** Bonferroni per resolution (α = 0.05/N).

---

## QLD baseline replication (§1, methodological-infrastructure check)

§1 re-runs nb06's QLD analysis (asymptotic, by design) against the cleaned v0.7.1 canonical:

| Test | Notebook 06 | v0.7.1 | Match |
|---|---|---|---|
| QLD first-entries (n) | 254 | 254 | exact |
| WD / WG / SD Claim 1b p | 0.0081 / 0.0023 / 0.00022 | 0.0081 / 0.0023 / 0.00022 | exact |
| Claim 3 concentration Fisher's combined | 7e-8 | 7.04e-8 | exact (3 s.f.) |

Confirms the v0.7.1 cleanup preserved the pipeline. (These §1 numbers are asymptotic and
carry the small-cell limitation — see the caveats; that is precisely why §2 onward switches
to bootstrap calibration.)

---

## Robustness — sensitivity to the confidence filter (§8)

Re-running on `{high, medium, review}`:

- **(a) temporal dispersion:** states 4/4, clusters 5/5, and the catchment significant set
  is **identical** (12 units) under both tiers — a stable core, unlike the asymptotic version
  where CWO flickered in/out.
- **(b) within-window concentration:** 11/18 windows significant; calibrated combined
  p ≈ 1.6e-18.

**Verdict: robust.** The result is carried by the high/medium core, not the noisier review
tier.

---

## Key caveats (full set in notebook §10)

1. Asymptotic chi-square is anti-conservative here (small expected counts) — corrected by
   bootstrap. Inherited from nb06 (recorded in `catchment_lookup_schema.md`).
2. Bootstrap floor 1e-4: floored units have true p < 1e-4 but unresolved at B = 10,000.
3. Cross-unit Fisher figures are **evidence indices, not probabilities** (independence
   violated by the mechanism; scale with unit count). The §5 within-window combined p **is**
   a legitimate probability (windows are disjoint event sets).
4. Cross-resolution agreement is not independent confirmation (clusters/states are sums of
   the same events); cross-**state** is the genuine independent replication.
5. Establishes clustering/herding (Test 4), **not** the causal herding → constraint link
   (Test 5 / Claim 4).
