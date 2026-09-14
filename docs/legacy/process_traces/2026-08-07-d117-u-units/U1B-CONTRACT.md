WRITE_SCOPE: ["joulewise/calibration_ledger.py","joulewise/calibration_bracketing.py","scripts/reserve_calibration_window_bracket.py","scripts/validate_powermetrics_fiducial.py","tests/test_calibration_ledger.py","tests/test_calibration_bracketing.py","tests/test_powermetrics_fiducial.py"]

IMPLEMENTATION UNIT U1b — writer integration for the two-slot bracket session (scope
expansion GRANTED by the lead over U1's NEEDS_SCOPE early return; approval note: the
production calibration writer is the §5A bookend tool and must consume reserved slots
— squarely inside U1's design intent).

THE WORKTREE ALREADY CONTAINS U1's COMPLETED WORK (two-slot session capability, exact
bracket binding, governed abort, 79 focused tests green). Do NOT redo or rework it;
build ON it. Read the prior session's own minimal-change plan and implement exactly
that residual: give scripts/validate_powermetrics_fiducial.py explicit session/slot/
attempt parameters so reservation-first capture accepts a predeclared session ID,
skips the ordinary reservation path, and finalizes or aborts that exact reserved
slot; route terminal and failure paths through the session APIs; add writer-level
reservation-order and crash-closure regressions in tests/test_powermetrics_fiducial.py.

Governing design: docs/process_traces/2026-08-07-d117-plan-freeze/DESIGN-MEMO.md
(§5A bookend sequence, F1 closure) + RATIFICATION.md rulings 1-2. Named decisions
(D-109/D-116) win over this prompt; report conflicts. Do not weaken any existing
fail-closed refusal.

Evidence: run the focused suites (test_calibration_ledger, test_calibration_bracketing,
test_powermetrics_fiducial) AND `python3 -m unittest discover -s tests` unpiped;
report exact tails + exit codes. Do NOT commit (worktree; lead commits). No
bookkeeping/audit-file edits. Report deviations + lead double-checks as your FINAL
MESSAGE.
