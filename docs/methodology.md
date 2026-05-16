# Methodology

*A Kuramoto-type framework for empirical analysis of investor synchronisation in NEM VRE buildout.*

This document specifies the theoretical framework, the empirical strategy, and the
specific tests the framework will run. It is the foundational reference for all
analysis in this repository. Other documents (`literature.md`, `preregistration.md`,
worked examples) reference and extend the structure laid out here.

---

## 1. Motivation and research question

The buildout of variable renewable energy (VRE) generation in Australia's National
Electricity Market (NEM) has displayed pronounced spatial and temporal concentration.
Specific Renewable Energy Zones (REZs) have attracted disproportionate investment over
short time windows, followed by sharp deterioration in marginal economics as
constraint regimes shift to accommodate the cluster. The pattern is well-documented
in the Western Downs cluster in Queensland (where transmission constraints emerged
faster than buildout, eroding revenue for late entrants), the Tarrone area in
Victoria, and the Broken Hill / Far West NSW area. It is widely anticipated that
the New England REZ in NSW may follow a similar trajectory.

Industry commentary characterises this as "herding": investors are alleged to imitate
each other's siting decisions rather than acting on independent assessments of
fundamentals. The claim is plausible but rarely tested rigorously. Existing studies
either describe the concentration pattern without identifying its mechanism, or
attribute it to specific exogenous causes (REZ declarations, network availability,
policy targets) without testing whether the residual clustering exceeds what those
exogenous causes alone would explain.

This framework proposes a more rigorous empirical approach. It asks:

**Can the observed temporal and spatial clustering of VRE investment decisions in
the NEM be characterised as a Kuramoto-type synchronisation phenomenon — that is, a
phase transition from independent to coupled investment behaviour, driven by
quantifiable changes in the strength of investor-to-investor coupling? And if so,
what does this imply for the trajectory of constraint emergence and the risk
profile of late entrants?**

The framework's intended outputs are:

1. A defensible empirical characterisation of investor synchronisation in NEM REZs.
2. Identification of the *mechanism* of coupling: direct observation of others'
   actions, shared information substrate, or both.
3. Testable predictions about how synchronisation propagates and dissipates.
4. Applications to risk assessment, policy design, and investment timing.

The framework is built from public data only, so its outputs are independently
reproducible. Where the framework departs from established methods, the departures
are explicit and motivated.

---

## 2. Theoretical framework

### 2.1 Background: the Kuramoto model

The Kuramoto model describes a population of *N* coupled oscillators, each with its
own natural frequency. The phase of the *i*-th oscillator evolves according to:

```
dθᵢ/dt = ωᵢ + (K/N) Σⱼ sin(θⱼ − θᵢ)
```

where:

- θᵢ is the phase of oscillator *i*
- ωᵢ is its natural frequency (drawn from some distribution with width σ)
- K is the coupling strength

A central result (Kuramoto, 1975; Strogatz, 2000) is that the system undergoes a
*phase transition* at a critical coupling strength K_c that depends on σ. Below K_c
the population is incoherent — each oscillator's phase evolves approximately
independently. Above K_c a *synchronised cluster* emerges: a macroscopic fraction
of the oscillators lock to a common frequency. The transition is sharp in the
thermodynamic limit and has been observed in many physical and biological systems
(circadian rhythms, flashing fireflies, neural ensembles, applauding crowds).

The order parameter:

```
r·e^(iψ) = (1/N) Σⱼ e^(iθⱼ)
```

quantifies the degree of synchronisation: r=0 means incoherent, r=1 means perfect
synchrony. The transition manifests as r jumping from ~0 to a positive value at
K = K_c.

### 2.2 Application to power systems

The Kuramoto framework was extended to power systems by Dörfler and Bullo (2014)
and earlier authors. Under standard simplifications (lossless transmission lines,
constant voltage magnitudes, fast-timescale dynamics ignored), the swing equation
for a synchronous generator's rotor angle reduces exactly to a Kuramoto-type
equation on the network graph:

```
dδᵢ/dt = ωᵢ − (1/Mᵢ) Σⱼ Bᵢⱼ VᵢVⱼ sin(δᵢ − δⱼ)
```

