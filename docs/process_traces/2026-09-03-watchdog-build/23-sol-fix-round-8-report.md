# Sol implementation report — fix round 8

Date: 2026-09-04. Baseline Git HEAD: `1b51fecfdae7246015ed9d981636e21939d760fc`; final Git HEAD: `a15cc15e7773a2d4a593cd1ad8814a9595b83d82` on `feat/2026-09-03-magistrate-watchdog`. Contract: trace 22 clauses C-1 through C-8; C-9 excluded. All writes stayed in the runner-owned allowlist. No install, real `launchctl`, agent/session launch, default-custody access, LaunchAgent mutation, signal to a production process, or quiet-machine work occurred.

## RED — tests landed before implementation

The first run below was made after adding only the C-1/C-5 tests; `scripts/magistrate_watchdog.py` was unchanged from the baseline:

```text
$ python3 -m unittest tests.test_magistrate_watchdog.SupervisorTests.test_latched_drain_at_t0_minus_22_is_killed_by_t0_minus_15 tests.test_magistrate_watchdog.SupervisorTests.test_latched_drain_inside_kill_phase_kills_on_first_poll tests.test_magistrate_watchdog.SupervisorTests.test_future_sibling_hold_is_killed_by_valid_plan_deadline tests.test_magistrate_watchdog.SupervisorTests.test_unsafe_replacement_tick_in_term_phase_signals_term_immediately
FFFF
test_latched_drain_at_t0_minus_22_is_killed_by_t0_minus_15: AssertionError: True is not false
test_latched_drain_inside_kill_phase_kills_on_first_poll: AssertionError: True is not false
test_future_sibling_hold_is_killed_by_valid_plan_deadline: AssertionError: True is not false
test_unsafe_replacement_tick_in_term_phase_signals_term_immediately: expected SIGTERM; observed []
Ran 4 tests in 0.033s
FAILED (failures=4)
```

C-3 was independently red against the unchanged watchdog:

```text
$ python3 -m unittest tests.test_magistrate_watchdog.BackoffAndEventTests.test_foreign_boot_discards_persisted_backoff_and_records_event
F
AssertionError: 'LAUNCHING' != 'BACKOFF_USAGE'
Ran 1 test in 0.005s
FAILED (failures=1)
```

C-6/C-7 were red before either documentation example or the limitation text changed:

```text
$ python3 -m unittest tests.test_magistrate_watchdog.ContractTests.test_documented_example_plans_use_the_production_writer tests.test_magistrate_watchdog.ContractTests.test_launchagent_login_limit_and_dead_watchdog_threshold_are_explicit
FFF
AssertionError: False is not true : /Users/edr/JouleWise-measurement-20260813
AssertionError: False is not true : /Users/edr/JouleWise-measurement-20260813
AssertionError: 'does not load before GUI login' not found
Ran 2 tests in 0.010s
FAILED (failures=3)
```

For C-2/C-4/C-8, the new behavioral module was replayed against an exact `git archive HEAD` extraction of the unchanged installer. The temp shadow changes only the expected canonical path and `/bin/ps` executable so the sandbox can exercise the transaction; the installed script logic is baseline bytes:

```text
$ python3 -m unittest tests.test_install_magistrate_watchdog  # SCRIPT_PATH/TEMPLATE_PATH = git-archive HEAD extraction
FF.FFF
test_failed_lock_seed_removes_the_plist_written_by_this_attempt: AssertionError: True is not false
test_install_from_noncanonical_checkout_refuses_before_writing: AssertionError: 3 != 1
test_render_refuses_system_python_without_repository_dependencies: AssertionError: 3 != 0
test_rendered_plist_pins_canonical_checkout: AssertionError: '/Users/edr/code/JouleWise' != '/private/tmp/joulewise-round8-red.gOiGCF'
test_rendered_plist_pins_test_interpreter: AssertionError: '/opt/homebrew/opt/python@3.14/bin/python3.14' != '/usr/bin/env'
Ran 6 tests in 1.601s
FAILED (failures=5)
```

The noncanonical baseline reached its pre-fix ancestry probe and the managed sandbox denied `/bin/ps`; critically, it did not produce the required early `noncanonical_checkout` refusal. The shadowed success path separately reached the lock collision and left the plist behind, supplying C-4's defect-shaped RED.

## Implementation and clause map

