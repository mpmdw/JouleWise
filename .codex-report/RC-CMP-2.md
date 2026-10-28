# RC-CMP-2 report (in progress)

Seat RC-CMP-2, branch `lane/2026-10-27-recompute-comparator`, base `234fbb127`. Brief: `docs/process_traces/2026-10-28-recompute-meter-fit/BRIEF.md` (main `9e985c59c`).

## Progress
- M1 done: `meter_clock_fit` in `scripts/independent_recompute_b5.py` implements the parser's clock-fit definition in the recompute's own code.
- M2 done: adversarial jitter now agrees (0.0 J difference, 0 ns at sample 1150; old binning 1249 ns, -0.02 J); 240-seed property test max host difference 1 ns; counterfactual: old binning fails 239/240 seeds.
- M3, M4, M5: pending.
