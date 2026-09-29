```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Repaired the floor fixtures and golden report; three granted T2 tests still need a ruling on current whole-window refusals.",
  "workspace": {
    "base_requested": "cdfb27ce",
    "base_mode": "exact",
    "head_start": "cdfb27ce1396fa98f8d20963cfdbbe7675d6ad66",
    "head_end": "cdfb27ce1396fa98f8d20963cfdbbe7675d6ad66",
    "upstream_end": null,
    "branch": "fix/2026-09-28-s1-r3-B"
  },
  "pathspec": [
    "tests/test_floor_extraction.py",
    "tests/fixtures/d117_postcollection_trust/extraction_report.json"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_floor_extraction",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 177 tests in 24.515s", "FAILED (failures=1, errors=24)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "set -o pipefail; PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_floor_extraction 2>&1 | tail -100",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 178 tests in 26.773s", "FAILED (failures=3)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_floor_extraction.CpuAndWholeWindowClaimBarrierTests.test_floor_cpu_ledger_rejects_duplicates_reordering_mismatch_and_absence tests.test_floor_extraction.D117MintConsumptionProfileTests.test_production_extractor_path_matches_checked_in_golden",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 2 tests in 0.060s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_floor_extraction.TelemetryIdentityGateTests.test_physical_member_exercises_floor_mock_barrier",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 0.028s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_bfgs_fixtures",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 23 tests in 146.632s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V7",
      "kind": "other",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B scripts/fixture_orphan_census.py --fail-on-orphans",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": ["{\"error\": \"PermissionError: [Errno 1] Operation not permitted: 'ps'\"}"]
      },
      "expected": {"exit_code": 0, "tail_regex": ".*"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "test_failed_adapter_continuity_refuses_but_clean_core_passes remains red: _current_core_rederivation_reasons emits environment_admission_missing; whole-window validation also emits whole_window_verdict_provenance_invalid.",
      "needs": "Rule this test ID without adding a parity ID or a third switch."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "test_later_passed_row_cannot_supersede_failed_whole_window_row remains red: current whole-window rederivation and _validate_row_uncached return adapter_continuity_failed, environment_admission_missing, whole_window_neg8_verdict_failed, and whole_window_verdict_provenance_invalid instead of the pinned conflict tuple.",
      "needs": "Rule this test ID without changing its assertion."
    },
    {
      "id": "F3",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "test_whole_window_rederives_neg8_verdict_from_member_summaries remains red: current whole-window rederivation and _validate_row_uncached return environment_admission_missing and whole_window_verdict_provenance_invalid.",
      "needs": "Rule this test ID without changing its assertion."
    },
    {
      "id": "F4",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The session-end orphan census could not invoke ps in this sandbox.",
      "needs": "Lead reruns the census where process observation is permitted."
    }
  ]
}
```

## Change

Added physical config binding and controller-helper battery pairs to the granted floor fixtures, with `exemption_parity(self.id())` inside each of the 21 granted T2 test bodies. The T1 ledger fixture now has its final passing pair. Added the floor mock-barrier sibling using the ruling’s consumer-side identity patch.

Regenerated the golden report from the extractor. Its leaf diff contains exactly five added `pass` statuses and five changed `summary_sha256` values. No numeric, exclusion, or refusal leaf changed; all five members remain admitted.

## Verification notes

For every ID below, prepend `tests.test_floor_extraction.`. **RED** means the charging-pair plant made the test fail. The plant exposed `battery_float_confounded` except for the T1 ledger test, which refused with `environment_admission_missing`. In two subtest cases, an ensuing `UnboundLocalError` followed the battery refusal.

