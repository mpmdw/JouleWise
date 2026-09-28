```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Repaired the 11 ruled legacy-identity test IDs; all six scoped modules pass, while the campaign importer has 17 failures outside this seat's write scope.",
  "workspace": {
    "base_requested": "6ac1b25f7e1a05640c4dbb6379df67b36ba50bb3",
    "base_mode": "exact",
    "head_start": "6ac1b25f7e1a05640c4dbb6379df67b36ba50bb3",
    "head_end": "6ac1b25f7e1a05640c4dbb6379df67b36ba50bb3",
    "upstream_end": null,
    "branch": "fix/2026-09-27-s1-r2-D"
  },
  "pathspec": [
    "tests/test_cli_run.py",
    "tests/test_audit_amplification.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest -q tests.test_cli_run tests.test_cli tests.test_audit_amplification tests.test_powermetrics tests.test_package_bundle_pack tests.test_partial_record_enclosure > /tmp/s1-seat-d-r2-modules.log 2>&1; result=$?; tail -n 80 /tmp/s1-seat-d-r2-modules.log; exit $result",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 247 tests in 132.617s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 247 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest -q tests.test_capture_pipeline_era tests.test_environment_admission tests.test_idle_admission > /tmp/s1-seat-d-r2-importers-small.log 2>&1; result=$?; tail -n 40 /tmp/s1-seat-d-r2-importers-small.log; exit $result",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 44 tests in 6.611s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 44 tests.*OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest -q tests.test_run_campaign > /tmp/s1-seat-d-r2-importer-run-campaign.log 2>&1; result=$?; tail -n 60 /tmp/s1-seat-d-r2-importer-run-campaign.log; exit $result",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 294 tests in 216.334s", "FAILED (failures=2, errors=15)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 294 tests.*OK"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The out-of-scope tests.test_run_campaign importer has 15 errors and 2 failures. Its errors include authenticate_window_members refusals, five duplicate battery_runner keyword errors, and three missing collection-key errors.",
      "needs": "Seat A or the lead repairs and reruns tests.test_run_campaign."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "A3 describes all 11 fixtures as mock bundles, but the raw-to-trace test formerly used powermetrics. Its spoof refusal now uses a mock bundle; a new sibling calls the raw-to-trace verifier on a powermetrics bundle.",
      "needs": "Lead reviews this fixture split with the R-list."
    }
  ]
}
```

## Change

A3 §5.9 rules that a written legacy identity does not exempt bytes absent from the historical list. Each of the 11 IDs now checks the **exact full problem list**. `B` below is `strict: battery_float_evidence_missing: not_applicable not bound (config.json digest does not match metadata.config_sha256)`.

| Test ID (`tests.test_cli_run.StrictValidateTests` unless noted) | Old expectation → new expectation | Coverage retained in sibling |
|---|---|---|
| `test_legacy_dispatch_tolerates_governed_additive_absence` | `[]` → `[B]` | Six-pair identity classification |
| `test_legacy_summary_missing_additive_null_keys_passes_strict` | `[]` → `[B]` | Six-pair identity classification |
| `test_all_six_allowlisted_legacy_bundles_keep_dispatch_semantics` | `[]` for each pair → `[B]` for each pair | `test_spoofed_legacy_identity_dispatch_classification_for_six_pairs` checks false before and true after each overwrite |
| `test_allowlisted_legacy_fresh_idle_metadata_mismatch_fails_strict` | `[raw idle trace mismatch]` → `[B]` | `test_legacy_idle_mismatch_diagnostic_directly` calls `_strict_idle_mean_uncertainty_problems` |
| `test_allowlisted_legacy_present_null_provenance_fails_strict` | Expected a provenance problem → `[B]` | `test_legacy_null_provenance_dispatch_diagnostic_directly` calls `_strict_reducer_version_dispatch` |
| `test_allowlisted_legacy_present_non_object_provenance_fails_strict` | Expected a provenance problem → `[summary provenance is not null or an object, B]` | The structural provenance problem remains in the exact list |
| `test_allowlisted_legacy_recorded_value_mutations_fail_strict` | Expected each mutated field in a problem → `[B]` | `test_legacy_recorded_value_mutations_compare_directly` calls `_strict_summary_differences` for all three fields |
| `test_current_bundle_spoofed_as_legacy_with_absent_provenance_passes` | `[]` → `[B]` | Six-pair identity classification |
| `test_legacy_summary_missing_honesty_fields_keeps_strict_tolerance` | `[]` → `[B]` | Six-pair identity classification |
| `tests.test_audit_amplification.StrictGateInteractionAmplification.test_allowlisted_legacy_identity_allows_missing_workload_provenance` | `[]` → `[B]` | Six-pair identity classification |
| `tests.test_audit_amplification.StrictGateInteractionAmplification.test_legacy_summary_tolerance_does_not_hide_raw_to_trace_order_drift` | Expected raw row/rail drift → `[B]` | `test_legacy_raw_to_trace_order_drift_diagnostic_directly` calls `_strict_raw_to_trace_problems` |

Before the edits, the 11 IDs produced **19 failures**: 17 in `test_cli_run.py` and 2 in `test_audit_amplification.py`. Afterward both modules pass whole; the other four scoped modules remain green. No historical identity was added, no pair was written to a mock bundle, and no file outside `WRITE_SCOPE` was edited.

## Verification notes

The remaining importer failures are in [test_run_campaign.py](/Users/edr/code/JouleWise-wt-s1r2-D-d528efb2/tests/test_run_campaign.py), outside this seat’s write scope. The five retry telemetry IDs (`test_cpu_admission_reads_final_attempt_telemetry`, `test_environment_refusal_does_not_hide_valid_retry_telemetry`, `test_missing_final_attempt_telemetry_fails_closed`, `test_retry_attempt_ledger_must_be_ordered_unique_and_decision_bound`, and `test_retry_member_survives_fixture_sleep_slack`) raise `TypeError` because `battery_runner` is passed twice. Seven IDs encounter `authenticate_window_members` refusals on prospective bundles: `test_r8_salvage_runner_appends_new_pinned_row_without_editing_failure`, `test_derivation_cli_mint_rejects_source_identity_postcondition_failure`, `test_neg8_reference_campaign_corpus_is_accepted_by_derivation_cli`, `test_recorded_supersession_resolves_present_retry_and_is_reported`, `test_whole_window_invalid_reference_is_excluded_and_cannot_pass`, `test_whole_window_production_verdict_fails_closed_without_end_reference`, and `test_whole_window_verdict_honors_and_reports_failed_member_waiver`. Three collection-verdict IDs raise `KeyError: 'collection'`; two whole-window assertions fail. The exact failures are in `/tmp/s1-seat-d-r2-importer-run-campaign.log`.

## Residual risk

The raw-to-trace fixture split noted in F2 needs the lead’s R-list review.