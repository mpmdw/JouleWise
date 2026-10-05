# Delta check: A6 review blocker R1 and its follow-on (PR #475, 64ef2471 → 14324c52)

Worktree: /Users/edr/code/JouleWise-wt-dd5-a6delta, detached at 14324c52. Diff to check: `git diff 64ef2471 14324c52 -- scripts joulewise tests` (76f8e948 merged unrelated main PRs #469-#471; ignore their files). Your earlier review (FAIL, R1 BLOCKER: driver death before PASS lost launcher custody) is /Users/edr/night-archive/desk-day-v5/sol-a6review.md, scripts under /tmp/dd5-a6review/. The fix: a durable exclusive `launch.pending` record (schema `joulewise.launch_pending.v1`: pid, pgid, start_time, plan_id, attempt_id, epoch_s) written before the recheck; dead-man, courier and the measurement-owner census (`joulewise/measurement_liveness.py`) treat a live or indeterminate pending group as alive; a recheck refusal leaves the pending record as evidence and no `chain.started`. Pack-window harvesters do not exist yet (they must read the pending record; tracked lane).

Executing: re-run your V5 driver-death reproducer (must now refuse delivery while the launcher lives); the barrier fault probes; the non-pack byte-identity comparison; a pending record with a dead leader or reused pid; a stale pending record from an earlier attempt (does it block a new attempt forever, or is it attributed by plan/attempt?); and the ruled regressions (tokenizer/model mutation refused before any bundle, no `chain.started`). Run `/Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider -o cache_dir=/tmp/dd5-a6delta/pc tests/test_measurement_liveness.py tests/test_launch_window.py tests/test_launch_window_realization_recheck.py tests/test_run_night.py`; compare failures with main.

Verdict line first: `DELTA: PASS` or `DELTA: FAIL`, then findings with severity and evidence.

WRITE_SCOPE: []
Scratch: /tmp/dd5-a6delta/ only. Never run sudo, launchctl or powermetrics. No background processes. Finish in this turn.
