# dev-03-s01 (dev-03 counted pilot, kit v1.1 class A smoke) pre-launch record, magistrate f845859d (headless, Opus 5.5), 2026-11-16 03:38 PST

Item 355 run as written. Start and check: custody `cadence-dev03-s01-check-f845859d.sh` (lines 2-295 of item 355's Start-and-check block, extracted mechanically from RUN_STATE on main `f899dba5a`, preceded by the inputs file `cadence-dev03-s01-inputs-f845859d.sh`); output custody `cadence-dev03-s01-out-f845859d.txt` (Start-and-check part reproduced below; every PASS line of measurement_mode kept in custody). Run: custody `cadence-dev03-s01-launch-f845859d.sh` = the same Start-and-check lines re-run on fresh state, then the Run block (lines 303-338) with the launcher's JSON captured to `cadence-dev03-s01-launch-f845859d.json` and `LAUNCH_RC`/`LAUNCH_EPOCH` printed. The launch is the activation's last action.

Dry tests (8 modules, worktree `/Users/edr/code/jw-wt/cadence-dev03-s01` at `2d347f721`, clean, own TMPDIR, `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONPATH=.:tests`, homebrew python3.13 `-B -m unittest`, one at a time): test_kit_v11 30 OK, test_span_reference 19 OK, test_legs_runner 42 OK, test_kit 18 OK, test_stops_desk 14 OK, test_runner_guards 8 OK, test_launch_cadence_span 12 OK, align.test_r1_smoke_launcher 58 OK (custody `cadence-dev03-s01-tests-f845859d.txt`).

Inputs: PY align-pilot2 venv; MAGISTRATE_PID 72616; PRIOR_CLOSE_EPOCH 1794827985 (later of dev-02-s03's receipt close 1794827163.90 and fence pid 59613 seen gone 03:19:45); LAST_CLOSE_KIND campaign, GAP 300 s; OTHER_CLOSE_EPOCH 0; HOST_RESTORE_OK 1 (RUN_STATE 361); SESSION_READY no (no lead READY record on main).

Journal copy (items 347/348, RL-173 A): the lead's marker `cq-dev-02-s03-a1.ok` was absent at close + 30 min (03:36:04); the MBP cloud offload ran 03:36:11-03:37:11 (custody `offload-dev02-s03-f845859d.sh`, `offload-dev02-s03-run-f845859d.sh`, output `offload-dev02-s03-out-f845859d.txt`, brctl log `offload-dev02-s03-brctl-f845859d.txt`). iCloud Drive `JouleWise-offload/cq-dev-02-s03-a1/`; encrypted archive sha256 `1756d49930eeb9e5aee563402c06935ce8e3015f52c841506beb1769e73bbb3d`; manifest 256 files, sha256 `5d02993731f4f3a68c68f048342d4a70772b6c7d77de5c96002adf96298de00b` (includes the Check's `maintenance-log.txt`/`.err`); cloud copy hash check OK; decrypt-and-list of the cloud copy 342 entries; key as item 350 (MBP + Air copy). Upload evidence: brctl at 03:36:44 three `needs-upload` lines; at 03:37:11 none, client idle, caught-up, last-sync 03:36:47 after the copy finished 03:36:32. Marker written 03:37:11 under `test ! -e`. **Path that wrote the marker: MBP cloud offload.**

measurement_mode NOTE 1: the one FAIL names 72631 (node codex-mcp-server, ppid 72616), 72632 (npm server-pdf, ppid 72616) and 72639 (codex app-server under 72634 under 72631): all this magistrate's tree; they end when it exits. WARN lines (battery limit syntax, softwareupdate schedule) recorded, not gates. Free disk 63 GiB at 03:37 (60 GiB line); the span uses about 5 GiB, so the next arm meets the line (lead: evict more uploaded archive or clear journals already copied off the host).

Plan: batch_windows ["02:00-02:35"], runner_kind cadence-legs-v1.1, expected 7,024 s, worst case 16,650 s, blackout_clear true, budgets L001 1,076 s, L002 1,642 s (g0_role consume, g0_shape span), L003 1,156 s, redo quota 2, fence end ~08:16 PST (well before 01:50 Tue).

## Start-and-check output

```
== start-and-check Mon Nov 16 03:37:23 PST 2026 epoch 1794829043
From https://github.com/mpmdw/JouleWise
 * branch                align/2026-11-14-kit-v1-1 -> FETCH_HEAD
72616 /Users/edr/.local/bin/claude
close interval GAP 300 s (RL-171 §6.1; 1,200 s after a Part C or F0, F2, a slot session or W1)
ARG 02:00-02:35 (RL-171 §3: 02:00-02:35 where this pin's own plan admits the t0, else the data-only 13:14-13:15)
2d347f721552fe03bdd19f113e7bad7a7c24908e
census: 14 receipts, newest mtime 1794827163.9046054 /Users/edr/campaign-out/cl-dev-02/cq-dev-02-s03-a1-20261116T080253Z/runner_receipt.json
journal copy of cq-dev-02-s03-a1: cq-dev-02-s03-a1 cloud-offload Mon Nov 16 03:37:11 PST 2026 | provider /Users/edr/Library/Mobile Documents/com~apple~CloudDocs (iCloud Drive) JouleWise-offload/cq-dev-02-s03-a1 | enc sha256 1756d49930eeb9e5aee563402c06935ce8e3015f52c841506beb1769e73bbb3d | manifest sha256 5d02993731f4f3a68c68f048342d4a70772b6c7d77de5c96002adf96298de00b files=256 | upload evidence brctl status com.apple.CloudDocs 03:37:11: no needs-upload, client idle, caught-up, last-sync 2026-11-16 03:36:47 after the copy at 2026-11-16 03:36:32; magistrate f845859d
t0-date 2026-11-16: development legs already launched 6 (mixed-size 0) [('cq-dev-02-s03-a1-20261116T080253Z', 6)]; this span 3, mixed True
PRED CLEAN dev-02-s03 /Users/edr/campaign-out/cl-dev-02/cq-dev-02-s03-a1-20261116T080253Z: rc 0, 6 of 6 legs, MEASURED_OK COMPLETE, close steps rc 0, overtime legs 0, contaminated redos 1, close_epoch 1794827164
expiry: this item is valid until 2026-11-16 15:42:10 PST (RL-173 D.5)
KIT exists from an earlier Start of this item (a WAIT retry): re-written from git below, sha asserted
{"campaign_id": "cl-dev-03", "frozen_commit": "2d347f721552fe03bdd19f113e7bad7a7c24908e", "frozen_paths_verified": true, "kit_sha256": "0f535774b413654d9d72b153a7dc8369df81575b34c5fa120898d76dfe04e14b", "legs": 12, "ok": true}
From https://github.com/mpmdw/JouleWise
 * branch                audit/2026-11-10-fable -> FETCH_HEAD
== measurement_mode verify 2026-11-16T11:37:25Z
SKIP  pmset ac autopoweroff: not reported by pmset on this Mac
SKIP  pmset batt autopoweroff: not reported by pmset on this Mac
SKIP  pmset ac proximitywake: not reported by pmset on this Mac
SKIP  pmset batt proximitywake: not reported by pmset on this Mac
SKIP  pmset ac lowpowermode: not reported by pmset on this Mac
SKIP  pmset batt lowpowermode: not reported by pmset on this Mac
SKIP  time machine AutoBackup: inert, no destination
WARN  battery charge limit: want 80, got none (syntax unverified on 26.6.2)
WARN  softwareupdate schedule: want off, got on (known non-persistent on 26.6.2, RUN_STATE 201)
FAIL  agent process present: 72639;72631 node scripts/codex-mcp-server.mjs;72632 npm exec @modelcontextprotocol/server-pdf --stdio HOME=/Users/edr LOGNAME=edr PATH=/Users/edr/.local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin SHELL=/bin/zsh;
INFO  display power state:  | "IOPowerManagement" = {"CapabilityFlags"=32768,"MaxPowerState"=1,"CurrentPowerState"=1} | "IOPowerManagement" = {"CapabilityFlags"=32768,"MaxPowerState"=1,"CurrentPowerState"=1}  (launch_align_r0.py runs displaysleepnow + dwell per span; not a gate)
VERIFY FAILED: 1 mismatch(es)
verify rc 1
Network Time: Off
boot 2026-10-14 15:07:51 PDT; next OS batch 2026-11-17 02:08:39 PST (boot + 12 h + 48 s + whole days)
night.lock: no holder
sudo kill rc 0
no r12
72631 node scripts/codex-mcp-server.mjs
72632 npm exec @modelcontextprotocol/server-pdf --stdio HOME=/Users/edr LOGNAME=edr PATH=/Users/edr/.local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin SHELL=/bin/zsh
72634 node /opt/homebrew/bin/codex app-server
72639 /opt/homebrew/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex app-server
no stray monitor
no root powermetrics
no night/smoke agent
 powermode            0
{"ac_power": true, "free_bytes": 68092977152, "disk_check": "report_only"}
{
 "batch_windows": [
  "02:00-02:35"
 ],
 "blackout_clear": true,
 "campaign_id": "cl-dev-03",
 "deadline_epoch_s": 1794845696.3195362,
 "expected_s": 7024,
 "fence_end_epoch_s": 1794847156.3195362,
 "fixed_overhead_s": 1200,
 "kit_sha256": "0f535774b413654d9d72b153a7dc8369df81575b34c5fa120898d76dfe04e14b",
 "launch_deadline_epoch_s": 1794846256.3195362,
 "leg_cap_s": 2700,
 "legs": [
  {
   "budget_s": 1076,
   "campaign_id": "cl-dev-03",
   "decode_tokens": 4096,
   "leg_id": "L001",
   "prefill_chars": 4111,
   "prefill_tokens": 2000,
   "quiet_s": 0,
   "schema": "joulewise.cadence_leg_spec.v1",
   "seed": 4129284831,
   "start_band": "q0"
  },
  {
   "budget_s": 1642,
   "campaign_id": "cl-dev-03",
   "decode_tokens": 4096,
   "g0_role": "consume",
   "g0_shape": "span",
   "leg_id": "L002",
   "prefill_chars": 40000,
   "prefill_tokens": 19458,
   "quiet_s": 0,
   "schema": "joulewise.cadence_leg_spec.v1.1",
   "seed": 319096281,
   "start_band": "q0"
  },
  {
   "budget_s": 1156,
   "campaign_id": "cl-dev-03",
   "decode_tokens": 4096,
   "leg_id": "L003",
   "prefill_chars": 20557,
   "prefill_tokens": 10000,
   "quiet_s": 0,
   "schema": "joulewise.cadence_leg_spec.v1",
   "seed": 512394455,
   "start_band": "q0"
  }
 ],
 "redo_quota": 2,
 "runner_kind": "cadence-legs-v1.1",
 "schema": "joulewise.cadence_span_plan.v1",
 "soak_s": 1950,
 "t0_epoch_s": 1794829046.3195362,
 "time_model": {
  "decode_tokens_per_s": 12.03,
  "fixed_s": 500.0,
  "g0_s": 209.0,
  "prefill_s_per_token": 0.005,
  "span_g0_s": 600.0,
  "warmup_extra_s": 6.0
 },
 "worst_case_s": 16650
}
== check done Mon Nov 16 03:37:26 PST 2026 epoch 1794829046
```
