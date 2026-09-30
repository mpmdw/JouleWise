```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"blocked","completion":"partial","summary":"R1, R2 and R3 implemented and deletion-checked; required commit blocked by sandbox Git metadata permissions.","workspace":{"base_requested":"36e8ba6e345653e4fb4ac54f711dc49b27c1d30c","base_mode":"exact","head_start":"36e8ba6e345653e4fb4ac54f711dc49b27c1d30c","head_end":"36e8ba6e345653e4fb4ac54f711dc49b27c1d30c","upstream_end":"36e8ba6e345653e4fb4ac54f711dc49b27c1d30c","branch":"feat/2026-09-28-ntp-n1"},"pathspec":["joulewise/network_time_window.py","tests/test_network_time_window.py","scripts/run_night.py","tests/test_run_night.py"],"unowned_dirty":[],"verdict":{"implementation":"implemented","acceptance":"pending_verification"},"verification":[{"id":"V1","kind":"suite","cmd":"PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest -v tests.test_network_time_window tests.test_run_night tests.test_night_gate tests.test_arm_retry tests.test_launch_window > /tmp/n1fix2c/modules-precommit.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 521 tests in 758.393s","FAILED (failures=38, skipped=9)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V2","kind":"test","cmd":"PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B /tmp/n1fix2c/run_regressions.py head-portable > /tmp/n1fix2c/candidate-portable-output.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 12 tests in 1.763s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V3","kind":"test","cmd":"PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B /tmp/n1fix2c/run_regressions.py baseline > /tmp/n1fix2c/baseline-replay-output.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":1,"tail":["Ran 15 tests in 2.558s","FAILED (failures=12)"]},"expected":{"exit_code":1,"tail_regex":"FAILED \\(failures=12\\)"}},{"id":"V4","kind":"test","cmd":"PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B /tmp/n1fix2c/run_regressions.py head > /tmp/n1fix2c/candidate-all-output.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 15 tests in 2.429s","FAILED (failures=3)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V5","kind":"test","cmd":"PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B /tmp/n1fix2c/run_mutations.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["R3: RED BY ASSERTION (exit 1)","R1: RED BY ASSERTION (exit 1)","R2: RED BY ASSERTION (exit 1)","All three deletions killed"]},"expected":{"exit_code":0,"tail_regex":"All three deletions killed"}},{"id":"V6","kind":"test","cmd":"PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B /tmp/n1fix2c/record_controls.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 2 tests in 0.102s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V7","kind":"test","cmd":"PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B /tmp/n1fix2c/record_controls.py","cwd":"/tmp/n1fix2c/base","observed":{"result":"pass","exit_code":0,"tail":["Ran 2 tests in 0.191s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V8","kind":"inspection","cmd":"/opt/homebrew/bin/python3 -B /tmp/n1fix2c/inspect_scope.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["supersede=True call sites: one","scope: PASS (4 paths)"]},"expected":{"exit_code":0,"tail_regex":"scope: PASS \\(4 paths\\)"}},{"id":"V9","kind":"test","cmd":"PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B /tmp/n1fix2c/replay_inherited_failures.py","cwd":".","observed":{"result":"pass","exit_code":1,"tail":["Ran 35 tests in 24.020s","FAILED (failures=36, errors=1)"]},"expected":{"exit_code":1,"tail_regex":"FAILED \\(failures=36, errors=1\\)"}},{"id":"V10","kind":"test","cmd":"PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest -v tests.test_run_night.NightDriverTests.test_installer_refuses_active_chain_and_rolls_back_partial_bootstrap > /tmp/n1fix2c/baseline-installer.log 2>&1","cwd":"/tmp/n1fix2c/base","observed":{"result":"pass","exit_code":1,"tail":["AssertionError: 2 != 3 : probe receipt driver_python mismatch","Ran 1 test in 2.574s","FAILED (failures=1)"]},"expected":{"exit_code":1,"tail_regex":"FAILED \\(failures=1\\)"}},{"id":"V11","kind":"other","cmd":"git diff --check; git add -- joulewise/network_time_window.py tests/test_network_time_window.py scripts/run_night.py tests/test_run_night.py; git commit -m 'NETWORK-TIME-OFF-ENFORCE-01 N1 fix round 2c: cleanup before proof without refusal repair; require explicit null claims; reject ambiguous census'","cwd":".","observed":{"result":"fail","exit_code":128,"tail":["fatal: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-ntp-n1-d528efb2/index.lock': Operation not permitted"]},"expected":{"exit_code":0,"tail_regex":"NETWORK-TIME-OFF-ENFORCE-01 N1 fix round 2c:"}}],"flags":[{"id":"F1","kind":"environment","level":"blocking","text":"git add and git commit both denied creation of index.lock in the shared Git metadata directory; no commit or push occurred.","needs":"Lead must stage and commit the four-file diff from this worktree using the supplied prefix."},{"id":"F2","kind":"environment","level":"nonblocking","text":"17 test IDs directly refused process listing, including the real-driver R3 case and unchanged deadline/census cases. SANDBOX-ONLY IDs are listed below.","needs":"Lead reruns on a process-listing-capable host with no foreign capture."},{"id":"F3","kind":"verification_gap","level":"nonblocking","text":"All 35 inherited failed IDs reproduced on the baseline: 34 in the archive replay, installer separately after supplying scratch Git metadata. Bind failures are baseline-reproduced, not asserted to be process-listing failures; two Python path mismatch cases remain.","needs":"Lead adjudicates inherited environment failures and owns final verification."},{"id":"F4","kind":"verification_gap","level":"nonblocking","text":"No new head exists. Final portable regressions pass on the uncommitted candidate; the full five-module run began before the final equivalent identity-access/docstring edits and new real-test receipt-check placement. Canonical discovery was not executed.","needs":"Final committed-head verification remains lead-owned."}]}
```

