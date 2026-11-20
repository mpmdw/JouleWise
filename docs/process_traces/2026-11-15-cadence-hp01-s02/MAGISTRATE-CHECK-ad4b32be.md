# hp-01-s02 Check, magistrate ad4b32be (headless, Opus 5.5), 2026-11-15 07:14 PST

Item 338 "Check" run verbatim: its fenced blocks (power reads, maintenance line, receipt asserts, RL-157 §1 print, RL-150 R1 print) concatenated with PY (align-pilot2 venv), OUT, CUSTODY and `ARG=02:00-02:35` (the argument recorded at the arm, RUN_STATE 339) set; cwd the span's own worktree `/Users/edr/code/jw-wt/cadence-hp01-s02` at `dd206025a`. Script: custody `cadence-hp01-s02-postcheck-ad4b32be.sh` (diffed against 2172c7d2's hp-01-s01 Check script: only OUT and the roster differ); output: custody `cadence-hp01-s02-postcheck-out-ad4b32be.txt` (reproduced below). The maintenance log itself is `$OUT/maintenance-log.txt`, not committed. Restore owed was NOT run: powermode 0, no marker, receipt and `span/result.json` present with `restore_proven` true.

Before the Check: no `standdown.request`, no `desk_fence.json`, no `com.joulewise.(night|align-r0)` label loaded (the grep count printed 0; only `com.joulewise.magistrate` listed), receipt mtime 07:09:39 PST (ended epoch 1794755379.34). This activation spawned 07:13:01, after the close.

measurement_mode NOTE 1: the one FAIL names 97639 (node codex-mcp-server, ppid 97624 = this magistrate), 97640 (npm server-pdf, ppid 97624) and 97643 (codex, ppid 97642 = node codex app-server, ppid 97639). All in this magistrate's tree. WARN lines (battery limit syntax, softwareupdate schedule) recorded, not gates.

Intervals (local, from chain-stages and leg_summary): soak ended and `high_power` set 05:46:29; L004 05:46:30-06:07:11; L005 06:07:12-06:28:01; L006 06:28:01-06:48:50; L007 06:48:51-07:09:38. One attempt each, no load redo (quota 2 unused). The span did not cross 00:00 and did not touch 02:00-02:35.

Maintenance overlap (print only): `dasd` logs about 1,400-2,100 lines per 10 min through the whole span (2,122 in 05:10, during the soak), as in hp-01-s01 and dev-01-s04. `mobileassetd` 173 lines in 06:40 (L006's last 9 min and L007's first 1 min; the bucket is not split), 3-21 elsewhere (05:00, 05:10, 05:40, 06:30, 06:50); `backupd` 3-24 per bucket; `softwareupdated` 17 and 37 in 05:00/05:10 (before L004) and 8 in 06:10 (L005). L004 has `os_level_max` 2 and `pm_nominal` false (L005-L007: 0 and true); no leg has a redo reason; rule 5 judgment is left to the desk.

Admission (D1, from each leg_summary): admitted 4 of 4; every leg's record shows AC powermode 2 at episode start; `high_power.revoked` null; `high_power.before_restore` {ac_powermode 2, marker present, marker_is_this_spans true, pmset_error null}. No named stop in the receipt (`fault` false, `error` null); the Air desk builds `stops.json`.

LEG_OVERTIME: none (wall 1,241.1 / 1,248.9 / 1,248.8 / 1,247.2 s against 1.5 x 1,251 = 1,876.5 s; all inside budget_s).

RL-157 §1: soak end to mode set 0.0 s; high_power end to L004 attempt start 0.7 s; to L004's G0 entry 517.2 s; G0 durations 200.9 / 208.1 / 204.0 / 204.1 s, all released.

## Check output, as printed

