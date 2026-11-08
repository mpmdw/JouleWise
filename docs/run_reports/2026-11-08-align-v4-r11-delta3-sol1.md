# ALIGN v4 R11 delta3 — Sol1 execution record (2026-11-08)

Verdict: **HOLD** at candidate **9891d679b**. Detailed findings and repairs:
`docs/align/squeeze/fanout/r11-delta3-review-sol1.md`. The four findings protect
the reviewed execution candidate, the previous-window cadence history, and
the meter source of a secondary DC diagnostic. Top-up, G2 ordering and the
24-capture ceiling are admitted for this delta.

## Scope and authority

The pre-provisioned branch `align/2026-11-08-v4-r11-delta3-sol1` was clean at
intake and already matched the requested new seat branch. Reviewed
`git diff f993b784f..9891d679b`, both delta2 reports via local origin objects,
and necessary production callers. Read repository conventions, M0, generated
stop card (NONE), project/workspace/next-work pointers, queue/do-not-do list,
orchestration, targeted decision authority (including D-050 and D-161),
protocol/lead rulings and `origin/main:docs/perf/SPEED-TOOLBOX.md`.
The explicit review brief supersedes ordinary queue selection, coordination
writes and the full-suite requirement. No coordination task was registered.
This is the independent Sol1 review seat; no peer/sub-agent was invoked.
The lead must adjudicate alongside the other seat and owns final verification.

Only these new repository files were written:

* `tests/align/test_r11_delta3_sol1.py` — failing-first witnesses and controls;
* `docs/align/squeeze/fanout/r11-delta3-review-sol1.md` — review;
* this execution record.

No product, generated kit, receipt, data, RUN_STATE, TASK_QUEUE, state kernel
or `tests/test_gen_state.py` bytes changed.

## Executed evidence

Every ordinary module below ran in a separate process, serially. Prefix for
the first table: `python3.13 -B -m unittest tests.align.`. Host-power state was
redirected with
`JOULEWISE_HOST_STATE_DIR=/private/tmp/r11-delta3-sol1-checks/host`.
Logs remained in `/private/tmp/r11-delta3-sol1-checks/`; the committed witnesses
and this table are the durable reproduction record.

| Module | Tests | Result | Process wall seconds |
|---|---:|---|---:|
| `test_r11_delta2_sol1` | 11 | PASS | 2.827 |
| `test_r11_delta2_sol2` | 10 | PASS | 3.229 |
| `test_r11_delta_sol1` | 8 | PASS | 1.660 |
| `test_r11_delta_sol2` | 6 | PASS | 4.098 |
| `test_km003c` | 19 | PASS | 4.550 |
| `test_r1_to_w1_chain` | 6 | PASS | 2.744 |
| `test_v4_cadence` | 27 | PASS | 0.903 |
| `test_v4_dynamic_closure` | 9 | PASS | 18.360 |
| `test_v4_executed_closure` | 4 | PASS | 5.581 |
| `test_v4_kit` | 116 | PASS | 15.401 |
| `test_v4_receipt_tiers` | 7 | PASS | 8.216 |
| `test_v4_record_binding` | 5 | PASS | 3.090 |
| `test_v4_registration` | 21 | PASS | 33.576 |
| `test_v4_topup` | 11 | PASS | 0.245 |
| `test_r1_turn_counts_export` | 11 | PASS | 1.713 |
| `test_w1_kit_r10` | 30 | PASS | 14.028 |
| `test_v4_opus_cold_witnesses` | 1 | PASS | 7.691 |

Additional isolated commands:

