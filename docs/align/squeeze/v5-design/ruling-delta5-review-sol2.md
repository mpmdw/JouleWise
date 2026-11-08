# Revision 5 ruling — independent delta5 review, Sol2

**Verdict: SIGN_WITH_CHANGES.** The attempt-level test is valid for the
registered conditional-mean null and repairs the date-level capital ceiling.
Baseline power is plausible. One material correction prevents signature:
the supplied script's macOS spawned workers silently run the stress scenario
with **2%, rather than 5%, regressions and missingness**. Correctly passing
those parameters makes the author's own sampler miss the 80% targets at
0.10. My independent, coupled simulation agrees that this stress is
underpowered. Correct the script/table and qualify the feasibility decision;
this is a bounded power-planning repair, not a redesign of the native hybrid.

Seat `sol2`, branch `align/2026-11-08-v5design-ruling-delta5-sol2`, candidate
`1cc050296` (revision 5). The ruling is unchanged. This is one seat's verdict;
I have not supplied a companion seat or delegated final judgment. Read the
revision-4-to-5 diff, both delta3 reviews (E1/E2, round 4), both delta4 reviews
(F1/F2), AP, D-062, and repository intake/orchestration instructions. Prior
reviews were read from existing Git objects without fetching. The independent
simulator was written and its six self-tests passed **before** opening the
author's simulator. Its pre-comparison/final SHA-256 is
`1ed19bfb3a63337ccc53ecd85e982858eafa4e57d5a5e5c35c9f18f2ebe2760e`.

## 1. The required power correction

In `ruling_power_sim.py`, `main --stress` changes module globals `R_REG` and
`MISS`, then launches `Pool()`. On this host Python 3.13 reports `darwin spawn`.
A spawned worker imports the module with its original `.02, .02` defaults;
neither parameter is in the job tuple. The worker's `simulate` and
`run_stream` therefore never receive the requested `.05, .05`. A one-worker
synthetic probe, without running a campaign or the script's unbounded pool,
printed:

```text
parent (0.05, 0.05) start_method spawn
spawned_worker (0.02, 0.02)
```

The unchanged author's sampler was then called **sequentially**, setting
its globals explicitly in the executing process, 2,000 replications per row.
Its baseline seed reproduces §4e. Selected verbatim output:

```json
{"name": "baseline", "mu": 0.1, "rho": 0.15, "regression": 0.02, "missing": 0.02, "reps": 2000, "seed": 20261133, "Holm": [0.9595, 0.956, 0.954, 0.881], "H123": 0.9055, "any_rejection": 0.9955}
{"name": "mac_spawn_stress_defaults", "mu": 0.1, "rho": 0.3, "regression": 0.02, "missing": 0.02, "reps": 2000, "seed": 20261216, "Holm": [0.934, 0.9285, 0.928, 0.858], "H123": 0.8695, "any_rejection": 0.982}
{"name": "intended_stress", "mu": 0.1, "rho": 0.3, "regression": 0.05, "missing": 0.05, "reps": 2000, "seed": 20261216, "Holm": [0.681, 0.694, 0.6855, 0.553], "H123": 0.508, "any_rejection": 0.873}
{"name": "intended_stress", "mu": 0.12, "rho": 0.3, "regression": 0.05, "missing": 0.05, "reps": 2000, "seed": 20261217, "Holm": [0.827, 0.8265, 0.8225, 0.717], "H123": 0.692, "any_rejection": 0.9495}
{"name": "intended_stress", "mu": 0.15, "rho": 0.3, "regression": 0.05, "missing": 0.05, "reps": 2000, "seed": 20261218, "Holm": [0.9465, 0.9405, 0.9445, 0.8765], "H123": 0.8835, "any_rejection": 0.9915}
```

