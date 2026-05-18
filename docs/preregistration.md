# Pre-registration

*Predictions, tests, and falsification criteria committed to before running analysis.*

This document operationalises the methodology (`methodology.md`) into specific
empirical claims. Each claim is stated as a numerical prediction with a documented
test procedure and a falsification criterion. The discipline is to commit to these
*before* the data is analysed, so that subsequent results can be evaluated against
the original hypothesis rather than against a hypothesis silently revised after
seeing the data.

**Version control commitment.** This document is dated. Subsequent versions —
which may revise predictions in light of analysis results — will be marked as
*revisions* with explicit notes about what changed and why. The original
predictions remain in git history.

**Reading guide.** Each test in this document specifies:

- **Hypothesis** — the claim in plain words
- **Operationalisation** — how the claim translates into measurable quantities
- **Test statistic** — what is computed
- **Prediction** — the predicted direction and (where possible) magnitude
- **Null behaviour** — what would be observed if the hypothesis is wrong
- **Falsification criterion** — the specific result that would falsify the
  hypothesis
- **Robustness checks** — variations to confirm the result is not artefactual

Predictions are *prior* to data collection completion in some cases. Where this
is the case, it is noted.

---

## Test 1 — Synchronisation existence

### Hypothesis

REZs that have undergone substantial investment exhibit self-exciting clustering
of investor decisions: past events make future events more likely than a Poisson
null would predict.

### Operationalisation

Fit a Hawkes-process model to events of each type (financial close, commissioning)
within each REZ, with self-excitation parameter α and exponential decay kernel
g(s) = exp(-s/τ).

The Hawkes intensity is:

```
λ(t, z) = μ(z) + Σⱼ:tⱼ<t α · exp(-(t-tⱼ)/τ)
```

### Test statistic

Maximum-likelihood estimate of α with standard error from the inverse Fisher
information matrix.

### Prediction

For REZs with cumulative committed capacity > 1 GW at time of analysis:

- **α > 0** with 95% confidence interval excluding zero
- **τ in range 6-24 months** (memory of past events neither immediate nor
  permanent)

For REZs with cumulative committed capacity < 250 MW (controls):

- **α ≈ 0** (not statistically distinguishable from zero)

### Null behaviour

If decisions are truly independent Poisson events, α ≈ 0 in all REZs and the
Hawkes likelihood is no better than the Poisson likelihood (formal test:
likelihood ratio).

### Falsification criterion

- α not distinguishable from zero in all "mature" REZs would falsify the
  framework's core synchronisation claim.
- τ outside the 6-24 month range would suggest a different temporal structure
  than the framework predicts and require methodological revision.
- α > 0 in both mature *and* immature REZs would suggest the synchronisation
  effect is not stage-dependent, requiring revision of the K_c-threshold claim.

### Robustness checks

1. **Alternative kernels.** Re-estimate with power-law and Weibull kernels.
   The qualitative result (α > 0 in mature REZs) should be robust to kernel
   choice. If not, the framework's claims about temporal structure require
   refinement.

2. **Subsample stability.** Estimate α separately for pre-2022 and post-2022
   subperiods. Result should be qualitatively consistent across subperiods
   for any single REZ.

3. **Aggregation level.** Re-estimate at monthly versus quarterly aggregation.
   The Hawkes specification should produce broadly similar conclusions.

4. **Cross-REZ comparison.** Across mature REZs, α should be of similar
   order of magnitude. Wildly disparate estimates would suggest REZ-specific
   confounders dominating over the framework's structural claim.

---

## Test 2 — Policy events as exogenous shocks

### Hypothesis

Layer A policy events shift investor intensity. The magnitude of the shift
depends on the event category in a predictable way:

- **Commitment events** (REZ declarations, FIDs, CIS auction announcements)
  produce the largest intensity jumps because they alter the substrate
  *and* trigger Layer 1 cascades.
- **Information events** (ISP releases, ESOO releases) produce intermediate
  jumps because they alter the substrate without (necessarily) triggering
  Layer 1 cascades.
