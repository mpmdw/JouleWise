```json
{
"schema":"claude-codex-report/v1",
"genre":"implementation",
"status":"findings",
"completion":"complete",
"summary":"Pack launcher recheck refusals leave no chain.started; final focused and non-pack byte checks pass.",
"workspace":{"base_requested":"8fa002f7","base_mode":"descendant","head_start":"578ff42c4776a76cd0c2ae93c887da9b82f3be37","head_end":"578ff42c4776a76cd0c2ae93c887da9b82f3be37","upstream_end":"578ff42c4776a76cd0c2ae93c887da9b82f3be37","branch":"feat/2026-10-04-launch-realization-recheck"},
"pathspec":["scripts/launch_window.py","scripts/run_night.py","tests/test_launch_window.py","tests/test_launch_window_realization_recheck.py","tests/test_run_night.py"],
"unowned_dirty":[],
"verdict":{"implementation":"implemented","acceptance":"ready"},
"verification":[
{"id":"V1","kind":"suite","cmd":"TMPDIR=/tmp/dd5-a6 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_launch_window tests.test_launch_window_realization_recheck tests.test_identity_pins > /tmp/dd5-a6/round2-launch-identity.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["FAILED (failures=1)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"V2","kind":"suite","cmd":"TMPDIR=/tmp/dd5-a6 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_launch_window.PackNightLaunchBoundaryTests.test_integrated_driver_arm_go_launcher_consumption_and_replay tests.test_launch_window_realization_recheck tests.test_run_night.PackNightProducerTests > /tmp/dd5-a6/round2-delta-final38.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 38 tests in 26.031s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"V3","kind":"suite","cmd":"TMPDIR=/tmp/dd5-a6 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6/run_selected_tests.py --output /tmp/dd5-a6/round2-night.json tests.test_run_night tests.test_run_night_probe_cadence tests.test_run_night_probe_worker_cadence tests.test_night_kinds tests.test_evidence_night > /tmp/dd5-a6/round2-night.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["FAILED (failures=67, errors=4, skipped=9)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"V4","kind":"suite","cmd":"TMPDIR=/tmp/dd5-a6 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6/run_selected_tests.py --output /tmp/dd5-a6/round2-base-night-final.json --failures-from /tmp/dd5-a6/round2-night.json > /tmp/dd5-a6/round2-base-night-final.log 2>&1","cwd":"/tmp/dd5-a6-base","observed":{"result":"fail","exit_code":1,"tail":["Ran 68 tests in 109.661s","FAILED (failures=62, errors=4)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"V5","kind":"test","cmd":"TMPDIR=/tmp/dd5-a6 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6/run_selected_tests.py --output /tmp/dd5-a6/round2-base-variable.json tests.test_run_night.BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go tests.test_run_night.BindSupervisionProcessTests.test_journal_failure_and_saturation_are_terminal tests.test_run_night.BindSupervisionProcessTests.test_journal_system_exit_records_failure_before_thread_exit tests.test_run_night.NightProbeTests.test_supervised_probe_success_and_refusal_with_fixture_census tests.test_run_night_probe_cadence.ProbeCadenceTests.test_timeout_retains_220_complete_slow_frames_after_term_delay > /tmp/dd5-a6/round2-base-variable.log 2>&1","cwd":"/tmp/dd5-a6-base","observed":{"result":"fail","exit_code":1,"tail":["FAILED (failures=1)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"V6","kind":"test","cmd":"TMPDIR=/tmp/dd5-a6 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6/run_selected_tests.py --output /tmp/dd5-a6/round2-current-variable-final.json tests.test_run_night.BindSupervisionProcessTests.test_journal_failure_and_saturation_are_terminal tests.test_run_night.NightProbeTests.test_supervised_probe_success_and_refusal_with_fixture_census tests.test_run_night_probe_cadence.ProbeCadenceTests.test_timeout_retains_220_complete_slow_frames_after_term_delay > /tmp/dd5-a6/round2-current-variable-final.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 3 tests in 18.114s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
{"id":"V7","kind":"test","cmd":"TMPDIR=/tmp/dd5-a6 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-a6/compare_nonpack_bytes.py > /tmp/dd5-a6/round2-nonpack-bytes-final.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["DIAGNOSTIC_NO_PACK: byte-identical artifacts=9","REHEARSAL_STUB: byte-identical artifacts=9"]},"expected":{"exit_code":0,"tail_regex":"byte-identical artifacts=9"}},
{"id":"V8","kind":"inspection","cmd":"git diff --check; git diff --exit-code 8fa002f7 -- joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/adapters/powermetrics.py joulewise/reduce.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},
{"id":"V9","kind":"inspection","cmd":"python3 /tmp/dd5-a6/compare_all_failures.py > /tmp/dd5-a6/round2-final-failure-comparison.log","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["pre_existing=68","initially_unmatched=3","tests.test_run_night.BindSupervisionProcessTests.test_journal_failure_and_saturation_are_terminal (mode='journal_saturation')","tests.test_run_night.NightProbeTests.test_supervised_probe_success_and_refusal_with_fixture_census (mode='ok')","tests.test_run_night_probe_cadence.ProbeCadenceTests.test_timeout_retains_220_complete_slow_frames_after_term_delay"]},"expected":{"exit_code":0,"tail_regex":"pre_existing=68[\\s\\S]*initially_unmatched=3"}},
{"id":"V10","kind":"other","cmd":"git add -- scripts/launch_window.py scripts/run_night.py tests/test_launch_window.py tests/test_launch_window_realization_recheck.py tests/test_run_night.py > /tmp/dd5-a6/round2-git-add.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":128,"tail":["fatal: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-dd5-a6/index.lock': Operation not permitted"]},"expected":{"exit_code":0,"tail_regex":"^$"}}
],
"flags":[
{"id":"F1","kind":"lead_ruling","level":"nonblocking","text":"Implemented ruled NULL refusal via launcher PASS/driver claim/ACK barrier; recheck remains solely in launcher.","needs":""},
{"id":"F2","kind":"environment","level":"nonblocking","text":"446 night tests completed. All 71 failing outcomes compared: 68 baseline matches; 3 transient mismatches pass final candidate and base replays. Matching ignores source paths and observer_cpu_s only.","needs":""},
{"id":"F3","kind":"environment","level":"nonblocking","text":"Plain base archive could not satisfy HEAD/clone-dependent fixtures; isolated Git metadata now pins exact 8fa002f7 without worktree registration.","needs":""},
{"id":"F4","kind":"scope_deviation","level":"nonblocking","text":"Initial required fixtures hardcoded /tmp and bypassed TMPDIR. Remaining comparisons redirected their temporary directories into /tmp/dd5-a6. No repository writes exceeded WRITE_SCOPE.","needs":""},
{"id":"F5","kind":"environment","level":"nonblocking","text":"Sandbox denied Git index.lock creation. Five-file diff remains uncommitted; no push.","needs":"Lead review, stage and commit from its authorized session."}
]
}
```