These stress failures are much larger than Monte Carlo error. This also
explains the draft's surprising claim that the increased-regression stress
barely changes its MDE. The supplied source matches its cited hash
`6ef6adfe2384317b616b65ce9521b5246d21584d8489df34156753e93a1c096f`.
I cannot establish which host/start method produced the historical table;
the defect and the sequential corrected results are directly reproduced.

**Required disposition:** pass all scenario parameters explicitly to workers
(or run sequentially), add a focused spawned-worker parameter check, rerun
the stress table, and replace “the targets are met ... every MDE is ≤ 0.10
under all simulated correlation scenarios.” Baseline feasibility can stay
labelled provisional. G12 must explicitly retain full-stage power checks
including threshold randomness, coupled streams/literal H4, adverse losses,
capability and honest/availability gates. Choose and recost a prospective
fix-menu option if the development-calibrated law misses the declared
targets. This review does not choose a different roster on the lead's behalf.

## 2. Independent simulation and its scope

[`power_sim_sol2.py`](power_sim_sol2.py) uses only the standard library, one
process, seed `2026110802`, and the stated `n0=20, m0=.05, s0=.12, c=.5`
prefix stake. All four terminal p-values enter exact Holm. No imported
author functions, project modules, data, weights, network, or native runtime
are used by this simulator. The author's sampler is used only in the
separate comparison above.

The legal phase offsets `(0,1,2,1,2,0)` give 28 windows × 12 attacks, exactly
8 H4 per window, every cell represented, 224 H4 total, 112 per pair, and
cell totals `(37,37,38,37,38,37)`. A synthetic roster is shuffled once before
any outcomes. H4 uses those **same attempts, scores, side outcomes and
missing flags**, not a separately generated stream.

Six alarms come from four common scalar scores `(M,E,T,S)`:
`M, E, max(M,T), S, max(M,E), max(S,E)`. Scores are abstract channel scalars,
not a model of the actual S components or proof that native energy can add
to strong software. E-rescues and M-rescues are disjoint on an attempt;
H1/H3/H4 are identical in the fixed-threshold example, with H4 restricted
to its roster. Thus the family is deliberately dependent and realizable by
common alarms. Recalibration permits regressions in both directions.

For fixed thresholds, each rescue category has probability `a=signal+r`
and the common regression category probability `r`. Nominal effect is
therefore exactly `signal` for every H before missingness. A beta window
propensity, common to all 12 attempts, sets the pre-threshold rescue
indicator's ICC to exactly the named rho without gamma clipping. With
`P_w=(1-r)*Beta(k*mu,k*(1-mu))`, `mu=2a/(1-r)` and
`k=(1-r-2a)/(2*rho*(1-a))-1`, `Var(P_w/2)/(a*(1-a))=rho`.
This is rescue ICC, not delta ICC. Regression probability is fixed.

Unknown side outcomes resolve to `min(0, alarm_rule-alarm_comparator)`.
Unknown channel scores are completed coherently using every threshold
region, separately minimizing each hypothesis; endpoints alone could miss
a solo alarm below its joint cutoff. Unknown side success is failure for
capability. Missingness is 2%, or 5% in stress. In calibrated scenarios,
frontier unavailability is independently .002 per attack/honest member;
the missing M score is completed coherently, and unavailable honest evidence
is counted as an alarm. This is a limited outage model, not all possible
infrastructure failures.

Calibrated scenarios draw **two 49-member calibration rosters**, each on
7 dates × 7 members, using the same calibrators for all six scalar ranks
`ceil(.95*50)=48`, strict `>`. Honest raw scores are uniform in this toy
law. Successful rescue scores are uniform on `[.985,1]`, so random cutoffs
can remove real rescues; regression scores and all joint cutoffs are also
reevaluated. `cal-iid` has iid C; `cal-cluster` copies a shared date vector
with probability .5 (raw within-date ICC .25), and honest-test window
vectors with probability .3 (conditional raw ICC .09). Attack rescue ICC
is .15 in both. This sensitivity is intentionally sensitive to near-cutoff
scores; it is not an estimate of the unknown v5 score distribution.

