Committed `6b8442d85` on `feat/2026-11-11-sm-window-state`. Applied F-1–F-7; only the module, its tests, and the [Round 2 report](/Volumes/JW-EXT/jw-wt/sol-sm-window-state-r2/docs/run_reports/2026-11-11-sm-window-state.md) changed. Working tree clean; nothing pushed.

Verification:

- Window-state module: 43 tests passed.
- Mutation pass: 160/160 killed; no survivors.
- Fixture census: 14 tests, two existing sandbox skips.
- State generation: 44 tests passed.
- Compilation and diff checks passed.

No blocking questions. Native `/var/folders` and Python 3.11 verification remain for the lead: this sandbox’s `/var/folders` setting fell back to `/tmp`. Exact commands, results, and uncertainty about possible overlap of two early test invocations are documented in the report.