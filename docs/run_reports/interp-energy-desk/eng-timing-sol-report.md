Committed locally as `1df16475e` on `perf/2026-11-08-eng-timing`. Working tree clean; nothing pushed.

Added five files: the timing reader, synthetic fixtures, tests, benchmark, and [handoff report](/Users/edr/code/CapstoneProject/jw-wt/sol-eng-timing/docs/perf/2026-11-08-eng-timing.md).

The reader produces disjoint member/window ledgers, flags unknown time and overlaps, and compares recorded closure with the plan ceiling. Capture code is unchanged.

Verification:

- `python3.13 -B -m unittest tests.align.test_window_timing` — 25 passed.
- `python3.13 -B -m unittest tests.align.test_records` — 4 passed.
- Syntax and diff checks passed.
- Synthetic scan/sweep comparison: **11.383 → 6.972 ms**, with byte-identical complete outputs.

No real measurement data, network, or full suite used. Production timing remains unmeasured. Next: fresh lead review, Python 3.11 checks, then an authorized committed-record run and MBP-gap I/O benchmark. A near-ceiling exit alone cannot establish that the program idled until it.