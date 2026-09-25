```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Focused parity and third-row tests pass, but driver kind selection gains an unauthenticated fallback and malformed plans can escape the sealer without a typed refusal.",
  "workspace": {
    "base_requested": "2ea6a7ec",
    "base_mode": "descendant",
    "head_start": "7647bb2e70c416f52518618b5efbc5a705d9584f",
    "head_end": "7647bb2e70c416f52518618b5efbc5a705d9584f",
    "upstream_end": "7647bb2e70c416f52518618b5efbc5a705d9584f",
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "location": "scripts/run_night.py:1005",
        "witness": "With no wrapper and no C5 receipt, _custody_row returned quiet_predicate_evidence from plan_id, receipt_class and registration_path. With a present calibration wrapper and a mocked valid idle C5, it returned calibration.",
        "cure": "Use authenticated wrapper identity and validated C5 consistently. Keep pre-wrapper reporting row-neutral where identity cannot be established."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "location": "joulewise/evidence_night.py:244",
        "witness": "sealed_candidate on a plan containing [] raised TypeError rather than Refused.",
        "cure": "Validate the plan as a NightPlan before reading chain_path, and translate malformed input to a typed Refused."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_night_kinds.NightKindTests.test_base_archive_byte_goldens tests.test_night_kinds.NightKindTests.test_refusal_parity tests.test_night_kinds.NightKindTests.test_unhandled_third_row_routes_or_refuses_across_shared_entries tests.test_night_kinds.NightKindTests.test_third_row_notice_text_and_corecaptured_flag tests.test_night_kinds.NightKindTests.test_third_row_generator_selects_manifest_executor_and_literals tests.test_night_kinds.NightKindTests.test_generator_refuses_two_rows_for_one_chain_source tests.test_kind_dispatch_literals",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 7 tests in 64.056s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_night_kinds.NightKindTests.test_gate_refuses_evidence_row_without_wrapper_literals tests.test_night_kinds.NightKindTests.test_calibration_keeps_legacy_artifact_and_courier_inventory tests.test_night_kinds.NightKindTests.test_prepare_authors_row_paths_and_seals_candidate_at_head",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 3 tests in 17.867s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "PYTHONPATH=. python3 -B /tmp/a280_b0_execution_probe.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["missing_no_C5: quiet_predicate_evidence", "missing_valid_C5: quiet_predicate_evidence", "present_wrapper_disagrees_C5: calibration", "source_wrapper_disagree: Refused candidate chain source differs from sealed binding", "malformed_plan_sealer: TypeError list indices must be integers or slices, not str", "duplicate_chain_source: GenerationRefusal calibration/derivation or alternate chain refused", "missing_wrapper_zero_facts_clean: False"]},
      "expected": {"exit_code": 0, "tail_regex": "missing_wrapper_zero_facts_clean: False"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONPATH=. python3 -B /tmp/a280_b0_mutation_probe.py 2>&1 | tail -n 5; exit ${pipestatus[1]}",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 1 test in 9.248s", "FAILED (failures=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=1\\)"}
    },
    {
      "id": "V5",
      "kind": "lint",
      "cmd": "git diff --check 2ea6a7ec 7647bb2e",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "R1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "This read-only review ran ten focused tests, not the full 598-test brief suite or live hardware gates.",
      "needs": "Lead should run final-head suite verification."
    }
  ]
}
```

## Findings

| ID | Severity | Finding and cure |
|---|---|---|
| F1 | **BLOCKER** | [run_night.py:1005](/Users/edr/code/wt-278ebc9e-b0lens-sol/scripts/run_night.py:1005) selects idle from plan fields when both wrapper and C5 are absent; a present wrapper can also override a disagreeing valid C5 for inventory and courier routing. The executed probe reproduced both selections. Derive the row from authenticated identity, and use row-neutral reporting before identity exists. |
| F2 | **should_fix** | [evidence_night.py:244](/Users/edr/code/wt-278ebc9e-b0lens-sol/joulewise/evidence_night.py:244) indexes the newly read plan before validating its shape. The executed `[]` plan raised `TypeError`. Validate it first and return `Refused` for malformed input. |

## Accepted clauses

- Idle byte goldens and refusal parity passed unchanged.
- The test-only third row, gate handler refusal, installer and driver dispatch, and literal guard passed their focused tests.
- A disagreeing chain source and wrapper refused; duplicate rows for one chain source refused.
- `zero_capture_facts` stayed unclean with a missing wrapper.
- A process-local hard-coded idle notice mutation failed `test_third_row_notice_text_and_corecaptured_flag`. The checkout stayed clean.

## Probe commands and tails

| Probe | Command | Tail |
|---|---|---|
| Focused parity and routing | `python3 -B -m unittest tests.test_night_kinds.NightKindTests.test_base_archive_byte_goldens tests.test_night_kinds.NightKindTests.test_refusal_parity tests.test_night_kinds.NightKindTests.test_unhandled_third_row_routes_or_refuses_across_shared_entries tests.test_night_kinds.NightKindTests.test_third_row_notice_text_and_corecaptured_flag tests.test_night_kinds.NightKindTests.test_third_row_generator_selects_manifest_executor_and_literals tests.test_night_kinds.NightKindTests.test_generator_refuses_two_rows_for_one_chain_source tests.test_kind_dispatch_literals` | `Ran 7 tests in 64.056s` / `OK` |
| Gate, inventory, preparation | `python3 -B -m unittest tests.test_night_kinds.NightKindTests.test_gate_refuses_evidence_row_without_wrapper_literals tests.test_night_kinds.NightKindTests.test_calibration_keeps_legacy_artifact_and_courier_inventory tests.test_night_kinds.NightKindTests.test_prepare_authors_row_paths_and_seals_candidate_at_head` | `Ran 3 tests in 17.867s` / `OK` |
| Counterfactuals | `PYTHONPATH=. python3 -B /tmp/a280_b0_execution_probe.py` | `missing_no_C5: quiet_predicate_evidence`; `present_wrapper_disagrees_C5: calibration`; `malformed_plan_sealer: TypeError ...`; `missing_wrapper_zero_facts_clean: False` |
| Mutation | `PYTHONPATH=. python3 -B /tmp/a280_b0_mutation_probe.py 2>&1 \| tail -n 5; exit ${pipestatus[1]}` | `Ran 1 test in 9.248s` / `FAILED (failures=1)` — expected mutant kill |
| Diff | `git diff --check 2ea6a7ec 7647bb2e` | Exit 0, no output |

## Residual risk

The focused probes did not replay the full brief suite or any live measurement gate. A missing wrapper produced a typed refusal at the supervised probe boundary; its direct worker raised `FileNotFoundError` before writing a worker receipt.