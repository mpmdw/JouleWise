# 2026-11-08 ALIGN v4 R11 delta3 Sol2

Verdict: **HOLD**, for executed receipt exceptions, unsupervised KM003C
salvage, and incomplete latest-record freshness. Full findings and the
seven requested dispositions are in
`docs/align/squeeze/fanout/r11-delta3-review-sol2.md`.

Candidate reviewed: `9891d679b`, range `f993b784f..9891d679b`.
Branch: `align/2026-11-08-v4-r11-delta3-sol2`, pre-provisioned and clean.
Mission M0, stop card (NONE), queue/do-not-do, project conventions,
orchestration, source-of-truth map and targeted D-161/D-186 authority were
read. The explicit review brief supersedes ordinary queue selection,
full-suite and coordination-write requirements. No kernel task was added.

## Changes and commits

Only three review artifacts changed:

- `tests/align/test_r11_delta3_sol2.py`: executable failing-first findings
  and passing controls; committed as `6e3962cd6`
  (`test(align): witness r11 delta3 receipt and custody gaps (Sol2)`).
- `docs/align/squeeze/fanout/r11-delta3-review-sol2.md`: findings,
  dispositions, limitations and exact lead handoff.
- This dated run report: execution evidence and coordination handoff.

The two reports are committed separately with message
`docs(align): record r11 delta3 Sol2 HOLD and verification`.
No product, generated registration kit or coordination-state file changed.
No commit was pushed, merged or deployed.

## Verification

For each ordinary ALIGN row below the exact command was
`python3.13 -B -m unittest tests.align.<module>`; every row ran in a new
process, sequentially. All test processes inherited
`JOULEWISE_HOST_STATE_DIR=/private/tmp/r11-delta3-sol2-tests/host`.
Hardware/host operations inside fixtures were mocked. Times below include
subprocess startup, except the witness rows, which use unittest's timer.

| Module | Tests | Result | Seconds |
|---|---:|---|---:|
| `test_km003c` | 19 | PASS | 5.337 |
| `test_r11_delta2_sol1` | 11 | PASS | 4.873 |
| `test_r11_delta2_sol2` | 10 | PASS | 6.360 |
| `test_r11_delta_sol1` | 8 | PASS | 2.639 |
| `test_r11_delta_sol2` | 6 | PASS | 3.127 |
| `test_r1_to_w1_chain` | 6 | PASS | 2.336 |
| `test_v4_cadence` | 27 | PASS | 0.781 |
| `test_v4_dynamic_closure` | 9 | PASS | 16.801 |
| `test_v4_executed_closure` | 4 | PASS | 5.213 |
| `test_v4_kit` | 116 | PASS | 15.473 |
| `test_v4_receipt_tiers` | 7 | PASS | 9.187 |
| `test_v4_record_binding` | 5 | PASS | 2.470 |
| `test_v4_registration` | 21 | PASS | 29.967 |
| `test_v4_topup` | 11 | PASS | 0.201 |
| `test_v4_w1_synthetic` with `JW_WP22_FULL=1` | 20 | PASS, one accepted xfail | 76.013 |
| `test_v4_opus_cold_witnesses` | 1 | PASS | 7.333 |
| `test_r1_rehearsal` | 74 | PASS | 7.436 |
| `test_r1_runtime_e2e` | 2 | PASS | 34.075 |
| `tests.test_km003c_parse` (exact module) | 3 | PASS | 0.178 |
| `tests.external.test_km003c_parse.OffsetTests` (exact class) | 1 | PASS | 0.169 |
| `test_r11_delta3_sol2` first iteration | 12 | Expected red: five failing methods / 10 failure records | 1.128 |
| `test_r11_delta3_sol2` final expanded inventory | 13 | Expected red: six failing methods / 17 failure records | 1.763 |

The 20 baseline selections total **361 test instances, zero unexpected
failures, 229.969 s process wall time**. The expected full-WP22 failure is
`InjectedWindowTests.test_collector_death_is_x4_and_episode_continues`, the
inherited accepted fail-fast divergence. The new final witness has seven
passing controls and zero errors. The expanded inventory adds the actual
session installer launch plus the campaign, harvest, watchdog and installer
module imports. Both witness executions together add 2.891 s of unittest
time; aggregate testing is well below twenty minutes.

`python3.13 -B -m compileall -q joulewise tests` exited 0.
`git diff --check` passed. No full suite was run, as directed. Existing
dynamic-closure testing includes its minimal live **synthetic** trace; the
whole committed trace was not regenerated. Independent code-only imports
and static edges were inspected without calling production entry points.

Temporary logs and the serial process-time summary are under
`/private/tmp/r11-delta3-sol2-tests/`; they are diagnostic scratch, not
measurement custody or durable claim evidence. The table and witnesses
are the tracked reproduction evidence.

## Limits, open choices and next step

Lead must choose/enforce the canonical latest-record location or equivalent
authoritative previous-window binding; no such naming policy was invented
here. The stream repair must preserve supervised crash-prefix salvage while
refusing unlisted/unsupervised input. The remaining allowlist branches and
all computed/native paths are not universally proven unreachable by this
review. The report distinguishes demonstrated execution from those limits.

No sealed Block-5 outcomes or real measurement inputs were opened. No
external home path was followed; absolute paths in source were treated as
text. No network, model download, hardware collection, native MLX, actual
host setting/LaunchAgent operation, process census of the blinded job or
external agent consult was used. Only synthetic temporary repositories and
streams were mutated. RUN_STATE, TASK_QUEUE, state_kernel and test_gen_state
remain lead-owned and untouched.

Outside this sandbox, on a separately authorized Metal host with tiny/random
offline models, lead still needs the existing native gates:
`python3.13 -B -m unittest tests.align.test_cache_checkpoint_native`,
`JW_ALIGN_MLX_NATIVE_TESTS=1 python3.13 -B -m unittest tests.align.test_thermal_mlx`,
and `python3.13 -B -m unittest tests.align.test_r0_mlx_native`, plus native
R1 termination/census and installed-deadline qualification. The continuous
battery logger also needs qualification for its actual through-window
procedure/observer accounting. Do not run these against or interrupt the
ongoing blinded job; no weights need downloading.

Next: lead adjudicates H1/H2/M1 with the other independent seat, repairs the
three bounded defects, reruns both seats' witnesses and touched modules
serially, and preserves the other pending registration/live gates.
