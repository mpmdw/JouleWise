# Revision 7 ruling — independent delta7 review, Sol2

**Verdict: SIGN, at the design-ruling level.** Revision 7 repairs the
spawn-worker defect and withdraws the erroneous all-scenarios power claim.
The prospective sizing/claim-narrowing rule is defensible. The honest gate
is an acceptable **gross-inflation screen**, with the limitations below;
it does not certify FPR ≤ .05. G12 and the native/capacity gates remain
unexecuted. This signature supplies neither a second seat nor the lead's
signature, and authorizes no measurements or model downloads.

Seat `sol2`; branch `align/2026-11-08-v5design-ruling-delta7-sol2`;
candidate `4078c08509d81d61818dc477e1368ef6672b3e5f`.
The candidate ruling, simulator and supplied tests are unchanged.
Read the revision-6-to-7 diff, operative §§4–6 and dispositions, my prior
delta5 review/simulator, M0, orchestration, AP and D-062. The explicit user
brief selects this synthetic review ahead of the ordinary queue and forbids
coordination-state updates, network, real data and the full suite.

## Independent evidence and reproducibility

[`power_sim_sol2.py`](power_sim_sol2.py) is restored **byte for byte** from
`origin/align/2026-11-08-v5design-ruling-delta5-sol2`, SHA-256
`1ed19bfb3a63337ccc53ecd85e982858eafa4e57d5a5e5c35c9f18f2ebe2760e`.
It was independently written before inspecting the author's sampler in
the prior review; I have not changed its law to match this revision.

[`power_delta7_sol2.py`](power_delta7_sol2.py) provides sequential replay,
roster resizing, gate arithmetic and worker-transport checks. Its independent
mode uses the prior simulator's actual common scores, six alarms, adverse
completion, predictable stakes, beta window shocks and literal H4 subset.
At 28 windows it reproduces the previous fixed-law curves exactly.
Resizing continues the phase cycle with every cell represented. H4=10 is
an abstract, preassigned promotion of two covers, not a replacement for
G12's final class roster. The old simulator's hardcoded capability and
strong-label flags are **not used** for resized designs; only the four
rejection flags/conjunction are used, and effect denominators are corrected.
The new honest gate is audited separately.

The author comparison calls `jobs_all()` and `simulate()` sequentially,
with the exact candidate seeds/parameters, rather than starting its
unbounded default pool. Power rows have 2,000 replications. Intervals are
pointwise Wilson 95% Monte Carlo intervals, not a simultaneous power
guarantee. The six-rule honest-gate simulation uses 20,000 replications.
All inputs are synthetic, all sampling is one process; the transport test
alone starts one spawned worker. No production modules, measurement data,
weights, network or live telemetry are involved.
Complete stdout is retained in
[`ruling-delta7-sol2-output.jsonl`](ruling-delta7-sol2-output.jsonl).

## Worker fix and inferential contract

The candidate source hash is
`87ef44815220ce9c37a03b9ddbc3aec4717a75d49bf39bc0e391b48161d31e04`,
matching the ruling. `r`, `miss` and `reps` are explicit job values, consumed
in `simulate()`; `r` and `miss` reach `run_stream()`, while `reps` controls
the outer loop. No parent-mutated law globals remain. The supplied test
genuinely starts a `spawn` worker and checks
the returned effective parameters. All three supplied tests pass.

My additional transport probe compares the complete serial and one-worker
spawned results, including byte-identical sorted-JSON serialization, and
checks that changing the law actually changes the result. The 64-replication
probe uses the same seed in both laws; it is a transport regression check,
not a power estimate. Both it and the prior simulator's six self-tests pass.

The stake denominator requirement `n0*s0 > 0` closes the prior edge case.
The attempt-level conditional-mean null, prefix-only stake, fixed horizon,
adverse lower bound and exact Holm remain as previously reviewed. H4
demotion now explicitly means exploratory/outside the confirmatory family,
so Holm over three is correct **only if frozen prospectively**. A failed or
degenerate H4 during the registered four-test campaign still stays at p4=1;
it cannot be dropped after outcomes. No new inferential defect was found.

