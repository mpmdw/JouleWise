Committed locally as `72d0019eb` on `interp/2026-11-07-weight-edits`. Worktree clean; nothing pushed.

Added all six reversible edit types, SHA-256 restoration checks, and timestamped `WeightSwap` in [weight_edits.py](/Users/edr/code/CapstoneProject/jw-wt/sol-weight-edits/joulewise/interp_energy/weight_edits.py), plus synthetic tests under `tests/interp_energy/`.

Verification:

- `python3 -B -m unittest tests.interp_energy.test_weight_edits` — **45 passed** on Python 3.14.
- `python3.13 -B -m unittest tests.interp_energy.test_weight_edits_import` — **1 passed**.
- Eight native MLX tests skipped because MLX is absent.
- Targeted compilation and staged diff checks passed.

NumPy swaps write only changed elements. MLX uses prepared resident tensor rebinding; native correctness and performance remain **provisional**. The lead should run outside the sandbox:

```sh
python3.13 -B -m unittest tests.interp_energy.test_weight_edits_mlx
```

Python 3.11/3.13 numerical validation also remains. No sealed data, network, downloads, full suite, or coordination-state edits were involved.

[Run report](/Users/edr/code/CapstoneProject/jw-wt/sol-weight-edits/docs/run_reports/2026-11-07-interp-weight-edits.md) contains usage, every test command/result, and remaining native gates.