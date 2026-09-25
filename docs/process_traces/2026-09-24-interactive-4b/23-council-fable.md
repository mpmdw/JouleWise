# Council seat (fresh Fable 5.1): OSCTX-MVP-01 session 2 stop

**Bench-verified**: D idle captures median 248.1/237.3/244.5 ms, 233/237/233 samples, each `TimeoutExpired 55.0 s`; `_capture_timeout_s` = max(15, 300×0.1×1.5+10) = 55 s. I cells 131.7–131.9 ms. Stage0U net energy: I 199.45 J ±0.19 %, SH 200.37 J ±0.62 %.

**(a) F-A.** Correctly scoped; fail-closed suffices for the operational decision. Three corrections:
1. "Every I and SH cell in those attempts was valid" is false: `U1-01.3.SH.a1–a3` hold only `discarded.json`. Block order was I→D→SH, discarded at D; only the warmup and three I cells ran (198.9–199.8 J, consistent with stage0U).
2. "Bias question moot" overclaims. Whether the D context throttles the workload (Q1's substance) is unmeasured: `cell.py` raises on production failure before the CPU probe, so every D cell has `cpu: []`. Say "unmeasured; not claim-relevant, since scout 03 found no claim-bearing corpus launched under D".
3. The display was on here; the September nights were display-asleep, so the night link is inference.
No raised-timeout D witness: the 55 s bound is correct production behaviour (a sampler at 2.5× nominal cadence should fail closed). Cheaper witness: two probe-only D cells.

**(b) Continuation.** Run it tonight; n = 6, 1 run/cell, I/SH balanced, 99.375 % kept (power 0.81 at 1.5×sd). Two defects:
- The harness hard-codes three arms (`runner.py`: `3 * block_count`, U2 check `arms != {"D","I","SH"}`; `analyze.py` loops `("D/I","SH/I")`; line 750 auto-runs U2 on any INCONCLUSIVE, which a missing D/I contrast triggers). A two-arm continuation is a harness change: tests plus one read-only delta audit before arming.
- B×2 cannot work as designed: Background is throttled harder than default, so its production run times out and the probe never runs. B and D cells must be probe-only (CPU probe and settle only), or B is dropped.

**(c) C3: modify.** "C3 (v2.5). Per cell, report E_drift_bound_j ÷ net energy and the widened interval; neither is decisive. EQUIVALENT on E additionally requires (i) the sample sd of log E across each tested arm's valid cells in the stage ≤ 1 %, and (ii) every cell's idle-baseline mean ≤ 1 W. The drift gate does not apply to R. Rationale: the drift bound is a one-sample envelope × window duration; the realized cell-to-cell scatter of E (0.19–0.62 %) is the direct measurement of what drift does, 20–100× smaller. Attended attempt 1 I r2 (idle 0.29 W, E +19 %) shows (i), not (ii), carries the gate. Astra's dissent stands; an EQUIVALENT whose widened interval crosses δ is reported with that label."

**(d) Before Ed:** fix the SH sentence and sample counts; `power.json` `stage0_context` still reads "attended, agents active"; state that U1-01 I data are excluded from the continuation verdict; commit v2.5 (arms, probe-only cells, C3, U2 rule) before t0.

**Verdict: PROCEED WITH CHANGES** (SH correction; "moot" → "unmeasured"; probe-only D and B cells; two-arm harness change with tests + delta audit; C3 text above; v2.5 committed before data).
