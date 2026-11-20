# hp-01-s02 (L004-L007, High Power): launch by magistrate c939ffc4 (2026-11-15, RUN_STATE item 338)

Written just before the launch, which is this activation's last act. Campaign span 5 (hp-01's second span, four type-H legs); no session, no W1, nothing else queued.

- Scratch worktree: `/Users/edr/code/jw-wt/cadence-hp01-s02`, fresh, detached at `dd206025abb30fd5c07515cd4b34b3e653174810`, clean.
- PY: `/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv/bin/python` (not symlink-resolved; same venv as items 332, 335).
- MAGISTRATE_PID: 88334 (`/Users/edr/.local/bin/claude`).
- KIT `/Users/edr/campaign-out/kits/cl-hp-01-bbd34dc87.json`, re-written from `bbd34dc87`, sha256 `7eaf2660312ce6b3af90e8a1d9da1e05a6c409366a88a7e5e558d3bebb9d2965`.
- OUT `/Users/edr/campaign-out/cl-hp-01/cq-hp-01-s02-a1-20261115T130957Z`; DEADLINE 1794769007.79 (check time + 20,810 s = 10:56:47 PST).
- ARG `02:00-02:35` (check time 05:09:56 PST is in the 02:35:00-10:50:00 band). LAST_CLOSE_KIND campaign, GAP 300 s. PRIOR_CLOSE_EPOCH 1794746986 (the later of the hp-01-s01 receipt end 1794746700.82 = 04:45:00 and the 04:48:46 Check that saw the fence gone, taken at a one-minute upper bound 04:49:46).
- Dry tests (own TMPDIR, `JW_B5_SYNTHETIC_ONLY=1`, `/opt/homebrew/bin/python3.13 -B -m unittest`, one module at a time, 05:09 PST): `test_high_power` 50 OK; `test_legs_runner` 42 OK; `test_kit` 18 OK; `test_stops_desk` 14 OK; `test_runner_guards` 8 OK; `test_r1_smoke_launcher` 58 OK.
- Start and check: script `cadence-hp01-s02-check-c939ffc4.sh`, output `cadence-hp01-s02-out-c939ffc4.txt` (custody). Run 05:09:56-05:09:57 PST, rc 0, every line passed:
  - `verify_r1_executed_sources` returned `dd206025abb30fd5c07515cd4b34b3e653174810`.
  - Receipt census: 7 receipts; effective close 1794746701, newest receipt `/Users/edr/campaign-out/cl-hp-01/cq-hp-01-s01-a1-20261115T110527Z/runner_receipt.json` (campaign, agrees with LAST_CLOSE_KIND).
  - Journal-copy line: `cq-hp-01-s01-a1 copied 2026-11-15 04:53:21 PST | cq-hp-01-s01-a1-20261115T110527Z files=124 manifest_sha256=ae311e185d396f4b9d219e1015cf94923fe1098712d2fb7d9ee94fdf5166600b`.
  - `validate-kit --batch-window 02:00-02:35`: ok true, campaign_id cl-hp-01, frozen_commit `dd206025a…`, frozen_paths_verified true, kit sha `7eaf2660…d2965`, legs 12.
  - measurement_mode verify rc 1, one FAIL: "agent process present: 88357;88349 node scripts/codex-mcp-server.mjs;88350 npm exec @modelcontextprotocol/server-pdf". All in this magistrate's tree (88349 and 88350 are children of 88334; 88357 <- 88352 <- 88349), so NOTE 1 admits it. WARN: battery charge limit (want 80, got none); softwareupdate schedule (want off, got on; item 201). Every other line PASS or SKIP (kernel frequency word 0 among them).
  - `systemsetup -getusingnetworktime`: Off. Batch print: boot 2026-10-14 15:07:51 PDT; next OS batch 2026-11-16 02:08:39 PST.
  - No desk fence; `sudo -n -l /bin/kill` rc 0; no r12; other agent processes = only the four above (this magistrate's MCP children); no stray monitor; no root powermetrics; no night/smoke agent; `pmset -g` powermode 0; preflight `ac_power` true (free 75,977,498,624 bytes). Battery: ExternalConnected Yes, IsCharging No, InstantAmperage 0.
  - High Power preflight: `JOULEWISE_HOST_STATE_DIR` unset; no marker (no file, no link); `pmset -g custom` AC powermode 0; both sudo rules listed (`/usr/bin/pmset -c powermode 0` and `2`); `night.lock` no holder.
  - Plan rc 0: batch_windows `["02:00-02:35"]`, blackout_clear true, roster L004-L007 (seeds 954626506, 983646378, 2048410933, 1350544700), budget_s 1251 each, expected_s 8154, worst_case_s 19350, soak_s 1950, redo_quota 2, leg_cap_s 2700. Whole plan in the custody output file.
- Line 6: no open `cadence-stop` issue; no open `directive` issue by `mpmdw` is a STOP/NO/HALT/VETO (seven open, all older standing directives); no RESTORE_UNPROVEN open; no `high_power.revoked` (hp-01-s01 null, item 337).
- Host gate inputs for the Run block: HOST_RESTORE_OK=1 (latest close = `hp-01-s01`, restore proven and every restore line OK per item 337); OTHER_CLOSE_EPOCH=0 (no slot session or W1 since); SESSION_READY=no (no lead record of a READY v4 session; item 338 is the top item). The Run block (`cadence-hp01-s02-launch-c939ffc4.sh`) re-runs the census, copy gate, band and marker checks; its printed host last close, the launch epoch (t0), rc and launcher JSON go to the custody output file. A "LAUNCH FAILED" or "STOP" line there means nothing ran.
- The lead's alarm: t0 + 19,350 s (worst-case end) and t0 + 20,810 s (fence end); t0 is the `LAUNCH_EPOCH` line in the custody output file (expected about 05:15 PST, so worst-case end about 10:38, fence end about 11:02).
- Owner mail: no unread from Ed at launch; no new directive issue. Ed is emailed a short arm note before the launch.
- Record numbering: this launch record takes 339, so the Check that item 338 calls "RUN_STATE 339" will be the next free item (340).
