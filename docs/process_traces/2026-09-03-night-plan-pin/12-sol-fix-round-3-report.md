# Night plan pin — Sol fix round 3 report

Date: 2026-09-04 PDT  
Branch: `feat/2026-09-03-night-plan-pin`  
Requested and observed HEAD: `906981507e053caffc3b6bcf35a35714cd0e7ac7`  
Authority: Fable fix-round-3 brief; exhaustive `WRITE_SCOPE` observed.

## Outcome

The authorized implementation is complete. The install-only raw-plan block now
uses `NightPlan.from_mapping`, `PlanError`, and the gate-owned
`PLAN_MAX_AGE_S` constant to refuse a plan authored in the future as
`night_plan_malformed` and a plan older than the gate's 36-hour limit as
`night_plan_stale`. Both checks run before either Git HEAD probe. Refusals print
the named reason and exit 3. Uninstall continues to bypass plan validation.

The successful install path now prints all validated pins: `repo_head`,
`measurement_root`, and `measurement_head`. The render-only positive regression
asserts those values and both rendered plists. New defect-shaped regressions
cover authored minus 40 hours and authored plus 2 hours.

## Verification

Baseline at the requested head, before edits:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_install_night_agent tests.test_night_gate tests.test_run_night
...............................................................................................................
----------------------------------------------------------------------
Ran 111 tests in 24.572s

OK
```

Focused installer module after implementation:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_install_night_agent
...........
----------------------------------------------------------------------
Ran 11 tests in 9.591s

OK
```

The three acceptance regressions after restoring the mutation:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_install_night_agent.InstallNightAgentTests.test_install_refuses_plan_authored_40_hours_ago_as_stale tests.test_install_night_agent.InstallNightAgentTests.test_install_refuses_plan_authored_2_hours_in_future_as_malformed tests.test_install_night_agent.InstallNightAgentTests.test_install_with_both_pins_matching_renders_both_plists
...
----------------------------------------------------------------------
Ran 3 tests in 2.376s

OK
```

`zsh -n scripts/install_night_agent.sh` and `git diff --check` both exited 0
with empty output. The restored installer SHA-256 is
`d5625ddd1f6ff926b9d991653a3e68aef055bbfb0b9dc0be1d5ffd4511683f9e`.

## Mutation proof

The executed mutation removed only the stale-age comparison and its
`night_plan_stale` raise from the installer's Python block. Command:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_install_night_agent.InstallNightAgentTests.test_install_refuses_plan_authored_40_hours_ago_as_stale
```

Observed failing tail:

```text
FAIL: test_install_refuses_plan_authored_40_hours_ago_as_stale (tests.test_install_night_agent.InstallNightAgentTests.test_install_refuses_plan_authored_40_hours_ago_as_stale)
----------------------------------------------------------------------
Traceback (most recent call last):
  File "/Users/edr/code/JouleWise-wt-planpin/tests/test_install_night_agent.py", line 135, in test_install_refuses_plan_authored_40_hours_ago_as_stale
    self.assertEqual(3, completed.returncode)
AssertionError: 3 != 0

----------------------------------------------------------------------
Ran 1 test in 1.445s

FAILED (failures=1)
```

The mutation was removed with `apply_patch`; the restored acceptance tests pass
as recorded above.

## Scope blocker

The final allowed three-module command is not green because seven installer
flow tests in `tests/test_run_night.py` derive install plans from the suite's
fixed 2026-09-02 gate time. The new cold gate correctly rejects those plans as
stale before their intended courier, dead-man-hour, custody-record, render, or
rollback assertions:

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_install_night_agent tests.test_night_gate tests.test_run_night
..........................................................................................FFFFFFF................
----------------------------------------------------------------------
Ran 113 tests in 17.719s

FAILED (failures=7)
```

Every failure received `night_plan_stale: plan is older than 36 hours`; the
affected tests expected their downstream condition (`result.json`,
`courier.sent`, `chain.started`, dead-man hour, courier lookup, or successful
render). The minimal repair is one line in
`NightDriverTests._installer_plan`: set the copied install plan's
`authored_epoch_s` to `time.time()` before writing it. `time` is already
imported. `tests/test_run_night.py` is outside this session's exhaustive write
scope, so it was not modified and the final suite cannot be claimed green.

## Scope and workspace

No commit, staging operation, LaunchAgent write, `~/night-custody` write,
quiet-machine measurement, or cross-model hop was performed. No out-of-scope
path was modified.
