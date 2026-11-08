# Revision 7 ruling review — Sol1

**Verdict: SIGN.** Revision 7 repairs the spawn-worker defect, reproduces
the corrected power deficit, and supplies a prospective sizing-or-narrowing
decision with explicit capacity gates. The new honest gate is defensible
as a **gross-inflation check**, with the reported point rates and conditional
upper bounds. It does not establish FPR ≤0.05. No remaining finding blocks
this draft ruling; G12 certification and the lead's signoff remain separate.

Candidate: `4078c0850`, revision 7. Seat: **sol1**, branch
`align/2026-11-08-v5design-ruling-delta7-sol1`. One independent seat;
the other seat's delta7 review was not consulted. All computations below
are synthetic, standard-library-only, with no measurements, models,
network access or hardware validation.

## 1. Worker fix and corrected table

The author's sampler SHA-256 is
`87ef44815220ce9c37a03b9ddbc3aec4717a75d49bf39bc0e391b48161d31e04`,
matching §4e. `r`, `miss` and `reps` now travel in each job dictionary and
are read inside `simulate`; `run_stream` receives the actual law parameters.
No parent-mutated law globals remain. The explicit-spawn transport unittest
passes. I also compared a complete 2,000-replication stress result under
one spawned worker and sequential execution: every returned value agrees;
changing to the baseline law with the same seed changes the powers.
The echo test is therefore supported by an actual computation comparison.

The complete author grid, with its published seeds and 2,000 replications
per row, reproduces the draft's table and ladder. Selected **verbatim
output** from [the author replay](delta7-author-sol1.txt):

```text
AUTHOR mu rho windows h4pw r miss | H1 H2 H3 H4 | H123
0.10 0.30 28  8 0.050 0.050 | 0.6835 0.6970 0.6965 0.5575 | 0.5155
0.10 0.30 36  8 0.050 0.050 | 0.8035 0.7890 0.7940 0.6600 | 0.6530
0.10 0.30 44  8 0.050 0.050 | 0.8860 0.8785 0.8810 0.7740 | 0.7830
0.10 0.30 52  8 0.050 0.050 | 0.9285 0.9265 0.9300 0.8250 | 0.8615
0.10 0.30 60  8 0.050 0.050 | 0.9525 0.9515 0.9540 0.8995 | 0.9105
0.10 0.30 28 10 0.050 0.050 | 0.6945 0.7015 0.6915 0.6400 | 0.5330
AUTHOR_GRID_MDE r,miss,rho=(0.05, 0.05, 0.3): [0.12, 0.12, 0.12, 0.14, 0.14]
SPAWN sequential == spawned entire result; same-seed baseline != stress
AUTHOR_NULL FWER=0.0005 reps=2000
```

Thus H4 reallocation does not suffice; +8 restores H1 but not the
conjunction; +16 still misses the conjunction; **+24 is the first author-law
option meeting both primary targets**. Intermediate inputs .035/.035/.15
select +8, with H1/conjunction/H4 = .9385/.8610/.8530. The stress +24
cost independently sums to 24 × (48×.25 + 1 + 22×.1 +
22×78.6/3600) = **376.328 base h**, or **470.410 reserved h**.

## 2. Existing independent simulator

I restored [power_sim_sol1.py](power_sim_sol1.py) from
`origin/align/2026-11-08-v5design-ruling-delta5-sol1`. Its original source
SHA-256 is `23f0e40e3bbedc61d3633845bab0c23eb0b87f3680836f00ed7eb0ea72691335`.
It was originally written before reading the author's sampler. This review
adds configurable window/H4 counts and the new honest gate; it retains the
coupled score law, adverse unknown-side completion, bounded-beta shocks,
literal H4 subset, seeds and default random-number order. Twelve old/new
power rows agree exactly, including all floating-point results. Seven
bounded self-tests pass, including all extended roster counts and cell
support. The independent sampler imports no author or JouleWise code.

Each attempt still generates one side outcome and shared M/E/T/S scores;
the six rules reuse those same scores. H1/H2 rescues are disjoint, H4 is a
literal subset, and rescue ICC before missingness is exactly the requested
rho. At the stress input, the adverse mean is .95×.10−.05×.05 = .0925.
Capability is deliberately favorable (marginal side success .60), and
availability is 100%; these are planning laws, not a fitted G12 certificate.

