# PR #425 (bookkeeping, light tier): gate-ledger evidence for rows 1, 9, 11 and 12, at head `f15be524`

**Row 1: independent audit by a fresh reviewer who is not the author.** A fresh Opus reviewer read `f15be524` read-only and returned **MERGE, with no blockers**. The review is recorded as item 5 of [activation 8e43cfa7 record 00](../../2026-09-26-activation-8e43cfa7/00-activation-record.md):
- Tier check passes.
- The merge SHAs match.
- The registration digest equals the file sha.
- `gen_state --check` exits 0.
- 75 tests are OK.
- Four NITs are fixed after merge on branch `docs/2026-09-26-8e43cfa7`.

**Row 9: lead full-suite replay at `f15be524`** (`scripts/shard_tests.py --workers 6`, worktree `JouleWise-wt-bk-152c9255`). The summary lines are in [row9-fullsuite-f15be524-tail.txt](row9-fullsuite-f15be524-tail.txt); the full log is `row9-fullsuite-f15be524.log.gz`.
- 7,381 tests: 0 failures, 1 error, 109 skipped.
- The single error is `test_arm_readiness_evidence_t0 … test_g4_real_ruled_census_pgrep_dialect`, which failed with `ValueError: invalid literal for int() … 'WORKTREE:'`.
- The test runs a real `pgrep -lf` over the live process table. It matched a concurrently running Sol seat whose multi-line prompt argv contains the census pattern text, and it assumes that every output line starts with a PID.
- The isolated rerun at the same head passed: `Ran 1 test … OK`.
- The PR changes no code. Its only test change is the `tests/test_gen_state.py` count pin. The error is therefore environmental: it is a test-hermeticity defect under concurrent agent load, noted for the flake lane, and it does not bear on this PR.

**Row 11: CI on the final head.** Hosted checks for `f15be524` at 09:57 PDT 09-26:
```
build	pass
calibration-exits-exclusive (3.13)	pass
calibration-writer-crash-matrix-exclusive (3.13, 1)	pass
calibration-writer-crash-matrix-exclusive (3.13, 2)	pass
changes	pass
fences	pass
gate-ledger	fail
installed-wheel	pass
quick	pass
test (3.13, 1)	pass
test (3.13, 2)	pass
test (3.13, 3)	pass
test (3.13, 4)	pass
test (3.13, 5)	pass
test (3.13, 6)	pass
```
Every job passes except `gate-ledger`, which is this ledger. The post-merge integration look is done after merge.

**Row 12: magistrate terminal review.** Opus 5.5, activation 6bec2aa6, full session context, of the exact merge candidate `f15be52493b478f828ed38417cf8e246bf9f341b`:
- Non-trace changes are `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json` (three lanes) and `tests/test_gen_state.py` (pin 257→260).
- Everything else is process traces.
- Nothing touches measurement, registration, analysis or claim code or text. The light tier is correct.
- Verdict: MERGE.
