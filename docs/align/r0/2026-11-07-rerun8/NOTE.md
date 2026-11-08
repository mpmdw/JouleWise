# ALIGN v4 R0 re-run 8 (2026-11-07 17:15 PST): refused in `smc` by a newly identified scheduled job

- Record: `/Users/edr/night-align/r0-v4-20261108T0115Z` (01:16:15Z-01:31:00Z, 884 s). Status `fail`, `complete_r0` false, `stopped_after` smc `fail` (exit 3, `NotQuiet`).
- Measurement checkout `5f817856b` (#692 merged; SMC runs first, DECISION D3). Launch id `9d6dbf3dc3504e58aa4775d6558dea68`, deadline 23:05 PST.
- `report.json` sha256 `14cd34f1f37ea8c57b0d45d1a2219b6f7b53f6399bb9f3425e6e44f0bd94b501`; `report.md` sha256 `91bfb819aba5aecf2f01e7a776e4fe65394de1e0c3341caea3dd521b12e1ce8f`.
- SMC journal `smc/samples.jsonl`, 43,697,636 bytes, sha256 `1ee178271f16d60b0329a13090bfa788eaca0b1a69d25c94c7b4c1e9ae149c82` (kept on the Mac, not committed).

## Refusal
Quiet census interval 17:30:29.786-17:30:59.905 PST (30.1 s): `frauddefensed` pid 61967 at 0.0920 CPU-s/s against the 0.05 per-process limit. Outside-tree total 0.181 CPU-s/s; host busy 0.351 of 16 CPUs. The refusal is correct: the contention is real, and it is not an R0 defect.

## Cause: a 4-hourly BackgroundSystemTasks job
Unified log (`/usr/bin/log show`, process `frauddefensed`, "Calling launch handler"): at 17:30:55.694 frauddefensed ran its launch handler for `com.apple.trustkit.signatures`, then loaded the `com.apple.TKModelMessages` asset set. Over the last four days that handler fires every 4 h at about xx:31 (observed 17:30:48 to 17:32:20): 01:31, 05:31, 09:31, 13:31, 17:31, 21:31 PST. A second handler, `com.apple.trustkit.notification`, fires daily at about 09:21.

## Checks
- D pins (`align_v4_verify_d_pins.py`): FAIL, "report has no single disk check". Not meaningful here: SMC runs first and the run stopped before the disk and load checks.
- Spotlight: corespotlightd 716 and spotlightknowledged 73957 both `S` (resumed). No `spotlight-stopped` record left.
- Preflight log: AC power, free 124,405,276,672 bytes.

## Disposition (item 194 (3), Ed's "go" of 00:08 PST 11-07)
A newly identified scheduled job, added to the known-contention list. Only the `smc` check runs the quiet census (`NotQuiet` is raised only in `joulewise/align/apple/smc_enumeration.py`), and SMC now runs first, at most 3,300 s. Re-launched as re-run 9 at about 17:50 PST, so SMC ends by about 18:45, well before the 21:31 trustkit run and the 23:09 scan; deadline 23:05 PST.
