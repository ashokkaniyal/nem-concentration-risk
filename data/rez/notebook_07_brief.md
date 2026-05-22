# One-page brief — do renewable projects "herd"? (notebook 07, v0.7.3)

*For a statistically-literate reader with no energy-market background. ~1 page. Please read
the "feedback wanted" section at the end — I want the methodology challenged.*

## The question

Australia's eastern power grid (the **National Electricity Market**, NEM) has a public quarterly
register of generation projects, published by the market operator. We track, for ~1,000 projects
over 18 quarters (2020–2025), the quarter in which each project **first appears** at an early
status ("Proposed"/"Anticipated") — its *first-entry*. Each project sits in one of 23
**catchments** (a transmission region; projects in one share the same stretch of grid).
**Question: do first-entries concentrate in particular catchments within particular quarters,
beyond what each catchment's existing pipeline would predict?** That would be consistent with
developer **herding** — piling into the same region at the same time (e.g. after a policy signal).

## Headline result

**Within a quarter, new projects crowd into specific catchments far beyond their baseline share —
combined p ≈ 3.7 × 10⁻¹⁸ across 18 independent quarters. 10 of the 18 quarters are individually
significant at p < 0.05 (uncorrected; the inferential claim is the combined test, not the count).**

What the test does: in each quarter, compare how the new projects split across the 23 catchments
to the split expected if they landed in proportion to each catchment's **exposure** (its existing
project count). A chi-square-type statistic measures the excess concentration, **calibrated by a
multinomial bootstrap** (B = 100,000; large-sample approximations fail at these small counts). It
**conditions on the quarter's total**, so a generally busy quarter creates no signal — only
*disproportionate* crowding does. The 18 quarters are **disjoint project sets**, so their p-values
are independent and Fisher's combination is valid.

**Permutation check.** Randomly reassign each project's catchment label by drawing from exposure
shares (destroying spatial structure, keeping timing). The concentration **vanishes** (combined p
≈ uniform, never < 0.05) — so the signal **reflects genuine spatial structure in the data**, not a
test artefact. (This shows the signal depends on spatial structure — not that the structure is
*herding* specifically; see "What this is NOT".)

## Supporting result (and a correction worth highlighting)

*Which* catchments herd? For each catchment, across quarters, does it capture **more than its
exposure share** when activity is high? After conditioning on each quarter's total, **5 of 21
catchments** show region-specific concentration (CWO, HCC, ILW, MN, NEW).

An earlier version reported **12**. Our verification (permutation) showed the earlier test
conflated a *national surge* (the whole market busy in a quarter) with *region-specific*
concentration. Conditioning on the quarter total separates them: the conditioned test now
**collapses to ~0 under permutation** (the earlier left ~7.7) — confound removed. We present this
as a **strength of the verification process**: found by our own checks and fixed, not buried.
Notably the single largest catchment is *not* a hotspot once you account for market-wide activity.

## What this is NOT

This establishes a **concentration pattern**, not a mechanism. (1) It does **not** show that
concentration *causes* downstream grid congestion — a separate, future analysis. (2) Concentration
is *consistent with* herding but does **not** rule out alternative drivers: resource geography
(the best wind/solar land clusters spatially), large multi-project proponents filing **co-located
portfolios**, or a single policy declaration mechanically generating many registrations at once.
The test measures concentration; **herding is the motivating interpretation, not a proven
mechanism.**

## Honest caveats

- **Exposure-baseline circularity.** The baseline is built from prior first-entries — the *same
  kind of event* being tested. If herding persists across quarters the baseline is itself herded,
  which biases the test (a persistently-herded catchment inflates its own expected share and masks
  its own signal). See feedback point 1.
- **Cross-scale comparisons are not independent.** We also aggregate to 5 corridors and 4 states;
  significance at all scales is partly mechanical (same events re-cut). The genuinely independent
  comparisons are **across quarters** and **across states** (both disjoint projects).
- **Some combined numbers are evidence indices, not probabilities.** Where we combine *per-unit*
  tests, Fisher's independence assumption is violated, so those are relative scores. The headline
  **per-quarter** combined p *is* a true probability (quarters are independent).

## Feedback wanted — please challenge the methodology

1. **Exposure baseline (most important).** We use each catchment's lagged prior-quarter
   first-entry count as the expected share — but that baseline is built from the same kind of event
   we test, so **persistent herding contaminates the null**. Is there a **herding-neutral**
   baseline you'd trust more: installed generation capacity, network transfer capacity, frozen
   pre-2020 counts, or land area?
2. **Bootstrap calibration.** Multinomial (within-quarter) and Poisson (conditioned test);
   B = 100,000. The floor (smallest resolvable p) is 10⁻⁵ *per quarter*; no quarter reached it, so
   every per-quarter p is a genuine point estimate and the 3.7×10⁻¹⁸ headline is their product
   across 18 quarters (not a single floored value). Concerns with the scheme?
3. **Permutation logic.** We permute catchment labels by exposure share, preserving quarter
   totals. Does that isolate the right thing? Is there a stronger permutation?
4. **Conditioning approach.** Expected[catchment, quarter] = (quarter total) × (exposure share).
   Does this correctly remove the national-trend confound, or over/under-correct?

Scripts and full verification: `scripts/verify_v07*.py`, `data/rez/v072_verification_report.md`.
