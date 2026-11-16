# dev-02-s03 Check, magistrate f845859d (headless, Opus 5.5), 2026-11-16 03:20 PST

Item 354 "Check" run verbatim: its two fenced blocks (maintenance line; the Check proper with receipt asserts, RL-150 R1 print, restore and measurement_mode lines). Every one of the 98 lines of those blocks (extracted mechanically from the item text on `origin/main` `3e0fa260b`) appears verbatim in the script (`grep -vxF` empty). Preceded by PY (align-pilot2 venv), OUT, `LEGS=L007,...,L012`, CUSTODY, `ARG=13:14-13:15` (the argument recorded at the arm, RUN_STATE 360) and the power reads used by the earlier Checks. cwd: the span's own worktree `/Users/edr/code/jw-wt/cadence-dev-02-s03` at `b4b6aeb19` (printed). Script: custody `cadence-dev02-s03-postcheck-f845859d.sh`; output: custody `cadence-dev02-s03-postcheck-out-f845859d.txt` (reproduced below). The maintenance log is `$OUT/maintenance-log.txt`, not committed. Nothing from `$OUT` is committed.

Before the Check: no `standdown.request`, no `desk_fence.json`, fence pid 59613 gone, no `com.joulewise.(night|align-r0)` label loaded and no such plist on disk (only `com.joulewise.magistrate`). Receipt `ended` epoch 1794827163.90 (03:06:03 PST). Activation 15139575 spawned 03:09:23 (after the close; its note calls it "inside the span", but the receipt had been written 3 min earlier) and exited without action; this activation spawned 03:19:26. No pending notices; no unread mail from Ed; the open directives (#587, #422, #421 and older) are standing; none names a stop and none changes this Check.

measurement_mode NOTE 1: the one FAIL names 72631 (node codex-mcp-server), 72632 (npm server-pdf) and 72639, all children of this magistrate (pid 72616). WARN lines (battery limit syntax, softwareupdate schedule) recorded, not gates. Free disk 63 GiB (>= 60).

Intervals (local, from chain-stages): launch 00:04:35 (OUT stamp 00:02:53); soak 00:09:53-00:39:54; L007 00:39:55-01:00:39; L008 01:00:39-01:21:30; L009 01:21:31-01:42:27; L010 01:42:28-02:03:25; L011 a1 02:03:26-02:24:05 (redo, `cpu_load`), a2 02:24:06-02:45:07; L012 02:45:07-03:06:03. One load redo used (quota 2). The span started after 00:00 and did not cross it.

Maintenance overlap (print only): `dasd` 1,064-1,854 lines per 10 min through the span, 5,620 in 02:00 and 2,893 in 02:10. The 02:00-02:20 buckets (inside L010's end and L011 a1) hold the nightly batch: `XProtectPluginService` 568 + 128 + 2, `XProtect` 26 + 35 + 35, `mobileassetd` 2,805 + 762 + 179, `mds` 21 + 52. L011 a1's redo reason `cpu_load` falls in this batch; that is the case rule 5 exists for (item 354: "one redo of about 21 min, quota 2"); the a2 attempt (02:24-02:45) overlaps the tail (`mobileassetd` 179-437, `dasd` ~1,550). Other: `mobileassetd` 3,652 in 01:20 (inside L008 end / L009 start, no redo); `backupd` 6-30 per bucket; `softwareupdated` 1-8. Rule 5 judgment of L008/L009 and L011 a2 is left to the desk.

Admission (from each leg_summary): admitted 6 of 6, all `g0_outcome` released (G0 201.1-215.2 s), `band_reached` true, start band q0. `contaminated_redos` 0 except L011 (1, `cpu_load`, attempts 2). Every leg `os_level_max` 2 and `pm_nominal` false (as `dev-02-s02`). No named stop in the receipt (`fault` false, `error` null); the Air desk builds `stops.json`.

LEG_OVERTIME: none (wall 1,244.2 / 1,250.5 / 1,256.8 / 1,257.3 / 1,261.2 / 1,255.2 s against 1.5 x 1,251 = 1,876.5 s). L009-L012 ran 4-10 s over budget_s itself; not a stop.

Restore lines: steps `restore`, `stop-volumes`, `stop-meter`, `stop-agents`, `close-volumes` all rc 0; after the close: AC powermode 0, no High Power marker, `night.lock` no holder, Network Time Off, kernel frequency word 0, no stray monitor, no root powermetrics. Meter: 54,359 polls, 0 bad, 0 USB errors, proven stopped.

dev-02 now has 12 of 12 legs collected (L001-L006 on 11-15, L007-L012 here).

## Check output (custody `cadence-dev02-s03-postcheck-out-f845859d.txt`)

```
== check Mon Nov 16 03:20:51 PST 2026 epoch 1794828051
b4b6aeb192da60d895a7529311b06599efff5be4
pmset -g custom AC powermode 0
no High Power marker
night.lock: no holder
maintenance window 2026-11-16 00:02:53 .. 2026-11-16 03:06:03
log show rc 0
   67059
00:00 XprotectService 3
00:00 backupd 12
00:00 dasd 1249
00:00 mds 6
00:00 softwareupdated 8
00:10 backupd 6
00:10 dasd 1609
00:10 mobileassetd 3
00:10 softwareupdated 8
00:20 dasd 1559
00:30 dasd 1684
00:30 mobileassetd 3
00:40 backupd 6
00:40 dasd 1624
00:50 backupd 30
00:50 dasd 1448
01:00 backupd 9
01:00 dasd 1854
01:10 backupd 6
01:10 dasd 1799
01:10 softwareupdated 8
01:20 dasd 1518
01:20 mobileassetd 3652
01:30 dasd 1433
01:40 backupd 6
01:40 dasd 1693
01:50 backupd 24
01:50 dasd 1569
01:50 mobileassetd 3
02:00 XProtect 26
02:00 XProtectPluginService 568
02:00 backupd 9
02:00 dasd 5620
02:00 mds 21
02:00 mobileassetd 2805
02:00 softwareupdated 1
02:10 XProtect 35
02:10 XProtectPluginService 128
02:10 backupd 6
02:10 dasd 2893
02:10 mds 52
02:10 mobileassetd 762
02:10 softwareupdated 8
02:20 XProtect 35
02:20 XProtectPluginService 2
02:20 dasd 1538
02:20 mobileassetd 179
02:30 dasd 1532
02:30 mds 5
02:30 mobileassetd 437
02:40 backupd 6
02:40 dasd 1600
02:40 mobileassetd 400
02:50 backupd 24
02:50 dasd 1748
02:50 mobileassetd 4
02:50 softwareupdated 8
03:00 backupd 9
03:00 dasd 1064
{"batch_windows": ["13:14-13:15"], "error": null, "legs_finished": 6, "legs_planned": 6, "load_redos_used": 1, "meter": {"bad_polls": 0, "elapsed_s": 10871.811074583, "polls": 54359, "present": true, "proven_stopped": true, "usb_errors": 0}, "rc": 0, "roster": ["L007", "L008", "L009", "L010", "L011", "L012"], "runner_kind": "cadence-legs-v1", "span_result": {"chain_exit_code": 0, "chain_outcome": "COMPLETE", "fault": false, "outcome": "MEASURED_OK", "verdict": "6/6 legs run"}}
[('deadline', 0), ('frozen', 0), ('night_agents', 0), ('ac_power', 0), ('condition13', 0), ('start-agents', 0), ('start-meter', 0), ('start-volumes', 0), ('read_power', 0), ('display', 0), ('dwell', 0), ('plan', 0), ('before-soak-volumes', 0), ('soak', 0), ('before-L007-volumes', 0), ('L007.a1', 0), ('before-L008-volumes', 0), ('L008.a1', 0), ('before-L009-volumes', 0), ('L009.a1', 0), ('before-L010-volumes', 0), ('L010.a1', 0), ('before-L011-volumes', 0), ('L011.a1', 0), ('before-L011-volumes', 0), ('L011.a2', 0), ('before-L012-volumes', 0), ('L012.a1', 0), ('restore', 0), ('stop-volumes', 0), ('stop-meter', 0), ('stop-agents', 0), ('close-volumes', 0)]
L007 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794819639.2274098, "g0_outcome": "released", "g0_s": 201.053117188, "leg_id": "L007", "os_level_max": 2, "pm_nominal": false, "redo_reasons": [], "seed": 756369387, "start_band": "q0", "started_epoch_s": 1794818395.044396, "wall_s": 1244.1826150417328}
L008 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794820890.348879, "g0_outcome": "released", "g0_s": 202.043663416, "leg_id": "L008", "os_level_max": 2, "pm_nominal": false, "redo_reasons": [], "seed": 2814803342, "start_band": "q0", "started_epoch_s": 1794819639.891062, "wall_s": 1250.457379102707}
L009 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794822147.955921, "g0_outcome": "released", "g0_s": 204.093868874, "leg_id": "L009", "os_level_max": 2, "pm_nominal": false, "redo_reasons": [], "seed": 3757715371, "start_band": "q0", "started_epoch_s": 1794820891.140567, "wall_s": 1256.8148789405823}
L010 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794823405.882567, "g0_outcome": "released", "g0_s": 211.292132876, "leg_id": "L010", "os_level_max": 2, "pm_nominal": false, "redo_reasons": [], "seed": 2990673426, "start_band": "q0", "started_epoch_s": 1794822148.6108391, "wall_s": 1257.2711737155914}
L011 {"admitted": true, "attempts": 2, "band_reached": true, "budget_s": 1251, "contaminated_redos": 1, "ended_epoch_s": 1794825907.2575092, "g0_outcome": "released", "g0_s": 215.219995355, "leg_id": "L011", "os_level_max": 2, "pm_nominal": false, "redo_reasons": ["cpu_load"], "seed": 3918830640, "start_band": "q0", "started_epoch_s": 1794823406.533876, "wall_s": 1261.1566061973572}
L012 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794827163.081017, "g0_outcome": "released", "g0_s": 211.201251895, "leg_id": "L012", "os_level_max": 2, "pm_nominal": false, "redo_reasons": [], "seed": 2835741939, "start_band": "q0", "started_epoch_s": 1794825907.916459, "wall_s": 1255.164025068283}
result {
 "chain_exit_code": 0,
 "chain_outcome": "COMPLETE",
 "fault": false,
 "outcome": "MEASURED_OK",
 "verdict": "6/6 legs run"
}
meter {
 "bad_polls": 0,
 "elapsed_s": 10871.811074583,
 "polls": 54359,
 "present": true,
 "proven_stopped": true,
 "usb_errors": 0
}
RECEIPT OK
soak_reference {'TV0h': 34.127195721959, 'TV1h': 34.127195721959} Tf08_last1200s_mean 26.64902840486474
L007 {"g0": {"duration_s": 201.053117188, "outcome": "released", "release": {"TV0h": 34.89231491088867, "TV1h": 34.89231491088867, "Tf08": 34.8728141784668}, "row_reference": {"fast_c": 34.16116714477539, "slow_c": 34.16116714477539, "source_member": "cadence-cl-dev-02-l007", "span_ns": [2803087261962416, 2803147261962416]}, "row_release": {"fast_c": 34.89231491088867, "slow_c": 34.89231491088867}}, "own_reference": {"TV0h": 34.16116714477539, "TV1h": 34.16116714477539, "Tf08_median": 27.027655601501465, "status": "captured"}}
L008 {"g0": {"duration_s": 202.043663416, "outcome": "released", "release": {"TV0h": 35.09697341918945, "TV1h": 35.09697341918945, "Tf08": 36.856563568115234}, "row_reference": {"fast_c": 34.6876106262207, "slow_c": 34.6876106262207, "source_member": "cadence-cl-dev-02-l008", "span_ns": [2804331683896791, 2804391683896791]}, "row_release": {"fast_c": 35.09697341918945, "slow_c": 35.09697341918945}}, "own_reference": {"TV0h": 34.6876106262207, "TV1h": 34.6876106262207, "Tf08_median": 32.50437355041504, "status": "captured"}}
L009 {"g0": {"duration_s": 204.093868874, "outcome": "released", "release": {"TV0h": 35.06171417236328, "TV1h": 35.06171417236328, "Tf08": 36.56687545776367}, "row_reference": {"fast_c": 34.71028137207031, "slow_c": 34.71028137207031, "source_member": "cadence-cl-dev-02-l009", "span_ns": [2805581992076728, 2805641992076728]}, "row_release": {"fast_c": 35.06171417236328, "slow_c": 35.06171417236328}}, "own_reference": {"TV0h": 34.71028137207031, "TV1h": 34.71028137207031, "Tf08_median": 32.690311431884766, "status": "captured"}}
L010 {"g0": {"duration_s": 211.292132876, "outcome": "released", "release": {"TV0h": 35.01874542236328, "TV1h": 35.01874542236328, "Tf08": 36.16343688964844}, "row_reference": {"fast_c": 34.71851921081543, "slow_c": 34.71851921081543, "source_member": "cadence-cl-dev-02-l010", "span_ns": [2806839435458833, 2806899435458833]}, "row_release": {"fast_c": 35.01874542236328, "slow_c": 35.01874542236328}}, "own_reference": {"TV0h": 34.71851921081543, "TV1h": 34.71851921081543, "Tf08_median": 32.72953224182129, "status": "captured"}}
L011 {"g0": {"duration_s": 215.219995355, "outcome": "released", "release": {"TV0h": 35.05911636352539, "TV1h": 35.05911636352539, "Tf08": 36.255001068115234}, "row_reference": {"fast_c": 34.80009841918945, "slow_c": 34.80009841918945, "source_member": "cadence-cl-dev-02-l011", "span_ns": [2809336524378103, 2809396524378103]}, "row_release": {"fast_c": 35.05911636352539, "slow_c": 35.05911636352539}}, "own_reference": {"TV0h": 34.80009841918945, "TV1h": 34.80009841918945, "Tf08_median": 33.57046890258789, "status": "captured"}}
L012 {"g0": {"duration_s": 211.201251895, "outcome": "released", "release": {"TV0h": 35.066017150878906, "TV1h": 35.066017150878906, "Tf08": 36.53156280517578}, "row_reference": {"fast_c": 34.780282974243164, "slow_c": 34.780282974243164, "source_member": "cadence-cl-dev-02-l012", "span_ns": [2810597920704750, 2810657920704750]}, "row_release": {"fast_c": 35.066017150878906, "slow_c": 35.066017150878906}}, "own_reference": {"TV0h": 34.780282974243164, "TV1h": 34.780282974243164, "Tf08_median": 33.41437530517578, "status": "captured"}}
0
 powermode            0
Network Time: Off
no stray monitor
no root powermetrics
== measurement_mode verify 2026-11-16T11:20:55Z
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
FAIL  agent process present: 72639;72631 node scripts/codex-mcp-server.mjs;72632 npm exec @modelcontextprotocol/server-pdf --stdio HOME=/Users/edr LOGNAME=edr PATH=/Users/edr/.local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin SHELL=/bin/zsh;
INFO  display power state:  | "IOPowerManagement" = {"CapabilityFlags"=32768,"MaxPowerState"=1,"CurrentPowerState"=1} | "IOPowerManagement" = {"CapabilityFlags"=32768,"MaxPowerState"=1,"CurrentPowerState"=1}  (launch_align_r0.py runs displaysleepnow + dwell per span; not a gate)
PASS  /private/tmp entries: 1688 < 10000
PASS  free disk: 63 GiB >= 60
PASS  no High Power marker
PASS  keep-awake caffeinate assertion present
VERIFY FAILED: 1 mismatch(es)
verify rc 1
```
