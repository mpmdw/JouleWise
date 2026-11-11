Committed `5dc2d4b48` on `align/2026-11-10-meter-outage-rl37`. Clean worktree; no push.

- Meter silence at 600 s now flags once and records `fault: true`; collection continues.
- Hazard stop and t0 probe remain unchanged.
- Added restart/coverage tests, the deviation row, and regenerated trace.

Targeted checks passed: reliability 19, meter 25, closures 4+10, restart 1; trace generator reported 418 tests across nine successful scenarios.

[Run report with every changed file and test command](/Volumes/JW-EXT/jw-wt/sol-meter-outage-rl37/docs/run_reports/2026-11-10-meter-outage-rl37.md).

Native checks, delta review, and STRICT re-registration remain lead-owned. Fixture census was unavailable because sandbox `ps` is denied; full suite was not run.