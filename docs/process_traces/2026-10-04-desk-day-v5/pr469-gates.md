# PR #469 gates (G2A-ATTACH-GUARD-TESTS-01 + #467 Fable N3/N5), desk-day v5 seat

- Seat: [11-sol-guard-tests-report.md](11-sol-guard-tests-report.md) (N3, N5 added; N5 mutation kill shown).
- Executing review (Sol 6.1 high, non-author) at 93b84dae: [14-sol-guardtests-review.md](14-sol-guardtests-review.md), FAIL. R1 MAJOR (the F6 cleanup in `scripts/recover_calibration_ledger.py` could unlink a writer-lease lock inode another writer holds; contract `docs/contracts/calibration_ledger_append.md`: the inode is never deleted): **fixed** in 7f7cbec6 by dropping the unlink; the lock stays in the archive. G1 (requested recovery module path absent): no change, recovery tests live in `tests/test_calibration_ledger.py` and passed. G2 (N3 mocks acceptance authentication and strict member validation): **accepted**, N3 is the conditional bracket-decision regression Fable N3 asked for. 19/19 mutants killed.
- Hosted CI shard 3 error in N3 (Linux): cause = 190 external D-079 import custody artifacts absent on CI ([28-sol-n3-ci-report.md](28-sol-n3-ci-report.md)); **fixed** in fa0c8fe6 with the file's existing custody skip reason and a verdict assertion before reading `bracket.json`.
- Fable final pass: N/A. After 7f7cbec6 the only non-test change is a docstring in `joulewise/controller.py` (reviewer: executable AST unchanged).
- Whole suite at fa0c8fe6 (main 8fa002f7 merged in as eb0c3926), CI shard method, local venv:
  - SHARD SUMMARY index=1/6 modules=1 tests=73 failures=0 errors=0 skipped=1 result=PASS
  - SHARD SUMMARY index=2/6 modules=55 tests=1420 failures=0 errors=0 skipped=3 result=PASS
  - SHARD SUMMARY index=3/6 modules=55 tests=1471 failures=8 errors=4 skipped=20 result=FAIL
  - SHARD SUMMARY index=4/6 modules=55 tests=1665 failures=3 errors=0 skipped=4 result=FAIL
  - SHARD SUMMARY index=5/6 modules=56 tests=1056 failures=3 errors=0 skipped=11 result=FAIL
  - SHARD SUMMARY index=6/6 modules=57 tests=1772 failures=50 errors=0 skipped=4 result=FAIL
  - exclusive: test_calibration_exits FAILED (errors=4); test_calibration_writer_crash_matrix OK
  Compared with base 8fa002f7 (67 known local-environment failures): the extra failures under 5-suite load are in `test_calibration_ledger_custody` and `test_collector_analysis_manifest_id`, which pass serially at fa0c8fe6 (78 tests OK), and `test_calibration_exits`, which errors at base too. None is attributable to this diff.
