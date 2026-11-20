# dev-03-s02 (dev-03's remainder, L004-L012, nine legs) pre-launch record, magistrate abc54ff5 (headless, Opus 5.5), 2026-11-16 ~07:52 PST

Item 366 run as written. Start and check: custody `cadence-dev03-s02-check-abc54ff5.sh` (item 366's Start-and-check block, extracted mechanically from RUN_STATE on main `dff82ba93`, every line verbatim (`grep -vxF` against the extract leaves nothing), preceded by the inputs file `cadence-dev03-s02-inputs-abc54ff5.sh`); output custody `cadence-dev03-s02-out-abc54ff5.txt` (Start-and-check part reproduced below). Run: custody `cadence-dev03-s02-launch-abc54ff5.sh` = the same Start-and-check lines re-run on fresh state, then item 366's Run block verbatim except that the launcher's JSON goes to `cadence-dev03-s02-launch-abc54ff5.json` and `LAUNCH_RC`/`LAUNCH_EPOCH` are printed (as the pilot's launch). The launch is the activation's last action; it is held until the close interval after F0 run 4 has passed (07:51:38 PST).

Dry tests (8 modules, fresh worktree `/Users/edr/code/jw-wt/cadence-dev03-rest` at `2d347f721`, clean, own TMPDIR, `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONPATH=.:tests`, homebrew python3.13 `-B -m unittest`, one at a time): test_kit_v11 30 OK, test_span_reference 19 OK, test_legs_runner 42 OK, test_kit 18 OK, test_stops_desk 14 OK, test_runner_guards 8 OK, test_launch_cadence_span 12 OK, align.test_r1_smoke_launcher 58 OK (custody `cadence-dev03-s02-tests-abc54ff5.txt`).

Inputs: PY align-pilot2 venv; MAGISTRATE_PID 92733; PRIOR_CLOSE_EPOCH 1794834969 (later of dev-03-s01's receipt close 1794834607.15 and its fence pid 75682 seen gone in the d59960c1 Check, by 05:16:09); LAST_CLOSE_KIND other (newest close is STANDING-F0 run 4, 07:31:37), GAP 1,200 s; OTHER_CLOSE_EPOCH 0; HOST_RESTORE_OK 1 (RUN_STATE 368); SESSION_READY no (no lead READY record on main `dff82ba93`).

Withdrawn unarmed by this arm record (item 366): `dev-03-s02b` and `dev-03-s03b`. Queue commit `b7a0d98822865a01e67fc3cc1833c9b186be2181`, sha256 `366662ce…3fbb` (asserted). Kit `/Users/edr/campaign-out/kits/cl-dev-03.v1.1-9cbb365a6-s02.json`, sha256 `0f535774…e14b`.

Journal copy: the newest close is a non-campaign F0 (copy gate: its Check covers the copy). The pilot's copy marker `cq-dev-03-s01-a1.ok` (lead's Air copy, 05:22:53) is recorded in item 364.

measurement_mode NOTE 1: the one FAIL names 92748 (node codex-mcp-server, ppid 92733), 92749 (npm server-pdf, ppid 92733) and 92752 (codex app-server under 92751 under 92748): all this magistrate's tree; they end when it exits. WARN lines (battery limit syntax, softwareupdate schedule) recorded, not gates. Free disk 66 GiB (60 GiB line); nine legs use roughly 5-7 GiB, so the next arm (dev-04-s01, Tue) may meet the line: the item-360 remedy (evict local copies of iCloud-held archive) or the lead clearing journals already copied off.

Plan: batch_windows ["02:00-02:35"], runner_kind cadence-legs-v1.1, expected 15,163 s, worst case 32,850 s, blackout_clear true, soak 1,950 s, redo quota 2; budgets L004 1,156 (capture, span), L005 1,076, L006 1,251, L007 1,156, L008 1,467 (consume), L009 1,642 (consume), L010 1,467 (consume), L011 1,251, L012 1,547 (consume). From a ~07:52 t0: expected end ~12:05, worst case ~17:00, fence end ~17:24 PST (well before 01:50 Tue).

## Start-and-check output (07:40:28-07:40:30, measurement_mode PASS/SKIP lines kept in custody)

