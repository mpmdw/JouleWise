# PR #473 gates (`_v5` contrast generator: generic replay, acceptance in force), desk-day v5 seat

- Seat: [17-sol-contrast-report.md](17-sol-contrast-report.md) (brief [17-sol-contrast-brief.md](17-sol-contrast-brief.md)): reproduced `evidence_author_pack_authentication_underivable` at base; fixed generator emission, `joulewise/arm_readiness_evidence.py` unchanged.
- Executing review (Sol 6.1 xhigh, non-author) at a42a26fd: [35-sol-contrast-review.md](35-sol-contrast-review.md), PASS, no findings.
- Cold Fable final pass at a42a26fd: [37-fable-contrast.md](37-fable-contrast.md), PASS. MINOR-1 (authentication proves self-consistency, not the provenance of carried inputs): **fixed by procedure**, at pack landing the source generator runs `--check` with the canonical panel, workload and committed pin against the committed pack (done on branch desk/2026-10-04-v5-pin-and-packs, all checks pass). MINOR-2 (`decode_workload_candidate.json` profile path names the pack copy): accepted, deterministic. NIT-1..4: deferred to lane `V5-FLOOR-HARDENING-01` (`_v5` generator hardening).
- Whole suite at a42a26fd (main 8fa002f7 + this branch), CI shard method, local venv:
  - SHARD SUMMARY index=1/6 modules=1 tests=73 failures=0 errors=0 skipped=1 result=PASS
  - SHARD SUMMARY index=2/6 modules=55 tests=1420 failures=0 errors=0 skipped=3 result=PASS
  - SHARD SUMMARY index=3/6 modules=55 tests=1465 failures=9 errors=1 skipped=20 result=FAIL
  - SHARD SUMMARY index=4/6 modules=55 tests=1665 failures=3 errors=0 skipped=4 result=FAIL
  - SHARD SUMMARY index=5/6 modules=56 tests=1059 failures=3 errors=0 skipped=11 result=FAIL
  - SHARD SUMMARY index=6/6 modules=57 tests=1767 failures=47 errors=0 skipped=4 result=FAIL
  - exclusive: test_calibration_exits FAILED (errors=2); test_calibration_writer_crash_matrix OK
  Compared with base 8fa002f7 (67 known local-environment failures): extras in `test_mint_floor_artifact_generalized` (passes serially) and a `test_run_night` timing case (family fails at base); `test_calibration_exits` errors at base. None attributable to this diff. Main (#469-#471, disjoint files) merged in afterwards; hosted CI on that head is the merged-tree run.
