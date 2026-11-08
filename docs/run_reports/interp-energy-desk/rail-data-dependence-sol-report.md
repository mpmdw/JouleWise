Implemented on `interp/2026-11-07-rail-data-dependence`; working tree clean, nothing pushed.

- Added operand statistics, synthetic MLX GEMM/GEMV fills, seeded ABBA scheduling, timing capture, and existing powermetrics/KM003C hooks.
- Added capture-free dry mode, synthetic unittest modules, and an operator draft. Default window estimate: **81.2 minutes**.
- Commits: `0931c1747` implementation; `51367f6e1` handoff.

Verification: **22 passed, 2 MLX tests skipped** on Python 3.14; **11 passed, 13 optional-dependency skips** on Python 3.13. Targeted compileall passed. Strict dry CLI completed all 384 slots. No full suite, network, measurement capture, or sealed-data access.

Native MLX behavior, collector integration, residency, and actual window duration remain unverified. The lead’s next check on Metal is:

```sh
python3.13 -B -m unittest tests.interp_energy.test_mlx_native
```

[Run report with changed files, exact test commands, results, and limitations](/Users/edr/code/CapstoneProject/jw-wt/sol-rail-data-dependence/docs/run_reports/2026-11-07-rail-data-dependence.md).