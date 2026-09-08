```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented R1, R2, R3, R5, and R6; all 377 targeted tests and bash syntax validation pass.",
  "workspace": {
    "base_requested": "a2cfb644",
    "base_mode": "exact",
    "head_start": "a2cfb644c934d2ab97e356403bc2be7d571740c2",
    "head_end": "a2cfb644c934d2ab97e356403bc2be7d571740c2",
    "upstream_end": null,
    "branch": "fix/2026-09-08-window-status-liveness"
  },
  "pathspec": [
    "joulewise/measurement_liveness.py",
    "scripts/run_campaign.py",
    "scripts/run_night.py",
    "tests/test_measurement_liveness.py",
    "tests/test_run_campaign.py",
    "tests/test_run_night.py",
    "tests/test_window_status_guard.py"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_window_status_guard tests.test_measurement_liveness tests.test_run_night tests.test_run_campaign > /tmp/window-liveness-fix-verified.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 377 tests in 323.399s", "OK", "unittest_rc=0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "bash -n scripts/window_status.sh",
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
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "R4 remains the registered WINDOW-LIVENESS-DOCS-01 follow-up; no documentation was edited.",
      "needs": "Lead completes the registry documentation follow-up."
    }
  ]
}
```

## Change

- **R1:** Empty successful probes now return UNKNOWN. `/usr/bin/true` regressions verify both identity classification and publication refusal; the previous classification would fail them.
- **R2:** The complete pid/pgid/epoch marker is written, fsynced, and closed before probing. Identity is then added through a fsynced temporary file and atomic replacement. Regressions verify the simulated crash boundary, preserved dead-man pgid readability, normal replacement, and refusal without `start_time`, including a dead PID.
- **R3:** Restored the real-corpus test and its guard verbatim from `HEAD~1`; retained synthetic coverage. The restored test ran successfully.
- **R5:** Both campaign paths convert publication `RuntimeError` into exit 2 with the reason. Failing-probe tests verify lock cleanup, no registry entry, and no child dispatch; the previous uncaught exception fails this regression.
- **R6:** Registry diagnostics accumulate per successful reconciliation attempt. The retry regression detects duplicate warnings and refusals.

## Verification notes

Intermediate runs caught a patch-placement error, two outdated test expectations/calls, and an overly strict stderr assertion. All were corrected before the passing [final acceptance log](/tmp/window-liveness-fix-verified.log).

No repository-wide suite, production measurement, or commit was performed. Changes are ready for the lead’s final review.