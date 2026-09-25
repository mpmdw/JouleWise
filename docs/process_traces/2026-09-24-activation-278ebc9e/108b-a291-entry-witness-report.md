```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Added three resealed public-entry witness tests and pinned the refusal codes production raises; all requested checks passed.",
  "workspace": {
    "base_requested": "6e2504b166a6c9b5be85b4b916adfd2d4dae814a",
    "base_mode": "exact",
    "head_start": "6e2504b166a6c9b5be85b4b916adfd2d4dae814a",
    "head_end": "6e2504b166a6c9b5be85b4b916adfd2d4dae814a",
    "upstream_end": "6e2504b166a6c9b5be85b4b916adfd2d4dae814a",
    "branch": "fix/2026-09-24-a291-r3-packer"
  },
  "pathspec": ["tests/test_scored_ownership_forgery.py"],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_scored_ownership_forgery.OwnershipForgeryTests.test_entry_path_witness_inv_23 tests.test_scored_ownership_forgery.OwnershipForgeryTests.test_entry_path_witness_inv_36 tests.test_scored_ownership_forgery.OwnershipForgeryTests.test_entry_path_witness_inv_37",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["...", "----------------------------------------------------------------------", "Ran 3 tests in 2.171s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 3 tests in .*\\n\\nOK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_scored_ownership_forgery",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [".", "----------------------------------------------------------------------", "Ran 10 tests in 584.956s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 10 tests in .*\\n\\nOK"}
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The public entry refuses all three witnesses, but its codes differ from the rows' listed codes.",
      "needs": "Lead review if row-specific refusal codes are required."
    }
  ]
}
```

## Change

Added one test per row in [test_scored_ownership_forgery.py](/Users/edr/code/wt-278ebc9e-a291p3/tests/test_scored_ownership_forgery.py). Each starts from a legal roster, applies the checker witness edit, confirms the checker row, reseals, and asserts the exact `PackingRefusal` code from `requeue_overrun(...)`.

| Row | Witness | Asserted code | Listed code |
|---|---|---|---|
| INV-23 | Changed a split single’s `predicted_s` | `inv_38` | `inv_23` |
| INV-36 | Set an advanced placement’s attempt to 2 | `inv_38` | `inv_36` |
| INV-37 | Added a terminal refusal for a live item | `inv_11` | `inv_37` |

The change is uncommitted and confined to the authorized test file.