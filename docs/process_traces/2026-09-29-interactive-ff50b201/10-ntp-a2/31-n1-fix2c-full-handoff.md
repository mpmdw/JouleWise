```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"blocked","completion":"partial","summary":"R1, R2 and R3 implemented and deletion-checked; required commit blocked by sandbox Git metadata permissions.","workspace":{"base_requested":"36e8ba6e345653e4fb4ac54f711dc49b27c1d30c","base_mode":"exact","head_start":"36e8ba6e345653e4fb4ac54f711dc49b27c1d30c","head_end":"36e8ba6e345653e4fb4ac54f711dc49b27c1d30c","upstream_end":"36e8ba6e345653e4fb4ac54f711dc49b27c1d30c","branch":"feat/2026-09-28-ntp-n1"},"pathspec":["joulewise/network_time_window.py","tests/test_network_time_window.py","scripts/run_night.py","tests/test_run_night.py"],"unowned_dirty":[],"verdict":{"implementation":"implemented","acceptance":"pending_verification"},"verification":[{"id":"V1","kind":"suite","cmd":"PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest -v tests.test_network_time_window tests.test_run_night tests.test_night_gate tests.test_arm_retry tests.test_launch_window > /tmp/n1fix2c/modules-precommit.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 521 tests in 758.393s","FAILED (failures=38, skipped=9)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V2","kind":"test","cmd":"PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B /tmp/n1fix2c/run_regressions.py head-portable > /tmp/n1fix2c/candidate-portable-output.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 12 tests in 1.763s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V3","kind":"test","cmd":"PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B /tmp/n1fix2c/run_regressions.py baseline > /tmp/n1fix2c/baseline-replay-output.log 2>&1","cwd":".","observed":{"result":"pass","exit_code":1,"tail":["Ran 15 tests in 2.558s","FAILED (failures=12)"]},"expected":{"exit_code":1,"tail_regex":"FAILED \\(failures=12\\)"}},{"id":"V4","kind":"test","cmd":"PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B /tmp/n1fix2c/run_regressions.py head > /tmp/n1fix2c/candidate-all-output.log 2>&1","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["Ran 15 tests in 2.429s","FAILED (failures=3)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V5","kind":"test","cmd":"PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B /tmp/n1fix2c/run_mutations.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["R3: RED BY ASSERTION (exit 1)","R1: RED BY ASSERTION (exit 1)","R2: RED BY ASSERTION (exit 1)","All three deletions killed"]},"expected":{"exit_code":0,"tail_regex":"All three deletions killed"}},{"id":"V6","kind":"test","cmd":"PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B /tmp/n1fix2c/record_controls.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["Ran 2 tests in 0.102s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V7","kind":"test","cmd":"PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B /tmp/n1fix2c/record_controls.py","cwd":"/tmp/n1fix2c/base","observed":{"result":"pass","exit_code":0,"tail":["Ran 2 tests in 0.191s","OK"]},"expected":{"exit_code":0,"tail_regex":"OK"}},{"id":"V8","kind":"inspection","cmd":"/opt/homebrew/bin/python3 -B /tmp/n1fix2c/inspect_scope.py","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["supersede=True call sites: one","scope: PASS (4 paths)"]},"expected":{"exit_code":0,"tail_regex":"scope: PASS \\(4 paths\\)"}},{"id":"V9","kind":"test","cmd":"PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B /tmp/n1fix2c/replay_inherited_failures.py","cwd":".","observed":{"result":"pass","exit_code":1,"tail":["Ran 35 tests in 24.020s","FAILED (failures=36, errors=1)"]},"expected":{"exit_code":1,"tail_regex":"FAILED \\(failures=36, errors=1\\)"}},{"id":"V10","kind":"test","cmd":"PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest -v tests.test_run_night.NightDriverTests.test_installer_refuses_active_chain_and_rolls_back_partial_bootstrap > /tmp/n1fix2c/baseline-installer.log 2>&1","cwd":"/tmp/n1fix2c/base","observed":{"result":"pass","exit_code":1,"tail":["AssertionError: 2 != 3 : probe receipt driver_python mismatch","Ran 1 test in 2.574s","FAILED (failures=1)"]},"expected":{"exit_code":1,"tail_regex":"FAILED \\(failures=1\\)"}},{"id":"V11","kind":"other","cmd":"git diff --check; git add -- joulewise/network_time_window.py tests/test_network_time_window.py scripts/run_night.py tests/test_run_night.py; git commit -m 'NETWORK-TIME-OFF-ENFORCE-01 N1 fix round 2c: cleanup before proof without refusal repair; require explicit null claims; reject ambiguous census'","cwd":".","observed":{"result":"fail","exit_code":128,"tail":["fatal: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-ntp-n1-d528efb2/index.lock': Operation not permitted"]},"expected":{"exit_code":0,"tail_regex":"NETWORK-TIME-OFF-ENFORCE-01 N1 fix round 2c:"}}],"flags":[{"id":"F1","kind":"environment","level":"blocking","text":"git add and git commit both denied creation of index.lock in the shared Git metadata directory; no commit or push occurred.","needs":"Lead must stage and commit the four-file diff from this worktree using the supplied prefix."},{"id":"F2","kind":"environment","level":"nonblocking","text":"17 test IDs directly refused process listing, including the real-driver R3 case and unchanged deadline/census cases. SANDBOX-ONLY IDs are listed below.","needs":"Lead reruns on a process-listing-capable host with no foreign capture."},{"id":"F3","kind":"verification_gap","level":"nonblocking","text":"All 35 inherited failed IDs reproduced on the baseline: 34 in the archive replay, installer separately after supplying scratch Git metadata. Bind failures are baseline-reproduced, not asserted to be process-listing failures; two Python path mismatch cases remain.","needs":"Lead adjudicates inherited environment failures and owns final verification."},{"id":"F4","kind":"verification_gap","level":"nonblocking","text":"No new head exists. Final portable regressions pass on the uncommitted candidate; the full five-module run began before the final equivalent identity-access/docstring edits and new real-test receipt-check placement. Canonical discovery was not executed.","needs":"Final committed-head verification remains lead-owned."}]}
```

