```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "WI-16 implemented with atomic archive publication, blind count checks, and synthetic verification; lead verification remains pending.",
  "workspace": {
    "base_requested": "main",
    "base_mode": "exact",
    "head_start": "fac86c0d43a17d3d21c311d8e861ba39cbba14ad",
    "head_end": "fac86c0d43a17d3d21c311d8e861ba39cbba14ad",
    "upstream_end": "fac86c0d43a17d3d21c311d8e861ba39cbba14ad",
    "branch": "feat/2026-09-30-wi16-harvest-automation"
  },
  "pathspec": [
    "scripts/harvest_window.py",
    "tests/test_harvest_window.py",
    "docs/phase_2/derivation_night_runbook.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_harvest_window tests.test_calibration_cadence_report tests.test_battery_float_consumers tests.test_battery_float_sweep",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 47 tests in 26.528s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 47 tests in .*s[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_harvest_window tests.test_calibration_cadence_report tests.test_battery_float_consumers tests.test_battery_float_sweep tests.test_issue_calibration_acceptance_generation",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 200 tests in 200.437s", "FAILED (failures=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 200 tests in .*s[\\s\\S]*OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_issue_calibration_acceptance_generation.DeskEpochWatchTests.test_live_probes_report_this_machine_against_the_active_epoch",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: None is not an instance of <class 'str'>",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
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
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "python3 -B scripts/harvest_window.py --help >/dev/null",
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
      "kind": "environment",
      "level": "nonblocking",
      "text": "The untouched live identity test requires an os_build string, but the sandbox returned None. The failure reproduced in isolation.",
      "needs": "Rerun the identity test in the lead environment."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Targeted checks were used for this tooling change. The canonical discovery suite and live harvest were not executed.",
      "needs": "Review the final diff and run the once-per-code-change canonical suite."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Archive publication is atomic, but launchd uninstall is external. An interruption after uninstall and before publication requires retry; source evidence remains retained.",
      "needs": ""
    }
  ]
}
```

## Change

Added authenticated, idempotent custody copying, per-capture verdicts, independent count arithmetic, battery-field cross-checks, and the existing uninstall call. The command publishes one JSON record with the archive and accesses no B field. Changes remain uncommitted.

## Verification notes

The final targeted run passed 47 tests. The broader run had one sandbox identity failure, reproduced independently. No real launchctl, sudo, powermetrics action, or live harvest was executed.

## Residual risk

A committed terminal ledger pin is required. The embedded battery record does not replace the official committed verdict. Current W1/W2 plan pointers contain no derivation count rule, so they produce `COUNTS_ONLY`.