# ASTRA-2CH analysis plan v0 (DRAFT)

**Status: DRAFT, NOT REGISTERED; 2026-11-07.** Companion to the proposed
[registration](../../registrations/astra_2ch_v0_draft.md) (REG). Neither file
alone authorizes collection or analysis of real data. REG owns the arms,
rosters, admissibility, custody, stopping, and open slots; this file owns
estimators, uncertainty, classifications, and outputs. All numeric examples
below are synthetic or explicitly labelled study planning anchors. This is
not executable analysis code and does not invoke the Block 5 pipeline.

## 1. Inputs, units, and frozen order of operations

Only a future, separately authorized ASTRA inventory may feed this plan.
Its manifest must bind code/runtime and artifact identities, coded arms,
problem and reference IDs, realized tokens, orders/seeds, scoring version,
native clock mapping, calibrated per-boundary floors, systematic uncertainty
methods, and append-only raw bundle hashes. Actual locations and digests are
`OPEN[A-1]` through `OPEN[A-7]` in REG. Do not resolve historical absolute
paths, discover arbitrary runs roots, or read any sealed Block 5 input.

Proposed reduction order:

1. Validate identities, manifests, reference-token hashes, timestamp support,
   sample coverage, and runtime path before estimating effects.
2. Apply only the frozen technical reason catalog to individual members and
   build complete paired F sets and complete T/P quads. Freeze that table
   while weights are coded. Never select on energy or correctness.
3. Score the first F answer under the pinned checker without energy labels;
   join scores and energy only after the prescribed release. Record all
   attempted problems, missing scores, cap hits, exclusions, and spent energy.
4. Integrate identical stamped spans at each boundary, preserving calibration,
   edge, meter, and battery uncertainty separately from sampling uncertainty.
5. Produce all predeclared estimates, floors, bounds, sensitivities, and
   unavailable-result reasons. Release the weight map only under REG §6.
6. Print the fixed report inventory (§8), including nulls, missingness and
   deviations. A failed gate never silently suppresses an unfavorable row.

F's unit is a **problem block**, containing its one attempt per arm. T's
unit is a **reference-sequence cluster**, containing its edited/base and
A/A′ quads. P's unit is a balanced fill/random quad, within one geometry.
Tokens, power samples, two copies within a quad, and repeated quads on the
same reference are not independent replicates. Within-session inference
does not estimate between-session variation; report sessions separately.

## 2. Measurement variables and systematic uncertainty

For member i and boundary b, let `E_ib` be gross J over `[start_i, end_i)`.
Use interval-average power over its supported overlap, with the approved
alignment method. `E_i,DC = E_i,cable + E_i,battery`; discharge is positive,
charging negative. Rails are CPU+GPU+ANE under the recorded rail manifest.
`E_i,rest = E_i,DC − E_i,rails` on the same span. No independent DRAM or
memory-controller attribution is implied.

Let `u_ib` bound member i's non-averaging systematic error. The calibrated
edge-shift envelope, meter alignment/coverage, signed battery uncertainty,
and any approved additional terms are propagated conservatively. Sum terms
unless the approved local calibration demonstrates and pins their dependence;
do not put conservative bounds into an SD or standard error. For rest,
use `u_rest ≤ u_DC + u_rails` unless a validated joint method is pinned.
Unknown required terms yield an unavailable bound, not zero uncertainty.
Local calibration must determine these methods; this draft supplies no new
numeric acceptance values.

For a linear estimate `theta = sum(w_i E_i)`, a conservative bound is
`B_theta = sum(abs(w_i) u_i)`. Average across repetitions only with those
weights; shared systematic error does not receive another `1/sqrt(n)`.
If `[L, U]` is its sampling CI, the decision interval is
`I = [L − B_theta, U + B_theta]`. Both intervals and B print. Deterministic
floor gates remain active **alongside** this widening; do not remove either
as double counting (D-078 and the local accepted successor methodology).

For ratios, propagate energy envelopes through the numerator/denominator
with conservative endpoint arithmetic. No ratio is issued if its energy
denominator's lower endpoint is nonpositive. Counts and correctness uncertainty
are treated separately below. Runtime-observed token counts are required;
configured caps are not denominator evidence.

## 3. F: behaviour and energy per correct answer

For arm a on its eligible set S of n problems, record `C_ia ∈ {0,1}`,
committed output count `D_ia`, prefill prompt count `P_ia`, decode step count
`K_ia = max(D_ia − 1, 0)`, cap indicator, and energies. D includes any
committed terminal token; stop-token semantics are frozen in the manifest.
All arms count tokens the same way. Correctness follows REG §3, including
wrong-at-cap. Abort/missing-score cases remain separate missing outcomes.

