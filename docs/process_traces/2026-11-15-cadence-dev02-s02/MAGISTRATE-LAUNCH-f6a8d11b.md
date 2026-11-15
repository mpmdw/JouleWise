# dev-02-s02 (L001-L006, dev-02's Sunday half): launch by magistrate f6a8d11b (2026-11-15, RUN_STATE item 344)

Written just before the launch, which is this activation's last act. Campaign span 7 (1 dev-01 pilot, 2 dev-01-s03, 3 dev-01-s04, 4 hp-01-s01, 5 hp-01-s02, 6 hp-01-s03, 7 this span); six type-A legs; no session, no W1, nothing else queued.

**dev-02-s01 WITHDRAWN UNARMED (RL-165 §2).** It never ran and never arms.

- Scratch worktree: `/Users/edr/code/jw-wt/cadence-dev02-s02`, fresh, detached at `b4b6aeb192da60d895a7529311b06599efff5be4`, clean (`align/2026-11-14-campaign-runner` and `audit/2026-11-10-fable` fetched).
- PY: `/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv/bin/python` (not symlink-resolved; same venv as items 338-342).
- MAGISTRATE_PID: 10492 (`/Users/edr/.local/bin/claude`; supervisor 10488).
- SPAN `dev-02-s02`; LEGS L001,L002,L003,L004,L005,L006.
- KIT `/Users/edr/campaign-out/kits/cl-dev-02-589748f15-s02.json`, written from `589748f15:docs/process/cadence/kits/cl-dev-02.json`, sha256 `d963500b39af8867576ab07e2086c22ffd4a176c9e2d6eb60c80f65bc03728a8`.
- Queue: `b7a0d98822865a01e67fc3cc1833c9b186be2181:docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/QUEUE-cl-dev-02-b4b6aeb19-6plus6-append.json`, sha256 `ad0212ae0f57deea871ccb13ce8f8591ff3247ea406dc8e56dddc59f4f91ca2e` (asserted).
- OUT `/Users/edr/campaign-out/cl-dev-02/cq-dev-02-s02-a1-20261115T180023Z`; DEADLINE 1794791834.52 (check time + 26,210 s = 17:17:14 PST).
- ARG `02:00-02:35` (check time 10:00:23 PST is in the 02:35:00-10:50:00 band). LAST_CLOSE_KIND campaign, GAP 300 s. PRIOR_CLOSE_EPOCH 1794764943 (the later of the hp-01-s03 receipt end 1794764750.92 = 09:45:50 and the 09:49:03 Check that saw the fence gone, epoch 1794764943).
- Dry tests (own TMPDIR, `JW_B5_SYNTHETIC_ONLY=1`, `/opt/homebrew/bin/python3.13 -B -m unittest`, one module at a time, 09:59 PST): `test_legs_runner` 42 OK; `test_kit` 18 OK; `test_stops_desk` 14 OK; `test_runner_guards` 8 OK; `test_r1_smoke_launcher` 58 OK.
- Start and check: script `cadence-dev02-s02-check-f6a8d11b.sh` (item 344's block lines verbatim, with the inputs above prefixed and an env file written at the end), output `cadence-dev02-s02-out-f6a8d11b.txt` (custody). Run 10:00:21-10:00:24 PST, rc 0, every line passed:
  - `verify_r1_executed_sources` returned `b4b6aeb192da60d895a7529311b06599efff5be4`.
  - Receipt census: 9 receipts; newest `/Users/edr/campaign-out/cl-hp-01/cq-hp-01-s03-a1-20261115T152452Z/runner_receipt.json` (mtime 1794764750.92; campaign, agrees with LAST_CLOSE_KIND).
  - Journal-copy line: `cq-hp-01-s03-a1 copied 2026-11-15 09:55:29 PST | cq-hp-01-s03-a1-20261115T152452Z files=192 manifest_sha256=042585323ba9eac4d8ff70f6d5a6507a8cce7e00c8d6bee5798cf57933cd2de9`.
  - day_gate: `t0-date 2026-11-15: development legs already launched 5 (mixed-size 0) [('cq-dev-01-s04-a1-20261115T080002Z', 5)]; this span 6, mixed False` (11 of 24).
  - `validate-kit --batch-window 02:00-02:35`: ok true, campaign_id cl-dev-02, frozen_commit `b4b6aeb19…`, frozen_paths_verified true, kit sha `d963500b…28a8`, legs 12.
  - measurement_mode verify rc 1, one FAIL: "agent process present: 10515;10507 node scripts/codex-mcp-server.mjs;10508 npm exec @modelcontextprotocol/server-pdf". All in this magistrate's tree (10507, 10508 <- 10492; 10510 <- 10507; 10515 <- 10510), so NOTE 1 admits it. WARN: battery charge limit (want 80, got none); softwareupdate schedule (want off, got on; item 201). Every other line PASS or SKIP (kernel frequency word 0, network time Off, power source AC, not charging, free disk 65 GiB, no High Power marker among them). The host is in measurement_mode as applied 11-13 23:47 apart from those lines; network time is off (checked on the host).
  - `systemsetup -getusingnetworktime`: Off. Batch print: boot 2026-10-14 15:07:51 PDT; next OS batch 2026-11-16 02:08:39 PST.
  - No High Power marker; `night.lock` no holder; no desk fence; `sudo -n -l /bin/kill` rc 0; no r12; other agent processes = only the four above; no stray monitor; no root powermetrics; no night/smoke agent; `pmset -g` powermode 0; preflight `ac_power` true (free 70,419,210,240 bytes). Battery (#421): ExternalConnected Yes, IsCharging No, InstantAmperage 0.
  - Plan rc 0: batch_windows `["02:00-02:35"]`, blackout_clear true, roster L001-L006 (seeds 3407196167, 1200148396, 4048253495, 2129654160, 2522171568, 606134315), budget_s 1251 each, expected_s 10656, worst_case_s 24750, soak_s 1950, redo_quota 2, leg_cap_s 2700. Whole plan in the custody output file.
- Line 6: no open `cadence-stop` issue; no open `directive` issue by `mpmdw` is a STOP/NO/HALT/VETO (seven open, all older standing directives); no RESTORE_UNPROVEN; `hp-01-s03` `high_power.revoked` null (item 343).
- Host gate inputs for the Run block: HOST_RESTORE_OK=1 (latest close = `hp-01-s03`, restore proven, every restore line OK per item 343); OTHER_CLOSE_EPOCH=0 (no slot session or W1 since); SESSION_READY=no (no lead record of a READY v4 session; item 344 is the top item). The Run block (`cadence-dev02-s02-launch-f6a8d11b.sh`) re-runs the census, copy gate, day gate, band and marker checks; its printed host last close, the launch epoch (t0), rc and launcher JSON go to the custody output file. A "LAUNCH FAILED" or "STOP" line there means nothing ran.
- The lead's alarm: t0 + 24,750 s (worst-case end) and DEADLINE (fence end); t0 is the `LAUNCH_EPOCH` line in the custody output file (expected about 10:05 PST: expected end about 13:03, worst-case end about 16:57, fence end 17:17).
- Owner mail: no unread from Ed at launch; no new directive issue. Ed is emailed a short arm note before the launch.
- Record numbering: this launch record takes 345, so the Check that item 344 calls "RUN_STATE 345" will be the next free item (346).
