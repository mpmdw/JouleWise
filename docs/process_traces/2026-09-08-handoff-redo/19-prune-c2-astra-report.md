```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Restored fail-closed corrupt-lock reconciliation and documented Ed-only manual recovery.",
  "workspace": {
    "base_requested": "b3eeee9a",
    "base_mode": "exact",
    "head_start": "b3eeee9a7dc57db1c56b19a288930d542523dfb7",
    "head_end": "b3eeee9a7dc57db1c56b19a288930d542523dfb7",
    "upstream_end": null,
    "branch": "feat/2026-09-08-watchdog-census-daemon"
  },
  "pathspec": [
    "docs/process/MAGISTRATE_WATCHDOG.md",
    "tests/test_magistrate_watchdog.py"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog.HandoffDefectTests.test_c2_corrupt_lock_recovery_refuses_even_with_absent_saved_owner -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog tests.test_magistrate_watchdog_cli tests.test_install_magistrate_watchdog -v > /private/tmp/watchdog-c2-prune-acceptance.log 2>&1; rc=$?; print \"acceptance_rc=$rc\" >> /private/tmp/watchdog-c2-prune-acceptance.log",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 95 tests in 19.108s", "", "OK", "acceptance_rc=0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK\\nacceptance_rc=0"
      }
    },
    {
      "id": "V3",
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
  "flags": []
}
```

## Change

Reverted step 4’s baseline lines 166–169 and 181–193: removed the inventory argument/imports and corrupt-lock conversion to `None`; restored `handoff_census([], lock, rows)`. The reconciliation Python now exactly matches `898e5305`.

Documented Ed-only observer inspection and manual `rm`, citing 2026-09-08 delta re-audit R1. C1, C3, C4, and C7 remain intact; the production script needed no edit.

The replacement regression covers `{torn`, `{}`, and `[]`, including absent saved owner PID 100 with live unrecorded resident PID 84232 using the resident launch options. It requires `handoff_lock_not_clear` containing `handoff_lock_invalid` and unchanged lock bytes.

## Verification notes

Fail-before tail: `FAILED (failures=12)`, rc 1. Pass-after tail: `OK`, rc 0. Logs: `/private/tmp/watchdog-c2-prune-{before,after}.log`.

All seven extracted shell blocks passed `zsh -n`; reconciliation, twin-stop, and reaper Python passed `compile()`. The three-space `watchdog_checkout=` … `   PY` extraction remains unchanged.

Acceptance: 95 tests, rc 0, recorded in `/private/tmp/watchdog-c2-prune-acceptance.log`. No repository-wide suite or commit.