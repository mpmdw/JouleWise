Implemented on `interp/2026-11-07-forced-decode`; clean worktree, committed locally, not pushed.

Added replay code, lazy MLX support, synchronized timestamps, JSONL hashes and diagnostics, local-only CLI, NumPy reference model, tests and documentation under `joulewise/interp_energy/`, `scripts/interp_energy/` and `tests/interp_energy/`.

Commits: `500035210`, `2f8f7bed5`.

Verification:

- `python3.13 -B -m unittest tests.interp_energy.test_forced_decode -v` — 14 passed.
- `python3 -B -m unittest tests.interp_energy.test_reference -v` — 9 passed.
- Syntax checks passed.
- Full suite intentionally omitted.

The lead’s next check outside this sandbox is:

```sh
python3.13 -B -m unittest tests.interp_energy.test_forced_decode_mlx -v
```

Its four tests skipped here. Native MLX/hybrid compatibility remains unverified, and diagnostic overhead needs assessment before energy claims. No design questions block handoff.

[Run report](docs/run_reports/2026-11-07-forced-decode.md) lists every changed file, results and limitations.