# R22 reserve-cap sweep — C10, C11, C12

**SYNTHETIC ONLY / PROVISIONAL.** Branch
`align/2026-11-08-r22-cap-sweep-sol`, base `8f81bf7bd`.
This is a sensitivity analysis of the unchanged R22-2 model, not a live
validation, observed exclusion rate, registered policy, or distribution-free
FPR guarantee. No measurement data, model weights, or network are inputs.

## Answers

**(a) A larger reserve cap does not remove the gate-selection effect relative
to the original oracle.** At b=0, successful R22 calibrations use eight
independent windows drawn from the gate-admitted distribution for every cap.
Changing C10 to C11/C12 changes availability, not that distribution. When bars
are independent of state, this is also the oracle's score distribution. When
bars preferentially remove hot states, the oracle still calibrates on all
states, so its cutoff and its FPR on the *same admitted future population*
differ from R22's. Evaluating both on admitted future windows does not make
their calibration populations equal.

An oracle defined instead as eight gate-admitted calibration windows would
match the R22 calibration law at b=0 in this model. That is a different
comparator from the inherited `oracle8`; the requested paired shifts retain
the inherited oracle.

For example, C10 at q=.25, e=.10, tau=.5, b=0 has maximum-rule
`future_pass_fpr` **2.245%** versus oracle `future_pass_fpr` **1.211%**.
Its all-window `fpr` is **4.040%**, versus oracle all-window `fpr`
**2.321%**. Comparing 2.245% to 2.321% mixes future populations; it is not
evidence that the oracle cutoff has been recovered. The cap sweep below
reports the same-population contrasts directly. An admitted-population
registration would also need to address clustering, drift, and the chosen
rank rule; selecting that target alone proves no nominal error guarantee.

**(b) None of C10/C11/C12 reaches 95% at q=1/4, e=.10.** Exact qualification
is **52.5588%, 71.3297%, 84.2348%**, respectively. The first cap reaching
95% is **C14: 96.1720%**; C13 reaches only **91.9778%**. C13/C14 are exact
availability calculations only; their FPRs were not simulated.

**(c) Positive drift makes the later calendar relevant.** Any study already
qualifying by C10 stops there, so its C11/C12 thresholds and risks are
identical to C10. Newly qualifying studies use later calibration windows.
With b=.05 and a common future test horizon, their later observations tend
to raise thresholds and lower future FPR. This is a change in each cap's
qualified population and calibration timing; it is not a threshold adjustment
on the studies that already passed C10. Detailed numerical contrasts follow.

## Complete tables and availability

The [joined table](r22-cap-sweep-table-sol1.csv) contains all **72 settings ×
four designs × three rules = 864 rows** for the primary common test horizon.
Every row includes exact and simulated qualification, both FPR populations,
paired threshold shift versus oracle, expected reserve attempts, pointwise
Monte Carlo intervals, and oracle reference risks. All probabilities in CSVs
are fractions, threshold shifts are in residual SD units, and reserve counts
are windows. The [full score table](r22-cap-sweep-scores-sol1.csv) also gives
each pair separately and the old-horizon compatibility calculation. The
[counts](r22-cap-sweep-counts-sol1.csv) and
[exact availability extension](r22-cap-sweep-availability-sol1.csv) are separate
machine-readable tables.

Exact qualification percentages, identical across mechanism, tau, and b in
this model:

| q | e | C10 | C11 | C12 |
|---:|---:|---:|---:|---:|
| .125 | .10 | 88.0489 | 96.1022 | 98.8705 |
| .125 | .20 | 84.2410 | 91.9460 | 94.5946 |
| .250 | .10 | 52.5588 | 71.3297 | 84.2348 |
| .250 | .20 | 50.2857 | 68.2449 | 80.5919 |

Exact expected reserve windows attempted, unconditional over **all started
studies**, including failures. A barred reserve consumes an attempt. Member
loss e does not affect this expectation because it cannot arm reserves.

| q | C10 | C11 | C12 |
|---:|---:|---:|---:|
| .125 | .969173 | 1.088675 | 1.127644 |
| .250 | 1.599548 | 2.073956 | 2.360651 |

Writing A_C for the event that at least eight windows pass among C attempts,
the exact qualification probability is
`P(A_C) × P[Binomial(56,1−e)≥39]^2`.
`E[reserves attempted] = sum(n=8..C−1) P[Binomial(n,1−q)<8]`.
These are study-level probabilities; structural failure is shared by the two
pairs and is not squared. No qualification failure receives no-alarm credit.

<!-- BEGIN NUMERICAL COMPARISONS -->
Maximum-rule results with hot-correlated bars, q=.25, e=.10, b=0.
Risks are percent; shifts are s_r. Brackets are pointwise 95% MC intervals.

