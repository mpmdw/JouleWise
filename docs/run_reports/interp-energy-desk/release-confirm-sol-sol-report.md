**HOLD.** F2 remains partially open: omitted U4/U6 output and matching undefined-H* omissions can still produce AGREE. Other prior findings are closed in tested paths.

- Added the [report](/Volumes/JW-EXT/jw-wt/sol-release-confirm-sol/docs/analysis/v4/RELEASE-CONFIRM-sol.md) and [synthetic witnesses](/Volumes/JW-EXT/jw-wt/sol-release-confirm-sol/tests/v4_release/test_confirm_sol.py).
- 73 targeted Python 3.13 tests passed; omission witnesses reproduce the blocker. Total test time was about nine minutes.
- Committed `90a9e85f3` on `align/2026-11-08-release-confirm-sol`. Tree clean; nothing pushed.

Next: fix independent completeness checks and convert witnesses to rejection regressions. Evidence is synthetic; actual producer omissions remain unproven.