# Literature Engagement

*Where this framework sits in the existing scholarly literature.*

This document is the framework's positioning relative to four bodies of work:
(1) financial econometrics on investor herding, (2) network economics of
information cascades, (3) dynamical systems and Kuramoto synchronisation theory,
and (4) power systems engineering on REZ planning and constraint formulation.

For each literature, the document identifies the foundational and current
references, summarises what they establish, identifies what they leave open,
and explains where this framework draws on them and where it departs.

The literature engagement is honest about the framework's contribution: most of
the constituent methods exist. The novelty is in the *synthesis* — specifically,
applying Kuramoto-type synchronisation analysis to investor behaviour in physical
asset investment, with explicit attention to the two-layer coupling structure
that distinguishes social from physical systems.

---

## 1. Financial econometrics on investor herding

### Foundational work

The modern econometric literature on herding begins with two near-simultaneous
1992 papers:

**Banerjee, A. V. (1992).** *A simple model of herd behavior.* QJE 107(3),
797-817. Banerjee shows that even rational Bayesian agents will rationally
imitate each other's actions in sequential decision settings, producing
information cascades that can be inefficient. The contribution is the
demonstration that herding need not require irrationality — observation-based
herding is consistent with full rationality given the information structure.

**Bikhchandani, S., Hirshleifer, D., & Welch, I. (1992).** *A theory of fads,
fashion, custom, and cultural change as informational cascades.* JPE 100(5),
992-1026. Develops the information-cascade model in parallel with Banerjee.
Shows that cascades are *fragile* — small changes in public information can
reverse them entirely. This is the theoretical basis for why synchronised
investment patterns can dissipate abruptly when conditions change.

Both papers establish what this framework calls Layer 1 coupling: direct
observation of others' actions producing imitation.

### Empirical methodology

**Lakonishok, J., Shleifer, A., & Vishny, R. W. (1992).** *The impact of
institutional trading on stock prices.* JFE 32(1), 23-43. Introduces the
"LSV measure" of herding — a now-standard cross-sectional measure that
tests whether institutional investors trade on the same side of the market
more often than would be expected by chance. Used extensively in equity
research; underused in physical-investment contexts.

**Sias, R. W. (2004).** *Institutional herding.* RFS 17(1), 165-206. Refines
the LSV measure and provides cleaner identification of herding versus correlated
trading on common signals. Distinguishes "investigative herding" (acting on
genuine information) from "spurious herding" (acting on noise that's correlated
across investors).

**Wermers, R. (1999).** *Mutual fund herding and the impact on stock prices.*
Journal of Finance 54(2), 581-622. Empirical evidence on mutual fund herding,
with attention to the question of whether herding has price effects (it does,
but modestly).

### Recent developments

**Hirshleifer, D., & Teoh, S. H. (2003).** *Herd behaviour and cascading in
capital markets: a review and synthesis.* European Financial Management 9(1),
25-66. Survey article that introduces the distinction this framework formalises
as Layer 1 versus Layer 2 coupling: between herding via observation of others'
actions and herding via shared information sources. This is the closest
prior conceptualisation to the two-layer model used here, although Hirshleifer
& Teoh do not develop it into a formal model.

**Aït-Sahalia, Y., Cacho-Diaz, J., & Laeven, R. J. A. (2015).** *Modeling
financial contagion using mutually exciting jump processes.* JFE 117(3),
585-606. Introduces Hawkes-process methodology for studying contagion across
financial markets. Methodologically influential for this framework's choice of
Hawkes specification.

**Hardiman, S. J., Bercot, N., & Bouchaud, J.-P. (2013).** *Critical reflexivity
in financial markets: a Hawkes process analysis.* European Physical Journal B
86(10), 442. Estimates Hawkes parameters for high-frequency equity data and
finds the self-excitation amplitude α very close to 1 — near-critical, suggesting
financial markets operate near a synchronisation threshold. The closeness to
criticality is suggestive for renewable energy markets too: REZs in late buildout
may approach a similar near-critical regime.

