```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Repaired six scoped test files; remaining claim-path fixtures and a finalizer identity pin need a lead ruling.",
  "workspace": {
    "base_requested": "4b4660dec4948f8b6d1f43a4d1e03569f886657b",
    "base_mode": "exact",
    "head_start": "4b4660dec4948f8b6d1f43a4d1e03569f886657b",
    "head_end": "4b4660dec4948f8b6d1f43a4d1e03569f886657b",
    "upstream_end": null,
    "branch": "fix/2026-09-27-s1-regress-A"
  },
  "pathspec": [
    "tests/test_run_campaign.py",
    "tests/test_analysis_claims.py",
    "tests/test_analysis_finalizer.py",
    "tests/test_collector_analysis_manifest_id.py",
    "tests/test_corpus_strict_validation.py",
    "tests/test_experiment.py"
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
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_run_campaign",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 294 tests in 869.860s", "FAILED (failures=8, errors=19)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_analysis_integration",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 116 tests in 180.982s", "FAILED (errors=45)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_analysis_finalizer",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 16 tests in 131.477s", "FAILED (failures=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_analysis_claims",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 64 tests in 7.076s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_collector_analysis_manifest_id",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 16 tests in 189.615s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_experiment",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 39 tests in 29.264s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_pipeline_smoke_tail",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 4 tests in 10.433s", "FAILED (errors=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_corpus_strict_validation",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 3 tests in 2.487s", "OK (skipped=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V9",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_cpu_admission_reads_final_attempt_telemetry tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_environment_refusal_does_not_hide_valid_retry_telemetry tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_missing_final_attempt_telemetry_fails_closed tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_retry_attempt_ledger_must_be_ordered_unique_and_decision_bound",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 4 tests in 98.566s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V10",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_retry_member_survives_fixture_sleep_slack",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 31.412s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V11",
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
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "tests.test_analysis_integration.AnalysisIntegrationTests.test_real_controller_unpinned_model_is_included_by_loader and 44 other outcomes use a mock claim corpus. Rebinding and pairing still leaves missing raw powermetrics, uncertainty evidence, and provenance mismatches.",
      "needs": "Rule the canonical strict-valid corpus construction for this claim path; keep the strict gate closed."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "tests.test_analysis_finalizer.AnalysisFinalizerTests.test_legacy_finalization_matches_parent_projection_without_floor_identity_fields pins am-4e496e5f..., while authenticated pair evidence changes the projection to am-6e45b574.... The permitted R-list rule does not cover this hash assertion.",
      "needs": "Rule whether to repin the projection or supply another evidence-bearing fixture."
    },
    {
      "id": "F3",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "tests.test_pipeline_smoke_tail.PipelineSmokeTailTests.test_mock_config_tail_pending_data_only_ruling reaches the strict mock refusal before its downstream assertions; tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_whole_window_cli_uses_campaign_membership_and_strict_validation still has an incomplete synthetic claim bundle.",
      "needs": "Rule the mock-refusal split and the evidence-bearing whole-window fixture."
    },
    {
      "id": "F4",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The last whole test_run_campaign run began before the final retry fixture edits. All five affected retry tests passed afterward in guarded targeted runs. Seven importing modules ran together: 235 tests, 3 failures and 19 errors in out-of-scope test_bracket_binding_cli and test_whole_window_selection.",
      "needs": "Lead reruns the combined gate after adjudication."
    }
  ]
}
```

## Change

Scout failing-outcome counts compared with the latest whole-module runs:

| File | Before → latest whole run | Repair |
|---|---:|---|
| `test_run_campaign.py` | 71 → 27 | Paired AXI entries, capture custody, anchor fixtures, and whole-window fixtures; five retry tests passed in later targeted runs |
| `test_analysis_integration.py` | 47 → 45 | No retained edit; central claim corpus needs a ruling |
| `test_analysis_finalizer.py` | 15 → 1 | Rebound nonmock bundles and wrote passing pairs |
| `test_analysis_claims.py` | 6 → 0 | Copied and paired floor members |
| `test_collector_analysis_manifest_id.py` | 8 → 0 | Added a temporary identity probe for standalone module execution |
| `test_experiment.py` | 12 → 0 | Injected battery runner; admitted mock aggregation only at the five allowed direct test calls |
| `test_pipeline_smoke_tail.py` | 4 → 1 | No retained edit; mock claim-path test needs a ruling |
| `test_corpus_strict_validation.py` | 3 → 0 | Rebound and paired its generated bundle |

**R-list, separate from call forms:** `test_campaign_core_callers_keep_replacement_custody_replay_only` and `test_direct_campaign_bracket_explicitly_replays_relocated_custody` previously expected `calibration_ledger_custody_invalid` when issuing custody had no original. They now assert `CustodyFailure` for capture `instrument_evidence.json`, its expected digest, and an absent observed digest, as text 10a requires. The new sibling `test_intact_issuing_custody_keeps_candidate_count_mismatch_condition` preserves the old condition assertion with intact original custody. `test_campaign_core_mode_counterfactuals` now accepts the same named custody failure from its planted issuing mutation instead of requiring an empty error list.

**Call-form list, separate from the R-list:** `test_experiment.py` direct `aggregate_experiment(..., admit_mock_window=True)` calls are in `test_three_complete_bundles_and_manifest` (line 555), `test_aggregate_reruns_from_minimal_manifest` (639), `test_partial_manifest_aggregates_only_listed_members` (653), `test_interrupt_before_aggregation_leaves_completed_member_registered` (714), and `test_aggregate_exception_is_recorded_for_retry` (740). Their assertions were retained.

## Verification notes

The campaign whole-module result predates the final retry edit; the five retry tests then passed under the guard. The importing-module run finished with `Ran 235 tests in 539.762s` and `FAILED (failures=3, errors=19)`; those failures are in files assigned outside seat A. `git diff --check` passed. Added diff lines contain no prohibited gate patches, skip annotations, raw battery writes, or pair observations outside the helper. No file outside `WRITE_SCOPE` was edited.

**NEEDS_RULING:** For `test_analysis_integration.py`’s named claim-corpus tests, the options are an approved strict-valid corpus construction or an explicitly ruled refusal split for mock-subject tests. I recommend defining the corpus first; the present generated bundles fail checks beyond the battery pair. For the finalizer hash pin, the options are a reviewed repin or another evidence-bearing fixture that preserves the old projection. The pipeline mock tail and the whole-window synthetic bundle need the corresponding refusal and fixture decisions. These decisions block completion; no production gate was relaxed.

## Residual risk

The lead’s post-ruling full run must establish the final campaign count and check the importer failures alongside seats B and C.