Committed `dd54b137a` on `feat/2026-11-11-sm-air-watch`. Worktree clean; no push.

Added the watcher, 37 synthetic tests, and Air/launchd documentation. Updated CANONICAL, the timing entry, and the [run report](/Volumes/JW-EXT/jw-wt/sol-sm-air-watch/docs/run_reports/2026-11-11-sm-air-watch.md).

Verification passed:

- Watcher: 37 tests.
- Window state: 43 tests.
- Fixture census: 14 tests, two sandbox `ps` skips.
- State generation: 44 tests.
- Compilation and diff checks.

`WATCHDOG_STATUS` was skipped because its API is absent on main. Live authentication, launchd, notifications, and Python 3.11 remain unverified; optional integrations were fake-tested. Exact commands and results are in the report.

Next: cold review and an Air-side synthetic smoke check. Keep the scratch watcher until the current chain exits.