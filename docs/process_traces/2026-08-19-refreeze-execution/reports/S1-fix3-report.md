```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Converted the live three-window scenario to anchor-v3 and retained a coherent anchor-v2 pre-filter refusal arm.",
  "workspace": {
    "base_requested": "d8f1202",
    "base_mode": "exact",
    "head_start": "d8f1202ec44f5da2a0e6fd758a57d74ec6863245",
    "head_end": "d8f1202ec44f5da2a0e6fd758a57d74ec6863245",
    "upstream_end": "d8f1202ec44f5da2a0e6fd758a57d74ec6863245",
    "branch": "impl/r2-s0-mint-resolver"
  },
  "pathspec": [
    "tests/fixtures/calibration_live_three_window/scenario.json",
    "tests/test_calibration_live_three_window.py"
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
      "cmd": "python3 -m unittest tests.test_calibration_live_three_window",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK (skipped=3)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=3\\)"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_calibration_bracketing",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK (skipped=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=1\\)"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest -v tests.test_arm_readiness_evidence_author.ArmReadinessEvidenceAuthorTests.test_production_suite_runner_records_exact_three_window_counts",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V4",
      "kind": "lint",
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
      "text": "The two known _v3-downstream reds remain classified as downstream baseline items; this scoped fixture repair neither changes nor masks them.",
      "needs": ""
    }
  ]
}
```

## Change

Updated the scenario’s T1 anchor identifier to the active rate-aware anchor-v3 method. The recorded fixture-generation provenance shows the n=17 numeric vectors were already regenerated for anchor-v3, so no hand-pinned values were guessed or changed.

Extended the existing endpoint-refusal coverage with a coherent all-live-endpoint anchor-v2 mutation. It asserts zero discovered candidates plus the `capture_pipeline_superseded` refusal diagnostics.

## Verification notes

`tests.test_arm_readiness_evidence_author` passed all 24 cases in bounded runs: 8 + 14 + 1 + 1. Its three-window count oracle remains 23 tests with 3 skips.