- **Competitive events** (auction results, access rights awards) produce
  concentrated jumps among the subset of investors competing for the
  announced opportunity, smaller on aggregate.
- **Adverse events** (MLF resets, curtailment announcements) produce
  delayed *negative* responses.

### Operationalisation

Extend the Hawkes specification with Layer A event indicators:

```
λ(t, z) = μ(z) + Σⱼ:tⱼ<t α · exp(-(t-tⱼ)/τ) + Σₖ βₖ · I[Aₖ(t, z)]
```

where Aₖ(t, z) is an indicator for an event of category k affecting REZ z
in a recent window (e.g., previous 90 days).

### Test statistic

Estimated coefficients β_commitment, β_information, β_competitive, β_adverse
with standard errors.

### Prediction

- **β_commitment > β_information > β_competitive > 0** (in magnitude)
- **β_adverse < 0** (with appropriate lag structure; predict 3-12 months)
- Magnitudes: β_commitment in the range 0.3-1.5 (intensity multiplier of
  ~30-150% over baseline); β_information in 0.1-0.5; β_competitive in
  0.05-0.3; β_adverse in -0.05 to -0.3.

The magnitude predictions are deliberately wide. They reflect priors rather
than precise estimates and serve as sanity checks against estimates that
imply implausibly large or small responses.

### Null behaviour

If policy events do not synchronise investors, all β coefficients are not
distinguishable from zero.

### Falsification criterion

- If β_information > β_commitment in magnitude, the framework's prediction
  about which event types dominate is wrong. This would not necessarily
  falsify the overall synchronisation framework but would require revision
  of the Layer 1 / Layer 2 mechanism story.
- If β_adverse > 0, the framework's reading of adverse events is wrong.
  This would suggest that adverse signals (curtailment, MLF degradation)
  paradoxically *accelerate* synchronised investment — a plausible but
  unexpected outcome that would itself be a finding.
- If all β coefficients are zero, the framework's claim about exogenous
  drivers of synchronisation is wrong.

### Robustness checks

1. **Event window length.** Re-estimate with 30-, 60-, and 180-day windows
   around event dates. Qualitative ordering of β coefficients should be
   stable.

2. **Lead-lag tests.** Estimate β with event indicators *leading* the
   analysis date (placebos). β should be significant only at non-negative
   lags, not at leads (otherwise the framework is picking up reverse
   causation).

3. **Outlier event sensitivity.** Drop the single largest β-contributing
   event in each category. Estimates should be qualitatively stable.

---

## Test 3 — Layer 2 information environment as time-varying coupling

### Hypothesis

The intensity of the information environment around a REZ — measured through
trade press article counts, conference session counts, and AEMO publication
frequency — acts as a multiplier on the coupling strength between investors.
Higher Layer C intensity means stronger Layer 2 coupling.

### Operationalisation

Extend the Hawkes specification with a Layer C intensity covariate I(t, z),
both as a main effect and as an interaction with Layer A event indicators:

```
λ(t, z) = μ(z) + Σⱼ α(t, z) · exp(-(t-tⱼ)/τ) + Σₖ βₖ · I[Aₖ] + γ · I(t, z) + Σₖ δₖ · I[Aₖ] · I(t, z)
```

where α(t, z) is also allowed to depend on I(t, z), capturing the framework's
hypothesis that Layer C amplifies Layer 1 coupling.

### Test statistic

Estimated γ (main effect) and δₖ (interactions) coefficients, with standard
errors. Likelihood-ratio test against the specification without Layer C.

### Prediction

- **γ > 0**: higher information intensity raises baseline investor intensity
  (Layer 2 coupling effect).
- **δₖ > 0 for k ∈ {commitment, information}**: higher information intensity
  amplifies the response to policy events.
- **δₖ ≈ 0 for k ∈ {competitive}**: competitive events affect specific
  bidders, not the herd at large; their response is less moderated by Layer
  C.

### Null behaviour

