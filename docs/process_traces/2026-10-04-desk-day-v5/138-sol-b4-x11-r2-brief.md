# Block-4 lane X11 round 2 (Sol 6.1 high): the shared T-0 sizing fixture

Worktree: /Users/edr/code/JouleWise-wt-dd5-b4int (integration branch; X11 round 1 committed). Scratch /tmp/dd5-x11/ only. Leave changes uncommitted; never push. No sudo, launchctl, powermetrics, systemsetup or Metal.

Round 1 (`/Users/edr/night-archive/desk-day-v5/sol-x11-r1.md`) flagged F2. The shared fixture `install_clock_sizing_inputs` in `tests/test_arm_readiness_evidence_t0.py` omits X10's source-bound `t0_stage_cap`, so the authoring test fails with `fixed.keys`. Modernize that shared fixture to the current sizing contract: the stage cap, `pack_t0` 360, and the allowance schema the writer accepts. Do not relax the writer's exact-key check.

Then run every module that imports the fixture (`grep -l install_clock_sizing_inputs tests/`), plus `tests.test_arm_readiness_evidence_t0 tests.test_arm_readiness_integration tests.test_launch_window tests.test_capture_t0_step`. Do not run the canonical suite; the lead runs it. Finish in this turn.

WRITE_SCOPE: ["tests/test_arm_readiness_evidence_t0.py", "tests/test_arm_readiness_integration.py", "tests/test_launch_window.py"]