| tau/s_r | Design | future_pass_fpr | fpr | Paired threshold shift vs oracle |
|---:|---|---:|---:|---:|
| .5 | oracle8 | 1.211 [1.204,1.219] | 2.321 [2.309,2.333] | 0 |
| .5 | C10 | 2.245 [2.231,2.260] | 4.040 [4.017,4.063] | −.221 [−.224,−.217] |
| .5 | C11 | 2.244 [2.231,2.257] | 4.038 [4.018,4.058] | −.269 [−.272,−.266] |
| .5 | C12 | 2.245 [2.234,2.257] | 4.039 [4.021,4.057] | −.298 [−.301,−.295] |
| .8077 | oracle8 | 1.169 [1.159,1.178] | 2.906 [2.886,2.926] | 0 |
| .8077 | C10 | 2.965 [2.944,2.986] | 6.741 [6.699,6.782] | −.432 [−.437,−.427] |
| .8077 | C11 | 2.966 [2.948,2.984] | 6.743 [6.708,6.779] | −.513 [−.518,−.508] |
| .8077 | C12 | 2.966 [2.950,2.983] | 6.743 [6.710,6.776] | −.558 [−.563,−.554] |

The changing paired threshold shifts do **not** mean that increasing the cap
lowers the threshold on already-C10-qualified studies. Each cap's contrast
conditions on a different intersection with oracle qualification; oracle
C1–C8 states also change under that conditioning. R22's own successful
eight-window score law is unchanged at b=0. Across the full no-drift grid,
C12−C10 maximum-risk point differences range from −.019 to +.004 percentage
points, consistent with this cap-invariant model law.

Under b=.05, q=.25, e=.10, tau=.8077, common T positions 13–15:

| Mechanism | Rule | C10 future_pass_fpr % | C11 % | C12 % | C12−C10, percentage points [95% MC] |
|---|---|---:|---:|---:|---:|
| gaussian_independent | maximum | 5.094 | 4.965 | 4.884 | −.209 [−.269,−.150] |
| hot_independent | maximum | 5.316 | 5.214 | 5.132 | −.184 [−.258,−.109] |
| hot_correlated | maximum | 5.447 | 5.343 | 5.263 | −.184 [−.247,−.121] |
| gaussian_independent | rank05 | 8.790 | 8.597 | 8.474 | −.316 [−.396,−.235] |
| hot_independent | rank05 | 8.928 | 8.779 | 8.657 | −.271 [−.366,−.176] |
| hot_correlated | rank05 | 8.972 | 8.811 | 8.691 | −.281 [−.365,−.196] |

These differences compare each cap's own qualification population; intervals
use the conservative Cauchy SE bound. Across **every** requested b=.05
setting, C12−C10 gate-risk point differences are negative: maximum
−.259 to −.054, rank05 −.420 to −.080, literal38 −.947 to −.174 percentage
points. Not every small difference has a pointwise interval excluding zero.
The later reserves move calibration closer to a fixed future T under this
positive drift; they do not increase gate-admitted FPR here. This conclusion
does not cover reversed drift, persistent state, or a different test calendar.

Even the admitted target can exceed the original nominal 2.5%/5% targets.
Worst mean gate risks across the requested q/e/tau/mechanism grid (percent):

| Cap | maximum, b=0 | rank05, b=0 | maximum, b=.05 | rank05, b=.05 |
|---|---:|---:|---:|---:|
| C10 | 3.369 | 5.838 | 5.992 | 9.869 |
| C11 | 3.370 | 5.838 | 5.956 | 9.811 |
| C12 | 3.368 | 5.836 | 5.936 | 9.783 |

All these maxima occur at hot-correlated q=.125, e=.20, tau=.8077.
For C12, no-drift maximum/rank05 intervals are [3.347,3.390] /
[5.807,5.864]%; drift intervals are [5.903,5.969] / [9.741,9.825]%.
<!-- END NUMERICAL COMPARISONS -->

## Model, calendar, and interpretation

The [original report](R22-SIM-sol1.md) defines the model. This sweep uses its
unchanged seed **202611082201**, **100,000 studies per setting**, memory chunk
**2,000**, seven assigned fresh benign members per pair/window, both m≥39,
and exactly eight counted unbarred windows. Reserves are attempted solely to
replace structural bars. Reaching eight counted windows with low m fails
immediately; there is no member top-up. A cap with fewer than eight counted
windows fails even if both m already exceed 39. No score enters selection.

The original score law is `S = epsilon + tau*Z + b*j` (zero-based j, s_r=1),
with independent Gaussian residuals and independent window states shared
across pairs. The mechanisms retain standard Gaussian/independent bars,
25%-hot/independent bars, and 25%-hot/correlated bars (3q hot, q/3 cool).
Member exclusions remain independent of scores, state, and bars.

