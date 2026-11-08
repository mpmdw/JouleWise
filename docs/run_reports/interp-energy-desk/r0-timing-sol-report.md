Added R0 JSON/NOTE support, synthetic tests, and four committed-record worksheets. Local commits: `43a3e21eb`, `39ea05ab4` on `perf/2026-11-08-r0-timing`. Tree clean; nothing pushed.

[Timing report](/Users/edr/code/CapstoneProject/jw-wt/sol-r0-timing/docs/perf/2026-11-08-r0-timing.md) includes quoted output, re-run comparisons, and A/B speedup candidates with conditional savings.

Re-run 11: **7,436.8 s + 300 s dwell**, with **32.3 s outside checks**. Largest sinks: long decode **55.3 min**, SMC **31.6 min**, ladder **21.1 min**, memory **12.4 min**.

Targeted checks passed:

- `python3.13 -B -m unittest tests.align.test_window_timing_r0` — 14 tests
- `python3.13 -B -m unittest tests.align.test_window_timing` — 25 tests
- `python3.13 -B -m unittest tests.align.test_records` — 4 tests

AST and diff checks passed. No full suite or MLX execution.

Only re-run 11’s NOTE is committed, so rung, finalize, and push timings remain unavailable. Next step: custodian-provided timing-only export from existing receipts. Python 3.11 verification remains open.

Initial NOTE inspection exposed status diagnostics beyond the field allowlist. They were excluded from calculations/output; the [run report](/Users/edr/code/CapstoneProject/jw-wt/sol-r0-timing/docs/run_reports/2026-11-08-r0-timing.md) documents this deviation and all changed files.