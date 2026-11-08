Committed locally on `align/2026-11-07-squeeze-analysis`; working tree is clean.

- `3dabcc824`: NumPy calibration, joint detection curves, adaptive attack simulator, frontier/power tooling, CLI and tests.
- `83575d712`: [handoff report](/Users/edr/code/CapstoneProject/jw-wt/sol-squeeze-analysis/docs/run_reports/2026-11-07-squeeze-analysis.md).

Changed `joulewise/align/squeeze/`, `tests/align/squeeze/`, package initializers and the optional dependency in `pyproject.toml`.

Verification: four targeted unittest modules run individually—**47 passed** on Python 3.14 with NumPy. Python 3.13: **10 passed, 37 skipped** because NumPy is absent. Targeted compileall and diff checks passed. Exact commands are in the report.

Under the illustrative combined attack assumptions, m=39 and SD=58 J give approximately **50% detection at H=512**, versus **98% at H=1,024**. Opaque logged work supplies a counterexample to an unrestricted squeeze claim.

Open: the locked cohort size remains unspecified; n=40 results are illustrative. The lead must validate monitor response, attack costs, supported Python numerical tests and hardware behavior.

No network, sealed-data access, full suite, coordination-state changes or push.