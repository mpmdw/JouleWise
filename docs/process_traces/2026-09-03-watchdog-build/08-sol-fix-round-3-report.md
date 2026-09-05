# Magistrate watchdog — Sol fix round 3

Date: 2026-09-04 PDT
Base/HEAD at intake: `953a1645abcb33b9b873bfeded1ee1b386146994`
Branch: `feat/2026-09-03-magistrate-watchdog`
Install/session/commit actions: none.

## Finding → cure → evidence

| Finding | Cure | Biting evidence |
|---|---|---|
| Row 4's resident `<=10 s` guarantee survived poll mutations to 60 and 600 seconds | Added an exact `SUPERVISOR_POLL_S == 10` assertion. Added a fake-clock test that runs the real resident loop from the exact TERM boundary and requires the signal-event timestamps to place KILL exactly `STOP_TERM_GRACE_S` (60 seconds) after TERM. The production literal was already 10, so no source edit was needed. | With poll 60 the literal test fails. With poll 600 both the literal test and deadline-hit test fail, the latter reporting `600.0 != 60`. The unmutated suite passes. |
| The relaunch prompt fenced only the development checkout while a plan was armed | Added an explicit plan-schema-v2 fence for `/Users/edr/JouleWise-measurement-20260813`: no fast-forward, pull, checkout, or other HEAD movement while armed; a post-arm fast-forward requires re-arm with a re-pinned plan. | The prompt contract test pins the path, forbidden operations, and re-arm consequence. The prompt is 23 lines. |
| The prompt omitted rule 11's authority boundary | Barred the relaunched session from ratifying or amending process rules, decision-log entries, or skill doctrine, routing those decisions to the cold gate or Ed. | The prompt contract test pins both the prohibition and authority destination. |
| The prompt omitted R-9 clause 3's session-exit obligation | Added one line stating that arming obligates the session to end its loop and exit by the request deadline, after which the LaunchAgent is the wake source. | The prompt contract test pins the obligation text. |

`MAGISTRATE_WATCHDOG.md` now carries the same measurement-checkout fence, re-pin consequence, armed-night exit obligation, and rule-11 authority boundary in its complete-write-inventory discussion, and cross-references the two-checkout fence in the install handoff.

## Clause-map delta

| Adopted proposition | Production site | Biting assertion | Counterfactual |
|---|---|---|---|
| File-15 row 4 — resident resolution is at most 10 seconds and the TERM→KILL interval is 60 seconds | `scripts/magistrate_watchdog.py:68`, `scripts/magistrate_watchdog.py:1219-1226` | `tests/test_magistrate_watchdog.py:297`; `tests/test_magistrate_watchdog.py:300` | Set `SUPERVISOR_POLL_S = 60`: the literal pin fails. Set it to 600: the deadline test observes a 600-second signal gap instead of 60. |
| Plan-schema-v2 armed-plan pin protects the measurement checkout | `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md:10` | `tests/test_magistrate_watchdog.py:671-673` | Delete the measurement-checkout fence: the path/operation/re-arm assertions fail. |
| R-9 clause 3 — an arming session ends its loop and exits by the request deadline | `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md:12` | `tests/test_magistrate_watchdog.py:676` | Delete the arming obligation: the prompt assertion fails. |
| Rule 11 — the relaunched session cannot ratify or amend process doctrine | `docs/process/MAGISTRATE_RELAUNCH_PROMPT.md:20` | `tests/test_magistrate_watchdog.py:674-675` | Delete the authority fence: the prohibition/destination assertions fail. |

## Focused verification

Per the runner preflight rule, no test module other than `tests.test_magistrate_watchdog` was run.

Preflight command, before edits:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog
```

Exit 0 tail:

```text
....................................
----------------------------------------------------------------------
Ran 36 tests in 0.170s

OK
```

Final command:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_magistrate_watchdog
```

Exit 0 tail:

```text
......................................
----------------------------------------------------------------------
Ran 38 tests in 0.178s

OK
```

## Mutation results

Both mutations were applied in memory before loading the focused suite; no production file was changed by either probe.

Poll 60 command:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -c 'import unittest; from scripts import magistrate_watchdog as wd; wd.SUPERVISOR_POLL_S = 60; suite = unittest.defaultTestLoader.loadTestsFromName("tests.test_magistrate_watchdog"); result = unittest.TextTestRunner().run(suite); raise SystemExit(not result.wasSuccessful())'
```

Expected exit 1 result:

```text
FAIL: test_supervisor_poll_is_exactly_ten_seconds (tests.test_magistrate_watchdog.SupervisorTests.test_supervisor_poll_is_exactly_ten_seconds)
AssertionError: 60 != 10
----------------------------------------------------------------------
Ran 38 tests in 0.185s

FAILED (failures=1)
```

Poll 600 command:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -c 'import unittest; from scripts import magistrate_watchdog as wd; wd.SUPERVISOR_POLL_S = 600; suite = unittest.defaultTestLoader.loadTestsFromName("tests.test_magistrate_watchdog"); result = unittest.TextTestRunner().run(suite); raise SystemExit(not result.wasSuccessful())'
```

Expected exit 1 result:

```text
FAIL: test_resident_loop_hits_term_to_kill_deadline (tests.test_magistrate_watchdog.SupervisorTests.test_resident_loop_hits_term_to_kill_deadline)
AssertionError: 600.0 != 60
FAIL: test_supervisor_poll_is_exactly_ten_seconds (tests.test_magistrate_watchdog.SupervisorTests.test_supervisor_poll_is_exactly_ten_seconds)
AssertionError: 600 != 10
----------------------------------------------------------------------
Ran 38 tests in 0.182s

FAILED (failures=2)
```

## Scope and residual gates

Only runner-authorized paths were modified. No commit was created, no package was installed, and no Claude or Codex session was started. This implementation seat performed no install, launchd, live-night, or quiet-machine action. Final cold-gate adjudication and any installation remain lead-owned.
