# PR #476 gates (`_v5` floors decode identity declares `prompt_tokens`), desk-day v5 seat

- Finding: throwaway-clone re-proof [44-clone-proof-report.md](44-clone-proof-report.md) F1. Seat: [51-sol-floor-identity-report.md](51-sol-floor-identity-report.md) (its sandbox has no Metal, so its clone projections refused `readiness_identity_artifact_unreadable`).
- Lead check (outside the sandbox): fresh clone at fd0b08db with the issued pin bundle; both floors generated; `scripts/project_identity_pins.py freeze` per floor, committing between: rc 0, status PASS for both (both refused before this change).
- Executing review (Sol 6.1 high, non-author) at fd0b08db: [55-sol-floor-identity-review.md](55-sol-floor-identity-review.md), PASS (all 200 science configs byte-identical to the parent's output; removing the field fails the new regression).
- Cold Fable final pass at fd0b08db: [54-fable-floor-identity.md](54-fable-floor-identity.md), PASS; informational notes only (no disposition needed).
- Whole suite at fd0b08db (main 784d12f1 + this branch), CI shard method, local venv:
  - SHARD SUMMARY index=1/6 modules=1 tests=73 failures=0 errors=0 skipped=1 result=PASS
  - SHARD SUMMARY index=2/6 modules=55 tests=1430 failures=0 errors=0 skipped=3 result=PASS
  - SHARD SUMMARY index=3/6 modules=55 tests=1471 failures=8 errors=0 skipped=20 result=FAIL
  - SHARD SUMMARY index=4/6 modules=55 tests=1672 failures=3 errors=0 skipped=4 result=FAIL
  - SHARD SUMMARY index=5/6 modules=56 tests=1078 failures=3 errors=0 skipped=11 result=FAIL
  - SHARD SUMMARY index=6/6 modules=57 tests=1777 failures=42 errors=1 skipped=4 result=FAIL
  - exclusive: test_calibration_exits FAILED (errors=2); test_calibration_writer_crash_matrix OK
  Failure set equals base 8fa002f7's 67 local-environment failures except `test_calibration_exits`, which errors at base too. Main (#474) merged in afterwards; hosted CI on that head is the merged-tree run.
