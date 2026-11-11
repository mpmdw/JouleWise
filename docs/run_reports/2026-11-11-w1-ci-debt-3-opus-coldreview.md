# Cold review: `ops/2026-11-11-w1-ci-debt-3` @ `91988e4e0`

Opus 5.5, interim lane lead, 2026-11-11. Diff `7d2f50ba1..276d02c02`: two test modules and
`configs/gates/physics_rows.json` (unbound: checked against `ARTIFACTS`).

**Verdict: ADMIT.** Each change is a stale expectation of an admitted W1-line commit; no check is loosened.

| Module | Change | Checked |
|---|---|---|
| `tests.test_magistrate_watchdog_span` (2 tests) | `HOLD_UNSAFE` -> `HOLD_PLIST_UNREADABLE`; the drain test now expects the named safety notice | `21029737a` ("Port admitted watchdog onto W1", RL-29) is on the line; the tests now ALSO assert the state is in `wd.UNSAFE_STATES`, no launch, no spawn: strengthened |
| `tests.test_s0_blocked_enumeration` | `expected_failures == []` -> exactly the two admitted `@expectedFailure` witnesses | `0b2d4d9b2` (hoff witness, D8) and `0d998b6bc` (WP22 F3) are on the line and add exactly these decorators (`tests/align/test_hoff_delta_sol1.py:353`, `tests/align/test_v4_w1_synthetic.py:216`); exact identities keep any addition, removal or rename visible |
| `tests.hazards.test_physics_coverage` via `configs/gates/physics_rows.json` | site `run_night.prepare_result` -> `_run_night.prepare_result` | `scripts/run_night.py:4831` `def _run_night`, `:5295` nested `prepare_result` |

**PARKED for the research lead (unchanged here):** `tests.test_battery_float_sweep` (2 tests). The seat's reading,
which I checked: `battery_float.PHASES` has no production reader; `observe` records the phase without checking it;
the gates that read a recorded phase (`authenticate_pair`, `v5_qualification.battery_boundaries`, the v5 assembler
and abort check) accept only their fixed phase names, so a `topup_log` record can never enter them; the top-up
derivation (`v4_topup`) does not read `phase`. `topup_log` came with `f993b784f` (Opus cold MED-3); no amendment
registered it in `PHASES`. By reading, the registry is stale and no classification changes; registering it
touches `joulewise/battery_float.py` (bound) or the test's registry, which is the research lead's call.