```
== check Sun Nov 15 07:14:24 PST 2026 epoch 1794755664
0
pmset -g custom AC powermode 0
no High Power marker
night.lock: no holder
 powermode            0
Network Time: Off
no stray monitor
no root powermetrics
== measurement_mode verify 2026-11-15T15:14:25Z
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
FAIL  agent process present: 97643;97639 node scripts/codex-mcp-server.mjs;97640 npm exec @modelcontextprotocol/server-pdf --stdio HOME=/Users/edr LOGNAME=edr PATH=/Users/edr/.local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin SHELL=/bin/zsh;
INFO  display power state:  | "IOPowerManagement" = {"CapabilityFlags"=32768,"MaxPowerState"=1,"CurrentPowerState"=1} | "IOPowerManagement" = {"CapabilityFlags"=32768,"MaxPowerState"=1,"CurrentPowerState"=1}  (launch_align_r0.py runs displaysleepnow + dwell per span; not a gate)
PASS  /private/tmp entries: 1659 < 10000
PASS  free disk: 68 GiB >= 60
PASS  no High Power marker
PASS  keep-awake caffeinate assertion present
VERIFY FAILED: 1 mismatch(es)
verify rc 1
maintenance window 2026-11-15 05:09:57 .. 2026-11-15 07:09:39
log show rc 0
   31381
05:00 backupd 3
05:00 dasd 18
05:00 mds 6
05:00 mobileassetd 21
05:00 softwareupdated 17
05:10 backupd 6
05:10 dasd 2122
05:10 mobileassetd 12
05:10 softwareupdated 37
05:20 dasd 1610
05:30 backupd 24
05:30 dasd 1677
05:40 backupd 6
05:40 dasd 1704
05:40 mobileassetd 3
05:50 backupd 24
05:50 dasd 1499
06:00 backupd 9
06:00 dasd 1485
06:10 backupd 6
06:10 dasd 1914
06:10 softwareupdated 8
06:20 dasd 1503
06:30 backupd 24
06:30 dasd 1382
06:30 mobileassetd 3
06:40 backupd 6
06:40 dasd 1752
06:40 mobileassetd 173
06:50 backupd 24
06:50 dasd 1676
06:50 mobileassetd 4
07:00 backupd 24
07:00 dasd 1911
{"batch_windows": ["02:00-02:35"], "error": null, "late_signals": null, "legs_finished": 4, "legs_planned": 4, "load_redos_used": 0, "meter": {"bad_polls": 0, "elapsed_s": 7091.811091333, "polls": 35459, "present": true, "proven_stopped": true, "usb_errors": 0}, "rc": 0, "roster": ["L004", "L005", "L006", "L007"], "runner_kind": "cadence-legs-v1", "span_result": {"chain_exit_code": 0, "chain_outcome": "COMPLETE", "fault": false, "outcome": "MEASURED_OK", "restore_proven": true, "verdict": "4/4 legs run"}}
[('deadline', 0), ('frozen', 0), ('night_agents', 0), ('ac_power', 0), ('condition13', 0), ('host_lock', 0), ('high_power_marker_absent', 0), ('start-agents', 0), ('start-meter', 0), ('start-volumes', 0), ('read_power', 0), ('powermode_guard', 0), ('display', 0), ('dwell', 0), ('plan', 0), ('before-soak-volumes', 0), ('soak', 0), ('high_power', 0), ('before-L004-volumes', 0), ('L004.a1-powermode', 0), ('L004.a1', 0), ('before-L005-volumes', 0), ('L005.a1-powermode', 0), ('L005.a1', 0), ('before-L006-volumes', 0), ('L006.a1-powermode', 0), ('L006.a1', 0), ('before-L007-volumes', 0), ('L007.a1-powermode', 0), ('L007.a1', 0), ('power_last_look', 0), ('restore', 0), ('power_proof', 0), ('host_lock_release', 0), ('stop-volumes', 0), ('stop-meter', 0), ('stop-agents', 0), ('close-volumes', 0)]
high_power.revoked null
high_power.before_restore {"ac_powermode": 2, "host_marker": "/Users/Shared/JouleWise/host-power/high-power.marker", "host_marker_present": true, "marker_is_this_spans": true, "pmset_error": null}
high_power.restore {"action": "restore_automatic", "attempts": 1, "deferred": false, "ok": true}
high_power.close_proof {"ac_powermode": 0, "host_marker": "/Users/Shared/JouleWise/host-power/high-power.marker", "host_marker_present": false, "pmset_error": null, "proven": true}
result {"chain_exit_code": 0, "chain_outcome": "COMPLETE", "fault": false, "outcome": "MEASURED_OK", "restore_proven": true, "verdict": "4/4 legs run"}
L004 admitted True revoked False leg_record.ac_powermode {"observed_at": "episode_start", "source": "pmset -g custom (AC Power block, exact powermode key)", "value": 2} g0_s 200.899775687 wall_s 1241.0831580162048 budget_s 1251 over_1.5x False
L004 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794751631.6360729, "g0_outcome": "released", "g0_s": 200.899775687, "leg_id": "L004", "os_level_max": 2, "pm_nominal": false, "redo_reasons": [], "seed": 954626506, "start_band": "q0", "started_epoch_s": 1794750390.552447, "wall_s": 1241.0831580162048}
L005 admitted True revoked False leg_record.ac_powermode {"observed_at": "episode_start", "source": "pmset -g custom (AC Power block, exact powermode key)", "value": 2} g0_s 208.089427291 wall_s 1248.8624351024628 budget_s 1251 over_1.5x False
L005 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794752881.176391, "g0_outcome": "released", "g0_s": 208.089427291, "leg_id": "L005", "os_level_max": 0, "pm_nominal": true, "redo_reasons": [], "seed": 983646378, "start_band": "q0", "started_epoch_s": 1794751632.313418, "wall_s": 1248.8624351024628}
L006 admitted True revoked False leg_record.ac_powermode {"observed_at": "episode_start", "source": "pmset -g custom (AC Power block, exact powermode key)", "value": 2} g0_s 204.015231812 wall_s 1248.7706518173218 budget_s 1251 over_1.5x False
L006 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794754130.657872, "g0_outcome": "released", "g0_s": 204.015231812, "leg_id": "L006", "os_level_max": 0, "pm_nominal": true, "redo_reasons": [], "seed": 2048410933, "start_band": "q0", "started_epoch_s": 1794752881.8866491, "wall_s": 1248.7706518173218}
L007 admitted True revoked False leg_record.ac_powermode {"observed_at": "episode_start", "source": "pmset -g custom (AC Power block, exact powermode key)", "value": 2} g0_s 204.081918417 wall_s 1247.17560505867 budget_s 1251 over_1.5x False
L007 {"admitted": true, "attempts": 1, "band_reached": true, "budget_s": 1251, "contaminated_redos": 0, "ended_epoch_s": 1794755378.498869, "g0_outcome": "released", "g0_s": 204.081918417, "leg_id": "L007", "os_level_max": 0, "pm_nominal": true, "redo_reasons": [], "seed": 1350544700, "start_band": "q0", "started_epoch_s": 1794754131.32286, "wall_s": 1247.17560505867}
meter {
 "bad_polls": 0,
 "elapsed_s": 7091.811091333,
 "polls": 35459,
 "present": true,
 "proven_stopped": true,
 "usb_errors": 0
}
RECEIPT OK
RL-157 §1 {"L004_attempt_start_epoch_s": 1794750390.552455, "L004_attempts": 1, "L004_g0_entry_epoch_s": 1794750907.1404061, "high_power_end_epoch_s": 1794750389.8932219, "mode_set_to_L004_G0_start_s": 517.2, "mode_set_to_L004_attempt_start_s": 0.7, "soak_end_epoch_s": 1794750389.863269, "soak_end_to_mode_set_s": 0.0}
soak_reference {'TV0h': 34.16996564229329, 'TV1h': 34.16996564229329} Tf08_last1200s_mean 27.04401355425517
L004 {"g0": {"duration_s": 200.899775687, "outcome": "released", "release": {"TV0h": 34.91654968261719, "TV1h": 34.91654968261719, "Tf08": 35.19499969482422}, "row_reference": {"fast_c": 34.17672348022461, "slow_c": 34.17672348022461, "source_member": "cadence-cl-hp-01-l004", "span_ns": [2735080172391166, 2735140172391166]}, "row_release": {"fast_c": 34.91654968261719, "slow_c": 34.91654968261719}}, "own_reference": {"TV0h": 34.17672348022461, "TV1h": 34.17672348022461, "Tf08_median": 27.223593711853027, "status": "captured"}}
L005 {"g0": {"duration_s": 208.089427291, "outcome": "released", "release": {"TV0h": 35.07354736328125, "TV1h": 35.07354736328125, "Tf08": 36.81624984741211}, "row_reference": {"fast_c": 34.67489814758301, "slow_c": 34.67489814758301, "source_member": "cadence-cl-hp-01-l005", "span_ns": [2736321364902708, 2736381364902708]}, "row_release": {"fast_c": 35.07354736328125, "slow_c": 35.07354736328125}}, "own_reference": {"TV0h": 34.67489814758301, "TV1h": 34.67489814758301, "Tf08_median": 32.48781204223633, "status": "captured"}}
L006 {"g0": {"duration_s": 204.015231812, "outcome": "released", "release": {"TV0h": 35.02997589111328, "TV1h": 35.02997589111328, "Tf08": 36.57374954223633}, "row_reference": {"fast_c": 34.652565002441406, "slow_c": 34.652565002441406, "source_member": "cadence-cl-hp-01-l006", "span_ns": [2737571786109854, 2737631786109854]}, "row_release": {"fast_c": 35.02997589111328, "slow_c": 35.02997589111328}}, "own_reference": {"TV0h": 34.652565002441406, "TV1h": 34.652565002441406, "Tf08_median": 32.18328094482422, "status": "captured"}}
L007 {"g0": {"duration_s": 204.081918417, "outcome": "released", "release": {"TV0h": 35.016910552978516, "TV1h": 35.016910552978516, "Tf08": 36.0859375}, "row_reference": {"fast_c": 34.662071228027344, "slow_c": 34.662071228027344, "source_member": "cadence-cl-hp-01-l007", "span_ns": [2738820980745103, 2738880980745103]}, "row_release": {"fast_c": 35.016910552978516, "slow_c": 35.016910552978516}}, "own_reference": {"TV0h": 34.662071228027344, "TV1h": 34.662071228027344, "Tf08_median": 32.21406364440918, "status": "captured"}}
```
