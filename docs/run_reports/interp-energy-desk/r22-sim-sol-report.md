Committed locally as `0aca87ad5` on `align/2026-11-08-r22-sim-sol`. Working tree clean; no push or coordination-state changes.

Delivered the [report](/Users/edr/code/CapstoneProject/jw-wt/sol-r22-sim/docs/align/v4/b3-sim/R22-SIM-sol1.md), simulator, validation script, numeric tables, logs and dated handoff.

- **R22 retains selection bias under hot-state bars.** At τ=.5 s_r and bar probability 1/4, maximum FPR is **4.040% [4.017,4.063]**, versus oracle **2.321% [2.309,2.333]**.
- With 10% member loss, exact qualification probabilities are **88.05% / 52.56%** for bar rates 1/8 / 1/4.
- **+.75 s_r** is the smallest tested margin restoring oracle-level mean FPR. **+1.25 s_r** meets nominal targets on this finite synthetic grid. Live scale and detection cost remain unresolved.

Verification passed: new simulator’s eight checks, `simulate_sol1.py --check` (six), and `python3.13 -B -m unittest tests.align.test_v4_estimands` (15), plus output/digest audits. No full suite or MLX tests ran; supported Python/NumPy reproduction remains necessary.

**Intake caveat:** an adjacent RUN_STATE excerpt exposed a Block 5 result summary. No underlying measurement data was opened or used, but complete outcome blindness cannot be claimed. This is recorded in the report.