# Block-4 lane X11 (Sol 6.1 xhigh): cross-lane integration failures after merging X7-X10

Worktree: /Users/edr/code/JouleWise-wt-dd5-b4int (integration branch `feat/2026-10-05-v5-qualification-code` at 2c1f64de: X7, X8, X9 and X10 merged onto bda1c180). Scratch /tmp/dd5-x11/ only. Leave changes uncommitted; never push. No sudo, launchctl, powermetrics, systemsetup or Metal. Never touch the four pinned estimator files.

Each lane passed its own focused tests. Merged, 12 tests fail. The full log is `/tmp/dd5-int2/focused.log`; the command is at its head, or rerun the module list below. The causes seen:

- 4 × `PackNightRefusal: qualification window/dwell cap`. X10 changed the window to `ceil_minute(span + T0_STAGE_CAP_S)`, and some driver or night-gate check (or an X7 fixture) still expects `span + 2700`.
- 4 × `ValueError: V5_QUALIFICATION_OCCURRENCE must be one literal export in the pinned chain`. X7's `s2` and fresh-attempt plans meet a chain renderer or reader that X10 or X9 touched, or a fixture is out of date.
- 2 × `HarvestRefusal: input_not_regular` (X2 harvest-replay tests, and the X1 capture-timeout test).
- 1 × `battery_boundary_lifecycle_missing` (X4 assembler test, pre-existing since X6 F4 bound battery records to lifecycle artifacts).
- `tests.test_capture_t0_step...test_produces_all_eight_inputs_then_author_reaches_normal_derivation`: an error, likely from the X8 T-0 dwell meeting X9 or X10 inputs.

For each failure:
- find the root cause, and say which lane's contract is right according to the spec (registration draft and ruling 76 addenda A-E on `origin/design/2026-10-04-v5-qualification-block`);
- fix the production code or the stale fixture accordingly;
- never relax a validator;
- report a table: test → cause → lane contract that wins → change.

Then run, and they must all pass: `tests.test_v5_block4_x7 tests.test_v5_block4_x9 tests.test_v5_block4_x10 tests.test_v5_block4_x6 tests.test_v5_block4_x4 tests.test_v5_block4_x1 tests.test_v5_block4_x2 tests.test_v5_qualification_plan tests.test_v5_s1_qualification tests.test_v5_s1_desk_closeout tests.test_harvest_v5_g2b_window tests.test_harvest_v5_qualification tests.test_v5_block4_replay tests.test_v5_block4_clock tests.test_v5_block4_composed tests.test_t0_anchor_positive_control tests.test_capture_t0_anchor_positive_control tests.test_capture_t0_anchor_positive_control_g10 tests.test_prewindow_check tests.test_capture_t0_step tests.test_revision6_seal tests.test_battery_float_consumers tests.test_git_fixture_maintenance tests.test_authentication_io tests.test_custody_mode_inventory tests.test_run_night tests.test_night_gate`. Watchdog `BindSupervisionProcessTests` timing failures in the sandbox are a known artefact; ignore them. Finish in this turn.

WRITE_SCOPE: ["scripts/write_v5_qualification_plan.py", "scripts/run_night.py", "joulewise/night_gate.py", "joulewise/night_plan_writer.py", "joulewise/v5_qualification.py", "joulewise/t0_rehearsal.py", "joulewise/arm_readiness_evidence_t0.py", "joulewise/prewindow.py", "scripts/capture_t0_step.py", "scripts/harvest_v5_g2b_window.py", "scripts/harvest_v5_qualification.py", "scripts/v5_s1_desk_closeout.py", "scripts/assemble_v5_battery_boundaries.py", "scripts/gen_g2_phase_d.py", "tests/test_v5_block4_x1.py", "tests/test_v5_block4_x2.py", "tests/test_v5_block4_x4.py", "tests/test_v5_block4_x7.py", "tests/test_v5_block4_x9.py", "tests/test_v5_block4_x10.py", "tests/test_capture_t0_step.py", "tests/test_v5_qualification_plan.py", "tests/test_run_night.py", "tests/fixtures/v5_qualification/**", "tests/fixtures/custody_read_replay_allowlist.json", "tests/test_authentication_io.py"]