### What this literature establishes

Three key results:

1. **Herding is mathematically tractable and empirically detectable.** It is
   not just a metaphor; it is a phenomenon with falsifiable predictions.
2. **Information cascades can be rational.** Observed clustering does not
   imply investor irrationality.
3. **Hawkes processes are the right tool** for studying self-excitation in
   point-process data. The empirical literature on financial market contagion
   has converged on this methodology.

### What this literature leaves open

For our purposes, three gaps:

1. **Almost all empirical herding work uses financial-market data** — stock
   trading, fund flows, IPO subscriptions. Applications to physical asset
   investment are rare. The few that exist (Calvet et al. on corporate
   investment; Bernheim on real estate) do not use Hawkes methodology or
   address the multi-year timescales of energy infrastructure.
2. **The Layer 1 / Layer 2 distinction** is acknowledged informally
   (Hirshleifer & Teoh) but not formally separated in econometric models.
3. **The connection to network and dynamical-systems perspectives** is
   underdeveloped. Sornette (below) is an exception but is from the physics
   side rather than the econometrics side.

### Where this framework sits

The framework adopts the Hawkes methodology from the financial-contagion
literature (Aït-Sahalia et al.; Hardiman et al.). It applies the methodology
to a context — VRE investment timing in physical REZs over multi-year horizons
— where it has not been applied. The two-layer specification operationalises
the Hirshleifer-Teoh distinction in a way that the econometric literature has
not previously done formally.

---

## 2. Network economics of information cascades

### Foundational work

**Bala, V., & Goyal, S. (1998).** *Learning from neighbours.* Review of
Economic Studies 65(3), 595-621. Models social learning on a network: agents
observe only their neighbours, not the whole population. Establishes that
network topology affects the speed and accuracy of learning. Foundational for
thinking about Layer 1 coupling as taking place over a non-complete graph.

**DeMarzo, P. M., Vayanos, D., & Zwiebel, J. (2003).** *Persuasion bias, social
influence, and unidimensional opinions.* QJE 118(3), 909-968. Shows that agents
in social networks often fail to fully account for repeated information when
updating beliefs, producing "persuasion bias" — the over-weighting of frequently
repeated information. Directly applicable to the Layer 2 dynamics of this
framework: investors reading the same trade press and AEMO publications can
over-weight repeated signals.

### Recent developments

**Acemoglu, D., Dahleh, M. A., Lobel, I., & Ozdaglar, A. (2011).** *Bayesian
learning in social networks.* Review of Economic Studies 78(4), 1201-1236.
Establishes conditions under which observation of neighbours' actions in a
network leads to asymptotic learning of the true state. Key result: learning
can fail if the network has "information bottlenecks" — a few agents whose
actions are widely observed and who themselves have limited information.
Implication for our context: developers whose actions are widely observed
(major utilities, large funds) can produce inefficient herding if their own
information is incomplete.

**Golub, B., & Jackson, M. O. (2010).** *Naïve learning in social networks and
the wisdom of crowds.* American Economic Journal: Microeconomics 2(1), 112-149.
Conditions under which simple averaging of neighbours' beliefs converges to
truth. Relevant because investor-decision systems are likely closer to "naïve
learning" than fully Bayesian — heuristics, rules of thumb, mental models
dominate.

**Acemoglu, D., & Ozdaglar, A. (2011).** *Opinion dynamics and learning in
social networks.* Dynamic Games and Applications 1(1), 3-49. Survey article.
Good entry point to the formal literature.

### What this literature establishes

1. **Network topology shapes learning outcomes.** Sparse and clustered
   networks can produce different convergence behaviour from complete or
   random networks.
2. **Naïve learning is often a good approximation** to actual social learning,
   suggesting Bayesian-optimality assumptions are not essential.
