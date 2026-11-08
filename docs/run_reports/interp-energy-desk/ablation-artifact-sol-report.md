Committed `25f20d95a` on `interp/2026-11-07-ablation-artifact`. Worktree clean; no push.

- Added zero, mean, resample and constant edits, sham controls, toggle statistics and downstream patching.
- Added a measurement draft: 40 cells, 1,920 members, 5.33 estimated work hours plus overhead.
- Ran both planner/demo CLIs. Targeted modules passed: ablation **19**, weight edits **45**, operand statistics **6**, integration **4**. Import and compilation checks passed.
- Synthetic row transitions support **zero = mean < resample**; physical energy ordering remains unverified.

Eight files changed. [Run report](docs/run_reports/2026-11-07-ablation-artifact.md) lists files, exact commands, results and open pins. It also records one rerun where brief test overlap cannot be ruled out.

Native MLX tests skipped. Next, the lead should run individually on a Metal-capable desk Mac:

```sh
python3.13 -B -m unittest tests.interp_energy.test_ablation_artifact_mlx
python3.13 -B -m unittest tests.interp_energy.test_weight_edits_mlx
python3.13 -B -m unittest tests.interp_energy.test_ablation_artifact
```

No energy was measured. Model/calibration choices, native graph validation and materiality thresholds remain open before registration.