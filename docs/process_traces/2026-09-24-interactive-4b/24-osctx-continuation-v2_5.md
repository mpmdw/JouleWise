# OSCTX-MVP-01 v2.5: the continuation after the session-2 stop (council ruling)

Written 2026-09-24 ≈23:50 PDT, **after** session 2's data and **before** any continuation data. Council seats: Astra 6 (22, PROCEED WITH CHANGES) and a fresh Fable 5.1 (23, PROCEED WITH CHANGES). The lead synthesizes. Amendments made after seeing data are labelled as such.

## Rulings

- **R1. F-A is recorded as scoped in 21:** the tested default-launchd configuration fails closed; its bias is unmeasured and not claim-relevant. Setting ProcessType=Interactive on the night job is a **supported candidate** only. Installing it goes through a gated PR and the council under D-184.
- **R2. The continuation (fresh registration).**
  - **Arms:** I and SH only.
  - **Blocks:** 6. Three run I→SH and three run SH→I, in an order drawn with seed 20260925 and frozen in the command sequence before t0.
  - **Runs:** 1 production run per cell.
  - **One look only:** no U2 and no extension. INCONCLUSIVE is an accepted outcome. Pre-computed power for E is 0.81 at 1.5 × the stage0U SD and 0.45 at 2 × SD.
  - **Tests:** the same validity rules and the same 99.375 % paired-t on log E and log R, with bounds log(0.97) and log(1.03).
  - **Exclusions:** stage0U, and the U1-01 I cells of session 2, are excluded from the verdict.
  - **Session order:** a discarded I warm-up cell, the 6 blocks, then the probe-only cells.
- **R3. Probe-only cells (Fable).** D ×2 and B ×2 run the CPU mechanism probe and the settle only, with no production run. They are descriptive: evidence on whether each context throttles a CPU workload on the quiet machine. They are outside the paired inference, and they are compared against the CPU probes that follow the I and SH production runs. A missing or failed probe is investigated; it never supports a small-effect claim.
- **R4. C3 v2.5.** This amendment follows observed data (stage0U), and the original C3 outcome is reported alongside it.
  - Per cell, report E_drift_bound_j ÷ net energy, and report the widened interval. Neither decides the verdict.
  - EQUIVALENT on E additionally requires both of:
    - (i) the sample SD of log E across each tested arm's valid cells in the stage is ≤ 1 %;
    - (ii) every cell's idle-baseline mean is ≤ 1 W.
  - The drift gate does not apply to R.
  - The verdict line states whether the widened interval crosses δ, labelled "widened interval crosses δ: yes/no".
  - Rationale: the drift bound is a one-sample envelope × window duration. The realized cell-to-cell scatter of E (0.19–0.62 %) is the direct measurement of what drift does, and it is 20–100 × smaller.
  - **Dissent recorded (Astra):** EQUIVALENT should require the widened interval inside δ; otherwise report "nominal agreement, INCONCLUSIVE-by-attribution". The lead's reason for Fable's text: the widened interval is 6–23 % wide by construction, so it would make EQUIVALENT unreachable on any machine, which violates the sensible-gates directive. The label keeps the conservative reading visible.
- **R5. The cadence criterion.** This amendment follows observed data (stage0U: I at 130–132 ms).
  - v2's Q2 "I cadence ≤ 130 ms" is **kept and reported as not met** (132 ms).
  - Its physical purpose was margin for production's timing, so the cure test now asks for:
    - every I production run valid (the idle baseline completes inside production's bound, and the anchor is ≤ 0.05 s);
    - I's median idle cadence ≤ 150 ms.
  - At 132 ms, 300 samples take 39.6 s against the 55 s bound.
  - SH validates a **contemporary** shell comparison, not July equivalence.
- **R6. Housekeeping before t0.**
  - Fix `power.json` `stage0_context`: session 2's stage 0 ran in state U, with agents drained.
  - Commit this file.
  - The harness change (two arms, probe-only cells, single look, C3 v2.5, R5) gets tests and one read-only Astra delta audit before arming.