3. **Information bottlenecks** (agents whose actions are widely observed but
   who have limited individual information) are a primary mechanism by which
   social learning fails.

### What this literature leaves open

1. **The continuous-time dynamics** of social learning are less well-developed
   than the discrete-time Bayesian models. Hawkes-process and Kuramoto frameworks
   fill this gap from the dynamical-systems side.
2. **Empirical applications** of network economics to investment decisions
   are limited, with most empirical network work focused on labour markets,
   technology adoption, and financial contagion.
3. **The interaction between Layer 1 (network observation) and Layer 2
   (shared information sources)** is underdeveloped. The network economics
   literature largely assumes Layer 1; the herding literature largely conflates
   the two.

### Where this framework sits

The framework draws on the recognition that *network structure matters* —
not all investors observe all others equally; some actors (incumbents, large
funds, listed players) are far more visible than others. This is the
"information bottleneck" structure of Acemoglu et al. (2011), applied to
NEM developers and operationalised through the `actor_lead_lag_pairs`
analysis in `corporate.py`.

The framework does not require complete-network assumptions and is structured
to test for asymmetric influence empirically rather than impose it.

---

## 3. Dynamical systems and Kuramoto synchronisation

### Foundational work

**Kuramoto, Y. (1975).** *Self-entrainment of a population of coupled
non-linear oscillators.* In International Symposium on Mathematical Problems
in Theoretical Physics, 420-422. The original model. Establishes the phase
transition from incoherent to synchronised behaviour at a critical coupling
strength.

**Kuramoto, Y. (1984).** *Chemical Oscillations, Waves, and Turbulence.*
Springer. Extended treatment. Includes the mean-field analysis that gives the
critical coupling K_c in closed form for the complete-graph case.

### Modern surveys

**Strogatz, S. H. (2000).** *From Kuramoto to Crawford: exploring the onset
of synchronization in populations of coupled oscillators.* Physica D 143(1-4),
1-20. The accessible introduction. Reviews the mathematical structure, the
phase transition, the role of heterogeneity, and the connections to other
synchronisation phenomena. Good starting point.

**Acebrón, J. A., et al. (2005).** *The Kuramoto model: A simple paradigm
for synchronization phenomena.* Reviews of Modern Physics 77(1), 137-185.
Comprehensive technical review. Includes finite-size effects, non-complete
networks, and noise-driven extensions.

**Arenas, A., Díaz-Guilera, A., Kurths, J., Moreno, Y., & Zhou, C. (2008).**
*Synchronization in complex networks.* Physics Reports 469(3), 93-153.
Network-Kuramoto literature. Key result: network topology fundamentally alters
the synchronisation transition. Algebraic connectivity (second-smallest
eigenvalue of the graph Laplacian) determines synchronisability.

### Power systems applications

**Dörfler, F., & Bullo, F. (2014).** *Synchronization in complex networks of
phase oscillators: A survey.* Automatica 50(6), 1539-1564. The canonical
reference for the Kuramoto-to-power-systems mapping. Derives the swing-equation
reduction explicitly and establishes synchronisation conditions for power
networks. The mathematical apparatus this framework borrows.

**Motter, A. E., Myers, S. A., Anghel, M., & Nishikawa, T. (2013).**
*Spontaneous synchrony in power-grid networks.* Nature Physics 9(3), 191-197.
Empirical and theoretical work on real power-grid topologies. Shows that the
synchronisation conditions for real grids are non-obvious and depend on
network structure in subtle ways. Relevant background even though this
framework applies Kuramoto to investors rather than generators.

### Economic and social applications

**Sornette, D. (2003).** *Why Stock Markets Crash: Critical Events in Complex
Financial Systems.* Princeton University Press. Applies critical-phenomena and
synchronisation concepts to financial markets. Establishes that financial
crashes can be understood as synchronisation events. The closest prior work
in spirit to this framework's application to investment markets, though
focused on equities rather than physical investment.

