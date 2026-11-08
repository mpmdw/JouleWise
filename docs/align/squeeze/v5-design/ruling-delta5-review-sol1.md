# Revision 5 ruling review — Sol1

**Verdict: SIGN_WITH_CHANGES.** The attempt-level betting test is valid for
the stated conditional null, and it materially improves power over revision
4. The ordinary-correlation planning results broadly reproduce. One concrete
bug changes the signature: the author's macOS stress workers reset the
regression/missingness parameters, and the intended stress law does **not**
meet the 80% targets at a 0.10 effect. Correct the simulation and feasibility
claim, then make the prospective sizing/claim decision on the corrected law.
This is a bounded repair, not a reason to abandon the native hybrid.

Candidate: `1cc050296`, revision 5. Seat: **sol1**. Branch:
`align/2026-11-08-v5design-ruling-delta5-sol1`. The ruling and author's script
are unchanged. This is one independent seat, not the other seat's verdict or
the lead's final signoff. All evidence below is synthetic.

## 1. Independent procedure and simulation

[`power_sim_sol1.py`](power_sim_sol1.py) was written from §4b **before** reading
the author's source. It uses only the standard library, has no repository or
author-code imports, reads no input files, and uses a separate generator,
seed and model. Later comparison runs imported the author's script separately
and called its `simulate` function sequentially; its default many-worker Pool
was never launched. Full output and reproduction snippets are in the
[run report](../../../run_reports/2026-11-08-v5-ruling-delta5-sol1.md).

The primary runs have 2,000 replications per grid point, seed 850137 with
documented law/effect offsets; null checks have 10,000 per law. Intervals are
**pointwise 95% Wilson Monte Carlo intervals**, not effect intervals or
simultaneous guarantees after searching the grid.

### Coupled law

* Exactly 28 windows × 12 attempts, six pair/optimizer cells, the sealed
  phase offsets `(0,1,2,1,2,0)` and shuffled chronological positions.
  H4 is literally the 224 assigned non-cover attempts from these same 336
  records, eight per window, 112 per pair. Cell totals are
  `(37,37,38,37,38,37)`.
* Each record has one side outcome and four channel scores M/E/T/S. The six
  rules are M, E, max(T,M), S, max(M,E), max(S,E); the same rule alarm is
  reused in every contrast. The nominal solo threshold is .95 and max-rule
  threshold is sqrt(.95), matching independent Uniform honest channels.
* In particular, the same-C order statistics imply the max-rule cutoff is
  at least either component's cutoff. H1 and H2 rescues cannot occur together.
  Independent ternary streams do not enforce that identity. H3/H4 are
  correlated with H1, but not identical to it.
* Let `p = Delta+r`. Mutually exclusive attack categories have probabilities
  `p` (E high/M low), `p` (M high/E low), `.1p` (E high/M medium), and `r`
  (M/E/S medium and T high, producing four regressions). The first category
  independently loses 10% of its H3/H4 rescues to high T/S; the third restores
  their means. All four nominal, pre-missing effects are therefore Delta.
* A common bounded-beta window shock varies p. Its ceiling is `(1-r)/2.1`,
  and its variance is exactly `rho*p*(1-p)`, giving rescue-indicator ICC rho
  before missingness. This preserves the intended mean without Gamma-tail
  clipping. Regressions remain present, at .02 or .05 per attempt.
* One shared unknown-side flag per attempt has probability .02 or .05.
  Its adverse completion changes positive differences to zero and preserves
  negative differences. The tested mean becomes `(1-miss)*Delta-miss*r`.
  Unknowns also fail capability; no favorable imputation is used.
* Residual zero-difference outcomes give marginal side success .60, chosen
  to keep the high-effect grid feasible with disjoint H1/H2 rescues. This is
  an **optimistic capability assumption**, not a fitted v5 rate. The point
  capability bar is checked; availability is fixed at 100%.

MDE means the first tested Delta with estimated per-hypothesis full-Holm
power ≥.80 when **all four nominal effects move together**. It is a grid
estimate, not an exact continuous MDE or a guarantee for unequal effects.

| Law | H1, n=336 | H2, n=336 | H3, n=336 | H4, n=224 | H1–H3 conjunction |
|---|---:|---:|---:|---:|---:|
| rho=0, r=.02, missing=.02 | .07 | .07 | .07 | .08 | .08 |
| rho=.05, r=.02, missing=.02 | .07 | .07 | .07 | .09 | .08 |
| rho=.15, r=.02, missing=.02 | .08 | .08 | .08 | .09 | .09 |
| **rho=.30, r=.05, missing=.05** | **.12** | **.12** | **.12** | **.14** | **.14** |

