# OSCTX-MVP-01 v2.3: validity rules after the v2.2 deltas and the anchor finding

Written 2026-09-24 ≈20:15 PDT, before any MVP data. v2.2 (09) stands except where amended here. Sources:
- Fable delta 2 (11) and the Fable anchor answer (below);
- Astra delta 2 (10);
- the literature scan (12);
- two bench smoke runs.

## The anchor finding (bench-verified)

A plain `joulewise run` captures too little post-request power for the reducer's clock fit. The fit needs ≥ 60 s of capture (`MIN_RATE_FIT_BASELINE_S`). Without it, the power timeline falls back to the midpoint of the sudo/powermetrics spawn bracket, which is ±0.55 s here. Fable measured the sensitivity on the smoke bundle: shifting the trace by ±0.1 s moves net energy by ±1.8 %, and ±0.55 s moves it by −9.6 / +7.4 %.

Spawn latency itself depends on the launch context, so this error would be **arm-correlated** and of the order of δ. Production avoids it with `--post-window-sampling-dwell-s`, which keeps sampling after the stop marker without extending the measured window.

Bench, the same config from the same shell, ≈19:55 PDT:

| Run | Anchor | E (J/output token) | R (tok/s) | Anchor-shift energy bound | Wall |
|---|---|---|---|---|---|
| no dwell | unresolved (spawn-midpoint fallback) | 0.3778 | 83.62 | n/a | 66 s |
| `--post-window-sampling-dwell-s 60` | bound 3.5 ms | 0.4055 | 84.65 | 0.027 J | 134 s |

With the dwell, the only failing precheck reasons left are `environment_admission_failed/missing` and `instrument_calibration_missing`.

## Amendments

- **C1. Dwell and validity.** Every run passes `--post-window-sampling-dwell-s 60`. A run is **valid** iff all of:
  - status == succeeded;
  - the idle-subtracted request precheck's `clock_anchor_bound_s` is present and ≤ 0.05 s;
  - every failing precheck reason is in the declared set {environment_admission_failed, environment_admission_missing, instrument_calibration_missing};
  - exactly 512 output tokens were observed;
  - the output-token hash equals the stage reference.

  A cell is valid iff all its runs are valid.
- **C2. Declared absences.**
  - `instrument_calibration_missing` is expected: no 25G83 calibration exists, which is the reopened acceptance lane. It widens only the eligibility envelope and does not change E or R (Fable, `reduce.py:1816`).
  - `environment_admission_*` is expected: plain `run` has no campaign policy. The in-cell census (A5) stands in for it.
- **C3. Drift (Fable 11; Astra 10 N2).**
  - Per cell, record the ratio E_drift_bound_j ÷ net energy.
  - EQUIVALENT is granted only if every cell in the tested arms has that ratio ≤ δ. Otherwise the verdict is **INCONCLUSIVE-by-attribution**, and it is reported as Ed's "lagging OS processes" question.
  - Also reported, and not decisive: "widened" intervals, formed by adding each cell's anchor, drift and edge bounds (converted to log-ratio, not shrunk by √n) to the paired interval. The widened interval is the conservative reading. **Astra's dissent is recorded:** it wanted the widened interval to be decisive. **Lead's reason:** the realized drift already appears in the paired scatter, and the worst-case one-sample envelope added on top would make every verdict INCONCLUSIVE by construction. The per-cell ratio gate keeps the worst case binding where it could matter.
- **C4. Edge bound per arm (Fable 11).**
  - The analyzer computes, from `power_trace.csv`, per request edge: ¼ × |P(first in-window sample) − P(idle mean)| × (the straddling sample's interval). The same applies at the stop edge. It is reported per arm.
  - A DIFFERENT verdict on E is downgraded to INCONCLUSIVE when |the mean D–I difference in J/token| is smaller than the difference between the arms' mean edge bounds in J/token.
- **C5. Stop rules (Fable 11; Astra 10).**
  - Per-arm invalid-cell counts are a reported endpoint. **≥ 3 invalid cells in one arm within a stage stops the stage and goes to council**: an arm-correlated failure is a finding.
  - A block is re-run at most twice. A third failure aborts the stage.
- **C6. Settling.** After the CPU mechanism probe, the wrapper idles 60 s before writing the done marker, so the next cell's idle baseline is clean.
- **C7. Sizing (Astra 10 N1; Fable 11).**
  - Stage 0 runs 2 runs per cell, which gives both the within-cell and the between-cell spread.
  - Before U1, the lead publishes the power table for both contrasts and both endpoints over a grid of paired SD = {1, 1.5, 2} × the stage-0 estimate.
  - `runs_per_cell` for U (1 or 2) and the stage size (a multiple of 6 blocks) are frozen in that table before U1 starts.
  - Stage-0 numbers are attended, with agents active. They are expected upper bounds on drift. They are not presumed conservative for spread.
- **C8. Budget.** Each run is ≈134 s.

| Item | Time |
|---|---|
| A cell of 1 run, plus probe and settle | ≈3.8 min |
| A cell of 2 runs | ≈6 min |
| Stage 0 (6 cells × 2 runs) | ≈36 min |
| U1 at 1 run per cell (21 cells) | ≈80 min |
