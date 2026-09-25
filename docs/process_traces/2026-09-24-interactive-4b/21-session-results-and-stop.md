# OSCTX-MVP-01 unattended session 2: results and pre-registered stop

Run 2026-09-24 22:37–23:24 PDT, `--session U`, harness `fix/2026-09-24-osctx-mvp-r3` (fix round 7 plus the display-state bench fix). Data: `/Users/edr/osctx-mvp-01/session2/`. Conditions: Ed away (HIDIdleTime > 7,000 s), display on at Ed's brightness, the magistrate drained (sleep ≥ 300 s, no seats), network time paused.

## Before session 2

**Session 1 failed closed at U admission** because the display state was unreadable. The harness probed `IODisplayWrangler`, which does not exist on Apple silicon, and a bare-integer `IOPowerManagement`.

A live test fixed the source:

| Source | Display on | After `pmset displaysleepnow` | After `caffeinate -u` |
|---|---|---|---|
| IOMobileFramebuffer CurrentPowerState | 1 | **1** (does not change) | 1 |
| powerd assertion "Prevent sleep while display is on" | present | **absent** | present |

The bench fix (commit on the fix branch) uses the powerd assertion, with 3 unit tests. HIDIdleTime was not reset by `caffeinate -u`.

## The stop

The stage0U, analyze_power and freeze steps completed. The freeze chose 6 blocks × 1 run per cell (79.8 min), with power at 1.5 × SD of 0.806 (E) and 1.0 (R).

**U1 stopped under rule C5: 3 invalid cells in arm D** (block U1-01, attempts a1–a3). **Correction (Fable council seat, bench-verified):** the block order was I → D → SH, and each attempt was discarded at D, so the three SH cells (U1-01.3.SH.a1–a3) never ran; they hold only `discarded.json`. The three I cells were valid (198.9–199.8 J net, consistent with stage0U).

**Mechanism** (bench-read from the bundles):
- Production's idle-baseline step runs `sudo -n /usr/bin/powermetrics -n 300 -b 0 -i 100 …` under a 55 s bound (`joulewise/adapters/powermetrics.py:1203`).
- In context D on the quiet machine the delivered cadence was 237–248 ms (p95 277–279 ms). 300 samples then need ≈ 74 s. Each D run failed with `TimeoutExpired … after 55.0 seconds`, having captured only 232–236 samples.
- The I cells in the same attempts ran at 132 ms (p95 134–135 ms).

**Finding F-A (scoped per council 22/23).** In session 2, the tested default-launchd configuration **failed closed** on all three D attempts, at production's 55 s idle-baseline bound (`_capture_timeout_s` = max(15, 300 × 0.1 × 1.5 + 10) = 55 s). This establishes that unchanged D is operationally non-viable in that configuration. Whether D would bias E or R when it can complete is **unmeasured**. It is not claim-relevant, because scout 03 found no claim-bearing corpus launched under D. This is the same 248 ms timer-coalescing cadence as the September nights, now shown at the production-workload level. The link to the September idle pilots' timing-check failures (2/12, 4/12, 7/12 valid) is an inference: those nights also had the display asleep, and this session had it on.

## Stage 0 in state U (sizing-only by pre-registration; descriptive here)

3 blocks of (I, SH), 2 production runs per cell. Every run was valid.

| Block | Arm | E (J/token, mean of 2) | R (tok/s) | Idle cadence | Idle baseline W | Max drift bound ÷ net |
|---|---|---|---|---|---|---|
| 01 | I | 0.3902 | 83.85 | 130 ms | 0.279 | 0.232 |
| 01 | SH | 0.3907 | 83.64 | 121 ms | 0.138 | 0.069 |
| 02 | I | 0.3897 | 84.16 | 132 ms | 0.102 | 0.085 |
| 02 | SH | 0.3900 | 83.66 | 121 ms | 0.171 | 0.087 |
| 03 | I | 0.3888 | 84.33 | 132 ms | 0.113 | 0.063 |
| 03 | SH | 0.3934 | 83.58 | 121 ms | 0.155 | 0.129 |

| Arm | E over 6 runs | R |
|---|---|---|
| I | 0.3896, sd 0.0007 (0.19 %) | 84.11 ± 0.27 |
| SH | 0.3914, sd 0.0024 (0.62 %) | 83.63 ± 0.11 |

- **The quiet idle baseline is 0.1–0.3 W**, against 5–10 W attended with agents active. E's spread fell from ~25 % attended to under 1 %. The unattended condition is what makes the numbers trustworthy.
- **I vs SH differ by about 0.5 % in E and about 0.6 % in R** (I slightly faster). Both are well inside δ = 3 %. This is descriptive only (n = 3, stage 0).

## A design problem the data expose: the C3 drift gate

Production's `E_drift_bound_j` is a one-sample worst-case envelope × duration. It was 6–23 % of net energy here, while the realized run-to-run spread of E is 0.2–0.6 %.

Under v2.3 C3, any cell with a drift ratio > δ blocks EQUIVALENT, so **no EQUIVALENT verdict is reachable even on a quiet machine**. The gate is not sized to the instrument (Ed's sensible-gates directive, 2026-09-10). It is for the council to rule on.
