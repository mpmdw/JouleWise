# dev-03-s01 (counted pilot) Check, magistrate d59960c1 (headless, Opus 5.5), 2026-11-16 05:15 PST

Item 355 "Check" run from its two fenced blocks (maintenance line; the Check proper with receipt asserts, the RL-150 R1 / RL-158 Q1 print, restore and measurement_mode lines), extracted mechanically from the item text on `origin/main` `3d0e248f3`. Preceded by PY (align-pilot2 venv), OUT, `LEGS=L001,L002,L003`, CUSTODY, `ARG=02:00-02:35` (the argument recorded at the arm, RUN_STATE 362) and the power reads used by the earlier Checks. cwd: the span's own worktree `/Users/edr/code/jw-wt/cadence-dev03-s01` at `2d347f721` (printed). Script: custody `cadence-dev03-s01-postcheck-d59960c1.sh`; output: custody `cadence-dev03-s01-postcheck-out-d59960c1.txt` (reproduced below). The extract stopped at the High Power marker line, so the last three lines of the block (the two `pgrep` lines and `measurement_mode.zsh verify`) were run verbatim right after, at 05:16:09, appended to the same output file under "== continuation". Every other one of the block's 110 lines appears verbatim in the script (`grep -vxF` leaves only those three). The maintenance log is `$OUT/maintenance-log.txt`, not committed. Nothing from `$OUT` is committed.