## Change

R3: early [K] cleanup now saves cleanup only, without repairing the outcome or writing a refusal (`scripts/run_night.py:1377,1410,3354`). Courier preparation retains full repair. Existing chain-written documents remain unchanged and are named under `prior_documents` (`scripts/run_night.py:3539`).

R1: one predicate requires present-and-null pid/pgid (`joulewise/network_time_window.py:352`), used by recovery (`:392`), the driver (`scripts/run_night.py:3564`) and dead-man (`:3619`); exit-record clauses remain at their original sites.

R2: exit-0 empty batch census is unproved with census_ambiguous (`scripts/run_night.py:3770`); nonzero attribution leaves every pid unresolved (`:3796`).

No A1/A2 stop condition was hit. All inherited class methods and the three protected proof functions are AST-identical to the baseline; one supersede call site remains. No scope expansion, subagent, real systemsetup/sntp/powermetrics/log query, or battery read was performed. Four allowlisted files are modified; no pre-existing dirty paths existed. RUN_STATE/TASK_QUEUE/repository reports were left lead-owned.

## Verification notes

No new head exists: staging and committing failed because sandbox permissions deny shared Git metadata. Candidate results below refer to the uncommitted diff at unchanged HEAD 36e8ba6e. Baseline production files came from git archive 36e8ba6e under /tmp/n1fix2c/base; current regression test files were overlaid. Scratch Git metadata was added solely to resolve the inherited installer test's HEAD lookup.

