Fixed all five failures in the three named test modules. Expectations were stale after `19a862dc8` and `454d78142`; no production defect was found.

- Strengthened dead-man checks to verify the restoration record.
- Added an explicit network-time fake and a guard against real sudo.
- Updated both smoke modules to verify the intentional `None` default and later runner isolation.

All six requested modules passed: **70 tests**. Diff checks passed. No bound files changed; full-suite and native checks were not run.

Local commits: `9a4a4c37d`, `f72327ab6`. Branch `ops/2026-11-11-w1-ci-debt-2` is clean; nothing pushed.

The lead-Mac sudo leak did not reproduce—the existing fixture supplies that response. Its provenance remains uncertain.

[Run report with commands, results, and handoff](/Volumes/JW-EXT/jw-wt/sol-w1-ci-debt-2/docs/run_reports/2026-11-11-w1-ci-debt-2.md). Next: lane-lead review/cherry-pick; native gates remain lead-owned.