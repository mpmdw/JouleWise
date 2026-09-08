WRITE_SCOPE: []

# Refuter brief — ICLOUD-CUSTODY-LOCATOR-01 landing, EXECUTION lens (gpt-6-astra, read-only)
HEAD = three commits on main (parts 1-2 superseded design, part 3 redesign). Packet: `git diff HEAD~3 HEAD`
(joulewise/calibration_ledger.py, joulewise/calibration_bracketing.py, two test modules). Ruling that governs
(trace docs/process_traces/2026-09-08-handoff-redo/84-brief-icloud-locator-part3-astra.md): the bounded probe is a
PURE path probe (`Path.exists`/`is_dir` only) in a daemon thread with a 2 s budget, run BEFORE and OUTSIDE any
authentication session or lock; timeout/exception → the locator is treated exactly as ABSENT and the authenticated
read is never attempted; the authenticated read itself is unchanged, synchronous, lock-safe; `JOULEWISE_BACKUP_ROOTS`
empty → backup-rooted locators treated absent without probing. Break it: (1) grep every worker/thread use in the
two modules: does ANY worker call anything other than `Path.exists`/`is_dir` (any read, open, hash, session, lock)?
A single such call is a BLOCKER; (2) absent-equivalence: for each probe site, run the entry point with (a) the
locator absent and (b) the probe mocked to block 10 s: the returned state/verdict/reason must be identical (diff the
structures); (3) lock safety: block one probe, then start an authentication session on another locator in the same
process: it must proceed; (4) `git diff HEAD~3 HEAD -- joulewise/authentication_io.py` must be EMPTY and
tests.test_authentication_io must pass unchanged; (5) override: empty string → zero probes (count calls);
non-empty override pointing at a scratch dir → that root probed, default root NOT; (6) mutation: reintroduce a
read inside the worker in a $TMPDIR copy and confirm the lock-safety regression fails; (7) the four modules
`tests.test_calibration_ledger_custody tests.test_calibration_bracketing tests.test_calibration_ledger
tests.test_authentication_io`. Never touch the real iCloud path. Report (genre review): `verdict` = {counts,
findings}; header < 8192 bytes; findings with file:line, severity, exact command.