## Change

- **R3:** cleanup-only early [K] at [run_night.py:3354](/Users/edr/code/JouleWise-wt-ntp-n1-d528efb2/scripts/run_night.py:3354), implemented at [1377](/Users/edr/code/JouleWise-wt-ntp-n1-d528efb2/scripts/run_night.py:1377). Courier repair remains intact. Chain-written documents stay immutable and are named in `prior_documents` at [3539](/Users/edr/code/JouleWise-wt-ntp-n1-d528efb2/scripts/run_night.py:3539).
- **R1:** shared predicate at [network_time_window.py:352](/Users/edr/code/JouleWise-wt-ntp-n1-d528efb2/joulewise/network_time_window.py:352), consumed by recovery at `:392`, driver at `run_night.py:3564`, and dead-man at `:3619`.
- **R2:** ambiguous census rejection at [run_night.py:3770](/Users/edr/code/JouleWise-wt-ntp-n1-d528efb2/scripts/run_night.py:3770); failed attribution leaves every pid unresolved at `:3796`.

No A1/A2 stop condition was hit. Inherited test methods and protected proof functions remain unchanged; one supersede call site remains.

## Verification notes

**No new head exists.** Both staging and committing failed because the sandbox denied the shared Git `index.lock`. Results below concern the uncommitted candidate; baseline execution used the `36e8ba6e` archive under `/tmp/n1fix2c/base`.

| Regression | Candidate | Baseline assertion/result |
|---|---|---|
| R3-A | PASS | Expected no refusal; `refusal.json` existed |
| R3-B | PASS | `None != ['refusal.json']` for `prior_documents` |
| R3-C | PASS | PASS, control |
| Real-driver [K] | SANDBOX-ONLY | `/bin/ps` denied on both trees |
| R1 recovery, both malformed claims | PASS | `'restored' != 'chain_unproved'`, each |
| R1 `_chain_never_launched`, both malformed claims | PASS | `True is not false`, each |
| R1 dead-man | PASS | `0 != 3` for missing pid plus launch error; the other malformed claim already refused |
| Complete-null recovery/driver/dead-man controls | PASS | PASS |
| R2 exit-0 empty census | PASS | `True is not false` |
| R2 exit-1 empty control | PASS | PASS |
| R2 failed attribution | PASS | `{456: ['101 child']} != {}` |
| Deadline/census live regressions | SANDBOX-ONLY | `/bin/ps` denied on both trees |
| Unchanged `_assert_one_chain_alive_cause`, production-helper controls | PASS, 2/2 | PASS, 2/2 |

The real-driver fixture validated a schema-valid `quiet_predicate_evidence` receipt before process listing was denied. Its real chain/proof path was not executed.

All three deletion checks executed and failed by assertion:

- Restore early [K] repair → R3-A finds an unwanted refusal.
- Remove key presence → R1 restores instead of refusing.
- Remove exit-0-empty rejection → R2 incorrectly proves absence.

Final portable set: **12/12 passed**. Full requested five-module run: **521 tests, 38 failed assertions, 9 skips**. All 35 inherited failed test IDs reproduced on the baseline. Two failures concern Python executable-path mismatches; other bind-supervision failures reproduced without a claimed root cause. Exact names, assertions, and logs are in the [full report](/tmp/n1fix2c/report.md).

`SANDBOX-ONLY` IDs below share prefix `tests.test_run_night.`:

- `CaptureRefusalRecordTests.test_R3_real_driver_idle_chain_crash_runs_cleanup_before_failed_proof`
- `NightDriverTests.test_census_stop_with_detached_child_blocks_query_and_on`
- `NightDriverTests.test_clean_chain_runs_off_query_on`
- `NightDriverTests.test_dead_man_both_recovery_calls_withhold_on_while_child_lives`
- `NightDriverTests.test_deadline_stop_with_detached_child_blocks_query_and_on`
- `NightDriverTests.test_journaled_detached_capture_blocks_query_and_on`
- `NightDriverTests.test_journaled_detached_capture_without_path_signature_blocks_by_registry`
- `NightDriverTests.test_recovery_from_run_night_waits_for_detached_child_then_restores`
- `NightDriverTests.test_recovery_withholds_on_while_same_group_child_without_signature_lives`
- `NightDriverTests.test_same_group_live_child_blocks_query_and_on`
- `NightDriverTests.test_same_group_live_child_without_signature_blocks_query_and_on`
- `NightDriverTests.test_sampler_named_detached_capture_outside_night_blocks_query_and_on`
- `NightDriverTests.test_sweep_excludes_its_own_matching_command_row`
- `NightDriverTests.test_sweep_nonzero_exit_refuses_before_query_and_on`
- `NightDriverTests.test_sweep_timeout_refuses_before_query_and_on`
- `NightDriverTests.test_sweep_unparsed_row_refuses_before_query_and_on`
- `NightDriverTests.test_unjournaled_detached_capture_blocks_query_and_on`

## Residual risk

Committed-head and live verification remain pending. Canonical discovery was not run. The full module run preceded the final minor edits; final named regressions and scope inspection cover the final candidate.

Next step: the lead reviews and commits the four-file diff outside this sandbox, then reruns the five modules and live cases with no foreign capture. The [patch](/tmp/n1fix2c/fix2c.patch) and [full handoff](/tmp/n1fix2c/report.md) are preserved. No push occurred.