The grid is `.04,.06,.07,.08,.09,.10,.12,.14,.16`; the .05 point was not
tested. For the first three rows the results agree broadly with §4e's
.07–.09 estimates. Coupling and the bounded shock law change the conjunction,
so these are not expected to be identical draws. At .12 in the stress row,
H1/H3 estimates are close to .80; their lower Monte Carlo limits are below
.80. Do not call the first crossing a 95%-certified power guarantee.

Selected **verbatim output**, columns H1 H2 H3 H4 H123 strong beyond
honest_gate, followed by adverse means:

```text
SCENARIO Scenario(name='coupled-rho15', rho=0.15, regression=0.02, missing=0.02, calibration='none')
effect=0.100 0.9455[0.9347,0.9546] 0.9610[0.9516,0.9686] 0.9470[0.9363,0.9560] 0.8935[0.8792,0.9063] 0.9285[0.9164,0.9390] 0.9285[0.9164,0.9390] 0.8815[0.8666,0.8949] 1.0000[0.9981,1.0000] mean=0.0973,0.0983,0.0976,0.0974
SCENARIO Scenario(name='coupled-stress', rho=0.3, regression=0.05, missing=0.05, calibration='none')
effect=0.100 0.6895[0.6689,0.7094] 0.6955[0.6750,0.7153] 0.6960[0.6755,0.7158] 0.5920[0.5703,0.6133] 0.6235[0.6020,0.6445] 0.6235[0.6020,0.6445] 0.5520[0.5301,0.5737] 1.0000[0.9981,1.0000] mean=0.0928,0.0931,0.0930,0.0927
GRID_MDE H1 H2 H3 H4 H123 strong beyond=[0.12, 0.12, 0.12, 0.14, 0.14, 0.14, 0.14]
```

### Threshold randomness and honest gates

Two additional sensitivities actually generate C and honest scores. Each
pair has 49 calibrators, cutoff rank 48, strict `score > cutoff`, and **the
same calibrators for every component and max rule**. There are 280 honest
tests: five per pair per window over 28 windows. The honest gate requires at
most 14 alarms for each of the six rules; capability and availability are
handled as above. Nothing is rethresholded after observing a gate loss.

The iid case has independent calibration/honest members with shared rule
components. The date case has seven independent, date-constant groups of
seven calibrators per pair and date-constant honest scores within each
pair/window. The two pairs' draws are independent. The latter is deliberately
severe, allowed within-date dependence, not an estimate of actual correlation.

| Calibration law | H1 MDE | H2 MDE | H3 MDE | H4 MDE | H1–H3 MDE |
|---|---:|---:|---:|---:|---:|
| iid | NF | NF | NF | .16 | NF |
| date-constant | .18 | .18 | .16 | .18 | NF |

NF means **no 80% crossing in the tested grid through .25**, not a proof
that 80% is unattainable at every larger/intermediate effect. The extended
grid adds `.18,.20,.22,.24,.25`; no interpolation is used. Neither law
reaches 80% strong-label or beyond-strong-software yield in this grid.
At nominal Delta=.10, honest-gate pass probabilities are .2655 and .0035;
strong-label yields are .0470 and .0005, respectively. Selected verbatim
output, with the same column order as above:

```text
SCENARIO Scenario(name='calibration-iid', rho=0.15, regression=0.02, missing=0.02, calibration='iid')
effect=0.100 0.4805[0.4587,0.5024] 0.4490[0.4273,0.4709] 0.5910[0.5693,0.6124] 0.6400[0.6187,0.6607] 0.2765[0.2573,0.2965] 0.0470[0.0386,0.0572] 0.0425[0.0345,0.0523] 0.2655[0.2466,0.2853] mean=0.0465,0.0410,0.0661,0.0674
GRID_MDE H1 H2 H3 H4 H123 strong beyond=[None, None, None, 0.16, None, None, None]
SCENARIO Scenario(name='calibration-date', rho=0.15, regression=0.02, missing=0.02, calibration='date')
effect=0.100 0.6605[0.6395,0.6809] 0.6640[0.6430,0.6844] 0.6915[0.6709,0.7114] 0.6185[0.5970,0.6395] 0.3860[0.3649,0.4075] 0.0005[0.0001,0.0028] 0.0005[0.0001,0.0028] 0.0035[0.0017,0.0072] mean=0.0681,0.0671,0.0809,0.0733
GRID_MDE H1 H2 H3 H4 H123 strong beyond=[0.18, 0.18, 0.16, 0.18, None, None, None]
```