If Layer C has no effect, γ ≈ 0 and δₖ ≈ 0 for all k. The model with Layer
C is no better than the model without.

### Falsification criterion

- γ ≤ 0 (not just statistically insignificant, but in the wrong direction)
  would falsify the framework's prediction about Layer 2 coupling. This
  would suggest the information environment either suppresses synchronisation
  (puzzling but possible) or is so noisy that the proxy is uninformative
  (which would require methodological revision rather than substantive
  revision).
- δₖ ≤ 0 would suggest information environment *suppresses* the response to
  policy events, contrary to the amplification hypothesis.

### Robustness checks

1. **Alternative Layer C proxies.** Re-estimate using only trade press counts;
   only conference sessions; only AEMO publications. Each should produce a
   directionally similar γ even if magnitudes differ.

2. **Reverse-causation test.** Layer C is included with a multi-month *lead*
   (e.g., I(t+6, z)) as a placebo. γ on the lead should be zero or smaller
   than γ on the contemporaneous specification. If not, the framework is
   picking up reverse causation: the herd is driving Layer C rather than the
   reverse.

3. **Granger-style test.** Run vector-autoregression on weekly Layer B event
   counts and Layer C intensity within each REZ. Test whether Layer C
   Granger-causes Layer B (predicted) versus the reverse (warning sign).

---

## Test 4 — Regime persistence and hysteresis

### Hypothesis

The self-excitation amplitude α is not constant within a REZ but rises with
cumulative committed capacity, plateauing at high cumulative capacity.
Specifically, the framework predicts the "hysteresis" pattern: once
synchronisation is established it is hard to break, even if exogenous
conditions deteriorate.

### Operationalisation

Estimate α as a function of cumulative committed capacity C(t, z):

```
α(t, z) = α₀ + α₁ · log(C(t, z) + 1)
```

(log scale to capture diminishing returns at high capacity)

Or, in a non-parametric specification, estimate α separately for capacity
quartiles within each REZ.

### Test statistic

Estimated α₁ with standard error; or non-parametric estimates of α at low,
medium, high cumulative capacity.

### Prediction

- **α₁ > 0**: α rises with cumulative capacity.
- **Non-parametric α** is higher in the medium-to-high capacity range than
  in the low range, and may plateau or decline very late.
- The implied "synchronisation threshold" — cumulative capacity at which α
  becomes statistically distinguishable from zero — is on the order of
  500 MW to 1 GW per REZ.

### Null behaviour

If there is no hysteresis, α₁ ≈ 0 and α is constant across buildout stages.

### Falsification criterion

- α₁ ≤ 0 would falsify the hysteresis prediction.
- α non-monotonic in cumulative capacity (e.g., rising and then sharply
  declining) would suggest a different dynamic than the framework predicts
  and require methodological extension (possibly a chimera-state or partial-
  synchronisation specification rather than uniform-synchronisation
  Kuramoto).

### Robustness checks

1. **Alternative capacity measures.** Replace cumulative committed capacity
   with cumulative connected capacity, cumulative operating capacity, or
   number of distinct investors. Direction of α dependence should be
   robust.

2. **Stage definitions.** Replace continuous capacity with discrete buildout
   stages (early / filling / mature). Same qualitative direction expected.

3. **Counterfactual unbuilt REZs.** Apply the same methodology to REZs that
   were declared but have low buildout (e.g., Hunter-Central Coast in early
   years). α should remain near zero throughout, consistent with the
   framework's "below threshold" prediction.

---

## Test 5 — Synchronisation onset precedes constraint emergence (Claim 4 / Option C)

> **v0.6 unit-of-analysis note.** This test was originally scoped against
> status-transition clustering windows. The methodology refinement of 2026-05-18
> (`docs/methodology_refinement_first_entries.md`) established that status
> transitions are 2-3 years downstream of the underlying herding decision.
> Onset is therefore defined on **first-entry clustering windows**
> (Proposed/Anticipated first-entries per release window per catchment, as in
> `notebooks/06_first_entry_tests.ipynb`), not on transition clustering
> windows. Using transitions would shift onset by roughly the typical
> Anticipated→Committed pipeline lag (~2-3 years) and invert the sign of the
> predicted lead-lag in at least one catchment (WD).

