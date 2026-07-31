# 🟢 BETWEEN RUNS

**Contrast window COLLECTED AND PASSED; D5-J merged; metrology suite authoring in flight**

| | |
|---|---|
| State | `between` |
| Updated | 2026-07-31 (post-window close-out session) |

## Does anything need you?

One thing: **restore network time** (`sudo systemsetup -setusingnetworktime on`)
— it was disabled 2026-07-30 19:02 PT for the window and is still off. Also
note the wall-meter purchase (D-092) whenever convenient; nothing blocks on it.

## Detail

`window_contrast_20260730` (splitwise decode contrast, 1.5B vs 7B, n=10 ABBA)
collected overnight 2026-07-30→31 and the whole-window verdict **PASSED**:
47 bundles, zero science-member failures, bracket drift 1.281 ms against the
10.818 ms screen, adapter continuity stable. Two start-triplet admission
failures (XProtect Remediator sweep, directly observed) were recovered by the
§10 quarantine/continuation path with a consult at the escalation trigger;
the third-failure salvage rule was never invoked. Backups verified to iCloud.
Per-block contrast diagnostic: 146.73 J (σ 0.24 J, n=10 blocks) — prose only;
the gated claim rides after MANIFEST-CONTRAST desk work. Close-out:
`~/JouleWise-window-custody/window_contrast_20260730/close-out.md`.

The next quiet window is the metrology suite's window A (linearity ramp +
additivity + null rung + hold, ~2.8 h) once its draft plans are ratified.

## How to read this

This file is published from the measurement machine at defined moments only:
before a window launches, after one completes or fails, and between runs.
It is **never** written while a measurement is in flight, because pushing
is network and CPU activity that would contaminate the run.

**A stale timestamp during a run is normal and expected** — it means a
window is still going. Compare the timestamp against the expected finish
time in the detail section rather than treating silence as a fault.

If the timestamp is old **and** the detail says a run should already have
finished, something went wrong in a way that stopped the session from
reporting. That is the one case worth waking the machine for.
