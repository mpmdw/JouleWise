```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Thin permanent-OFF receipts and capture admission implemented; restore-registry retirement and bench migration need scope.",
  "workspace": {
    "base_requested": "32ff9013",
    "base_mode": "exact",
    "head_start": "32ff901374024defa97fc3d137c5a699423676e7",
    "head_end": "32ff901374024defa97fc3d137c5a699423676e7",
    "upstream_end": "32ff901374024defa97fc3d137c5a699423676e7",
    "branch": "feat/2026-09-29-ntp-off-thin"
  },
  "pathspec": [
    "joulewise/network_time_off.py",
    "joulewise/arm_readiness_evidence_t0.py",
    "joulewise/quiet_predicate_campaign.py",
    "joulewise/t0_rehearsal.py",
    "scripts/capture_t0_step.py",
    "scripts/quiet_window_clock.sh",
    "scripts/run_night.py",
    "scripts/sample_quiet_predicate_evidence.py",
    "docs/phase_2/window_runbook.md",
    "tests/test_arm_readiness_dry_run.py",
    "tests/test_arm_readiness_evidence_author.py",
    "tests/test_arm_readiness_evidence_t0.py",
    "tests/test_capture_t0_step.py",
    "tests/test_quiet_predicate_campaign.py",
    "tests/test_run_night.py",
    "tests/test_sample_quiet_predicate_evidence.py",
    "tests/test_t0_rehearsal.py",
    "tests/test_network_time_off.py",
    "tests/fixtures/historical_clock_restore_5a.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_network_time_off > /tmp/ntpthin-module-final-v2.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "^OK(?: \\(skipped=\\d+\\))?$"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_capture_t0_step tests.test_t0_rehearsal tests.test_network_time_off > /tmp/ntpthin-capture-rehearsal-final.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "^OK(?: \\(skipped=\\d+\\))?$"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_t0_rehearsal > /tmp/ntpthin-rehearsal-final-v2.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK"]},
      "expected": {"exit_code": 0, "tail_regex": "^OK(?: \\(skipped=\\d+\\))?$"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_run_night > /tmp/ntpthin-night-final.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK (skipped=9)"]},
      "expected": {"exit_code": 0, "tail_regex": "^OK(?: \\(skipped=\\d+\\))?$"}
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_arm_readiness_evidence_t0 tests.test_arm_readiness_dry_run tests.test_arm_readiness_evidence_author > /tmp/ntpthin-arm-final.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK (skipped=5)"]},
      "expected": {"exit_code": 0, "tail_regex": "^OK(?: \\(skipped=\\d+\\))?$"}
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_quiet_predicate_campaign tests.test_sample_quiet_predicate_evidence > /tmp/ntpthin-qpe-final-v4.log 2>&1",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (failures=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "^OK(?: \\(skipped=\\d+\\))?$"}
    },
    {
      "id": "V7",
      "kind": "lint",
      "cmd": "/bin/bash -n scripts/quiet_window_clock.sh",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "NEEDS_SCOPE: active registry still requires clock.restore_recipe.v1. Its retirement and the bench's removed campaign hooks require unlisted paths. No out-of-scope edits; generic restore derivation/maps remain unchanged.",
      "needs": "Resume with the requested paths authorized; coordinate registry retirement with authorized Python removal and migrate the bench injection seam."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "SANDBOX-ONLY failure: tests.test_sample_quiet_predicate_evidence.CollectionTests.test_real_collect_no_power_reaps_all_recorded_workers. Diagnostic replay recorded PermissionError EPERM for /bin/ps.",
      "needs": "Lead rerun this whole module in an environment permitting its process probe."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Full canonical discovery and live hardware verification were not run; touched modules ran whole. Fixture passes do not qualify successor freeze/ARM while the registry requires restoration.",
      "needs": "After scope resolution, lead perform canonical discovery, final diff review and owned live gates."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "configs/arm_readiness/d117_row_registry_v2.json",
      "scripts/bench_replay_start_drift.py"
    ],
    "reason": "The active registry hard-requires restoration; the bench still rebinds removed SUDO/SYSTEMSETUP hooks.",
    "blocked_work": "Coherent removal of clock.restore_recipe.v1 and restore_after_* requirements; functioning safe bench replay.",
    "minimal_change": "Retire the active restore row and profile/lifecycle references; update already-authorized derivation/maps and validator count; switch bench to the injectable OFF runner and new receipt fields. Preserve historical sealed records."
  }
}
```

## Change

Implemented write-once OFF receipts, exact stdout admission, and same-boot ≥600-second admission on both clocks. Wired derivation, pack, evidence and claim-arm paths. Arm resync finishes OFF before the existing dwell and refuses existing captures. Removed automatic restore and prospective log admission from the evidence executor; preserved historical interpretation.

Removed the shell enable close-out and updated the runbook. Generic restore derivation/maps remain unchanged pending registry scope.

Line counts from `git diff --stat`, including untracked additions:

