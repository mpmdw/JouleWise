Implemented and committed locally on `interp/2026-11-07-joule-map`; working tree is clean.

- Added component removal/replacement seams, downstream-behavior correction, interleaved J/token analysis, bootstrap CIs, and additivity audits.
- Added a CLI, synthetic tests, gated MLX tests, and a [design/run plan](/Users/edr/code/CapstoneProject/jw-wt/sol-joule-map/docs/design/interp_joule_map.md) citing CLEAR and HYMELL.
- Commits: `200152c1b`, `781157363`. No push.

Validation: analysis/CLI tests **12 passed** on both interpreters; NumPy seam tests **3 passed**; existing integration tests **4 passed**. Syntax and diff checks passed. MLX tests were skipped; native correctness remains unverified.

Next, the lead should run outside this sandbox:

```sh
python3.13 -B -m unittest tests.interp_energy.test_joule_map_mlx -v
```

Complete per-layer hardware mapping still needs cache-position adapters; MoE/hybrid support and instrument bounds remain open.

The [run report](/Users/edr/code/CapstoneProject/jw-wt/sol-joule-map/docs/run_reports/2026-11-07-interp-joule-map.md) lists all 10 changed files, exact test commands/results, and uncertainties. No network, sealed data, measurements, downloads, or full suite were used.