# Implementation seat, round 6: A6 second Fable pass — G1 (red test where ps works), G2, G3

Worktree: /Users/edr/code/JouleWise-wt-dd5-a6 (branch feat/2026-10-04-launch-realization-recheck, head aba27481, PR #475). Fable's second ruling: /Users/edr/night-archive/desk-day-v5/fable-a6-2.md (read it; its probes are under /tmp/dd5-fable-a6b/: faithful.py, residual.py). Fable found the product code sound and F1/F2 cured. Commit if your sandbox allows; otherwise leave changes uncommitted. Do not push.

IMPORTANT: your sandbox denies `/bin/ps`, which is exactly why G1 was invisible to you. Any test you write must pass BOTH with a working identity probe and without one; where you cannot run real `ps`, use a stub that returns the start time recorded in `launch.pending` (the faithful case) and a stub that returns a different time (the reused case).

- **G1 MAJOR (fix, test only):** `tests/test_launch_window_realization_recheck.py:~419-491` (assertion ~486): inside the `try` at ~481 give the driver the real identity probe for the `dead_man` call, or a stub returning the start time recorded in `launch.pending`; keep the separate "reused pid" test. The test must pass with real `ps` (the lead will run it outside the sandbox) and with the probe unavailable.
- **G2 MINOR (fix):** pin `TZ=UTC` (and keep `LC_ALL`) in `observe_identity`'s environment, or compare an epoch instead of text; show the same pid's start time compares equal across differing caller `TZ`. Note the census already has this sensitivity for `chain.started` on main: fix it in the shared function so both benefit.
- **G3 MINOR (fix):** when the dead-man (or any reader that proves the pending group gone) finds an unclosed `launch.pending`, it writes the write-once `launch.resolved` closure, so later censuses stop probing an old pid/pgid. Test the two refusing rows of Fable's residual table become clear after resolution, and that a live group still refuses.
- G4, G5, G6 NIT: leave unless a one-line fix is obvious; list them.

Run to completion with `/Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider -o cache_dir=/tmp/dd5-a6r6/pc` (set TMPDIR=/tmp/dd5-a6r6): `tests/test_launch_window_realization_recheck.py tests/test_measurement_liveness.py tests/test_run_night.py tests/test_launch_window.py`; compare failures with main. No background processes.

WRITE_SCOPE: ["joulewise/measurement_liveness.py", "scripts/run_night.py", "scripts/launch_window.py", "tests/test_launch_window_realization_recheck.py", "tests/test_measurement_liveness.py", "tests/test_run_night.py", "tests/test_launch_window.py", "tests/fixtures/**"]
Scratch: /tmp/dd5-a6r6/ only. Never run sudo, launchctl or powermetrics; never touch the four pinned estimator files. Finish in this turn.
