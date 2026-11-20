# Part C at the W1-line commit: launch by magistrate f6c8a352 (2026-11-14, RUN_STATE item 319)

Written just before the launch, which is this activation's last act. A diagnostic: no slots, no arm, no session, no W1. Run 1 of tonight's order (RL-155a §1.2).

- Smoke worktree: `/Users/edr/code/jw-wt/partc-w1line`, detached at `f30a97d008b57acde9adec0f789dff13c9d6ef23`, clean; `a6a09e6d7` and `f006b7aa6` are ancestors; `git diff ae340d3da HEAD` empty.
- Mode: `--fresh-soak --parts C`.
- PY: `/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv/bin/python` (same measurement venv as item 315's run; not symlink-resolved).
- MAGISTRATE_PID: 86554 (`/Users/edr/.local/bin/claude`).
- OUT: `/Users/edr/code/jw-wt/partc-w1line/.desk/r1-partc-w1line-20261115T004253Z` (fresh).
- DEADLINE: min(launch + 14,400 s, 1794735000 = 01:30:00 PST Sun 15 Nov), computed at launch. Launch at about 16:44 PST, so the deadline is launch + 4 h (about 20:44 PST) and the worst-case end (launch + 12,180 s) about 20:07 PST. 00:00 falls outside the span. The exact DEADLINE and launch epoch are in `/Users/edr/night-custody/magistrate/r1-partc-w1line-out-f6c8a352.txt`.
- Launch gate (RL-155 §3.1): item 318 and `PARTC-W1LINE-JOURNAL-COPY-DONE` on `origin/main`; no desk fence; pilot close (`runner_receipt.json` mtime) 1794702159 = 16:22:39 PST; gate 16:42:39 PST; checks ran 16:42:48 PST. Item 318 names no "restore unproven", host-state stop or High Power marker.
- Dry checks (scratch worktree detached at the full sha, own TMPDIR, `JW_B5_SYNTHETIC_ONLY=1`, `python3.13 -B -m unittest`, one module at a time): `test_rl145_gate_hashes` 1 OK; `test_rl145_part_c` 30 OK; `test_r1_smoke_launcher` 58 OK; `test_v4_registration` 24 OK; `hazards.test_refusal_allowlist` 24 OK. Scratch worktree removed.
- Start-and-check block: all passed (script `/Users/edr/night-custody/magistrate/partc-w1line-startcheck-f6c8a352.sh`).
  - The seventeen hashes match item 319's two tables (`partc-w1line-hashes-f6c8a352.txt` in custody).
  - `verify_r1_executed_sources` returned `f30a97d008b57acde9adec0f789dff13c9d6ef23`.
  - `RL-89 MAC CHECK OK e6231a8f3e6ab6177bbedbf12b878c958a7b4d4331e36472c74c2a192588769b 60 16 44 bf2cb2e6503c46373b52b10f32642d95a66a6636a3d7caaad0ce8b2b756781df`.
  - `test_r1_smoke_plist_runs_interactive_like_the_night_templates` OK.
  - No High Power marker; `sudo -n -l /bin/kill` rc 0; no r12; no campaign span; no stray monitor; no root powermetrics.
  - Network Time: Off; powermode 0. Kernel frequency word (`ntp_adjtime`, modes 0): offset 0, freq 0, status 0x2081; wall-raw rate +0.47 ppm over 1.15 s.
  - No `com.joulewise.night*` or `align-r0` agent loaded. Preflight `{"ac_power": true, "free_bytes": 88652206080, "disk_check": "report_only"}`.
  - Only other agent-family processes: this session's own Codex MCP adapter (`node scripts/codex-mcp-server.mjs` 86569, child of 86554, and its `codex app-server` 86572/86577). They exit with this session. No Codex child was started.
- `/Users/Shared/JouleWise/host-power/night.lock` left as found: `{"epoch_s": 1794702144.728242, "pid": 78902, "role": "r1-smoke-close"}`.
- No unread mail from Ed; no new directive issue (standing #587, #422, #421, #417, #416, #408, #405). Canonical root fast-forwarded to `5090e66fe` (no night label or plist).
- No email at launch: a diagnostic smoke is not an arm and nothing changed state for Ed. The report after the run goes to Ed and the lead (item 319 "Report").

If the launch command fails, this activation appends the failure to the custody file `r1-partc-w1line-out-f6c8a352.txt` before exiting and mails the lead. If that file has no failure line, launch returned rc 0 with a claimed fence.

Next activation: after the desk fence is gone, run item 319's "Check" block on OUT and report by email to Ed and the lead and as RUN_STATE 320. Blinding: print from `smoke_part_c.json` only `evaluation`, N_chunk and T_dead with item 319's script; never open it or `smoke.json` otherwise. Nothing is re-run. The second Part C (ITEM-PARTC2) reads this t0 and OUT from the custody file.
