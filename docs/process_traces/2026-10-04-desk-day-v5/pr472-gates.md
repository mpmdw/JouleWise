# PR #472 gates (`_v5` floors at the pin's prefill length), desk-day v5 seat

- Seat rounds: [16-sol-floors-report-r1.md](16-sol-floors-report-r1.md); orchestrator rulings in [20-sol-floors-r2-brief.md](20-sol-floors-r2-brief.md) (F1 ladder-specific `prefill-p<L>` reported cells, historical p512 unchanged, one length per family; F2 test fixtures; F6 end-state 4096 authority; the round-1 whole-window × L/512 span projection rejected for a component estimate); [20-sol-floors-report-r2.md](20-sol-floors-report-r2.md). Lead applied the seat's `configs/paper_supply/supply_map.json` repin (two `test_fixture_non_issuing` digests only).
- Executing review (Sol 6.1 xhigh, non-author) at a1133594: [29-sol-floors-review.md](29-sol-floors-review.md), PASS, no findings.
- Cold Fable final pass at a1133594: [34-fable-floors.md](34-fable-floors.md), PASS. MINOR-1 (undeclared spec defaults to 512 in the reported-energy census; the generator cannot emit it, `--check` flags it), MINOR-2 (floor-to-contrast join tested only at 512), MINOR-3 (end-state branch ahead of the contrast generator; both fail closed), NIT-1..4: **deferred** to lane `V5-FLOOR-HARDENING-01`. MINOR-2 is exercised on real bytes by the desk generation and its review (branch desk/2026-10-04-v5-pin-and-packs).
- Whole suite at a1133594 (main 8fa002f7 + this branch), CI shard method, local venv:
  - SHARD SUMMARY index=1/6 modules=1 tests=73 failures=0 errors=0 skipped=1 result=PASS
  - SHARD SUMMARY index=2/6 modules=55 tests=1429 failures=0 errors=0 skipped=3 result=PASS
  - SHARD SUMMARY index=3/6 modules=55 tests=1465 failures=9 errors=1 skipped=20 result=FAIL
  - SHARD SUMMARY index=4/6 modules=55 tests=1665 failures=3 errors=0 skipped=4 result=FAIL
  - SHARD SUMMARY index=5/6 modules=56 tests=1056 failures=3 errors=0 skipped=11 result=FAIL
  - SHARD SUMMARY index=6/6 modules=57 tests=1771 failures=48 errors=0 skipped=4 result=FAIL
  - exclusive: test_calibration_exits FAILED (errors=2); test_calibration_writer_crash_matrix OK
  Compared with base 8fa002f7 (67 known local-environment failures): extras in `test_mint_floor_artifact_generalized` (passes serially, see PR #471's gates) and a `test_run_night` timing case (the same family fails at base); `test_calibration_exits` errors at base. None attributable to this diff. Main (#469-#471, disjoint files) merged in afterwards; hosted CI on that head is the merged-tree run.
