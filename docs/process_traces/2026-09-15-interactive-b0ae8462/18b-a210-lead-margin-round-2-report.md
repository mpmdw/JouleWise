```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented PLAN/REQUEST/TERM/KILL leads of 5/5/3/2 minutes, preserving the 120-second install pad: the arm-to-t0 floor is strictly more than seven minutes.",
  "workspace": {
    "base_requested": "69d668be8da302c10860b4b3d4d64c08d8ba2a37",
    "base_mode": "exact",
    "head_start": "69d668be8da302c10860b4b3d4d64c08d8ba2a37",
    "head_end": "69d668be8da302c10860b4b3d4d64c08d8ba2a37",
    "upstream_end": "69d668be8da302c10860b4b3d4d64c08d8ba2a37",
    "branch": "feat/2026-09-15-lead-margin"
  },
  "pathspec": [
    "scripts/run_night.py",
    "scripts/magistrate_watchdog.py",
    "tests/test_run_night.py",
    "tests/test_magistrate_watchdog.py",
    "docs/phase_2/derivation_night_runbook.md",
    "docs/process/NIGHT_HANDBACK.md",
    "docs/process/MAGISTRATE_RELAUNCH_PROMPT.md",
    "docs/process/MAGISTRATE_WATCHDOG.md"
  ],
  "unowned_dirty": [
    "scripts/run_night.py",
    "scripts/magistrate_watchdog.py",
    "tests/test_run_night.py",
    "tests/test_magistrate_watchdog.py",
    "docs/phase_2/derivation_night_runbook.md",
    "docs/process/NIGHT_HANDBACK.md"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1-RED",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p python3 -B -m unittest tests.test_run_night.NightDriverTests.test_fixed_epoch_install_close_is_1799999580 tests.test_magistrate_watchdog.SupervisorTests.test_deadline_gaps_use_resident_poll_not_launchd_tick",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 2 tests in 0.013s", "FAILED (failures=2)", "real 0.55"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=2\\)"
      }
    },
    {
      "id": "V2-GREEN",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p python3 -B -m unittest tests.test_magistrate_watchdog",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 95 tests in 2.312s", "OK", "real 2.85", "user 1.95", "sys 0.62"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 95 tests[\\s\\S]*OK"
      }
    },
    {
      "id": "V3-GREEN",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -p python3 -B -m unittest tests.test_run_night",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 101 tests in 19.257s", "OK", "real 19.61", "user 15.97", "sys 2.10"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 101 tests[\\s\\S]*OK"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --check && git diff --exit-code -- joulewise/night_gate.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "! git diff --name-only | grep -E '(^|/)night_gate\\.py$'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "! git diff -U0 -- scripts/run_night.py scripts/magistrate_watchdog.py | grep -E '^[+-][^+-].*(LOAD|HID|BOOT|CENSUS_|PROBE_TIMEOUT|custody)'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "! rg -n -U '(t0\\s*[-−]\\s*(25|16|15|27|85)\\b|\\b(25|16|27|85)[ -]*(\\n)?min|nine.minute|1500)' scripts/run_night.py scripts/magistrate_watchdog.py docs/phase_2/derivation_night_runbook.md docs/process/NIGHT_HANDBACK.md docs/process/MAGISTRATE_RELAUNCH_PROMPT.md docs/process/MAGISTRATE_WATCHDOG.md",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B scripts/bridge scope-check --baseline .codex-bridge/baselines/mag-a210b-20260915.json --expect-digest sha256:160ae7c629d5382eacff419bf0eeceda4593a64c5c58d76a487b9f82185af031 --lease-id lease-bec59018ed5c4cc39b129da28bd9e153 --scope scripts/run_night.py scripts/magistrate_watchdog.py tests/test_run_night.py tests/test_magistrate_watchdog.py docs/phase_2/derivation_night_runbook.md docs/process/NIGHT_HANDBACK.md docs/process/MAGISTRATE_RELAUNCH_PROMPT.md docs/process/MAGISTRATE_WATCHDOG.md | python3 -B -c 'import json,sys; v=json.load(sys.stdin)[\"verdict\"]; print(v); sys.exit(0 if v == \"SCOPE_OK\" else 1)'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["SCOPE_OK"]},
      "expected": {"exit_code": 0, "tail_regex": "^SCOPE_OK\\s*$"}
    }
  ],
  "flags": []
}
```

## Change

All six prose sites are aligned:

- Driver constant commentary: seven-minute exclusive floor; 120-second pad preserved.
- Watchdog constants and request payload: 5/5/3/2 leads, two-minute courtesy, physical derivation and recovery limitations.
- Derivation runbook: fence definition, census/exit instructions, cutoff arithmetic, staged-plan assertion, evidence requirements, source table and glossary.
- Night handback: timeline, worked local/epoch boundaries and notice template.
- Relaunch prompt: exit within two minutes; absolute TERM/KILL deadlines prevail.
- Watchdog runbook: state descriptions, deadline table, recovery explanation and both boundary examples.

Tests pin constants, ordering, cutoff `1799999580`, six-poll minimum gaps, 110/50-second nominal slack, and late-request enforcement. Existing boundary fixtures were adjusted.

## Verification notes

The first watchdog run exposed six stale fixture/assertion failures; all were corrected before the final passing run. Only the two requested modules ran, sequentially and timed.

Baseline digest and all six pre-existing dirty-file hashes matched. Those round 1 changes were preserved and extended. Unrelated 15-minute liveness/courier allowances and standalone stop fallback timers remain unchanged. No commit, installation or live measurement occurred.

## Residual risk

KILL leaves less than two full minutes after teardown latency. Launchd recovery cannot guarantee the shortened phases after supervisor failure. The unchanged t0 gates refuse surviving agents or excess load.

Next: lead final diff review and verification under the normal merge gate.