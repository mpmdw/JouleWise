# dev-01-s04 (L008-L012): launch by magistrate a1988f09 (2026-11-15, RUN_STATE item 331)

Written just before the launch, which is this activation's last act. Campaign span 3 of cl-dev-01; five counted development legs; no session, no W1.

- Scratch worktree: `/Users/edr/code/jw-wt/cadence-dev01-s04`, detached at `b4b6aeb192da60d895a7529311b06599efff5be4`, clean.
- PY: `/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv/bin/python` (not symlink-resolved; same venv as items 319, 323, 325).
- MAGISTRATE_PID: 43570 (`/Users/edr/.local/bin/claude`).
- SPAN `dev-01-s04`; LEGS `L008,L009,L010,L011,L012`.
- KIT `/Users/edr/campaign-out/kits/cl-dev-01-589748f15-s04.json` from `589748f15`, sha256 `c76344c50aebc271cef5711ecb4f9b05482e8b5593a57afa16e973dfe1dc66d7`.
- OUT `/Users/edr/campaign-out/cl-dev-01/cq-dev-01-s04-a1-20261115T080002Z`; DEADLINE 1794753113.393282 (check time + 23,510 s = 06:31:53 PST, inside the 10:50 bound).
- Dry tests (own TMPDIR, `JW_B5_SYNTHETIC_ONLY=1`, `/opt/homebrew/bin/python3.13 -B -m unittest`, one module at a time, 23:58 PST Sat): `test_legs_runner` 42 OK; `test_kit` 18 OK; `test_stops_desk` 14 OK; `test_runner_guards` 8 OK; `test_r1_smoke_launcher` 58 OK.
- Start and check: script `cadence-dev01-s04-check-a1988f09.sh`, output `cadence-dev01-s04-out-a1988f09.txt` (custody). A first run at 23:59:16 stopped on the script's own 00:00 window line before creating the kit or OUT; the rerun at 00:00:02 PST passed every line:
  - `verify_r1_executed_sources` returned `b4b6aeb192da60d895a7529311b06599efff5be4`.
  - `validate-kit --batch-window 13:14-13:15`: ok true, frozen_commit `b4b6aeb19…`, frozen_paths_verified true, kit sha `c76344c5…66d7`, legs 12.
  - measurement_mode verify rc 1, one FAIL: "agent process present: 43593;43585 node scripts/codex-mcp-server.mjs;43586 npm exec @modelcontextprotocol/server-pdf". All three are in the magistrate's own tree (43585 and 43586 are children of 43570; 43593's parent 43588's parent is 43585), so NOTE 1 admits it. WARN: battery charge limit (want 80, got none); softwareupdate schedule (want off, got on). PASS: network time Off, kernel frequency word 0, power source AC, not charging, no external volume, /private/tmp 1959 entries, free disk 75 GiB, no High Power marker, caffeinate assertion present.
  - `systemsetup -getusingnetworktime`: Off. No High Power marker; no desk fence; `sudo -n -l /bin/kill` rc 0; no r12; no stray monitor; no root powermetrics; no night/smoke agent; powermode 0; preflight ac_power true.
  - Battery: ExternalConnected Yes, IsCharging No, InstantAmperage 0.
  - Plan rc 0: batch_windows `["13:14-13:15"]`, blackout_clear true, roster L008-L012, budget_s 1251 each, expected_s 9405, worst_case_s 22050, soak_s 1950, redo_quota 2. Whole plan in the custody output file.
- Line 6: no open `directive` issue by `mpmdw` starting STOP/NO/HALT/VETO; no open `cadence-stop` issue; no named stop from `dev-01-s03` (item 326) or the second Part C (item 328).
- Host gate inputs for the Run block: HOST_RESTORE_OK=1 (latest close = the second Part C, receipt mtime 1794727353 = 23:22:33 PST, restore clean per item 328); OTHER_CLOSE_EPOCH=0 (no slot session or W1 since); SESSION_READY=no and SESSION_T0=none (item 331 is the top item; no session is staged). The receipt census runs inside the launch script; its printed host last close and the launch epoch, rc and launcher JSON go to the custody output file. A "LAUNCH FAILED" line there means nothing ran.
- No Ed mail unread at launch. Ed is emailed a short arm note before the launch.