Here Delta indexes the **nominal pre-calibration score law**. Random cutoffs
change the realized conditional effect; these MDEs must not be presented as
power for a fixed post-calibration .10 effect. That difference is exactly why
calibration must be included in planning. Gate-passing is a different event
again. No 80% strong-label probability is established by favorable rejection
power alone, and adding windows cannot cure a threshold/gate problem by itself.

These are sensitivities, not a full G12 certificate: no calibration attrition,
score missingness, +infinity degeneration, monitor outages, fitted helper
distribution, unequal effects or .30–.40 capability uncertainty is modelled.
Those remain in the development-calibrated re-run. The iid/date examples
establish that the omitted stage can materially affect a reviewer's forecast;
they do not predict v5's actual gate yield.

### Conditional-null size at Delta=0

Four new null laws have **zero true conditional means before adverse
missingness**: random shared-window variance, rare −1 regressions against
small +.02 gains, deterministic variance drift, and prefix-adaptive variance.
Fresh signed innovations keep every conditional mean ≤0 after missingness.
Streams share the same attempt roster, a common innovation with probability
.7, and H4's literal subset. The fractional-gain law exercises the broader
bounded-input algorithm, not literal binary-alarm outcomes. These null checks
are distinct from the physical channel-score power model.

```text
NULL window-variance FWER=0.0014[0.0008,0.0023]
NULL rare-regression FWER=0.0000[0.0000,0.0004]
NULL drift FWER=0.0015[0.0009,0.0025]
NULL adaptive FWER=0.0018[0.0011,0.0028]
```

All 4×4 pointwise Monte Carlo upper bounds for constituent rejection at
`.05/4,.05/3,.05/2,.05` are below their respective thresholds. This passes
these synthetic regression checks, not a universal simulation proof. A
mean-zero **random-mean** window shock with fixed regressions would generally
violate the registered conditional null once earlier attempts reveal it; it
must not be counted as a valid-null FWER experiment. The mathematical proof
below, rather than these few laws, supplies the family guarantee.

## 2. P1 — actual stress parameters are lost under spawn

`ruling_power_sim.py` changes `R_REG,MISS` in `main(--stress)`, then creates
`Pool()`; jobs do not carry those parameters. On this Mac, Python 3.13's
default start method is **spawn**. The child reimports the module with the
top-level defaults `.02,.02`, so the requested `.05,.05` is silently lost.
A one-worker synthetic probe, without any measurement/job inspection, gives:

```text
parent (0.05, 0.05)
spawn worker [(0.02, 0.02)]
```

This is a reproducible implementation defect, not a disagreement about the
dependence model. I then bypassed Pool and set the globals in the same process
before calling the author's unmodified `simulate`, with the published seeds.
Selected verbatim output (2,000 reps; same Wilson convention):

```text
r=0.02 missing=0.02 effect=0.1 rho=0.15 seed=20261133 H= 0.9595[0.9499,0.9673] 0.9560[0.9461,0.9641] 0.9540[0.9439,0.9623] 0.8810[0.8661,0.8945] H123=0.9055[0.8919,0.9176] any=0.9955[0.9915,0.9976]
r=0.05 missing=0.05 effect=0.1 rho=0.3 seed=20261216 H= 0.6810[0.6602,0.7011] 0.6940[0.6734,0.7138] 0.6855[0.6648,0.7055] 0.5530[0.5311,0.5747] H123=0.5080[0.4861,0.5299] any=0.8730[0.8577,0.8869]
r=0.05 missing=0.05 effect=0.12 rho=0.3 seed=20261217 H= 0.8270[0.8098,0.8429] 0.8265[0.8093,0.8425] 0.8225[0.8051,0.8386] 0.7170[0.6969,0.7363] H123=0.6920[0.6714,0.7118] any=0.9495[0.9390,0.9583]
r=0.05 missing=0.05 effect=0.15 rho=0.3 seed=20261218 H= 0.9465[0.9358,0.9555] 0.9405[0.9293,0.9500] 0.9445[0.9336,0.9537] 0.8765[0.8614,0.8902] H123=0.8835[0.8687,0.8968] any=0.9915[0.9864,0.9947]
```

