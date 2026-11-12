# R1 follow-up smoke re-run: launch by magistrate 354d3889 (2026-11-12, RUN_STATE item 281)

Written just before the launch, which is this activation's last act.

- Smoke worktree: `/Users/edr/code/jw-wt/r1-followup-smoke`, detached at `22f438fd36b0cae30a90676785848923538fb635`, clean.
- PY: `/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv/bin/python` (same measurement venv as items 273 to 279). Not symlink-resolved.
- MAGISTRATE_PID: 58220 (`/Users/edr/.local/bin/claude`).
- OUT: computed at launch and written to `/Users/edr/night-custody/magistrate/r1-smoke-out-354d3889.txt`. Fresh; no earlier OUT (items 273, 275, 277, 279) reused.
- Start-and-check block: all passed. `verify_r1_executed_sources` OK at 22f438fd3; ancestors 9b4817f36 and 4c27eba47 present; caps {A: 3120, B: 5720}, minimum 9510 s; `test_r1_smoke_plist_runs_interactive_like_the_night_templates` OK; no High Power marker; preflight `{"ac_power": true, "free_bytes": 108997861376, "disk_check": "report_only"}`.
- Nothing armed: only `com.joulewise.magistrate` loaded; no `com.joulewise.night*` plist in `~/Library/LaunchAgents`. AC power, battery 100% charged.
- No unread mail from Ed; no new directive issue (standing #587, #422, #421, #417, #416, #408, #405). Canonical root fast-forwarded to `fb10dcea1`.
- `/Users/Shared/JouleWise/host-power/night.lock` left as found: `{"pid": 50618, "role": "r1-smoke-close", "epoch_s": 1794477026.82}` (item 279's smoke close; pid not running).
- Only other agent-family process: this session's own Codex MCP adapter child (`codex`, pid 58243); it exits with this session.
- No email at launch: a smoke is not an arm, and nothing changed state for Ed.
- DEADLINE: now + 11400, computed at launch.

If the launch command fails, this activation appends the failure below before exiting; no line below means launch returned rc 0 with a claimed fence.

Next activation: run item 281's receipt check on OUT (report per-phase coverage fractions for the sampler and every key, and `selection.ok`, s_fast, s_slow from `smoke_part_b.json`; on a G0 timeout read that part's `g0.outcome`) and report by email and as RUN_STATE 282.
