# ALIGN v4 R0 re-run 9 (2026-11-07 17:38 PST): refused in `smc` by an unscheduled, transient UI-process burst

- Record: `/Users/edr/night-align/r0-v4-20261108T0140Z` (finished 01:39:05Z; 92 s wall). Status `fail`, `complete_r0` false, `stopped_after` smc `fail` (exit 3, `NotQuiet`, after 61.7 s).
- Measurement checkout `5f817856b`, clean. Launch id `20a062337aed495b840c5b55c99d5dbe`, deadline 23:05 PST. Launched by activation f1717cac, which exited cleanly at 17:37:33 PST (watchdog event 6454) before the desk fence engaged (17:38:10), so no agent session was alive during the census.
- `report.json` sha256 `35b0e9672a3757a11f30b6796871be5c132088a911cd09f50200d4f7ec98efad`; `report.md` sha256 `bb140890c71aed6f3f159db63db1598d82d75f3fd4bc67c314a68f230326a862`.
- SMC journal `smc/samples.jsonl`, 1,588,683 bytes, sha256 `db6fe9fe3eddb2ea6ef34b849da85461b61679f4093b11188b0774a32971cc5f` (kept on the Mac, not committed).

## Refusal
The first quiet-census interval, 17:38:34.96-17:39:05.65 PST (30.7 s): `WindowServer` pid 415 at 0.0838 CPU-s/s and `ControlCenter` pid 676 at 0.0570, against the 0.05 per-process limit. Outside-tree total 0.224 CPU-s/s; host busy 0.352 of 16 CPUs. The refusal is correct: the contention was real.

## Cause: not identified; not on the known schedule
- No scheduled job from the known-contention list (RUN_STATE item 205) falls in 17:38-17:39.
- Not an operator: HID idle was about 6,756 s at 17:44 (last input about 15:51, during Ed's visit). The display does not sleep (`displaysleep 0`; on since 11-05), as in earlier runs.
- Unified log in the interval: ControlCenter updated its location-services menu-bar indicator twice (17:38:46, 17:39:02; "Recent activity attributions changed to [loc:System Services]"); locationd (1,050 lines, a WirelessDiagnostics client) and airportd (462) were busy. Those indicator updates run about 28 per hour, steadily, for the last four days, including through re-run 7's full clean SMC capture, so they alone do not explain it. The aerial wallpaper extension logs a constant 40 lines a minute with 0 frames enqueued, unchanged. WindowServer logged nothing.
- At 17:44, the same two processes measured 0.002 (WindowServer) and 0.000 (ControlCenter) CPU-s/s over 30 s: the burst was transient.

## Checks
- D pins (`align_v4_verify_d_pins.py`): FAIL, "report has no single disk check". Expected: SMC runs first and the run stopped before the disk and load checks.
- Spotlight: corespotlightd 716 and spotlightknowledged 73957 both `S` (resumed). No `spotlight-stopped` record left.
- Preflight log: AC power, free 124,357,226,496 bytes.

## Disposition (item 194 (3))
The source is unidentified and not on the schedule, so item 194 (3) applies: mail Ed and wait. Not re-launched by the magistrate.
