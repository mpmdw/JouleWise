```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Round 7 implements S-2b by adopting a state-recorded live session on unsafe replacement ticks and durably continuing its drain ladder.",
  "workspace": {
    "base_requested": "cc4df46d17bcdc1f04aa860a45d166c6f848fb66",
    "base_mode": "exact",
    "head_start": "cc4df46d17bcdc1f04aa860a45d166c6f848fb66",
    "head_end": "cc4df46d17bcdc1f04aa860a45d166c6f848fb66",
    "upstream_end": "cc4df46d17bcdc1f04aa860a45d166c6f848fb66",
    "branch": "feat/2026-09-03-magistrate-watchdog"
  },
  "pathspec": [
    "docs/process/MAGISTRATE_WATCHDOG.md",
    "docs/process_traces/2026-09-03-watchdog-build/01-sol-landing-report.md",
    "docs/process_traces/2026-09-03-watchdog-build/19-sol-fix-round-7-report.md",
    "scripts/magistrate_watchdog.py",
    "tests/test_magistrate_watchdog.py",
    "tests/test_magistrate_watchdog_cli.py"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog.SupervisorTests.test_replacement_ticks_adopt_recorded_session_and_continue_unsafe_drain tests.test_magistrate_watchdog_cli.MagistrateWatchdogCliTests.test_real_cli_adopts_recorded_resident_on_unsafe_replacement_tick",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 2 tests in 0.318s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 2 tests.*OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 53 tests in 0.299s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 53 tests.*OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog_cli",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 3 tests in 11.259s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 3 tests.*OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_night_gate",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 47 tests in 0.560s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 47 tests.*OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 55 tests in 8.512s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 55 tests.*OK"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_install_night_agent",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 11 tests in 6.291s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 11 tests.*OK"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "No install, agent launch, launchd mutation, default-custody write, production-agent signal, or quiet-machine measurement occurred; the CLI test used a disposable sleep stub and an injected process-table seam because managed execution forbids /bin/ps.",
      "needs": "The lead and cold gate retain installed/live verification."
    }
  ]
}
```

## Change

S-2b is implemented without changing any other decision path. Each successful spawn or ordinary adoption persists the complete session identity in `state.json`. A replacement tick whose decision is `HOLD_UNSAFE` validates that recorded PID and start token, appends `resident_adopted{pid,start_time,activation}`, and executes one bounded step of the existing drain. `resident_hold_drain.stage` persists `REQUEST`, `TERM`, and terminal `KILL` progress while the original `standdown.request` timestamps remain unchanged. A missing process or changed start token records `already_gone`, clears the identity, and is never signalled.

### S-2b map

| S-2b clause | Production site | Biting assertion |
|---|---|---|
| State records PID + start time + activation | `scripts/magistrate_watchdog.py:472-490,1766-1783,1818-1834` | `tests/test_magistrate_watchdog.py:690-719`; `tests/test_magistrate_watchdog_cli.py:306-329` |
| Unsafe replacement tick adopts and records the exact live session | `scripts/magistrate_watchdog.py:1857-1937,1956-1987` | `tests/test_magistrate_watchdog.py:714-746`; `tests/test_magistrate_watchdog_cli.py:332-379` |
| Successive ticks retain the original request and continue REQUEST → TERM → KILL | `scripts/magistrate_watchdog.py:1533-1595,1630-1664` | `tests/test_magistrate_watchdog.py:711-768` |
| Start-token mismatch is `already_gone`, never signal authority | `scripts/magistrate_watchdog.py:1870-1899` | `tests/test_magistrate_watchdog.py:770-795` |
| Operator contract describes adoption and ladder continuation | `docs/process/MAGISTRATE_WATCHDOG.md:13-16,51-55,75-78` | Watchdog contract module remained green. |

### RED then GREEN

Tests were written first. On unchanged production code (exit 1):

```text
EF
ERROR: test_replacement_ticks_adopt_recorded_session_and_continue_unsafe_drain
TypeError: 'NoneType' object is not subscriptable
FAIL: test_real_cli_adopts_recorded_resident_on_unsafe_replacement_tick
AssertionError: False is not true
Ran 2 tests in 0.593s
FAILED (failures=1, errors=1)
```

After S-2b (exit 0):

```text
..
----------------------------------------------------------------------
Ran 2 tests in 0.318s

OK
```

### Five-module tails

```text
tests.test_magistrate_watchdog
Ran 53 tests in 0.299s
OK

tests.test_magistrate_watchdog_cli
Ran 3 tests in 11.259s
OK

tests.test_night_gate
Ran 47 tests in 0.560s
OK

tests.test_run_night
Ran 55 tests in 8.512s
OK

tests.test_install_night_agent
Ran 11 tests in 6.291s
OK
```

## Verification notes

The real-CLI regression runs `main()`, argument parsing, service locking, and `tick` in a separate Python process. Only the process-table dependency is injected because `/bin/ps` is denied by the managed sandbox. Its first drain action stays cooperative; test cleanup terminates only the disposable sleep stub.

## Residual risk

Installed launchd recovery and signalling of an actual ignored session remain lead/cold-gate work. No `[QUIET-MAC]` activity was started.
