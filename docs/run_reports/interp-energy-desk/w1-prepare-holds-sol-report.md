Committed on `ops/2026-11-11-w1-prepare-holds`; clean tree, no push.

- Added runtime preflight, previous-window hold statements, three held-reason arm refusals, signed-ruling CLI fallback, and reusable weight preflight.
- Commits: `73eff70c1`, `3962cb34e`, `ba515252c`.
- Final runtime/parser witnesses and all 22 registration tests pass. Prior failures and timed-out modules remain documented; testing totaled about 18.4 minutes.

[Run report](docs/run_reports/2026-11-11-w1-prepare-holds.md) lists changed files, commands, red/green evidence, limits, and native checks.

**NEEDS_RULING:** Which authenticated desk-runtime signal should trigger RL-73’s hold? Current exclusions cannot distinguish it from arm identity mismatches, so that sub-item remains stopped as instructed.