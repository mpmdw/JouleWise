```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Corrected the F4 seam so occupied live roots pass and occupied stale roots refuse, with an executed regression and red-then-green evidence.",
  "workspace": {
    "base_requested": "eb04273f",
    "base_mode": "exact",
    "head_start": "eb04273fdff58cd09c40cc5110dd892673000f60",
    "head_end": "eb04273fdff58cd09c40cc5110dd892673000f60",
    "upstream_end": "eb04273fdff58cd09c40cc5110dd892673000f60",
    "branch": "feat/2026-09-04-fan-PREWINDOW-V5-PIN-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/PREWINDOW-V5-PIN-01/05-sol-wave2-seam-fix.md",
    "scripts/prewindow_check.sh",
    "tests/test_capture_t0_step.py"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-04-fanout/PREWINDOW-V5-PIN-01/04-delta-reaudit-round-1.md"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "audit_tmp=$(mktemp -d /private/tmp/jw-prewindow-wave2.XXXXXX); mkdir -p \"$audit_tmp/tests\" \"$audit_tmp/scripts\" \"$audit_tmp/configs/arm_readiness\"; cp tests/test_capture_t0_step.py \"$audit_tmp/tests/test_capture_t0_step.py\"; cp scripts/prewindow_check.sh \"$audit_tmp/scripts/prewindow_check.sh\"; cp configs/arm_readiness/d117_row_registry_v2.json \"$audit_tmp/configs/arm_readiness/d117_row_registry_v2.json\"; sed -i.bak 's/\"$STALE_WINDOW_RUNS_PREFIX\"/\"$WINDOW_RUNS_PREFIX\"/' \"$audit_tmp/scripts/prewindow_check.sh\"; PYTHONPATH=. python3 \"$audit_tmp/tests/test_capture_t0_step.py\" CaptureT0StepTests.test_prewindow_runs_prefixes_accept_live_family_and_refuse_stale_family",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": [
          "Ran 1 test in 1.213s",
          "",
          "FAILED (failures=6)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "Ran 1 test in [0-9.]+s\\n\\nFAILED \\(failures=6\\)"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_capture_t0_step.CaptureT0StepTests.test_prewindow_runs_prefixes_accept_live_family_and_refuse_stale_family",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 0.874s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_capture_t0_step",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 31 tests in 35.022s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 31 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V4",
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

Both sides of F4 were wrong against the authority at `docs/process/state_kernel.json:3986` and `TASK_QUEUE.md:711,856`: the shell scanned the live prefix, so occupied live roots refused and stale roots passed; the fix-round regression asserted that same inverse behavior.

The live `_v5` selector remains explicit, while each window now also names its retired `_v2` refusal prefix. The executed scan checks the stale prefix, making occupied live roots admissible and occupied stale roots fail closed. The CLI regression asserts both directions for alpha, beta, and gamma while retaining the unreachable-selector decoy.

Red, after correcting the assertions but before changing the shell:

```text
$ python3 -m unittest tests.test_capture_t0_step.CaptureT0StepTests.test_prewindow_runs_prefixes_accept_live_family_and_refuse_stale_family
Ran 1 test in 1.164s

FAILED (failures=6)
```

Green, after the shell cure:

```text
$ python3 -m unittest tests.test_capture_t0_step.CaptureT0StepTests.test_prewindow_runs_prefixes_accept_live_family_and_refuse_stale_family
Ran 1 test in 0.874s

OK
```

## Verification notes

Per the preflight rule, no test module other than `tests.test_capture_t0_step` was run. V1 replays the pre-fix reverse scan in a temporary copy and kills it with the same six directional failures.