### Hypothesis

Within a catchment, the **onset of investor synchronisation** —
operationalised as the first release window in which the catchment exhibits a
statistically anomalous concentration of project first-entries — *precedes*
the **onset of binding transmission constraint regimes** in that catchment by
a lag consistent with the development pipeline. The framework predicts a lag
in the range of 18-48 months: the time between a herding-stage decision
(first-entry) and the network's first sustained inability to dispatch the
resulting cluster (binding constraint). The range reflects process arguments
about typical first-entry-to-binding sub-intervals (2-5 years with real
spread); it is deliberately not narrowed to fit any single catchment's
qualitative history.

This is the framework's central practical claim. If first-entry clustering
does not lead constraint emergence, then the synchronisation pattern is
either (i) not causally upstream of physical constraint risk, or (ii) the
constraint regime adapts faster than the framework supposes, neither of
which supports the v0.5 risk-assessment use case.

### Operationalisation

**Onset of synchronisation (per catchment z).** The first release window w*(z)
satisfying *both*:

1. **Per-window concentration significant.** w* falls in the set of release
   windows for which the per-window first-entry concentration chi-square
   against exposure-weighted expected (notebook 06, Section 4) returns
   p < 0.05.
2. **Catchment z is one of the concentrated catchments at w*.** Catchment z's
   first-entry rate ratio (observed / expected at w*) is ≥ 2.0.

If no window satisfies both conditions, w*(z) is right-censored at the panel
end (2025-07) and the catchment contributes a censored observation.

**Onset of constraint emergence (per catchment z).** The first month m*(z)
satisfying:

1. **Persistent binding.** A transmission element mapped to catchment z is
   binding for ≥ 5% of dispatch intervals within a rolling 90-day window.
   (The 5%/90-day threshold is a commitment; see Robustness check 2 for the
   sensitivity grid.)
2. **Affecting catchment generation.** The binding constraint's right-hand-side
   equation includes at least one generator located in catchment z.

Binding-event timestamps come from the sibling `nem-constraints` repository's
DuckDB warehouse. The transmission-element-to-catchment mapping and other
prerequisites are tracked in `docs/test_5_prerequisites.md`; Test 5 does not
run until all items listed there are complete and committed.

**Lead-lag statistic (per catchment z).** Δ(z) = m*(z) − w*(z), measured in
months. Defined only for catchments where both w*(z) and m*(z) are observed
(not censored).

### Test statistic

1. **Sign test** on {Δ(z)} across QLD catchments: H₀ median Δ = 0. Reported
   as one-sided p-value for Δ > 0.
2. **Median and bootstrap CI** on Δ across catchments (B = 5000 resamples).
3. **Per-catchment Δ(z) table** with onset windows, binding-onset months,
   censoring flags.

### Prediction

Across the eight QLD catchments {WD, SD, DD, TG, WG, FNQ, CQ, SEQ}:

- **Median Δ in the range 18-48 months**, positive (onset leads constraint
  emergence). The 18-48 month range is grounded in process arguments about
  the first-entry-to-binding development pipeline (typical 2-5 years with
  real spread), not in fit to any specific catchment.
- **Sign-test one-sided p < 0.05** for Δ > 0.
- **Catchments with low / no first-entry concentration** (e.g., DD, TG, FNQ)
  are left-censored on w*; they contribute to a robustness check but not to
  the headline statistic.

### Null behaviour

If first-entry clustering is not causally upstream of constraint emergence:

- Δ values are roughly symmetric around zero across catchments.
- Sign-test p ≈ 0.5.
- No systematic relationship between first-entry rate-ratio magnitude at
  w*(z) and Δ(z) or constraint severity at m*(z).

### Falsification criterion

The framework's Claim 4 is falsified, or seriously qualified, if any of:

