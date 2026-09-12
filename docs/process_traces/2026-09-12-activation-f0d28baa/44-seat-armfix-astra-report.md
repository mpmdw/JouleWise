```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Shared freeze fixture now authors at current monotonic time; literal-origin mutation is killed, and all requested runnable tests pass.",
  "workspace": {
    "base_requested": "origin/main@ace4cc3c",
    "base_mode": "exact",
    "head_start": "ace4cc3cf545728e7327c14ba1084cbabb47e3ad",
    "head_end": "ace4cc3cf545728e7327c14ba1084cbabb47e3ad",
    "upstream_end": "ace4cc3cf545728e7327c14ba1084cbabb47e3ad",
    "branch": "fix/2026-09-12-arm-readiness-fixture-clock-origin"
  },
  "pathspec": ["tests/test_arm_readiness_dry_run.py"],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest -v tests.test_arm_readiness_dry_run.FreezeFixtureClockOriginTests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "joulewise.arm_readiness.ArmReadinessError: evidence item expired",
          "Ran 2 tests in 1.581s",
          "FAILED (errors=1)"
        ]
      },
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(errors=1\\)"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest -v tests.test_arm_readiness_dry_run.FreezeFixtureClockOriginTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 2 tests in 1.671s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest -v tests.test_arm_readiness_dry_run.ArmReadinessDryRunTests.test_dry_run_becomes_stale_after_later_head_even_when_pack_bytes_do_not_change tests.test_arm_readiness_dry_run.ArmReadinessDryRunTests.test_dry_run_rehearsal_root_and_id_are_single_use tests.test_arm_readiness_dry_run.ArmReadinessDryRunTests.test_real_under_lease_rehearsal_uses_reservation_and_both_writer_slots tests.test_arm_readiness_lifecycle.ArmReadinessLifecycleTests.test_atomic_launch_capability_race_exactly_one_consumer_and_replay_refuses tests.test_arm_readiness_lifecycle.ArmReadinessLifecycleTests.test_boot_session_change_voids_verification_and_consumption tests.test_arm_readiness_lifecycle.PostSupersessionLayeringTests.test_historical_predecessor_resolves_and_still_anchors_the_chain tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_acid_real_boot_session_then_real_arm_generator_reaches_go",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 7 tests in 51.294s", "OK (skipped=1)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=1\\)"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python3 -B -m unittest -v tests.test_arm_readiness_dry_run tests.test_arm_readiness_lifecycle tests.test_arm_readiness_evidence_t0 > /tmp/armfix-three-modules.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 152 tests in 562.344s", "OK (skipped=2)"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK \\(skipped=2\\)"}
    },
    {
      "id": "V5",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Six of the seven named tests passed; real-boot ACID skipped because sandboxed kern.bootsessionuuid access is denied. The full modules also retained the existing structural skip for the synthetic fixture's absent family-publication marker.",
      "needs": "Lead owns final review and real-boot ACID verification where sysctl is available."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The full module process exited 0, then printed an ignored atexit RuntimeError reporting no accessible Metal device.",
      "needs": ""
    }
  ]
}
```

## Change

`install_passing_freeze` samples `time.monotonic_ns()` once at line 145 and passes it to every receipt assembler at line 180. Search found exactly one literal `now_monotonic_ns=1` authoring site; it is removed. Production expiry checks, horizons, and existing assertions are untouched.

All existing callers already share this helper:

- `tests/test_arm_readiness_dry_run.py`: 348, 650, 700, 725, 748; new regression caller: 281.
- `tests/test_arm_readiness_lifecycle.py`: 853, 982, 3074.
- `tests/test_arm_readiness_evidence_t0.py`: 433, 443.

Regressions at lines 297 and 311 author at simulated uptime `648000000000001` ns. Authentication at origin + 1 second passes; origin + 8 days raises `readiness_record_expired`, specifically “evidence item expired.”

Final workspace:

```text
 M tests/test_arm_readiness_dry_run.py
 tests/test_arm_readiness_dry_run.py | 59 ++++++++++++++++++++++++++++++++++++-
 1 file changed, 58 insertions(+), 1 deletion(-)
```

No commit, push, HEAD movement, NEEDS_SCOPE, or NEEDS_RULING.

## Verification notes

V1 is the deliberate killed cut at line 180:

```diff
-            now_monotonic_ns=authored_at_monotonic_ns,
+            now_monotonic_ns=1,
```

The fresh-evidence regression reached production line 6299 and failed with `evidence item expired`; the eight-day expiry test still passed. Restoring the helper produced V2.

SHA256 of `tests/test_arm_readiness_dry_run.py`:

```text
Original baseline:
c71dd99e9904536ad156d97dae70aa2b98a0747803556247fc8bf9e18c06913a
Cured, before mutation:
6d654437ab3434c173e3987b39cb710d850d544590bc9334ed41f248bd37ef91
Literal-1 mutation:
28ed30fa705131b8196a17315f72011f7b67a2180005e2e9a09c960e71c03b09
Restored cure, final:
6d654437ab3434c173e3987b39cb710d850d544590bc9334ed41f248bd37ef91
```

`cmp` also confirmed byte-identical restoration. Full module output is retained at `/tmp/armfix-three-modules.log`.