Committed `ba87e1cd4` on `feat/2026-11-11-sm-window-state`. Working tree is clean; nothing pushed.

Built the shadow lifecycle, outcome classifier, invariants, safe observer, CLI, and synthetic tests. Only five authorized files changed, including the single timing line and tool-map row.

Verification:

- `tests.test_window_state`: 32 passed.
- `tests.test_fixture_orphan_census`: 14 run, two sandbox skips.
- `tests.test_gen_state`: 44 passed.
- Compilation and diff checks passed.

Python 3.11 was unavailable on PATH. Installation states require caller-supplied plist facts; no live hardware validation is claimed. No blocking questions.

Next: lead runs Python 3.11 tests and cold review. Details: [run report](/Volumes/JW-EXT/jw-wt/sol-sm-window-state/docs/run_reports/2026-11-11-sm-window-state.md).