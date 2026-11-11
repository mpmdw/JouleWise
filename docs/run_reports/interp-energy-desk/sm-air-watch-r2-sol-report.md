Fixed AW-1 through AW-4, failing-first. AW-5 remains untouched.

- Corrected published layout and allowlist; added the HEAD writer AST drift test.
- Removed `--since-epoch`; added validated, repeatable `--include-plan`.
- Added origin protocol preflight and persistent read-failure escalation.

Changed the watcher, README, tests, and appended [Round 2 report](/Volumes/JW-EXT/jw-wt/sol-sm-air-watch-r2/docs/run_reports/2026-11-11-sm-air-watch.md:142).

Verification passed:

- `python3.13 -B -m unittest tests.test_night_results_watch`: 50 tests.
- `python3.13 -B -m unittest tests.test_fixture_orphan_census tests.test_gen_state`: 58 tests, two sandbox skips.
- `python3.13 -m compileall -q joulewise tests scripts`.
- All 17 targeted mutations caught.

Local commits: `849d5cc00` and `a0bdc35c5`. Worktree clean; nothing pushed. No network or real measurement data used.

No open questions. Live behavior remains unverified: the lead’s next step is one Air poll with `--once --include-plan <known-finished-rehearsal>` and a scratch state file.