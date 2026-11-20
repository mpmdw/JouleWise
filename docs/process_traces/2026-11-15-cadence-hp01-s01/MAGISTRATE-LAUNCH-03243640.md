# hp-01-s01 (L001-L003, High Power smoke): launch by magistrate 03243640 (2026-11-15, RUN_STATE item 334)

Written just before the launch, which is this activation's last act. Campaign span 4 (hp-01's counted smoke, three type-H legs); no session, no W1, nothing else queued.

- Scratch worktree: `/Users/edr/code/jw-wt/cadence-hp01-s01`, fresh, detached at `dd206025abb30fd5c07515cd4b34b3e653174810`, clean.
- PY: `/Users/edr/night-custody/measurement/JouleWise-measurement-20261102-align-pilot2/.venv/bin/python` (not symlink-resolved; same venv as items 319, 323, 325, 332).
- MAGISTRATE_PID: 79569 (`/Users/edr/.local/bin/claude`).
- KIT `/Users/edr/campaign-out/kits/cl-hp-01-bbd34dc87.json` from `bbd34dc87`, sha256 `7eaf2660312ce6b3af90e8a1d9da1e05a6c409366a88a7e5e558d3bebb9d2965`.
- OUT `/Users/edr/campaign-out/cl-hp-01/cq-hp-01-s01-a1-20261115T110527Z`; DEADLINE 1794758838.25 (check time + 18,110 s = 08:07:18 PST).
- ARG `02:00-02:35` (check time 03:05:26 PST is in the 02:35:00-10:50:00 band). LAST_CLOSE_KIND campaign, GAP 300 s. PRIOR_CLOSE_EPOCH 1794739499 (the later of the s04 receipt end 1794739305.27 = 02:41:45 and the 02:44 Check that saw the fence gone, taken at its upper bound 02:44:59).
- Dry tests (own TMPDIR, `JW_B5_SYNTHETIC_ONLY=1`, `/opt/homebrew/bin/python3.13 -B -m unittest`, one module at a time, 03:04 PST): `test_high_power` 50 OK; `test_legs_runner` 42 OK; `test_kit` 18 OK; `test_stops_desk` 14 OK; `test_runner_guards` 8 OK; `test_r1_smoke_launcher` 58 OK.
- Preflight sudo read (the item's PREFLIGHT READ): `sudo -n -l` lists both `/usr/bin/pmset -c powermode 0` and `/usr/bin/pmset -c powermode 2`.
- Start and check: script `cadence-hp01-s01-check-03243640.sh`, output `cadence-hp01-s01-out-03243640.txt` (custody). Run 03:05:26-03:05:28 PST, rc 0, every line passed:
  - `verify_r1_executed_sources` returned `dd206025abb30fd5c07515cd4b34b3e653174810`.
  - Receipt census: 6 receipts; effective close 1794739306, newest receipt `/Users/edr/campaign-out/cl-dev-01/cq-dev-01-s04-a1-20261115T080002Z/runner_receipt.json` (campaign, agrees with LAST_CLOSE_KIND).
  - Journal-copy line: `cq-dev-01-s04-a1 copied 2026-11-15 02:56:15 PST | cq-dev-01-s04-a1-20261115T080002Z files=222 manifest_sha256=77dbfab97f6dbbe9774f1ad743ffc47aab278a550b171820b5be94484e462d4b | r1-partc2-c3f4-20261115T052325Z files=131 manifest_sha256=c42fad545ccd4f526d97f8664de25e52826c1fe43460b0f1cf89d215d67eeb0c`.
  - `validate-kit --batch-window 02:00-02:35`: ok true, campaign_id cl-hp-01, frozen_commit `dd206025a…`, frozen_paths_verified true, kit sha `7eaf2660…d2965`, legs 12.
  - measurement_mode verify rc 1, one FAIL: "agent process present: 79592;79584 node scripts/codex-mcp-server.mjs;79585 npm exec @modelcontextprotocol/server-pdf". All in this magistrate's tree (79584 and 79585 are children of 79569; 79592's parent 79587's parent is 79584), so NOTE 1 admits it. WARN: battery charge limit (want 80, got none); softwareupdate schedule (want off, got on; item 201). PASS: pmset powermode 0, network time Off, kernel frequency word 0, power source AC, not charging, no external volume, /private/tmp 1645 entries, free disk 72 GiB, no High Power marker, caffeinate assertion present.
  - `systemsetup -getusingnetworktime`: Off. Batch print: boot 2026-10-14 15:07:51 PDT; next OS batch 2026-11-16 02:08:39 PST.
  - No desk fence; `sudo -n -l /bin/kill` rc 0; no r12; no stray monitor; no root powermetrics; no night/smoke agent; `pmset -g` powermode 0; preflight `ac_power` true (free 77,967,024,128 bytes). Battery: ExternalConnected Yes, IsCharging No, InstantAmperage 0.
  - High Power preflight: `JOULEWISE_HOST_STATE_DIR` unset; no marker (no file, no link); `pmset -g custom` AC powermode 0; both sudo rules listed; `night.lock` no holder.
  - Plan rc 0: batch_windows `["02:00-02:35"]`, blackout_clear true, roster L001-L003 (seeds 4048693807, 1251089132, 3543179003), budget_s 1251 each, expected_s 6903, worst_case_s 16650, soak_s 1950, redo_quota 2, leg_cap_s 2700. Whole plan in the custody output file.
- Line 6: no open `directive` issue by `mpmdw` starting STOP/NO/HALT/VETO; no open `cadence-stop` issue; no RESTORE_UNPROVEN open (s04 closed clean, item 333).
- Host gate inputs for the Run block: HOST_RESTORE_OK=1 (latest close = `dev-01-s04`, every restore line OK per item 333); OTHER_CLOSE_EPOCH=0 (no slot session or W1 since); SESSION_READY=no (no lead record of a READY v4 session; item 334 is the top item). The Run block (`cadence-hp01-s01-launch-03243640.sh`) re-runs the census, copy gate, band and marker checks; its printed host last close, the launch epoch (t0), rc and launcher JSON go to the custody output file. A "LAUNCH FAILED" or "STOP" line there means nothing ran.
- The lead's alarm: t0 + 16,650 s (worst-case end) and t0 + 18,110 s (fence end); t0 is the `LAUNCH_EPOCH` line in the custody output file (expected about 03:08 PST, so worst-case end about 07:46, fence end about 08:10).
- Owner mail: no unread from Ed at launch; no new directive issue. Ed is emailed a short arm note before the launch.
- Record numbering: this launch record takes 335, so the Check that item 334 calls "RUN_STATE 335" will be the next free item (336).
