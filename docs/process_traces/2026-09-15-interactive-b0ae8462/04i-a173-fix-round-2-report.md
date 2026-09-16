```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented F1 ruling, preserved round 2 edits, passed both modules, and killed both required mutations.",
  "workspace": {
    "base_requested": "c3eedd8d0d41568f8be589edca97d8cc12cf0cb4",
    "base_mode": "exact",
    "head_start": "c3eedd8d0d41568f8be589edca97d8cc12cf0cb4",
    "head_end": "c3eedd8d0d41568f8be589edca97d8cc12cf0cb4",
    "upstream_end": "c3eedd8d0d41568f8be589edca97d8cc12cf0cb4",
    "branch": "feat/2026-09-15-arm-census-idle"
  },
  "pathspec": [
    "joulewise/arm_census.py",
    "tests/test_arm_census.py"
  ],
  "unowned_dirty": [
    "joulewise/arm_census.py",
    "tests/test_arm_census.py"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_arm_census",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 20 tests in 0.034s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_run_night",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 104 tests in 17.978s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B mutation_probe.py",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/b0ae8462-f5fb-4c83-baa6-1882cb05ff89/scratchpad/seats/a173-fix2b-mut",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "DROP_B_RED: exit=1",
          "FAIL: test_unreadable_own_root_retains_known_side_work (tests.test_arm_census.ArmCensusTests.test_unreadable_own_root_retains_known_side_work) (busy=True)",
          "AssertionError: True != False",
          "FAILED (failures=1)",
          "DROP_B_RESTORED_GREEN: exit=0",
          "OK",
          "DROP_A_RED: exit=1",
          "FAIL: test_own_root_selection_without_ancestor_discovery_hits (tests.test_arm_census.ArmCensusTests.test_own_root_selection_without_ancestor_discovery_hits) (case='helper_only')",
          "AssertionError: False != True",
          "FAILED (failures=3)",
          "DROP_A_RESTORED_GREEN: exit=0",
          "OK",
          "MUTATIONS 2/2 RED; BOTH RESTORED GREEN"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "MUTATIONS 2/2 RED; BOTH RESTORED GREEN"
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
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/bridge scope-check --baseline .codex-bridge/baselines/mag-a173-fix2b-20260915.json --expect-digest sha256:d4a290bef98623a6abc7fef5642823748501136d029fee04ae9f8a9341c32b57 --scope joulewise/arm_census.py tests/test_arm_census.py --lease-id lease-5a2b686ab6f14e548e0f2196026cfe74",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\"verdict\":\"SCOPE_OK\""
      }
    }
  ],
  "flags": []
}
```

## Change

Hunks added over the preserved baseline:

- `_own_root` accepts discovery hits and selects an unreadable own-chain hit through branch (b), retaining readable-root branch (a).
- Observation and classification both supply discovery hits to the selector.
- Added an unreadable outer-root regression covering readable inner ancestry, descendant workload blocking, and idle-helper exemption.

The existing unreadable-root test and round 2 fixtures remain unchanged.

## Verification notes

The baseline unreadable-root failure was reproduced before repair. Dropping branch (b) reproduces that failure; dropping branch (a) fails the helper-only CLEAR cell.

`unowned_dirty` records the two baseline-dirty files whose existing changes were preserved. Scope checking returned `SCOPE_OK`. Verification used individual modules and an isolated `cp -R` mutation copy. No commit or real `launchctl` ran.

Next step: lead final diff review and verification.