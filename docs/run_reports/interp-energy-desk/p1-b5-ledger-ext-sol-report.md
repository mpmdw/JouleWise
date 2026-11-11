Committed a **partial extension** on `analysis/2026-11-11-b5-ledger-ext`:

- Added 263 rows: 118 exact, 137 within-rounding, 8 recorded-judgment; no new mismatch.
- Preserved the original 538 rows, `RESULTS.md`, and coordination files.
- Added the stdlib checker and tests. The focused unittest module passes **27 tests**; arithmetic replay is byte-identical.
- Commits: `b9ea4cd11` (extended table), `d0365fd7a` (handoff). Working tree clean; nothing pushed.

Files, hashes, checks, remaining scope, and the authority SHA are in the [run report](/Volumes/JW-EXT/jw-wt/sol-p1-b5-ledger-ext/docs/run_reports/2026-11-11-p1-b5-ledger-ext.md).

**NEEDS_RULING:** May I read the exact hash-pinned files under `dry-m/dry-run/restricted/`? I recommend authorizing only those pinned files. Remaining disclosure sourcing and the subsequent Opus review are pending.

The brief authorizes the two custody roots but separately forbids every real `restricted/` directory. [AGENTS.md](/Volumes/JW-EXT/jw-wt/sol-p1-b5-ledger-ext/AGENTS.md) requires an early return for this authority gap.