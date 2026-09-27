```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented bundle authentication using controller monotonic event bounds; the required suites pass except for the previously observed sandbox live-probe failure.",
  "workspace": {
    "base_requested": "8b4e1bd4c7e3b0b2c896122194f57747fbb840c9",
    "base_mode": "exact",
    "head_start": "8b4e1bd4c7e3b0b2c896122194f57747fbb840c9",
    "head_end": "8b4e1bd4c7e3b0b2c896122194f57747fbb840c9",
    "upstream_end": "8b4e1bd4c7e3b0b2c896122194f57747fbb840c9",
    "branch": "feat/2026-09-26-bfgs-s0-helper-fence"
  },
  "pathspec": [
    "joulewise/battery_float.py",
    "tests/test_battery_float.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_battery_float tests.test_battery_float_consumers tests.test_battery_float_sweep",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["...............................................................................................", "----------------------------------------------------------------------", "Ran 95 tests in 77.804s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_evidence_night tests.test_night_kinds",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["..................................................................................................................................................................................", "----------------------------------------------------------------------", "Ran 178 tests in 333.816s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_epoch_continuation",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["....................................................................", "----------------------------------------------------------------------", "Ran 68 tests in 61.674s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_issue_calibration_acceptance_generation",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["", "----------------------------------------------------------------------", "Ran 156 tests in 281.441s", "", "FAILED (failures=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_run_night",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [".......................................................................................................................sss....................................................ssssss", "----------------------------------------------------------------------", "Ran 237 tests in 171.317s", "", "OK (skipped=9)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK \\(skipped=9\\)$"}
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_validate_powermetrics_fiducial_derivation_only",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["....", "----------------------------------------------------------------------", "Ran 27 tests in 384.297s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "V4 has the same sole live-machine failure as round 1: test_live_probes_report_this_machine_against_the_active_epoch received os_build=None.",
      "needs": "Lead reruns the live sysctl probe at the bench."
    }
  ]
}
```

## Change

[authenticate_bundle](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/joulewise/battery_float.py:888) reads the first `idle_baseline` start and last `idle_drift_sentinel` completion from `events.jsonl`, validates their `metadata.monotonic_ns` bounds, and calls `authenticate_pair` once. An unavailable span produces `battery_float_evidence_missing` at the span rung. [Fixture tests](/Users/edr/code/JouleWise-wt-bfgs-s0-6bec2aa6/tests/test_battery_float.py:166) cover boundaries, missing and invalid fields, repeated events, and earlier-rung precedence.

## Verification notes

**RED proof:** Before the production edit, `python3 -m unittest tests.test_battery_float.BundleAuthenticationTests` failed all nine new tests because `battery_float.authenticate_bundle` was absent (`AttributeError`; `FAILED (errors=20)` including subtests). The same class and V1 now pass. Frozen-function source pins and `git diff --check` also pass. No commit, push, or full suite was run.

V4’s sole failure is `AssertionError: None is not an instance of <class 'str'>` for the live `os_build` probe.

## Residual risk

S1 must write the two ruled monotonic event fields before new non-mock bundles can pass this wrapper.