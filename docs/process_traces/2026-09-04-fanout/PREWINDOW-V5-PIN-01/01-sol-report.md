```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Retargeted all pre-window selectors to the registered Qwen3 _v5 family and added an exact live-versus-retired regression.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-fan-PREWINDOW-V5-PIN-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/PREWINDOW-V5-PIN-01/01-sol-report.md",
    "scripts/prewindow_check.sh",
    "tests/test_capture_t0_step.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_capture_t0_step tests.test_prewindow_check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 32 tests in 42.414s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 32 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "bash -n scripts/prewindow_check.sh && git diff --check",
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
  "flags": []
}
```

## Change

The pre-window readiness check now selects the three pack identifiers installed as the live family in `configs/arm_readiness/d117_row_registry_v2.json`: Qwen3 1.7B for alpha, Qwen3 8B for beta, and their contrast for gamma. Only the three runs-root literals and their explanatory comment changed; the readiness checks, refusal behavior, command-line interface, and admission lanes are unchanged.

The regression reads the independent governed registry, derives the required `runs_<pack_id>` values, and compares all three script selectors exactly. It also names and rejects all three retired Qwen2.5 `_v2` selectors. Reverting the production retarget while retaining the test therefore fails the exact-map assertion; the former test did not, because `_v2` still satisfies the broad successor-name regular expression.

| Finding | Decision | Result |
|---|---|---|
| The alpha, beta, and gamma selectors named retired Qwen2.5 `_v2` roots. | Apply ruling R-12 as a literal-only retarget to the registered Qwen3 `_v5` identifiers. | Implemented. |
| The existing regression accepted any syntactically valid successor, including the stale family. | Bind the test to the registry's exact `successor_pack_ids` map and enumerate the retired values as negative cases. | Implemented; counterfactual-shaped. |
| The kernel row has no dependency, hardware step, or unresolved design choice. | Do not widen the task into a new validation or admission mechanism. | Complete at the desk. |

Magistrate-owned follow-up: change `PREWINDOW-V5-PIN-01` from `queued` to its completed state in `docs/process/state_kernel.json`, then regenerate the owned projections in `TASK_QUEUE.md` and `RUN_STATE.md`. Those files were intentionally not edited under the preflight rule. No decision-log or paper change is needed.

## Verification notes

The repository-wide test suite was not run, as required by the preflight rule. Verification was limited to the two directly relevant test modules, shell syntax, and diff whitespace/error checks.
