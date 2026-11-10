Committed locally on `ops/2026-11-10-watchdog-v5-installed`; worktree clean, nothing pushed.

- `9277b5913`: added three measured timing weights; scoped agent-test assertions to fixture PIDs; strengthened child reaping. Production matcher unchanged.
- `416f28368`: added the [run report](/Volumes/JW-EXT/jw-wt/sol-wdv5-fix4/docs/run_reports/interp-energy-desk/2026-11-10-wdv5-fix4-sol.md).

Targeted unittest runs passed for the three timed modules. The combined `run_units` shard covering agent identity, night gate, and shard tests passed: **136 tests, one skip**. All **74 captured child handles were reaped**.

Unresolved: I could not identify a separate leaking module or reproduce the original CI failure. Sandbox restrictions also leave three native tests and the machine-wide orphan census pending. The report records exact commands, results, and the next verification steps.