| Estimand | Estimator |
|---|---|
| Primary EPC at DC | `EPC_a = sum_i E_ia,DC / sum_i C_ia`; ratio of totals, never the mean of correct-only energies |
| Primary edited/base ratio | `R_EPC = EPC_F1 / EPC_F0` on the same complete F0/F1 set, when both have successes |
| Mean J/problem | `mean_i E_ia,b` |
| Tokens/answer, accuracy, cap-hit rate | `mean(D_ia)`, `mean(C_ia)`, `mean(cap_ia)` |
| Request J/output token | `sum_i E_ia,b / sum_i D_ia`; includes prefill and sampling overhead |
| Decode J/step | `sum_i E_decode,ia,b / sum_i K_ia`; only if phase support and realized counts are valid |
| Comparator contrasts | F1−F2 and F1−F3, with EPC ratios and the same secondary metrics; F1−F0 remains the primary comparison |

Use complete pairs for each contrast; report exactly which set each estimate
uses. The individual-arm values printed alongside a contrast use that same
set. Also print all-arm complete-set sensitivities. No loss of one arm may
change another arm's denominator without an explicit roster label.

**Correctness-limited uncertainty.** Resample entire problem blocks, jointly
across compared arms, 10,000 times with a frozen analysis RNG seed. Recompute
ratios of totals on every draw. Report percentile 95% intervals for EPC,
its ratio, and tokens/J-token ratios, plus raw correct counts and a 95%
Clopper–Pearson interval for each arm's accuracy. The binomial interval is
descriptive under an exchangeable-problem interpretation; the sample is a
subset without replacement, not independent repeat generations on each item.
Inference concerns this problem-selection/sampling protocol, not arbitrary
benchmarks. Show raw problem values as well as aggregates.

If an arm has zero correct answers, EPC is `+infinity` (positive energy,
zero successes), and a finite edited/base improvement ratio is **not
estimable**. During bootstrap, keep zero-success draws: their EPC is
`+infinity`; for R_EPC use 0 when only base has zero successes, `+infinity`
when only edited does, and unidentified when both do. If any both-zero draw
occurs, withhold the ratio interval as unstable/unidentified rather than
dropping draws or adding pseudocounts. State the zero-success draw frequency.
An infinite endpoint remains infinite. A degenerate bootstrap at observed
all-zero/all-one correctness is not evidence of exact population accuracy.
The binomial interval and absence of a finite EPC statement must remain visible.

For every bootstrap draw also compute conservative energy-envelope endpoints
using that draw's same success counts, preserving zero-success endpoints.
Use their lower/upper percentile endpoints for the widened interval and print
it beside the sampling-only interval. Never compute an EPC interval by
dividing an energy-only CI by a fixed point accuracy. These bootstrap
intervals are estimation summaries in a small
pilot, not calibrated superiority tests. Do not declare a Pareto improvement
from their marginal endpoints. No primary hypothesis test or p-value is
assigned to F-EPC; the primary role denotes the scientific target.

For paired mean-energy/token differences use Student-t 95% intervals on
problem differences. A permutation sensitivity follows the actual randomized
within-problem arm-order scheme for an appropriate sharp-null contrast;
do not treat it as an exact test of equal EPC alone. With fewer than six
exchangeable blocks mark that sensitivity not run. Report an influence
analysis for n≤10, flagging any sign, floor, or interval-class change; outliers
remain in the estimate. The same rule applies to T/P below.

## 4. T: fixed-token estimand, null, equivalence, and upper bound

Let `barE_j1,b` and `barE_j0,b` be the means of the two edited and two base
members of reference j's ABBA/BAAB quad. Form

    d_jb = barE_j1,b − barE_j0,b
    r_jb = d_jb / barE_j0,b
    theta_b = mean_j d_jb             [J per reference replay]
    rho_b = mean_j r_jb               [dimensionless]

These are **equal-reference** means. Do not replace rho by a token-weighted
ratio or ratio of mean energies; those are separately labelled sensitivities.
The six/six selection is stratified on cap status, so the primary describes
that reference selection, not the natural prevalence of edited cap hits.
If deficits change the selected mix, print it; do not weight to recover an
unobserved population. D−1 decode calls, cache/state reset and reference-token
identity must pass before calling this a weight-only contrast.

For n unique reference clusters, use paired t sampling intervals
`theta ± t_(.975,n−1) SD(d)/sqrt(n)` and likewise for rho. Report sample
SD and a cluster bootstrap sensitivity. If repeated quads are later approved,
average within reference first. With one quad per reference, uncertainty
mixes reference heterogeneity and measurement noise; the two repetitions per
side do not double n. Respect n≥5 and the n≤10 influence rule.

