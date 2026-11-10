Committed `43b7e2521` on `ops/2026-11-10-watchdog-v5-installed`. Tree clean; not pushed.

Fixed D1’s descendant exemption, added all three refusal cases, and corrected L1’s temp-root, PWD and log handling. Changed the script, its tests and the [run report](/Volumes/JW-EXT/jw-wt/sol-wdv5-fix3/docs/run_reports/interp-energy-desk/2026-11-10-wdv5-fix3-sol.md).

All modules ran serially without `PYTHONNOUSERSITE`:

| Module | Result |
|---|---|
| `test_post_window_unstrand` | 22 passed, 2 skipped |
| `test_run_night` | 280 passed, 2 failures, 1 error, 9 skipped |
| `test_magistrate_watchdog_yield` | 17 passed, 3 failures |
| `test_night_ac_powermode` | 6 passed |

The symlinked-TMPDIR alias check also passed.

`/bin/ps` denial specifically blocked:

- `PostWindowUnstrandTests.test_native_ps_clean_completed_window_under_caffeinate`
- `PostWindowUnstrandTests.test_native_ps_clean_completed_window_under_wrapping_zsh`
- `HazardPackPrimitiveTests.test_dead_man_stops_the_hazard_monitor_a_dead_driver_left_running`

Unavailable `pgrep` explains the other five failures and nine skips; exact names and commands are in the report. Native verification remains open.

Next: inspect synthetic monitor PIDs **30995, 31122, 31248**—sandbox cleanup was denied—then rerun the four modules natively. No outstanding code questions.