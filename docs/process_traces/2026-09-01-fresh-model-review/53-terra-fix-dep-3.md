```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented the sheet-as-fixture rule, repaired the documented replay command and anchors, and passed focused plus canonical tests.",
  "workspace": {
    "base_requested": "35716229f181268407c3e42826540ef080ec17e0",
    "base_mode": "exact",
    "head_start": "35716229f181268407c3e42826540ef080ec17e0",
    "head_end": "35716229f181268407c3e42826540ef080ec17e0",
    "upstream_end": "35716229f181268407c3e42826540ef080ec17e0",
    "branch": "feat/2026-09-01-dependence"
  },
  "pathspec": [
    "docs/paper/round7/dependence-sensitivity.md",
    "scripts/dependence_sensitivity.py",
    "tests/test_dependence_sensitivity.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_dependence_sensitivity tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 22 tests in 4.653s",
          "OK",
          "MUTATION_TABLE zero survivors: sheet-number=0, command=0, draft-anchor=0, refusal-delete-add=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "sed -n '99p' docs/paper/round7/dependence-sensitivity.md | bash",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "  \"comparison\": {",
          "    \"direction_gate_outcomes_agree\": false",
          "  }",
          "}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\"direction_gate_outcomes_agree\": false"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": ".*"
      }
    },
    {
      "id": "V4",
      "kind": "lint",
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
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git status --short",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " M docs/paper/round7/dependence-sensitivity.md",
          " M scripts/dependence_sensitivity.py",
          " M tests/test_dependence_sensitivity.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "dependence-sensitivity.md.*dependence_sensitivity.py.*test_dependence_sensitivity.py"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The two cited 2026-09-01 ruling files are absent at the exact requested HEAD; the explicit prompt amendments supplied the applied authority.",
      "needs": "Lead may restore or custody those trace files if their absence is unexpected."
    }
  ]
}
```

## Change

- Rule 1 → `test_every_documented_command_executes_verbatim_with_its_claimed_outcome`: regex-extracts every fenced/indented command, runs the extracted text from the repository root, and checks its claimed JSON outcome. Command mutation: zero survivors.

- Rule 2 → `test_every_worked_example_number_is_rendered_from_output_or_input_constant` and `test_every_sheet_numeric_token_is_source_bound_by_the_fixture_rule`: parses the worked prose/table rows, binds rendered values and inputs, and fingerprints the full numeric-token inventory. Numeric mutation: zero survivors.

- Rule 3 → `test_every_draft_line_anchor_resolves_in_the_frozen_draft`: resolves all four anchors against frozen `draft-v1.md`; DS/PG-SENS-02 now use line 294.

- Rule 4 → `test_refusal_row_set_is_exact_and_every_row_binds_to_a_source_site`: asserts the exact refusal-row set, no duplicates, and named script-site bindings. Delete/add mutations: zero survivors.

- Rule 5 → `test_every_bracketed_ten_number_list_equals_the_example_constant`: both sheet lists equal `EXAMPLE_BLOCK_DELTAS_J`.

Content cures landed at sheet lines 11, 35–37, 81–85, 99, and 109–116. The script now emits the beta-tail replay formula and `x` for each model.

## Verification notes

The exact line-99 replay emitted `"direction_gate_outcomes_agree": false`. The canonical test suite also exited 0.