All laws simulate 280 interleaved honest members (140 per pair). The strong
and beyond-software outputs also require all six honest point FPRs ≤ .05,
the pooled .30/per-pair .20 capability bars for both rosters, and ≥99%
availability. Synthetic side-success expectation is .40 at small signals;
it increases as printed `q` when necessary to fit larger rescue categories.
Those large-signal rows are not evidence of actual capability.

The calibrated curves' nominal signal is **not** their final effect. Output
prints each H's attained adverse-bound mean and Monte Carlo SE. Report MDE
coordinates accordingly; never equate an input rescue mixture with a
post-calibration .10 escape reduction. All intervals below are pointwise
two-sided Wilson 95% Monte Carlo intervals, not simultaneous curve bands.
Grid crossings are estimates, not exact roots or G12 certifications.

### Power, MDE and Monte Carlo output

There are 2,000 replications per power row. At **nominal signal .10**, full
Holm rejection probabilities are:

| Law | H1 | H2 | H3 | H4 | H1–H3 conjunction |
|---|---:|---:|---:|---:|---:|
| Fixed, rho 0 | .9795 | .9880 | .9795 | .9300 | .9710 |
| Fixed, rho .05 | .9665 | .9775 | .9665 | .9235 | .9540 |
| Fixed, rho .15 | .9310 | .9485 | .9310 | .8825 | .9125 |
| Fixed stress: rho .30, r .05, missing .05 | .6760 | .6910 | .6760 | .5820 | .6160 |
| Random C, iid | .7210 | .7300 | .6995 | .8700 | .5680 |
| Random C, clustered | .8000 | .8095 | .7755 | .8895 | .6790 |

For fixed rho .15, H4's interval is `[.867649,.895885]` and the conjunction's
`[.899312,.924106]`. Under fixed stress they are `[.560247,.603439]` and
`[.594482,.637074]`. The calibrated conjunction intervals are
`[.546181,.589559]` and `[.658213,.699101]`.

**80% per-hypothesis Holm MDEs**, along the explicitly specified curves:
each cell is `nominal signal (attained adverse-bound absolute effect)`.
Fixed-law grid spacing is .01. Calibrated curves add .15, .16, then .02
steps through .30. An asterisk means the crossing row's Monte Carlo interval
still includes .80; its point crossing does not certify ≥80% power.

| Law | H1, n336 | H2, n336 | H3, n336 | H4, n224 | H1–H3 nominal crossing |
|---|---:|---:|---:|---:|---:|
| Fixed rho 0 | .07 (.0684) | .07 (.0686) | .07 (.0684) | .08 (.0781)* | .08 |
| Fixed rho .05 | .08 (.0776) | .07 (.0687) | .08 (.0776) | .08 (.0777)* | .08 |
| Fixed rho .15 | .08 (.0776) | .08 (.0777) | .08 (.0776) | .09 (.0882) | .09 |
| Fixed stress | .12 (.1115) | .12 (.1113) | .12 (.1115) | .14 (.1315) | .13 |
| Random C, iid | .16 (.1187)* | .16 (.1185)* | .15 (.1166)* | .09 (.0815) | Not reached through .30 |
| Random C, clustered | .10 (.0842)* | .10 (.0848)* | .12 (.1032) | .09 (.0862) | .30* |

Examples of grid/Monte Carlo uncertainty: fixed-stress H4 at .13 has
power `.7890 [.770573,.806319]`, while .14 gives
`.8470 [.830559,.862111]`. Random-C iid H1's .16 point crossing is
`.8005 [.782417,.817431]`; the first sampled row whose lower interval is
≥.80 is .22. Do not assign spurious decimal precision to these MDEs.
For the clustered-C conjunction at .30, attained effects are
`(.230033,.230726,.247714)` and power is
`.8025 [.784479,.819361]`; no row through .30 has a lower interval ≥.80.
The iid-C conjunction never reaches .80 on this grid (final attained
effects `(.210454,.212458,.236667)`). This reflects persistent random
threshold variation in this particular near-cutoff score law, not a
universal MDE or a prediction about the actual detectors.

