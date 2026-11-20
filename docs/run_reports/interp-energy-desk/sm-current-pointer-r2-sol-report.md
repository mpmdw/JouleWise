Committed locally as `8e614d69a` on `feat/2026-11-11-sm-current-pointer`. Working tree clean; nothing pushed.

- Replaced the manual pointer script/tests with `gen_current.py` and 46 tests.
- Generated the required no-pointer CURRENT.json and updated the pointer documentation.
- Restored WINDOW_STATUS.md unchanged because its publisher remains procedurally wired.
- Reverted the generated HTML hand edit.
- Required test modules passed; publisher guards, compileall, and 12 mutation checks passed.

Lead follow-up: integrate the hooks into `gen_state.py` using the exact edits in the [Round 2 report](/Volumes/JW-EXT/jw-wt/sol-sm-current-pointer-r2/docs/run_reports/2026-11-11-sm-current-pointer.md:93).

Live census verification remains **PROVISIONAL**: two tests skipped and the standalone census exited 2 because the sandbox denies `ps`. Python 3.11 remains untested locally. No unresolved implementation questions.