# Controller round 2 (Sol 6.1 high): PR #482 review finding F1

Worktree: /Users/edr/code/JouleWise-wt-dd5-ctl (branch feat/2026-10-05-controller-g2b-attach-battery, head 9b08ecf6). Scratch /tmp/dd5-ctl2/ only. Leave changes uncommitted; never push.

Executing review FAIL, `/Users/edr/night-archive/desk-day-v5/sol-ctrev.md` F1, repro `/tmp/dd5-ctrev/regressions.py`: the G2-b exception at `joulewise/controller.py:452` authenticates the runs root but not the running config, so an untagged config absent from the authenticated pack inventory is accepted with `g2b_pre_slot` metadata and no full launch lineage; main refused it. Fix: grant the exception only when the running config is authenticated as a member of the lineage's pack (the existing member-authentication path the tagged writer uses) and the member carries the launch-lineage marker; otherwise keep the Revision-5 refusal exactly as on main. Turn the repro into a regression, and keep every existing attachment test green. The cold Fable pass (`/Users/edr/night-archive/desk-day-v5/fable-ctl.md`) passed; do not change the battery part. Run `tests/test_controller*.py tests/test_battery_float*.py tests/test_g2a_calibration_attachment.py`. Finish in this turn.

WRITE_SCOPE: ["joulewise/controller.py", "tests/test_controller_g2b_attachment.py", "tests/fixtures/controller_g2b/**"]
