```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"findings",
  "completion":"complete",
  "summary":"The intact cure reproduces report 19, but arithmetic and expectation cuts survive the brief's literal isolation criterion.",
  "workspace":{"base_requested":"0ff8ac04","base_mode":"exact","head_start":"74a547cd9037f7c43fc7470bab81d133509ab3c0","head_end":"74a547cd9037f7c43fc7470bab81d133509ab3c0","upstream_end":"74a547cd9037f7c43fc7470bab81d133509ab3c0","branch":"fix/2026-09-12-fixture-sentinel-controller"},
  "pathspec":[],
  "unowned_dirty":[],
  "verdict":{"findings":[
    {"id":"R1","severity":"blocker","path":"tests/test_controller.py","line":1688,"summary":"Removing the timeout floor survives the unchanged regression; replacing the inequality's timeout operand with zero also survives."},
    {"id":"R2","severity":"blocker","path":"tests/test_controller.py","line":1674,"summary":"Terminal expectation deletions, strict-mode weakening, canned validation results, and policy-case deletions survive the requested all-clause cut rule."}
  ]},
  "verification":[
    {"id":"V1","kind":"suite","cmd":"/Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest tests.test_controller -q","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 74 tests in 68.681s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V2","kind":"test","cmd":"env PYTHONPATH=/private/tmp:$PWD FAKE_POWERMETRICS_SLEEP_SCALE=1 A177_CUT=stress_timeout_zero /Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest a177_fresh.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce -q","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 1 test in 21.168s","OK"]},"expected":{"exit_code":1,"tail_regex":"FAILED"}},
    {"id":"V3","kind":"test","cmd":"env PYTHONPATH=/private/tmp:$PWD FAKE_POWERMETRICS_SLEEP_SCALE=12 A177_CUT=cure /Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest a177_fresh.HappyPathTests.test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce -q","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["CAPTURE_EXCEPTION TimeoutExpired","Ran 1 test in 34.325s","FAILED (failures=1)"]},"expected":{"exit_code":1,"tail_regex":"FAILED"}},
    {"id":"V4","kind":"inspection","cmd":"git status --short","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}
  ],
  "flags":[]
}
```

## Findings

**R1 — blocker: arithmetic cuts survive.** With the ordinary regression requesting 89 samples, changing the expected timeout from `max(15.0, nominal_s * 1.5 + 10.0)` to `max(0.0, nominal_s * 1.5 + 10.0)` passes. The affine branch masks the removed floor. Separately, replacing the stressed-duration inequality’s right operand with zero passes.

Conditioning the baseline to 1.5 seconds kills the floor cut, but that conditioning is absent from the final regression. Report 39’s conditioned experiment therefore does not establish an unconditional kill by the committed test. Cover both timeout branches in durable tests if every formula term must be protected.

**R2 — blocker under the brief’s literal cut rule: terminal oracles remain removable.** All twelve added expectation deletions pass. Either validation call can independently use `strict=False`; both calls can become canned `[]`. The policy comparison can become `expected == expected`, and each policy case can independently disappear.

These are oracle edits, distinct from report 37’s removable mock delegation. Report 39 tested falsified inputs instead of these deletions. Those input probes fail, but do not satisfy the brief’s stronger requirement. The lead must either require durable protection for these cuts or explicitly exempt terminal-oracle edits; adding recursive assertions without that ruling would repeat the overbuild problem.

**Same-signature: YES—new unprotected arithmetic and terminal-oracle clauses; NO recurrence of “stress on the wrong capture (CI-red)”, “unprotected stress wiring”, or the prior “unprotected validator delegation” wrapper.**

No should-fix or nit established. No pair was established as killed exclusively by the same single cut: the boundary probes supply distinct witnesses. No host-derived count or duration is pinned; no replacement bound is needed.

The inventory below was derived from the source. Every row ran separately with source changes compiled **in memory**. There were **71 cut runs and three controls**.

`1/F1` = **Ran 1 test; FAILED (failures=1)**; `1/F3` = three failures; `1/E1` = one error; `1/OK` = **Ran 1 test; OK**. Failed/error runs exited 1; OK runs exited 0.

Replay using V2 with the corresponding `A177_CUT` from the [driver](/private/tmp/a177_fresh.py). Use external scale 12 for `outer_reset`. Policy rows select `test_powermetrics_fixture_command_only_unpaces_bounded_captures`. Conditioned rows additionally set `A177_DURATION`. [Logs](/private/tmp/a177-fresh-logs/) preserve exact tails.