| Test ID suffix | Class | Result | Plant |
|---|---|---|---|
| `CpuAndWholeWindowClaimBarrierTests.test_current_campaign_log_malformed_row_refuses_join` | T2 | GREEN | RED |
| `CpuAndWholeWindowClaimBarrierTests.test_failed_adapter_continuity_refuses_but_clean_core_passes` | T2 | NEEDS_RULING | RED |
| `CpuAndWholeWindowClaimBarrierTests.test_floor_requires_campaign_bound_whole_window_and_adapter_evidence` | T2 | GREEN | RED |
| `CpuAndWholeWindowClaimBarrierTests.test_frozen_replay_manifest_duplicate_retains_committed_semantics` | T2 | GREEN | RED |
| `CpuAndWholeWindowClaimBarrierTests.test_later_passed_row_cannot_supersede_failed_whole_window_row` | T2 | NEEDS_RULING | RED |
| `CpuAndWholeWindowClaimBarrierTests.test_whole_window_core_rejects_duplicate_member_occurrences` | T2 | GREEN | RED |
| `CpuAndWholeWindowClaimBarrierTests.test_whole_window_rederives_neg8_verdict_from_member_summaries` | T2 | NEEDS_RULING | RED |
| `D117MintConsumptionProfileTests.test_production_extractor_path_matches_checked_in_golden` | T2 | GREEN | RED |
| `EvaluationBasisPlumbingTests.test_explicit_basis_reaches_both_consumers_and_allowance_records` | T2 | GREEN | RED |
| `ExtractionCliTests.test_additional_refusal_is_not_rescued_by_attribution_label` | T2 | GREEN | RED |
| `ExtractionCliTests.test_cli_relocated_custody_does_not_suppress_floors` | T2 | GREEN | RED |
| `ExtractionCliTests.test_evaluation_basis_flag_reaches_extract_cells` | T2 | GREEN | RED |
| `ExtractionCliTests.test_spec_extraction_report_and_exit_codes` | T2 | GREEN | RED |
| `ExtractionCliTests.test_spec_extraction_via_extract_cells_matches_direct_calls` | T2 | GREEN | RED |
| `ExtractionCliTests.test_zero_scatter_with_nonzero_admissible_width_is_labelled_extraction` | T2 | GREEN | RED |
| `SpecMembershipBindingTests.test_full_coverage_has_no_membership_refusal` | T2 | GREEN | RED |
| `SpecMembershipBindingTests.test_omission_within_addressed_campaign_still_refuses` | T2 | GREEN | RED |
| `SpecMembershipBindingTests.test_omitted_null_manifest_member_refuses_as_unattributable` | T2 | GREEN | RED |
| `SpecMembershipBindingTests.test_omitting_a_campaign_member_refuses_the_extraction` | T2 | GREEN | RED |
| `SpecMembershipBindingTests.test_referenced_null_manifest_member_not_flagged_unattributable` | T2 | GREEN | RED |
| `SpecMembershipBindingTests.test_sibling_campaign_under_runs_root_does_not_force_refusal` | T2 | GREEN | RED |
| `CpuAndWholeWindowClaimBarrierTests.test_floor_cpu_ledger_rejects_duplicates_reordering_mismatch_and_absence` | T1 | GREEN | RED |
| `TelemetryIdentityGateTests.test_physical_member_exercises_floor_mock_barrier` | sibling | GREEN | RED |

The **R-list is empty**. The three `NEEDS_RULING` IDs and refusing checks are recorded in flags F1–F3. Floor-module results moved from **1 failure and 24 errors in 177 tests** to **3 failures and no errors in 178 tests**; the added test is the sibling. An in-memory omission of the floor mock refusal also made the sibling RED (`mock_telemetry_claim_ineligible` absent).

The charging-pair plant was run under the battery guard with this exact harness; its tail was `PLANT COUNTS 23 1 25` (23 test IDs; subtests account for multiple errors):

```sh
PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B - <<'PY'
import unittest
import tests.test_floor_extraction as m
import tests.bfgs_fixtures as f
real_bind=m.bind_passing_claim_bundle
def planted_bind(*args,**kwargs):
    real_bind(*args,**kwargs)
    f.write_charging_pair(args[0]/args[1])
m.bind_passing_claim_bundle=planted_bind
m.write_passing_pair=f.write_charging_pair
f.write_passing_pair=f.write_charging_pair
ids=[i for i in sorted(f.PARITY_TEST_IDS) if i.startswith('tests.test_floor_extraction.')]
ids += ['tests.test_floor_extraction.CpuAndWholeWindowClaimBarrierTests.test_floor_cpu_ledger_rejects_duplicates_reordering_mismatch_and_absence','tests.test_floor_extraction.TelemetryIdentityGateTests.test_physical_member_exercises_floor_mock_barrier']
class Result(unittest.TextTestResult):
 def addSuccess(self,test): super().addSuccess(test); print('PLANT GREEN',test.id(),flush=True)
 def addFailure(self,test,err): super().addFailure(test,err); print('PLANT RED',test.id(),str(err[1]).splitlines()[0],flush=True)
 def addError(self,test,err): super().addError(test,err); print('PLANT RED',test.id(),str(err[1]).splitlines()[0],flush=True)
runner=unittest.TextTestRunner(stream=open('/dev/null','w'),resultclass=Result,verbosity=0)
result=runner.run(unittest.defaultTestLoader.loadTestsFromNames(ids))
print('PLANT COUNTS',result.testsRun,len(result.failures),len(result.errors),flush=True)
PY
```

## Residual risk

The three red T2 tests need the lead’s per-ID ruling. Their current whole-window refusals survive the granted first-form parity; no ID list, production check, assertion, or third switch was changed.