For each A/A′ quad define `z_jb = mean(A′) − mean(A)` with the identical
orientation/placement convention and its own mean and interval. Print both
z and d. The primary is the raw d contrast with its local null floor and
placement control. Do **not** subtract the null mean after seeing results.
`mean(d_jb − z_jb)` is a paired, explicitly secondary diagnostic with all
its uncertainty propagated. A systematic non-null A/A′ prevents a clean
edit attribution; do not hide it through correction. The numerical null
acceptance rule (including its interval, floor, and placement-bias allowance)
is a required prospective fill in OPEN[A-2]. Until it is fixed and validated,
there is no passing null gate. Any allowed residual placement-bias envelope
must also widen d and r; a passing null is not permission to set bias to zero.

Let `F_b` be the frozen local `max(absolute floor, comparative floor)` in J
for this metric/window and design. Let `F_rel,b` be its conservatively
propagated relative counterpart on these units, with its method pinned before
outcomes. Estimate-level absolute/relative floors, their provenance and
scaling are `OPEN[A-2]`; no historical phase/DC number is automatically F_b.
An unknown required floor prevents an inferential classification.

**Primary test.** T-DC equivalence is the sole confirmatory test proposed
for this pilot: family `ASTRA-T-DC-EQ-v0`, m=1, alpha=0.05 (Holm with one
member). The hypotheses are `H0: rho_DC ≤ −0.001 or rho_DC ≥ 0.001`,
`H1: −0.001 < rho_DC < 0.001`. TOST requires the **90%** t sampling interval,
widened by the relative systematic envelope, to lie strictly inside
`(−0.001, +0.001)`. Both one-sided tests must pass; their maximum p-value
is the TOST p-value. With bounded systematics test the worst allowed shift,
not only the point estimate. Also require `F_rel,DC < 0.001`, valid local
A/A′ evidence, and matched replay path. Failure of a floor/null/path gate
cannot be overruled by a small statistical p-value. Print the 95% interval
as the primary uncertainty display even when the 90% TOST gate passes.

The target is ±0.1% **at DC**, not automatically at the GPU rail. Equivalence
on other boundaries is descriptive against their frozen margins, without
confirmatory tests or cross-boundary success claims. No multiplicity is
spent on F estimation or descriptive secondary rows; their intervals are
marginal and not simultaneous. Adding confirmatory comparators requires a
prospectively revised family/registry (Holm for a small family), not selection
of the best-looking endpoint after collection.

**Upper bound regardless of equivalence.** From a valid widened 95% interval
`[L_b,U_b]`, print `U_abs,b = max(abs(L_b), abs(U_b), F_b)` in J; from the
relative interval print `U_rel,b = max(abs(L_rel,b), abs(U_rel,b), F_rel,b)`
as a percentage. The floor is a conservative lower limit on reported
resolution, not itself a confidence interval. State both sources of width.
These bound the magnitude of the **mean contrast**, not each sequence's
effect or individual edited weights' power. Preserve signed intervals too.

Below-floor d is `not_resolvable`; above-floor d whose widened interval
includes zero is `unresolved`. A widened interval excluding zero above the
floor is a resolved **execution-energy contrast** requiring diagnosis, not
automatic evidence of transistor switching. A nonsignificant difference is
not equivalence. Invalid required evidence means `not_estimable`; unknown
uncertainty never becomes a numerical bound. No p-value or upper bound
triggers extra collection.

**Synthetic illustration.** If a relative estimate is 0.00002, its 95%
sampling half-width is 0.0004, its systematic envelope is 0.0003, and its
local relative floor is 0.0002, the widened interval is
`[−0.00068, +0.00072]` and U_rel is 0.072%. This is an illustration only;
it is not an ASTRA forecast and does not by itself test null validity.

## 5. P: synthetic ladder and rail/DC interpretation

For each geometry and each fill v versus random, compute one side-mean
energy difference per ABBA/BAAB quad as in T. Report mean J/dispatch and
W contrasts, paired t 95% intervals, locally calibrated floors, widened
intervals, durations, GPU clock/residency, kernel identities, and null values.
J/GB is optional descriptive logical-byte normalization and never an assumed
hardware traffic measurement. Decode-like and GEMM results are separate;
do not pool them or infer one regime from the other.

