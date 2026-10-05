```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented authorized X7 history, admission recovery, NULL restore, and s2 writer changes; remaining runtime consumers require scope expansion.",
  "workspace": {
    "base_requested": "bda1c180",
    "base_mode": "exact",
    "head_start": "bda1c180cf156ecedcbe01a6010390dcd724c8cc",
    "head_end": "bda1c180cf156ecedcbe01a6010390dcd724c8cc",
    "upstream_end": "e7d13a1706d6352e0b3d9624dcf4c897671393da",
    "branch": "lane/2026-10-05-b4-x7"
  },
  "pathspec": [
    "joulewise/arm_readiness.py",
    "joulewise/night_gate.py",
    "joulewise/night_plan_writer.py",
    "joulewise/v5_qualification.py",
    "scripts/harvest_v5_g2b_window.py",
    "scripts/harvest_v5_qualification.py",
    "scripts/restore_v5_null_reservation.py",
    "scripts/write_v5_qualification_plan.py",
    "tests/fixtures/custody_read_replay_allowlist.json",
    "tests/test_authentication_io.py",
    "tests/test_harvest_v5_g2b_window.py",
    "tests/test_harvest_v5_qualification.py",
    "tests/test_v5_block4_replay.py",
    "tests/test_v5_block4_x7.py",
    "tests/test_v5_qualification_plan.py",
    "tests/test_v5_s1_qualification.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-x7 python3 -m unittest tests.test_v5_block4_x7 tests.test_v5_qualification_plan tests.test_harvest_v5_g2b_window tests.test_harvest_v5_qualification tests.test_v5_block4_x6 tests.test_v5_block4_replay tests.test_v5_s1_qualification tests.test_v5_s1_desk_closeout > /tmp/dd5-x7/focused-complete.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 174 tests in 152.218s", "OK (skipped=4)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=4\\)"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-x7 python3 -m unittest tests.test_authentication_io tests.test_custody_mode_inventory > /tmp/dd5-x7/authorized-registries-final.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 29 tests in 47.940s", "OK", "KILLED 3 renderer AST mutations: wrapper deletion, widened annotation, unregistered renderer"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^OK$"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-x7 python3 -m unittest tests.test_battery_float_consumers tests.test_git_fixture_maintenance > /tmp/dd5-x7/unowned-registries-final.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 22 tests in 26.879s", "FAILED (failures=3)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^OK$"
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
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "Untouched runtime consumers reject the new behavior: run_night.py:2427 requires the night plan ID to equal the frozen calibration plan ID; run_night.py:2370,3696 and produce_t0_rehearsal_bundle.py:429, v5_s1_desk_closeout.py:131, and t0_rehearsal.py:1314 retain s1-only checks.",
      "needs": "Lead-issued scope expansion for the four runtime paths, or assignment to another lane."
    },
    {
      "id": "F2",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "Battery registry tests retain two failures for existing unregistered production parse consumers in v5_qualification.battery_boundaries and check_v5_arm_abort, plus the existing test_install_night_agent fixture reference. The owning registry test is outside scope and was preserved.",
      "needs": "Authorize tests/test_battery_float_consumers.py for honest consumer and fixture registration."
    },
    {
      "id": "F3",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "Git fixture maintenance still detects direct initialization in test_v5_block4_x1.py, test_v5_block4_x2.py, and test_v5_s1_desk_closeout.py.",
      "needs": "Lane X8 owns these repairs under the lead ruling."
    },
    {
      "id": "F4",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Four joined replay tests explicitly skip because committed GAMMA lacks D-134 freeze authority. Canonical unittest discovery was interrupted earlier with exit 130 and was not completed against the final changes. Component fixtures do not establish live qualification.",
      "needs": "Lead completes joined verification and canonical discovery after resolving the remaining dependencies."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "scripts/run_night.py",
      "scripts/produce_t0_rehearsal_bundle.py",
      "scripts/v5_s1_desk_closeout.py",
      "joulewise/t0_rehearsal.py",
      "tests/test_battery_float_consumers.py"
    ],
    "reason": "Fresh attempt IDs and s2 plans now pass the authorized writer and harvest interfaces, but existing runtime and qualification consumers reject them; battery registry checks also require their owning allowlist.",
    "blocked_work": "Complete fresh-attempt launch, s2 observation and closeout, qualification evaluation, and clean battery registry verification.",
    "minimal_change": "Separate night attempt identity from frozen calibration identity, extend consuming occurrence checks to authenticated s1/s2 plans, and register the exact existing battery consumers and fixture reference."
  }
}
```

## Change

Added authenticated attempt chains and the registered census, native admission-abort replay and re-arm handling, an `s2` writer, and NULL restore for the exact native two-row reservation unit. Registered four replay calls and the restore authentication surface. Changes remain uncommitted; pinned estimator files were untouched.

## Verification notes

Remaining failures concern the out-of-scope battery registry and X8-owned Git fixtures. Joined replay remains skipped pending freeze authority; canonical discovery remains incomplete.

## Residual risk

Fresh-attempt and `s2` runtime completion requires the five-path scope expansion above.