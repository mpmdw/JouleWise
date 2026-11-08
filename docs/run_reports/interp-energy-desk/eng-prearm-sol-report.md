Committed on `perf/2026-11-08-eng-prearm`; clean tree, no push.

- `2f4cb41bd`: immutable packet tooling and terminal wake, retaining the 300 s watchdog.
- `b1290e99c`: [report with files, commands, timings, and handoff](/Users/edr/code/CapstoneProject/jw-wt/sol-eng-prearm/docs/perf/2026-11-08-eng-prearm.md).
- 83 targeted tests, compilation, and diff checks passed. No full suite.
- Synthetic checks: **0.237 → 0.134 s**, with exact result equality.

**Remaining blocker:** production ALIGN integration needs its owning lane/head and reviewed recipe; those modules are absent from main. Existing arm checks remain enabled. Native MBP wake latency is unverified. Coordination files and installed jobs were untouched.