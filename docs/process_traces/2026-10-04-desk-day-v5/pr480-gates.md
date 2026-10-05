# PR #480 gates (mlx runtime: detokenizer built outside the measured prefill window), desk-day v5 seat 2

- Finding: Opus pre-mortem (lane ia-0a40, run from the interactive session) memo §3.1. Ruling: ruling 76 addendum B item 7 (fix before the block-4 seal; prospective registration note).
- Seat round 1 [91-sol-detok-report.md](91-sol-detok-report.md) (brief 91) at 33b68dfd.
- Executing review (Sol 6.1 high, non-author) at 33b68dfd: [95-sol-detok-review.md](95-sol-detok-review.md), PASS (one real BPE construction in `prepare()`, none during generation; shared map unchanged; per-run state reset; fallback matches the parent; event order identical under a fake clock).
- Cold Fable final pass at 33b68dfd: [96-fable-detok.md](96-fable-detok.md), FAIL: F1 pinned generator-record test red; F2 recorded tokenizer identity class renamed to `PreparedTokenizerWrapper` on the optimized path (identity pins, analysis matching and the determinism gate compare it); F3 determinism gate does not see the detokenizer path; F4 unguarded construction in `prepare()`; F5 notes.
- Round 2 [98-sol-detok-report-r2.md](98-sol-detok-report-r2.md) (brief 98) at a668bdfe: F1 FIXED (pin updated deliberately to the new exact shape), F2 FIXED (identity records mlx-lm's wrapper class on every path; equality test across parent, optimized and fallback), F4 FIXED (construction failure becomes a recorded fallback). **F3 DEFERRED** to lane `DETERMINISM-GATE-DETOK-PATH-01`: text and token counts are identical on both paths, only prefill energy differs, and every supported stack takes the optimized path; a consumer that must refuse a mixed set reads `generator.detokenizer.path`.
- Delta cold Fable at a668bdfe: [105-fable-detok-delta.md](105-fable-detok-delta.md), PASS (F1, F2, F4 closed; identity byte-identical to the parent on every path; nothing new inside a measured window).
- Whole suite at 33b68dfd (main b2ff2f36), CI shard method:
  - SHARD SUMMARY index=1/6 modules=1 tests=74 failures=0 errors=0 skipped=1 result=PASS
  - SHARD SUMMARY index=2/6 modules=55 tests=1324 failures=1 errors=0 skipped=14 result=FAIL
  - SHARD SUMMARY index=3/6 modules=56 tests=1627 failures=8 errors=0 skipped=10 result=FAIL
  - SHARD SUMMARY index=4/6 modules=56 tests=1462 failures=2 errors=0 skipped=3 result=FAIL
  - SHARD SUMMARY index=5/6 modules=57 tests=1533 failures=7 errors=0 skipped=3 result=FAIL
  - SHARD SUMMARY index=6/6 modules=57 tests=1565 failures=44 errors=0 skipped=12 result=FAIL
  - exclusive: test_calibration_exits OK; test_calibration_writer_crash_matrix OK.
  Failures beyond base 8fa002f7's local-environment set: `test_backend_outcomes_are_independently_pinned` (Fable F1, fixed in round 2) and `test_installer_refuses_outside_a_listed_install_span` (live battery probe UpdateTime stale on this machine; not code). Round 2's three files were rerun focused (`tests/test_mlx_runtime*.py`, `tests/test_suite_control_parity.py`, identity and determinism tests: pass); hosted CI on the final head is the merged-tree run.
