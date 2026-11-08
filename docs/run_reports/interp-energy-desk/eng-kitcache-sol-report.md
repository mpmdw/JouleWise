Committed locally on `perf/2026-11-08-eng-kitcache`; working tree clean. Nothing pushed.

- `cefbf2373`: content-addressed caches, batched Git reads, overlapping input hashing, tests and benchmark. `--check` always regenerates; refusals are never cached.
- `4e3972cc3`: [performance report](docs/perf/2026-11-08-eng-kitcache.md), timing samples and handoff.

Synthetic results: static arm components **1.316 → 0.196 s**; 221-path mutation loop **23.678 → 2.376 s**. Exact byte equality passed for pending and filled plans.

**185 targeted tests passed**, plus compilation and diff checks. [Commands, results and changed files](docs/run_reports/2026-11-08-eng-kitcache.md) are recorded, including one brief test-module overlap.

Caveats: tiny receipt cache hits regressed by 18 ms; batched uncached generation is fastest on these fixtures. Real arm savings remain unverified. No scientific ruling is open; existing registration/native gates remain lead-owned, and `--check` still refuses pending R0/R1 prerequisites.