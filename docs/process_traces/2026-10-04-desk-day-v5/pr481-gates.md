# PR #481 gates (`_v5` idle 75 s), desk-day v5 seat 2

- Ruling: ruling 76 addendum B item 1 (Opus pre-mortem memo §1.8: at idle 30 every `_v5` sampler stream is shorter than the 60-second clock-fit minimum; block 3 ran idle 75 with all 50 anchors bounded).
- Round 1 [94-sol-packs-idle75-report.md](94-sol-packs-idle75-report.md) at c3f4ea14. Cold Fable [100-fable-regen.md](100-fable-regen.md): FAIL. F1 the shared NEG-8 corpus and window-reference configs were edited in place, so nine older plan trees and six window records named bytes that no longer existed; F2 the interior-reference run-id fix would make the whole-window verdict see three midpoint references and fail.
- Round 2 (brief 101; the seat timed out after doing the work; the lead verified and committed it) at cfd51a96: shared directories restored byte-for-byte; 75 s copies in `configs/campaigns/neg8_reference_corpus_v5/` and `window_references_v5/`, used by the `_v5` packs and, opt-in (`v5_references=True`), by `scripts/gen_g2_phase_d.py`; run-id change reverted. F1 FIXED. **F2 DEFERRED** to lane `GAMMA-INTERIOR-REFERENCES-01` (two of GAMMA's three registered interior references are silently skipped by the run-id collision on main; the cure needs an evaluator design for three interior points before the full GAMMA claim window; the one-block G2-b chain dispatches one midpoint and is unaffected). F3 moot after the revert.
- Executing review at cfd51a96 [116-sol-regen-review2.md](116-sol-regen-review2.md): PASS (245 tests; fresh regeneration diffs empty; every emitted `--check` passes on committed bytes; default render byte-identical to main).
- Delta cold Fable at cfd51a96 [117-fable-regen-delta.md](117-fable-regen-delta.md): PASS. N1 (the opt-in render has no production caller): **FIXED on PR #483** (lane X6 wires the block-4 plan writer to it); does not affect this merge.
- Lead checks: `git diff --quiet b2ff2f36 cfd51a96 -- configs/campaigns/neg8_reference_corpus configs/campaigns/window_references`; the three emitted `--check`s and `gen_g2_phase_d.py --check` pass; the historical floor plan tests pass.
- Whole suite at cfd51a96 (main b2ff2f36), CI shard method:
  - SHARD SUMMARY index=1/6 modules=1 tests=74 failures=0 errors=0 skipped=1 result=PASS
  - SHARD SUMMARY index=2/6 modules=55 tests=1303 failures=0 errors=0 skipped=14 result=PASS
  - SHARD SUMMARY index=3/6 modules=56 tests=1626 failures=9 errors=5 skipped=10 result=FAIL
  - SHARD SUMMARY index=4/6 modules=56 tests=1459 failures=3 errors=0 skipped=3 result=FAIL
  - SHARD SUMMARY index=5/6 modules=57 tests=1529 failures=7 errors=0 skipped=3 result=FAIL
  - SHARD SUMMARY index=6/6 modules=57 tests=1594 failures=45 errors=0 skipped=12 result=FAIL
  - exclusive: test_calibration_exits FAILED (errors=4, fixture timeouts under machine load; the named cases pass serially); test_calibration_writer_crash_matrix OK.
  Failures beyond base 8fa002f7's local-environment set: three collector-manifest tests and two calibration-exit tests (all pass serially: load), the known 8-second watchdog test, and `test_installer_refuses_outside_a_listed_install_span` (live battery probe; not code).
