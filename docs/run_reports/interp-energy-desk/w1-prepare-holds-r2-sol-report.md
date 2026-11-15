Implemented on `ops/2026-11-11-w1-prepare-holds-r2`. Clean worktree; no push.

- Checks every earlier final window and requires a ruling for each held window.
- Authenticates committed ruling files and records their digest, fields, and capped text.
- Updated PREQUAL, two test files, and the [Round 2 report](/Volumes/JW-EXT/jw-wt/sol-w1-prepare-holds-r2/docs/run_reports/2026-11-11-w1-prepare-holds.md:351).

Passed: 76 arm tests, 36 closure/registration tests, PREQUAL, and three final ruling tests. Broader regression attempts left **two failing modules and 43 timed-out modules**. Total test time: **19.833 minutes**. Exact commands and diagnostics are in the report.

Commits: `081f7f457`, `7d472758a`, `b898d5db0`.

No research ruling question remains. Next: lead review, finish incomplete regressions, and run native qualification.