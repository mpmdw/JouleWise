# 🟢 BETWEEN RUNS

**Both metrology windows collected + salvage-closed; both verdicts FAILED as-issued and ADJUDICATED (D-100/D-106): window A permanently non-claim-bearing, window B's re-evaluation hard-blocked on `D100-BII-BINDING-01`; next window (C) awaits a fresh post-move Ed §5A**

| | |
|---|---|
| State | `between` |
| Updated | 2026-08-01 ~07:45 PT (post window B, post both verdicts) |

## Does anything need you?

One thing: **restore network time** (`sudo systemsetup
-setusingnetworktime on`) — disabled for last night's §5A and still off.
Wall-meter purchase (D-092) remains open, nothing blocks on it.

Expectation-setting on the two FAILED verdicts below (adjudicated
2026-08-01/02, D-100 + D-106): the collected bundles are banked and
backed up either way, but the two windows differ. **Window A is
permanently non-claim-bearing** — its deviation retry bound an
incompatible power policy at collection time (immutable), so C1
re-collects in window C. **Window B's data remains eligible** for a
licensed re-evaluation, which is hard-blocked on the
`D100-BII-BINDING-01` capture-identity fixes (D-106). The machinery
repairs themselves landed 2026-08-02 (PR #94).

## Detail

`window_metrologyB_20260801` ran overnight 2026-07-31→08-01 in three
launches and salvage-closed at the third member failure. Collected and
verified to iCloud (72+13 bundles): NEG-8 bound corpus 12/12 + in-window
bound mint, references 7/7, **null_o0128 + null_o0512 complete** (claim
C2, 2 of 3 rungs), **additivity 23/24 single-root** (C4), calibration
bracket clean (2.25 ms drift vs the 10 ms policy). Launch 1 aborted at
the pre-calibration gate twice (clock-anchor knife-edge — a real
instrument finding, see the run report), which fired the escalation
trigger and went to a bounded Sol consult; launch 2 ran under a new
suspended-cloud-sync protocol and passed pre-cal on the first attempt.
Failure #3's cause is recorded honestly: the operating session's own
output streaming during a member's idle gate. Remainder (null_o2048,
long_holds, one additivity slot) moves to metrology window C.

Both metrology verdicts **FAILED and stand as issued** — window A on the
dangling quarantined slot + refused deviation post-cal, window B on
manifest/membership resolution + NEG-8 bracket evaluation. The
three-part machinery adjudication is COMPLETE (D-100, 2026-08-01) and
the repair is mainline (PR #94, 2026-08-02); window B's re-evaluation
waits only on `D100-BII-BINDING-01` (D-106); window C waits on a fresh
post-move Ed §5A.

**New standing doc:** `CLAIMS_STATUS.md` (repo root) — the single home
for what is claimable right now, what is holding, and which numbers must
not be quoted. Full session narrative:
`docs/run_reports/2026-08-01-metrology-window-b.md`.

## How to read this

This file is published from the measurement machine at defined moments
only: before a window launches, after one completes or fails, and
between runs. It is **never** written while a measurement is in flight,
because pushing is network and CPU activity that would contaminate the
run.

**A stale timestamp during a run is normal and expected** — it means a
window is still going. Compare the timestamp against the expected finish
time in the detail section rather than treating silence as a fault.

If the timestamp is old **and** the detail says a run should already have
finished, something went wrong in a way that stopped the session from
reporting. That is the one case worth waking the machine for.
