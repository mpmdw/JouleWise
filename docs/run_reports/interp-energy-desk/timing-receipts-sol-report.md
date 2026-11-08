Committed locally on `perf/2026-11-08-timing-receipts`:

- `3c9c47a4e` — boundary hooks, offline reader projection and tests.
- `0db040044` — handoff report. Tree clean; no push.

Verification passed: full W1 regression (20 tests, one existing expected failure), full receipt comparison (12 tests), and final focused receipt suite (14 tests). Synthetic capture bytes matched after removing only marker lines; no-fsync checks passed.

**Not registration-ready:** R16’s evaluator is absent, and external desk boundaries remain unwired. Please supply its code/ref. Native MLX verification remains pending; an existing arm test hit the sandbox’s process-census restriction.

[Report with all 13 changed files, exact commands and blockers](/Users/edr/code/CapstoneProject/jw-wt/sol-timing-receipts/docs/run_reports/2026-11-08-timing-receipts.md) · [Implementation note](/Users/edr/code/CapstoneProject/jw-wt/sol-timing-receipts/docs/perf/TIMING-RECEIPTS-IMPL.md)