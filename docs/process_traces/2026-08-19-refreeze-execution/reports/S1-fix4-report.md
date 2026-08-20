```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "partial",
  "summary": "Fixed all four scoped failure clusters; focused suites pass, but the fresh canonical run stalled before a final result.",
  "workspace": {
    "base_requested": "d279bd2",
    "base_mode": "exact",
    "head_start": "d279bd2fc88a0d9ffcef38b17b41de082fb8c312",
    "head_end": "d279bd2fc88a0d9ffcef38b17b41de082fb8c312",
    "upstream_end": "d279bd2fc88a0d9ffcef38b17b41de082fb8c312",
    "branch": "impl/r2-s0-mint-resolver"
  },
  "pathspec": [
    "docs/contracts/d078_reason_registry_amendment.md",
    "tests/test_authentication_io.py",
    "tests/test_controller.py",
    "tests/test_d078_reason_registry.py",
    "tests/test_detection_floor.py"
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
      "cmd": "python3 -m unittest tests.test_d078_reason_registry tests.test_authentication_io tests.test_detection_floor.TestAnchorFallbackFloorMemberGate tests.test_controller -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 103 tests in 25.817s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 103 tests in [0-9.]+s\\s+OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_detection_floor",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 159 tests in 1.687s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 159 tests in [0-9.]+s\\s+OK"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_controller",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 70 tests in 27.339s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 70 tests in [0-9.]+s\\s+OK"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_authentication_io tests.test_d078_reason_registry tests.test_capture_pipeline_era tests.test_floor_extraction tests.test_whole_window",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 259 tests in 6.168s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 259 tests in [0-9.]+s\\s+OK"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_controller.HappyPathTests.test_powermetrics_thermal_coverage_is_continuous_across_admission_handoff -v",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["KeyError: 'clock_anchor'", "FAILED (errors=1)"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "KeyError: 'clock_anchor'"
      }
    },
    {
      "id": "V6",
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
      "kind": "verification_gap",
      "level": "blocking",
      "text": "A fresh `python3 -m unittest discover -s tests` run produced normal passing progress but stopped advancing at 27,707 log bytes without a final result or exit code.",
      "needs": "Rerun canonical in a clean runner and confirm the final residual set."
    }
  ]
}
```

## Change

Added the scoped D-078 amendment contract with the three requested reason-code semantics; registry tests now combine it with the governing historical registry.

Re-pinned the reducer SHA and the still-five direct reads. Updated floor fixtures to present schema/method v3 so the anchor-fallback gate remains their subject.

Updated the thermal handoff test to isolate v3 reconstruction from its intentionally too-short capture, while asserting the controller-persisted v3 identity. A temporary controller mutation replacing persisted evidence with `capture_pipeline_absent` made the test error on the missing `clock_anchor`; the mutation was restored.

## Verification notes

All requested focused suites passed: 103 combined cluster tests, 159 detection-floor tests, 70 controller tests, and 259 authentication/registry/capture-era/floor-extraction/whole-window tests.

Residual-red declaration is pending canonical completion. Focused verification introduces no residuals; the expected remaining set is only the evidence-author pair and docs-freshness.