The denser grid now tests every .01 from .05 through .15, including the
previously untested .11 and .13 points. Selected **verbatim output** from
[the independent grid](delta7-coupled-sol1.txt), with MDE columns
H1/H2/H3/H4/H123:

```text
COUPLED_GRID_MDE coupled-rho0: [0.07, 0.07, 0.07, 0.08, 0.08]
COUPLED_GRID_MDE coupled-rho05: [0.07, 0.07, 0.07, 0.09, 0.08]
COUPLED_GRID_MDE coupled-rho15: [0.08, 0.08, 0.08, 0.09, 0.09]
COUPLED_GRID_MDE coupled-stress: [0.12, 0.12, 0.12, 0.14, 0.13]
```

The baseline MDEs reproduce. The stress conjunction now crosses at .13,
power .8315 with pointwise 95% Wilson Monte Carlo interval [.8145,.8473];
the old coarser grid first crossed at .14. H4 at .13 is .7935
[.7752,.8107], so its first crossing remains .14. Update the draft's
“identical” reconciliation to explain the old grid resolution; agreement
within .01 remains sound. These intervals quantify Monte Carlo error,
not uncertainty about the real score/dependence law or simultaneous
coverage after searching the grid.

The independent sizing replay differs in conjunction power because its
rules and H4 records are coupled. At Δ=.10:

| Stress option | Author H1 / H123 / H4 | Independent H1 / H123 / H4 |
|---|---|---|
| 28 windows | .6835 / .5155 / .5575 | .6895 / .6235 / .5920 |
| H4 reallocation | .6945 / .5330 / .6400 | .6925 / .6285 / .6490 |
| 36 windows | .8035 / .6530 / .6600 | .7940 / .7400 / .6925 |
| 44 windows | .8860 / .7830 / .7740 | .8790 / .8355 / .7885 |
| 52 windows | .9285 / .8615 / .8250 | .9170 / .8935 / .8500 |
| 60 windows | .9525 / .9105 / .8995 | .9480 / .9315 / .9015 |

The coupled law first meets H1 and H123 at **+16**, not +24. The author's
+24 choice is conservative relative to this independent law, and clears
all three columns in both. It is not a law-independent minimum. Under
the independent intermediate law, the 28-window conjunction is .8020
[.7840,.8189], borderline; at 36 windows it is .8980 [.8840,.9105]. The
author's +8 choice gives a clear margin in both laws. These differences
are larger than Monte Carlo error alone for some conjunction rows; the
coupling structure matters. Full evidence is in
[the ladder output](delta7-ladder-sol1.txt).

The new gate also does **not** eliminate threshold uncertainty. In the
same old iid-calibration toy, changing only the honest gate increases
honest-gate passage from .2655 to .7595 and strong-label yield from .0470
to .1870 at nominal Δ=.10; H1 and H123 power remain .4805 and .2765.
With date-constant calibration/honest scores, gate passage is .0210 and
strong-label yield .0050. The unresolved calibration-stage G12 gate is
therefore still material, exactly as revision 7 acknowledges. These
nominal score laws are not fixed post-calibration .10 effects.

## 3. Prospective sizing, ICC and capacity

The timing is sound under D-062/AP: the inputs come from development,
the decision is made at G12 **before calibration and test outcomes**,
and the selected counts, family and fallback claim are frozen. The
80% rate UCBs are a planning cushion; their confidence level is separate
from inferential alpha and from 80% power. They are not a joint 80%
guarantee for both rates, ICC, score law and selected option.

Using .15 as an ICC floor and stepping to .30 is a sensible coarse
planning stress. It is **not an upper confidence bound on dependence**.
At G12, define the ICC estimand/estimator and its development-window
support: the sampler parameter refers to rescue indicators before
missingness, which need not equal the ICC of ternary net differences.
Sparse or near-threshold estimates need sensitivity checks. An estimate
or plausible dependence range above .30 cannot be certified by clamping
it to .30; the development-calibrated re-run must cover that law or
narrow the power claim. Rate-UCB construction also needs to respect
development clustering. These are requirements for the already-mandated
G12 certificate, not grounds to demand a new measurement campaign now.

The baseline branch must still pass that G12 calibration/honest-stage
check. Low regression/missingness alone does not cure unstable calibration
thresholds. The draft explicitly retains this gate and prospective
calibration enlargement or claim narrowing. The 470.4 h line applies to
**sizing inputs** .05/.05/.30; UCBs obtained from a finite sample with
true rates .05 can be higher and select a later rung or exhaust the
ladder. It is not a guaranteed maximum stress cost.