## Change

The launcher remains the sole identity-recheck decision point. After consumed replay and recheck PASS, it requests the driver’s start claim and waits for acknowledgement before `execve`. Recheck refusals preserve the exact launcher refusal as evidence and leave no `chain.started`, `chain.exited`, or bundle.

Preserved invariants:

- **Single claim:** clean launch claims exactly once; an existing marker blocks collection and retains its bytes.
- **Exclusive creation:** unchanged `O_CREAT | O_EXCL | O_WRONLY`, mode `0600`; no retry or marker deletion.
- **Process identity:** `start_new_session=True` and launcher `execve` preserve PID/PGID.
- **Harvest timestamps:** unchanged record-writing function retains `epoch_s` and `start_time`; full publication finishes before acknowledgement permits collection.
- **Supervision:** census and monotonic deadline enforcement remain active while awaiting PASS.
- **Capability handoff:** FD `198` remains reserved; the new barrier closes before collection and its environment key is removed.
- **Non-pack behavior:** both kinds match base in exit code, command, child environment, and all nine custody artifacts under deterministic fixtures.

## Verification notes

The 93-test launcher/identity batch completed with one launcher-stand-in failure. Its missing PASS signal was fixed; the final focused run passed all 38 tests.

Night-driver comparison produced these two lists:

- **Pre-existing:** [68 matched failures/errors](/tmp/dd5-a6/round2-preexisting-failures.txt): 46 battery-fixture failures and 22 supervision outcomes. [Comparison evidence](/tmp/dd5-a6/round2-final-failure-comparison.json) records each baseline match.
- **Initially new/different:** [three outcomes](/tmp/dd5-a6/round2-initially-unmatched-failures.txt): journal saturation, probe success, and the 220-frame cadence timeout. All three passed final candidate tests and base replays; no new failure remains reproduced.

The archive was created with the requested `git archive` command. Local Git metadata was subsequently added for HEAD/clone-dependent fixtures, retaining exact base `8fa002f7` without registering a worktree.

Process/exec and hashing regressions use synthetic ARM/runtime metadata; the collision test uses fixture census evidence. All four estimator pins remain unchanged.

Changes are uncommitted because staging was sandbox-denied. Next: lead review `git diff`, perform final verification, and commit from its authorized session.