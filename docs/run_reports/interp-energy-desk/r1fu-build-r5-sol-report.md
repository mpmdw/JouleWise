Committed locally on `ops/2026-11-11-r1-followup-kit`; working tree clean, nothing pushed.

- `52060d393`: restored classifier refusals, fixed packet delivery through `$MEASUREMENT_ROOT/.align-r1-prepare.json` after Automatic restore, and stabilized bundle equality.
- `f7174e0b7`: round-5 report and handoff.

Changed the kit script, chain, three test files and report. All ten condition-13 files and forbidden coordination files remain unchanged.

Verification:

- R1 regressions, registration, runtime contract, static closure and kit reproduction passed.
- Equality witness passed **5/5** isolated runs.
- `test_run_night`: **15 failures, 2 errors, 9 skips** across 318 tests.
- Dynamic closure timed out at the aggregate test cap. Fixture census was unavailable because `ps` was denied.

D-4 remains conditional: registration specifies token limits and a deadman, with no fixed D-load duration or 150 s minimum. Native MLX checks remain lead-owned.

Next: triage the night-driver failures, complete dynamic closure and process cleanup verification, then obtain the delta review before arming.

[Full report, commands, results and remaining gates](/Volumes/JW-EXT/jw-wt/sol-r1fu-build-r5/docs/run_reports/2026-11-11-r1-followup-kit.md:715)