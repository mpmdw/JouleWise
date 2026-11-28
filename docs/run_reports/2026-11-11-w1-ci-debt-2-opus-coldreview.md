# Cold review: `ops/2026-11-11-w1-ci-debt-2` @ `030dfcb99`

Opus 5.5, interim lane lead, 2026-11-11 07:40 PST, on the Air. Reviewed cold: the diff `4aebac1eb..f72327ab6` and the
cited production commits, not the seat's conclusions.

**Verdict: ADMIT.** Test-only; no bound file changed (`ARTIFACTS` membership checked for all three files: none bound).

## What changed and whether each change is a stale expectation

| Module | Change | Checked against |
|---|---|---|
| `tests.align.test_r1_round6_exec_review` | Dead-man test: fakes the network-time read (`NETWORK_TIME_QUERY_ARGV` -> `Network Time: Off`); log expectation `exit restore (dead_man)` -> `close: restore Automatic; network time left_off:`; now also asserts the `deadman_host_restoration-*.json` record. Module-level guard refuses `sudo`/`/usr/bin/sudo` through `subprocess.run` and fails the module on teardown even if the call was swallowed. | `19a862dc8` and `c6d25d963` are on the W1 line; `run_night._deadman_host_restore` calls `_close_ac_powermode` and writes `deadman_host_restoration-<ns>.json` (`scripts/run_night.py:5450-5494` at `4aebac1eb`). The assertion is strengthened, not loosened. |
| `tests.align.test_smoke_delta4_sol1/sol2` | `_probe_meter_live`'s `runner` default is now expected to be `None` (dispatch at call time); new assertion that a later call uses the CURRENT `subprocess.run`. | `454d78142` (on the line) made the default `None` (`scripts/align_v4_session.py:632`). Strengthened. |

## Tests run (Air, `python3.13 -B -m unittest`, one module at a time)

- `tests.align.test_r1_round6_exec_review`: 9 OK. `tests.align.test_smoke_delta4_sol1`: 12 OK.
  `tests.align.test_smoke_delta4_sol2`: 11 OK.

## Mutation checks

| Mutant | Expected | Result |
|---|---|---|
| Remove the network-time fake in the dead-man test | the `left_off` assertion fails (fixture default is `On`; no real sudo) | killed (1 failure) |
| Inject a swallowed `subprocess.run(["/usr/bin/sudo","-n","/usr/bin/true"])` (inside `try/except Exception`) | module fails on teardown naming the call; nothing executes | killed (`tearDownModule` error, `real sudo attempted`) |
| Production: `_probe_meter_live(..., runner=subprocess.run)` (captured at import) | both smoke-delta4 modules fail | killed (2 + 2 failures) |

## Notes, no action needed here

- The module guard covers `subprocess.run` with argv[0] `sudo` only. The suite-wide host-command guard
  (`ops/2026-11-11-w1-host-guard`) supersedes it; this guard can stay as a local belt.
- The seat's "lead-Mac sudo leak did not reproduce" is consistent with what I saw: `tests/test_run_night.py:122`
  supplies a fake `Network Time: On` read for this fixture. Provenance of the earlier leak is the host guard's job.
