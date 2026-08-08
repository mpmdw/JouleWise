# 🟢 BETWEEN RUNS

**D-117 pre-window state; this document does not assert a measurement is in flight. 2026-08-07 supersession (D-117): the historical a10/re-mint and old C/D plan are retired. Claim authority can now arise only from the prospective alpha, beta, and gamma windows; the separately named Window C characterization night remains Ed ruling #1.**

| | |
|---|---|
| State | `between` |
| Updated | 2026-08-07 (documentation correction; no machine-setting assertion) |

## Does anything need you?

Verify network-time state directly before the next §5A sequence; this
document does not assert the current machine setting. Wall-meter purchase
(D-092) remains open.

Expectation-setting on the two FAILED verdicts below (adjudicated
2026-08-01/02, D-100 + D-106): the collected bundles are banked and
backed up either way, but the two windows differ. **Window A is
permanently non-claim-bearing** — its deviation retry bound an
incompatible power policy at collection time (immutable), so C1
re-collects in window C. **Window B's re-evaluation ran 2026-08-03** after the
D-108 gate cleared (`D100-BII-BINDING-01` CLOSED, PR #99): the governed
run REFUSED correctly pre-verdict on one bundle's collection-time
clock-anchor failure (r06; cold gate D-112: correct machinery; license
EXHAUSTED AS DRAWN). The original FAILED verdict stands untouched.
**2026-08-05 supersession (D-113): Window B is permanently
non-claim-bearing; its re-evaluation/license chain is retired and no
set-aside or claim-consumption decision remains pending.**

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
output streaming during a member's idle gate. Under the superseded plan,
the remainder (null_o2048, long_holds, one additivity slot) was assigned
to metrology Window C; the D-117 supersession in the headline now governs.

Both metrology verdicts **FAILED and stand as issued** — window A on the
dangling quarantined slot + refused deviation post-cal, window B on
manifest/membership resolution + NEG-8 bracket evaluation. The
three-part machinery adjudication is COMPLETE (D-100, 2026-08-01) and
the repair is mainline (PR #94, 2026-08-02); window B's re-evaluation
EXECUTED and stopped correctly 2026-08-03 (D-112). D-113 permanently
retired Window B's re-evaluation/license chain; no set-aside or
claim-consumption decision remains pending. D-117 governs the prospective
alpha/beta/gamma path separately from the named Window C characterization
night.

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