Primary instrument reading uses the **predeclared zero-versus-random**
contrast in each geometry; other fills diagnose alternatives. All are
descriptive instrument estimates. If a later confirmatory ladder is wanted,
enumerate its full family prospectively; do not select the strongest fill
and quote an unadjusted detection. No monotone sparsity/entropy response or
sign of the zero-fill contrast is assumed.

A matched-state operand interpretation first requires fixed work/path,
residency, comparable elapsed dispatch time and GPU frequency within
`OPEN[A-3]` tolerances, and a valid A/A′ null. Then print the following
boundary-specific descriptions:

- **Both resolve:** DC and GPU-rail widened intervals exclude zero beyond
  their respective floors, with consistent signs. This supports response at
  both boundaries, without identifying the rail's internal implementation.
- **DC resolves, rail equivalent:** DC clears its floor; the rail's widened
  equivalence interval lies inside its separately justified frozen margin
  and its floor is smaller than that margin. This demonstrates a sensitivity
  mismatch for this contrast; off-rail load or modelled telemetry may explain it.
- **Neither resolves:** print both upper bounds. Only passing equivalence
  gates permit "flat within X". Otherwise say "not resolved at these bounds".
- **Other:** rail-only detection, unknown DC, a wide rail interval, opposite
  signs, or failed matched-state/null checks are explicitly inconclusive or
  discordant. Print results; do not classify them by whichever meter is finer.

These classifications describe instrument validation, not a hard gate that
discards F. Failed sensitivity limits T's mechanistic interpretation; a valid
DC confidence bound may still be reported as a boundary-specific bound.
If timing or frequency changes, report both energy and time as a combined
data-dependent execution effect; no pure fixed-work switching conclusion.

## 6. Token/context explanation, not a causal mediation percentage

Fit fresh coefficients on a separately frozen calibration set, disjoint from
the scored F problems and software smoke, using the same model, precision,
runtime, and boundary, including F's sampling/host overhead policy. The
calibration design and holdouts are
`OPEN[A-4]`; no coefficients from ALIGN's larger MoE transfer by assumption.
Proposed boundary-specific gross energy model:

    Ehat = beta0 + betaP P + betaD K + betaC sum_(t=1..K)(P+t)

P is realized prompt tokens and K=D−1 decode calls. The context exposure
term captures growing attention state in the hybrid; recurrent fixed-state
cost is absorbed in decode cost. Specify full-rank calibration lengths and
holdout coverage through 32k before fitting; a rank-deficient or out-of-range
fit is reported unavailable. Fit ordinary least squares with the fixed terms,
one coefficient set per boundary, without stepwise selection or an arm term.
Check held-out prediction error. Freeze coefficients before reading F
contrasts. Propagate calibration uncertainty with calibration-block resampling
separate from the paired F resampling; do not reuse scored observations for
both fit and apparent explanation. Do not add elapsed time to this model:
that would absorb part of the energy effect it is meant to explain.

For F1−F0, report `DeltaE = mean(E1−E0)`,
`DeltaEhat = mean(Ehat1−Ehat0)`, and
`residual = DeltaE−DeltaEhat`, with intervals and all boundaries named.
Only if `abs(DeltaE)/mean(E0) > 0.05` report the descriptive share
`1 − residual/DeltaE`; retain values outside [0,1], and withhold an interval
if its denominator uncertainty includes zero. This share is neither a causal
mediation estimate nor a hypothesis that ≥90–95% must be explained. A model
failure does not change F/T exclusions, sample size, or stopping.

At standardized replay procedure E, the identity on the **edited** reference is

    E(W1,s1) − E(W0,s0)
      = [E(W1,s1) − E(W0,s1)] + [E(W0,s1) − E(W0,s0)].

T samples the first bracket; it includes downstream activation/recurrent
value changes and any remaining timing effects, not only toggles in the
edited tensors. The second bracket is not directly measured here. F uses
free-running sampling and a different sequence distribution, whereas T
omits that sampling work and balances reference cap strata. Thus subtracting
T's mean from F is **not** an exact experimental decomposition. Report the
two channels and model residual honestly; no "entirely behavioural" claim
can follow just from a narrow GPU-rail interval.

## 7. Compact analysis registry (proposed, unfilled)

These rows follow the [analysis-plan contract](../../contracts/analysis_plans.md).
They are not a frozen machine-readable registry. No L2/L3 reader-facing
claim is licensed until the local evidence and registration review exist.