The requested Cartesian grid is q∈{1/8,1/4}, e∈{.10,.20},
tau/s_r∈{0,.5,.8077}, b∈{0,.05}, all three mechanisms. The rounded .8077
label retains the original exact `.0021/.0026 = .8076923076923077` value;
there is no new estimated prior or residual-scale conversion. This expands
e=.20 to the independent mechanisms as requested; the original R22 e=.20
grid covered only hot-correlated bars. Other original tau values and
exploratory margin repairs are outside this cap question.

The primary horizon is **common T1–T3 at positions 13–15**, after potential
C12, for every cap and oracle. Unused reserve slots are not reassigned.
Thus b=.05 gives test means .60/.65/.70 s_r. The previous C10 experiment
used positions 11–13, test means .50/.55/.60. That horizon is also retained
as `legacy_C10` in the full score CSV solely to prove exact old-result
preservation and quantify calendar sensitivity. It overlaps potential
C11/C12 and must not be interpreted as an implementable sequential schedule
for those caps. The common post-C12 calendar is an explicit modeling
assumption, not a registration change. No user calendar ruling was supplied
during execution. With b=0 the two horizons are byte-identical.

`fpr` averages the integrated future strict exceedance probability over each
design's **own qualified studies** and all future states. `future_pass_fpr`
uses the same qualified studies and conditions future windows on passing
the same structural gate. The admitted hot fraction is
`.25*(1−3q)/(1−q)` (.178571 at q=1/8; .083333 at q=1/4); independent member
loss cancels on conditioning. Barred future windows are unavailable, not
true negatives. Future Gaussian/state tails are integrated, not estimated
from three realized future observations.

`maximum` uses rank m; `rank05` uses ceil(.95*(m+1)); `literal38` always uses
rank 38. At m>39, literal38 is not a nominal 5% rule. All three are retained
from the same simulator and reported separately. Pair means average the
two pair risks **within study** before calculating their uncertainty.

Paired oracle differences use the intersection of design and oracle
qualification. Own-population differences condition each design on its own
qualification; their intervals use the conservative Cauchy upper bound on
the standard error of the difference of dependent means. The same applies
to own-population C11/C12−C10 comparisons. In contrast, paired comparisons
restricted to C10-qualified studies are exactly zero, because collection
has already stopped. Intervals are pointwise 95% Monte Carlo numerical
intervals, not simultaneous bounds, live uncertainty, or conditional
conformal guarantees.

## Reproduction and limits

[Simulator](simulate_r22_cap_sweep_sol1.py),
[stdlib audit](audit_r22_cap_sweep_sol1.py),
[metadata](r22-cap-sweep-metadata-sol1.json),
[audit receipt](r22-cap-sweep-audit-sol1.json),
[unit checks](r22-cap-sweep-checks-sol1.txt),
[pilot timing](r22-cap-sweep-profile-sol1.txt), and
[full run log](r22-cap-sweep-run-sol1.txt) accompany the tables.

C1–C10 preserve the original RNG call order, shapes, seed, chunk size, and
score arithmetic. Independent C11/C12 draws use a separate generator with
SeedSequence `[202611082201,11,12]`, so they cannot perturb later C10 chunks.
Settings and caps share their synthetic tapes. This is unmeasured synthetic
batching only; no measured episode, decision cache, or throughput change is
introduced. Original scripts and numerical artifacts are unchanged.

Six new checks cover all 4,096 bar tapes, exact probabilities/workload, no
top-up, original prefix bytes, scalar tails, and deterministic serialization.
The original simulator's eight checks and the estimand module's 15 tests pass.
The run checks exact qualification and iid rank expectations; the stdlib audit
checks every row, pair mean, interval, horizon, and old-result serialization.
The 72-setting run took **1,158.7 s**; **17,568** overlapping original
numerical fields serialize byte-identically. The audit validates **52,992**
intervals, 288 count rows, 5,184 score rows, and 864 joined rows.
Commands, host issues, and detailed verification are in the
[dated handoff](../../../run_reports/2026-11-08-align-v4-r22-cap-sweep-sol1.md).

Numerical execution used Python 3.14.6 / NumPy 2.2.6; Python 3.13 lacked NumPy.
The host's documented large-array comparison issue required testing raw array
bytes instead of `np.testing.assert_array_equal`. **Supported Python
3.11/3.13 + NumPy reproduction remains a lead gate.** No full suite or native
MLX tests ran; no MLX/product code changed. No coordination state or scientific
policy changed. State persistence, non-Gaussian tails, gate drift, dependent
member exclusions, and native scorer/eligibility validity remain unqualified.

Next exact step: lead reviews the proposed admitted-population FPR target and
test calendar, reproduces the sweep on a supported numerical runtime, and
decides whether to qualify C14 FPR/detection cost before selecting a ≥95%
availability design. C10–C12 FPR results do not qualify C14's FPR.