This mathematical equivalence means that the substantial body of synchronisation
theory developed for Kuramoto systems applies, mutatis mutandis, to the network of
synchronous machines. Critical phenomena like transient stability boundaries,
cascading desynchronisation events, and the role of network topology in determining
synchronisation robustness can all be analysed using the Kuramoto-derived toolkit.

This framework draws on that mathematical apparatus but applies it to a different
class of system: the network of *investors* whose decisions about whether and when
to commit to projects in a given REZ collectively determine the buildout trajectory
of that zone.

### 2.3 Investors as coupled oscillators

We map the investor-decision problem to Kuramoto as follows.

**Oscillators.** Each investor *i* (developer, fund, utility) has a "phase" θᵢ(t)
that represents their position in the decision cycle for a given REZ. The phase is
operationalised through observable events: connection enquiry submission (entry
into the cycle), financial close (commitment), commissioning (completion). An
investor's phase advances over time as they progress through this cycle.

**Natural frequencies.** Each investor has an intrinsic pace ωᵢ at which they would
progress through investment decisions in the absence of coupling — driven by their
capital availability, organisational capacity, internal risk appetite, and private
view of the zone's fundamentals. The distribution of ωᵢ across investors has width
σ, reflecting the heterogeneity of investor types and circumstances.

**Coupling.** Investors influence each other's decisions through two distinct
mechanisms (see Section 2.4). The coupling strength K reflects the aggregate
intensity of these mechanisms. Crucially, K is not constant — it varies over time
and across REZs.

**Synchronisation.** When K > K_c (where K_c depends on σ), investor decisions
become temporally clustered: they "lock" to similar timing rather than spreading
out according to their natural frequencies. This is the empirical herding pattern.
When K < K_c, decisions remain approximately independent, and the buildout
trajectory looks like a Poisson process driven by exogenous shocks.

### 2.4 The two-layer coupling model

A distinctive feature of this framework — and a refinement of standard Kuramoto —
is the recognition that investor coupling operates through two structurally
different mechanisms.

**Layer 1: Direct observation.** Investor *i* observes investor *j*'s actions
directly: *j* submits a connection enquiry, achieves financial close, or commissions
a project, and *i* updates their own decision based on *j*'s observed behaviour.
This is the standard "information cascade" mechanism of Banerjee (1992) and
Bikhchandani-Hirshleifer-Welch (1992). The coupling is *dyadic* and bounded by the
number of observable peers.

**Layer 2: Shared information substrate.** Investors *i* and *j* both consume the
same information sources — AEMO publications, TNSP annual planning reports, trade
press (RenewEconomy, AFR, Energy Source & Distribution), consultancy reports
(Cornwall Insight, Aurora, Edge2020), conference proceedings, broker research.
Their private signals about the zone are *correlated* because they're drawn from a
common substrate. This is "informational synchronisation" in the sense of
Hirshleifer and Teoh (2003). The coupling operates *one-to-many* through the
information channel rather than pairwise.

Both layers produce Kuramoto-like synchronisation. The mathematical structure is
essentially identical at first order. But the *drivers* of K differ between layers,
and so do the *policy implications* of dominance by one layer or the other.

#### Information environment as time-varying K

Layer 2 coupling strength depends on the density of the information substrate.
When AEMO releases an ISP, when a REZ is declared, when trade press intensifies
coverage of a corridor, the substrate becomes denser and Layer 2 coupling rises.

In Kuramoto terms, this means K is not a constant but a function of time and of
the information environment. We write:

```
K(t, z) = K_1(t, z) + K_2(t, z) · I(t, z)
```

where K_1 captures Layer 1 (direct) coupling, K_2 the responsiveness to information
substrate, and I(t, z) is a measure of information environment intensity for REZ z
at time t. I(t, z) is operationalised through trade press article counts, AEMO
publication frequency, conference session counts, and similar proxies (see Section
3.4).

#### Endogenous feedback

A subtler dynamic: I(t, z) itself depends on the level of buildout activity in REZ
z. When investors synchronise on a zone, more analysts cover it, more conferences
discuss it, more reports examine it. The information substrate thickens *because*
the herd is synchronised, which *further increases* Layer 2 coupling, which deepens
synchronisation.

This is K with positive feedback on the order parameter:

```
K(t, z) = K_1(t, z) + K_2(t, z) · I(t, z, r(t, z))
```

