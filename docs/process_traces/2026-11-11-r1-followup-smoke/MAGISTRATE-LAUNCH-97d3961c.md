# RL-89 Part A smoke 2: launch by magistrate 97d3961c (2026-11-12, RUN_STATE item 294)

Written just before the launch, which is this activation's last act.

- Smoke worktree: `/Users/edr/code/jw-wt/r1-followup-smoke`, detached at `99622e96cf83d578672747a90db1d8128a57eae9` (the night sha, item 290), clean.
- Mode: `--fresh-soak --parts A`. No prepare, no arm. Launched after 13:15 PST, the end of the OS batch window.
- PY: `/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv/bin/python`. MAGISTRATE_PID: 84554 (`/Users/edr/.local/bin/claude`).
- OUT: `/Users/edr/code/jw-wt/r1-followup-smoke/.desk/r1-followup-smoke-20261112T210906Z`. Fresh; no earlier OUT reused.
- Only other agent-family processes: this session's Codex MCP adapter (`node scripts/codex-mcp-server.mjs` 84569, `codex app-server` 84572/84577). They exit with this session. No Codex child was started. All background waiters were stopped before the launch.
- `night.lock` left as found: `{"epoch_s": 1794494120.826043, "pid": 77434, "role": "r1-smoke-close"}`.
- No unread mail from Ed at 13:08; directives are the standing set (#587, #422, #421, #417, #416, #408, #405).

Start-and-check output (13:08 PST):

```
HEAD_OK
84554 /Users/edr/.local/bin/claude
CLEAN
99622e96cf83d578672747a90db1d8128a57eae9
RL-89 MAC CHECK OK e6231a8f3e6ab6177bbedbf12b878c958a7b4d4331e36472c74c2a192588769b 60 16 44 95825997f7fd50e3a86342c059bd1eba2cc37139684c76eed35f0ca6ed0a1dad
OK
NO_HIGH_POWER_MARKER
{"ac_power": true, "free_bytes": 105708982272, "disk_check": "report_only"}
-	0	com.joulewise.magistrate
0
Now drawing from 'AC Power'
 -InternalBattery-0 (id=23265379)	100%; charged; 0:00 remaining present: true
```

If the launch command fails, this activation appends the failure below before exiting. No line below means the launch returned rc 0 with a claimed fence.

Next activation: run item 285's check block on OUT and report as RUN_STATE 295. On PASS, arm under item 289 step 3.
