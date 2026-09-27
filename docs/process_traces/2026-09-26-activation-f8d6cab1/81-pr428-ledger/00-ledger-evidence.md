# PR #428 (A310, light tier, test-only): gate-ledger evidence for rows 1, 9, 11 and 12, at head `d8aed7cd`

**Row 1: an independent audit by a fresh reviewer who is not the author.** A fresh Opus reviewer returned **MERGE with no blockers** (activation f8d6cab1 record 00, item 8).
- The only file touched is `tests/test_sample_quiet_predicate_evidence.py`. The production cleanup at `scripts/sample_quiet_predicate_evidence.py:1399-1406` is unchanged.
- Mutations: removing TERM turns the test RED (−9 ≠ −15). Removing KILL passes, but that gap already exists on main.
- The module ran 3 times: 79 of 79 OK each run.

**Row 9: the lead's full-suite replay at `d8aed7cd`** (the seat commit `37f9b935` plus main `5d5a0b75`; `scripts/shard_tests.py --workers 6`; worktree `JouleWise-wt-flake-6bec2aa6`). It gave **7,384 tests, 0 failures, 0 errors, 109 skipped: PASS**.
- It ran under heavy concurrent load: a second full suite, a Sol seat, and Astra and Opus lenses.
- `test_load_join_ladder_accepts_slow_exit_and_escalates_a_stuck_child` passed. That is the test that failed in four earlier loaded replays.
- The tail is in [row9-fullsuite-d8aed7cd-tail.txt](row9-fullsuite-d8aed7cd-tail.txt) and the full log is `row9-fullsuite-d8aed7cd.log.gz`.

**Row 11: CI on `d8aed7cd`.** Every job passes: `build`, `changes`, `fences`, `installed-wheel`, `quick`, `test (3.13, 1..6)`, `calibration-exits-exclusive (3.13)`, and `calibration-writer-crash-matrix-exclusive (3.13, 1..2)`. `gate-ledger` is this ledger. The post-merge integration look follows the merge.

**Row 12: the magistrate's terminal review.** Opus 5.5, activation f8d6cab1, of `d8aed7cd433fcc68c3acba1866d3e09dd1d7f1f0`.
- The change is test-only: one test-module subclass that widens only the post-TERM `join(1)` to 3 s. Its assertions are unchanged.
- Nothing touches measurement, registration, analysis or claim code or text, so the light tier is correct.
- The reviewer's two NITs are recorded for the follow-up and are not merge conditions: comment the post-KILL join widening, and add a SIGTERM-ignoring fixture so a test covers KILL.
- Verdict: **MERGE**.