where r(t, z) is the synchronisation order parameter (Section 2.5).

Standard Kuramoto assumes constant K. The feedback structure here produces
*hysteresis*: once a zone is synchronised, it is harder to desynchronise than the
original K_c threshold would suggest, because the information density locking it
in is sustained by the synchronisation itself. This is the structural pathology
behind the Western Downs over-buildout: the herd kept synchronising past the point
where marginal economics no longer supported new entry, because the information
substrate was self-reinforcing.

### 2.5 The order parameter for investor systems

The Kuramoto order parameter r ∈ [0, 1] measures the degree of phase coherence
among the oscillators. For an investor system, we operationalise r through
*temporal clustering of decisions*:

```
r(t, z, Δ) = 1 − (entropy of decision times in window [t−Δ, t+Δ]) / (max entropy)
```

where decision times are FID dates, commissioning dates, or connection enquiry
submission dates for projects in REZ z. r ≈ 0 means decisions are uniformly
distributed in time (incoherent); r ≈ 1 means decisions cluster in narrow time
windows (synchronised).

More formally, the temporal clustering is tested via Hawkes-process estimation,
which gives both a parametric model and a goodness-of-fit framework (Section 3.3).

---

## 3. Empirical strategy

The empirical work proceeds in five sequential layers, each building on the
previous.

### 3.1 Data infrastructure (three layers)

The framework's data foundation is the three-layer information taxonomy described
in the README and implemented in the repository.

**Layer A** — Policy events: discrete announcements from institutional actors,
treated as exogenous shocks. Tracked in `data/events/policy_events.csv`.

**Layer B** — Corporate events: dated actions by named private actors (FIDs,
commissionings, M&A, capital raises), treated as the endogenous point process being
modelled. Tracked in `data/events/corporate_events.csv` with actor metadata in
`data/actors.csv`.

**Layer C** — Information environment: continuous-ish measures of substrate density
(trade press counts, conference sessions, AEMO publication frequency). Tracked in
`data/info_environment/`.

The collection methodology for each layer is documented in
`notebooks/02_data_collection_guide.ipynb`. The verification regime for ensuring
primary-source provenance is documented in the same notebook and enforced by the
`confidence` column in each register.

### 3.2 Outcome variables

The principal outcome variables are *event rates per REZ over time*. Specifically:

- **Connection enquiry rate** λ_e(t, z): new connection enquiries per month for
  REZ z. Captures the earliest signal of investor intent.
- **Financial close rate** λ_f(t, z): projects reaching FID per quarter for REZ z.
  Captures commitment.
- **Commissioning rate** λ_c(t, z): projects energising per quarter for REZ z.
  Captures completion.

Each rate is a stochastic point process. Under the null hypothesis of independent
investor decisions, each rate is a non-homogeneous Poisson process driven by
exogenous shocks (Layer A events) and any persistent macroeconomic factors. Under
the alternative hypothesis of synchronised behaviour, each rate is a *self-exciting*
point process: prior events within REZ z make subsequent events more likely than
the Poisson model predicts.

### 3.3 Hawkes process specification

We model each event rate as a Hawkes process with exogenous covariates:

```
λ(t, z) = μ(t, z) + Σⱼ:tⱼ<t α · g(t − tⱼ) + β · X(t, z)
```

where:

- μ(t, z) is the baseline intensity (slow-varying background rate)
- {tⱼ} are previous events of the same type within REZ z
- α is the self-excitation amplitude (the key parameter — captures Layer 1 coupling)
- g(·) is a decay kernel, typically exponential: g(s) = exp(−s/τ)
- τ is the decay timescale
- X(t, z) is a vector of exogenous covariates (Layer A event indicators, Layer C
  intensity measures)
- β is a vector of covariate coefficients

The framework's central empirical claims map directly to parameter estimates:

| Claim | Parameter | Interpretation |
|---|---|---|
| Herding exists | α > 0 | Investor decisions self-excite |
| Herding has finite memory | τ is small | Past events fade after time τ |
| Policy events matter | β_policy > 0 | Layer A shocks shift intensity |
| Layer 2 matters | β_info > 0 | Information density shifts intensity |
| Layer 2 amplifies Layer A | β_interaction > 0 | Info × policy interaction |
| Hysteresis | α grows with cumulative events | Coupling self-reinforces |

