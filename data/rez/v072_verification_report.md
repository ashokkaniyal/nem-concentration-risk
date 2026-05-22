# v0.7.2 verification battery — report

Date: 2026-05-22. Verifies the bootstrap-calibrated v0.7.2 analysis in
`notebooks/07_nem_first_entry_tests.ipynb`. Three independent checks: synthetic
data (Type I + power), independent manual re-derivation, and a permutation test.

**Scripts:** `scripts/v072_pipeline.py` (faithful parameterised copy of the notebook's
exact functions, self-checked against committed numbers), `scripts/verify_v072_synthetic.py`,
`scripts/verify_v072_manual.py`, `scripts/verify_v072_permutation.py`.

---

## Verdict (read this first)

| Check | Result |
|---|---|
| Pipeline faithfulness (self-check) | ✅ reproduces committed numbers exactly (max p diff 5.6e-17 = machine ε) |
| Type I error — temporal test (synthetic null) | ✅ well-calibrated (FPR 5.95% vs 5%; 0% after Bonferroni) |
| Type I error — within-window test (synthetic null) | ✅ well-calibrated (FPR 4.5% vs 5% over 200 runs) |
| Power (synthetic planted clustering) | ✅ detects planted signal in exactly the planted units/windows |
| Manual re-derivation (independent code) | ✅ exact-seed reproduction matches; high-B confirms within MC noise |
| Permutation — within-window concentration (§5) | ✅ collapses to null → §5 detects genuine spatial concentration |
| Permutation — temporal dispersion (§2–§4) | ⚠️ **only drops 12→~7.7 sig units → partly a global temporal trend, not unit-specific** |

**Bottom line.** The **§5 within-window cross-catchment concentration test is fully
verified and is the load-bearing, defensible result** (p ≈ 1.4e-17; survives permutation;
correctly calibrated; strong power). The **§2–§4 within-unit temporal-dispersion results
are calibrated and reproducible, but the permutation test shows they substantially reflect a
shared national temporal trend rather than unit-specific herding** — they must be reframed
before external use (see "Methodology issues", item 1).

---

## 0. Pipeline self-check

`scripts/v072_pipeline.py` lifts the notebook's globals to arguments but is otherwise the
identical code. Run on real data it reproduces the committed results exactly:

- Catchment significant set: 12 (identical list: CN-VIC, CQ, GIP, MN, NEW, SD, SEQ, SW-NSW,
  SW-VIC, TAS-NW, WG, WV).
- Max |p_bootstrap − committed CSV| = **5.55e-17** (machine epsilon from CSV float round-trip).
- Within-window: 10/18 windows significant; combined p = 1.375e-17.

So the verification scripts (tasks 1 & 3) exercise the *actual* v0.7.2 machinery.

---

## 1. Synthetic data

### Scenario A — null (rate ∝ exposure baseline), 20 runs

Synthetic first-entries generated with per-(catchment, window) rate exactly proportional to
the real lagged-exposure matrix — i.e. the precise null both tests assume (no clustering
beyond exposure). *(Design note: a "uniform-over-windows timing" generator would not be the
right null — flat timing against growing exposure is itself a departure from baseline that the
temporal test is designed to flag. The correct no-clustering null is rate ∝ lagged exposure.)*

**(a) Temporal dispersion (calibrated bootstrap p):**
- Uncorrected FPR: **5.95%** vs nominal 5.00% (per-run range 0–14%).
- Bonferroni FPR: **0.000%** vs nominal 0.238% — no false positives survive correction.
- Pooled per-unit p (n=420): mean **0.514** (uniform → 0.5); KS vs Uniform[0,1] D=0.051,
  p=0.209 → consistent with uniform. (Bootstrap p is mildly discrete/conservative via
  (cnt+1)/(B+1).)

**(b) Within-window concentration (calibrated multinomial bootstrap):**
- Per-window FPR: mean 0.85 of 18 windows significant per run = **4.7%** vs nominal 5%.
- Combined-p (20 runs): median 0.66, min 0.017.
- Focused high-N check (**200 runs**): combined p<0.05 in **4.5%** (nominal 5%), median 0.535,
  min 0.0088. The 15% seen in the 20-run sample was small-sample noise.
- The null **never approaches** the real combined p (real 1.4e-17; null min 0.0088).

**Conclusion:** both tests control Type I error at the nominal rate. The calibration works.

### Scenario B — planted clustering (80% of events in 3 catchments × 4 windows)

Planted in 3 catchments that are **non-significant in the real data** (HCC, SE-SA, ILW) so
detection is cleanly attributable to the plant.

- All 3 planted catchments detected at the bootstrap floor (p_boot = 1.0e-4) in all 5 runs.
- Planted windows detected at the floor; within-window combined p = 1e-6 to 1e-9.

**Conclusion:** the pipeline has strong power to detect concentration where it genuinely exists.

