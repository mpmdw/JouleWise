Committed locally on `perf/2026-11-08-eng-ci`; tree clean. Commits: `14b16ff79`, `ba05d3c14`, `eaf3143f7`. Nothing pushed.

- Merged `origin/main`, fixed missing timing declarations and clone-maintenance ordering, and preserved active CI coverage.
- Added a separate BYTES three-world patch with synthetic aggregate equality checks. BYTES remains absent from main.
- All 90 targeted tests, compilation, and diff checks pass. Full suite and native BYTES validation were not run.

**PR #685 remains gated:** the saved PR body fails gate-ledger validation; the actual hosted failure is unconfirmed offline. The 56.3-minute shard target remains a projection.

[Engineering report, timings, and shard map](/Users/edr/code/CapstoneProject/jw-wt/sol-eng-ci/docs/perf/2026-11-08-eng-ci.md) · [Changed files, test commands, and remaining steps](/Users/edr/code/CapstoneProject/jw-wt/sol-eng-ci/docs/run_reports/2026-11-08-eng-ci.md)