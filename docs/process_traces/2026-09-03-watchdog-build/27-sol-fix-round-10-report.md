# Sol implementation report — fix round 10

Date: 2026-09-04. Starting and current committed HEAD: `fdbb840c11aea3f6abd30c9ad5c199487fe7299c` on `feat/2026-09-03-magistrate-watchdog`; all round-10 changes are intentionally uncommitted. Contract: the round-10 rows in packet-21 synthesis trace 24, cold ruling trace 22 §3/§4, and Opus refutation trace 23 H-2. No install, canonical-checkout mutation, default-custody access, agent launch, signal, email, or quiet-machine work occurred.

## Clause map

| Clause | Production/documentation site | Biting evidence |
|---|---|---|
| M-A — v2 label on the complete v1 key set and v1 label on a subset both HOLD | unchanged classifier `scripts/magistrate_watchdog.py:133-141`; CLI siblings `tests/test_magistrate_watchdog_cli.py:174-205` | Real `tick` subprocess test; M1 and M9 each failed independently on the missing sibling path. |
| M-C — mutation M8 is named and pinned | installer rollback behavior at `scripts/install_magistrate_watchdog.sh:155-205,238-284`; named test `tests/test_magistrate_watchdog.py:1208-1235` | A failed first-install lock collision must remove the plist created by that attempt, preserve the existing lock bytes, and call no `launchctl`. |
| M-B — detached handoff reaper | snippet `docs/process/MAGISTRATE_WATCHDOG.md:133-218`; execution test `tests/test_magistrate_watchdog.py:1424-1471` | The exact extracted heredoc begins `import os; os.setsid()`, executes against safe shadow dependencies, and reports `reaper_pid == reaper_session_id`. |
| H-2 — independent dead-watchdog detector | `scripts/run_night.py:619-664`; `tests/test_run_night.py:636-657`; `docs/process/NIGHT_HANDBACK.md:15-22` | The courier reads the plan-configured sibling `magistrate/state.json` directly, renders mtime age and last `state` into its email instruction, and labels >900 s/unavailable dead; no watchdog import exists. |
| B-A — landing precedes handoff | `docs/process/MAGISTRATE_WATCHDOG.md:92` | Checklist step 0 requires the twelve-row gate, integration replay/PR/CI/authorized merge, canonical `pull --ff-only`, then SHA-256 comparison of all five pinned files with packet exhibits before step 3. |
| S-A — round-9 licence | `24a-magistrate-ruling-delta-8-signature.md:3` | One-paragraph ruling quotes trace 24's delta-8 same-signature YES and trace 16's written-ruling/dissent basis, and points to trace 22's relocated installer surface. |

## RED and mutation evidence

Before the courier implementation and reaper amendment, the new focused run ended:

```text
FAIL: test_documented_reaper_executes_in_its_own_session
AssertionError: False is not true : the executable reaper must detach before importing project code
FAIL: test_courier_body_reads_watchdog_age_and_last_decision_directly
AssertionError: 'Watchdog state path: .../magistrate/state.json' not found in <courier prompt>
Ran 4 tests in 1.342s
FAILED (failures=3)
```

The third failure was a test-assertion adjustment needed once the new v1-labelled malformed sibling correctly named the retired schema in its error; it was not a production defect. The two classifier limbs were then mutation-tested independently against the real CLI entry point:

```text
M1 (remove schema-label conjunct):
FAIL: test_real_cli_consumes_production_plan_set_and_fails_closed
AssertionError: '<temp>/v2-label-v1-keys/night_plan.json' not found in <HOLD_UNSAFE reason>
Ran 1 test in 0.405s
FAILED (failures=1)

M9 (remove complete-required-keys conjunct):
FAIL: test_real_cli_consumes_production_plan_set_and_fails_closed
AssertionError: '<temp>/v1-label-subset/night_plan.json' not found in <HOLD_UNSAFE reason>
Ran 1 test in 0.402s
FAILED (failures=1)
```

Both mutations were restored; `scripts/magistrate_watchdog.py` has no final diff.

## GREEN — required six-module gate

Command:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog tests.test_magistrate_watchdog_cli tests.test_run_night tests.test_night_gate tests.test_install_night_agent tests.test_install_magistrate_watchdog
```

Tail, exit 0:

```text
...........................................................................................................................................................................................
----------------------------------------------------------------------
Ran 187 tests in 32.484s

OK
```

Only the six preflight-authorized modules were run. No broader discovery was attempted.