**Niebuhr, S., Lewenstein, M., & Hołyst, J. A. (2009).** *Synchronization
phenomena in two-dimensional networks of oscillators with quenched disorder.*
Various venues. One of several attempts to apply Kuramoto-type models to
opinion dynamics. The empirical work in these papers is generally weaker than
the theoretical apparatus, leaving room for more rigorous empirical
applications.

**Cumming, G. S. (2018).** Various ecology-Kuramoto applications. The broader
"synchronisation in social-ecological systems" literature gestures at the
applicability of Kuramoto frameworks to coordination problems but rarely with
the empirical rigour of the physics literature.

### What this literature establishes

1. **Synchronisation is a phase transition** — sharp, with predictable scaling
   behaviour, and well-characterised theoretically.
2. **Network topology matters** in ways that the mean-field analysis misses.
   Algebraic connectivity, degree distribution, clustering, and community
   structure all affect synchronisation.
3. **The Kuramoto framework extends naturally to power systems** (Dörfler &
   Bullo) and to a lesser extent to social and economic systems (Sornette,
   Niebuhr et al.).

### What this literature leaves open

1. **Time-varying coupling K(t).** Most Kuramoto work assumes constant K.
   Some recent work (Stankovski et al., Cesa et al.) treats time-varying
   coupling but the empirical infrastructure is limited.
2. **Endogenous coupling** — K dependent on the state of the system, not just
   exogenously time-varying. The hysteresis dynamics this implies are
   underexplored.
3. **Empirical application to investment systems.** Sornette is the
   exception, focused on equity markets. Application to physical asset
   investment with multi-year timescales is, as far as I can determine, novel.

### Where this framework sits

The framework adopts the Kuramoto-derived concepts (synchronisation threshold,
order parameter, phase transition) and applies them to investor behaviour
rather than physical oscillators. The mathematical apparatus is borrowed
from Strogatz (2000) and Dörfler & Bullo (2014). The empirical estimation,
via Hawkes processes, is borrowed from the financial-contagion literature.

The framework's specific extensions:

- **Two-layer coupling** structure (Section 2.4 of methodology) decomposing
  K into K_1 (direct observation) and K_2 · I(t, z) (information-substrate-
  mediated).
- **State-dependent K** through positive feedback I(t, z, r(t, z)) on the
  order parameter, producing hysteresis.
- **Empirical estimation** of these from public investment-decision data.

---

## 4. Power systems engineering on REZ planning

### Australian-specific work

**AEMO (various).** Integrated System Plan (ISP), biennial since 2018.
The official scenario-based plan for NEM transmission and generation
investment. ISP releases are themselves modelled in this framework as
Layer A events.

**AEMC (various).** Transmission Access Reform materials, 2018-present.
Background to the access-rights mechanisms that shape REZ investment.

**Energy Security Board (2021).** *Post-2025 Market Design Final Advice.*
The conceptual basis for capacity investment schemes that this framework
treats as Layer A events.

**Mountain, B., & Percy, S. (2020).** *Wind, sun, water, fire and money:
Australia's electricity sector at the dawn of the next decade.* Victoria
Energy Policy Centre. Critical commentary on transmission planning and REZ
selection. Useful context though not directly methodological for this
framework.

**Riesz, J., & MacGill, I. (2013).** *100% Renewables in Australia: A
research framework.* And related UNSW CEEM work. Background context on
the planning challenges that motivated the REZ framework.

### International work

**Mai, T., Mowers, M., & Eurek, K. (2021).** *Variable Renewable Energy
in Long-Term Planning Models.* NREL. Discusses how planners handle VRE
concentration risk in long-term models. Useful comparator for what this
framework's outputs could feed into.

**Wiser, R., & Bolinger, M. (annual).** US Land-Based Wind Market Report,
Lawrence Berkeley National Laboratory. Empirical patterns in US wind
buildout, including geographic concentration. The US analogues to Australian
REZ dynamics, though without the formal REZ framework.

