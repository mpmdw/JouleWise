# Record 09 — magistrate terminal review of the exact merge candidate `c5d29b9b` (PR #359), activation 28ff4b28, 21:1x PDT

## What the head is
`c5d29b9b` = `3855ad25` (fix round 1) + a records-only merge of `bookkeeping/2026-09-18-activation-28ff4b28`. Executed: `git diff 3855ad25 c5d29b9b -- tests joulewise scripts docs/contracts docs/process` is EMPTY (0 lines); every non-record path is byte-identical to the head the full replay (record 08) and hosted CI run 35418532801 executed. `git diff 6ec5b460 c5d29b9b --stat -- . ':!docs/process_traces'` = two test files only.

## The production diff, read in full by the magistrate this session
- Round 0 (`6ec5b460..e32ea56c`, 4635 bytes, +23/−7): worker-side expansion keyed by `large_frame_bytes`; `argv_for` closure records the largest argv string into the row; `max_arg_bytes` surfaced in both result-row builders; one regression asserting < 131,072 with the `execve(2)` reference. Read at the bench before commit (record 03).
- Round 1 (`e32ea56c..3855ad25`, 1795 bytes, +3/−1): `ack_until` initialised to `None` and set after `_BindTask` exists (restores base ordering; contract refuter C3-01, delta D1 probe base-equivalent); `assertGreater(max_arg_bytes, 0)` (execution refuter finding 1; delta D2 mutant fails `0 not greater than 0`). Applied at the bench by the magistrate (both below the bench-vs-session threshold), verified, then delta re-audited by an independent Astra seat (record 06).
- Whole change `6ec5b460..c5d29b9b -- tests`: 4763 bytes; the four assertions of `test_large_frame_is_incremental_and_still_bounded` byte-identical to base (contract refuter C2, delta D3).

## Design-level questions (row 7)
1. Does the fix keep the property the test exists for? Yes: the worker still publishes the identical 200,761-byte frame (contract refuter C1 measured base and head equal), `max_buffer=200761`, `max_reads=2`, `max_bytes=65536`, GO.
2. Is the regression defect-shaped and non-vacuous? Yes: fails `200885 not less than 131072` when the parent-side expansion is restored (records 03, 05 mutation kill) and `0 not greater than 0` when the recording is removed (delta D2).
3. Is anything platform-conditional or production-touching? No: no `sys.platform`, no skips, no change under `scripts/` or `joulewise/` (contract refuter C5/C6; `git diff --exit-code` on `scripts/run_night.py` and `joulewise/quiet_admission.py` clean).
4. Same-signature: all three seats state "none found"; round 1 introduced no evaluation-order change (delta D5 checked every field initialised before the task exists).

## Deferred with record
- Opus nit: the guard is per-string `MAX_ARG_STRLEN`, not total `ARG_MAX`; largest observed total ≈ 2.6 KB, no present exposure. Not registered as a lane (no mechanism to reach it from this bench); noted in kernel row 238's evidence via this record.

## Verdict
MERGE. Twelve-row ledger on PR #359 updated to RUN with this head; hosted CI on `c5d29b9b` is the post-review confirmation (code identical to the green run on `3855ad25`, including `test (3.13, 5)`).
