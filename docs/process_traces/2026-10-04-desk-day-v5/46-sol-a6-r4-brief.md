# Implementation seat, round 4: A6 — the measurement-owner census must see a live pending launcher (scope granted)

Worktree: /Users/edr/code/JouleWise-wt-dd5-a6 (branch feat/2026-10-04-launch-realization-recheck; head 76f8e948 = your round 3 committed as 061c60cc + a merge of current main). Round-3 report: /Users/edr/night-archive/desk-day-v5/sol-a6c.md. Commit if your sandbox allows; otherwise leave changes uncommitted. Do not push.

Rulings: F1 scope granted for `joulewise/measurement_liveness.py` and `tests/test_measurement_liveness.py`: the census (~186, ~260) must treat a live `launch.pending` process group exactly as it treats a live started chain (owner LIVE), and fail closed when liveness cannot be established; reuse the identity fields you persisted; add the V8 case as a test. F2 deferred: `scripts/harvest_g2a_window.py` serves only DIAGNOSTIC_NO_PACK windows, which never write `launch.pending` (non-pack paths byte-identical); the block-4 pack-window harvest scripts (lane in `docs/process_traces/2026-10-04-desk-day-v5/42-block4-required-code.md`) must read `launch.pending` — list the exact fields they need in your report. F6: main merged in by the lead; re-run your round-3 checks at the new head.

Run to completion: `tests/test_measurement_liveness.py tests/test_launch_window.py tests/test_launch_window_realization_recheck.py tests/test_identity_pins.py tests/test_run_night.py` (compare failures with base as before) and re-run V5/V6/V7/V8. No background processes.

WRITE_SCOPE: ["joulewise/measurement_liveness.py", "tests/test_measurement_liveness.py", "scripts/launch_window.py", "scripts/run_night.py", "tests/test_launch_window.py", "tests/test_launch_window_realization_recheck.py", "tests/test_run_night.py", "tests/fixtures/**", "tests/fixtures/custody_read_replay_allowlist.json"]
Scratch: /tmp/dd5-a6r4/ only. Never run sudo, launchctl or powermetrics; never touch the four pinned estimator files. Finish in this turn.
