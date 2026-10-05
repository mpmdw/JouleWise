# Block-4 lane X10 (Sol 6.1 xhigh): the T-0 stage cap, the window formula and the stream bounds (ruling 76 addendum E)

Worktree: /Users/edr/code/JouleWise-wt-dd5-sz (branch `lane/2026-10-05-b4-sizing2`; sizing round 2 committed as 280f2fec). Scratch /tmp/dd5-sz/ only. Leave changes uncommitted; never push. No sudo, launchctl, powermetrics or Metal. Never touch the four pinned estimator files. Lane X7 is editing `scripts/write_v5_qualification_plan.py` in parallel (attempt history, `s2`, NULL restore). Keep your writer edits inside the sizing and deadline functions (around lines 140-200 and 395-420) so the merge is clean.

Read addendum E: `git show origin/design/2026-10-04-v5-qualification-block:docs/process_traces/2026-10-04-desk-day-v5/76-r1-fold-ruling.md` (last section). Your round-2 report is `/Users/edr/night-archive/desk-day-v5/sol-sz2-r1.md`. Implement:

1. **`T0_STAGE_CAP_S` = 3300.** It is a source-bound allowance (`fixed/t0_stage_cap`) in `sizing_allowances.json`, derived in `sizing_sources/sizing_source_v2.json` (dwell cap 2700 + 600 for the other captures and the OFF margin).
   - The writer refuses a cap outside 3180-3480 s.
   - `T_pack_t0` returns to 360 s: the post-stage author, verification and consuming start.
   - `WINDOW_MAX_S = 60·ceil((span + T0_STAGE_CAP_S)/60)` replaces `span + DWELL_CAP_S`.
   - Deadlines, latest chain start, emergency, courier and dead-man follow from that.
   - Prerequisite boundary (`write_v5_qualification_plan.py:585`): use `t0 − T0_STAGE_CAP_S`, not `t0 − pack_t0`, if the intent is "controls expire before the stage can start". Read the code and say which is right.
2. **`scripts/run_night.py::_capture_qualification_t0`** bounds the stage by the plan's bound `T0_STAGE_CAP_S` (read it from the authenticated qualification plan record; do not hard-code it), not by 3600 s. `_admit_qualification_clean_dwell` keeps its 600-2700 s dwell check.
3. **Stream coverage** (`write_v5_qualification_plan.py:179-188`):
   - Exclude the cooldown from each member's sampled components. The cooldown runs on its own sampler (`joulewise/controller.py:1607`); cite that in a comment.
   - Add a 60 s minimum for every anchor-bearing stream: science, NEG-8 bound, references and brackets.
   - Helper captures without a clock anchor are exempt. Name how the code tells them apart: the `nonsampling` roster, or something else.
4. **Recompute** with the new formula. Report span, window, latest start and the three deadlines, and the frequency gate at −3.17 ppm.
   - Expected span: 25434 − 3300 + 360 = 22494 s.
   - Expected window: 60·ceil(25794/60) = 25800 s.

   Confirm or correct these.

Tests: kill-tests for a cap of 3179 or 3481, for a stream of 59 s, and for cooldown counted in a stream (accept the 335 s file and refuse a 334 s maximum). Also a test that `_capture_qualification_t0` uses the plan's cap. Run the sizing replay `/tmp/dd5-sz/replay_sizing.py` (it must now pass) and `tests.test_v5_qualification_plan tests.test_v5_block4_clock tests.test_v5_block4_x6 tests.test_run_night`. Finish in this turn.

WRITE_SCOPE: ["scripts/write_v5_qualification_plan.py", "scripts/run_night.py", "configs/campaigns/v5_qualification_25g83/sizing_allowances.json", "configs/campaigns/v5_qualification_25g83/sizing_sources/**", "tests/test_v5_qualification_plan.py", "tests/test_v5_block4_clock.py", "tests/test_v5_block4_x6.py", "tests/test_v5_block4_x10.py", "tests/test_run_night.py", "tests/fixtures/v5_qualification/**"]