Estimation is by maximum likelihood, with standard errors from the inverse Fisher
information. The `tick` Python library provides production-grade Hawkes estimators
with regularisation (necessary when the number of covariates is large relative to
the number of events). We use exponential kernels in v1 for tractability and
interpretability; power-law kernels (Hardiman et al. 2013) are a v2 robustness
check.

#### Why Hawkes rather than ARIMA, panel regression, or hazard models

Hawkes processes are specifically designed for *self-exciting point processes* —
discrete events whose occurrence increases the probability of similar subsequent
events. They are widely used in financial econometrics for studying contagion,
order-book dynamics, and trading clusters. They are the right tool here for three
reasons:

1. **Decisions are discrete events, not continuous flows.** ARIMA on monthly
   commissioning counts loses the timing information that distinguishes "five
   commissionings spread over the month" from "five commissionings in one week."
2. **Self-excitation is the explicit hypothesis.** Hawkes parameters directly
   represent the coupling strength K in the Kuramoto framework. Other point-process
   models (e.g., renewal processes) don't capture this naturally.
3. **The decay kernel encodes memory.** The parameter τ tells us how long the
   herding effect persists — a quantity of direct interest, not a nuisance.

Where panel regression and hazard models are appropriate is for cross-sectional
questions (which projects within a synchronised zone succeed) — these are
complementary, not competing, methods. v2 of the framework will likely incorporate
panel methods for project-level outcomes.

### 3.4 The four central tests

The framework's empirical contribution rests on four pre-registered tests. Each is
spelled out in `preregistration.md` with predicted direction, magnitude, and the
falsification criterion. Briefly:

**Test 1 — Synchronisation existence.** Fit the Hawkes specification with α and τ
unconstrained. Predict α > 0 in synchronised zones and α ≈ 0 in unsynchronised
zones, with τ in the range 6–24 months. Falsified if α is not statistically
distinguishable from zero in zones with apparent clustering.

**Test 2 — Policy events as exogenous shocks.** Estimate β for indicator variables
of Layer A event types (commitment, information, competitive, adverse). Predict
β_commitment > β_information > β_competitive (in magnitude). Falsified if
information events produce larger responses than commitment events (would suggest
Layer 2 dominance from the start, refining rather than supporting the original
hypothesis).

**Test 3 — Layer 2 (information environment) as time-varying coupling.** Include
Layer C intensity I(t, z) as a covariate. Predict β_I > 0 and significant
interaction with Layer A event indicators. Falsified if information environment
shows no measurable effect after controlling for policy events.

**Test 4 — Regime persistence and hysteresis.** Estimate α as a function of
cumulative committed capacity in the zone. Predict α(cumulative) rises with
cumulative buildout (positive feedback), then plateaus or declines at saturation.
Falsified if α is constant across buildout stages.

A fifth, exploratory test concerns *actor lead-lag relationships*: do specific
named actors (Origin, AGL, Squadron, Brookfield) systematically precede others'
decisions in synchronised zones? This is more descriptive than testing a specific
prediction, but the results have direct application to investment timing strategy.

### 3.5 Identification and confounding

Three confounding mechanisms could produce apparent synchronisation without
genuine investor coupling:

**Common shocks.** All investors respond to the same exogenous events (REZ
declarations, ISP releases, policy changes). The framework addresses this by
explicitly modelling Layer A events as covariates; α captures synchronisation
*beyond* what the common-shocks explanation predicts.

**Common fundamentals.** All investors observe the same underlying fundamentals
(transmission capacity, resource quality) and respond similarly. The framework
addresses this through the REZ-as-fixed-effect structure: synchronisation is
estimated within-REZ, and fundamentals are roughly constant within-REZ during the
observation window.

**Reverse causation.** Synchronisation could drive information environment changes
rather than the reverse, contaminating Test 3. The framework addresses this through
lag structure: I(t, z) is included with a multi-month lead, so contemporaneous
feedback is controlled for, and Granger-style tests on the lead-lag direction are
run as robustness checks.

Residual unobserved confounding cannot be ruled out from observational data alone.
The framework is honest about this: results are characterised as "consistent with
the synchronisation hypothesis" rather than "proof of synchronisation." A
randomised intervention is, of course, infeasible.

