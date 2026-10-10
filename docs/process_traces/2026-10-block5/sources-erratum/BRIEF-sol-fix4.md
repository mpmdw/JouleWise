SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["tests/**"]

For the report envelope: genre implementation; keep the JSON header under 4,000 bytes and put all evidence in the markdown body. End your turn after writing the report. Start no background task. Commit nothing; leave your changes uncommitted in the working tree.

# Round 4 (tests only): the independent reviewer's test additions on the harvest lane

You work in `/Users/edr/code/JouleWise-wt-harvest-sources`, branch `lane/2026-10-10-harvest-screen-sources`, head `067f4deabe45e5192553f26cf42a2ca087fb8704`. Change files under `tests/` only; no production file changes. Run only the modules you touch, one at a time, with `PYTHONDONTWRITEBYTECODE=1 TMPDIR=/Users/edr/.jwtmp/v4 /opt/homebrew/bin/python3.13 -m unittest <module>` (the directory `/Users/edr/.jwtmp/v4` exists and is writable; if your sandbox cannot write there, use the default temp directory, but create no directory inside the working tree). Never `unittest discover` or `shard_tests.py`. No Homebrew, no network, no other agents, no measurement. Do not open anything under `/Users/edr/night-custody/v5-b5-*`, `/Users/edr/night-b5/` or `/Users/edr/night-archive/harvest-v5-b5-*`. The owner's name and address go into no file and no request.

An independent executing reviewer approved the program and found surviving mutants: checks that are right in the program but that no test would catch if they were deleted. Its proposed tests, each verified by it against the mutant, are in `/Users/edr/.jwtmp/review/mut/tests/test_zz_review_proposed.py` (read it). Do this:

1. Add to `SourceRecoveryTests` in `tests/test_harvest_b5_sources.py`, adapting names to the fixture as it is at this head, the reviewer's tests for:
   - S1: `test_recovery_never_uses_collected_or_stored_bound` (no clean bound, a collected bound present and a bound on the stored bracket: still `clean_bound_unavailable`).
   - S2: `test_insufficient_shape_with_surviving_midpoint_records_midpoint_not_lost` (survivors (2,1,1): failed, `references_insufficient`, `midpoint_lost` false, no `neg8.midpoint_lost` flag).
   - S3: `test_basis_check_compares_each_of_the_three_hashes` (config, metadata and summary hash each decide by themselves), and add a sub-case in which one of the survivor's three files cannot be read: the check must return `reference_not_in_verdict_basis`, not accept it.
   - S4: `test_extra_member_with_disagreeing_role_fails_a_full_shape` (a full (3,1,3) window plus one invoked member whose role and sentinel position disagree: failed, `neg8_bracket_reference_invalid`).
   - N1: in `test_malformed_present_source_list_never_enters_recovery`, loop the present-but-not-a-list values `None`, `{}`, `""`, `0` as well as the string already there.
   - N4: in `test_noninvoked_references_never_count`, also assert that the screen record's `harvest_reference_losses` is empty.
2. Revert one hunk: `tests/test_harvest_b5_window.py`, `HarvestCheckoutTests`, the edit made in round 2 near lines 2628 to 2652 that replaced an independent `git status` call with the status the program itself captured. Restore that test to its text at `224a264c5faaae90cdf56118df37e773a932700b` (`git show 224a264c5:tests/test_harvest_b5_window.py`), leaving the round-2 edits near lines 1856, 1876 and 1887 (`recovery_predates_erratum`) as they are. With TMPDIR outside the working tree the original test passes.
3. Run `tests.test_harvest_b5_sources` and `tests.test_harvest_b5_window.HarvestCheckoutTests` and report the result lines. Report `git status --short` (it must list only files under `tests/`).

If a proposed test does not pass against the unchanged program, do not weaken it and do not change the program: report exactly what it asserted and what the program returned.