## Corrected MDE and window ladder

The exact author-job replay reproduces the corrected MDEs and null row.
The independent MDEs reproduce my previous branch, including the already
disclosed one-grid-step differences. Each vector is H1/H2/H3/H4/conjunction;
these are input-signal grid crossings, not measured detector effects.

| Law | Author MDEs | Independent MDEs |
|---|---|---|
| Baseline, rho=0 | .07/.07/.07/.08/.08 | .07/.07/.07/.08/.08 |
| Baseline, rho=.05 | .07/.07/.07/.09/.08 | .08/.07/.08/.08/.08 |
| Baseline, rho=.15 | .08/.08/.08/.09/.09 | .08/.08/.08/.09/.09 |
| Stress r=miss=.05, rho=.30 | **.12/.12/.12/.14/.14** | **.12/.12/.12/.14/.13** |

Verbatim summary output of the replay (author rows parsed from its JSON):

```text
AUTHOR MDE 0 0.02 [0.07, 0.07, 0.07, 0.08, 0.08]
AUTHOR MDE 0.05 0.02 [0.07, 0.07, 0.07, 0.09, 0.08]
AUTHOR MDE 0.15 0.02 [0.08, 0.08, 0.08, 0.09, 0.09]
AUTHOR MDE 0.3 0.05 [0.12, 0.12, 0.12, 0.14, 0.14]
NULL 0.0005
```

Verbatim independent MDE output:

```json
{"H1": 0.07, "H123": 0.08, "H2": 0.07, "H3": 0.07, "H4": 0.08, "MDE": "fixed-rho0"}
{"H1": 0.08, "H123": 0.08, "H2": 0.07, "H3": 0.08, "H4": 0.08, "MDE": "fixed-rho05"}
{"H1": 0.08, "H123": 0.09, "H2": 0.08, "H3": 0.08, "H4": 0.09, "MDE": "fixed-rho15"}
{"H1": 0.12, "H123": 0.13, "H2": 0.12, "H3": 0.12, "H4": 0.14, "MDE": "fixed-stress"}
```

At nominal signal .10 under stress, full-Holm powers are:

| Option | Author H1 / conjunction / H4 | Independent H1 / conjunction / H4 |
|---|---|---|
| 28 windows, H4=8 | .6835/.5155/.5575 | .6760/.6160/.5820 |
| 28 windows, H4=10 | .6945/.5330/.6400 | .6760/.6205/.6435 |
| 36 windows | .8035/.6530/.6600 | .7730/.7255/.6955 |
| 44 windows | .8860/.7830/.7740 | .8665/.8335/.7880 |
| **52 windows** | **.9285/.8615/.8250** | **.9150/.8915/.8585** |
| 60 windows | .9525/.9105/.8995 | .9410/.9260/.9065 |

Thus the **frozen author law selects +24** exactly as stated. My coupled
law would first meet the H1/conjunction target at +16; H4 remains slightly
below .80 there, and is secondary to sizing. At +24 both laws meet all three
point targets. My stress conjunction at +16 is .8335, MC interval
[.816537,.849184]; at +24 it is .8915 [.877111,.904387]. This is not an
implementation disagreement: H1 and H3 are identical in my fixed-score toy
law, whereas the author draws distinct streams given its window shock.
Its ladder is more conservative for the conjunction in this comparison,
not a guarantee for every possible coupled score law.

For the **intermediate law**, author H1/conjunction/H4 changes from
.8550/.7240/.7315 at 28 to .9385/.8610/.8530 at 36. My coupled law changes
from .8210/.7785/.7405 to .9130/.8860/.8540. **Both select +8**.
The exact author's unrounded values agree with the ruling to display
rounding (some values end in .0005).

