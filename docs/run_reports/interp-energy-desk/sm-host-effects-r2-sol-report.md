Committed `f0546916f` on `feat/2026-11-11-sm-host-effects`. Tree is clean; nothing pushed.

Applied HE-1–HE-3 in [host_effects.py](/Volumes/JW-EXT/jw-wt/sol-sm-host-effects-r2/joulewise/host_effects.py), expanded [tests](/Volumes/JW-EXT/jw-wt/sol-sm-host-effects-r2/tests/test_host_effects.py), and appended the [Round 2 report](/Volumes/JW-EXT/jw-wt/sol-sm-host-effects-r2/docs/run_reports/2026-11-11-sm-host-effects.md:148). Unknown observations remain unknown.

Verification passed with default TMPDIR:

- `unittest tests.test_host_effects`: 39 tests.
- `unittest tests.test_fixture_orphan_census`: 14 tests, 2 skipped.
- `unittest tests.test_gen_state`: 44 tests.
- Compilation and `git diff --check`.

Mutation pass: **278/279 killed**. The sole survivor is equivalent: `< start` → `<= start` after equality already returns active. Full commands and justification are in the report.

No open questions. Python 3.11, native validation and the full suite were not run. Next step: lead cold review.