Missingness is not the whole explanation for the stress failure. At signal
.11 the tested adverse means are approximately `(.1023,.1018,.1023,.1028)`;
H1–H3 conjunction is only `.7030 [.682601,.722621]` and H4 is
`.6675 [.646549,.687808]`. Likewise iid random C at signal .13 produces
means `(.098085,.096952,.103077,.115141)` yet conjunction power is only
`.6535 [.632369,.674043]`. Thus losses remain around the intended **final**
.10 effect, not just when a nominal .10 input is reduced by imputation.

At nominal .10 the honest-gate pass probabilities are `.1040, .1015,
.1055, .1070, .2570, .0705` in table order; corresponding entire strong-label
probabilities are `.1005, .0955, .0950, .0600, .1075, .0310`. Under fixed
population thresholds each honest rule is at the .05 boundary, so meeting
all six point bars is intrinsically unlikely. The clustered-C law changes
operating FPR as well as attack thresholds. These are **label-yield**
sensitivities, distinct from the draft's inferential power targets; I do not
impose a new 80% strong-label requirement. The results do show why high
conditional detection power is insufficient to forecast a strong headline.

**Familywise error at Delta=0:** 20,000 independent replications of each
joint null law, always with the actual H4 subset. A shared beta window
activity changes the variance but keeps each conditional mean zero.
`symmetric` uses equiprobable signed E/M return vectors; `skew` uses +.1
with probability 10/11 and -1 with probability 1/11 on active attempts;
`drift` also varies activity predictably over the 28 windows. The latter
two stress the bounded-return theorem/code rather than literal ternary
escape indicators. Null laws omit missingness; taking an adapted adverse
bound also preserves the null inequality. Selected **verbatim summary
output**, generated from the simulation's JSON:

```text
NULL symmetric FWER {"p": 0.00235, "ci95": [0.001768, 0.003123], "k": 47, "n": 20000} max_H_tail_upper95 [0.001544, 0.001964, 0.002664, 0.00503]
NULL skew FWER {"p": 0.0, "ci95": [0.0, 0.000192], "k": 0, "n": 20000} max_H_tail_upper95 [0.000192, 0.000283, 0.000365, 0.002433]
NULL drift FWER {"p": 0.0, "ci95": [0.0, 0.000192], "k": 0, "n": 20000} max_H_tail_upper95 [0.000192, 0.000192, 0.000192, 0.000192]
```

Tail maxima range over H1–H4 at `.05/4,.05/3,.05/2,.05` respectively; all
are below their nominal thresholds. Zero observed rejections is not zero
population error. These finite-law Monte Carlo checks are regression
evidence; validity comes from the proof in §3. The author's null replay
also reproduces `.0005` (1/2,000; Wilson interval approximately
`[.000088,.002827]`). It has smaller regression/activity rates and adverse
missingness, so equality with my null estimates is neither expected nor
required. None of these numbers is an unrestricted marginal-null FWER.

**Comparison with §4e:** the independent fixed-law rho-.15 MDEs
`.08/.08/.08/.09` and conjunction .09 agree with its baseline planning
scale. At nominal .10 my H4 `.8825` agrees with its `.881`; my conjunction
`.9125` agrees with `.9055`. H1 `.931` versus `.9595` reflects disjoint,
coupled rescue categories, different dependence, no clipping, and Monte
Carlo variation; there is no reason for the two joint laws to match exactly.
The large stress difference is reproduced inside the **author's own law**
when the requested parameters actually reach the sampler. Random thresholds
can additionally change both effect sizes and the distribution of wealth;
honest gates reduce headline yield. This supports baseline conditional
feasibility, not the draft's all-scenarios power conclusion.