Before the Check: no `standdown.request`, no `desk_fence.json`, fence pid 75682 gone, no `com.joulewise.(night|align-r0)` label loaded and no such plist on disk (only `com.joulewise.magistrate`). Receipt `ended` epoch 1794834607.15 (05:10:07 PST). This activation spawned 05:14:34, after the close. No pending notices; no unread mail from Ed; the open directives (#587, #422, #421 and older) are standing; none names a stop and none changes this Check. Canonical root fast-forwarded `3e0fa260b` → `3d0e248f3` (clean tree, no night agent loaded or on disk).

measurement_mode NOTE 1: the one FAIL names 82001 (codex app-server), 81997 (node codex-mcp-server) and 81998 (npm server-pdf), all children of this magistrate. WARN lines (battery limit syntax, softwareupdate schedule) recorded, not gates. Free disk 62 GiB (>= 60).

Intervals (local, from chain-stages and leg_summary): launch 03:38:31 (OUT stamp 03:38:30); soak 03:43:46-04:13:46; L001 04:13:47-04:29:57; L002 04:29:58-04:50:50; L003 04:50:50-05:10:06; close 05:10:07. No load redo (quota 2 unused). The span started after 00:00 and did not cross it.

Maintenance overlap (print only): `dasd` 1,327-2,040 lines per 10 min through the span; `backupd` 3-36; `mobileassetd` 122 in 03:50 (soak). The 05:00 bucket (inside L003, 04:50:50-05:10:06) holds `softwareupdated` 2,598, `mobileassetd` 2,217, `XProtectPluginService` 562, `XProtect` 50, `backupd` 36: L003 ran with no redo (`contaminated_redos` 0, admitted). Rule 5 judgment of L003 is left to the desk.

Admission (from each leg_summary): admitted 3 of 3, all `g0_outcome` released, `band_reached` true, start band q0, attempts 1, `contaminated_redos` 0.
- L001: 2,000 nominal (2,024 realized, +1.2 %), own-shaped, `g0_role` capture, G0 136.5 s, `span_reference` null; `os_level_max` 1.
- **L002 (the class A smoke line): 19,458 tokens span-shaped, `g0_role` consume, G0 released after 209.1 s against L001's capture** (`g0_reference_source` `cadence-cl-dev-03-l001`, reference record sha256 `1675f044…bf6e`, `span_reference` {leg L001, attempt 1, excluded false, redone false}); reference TV0h/TV1h 34.174 °C, release reading 35.019 °C, Tf08 35.90; **it ran its turn** (`leg_status` complete, prefill 19,458, decode 4,096). `os_level_max` 2.
- L003: 10,000 nominal (10,015 realized, +0.15 %), own-shaped, capture, G0 221.5 s, own reference 34.755 °C, release 35.055 °C; `os_level_max` 2.
- Every leg `pm_nominal` false (as dev-02).

Soak reference TV0h/TV1h 34.159 °C; Tf08 mean over the soak's last 1,200 s 26.96.

LEG_OVERTIME: none (wall 970.2 / 1,251.9 / 1,155.4 s against 1.5 x budget 1,614 / 2,463 / 1,734 s). No named stop in the receipt (`fault` false, `error` null); the Air desk builds `stops.json`.

Restore lines: steps `restore`, `stop-volumes`, `stop-meter`, `stop-agents`, `close-volumes` all rc 0; after the close: AC powermode 0, no High Power marker, `night.lock` no holder, Network Time Off, kernel frequency word 0, no stray monitor, no root powermetrics, no align-r0 label. Meter: 27,414 polls, 0 bad, 0 USB errors, proven stopped.

The magistrate reports; it does not decide. R9 and the class A smoke verdict are the lead's hand-read (item 355 "After"); the remainder L004-L012 arms only by its own item.

## Check output (custody `cadence-dev03-s01-postcheck-out-d59960c1.txt`)

```
== check Mon Nov 16 05:15:47 PST 2026 epoch 1794834947
2d347f721552fe03bdd19f113e7bad7a7c24908e
pmset -g custom AC powermode 0
no High Power marker
night.lock: no holder
maintenance window 2026-11-16 03:38:30 .. 2026-11-16 05:10:07
log show rc 0
   39563
03:30 backupd 3
03:30 dasd 318
03:30 mds 6
03:30 softwareupdated 8
03:40 backupd 6
03:40 dasd 1419
03:50 backupd 24
03:50 dasd 1599
03:50 mobileassetd 122
04:00 backupd 9
04:00 dasd 1587
04:10 backupd 6
04:10 dasd 1959
04:10 mobileassetd 3
04:10 softwareupdated 8
04:20 dasd 1693
04:30 dasd 1689
04:40 backupd 6
04:40 dasd 1327
04:40 mobileassetd 3
04:50 dasd 1587
05:00 XProtect 50
05:00 XProtectPluginService 562
05:00 backupd 36
05:00 dasd 2040
05:00 mobileassetd 2217
05:00 softwareupdated 2598
{"batch_windows": ["02:00-02:35"], "error": null, "legs_finished": 3, "legs_planned": 3, "load_redos_used": 0, "meter": {"bad_polls": 0, "elapsed_s": 5482.812866542, "polls": 27414, "present": true, "proven_stopped": true, "usb_errors": 0}, "rc": 0, "roster": ["L001", "L002", "L003"], "runner_kind": "cadence-legs-v1.1", "span_result": {"chain_exit_code": 0, "chain_outcome": "COMPLETE", "fault": false, "outcome": "MEASURED_OK", "verdict": "3/3 legs run"}}
[('deadline', 0), ('frozen', 0), ('night_agents', 0), ('ac_power', 0), ('condition13', 0), ('start-agents', 0), ('start-meter', 0), ('start-volumes', 0), ('read_power', 0), ('display', 0), ('dwell', 0), ('plan', 0), ('before-soak-volumes', 0), ('soak', 0), ('before-L001-volumes', 0), ('L001.a1', 0), ('before-L002-volumes', 0), ('L002.a1', 0), ('before-L003-volumes', 0), ('L003.a1', 0), ('restore', 0), ('stop-volumes', 0), ('stop-meter', 0), ('stop-agents', 0), ('close-volumes', 0)]
L001 admitted True g0_role capture g0_outcome released g0_s 136.513185104 span_reference null
L001 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1076, "contaminated_redos": 0, "ended_epoch_s": 1794832197.5727391, "g0_outcome": "released", "g0_role": "capture", "g0_s": 136.513185104, "g0_shape": "own", "leg_id": "L001", "os_level_max": 1, "pm_nominal": false, "prefill_tokens": 2000, "redo_reasons": [], "seed": 4129284831, "span_reference": null, "start_band": "q0", "started_epoch_s": 1794831227.37307, "wall_s": 970.1993181705475}
L002 admitted True g0_role consume g0_outcome released g0_s 209.094837146 span_reference {"attempt": 1, "excluded": false, "leg_id": "L001", "redone": false}
L002 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1642, "contaminated_redos": 0, "ended_epoch_s": 1794833450.123209, "g0_outcome": "released", "g0_role": "consume", "g0_s": 209.094837146, "g0_shape": "span", "leg_id": "L002", "os_level_max": 2, "pm_nominal": false, "prefill_tokens": 19458, "redo_reasons": [], "seed": 319096281, "span_reference": {"attempt": 1, "excluded": false, "leg_id": "L001", "redone": false}, "start_band": "q0", "started_epoch_s": 1794832198.245632, "wall_s": 1251.8771300315857}
L003 admitted True g0_role capture g0_outcome released g0_s 221.521905438 span_reference null
L003 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1156, "contaminated_redos": 0, "ended_epoch_s": 1794834606.1917188, "g0_outcome": "released", "g0_role": "capture", "g0_s": 221.521905438, "g0_shape": "own", "leg_id": "L003", "os_level_max": 2, "pm_nominal": false, "prefill_tokens": 10000, "redo_reasons": [], "seed": 512394455, "span_reference": null, "start_band": "q0", "started_epoch_s": 1794833450.784663, "wall_s": 1155.4066090583801}
result {
 "chain_exit_code": 0,
 "chain_outcome": "COMPLETE",
 "fault": false,
 "outcome": "MEASURED_OK",
 "verdict": "3/3 legs run"
}
meter {
 "bad_polls": 0,
 "elapsed_s": 5482.812866542,
 "polls": 27414,
 "present": true,
 "proven_stopped": true,
 "usb_errors": 0
}
RECEIPT OK
soak_reference {'TV0h': 34.15946151097616, 'TV1h': 34.15946151097616} Tf08_last1200s_mean 26.964142163594563
L001 {"decode_tokens": 4096, "g0": {"duration_s": 136.513185104, "outcome": "released", "release": {"TV0h": 34.47814178466797, "TV1h": 34.47814178466797, "Tf08": 30.729999542236328}, "row_reference": {"fast_c": 34.17414474487305, "slow_c": 34.17414474487305, "source_member": "cadence-cl-dev-03-l001", "span_ns": [2815919763784083, 2815979763784083]}, "row_release": {"fast_c": 34.47814178466797, "slow_c": 34.47814178466797}}, "g0_outcome": "released", "g0_reference_record_sha256": null, "g0_reference_source": "cadence-cl-dev-03-l001", "g0_released": true, "g0_role": "capture", "g0_shape": "own", "g0_wait_s": 136.513185104, "leg_status": "complete", "own_reference": {"TV0h": 34.17414474487305, "TV1h": 34.17414474487305, "Tf08_median": 27.206406593322754, "status": "captured"}, "prefill_tokens": 2024, "span_reference": null}
L002 {"decode_tokens": 4096, "g0": {"duration_s": 209.094837146, "outcome": "released", "release": {"TV0h": 35.01946258544922, "TV1h": 35.01946258544922, "Tf08": 35.90250015258789}, "row_reference": {"fast_c": 34.17414474487305, "slow_c": 34.17414474487305, "source_member": "cadence-cl-dev-03-l001", "span_ns": [2815919763784083, 2815979763784083]}, "row_release": {"fast_c": 35.01946258544922, "slow_c": 35.01946258544922}}, "g0_outcome": "released", "g0_reference_record_sha256": "1675f04465f9a0db0eb2511d03f1c9c8c12afc6747912ace010d0e9cc854bf6e", "g0_reference_source": "cadence-cl-dev-03-l001", "g0_released": true, "g0_role": "consume", "g0_shape": "span", "g0_wait_s": 209.094837146, "leg_status": "complete", "own_reference": null, "prefill_tokens": 19458, "span_reference": {"attempt": 1, "dir": "legs/L001/runtime", "excluded": false, "leg_id": "L001", "redone": false}}
L003 {"decode_tokens": 4096, "g0": {"duration_s": 221.521905438, "outcome": "released", "release": {"TV0h": 35.055049896240234, "TV1h": 35.055049896240234, "Tf08": 36.39656066894531}, "row_reference": {"fast_c": 34.754634857177734, "slow_c": 34.754634857177734, "source_member": "cadence-cl-dev-03-l003", "span_ns": [2818142188301896, 2818202188301896]}, "row_release": {"fast_c": 35.055049896240234, "slow_c": 35.055049896240234}}, "g0_outcome": "released", "g0_reference_record_sha256": null, "g0_reference_source": "cadence-cl-dev-03-l003", "g0_released": true, "g0_role": "capture", "g0_shape": "own", "g0_wait_s": 221.521905438, "leg_status": "complete", "own_reference": {"TV0h": 34.754634857177734, "TV1h": 34.754634857177734, "Tf08_median": 33.1417179107666, "status": "captured"}, "prefill_tokens": 10015, "span_reference": null}
0
 powermode            0
Network Time: Off
== continuation (the first script's extract stopped at the high-power marker line) Mon Nov 16 05:16:09 PST 2026
no High Power marker
no desk fence
1
no stray monitor
no root powermetrics
== measurement_mode verify 2026-11-16T13:16:09Z
PASS  pmset ac powernap: 0
PASS  pmset batt powernap: 0
PASS  pmset ac standby: 0
PASS  pmset batt standby: 0
SKIP  pmset ac autopoweroff: not reported by pmset on this Mac
SKIP  pmset batt autopoweroff: not reported by pmset on this Mac
SKIP  pmset ac proximitywake: not reported by pmset on this Mac
SKIP  pmset batt proximitywake: not reported by pmset on this Mac
PASS  pmset ac womp: 0
PASS  pmset batt womp: 0
PASS  pmset ac ttyskeepawake: 1
PASS  pmset batt ttyskeepawake: 1
SKIP  pmset ac lowpowermode: not reported by pmset on this Mac
SKIP  pmset batt lowpowermode: not reported by pmset on this Mac
PASS  pmset ac sleep: 0
PASS  pmset ac disksleep: 0
PASS  pmset ac powermode: 0
PASS  pmset batt sleep: 0
PASS  spotlight indexing /: disabled
PASS  spotlight indexing /System/Volumes/Data: disabled
SKIP  time machine AutoBackup: inert, no destination
WARN  battery charge limit: want 80, got none (syntax unverified on 26.6.2)
WARN  softwareupdate schedule: want off, got on (known non-persistent on 26.6.2, RUN_STATE 201)
PASS  network time: Off
PASS  kernel frequency word: 0
PASS  agent disabled com.apple.spotlightknowledged: true
PASS  agent disabled com.apple.spotlightknowledged.updater: true
PASS  agent disabled com.apple.spotlightknowledged.importer: true
PASS  agent disabled com.apple.corespotlightd: true
PASS  power source: AC
PASS  not charging
PASS  no external volume
FAIL  agent process present: 82001;81997 node scripts/codex-mcp-server.mjs;81998 npm exec @modelcontextprotocol/server-pdf --stdio HOME=/Users/edr LOGNAME=edr PATH=/Users/edr/.local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin SHELL=/bin/zsh;
INFO  display power state:  | "IOPowerManagement" = {"CapabilityFlags"=32768,"MaxPowerState"=1,"CurrentPowerState"=1} | "IOPowerManagement" = {"CapabilityFlags"=32768,"MaxPowerState"=1,"CurrentPowerState"=1}  (launch_align_r0.py runs displaysleepnow + dwell per span; not a gate)
PASS  /private/tmp entries: 1695 < 10000
PASS  free disk: 62 GiB >= 60
PASS  no High Power marker
PASS  keep-awake caffeinate assertion present
VERIFY FAILED: 1 mismatch(es)
verify rc 1
/dev/disk3s5       926  841        62    94% 7791961 652833360    1%   /System/Volumes/Data
```
