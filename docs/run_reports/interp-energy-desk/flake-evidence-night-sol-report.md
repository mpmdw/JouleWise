Committed `e094ba445` on `fix/2026-11-11-evidence-night-flake`. Working tree clean; no push.

Root cause: fetch detached Git maintenance/GC, which wrote after the builder error. Fixed with `--no-auto-maintenance`; added regression tracing, a stress harness, contract notes and the [run report](/Volumes/JW-EXT/jw-wt/sol-flake-evidence-night/docs/run_reports/2026-11-11-evidence-night-flake.md).

Verification:

- `tests.test_evidence_night`: 168 passed before and after.
- Controlled stress: 20/20 failed before; 200/200 passed after.
- Syntax and diff checks passed.

The original Ubuntu `ENOTEMPTY` wasn’t directly reproduced; post-return Git writes were confirmed. Next: hosted CI confirmation.