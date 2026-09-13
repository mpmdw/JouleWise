```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Replaced G4's grep control with real-pgrep decoy controls; preserved round 1 edits; requested offline checks pass.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "4b9a34111d33a04727a09127a1c1fbd8aab87052",
    "head_end": "4b9a34111d33a04727a09127a1c1fbd8aab87052",
    "upstream_end": "4b9a34111d33a04727a09127a1c1fbd8aab87052",
    "branch": "fix/2026-09-13-arm-census-system-services"
  },
  "pathspec": ["tests/test_arm_readiness_evidence_t0.py"],
  "unowned_dirty": [
    "joulewise/arm_readiness_evidence_t0.py",
    "tests/test_arm_readiness_evidence_t0.py"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_evidence_t0 -k g1 -k g2 -k g3",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 3 tests in 12.944s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 3 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_integration tests.test_arm_readiness_registry tests.test_arm_readiness_schemas",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 69 tests in 274.925s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 69 tests in .*s\\n\\nOK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_t0_liveness_constant_is_derived_from_the_post_r1_probe_census",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 0.043s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 1 test in .*s\\n\\nOK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_evidence_t0 -k g4",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: 3 != 0 : sysmon request failed with error: sysmond service not found",
          "pgrep: Cannot get process list",
          "",
          "",
          "----------------------------------------------------------------------",
          "Ran 1 test in 0.801s",
          "",
          "FAILED (failures=2)"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 1 test in .*s\\n\\nOK"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --stat -- joulewise/arm_readiness_evidence_t0.py tests/test_arm_readiness_evidence_t0.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " joulewise/arm_readiness_evidence_t0.py  |   8 +-",
          " tests/test_arm_readiness_evidence_t0.py | 141 +++++++++++++++++++++++++++++++-",
          " 2 files changed, 145 insertions(+), 4 deletions(-)"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "2 files changed"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git status --short",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " M joulewise/arm_readiness_evidence_t0.py",
          " M tests/test_arm_readiness_evidence_t0.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^ M joulewise/arm_readiness_evidence_t0.py\\n M tests/test_arm_readiness_evidence_t0.py$"
      }
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Both G4 subtests reached real pgrep and received the declared sandbox exit 3. This is an environment limitation, not evidence of an implementation defect. G4 remains Darwin-only and enabled.",
      "needs": "Lead must run G4 at the Darwin bench and verify both decoy controls."
    }
  ]
}
```

## Change

`tests/test_arm_readiness_evidence_t0.py:2628–2658`: removed the grep loop. Each pattern now gets a `/bin/sleep` decoy with the specified argv0, a 0.3-second wait, and the existing real-probe path. Assertions require exit 0, the decoy’s PID line, pattern re-matching, and exclusion of recorded service basenames. Cleanup calls `terminate()` and `wait(timeout=5)` in `finally`.

The raw docstring names M10 and explains the bench-proven `\bwatch\b` failure under pgrep’s engine. Round 1 edits remain; no commit or out-of-scope edit was made.

## Verification notes

G4 produced the expected sandbox restriction; no retry or repository skip was added. Test commands used `PYTHONDONTWRITEBYTECODE=1` to prevent bytecode writes. Verification followed the requested targeted checks; the canonical full suite was not run. Diff statistics include preserved round 1 changes.

## Residual risk

What the lead should double-check: run V4 on Darwin with process-list access, confirm both decoy PID assertions and cleanup, and confirm any real Firefox output passes the retained checks.