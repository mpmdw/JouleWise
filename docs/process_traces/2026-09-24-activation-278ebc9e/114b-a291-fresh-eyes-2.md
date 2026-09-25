```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "FINDINGS: the retirement and requested checks are correct; two hand-maintained descriptions remain stale.",
  "workspace": {
    "base_requested": "7c56aa33^",
    "base_mode": "exact",
    "head_start": "37f47475d5def39fef8dff85ff90b3ce03e57064",
    "head_end": "37f47475d5def39fef8dff85ff90b3ce03e57064",
    "upstream_end": "37f47475d5def39fef8dff85ff90b3ce03e57064",
    "branch": "fix/2026-09-24-a291-merge-candidate"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "path": ".github/workflows/gate-ledger.yml",
        "line": 3,
        "text": "Workflow comments still call gate-ledger advisory and point to the retired E1 task as the future promotion gate, contradicting the stated completed branch-protection action."
      },
      {
        "id": "F2",
        "severity": "nit",
        "path": "TASK_QUEUE.md",
        "line": 670,
        "text": "The hand-maintained Kernel count still says 245; the kernel and pinned test set now contain 244 live tasks."
      }
    ],
    "retirement_precedent": "0f02008d removed completed A294/A295 tasks from the kernel and generated queue and updated the test pin.",
    "live_dangling_references": "none found"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --numstat 7c56aa33^ 37f47475",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "0\t2\tTASK_QUEUE.md",
          "0\t50\tdocs/process/state_kernel.json",
          "1\t2\ttests/test_gen_state.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "1\\t2\\ttests/test_gen_state.py"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "python3 scripts/gen_state.py --check",
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
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_gen_state",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 44 tests in 1.987s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 44 tests.*\\n\\nOK"
      }
    }
  ],
  "flags": []
}
```

## Findings

- **F1 — should fix:** [gate-ledger.yml](/Users/edr/code/wt-278ebc9e-a291mc/.github/workflows/gate-ledger.yml:3) still describes the check as advisory; its later comment names the retired E1 task as the future promotion gate. These are comments, so they do not break CI, but they now misstate the gate’s status.
- **F2 — nit:** [TASK_QUEUE.md](/Users/edr/code/wt-278ebc9e-a291mc/TASK_QUEUE.md:670) still labels the kernel count as 245. The current count is 244.

The kernel diff deletes exactly one 50-line task block with all other bytes unchanged. The queue diff deletes only its two generated E8 rows. The pinned ID set loses exactly that ID and matches all 244 kernel IDs. Commit `0f02008d` provides a prior completed-task retirement. Remaining ID references are historical prose, workflow comments, and an archived replay script; no live kernel dependency or test dereference remains.

## Residual risk

Per the requested CPU limit, this review ran only `tests.test_gen_state`, not the full suite.