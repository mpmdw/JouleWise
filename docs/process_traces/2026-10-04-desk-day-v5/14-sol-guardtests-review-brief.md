# Executing review: branch tests/2026-10-03-g2a-attach-guard-tests (lane G2A-ATTACH-GUARD-TESTS-01) at 93b84dae

Worktree: /Users/edr/code/JouleWise-wt-dd5-gtreview, detached at 93b84dae (main 8fa002f7 merged in). Review the whole diff `git diff 8fa002f7...93b84dae` (7 files). You are a non-author reviewer with an EXECUTING lens: run the code, do not only read it.

Production changes in the diff: `joulewise/controller.py` (docstring only) and `scripts/recover_calibration_ledger.py` (removes the transient `terminal-ledger.jsonl.lock` from the harvest's derived ledger copy after governed operations release their leases). The rest are tests: #461 surviving mutations (Fable F1/F2), F4 inventory, F6 derived lock, and #467's Fable N3 (the real bracket decision reaches `passed` through the harvest with a non-zero acceptance cutoff) and N5 (the `acceptance is None` clause at `scripts/harvest_g2a_window.py:~178`). Records: `docs/process_traces/2026-10-03-activation-adaebcc6/30-guard-tests-brief.md`, `31-guard-tests.md`; `docs/process_traces/2026-10-04-activation-df31cb27/21-fable-final-pass.md` (N3, N5).

Check, executing:
1. Every new test passes, and each one that claims to kill a mutant does: apply each named mutation in a scratch copy under /tmp (never in the worktree), run the test, confirm failure; report a table mutant → test → killed/survived.
2. The N3 fixture is physically and contractually honest: it drives the real `calibration_bracket_for_bundles` (no mock of the decision), the cutoff is non-zero, the head is past the cutoff, and `passed` is reached for the right reasons (not by a fixture short-cut that bypasses a check production applies). Name any check the fixture skips.
3. The lock removal: can it ever delete a lock that a live writer holds (when is it called; who else might hold it)? Can it change a ledger or head-pin byte? Does it alter any harvest output other than dropping `terminal-ledger.jsonl.lock` from the archive? Is anything downstream (harvest `outputs`, SHA256SUMS, the issuer) relying on the lock file existing?
4. Run: `python3 -m pytest -q tests/test_harvest_g2a_window.py tests/test_g2a_calibration_attachment.py tests/test_battery_float_sweep.py tests/test_controller_retry_backoff.py tests/test_calibration_bracketing.py tests/test_generate_g2a_probe_inputs.py tests/test_recover_calibration_ledger.py` (use /Users/edr/code/JouleWise/.venv/bin if system python lacks pytest); report counts.

Verdict line first: `REVIEW: PASS` or `REVIEW: FAIL`, then findings with severity (BLOCKER/MAJOR/MINOR/NIT), file:line and a failing command where possible.

WRITE_SCOPE: []
Scratch: /tmp/dd5-gtreview/ only. Finish in this turn.