```
== start-and-check Mon Nov 16 07:40:28 PST 2026 epoch 1794843628
From https://github.com/mpmdw/JouleWise
 * branch                align/2026-11-14-kit-v1-1 -> FETCH_HEAD
92733 /Users/edr/.local/bin/claude
close interval GAP 1200 s (RL-171 §6.1; 1,200 s after a Part C or F0, F2, a slot session or W1)
ARG 02:00-02:35 (RL-171 §3: 02:00-02:35 where this pin's own plan admits the t0, else the data-only 13:14-13:15)
SPAN dev-03-s02 LEGS L004,L005,L006,L007,L008,L009,L010,L011,L012
2d347f721552fe03bdd19f113e7bad7a7c24908e
census: 16 receipts, newest mtime 1794843097.1074474 /Users/edr/code/jw-wt/partc-b2e01464d/.desk/r1-partc-f0-20261116T133233Z/runner_receipt.json
copy gate: newest close is non-campaign (/Users/edr/code/jw-wt/partc-b2e01464d/.desk/r1-partc-f0-20261116T133233Z/runner_receipt.json); its Check covers the copy
t0-date 2026-11-16: development legs already launched 9 (mixed-size 3) [('cq-dev-02-s03-a1-20261116T080253Z', 6), ('cq-dev-03-s01-a1-20261116T113830Z', 3)]; this span 9, mixed True
PRED CLEAN dev-03-s01 /Users/edr/campaign-out/cl-dev-03/cq-dev-03-s01-a1-20261116T113830Z: rc 0, 3 of 3 legs, MEASURED_OK COMPLETE, close steps rc 0, overtime legs 0, contaminated redos 0, close_epoch 1794834608
expiry: this item is valid until 2026-11-17 05:38:05 PST (RL-173 D.5)
{"campaign_id": "cl-dev-03", "frozen_commit": "2d347f721552fe03bdd19f113e7bad7a7c24908e", "frozen_paths_verified": true, "kit_sha256": "0f535774b413654d9d72b153a7dc8369df81575b34c5fa120898d76dfe04e14b", "legs": 12, "ok": true}
From https://github.com/mpmdw/JouleWise
 * branch                audit/2026-11-10-fable -> FETCH_HEAD
== measurement_mode verify 2026-11-16T15:40:29Z
WARN  battery charge limit: want 80, got none (syntax unverified on 26.6.2)
WARN  softwareupdate schedule: want off, got on (known non-persistent on 26.6.2, RUN_STATE 201)
FAIL  agent process present: 92752;92748 node scripts/codex-mcp-server.mjs;92749 npm exec @modelcontextprotocol/server-pdf --stdio HOME=/Users/edr LOGNAME=edr PATH=/Users/edr/.local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin SHELL=/bin/zsh;
INFO  display power state:  | "IOPowerManagement" = {"CapabilityFlags"=32768,"MaxPowerState"=1,"CurrentPowerState"=1} | "IOPowerManagement" = {"CapabilityFlags"=32768,"MaxPowerState"=1,"CurrentPowerState"=1}  (launch_align_r0.py runs displaysleepnow + dwell per span; not a gate)
VERIFY FAILED: 1 mismatch(es)
verify rc 1
Network Time: Off
boot 2026-10-14 15:07:51 PDT; next OS batch 2026-11-17 02:08:39 PST (boot + 12 h + 48 s + whole days)
night.lock: no holder
sudo kill rc 0
no r12
92748 node scripts/codex-mcp-server.mjs
92749 npm exec @modelcontextprotocol/server-pdf --stdio HOME=/Users/edr LOGNAME=edr PATH=/Users/edr/.local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin SHELL=/bin/zsh
92751 node /opt/homebrew/bin/codex app-server
92752 /opt/homebrew/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex app-server
no stray monitor
no root powermetrics
no night/smoke agent
 powermode            0
{"ac_power": true, "free_bytes": 71695396864, "disk_check": "report_only"}
{
 "batch_windows": [
  "02:00-02:35"
 ],
 "blackout_clear": true,
 "campaign_id": "cl-dev-03",
 "deadline_epoch_s": 1794876480.7257159,
 "expected_s": 15163,
 "fence_end_epoch_s": 1794877940.7257159,
 "fixed_overhead_s": 1200,
 "kit_sha256": "0f535774b413654d9d72b153a7dc8369df81575b34c5fa120898d76dfe04e14b",
 "launch_deadline_epoch_s": 1794877040.7257159,
 "leg_cap_s": 2700,
 "legs": [ ... nine legs as listed above ... ],
 "redo_quota": 2,
 "runner_kind": "cadence-legs-v1.1",
 "schema": "joulewise.cadence_span_plan.v1",
 "soak_s": 1950,
 "t0_epoch_s": 1794843630.7257159,
 "time_model": {
  "decode_tokens_per_s": 12.03,
  "fixed_s": 500.0,
  "g0_s": 209.0,
  "prefill_s_per_token": 0.005,
  "span_g0_s": 600.0,
  "warmup_extra_s": 6.0
 },
 "worst_case_s": 32850
}
OUT=/Users/edr/campaign-out/cl-dev-03/cq-dev-03-s02-a1-20261116T154029Z
DEADLINE=1794877940.7499158
KIT=/Users/edr/campaign-out/kits/cl-dev-03.v1.1-9cbb365a6-s02.json 0f535774b413654d9d72b153a7dc8369df81575b34c5fa120898d76dfe04e14b
== start-and-check end Mon Nov 16 07:40:30 PST 2026 epoch 1794843630
```

The OUT, DEADLINE and plan t0 above belong to the 07:40 Start and check; the Run re-computes them on fresh state, and the launched OUT, t0 and rc are in custody `cadence-dev03-s02-out-abc54ff5.txt` and `cadence-dev03-s02-launch-abc54ff5.json`.
