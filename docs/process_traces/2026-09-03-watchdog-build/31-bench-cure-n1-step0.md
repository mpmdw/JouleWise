# Bench cure of delta-11 finding N1 (magistrate, 2026-09-04)

N1 (trace 30): checklist step 0 continued after an early digest mismatch and returned success (a `for` loop whose `test` failures did not abort the block). Cure applied at the bench (smaller than a delegation contract): every `test` in step 0 now aborts with a named reason and exit 3 (`STEP0_FAIL …`, `STEP0_DIGEST_MISMATCH <path>`), and the block ends with `echo STEP0_OK`.

Executed (temp repo with a real merge commit and the five pinned paths, snippet extracted verbatim from the doc and run with `/bin/zsh`):
- tampered `scripts/install_magistrate_watchdog.sh` in the checkout → `rc=3 STEP0_DIGEST_MISMATCH scripts/install_magistrate_watchdog.sh` (aborted at the second file; nothing after it ran);
- clean checkout → last line `STEP0_OK`, `rc=0`.
`tests.test_magistrate_watchdog` OK after the edit (the doc-snippet tests still pass). This closes the delta-11 residual; the same-signature statement in trace 30 concerned this snippet only.
