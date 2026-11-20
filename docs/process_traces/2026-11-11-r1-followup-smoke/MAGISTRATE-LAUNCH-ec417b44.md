# R1 follow-up smoke re-run: launch by magistrate ec417b44 (2026-11-11, RUN_STATE item 277)

Written just before the launch, which is this activation's last act.

- Smoke worktree: `/Users/edr/code/jw-wt/r1-followup-smoke`, detached at `9c5ba057e664bc24d605df4d34a611bbb6b1c718`, clean.
- PY: `/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv/bin/python` (same measurement venv as items 273 and 275). Not symlink-resolved.
- MAGISTRATE_PID: 43677 (`/Users/edr/.local/bin/claude`).
- OUT: `/Users/edr/code/jw-wt/r1-followup-smoke/.desk/r1-followup-smoke-20261112T061727Z` (also in `/Users/edr/night-custody/magistrate/r1-smoke-out-ec417b44.txt`). Fresh; items 273's and 275's OUT not reused.
- Start-and-check block: all passed. `verify_r1_executed_sources` OK at 9c5ba057e; ancestors 9b4817f36 and 4c27eba47 present; caps {A: 3120, B: 5720}, minimum 9510 s; `test_r1_smoke_plist_runs_interactive_like_the_night_templates` OK; no High Power marker; preflight `{"ac_power": true, "free_bytes": 113093820416, "disk_check": "report_only"}`.
- Nothing armed: only `com.joulewise.magistrate` loaded; no `com.joulewise.night*` plist in `~/Library/LaunchAgents`.
- No unread mail from Ed; no new directive issue (standing #587, #422, #421, #417, #416, #408, #405). Canonical root fast-forwarded to `0e8b04f77`.
- Stale `/Users/Shared/JouleWise/host-power/night.lock` left as found.
- No email at launch: a smoke is not an arm, and nothing changed state for Ed.
- DEADLINE: now + 11400, computed at launch.

If the launch command fails, this activation appends the failure below before exiting; no line below means launch returned rc 0 with a claimed fence.

Next activation: run item 277's receipt check on OUT (including the plist ProcessType check; on a Part A refusal read step D's `g0.outcome`) and report by email and as RUN_STATE 278.
