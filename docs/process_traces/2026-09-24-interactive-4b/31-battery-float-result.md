# Battery float observation (#420 and #421 input), 2026-09-25

A read-only logger (`ioreg -r -c AppleSmartBattery` every 30 s) ran 13:54:47 → ≈15:03 PDT. The raw data are in `31-battery-float-log.jsonl`, 140 rows. The charge setting was 100 % (Ed changed it from the 80 % cap today). The Mac was on AC throughout.

| Phase | Time | Capacity | InstantAmperage | IsCharging | FullyCharged |
|---|---|---|---|---|---|
| Charging | 13:54:47 → 14:42:22 | 83 → 99 % | +3,891 → +1,716 mA (tapering) | Yes | No |
| **Float** | **14:42:52 onward, 39 samples over 19.1 min** | **100 %** | **0 mA on every sample** | **No** | **Yes** |

**Result:** once full, the battery floats at exactly 0 mA while on AC, at least over the first 19 minutes. The 09-23 single observation (−439 mA at 100 %) did not recur in this span. Longer-horizon top-off cycling is not excluded by 19 minutes. The mandatory per-window battery gate (#421) and its per-slot brackets are what protect windows, whatever the setting.

**Logger stopped** at ≈15:03 PDT, and `pgrep -fl battery-log` is empty. This clears W1 prerequisite 4 (cold ruling BATTERY-FLOAT-01 F-6).