The capacity fallback is honest: failure to fund the selected roster
withdraws the .10/80% planning claim before data and reports the actual
28-window design MDE. At 900 s the illustrated stress GO envelope becomes
1,386.3 reserved h; no schedule feasibility has been measured here. A
larger MDE is a sensitivity statement, not a larger observed effect or
a reason to promote a negative/inconclusive result into a strong result.

H4 demotion is correctly explicit: exploratory and outside the family,
with Holm over three. It must be frozen prospectively; it differs from
keeping a degenerate H4 confirmatory with p=1 in Holm over four. Reallocation
also needs a sealed replacement class roster and re-powered mixtures at
G12. The existing all-six-cell support must survive. Reallocation can
slightly improve H1 through Holm, as the table shows; “never restores”
should be read as the conclusion for these displayed cases, not a theorem.

## 4. Honest gate and label

For 280 independent honest Bernoulli(.05) members, the exact false-fail
probability is P[Binomial(280,.05)>22] = **.01432719 per rule**.
With six independent rules the false-fail probability is .08294231
(pass .91705769). Without independence **across rules**, but retaining
the iid member law for each, the union bound is .08596314; perfect
across-rule dependence gives .01432719. Shared maxima require their own
joint calculation, rather than raising one marginal pass rate to six.

The old ≤14 gate falsely fails **.42954005 per rule** even at exactly
nominal FPR, and passes all six independent rules only .03446283 of
the time. The draft's “about 10%” concerns a correlated six-rule toy,
not a universal nominal rate. My 20,000-replication replay with shared
M/E/T/S channels, literal maxima and fixed population cutoffs reproduces
that distinction. Selected **verbatim output**:

```text
cutoff=22 per_rule_false_fail=0.01432719 six_independent_fail=0.08294231 six_independent_pass=0.91705769 six_union_bound=0.08596314
COUPLED_NOMINAL six_rule old_pass=0.1068[0.1026,0.1112] new_pass=0.9281[0.9244,0.9316]
```

Thus in this coupled nominal toy the new all-six false-fail rate is
**7.19%**, versus the old **89.32%**. The revised gate substantially
reduces that avoidable failure rate.

The new cutoff accepts point FPR up to 22/280 = .07857143. At true iid
FPR .10 its per-rule pass probability is .13509284, and at .125 it is
.00884819. This is a useful gross-inflation screen, not an equivalence
test or certification at .05. The fixed-lambda Hoeffding construction
is executable and valid for the stated average conditional rate:
width sqrt(log(20)/(2×280)) = **.07314043**, so U(22/280) =
**.15171185**. Coverage is per rule; do not silently claim simultaneous
95% coverage or a marginal/population .05 guarantee.

Arbitrary within-date dependence changes the gate's operating rate:
with 56 independent date/group draws, each repeated five times, every
member is marginally Bernoulli(.05), yet the per-rule false-fail rate is
.14744374. Six independent such rule streams fail at least one gate with
probability .61599376. This is an illustrative dependence sensitivity,
not a measured forecast. The conditional-rate Hoeffding bound retains
its stated coverage; the iid false-fail calculation does not transfer.

The strong label stays honest if its stated meaning remains: H1-H3
conditional-null rejections, capability and availability gates, plus
this **gross-inflation check**, with actual honest FPRs, per-window
rates and upper bounds disclosed. It cannot be paraphrased as “all
six rules verified at ≤5% FPR.” The stale §4b guard bullet that still
says “requires honest FPR ≤0.05 per rule” should be aligned with the
operative conjunction. This is a wording repair, not a reason to reject
the prospective change.

Full gate output is in [delta7-gates-sol1.txt](delta7-gates-sol1.txt).

## 5. Verification and handoff

Reproduction commands, outputs, changed files and limits are in the
[dated run report](../../../run_reports/2026-11-08-v5-ruling-delta7-sol1.md).
No production source, ruling text, coordination state or sealed evidence
was edited. The full suite was deliberately not run. No native MLX code
or native test was introduced; no live capability, replay, energy or
capacity gate was run. Novelty/venue verification remains open under
separate network authority. The lead should consume both delta7 seats,
apply the small wording reconciliations, and retain all G12/CAP gates
before registration or measurement.
