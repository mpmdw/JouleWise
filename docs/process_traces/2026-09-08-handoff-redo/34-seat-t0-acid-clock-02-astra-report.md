```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Separated RAW author anchors from ordinary-monotonic sequence timing; both offset regressions and the full module pass.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "e4ce8b3bece33db40de68b6c407a514fbaed9a26",
    "head_end": "e4ce8b3bece33db40de68b6c407a514fbaed9a26",
    "upstream_end": null,
    "branch": "fix/2026-09-08-t0-acid-clock-02"
  },
  "pathspec": ["tests/test_launch_window.py"],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_launch_window.ProductionArmRelocationLaunchTests.test_real_minted_v4_launch_accepts_relocation_and_refuses_content_change > /tmp/t0-acid-clock-02-baseline.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "joulewise.arm_readiness_evidence_t0.T0EvidenceAuthoringError: T-0 RAW anchor span is below 600000000000 ns",
          "Ran 1 test in 50.093s",
          "FAILED (errors=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(errors=1\\)"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_launch_window.ProductionArmRelocationLaunchTests.test_mint_keeps_raw_anchors_separate_from_sequence_clock > /tmp/t0-acid-clock-02-regression-before.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "joulewise.arm_readiness_evidence_t0.T0EvidenceAuthoringError: T-0 RAW anchor span is below 600000000000 ns",
          "joulewise.arm_readiness_evidence_t0.T0EvidenceAuthoringError: T-0 RAW anchor span exceeds 3600000000000 ns",
          "Ran 1 test in 100.246s",
          "FAILED (errors=2)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(errors=2\\)"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_launch_window > /tmp/t0-acid-clock-02-module-after.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 26 tests in 287.052s", "OK"]
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
    }
  ],
  "flags": []
}
```

## Change

The author now uses `sample_anchor()`’s RAW endpoint, matching R0’s clock family. Capture ordering and sequence age retain ordinary monotonic time. No other affected helper was found.

Counterfactual killed: using ordinary monotonic time as the RAW author endpoint. Fixed offsets of −2 hours and +2 hours failed before the change and passed afterward.

## Verification notes

The reported baseline refusal reproduced. Post-fix module rc: **0**, all **26 tests passed**, including relocation acceptance and content-change refusal. Logs are recorded above.

Production code remained unchanged. No repository-wide suite or repository commit was run.