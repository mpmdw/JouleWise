```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented A210 round-3 documentation and test amendments; 197 focused tests pass and scope check is SCOPE_OK.",
  "workspace": {
    "base_requested": "e05e497a292d78c131397a87029f9f64ca9db9b9",
    "base_mode": "exact",
    "head_start": "e05e497a292d78c131397a87029f9f64ca9db9b9",
    "head_end": "e05e497a292d78c131397a87029f9f64ca9db9b9",
    "upstream_end": "e05e497a292d78c131397a87029f9f64ca9db9b9",
    "branch": "feat/2026-09-15-lead-margin"
  },
  "pathspec": [
    "docs/decision_log.md",
    "docs/phase_2/derivation_night_runbook.md",
    "docs/process/MAGISTRATE_WATCHDOG.md",
    "docs/process/NIGHT_HANDBACK.md",
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 96 tests in 2.355s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 96 tests in .*s\\s+OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 101 tests in 17.328s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 101 tests in .*s\\s+OK"
      }
    },
    {
      "id": "V3",
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
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 scripts/bridge scope-check --baseline .codex-bridge/baselines/mag-a210c-20260916.json --expect-digest sha256:8f729032d6efbbc2c9d7a5d2a0db7c435d25ef3a65496e14dec2991a8110fe49 --lease-id lease-56cbed85a77a4aa39b0bfdf6acccd12d --scope scripts/magistrate_watchdog.py tests/test_magistrate_watchdog.py tests/test_run_night.py docs/phase_2/derivation_night_runbook.md docs/process/NIGHT_HANDBACK.md docs/process/MAGISTRATE_WATCHDOG.md docs/decision_log.md",
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
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "Requested amendments are complete. D-171(b)'s reinterpretation remains explicitly PENDING Ed's ratification; 8/8/6/5 is recorded as the conservative alternative.",
      "needs": "Lead to obtain and record Ed's ratification and perform final review before landing."
    }
  ]
}
```

## Change

Documented idle-daemon timing, reduced scan margin, KILL-only load bounds, and TERM as the working teardown. Added the chain-parsed 600-second settle test, removed the weakness assertion, corrected stale decision-log boundaries, and updated interactive handback and the rehearsal example to +10 minutes.

## Verification notes

Ran both requested modules individually. Full discovery was unnecessary for this documentation/test-only amendment. No runtime changes, commits, installation, or live measurements.

## Residual risk

Ratification remains pending. The documented late-scan margin and launchd recovery limitations remain for lead review.