# Replay 6 — SUPERSEDED, no result

Replay 6 (worktree /Users/edr/code/JouleWise-wt-replay-6, HEAD f2a027c12d714296adcc24dcaa37ea36ae06fe7d, started 2026-09-10 16:45:15 PDT, command `PYTHONDONTWRITEBYTECODE=1 python3 scripts/shard_tests.py --workers 4 --split`) was STOPPED BY THE LEAD at ~17:03 PDT as superseded: that head carried a merge-surfaced test defect (direct `git init` in tests/test_gen_derivation_night.py, refused by the git-fixture maintenance guard; found by replay 3), now fixed and re-run as replay 7 at a new head in a separate worktree.

NO RESULT: the run was terminated mid-suite, so there is no `REPLAY_RC=` line and no valid per-shard totals — the truncated log at /tmp/magistrate-96bfeca7/replay-6.log ends with `WORKERS SUMMARY shards=4 modules=0 tests=0 failures=0 errors=0 skipped=0 failed_shards=1,2,3,4 result=FAIL`, which is the kill artifact (background wrapper exit 144), not a suite verdict; nothing here bears on pass/fail at any head.
