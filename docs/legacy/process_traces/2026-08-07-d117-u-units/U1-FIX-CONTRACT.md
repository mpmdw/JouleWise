WRITE_SCOPE: ["joulewise/calibration_ledger.py","joulewise/calibration_bracketing.py","scripts/reserve_calibration_window_bracket.py","scripts/validate_powermetrics_fiducial.py","tests/test_calibration_ledger.py","tests/test_calibration_bracketing.py","tests/test_powermetrics_fiducial.py"]

FIX ROUND — U1/U1b bracket session + writer. Close ALL findings below (from two
adversarial audits). No scope creep; NEEDS_SCOPE early-return if a fix truly needs
another file. Do NOT commit. Named decisions (D-109/D-116) and existing fail-closed
invariants win over this prompt — report conflicts rather than forcing. Every fix
gets a defect-shaped regression that FAILS against the pre-fix behavior.

FIX-1 (BLOCKER — L5 closure incomplete): the session capability and the bracket
binding must make intended-window identity and runs_root binding MANDATORY, not
optional: session-open records plan ID/SHA + evidence-root ID + runs_root; binding
verification refuses any candidate whose session fields do not exactly match the
window under evaluation. Regression: the night-hardening L5 borrowing scenario (a
later same-T1 calibration in another root within 24h) must refuse.

FIX-2 (BLOCKER — observation universe): finalized observations of an ABORTED session
(including systematic-invalid PRE) remain in the ledger observation universe for
D-109 R2.3/R2.5 evaluation and CAN fire
new_systematic_failure_challenges_preflight_screen; they are excluded ONLY from
bracket-candidate discovery. Fix the test at tests/test_calibration_ledger.py:599
that codifies the wrong empty-universe expectation.

FIX-3 (HIGH — mid-window pin escape): the generic head_pin_for_receipt() must REFUSE
bracket-session receipts (session-open and PRE finalization);
terminal_head_pin_for_session() is the only pin route for session receipts.
Regression: the auditor's probe (pin candidate for slot=pre after PRE finalization)
must refuse.

FIX-4 (HIGH — concurrent double-arm): writer session begin() must take an EXCLUSIVE
slot claim (ledger-visible or lock-file-with-identity under the ledger's custody
directory — your design choice, but it must survive process death recoverably and
refuse a second claimant with a named reason). Regression: two synchronized
begin() calls for the same session/slot/attempt — exactly one accepted.
Also: a failing second writer's exit path must NOT abort the first writer's session.

FIX-5 (HIGH — candidate leak): _bracket_sessions_and_observations()/
discover_calibration_candidates() publish session observations ONLY from sessions in
a terminal governed state (both slots finalized, or finalized+governed-abort);
open-session PRE never appears as a candidate. Rewrite the never_leak test to assert
NON-leakage (the current one asserts the leak), and make it mutation-sensitive to
aborted-session leakage too (no synthetic-snapshot laundering).

FIX-6 (BLOCKER — torn-tail recovery): make ledger appends crash-safe. Design freedom
within these invariants: append-only semantics preserved; no silent byte deletion;
recovery is GOVERNED and evidenced (a recovery action must itself leave a receipt or
journal evidence); after a simulated torn final line, loading + governed abort + full
recovery must succeed within the protocol. A sidecar write-ahead journal
(write+fsync journal line → append+fsync ledger → clear journal) with loader
torn-tail recognition bounded to journal-matching bytes is an acceptable shape;
document the chosen shape in the module docstring. Regression: inject a partial
finalization line (the auditor's scenario) and prove governed recovery.

FIX-7 (MEDIUM — non-discriminating tests): (a) crash-closure test must actually
simulate interpreter exit (subprocess that dies mid-operation) rather than calling
abandon() directly; reservation-order test must assert behavior, not source strings;
(b) add rollback-against-committed-pin coverage for the session loader path.

FIX-8 (LOW): reservation CLI dry-run/execute validation parity — dry-run must run the
same validation as execute; regression for the malformed-input case.

Evidence: three focused suites + FULL suite unpiped; exact tails + exit codes.
Report per-FIX status, deviations, chosen FIX-6 design, and lead double-checks as
your FINAL MESSAGE.
