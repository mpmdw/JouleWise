# R24 C14 confirmation and T following the stop

**SYNTHETIC ONLY / PROVISIONAL.** Branch
`align/2026-11-08-r24-c14-confirm-sol`, base `53556a3d6`.
Task authority: the user's R24 brief installs C14 as the lead's reserve-cap
ruling and specifies T immediately after the eighth admitted window. This
report evaluates that ruling under the inherited model; it changes no
registration, production code, or coordination state.

**The “C14 stays at C10 FPR or below on every setting” claim is refuted
for T following the stop.** At b=.05, C14 increases gate-admitted FPR at
all 108 pair-mean rule/setting points (and all 324 points including each
individual pair). A fixed common horizon gives the opposite conclusion.
At b=0, the successful calibration law is cap-invariant in this model.

The [simulator](../align/v4/b3-sim/simulate_r24_c14_confirm_sol1.py) extends
the unchanged R22 sweep to C13/C14. The
[complete pair-mean table](../align/v4/b3-sim/r24-c14-confirm-table-sol1.csv)
reports qualification, `future_pass_fpr`, all-state `fpr`, paired threshold
shift versus `oracle8`, expected reserve attempts, and pointwise 95% Monte
Carlo intervals for every setting, rule, cap, and calendar. Separate
[scores](../align/v4/b3-sim/r24-c14-confirm-scores-sol1.csv) retain both pairs;
[counts](../align/v4/b3-sim/r24-c14-confirm-counts-sol1.csv) retain exact
availability and workload. Probabilities in CSVs are fractions; shifts are
residual SD units; reserve attempts are windows.

## Qualification and reserve cost

Exact qualification percentages (independent of mechanism, tau, b, and T):

| q | e | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|---:|
| .125 | .10 | 88.0489 | 96.1022 | 98.8705 | 99.7010 | 99.9259 |
| .125 | .20 | 84.2410 | 91.9460 | 94.5946 | 95.3892 | 95.6044 |
| .250 | .10 | 52.5588 | 71.3297 | 84.2348 | 91.9778 | 96.1720 |
| .250 | .20 | 50.2857 | 68.2449 | 80.5919 | 88.0000 | 92.0128 |

C14 is the first cap reaching 95% at q=.25, e=.10; it does not reach 95%
at q=.25, e=.20. Expected reserve attempts are unconditional over all
started studies, including failures and barred reserves:

| q | C10 | C11 | C12 | C13 | C14 |
|---:|---:|---:|---:|---:|---:|
| .125 | .969173 | 1.088675 | 1.127644 | 1.138930 | 1.141910 |
| .250 | 1.599548 | 2.073956 | 2.360651 | 2.518295 | 2.598507 |

These use `P[Binomial(C,1−q)≥8] × P[Binomial(56,1−e)≥39]^2`
and `sum(n=8..C−1) P[Binomial(n,1−q)<8]`. The structural probability is
shared by the pairs, not squared. Member attrition cannot arm reserves;
low m after eight admitted windows fails immediately.

## FPR, paired threshold shifts, and drift

Example: hot-correlated bars, q=.25, e=.10, tau/s_r=.8076923, maximum
rule. Risks are percent; threshold shifts are residual SD units with
pointwise 95% MC intervals. The same cutoffs serve both calendars.

| b | T calendar | Cap | future_pass_fpr | fpr | Paired threshold shift vs oracle |
|---:|---|---|---:|---:|---:|
| 0 | either | C10 | 2.965 | 6.741 | -.432 [-.437, -.427] |
| 0 | either | C13 | 2.967 | 6.744 | -.584 [-.588, -.580] |
| 0 | either | C14 | 2.968 | 6.747 | -.598 [-.602, -.594] |
| .05 | fixed 15–17 | C10 | 6.236 | 12.137 | -.391 [-.396, -.386] |
| .05 | fixed 15–17 | C13 | 5.972 | 11.739 | -.510 [-.514, -.506] |
| .05 | fixed 15–17 | C14 | 5.936 | 11.684 | -.519 [-.523, -.515] |
| .05 | after stop | C10 | 4.498 | 9.422 | -.391 [-.396, -.386] |
| .05 | after stop | C13 | 4.628 | 9.636 | -.510 [-.514, -.506] |
| .05 | after stop | C14 | 4.650 | 9.671 | -.519 [-.523, -.515] |

