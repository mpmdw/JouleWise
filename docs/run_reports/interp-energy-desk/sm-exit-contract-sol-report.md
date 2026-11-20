Committed `dad404132` on `feat/2026-11-11-sm-exit-contract`. Working tree is clean; nothing pushed.

Added nine immutable vocabularies, the fail-closed classifier, plan parser, outcome-map adapter and AST drift tests. Also added one CANONICAL row and one timing line.

Verification:

- `tests.test_exit_contract`: 26 passed.
- `tests.test_fixture_orphan_census`: OK, 2 sandbox skips.
- `tests.test_gen_state`: 44 passed.
- Compileall, 65 source-provenance checks and 10 classifier mutations passed.

Full suite was not run, as instructed. Python 3.11 runtime remains for CI. The report documents W1-only code 13, stage-only code 75 and other ambiguities.

No blocking questions. Next step: lead cold review.

[Run report](/Volumes/JW-EXT/jw-wt/sol-sm-exit-contract/docs/run_reports/2026-11-11-sm-exit-contract.md)