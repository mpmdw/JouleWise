```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented F1–F4; all five new regressions fail against a37de2ec and all 10 focused tests pass.",
  "workspace": {
    "base_requested": "a37de2ec",
    "base_mode": "exact",
    "head_start": "a37de2ec31d32be02cec0fa5c3ffd9bde6c5da83",
    "head_end": "a37de2ec31d32be02cec0fa5c3ffd9bde6c5da83",
    "upstream_end": null,
    "branch": "fix/2026-09-08-window-status-guard"
  },
  "pathspec": ["scripts/window_status.sh", "tests/test_window_status_guard.py"],
  "unowned_dirty": [],
  "verdict": {"implementation": "implemented", "acceptance": "ready"},
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_window_status_guard",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK", "rc=0"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "bash -n scripts/window_status.sh",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "cd /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/window-status-f1-f4-yhxpb7ic/baseline && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_window_status_guard.WindowStatusGuardTests.test_run_night_custom_chain_refuses",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (failures=2)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "cd /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/window-status-f1-f4-yhxpb7ic/baseline && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_window_status_guard.WindowStatusGuardTests.test_paths_with_spaces_refuse",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (failures=2)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "cd /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/window-status-f1-f4-yhxpb7ic/baseline && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_window_status_guard.WindowStatusGuardTests.test_python_option_separator_refuses",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (failures=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "cd /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/window-status-f1-f4-yhxpb7ic/baseline && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_window_status_guard.WindowStatusGuardTests.test_garbage_census_refuses",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (failures=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED"}
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "cd /var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/window-status-f1-f4-yhxpb7ic/baseline && PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_window_status_guard.WindowStatusGuardTests.test_empty_census_refuses",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (failures=1)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED"}
    }
  ],
  "flags": []
}
```

## Change

The guard now validates PID/PPID census rows, matches measurement path components across spaces and interpreter options, and recognizes `run_night` with custom chains. Sibling-test, dry-run, grep, and Codex-prompt exclusions remain covered.

## Verification notes

Baseline failures are expected: every new regression observed the old script returning success instead of refusing. Logs, including acceptance output and return code, are in [the verification directory](/var/folders/p3/fpwjrcg55vb0zsn3knm7xk2m0000gn/T/window-status-f1-f4-yhxpb7ic).

No repository-wide suite or repository commit was performed. Ready for lead review.