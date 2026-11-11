Committed locally as `e34988225` on `test/2026-11-11-w1-harvest-exec`. Working tree is clean; nothing pushed.

- All 18 synthetic W1 identities derived. Removing ordinal 5’s identity added `model.identity_underivable` to exactly that member.
- The full synthetic harvest still excluded 43 members and ended `HARVEST_FAULT` because its physics/scaffold evidence is incomplete.
- Changed only the new test module, one timing entry, and the [run report](/Volumes/JW-EXT/jw-wt/sol-w1-harvest-exec/docs/run_reports/2026-11-11-w1-harvest-exec.md).

Verification passed: 3 module tests, the expanded full-harvest negative control, fixture census (16 tests, 2 skipped), generated-state checks (44 tests), and compileall. Total unittest time: 16.23 minutes.

The report contains all exclusions, identity provenance, exact commands, and the 19-code table: **9 MATTERS, 9 DOES-NOT-MATTER, 1 UNSURE**. Lead confirmation of `precheck.certain_exclusion` and native smoke remain open.