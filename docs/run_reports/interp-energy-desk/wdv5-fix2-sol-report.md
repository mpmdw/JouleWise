Fixed N1, N2, and F1 on `ops/2026-11-10-watchdog-v5-installed`. Siblings and orphans still refuse; descendant and relative-path regressions pass.

Commits: `8555b1313` (fixes/tests), `939c684bb` (report). Working tree clean; no push.

Ran each module separately with `python3.13 -B -m unittest`:

| Module | Result |
|---|---|
| `tests.test_run_night` | 280 passed, 2 failed, 1 error, 9 skipped |
| `tests.test_post_window_unstrand` | 21 passed, 2 skipped |
| `tests.test_night_ac_powermode` | 6 passed |
| `tests.test_magistrate_watchdog_yield` | 17 passed, 3 failed |

N1’s registry test now passes. **Full native verification remains open:** `/bin/ps` is denied and `pgrep` cannot obtain the process list.

The [handoff report](/Volumes/JW-EXT/jw-wt/sol-wdv5-fix2/docs/run_reports/interp-energy-desk/2026-11-10-wdv5-fix2-sol.md) lists all four changed files, exact affected test IDs, failure attribution, and fixture-process uncertainty. Next step: rerun these modules outside the sandbox with native process visibility. Coordination state was untouched.