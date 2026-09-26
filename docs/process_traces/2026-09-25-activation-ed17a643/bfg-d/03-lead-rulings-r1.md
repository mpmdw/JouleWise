# BFG-D round-1 early return: lead rulings (magistrate ed17a643)

These rulings answer the seat's F1–F3 (report `02-seat-report-r1.md`). They are operational, interface and test-contract rulings inside the cold texts (final texts v1.1 §5). No science rule moves.

**R1 (F1, historical fixtures and applicability).**
- The battery obligation applies to derivation sessions evaluated for the epoch-25G83 / Revision-5 acceptance generation, the one A-R5b amends. Other generations and epochs the issuer can still process keep today's behaviour byte for byte: no battery check, and no change to their assertions. Key the check on the generation or registration identity the issuer already resolves; never key it on a flag the caller supplies.
- Test fixtures that build 25G83/Revision-5 derivation sessions represent the post-BFG-D writer. Their builders therefore gain passing `battery_float` pre/post observations built from the real fixture in `tests/fixtures/battery_float/`. This is a fixture update, not a loosened assertion.
- Every pre-existing assertion must still hold unchanged. If a Revision-5 test's expected output must change because a field was added (for example, the exact C3 receipt now carries `measured.battery_float`), update the expected value to add exactly that field, and list each such edit in your report with before/after.
- The exact legacy-receipt assertion in `tests/test_night_gate.py` gets the new C3 `battery_float` entry and the new probe in the sequence, and nothing else.
- `scripts/issue_epoch_continuation.py`: first establish from code whether it can accept any session of epoch 25G83/v3 under Revision 5. Revision 5 says there is no PASS continuation branch for this epoch.
  - If it cannot, revert every change to that file and its tests, and add one test proving that it refuses a 25G83/v3 session (only if that refusal already exists; otherwise report NEEDS_RULING).
  - If it can, gate it exactly as the issuer is gated, with the same generation keying.

**R2 (F2, cadence report input).**
- `report_window` gains keyword arguments `ledger: Path` and `session_id: str`. It resolves the session through the ledger's own authenticated readers, as the issuer does, calls `joulewise.battery_float.validate_window` first, and on a non-pass verdict labels its output `diagnostic_only: battery_float_confounded|battery_float_evidence_missing`. It still computes and prints the cadence numbers.
- CLI: add a required `--calibration-ledger PATH` and a repeatable required `--session LABEL=SESSION_ID`. The command refuses (exit 2) if any `--window` label has no matching `--session`, or if any `--session` label has no matching `--window`.
- Add tests for: a pass session; a confounded session (labelled diagnostic, cadence numbers still present); a missing mapping (refusal).

**R3 (F3, scope).** APPROVED prospectively: `docs/process/NIGHT_HANDBACK.md` and `docs/phase_2/derivation_night_runbook.md`, for regenerating the ARM-RETRY-POLICY v1 block only, byte-exact from `arm_retry.render_policy()`.

**R4 (F4, git).** The seat cannot write git metadata from this worktree. Leave the work uncommitted; the lead commits.

**R5 (completion).** Finish every §5.6 test (3, 5, 6, 8 and 9 are missing or unproved) at the production call sites named there. Run each touched test module to completion and paste its tail; do not interrupt a suite for slowness. `tests.test_validate_powermetrics_fiducial*` and the evidence-night suites may take minutes. That is expected.
