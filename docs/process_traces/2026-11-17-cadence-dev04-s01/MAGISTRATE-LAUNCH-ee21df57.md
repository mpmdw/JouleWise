# dev-04-s01 (block dev-04's first span, L001-L006, six legs) pre-launch record, magistrate ee21df57 (headless, Opus 5.5), 2026-11-17 ~00:01 PST

Item 367 run as written. Start and check: custody `cadence-dev04-s01-check-ee21df57.sh` (item 367's Start-and-check block, extracted mechanically from RUN_STATE on main `f375aa994`, lines 1647-1944), preceded by the inputs file `cadence-dev04-s01-inputs-ee21df57.sh` and followed by three print lines (OUT, DEADLINE, KIT). One change to the item's text: its three `git -C /Users/edr/code/JouleWise fetch origin …` lines are replaced by `git cat-file -e <commit>^{commit}` presence checks of the three commits they exist to bring in (`2d347f721`, `fecaf73f3`, `b7a0d9882`), all already local; the canonical root takes no fetch (launch-prompt rule: no git operation there but the ff). Output custody `cadence-dev04-s01-out-ee21df57.txt` (Start-and-check part reproduced below). Run: custody `cadence-dev04-s01-launch-ee21df57.sh` = the same Start-and-check lines re-run on fresh state, then item 367's Run block verbatim except that the launcher's JSON goes to `cadence-dev04-s01-launch-ee21df57.json` and `LAUNCH_RC`/`LAUNCH_EPOCH` are printed (as abc54ff5's launch). The launch is the activation's last action.

Dry tests (8 modules, fresh worktree `/Users/edr/code/jw-wt/cadence-dev-04-s01` at `2d347f721`, clean before and after, own TMPDIR, `JW_B5_SYNTHETIC_ONLY=1`, `PYTHONPATH=.:tests`, homebrew python3.13 `-B -m unittest`, one at a time, Mon 23:25 PST): test_kit_v11 30 OK, test_span_reference 19 OK, test_legs_runner 42 OK, test_kit 18 OK, test_stops_desk 14 OK, test_runner_guards 8 OK, test_launch_cadence_span 12 OK, align.test_r1_smoke_launcher 58 OK (custody `cadence-dev04-s01-tests-ee21df57.txt`).

Inputs: PY align-pilot2 venv; MAGISTRATE_PID 56157; PRIOR_CLOSE_EPOCH 1794856867 (later of dev-03-s02's receipt close 1794856578.70 and its fence seen gone at the 1292492b Check, 11:21:07); LAST_CLOSE_KIND other (newest close is STANDING-F0 run 6, 20:14:52), GAP 1,200 s; OTHER_CLOSE_EPOCH 0; HOST_RESTORE_OK 1 (RUN_STATE 378); SESSION_READY no (no lead READY record on main `f375aa994`).

Arm-record lines (RL-149 §2.8) as the item states them: 1 kit `cl-dev-04.v1.1` sha256 `1cc6673d…2228` (asserted; validate-kit ok, frozen_paths_verified, 12 legs); 2 CI line as dev-03's; 3 queue `b7a0d9882`, sha256 `69131963…0d72` (asserted); 4 OUT outside every registration and custody root (case check passed); 5 no checklist/next run; 6 no open named stop (directive issues #405-#587 unchanged; no `cadence-stop` read here beyond the item's own by-hand list); 7 watcher observation 1794836276, WATCH_UNTIL_EPOCH 1794922676 (Tue 05:37:56), re-checked by watch_gate at the launch; 8 dev-03 R9 PASSED and class A smoke MET (RUN_STATE 365); 9 span two back `dev-03-s01` desk FINAL.

measurement_mode NOTE 1: the one FAIL names 56172 (node codex-mcp-server, ppid 56157), 56173 (npm server-pdf, ppid 56157) and 56180 (codex app-server under 56175 under 56172): all this magistrate's tree; they end when it exits. WARN lines (battery limit syntax, softwareupdate schedule) recorded, not gates. Free disk 241 GiB.

Plan: batch_windows ["13:14-13:15"], runner_kind cadence-legs-v1.1, expected 10,507 s, worst case 24,750 s, blackout_clear true, soak 1,950 s, redo quota 2; budgets L001 1,156 (10000, first leg: span reference), L002 1,251, L003 1,076, L004 1,156, L005 1,467 (span, consume), L006 1,251. From a ~00:01 t0: expected end ~02:56, worst case ~06:54, fence end ~07:18 PST. With `13:14-13:15` legs may run through the 02:00-02:35 OS batch (next batch print 02:08:39): rule 5's case.

## Start-and-check output (00:00:23-00:00:26; measurement_mode PASS/SKIP lines and the whole plan kept in custody)

```
== start-and-check Tue Nov 17 00:00:23 PST 2026 epoch 1794902423
56157 /Users/edr/.local/bin/claude
close interval GAP 1200 s (RL-171 §6.1; 1,200 s after a Part C or F0, F2, a slot session or W1)
ARG 13:14-13:15 (RL-171 §3: 02:00-02:35 where this pin's own plan admits the t0, else the data-only 13:14-13:15)
SPAN dev-04-s01 LEGS L001,L002,L003,L004,L005,L006
2d347f721552fe03bdd19f113e7bad7a7c24908e
census: 19 receipts, newest mtime 1794888892.640822 /Users/edr/code/jw-wt/partc-b2e01464d/.desk/r1-partc-f0-20261117T021602Z/runner_receipt.json
copy gate: newest close is non-campaign (/Users/edr/code/jw-wt/partc-b2e01464d/.desk/r1-partc-f0-20261117T021602Z/runner_receipt.json); its Check covers the copy
t0-date 2026-11-17: development legs already launched 0 (mixed-size 0) []; this span 6, mixed True
PRED CLEAN dev-03-s02 /Users/edr/campaign-out/cl-dev-03/cq-dev-03-s02-a1-20261116T155204Z: rc 0, 9 of 9 legs, MEASURED_OK COMPLETE, close steps rc 0, overtime legs 0, contaminated redos 0, close_epoch 1794856579
expiry: this item is valid until 2026-11-17 05:38:05 PST (RL-173 D.5)
{"campaign_id": "cl-dev-04", "frozen_commit": "2d347f721552fe03bdd19f113e7bad7a7c24908e", "frozen_paths_verified": true, "kit_sha256": "1cc6673d78922a67b381155e24d53744e8515a6ca821e9a4a0ed62943d752228", "legs": 12, "ok": true}
== measurement_mode verify 2026-11-17T08:00:25Z
WARN  battery charge limit: want 80, got none (syntax unverified on 26.6.2)
WARN  softwareupdate schedule: want off, got on (known non-persistent on 26.6.2, RUN_STATE 201)
FAIL  agent process present: 56180;56172 node scripts/codex-mcp-server.mjs;56173 npm exec @modelcontextprotocol/server-pdf --stdio HOME=/Users/edr LOGNAME=edr PATH=/Users/edr/.local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin SHELL=/bin/zsh;
INFO  display power state:  | "IOPowerManagement" = {"CapabilityFlags"=32768,"MaxPowerState"=1,"CurrentPowerState"=1} | "IOPowerManagement" = {"CapabilityFlags"=32768,"MaxPowerState"=1,"CurrentPowerState"=1}  (launch_align_r0.py runs displaysleepnow + dwell per span; not a gate)
VERIFY FAILED: 1 mismatch(es)
verify rc 1
Network Time: Off
boot 2026-10-14 15:07:51 PDT; next OS batch 2026-11-17 02:08:39 PST (boot + 12 h + 48 s + whole days)
night.lock: no holder
sudo kill rc 0
no r12
56172 node scripts/codex-mcp-server.mjs
56173 npm exec @modelcontextprotocol/server-pdf --stdio HOME=/Users/edr LOGNAME=edr PATH=/Users/edr/.local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin SHELL=/bin/zsh
56175 node /opt/homebrew/bin/codex app-server
56180 /opt/homebrew/lib/node_modules/@openai/codex/node_modules/@openai/codex-darwin-arm64/vendor/aarch64-apple-darwin/bin/codex app-server
no stray monitor
no root powermetrics
no night/smoke agent
 powermode            0
{"ac_power": true, "free_bytes": 258985177088, "disk_check": "report_only"}
{
 "batch_windows": [
  "13:14-13:15"
 ],
 "blackout_clear": true,
 "campaign_id": "cl-dev-04",
 "deadline_epoch_s": 1794927176.313706,
 "expected_s": 10507,
 "fence_end_epoch_s": 1794928636.313706,
 "fixed_overhead_s": 1200,
 "kit_sha256": "1cc6673d78922a67b381155e24d53744e8515a6ca821e9a4a0ed62943d752228",
 "launch_deadline_epoch_s": 1794927736.313706,
 "leg_cap_s": 2700,
 "legs": [ ... six legs as listed above ... ],
 "redo_quota": 2,
 "runner_kind": "cadence-legs-v1.1",
 "schema": "joulewise.cadence_span_plan.v1",
 "soak_s": 1950,
 "t0_epoch_s": 1794902426.313706,
 "time_model": {
  "decode_tokens_per_s": 12.03,
  "fixed_s": 500.0,
  "g0_s": 209.0,
  "prefill_s_per_token": 0.005,
  "span_g0_s": 600.0,
  "warmup_extra_s": 6.0
 },
 "worst_case_s": 24750
}
OUT=/Users/edr/campaign-out/cl-dev-04/cq-dev-04-s01-a1-20261117T080025Z
DEADLINE=1794928636.3378549
KIT=/Users/edr/campaign-out/kits/cl-dev-04.v1.1-fecaf73f3-s01.json 1cc6673d78922a67b381155e24d53744e8515a6ca821e9a4a0ed62943d752228
== start-and-check end Tue Nov 17 00:00:26 PST 2026 epoch 1794902426
```

The OUT, DEADLINE and plan t0 above belong to the 00:00 Start and check; the Run re-computes them on fresh state, and the launched OUT, t0 and rc are in custody `cadence-dev04-s01-out-ee21df57.txt` and `cadence-dev04-s01-launch-ee21df57.json` (a STOP, WAIT, CEDE or VOID line, or LAUNCH_RC other than 0, means nothing ran).
