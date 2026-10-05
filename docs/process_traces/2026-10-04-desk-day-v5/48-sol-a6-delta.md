```json
{
"schema":"claude-codex-report/v1",
"genre":"review",
"status":"clean",
"completion":"complete",
"summary":"DELTA: PASS; R1 closed; all 14 focused-suite failures reproduce on main.",
"workspace":{"base_requested":"64ef2471","base_mode":"exact","head_start":"14324c5260df33513736f5f4be067b3019bb3b5a","head_end":"14324c5260df33513736f5f4be067b3019bb3b5a","upstream_end":"784d12f1b996865c8cf4053bb70101804346ceae","branch":null},
"pathspec":[],
"unowned_dirty":[],
"verdict":{"delta":"PASS","prior_R1":"closed","findings":[]},
"verification":[
{"id":"V1","kind":"suite","cmd":"TMPDIR=/tmp/dd5-a6delta/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-a6delta/site:. PYTEST_PLUGINS=review_results REVIEW_RESULTS=/tmp/dd5-a6delta/head-results.json /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider -o cache_dir=/tmp/dd5-a6delta/pc tests/test_measurement_liveness.py tests/test_launch_window.py tests/test_launch_window_realization_recheck.py tests/test_run_night.py > /tmp/dd5-a6delta/head-suite.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["14 failed, 322 passed, 9 skipped, 17 warnings, 264 subtests passed in 2440.60s (0:40:40)"]},"expected":{"exit_code":0,"tail_regex":"^\\d+ passed"}},
{"id":"V2","kind":"test","cmd":"TMPDIR=/tmp/dd5-a6delta/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-a6delta/site:. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6delta/run_main_candidates.py > /tmp/dd5-a6delta/main-candidates-run.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["main candidates: 13 prior failing nodes; exit 1"]},"expected":{"exit_code":1,"tail_regex":"main candidates: 13 prior failing nodes; exit 1"}},
{"id":"V3","kind":"other","cmd":"TMPDIR=/tmp/dd5-a6delta/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-a6delta/site:. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6delta/run_main_failures.py > /tmp/dd5-a6delta/main-coverage.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["main comparison coverage: 14 current head failing nodes; 1 additional nodes replayed","main unavailable: 0"]},"expected":{"exit_code":0,"tail_regex":"main unavailable: 0"}},
{"id":"V4","kind":"test","cmd":"TMPDIR=/tmp/dd5-a6delta/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-a6delta/site:. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6delta/run_current_main_failures.py > /tmp/dd5-a6delta/main-end-run.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["current main replay: 14 current head failing nodes; exit 1"]},"expected":{"exit_code":1,"tail_regex":"current main replay: 14 current head failing nodes; exit 1"}},
{"id":"V5","kind":"inspection","cmd":"python3 -B /tmp/dd5-a6delta/comparison_summary.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["startup_main_cfdb90d6: reproduced=14/14; identical_assertions=14/14","ending_main_784d12f1: reproduced=14/14; identical_assertions=9/14"]},"expected":{"exit_code":0,"tail_regex":"ending_main_784d12f1: reproduced=14/14"}},
{"id":"V6","kind":"test","cmd":"TMPDIR=/tmp/dd5-a6delta/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-a6delta/site:. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6delta/driver_death.py > /tmp/dd5-a6delta/driver-death.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["PASS: launcher process-group custody survives driver death"]},"expected":{"exit_code":0,"tail_regex":"PASS: launcher process-group custody survives driver death"}},
{"id":"V7","kind":"test","cmd":"TMPDIR=/tmp/dd5-a6delta/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-a6delta/site:. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6delta/barrier_faults.py > /tmp/dd5-a6delta/barrier-faults.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["barrier fault probes completed"]},"expected":{"exit_code":0,"tail_regex":"barrier fault probes completed"}},
{"id":"V8","kind":"test","cmd":"TMPDIR=/tmp/dd5-a6delta/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-a6delta/site:. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6delta/custody_faults.py > /tmp/dd5-a6delta/custody-faults.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["PASS: custody persistence and acknowledgement fault probes"]},"expected":{"exit_code":0,"tail_regex":"PASS: custody persistence and acknowledgement fault probes"}},
{"id":"V9","kind":"test","cmd":"TMPDIR=/tmp/dd5-a6delta/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-a6delta/site:. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6delta/pending_cases.py > /tmp/dd5-a6delta/pending-cases.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["PASS: pending dead-leader, reused-PID, stale-attempt and indeterminate cases"]},"expected":{"exit_code":0,"tail_regex":"PASS: pending dead-leader, reused-PID, stale-attempt and indeterminate cases"}},
{"id":"V10","kind":"test","cmd":"TMPDIR=/tmp/dd5-a6delta/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-a6delta/site:. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6delta/compare_nonpack_bytes.py > /tmp/dd5-a6delta/nonpack-bytes.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["DIAGNOSTIC_NO_PACK: byte-identical artifacts=9","REHEARSAL_STUB: byte-identical artifacts=9"]},"expected":{"exit_code":0,"tail_regex":"REHEARSAL_STUB: byte-identical artifacts=9"}},
{"id":"V11","kind":"test","cmd":"TMPDIR=/tmp/dd5-a6delta/tmp PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-a6delta/site:. /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider -o cache_dir=/tmp/dd5-a6delta/pc tests/test_launch_window_realization_recheck.py -k mutation > /tmp/dd5-a6delta/ruled-regressions.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["5 passed, 12 deselected, 1 warning in 18.16s"]},"expected":{"exit_code":0,"tail_regex":"5 passed, 12 deselected"}},
{"id":"V12","kind":"inspection","cmd":"TMPDIR=/tmp/dd5-a6delta/tmp PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6delta/check_probe_cleanup.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["PASS: all 16 owned probe groups absent"]},"expected":{"exit_code":0,"tail_regex":"PASS: all 16 owned probe groups absent"}}
],
"flags":[
{"id":"F1","kind":"environment","level":"nonblocking","text":"Focused suite: 14 failures (8 battery-child fixture setup failures and 6 supervision failures); every failing node reproduces on both main snapshots. All assertion lines match startup main cfdb90d6. Process identity probes are sandbox-restricted; controlled identity fixtures are not hardware validation.","needs":""},
{"id":"F2","kind":"baseline_drift","level":"nonblocking","text":"Main advanced cfdb90d6 to 784d12f1 via unrelated PRs #472-#473. Reviewed custody code and supervision fixtures are unchanged. Ending main fails the same 14 nodes; 9 assertion sets match, while 5 supervision timing diagnostics differ.","needs":""},
{"id":"F3","kind":"residual_risk","level":"nonblocking","text":"Pack-window harvesters do not exist yet and must census launch.pending before treating absent chain.started as NULL. The legacy non-pack G2-a harvester still ignores pending custody; this is the stated tracked follow-up.","needs":"Keep pending-group custody in the pack-harvester acceptance gate."}
]
}
```

## Findings

DELTA: PASS

R1 is closed; no new findings. The [driver-death replay](/tmp/dd5-a6delta/driver-death.log) retains pending custody, leaves no `chain.started`, makes dead-man refuse, and prevents courier delivery while the launcher lives. The owner census also refuses.

Barrier faults, persistence faults, dead-leader/reused-PID cases, and tokenizer/model mutations passed. Both non-pack routes retain nine byte-identical artifacts each.

[Stale-record checks](/tmp/dd5-a6delta/pending-cases.log): a proven-dead earlier group permits a fresh custody directory. Reusing its old directory remains refused as `night_record_exists`, regardless of plan/attempt fields, under the existing write-once rule.

The requested suite returned **14 failed, 322 passed, 9 skipped**. All fourteen failures reproduce on main; all assertion lines match startup main. Newer main fails the same nodes with five varying supervision diagnostics.

Repository unchanged; all 16 scratch-probe groups confirmed absent.

## Residual risk

Future pack-window harvesters must read pending custody before declaring NULL. These checks provide fixture and process evidence, not live hardware validation.