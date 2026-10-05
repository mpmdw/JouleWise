# Implementation seat: V5-LAUNCH-REALIZATION-RECHECK-01 (queue row A6)

Worktree: /Users/edr/code/JouleWise-wt-dd5-a6 (branch feat/2026-10-04-launch-realization-recheck, based on main 8fa002f7). Commit if your sandbox allows; otherwise leave changes uncommitted. Do not push.

## The row (TASK_QUEUE.md A6, authority `docs/process_traces/2026-09-02-projection-02/150a-RULING-post-arm-recheck.md`; read both)
Close the post-arm identity window: the launch step that precedes collection (`scripts/launch_window.py`, immediately after `verify_consumed_launch` succeeds, ~272-286) re-derives the identity projection the way `joulewise/arm_readiness_evidence_t0.py` does and refuses `readiness_identity_environment_dirty` on any projection-digest or unit mismatch BEFORE the chain reaches `RunBundleWriter.create`; reuse the existing derivation helpers, add no new identity code. Regressions ruled: (1) a post-arm tokenizer mutation is refused before `RunBundleWriter.create`; (2) the refusal is emitted with the chain NOT started (no `chain.started` file). Both the next qualification windows (pack-bound rehearsal, G2-b) and the claim windows will run this launch path, so it must land before them; DIAGNOSTIC_NO_PACK and rehearsal-stub paths must stay unaffected in behaviour (state which paths reach the new check).

## Do
Implement it; tests for both ruled regressions, a model-file mutation, the unchanged pass path on a clean projection, and each non-pack path's behaviour; run the touched modules plus `tests/test_launch_window*.py`, `tests/test_arm_readiness*.py`, `tests/test_run_night*.py` (grep for importers of `launch_window`). Report the measured extra launch latency of the recheck on this machine with a real projection if you can derive one without sudo, launchctl or powermetrics (else say so). No background processes; do not run the whole suite.

WRITE_SCOPE: ["scripts/launch_window.py", "joulewise/arm_readiness_evidence_t0.py", "tests/test_launch_window.py", "tests/test_launch_window_realization_recheck.py", "tests/fixtures/**", "tests/fixtures/custody_read_replay_allowlist.json"]
Scratch: /tmp/dd5-a6/ only. Never touch the four pinned estimator files (`joulewise/powermetrics_fiducial.py`, `joulewise/uncertainty_evidence.py`, `joulewise/adapters/powermetrics.py`, `joulewise/reduce.py`). If the right fix needs another file, stop and report why. Finish in this turn.
