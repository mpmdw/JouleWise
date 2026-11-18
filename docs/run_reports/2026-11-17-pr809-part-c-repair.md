# PR #809 Part C repair and STANDING-F0 rebind

The replacement W1 renewal candidate is `5434cb49d805768f6d5b8f82d71a3bef04901aba`
on `ops/2026-11-17-astra-small-fixes-f0-rebind`, a direct child of
`4d7dd28cc93bb02f6f6782dacd7af04abd6eda8e`. The candidate tree is
`7ea2f135e316417c30ab4c42bd1504c0cd6e6bff`. Its evaluator and the PR evaluator
have the same SHA-256, `f3a5211bdbae69160f43d9b354e96b95cd0534b85a7bb097ec2041d13fffa6c1`.
The W1 kit uses the runtime receipt and bundle as separate sources. The W1
runtime invocation distinguishes launch refusal from unusable evidence after
launch.

| Astra finding | Commit | Regression |
| --- | --- | --- |
| HIGH. Completed X_G disappears from the verdict | `48480e220`, `5434cb49d` | `KitSequenceTests.test_completed_x_g_with_missing_or_unreadable_evidence_fails`, `test_zero_exit_x_g_missing_contract_fields_fails` |
| HIGH. W1 missed the flag-only G1 timeout | `5434cb49d` | `PartCEvaluatorTimeoutTests.test_flag_only_timeout_on_next_unadmitted_turn_fails` and Astra's original `timeout` |
| HIGH. Failure sources are discarded | `48480e220`, `5434cb49d` | `PartCEvidenceReconciliationTests.test_failure_in_either_flag_source_or_later_interval_fails_both_roles`, `test_runtime_gate_waits_cannot_disagree_with_the_bundle`, `SidecarJournalTests.test_finalized_journal_failure_disagrees_with_bundle_for_both_roles` |
| HIGH. Truncated admissions hide a missing G1 | `48480e220`, `5434cb49d` | `PartCEvidenceReconciliationTests.test_admissions_count_cannot_be_reconciled_to_truncated_turns` |
| HIGH. Step-D trusts a contradictory summary | `48480e220`, `5434cb49d` | `PartCEvidenceReconciliationTests.test_step_d_g0_interval_must_agree_with_summary_and_bounds`, `test_step_d_requires_finite_nonnegative_wait_and_finite_release_facts` |
| HIGH. D_bank skips an errored first reading | `48480e220`, `5434cb49d` | `SidecarJournalTests.test_failed_first_reading_cannot_be_replaced_by_a_later_nominal_reading` |
| MED. Duty budget silently picks the runtime | `48480e220`, `5434cb49d` | `PartCEvidenceReconciliationTests.test_runtime_and_bundle_duty_budgets_are_reported_and_must_match` |
| MED. Failed Air notification starts suppression | `5be6047c0` | `InstallerTest.test_missing_repo_wrapper_retries_after_failed_notification` |

## Synthetic verification

The regressions reproduced the defects before repair. Astra's harness replays
the PR evaluator through the W1 kit and runs the W1 evaluator through that same
kit. The post-repair replay keeps Astra's inputs and changes the assertions
to expect refusal. The contrast replay reads the saved table after the
expected failure. Both evaluator selections completed all Part C probes.
The Air probe executes the PR wrapper for both harness selections because the
Air watcher is shipped on the PR line.

| Probe | Output on both evaluator selections |
| --- | --- |
| Original flag-only timeout, with or without an interval | `other_failure` |
| Original completed X_G with missing episode, and zero-exit incomplete receipt | `other_failure`, X_G line present |
| Runtime-only, bundle-only, thermal and journal timeouts or deadman evidence | `other_failure` |
| Three runtime admissions with a truncated list or missing G1 | `other_failure` |
| Contradictory or invalid Step-D interval, wait, reference or slope | `other_failure` |
| First reading has a reader error or nonzero OS level | `start_state_failed` |
| Matching over-limit budget, then disagreeing budgets | `mechanics_gate_time_failed`, then `other_failure` with both budgets shown |
| Failed then successful Air notification | `NOTIFY failed`, then `NOTIFY ok` |

Astra's guarded focused selection passed 177 PR tests and 41 W1 tests.
Seventeen supplemental W1 sidecar and runtime contract tests also passed.
The W1 clean launcher refusal control still passes with X_G recorded as
not run. The local selection uses synthetic fixtures. The complete sharded
suite and the live gate require separate verification.

The prior CI failure in run `44210289036` was shard 4. Both failures were in
`tests/test_calibration_ledger_custody.py` and concerned fixture CLI deadlines.
The test module and implementation are outside the PR diff. The lead review
and the renewal gate can use the exact replacement candidate above.
