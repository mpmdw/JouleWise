```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented entry-point measurement detection and isolated process-census regressions; all requested checks pass.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "1c83f2af48df5611c7bbf824bec818209c252d0d",
    "head_end": "1c83f2af48df5611c7bbf824bec818209c252d0d",
    "upstream_end": null,
    "branch": "fix/2026-09-08-window-status-guard"
  },
  "pathspec": ["scripts/window_status.sh", "tests/test_window_status_guard.py"],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_window_status_guard > /private/tmp/WINDOW-STATUS-GUARD-CENSUS-01-unittest.log 2>&1\nresult=$?\nprintf 'rc=%s\\n' \"$result\" >> /private/tmp/WINDOW-STATUS-GUARD-CENSUS-01-unittest.log\ncat /private/tmp/WINDOW-STATUS-GUARD-CENSUS-01-unittest.log\nexit \"$result\"",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["OK", "rc=0"]},
      "expected": {"exit_code": 0, "tail_regex": "OK\\nrc=0"}
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "bash -n scripts/window_status.sh\nresult=$?\nprintf 'bash-n rc=%s\\n' \"$result\"\nexit \"$result\"",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["bash-n rc=0"]},
      "expected": {"exit_code": 0, "tail_regex": "bash-n rc=0"}
    },
    {
      "id": "V3",
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

Matches campaign and `window-chain` entry points instead of arbitrary command-line mentions; excludes campaign `--dry-run`. Night launch records persist after exit, so they cannot establish liveness. Custody-path restrictions would miss standalone campaigns.

Added `JOULEWISE_STATUS_PS_COMMAND`, defaulting to real `ps`, for deterministic test censuses. Census failure refuses before writing.

Counterfactual coverage: substring matching would fail the sibling-process regression; removing measurement detection would fail real-chain refusal assertions. Both existing sentinel tests pass.

## Verification notes

Five focused tests passed. Repository-wide suite intentionally omitted. No repository commit created. Branch has no configured upstream.

## Residual risk

Detection covers the inspected command shapes, not every possible interpreter wrapper or whitespace-containing executable path. The census remains a snapshot, with the existing race before publication.