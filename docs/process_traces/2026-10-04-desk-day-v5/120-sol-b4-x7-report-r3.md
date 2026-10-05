```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented authenticated attempt history, admission re-arm, NULL reservation restore, and s2 runtime support; changes remain uncommitted.",
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
    "joulewise/t0_rehearsal.py",
    "joulewise/v5_qualification.py",
    "scripts/harvest_v5_g2b_window.py",
    "scripts/harvest_v5_qualification.py",
    "scripts/produce_t0_rehearsal_bundle.py",
    "scripts/restore_v5_null_reservation.py",
    "scripts/run_night.py",
    "scripts/v5_s1_desk_closeout.py",
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
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-x7 python3 -m unittest tests.test_v5_block4_x7 tests.test_v5_qualification_plan tests.test_harvest_v5_g2b_window tests.test_harvest_v5_qualification tests.test_v5_block4_x6 tests.test_v5_block4_replay tests.test_v5_s1_qualification tests.test_v5_s1_desk_closeout > /tmp/dd5-x7/focused-allowance-final.log 2>&1",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK (skipped=4)"]},
      "expected": {"exit_code": 0, "tail_regex": "^OK \\(skipped=4\\)$"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-x7 python3 -m unittest tests.test_authentication_io tests.test_custody_mode_inventory tests.test_run_night.PackNightProducerTests tests.test_run_night.Ruling76DriverTests > /tmp/dd5-x7/registries-runtime-consumers-final.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK", "KILLED 3 renderer AST mutations: wrapper deletion, widened annotation, unregistered renderer"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-x7 python3 -m unittest tests.test_battery_float_consumers tests.test_git_fixture_maintenance > /tmp/dd5-x7/x8-owned-registry-final.log 2>&1",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (failures=3)"]},
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-x7 python3 -m unittest discover -s tests -f > /tmp/dd5-x7/canonical-final-failfast.log 2>&1",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (failures=1, skipped=3)"]},
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "cd /tmp/dd5-x7/base-bda1c180 && PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/dd5-x7 python3 -m unittest tests.test_arm_readiness.LaunchConsumptionV2Tests.test_launch_recipe_reconciliation_reads_each_artifact_once > /tmp/dd5-x7/arm-read-count-base.log 2>&1",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (failures=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V6",
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
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The three X8-owned battery-consumer and git-fixture maintenance failures remain unchanged. Their paths were preserved as instructed.",
      "needs": "Integrate X8 fixes and rerun these checks."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Four joined replay tests remain skipped because the committed GAMMA pack lacks freeze authority. Component fixtures do not establish joined or live qualification.",
      "needs": "Close the genuine freeze-authority gate, then complete the joined replay cases."
    },
    {
      "id": "F3",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "Canonical fail-fast discovery stopped after 450 tests at LaunchConsumptionV2Tests.test_launch_recipe_reconciliation_reads_each_artifact_once: chain reads were 3, expected 1. The identical failure was reproduced from an unchanged bda1c180 archive in scratch. Remaining canonical tests were not run.",
      "needs": "Lead adjudicate the baseline read-cache/test contract and rerun canonical discovery on the integrated tree."
    }
  ]
}
```

## Change

Added mandatory history bindings, authenticated chain walking and census, guard-attested admission re-arm, and tooling-only `s2`. NULL restore preserves the attempted ledger and validates the exact native reservation unit before restoring seed bytes with the pin unchanged.

Runtime consumers now accept authenticated `s1`/`s2` occurrences and distinguish fresh night identity from frozen calibration identity. Registered the restore authentication surface and four retained-ledger replay sites.

## Verification notes

The focused suite ran 179 tests; registry and runtime-consumer checks ran 56. Acceptance remains pending the flagged X8 fixes, missing freeze authority, and independently reproduced canonical baseline failure.

All 20 modified paths are authorized. HEAD is unchanged; nothing was staged, committed, or pushed.