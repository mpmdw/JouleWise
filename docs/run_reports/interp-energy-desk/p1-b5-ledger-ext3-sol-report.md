Committed F1–F4 fixes locally; one validation ruling remains.

- `60f66800f`: fixes and new print authority.
- `52c43499c`: records the authority SHA and handoff.
- Changed REDERIVATION, three checkers, the fill checker, existing tests, and [run report](/Volumes/JW-EXT/jw-wt/sol-p1-b5-ledger-ext3/docs/run_reports/2026-11-11-p1-b5-ledger-ext.md:385).
- Requested unittest module: **48 passed**. All five B5 checkers with `--repo-only`: **passed**. `git diff --check`: **passed**.
- All 1,419 ledger-value and 111 cited-paper-value perturbations were rejected.
- Ledger, paper, and coordination files unchanged. Tree clean; no network, custody access, or push.

**NEEDS_RULING:** The base predates the first paper fill. The fill checker passes against the pinned admitted first-fill fixture, but its default invocation retains **123 existing paper failures**.

May I add `--paper-ref` to validate that pinned first fill (**recommended**), or bring the existing first fill into this branch? A passing standalone fill-check invocation remains blocked on this choice.