Here the stop-relative C14−C10 gate-risk difference is **+.1519 percentage
points [.0985, .2052]**; C13−C10 is **+.1306 [.0769, .1844]**.
With fixed T, C14−C10 is **−.3004 [−.3695, −.2313]**.

Across all 36 b=.05 settings, cap−C10 pair-mean gate-risk ranges in
**percentage points** are:

| Calendar | Cap | maximum | rank05 | literal38 |
|---|---|---:|---:|---:|
| fixed 15–17 | C13 | −.3845 to −.0679 | −.6126 to −.0969 | −1.2533 to −.2036 |
| fixed 15–17 | C14 | −.4399 to −.0699 | −.7012 to −.1009 | −1.4360 to −.2115 |
| after stop | C13 | +.0326 to +.1486 | +.0529 to +.2583 | +.1131 to +.7704 |
| after stop | C14 | +.0332 to +.1721 | +.0553 to +.2994 | +.1174 to +.8905 |

Every b=.05 point has the indicated sign, including both individual pairs.
For stop-relative C14, conservative pointwise intervals exclude zero at
28/36 maximum, 30/36 rank05, and 34/36 literal38 settings; the remaining
intervals contain zero. At b=0, C14−C10 maximum/rank05 point differences
range from −.0240 to +.0058 / −.0319 to +.0090 points; all their intervals
contain zero. These Monte Carlo fluctuations do not contradict cap-invariance.
C14's worst stop-relative b=.05 maximum/rank05 gate-risk means are
5.019%/8.463%; larger availability does not establish nominal FPR control.

## Calendar interpretation

`after_stop` uses T1–T3 at one-based positions `stop+1..stop+3` in each
qualified study. For C14, stop ranges from 8 to 14, so T ranges from 9–11
through 15–17. The oracle stops at 8. `fixed_after_C14` uses a common
15–17 horizon for all caps and the oracle. The earlier fixed 13–15 and
legacy 11–13 calculations are used only to replay old artifacts, since
they overlap potential C13/C14 calibration slots.

Exact mean T1 positions among qualified studies (the table also gives
position ranges and Monte Carlo stop-time intervals):

| q | C10 | C13 | C14 |
|---:|---:|---:|---:|
| .125 | 9.829268 | 10.127387 | 10.138355 |
| .250 | 10.238095 | 11.301871 | 11.463149 |

These follow the negative-binomial stop law truncated at the cap and do
not depend on e, since member qualification is independent of the gaps.

At b=0, the successful eight-window calibration law and FPR are cap-invariant;
small Monte Carlo differences are numerical sampling noise. Hot-correlated
bars still make that law differ from the inherited all-state oracle.
Paired oracle threshold shifts condition on a different qualification
intersection at each cap. Already-C10-qualified studies have exactly the
same thresholds, stop times, and risks for every cap under either calendar.
Both calendars reuse the same calibration thresholds; the reported oracle
shift is in absolute score units, without recentering by T's position.

For b>0, later calibration is closer to a fixed T, lowering FPR. When T
follows the stop, extra bars instead spread calibration farther back from
T, raising FPR. Under this iid model the direction follows by coupling:
conditional on stop L, the earlier seven admitted positions (and their
ages) are uniform subsets of 1..L−1. Extending L by reservoir sampling can
only increase their sorted coordinates. Accepted states, residuals, and
member losses are independent of the gaps. Thus fixed-horizon order
statistics increase, while stop-relative order statistics decrease, for
all three rank rules. Member qualification does not change the gap law.

`future_pass_fpr` conditions future windows on passing the structural gate;
`fpr` averages over all future states. Both condition calibration on the
design's own qualified studies; unavailable studies get no no-alarm credit.
Future tails are integrated with unchanged arithmetic and admission weights.
T refers to three
consecutive assigned future positions, with gate conditioning in
`future_pass_fpr`, not three future successes collected by another stopping
rule. No extra waiting time or future-state persistence is modeled.