### 3.6 What the framework does not claim

To avoid over-selling, several limitations are explicit:

- **The framework characterises past patterns; it does not directly forecast.**
  Forward use requires structural assumptions about how parameters evolve as new
  buildout occurs, and these assumptions are not yet validated.
- **The framework is REZ-level, not project-level.** It tells you which zones are
  synchronising and which mechanisms dominate; it does not tell you which specific
  projects within a synchronised zone will succeed or fail.
- **The framework is silent on policy desirability.** Whether synchronised buildout
  is good or bad depends on social welfare functions, not just empirical
  characterisation. Synchronisation in early-stage REZs may accelerate beneficial
  scale; synchronisation in saturated REZs may produce malinvestment.
- **The framework does not replace power-systems engineering models.** It is
  complementary: it characterises *investor behaviour*; the operational
  consequences (constraint emergence, MLF degradation, voltage stability) still
  require AC OPF and dynamic simulation tools to model.

---

## 4. Application to specific questions

The framework's principal applications:

**Investment risk assessment.** Given a REZ at some stage of buildout, what does
the synchronisation analysis say about the likelihood that further investment will
encounter the Western-Downs-style trajectory of late entrants facing constraint
emergence and MLF degradation? Operationalised via estimated α, τ, and the position
of cumulative capacity on the α(cumulative) curve.

**Policy timing.** Given the framework's identification of which event types
produce the largest synchronisation responses, when should policy makers release
which signals? An ISP release into a saturated zone amplifies synchronisation in
that zone — possibly undesirable. An ISP release into a zone at early buildout may
catalyse beneficial coordination — possibly desirable. The framework helps make
these judgements quantitative rather than rhetorical.

**Constraint forecasting.** Synchronised buildout drives the emergence of binding
constraints (the connection to the stwf1 work in the related `nem-constraints`
repository). The framework provides a leading indicator: when a zone enters the
synchronised regime, expect constraints to follow with a lag determined by
commissioning timelines plus AEMO's constraint-formulation cadence.

**Competitive intelligence.** The actor lead-lag analysis (Section 3.4) identifies
which actors systematically lead the herd. For a developer deciding when to enter
a new REZ, this is direct strategic information.

---

## 5. Relationship to existing methodology

This framework is novel as a synthesis but builds on several established methods.
See `literature.md` for full discussion. Briefly:

- Hawkes processes have been used to study herding in financial markets (Hardiman
  et al. 2013; Aït-Sahalia et al. 2015). The novel application here is to physical
  asset investment timing rather than financial transactions.
- The Kuramoto framework has been applied to economic and social systems
  (Sornette 2003 on financial markets; Niebuhr et al. 2009 on opinion dynamics).
  The application to renewable energy investment is, as far as I can determine, new.
- Empirical herding tests in the spirit of Lakonishok-Shleifer-Vishny (1992) and
  Sias (2004) have been applied to stock-trading data extensively but rarely to
  physical investment decisions in energy.
- The connection between investor synchronisation and grid synchronisation
  phenomena is, as far as I can determine, original to this framework.

Where this framework departs from established methods, the departures are:

1. The **two-layer coupling model** (Section 2.4) is a refinement of the standard
   Kuramoto specification. It is necessary to distinguish direct from informational
   coupling in social systems.
2. The **K(t, z) with feedback on r(t, z)** structure (Section 2.4) captures
   hysteresis. Standard Kuramoto with constant K cannot.
3. The **explicit linkage to constraint emergence** through the related
   constraint-binding analysis is an integration across what are usually separate
   research domains (investor behaviour and power systems engineering).

---

## 6. Version 1 scope and version 2 deferral

To prevent scope creep, v1 of the framework commits to:

**In scope for v1:**
- Three-layer data infrastructure for NSW and QLD REZs, 2019–2025
- Hawkes regression with exponential kernels, Layer A covariates, Layer C
  multiplier, and self-excitation
- The four central tests in Section 3.4 plus the lead-lag exploration
- A single worked example (Western Downs) demonstrating the full pipeline
- Public release of methodology, data, and code via GitHub

**Deferred to v2:**
- Victoria, South Australia, and Tasmania (different REZ frameworks)
- Power-law and non-parametric Hawkes kernels
- Marked Hawkes processes (capacity-weighted events rather than equal-weight)
- Network-Hawkes processes capturing cross-REZ spillovers
- Forward-looking application (forecasting next-zone synchronisation)
- Project-level outcome analysis (which projects within synchronised zones succeed)