| Area | Added | Deleted | Net |
|---|---:|---:|---:|
| Production code | 299 | 320 | −21 |
| Runbook | 51 | 91 | −40 |
| Tests and fixtures | 589 | 753 | −164 |

Changes remain uncommitted. Intended commits:

- `feat(network-time): require settled OFF receipts before capture`
- `docs(network-time): keep OFF and resync only at arm`

Deleted test IDs below share the prefix `tests.test_quiet_predicate_campaign.`:

| Deleted ID suffix | Reason |
|---|---|
| `NetworkTimeControlTests.test_exact_off_stdout_reaches_settle_and_records_both_toggles` | Two-toggle behavior removed; receipt tests replace it. |
| `NetworkTimeControlTests.test_lower_case_stdout_or_nonzero_exit_refuses_before_any_envelope` | Replaced by module refusal tests. |
| `NetworkTimeControlTests.test_termination_during_settle_still_restores_network_time` | Automatic restoration removed. |
| `NetworkTimeControlTests.test_failed_restore_is_reported_with_its_own_exit_code` | Restore exit semantics removed. |
| `NetworkTimeControlTests.test_every_envelope_is_attested_from_the_timed_log` | Prospective H6 queries removed. |
| `NetworkTimeControlTests.test_an_applied_slew_inside_a_window_excludes_that_night_envelope` | Prospective H6 admission removed. |
| `NetworkTimeControlTests.test_the_production_commands_are_the_ruled_absolute_argv` | Replaced by exact OFF module tests. |
| `StartDriftCadenceTests.test_regression_5_the_attestation_runs_in_the_gap_never_beside_a_capture` | No prospective attestation runs. |
| `StartDriftCadenceTests.test_regression_5_a_stepped_wall_clock_keeps_the_window_over_the_capture` | Prospective query window removed. |
| `StartDriftCadenceTests.test_regression_6_a_failed_query_reaches_the_summary_as_unattested` | Prospective query admission removed. |
| `AttestationBudgetTests.test_a_gap_under_six_seconds_pushes_every_spawn_late_by_six_minus_gap` | Attestation gap cost removed. |
| `AttestationBudgetTests.test_the_bound_is_the_registrations_gap_and_a_timeout_keeps_the_schedule` | Attestation query budget removed. |
| `ZeroOutputGuardTests.test_a_body_without_the_syslog_header_is_asserted_never_authenticated` | Prospective query admission removed. |
| `UnreadableSessionRecordTests.test_a_record_that_vanishes_before_the_annotation_is_journalled_asserted` | Prospective session annotation removed. |
| `ExitCodePrecedenceTests.test_the_truth_table_over_outcome_cleanup_and_restore` | Restore-dependent exit precedence removed. |
| `NetworkTimeReceiptTests.test_an_off_that_times_out_writes_its_receipt_before_refusing` | Replaced by module timeout receipt test. |
| `RestoreReceiptTests.test_an_unreadable_or_non_dict_record_keeps_its_bytes` | Restore receipt removed. |
| `RestoreReceiptTests.test_no_exception_class_escapes_the_restore` | Restore function removed. |
| `RestoreReceiptTests.test_a_night_whose_record_is_corrupted_still_writes_its_outcome` | Restore receipt behavior removed. |
| `SessionRewriteFailureTests.test_a_night_whose_annotations_cannot_land_still_finishes` | Prospective annotations removed. |
| `RestoreOrderTests.test_the_restore_precedes_the_cleanup_record_on_every_path` | Automatic restore ordering removed. |

Three old IDs were renamed with updated coverage:

- `tests.test_capture_t0_step.CaptureT0StepTests.test_clock_disable_nonzero_refuses_command_failed`: now tests failed saved-receipt refusal without another command.
- `tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_rf21_rf22_fresh_clock_disable_requires_exit_and_exact_stdout`: now validates the saved OFF receipt.
- `tests.test_run_night.NightDriverTests.test_legacy_write_once_tuple_matches_base`: now requires the OFF receipt alongside all prior records.

## Verification notes

Every touched test module ran whole using `python3 -B`.

**SANDBOX-ONLY failure:** `tests.test_sample_quiet_predicate_evidence.CollectionTests.test_real_collect_no_power_reaps_all_recorded_workers`. Diagnostic replay recorded `/bin/ps` denied with `PermissionError: [Errno 1] Operation not permitted`. No failure was skipped or weakened.

Canonical discovery and live hardware validation were not run. Historical restore-registry tests use an explicit historical runbook fixture; those passes do not establish current freeze readiness.

## Residual risk

**NEEDS_SCOPE:** the active registry still requires restoration, so the new runbook currently blocks successor freeze/ARM. Code-only deletion would leave the registry unsatisfied; silently filtering its row would invent authority. Recommend coordinated prospective retirement while preserving historical seals.

Next step: resume with the two requested paths authorized, remove the generic restore requirements coherently, migrate the bench hooks, then perform canonical and lead-owned live verification.