---

## 2. Independent manual re-derivation

`scripts/verify_v072_manual.py` re-implements the observed statistic, the null specification,
and the bootstrap **from scratch** (no import of the pipeline). Two checks per catchment:
(A) reproduce the notebook's count using its exact seed; (B) estimate the true p at high B.

| Catchment | Observed T | (A) notebook seed, B=10k | Notebook | Match | (B) high-B (500k) true p | Notebook count vs true |
|---|---:|---|---|---|---|---|
| **MN** | 51.92 | count=3, p=4.00e-4 | count=3, p=4.00e-4 | **exact** | p≈5.0e-5 (±1.0e-5) | 3 vs exp 0.5 → +2.5σ (conservative) |
| **WD** | 36.09 | count=64, p=6.50e-3 | count=64, p=6.50e-3 | **exact** | p≈6.02e-3 (±1.1e-4) | 64 vs exp 60.2 → **0.49σ** |

**Reading:**
- The exact-seed reproduction (A) is the definitive check — independent code reproduces the
  notebook's bootstrap counts precisely (MN 3, WD 64). The reported p-values are exactly
  reproducible.
- WD's true p (6.02e-3) matches the notebook's 6.5e-3 within Monte-Carlo noise (0.49σ) — clean.
- MN's true p (≈5e-5) is actually **below the 1e-4 floor**; the notebook's B=10,000 estimate
  (4e-4) caught a +2.5σ upward fluctuation at near-floor counts. This is in the **conservative
  direction** (reports a *larger*, less-significant p than truth), and it confirms why
  near-floor units should be read as thresholds, not precise values (see issue 2).

No discrepancy indicating a bug; the bootstrap is correctly implemented.

---

## 3. Permutation test (20 permutations)

Each event keeps its window (preserving the temporal structure / window totals) but is
reassigned a catchment drawn from that window's lagged-exposure shares (destroying spatial
structure). The real v0.7.2 pipeline is then run.

**(b) Within-window cross-catchment concentration — the critical check:**
- Windows significant @0.05: mean **0.90 of 18** = nominal 5%; combined p median **0.493**,
  min 0.053, fraction <0.05 = **0%**.
- Real combined p was 1.4e-17; the permuted analysis **never approaches it**.
- ✅ **Spatial concentration is destroyed by the permutation, exactly as it should be.** The
  §5 result is detecting genuine cross-catchment concentration, not a test artefact. No bug.

**(a) Within-unit temporal dispersion under permutation:**
- Catchments significant: mean **7.7 of 21** (real = 12; range 6–10).
- It does **not** collapse to ~0. Because the permutation preserves window totals, it preserves
  the *global* temporal burst (the overall first-entry rate varying over time relative to
  exposure); only the catchment-*specific* component is destroyed.

---

## Methodology issues uncovered (honest assessment)

**1. (Material) The §2–§4 temporal-dispersion test conflates a global temporal trend with
unit-specific herding.** Under a permutation that destroys all catchment-specific structure
but preserves window totals, ~7.7 of the 12 significant catchments remain significant. So a
majority (~64%) of the temporal-dispersion significance is attributable to a *shared national
rate trend* — the whole NEM's first-entry rate surging in particular windows (2021-05,
2023-01, 2024-04) relative to exposure — not to catchments behaving differently from one
another. Root cause: the test's expected count uses a single constant `mean_rate` per unit and
does not condition on the per-window total, so a global surge inflates every unit's statistic
simultaneously. **Implication:** "12 of 21 catchments individually significant" must not be
read as 12 independent unit-specific herding events; and the cross-state "replication"
partly reflects a common national driver firing in all states at once. *(That common driver
may itself be the policy signal — interesting — but it is a different claim from unit-specific
herding.)* **Fix options:** (i) foreground §5 as the herding test and explicitly down-weight
§2–§4 to "consistent with clustering, not isolating unit-specific from global-temporal"; or
(ii) add a global-rate-controlled temporal test (expected_w = (n_w / Σ_u exposure_w) ×
exposure_w[u], i.e. condition on the window total — which is essentially what §5 already does).

**2. (Minor) Near-floor bootstrap p-values are noisy at B = 10,000.** MN's reported 4e-4 has
a true value ≈5e-5; at B = 10,000 the expected count is <1, so the estimate swings several σ.
This does not change any significance decision (floor < every Bonferroni threshold), but the
*magnitudes* of strong/near-floor units are unreliable. **Fix:** report such units as "< 1e-4"
(already the convention) and/or raise B (e.g. 10⁵–10⁶) if precise magnitudes are wanted.

**3. (Already documented, confirmed.) The cross-unit Fisher "evidence indices" are not
probabilities** (independence violated; scale with unit count) — unchanged from §10 of the
notebook. The §5 within-window combined p **is** a legitimate probability because windows are
disjoint event sets; the synthetic-null and permutation checks both confirm it is calibrated.

