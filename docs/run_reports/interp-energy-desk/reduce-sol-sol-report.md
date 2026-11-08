Implemented on `perf/2026-11-08-reduce-sol`. Clean tree; committed locally, no push.

Commits: `378820341` implementation/tests; `bcef9c96b` benchmarks/documentation.

Added the columnar reducer, digest-bound observation cache, fresh turn-energy tables, parallel CLI, synthetic generator, and equality tests. Files and integration instructions are in the [performance document](/Users/edr/code/CapstoneProject/jw-wt/sol-reduce-sol/docs/perf/2026-11-08-reduce-sol.md).

Measured under load:

- Parsing: **12.0 → 19.5 MB/s/core**.
- **506 MB → 577 kB** compact output.
- 22 full-size extraction passes: **13.12 minutes**.
- Short-member synthetic 11-window series: **46.6 s raw → 20.8 s cold / 1.89 s cached**, with byte-identical output.

`python3.13 -B -m unittest <module>` passed for:

- `tests.align.test_reduce_sol`: 18 tests.
- `tests.test_powermetrics`: 61 tests.
- `tests.align.test_attribution_holds`: 6 tests.
- `tests.align.test_thermal_desk`: 25 tests.

Compileall and diff checks passed. No full suite, sealed-data access, network, or coordination-state edits.

Next: integrate into the separate primary engine and verify its final raw/reduced outputs. Python 3.11, cold-disk performance, and full-series throughput remain unverified. Details and review dispositions: [handoff report](/Users/edr/code/CapstoneProject/jw-wt/sol-reduce-sol/docs/run_reports/2026-11-08-reduce-sol.md).