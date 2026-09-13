```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented recursive fail-closed metadata classification, repaired the shared closure fixture, and passed all focused and canonical verification.",
  "workspace": {
    "base_requested": "a6ce7af",
    "base_mode": "exact",
    "head_start": "a6ce7af7c6c4e1119d6c4365fb63ce4482f9e246",
    "head_end": "a6ce7af7c6c4e1119d6c4365fb63ce4482f9e246",
    "upstream_end": "a6ce7af7c6c4e1119d6c4365fb63ce4482f9e246",
    "branch": "impl/d100-bii-binding"
  },
  "pathspec": [
    "joulewise/salvage_dangler.py",
    "tests/test_salvage_dangler.py",
    "tests/test_run_campaign.py"
  ],
  "unowned_dirty": [
    "BRIEF.md"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_salvage_dangler -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 25 tests in 0.106s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 25 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest -v tests.test_analysis_integration.AnalysisIntegrationTests.test_b4_salvage_floor_binder_accepts_correct_pair_after_real_row_validation tests.test_run_campaign.D100MembershipRepairTests.test_r8_salvage_runner_appends_new_pinned_row_without_editing_failure tests.test_whole_window_selection.SalvageSemanticsDispatchTests.test_no_argument_consumers_exclude_salvage_rows tests.test_whole_window_selection.SalvageSemanticsDispatchTests.test_explicit_salvage_dispatch_selects_only_salvage tests.test_whole_window_selection.SalvageSemanticsDispatchTests.test_multiple_salvage_rows_for_one_basis_conflict_even_if_identical tests.test_whole_window_selection.SalvageSemanticsDispatchTests.test_b5_real_row_rejects_same_policy_binding_substitution",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 6 tests in 0.559s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 6 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 2404 tests in 797.862s",
          "",
          "OK (skipped=25)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 24[0-9]+ tests in .*s\\n\\nOK \\(skipped=25\\)"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "d100_snapshot=\"$(mktemp -d /private/tmp/d100-bii-a6ce7af.XXXXXX)\"\ngit archive a6ce7af | tar -x -C \"$d100_snapshot\"\ncp tests/test_salvage_dangler.py \"$d100_snapshot/tests/test_salvage_dangler.py\"\ncd \"$d100_snapshot\"\n/Users/edr/code/JouleWise/.venv/bin/python -m unittest -v tests.test_salvage_dangler.SalvageDanglerTests.test_recursive_metadata_rejects_workload_scalar_in_allowlisted_mapping tests.test_salvage_dangler.SalvageDanglerTests.test_recursive_metadata_rejects_workload_evidence_through_list",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 2 tests in 0.006s",
          "",
          "FAILED (failures=2)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=2\\)"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "d100_parent_snapshot=\"$(mktemp -d /private/tmp/d100-bii-bc2ab19.XXXXXX)\"\ngit archive bc2ab19 | tar -x -C \"$d100_parent_snapshot\"\ncp tests/test_salvage_dangler.py \"$d100_parent_snapshot/tests/test_salvage_dangler.py\"\ncd \"$d100_parent_snapshot\"\n/Users/edr/code/JouleWise/.venv/bin/python -m unittest -v tests.test_salvage_dangler.SalvageDanglerTests.test_d106_early_telemetry_substitution_refuses tests.test_salvage_dangler.SalvageDanglerTests.test_d106_nested_metadata_workload_evidence_refuses tests.test_salvage_dangler.SalvageDanglerTests.test_d106_quarantine_digest_freeze_rejects_sibling_copy",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 3 tests in 0.022s",
          "",
          "FAILED (failures=3)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=3\\)"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "python3 - <<'PY'\nimport ast\nimport subprocess\nfrom pathlib import Path\nnames = {\"test_d106_early_telemetry_substitution_refuses\", \"test_d106_nested_metadata_workload_evidence_refuses\", \"test_d106_quarantine_digest_freeze_rejects_sibling_copy\"}\nbaseline = subprocess.run([\"git\", \"show\", \"a6ce7af:tests/test_salvage_dangler.py\"], check=True, capture_output=True, text=True).stdout\ncurrent = Path(\"tests/test_salvage_dangler.py\").read_text(encoding=\"utf-8\")\ndef methods(source):\n    tree = ast.parse(source)\n    return {node.name: ast.get_source_segment(source, node) for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names}\nbefore = methods(baseline)\nafter = methods(current)\nfor name in sorted(names):\n    print(f\"{name}: {'IDENTICAL' if before[name] == after[name] else 'CHANGED'}\")\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "test_d106_early_telemetry_substitution_refuses: IDENTICAL",
          "test_d106_nested_metadata_workload_evidence_refuses: IDENTICAL",
          "test_d106_quarantine_digest_freeze_rejects_sibling_copy: IDENTICAL"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "test_d106_quarantine_digest_freeze_rejects_sibling_copy: IDENTICAL"
      }
    },
    {
      "id": "V7",
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
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "The R1 ruling authorized updating the shared production-shaped closure fixture in tests/test_run_campaign.py.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "D-106's documented concurrent-capture limitation remains unchanged; interval containment cannot identify simultaneous captures.",
      "needs": "Retain this as the recorded limitation."
    }
  ]
}
```

## Change

FIX-1 complete: metadata and event metadata now receive recursive mapping/list/scalar traversal. `model_output` is classified as workload evidence at any depth, closing both the allowlisted-mapping scalar bypass and list-container bypass.

The admissible `extra` shape is now a nonempty subset of these exact producer-owned scalar fields:

- `preceding_member_end_s`: finite number or null, supplied by the experiment runner.
- `idle_start_s`: finite number stamped by the controller.
- `preceding_gap_s`: finite signed number or null, derived by the controller.
- `clock_step_suspect`: literal `true`, emitted by the controller for a negative derived gap.
- `cooldown_cap_hit`: literal `true`, emitted by the experiment runner from the prior cooldown result.
- `environment_admission_failed`: literal `true`, emitted by the experiment runner’s fail-closed cooldown action.

FIX-2 complete: the shared fixture now records `quarantine_root` and a canonical manifest containing each quarantined file’s relative path, SHA-256, and size. Manifest-less pre-workload closures remain refusing and have explicit coverage.

FIX-3 complete: two new discriminating regressions exercise the allowlisted-mapping scalar and list-container bypasses. The three existing `test_d106_*` methods were not changed.

The interval-containment implementation, digest-freeze implementation, in-code marker, and protected D-106 regressions were untouched.

## Verification notes

The historical nonzero exits are expected successes: both FIX-1 regressions licensed at `a6ce7af`, while all three protected D-106 regressions licensed at parent `bc2ab19`. The pre-fix six-test command reproduced `FAILED (errors=6)` before the fixture repair and passed afterward.

No scope deviation occurred. Pre-existing untracked `BRIEF.md` was preserved. No commit was created.

## Residual risk

The lead should double-check that the six-field `extra` allowlist matches the focused audit’s compatibility record, then review and commit the three scoped files. The known concurrent-capture limitation remains exactly as D-106 records it.