| Regression | Candidate | Assertion on 36e8ba6e |
|---|---|---|
| R3-A test_R3_A_early_cleanup_leaves_verdict_to_failed_proof | PASS | _refusal_paths(night) == [] failed: refusal.json existed |
| R3-B test_R3_B_chain_refusal_is_immutable_and_named_by_driver | PASS | prior_documents: None != ['refusal.json'] |
| R3-C test_R3_C_complete_outcome_control | PASS | PASS (control) |
| Real driver test_R3_real_driver_idle_chain_crash_runs_cleanup_before_failed_proof | SANDBOX-ONLY | SANDBOX-ONLY: /bin/ps denied; no defect assertion executed |
| R1 test_R1_recovery_rejects_missing_identity_keys | PASS | 'restored' != 'chain_unproved' |
| R1 test_R1_recovery_rejects_missing_pid_with_launch_error | PASS | 'restored' != 'chain_unproved' |
| R1 test_R1_driver_rejects_incomplete_nonlaunch_claims | PASS | True is not false, for both malformed claims |
| R1 test_R1_deadman_rejects_incomplete_nonlaunch_claims | PASS | 0 != 3 for missing pid + launch_error; missing both + popen_attempted=False already refused on baseline |
| Complete null recovery / driver / inherited dead-man control | PASS | PASS |
| R2 test_R2_empty_successful_batch_is_not_capture_proof | PASS | True is not false |
| R2 test_R2_empty_absent_batch_still_proves_capture_absent | PASS | PASS (control) |
| R2 test_R2_failed_attribution_leaves_every_pid_unresolved | PASS | {456: ['101 child']} != {} |
| Unchanged deadline/census live tests | SANDBOX-ONLY | SANDBOX-ONLY: /bin/ps denied |
| Unchanged _assert_one_chain_alive_cause through production helper controls, deadline/census | PASS (2/2) | PASS (2/2) |

The real-driver fixture can produce the receipt: final execution validated a schema-valid C5 quiet_predicate_evidence receipt before the process-listing gate refused. Its real chain/proof path was not executed. The read production order is 3353/3354 cleanup → 3366 proof → 3367/3369 failed-proof abort → 3425/3428 result-step refusal.

All three red-by-deletion checks executed in scratch: restoring early [K]'s full repair made R3-A fail with an unexpected refusal document; deleting key presence made R1 fail with restored != chain_unproved; deleting exit-0-empty rejection made R2 fail with True is not false. Every mutant failed by assertion (exit 1); no candidate file was mutated.

Final portable set: 12/12 PASS. Final named set: 15 tests, 3 SANDBOX-ONLY failures. Baseline named set: 15 tests, 12 failed assertions (9 defect assertions plus 3 environment assertions). Full requested five-module run: 521 tests, 38 failed assertions, 9 skips. All inherited failed test IDs were reproduced on the baseline; no inherited assertion was weakened. Two full-run failures are Python executable-path mismatches, and bind-supervision failures are baseline-reproduced without a claimed root cause.

SANDBOX-ONLY (direct process-listing denial):

- `tests.test_run_night.CaptureRefusalRecordTests.test_R3_real_driver_idle_chain_crash_runs_cleanup_before_failed_proof`
- `tests.test_run_night.NightDriverTests.test_census_stop_with_detached_child_blocks_query_and_on`
- `tests.test_run_night.NightDriverTests.test_clean_chain_runs_off_query_on`
- `tests.test_run_night.NightDriverTests.test_dead_man_both_recovery_calls_withhold_on_while_child_lives`
- `tests.test_run_night.NightDriverTests.test_deadline_stop_with_detached_child_blocks_query_and_on`
- `tests.test_run_night.NightDriverTests.test_journaled_detached_capture_blocks_query_and_on`
- `tests.test_run_night.NightDriverTests.test_journaled_detached_capture_without_path_signature_blocks_by_registry`
- `tests.test_run_night.NightDriverTests.test_recovery_from_run_night_waits_for_detached_child_then_restores`
- `tests.test_run_night.NightDriverTests.test_recovery_withholds_on_while_same_group_child_without_signature_lives`
- `tests.test_run_night.NightDriverTests.test_same_group_live_child_blocks_query_and_on`
- `tests.test_run_night.NightDriverTests.test_same_group_live_child_without_signature_blocks_query_and_on`
- `tests.test_run_night.NightDriverTests.test_sampler_named_detached_capture_outside_night_blocks_query_and_on`
- `tests.test_run_night.NightDriverTests.test_sweep_excludes_its_own_matching_command_row`
- `tests.test_run_night.NightDriverTests.test_sweep_nonzero_exit_refuses_before_query_and_on`
- `tests.test_run_night.NightDriverTests.test_sweep_timeout_refuses_before_query_and_on`
- `tests.test_run_night.NightDriverTests.test_sweep_unparsed_row_refuses_before_query_and_on`
- `tests.test_run_night.NightDriverTests.test_unjournaled_detached_capture_blocks_query_and_on`

