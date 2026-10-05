# PR #474 gates (G2-b unattended one-block stop), desk-day v5 seat

- Seat rounds: [24-sol-g2bstop-report-r1.md](24-sol-g2bstop-report-r1.md), [33-sol-g2bstop-report-r2.md](33-sol-g2bstop-report-r2.md), [43-sol-g2bstop-report-r3.md](43-sol-g2bstop-report-r3.md).
- Executing review (Sol 6.1 xhigh, non-author) at 278a719c: [36-sol-g2bstop-review.md](36-sol-g2bstop-review.md), FAIL. R1 (a bounded run silently ignored `--max-failures`): **fixed** in 0636046c (a block limit refuses any failure budget other than 1; stopping at the first failure is intended, D-078 / Q3 fence). R2 (the shared `run_stage` helper in the G2-a region changed): **rejected**, the explicit `|| return $?` keeps G2-a behaviour under its `set -e` and lets G2-b capture rc 3.
- First cold Fable pass at 0636046c: [39-fable-g2bstop.md](39-fable-g2bstop.md), **FAIL**, F1 MAJOR (the authenticated binding bounded every contrast stage, claim chain included). **Fixed** in ffc18054 with Fable's cure (a): only `purpose = G2B_SHAKEDOWN` runs with `--max-blocks` are bounded; other authenticated paths byte-identical to main (golden test). F2, F3, F6 **fixed**; F4 **deferred** to the qualification block's desk proof (mock-runner rehearsal of the real GAMMA first stage with the production policy); F5 **rejected** (unreachable). The seat's pytest wrote `.pytest_cache` outside its scope: accepted and removed (gitignored, no tracked byte).
- Second cold Fable pass at ffc18054: [47-fable-g2bstop-2.md](47-fable-g2bstop-2.md), **PASS** (F1 cured). N1 (three extra authenticated reads before the purpose test; fail-closed) and N3: **deferred** to lane `V5-FLOOR-HARDENING-01` (`_v5` hardening). N2 (an unrelated cooldown-provenance test in `tests/test_run_campaign.py` narrowed to two plain members for its 60 s deadline): **recorded** here; restoring the strict-analysis variant is deferred to lane `TEST-LOCAL-ENV-ISOLATION-01`.
- Whole suite at ffc18054 (current main merged in), CI shard method, local venv:
  - SHARD SUMMARY index=1/6 modules=1 tests=73 failures=0 errors=0 skipped=1 result=PASS
  - SHARD SUMMARY index=2/6 modules=54 tests=1325 failures=3 errors=0 skipped=18 result=FAIL
  - SHARD SUMMARY index=3/6 modules=56 tests=1408 failures=11 errors=0 skipped=4 result=FAIL
  - SHARD SUMMARY index=4/6 modules=55 tests=1554 failures=0 errors=0 skipped=12 result=PASS
  - SHARD SUMMARY index=5/6 modules=57 tests=1220 failures=3 errors=0 skipped=7 result=FAIL
  - SHARD SUMMARY index=6/6 modules=57 tests=1929 failures=38 errors=0 skipped=1 result=FAIL
  - exclusive: test_calibration_exits FAILED (errors=2); test_calibration_writer_crash_matrix OK
  Compared with base 8fa002f7 (67 known local-environment failures): extras only in `test_run_night` (3, the supervision timing family that fails at base under load; this change does not touch the night driver); `test_calibration_exits` errors at base. None attributable to this diff.
