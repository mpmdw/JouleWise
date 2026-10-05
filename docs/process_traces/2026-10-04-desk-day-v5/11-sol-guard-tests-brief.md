# Tests seat: lane G2A-ATTACH-GUARD-TESTS-01, plus PR #467's deferred Fable findings N3 and N5

Repository worktree: /Users/edr/code/JouleWise-wt-adae-tests (branch tests/2026-10-03-g2a-attach-guard-tests; main 8fa002f7 was just merged in as eb0c3926). Commit on this branch if your sandbox allows; otherwise leave the changes uncommitted and say so. Do not push.

## Context
The branch already carries commit c38791cc (tests pinning #461's surviving mutations, Fable F1/F2; docstring F3; inventory F4; derived lock F6); its records are `docs/process_traces/2026-10-03-activation-adaebcc6/30-guard-tests-brief.md` and `31-guard-tests.md`. Main has since gained PR #465 (controller retry backoff) and PR #467 (`scripts/harvest_g2a_window.py` judges the bracket against the acceptance cutoff; Fable final pass `docs/process_traces/2026-10-04-activation-df31cb27/21-fable-final-pass.md`).

## What to do
1. Re-run the branch's tests after the merge (`tests/test_g2a_calibration_attachment.py`, `tests/test_harvest_g2a_window.py`, `tests/test_battery_float_sweep.py`, `tests/test_controller_retry_backoff.py`) and repair any conflict between c38791cc's tests and #465/#467 behaviour. A test that disagrees with merged behaviour is fixed to the merged behaviour, never the code to the test (report each).
2. **Fable N3:** add a harvest-level test that drives the REAL bracket decision (`joulewise/calibration_bracketing.calibration_bracket_for_bundles` through `scripts/harvest_g2a_window.py`, no mock of the decision) to status `passed` with a NON-ZERO acceptance `ledger_cutoff` and a ledger whose head is past the cutoff (the window's own bracket session appended), and asserts the harvest verdict that follows. Build fixtures the way the existing tests do; if no fixture can reach `passed`, build the narrowest synthetic one that can and explain what it needed.
3. **Fable N5:** a test that kills the surviving mutant at `scripts/harvest_g2a_window.py:~178` (the `acceptance is None` clause): with that clause removed the harvest must end with a DIFFERENT, asserted cause code than with it. Assert the exact refusal code the clause produces. Prove the kill: apply the mutation in a scratch copy (not the worktree file), run the test, show it fails, restore.
4. Run `python3 -m pytest -q` on every file you touched plus `tests/test_calibration_bracketing.py` and `tests/test_generate_g2a_probe_inputs.py`; report counts.

## Write scope (exhaustive)
WRITE_SCOPE: ["tests/test_harvest_g2a_window.py", "tests/test_g2a_calibration_attachment.py", "tests/test_battery_float_sweep.py", "tests/test_controller_retry_backoff.py", "tests/fixtures/**"]
No production code. If a test exposes a production defect, stop and report it with file:line and a failing test name; do not fix it.

## Report
Files changed, commit sha (or "uncommitted"), test commands with counts, the N5 mutation-kill evidence, any production finding. Finish in this turn.
