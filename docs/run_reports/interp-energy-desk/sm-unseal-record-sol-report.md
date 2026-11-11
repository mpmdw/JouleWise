Committed `144c9ce8c` on `feat/2026-11-11-sm-unseal-record`. Working tree is clean; no push.

Added the unseal schema, committed-record enforcement, verdict digest binding, path permissions, guard CLI, tests and documentation. Updated CANONICAL and the timing map. Block 5’s release tool is unchanged.

Verification:

- `tests.test_unseal_record`: 31 passed.
- `tests.test_fixture_orphan_census`: 14 tests, two sandbox skips.
- `tests.test_gen_state`: 44 passed.
- Compilation of touched Python files passed.

The [run report](/Volumes/JW-EXT/jw-wt/sol-sm-unseal-record/docs/run_reports/2026-11-11-sm-unseal-record.md) lists all files, commands, v4 integration lines and remaining checks. Python 3.11 and the skipped live census checks remain for the lead.

Intake mistake: decision-file reads included later Block 5 prose. No custody files were opened or outcome values copied into the implementation or tests.