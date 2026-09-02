```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Audit complete: W2a survives; the other eight requested mutations are killed.",
  "workspace": {
    "base_requested": "cf27e8ce~1",
    "base_mode": "exact",
    "head_start": "cf27e8cee87266538ec694b30e274d63d69a82ce",
    "head_end": "cf27e8cee87266538ec694b30e274d63d69a82ce",
    "upstream_end": null,
    "branch": "feat/2026-09-01-dependence-r6"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "title": "W2a remains structurally untested",
        "evidence": "Changing the rendered example-agreement slot to the byte-identical literal \"agree\" leaves all 26 focused tests green."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_dependence_sensitivity",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 26 tests in 3.172s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 26 tests.*OK"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "python3 scripts/dependence_sensitivity.py --check-sheet",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 scripts/dependence_sensitivity.py --render-sheet | cmp -s - docs/paper/round7/dependence-sensitivity.md",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V4",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Shared-worktree Git metadata denied index-lock creation for git checkout; inverse scoped patches reverted every probe, and final status is empty.",
      "needs": ""
    }
  ]
}
```

## Mutation table

| Survivor | Mutation result |
|---|---|
| W1 | FAIL `test_correlation_limit_slot_is_bound_to_the_estimator_guard` |
| W2a | **SURVIVED** — hard-code example word to `"agree"`; 26 tests OK |
| W4 | FAIL `test_tail_replay_formula_values_and_source_locations_are_current` |
| W5 | FAIL `test_template_digit_and_code_citation_lint_has_a_closed_shape_allowlist` |
| W7 | FAIL `test_every_pre_example_slot_matches_a_closed_context_rule` |
| W8 | FAIL `test_every_pre_example_slot_matches_a_closed_context_rule` |
| W10 | ERROR `test_rendered_sheet_is_byte_equal_to_the_tracked_document` (`SheetRenderError`) |
| W11b | FAIL `test_every_pre_example_slot_matches_a_closed_context_rule` |
| W9 | ERROR `test_rendered_sheet_is_byte_equal_to_the_tracked_document` (`SheetRenderError`) |

## Findings

- **blocker F1:** W2a is not killed. The new test reads the tracked document via `self._document()` and compares its word to the command payload; it does not prove `sheet_slots()` derives that word. A literal `"agree"` renders byte-identically for today’s example and passes the entire focused suite. Add a counterfactual payload/mock assertion against freshly rendered output or `sheet_slots()`.

Quality checks otherwise pass: the W7/W8/W11b rule table is closed and table-driven; generator registration is AST-read; alpha renders exactly `95%`; digit lint rejects `+3\sum`; no `95%` or `95/95` remains in the template. No new professor-facing prose was introduced.

## Verify tails

- Focused suite: `Ran 26 tests in 3.172s` / `OK`
- Targeted lint/context/registration tests: `Ran 3 tests in 0.361s` / `OK`
- `--check-sheet`, render byte comparison, and `git diff --check`: rc 0
- Final `git status --short`: empty.