| Clause | Production and documentation | Biting tests | Result |
|---|---|---|---|
| C-1 | `scripts/magistrate_watchdog.py:1596-1770` | `tests/test_magistrate_watchdog.py:690-783` | Every resident poll selects the earliest relevant parseable plan before any latched drain return; cooperative TERM/KILL thresholds are ORed with the plan phase, and the request records the plan deadlines. |
| C-2 | `scripts/install_magistrate_watchdog.sh:35-75,190-209`; `docs/process/MAGISTRATE_WATCHDOG.md:105-123` | `tests/test_install_magistrate_watchdog.py:132-186` | `--install` requires both the resolved script repo and `/usr/bin/git rev-parse --show-toplevel` to equal `/Users/edr/code/JouleWise`; rendered plist paths always use that literal. |
| C-3 | `scripts/magistrate_watchdog.py:472-492,504-508,1139-1186,1198,1258` | `tests/test_magistrate_watchdog.py:1041-1086` | Backoff records a wall epoch and boot identifier; a foreign or legacy boot identity clears both deadlines and emits `backoff_reset_after_reboot`. |
| C-4 | `scripts/install_magistrate_watchdog.sh:85-263` | `tests/test_install_magistrate_watchdog.py:188-218` | Real zsh subprocess tests use temp HOME, a stubbed process view and launchctl, parse plist bytes, inspect the exclusive lock, inspect launchctl argv, and prove failed lock seeding removes only the attempted plist. |
| C-5 | `scripts/magistrate_watchdog.py:1630-1659,1705-1757` | `tests/test_magistrate_watchdog.py:751-783` | An overdue replacement tick emits TERM and then immediate KILL on its first observed KILL-phase poll; thus the literal “TERM now” and already-passed KILL bound both hold. |
| C-6 | `docs/process/MAGISTRATE_WATCHDOG.md:61,76-77` | `tests/test_magistrate_watchdog.py:1395-1406` | The GUI-login limitation, accepted logged-in-week posture, 15-minute state-write threshold, and next-window courier report are explicit. |
| C-7 | `docs/process/MAGISTRATE_WATCHDOG.md:222,253,343` | `tests/test_magistrate_watchdog.py:1352-1393` | Both executable rehearsal examples use distinct, clearly fake `/private/tmp/...` measurement roots; the real-plan cleanup warning is explicit. Conflict semantics are unchanged. |
| C-8 | `scripts/install_magistrate_watchdog.sh:49-64,190-209` | `tests/test_install_magistrate_watchdog.py:147-176` | Install-time `sys.executable` becomes the single absolute plist interpreter; `/usr/bin/env python3` is absent from rendered bytes, and `/usr/bin/python3` is explicitly refused as dependency-incomplete. |

The relaunch prompt was not changed and remains 23 lines, below the 25-line ceiling.

## GREEN — clause-focused checks

```text
$ python3 -m unittest <the four C-1/C-5 SupervisorTests above>
....
Ran 4 tests in 0.030s
OK

$ python3 -m unittest tests.test_magistrate_watchdog.BackoffAndEventTests.test_foreign_boot_discards_persisted_backoff_and_records_event
.
Ran 1 test in 0.006s
OK

$ python3 -m unittest tests.test_magistrate_watchdog.ContractTests.test_documented_example_plans_use_the_production_writer tests.test_magistrate_watchdog.ContractTests.test_launchagent_login_limit_and_dead_watchdog_threshold_are_explicit
..
Ran 2 tests in 0.008s
OK

$ python3 -m unittest tests.test_install_magistrate_watchdog
......
Ran 6 tests in 1.817s
OK
```

## Required six-module tails

```text
$ python3 -m unittest tests.test_magistrate_watchdog
............................................................
Ran 60 tests in 0.316s
OK

$ python3 -m unittest tests.test_magistrate_watchdog_cli
...
Ran 3 tests in 10.850s
OK

$ python3 -m unittest tests.test_install_magistrate_watchdog
......
Ran 6 tests in 1.881s
OK

$ python3 -m unittest tests.test_night_gate
...............................................
Ran 47 tests in 0.095s
OK

$ python3 -m unittest tests.test_run_night
.......................................................
Ran 55 tests in 5.118s
OK

$ python3 -m unittest tests.test_install_night_agent
...........
Ran 11 tests in 3.423s
OK
```

No broader discovery was run because the runner's PREFLIGHT RULE exhaustively allowed only these six modules.