The base rho=.15 row reproduces §4e. The intended stress row plainly fails
the .80 targets; the author's own tested stress grid crosses at .12 for
H1–H3 individually and .15 for H4/conjunction. My coupled law gives .12/.14.
Remaining differences are expected: exact bounded-beta rather than clipped
Gamma shocks, mutually exclusive H1/H2 rescues, shared H4 outcomes and
correlated rule decisions. They do not explain away the large stress deficit.

**Required change:** pass r/missing explicitly in every job, or use an explicit
worker initializer; expose the effective parameters in results and test spawn
with one worker. Replace the stress table and withdraw “Every MDE is ≤0.10
under all simulated correlation scenarios.” Choose a prospective fix or state
the narrower power envelope explicitly, with an early feasibility re-run
before committing the expensive development/confirmatory roster. H4 demotion
alone does not repair H1's .69 stress power. Preserve calibration/gate stages
in G12's acceptance law, not just independent ternary streams.

If the family is narrowed to three, H4 must become exploratory/outside the
confirmatory family; calling it a confirmatory **secondary** contrast does
not by itself remove AP multiplicity. No claim/family change is made here.

## 3. Stake validity and honest-FPR bound

For the specified planning prior, the exact prefix stake is

```text
lambda_i = clip((20*.05 + sum_{j<i} L_j) /
                (20*.12 + sum_{j<i} L_j**2), 0, .5).
```

The common moment denominator `20+i-1` cancels. The first stake is 5/12;
the denominator stays ≥2.4. No current/future observation enters it. Since
`L_i in [-1,1]`, every factor is ≥.5 and capital is strictly positive. Under
the registered null, `L_i <= delta_i` pathwise gives

```text
E[K_i | F_(i-1)]
 = K_(i-1) * (1 + lambda_i*E[L_i | F_(i-1)]) <= K_(i-1).
E[K_n | F_0] <= 1
P(min(1,1/K_n) <= u | F_0) <= u.
```

Coherent missing-score completions must contain the true completion and be
adapted when that record is processed. The argument preserves the null;
it does not require, or assert, that capital with re-adapted stakes is
pathwise monotone in every imputed observation.

Holm with exact `.05/4,.05/3,.05/2,.05` then gives strong FWER≤.05 under
arbitrary cross-stream dependence. A frozen nonnegative normalized mixture
of wealth processes also works. A frozen development prior changes power,
not the proof. G12 must require a positive second-moment denominator (or a
specified zero-denominator rule) if it replaces the planning prior. All
tuning, order, exclusions and mixtures must be fixed before test outcomes;
custodian replay uses chronological prefixes after the global seal. No
interim policy feedback, maximum-wealth substitution, late reorder, dropped
loss or outcome-dependent horizon is licensed. The six focused checks cover
these arithmetic/roster invariants, including exact null expectation over a
small enumerated tree and a losing suffix charged at the terminal horizon.

The confirmatory statement remains **failure of the all-attempt conditional
nonpositive null**, not proof of a positive marginal/population mean or a
stable gain on every window. This restriction was explicit in the reviewed
ruling and is retained; changing to attempts does not remove it.

**Honest-FPR: target correct; algorithm not yet fully specified.** §4b now
names the average predictable rate, which resolves the prior estimand
ambiguity. But “a betting confidence sequence ... inverted over q” is a
specification requirement, not an executable bound/proof. Inverting a
product betting on `q-R_i` valid under `E[R_i|past]>=q` *at every i* does
not automatically bound an average of heterogeneous conditional rates.
For example, deterministic honest rates 0 for 140 then 1 for 140 have mean
.5. A predictable schedule betting only in the first half can reject a
constant-q null spectacularly, without refuting that average.

One sufficient concrete completion, implemented separately as `honest_upper`
in my script, is a fixed Hoeffding exponential mixture. Let
`S_n=sum R_i`, `A_n=sum E[R_i|past]`. For fixed positive eta and weights,

```text
Z_n = sum_j w_j * exp(eta_j*(A_n-S_n) - n*eta_j**2/8)
eta = (1/8, 1/4, 1/2, 1), w_j=1/4.
```

Conditional Hoeffding's bound makes each summand a nonnegative
supermartingale at the true predictable `A_n`; the weights sum to one.
Ville's inequality plus monotone inversion of
`sum w_j exp(eta_j*(n*q-S_n)-n*eta_j**2/8) < 1/alpha` gives a simultaneous
upper confidence sequence for `A_n/n`, capped at 1. It needs neither constant
conditional means nor independent honest attempts. This illustrates a valid
completion, not an attribution to the author's unspecified algorithm.

