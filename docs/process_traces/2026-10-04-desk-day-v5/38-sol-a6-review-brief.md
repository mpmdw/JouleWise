# Executing review: V5-LAUNCH-REALIZATION-RECHECK-01 (branch feat/2026-10-04-launch-realization-recheck at 64ef2471)

Worktree: /Users/edr/code/JouleWise-wt-dd5-a6review, detached at 64ef2471 (parent main 8fa002f7). Diff: `git diff 8fa002f7 64ef2471` (`scripts/launch_window.py`, `scripts/run_night.py`, tests). Row A6 in TASK_QUEUE.md and ruling `docs/process_traces/2026-09-02-projection-02/150a-RULING-post-arm-recheck.md` define the requirement; briefs/reports `docs/process_traces/2026-10-04-desk-day-v5/23-*`, `27-*` on branch records/2026-10-04-desk-day-v5 (or /Users/edr/night-archive/desk-day-v5/sol-a6.md, sol-a6b.md). You are a non-author reviewer with an EXECUTING lens.

The change: after `verify_consumed_launch` the launcher re-derives the identity projection (existing helpers) and refuses `readiness_identity_environment_dirty` on any digest/unit mismatch before any bundle; to keep the ruled "chain NOT started" property, the driver no longer claims `chain.started` before the launcher: the launcher, after recheck PASS, asks the driver to claim the start and waits for an ACK before `execve`. DIAGNOSTIC_NO_PACK and REHEARSAL_STUB paths are claimed to be byte-identical to main. This is the launch path of every pack window, claim windows included.

Check, executing:
1. Ruled regressions: a post-arm tokenizer mutation and a model-file mutation are refused before `RunBundleWriter.create`, with no `chain.started`/`chain.exited`/bundle; the clean path launches with exactly one `chain.started` whose fields equal main's.
2. The new PASS/claim/ACK barrier: deadlock or hang cases (driver dies, launcher dies, ACK never arrives, PASS sent twice, a stale FD), and what the harvest sees in each (NULL vs RECOVER). Is the monotonic deadline still enforced while waiting? Can collection begin without a claimed start, or a start be claimed without a PASS?
3. Non-pack kinds: byte-identical artifacts, env and argv vs main (reproduce the seat's comparison).
4. Recheck cost: time the recheck on a realistic projection if possible without Metal/sudo/launchctl/powermetrics; else estimate from the helpers it calls.
5. Run `/Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_launch_window.py tests/test_launch_window_realization_recheck.py tests/test_identity_pins.py` and `tests/test_run_night.py`; compare failures to main 8fa002f7 (a family of "battery fixture in child Pythons" and supervision timing failures is pre-existing locally; prove each failure is pre-existing by running it at base).

Verdict line first: `REVIEW: PASS` or `REVIEW: FAIL`, then findings with severity, file:line and a failing command where possible.

WRITE_SCOPE: []
Scratch: /tmp/dd5-a6review/ only. Never run sudo, launchctl or powermetrics. No background processes. Finish in this turn.