All classes/cells share the toy attack law. Actual class/optimizer effects,
more complex outage patterns, and the genuine S component distribution
remain development-calibrated G12 work; literal-subset coupling alone does
not supply those unknown rates.

## 3. Stake validity and honest-rate confidence bound

The common denominators in the two shrunken moments cancel, giving

```text
lambda_i = clip((1 + sum_(j<i) delta_j) /
                (2.4 + sum_(j<i) delta_j^2), 0, .5).
```

The initial stake is `1/2.4`, before observing the first outcome. The prior
is coherent for ternary outcomes (`p+=.085, p-=.035, p0=.88`); its second
moment is positive. Prefix sums only make every stake predictable. The
current prior and any replacement, transforms/mixture/exclusions/order must
be frozen from development/search **before test outcomes** at G12. Fitting
them to the sealed test data would violate predictability/freeze even if
the final replay is chronological. G12's final values remain unexecuted.

Since `delta_i >= -1`, every factor is at least `.5`, so capital stays
strictly positive (including all-zero or all-regression paths). Under the
registered null:

```text
E[K_i | F_(i-1)]
  = K_(i-1) * (1 + lambda_i E[delta_i | F_(i-1)]) <= K_(i-1).
E[K_n | F_0] <= 1.
P(min(1,1/K_n) <= u | F_0) = P(K_n >= 1/u | F_0) <= u, 0<u<1.
```

The pathwise adverse lower bound preserves the conditional-mean inequality;
it does not need capital itself to be monotone in all completed outcomes.
Normalized nonnegative frozen mixtures are valid too. Exact Holm thresholds
`.05/4, .05/3, .05/2, .05` control FWER≤.05 under any dependence among valid
p-values. A degenerate H4 stays with p=1. No running maximum, procedure
switch, optional stopping, future-prefix use or outcome-dependent top-up is
authorized. Post-seal custodian replay is compatible with predictability
only because its computation uses prior prefixes and frozen constants.

**Interpretation:** this rejects the intersection of the attempt-specific
conditional nulls. It does not prove a positive marginal campaign effect,
a stable advantage, benefit on every attempt, or prevention. A shared window
shock changing rescues but not regressions can violate this null even when
the marginal mean is zero. That is why the positive-shock power laws at
signal=0 are not used as null size laws.

**Honest-FPR:** the revised target, `n^-1 sum E[R_i|F_(i-1)]`, is appropriate
and can be bounded without independent honest members. However, “a betting
confidence sequence ... inverted over q” names a class, not an executable
interval algorithm or a confidence level. No actual numerical bound is
certified yet. This is a G12 implementation obligation, not an additional
charter-level signature blocker. Inverting a product testing
`E[R_i|past]>=q` for **every** i does not automatically upper-bound the
average under heterogeneous predictable rates.

One sufficient construction, implemented as a reference in this simulator:
write `mu_i=E[R_i|past]` and fix lambda>0 before outcomes. Conditional
Hoeffding gives the nonnegative supermartingale

```text
L_n = exp(lambda * sum_i(mu_i-R_i) - n*lambda^2/8).
U_n = min(1, Rbar_n + log(1/alpha_h)/(lambda*n) + lambda/8).
```

Ville's inequality gives simultaneous coverage of the average predictable
rate by `U_n` for all n. For example, freeze
`lambda=sqrt(8*log(20)/280)` and `alpha_h=.05`; at n=280 the additive width
is `.0731404260`. This is a conservative existence proof/reference, not a
request to require U≤.05. The strong-result rule uses the **point** FPR bar.
G12 may choose a tighter valid bound, but must specify its target, level,
formula, filtration, missingness and inversion. Per-rule coverage is not
simultaneous coverage of every rule unless separately arranged.

## 4. Earlier findings and authority boundaries

Every round-4 R1–R4 remains resolved at ruling level; native gate completion
is a different question. The later power issue remains open as corrected
above.

