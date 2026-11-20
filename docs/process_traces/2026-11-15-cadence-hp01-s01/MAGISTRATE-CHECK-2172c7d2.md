# hp-01-s01 Check, magistrate 2172c7d2 (headless, Opus 5.5), 2026-11-15 04:48 PST

Item 334 "Check" run verbatim: its fenced blocks (power reads, maintenance line, receipt asserts, RL-157 §1 print, RL-150 R1 print) concatenated with PY (align-pilot2 venv), OUT, CUSTODY and `ARG=02:00-02:35` (the argument recorded at the arm, RUN_STATE 335) set; cwd the span's own worktree `/Users/edr/code/jw-wt/cadence-hp01-s01` at `dd206025a`. Script: custody `cadence-hp01-s01-postcheck-2172c7d2.sh`; output: custody `cadence-hp01-s01-postcheck-out-2172c7d2.txt` (reproduced below). The maintenance log itself is `$OUT/maintenance-log.txt`, not committed. Restore owed was NOT run: powermode 0, no marker, receipt and `span/result.json` present with `restore_proven` true.

Before the Check: the fence process (pid 80656) gone, no `desk_fence.json`, no `com.joulewise.(night|align-r0)` label loaded (the grep count printed 0), receipt mtime 04:45:00 PST. This activation spawned 04:47:47, after the close.

measurement_mode NOTE 1: the one FAIL names 87380 (node codex-mcp-server, ppid 87365 = this magistrate), 87381 (npm server-pdf, ppid 87365) and 87384 (codex, ppid 87383 = node codex app-server, ppid 87380). All in this magistrate's tree. WARN lines (battery limit syntax, softwareupdate schedule) recorded, not gates.

Intervals (local, from chain-stages and leg_summary): soak 03:12:38-03:42:38 (1,800 s, Automatic); `high_power` 03:42:38; L001 03:42:39-04:03:18; L002 04:03:18-04:24:10; L003 04:24:11-04:45:00. One attempt each, no load redo (quota 2 unused). The span did not cross 00:00.

Maintenance overlap (print only): `dasd` logs about 1,500-1,900 lines per 10 min through the whole span, as in `dev-01-s04`. `mobileassetd` 122 lines in 03:50 (L001), 417 in 04:20 (L002's last 4 min and L003's first 6 min; the bucket is not split), 3 each in 03:40 and 04:10; `backupd` 6-33 per bucket; `softwareupdated` 8 in 04:10 (L002). Every leg has `os_level_max` 0, `pm_nominal` true and no redo reason; rule 5 judgment is left to the desk.

RL-150 R9 (rule 6 = High Power): (1) three closes with complete records: yes (3 leg summaries, span result, meter); (2) admitted 3 of 3 (from each leg_summary); (3) no excluded leg; every leg's record shows AC powermode 2 at episode start, `high_power.revoked` null; (4) left to the lead's hand-read. No named stop in the receipt (`fault` false, `error` null); the Air desk builds `stops.json`.

LEG_OVERTIME: none (wall 1,238.4 / 1,252.1 / 1,248.9 s against 1.5 x 1,251 = 1,876.5 s). L002 ran 1.1 s over its budget_s, well inside 1.5x.

RL-157 §1: high_power end to L001 attempt start 0.7 s; to L001's G0 entry 516.6 s; G0 durations 198.7 / 211.2 / 204.1 s, all released.

## Check output, as printed

