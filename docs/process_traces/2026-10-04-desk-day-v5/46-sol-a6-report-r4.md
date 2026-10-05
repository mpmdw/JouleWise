```json
{
"schema":"claude-codex-report/v1",
"genre":"implementation",
"status":"findings",
"completion":"complete",
"summary":"Pending-launcher census implemented; V5-V8 passed and all 11 suite failures exactly reproduced at merged main.",
"workspace":{"base_requested":"76f8e948","base_mode":"exact","head_start":"76f8e948b3e5c2848b61aab9125e8c8ba694404a","head_end":"76f8e948b3e5c2848b61aab9125e8c8ba694404a","upstream_end":"cfdb90d6c9c8c3ee512e258c05ffa2d2b1676b1f","branch":"feat/2026-10-04-launch-realization-recheck"},
"pathspec":["joulewise/measurement_liveness.py","tests/test_measurement_liveness.py"],
"unowned_dirty":[],
"verdict":{"implementation":"implemented","acceptance":"pending_verification"},
"verification":[
{"id":"V1","kind":"suite","cmd":"TMPDIR=/tmp/dd5-a6r4 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-a6r4/site:. PYTEST_PLUGINS=review_results REVIEW_RESULTS=/tmp/dd5-a6r4/head-tests.json /Users/edr/code/JouleWise/.venv/bin/python -B -m pytest -q -p no:cacheprovider tests/test_measurement_liveness.py tests/test_launch_window.py tests/test_launch_window_realization_recheck.py tests/test_identity_pins.py tests/test_run_night.py > /tmp/dd5-a6r4/head-tests.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["11 failed, 367 passed, 9 skipped, 16 warnings, 284 subtests passed in 2141.90s (0:35:41)"]},"expected":{"exit_code":0,"tail_regex":"^[0-9]+ passed"}},
{"id":"V2","kind":"test","cmd":"TMPDIR=/tmp/dd5-a6r4 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-a6r4/site:. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6r4/run_base_failures.py > /tmp/dd5-a6r4/base-replay.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["base replay: 11 failed head test nodes; exit 1"]},"expected":{"exit_code":1,"tail_regex":"base replay: 11 failed head test nodes; exit 1"}},
{"id":"V3","kind":"inspection","cmd":"TMPDIR=/tmp/dd5-a6r4 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6r4/compare_failures.py > /tmp/dd5-a6r4/failure-comparison.log","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["head failing nodes: 11","baseline reproduced nodes: 11","same assertion lines: 11"]},"expected":{"exit_code":0,"tail_regex":"same assertion lines: 11"}},
{"id":"V4","kind":"inspection","cmd":"TMPDIR=/tmp/dd5-a6r4 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6r4/compare_bind_source.py > /tmp/dd5-a6r4/bind-source-comparison.log","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Bind and probe supervision: 15 definitions AST-identical to exact base cfdb90d6"]},"expected":{"exit_code":0,"tail_regex":"15 definitions AST-identical"}},
{"id":"V5","kind":"test","cmd":"TMPDIR=/tmp/dd5-a6r4 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-a6r4/site:. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6r4/driver_death.py > /tmp/dd5-a6r4/driver-death.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["PASS: launcher process-group custody survives driver death"]},"expected":{"exit_code":0,"tail_regex":"PASS: launcher process-group custody survives driver death"}},
{"id":"V6","kind":"test","cmd":"TMPDIR=/tmp/dd5-a6r4 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-a6r4/site:. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6r4/barrier_faults.py > /tmp/dd5-a6r4/barrier-faults.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["barrier fault probes completed"]},"expected":{"exit_code":0,"tail_regex":"barrier fault probes completed"}},
{"id":"V7","kind":"test","cmd":"TMPDIR=/tmp/dd5-a6r4 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-a6r4/site:. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6r4/compare_nonpack_bytes.py > /tmp/dd5-a6r4/nonpack-bytes.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["DIAGNOSTIC_NO_PACK: byte-identical artifacts=9","REHEARSAL_STUB: byte-identical artifacts=9"]},"expected":{"exit_code":0,"tail_regex":"REHEARSAL_STUB: byte-identical artifacts=9"}},
{"id":"V8","kind":"test","cmd":"TMPDIR=/tmp/dd5-a6r4 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-a6r4/site:. /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_measurement_liveness.MeasurementLivenessTests.test_v8_live_pending_launcher_is_measurement_owner_without_chain_started > /tmp/dd5-a6r4/v8.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"^OK$"}},
{"id":"V9","kind":"inspection","cmd":"TMPDIR=/tmp/dd5-a6r4 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6r4/verify_cleanup.py > /tmp/dd5-a6r4/cleanup-final.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Probe cleanup: 10 process groups proven absent"]},"expected":{"exit_code":0,"tail_regex":"10 process groups proven absent"}},
{"id":"V10","kind":"inspection","cmd":"PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6r4/check_scope.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Scope and estimator pins: pass"]},"expected":{"exit_code":0,"tail_regex":"Scope and estimator pins: pass"}}
],
"flags":[
{"id":"F1","kind":"lead_ruling","level":"nonblocking","text":"Granted census scope implemented, including V8 and fail-closed pending-group identity and read-race cases.","needs":""},
{"id":"F2","kind":"lead_ruling","level":"nonblocking","text":"Diagnostic harvester remains unchanged under the deferral. Required launch.pending fields for both block-4 pack harvesters are listed below.","needs":"Implement pending custody in the block-4 pack harvesters before their first use."},
{"id":"F3","kind":"environment","level":"nonblocking","text":"Eight installer failures stop at the child battery-fixture assertion; three bind tests hit the external 8-second watchdog. All 11 assertions match merged main cfdb90d6. Initial metadata-free baseline replay was corrected and retained separately.","needs":""},
{"id":"F4","kind":"environment","level":"nonblocking","text":"git add exited 128: sandbox denied /Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-dd5-a6/index.lock creation. Patch is uncommitted; no push.","needs":"Lead review, stage and commit the two-file patch."},
{"id":"F5","kind":"environment","level":"nonblocking","text":"V5 retained null start_time and census refused clearance. V8 separately supplies a matching LIVE identity and live group. These are process/fixture checks, not quiet-window hardware validation.","needs":""},
{"id":"F7","kind":"verification_gap","level":"nonblocking","text":"Canonical unittest discovery was not run: its fixed /tmp/joulewise-test-d165-phase0-floor-pin fixture is outside authorized /tmp/dd5-a6r4 scratch. All five requested files completed.","needs":"Lead run canonical discovery and final integrated-head verification with appropriate scratch authority."}
]
}
```

## Change

The census now refuses live or indeterminate pending launcher groups, including groups with dead or reused leaders. Read reconciliation avoids duplicate diagnostics and preserves pending evidence. Added V8 and related regressions.

## Verification notes

All 11 suite failures reproduced with identical assertions at `cfdb90d6`. The initial baseline archive lacked Git metadata; that comparison was corrected.

Sandbox denial left the patch uncommitted. Canonical discovery remains a lead check because its fixed temporary path exceeds the authorized scratch scope.

## Residual risk

`scripts/harvest_v5_pack_rehearsal.py` and `scripts/harvest_v5_g2b_window.py` must read these `launch.pending` fields:

- `schema`: validate `joulewise.launch_pending.v1`.
- `pgid`: prove process-group absence.
- `pid`, `start_time`: establish leader identity.
- `plan_id`, `attempt_id`: attribute the attempt.
- `epoch_s`: retain ordering evidence.

NULL requires absent `chain.started` and a proven-gone pending group. Unknown liveness must refuse.