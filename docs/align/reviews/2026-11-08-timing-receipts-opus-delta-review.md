# Timing receipts: Opus delta review of the cold-review fixes

2026-11-08. Reviewer: Claude Opus 5.5. Target: the fix range `0b2d4d9b2..43af8f007` on `align/2026-11-08-v4-r11`,
whose content change is commit `f455366162ffab6bcf7ecc4b5039f3b7d37f0c15` (the Opus cold-review fixes and the R17
finality repair). It follows `docs/align/reviews/2026-11-08-timing-receipts-opus-cold-review.md`.

**Record status.** The reviewer's report was relayed by the lead, not committed to a branch. This file is a summary
of that relayed verdict; it adds no finding and no verdict of its own.

## Verdict: ADMIT

- **MEDIUM-1 closed.** The settle probe sleeps its full duration in four cases: the good case, a broken `joulewise`
  package, a shadowed `json` module, and no interpreter.
- **MEDIUM-2 and LOW-1 to LOW-6 closed.**
- Every finding is closed. Nothing new runs inside a measured member or the dwell. `CaptureEqualityTests` passes.

## Two LOW notes (no fix required)

1. The spill file `night/timing-receipts.jsonl` is a new file. The lead accepted it as a deviation
   (`docs/align/v4/DEVIATIONS.md`, TR-spill-LOW-2): it is written after the operation, never during a window or dwell.
2. An end-without-start edge exists if the `CHAIN_LOG` is missing between the settle's start and end markers. It is
   impossible in production, where the chain log exists before the chain runs.

## Scope

The range also contains the R17 finality repair (`joulewise/align/apple/light_triage.py`,
`joulewise/align/apple/v4_contention.py`, `scripts/align_v4_next_arm_packet.py`). That part is covered by the Sol
merge-c84 review (`docs/align/reviews/2026-11-08-merge-c84-sol-review.md`), not by this review.