```
== check Sun Nov 15 04:48:46 PST 2026 epoch 1794746926
0
pmset -g custom AC powermode 0
no High Power marker
night.lock: no holder
 powermode            0
Network Time: Off
no stray monitor
no root powermetrics
== measurement_mode verify 2026-11-15T12:48:46Z
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
FAIL  agent process present: 87384;87380 node scripts/codex-mcp-server.mjs;87381 npm exec @modelcontextprotocol/server-pdf --stdio HOME=/Users/edr LOGNAME=edr PATH=/Users/edr/.local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin SHELL=/bin/zsh;
INFO  display power state:  | "IOPowerManagement" = {"CapabilityFlags"=32768,"MaxPowerState"=1,"CurrentPowerState"=1} | "IOPowerManagement" = {"CapabilityFlags"=32768,"MaxPowerState"=1,"CurrentPowerState"=1}  (launch_align_r0.py runs displaysleepnow + dwell per span; not a gate)
PASS  /private/tmp entries: 1647 < 10000
PASS  free disk: 71 GiB >= 60
PASS  no High Power marker
PASS  keep-awake caffeinate assertion present
VERIFY FAILED: 1 mismatch(es)
verify rc 1
maintenance window 2026-11-15 03:05:27 .. 2026-11-15 04:45:00
log show rc 0
   27187
03:00 backupd 3
03:00 dasd 1071
03:00 mds 6
03:00 softwareupdated 8
03:10 backupd 6
03:10 dasd 1729
03:10 mobileassetd 3
03:10 softwareupdated 8
03:20 dasd 1643
03:30 dasd 1495
03:40 backupd 33
03:40 dasd 1770
03:40 mobileassetd 3
03:50 backupd 27
03:50 dasd 1581
03:50 mobileassetd 122
04:00 backupd 9
04:00 dasd 1695
04:10 backupd 30
04:10 dasd 1893
04:10 mobileassetd 3
04:10 softwareupdated 8
04:20 dasd 1768
04:20 mds 5
04:20 mobileassetd 417
04:30 backupd 24
04:30 dasd 1852
04:40 backupd 6
04:40 dasd 802
{"batch_windows": ["02:00-02:35"], "error": null, "late_signals": null, "legs_finished": 3, "legs_planned": 3, "load_redos_used": 0, "meter": {"bad_polls": 0, "elapsed_s": 5844.610897875, "polls": 29223, "present": true, "proven_stopped": true, "usb_errors": 0}, "rc": 0, "roster": ["L001", "L002", "L003"], "runner_kind": "cadence-legs-v1", "span_result": {"chain_exit_code": 0, "chain_outcome": "COMPLETE", "fault": false, "outcome": "MEASURED_OK", "restore_proven": true, "verdict": "3/3 legs run"}}
[('deadline', 0), ('frozen', 0), ('night_agents', 0), ('ac_power', 0), ('condition13', 0), ('host_lock', 0), ('high_power_marker_absent', 0), ('start-agents', 0), ('start-meter', 0), ('start-volumes', 0), ('read_power', 0), ('powermode_guard', 0), ('display', 0), ('dwell', 0), ('plan', 0), ('before-soak-volumes', 0), ('soak', 0), ('high_power', 0), ('before-L001-volumes', 0), ('L001.a1-powermode', 0), ('L001.a1', 0), ('before-L002-volumes', 0), ('L002.a1-powermode', 0), ('L002.a1', 0), ('before-L003-volumes', 0), ('L003.a1-powermode', 0), ('L003.a1', 0), ('power_last_look', 0), ('restore', 0), ('power_proof', 0), ('host_lock_release', 0), ('stop-volumes', 0), ('stop-meter', 0), ('stop-agents', 0), ('close-volumes', 0)]
high_power.revoked null
high_power.before_restore {"ac_powermode": 2, "host_marker": "/Users/Shared/JouleWise/host-power/high-power.marker", "host_marker_present": true, "marker_is_this_spans": true, "pmset_error": null}
high_power.restore {"action": "restore_automatic", "attempts": 1, "deferred": false, "ok": true}
high_power.close_proof {"ac_powermode": 0, "host_marker": "/Users/Shared/JouleWise/host-power/high-power.marker", "host_marker_present": false, "pmset_error": null, "proven": true}
result {"chain_exit_code": 0, "chain_outcome": "COMPLETE", "fault": false, "outcome": "MEASURED_OK", "restore_proven": true, "verdict": "3/3 legs run"}
L001 admitted True revoked False leg_record.ac_powermode {"observed_at": "episode_start", "source": "pmset -g custom (AC Power block, exact powermode key)", "value": 2} g0_s 198.655667209 wall_s 1238.4428086280823 budget_s 1251 over_1.5x False
L001 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794744197.6601129, "g0_outcome": "released", "g0_s": 198.655667209, "leg_id": "L001", "os_level_max": 0, "pm_nominal": true, "redo_reasons": [], "seed": 4048693807, "start_band": "q0", "started_epoch_s": 1794742959.2168362, "wall_s": 1238.4428086280823}
L002 admitted True revoked False leg_record.ac_powermode {"observed_at": "episode_start", "source": "pmset -g custom (AC Power block, exact powermode key)", "value": 2} g0_s 211.212001083 wall_s 1252.1031920909882 budget_s 1251 over_1.5x False
L002 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794745450.424456, "g0_outcome": "released", "g0_s": 211.212001083, "leg_id": "L002", "os_level_max": 0, "pm_nominal": true, "redo_reasons": [], "seed": 1251089132, "start_band": "q0", "started_epoch_s": 1794744198.320852, "wall_s": 1252.1031920909882}
L003 admitted True revoked False leg_record.ac_powermode {"observed_at": "episode_start", "source": "pmset -g custom (AC Power block, exact powermode key)", "value": 2} g0_s 204.131255501 wall_s 1248.8816318511963 budget_s 1251 over_1.5x False
L003 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794746699.9642398, "g0_outcome": "released", "g0_s": 204.131255501, "leg_id": "L003", "os_level_max": 0, "pm_nominal": true, "redo_reasons": [], "seed": 3543179003, "start_band": "q0", "started_epoch_s": 1794745451.082077, "wall_s": 1248.8816318511963}
meter {
 "bad_polls": 0,
 "elapsed_s": 5844.610897875,
 "polls": 29223,
 "present": true,
 "proven_stopped": true,
 "usb_errors": 0
}
RECEIPT OK
RL-157 §1 {"L001_attempt_start_epoch_s": 1794742959.2168472, "L001_attempts": 1, "L001_g0_entry_epoch_s": 1794743475.1567109, "high_power_end_epoch_s": 1794742958.5519328, "mode_set_to_L001_G0_start_s": 516.6, "mode_set_to_L001_attempt_start_s": 0.7, "soak_end_epoch_s": 1794742958.5203378, "soak_end_to_mode_set_s": 0.0}
soak_reference {'TV0h': 34.18005036036173, 'TV1h': 34.18005036036173} Tf08_last1200s_mean 27.18221978823344
L001 {"g0": {"duration_s": 198.655667209, "outcome": "released", "release": {"TV0h": 34.89183807373047, "TV1h": 34.89183807373047, "Tf08": 34.87312316894531}, "row_reference": {"fast_c": 34.18595886230469, "slow_c": 34.18595886230469, "source_member": "cadence-cl-hp-01-l001", "span_ns": [2727648760374021, 2727708760374021]}, "row_release": {"fast_c": 34.89183807373047, "slow_c": 34.89183807373047}}, "own_reference": {"TV0h": 34.18595886230469, "TV1h": 34.18595886230469, "Tf08_median": 27.405780792236328, "status": "captured"}}
L002 {"g0": {"duration_s": 211.212001083, "outcome": "released", "release": {"TV0h": 35.00049591064453, "TV1h": 35.00049591064453, "Tf08": 35.760623931884766}, "row_reference": {"fast_c": 34.68831825256348, "slow_c": 34.68831825256348, "source_member": "cadence-cl-hp-01-l002", "span_ns": [2728888218211020, 2728948218211020]}, "row_release": {"fast_c": 35.00049591064453, "slow_c": 35.00049591064453}}, "own_reference": {"TV0h": 34.68831825256348, "TV1h": 34.68831825256348, "Tf08_median": 32.50687599182129, "status": "captured"}}
L003 {"g0": {"duration_s": 204.131255501, "outcome": "released", "release": {"TV0h": 35.03055191040039, "TV1h": 35.03055191040039, "Tf08": 36.0959358215332}, "row_reference": {"fast_c": 34.68604278564453, "slow_c": 34.68604278564453, "source_member": "cadence-cl-hp-01-l003", "span_ns": [2730140306588208, 2730200306588208]}, "row_release": {"fast_c": 35.03055191040039, "slow_c": 35.03055191040039}}, "own_reference": {"TV0h": 34.68604278564453, "TV1h": 34.68604278564453, "Tf08_median": 32.43874931335449, "status": "captured"}}
```
