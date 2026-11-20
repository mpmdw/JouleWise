# dev-02-s02 Check, magistrate a187f945 (headless, Opus 5.5), 2026-11-15 12:44 PST

Item 344 "Check" run verbatim: its two fenced blocks (maintenance line; the Check proper with receipt asserts, RL-150 R1 print, restore and measurement_mode lines), extracted mechanically from the item text on `origin/main` (`74eee9f69`) and preceded by PY (align-pilot2 venv), OUT, `LEGS=L001,...,L006`, CUSTODY, `ARG=02:00-02:35` (the argument recorded at the arm, RUN_STATE 345) and the power reads used by the hp-01 Checks. cwd: the span's own worktree `/Users/edr/code/jw-wt/cadence-dev02-s02` at `b4b6aeb19` (printed). Script: custody `cadence-dev02-s02-postcheck-a187f945.sh`; output: custody `cadence-dev02-s02-postcheck-out-a187f945.txt` (reproduced below). The maintenance log is `$OUT/maintenance-log.txt`, not committed. Nothing from `$OUT` is committed.

Before the Check: no `standdown.request`, no `desk_fence.json`, fence pid 11659 gone, no `com.joulewise.(night|align-r0)` label loaded and no such plist on disk (only `com.joulewise.magistrate`). Receipt `ended` epoch 1794775365.16 (12:42:45 PST); this activation spawned 12:43:28, after the close. No pending notices; no unread mail from Ed; the open directives (#587, #422, #421 and older) are standing; none names a stop and none changes this Check.

measurement_mode NOTE 1: the one FAIL names 22888 (node codex-mcp-server, ppid 22868 = this magistrate), 22889 (npm server-pdf, ppid 22868) and 22892 (codex binary under 22891, the adapter's app-server child). All in this magistrate's tree. WARN lines (battery limit syntax, softwareupdate schedule) recorded, not gates.

Intervals (local, from chain-stages and leg_summary): launch 10:02:15 (OUT stamp 10:00:23); soak 10:07:34-10:37:35; L001 10:37:35-10:58:27; L002 10:58:28-11:19:19; L003 11:19:20-11:40:12; L004 11:40:13-12:01:07; L005 12:01:08-12:21:53; L006 12:21:54-12:42:44. One attempt each, no load redo (quota 2 unused). The span did not cross 00:00 and did not touch 02:00-02:35.

Maintenance overlap (print only): `dasd` 1,259-2,025 lines per 10 min through the span (495 in the partial 12:40 bucket). The 11:00 bucket (inside L002, 10:58:28-11:19:19) is the heavy one: `softwareupdated` 2,596, `mobileassetd` 2,044, `XProtectPluginService` 1,124, `XProtect` 62, `backupd` 42. `mobileassetd` 174 in 10:30 (soak / L001 start), 122 in 11:50 (L004); 3-16 elsewhere. `softwareupdated` 8-9 in 10:00, 10:10 (soak), 33 in 11:10 (L002), 8 in 12:10 (L005). `backupd` 6-54 per bucket; `mds` 6 in 10:00. No leg has a redo reason; rule 5 judgment of L002 is left to the desk.

Admission (from each leg_summary): admitted 6 of 6, all `g0_outcome` released (G0 204.0-210.4 s), `band_reached` true, start band q0, `contaminated_redos` 0. Every leg has `os_level_max` 2 and `pm_nominal` false (in hp-01 only the first leg showed this; here all six do; for the desk). No named stop in the receipt (`fault` false, `error` null); the Air desk builds `stops.json`.

LEG_OVERTIME: none (wall 1,251.7 / 1,251.3 / 1,252.7 / 1,254.6 / 1,245.2 / 1,249.8 s against 1.5 x 1,251 = 1,876.5 s). L001-L004 ran 0.3-3.6 s over budget_s itself; not a stop.

Restore lines: steps `restore`, `stop-volumes`, `stop-meter`, `stop-agents`, `close-volumes` all rc 0; after the close: AC powermode 0, no High Power marker, `night.lock` no holder, Network Time Off, kernel frequency word 0, no stray monitor, no root powermetrics. Meter: 48,062 polls, 0 bad, 0 USB errors, proven stopped.

Copy (items 347/348): the lead's marker `cq-dev-02-s02-a1.ok` was absent at 12:47. Per item 348 the cloud offload is a fallback that runs only if the marker is still absent at close + 30 min = 13:12:45 PST (epoch 1794777165).

## Check output

```
== check Sun Nov 15 12:44:24 PST 2026 epoch 1794775464
b4b6aeb192da60d895a7529311b06599efff5be4
pmset -g custom AC powermode 0
no High Power marker
night.lock: no holder
maintenance window 2026-11-15 10:00:23 .. 2026-11-15 12:42:45
log show rc 0
   58295
10:00 backupd 12
10:00 dasd 1493
10:00 mds 6
10:00 softwareupdated 9
10:10 backupd 6
10:10 dasd 1928
10:10 softwareupdated 8
10:20 dasd 1481
10:30 dasd 1459
10:30 mobileassetd 174
10:40 backupd 9
10:40 dasd 1592
10:40 mobileassetd 4
10:50 dasd 1481
11:00 XProtect 62
11:00 XProtectPluginService 1124
11:00 backupd 42
11:00 dasd 2025
11:00 mobileassetd 2044
11:00 softwareupdated 2596
11:10 backupd 6
11:10 dasd 1920
11:10 mobileassetd 16
11:10 softwareupdated 33
11:20 dasd 1259
11:20 mobileassetd 3
11:30 dasd 1782
11:40 backupd 10
11:40 dasd 1839
11:40 mobileassetd 3
11:50 backupd 54
11:50 dasd 1653
11:50 mobileassetd 122
12:00 backupd 9
12:00 dasd 1663
12:00 mobileassetd 3
12:10 backupd 6
12:10 dasd 1976
12:10 softwareupdated 8
12:20 dasd 1720
12:30 dasd 1489
12:40 backupd 6
12:40 dasd 495
{"batch_windows": ["02:00-02:35"], "error": null, "legs_finished": 6, "legs_planned": 6, "load_redos_used": 0, "meter": {"bad_polls": 0, "elapsed_s": 9612.411572375, "polls": 48062, "present": true, "proven_stopped": true, "usb_errors": 0}, "rc": 0, "roster": ["L001", "L002", "L003", "L004", "L005", "L006"], "runner_kind": "cadence-legs-v1", "span_result": {"chain_exit_code": 0, "chain_outcome": "COMPLETE", "fault": false, "outcome": "MEASURED_OK", "verdict": "6/6 legs run"}}
[('deadline', 0), ('frozen', 0), ('night_agents', 0), ('ac_power', 0), ('condition13', 0), ('start-agents', 0), ('start-meter', 0), ('start-volumes', 0), ('read_power', 0), ('display', 0), ('dwell', 0), ('plan', 0), ('before-soak-volumes', 0), ('soak', 0), ('before-L001-volumes', 0), ('L001.a1', 0), ('before-L002-volumes', 0), ('L002.a1', 0), ('before-L003-volumes', 0), ('L003.a1', 0), ('before-L004-volumes', 0), ('L004.a1', 0), ('before-L005-volumes', 0), ('L005.a1', 0), ('before-L006-volumes', 0), ('L006.a1', 0), ('restore', 0), ('stop-volumes', 0), ('stop-meter', 0), ('stop-agents', 0), ('close-volumes', 0)]
L001 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794769107.464917, "g0_outcome": "released", "g0_s": 210.363921979, "leg_id": "L001", "os_level_max": 2, "pm_nominal": false, "redo_reasons": [], "seed": 3407196167, "start_band": "q0", "started_epoch_s": 1794767855.717856, "wall_s": 1251.7466361522675}
L002 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794770359.3910458, "g0_outcome": "released", "g0_s": 205.12594827, "leg_id": "L002", "os_level_max": 2, "pm_nominal": false, "redo_reasons": [], "seed": 1200148396, "start_band": "q0", "started_epoch_s": 1794769108.1329632, "wall_s": 1251.2575407028198}
L003 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794771612.727964, "g0_outcome": "released", "g0_s": 207.138694646, "leg_id": "L003", "os_level_max": 2, "pm_nominal": false, "redo_reasons": [], "seed": 4048253495, "start_band": "q0", "started_epoch_s": 1794770360.052832, "wall_s": 1252.674639225006}
L004 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794772867.9824378, "g0_outcome": "released", "g0_s": 209.183014251, "leg_id": "L004", "os_level_max": 2, "pm_nominal": false, "redo_reasons": [], "seed": 2129654160, "start_band": "q0", "started_epoch_s": 1794771613.380777, "wall_s": 1254.6011452674866}
L005 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794774113.829001, "g0_outcome": "released", "g0_s": 204.041204292, "leg_id": "L005", "os_level_max": 2, "pm_nominal": false, "redo_reasons": [], "seed": 2522171568, "start_band": "q0", "started_epoch_s": 1794772868.662914, "wall_s": 1245.1655459403992}
L006 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794775364.2653718, "g0_outcome": "released", "g0_s": 205.036503416, "leg_id": "L006", "os_level_max": 2, "pm_nominal": false, "redo_reasons": [], "seed": 606134315, "start_band": "q0", "started_epoch_s": 1794774114.485753, "wall_s": 1249.7790348529816}
result {
 "chain_exit_code": 0,
 "chain_outcome": "COMPLETE",
 "fault": false,
 "outcome": "MEASURED_OK",
 "verdict": "6/6 legs run"
}
meter {
 "bad_polls": 0,
 "elapsed_s": 9612.411572375,
 "polls": 48062,
 "present": true,
 "proven_stopped": true,
 "usb_errors": 0
}
RECEIPT OK
soak_reference {'TV0h': 34.19503404933348, 'TV1h': 34.19503404933348} Tf08_last1200s_mean 27.31282500045484
L001 {"g0": {"duration_s": 210.363921979, "outcome": "released", "release": {"TV0h": 34.86099624633789, "TV1h": 34.86099624633789, "Tf08": 34.50843811035156}, "row_reference": {"fast_c": 34.19404220581055, "slow_c": 34.19404220581055, "source_member": "cadence-cl-dev-02-l001", "span_ns": [2752545894160646, 2752605894160646]}, "row_release": {"fast_c": 34.86099624633789, "slow_c": 34.86099624633789}}, "own_reference": {"TV0h": 34.19404220581055, "TV1h": 34.19404220581055, "Tf08_median": 27.376874923706055, "status": "captured"}}
L002 {"g0": {"duration_s": 205.12594827, "outcome": "released", "release": {"TV0h": 35.074378967285156, "TV1h": 35.074378967285156, "Tf08": 36.634376525878906}, "row_reference": {"fast_c": 34.703765869140625, "slow_c": 34.703765869140625, "source_member": "cadence-cl-dev-02-l002", "span_ns": [2753798138938104, 2753858138938104]}, "row_release": {"fast_c": 35.074378967285156, "slow_c": 35.074378967285156}}, "own_reference": {"TV0h": 34.703765869140625, "TV1h": 34.703765869140625, "Tf08_median": 32.66171836853027, "status": "captured"}}
L003 {"g0": {"duration_s": 207.138694646, "outcome": "released", "release": {"TV0h": 35.07557678222656, "TV1h": 35.07557678222656, "Tf08": 36.645626068115234}, "row_reference": {"fast_c": 34.71480751037598, "slow_c": 34.71480751037598, "source_member": "cadence-cl-dev-02-l003", "span_ns": [2755050781049146, 2755110781049146]}, "row_release": {"fast_c": 35.07557678222656, "slow_c": 35.07557678222656}}, "own_reference": {"TV0h": 34.71480751037598, "TV1h": 34.71480751037598, "Tf08_median": 32.744062423706055, "status": "captured"}}
L004 {"g0": {"duration_s": 209.183014251, "outcome": "released", "release": {"TV0h": 35.063751220703125, "TV1h": 35.063751220703125, "Tf08": 36.54343795776367}, "row_reference": {"fast_c": 34.71917724609375, "slow_c": 34.71917724609375, "source_member": "cadence-cl-dev-02-l004", "span_ns": [2756302443262792, 2756362443262792]}, "row_release": {"fast_c": 35.063751220703125, "slow_c": 35.063751220703125}}, "own_reference": {"TV0h": 34.71917724609375, "TV1h": 34.71917724609375, "Tf08_median": 32.76093864440918, "status": "captured"}}
L005 {"g0": {"duration_s": 204.041204292, "outcome": "released", "release": {"TV0h": 35.07395935058594, "TV1h": 35.07395935058594, "Tf08": 36.56624984741211}, "row_reference": {"fast_c": 34.725507736206055, "slow_c": 34.725507736206055, "source_member": "cadence-cl-dev-02-l005", "span_ns": [2757558600035104, 2757618600035104]}, "row_release": {"fast_c": 35.07395935058594, "slow_c": 35.07395935058594}}, "own_reference": {"TV0h": 34.725507736206055, "TV1h": 34.725507736206055, "Tf08_median": 32.78093910217285, "status": "captured"}}
L006 {"g0": {"duration_s": 205.036503416, "outcome": "released", "release": {"TV0h": 35.063472747802734, "TV1h": 35.063472747802734, "Tf08": 36.38468933105469}, "row_reference": {"fast_c": 34.732614517211914, "slow_c": 34.732614517211914, "source_member": "cadence-cl-dev-02-l006", "span_ns": [2758803908212604, 2758863908212604]}, "row_release": {"fast_c": 35.063472747802734, "slow_c": 35.063472747802734}}, "own_reference": {"TV0h": 34.732614517211914, "TV1h": 34.732614517211914, "Tf08_median": 32.99609375, "status": "captured"}}
0
 powermode            0
Network Time: Off
no stray monitor
no root powermetrics
== measurement_mode verify 2026-11-15T20:44:27Z
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
FAIL  agent process present: 22892;22888 node scripts/codex-mcp-server.mjs;22889 npm exec @modelcontextprotocol/server-pdf --stdio HOME=/Users/edr LOGNAME=edr PATH=/Users/edr/.local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin SHELL=/bin/zsh;
INFO  display power state:  | "IOPowerManagement" = {"CapabilityFlags"=32768,"MaxPowerState"=1,"CurrentPowerState"=1} | "IOPowerManagement" = {"CapabilityFlags"=32768,"MaxPowerState"=1,"CurrentPowerState"=1}  (launch_align_r0.py runs displaysleepnow + dwell per span; not a gate)
PASS  /private/tmp entries: 1678 < 10000
PASS  free disk: 62 GiB >= 60
PASS  no High Power marker
PASS  keep-awake caffeinate assertion present
VERIFY FAILED: 1 mismatch(es)
verify rc 1
```
