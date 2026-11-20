# RL-145 close §8 Part C smoke: launch by magistrate b8fdbe1b (2026-11-13, RUN_STATE item 315)

Written just before the launch, which is this activation's last act. A diagnostic: no slots, no arm, no session, no W1.

- Smoke worktree: `/Users/edr/code/jw-wt/r1-followup-smoke`, detached at `f006b7aa665280253db10d7a167599ff385fcec4`, clean. **Decision I made:** that path no longer existed (item 2796 had marked it superseded and removable, and it was cleaned up), so I re-created it with `git worktree add --detach` at the smoke sha, as earlier items' `test -d … || git worktree add` lines did. Nothing from earlier OUT directories was reused.
- Mode: `--fresh-soak --parts C`. Replaces the Part A smoke on `c3dbc33ed`; that one is not run.
- PY: `/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv/bin/python` (same measurement venv as items 273-285). Not symlink-resolved.
- MAGISTRATE_PID: 44337 (`/Users/edr/.local/bin/claude`).
- OUT: `/Users/edr/code/jw-wt/r1-followup-smoke/.desk/r1-partc-smoke-20261114T052520Z` (also in `/Users/edr/night-custody/magistrate/r1-partc-out-b8fdbe1b.txt`). Fresh.
- DEADLINE: launch time + 14,400 s, computed at launch; the exact value and launch time are in the custody file above. Launch at about 21:30 PST Fri 13 Nov, before the 02:15 PST cutoff. Worst-case end (launch + 12,180 s) is about 00:55 PST, so 00:00 probably falls inside the span (midnight `/private/tmp` walk, item 29; not a gate). The next activation records whether it did.
- Dry checks (scratch worktree detached at the full sha, own TMPDIR, `JW_B5_SYNTHETIC_ONLY=1`, `python3.13 -B -m unittest`, one module at a time): `test_rl145_gate_hashes` 1 OK; `test_rl145_part_c` 22 OK; `test_r1_smoke_launcher` 58 OK; `test_v4_registration` 24 OK. `test_refusal_allowlist` not run, as item 315 says.
- Start-and-check block: all passed.
  - HEAD = full sha; `a6a09e6d7` is an ancestor; tree clean.
  - The ten condition-13 hashes match item 315's table and item 306's six prefixes.
  - `verify_r1_executed_sources` returned `f006b7aa665280253db10d7a167599ff385fcec4`.
  - `RL-89 MAC CHECK OK e6231a8f3e6ab6177bbedbf12b878c958a7b4d4331e36472c74c2a192588769b 60 16 44 bf2cb2e6503c46373b52b10f32642d95a66a6636a3d7caaad0ce8b2b756781df`.
  - `test_r1_smoke_plist_runs_interactive_like_the_night_templates` OK.
  - No High Power marker; `sudo -n -l /bin/kill` rc 0; no r12 process; no stray monitor; no root powermetrics.
  - Network Time: Off; powermode 0. Kernel frequency word read with `ntp_adjtime` (modes 0): offset 0, freq 0, status 0x2081.
  - No `com.joulewise.night*` or `align-r0` agent loaded; no desk fence present. Preflight `{"ac_power": true, "free_bytes": 90362388480, "disk_check": "report_only"}`.
  - Only other agent-family processes: this session's own Codex MCP adapter (`node scripts/codex-mcp-server.mjs` 44352, child of 44337, and its `codex app-server` 44355/44356). They exit with this session. No Codex child was started.
- `/Users/Shared/JouleWise/host-power/night.lock` left as found: `{"epoch_s": 1794618287.072775, "pid": 95360, "role": "night-close:align-r1-20261113T1508Z"}`.
- No unread mail from Ed; no new directive issue (standing #587, #422, #421, #417, #416, #408, #405). Canonical root fast-forwarded to `fa7aa9417`.
- No email at launch: a smoke is not an arm, and nothing changed state for Ed. The report after the run goes to Ed and the lead (item 315 "Report").

If the launch command fails, this activation appends the failure to the custody file `r1-partc-out-b8fdbe1b.txt` before exiting and mails the lead. If that file has no failure line, launch returned rc 0 with a claimed fence.

Next activation: after the desk fence is gone, run item 315's "Check" block on OUT and report by email to Ed and the lead and as RUN_STATE 316. Blinding: print from `smoke_part_c.json` only `evaluation`, N_chunk and T_dead with item 315's script; never open it or `smoke.json` otherwise. Nothing is re-run.
