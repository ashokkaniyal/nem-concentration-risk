# Worked Example: Western Downs

*A retrospective application of the framework to the Western Downs cluster, 2018-2024.*

**Status: STUB.** Section headers, the analysis structure, and the questions
each section will answer are in place. Numerical results, charts, and detailed
discussion are placeholders to be filled in when the analysis runs. The stub
forces commitment to a structure before the analysis, so that the eventual
write-up is disciplined by the structure rather than meandering.

---

## Why Western Downs?

The Western Downs region in southern Queensland is the closest thing the NEM
has to a textbook case of investor synchronisation followed by constraint
emergence. Between approximately 2017 and 2022, a substantial cluster of
large-scale solar and wind projects committed to the corridor — Coopers Gap,
Western Downs Green Power Hub, Wandoan South, Columboola, Kennedy Phase 1,
and others — driven by good resource quality, available land, and proximity
to (then) under-utilised transmission. By 2022-2023 the corridor was
substantially congested, marginal loss factors had degraded for incoming
projects, and curtailment events had become routine. Late entrants found
that the economics that justified their FID had eroded by commissioning.

This trajectory is widely cited in industry commentary as a cautionary tale.
But the question of whether it represents *herding* in any formal sense —
investor decisions clustering beyond what fundamentals alone would explain
— has not been rigorously tested. This worked example applies the framework
to that question.

The choice of Western Downs as the first worked example serves three purposes:

1. It is *retrospective*, allowing comparison of the framework's
   characterisation against known outcomes.
2. It is *Queensland-based*, complementing the New England engagement work
   (which is NSW) and avoiding any IP conflict.
3. It is *well-documented* in trade press and AEMO publications, giving
   richer Layer A and Layer C data than less-covered REZs.

---

## 1. Setting and timeline

This section will document the institutional and physical setting.

To include:

- **Geography and resource quality.** Map of the Western Downs corridor. Notes
  on wind and solar resource availability. Why this corridor was attractive
  initially.
- **Existing infrastructure 2017.** Transmission lines (Wandoan-Tarong-Mt
  England 275 kV corridor), substations, generation already present.
- **Institutional setting 2017-2019.** Pre-REZ formal designation. Queensland
  policy context (Powering Queensland Plan, Queensland Renewable Energy Target).
- **Key institutional changes.** Queensland Energy and Jobs Plan (2022), CIS
  auctions (2023-2024), Queensland LNP election (2024) and subsequent
  policy reviews.

This is essentially the *fundamentals* story: what would have driven any
investor to look at Western Downs in 2017-2019, before any herding effect.
The Hawkes-process residuals after controlling for these fundamentals are
where the framework's claim of synchronisation will be tested.

---

## 2. Investor cohort

This section will document the cohort of named actors and their decision
timing.

To include:

- **Project-level table.** Every grid-scale VRE project in Western Downs from
  2017 to current. Columns: project name, lead developer, technology,
  capacity, FID date, commissioning date, current status.
- **Actor-level summary.** Number of distinct developers, breakdown by actor
  type, capacity distribution.
- **Decision-timing visualisation.** Timeline plot of FID and commissioning
  events, colour-coded by actor.

The visualisation here is doing most of the persuasive work for non-
specialist audiences. If the framework's claim is correct, the timeline
plot should show visible temporal clustering of FID events around specific
policy or environmental shocks.

---

## 3. Layer A event timeline

This section will document the policy events affecting Western Downs and
test whether observed investor clustering aligns with them.

To include:

- **Event list.** All Layer A events relevant to Western Downs from 2017
  forward, drawn from `data/events/policy_events.csv` (Queensland-specific
  events plus federal events with Queensland scope).
- **Event-event overlap.** When did events cluster? Is there a "policy
  wave" structure to the timing?
- **Coupling layer breakdown.** Which events affected the substrate (Layer
  2), versus triggered direct cascades (Layer 1), versus both?

The pre-registered prediction (from `preregistration.md`) is that commitment
events produce the largest effects. The Western Downs case will test
specifically whether the Queensland Energy and Jobs Plan release (2022), the
CIS auction announcements (2023-2024), and the LNP election (2024) produced
the predicted ordering of intensity responses.

---

## 4. Layer B corporate event analysis

This section runs the corporate-event analysis on the Western Downs cohort
specifically.

To include:

- **Actor lead-lag analysis.** Apply `actor_lead_lag_pairs` to Western Downs
  events. Which actors consistently led? Which followed?
- **Event-type distribution over time.** When did pipeline announcements
  versus FIDs versus commissionings cluster?
- **M&A and consolidation events.** Did transactions like
  Squadron-acquires-CWP (2022) affect Western Downs-specific dynamics?

Expected qualitative findings (to be confirmed):

- A small subset of actors (Acen, Lightsource bp, Origin) lead.
- Mid-market developers and incoming funds follow.
- M&A events produce visible Hawkes intensity jumps as new owners
  reassess pipelines.

---

## 5. Layer C information environment

This section quantifies the information environment around Western Downs
over time.

To include:

- **Trade press intensity.** Monthly counts of articles in major trade press
  outlets mentioning Western Downs from 2017 to current. Plot against
  capacity buildout.
- **Conference session counts.** Annual conference sessions referencing
  Western Downs from 2017 to current.
- **AEMO publication frequency.** AEMO documents referencing the corridor
  by quarter.

