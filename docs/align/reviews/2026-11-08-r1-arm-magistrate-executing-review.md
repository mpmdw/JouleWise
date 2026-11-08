# R1-ARM-1 executing review (magistrate activation 17ca7bed, Opus 5.5 reviewer run on the measurement Mac)

Target: `lane/2026-11-08-r1-arm` @ `0b54827da` (Sol 6.1 xhigh build, route (a): HAZARD_PACK window around the unchanged R1 chain). The reviewer ran on the Mac with live process-table access, wrote nothing in the repo, and kept its scratch files under `/tmp/jw-r1rev-tmp`. **VERDICT: ADMIT_WITH_FIXES** (no BLOCKER; fixes can wait). This is input to the item 220 agreement step. It does not authorize an arm.

## Executed
- `tests.align.test_r1_arm`, `test_v4_kit`, `test_r1_runtime`, `test_r1_rehearsal`: 226 tests, all passed, none skipped. The live `ps` census path was exercised in `test_r1_rehearsal`. `test_r1_arm` still uses fixture censuses.
- `tests.test_run_night`, 318 tests on both this head and base `e901eb2a4`: exactly the same single ERROR (`Ruling76DriverTests.test_observer_faults_do_not_change_success_or_failure_chain_rc`, mocked `SystemExit: 19`). It is pre-existing. The four census failures the sandboxed seat saw do not occur on the Mac.
- `prepare` with t0 two days out:
  - the plan parses as `joulewise.night_plan.v5` HAZARD_PACK, `ac_powermode` 0;
  - `window_max_s` 105,127 = 96,427 + 3,300 (`b5/plan.py:59`) + 2×(1,800 + 600) (`b5/chain.py:182,188`) + 600;
  - the chain sidecar matches the wrapper.
- The plists rendered (installer `--render-only`). The watchdog reader `_installed_agent_plans`/`plan_span_active` fences t0−180 s through completion, including t0+25 h and t0+29 h. The early daily dead-man fire stands down before completion (`run_night.py:5044`).
- The wrapper runs the unchanged R1 zsh. `NIGHT_DIR`, `MEASUREMENT_ROOT` and `PY` come from `run_night.py:704-729`.
- Clock hold at a 5,764 s span: max |rate| 0.6175 ppm, bound 1.441 ms at 0 ppm. Every recorded rate on disk lies between −0.00036 and +0.0011 ppm. A healthy clock cannot refuse.
- `--dry-arm` writes only under `<custody>/dry-arm/` and refused at the census with `night_refused_agent_present`, the live magistrate. That refusal is correct while an agent is alive.
- No new non-physical refusal. Bookend failures are flags (`r1.bookend_failed`). No dependency file differs from `9c40e4e5d`.

## Findings
- **MEDIUM** `r1_arm.py:23,30`: the ceiling includes the R6-2 retries plus one batch encounter, but no ruling-8 load redo (up to 2 per quiet segment, each up to 665 + 5,764 s). Unspent arm and bookend time probably covers about one redo. More redos reach the deadline: TERM restores Automatic; KILL 30 s later leaves the High Power marker for the next admission. This meets item 216's floor.
- **LOW** `r1_arm.py:57-62`: `clock.rate_above_budget` flags on every R1 arm (1.441 + 3.7 > 5 ms). It is a flag, but it is noise.
- **LOW** `r1_arm.py:180-182`: the bookends omit `--ledger`, so live D-109 rows land in the measurement checkout's `runs/calibration_observation_ledger.jsonl`.
- **LOW** runbook :67: the t0 formula leaves about 3 min between `prepare` and the installer cutoff, too little for the arm notice. Use t0 ≥ now + 15 min.
- **LOW** numbers: `CLOSE_S`/`HARVEST_S` are borrowed 600 s budgets with a citation, not derived from R1's teardown. Generous, so harmless.
- **LOW** runbook :130,152: `uninstall` passes `--python`, which the installer ignores.

## Item 202 (4) (magistrate)
The scheduled jobs measured in R0 re-runs 8-11 are all far below R1's ruling-8 redo bar (> 0.5 core for 60 consecutive samples):
- softwareupdated 0.25-0.29 core;
- trustkit 0.09;
- routined 0.05.

The known schedule should produce flags, not redos or a refusal. No lead notification is needed on that ground.
