# 32 — Replay 5 record: integration tree `ee82373b` = PR #317 `c59bdc57` + PR #334 `f8bcccb2` over main `64fc4e27` (gate row 9 for both PRs)

Tree `/Users/edr/code/JouleWise-wt-integ-c5048879` detached at `ee82373b` (merge of `f8bcccb2` into `c59bdc57`; `git diff --stat origin/main..HEAD` = exactly the two PRs' files: `.github/workflows/ci.yml`, `scripts/test_timings.json`, two side-thread records, `docs/phase_2/derivation_night_runbook.md`, `docs/process/NIGHT_HANDBACK.md`, `tests/test_night_gate.py`), clean before and after. Command (lead, unpiped to the log): `PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python3 scripts/shard_tests.py --workers 4 --split`, launched 07:33 PDT, finished 08:16 PDT. Exact tail:

```
MODULE PASS tests.test_workload_profile tests=7 failures=0 errors=0 skipped=0 seconds=0.004
SHARD SUMMARY index=4/4 modules=61 tests=1748 failures=0 errors=0 skipped=3 result=PASS
WORKERS SUMMARY shards=4 modules=233 tests=6049 failures=0 errors=0 skipped=103 failed_shards=none result=PASS
REPLAY_RC=0
```

6049 tests = 6048 at #329's head + the one new census regression. `tests.test_calibration_exits` (exclusive) passed locally, including `test_forced_auto_maintenance_mutation_reproduces_cleanup_race`, which failed once on hosted 3.11 at `c59bdc57` (run 34762906269; the same known race-reproduction flake recorded in `docs/process_traces/2026-09-08-handoff-redo/99gl-terminal-review-d176.md`; it passed on main `64fc4e27` and on #334's run); the failed jobs were re-run at 08:07. Replay 4 (`ebcb9850`) was stopped when main moved; this replay is at both final heads.

CI: #334 `f8bcccb2` run 34762907523; #317 `c59bdc57` run 34762906269 attempt 2. Post-merge cross-unit reviews follow each merge.