The framework predicts that information intensity should *rise* with
cumulative buildout, then *plateau or decline* once the constraint situation
became broadly understood (likely 2022-2023). The visual evidence of this
pattern is itself important — it operationalises the hysteresis prediction.

---

## 6. Constraint emergence

This section documents when binding constraints emerged in Western Downs and
links to the related constraint-binding analysis from the `nem-constraints`
repository.

To include:

- **Pre-buildout constraint structure.** Which AEMO constraint equations were
  active in 2017 and how often did they bind? (Likely: very few, rarely.)
- **Constraint equation additions.** When did AEMO add Western Downs-specific
  constraint equations? Cross-reference with capacity buildout.
- **Binding frequency over time.** Using the framework from the
  `nem-constraints/analysis/stwf1_*` scripts, characterise binding
  frequency for Western Downs constraints over 2018-2024.
- **MLF history.** Marginal loss factor history for Western Downs projects.
  When did MLF degrade most sharply?

The story this section should tell, if the framework is correct: investor
synchronisation in 2019-2021 produced a buildout trajectory that AEMO's
constraint formulation could not accommodate; binding frequency rose sharply
in 2022-2023; MLF degradation followed with a lag.

---

## 7. Hawkes regression results

This section runs the central methodology on the Western Downs data and
reports results in the format committed in `preregistration.md`.

For each pre-registered test:

- **Test 1 (synchronisation existence):** estimated α, τ, with confidence
  intervals; comparison to Poisson null.
- **Test 2 (policy events as exogenous shocks):** estimated β coefficients
  for Layer A event types; comparison to predicted ordering.
- **Test 3 (Layer 2 amplification):** estimated γ and δ coefficients;
  Granger-style tests on Layer C causation.
- **Test 4 (regime persistence and hysteresis):** estimated α as a function
  of cumulative capacity; non-parametric estimates by buildout stage.

Robustness checks per the pre-registration follow each result.

---

## 8. Interpretation

This section synthesises the quantitative results into a narrative.

To include:

- **Did the framework's predictions hold?** Test by test.
- **Where the framework departed from prediction.** Honest reporting of
  what did not match expectations.
- **What the results say about Western Downs specifically.** Was the buildout
  synchronisation pattern severe? Moderate? When could it have been
  identified ex ante?
- **What the results say about the framework's generality.** Is Western
  Downs typical of NEM REZs in synchronisation magnitude, or an extreme case?

The interpretation must be disciplined by the pre-registration. Results
that match predictions get reported as confirmations; results that diverge
get reported as falsifications or partial-falsifications; results that
suggest framework extensions are reported as findings that motivate future
work, not retrofitted as predictions.

---

## 9. Lessons and limitations

This section addresses what Western Downs as a case study can and cannot
establish.

To include:

- **What is generalisable.** Patterns likely to recur in similar REZs.
- **What is Western Downs-specific.** Factors that may not apply elsewhere
  (Queensland-specific policy context, particular actor cohort, specific
  resource quality).
- **What the framework cannot say.** Counterfactual scenarios (what would
  have happened with different policy), individual investment outcomes
  (which projects within the synchronised cohort fared best or worst).
- **Implications for the New England REZ comparison.** Without using any
  proponent-confidential information, what does the Western Downs analysis
  suggest about how to think about New England's trajectory?

The last bullet is potentially the most commercially valuable section. It
must be carefully drafted so that nothing in the discussion uses
proponent-confidential information, but the substantive conclusions remain
useful to a thoughtful reader who is themselves working in or around the
New England engagement.

---

## 10. Methodology notes specific to this case

This section documents methodological choices specific to Western Downs.

To include:

- **REZ boundary definition.** Western Downs is not formally a designated
  REZ under the Queensland framework (it's been incorporated into the
  Southern Queensland REZ). Boundary choices used here.
- **Project tagging.** How projects were tagged to Western Downs versus
  other Queensland regions.
- **Data gaps.** Periods where Layer A or Layer C data is sparse and how
  this affects interpretation.
- **Comparison set.** Which other regions (Tarrone? Broken Hill? Coopers
  Gap pre-cluster?) serve as comparison cases.

---

## 11. Data and code availability

All data and code used to produce the analysis in this document are in this
repository (`nem-concentration-risk`) under versions tagged at the time of
analysis. The specific commit hash that produced each chart and table is
referenced inline.

External data dependencies:

- AEMO Generator Information register, quarterly releases 2017-current
- AEMO MMS dispatch and constraint data (from the related
  `nem-constraints` repository)
- Public ASX disclosures for listed actors involved
- Public corporate media releases for unlisted actors involved
- Trade press as documented in `data/info_environment/`
- Conference programmes as documented in `data/info_environment/`

A reader with access to these sources should be able to reproduce every
result in this document.

---

## 12. Acknowledgements and disclosures

This worked example uses only public data. No proponent-confidential
information is used.

The author has an active consulting engagement with a developer working on
the New England REZ. The choice of Western Downs as the worked example
(rather than New England) is partly to maintain this separation. Any
discussion of New England in this document is restricted to inferences
drawn from public data and from the Western Downs analysis.

---

*Document version: 0.0 (stub, May 2026). Section structure committed; numerical
results to be added when analysis runs. Estimated time to complete the
analysis and write-up: 4-6 focused weeks after data collection is complete.*
