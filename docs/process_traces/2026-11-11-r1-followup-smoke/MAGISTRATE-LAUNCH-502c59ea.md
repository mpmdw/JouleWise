# RL-89 Part A smoke: launch by magistrate 502c59ea (2026-11-12, RUN_STATE item 285)

Written just before the launch, which is this activation's last act.

- Smoke worktree: `/Users/edr/code/jw-wt/r1-followup-smoke`, detached at `bb6394f2bf290550b43a87efecb15d581839b845`, clean.
- Mode: `--fresh-soak --parts A` (fresh 1,800 s TV0h/Th0C idle soak, then Part A only). No prepare, no arm.
- PY: `/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv/bin/python` (same measurement venv as items 273 to 281). Not symlink-resolved.
- MAGISTRATE_PID: 77113 (`/Users/edr/.local/bin/claude`).
- OUT: `/Users/edr/code/jw-wt/r1-followup-smoke/.desk/r1-followup-smoke-20261112T132843Z` (also in `/Users/edr/night-custody/magistrate/r1-smoke-out-502c59ea.txt`). Fresh; no earlier OUT reused.
- Start-and-check block: all passed. `verify_r1_executed_sources` returned bb6394f2b; `RL-89 MAC CHECK OK e6231a8f…769b 60 16 44`, config sha256 `95825997f7fd50e3a86342c059bd1eba2cc37139684c76eed35f0ca6ed0a1dad`; `test_r1_smoke_plist_runs_interactive_like_the_night_templates` OK; no High Power marker; preflight `{"ac_power": true, "free_bytes": 106731470848, "disk_check": "report_only"}`.
- Nothing armed: only `com.joulewise.magistrate` loaded; no `com.joulewise.night*` plist on disk. AC power, battery 100% charged.
- No unread mail from Ed; no new directive issue (standing #587, #422, #421, #417, #416, #408, #405). Canonical root fast-forwarded to `fa6e32be0`.
- `/Users/Shared/JouleWise/host-power/night.lock` left as found: `{"epoch_s": 1794485069.0128481, "pid": 58535, "role": "r1-smoke-close"}` (item 281's smoke close).
- Only other agent-family process: this session's own Codex MCP adapter (`node scripts/codex-mcp-server.mjs` pid 77128, its `codex app-server` 77131/77136); they exit with this session. No Codex child was started.
- No email at launch: a smoke is not an arm, and nothing changed state for Ed.
- DEADLINE: now + 7200, computed at launch; launched at about 05:30 PST, well before item 285's 11:05 cutoff.

If the launch command fails, this activation appends the failure below before exiting; no line below means launch returned rc 0 with a claimed fence.

Next activation: after the desk fence is gone, run item 285's check block on OUT (receipt asserts, soak rc and reference sha256, `smoke_part_a.json` G0 outcome and `duration_s` against the 1,200 s bar, release minus reference for fast/slow/Tf08, plist `ProcessType Interactive`) and report by email and as RUN_STATE 286. A G0 timeout means nothing arms and it goes to the research lead.
