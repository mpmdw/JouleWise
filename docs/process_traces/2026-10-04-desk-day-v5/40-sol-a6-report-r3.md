```json
{
"schema":"claude-codex-report/v1",
"genre":"implementation",
"status":"blocked",
"completion":"partial",
"summary":"NEEDS_SCOPE: pending-launcher custody implemented; measurement-owner census still ignores it outside WRITE_SCOPE.",
"workspace":{"base_requested":"8fa002f7","base_mode":"exact","head_start":"64ef2471164f1f7d87fd4946ee5defa1ea685235","head_end":"64ef2471164f1f7d87fd4946ee5defa1ea685235","upstream_end":"cfdb90d6c9c8c3ee512e258c05ffa2d2b1676b1f","branch":"feat/2026-10-04-launch-realization-recheck"},
"pathspec":["scripts/launch_window.py","scripts/run_night.py","tests/test_launch_window_realization_recheck.py","tests/test_run_night.py"],
"unowned_dirty":[],
"verdict":{"implementation":"partial","acceptance":"needs_ruling"},
"verification":[
{"id":"V1","kind":"suite","cmd":"TMPDIR=/tmp/dd5-a6r3 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-a6r3/site:. PYTEST_PLUGINS=review_results REVIEW_RESULTS=/tmp/dd5-a6r3/head-launch.json /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_launch_window.py tests/test_launch_window_realization_recheck.py tests/test_identity_pins.py > /tmp/dd5-a6r3/head-launch.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["97 passed, 16 warnings, 48 subtests passed in 1932.44s (0:32:12)"]},"expected":{"exit_code":0,"tail_regex":"97 passed"}},
{"id":"V2","kind":"suite","cmd":"TMPDIR=/tmp/dd5-a6r3 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-a6r3/site:. PYTEST_PLUGINS=review_results REVIEW_RESULTS=/tmp/dd5-a6r3/head-night.json /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_run_night.py > /tmp/dd5-a6r3/head-night.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["33 failed, 229 passed, 9 skipped, 187 subtests passed in 397.22s (0:06:37)"]},"expected":{"exit_code":0,"tail_regex":"0 failed"}},
{"id":"V3","kind":"test","cmd":"TMPDIR=/tmp/dd5-a6r3 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-a6r3/site:. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6r3/run_base_failures.py > /tmp/dd5-a6r3/base-replay.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["base replay: 29 failed head test nodes; exit 1"]},"expected":{"exit_code":1,"tail_regex":"base replay: 29 failed head test nodes; exit 1"}},
{"id":"V4","kind":"inspection","cmd":"TMPDIR=/tmp/dd5-a6r3 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6r3/compare_failures.py > /tmp/dd5-a6r3/failure-comparison.log; head -3 /tmp/dd5-a6r3/failure-comparison.log","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["head failing nodes: 29","baseline reproduced nodes: 29","same assertion lines: 28"]},"expected":{"exit_code":0,"tail_regex":"same assertion lines: 28"}},
{"id":"V5","kind":"test","cmd":"TMPDIR=/tmp/dd5-a6r3 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-a6r3/site:. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6r3/driver_death.py > /tmp/dd5-a6r3/driver-death.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["PASS: launcher process-group custody survives driver death"]},"expected":{"exit_code":0,"tail_regex":"PASS: launcher process-group custody survives driver death"}},
{"id":"V6","kind":"test","cmd":"TMPDIR=/tmp/dd5-a6r3 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-a6r3/site:. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6r3/barrier_faults.py > /tmp/dd5-a6r3/barrier-faults.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["barrier fault probes completed"]},"expected":{"exit_code":0,"tail_regex":"barrier fault probes completed"}},
{"id":"V7","kind":"test","cmd":"TMPDIR=/tmp/dd5-a6r3 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-a6r3/site:. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6r3/compare_nonpack_bytes.py > /tmp/dd5-a6r3/nonpack-bytes.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["DIAGNOSTIC_NO_PACK: byte-identical artifacts=9","REHEARSAL_STUB: byte-identical artifacts=9"]},"expected":{"exit_code":0,"tail_regex":"byte-identical artifacts=9"}},
{"id":"V8","kind":"inspection","cmd":"TMPDIR=/tmp/dd5-a6r3 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6r3/measurement_pending_gap.py > /tmp/dd5-a6r3/measurement-guard-gap.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Confirmed scope gap: measurement_liveness.census ignores synthetic live launch.pending"]},"expected":{"exit_code":0,"tail_regex":"Confirmed scope gap"}},
{"id":"V9","kind":"inspection","cmd":"TMPDIR=/tmp/dd5-a6r3 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6r3/verify_cleanup.py > /tmp/dd5-a6r3/cleanup.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Probe cleanup: 10 process groups proven absent"]},"expected":{"exit_code":0,"tail_regex":"10 process groups proven absent"}},
{"id":"V10","kind":"inspection","cmd":"PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6r3/check_scope.py > /tmp/dd5-a6r3/scope-pins.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Scope and estimator pins: pass"]},"expected":{"exit_code":0,"tail_regex":"Scope and estimator pins: pass"}}
],
"flags":[
{"id":"F1","kind":"scope_deviation","level":"blocking","text":"NEEDS_SCOPE: measurement_liveness.py:186,260 skips pending-only launchers. V8 confirms a clear census without observing its synthetic LIVE owner. No out-of-scope writes.","needs":"Authorize the two requested paths, or explicitly defer this consumer."},
{"id":"F2","kind":"residual_risk","level":"nonblocking","text":"V5 verifies pending identity/dead-man refusal; its original external-harvest check still reports clear. The brief permits this harvester follow-up.","needs":"Update scripts/harvest_g2a_window.py:45 before using its :125 NULL branch with pending-launch attempts."},
{"id":"F3","kind":"environment","level":"nonblocking","text":"All 29 failing night nodes reproduce at base; 28 assertion sets match. One NightProbeTests node fails in different timeout subcases. Fifteen bind/probe definitions are AST-identical.","needs":""},
{"id":"F4","kind":"environment","level":"nonblocking","text":"git add exited 128: sandbox denied shared worktree index.lock creation. Changes are uncommitted; no push.","needs":""},
{"id":"F5","kind":"environment","level":"nonblocking","text":"Process listing unavailable (no sysmond); V5 start_time is null under the existing observer. Pending group checks fail closed; cleanup uses killpg.","needs":""},
{"id":"F6","kind":"baseline_drift","level":"nonblocking","text":"origin/main moved 8fa002f7 -> cfdb90d6. Worker HEAD remains 64ef2471; comparisons use exact base 8fa002f7.","needs":"Lead reconcile with current main before final review."},
{"id":"F7","kind":"verification_gap","level":"nonblocking","text":"Requested four files completed; repository-wide unittest discovery remains unrun while the remaining guard is scope-blocked.","needs":"Lead run canonical discovery after the remaining guard is implemented."}
],
"scope_expansion":{"requested_paths":["joulewise/measurement_liveness.py","tests/test_measurement_liveness.py"],"reason":"The every-consumer requirement includes a measurement-owner census that reports clear for pending-only live launchers.","blocked_work":"Guard the measurement-owner/publication census and add its pending live, gone and unreadable identity regressions.","minimal_change":"Inspect launch.pending in _inspect_chain and census reconciliation; refuse live/indeterminate groups and retain immutable evidence."}
}
```

## Change

Added exclusive, fsynced `launch.pending` custody and a handshake before recheck. Dead-man and courier guard pending launchers. Refusals retain pending evidence without start/exit markers or bundles. Added V5 and guard regressions.

## Verification notes

All requested files completed. Every failing night node reproduced at base; one probe node differed in timeout subcase. Changes remain uncommitted because the sandbox denied Git index writes.

## Residual risk

**NEEDS_SCOPE:** [measurement_liveness.py](/Users/edr/code/JouleWise-wt-dd5-a6/joulewise/measurement_liveness.py:186) still ignores pending custody. The next step is to authorize the two requested paths or explicitly defer that consumer.

Harvester follow-up: [group_clear()](/Users/edr/code/JouleWise-wt-dd5-a6/scripts/harvest_g2a_window.py:45) must read pending `pgid` for liveness and `pid`, `start_time`, `plan_id`, `attempt_id` for attribution. Missing `chain.started` may reach the existing NULL branch at line 125 only after the pending group is proven gone.