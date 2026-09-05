```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "The pre-window gate already carried the ruled agent-process pattern; its regression now isolates every ruled alternative and fails under the former pattern.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-fan-PREWINDOW-REGEX-01"
  },
  "pathspec": [
    "tests/test_prewindow_check.py",
    "docs/process_traces/2026-09-04-fanout/PREWINDOW-REGEX-01/01-sol-report.md"
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
      "cmd": "python3 -m unittest tests.test_prewindow_check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 0.699s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK$"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "/bin/bash -n scripts/prewindow_check.sh",
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
      "cmd": "python3 -m unittest tests.test_prewindow_check",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (failures=1)"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=1\\)$"
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
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The kernel still marks PREWINDOW-REGEX-01 queued although commit bea06481 and the issued 2026-08-20 session report record the implementation and its merge before the pending ED-Q-L9-3 capture.",
      "needs": "The magistrate should mark PREWINDOW-REGEX-01 complete in docs/process/state_kernel.json and regenerate TASK_QUEUE.md and RUN_STATE.md; those files were explicitly reserved from this session."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "Ruling S-7 records that the next council touch should solicit the owning environmental-census seat's assent to the tightening; the same ruling says the conservative-default rule is not violated because this change only tightens admission.",
      "needs": "Record the owning seat's assent at the next council touch; no implementation work is blocked."
    }
  ]
}
```

## Change

The pre-window dwell-admission check—the operator script that must approve a quiet interval before a measurement window begins—already used the cold-ratified `codex|claude|t3|mcp-server` alternation on the starting head. Commit `bea06481` introduced that shell change and the first regression; the issued session report records its merge before the still-pending ED-Q-L9-3 agent-free capture.

This run strengthened the regression. The synthetic process table now contains separate Claude, Codex, `t3`, and Model Context Protocol server rows. Previously the Codex row also contained `mcp-server`, and no row contained `t3`; deleting either of those pattern alternatives could therefore leave the test green. The expected refusal count now binds all four alternatives independently.

| Finding | Decision | Evidence |
|---|---|---|
| The governed shell pattern is already installed. | Preserve it without a needless rewrite. | `scripts/prewindow_check.sh`; implementation commit `bea06481`; issued report `docs/run_reports/2026-08-20-t18-t19-session.md`. |
| The regression did not isolate every ruled alternative. | Give each alternative its own live-process-shaped row and bind the total refusal count. | Focused test V1 passes; counterfactual V3 fails after temporarily restoring the former narrow pattern. |
| The registry projects installed work as queued. | Leave the magistrate-owned registry files untouched and report the required state transition. | Kernel row PREWINDOW-REGEX-01 is `queued`; its acceptance evidence is already present in code, test, merge history, and the issued report. |

No new design choice was required. Sitting ruling C-6(iii), amended by ruling S-7, already fixes the forcing problem, the four process-name alternatives, and the ordering before the external capture.

## Verification notes

V3 is an expected-failure mutation check. I temporarily replaced the governed alternation with the former `codex exec|codex-run|run_campaign|window-chain` pattern, ran the focused module, observed the false `READY` result and test failure, and immediately restored the governed pattern. V1 was then repeated on the restored source. Per the preflight rule, the repository-wide test suite was not run.

## Residual risk

NEEDS_RULING (nonblocking): the magistrate must install the already-evidenced completion in the state kernel and its generated projections. At the next council touch, the magistrate should also obtain the owning environmental-census seat's assent required by ruling S-7. Neither item changes the implemented fail-closed behavior.