Missingness reduces the final adverse-bound effect: independent stress
signal .10 attains about .0925, and signal .14 about .1315. The table's
“Delta” is therefore a planning-law coordinate, as in the prior review,
not a fitted post-missingness effect. G12 must state both coordinates.
At signal .11, the prior independent evidence already showed underpower
near an attained .10 effect, so this distinction does not erase the stress
failure or justify reverting to 28 windows.

## Sizing judgment and registration obligations

**Prospective, rather than test-data peeking:** the nuisance-rate estimates,
power rerun, selected counts, prior/stake, full-stage law, costs and any
narrowed design MDE are fixed at G12, before calibration and test outcomes.
That satisfies D-062. Simulating the menu against development data does not
spend confirmatory alpha. The fallback must mean registering/reporting the
larger *design MDE*, never claiming that an observed effect is at least that
size merely because the design was powered there. Outcome-dependent growth
or later re-promotion remains prohibited.

The .15 ICC floor and .30 higher tier are sensible **planning stresses**,
not confidence bounds on actual ICC. They avoid treating a noisy near-zero
estimate as independence, but .30 is not conservative if development supports
larger dependence. The ICC here is rescue-indicator ICC, not automatically
delta ICC or calibrated-detector ICC. G12 must freeze the estimator, channel/
pair/class aggregation and uncertainty treatment, and address high or poorly
estimated ICC in its required development-calibrated, coupled full-stage
rerun. The tier rule alone cannot certify 80% power under arbitrary dependence.
As a bounded check of the low-rate override, my fixed law at r=miss=.02,
28 windows gives H1/conjunction/H4 .9040/.8885/.8510 at rho=.30 and
.8815/.8535/.8210 at rho=.40. That supports the baseline branch under these
toy stresses, without turning the tier into an ICC upper confidence bound.

Likewise, two separate one-sided 80% rate UCBs are a modest planning cushion,
not simultaneous 80% coverage of all nuisance parameters or 80% assurance
that the selected design is adequately powered. G12 must specify a construction
appropriate to adaptive/clustered development data and avoid pooling away a
high-regression contrast. As an iid illustration only, zero events in 80
trials gives an exact one-sided 80% upper bound .019917. The low-rate branch
therefore needs evidence; it is not selected merely because a point estimate
is near .02. “Stress → +24” describes **input bounds** r=miss=.05, rho=.30;
if the *true* rates are .05, their estimated upper bounds will often be higher,
and the rule may choose +32 or narrow the MDE.

The ruling expressly requires G12 to simulate calibration and honest-gate
stages. That requirement remains essential, including on the low-rate
28-window branch: the r/m shortcut does not waive the full-stage gate.
Our earlier random-threshold sensitivities remain relevant; this review
does not fit a detector distribution or certify that more attack windows
will cure threshold randomness. The mandatory full-stage G12 check and
prospective narrowing prevent a claim of unconditional baseline feasibility.

The stress increment independently costs
`24 * [48*900/3600 + 1 + 22*.4*900/3600 +
22*(30000/600 + 1000/35)/3600] = 376.323810` base hours,
or **470.404762 reserved hours**. The cap-inclusive total is about
**1,386.3 reserved hours** at 900 s, s=1. That is conditional funding, not
observed available capacity; the increment alone consumes about 29.4 days
at 16 gross h/day. The dated CAP schedule must pass or the claim narrows.
The fallback is scientifically honest and does not silently fund an
impossible calendar.

**Carry the selected roster into every G12 registration field.** The draft's
336/224 attacks and **22/280 honest** bar describe the baseline design.
At 52 full windows there are 624/416 attacks and 520 honest members. Freeze
whether the gross-inflation screen uses a preassigned 280-member subset or
a prespecified cutoff for all 520; do not accidentally apply an absolute
22-alarm ceiling to all 520 (that falsely fails a nominal iid rule 75.46%
of the time). Freeze the capability denominators, phase totals,
honest bound and release ledger consistently as part of the already-required
roster/strong-conjunction registration. This is an implementation obligation
before data, not authorization for a later outcome-dependent change.

## Honest-gate judgment