## Reproduction and limits

Seed **202611082201**, **100,000 studies per setting**, memory chunk
**2,000**, and all **72** grid settings are unchanged: three mechanisms,
q∈{.125,.25}, e∈{.10,.20}, tau/s_r∈{0,.5,.0021/.0026}, b∈{0,.05}.
C1–C10 retain the original generator; C11/C12 retain SeedSequence
`[seed,11,12]`; C13/C14 append independent `[seed,13,14]` draws. Caps and
settings share synthetic tapes. No speed optimization or decision cache
was introduced; batching is solely unmeasured synthetic memory chunking.

Intervals use whole two-pair studies. Oracle threshold contrasts are
paired; own-population cap contrasts use the conservative Cauchy SE bound.
All intervals are pointwise 95% MC, not simultaneous or live uncertainty.
Literal38 remains exploratory at m>39. This study establishes no nominal
FPR guarantee or live gate/state validity.

Commands below use `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
VECLIB_MAXIMUM_THREADS=1` for numerical execution, one process/thread:

- `python3 -B docs/align/v4/b3-sim/simulate_r22_cap_sweep_sol1.py --check`:
  **6 passed**, .529 s.
- `python3 -B docs/align/v4/b3-sim/simulate_r24_c14_confirm_sol1.py --check`:
  **7 passed**, .889 s; all 16,384 bar patterns, no top-up, C13/C14 rescue,
  C1–C12 tape/threshold bytes, exact workload, scalar T tails, stopped-study
  identity, and deterministic serialization.
- New simulator `--profile`: **10,000 studies in 1.728 s**. The unchanged
  old pilot took .846 s; workloads differ, and no speed saving is claimed.
- New simulator without flags: **72 × 100,000 studies**, both calendars,
  **3,157.7 s (52.6 min)**; all internal assertions passed.
- `python3.13 -B -m unittest tests.align.test_v4_estimands`:
  **15 passed**, .006 s. Python 3.13 AST checks of both new scripts passed.
- `python3.13 -B docs/align/v4/b3-sim/audit_r24_c14_confirm_sol1.py`:
  **passed** for 432 counts, 7,776 scores, 2,592 joined rows, **87,696
  intervals**, exact counts/workload/stop means, both pairs, both calendars,
  source/input/output hashes, and C10-qualified identity.

All **218,880 fields** from the prior 288 count and 5,184 score rows replay
byte-identically on their original calendars; matching serialized digest
`4ff15bd28410679ecba21a3588d106d1538397f02ab6b973502900e195d8fc7e`.
Original sources and evidence are unchanged. The
[metadata](../align/v4/b3-sim/r24-c14-confirm-metadata-sol1.json),
[audit receipt](../align/v4/b3-sim/r24-c14-confirm-audit-sol1.json), and
`r24-c14-confirm-*-sol1.txt` logs retain the checks and run. One initial
unit-check expectation incorrectly barred `oracle8`; corrected to reflect
the inherited oracle ignoring bars. Its failed log is preserved; no
simulation output was changed.

Numerics used **Python 3.14.6 / NumPy 2.2.6**. Python 3.13 has no NumPy;
Python 3.11 is unavailable. The inherited explicit ufunc arithmetic and raw
array-byte checks avoid the previously documented host comparison/temporary
issue. **Lead reproduction on Python 3.11/3.13 with NumPy remains required
before reliance.** No MLX/product code changed; no new native MLX tests are
owed. Actual state persistence, gate drift, residual tails, and dependent
member loss remain unqualified.

Only two new synthetic scripts, generated tables/receipts/logs, and this
report were added. No full suite, measurement pipeline/data, real restricted
directory, external user path, other-job inspection/control, network, model
weights, push, or coordination-state edit was used. Targeted tests took only
seconds; the declared synthetic study was the long-running computation.
No blocking questions remain. Next: lead reproduces on a supported NumPy
runtime and carries the stop-relative drift increase into its C14 review.
