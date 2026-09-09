```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented F2–F4 and documented the process-identity residual; all 100 scoped tests pass.",
  "workspace": {
    "base_requested": "138e7edb",
    "base_mode": "descendant",
    "head_start": "1c83f2af48df5611c7bbf824bec818209c252d0d",
    "head_end": "1c83f2af48df5611c7bbf824bec818209c252d0d",
    "upstream_end": "1c83f2af48df5611c7bbf824bec818209c252d0d",
    "branch": "fix/2026-09-08-watchdog-nits"
  },
  "pathspec": [
    "scripts/magistrate_watchdog.py",
    "scripts/install_magistrate_watchdog.sh",
    "docs/process/MAGISTRATE_WATCHDOG.md",
    "tests/test_magistrate_watchdog.py",
    "tests/test_install_magistrate_watchdog.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog tests.test_magistrate_watchdog_cli tests.test_install_magistrate_watchdog > /tmp/watchdog-nits-01-tests-final.log 2>&1; result=$?; print \"TEST_RC=$result\" >> /tmp/watchdog-nits-01-tests-final.log; tail -n 7 /tmp/watchdog-nits-01-tests-final.log; exit \"$result\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 100 tests in 21.367s", "", "OK", "TEST_RC=0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 100 tests in .*s\\n\\nOK\\nTEST_RC=0"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": []
}
```

## Change

- **F2:** Deduplicated refusal events per full reason and activation, with matching notice IDs. Regression covers ten identical ticks producing one event/notice, changed PIDs producing a second, acknowledgement independence, and activation reset.
- **F3:** Installer calls shared `handoff-daemons`, retaining refusal before writes. All five daemon shapes remain covered; a new test rejects inline classifier duplication.
- **F4:** Documented reconciliation now names `handoff_lock_absent` before reading. Extraction regression checks that refusal, Python compilation, and `zsh -n`.

## Verification notes

The first run exposed an obsolete assertion expecting two installer regex copies. Updated it for the remaining ancestry check; acceptance rerun passed. No repository-wide suite or commit was performed. Changes are ready for lead review.

## Residual risk

Documented that PID plus seconds-resolution `lstart` remains weaker than XNU’s unique PID.