For **iid honest members** at constant nominal FPR .05, exact binomial
arithmetic gives:

| Gate at n=280 | Per-rule false fail | Any fail, six independent rules |
|---|---:|---:|
| Old, ≤14 alarms | 42.9540% | 96.5537% |
| New, ≤22 alarms | **1.4327%** | **8.2942%** |

With arbitrary dependence **between rules** but the same binomial marginal
counts, the new any-rule false-fail probability lies between 1.4327% and
the union bound **8.5963%**. Six independent rules are a benchmark, not the
actual shared-channel structure. The old ~10% all-six pass rate cited in
the ruling belongs to my coupled score law; it is not a universal consequence
of nominal FPR.

The new simulation draws all six rules from the prior simulator's common
four scores and fixed population cutoffs, so every rule's true marginal
FPR is .05. With 20,000 trials:

| Honest-member law | Old all-six pass | New all-six pass | New any-rule false fail |
|---|---:|---:|---:|
| iid members, coupled rules | .10180 | **.92830** | **.07170** |
| Clustered members, coupled rules | .10490 | **.85755** | **.14245** |

The clustered law copies one shared score vector with probability .3,
separately for the five honest members of each pair/window. This gives
within-group alarm ICC .09 while preserving nominal marginal FPR. New
per-rule false-fail estimates range from .02985 to .03275. The new all-six
pass intervals are [.924642,.931794] iid and [.852637,.862325] clustered.
These are finite-law checks, not generic dependence guarantees.

The 1.43% binomial calculation does **not** hold under arbitrary dependence
between honest members. For example, 28 independent dates, each with ten
identical Bernoulli(.05) alarms, have a 16.2665% per-rule false-fail rate at
22/280. This is why the required development-calibrated honest/calibration
simulation and dependence-valid bound cannot be replaced by iid arithmetic.

As an inflation screen, ≤22/280 is reasonable: at actual iid FPR .075, .08,
.10 and .15 it rejects a rule with probabilities **.3562, .4789, .8649 and
.999775**. It is weak against modest inflation and strong against large
inflation. Do not describe passing it as 95% confidence that FPR≤.05, or
as a distribution-free acceptance test. The explicit “gross-inflation”
wording, nominal calibration target, point FPR and reported upper bound
keep the label honest. “Strong result” must retain that operational meaning,
without being paraphrased as detection at a certified 5% operating FPR.

The registered Hoeffding formula is executable and correct for the average
conditional honest alarm probability, with fixed positive lambda and alpha=.05.
It remains valid with adapted dependent Bernoulli outcomes; its coverage is
per rule, not simultaneous across six. At n=280 the width is
**.0731404260**, and even a passing 22-alarm sample reports an upper bound
**.1517118546**. That looseness must remain visible. The construction is
not a bound on each member/date's FPR.

No additional design blocker was found. The exact nuisance estimators,
expanded honest roster and native feasibility remain G12/lead work, not
completed facts. The next step is for the lead to combine the two independent
seat verdicts, then carry these existing gate obligations into registration.

## Verification and handoff

- Supplied `test_ruling_power_sim`: **3/3 pass** (0.088 s).
- Prior independent simulator `--self-test`: **6/6 pass** (0.038 s).
- Independent curves/ladder, exact author jobs, honest gate and ICC probes:
  completed sequentially; complete stdout linked above.
- Final 64-replication worker probe: `spawn_equals_serial: true` and
  `canonical_json_byte_equal: true`; effective stress r=miss=.05.
- All four simulation/test source files parse; staged diff whitespace checks pass.
- No full suite, network, measurements, model weights or MLX execution.
  No production/native code changed, so this review introduces no native
  test to replay. The lead still owns native G4–G9 qualification and G12's
  fully calibrated power/registration gates outside this sandbox; none is
  represented as passed here.

Exact commands, changed files, authority boundaries and remaining uncertainty
are recorded in the [run report](../../../run_reports/2026-11-08-v5-ruling-delta7-sol2.md).
