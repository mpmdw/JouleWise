# 🟢 BETWEEN RUNS
> **LIVE HAZARD (2026-08-19):** the three `_v3` packs' authored freeze
> evidence (33 receipts) EXPIRES ~2026-08-20T16:51Z and DIES ON ANY
> REBOOT (boot session da90818c…). Do not reboot before the S5
> freeze-0003 mints land. Details: docs/process/ed-s5-mint-decision-2026-08-19.md.

Terms used here: a *measurement window* is one uninterrupted, calibrated
collection session; a *pack* is the frozen campaign plan and its authenticated
supporting files; a *detection floor* is the largest false difference the
admitted measurement system can produce; a *mint* is the governed process that
issues a floor artifact; an *arm* is one pre-registered workload or comparison
track; a *verdict* is the final governed decision to admit or refuse evidence;
and a *refusal* is a recorded decision not to issue a result when a required
gate or piece of evidence fails. A *bundle* is the self-contained record of one
workload run, including its configuration, raw trace, events, and derived
summary.

**D-117 pre-window state. This document does not assert that a measurement is
in flight. Under the 2026-08-07 D-117 supersession, the historical a10/re-mint
and old C/D plan are retired. Claim authority can now arise only from the
prospective alpha, beta, and gamma windows; the separately named Window C
characterization night remains Ed ruling #1.**

| | |
|---|---|
| State | `between` |
| Updated | 2026-08-17 (documentation clarity pass; no machine-setting assertion) |

## Live machine rules

- Do not modify or dirty the dedicated measurement checkout.
- Do not reboot before T-0. A reboot voids the current arm-readiness evidence,
  which must then be authored again before T-0.
- Do not launch a measurement window before a READY-candidate council issues a
  qualifying verdict.

## Does anything need you?

Verify network-time state directly before the next §5A sequence; this
document does not assert the current machine setting. Wall-meter purchase
(D-092) remains open.

The two FAILED verdicts below were adjudicated on 2026-08-01/02 under D-100
and D-106. The collected bundles are banked and backed up, but the two windows
have different dispositions. **Window A is
permanently non-claim-bearing** — its deviation retry bound an
incompatible power policy at collection time (immutable), so C1
re-collects in window C. **Window B's re-evaluation ran 2026-08-03** after the
D-108 gate cleared (`D100-BII-BINDING-01` CLOSED, PR #99). The governed run
correctly REFUSED before issuing a verdict because member r06 has a
collection-time clock-anchor failure. The independent cold-gate review under
D-112 confirmed that the machinery was correct and that the license was
EXHAUSTED AS DRAWN. The original FAILED verdict stands untouched.
**2026-08-05 supersession (D-113): Window B is permanently
non-claim-bearing; its re-evaluation/license chain is retired and no
set-aside or claim-consumption decision remains pending.**

## Detail

`window_metrologyB_20260801` ran overnight 2026-07-31→08-01 in three
launches and closed as salvage at the third member failure. The collected
evidence was verified and backed up to iCloud (72+13 bundles). It contains the
NEG-8 bound corpus 12/12 plus the in-window bound mint; references 7/7;
**null_o0128 + null_o0512 complete** (claim C2, 2 of 3 rungs);
**additivity 23/24 single-root** (C4); and a clean calibration bracket (2.25 ms
drift versus the 10 ms policy).

Launch 1 aborted twice at the pre-calibration gate because of the clock-anchor
knife-edge, a real instrument finding documented in the run report. That
recurrence triggered escalation and a bounded independent consultation with
the second model (Sol). Launch 2 used the new suspended-cloud-sync protocol and
passed pre-calibration on its
first attempt. Failure #3 came from the operating session's own output
streaming during a member's idle gate. Under the superseded plan, the remaining
`null_o2048`, `long_holds`, and one additivity slot were assigned to metrology
Window C; the D-117 supersession in the headline now governs.

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
