# ALIGN v4 R0 re-run 10 (2026-11-07 18:25 PST): refused in `smc` by routined (CoreRoutine) during a background-task wave; display was off

- Record: `/Users/edr/night-align/r0-v4-20261108T0224Z` (created 02:25:18Z, finished 02:41:45Z; 987 s wall). Status `fail`, `complete_r0` false, smc `fail` (exit 3, `NotQuiet`, after 956.8 s).
- Measurement checkout `5f817856b`, clean. Launch id `1b20b6783709436f88395f7a818ce623`, deadline 23:05 PST (`1794121500`). Launched by activation 707dd8f4, which exited cleanly at 18:25:18 PST (watchdog event 6458) before the desk fence engaged (18:28:13, event 6459). The next activation (5bcfa84e) spawned at 18:43:15, after the run ended. No agent session was alive during the census.
- `report.json` sha256 `0a8c79351a41bd5db9d7c5628ef8242e2805e285385f436eae429b35012e1e6b`; `report.md` sha256 `a4da53348cc34e4bee5d2f466f440f6d2097057fb2f1cc6392007052c93b139f`.
- SMC journal `smc/samples.jsonl`, 49,226,165 bytes, sha256 `77410460b8d9570b98a1abed31eaf784549c472d3e573cc872b18e033ef22879` (kept on the Mac, not committed).

## Display
First R0 run with the display off: `pmset displaysleepnow` at 18:08:12 PST (RUN_STATE 206). `pmset -g log` shows no "Display is turned on" after that through 18:43, so the display stayed off for the whole run. No WindowServer or ControlCenter entry is over the limit in the refusal row.

## Refusal
Census interval 18:41:09.6-18:41:45.5 PST (35.9 s): `routined` pid 794 at 0.0521 CPU-s/s against the 0.05 per-process limit (the only process over). Outside-tree total 0.087 CPU-s/s listed, aggregate 0.180; host busy 0.266 of 16 CPUs. The refusal is correct under the current rule: the contention was real but small (4% over the bar).

## Cause: a dasd background-task wave
The unified log in the interval shows dasd starting a wave of maintenance/utility activities at 18:41:39 and 18:41:55: five `com.apple.private.contacts.accounts.validate-cache` instances (contactsd had spawned ten helpers at 18:40:32), `coreduetd.people`, `coreduetd.homecontrolsuggestion.notification.task`, `prngseedd.reseed`, `diagnosticpipeline.cloudkit_expedited_upload`, `bluetooth.CBMetrics`, `ids.accountrepair`. From 18:41:39.990 routined logged about 1,150 CoreRoutine "LEARNED LOCATION" place/visit lines in two minutes: a learned-locations database pass. None of these is on the known schedule (RUN_STATE 205); they are among the roughly 650 dasd starts per hour (RUN_STATE 206).

## Checks
- D pins (`align_v4_verify_d_pins.py`): FAIL, "report has no single disk check". Expected: SMC runs first and the run stopped before the disk and load checks.
- Spotlight: corespotlightd 716 and spotlightknowledged 73957 both `S` (resumed). No `spotlight-stopped` record left.

## Disposition
Second consecutive refusal by an unscheduled burst (re-run 9: WindowServer/ControlCenter; re-run 10: routined). Under RUN_STATE 206 next (3) this is the pattern: no blind re-launch under the 0.05 abort rule. Ed's 18:28 PST answer asks for the amendments (display sleep in the launcher; redo or flag instead of abort). Those are R0-L3, PRs #699 and #700 by the laptop lead; R0 re-runs once they merge.
