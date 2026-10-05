```json
{
  "schema":"claude-codex-report/v1",
  "genre":"review",
  "status":"findings",
  "completion":"partial",
  "summary":"REVIEW: FAIL; driver death before PASS loses launcher custody; 12 of 13 night failures reproduced at base.",
  "workspace":{"base_requested":"8fa002f7","base_mode":"exact","head_start":"64ef2471164f1f7d87fd4946ee5defa1ea685235","head_end":"64ef2471164f1f7d87fd4946ee5defa1ea685235","upstream_end":"8fa002f77db7af1e261a30e3787e38af2ab5e946","branch":null},
  "pathspec":[],
  "unowned_dirty":[],
  "verdict":{"review":"FAIL","findings":[{"id":"R1","severity":"blocker","location":"scripts/run_night.py:945","related_locations":["scripts/run_night.py:1007","scripts/run_night.py:3871","scripts/harvest_g2a_window.py:49"],"description":"Until PASS, the launcher PID/PGID exists only in driver memory. Killing the driver during a stalled recheck leaves a live launcher with no chain.started; dead_man returns GO and attempts courier delivery, and marker-based harvest reports the group clear/NULL. Base retains the group identity and dead_man refuses night_chain_alive.","reproducer":"V5","recommendation":"Persist separate pending-launcher process identity before recheck; make dead-man and harvest guard it while preserving no chain.started until PASS."}]},
  "verification":[
    {"id":"V1","kind":"suite","cmd":"TMPDIR=/tmp/dd5-a6review PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-a6review/site:. /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_launch_window.py tests/test_launch_window_realization_recheck.py tests/test_identity_pins.py > /tmp/dd5-a6review/head-launch.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["95 passed, 16 warnings, 48 subtests passed in 906.04s (0:15:06)"]},"expected":{"exit_code":0,"tail_regex":"95 passed"}},
    {"id":"V2","kind":"suite","cmd":"TMPDIR=/tmp/dd5-a6review PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-a6review/site:. PYTEST_PLUGINS=review_results REVIEW_RESULTS=/tmp/dd5-a6review/head-night.json /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_run_night.py > /tmp/dd5-a6review/head-night.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["13 failed, 236 passed, 9 skipped, 192 subtests passed in 276.65s (0:04:36)"]},"expected":{"exit_code":0,"tail_regex":"0 failed"}},
    {"id":"V3","kind":"test","cmd":"TMPDIR=/tmp/dd5-a6review PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-a6review/site:. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6review/run_base_failures.py > /tmp/dd5-a6review/base-replay.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["base replay: 13 failed head test nodes; exit 1"]},"expected":{"exit_code":1,"tail_regex":"base replay: 13 failed head test nodes; exit 1"}},
    {"id":"V4","kind":"test","cmd":"TMPDIR=/tmp/dd5-a6review PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-a6review/site:. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6review/compare_nonpack_bytes.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["DIAGNOSTIC_NO_PACK: byte-identical artifacts=9","REHEARSAL_STUB: byte-identical artifacts=9"]},"expected":{"exit_code":0,"tail_regex":"byte-identical artifacts=9"}},
    {"id":"V5","kind":"test","cmd":"TMPDIR=/tmp/dd5-a6review PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-a6review/site:. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6review/driver_death.py > /tmp/dd5-a6review/driver-death.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["AssertionError: candidate loses launcher process-group custody before PASS; base retains it"]},"expected":{"exit_code":0,"tail_regex":"PASS: launcher process-group custody survives driver death"}},
    {"id":"V6","kind":"test","cmd":"TMPDIR=/tmp/dd5-a6review PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-a6review/site:. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6review/barrier_faults.py > /tmp/dd5-a6review/barrier-faults.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["barrier fault probes completed"]},"expected":{"exit_code":0,"tail_regex":"barrier fault probes completed"}},
    {"id":"V7","kind":"other","cmd":"TMPDIR=/tmp/dd5-a6review PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-a6review/site:. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6review/recheck_cost.py > /tmp/dd5-a6review/recheck-cost.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Full recheck unmeasured: real derivation calls MLX prepare/load; no Metal invoked"]},"expected":{"exit_code":0,"tail_regex":"Full recheck unmeasured"}},
    {"id":"V8","kind":"test","cmd":"TMPDIR=/tmp/dd5-a6review PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-a6review/site:. /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6review/replay_quiet.py > /tmp/dd5-a6review/quiet-replays.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["base cancellation timeout did not recur in three additional replays","head-quiet-replay exit 0"]},"expected":{"exit_code":0,"tail_regex":"head-quiet-replay exit 0"}},
    {"id":"V9","kind":"inspection","cmd":"python3 -B /tmp/dd5-a6review/compare_failures.py > /tmp/dd5-a6review/failure-comparison.log","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["head failing nodes: 13","baseline reproduced nodes: 12","same assertion lines: 12"]},"expected":{"exit_code":0,"tail_regex":"same assertion lines: 12"}}
  ],
  "flags":[
    {"id":"F1","kind":"verification_gap","level":"nonblocking","text":"Initial QuietDriverIntegrationTests.test_supervised_worker_is_reaped_on_cancellation timed out at 8 seconds. It passed all five base executions and the head replay; its initial failure is not proven pre-existing. Fixture and bind_until_quiet source are unchanged. Partial completion reflects this one requested parity proof.","needs":"Disposition the transient timeout separately from R1."},
    {"id":"F2","kind":"environment","level":"nonblocking","text":"Eight installer/battery-child fixture failures and four supervision timeouts reproduced at exact base, with matching assertion lines after path normalization. Base archive has isolated Git metadata pinned to 8fa002f7. Temporary directories redirected to scratch; repository unchanged; all probe processes ended.","needs":""},
    {"id":"F3","kind":"verification_gap","level":"nonblocking","text":"No full real projection timing: derivation requires MLX model loading. Real Qwen3 weight hashing took 0.969 s for 1.7B and 4.624 s for 8B. Two hashes per identity unit imply about 3.9/18.5 s for two-unit packs, plus unmeasured model load, tokenize and cleanup. No Metal or machine sudo/launchctl/powermetrics binaries invoked.","needs":""}
  ]
}
```

## Findings

REVIEW: FAIL

**R1 — blocker — [scripts/run_night.py:945](/Users/edr/code/JouleWise-wt-dd5-a6review/scripts/run_night.py:945): Driver death before PASS loses launcher custody.** A stalled recheck survives driver termination without a persisted PID/PGID. The real dead-man handler then attempts courier delivery while the launcher remains alive; marker-based harvest treats it as NULL. Base retains the process identity and refuses delivery. Reproducer: V5 above; [evidence](/tmp/dd5-a6review/driver-death.log).

Persist pending-launcher identity separately and guard it in dead-man/harvest, keeping `chain.started` absent until PASS.

Other checks passed: both mutations leave no start/exit/bundle; clean launch claims once with main’s fields; duplicate PASS claims once; waiting deadlines remain enforced. Non-pack artifacts, environment, argv, and exit codes match base.

## Residual risk

One initial cancellation timeout remains unproven at base despite five passing base executions and a passing head replay. Full recheck latency was estimated from hashing; MLX loading was not measured. Repository unchanged; all processes ended.