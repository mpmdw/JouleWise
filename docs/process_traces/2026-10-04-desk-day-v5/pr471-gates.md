# PR #471 gates (G2-a prompt-pin issuer, seal record 52 obligation), desk-day v5 seat

- Seat rounds: [10-sol-issuer-report-r1.md](10-sol-issuer-report-r1.md) (rulings F1: the end-state pin keeps D-166's static `exhausted_ladder_branch` declaration, authority is the closed end-state record; F2: scope added for the desk-chain integration test), [18-sol-issuer-report-r2.md](18-sol-issuer-report-r2.md), [22-sol-issuer-report-r3.md](22-sol-issuer-report-r3.md).
- Executing review (Sol 6.1 xhigh, non-author) at a1126009: [19-sol-issuer-review.md](19-sol-issuer-review.md), FAIL. F1 MAJOR (block-3 provenance from editable declarations): **fixed** in c783f0ee by anchoring `harvest.json` and selection bytes to the records committed under `docs/process_traces/2026-10-03-design-block3/windows/<plan_id>/`, the archive's `SHA256SUMS` and `outputs`, and the frozen plan's block-3 policy; coordinated multi-file forgery beyond that is outside the threat model (D-161). F2 MAJOR (permitted validity-filtered SELECT refused): **fixed** in c783f0ee.
- Delta check (Sol 6.1 high) at c783f0ee: [25-sol-issuer-delta.md](25-sol-issuer-delta.md), PASS.
- Cold Fable final pass at c783f0ee: [26-fable-issuer.md](26-fable-issuer.md), PASS, no BLOCKER/MAJOR. MINOR-2 (anchor is the checkout's HEAD): **fixed by procedure**, the pin is issued only from a detached checkout of origin/main after this merges. MINOR-1, MINOR-3, MINOR-4, MINOR-5, NIT-1..5: **deferred** to lane `G2A-ISSUER-HARDENING-01`; none affects the pin issued from the block-3 SELECT record (Fable reproduced it from the archive and committed records and closed MINOR-3 by hand for this record).
- Whole suite at c783f0ee (main 8fa002f7 + this branch), CI shard method, local venv:
  - SHARD SUMMARY index=1/6 modules=1 tests=73 failures=0 errors=0 skipped=1 result=PASS
  - SHARD SUMMARY index=2/6 modules=55 tests=1420 failures=0 errors=0 skipped=3 result=PASS
  - SHARD SUMMARY index=3/6 modules=55 tests=1465 failures=9 errors=2 skipped=20 result=FAIL
  - SHARD SUMMARY index=4/6 modules=55 tests=1665 failures=3 errors=0 skipped=4 result=FAIL
  - SHARD SUMMARY index=5/6 modules=56 tests=1075 failures=4 errors=0 skipped=11 result=FAIL
  - SHARD SUMMARY index=6/6 modules=57 tests=1768 failures=57 errors=0 skipped=4 result=FAIL
  - exclusive: test_calibration_exits FAILED (errors=5); test_calibration_writer_crash_matrix OK
  Compared with base 8fa002f7: base failures are the known local-environment set (67). Fourteen more appeared under 4-suite load, the same set as on PR #470's unrelated diff; their modules (`test_calibration_ledger_custody`, `test_magistrate_watchdog_cli`, `test_mint_floor_artifact_generalized`) pass serially at c783f0ee (151 tests OK); `test_calibration_exits` and the `test_run_night` timing case also fail at base. None is attributable to this diff. Hosted CI (whole suite, Linux) green on c783f0ee.