| Command/selection | Tests | Result | Process wall seconds |
|---|---:|---|---:|
| `JW_WP22_FULL=1 python3.13 -B -m unittest tests.align.test_v4_w1_synthetic` | 20 | PASS; one documented expected failure | 81.277 |
| `python3.13 -B -m unittest tests.test_km003c_parse` | 3 | PASS | 0.229 |
| `python3.13 -B -m unittest tests.external.test_km003c_parse.UnwrapAndDropTests tests.external.test_km003c_parse.ClockFitTests tests.external.test_km003c_parse.EnergyTests tests.external.test_km003c_parse.OffsetTests tests.external.test_km003c_parse.FlagTests` | 22 | PASS; synthetic classes only | 0.441 |
| `python3.13 -B -m unittest tests.align.test_r11_delta3_sol1` (initial) | 17 | deliberate RED: 12 failure records | 7.610 unittest seconds |
| same new witness module (final) | 17 | deliberate RED: 13 failure records, ten failing methods, seven passing controls | 8.576 unittest seconds |

The 20 existing selections total **347 test instances**, **209.859 process
wall seconds**, no unexpected failures. The witness changed only to remove
unused imports and assert production trace coverage as a separate subtest;
the thirteenth failure is that demonstrated coverage gap. A separate
single-test production-night trace passed (101 executed paths; eight absent
from the committed 159; none unbound; two amendable). Total test time,
including the witness executions and extra trace, remained under five
minutes, well below the twenty-minute limit. No full suite ran.

`PYTHONPYCACHEPREFIX=/private/tmp/r11-delta3-sol1-checks/pycache python3.13 -B -m compileall -q joulewise tests`
passed. `git diff --check` and staged whitespace checks passed. The final
diff was inspected; product bytes remain the candidate's bytes.

Full WP22's expected failure is the inherited collector-death case
`InjectedWindowTests.test_collector_death_is_x4_and_episode_continues`:
the accepted fail-fast behavior disagrees with the old success expectation.
This result does not close U3 or establish a hardware gate.

## Blinding, safety and uncertainty

All execution used synthetic rows, temporary Git repositories, tiny fake
children, or repository code/config objects. Production modules were imported
without calling their mains for the execution inventory. The short night
fixture uses synthetic processes and mocked hardware/census seams; it does
not run a measurement campaign or inspect the active job. No network, push,
model weights, MLX execution, Block-5 analysis pipeline, real measurement
input, real restricted directory or outside-home data access was used.
Absolute data paths in repository text were never followed. No live job,
machine setting or real process census was inspected or changed.

The external parser's recorded-fixture and review-regression classes were
excluded because they read real recorded meter slices; only the named
synthetic classes above ran. No claim of live validation follows from any
passing test. No optimization or decision cache was introduced.

The closure audit proves concrete counterexamples, not universal completeness.
The new night trace is one branch with fake physical seams; native and
configuration-dependent paths remain a separate gate. The exact canonical
previous-record contract for F03 belongs to the lead. For G3, absent a
capture-time digest, disclosed unclosed salvage cannot authenticate arbitrary
byte changes; the witness targets an accidental unlisted stream selection.

On an authorized Metal host with pinned offline dependencies, the lead still
owes these separate tiny/random native commands, one process each:

* `python3.13 -B -m unittest tests.align.test_cache_checkpoint_native`
* `JW_ALIGN_MLX_NATIVE_TESTS=1 python3.13 -B -m unittest tests.align.test_thermal_mlx`
* `python3.13 -B -m unittest tests.align.test_r0_mlx_native`

Use their importability gates; download no weights. Native R1 termination,
census and installed-deadline qualification and every live custody gate stay
lead-owned, outside this sandbox, without interrupting the blinded job.

## Local commits and next step

* **a7300ba4f** — `test(align): expose delta3 receipt and custody gaps in Sol1 review`.
* The subsequent docs commit contains this record and the review; obtain its
  exact SHA with `git log -1` on the named seat branch.

Lead disposition F01–F04 with the independent Sol2 seat, integrate repairs,
then rerun both delta3 witnesses plus affected modules serially. Deliberately
red review witnesses must be repaired/dispositioned before being treated as
an admission gate. No push, merge, deployment or live arm was performed.