1. **Sign-test one-sided p > 0.20** for Δ > 0 across QLD catchments (no
   detectable lead).
2. **Median Δ < 6 months.** Lead exists but is too short to be consistent
   with the buildout-pipeline mechanism; would suggest the apparent lead is
   an artefact of measurement timing rather than a structural lag.
3. **Median Δ < 0** (constraint emergence *precedes* first-entry clustering).
   Would invert the framework's causal direction and require a different
   mechanism story (e.g., constraint relief triggering speculative
   first-entries rather than first-entries provoking constraint regimes).
4. **Δ(WD) ≤ 0 and the QLD cross-sectional median Δ is also non-positive,
   *conditional on m*(WD) being observed (not censored)*.** If WD is
   censored on binding onset, this criterion is inapplicable and the
   headline cross-sectional median governs alone. WD alone with a positive
   cross-section is a partial result, not a falsification.

### Robustness checks

1. **Onset-definition sensitivity.** Re-compute w*(z) under three alternative
   definitions:
   (a) first window with rate ratio ≥ 2.0 *without* requiring per-window
       chi-square significance (more permissive),
   (b) first window in a run of ≥ 2 consecutive windows with rate ratio
       ≥ 1.5 (smoother),
   (c) the v0.5 transition-based definition (for explicit methodological
       comparison; expected to produce systematically later w* and
       consequently shorter or negative Δ).
   The qualitative direction (Δ > 0) should be robust to (a) and (b); (c) is
   reported as a methodological-sensitivity exhibit, not as a competing
   headline.

2. **Constraint-threshold sensitivity.** Re-compute m*(z) on the full 12-point
   grid {2%, 5%, 10%} × {30, 60, 90, 180}-day rolling windows. Median Δ
   should remain in the predicted 18-48 month range across these grid
   points; if it moves by more than ±12 months across the grid, the
   threshold is doing too much work and the result is fragile.

3. **Phantom-risk sensitivity.** Re-run with phantom-risk threshold at
   {1, 2, 3} (headline uses < 2). First-entry concentrations are more
   phantom-exposed than transition concentrations (per the methodology
   refinement); this check is more material here than in Tests 1b/3.

4. **Catchment-permutation placebo.** Permute the catchment label on
   first-entries (keeping window dates fixed) and re-run the full pipeline
   1000 times. The observed median Δ should fall outside the 5th-95th
   percentile of the permuted distribution.

5. **Censoring robustness.** Compare onset rate-ratio magnitudes between
   catchments with observed m*(z) and those right-censored on m*. A
   correlation between first-entry rate-ratio magnitude and probability of
   having a constraint regime by 2025-07 is itself supporting evidence.

### Notes on dependence with other tests

- Test 5 is downstream of Test 1b (first-entry over-dispersion) and Test 3
  (per-window first-entry concentration). Both are established at p < 0.001
  for QLD under the v0.6 unit (`notebooks/06_first_entry_tests.ipynb`). The
  onset definition reuses Test 3's per-window concentration p-values, so the
  two tests are not statistically independent. Test 5 is a *consequence*
  test, not an independent confirmation.