| Earlier finding | Check against operative revision 5 |
|---|---|
| E1 R1 / E2 R2: conditional null versus marginal effect | §4b explicitly adopts the attempt-level predictable conditional-mean null, conditions on F/C/thresholds/roster and previous attempts, and disclaims marginal inference. Changing dates to attempts also changes the null; it is not a claim to infer the old marginal target. |
| E1 R2 / E2 R1: 1.2× tolerance and switched procedure | Removed. A single valid primary, exact Holm, fixed horizon, retained p4=1, and simulation as regression evidence rather than proof remain explicit. |
| E1 R3 / E2 R3: H4 support and estimator | The phased roster supplies exactly 8/12 H4 every window and all six cells. Exhaustive roster assertions pass. The equal-cell date mean is still defined for the sensitivity. |
| E1 R4 / E2 R4: CAP units/double yield | CAP uses gross hours/day with factor 24, all windows, yield 1.25 or 1/a once, separate .85 transfer margin, and CAP-1b ≥5 windows/≥7 calendar days. Independent arithmetic: 112/168×24=16 h/day; 125/16=7.8125 days for 100 accepted hours at .80 yield. |
| E1 L1 / E2 local cap note | Actual eligible C roster and up to 28 extra local scores are billed. GO at 900 s is 732.689683/915.862103 h; at 1200 s 952.823016/1191.028770; at 1800 s 1393.089683/1741.362103. |
| E1 L2 / E2 rank note | `(m+1-ceil(.95*(m+1)))/(m+1)` is correct under individual-score joint exchangeability. Checked m39/k38=.05, m44/k43=.044444, m49/k48=.04, m63/k61=.046875. Date exchangeability still does not supply that guarantee. |
| E2 F-fitting exception | F selection/fitting is explicitly before G12; C/test local scoring waits for T3, with the access ledger and single release. |
| F1/F2 P1 | Attempt-level factors remove the old date-level ceiling, but feasibility is only partly resolved: intended effects/targets are installed, baseline works in toy laws, and the stress power claim needs correction. |
| F1/F2 honest bound, exact Holm, mixture/prior/order freeze | Target repaired; actual CS algorithm remains G12 work. Exact thresholds, normalized mixtures, no feedback and prefix replay are specified. |

Evidence fairness, deployable S, original invocation versus submitted
projection, +infinity/DEGENERATE_CALIBRATION, fresh nominal calibration,
immutable failure denominators, frozen S/E-aware search, local transfer
scope and v4 separation stay closed as design obligations. §9's historical
date-level R1 description is superseded by the operative attempt-level §4b;
that editorial history is not another signature condition. No additional
cosmetic changes are requested.

## 5. Handoff

The exact next step is to repair explicit scenario transport in the author's
simulation, rerun/correct §4e, and disposition the remaining power risk with
the prospective fix menu and measured CAP budget. Preserve the valid narrow
null, honest-rate target, evidence contract, and G12 freeze. The lead then
adjudicates this and the other independent seat on the corrected candidate.

No actual v5 rescue/regression rate, score distribution, capability,
availability, threshold behavior, host capacity, receipt coverage, physical
resolution or native replay parity was measured. Novelty and NeurIPS 2027
dates/eligibility remain unverified under the no-network rule. No native
tests apply to this standard-library-only change; future G3–G9 native and
physical gates, including G6 token-identical replay/twins, must run in the
lead-controlled environment, with quiet captures after agents stop. This
review adds no MLX implementation or test and claims none passed.

Only this review, the independent simulator, and the dated run report are
changed. Coordination files and the ruling are preserved. No network,
model download, real measurement/restricted-directory read, sealed pipeline,
process/job inspection, native probe, push or external integration was used.
Local commits and complete commands/results are recorded in the
[run report](../../../run_reports/2026-11-08-v5-ruling-delta5-sol2.md).
