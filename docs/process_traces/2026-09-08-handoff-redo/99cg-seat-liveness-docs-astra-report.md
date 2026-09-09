```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Documented window liveness, operator stale-entry repair, publication decisions, and consumer pointers; marked the task done.",
  "workspace": {
    "base_requested": "main ac092ccd",
    "base_mode": "exact",
    "head_start": "ac092ccd507c2e369ac4642dfce31352769ee698",
    "head_end": "ac092ccd507c2e369ac4642dfce31352769ee698",
    "upstream_end": "ac092ccd507c2e369ac4642dfce31352769ee698",
    "branch": "docs/2026-09-08-window-liveness-docs"
  },
  "pathspec": [
    "docs/process/MAGISTRATE_WATCHDOG.md",
    "docs/process/NIGHT_HANDBACK.md",
    "docs/contracts/window_liveness.md",
    "docs/process_traces/2026-08-28-live-smoke/SHAKEDOWN-G2-RUNSHEET.md",
    "TASK_QUEUE.md"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_docs_freshness > /private/tmp/window-liveness-docs-01-docs-freshness.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 31 tests in 0.920s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
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
      "kind": "environment",
      "level": "nonblocking",
      "text": "The sandbox blocked /bin/ps. The worked example uses a cited historical real PID/lstart capture and matching ownership record, explicitly labeled historical.",
      "needs": ""
    }
  ]
}
```

## Change

Added the reconstructable contract, including an operator repair command and publication decision table. All five scoped files are updated. No commit was made; lead diff review is next.

## Verification notes

Also checked contract links, embedded repair-command syntax, and new-file whitespace. The full suite was not needed for this docs-only change.