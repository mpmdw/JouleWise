# hp-01-s03 Check, magistrate 2e53c580 (headless, Opus 5.5), 2026-11-15 09:49 PST

Item 341 "Check" run verbatim: its fenced blocks (power reads, maintenance line, receipt asserts, RL-157 §1 print, RL-150 R1 print) concatenated with PY (align-pilot2 venv), OUT, CUSTODY and `ARG=02:00-02:35` (the argument recorded at the arm, RUN_STATE 342) set; cwd the span's own worktree `/Users/edr/code/jw-wt/cadence-hp01-s03` at `dd206025a`. Script: custody `cadence-hp01-s03-postcheck-2e53c580.sh`, derived from ad4b32be's hp-01-s02 script by substituting OUT, worktree and roster (L004-L007 to L008-L012); every line from the power reads on was then matched verbatim against item 341's Check text (no line missing from it). Output: custody `cadence-hp01-s03-postcheck-out-2e53c580.txt` (reproduced below). The maintenance log itself is `$OUT/maintenance-log.txt`, not committed. Restore owed was NOT run: powermode 0, no marker, receipt and `span/result.json` present with `restore_proven` true.

Before the Check: no `standdown.request`, no `desk_fence.json`, fence pid 99437 gone, no `com.joulewise.(night|align-r0)` label loaded (the grep count printed 0; only `com.joulewise.magistrate` listed), receipt mtime 09:45:50 PST (ended epoch 1794764750.92). This activation spawned 09:48:14, after the close.

measurement_mode NOTE 1: the one FAIL names 9854 (node codex-mcp-server, ppid 9839 = this magistrate), 9855 (npm server-pdf, ppid 9839) and 9858 (codex, ppid 9857 = node codex app-server, ppid 9854). All in this magistrate's tree. WARN lines (battery limit syntax, softwareupdate schedule) recorded, not gates.

Intervals (local, from chain-stages and leg_summary): launch 07:26:00 (stamp 07:24:52); soak ended and `high_power` set 08:01:21; L008 08:01:21-08:22:15; L009 08:22:15-08:43:11; L010 08:43:11-09:04:09; L011 09:04:09-09:24:59; L012 09:25:00-09:45:50. One attempt each, no load redo (quota 2 unused). The span did not cross 00:00 and did not touch 02:00-02:35.

Maintenance overlap (print only): `dasd` logs about 900-3,100 lines per 10 min through the whole span (3,128 in 08:00, L008; 2,845 in 09:20, L011 end / L012 start), as in earlier spans. `mobileassetd` 1,396 lines in 09:20 (L011's last 5 min and L012's first 5 min; the bucket is not split), 208 in 08:00 and 177 in 08:10 (L008), 179 in 08:20 (L008 end / L009 start), 122 in 07:50 (soak), 69 in 09:00 (L010 / L011), 3-4 elsewhere; `backupd` 3-24 per bucket; `softwareupdated` 8 in 07:20, 08:10 (L008) and 09:10 (L011); `mds` 6 in 07:20, 3 in 09:20. L008 has `os_level_max` 2 and `pm_nominal` false (L009-L012: 0 and true), the same first-leg pattern as L004 in hp-01-s02; no leg has a redo reason; rule 5 judgment is left to the desk.

Admission (D1, from each leg_summary): admitted 5 of 5; every leg's record shows AC powermode 2 at episode start; `high_power.revoked` null; `high_power.before_restore` {ac_powermode 2, marker present, marker_is_this_spans true, pmset_error null}. No named stop in the receipt (`fault` false, `error` null); the Air desk builds `stops.json`.

LEG_OVERTIME: none (wall 1,253.1 / 1,255.4 / 1,257.3 / 1,250.1 / 1,249.5 s against 1.5 x 1,251 = 1,876.5 s). Three legs ran 2-6 s over budget_s itself (L008, L009, L010); not a stop.

RL-157 §1: soak end to mode set 0.0 s; high_power end to L008 attempt start 0.7 s; to L008's G0 entry 517.8 s; G0 durations 204.9 / 212.1 / 213.2 / 210.2 / 204.0 s, all released.

