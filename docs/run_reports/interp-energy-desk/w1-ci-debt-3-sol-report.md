Committed `276d02c02` on `ops/2026-11-11-w1-ci-debt-3`. Worktree clean; no push.

Items 1–3 were stale expectations. Changed two test modules, `configs/gates/physics_rows.json`, and the [run report](/Volumes/JW-EXT/jw-wt/sol-w1-ci-debt-3/docs/run_reports/2026-11-11-w1-ci-debt-3.md). No production code or bound files changed.

Each module reproduced red on the exact base, then passed:

- `tests.test_s0_blocked_enumeration`: 1 test.
- `tests.hazards.test_physics_coverage`: 7 tests, 1 skip; used a safe temporary inventory override.
- `tests.test_magistrate_watchdog_span`: 24 tests.
- `compileall` and diff checks passed. No full suite ran.

Battery changes remain parked. The report identifies phase consumers, both missing caller entries, introducing commits, and admission evidence. The research lead must rule on `topup_log` registration.

Fixture census remains unverified because the sandbox denied `ps`. Next: lead review, Linux CI, and census in an authorized environment.