| Cut ID / clause | Ran/result |
|---|---|
| control | 1/OK |
| wiring: adapter assignment removed | 1/F1 |
| wiring_cure: assignment + cure removed | 1/F1 |
| cure: bounded `--no-sleep` removed | 1/F1 |
| inheritance: production parent | 1/F1 |
| outer_reset: remove surrounding 1x reset | 1/F1 |
| stress_patch: bounded scale → 1 | 1/F1 |
| stress_floor: bounded scale → 3.5 | 1/F1 |
| stress_scope: remove bounded environment change | 1/F1 |
| forward: bounded forwarding → empty bytes | 1/F1 |
| command_forward: bypass fixture command policy | 1/F1 |
| command_return: return empty argv | 1/F1 |
| guard_false: disable bounded recording | 1/F1 |
| guard_removed: record continuous commands too | 1/F1 |
| record: discard capture record | 1/F1 |
| record_count: count + 1 | 1/F1 |
| record_interval: conversion doubled | 1/F1 |
| record_scale: record 1 | 1/F1 |
| record_timeout: record zero | 1/F1 |
| record_argv: record empty argv | 1/F1 |
| record_flag: omit only recorded no-sleep flag¹ | 1/F1 |
| drift_status: observed status → unknown | 1/F1 |
| argv_count: parsed count + 1 | 1/F1 |
| argv_interval: parsed conversion doubled | 1/F1 |
| argv_count_index: remove index + 1 | 1/E1 |
| argv_interval_index: remove index + 1 | 1/E1 |
| nominal_count_zero: count operand → 0 | 1/F1 |
| nominal_count_one: remove count multiplicand | 1/F1 |
| nominal_interval_zero: interval operand → 0 | 1/F1 |
| nominal_interval_one: remove interval multiplicand | 1/F1 |
| stress_nominal: remove nominal multiplicand | 1/F1 |
| stress_scale: remove scale multiplicand | 1/F1 |
| stress_timeout_zero: timeout operand → 0 | **1/OK** |
| stress_timeout_high: timeout operand → infinity | 1/F1 |
| formula_floor: 15 → 0 | **1/OK** |
| formula_nominal: remove nominal multiplicand | 1/F1 |
| formula_factor: remove 1.5 multiplicand | 1/F1 |
| formula_offset: remove + 10 | 1/F1 |
| formula_max: max → min | 1/F1 |
| post_count: compared capture count + 1 | 1/F1 |
| continuous_argv: observed argv gains no-sleep | 1/F1 |
| strict_before_input: first result nonempty | 1/F1 |
| strict_after_input: final result nonempty | 1/F1 |
| strict_flag_before: first strict → False | **1/OK** |
| strict_flag_after: final strict → False | **1/OK** |
| strict_flags: both strict → False | **1/OK** |
| strict_canned: both validation expressions → [] | **1/OK** |
| delete_witness | **1/OK** |
| delete_strict_before | **1/OK** |
| delete_drift | **1/OK** |
| delete_floor | **1/OK** |
| delete_bounded_flag | **1/OK** |
| delete_count_agreement | **1/OK** |
| delete_interval_agreement | **1/OK** |
| delete_formula | **1/OK** |
| delete_inequality | **1/OK** |
| delete_post_agreement | **1/OK** |
| delete_continuous_flag | **1/OK** |
| delete_strict_after | **1/OK** |
| policy_guard: expected flag unconditional | 1/F1 |
| policy_append: remove expected bounded flag | 1/F3 |
| policy_expectation: compare expected to itself | **1/OK** |
| cure_guard: actual flag unconditional | 1/F1 |
| policy_case_None: remove continuous case | **1/OK** |
| policy_case_3: remove count 3 | **1/OK** |
| policy_case_7: remove count 7 | **1/OK** |
| policy_case_100: remove count 100 | **1/OK** |
| control; duration 1.5 | 1/OK |
| formula_floor; duration 1.5 | 1/F1 |
| control; duration 5 | 1/OK |
| formula_nominal; duration 5 | 1/F1 |
| formula_factor; duration 5 | 1/F1 |
| formula_offset; duration 5 | 1/F1 |
| formula_max; duration 5 | 1/F1 |

¹ Uses [a177_recordflag](/private/tmp/a177_recordflag.py) as the unittest module.

The isolated cure cut produced the required report-19 signature:

```text
CAPTURE count=None scale=1
CAPTURE count=94 scale=12
CAPTURE_EXCEPTION TimeoutExpired
DRIFT {'reason': 'post_idle_unavailable', 'status': 'unknown'}
- ['strict: uncertainty evidence: idle_drift does not match pre/post raw '
-  'sentinel derivation',
-  'strict: uncertainty evidence: idle_drift_bound_w does not match effective '
-  'drift derivation']
Ran 1 test in 34.325s
FAILED (failures=1)
```

CI-safety: the surrounding execution uses `with patch.dict(os.environ, {"FAKE_POWERMETRICS_SLEEP_SCALE": "1"}):`; observations confirmed `CAPTURE count=None scale=1`. The 12x override exists only inside bounded capture. No sleep call was added to the regression body. A literal sleep-free execution cannot be confirmed: the pre-existing producer uses `SystemClock`, a one-second post-window dwell, and paced continuous child sampling.

The venv controller suite ran **once**: `Ran 74 tests in 68.681s` / `OK`. Final `git status --short` was empty; HEAD and upstream remained unchanged. Both diff checks passed.

## Residual risk

Hosted CI and full repository discovery were not run. Evidence is synthetic fixture execution, not live hardware validation. The next step is lead adjudication of R1/R2 against the intended terminal-oracle exemption, followed by any authorized regression changes.