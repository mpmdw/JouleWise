WRITE_SCOPE: ["scripts/run_night.py","joulewise/t0_rehearsal.py","joulewise/arm_readiness.py","scripts/launch_window.py","scripts/rehearse_t0_unattended.py","tests/test_run_night.py","tests/test_t0_rehearsal.py","tests/test_launch_window.py","tests/test_rehearse_t0_unattended.py","tests/test_arm_readiness.py","docs/contracts/pack_night_go_receipt.md","docs/process/NIGHT_HANDBACK.md"]

# D-176 seat 4 — fix round (gpt-6-astra, HIGH, genre implementation)
Branch feat/2026-09-08-d176-seat4-rehearsal at 3032dd93. Two refuters: Opus contract lens at the absolute path
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99fw-ref-d176-seat4-opus-contract-review.md (findings 1–7) and the Astra execution delta at
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99fx-delta-d176-seat4-astra-report.md (F1). Cure all with these RULINGS (verify every line by reading the code):
1 (BLOCKER, RULED): the bundle MUST load without `g7_control`: make the locator OPTIONAL in the loader's record-name
  census (absent → G7 evaluates FAIL with detail `g7_control_pending`, never a load error; present → validated as now);
  add an explicit sequencing clause to §6/§10.5 ("the completed rehearsal bundle loads and evaluates G1–G6 + G8–G10
  before the G7 control is produced; G7 PASS requires the post-night `run_night.py g7-control` step") and the matching
  step in docs/process/NIGHT_HANDBACK.md (post-night sequence: harvest → g7-control → re-evaluate bundle).
2 (BLOCKER): compose an overall PASS through the REAL loader: FixtureBuilder emits a current pack_night GO (not a
  legacy d149_go) so G5 passes, and at least one test asserts overall_verdict PASS across all ten gates via
  load_evidence_bundle; keep the D-149 refusal test.
3 (should-fix, RULED): distinct refusal details — `go_receipt.receipt_class` (presented GO's key shape) vs
  `night_plan.receipt_class` (control plan not TRANSACTION_PACK); validate_g7_control accepts ONLY
  `go_receipt.receipt_class` for the rehearsal_receipt presentation; pin in §6/§10.5 and the validator; regression: a
  control built on a non-pack plan yields an artifact that FAILS acceptance from bytes alone.
4/5: §9 rows S1/S4/B4/N1 and §7.1 row 4 carry file:line pins (re-read each symbol); restore the dropped citations
  (tests/test_run_night.py ~:2197, tests/test_rehearse_t0_unattended.py ~:21/:127,
  test_gate_checks_authorization_fields_and_confirmation_bytes).
6: a real T-0 evidence counterfactual on the G5 PASS path — mutate/omit/substitute one T-0 evidence file → G5 C2 FAIL.
7: remove the debug print in tests/test_launch_window.py; restore the deleted explanatory comment in launch_window.py.
Astra F1 (should-fix): produce_g7_control must refuse a symlinked destination (`<control>` and `<control>/night`,
  resolve(strict) equality with the intended path before ANY write) and confine writes beneath the verified control
  directory; regression: a `night` symlink pointing at the completed rehearsal → refusal, zero files created there.
Preserve the census-cure bytes in arm_readiness.py/night_gate.py apart from admission (do not edit night_gate.py).
Acceptance (rc-gated to a log; named modules ONLY, NEVER discover/shard; end your turn after the named acceptance):
tests.test_run_night tests.test_t0_rehearsal tests.test_launch_window tests.test_night_gate tests.test_arm_readiness
tests.test_rehearse_t0_unattended tests.test_docs_freshness; git diff --check; no commit; header < 8192 bytes; report
per finding with file:line and counterfactual.