- Test 5 is upstream of any future Claim 4b ("late entrants have lower
  realised revenue than early entrants in a synchronised catchment"), which
  would require project-level revenue data outside the current scope.

### Prerequisites

This test does not run until every item in `docs/test_5_prerequisites.md` is
complete: the transmission-element-to-catchment lookup, `nem-constraints`
schema confirmation, frozen first-entry onsets CSV, pipeline code, analysis
notebook, and reproducibility hooks.

---

## Test 6 — Actor lead-lag relationships (exploratory)

### Hypothesis (less specific than Tests 1-4)

A small subset of named actors systematically precede others' decisions in
synchronised REZs. The leading actors are characterised by larger pipeline,
greater institutional capacity, or established incumbency.

### Operationalisation

Use the `actor_lead_lag_pairs` function in `corporate.py` to enumerate all
pairs of (leader_id, follower_id, event_type, rez) where the follower's
event of the same type within the same REZ occurs within 180 days of the
leader's. Then count appearances of each actor as leader versus follower.

Statistical significance is established by comparison to a null where actor
identities are permuted within event-type/REZ groupings.

### Test statistic

For each actor a, compute the leadership rate L(a) = (times a appears as
leader) / (total a appearances) and compare to the null distribution.

### Prediction

- A subset of approximately 3-5 actors have L(a) > 0.65 (i.e., they lead
  more than they follow) with permutation-test p-value < 0.05.
- The high-L(a) actors are predominantly utilities or large funds (AGL,
  Origin, Squadron, Brookfield, Quinbrook).
- The opposite extreme — actors with L(a) < 0.35 (followers) — are
  predominantly mid-market developers and late-arriving funds.

### Null behaviour

If actor identities are interchangeable (no leadership structure), L(a) is
distributed around 0.5 for all actors.

### Falsification criterion

- No actors with L(a) significantly different from 0.5 would mean no
  detectable leadership structure.
- High-L(a) actors not concentrated among utilities and large funds (e.g.,
  if they are predominantly small developers) would falsify the specific
  prediction about which actor types lead.

### Robustness checks

1. **Event-type sensitivity.** Compute L(a) separately for FID events versus
   commissioning events. Leadership in one but not the other suggests the
   leader role is event-type-specific.

2. **Window sensitivity.** Re-estimate L(a) with 90- and 365-day windows.
   Identity of leading actors should be robust.

3. **Capacity-weighted leadership.** Weight each event by capacity_mw. High-
   L(a) actors may shift identity if leadership is measured in capacity
   rather than event-count.

---

## Test 7 — Cross-REZ spillover (exploratory)

### Hypothesis

A synchronisation event in one REZ produces measurable intensity changes in
adjacent or substitute REZs. Specifically, an exogenous shock to REZ z₁
(e.g., transmission FID, REZ declaration) may produce *positive* spillover
to nearby REZs (substrate-wide attention) or *negative* spillover to
substitute REZs (investor reallocation).

### Operationalisation

Extend the Hawkes specification to include cross-REZ event indicators as
covariates. For REZ z, include indicators of recent Layer A events in
neighbouring REZs.

### Test statistic

Estimated cross-REZ coefficients with standard errors.

### Prediction

- **Positive spillovers** for events in the same jurisdiction (NSW REZ
  declarations have positive cross-effects on other NSW REZs).
- **Mixed or negative spillovers** for events affecting close substitutes
  (e.g., CWO access rights award may reduce intensity in NER if it
  reallocates developer attention).
- Magnitudes of cross-REZ effects are 20-50% of own-REZ effects.

### Null behaviour

Cross-REZ coefficients are zero. Each REZ's investor dynamics are independent
of other REZs.

### Falsification criterion

Either direction would be a finding. The framework does not strongly predict
the sign here; the exploratory nature is acknowledged.

---

## Documentation discipline

For each test:

1. The first analysis of the test is dated and committed before running.
2. The analysis script is committed before the result is interpreted.
3. Any revisions to the test specification are tracked in git history with
   reasoning.
4. The final result is reported regardless of whether it confirms or
   falsifies the prediction.

If any test is *not run* in the eventual write-up, the reason is documented.

---

## What this document is not

- This is not a methodological apology. The predictions are commitments,
  not hedges. Each one is a falsifiable claim.
- This is not a forecast of what will be found. It is a forecast of what
  the framework *predicts* will be found if the framework is correct.
- This is not exhaustive. Subsequent analyses may add tests not in this
  pre-registration. They will be marked as exploratory.

---

*Document version: 0.2 (May 2026). Test 5 (synchronisation onset →
constraint emergence; Claim 4) added under the v0.6 methodology refinement
that established first-entry events as the upstream herding signal. Tests
1-4, 6, 7 unchanged from v0.1. Revision history tracked in git; the
pre-data commitment of predictions for Test 5 is this revision's commit.*
