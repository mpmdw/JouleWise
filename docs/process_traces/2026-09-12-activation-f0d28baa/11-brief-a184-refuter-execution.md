# Refuter brief — A184 landing, EXECUTION lens

SESSION_MODE: delegated
WRITE_SCOPE: []

You are a READ-ONLY refuter (sandbox read-only; run tests with `python3 -m unittest`, never edit; no pytest on this host). Branch `fix/2026-09-12-recover-window-exhausted` in this worktree, one commit over origin/main `ace4cc3c`: `git diff ace4cc3c..HEAD` (5 files, +53/-1). Seat reports: `../JouleWise-wt-bk-f0d28baa/docs/process_traces/2026-09-12-activation-f0d28baa/02-seat-a184-resume-astra-report.md` and the governing brief `../JouleWise-wt-bk-b02193d2/docs/process_traces/2026-09-12-activation-b02193d2/01-brief-a184-recover-window-exhausted.md`. Never touch `/Users/edr/code/JouleWise` or `/Users/edr/JouleWise-measurement-20260913-derivation` (a measurement night is armed there; both fenced). The whole `tests.test_calibration_exits` module takes ~500 s; run single tests by dotted name instead unless told otherwise.

Kernel acceptance (lane A184): "session-refusal on a window_exhausted-aborted derivation session prints that reason with a defect-shaped test and a killed cut; the runbook harvest section cites it."

Report (claude-codex-report/v1, genre review): findings tiered blocker / should-fix / nit, each with the reproducing command or quoted file:line; explicit "no blocker found" if none. Under 8000 bytes.

## Your lens: does the code do what the test claims, and could the test pass for the wrong reason?

1. Reproduce the killed cut yourself in a scratch COPY: copy `scripts/recover_calibration_ledger.py` to /tmp, you cannot edit the tree, so instead reason from the diff and run the new test once (`python3 -m unittest tests.test_calibration_exits.PublicGovernedExitWitnessTests.test_session_refusal_reports_window_exhausted_derivation_abort`); paste the result line. Then read the `session-refusal` branch in `scripts/recover_calibration_ledger.py` and state exactly which code path produces `calibration_window_exhausted` and which produced `calibration_session_not_open` before the map entry (file:line both).
2. Process exit: the test asserts `REFUSAL_BY_CODE[RefusalCode.WINDOW_EXHAUSTED].process_exit`. Determine that value from the registry and confirm it equals the three sibling automatic-abort codes' exit (quote). If the new code lands in a family/tier set the siblings are NOT in, or misses one they ARE in (`_ABORT`, `_WRITER_COMPONENT`, any operational/pre-slot set, any `witness.*` inventory), that is a blocker; enumerate every set that contains `ROLLOVER_GATE_TIMEOUT` and check membership of `WINDOW_EXHAUSTED` in each.
3. `WITNESS_CASES` gained an entry with observer `"session-refusal"` and the generic loop gained an `elif case.observer == "session-refusal"` branch that asserts `terminal_result == "session_aborted"` INSTEAD of the sibling assertion. Read the loop (~line 5455-5470) and say whether the sibling cases' assertions are byte-identical in behaviour to before; and whether the new observer string is a real observer the harness dispatches (grep how `case.observer` is consumed elsewhere) or merely a label that makes the generic loop skip work for this case. Run the generic witness test(s) that iterate `WITNESS_CASES` by dotted name (find them with grep) and paste result lines.
4. The abort path: `abort-session --reason window_exhausted` is what the night chain runs (`scripts/night_chains/calibration_derivation_only.zsh` ~line 121). Quote that line and confirm the literal reason string matches the map key byte-for-byte.
5. Anything in the diff outside the brief's scope (an unrelated behaviour change) is a should-fix; quote it.
