A, B and D hold. C’s immediate-successor rule holds, but its stated diagnostic differs: C3’s misplaced `previous_final` fails binding before R17.

- **A:** Replay lowers C1’s count exactly. A stale pool fails the roster check first; a corrected ledger commit repairs it.
- **B:** Raising counts above the desk ceiling refuses at series binding.
- **D:** Re-issued tail C2 plus an updated ledger passes. No deadlock found in this tested case.

Changed only the [new test module](/Volumes/JW-EXT/jw-wt/sol-w1-finality-tests/tests/align/test_v4_finality_paths.py), one timing-map line, and the [run report](/Volumes/JW-EXT/jw-wt/sol-w1-finality-tests/docs/run_reports/2026-11-11-w1-finality-tests.md). The report contains exact commands, results, test names and deciding code lines.

Verification: 6 new tests, 12 existing finality tests and 44 state-generator tests pass; compilation passes. The unchanged orphan-census test fails with 1 failure and 2 subtest errors; 2 tests skip.

Local commits: `b83bc97a4` and `8bf180882`. Branch `test/2026-11-11-w1-finality-tests` is clean; nothing pushed.

Next: lead review, runbook correction and disposition of the census failure. Evidence is synthetic; repair after C3 already exists remains untested.