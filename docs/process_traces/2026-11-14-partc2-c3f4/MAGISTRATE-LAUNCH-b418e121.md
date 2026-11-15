# Second Part C at c3f4bacd8: launch by magistrate b418e121 (2026-11-14, RUN_STATE item 325)

Written just before the launch, which is this activation's last act. A diagnostic: no slots, no arm, no session, no W1. Run 3 of tonight's order (RL-155a §1.2); filler F0, journals only. Supersedes item 324, which did not launch (no `r1-partc2-w1line-*` OUT or custody record).

- Smoke worktree: `/Users/edr/code/jw-wt/partc-c3f4`, detached at `c3f4bacd8013ca98c19cf8d41f830c701930cd41`, clean; `f30a97d00`, `a6a09e6d7` and `f006b7aa6` are ancestors; `git diff 0ec600128 HEAD` empty.
- Mode: `--fresh-soak --parts C`.
- PY: `/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv/bin/python` (not symlink-resolved; same venv as items 319 and 323).
- MAGISTRATE_PID: 30940 (`/Users/edr/.local/bin/claude`).
- OUT1 (first Part C, item 319): `/Users/edr/code/jw-wt/partc-w1line/.desk/r1-partc-w1line-20261115T004253Z`; T0_1 1794703408 (16:43:28 PST); F0 spacing met from 20:43:28 PST.
- LAST_RECEIPT: the sub-span's `/Users/edr/campaign-out/cl-dev-01/cq-dev-01-s03-a1-20261115T030242Z/runner_receipt.json`; LAST_CLOSE (mtime) 1794718908 = 21:01:48 PST; 20-minute gate 21:21:48 PST. Item 319's Check (item 322) and the sub-span's Check (item 326) name no "restore unproven", host-state stop or High Power marker.
- OUT, DEADLINE (min(launch + 14,400 s, 1794735000 = 01:30:00 PST Sun 15 Nov); the cap binds after 21:30) and the launch epoch: in `/Users/edr/night-custody/magistrate/r1-partc2-c3f4-out-b418e121.txt`. A launch after 20:57 can run through the 00:00 `/private/tmp` walk; the next activation records whether it did.
- Dry checks (scratch worktree `partc-c3f4-dry` detached at the full sha, own TMPDIR, `JW_B5_SYNTHETIC_ONLY=1`, `/opt/homebrew/bin/python3.13 -B -m unittest`, one module at a time, 21:04-21:08 PST): `test_rl145_gate_hashes` 1 OK; `test_rl145_part_c` 31 OK; `test_pr777_attack_repros` 15 OK; `test_r1_smoke_launcher` 58 OK; `test_v4_registration` 24 OK; `hazards.test_refusal_allowlist` 24 OK (skipped=1). Same counts as the Air pre-check. Scratch worktree removed.
- Start-and-check block: script `/Users/edr/night-custody/magistrate/partc2-c3f4-startcheck-b418e121.sh`, output `partc2-c3f4-startcheck-out-b418e121.txt` (custody). All passed at 21:22:36 PST (rc 0).
  - The first run at 21:22:24 stopped on a bug in the script's own item-324 check (with no matching file, `ls -d` got no argument and listed `.`); fixed to a zsh null-glob array and rerun. It stopped before creating the worktree; item 324's OUT and custody record are absent.
  - The seventeen hashes match item 325's two tables (`partc2-c3f4-hashes-b418e121.txt` in custody).
  - `verify_r1_executed_sources` returned `c3f4bacd8013ca98c19cf8d41f830c701930cd41`.
  - `RL-89 MAC CHECK OK e6231a8f3e6ab6177bbedbf12b878c958a7b4d4331e36472c74c2a192588769b 60 16 44 272aecb8bc0d9e33defd7f686b129ea236b925fdfbf68137697120dd63232f46`.
  - `test_r1_smoke_plist_runs_interactive_like_the_night_templates` OK.
  - No High Power marker; `sudo -n -l /bin/kill` rc 0; no r12; no campaign span; no stray monitor; no root powermetrics.
  - Network Time: Off; powermode 0. Kernel frequency word (`ntp_adjtime`, modes 0): offset 0, freq 0, status 0x2081; wall-raw rate +3.21 ppm over 1.15 s (recorded, not a gate).
  - No `com.joulewise.night*` or `align-r0` agent loaded. Preflight `{"ac_power": true, "free_bytes": 83631919104, "disk_check": "report_only"}`. Battery: ExternalConnected Yes, IsCharging No, InstantAmperage 0.
  - Only other agent-family processes: this session's own Codex MCP adapter (`node scripts/codex-mcp-server.mjs` 30955, child of 30940, and its `codex app-server` 30958/30959) and the PDF MCP server 30956 (child of 30940). They exit with this session. No Codex child was started.
  - `night.lock` read: `{"epoch_s": 1794718894.063314, "pid": 22775, "role": "r1-smoke-close"}`.
- `/Users/Shared/JouleWise/host-power/night.lock` left as found.
- No unread mail from Ed; no open STOP/NO/HALT/VETO directive; no open `cadence-stop` issue.
- Email: one short email to Ed with the sub-span result (item 326) and this launch, sent before the launch.

If the launch command fails, this activation appends the failure to the custody file `r1-partc2-c3f4-out-b418e121.txt` before exiting and mails the lead. If that file has no failure line, launch returned rc 0 with a claimed fence.

Next activation: after the desk fence is gone, run item 325's "Check" block on OUT and report by email to Ed and the lead and as the next RUN_STATE item, with item 319's (item 322's) `pass` beside each `lines` entry. Blinding: print from `smoke_part_c.json` only `evaluation`, N_chunk and T_dead with item 325's script; never open it or `smoke.json` otherwise. Nothing is re-run. After this run the night is quiet (no further Part C or campaign span tonight; Sunday's 02:40 span needs its own lead item).
