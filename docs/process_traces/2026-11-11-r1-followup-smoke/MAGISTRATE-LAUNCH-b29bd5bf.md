# R1 follow-up smoke re-run: launch by magistrate b29bd5bf (2026-11-12, RUN_STATE item 279)

Written just before the launch, which is this activation's last act.

- Smoke worktree: `/Users/edr/code/jw-wt/r1-followup-smoke`, detached at `8f5a1a0f9be4a65ae735bd6a501e793b526fc902`, clean.
- PY: `/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv/bin/python` (same measurement venv as items 273, 275 and 277). Not symlink-resolved.
- MAGISTRATE_PID: 50286 (`/Users/edr/.local/bin/claude`).
- OUT: path is computed at launch and written to `/Users/edr/night-custody/magistrate/r1-smoke-out-b29bd5bf.txt`. Fresh; items 273's, 275's and 277's OUT not reused.
- Start-and-check block: all passed. `verify_r1_executed_sources` OK at 8f5a1a0f9; ancestors 9b4817f36 and 4c27eba47 present; caps {A: 3120, B: 5720}, minimum 9510 s; `test_r1_smoke_plist_runs_interactive_like_the_night_templates` OK; no High Power marker; preflight `{"ac_power": true, "free_bytes": 111180750848, "disk_check": "report_only"}`.
- Nothing armed: only `com.joulewise.magistrate` loaded; no `com.joulewise.night*` plist in `~/Library/LaunchAgents`.
- No unread mail from Ed; no new directive issue (standing #587, #422, #421, #417, #416, #408, #405). Canonical root fast-forwarded to `d67399cde`.
- `/Users/Shared/JouleWise/host-power/night.lock` left as found. It now reads `{"pid": 43989, "role": "r1-smoke-close", "epoch_s": 1794468800.77}` (written 23:33 PST 11-11 by item 277's smoke close; pid 43989 not running), not the R1 driver pid 52565 that item 279 describes. Reported for the lead: the smoke close step seems to leave its lock behind.
- Only other agent-family process: this session's own Codex MCP adapter child (`codex app-server`, parent `node scripts/codex-mcp-server.mjs`, parent 50286); it exits with this session.
- No email at launch: a smoke is not an arm, and nothing changed state for Ed.
- DEADLINE: now + 11400, computed at launch.

If the launch command fails, this activation appends the failure below before exiting; no line below means launch returned rc 0 with a claimed fence.

Next activation: run item 279's receipt check on OUT (including the plist ProcessType check; on a G0 timeout read that part's `g0.outcome`) and report by email and as RUN_STATE 280.
