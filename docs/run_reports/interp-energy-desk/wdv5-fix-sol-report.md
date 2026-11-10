Fixed F1–F5 on `ops/2026-11-10-watchdog-v5-installed`.

- `2181b000e` — fixes, tests, and refusal-routing docs.
- `c9b10b30a` — verification report.

Recovery now excludes the full ancestor chain and matches custody aliases and inner chains. Driver/installer admission refuses power mode `2`; parsing remains compatible.

Verification: **453 passed, 3 failed, 1 skipped** across 457 targeted tests. Syntax, AST, and diff checks passed.

Native process visibility blocked these tests:

- `test_magistrate_watchdog_yield.DriverRecordsToWatchdogTests.test_a_chain_stop_is_released_on_the_driver_records`
- `test_magistrate_watchdog_yield.DriverRecordsToWatchdogTests.test_a_live_process_naming_the_custody_holds_the_release`
- `test_magistrate_watchdog_yield.DriverRecordsToWatchdogTests.test_an_empty_window_alerts_ed_in_window_and_is_released_after_delivery`
- `test_post_window_unstrand.PostWindowUnstrandTests.test_native_ps_clean_completed_window_under_wrapping_zsh` — skipped.

The three failures reproduce with the original driver. `/bin/ps` is denied; `pgrep` cannot obtain the process list. Next: rerun those two modules outside the sandbox.

[Report with changed files, commands, results, and limitations](/Volumes/JW-EXT/jw-wt/sol-wdv5-fix/docs/run_reports/interp-energy-desk/wdv5-installed-fix-2026-11-10.md).

Working tree clean. No push; coordination state untouched.