# dev-01-s04 Check, magistrate 7695a93c (headless, Opus 5.5), 2026-11-15 02:44 PST

Item 331 Check run verbatim (fenced blocks of item 331 "Check", with PY, OUT, LEGS, CUSTODY set; cwd the s04 scratch worktree at b4b6aeb19). Script: custody `cadence-dev01-s04-postcheck-7695a93c.sh`. Full output below, as printed (maintenance log itself is `$OUT/maintenance-log.txt`, not committed).

measurement_mode NOTE 1: the one FAIL names 78565 (node codex-mcp-server, ppid 78545 = this magistrate), 78566 (npm server-pdf, ppid 78545) and 78569 (codex, ppid 78568, whose ppid is 78565). All in this magistrate's tree, and the span had already closed (receipt 02:41:45; this session spawned 02:42:35).

Leg intervals (local, from leg_summary / receipt steps): soak 00:06:41-00:36:41; L008 00:36:42-00:57:27; L009 00:57:28-01:18:16; L010 01:18:17-01:39:09; L011 01:39:10-02:00:06; L012.a1 02:00:06-02:21:00 (redone: cpu_load); L012.a2 02:21:01-02:41:44.

```
maintenance window 2026-11-15 00:00:02 .. 2026-11-15 02:41:45
log show rc 0
   61953
00:00 backupd 27
00:00 dasd 1810
00:00 mds 9
00:00 softwareupdated 9
00:10 backupd 9
00:10 dasd 1986
00:10 softwareupdated 8
00:20 dasd 1660
00:30 dasd 1515
00:30 mobileassetd 69
00:40 backupd 6
00:40 dasd 1665
00:40 mobileassetd 3
00:50 backupd 33
00:50 dasd 1499
01:00 backupd 9
01:00 dasd 1843
01:00 mobileassetd 171
01:10 backupd 6
01:10 dasd 1877
01:10 mobileassetd 1
01:10 softwareupdated 8
01:20 dasd 1644
01:20 mobileassetd 3652
01:30 backupd 264
01:30 dasd 1561
01:40 backupd 6
01:40 dasd 1607
01:50 backupd 24
01:50 dasd 1293
02:00 XProtect 26
02:00 XProtectPluginService 565
02:00 backupd 9
02:00 dasd 5857
02:00 mds 20
02:00 mobileassetd 2212
02:00 softwareupdated 1
02:10 XProtect 35
02:10 XProtectPluginService 131
02:10 backupd 6
02:10 dasd 2994
02:10 mds 53
02:10 mobileassetd 1150
02:10 softwareupdated 8
02:20 XProtect 35
02:20 XProtectPluginService 2
02:20 dasd 1495
02:20 mobileassetd 179
02:30 dasd 1370
02:30 mobileassetd 1
02:40 backupd 6
02:40 dasd 626
{"batch_windows": ["13:14-13:15"], "error": null, "legs_finished": 5, "legs_planned": 5, "load_redos_used": 1, "meter": {"bad_polls": 0, "elapsed_s": 9606.011367625, "polls": 48030, "present": true, "proven_stopped": true, "usb_errors": 0}, "rc": 0, "roster": ["L008", "L009", "L010", "L011", "L012"], "runner_kind": "cadence-legs-v1", "span_result": {"chain_exit_code": 0, "chain_outcome": "COMPLETE", "fault": false, "outcome": "MEASURED_OK", "verdict": "5/5 legs run"}}
[('deadline', 0), ('frozen', 0), ('night_agents', 0), ('ac_power', 0), ('condition13', 0), ('start-agents', 0), ('start-meter', 0), ('start-volumes', 0), ('read_power', 0), ('display', 0), ('dwell', 0), ('plan', 0), ('before-soak-volumes', 0), ('soak', 0), ('before-L008-volumes', 0), ('L008.a1', 0), ('before-L009-volumes', 0), ('L009.a1', 0), ('before-L010-volumes', 0), ('L010.a1', 0), ('before-L011-volumes', 0), ('L011.a1', 0), ('before-L012-volumes', 0), ('L012.a1', 0), ('before-L012-volumes', 0), ('L012.a2', 0), ('restore', 0), ('stop-volumes', 0), ('stop-meter', 0), ('stop-agents', 0), ('close-volumes', 0)]
L008 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794733047.759088, "g0_outcome": "released", "g0_s": 200.787497917, "leg_id": "L008", "os_level_max": 2, "pm_nominal": false, "redo_reasons": [], "seed": 4194947539, "start_band": "q0", "started_epoch_s": 1794731802.220026, "wall_s": 1245.5386400222778}
L009 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794734296.9230971, "g0_outcome": "released", "g0_s": 203.977064292, "leg_id": "L009", "os_level_max": 2, "pm_nominal": false, "redo_reasons": [], "seed": 1934072354, "start_band": "q0", "started_epoch_s": 1794733048.412556, "wall_s": 1248.5100989341736}
L010 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794735549.405664, "g0_outcome": "released", "g0_s": 207.134823791, "leg_id": "L010", "os_level_max": 2, "pm_nominal": false, "redo_reasons": [], "seed": 1942037262, "start_band": "q0", "started_epoch_s": 1794734297.5735822, "wall_s": 1251.8316259384155}
L011 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794736806.0794291, "g0_outcome": "released", "g0_s": 211.144511395, "leg_id": "L011", "os_level_max": 2, "pm_nominal": false, "redo_reasons": [], "seed": 2179981163, "start_band": "q0", "started_epoch_s": 1794735550.0576088, "wall_s": 1256.021255016327}
L012 {"admitted": true, "attempts": 2, "band_reached": true, "budget_s": 1251, "contaminated_redos": 1, "ended_epoch_s": 1794739304.3755388, "g0_outcome": "released", "g0_s": 192.677321459, "leg_id": "L012", "os_level_max": 2, "pm_nominal": false, "redo_reasons": ["cpu_load"], "seed": 4264228373, "start_band": "q0", "started_epoch_s": 1794736806.753068, "wall_s": 1242.9232831001282}
result {
 "chain_exit_code": 0,
 "chain_outcome": "COMPLETE",
 "fault": false,
 "outcome": "MEASURED_OK",
 "verdict": "5/5 legs run"
}
meter {
 "bad_polls": 0,
 "elapsed_s": 9606.011367625,
 "polls": 48030,
 "present": true,
 "proven_stopped": true,
 "usb_errors": 0
}
RECEIPT OK
soak_reference {'TV0h': 34.134375953674315, 'TV1h': 34.134375953674315} Tf08_last1200s_mean 26.73908176581065
L008 {"g0": {"duration_s": 200.787497917, "outcome": "released", "release": {"TV0h": 34.898582458496094, "TV1h": 34.898582458496094, "Tf08": 34.95781326293945}, "row_reference": {"fast_c": 34.15072059631348, "slow_c": 34.15072059631348, "source_member": "cadence-cl-dev-01-l008", "span_ns": [2716493565065604, 2716553565065604]}, "row_release": {"fast_c": 34.898582458496094, "slow_c": 34.898582458496094}}, "own_reference": {"TV0h": 34.15072059631348, "TV1h": 34.15072059631348, "Tf08_median": 26.964062690734863, "status": "captured"}}
L009 {"g0": {"duration_s": 203.977064292, "outcome": "released", "release": {"TV0h": 35.0888671875, "TV1h": 35.0888671875, "Tf08": 36.76531219482422}, "row_reference": {"fast_c": 34.683895111083984, "slow_c": 34.683895111083984, "source_member": "cadence-cl-dev-01-l009", "span_ns": [2717739308785562, 2717799308785562]}, "row_release": {"fast_c": 35.0888671875, "slow_c": 35.0888671875}}, "own_reference": {"TV0h": 34.683895111083984, "TV1h": 34.683895111083984, "Tf08_median": 32.572654724121094, "status": "captured"}}
L010 {"g0": {"duration_s": 207.134823791, "outcome": "released", "release": {"TV0h": 35.041690826416016, "TV1h": 35.041690826416016, "Tf08": 36.23781204223633}, "row_reference": {"fast_c": 34.71386528015137, "slow_c": 34.71386528015137, "source_member": "cadence-cl-dev-01-l010", "span_ns": [2718989271688958, 2719049271688958]}, "row_release": {"fast_c": 35.041690826416016, "slow_c": 35.041690826416016}}, "own_reference": {"TV0h": 34.71386528015137, "TV1h": 34.71386528015137, "Tf08_median": 32.817657470703125, "status": "captured"}}
L011 {"g0": {"duration_s": 211.144511395, "outcome": "released", "release": {"TV0h": 35.01863479614258, "TV1h": 35.01863479614258, "Tf08": 36.142189025878906}, "row_reference": {"fast_c": 34.71567916870117, "slow_c": 34.71567916870117, "source_member": "cadence-cl-dev-01-l011", "span_ns": [2720239501404728, 2720299501404728]}, "row_release": {"fast_c": 35.01863479614258, "slow_c": 35.01863479614258}}, "own_reference": {"TV0h": 34.71567916870117, "TV1h": 34.71567916870117, "Tf08_median": 32.8125, "status": "captured"}}
L012 {"g0": {"duration_s": 192.677321459, "outcome": "released", "release": {"TV0h": 35.14943313598633, "TV1h": 35.14943313598633, "Tf08": 37.11249923706055}, "row_reference": {"fast_c": 34.78431701660156, "slow_c": 34.78431701660156, "source_member": "cadence-cl-dev-01-l012", "span_ns": [2722752748923062, 2722812748923062]}, "row_release": {"fast_c": 35.14943313598633, "slow_c": 35.14943313598633}}, "own_reference": {"TV0h": 34.78431701660156, "TV1h": 34.78431701660156, "Tf08_median": 33.521562576293945, "status": "captured"}}
0
 powermode            0
Network Time: Off
no stray monitor
no root powermetrics
== measurement_mode verify 2026-11-15T10:44:31Z
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
FAIL  agent process present: 78569;78565 node scripts/codex-mcp-server.mjs;78566 npm exec @modelcontextprotocol/server-pdf --stdio HOME=/Users/edr LOGNAME=edr PATH=/Users/edr/.local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin SHELL=/bin/zsh;
INFO  display power state:  | "IOPowerManagement" = {"CapabilityFlags"=32768,"MaxPowerState"=1,"CurrentPowerState"=1} | "IOPowerManagement" = {"CapabilityFlags"=32768,"MaxPowerState"=1,"CurrentPowerState"=1}  (launch_align_r0.py runs displaysleepnow + dwell per span; not a gate)
PASS  /private/tmp entries: 1632 < 10000
PASS  free disk: 72 GiB >= 60
PASS  no High Power marker
PASS  keep-awake caffeinate assertion present
VERIFY FAILED: 1 mismatch(es)
verify rc 1
== close epoch
1794739305.274485572
```