Restore lines: `power_last_look`, `restore`, `power_proof`, `host_lock_release`, `stop-volumes`, `stop-meter`, `stop-agents`, `close-volumes` all rc 0; restore `{action restore_automatic, attempts 1, deferred false, ok true}`; close proof `{ac_powermode 0, host_marker_present false, pmset_error null, proven true}`. Meter: 41,860 polls, 0 bad, 0 USB errors, proven stopped.

## Check output, as printed

```
== check Sun Nov 15 09:49:03 PST 2026 epoch 1794764943
0
pmset -g custom AC powermode 0
no High Power marker
night.lock: no holder
 powermode            0
Network Time: Off
no stray monitor
no root powermetrics
== measurement_mode verify 2026-11-15T17:49:04Z
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
FAIL  agent process present: 9858;9854 node scripts/codex-mcp-server.mjs;9855 npm exec @modelcontextprotocol/server-pdf --stdio HOME=/Users/edr LOGNAME=edr PATH=/Users/edr/.local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin SHELL=/bin/zsh;
INFO  display power state:  | "IOPowerManagement" = {"CapabilityFlags"=32768,"MaxPowerState"=1,"CurrentPowerState"=1} | "IOPowerManagement" = {"CapabilityFlags"=32768,"MaxPowerState"=1,"CurrentPowerState"=1}  (launch_align_r0.py runs displaysleepnow + dwell per span; not a gate)
PASS  /private/tmp entries: 1664 < 10000
PASS  free disk: 65 GiB >= 60
PASS  no High Power marker
PASS  keep-awake caffeinate assertion present
VERIFY FAILED: 1 mismatch(es)
verify rc 1
maintenance window 2026-11-15 07:24:52 .. 2026-11-15 09:45:50
log show rc 0
   40635
07:20 backupd 3
07:20 dasd 696
07:20 mds 6
07:20 softwareupdated 8
07:30 dasd 1237
07:40 backupd 6
07:40 dasd 1597
07:40 mobileassetd 3
07:50 backupd 24
07:50 dasd 1432
07:50 mobileassetd 122
08:00 backupd 9
08:00 dasd 3128
08:00 mobileassetd 208
08:10 backupd 6
08:10 dasd 1777
08:10 mobileassetd 177
08:10 softwareupdated 8
08:20 dasd 1544
08:20 mobileassetd 179
08:30 dasd 1565
08:30 mobileassetd 3
08:40 backupd 6
08:40 dasd 1693
08:50 backupd 24
08:50 dasd 1586
08:50 mobileassetd 4
09:00 backupd 9
09:00 dasd 1727
09:00 mobileassetd 69
09:10 backupd 6
09:10 dasd 1726
09:10 mobileassetd 3
09:10 softwareupdated 8
09:20 dasd 2845
09:20 mds 3
09:20 mobileassetd 1396
09:30 dasd 1486
09:40 backupd 6
09:40 dasd 921
{"batch_windows": ["02:00-02:35"], "error": null, "late_signals": null, "legs_finished": 5, "legs_planned": 5, "load_redos_used": 0, "meter": {"bad_polls": 0, "elapsed_s": 8372.011276083, "polls": 41860, "present": true, "proven_stopped": true, "usb_errors": 0}, "rc": 0, "roster": ["L008", "L009", "L010", "L011", "L012"], "runner_kind": "cadence-legs-v1", "span_result": {"chain_exit_code": 0, "chain_outcome": "COMPLETE", "fault": false, "outcome": "MEASURED_OK", "restore_proven": true, "verdict": "5/5 legs run"}}
[('deadline', 0), ('frozen', 0), ('night_agents', 0), ('ac_power', 0), ('condition13', 0), ('host_lock', 0), ('high_power_marker_absent', 0), ('start-agents', 0), ('start-meter', 0), ('start-volumes', 0), ('read_power', 0), ('powermode_guard', 0), ('display', 0), ('dwell', 0), ('plan', 0), ('before-soak-volumes', 0), ('soak', 0), ('high_power', 0), ('before-L008-volumes', 0), ('L008.a1-powermode', 0), ('L008.a1', 0), ('before-L009-volumes', 0), ('L009.a1-powermode', 0), ('L009.a1', 0), ('before-L010-volumes', 0), ('L010.a1-powermode', 0), ('L010.a1', 0), ('before-L011-volumes', 0), ('L011.a1-powermode', 0), ('L011.a1', 0), ('before-L012-volumes', 0), ('L012.a1-powermode', 0), ('L012.a1', 0), ('power_last_look', 0), ('restore', 0), ('power_proof', 0), ('host_lock_release', 0), ('stop-volumes', 0), ('stop-meter', 0), ('stop-agents', 0), ('close-volumes', 0)]
high_power.revoked null
high_power.before_restore {"ac_powermode": 2, "host_marker": "/Users/Shared/JouleWise/host-power/high-power.marker", "host_marker_present": true, "marker_is_this_spans": true, "pmset_error": null}
high_power.restore {"action": "restore_automatic", "attempts": 1, "deferred": false, "ok": true}
high_power.close_proof {"ac_powermode": 0, "host_marker": "/Users/Shared/JouleWise/host-power/high-power.marker", "host_marker_present": false, "pmset_error": null, "proven": true}
result {"chain_exit_code": 0, "chain_outcome": "COMPLETE", "fault": false, "outcome": "MEASURED_OK", "restore_proven": true, "verdict": "5/5 legs run"}
L008 admitted True revoked False leg_record.ac_powermode {"observed_at": "episode_start", "source": "pmset -g custom (AC Power block, exact powermode key)", "value": 2} g0_s 204.949684228 wall_s 1253.1046578884125 budget_s 1251 over_1.5x False
L008 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794759735.10056, "g0_outcome": "released", "g0_s": 204.949684228, "leg_id": "L008", "os_level_max": 2, "pm_nominal": false, "redo_reasons": [], "seed": 1180804720, "start_band": "q0", "started_epoch_s": 1794758481.9954932, "wall_s": 1253.1046578884125}
L009 admitted True revoked False leg_record.ac_powermode {"observed_at": "episode_start", "source": "pmset -g custom (AC Power block, exact powermode key)", "value": 2} g0_s 212.137303439 wall_s 1255.368010044098 budget_s 1251 over_1.5x False
L009 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794760991.15302, "g0_outcome": "released", "g0_s": 212.137303439, "leg_id": "L009", "os_level_max": 0, "pm_nominal": true, "redo_reasons": [], "seed": 3701535075, "start_band": "q0", "started_epoch_s": 1794759735.784608, "wall_s": 1255.368010044098}
L010 admitted True revoked False leg_record.ac_powermode {"observed_at": "episode_start", "source": "pmset -g custom (AC Power block, exact powermode key)", "value": 2} g0_s 213.152328333 wall_s 1257.2693181037903 budget_s 1251 over_1.5x False
L010 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794762249.0903418, "g0_outcome": "released", "g0_s": 213.152328333, "leg_id": "L010", "os_level_max": 0, "pm_nominal": true, "redo_reasons": [], "seed": 2827066148, "start_band": "q0", "started_epoch_s": 1794760991.8206038, "wall_s": 1257.2693181037903}
L011 admitted True revoked False leg_record.ac_powermode {"observed_at": "episode_start", "source": "pmset -g custom (AC Power block, exact powermode key)", "value": 2} g0_s 210.169858501 wall_s 1250.0950140953064 budget_s 1251 over_1.5x False
L011 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794763499.8607209, "g0_outcome": "released", "g0_s": 210.169858501, "leg_id": "L011", "os_level_max": 0, "pm_nominal": true, "redo_reasons": [], "seed": 2178814401, "start_band": "q0", "started_epoch_s": 1794762249.765188, "wall_s": 1250.0950140953064}
L012 admitted True revoked False leg_record.ac_powermode {"observed_at": "episode_start", "source": "pmset -g custom (AC Power block, exact powermode key)", "value": 2} g0_s 203.96912123 wall_s 1249.4911050796509 budget_s 1251 over_1.5x False
L012 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794764750.083714, "g0_outcome": "released", "g0_s": 203.96912123, "leg_id": "L012", "os_level_max": 0, "pm_nominal": true, "redo_reasons": [], "seed": 1042807770, "start_band": "q0", "started_epoch_s": 1794763500.592098, "wall_s": 1249.4911050796509}
meter {
 "bad_polls": 0,
 "elapsed_s": 8372.011276083,
 "polls": 41860,
 "present": true,
 "proven_stopped": true,
 "usb_errors": 0
}
RECEIPT OK
RL-157 §1 {"L008_attempt_start_epoch_s": 1794758481.9955, "L008_attempts": 1, "L008_g0_entry_epoch_s": 1794758999.111317, "high_power_end_epoch_s": 1794758481.3329952, "mode_set_to_L008_G0_start_s": 517.8, "mode_set_to_L008_attempt_start_s": 0.7, "soak_end_epoch_s": 1794758481.301009, "soak_end_to_mode_set_s": 0.0}
soak_reference {'TV0h': 34.20161952972412, 'TV1h': 34.20161952972412} Tf08_last1200s_mean 27.403126834233603
L008 {"g0": {"duration_s": 204.949684228, "outcome": "released", "release": {"TV0h": 34.90441131591797, "TV1h": 34.90441131591797, "Tf08": 35.05406188964844}, "row_reference": {"fast_c": 34.18472862243652, "slow_c": 34.18472862243652, "source_member": "cadence-cl-hp-01-l008", "span_ns": [2743172802004146, 2743232802004146]}, "row_release": {"fast_c": 34.90441131591797, "slow_c": 34.90441131591797}}, "own_reference": {"TV0h": 34.18472862243652, "TV1h": 34.18472862243652, "Tf08_median": 27.348593711853027, "status": "captured"}}
L009 {"g0": {"duration_s": 212.137303439, "outcome": "released", "release": {"TV0h": 35.04010009765625, "TV1h": 35.04010009765625, "Tf08": 36.255313873291016}, "row_reference": {"fast_c": 34.68247032165527, "slow_c": 34.68247032165527, "source_member": "cadence-cl-hp-01-l009", "span_ns": [2744424892207333, 2744484892207333]}, "row_release": {"fast_c": 35.04010009765625, "slow_c": 35.04010009765625}}, "own_reference": {"TV0h": 34.68247032165527, "TV1h": 34.68247032165527, "Tf08_median": 32.53249931335449, "status": "captured"}}
L010 {"g0": {"duration_s": 213.152328333, "outcome": "released", "release": {"TV0h": 35.04212951660156, "TV1h": 35.04212951660156, "Tf08": 36.3515625}, "row_reference": {"fast_c": 34.665910720825195, "slow_c": 34.665910720825195, "source_member": "cadence-cl-hp-01-l010", "span_ns": [2745681502435458, 2745741502435458]}, "row_release": {"fast_c": 35.04212951660156, "slow_c": 35.04212951660156}}, "own_reference": {"TV0h": 34.665910720825195, "TV1h": 34.665910720825195, "Tf08_median": 32.28281211853027, "status": "captured"}}
L011 {"g0": {"duration_s": 210.169858501, "outcome": "released", "release": {"TV0h": 35.07563781738281, "TV1h": 35.07563781738281, "Tf08": 36.65687561035156}, "row_reference": {"fast_c": 34.67147445678711, "slow_c": 34.67147445678711, "source_member": "cadence-cl-hp-01-l011", "span_ns": [2746939005788208, 2746999005788208]}, "row_release": {"fast_c": 35.07563781738281, "slow_c": 35.07563781738281}}, "own_reference": {"TV0h": 34.67147445678711, "TV1h": 34.67147445678711, "Tf08_median": 32.32796859741211, "status": "captured"}}
L012 {"g0": {"duration_s": 203.96912123, "outcome": "released", "release": {"TV0h": 35.070953369140625, "TV1h": 35.070953369140625, "Tf08": 36.634376525878906}, "row_reference": {"fast_c": 34.66135215759277, "slow_c": 34.66135215759277, "source_member": "cadence-cl-hp-01-l012", "span_ns": [2748189658483729, 2748249658483729]}, "row_release": {"fast_c": 35.070953369140625, "slow_c": 35.070953369140625}}, "own_reference": {"TV0h": 34.66135215759277, "TV1h": 34.66135215759277, "Tf08_median": 32.21421813964844, "status": "captured"}}
```