**No bugs were found.** All three issues are interpretation/limitation matters, not coding
errors; the pipeline is faithful (self-check) and the implementations are correct (manual
re-derivation).

---

## What is defensible externally

**Ready now (survives every check):**
- The **§5 within-window cross-catchment concentration result** — the direct herding test.
  Calibrated (synthetic null), powerful (planted clustering), and verified genuine
  (permutation collapses it to null). Combined p ≈ 1.4e-17, robust to confidence tier
  (§8: 11/18 at +review). This is the headline that should lead any external presentation.
- The **existence** of NEM-wide, multi-state clustering on disjoint project sets.

**Needs reframing before external use:**
- The §2–§4 "12/21 catchments / 4/4 states / 5/5 clusters individually significant"
  temporal-dispersion magnitudes — re-state with the global-trend caveat (issue 1), or add the
  window-total-controlled version of the temporal test.
- Strong/near-floor per-unit magnitudes — report as thresholds or raise B (issue 2).

**Recommendation:** apply the issue-1 reframe (and optionally the controlled temporal test) as
a v0.7.3 revision, then the analysis is ready for a statistically-literate colleague and
subsequently Barry O'Connell. The within-window finding is the solid core; the temporal-
dispersion section should support it, not lead.

---

# v0.7.3 re-verification (2026-05-22)

v0.7.3 implemented the issue-1 fix: §3–§5 now use a **window-total-conditioned** temporal test
(`scripts/v072_pipeline.py::conditioned_temporal`), expected[X,W] = n_W × exposure_share_W[X].
Re-verification script: `scripts/verify_v073_conditioned.py`.

## Confirmation criterion — permutation collapse of the conditioned test

The decisive check: re-run the same exposure-baseline label permutation on the **conditioned**
test. If the fix works it should collapse close to null (the way the within-window §5 test
does), unlike the old test's 12 → ~7.7.

| Resolution | Real conditioned-significant | Permuted (20 perms), mean [range] | Nominal | v0.7.2 unconditioned (permuted) |
|---|---:|---|---:|---:|
| Catchment | 5 | **0.00** [0–0] | ~1.1 | ~7.7 |
| Cluster | 4 | **0.05** [0–1] | ~0.2 | — |
| State | 4 | **0.00** [0–0] | ~0.2 | — |

✅ **The conditioned test collapses to ~0 under permutation at every resolution.** The
national-trend confound is removed. (Confirmation criterion passed.)

## Type I — synthetic null (conditioned test)

Generated under the exposure-proportional null (20 runs); conditioned test:
- uncorrected FPR **4.79%** (nominal 5%); pooled per-catchment p mean 0.495; frac<0.05 4.76%;
  KS vs Uniform p = 0.792 → well-calibrated.

## Effect on the real result

| | v0.7.2 (unconditioned) | v0.7.3 (conditioned) |
|---|---|---|
| Catchment significant | 12 of 21 | **5 of 21** (CWO, HCC, ILW, MN, NEW) |
| Cluster significant | 5 of 5 | **4 of 5** (not Northern Victoria) |
| State significant | 4 of 4 | **4 of 4** (unchanged) |

Membership also changed at the catchment level: only MN and NEW are significant under both;
CWO/HCC/ILW emerge under conditioning; SW-NSW (the largest catchment) drops to p≈0.47 — it
tracked its exposure share rather than herding.

## Headline (§2) at raised B = 100,000

The within-window concentration test (unchanged in logic — it always conditioned on window
totals) re-run at B = 100,000: **10/18 windows significant, combined p = 3.69e-18**, with **no
window at the floor** (genuine point estimates; at B=10,000 one window had been floored). The
headline strengthened marginally and is now floor-free.

## Updated honest assessment — is v0.7.3 externally defensible?

**Yes, with the framing now correct.**
- The **§2 within-window concentration result** (p ≈ 3.7e-18) is the load-bearing finding:
  calibrated (Type I 4.5%), powerful (planted-signal recovery), verified genuine (permutation
  collapse), and now floor-free at B=100,000.
- The **§3–§5 conditioned temporal results** (5 catchments / 4 clusters / 4 states) are the
  honest, confound-corrected "which units herd" numbers — and the conditioned test itself is
  now permutation-confirmed (collapses to ~0).
- The national-trend confound that v0.7.2 carried is documented (notebook §10, item 1) and
  fixed; this is a clean audit trail rather than a hidden correction.

**Nothing new surfaced** in the v0.7.3 re-verification. Remaining boundaries are unchanged and
already documented: this establishes the herding *pattern* (Test 4), not the causal
herding → constraint link (Test 5 / Claim 4); cross-resolution results are not independent (the
independent comparisons are across windows and across states). v0.7.3 is ready for a
statistically-literate colleague and then Barry O'Connell.