The v1 scope is sized for one focused researcher working part-time over roughly
12 months, with the goal of a defensible methodology note plus the worked example
in months 1-6, and a peer-reviewable paper or substantive whitepaper in months
6-12. v2 directions are options to be evaluated based on v1 reception, not
commitments.

---

## 7. Data provenance and reproducibility

All data used in this framework is public. The data registers are versioned in
this repository. Verification provenance is tracked at row-level via the
`confidence` and `source_url` columns.

Reproducibility commitments:

- Every analysis runs from the data in this repository plus public sources
  cited in registers.
- Code is in `src/nem_herding/` with explicit dependencies in `pyproject.toml`.
- Random seeds are pinned in all stochastic analyses (Hawkes simulation,
  bootstrap robustness checks).
- Pre-registration commitments (in `preregistration.md`) are dated and
  versioned in git history.

The framework is built to be auditable. A skeptical reader should be able to
reproduce every result, verify every event in the registers against its primary
source, and challenge every methodological choice with reference to the
documented reasoning.

---

## 8. Glossary

- **Coupling strength (K)** — Kuramoto parameter representing the intensity of
  interaction between oscillators. In this framework: the intensity of mutual
  influence among investor decisions.
- **Hawkes process** — A self-exciting point process where past events increase
  the probability of future events.
- **Layer A / B / C** — The three-layer information taxonomy of this framework.
  See README and Section 3.1.
- **Order parameter (r)** — Measure of synchronisation, r ∈ [0, 1]. r ≈ 0 is
  incoherent, r ≈ 1 is perfectly synchronised.
- **REZ** — Renewable Energy Zone, as defined in each state's planning framework.
- **Synchronisation threshold (K_c)** — Critical coupling strength above which
  synchronisation emerges. Depends on heterogeneity σ.
- **VRE** — Variable Renewable Energy (wind, solar).

---

## References

Detailed literature engagement is in `literature.md`. The principal references
for this methodology are:

- Aït-Sahalia, Y., Cacho-Diaz, J., & Laeven, R. J. A. (2015). Modeling financial
  contagion using mutually exciting jump processes. *Journal of Financial
  Economics*, 117(3), 585-606.
- Banerjee, A. V. (1992). A simple model of herd behavior. *Quarterly Journal of
  Economics*, 107(3), 797-817.
- Bikhchandani, S., Hirshleifer, D., & Welch, I. (1992). A theory of fads,
  fashion, custom, and cultural change as informational cascades. *Journal of
  Political Economy*, 100(5), 992-1026.
- Dörfler, F., & Bullo, F. (2014). Synchronization in complex networks of phase
  oscillators: A survey. *Automatica*, 50(6), 1539-1564.
- Hardiman, S. J., Bercot, N., & Bouchaud, J.-P. (2013). Critical reflexivity in
  financial markets: a Hawkes process analysis. *European Physical Journal B*,
  86(10), 442.
- Hirshleifer, D., & Teoh, S. H. (2003). Herd behaviour and cascading in capital
  markets: a review and synthesis. *European Financial Management*, 9(1), 25-66.
- Kuramoto, Y. (1975). Self-entrainment of a population of coupled non-linear
  oscillators. In *International Symposium on Mathematical Problems in
  Theoretical Physics*, 420-422.
- Lakonishok, J., Shleifer, A., & Vishny, R. W. (1992). The impact of
  institutional trading on stock prices. *Journal of Financial Economics*, 32(1),
  23-43.
- Sias, R. W. (2004). Institutional herding. *Review of Financial Studies*, 17(1),
  165-206.
- Sornette, D. (2003). *Why Stock Markets Crash: Critical Events in Complex
  Financial Systems*. Princeton University Press.
- Strogatz, S. H. (2000). From Kuramoto to Crawford: exploring the onset of
  synchronization in populations of coupled oscillators. *Physica D*, 143(1-4),
  1-20.

---

*Document version: 0.1 (draft, May 2026). Subsequent versions will incorporate
feedback from initial worked-example analysis, peer review, and methodological
refinements. Version history is tracked in git.*
