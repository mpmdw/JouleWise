```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Added direct regressions that reject the refuter's status-list and five-row evidence-matrix counterfactual.",
  "workspace": {
    "base_requested": "85b8cd7e5f1895897abdb110ce038f0ae6fd419e",
    "base_mode": "exact",
    "head_start": "85b8cd7e5f1895897abdb110ce038f0ae6fd419e",
    "head_end": "85b8cd7e5f1895897abdb110ce038f0ae6fd419e",
    "upstream_end": "85b8cd7e5f1895897abdb110ce038f0ae6fd419e",
    "branch": "feat/2026-09-04-fan-p1-rows"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/p1-rows/03-sol-fix-round-1-report.md",
    "tests/test_phase1_row_dispositions.py"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-04-fanout/p1-rows/02-refuter-merge-base.md"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_phase1_row_dispositions >/private/tmp/jw-p1-fix-round1-positive.log 2>&1; rc=$?; tail -n 2 /private/tmp/jw-p1-fix-round1-positive.log; echo \"positive_rc=$rc\"; exit $rc",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "OK",
          "positive_rc=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "positive_rc=0$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "cd /private/tmp/jw-p1-fix-round1-counterfactual.ffqW2a; cp /Users/edr/code/JouleWise-wt-fan-p1-rows/tests/test_phase1_row_dispositions.py tests/test_phase1_row_dispositions.py; python3 -m unittest tests.test_phase1_row_dispositions >/private/tmp/jw-p1-fix-round1-counterfactual.log 2>&1; rc=$?; tail -n 2 /private/tmp/jw-p1-fix-round1-counterfactual.log; echo \"counterfactual_rc=$rc\"; test \"$rc\" -eq 1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "FAILED (failures=6)",
          "counterfactual_rc=1"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "counterfactual_rc=1$"
      }
    },
    {
      "id": "V3",
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
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "python3 -c 'import json,pathlib; p=pathlib.Path(\"docs/process_traces/2026-09-04-fanout/p1-rows/03-sol-fix-round-1-report.md\"); lines=p.read_text(encoding=\"utf-8\").splitlines(); fence=chr(96)*3; assert lines[0] == fence+\"json\"; end=lines.index(fence,1); b=(\"\\n\".join(lines[1:end])+\"\\n\").encode(\"utf-8\"); assert len(b) <= 8192; json.loads(b); print(\"report-envelope-ok\")'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "report-envelope-ok"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^report-envelope-ok$"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "test -z \"$(git diff --name-only -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json docs/decision_log.md)\"; echo 'magistrate-owned delta: empty'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "magistrate-owned delta: empty"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^magistrate-owned delta: empty$"
      }
    }
  ],
  "flags": []
}
```

## Change

| Finding | Cure | File:line |
|---|---|---|
| P1R2-1 | Parse the first paragraph after `Still required:` and assert that its complete contents are solely the calendar-mapping bullet. Re-adding the refuter's four named bullets now fails this regression. | `tests/test_phase1_row_dispositions.py:25`, `tests/test_phase1_row_dispositions.py:50` |
| P1R2-1 | Parse the Evidence Matrix and directly assert the reconciled Supervisor, wall-meter, network, NVIDIA, and Orin statuses. Restoring the refuter's five old pending/partially-checked dispositions now fails five subtests. | `tests/test_phase1_row_dispositions.py:34`, `tests/test_phase1_row_dispositions.py:55` |

The refuter verdict contained no `should_fix` items beyond blocker P1R2-1.
The cure is test-only: it requires no checklist change and no magistrate-owned
state row.
