# Record 21 — full sharded replay at the lane 232 final head (the R3 bench commit on `feat/2026-09-18-quiet-predicate-evidence-harness`, base main `2f79e633`), lead, 2026-09-19 09:12–10:0x PDT

`python3 -B scripts/shard_tests.py --workers 4 --split` in the detached worktree `wt-fresh232-d0b83820`; log `21-full-replay-final-head.log.gz`; rc 1.

- 6,471 tests, 242 modules; 233 `OK` module lines; 9 `FAILED` module lines.
- Every failing test (22 test ids across 9 modules: `test_arm_readiness_evidence_packauth`, `test_arm_readiness_registry`, `test_calibration_bracketing`, `test_campaign_generator_core`, `test_d117_decode_contrast_plan`, `test_d117_floor_qwen25_1p5b_plan`, `test_d117_floor_qwen25_7b_plan`, `test_d117_floor_qwen3_v5_generate`, `test_d117_v3_family`) is in the set record 14 established as main's red on the advanced ledger head pin (`pinned input drifted` / `external input drift` / `cutoff == pin`), and every one of those modules passes at the head-pin repair's round-2 head at the bench (record 28). **No test in `tests/test_sample_quiet_predicate_evidence.py` or any other module failed.** The lane's own module: 45 tests OK inside the replay.
- Ran concurrently with delegated seats and, for its last ~15 minutes, with the head-pin replay (record 23); no timing-sensitive module failed.

Disposition for gate row 9: the lane is clean on the full suite; the residual red is main's, cured by PR #361, which merges first. After #361 lands, main is merged into the lane branch and the terminal review (record 22) re-runs the nine modules above on the merge head.