```text
Explicit Hoeffding-mixture honest U(14/280)=0.135334
```

At alpha=.05 this is a **per-rule** bound; simultaneous six-rule coverage
would need a separately frozen allocation. The current strong-result gate
uses the **point** FPR≤.05 with the upper bound reported, so the .1353 upper
limit is not itself a failed gate. No requirement to have U≤.05 is invented.
Freeze the actual average-rate formula/inversion and coverage scope at G12;
do not mark numerical coverage as verified before that exists. This is an
existing completion obligation, not a new primary-test invalidity finding.

## 4. Every round-4 finding and carried delta4 item

Both original E1/E2 reports and both F1/F2 reports were read from existing
local Git objects; no fetching. “Resolved” below means ruling-level repair,
not a passed native or registration gate.

| Finding | Revision-5 status and operative check |
|---|---|
| E1 R1 / E2 R2: null/claim mismatch | **Resolved.** §4b states the attempt-level conditional null and expressly excludes unrestricted marginal inference, including shared shocks. |
| E1 R2 / E2 R1: 1.2× tolerance, switched inference, Holm | **Resolved.** One primary wealth procedure, exact thresholds, no switch; simulation is a code regression gate. Degenerate H4 remains p=1 in m=4. |
| E1 R3 / E2 R3: H4 support and estimator | **Resolved.** §4a's phases give eight per window and every cell present; exact counts reproduced in tests. §4b retains equal-cell date means as sensitivity, with primary order/units explicitly changed. |
| E1 R4 / E2 R4: CAP units, yield, observation span | **Resolved.** §5 multiplies by 24 for h/day, uses gross capacity, charges max(1.25,1/a) once, separates .85 transfer stress, and requires CAP-1b ≥5 windows over ≥7 days. No measurement inspected. |
| E1 L1 / E2 local-C note | **Resolved.** §4d uses actual eligible C; §5 includes 28 extra local scores, .611111 h. Cap envelope remains 732.689683/915.862103 h at t=900 s by the unchanged arithmetic. |
| E1 L2 / E2 rank note | **Resolved.** §4c has `(m+1-ceil(.95*(m+1)))/(m+1)`; m=39/44/49/63 gives .05/.044444/.04/.046875 under individual exchangeability only. |
| E2 F-fitting exception | **Resolved.** §4d allows F fitting before G12; only C/test scoring waits for T3. |
| F1/F2 P1: date-test low power | **Partly resolved.** Numerical .10/.80 targets, attempt test and fix menu are installed, and base cases work. The asserted full stress feasibility is false as demonstrated above. |
| F1/F2 honest bound target/inversion | **Target resolved; formula gated.** Average conditional rate is named. A matching actual CS still needs the completion just discussed. |
| F1/F2 exact Holm, mixture, exclusions and replay | **Resolved as contract.** Prefix-predictable cap/prior, exact Holm, normalized frozen mixture, pre-test freeze and no-feedback replay are explicit. |
| F1 date preference | **Adopted.** All 28 distinct dates preferred; ≥20 retained for sensitivity. |
| F1/F2 phase/CAP/rank arithmetic | **Reproduces.** No new accounting policy is requested. |
| Cosmetics | None affecting signature. |
| Novelty and NeurIPS 2027 eligibility/dates | **Still Open, explicitly deferred.** No network authority here; no venue/novelty conclusion is supplied. |

## 5. Handoff

Changed files: this review, `power_sim_sol1.py`, and the dated run report.
Six focused stdlib unittest checks pass; the quoted simulations completed;
`git diff --check` passes. No full/sharded suite was run: the user prohibits
it and only isolated review tooling/documentation changed. No production,
MLX, hardware or measurement code changed. No native test is claimed passed;
this change adds no native test the lead must run outside the sandbox.
Future tiny-synthetic native replay/helper/teardown tests and G0–G12 physical
gates remain lead-owned, with agents stopped for quiet collection.

**Next exact step:** lead repairs the stress parameter transport and §4e's
feasibility statement, adjudicates the two independent seats, and chooses or
explicitly conditions the prospective power envelope. Keep the closed R1–R4
repairs; complete the average-rate CS and full-stage G12 law before freezing
registration. Actual effects, calibration yield, capability, capacity, native
coverage and the companion verdict remain unknown here.