### Constraint formulation literature

**Xu, T., Birge, J. R., et al. (various).** Operational and optimisation
work on AC power flow, constraint relaxations (SDP, SOCP, LinDistFlow), and
the AC-DC gap. Methodologically deep but operates at a different level of
abstraction from this framework. The related repository `nem-constraints`
contains empirical work in this area.

**Frank, S., Steponavice, I., & Rebennack, S. (2012).** *Optimal power flow:
a bibliographic survey.* Energy Systems 3(3), 221-258. Comprehensive
optimisation-side survey. Cited here as background for how this framework's
"synchronised buildout drives constraint emergence" claim would be tested
on the operational-engineering side.

### What this literature establishes

1. **REZ frameworks are recent and Australia-specific.** The international
   comparators are imperfect.
2. **Concentration risk in VRE buildout is recognised as a problem** but
   the prevailing approach is to address it through planning (better
   identification of corridors) rather than through empirical analysis of
   why investors herd.
3. **Operational consequences of concentrated buildout** — constraint
   emergence, MLF degradation, voltage stability concerns — are studied
   separately from the investment-decision side. Integration is rare.

### What this literature leaves open

1. **Empirical analysis of investor behaviour in the REZ context** is, as
   far as I can determine, limited. The planning literature treats investor
   behaviour as either fixed (a scenario assumption) or rational (responding
   to fundamentals). Neither characterisation matches the empirical record
   in Western Downs, Tarrone, and similar clusters.
2. **The bridge between investment behaviour and constraint emergence** is
   typically a one-way street: planning models assume an investment
   trajectory and compute the operational consequences. This framework's
   contribution is to estimate the investment trajectory empirically and
   characterise its dependence on observable signals.

### Where this framework sits