| Required field | F-EPC | T-DC |
|---|---|---|
| Plan ID / consumer | ASTRA-F-EPC-v0 / edit frontier | ASTRA-T-DC-v0 / fixed-token bound |
| family_id; claim_role | ASTRA-F-EST-v0; primary estimation | ASTRA-T-DC-EQ-v0; primary |
| selection_scope | F0/F1, frozen 40-problem set, bf16, 32k, stated sampler, one MBP | Edited-minus-base, 12 selected edited sequences, equal-reference whole-replay DC |
| multiplicity_rule | No confirmatory test; marginal estimation intervals; no superiority verdict | Holm m=1, TOST alpha=.05; no secondary boundary promotion |
| Metric/window class | Gross request DC J per correct answer | Gross request replay DC J and relative difference |
| Unit/dependence | Problem block, all arms resampled jointly | Unique reference cluster, paired quad side means |
| Estimator | §3 ratio of totals; pair-specific common roster | §4 means of signed/relative paired differences |
| Inclusion/exclusion/waivers | REG §5, frozen reason catalog; no outcome waivers | Same, plus token/path/state/null evidence; no outcome waivers |
| Order/blocking/covariates | Randomized within problem; no fitted arm covariates in primary | Balanced ABBA/BAAB; no clock regression to manufacture primary significance |
| Floor gate | Local request `max(abs,cmp)` and propagated systematic/accuracy uncertainty; OPEN[A-2] | Local replay `max(abs,cmp)`, systematic envelope and null validity; OPEN[A-2] |
| MDE/n/top-up | 40 proposed; correctness counts limit precision; no replacements/top-ups | 12 proposed; local SD/MDE/power at seal; no replacements/top-ups |
| Denominator provenance | Pinned checker scores and runtime-observed tokens on the same kept set | Measured base J for r; realized token stream; no cap-as-count fallback |
| Holdout cells | No L3 claim; separate model calibration/holdouts only | Not applicable |
| Ceiling/forbidden upgrade | Conditional pilot estimation; no universal Pareto/causal capability claim | Conditional DC bound/equivalence; no exact-zero or per-weight claim |
| Disqualifiers | Zero successes: infinite EPC/no finite ratio; missing scores/energy; n<5 inference withheld | Missing local floors/bounds/null/path evidence; n<5; margin below floor |
| Manifest/bundle hashes | OPEN[A-1], OPEN[A-4], OPEN[A-6]; filled before seal/release as appropriate | Same plus selected reference manifest, A/A′ and calibration hashes |

Secondary rows (all descriptive, no confirmatory tests) enumerate exactly
F1−F2 and F1−F3 with EPC, accuracy, cap hits, tokens/answer, J/problem and
request J/token; F1−F0 secondary metrics; T GPU/summed rails/IOReport/rest,
time/frequency and null-corrected sensitivity; P's four non-null fill/random
comparisons plus A/A′ in each of two geometries; and the whole-MLP zero
control on its frozen subset. Runtime availability may make a row unavailable,
but cannot replace it with an unlisted search. Any extra model, strength,
cap, subset, metric, covariate model, or best-fill claim is exploratory.

## 8. Report, deviations, and verification before use

The future output must include:

1. Status, frozen design/analysis/code hashes, stack and meter identities,
   named boundaries, release inventory, and the applicable deviation log.
2. Attempted/kept F problems, scores, cap hits, missingness, and the complete
   EPC/frontier table, with bootstrap zero-success counts and infinite values.
3. Every T reference's length/cap stratum and d/z values; mean, SD, 95% CI,
   systematic bound, widened interval, floors, absolute/relative upper bound,
   TOST outcome and gate reasons. State whether ±0.1% DC was established.
4. P's full ladder, A/A′ and zero-control outcomes, matched-path checks,
   DC/rail interpretation, and all inconclusive cases.
5. Gross and available request idle-subtracted sensitivities, raw points,
   small-n influence and block-resampling checks, token/context holdout
   performance and explanation residual, without selecting favorable rows.
6. Limits: single machine/window, conditional cap/reference distribution,
   imperfect transcript blinding, small correctness counts, and separate
   physical-boundary sensitivity. No data-dependent extension of the roster.

Apply REG §8's prospective amendment policy. No observed F/T/P outcome may
repair the rules on its own data. Neither a measurement null nor a successful
equivalence test closes a hardware gate outside this named stack.

Before use, the lead must validate future reducers on **synthetic** bundles:
known J integrals and quad signs in both orientations; battery charge and
discharge; widened intervals that cannot shrink a systematic term; meter
gaps; missing-pair/quad propagation; zero-correct and infinite bootstrap
endpoints; mean-of-ratios versus ratio-of-means; floor/CI/TOST boundary cases;
and deterministic reference selection without energy access. Native MLX
acceptance is listed in REG §8 and must run outside this sandbox after
authorization. No such reducer, package, test command, native run, or live
validation is claimed by this documentation-only deliverable.
