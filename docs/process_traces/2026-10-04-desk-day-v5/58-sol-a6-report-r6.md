```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "G1–G3 implemented and verified with both probe states; suite failures compared with main; changes left uncommitted.",
  "workspace": {
    "base_requested": "aba27481",
    "base_mode": "exact",
    "head_start": "aba274813d0086e53244fa1041dfde806cc3e759",
    "head_end": "aba274813d0086e53244fa1041dfde806cc3e759",
    "upstream_end": "aba274813d0086e53244fa1041dfde806cc3e759",
    "branch": "feat/2026-10-04-launch-realization-recheck"
  },
  "pathspec": [
    "joulewise/measurement_liveness.py",
    "scripts/run_night.py",
    "tests/test_launch_window_realization_recheck.py",
    "tests/test_measurement_liveness.py",
    "tests/test_run_night.py"
  ],
  "unowned_dirty": [],
  "verdict": {"implementation": "implemented", "acceptance": "pending_verification"},
  "verification": [
    {
      "id": "V1", "kind": "suite",
      "cmd": "env TMPDIR=/tmp/dd5-a6r6 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider -o cache_dir=/tmp/dd5-a6r6/pc tests/test_launch_window_realization_recheck.py tests/test_measurement_liveness.py tests/test_run_night.py tests/test_launch_window.py",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["12 failed, 335 passed, 9 skipped, 17 warnings, 280 subtests passed in 1048.39s (0:17:28)"]},
      "expected": {"exit_code": 0, "tail_regex": "^347 passed, 9 skipped, .*280 subtests passed in.*$"}
    },
    {
      "id": "V2", "kind": "test",
      "cmd": "cd /Users/edr/code/JouleWise && env TMPDIR=/tmp/dd5-a6r6 PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/Users/edr/code/JouleWise /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider -o cache_dir=/tmp/dd5-a6r6/pc tests/test_run_night.py -k 'installer or launch_agent_template_disables_restart or blocked_journal_never_blocks_deadline_or_grants_go or blocking_join_startup_and_post_publication or pre_send_local_timeout_and_late_global_expiry or startup_hang_is_nonblocking'",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["10 failed, 3 passed, 244 deselected, 1 warning in 40.50s"]},
      "expected": {"exit_code": 0, "tail_regex": "^13 passed, 244 deselected, .*"}
    },
    {
      "id": "V3", "kind": "test",
      "cmd": "env TMPDIR=/tmp/dd5-a6r6 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider -o cache_dir=/tmp/dd5-a6r6/pc tests/test_run_night.py::BindSupervisionProcessTests::test_blocked_journal_never_blocks_deadline_or_grants_go tests/test_run_night.py::BindSupervisionProcessTests::test_blocking_join_startup_and_post_publication tests/test_run_night.py::BindSupervisionProcessTests::test_pre_send_local_timeout_and_late_global_expiry tests/test_run_night.py::BindSupervisionProcessTests::test_startup_hang_is_nonblocking",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["2 failed, 2 passed, 1 warning in 36.59s"]},
      "expected": {"exit_code": 0, "tail_regex": "^4 passed, .*"}
    },
    {
      "id": "V4", "kind": "test",
      "cmd": "env TMPDIR=/tmp/dd5-a6r6 PYTHONDONTWRITEBYTECODE=1 JOULEWISE_IDENTITY_PROBE=/tmp/dd5-a6r6/identity-probe /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider -o cache_dir=/tmp/dd5-a6r6/pc tests/test_launch_window_realization_recheck.py tests/test_measurement_liveness.py tests/test_run_night.py -k 'driver_death_during_stalled_recheck or same_pid_start_time or dead_man_resolution_clears_later_census or unresolved_pending_reused_pid'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["5 passed, 312 deselected, 1 warning, 7 subtests passed in 2.47s"]},
      "expected": {"exit_code": 0, "tail_regex": "^5 passed, 312 deselected, 1 warning, 7 subtests passed in.*$"}
    },
    {
      "id": "V5", "kind": "test",
      "cmd": "env TMPDIR=/tmp/dd5-a6r6 PYTHONDONTWRITEBYTECODE=1 JOULEWISE_IDENTITY_PROBE=/tmp/dd5-a6r6/unavailable-probe /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider -o cache_dir=/tmp/dd5-a6r6/pc tests/test_launch_window_realization_recheck.py tests/test_measurement_liveness.py tests/test_run_night.py -k 'driver_death_during_stalled_recheck or same_pid_start_time or dead_man_resolution_clears_later_census or unresolved_pending_reused_pid'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["5 passed, 312 deselected, 1 warning, 7 subtests passed in 2.46s"]},
      "expected": {"exit_code": 0, "tail_regex": "^5 passed, 312 deselected, 1 warning, 7 subtests passed in.*$"}
    },
    {
      "id": "V6", "kind": "inspection", "cmd": "git diff --check", "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {"id": "F1", "kind": "environment", "level": "nonblocking", "text": "At main b53c58d8fd219a2e32a369bfe3361f89edc05900, all eight installer failures reproduce the same child-Python battery-fixture assertion. Main and the branch retry both fail only journal_block and startup_hang watchdog tests; the two additional full-run watchdog failures pass on retry.", "needs": "Lead adjudicates baseline failures during final verification."},
    {"id": "F2", "kind": "verification_gap", "level": "nonblocking", "text": "Real ps is unavailable in this sandbox. Faithful start-time, reused-PID, and unavailable-probe cases passed using stubs.", "needs": "Lead runs G1 outside the sandbox with real ps."},
    {"id": "F3", "kind": "environment", "level": "nonblocking", "text": "git add failed with exit 128: cannot create /Users/edr/code/JouleWise/.git/worktrees/JouleWise-wt-dd5-a6/index.lock (Operation not permitted). Changes remain unstaged and uncommitted; nothing pushed.", "needs": "Lead reviews and commits the five-file diff."},
    {"id": "F4", "kind": "residual_risk", "level": "nonblocking", "text": "G4, G5, and G6 remain unchanged as requested.", "needs": ""}
  ]
}
```

## Change

G1 now observes the start time recorded in `launch.pending`; the separate reused-PID tests remain. G2 pins the shared probe to UTC while retaining locale settings. G3 writes the existing durable closure after proving group absence; tests cover both residual-table collisions and live-group refusal.

## Verification notes

The requested suite completed in the foreground. Installer failures reproduced on main; the supervision retry matched main’s two watchdog failures. No branch-only failure remained in the comparison. Real-`ps` verification and committing remain with the lead.

## Residual risk

- G4: barrier constants do not prove handshake behavior.
- G5: deadline/claim race can leave an unclosed chain marker conservatively.
- G6: unexpected helper exceptions retain their general error mapping.