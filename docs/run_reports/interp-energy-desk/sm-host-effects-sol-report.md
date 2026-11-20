Committed `c407decd0` on `feat/2026-11-11-sm-host-effects`. Working tree is clean; nothing pushed.

Added the shadow reader/CLI and tests. Updated `CANONICAL.md`, the timing map, and the [run report](/Volumes/JW-EXT/jw-wt/sol-sm-host-effects/docs/run_reports/2026-11-11-sm-host-effects.md).

Checks passed:

- Host-effects unittest module: 30 tests.
- Fixture census: 14 tests, 2 skips.
- State validation: 44 tests.
- Compileall and diff checks.
- Ten selected local mutations caught.

No blockers. Python 3.11 and live-host validation were not executed. The audit’s network-time invariant remains advisory where operational instructions deliberately keep time OFF. Next step: lead cold review.