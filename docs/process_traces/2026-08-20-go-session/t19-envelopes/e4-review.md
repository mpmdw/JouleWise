```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "UPHELD-WITH-FOLLOWUP: ENOENT is a valid Python 3.11 stale-descendant cleanup race, while other cleanup errnos remain rejected.",
  "workspace": {
    "base_requested": "aedf530",
    "base_mode": "informational",
    "head_start": "c423f59264c8a6e80dac5c0af7fe3c1173c34a70",
    "head_end": "c423f59264c8a6e80dac5c0af7fe3c1173c34a70",
    "upstream_end": "c423f59264c8a6e80dac5c0af7fe3c1173c34a70",
    "branch": "main"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "label": "UPHELD-WITH-FOLLOWUP",
    "findings": [
      {
        "id": "R1",
        "severity": "should_fix",
        "summary": "Add a deterministic follow-up harness for the two cleanup interleavings.",
        "text": "Do not disable maintenance in this claim-bearing test: removing the controls and observing detached maintenance are part of its claim. A future deterministic injected-writer/remover harness could reduce dependence on Git scheduling, but this is nonblocking."
      }
    ],
    "errno_allowlist": {
      "accepted": [
        "ENOTEMPTY",
        "ENOENT"
      ],
      "third_value": "refuse"
    },
    "conclusion": "The widening is sound and does not open a wrong-cleanup acceptance path."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3.11 -m unittest -v tests.test_calibration_exits.CalibrationExitReliabilityTests.test_forced_auto_maintenance_mutation_reproduces_cleanup_race",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "RACE_EXERCISED=0 NO_RACE_PRE_WRITE=1 TRACE_INCOMPLETE=0",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3.13 -m unittest -v tests.test_calibration_exits.CalibrationExitReliabilityTests.test_forced_auto_maintenance_mutation_reproduces_cleanup_race",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "RACE_EXERCISED=1 NO_RACE_PRE_WRITE=0 TRACE_INCOMPLETE=0",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test[\\s\\S]*OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest -v tests.test_calibration_exits.CalibrationExitReliabilityTests.test_delayed_object_writers_never_escape_bounded_cleanup",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "P1_DELAYED_WRITERS=1 EVENT_GATED_FINAL_WRITES=1 BOUNDED_RETRIES=0 THREAD_REGISTRY_EMPTY=1 ESCAPED=0",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test[\\s\\S]*OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The full suite and Python 3.14 were not run locally; Python 3.13 confirmed the newer rmtree behavior, and the exact hosted Git environment was unavailable.",
      "needs": ""
    }
  ]
}
```

## Findings

1. R1 — should_fix: The widened assertion accepts only the two race-shaped outcomes. `ENOTEMPTY` means a child remained or was created before directory removal; `ENOENT` means Git removed an enumerated descendant before Python 3.11 accessed it. Other `OSError` values still fail the `assertIn`. A Python 3.11 probe reproduced errno 2 for the stale-child case; Python 3.13 completed successfully.

2. The quiescence guard exists in [`tests/test_calibration_exits.py`](/Users/edr/code/JouleWise/tests/test_calibration_exits.py:1445), and the focused test passed. Its negative control also fired on the exact original ordering: “rmtree began before the writer observed its stop request.”

3. Disabling `gc.auto`/`maintenance.auto` as in `037d9dd` is not applicable here: this test deliberately removes those controls and asserts detached maintenance starts at [`tests/test_calibration_exits.py`](/Users/edr/code/JouleWise/tests/test_calibration_exits.py:1745). The `b01d9a2` parseable-PID polling fix is consistent with the same broader timing-race family.

## Residual risk

The real Git mutation test passed locally without producing ENOENT; the causal mechanism was independently reproduced at the Python `rmtree` level. No repository files were modified.