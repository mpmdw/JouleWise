Committed locally on `ops/2026-11-11-w1-p2c`; worktree clean, no push.

- `70efa260e` — applied RL-86 registry rulings, classified all 41 keys INTERNAL, added the probe pin test.
- `0f94b6503` — added the [run report](/Volumes/JW-EXT/jw-wt/sol-w1-p2c/docs/run_reports/2026-11-11-w1-p2c.md) with citations, the 41-key table, commands and mutation evidence.

Changed only the registry, its test and the report. The intermediate census matched exactly: 17 exporter keys and 24 launcher keys, with no other discrepancies.

Focused unittest result: **23 tests / 2 failures → 24 tests green / 1 skip**. Both required mutants were detected. Frozen baseline and coordination files remain unchanged; custody checks recorded zero forbidden accesses.

No keys require a ruling. The lead still owes RL-86’s independent Opus cold review before landing.