The framework is complementary to the power-systems engineering literature,
not competing. It takes the constraint-formulation work (e.g., AEMO's NEM
constraint equation set, the AEMC's access-rights frameworks) as given and
asks: *what determines whether and when investors collectively produce
buildout patterns that stress those constraints?* The answer to that
question feeds back into planning, but does not replace the planning models
themselves.

---

## 5. Synthesis: what this framework contributes

Across the four literatures:

**Borrowed:**
- Hawkes-process methodology from financial econometrics (Aït-Sahalia et al.;
  Hardiman et al.).
- Kuramoto framework from physics and applied mathematics (Strogatz; Dörfler
  & Bullo).
- Information-cascade theory from financial herding literature (Banerjee;
  Bikhchandani et al.; Hirshleifer & Teoh).
- Network learning concepts from network economics (Acemoglu et al.;
  DeMarzo et al.).
- REZ institutional structure from Australian power-systems context (AEMO
  ISP; AEMC; ESB).

**Extended:**
- The Layer 1 / Layer 2 distinction (Hirshleifer-Teoh, informally) becomes
  a formal model with separate estimation of each.
- Constant-K Kuramoto becomes state-dependent K(t, z, r), capturing hysteresis.

**Novel:**
- Application of Kuramoto-type synchronisation analysis to physical
  investment decisions on multi-year timescales.
- Integration of investment-behaviour analysis with constraint-emergence
  analysis through the linked `nem-constraints` work.
- Empirical specification using public Australian NEM data with documented
  primary-source provenance.

The framework's most defensible single claim to contribution: *making
quantitative what has previously been qualitative in the Australian energy
context*. "Herding" is widely invoked; this framework operationalises it
into testable Hawkes-parameter estimates with documented falsification
conditions.

---

## 6. References (alphabetical, all explicitly engaged above)

- Acebrón, J. A., et al. (2005). The Kuramoto model: A simple paradigm for
  synchronization phenomena. *Reviews of Modern Physics* 77(1), 137-185.
- Acemoglu, D., Dahleh, M. A., Lobel, I., & Ozdaglar, A. (2011). Bayesian
  learning in social networks. *Review of Economic Studies* 78(4), 1201-1236.
- Acemoglu, D., & Ozdaglar, A. (2011). Opinion dynamics and learning in
  social networks. *Dynamic Games and Applications* 1(1), 3-49.
- AEMO. Integrated System Plan, biennial editions 2018-2024.
- Aït-Sahalia, Y., Cacho-Diaz, J., & Laeven, R. J. A. (2015). Modeling
  financial contagion using mutually exciting jump processes. *JFE* 117(3),
  585-606.
- Arenas, A., Díaz-Guilera, A., Kurths, J., Moreno, Y., & Zhou, C. (2008).
  Synchronization in complex networks. *Physics Reports* 469(3), 93-153.
- Bala, V., & Goyal, S. (1998). Learning from neighbours. *Review of
  Economic Studies* 65(3), 595-621.
- Banerjee, A. V. (1992). A simple model of herd behavior. *QJE* 107(3),
  797-817.
- Bikhchandani, S., Hirshleifer, D., & Welch, I. (1992). A theory of fads,
  fashion, custom, and cultural change as informational cascades. *JPE*
  100(5), 992-1026.
- DeMarzo, P. M., Vayanos, D., & Zwiebel, J. (2003). Persuasion bias, social
  influence, and unidimensional opinions. *QJE* 118(3), 909-968.
- Dörfler, F., & Bullo, F. (2014). Synchronization in complex networks of
  phase oscillators: A survey. *Automatica* 50(6), 1539-1564.
- Energy Security Board (2021). Post-2025 Market Design Final Advice.
- Frank, S., Steponavice, I., & Rebennack, S. (2012). Optimal power flow:
  a bibliographic survey. *Energy Systems* 3(3), 221-258.
- Golub, B., & Jackson, M. O. (2010). Naïve learning in social networks
  and the wisdom of crowds. *AEJ: Microeconomics* 2(1), 112-149.
- Hardiman, S. J., Bercot, N., & Bouchaud, J.-P. (2013). Critical
  reflexivity in financial markets: a Hawkes process analysis. *EPJ B*
  86(10), 442.
- Hirshleifer, D., & Teoh, S. H. (2003). Herd behaviour and cascading in
  capital markets. *European Financial Management* 9(1), 25-66.
- Kuramoto, Y. (1975). Self-entrainment of a population of coupled non-linear
  oscillators.
- Kuramoto, Y. (1984). *Chemical Oscillations, Waves, and Turbulence.*
  Springer.
- Lakonishok, J., Shleifer, A., & Vishny, R. W. (1992). The impact of
  institutional trading on stock prices. *JFE* 32(1), 23-43.
- Mai, T., Mowers, M., & Eurek, K. (2021). Variable Renewable Energy in
  Long-Term Planning Models. NREL.
- Motter, A. E., Myers, S. A., Anghel, M., & Nishikawa, T. (2013).
  Spontaneous synchrony in power-grid networks. *Nature Physics* 9(3),
  191-197.
- Mountain, B., & Percy, S. (2020). Wind, sun, water, fire and money. VEPC.
- Niebuhr, S., et al. (2009). Synchronization in 2D oscillator networks.
- Riesz, J., & MacGill, I. (2013). 100% Renewables in Australia. UNSW CEEM.
- Sias, R. W. (2004). Institutional herding. *RFS* 17(1), 165-206.
- Sornette, D. (2003). *Why Stock Markets Crash.* Princeton.
- Strogatz, S. H. (2000). From Kuramoto to Crawford. *Physica D* 143(1-4),
  1-20.
- Wermers, R. (1999). Mutual fund herding and the impact on stock prices.
  *Journal of Finance* 54(2), 581-622.
- Wiser, R., & Bolinger, M. (annual). US Land-Based Wind Market Report. LBNL.

---

*Document version: 0.1 (draft, May 2026). Reference list to be expanded as
the framework develops and additional related work is identified.*