Other inherited failed IDs, baseline-reproduced (not labelled SANDBOX-ONLY):

- `tests.test_run_night.BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go`
- `tests.test_run_night.BindSupervisionProcessTests.test_blocking_join_startup_and_post_publication`
- `tests.test_run_night.BindSupervisionProcessTests.test_census_hit_interrupts_a_real_hung_sample`
- `tests.test_run_night.BindSupervisionProcessTests.test_descendant_descriptor_and_group_cancellation`
- `tests.test_run_night.BindSupervisionProcessTests.test_exit_without_result_is_error_never_quiet`
- `tests.test_run_night.BindSupervisionProcessTests.test_final_hard_checks_follow_delayed_journal_ack`
- `tests.test_run_night.BindSupervisionProcessTests.test_header_plus_one_byte_never_blocks_recv`
- `tests.test_run_night.BindSupervisionProcessTests.test_large_frame_is_incremental_and_still_bounded`
- `tests.test_run_night.BindSupervisionProcessTests.test_oversized_length_and_flood_are_bounded`
- `tests.test_run_night.BindSupervisionProcessTests.test_parent_measures_whole_round_cost`
- `tests.test_run_night.BindSupervisionProcessTests.test_partial_header_and_body_eof_are_errors`
- `tests.test_run_night.BindSupervisionProcessTests.test_post_send_hang_is_consumed_once_and_reaped`
- `tests.test_run_night.BindSupervisionProcessTests.test_pre_send_local_timeout_and_late_global_expiry`
- `tests.test_run_night.BindSupervisionProcessTests.test_signalled_child_cannot_hold_cleanup_past_budget`
- `tests.test_run_night.BindSupervisionProcessTests.test_slow_chunks_keep_census_and_deadline_fixed`
- `tests.test_run_night.BindSupervisionProcessTests.test_stalled_census_does_not_suppress_later_census`
- `tests.test_run_night.NightDriverTests.test_installer_refuses_active_chain_and_rolls_back_partial_bootstrap`
- `tests.test_run_night.NightDriverTests.test_preflight_emits_json_without_running_or_creating_custody`
- `tests.test_run_night.QuietDriverIntegrationTests.test_supervised_worker_is_reaped_on_cancellation`

## Residual risk

Live proof and committed-head verification remain pending. Registered R4/R5/NIT-1/NIT-2/NIT-3 limits were not changed. Canonical unittest discovery was not run. The full module run preceded final non-loop edits; final portable/named regressions and scope inspection cover the final uncommitted candidate, not a new commit.

Next exact step: in the lead's authorized environment, inspect the four-file diff, stage it, and execute:

```
git commit -m 'NETWORK-TIME-OFF-ENFORCE-01 N1 fix round 2c: cleanup before proof without refusal repair; require explicit null claims; reject ambiguous census'
```

Then run the five modules and real-driver/deadline/census cases on the committed head outside this sandbox with no foreign capture, and carry the result to the fresh delta seat. Do not push from this seat.

Artifacts: fix2c.patch; report-envelope.json; modules-precommit.log; head-portable-regressions-final.log; head-regressions-final.log; baseline-regressions-final.log; deletion-R1.log; deletion-R2.log; deletion-R3.log; inherited-failures-baseline.log; baseline-installer.log; record_controls.py; run_regressions.py; run_mutations.py; inspect_scope.py.
