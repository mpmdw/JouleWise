SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["joulewise/whole_window.py", "joulewise/neg8_survivors.py", "configs/gates/hazard_refusals.json", "configs/pins/**", "scripts/digest_pin_census.py", "tests/test_analysis_integration.py", "tests/test_repin.py", "tests/b5_analysis/test_validator_context.py", ".scratch-s3suite/**"]

For the report envelope: genre implementation; keep the JSON header under 4,000 bytes and put all evidence in the markdown body. End your turn only after the work is complete and the report is written. Start no background task and no other agent. Commit nothing. **You have 90 minutes of wall time; write the report by minute 80 whatever is unfinished.**

# Lane L9 stage S3: five whole-suite failures on the S3 head, two of them regressions of existing callers

You work in `/Users/edr/code/JouleWise-wt-l9-s3` (branch `lane/2026-10-12-l9-s3`, head `9f2a7e27b`, clean).
The lead ran the whole suite on this head (logs:
`/Users/edr/night-archive/b5-consults/l9-rulings/suite-s3/shard{1..6}.log`). Five failures are caused by
stage S3's changes. Fix each at its cause; silence no check. Items 1 and 2 are **regressions of callers that
pass no archive context**, which the rulings forbid (`RULING.md` J1 item 12, in
`/Users/edr/code/JouleWise-wt-b5-records/docs/process_traces/2026-10-block5/l9-rulings/`: "Without a context
every function behaves byte for byte as today, on every root"): the pinned base is
`git show b039c0257d1b1d407ee9598222db3f78f6ad7beb:joulewise/whole_window.py`.

1. `tests.test_run_campaign` `IdleAdmissionCoreVerdictTests.test_claim_row_rejects_structurally_valid_unregistered_drift_corpus`
   (`shard5.log`): the test hands `_validate_row` a `unittest.mock.Mock` as the consumption session and no
   context; the new code reaches `harvest_neg8_allowance_bracket(context.neg8_harvest_archive, row)` and fails
   with a `TypeError` on a `Mock`. So the validator takes a context from an attribute of whatever session
   object it is given. Required: a context exists only when it is an actual `ArchiveContext` instance, at
   every site that reads one (session attribute, argument, cache key); anything else is "no context" and
   behaves as the base. Find every such site. Add a test in
   `tests/b5_analysis/test_validator_context.py`: a session double whose attribute is not an `ArchiveContext`
   gives exactly the base's result on a stored-failed row.
2. `tests.test_harvest_g2a_window`
   `G2aHarvestTests.test_real_passed_bracket_after_nonzero_acceptance_cutoff_selects` (`shard6.log`; it fails
   alone too): the outcome is `('REFUSED', ['ledger_authentication_failed'])` where the base gives
   `('SELECT', [])`. This is an older block's harvest (no context anywhere). Find which S3 edit changed it
   (bisect by restoring functions from the pinned base in a scratch copy), state the cause in one sentence,
   and restore the base behaviour for a caller without a context. Then extend the no-context differential:
   add to `tests/b5_analysis/test_validator_context.py` a test that runs this harvest path's validator and
   allowance calls against the pinned base and the current file and compares results exactly.
   For both items, after the fix run the whole of `tests.test_run_campaign` and `tests.test_harvest_g2a_window`
   once (they take several minutes each) and report the results.
3. `tests.hazards.test_refusal_allowlist` (`shard4.log`, two tests): new refusal sites in
   `joulewise/whole_window.py` are unlisted, and `whole_window.py` now depends on
   `joulewise/neg8_survivors.py`, which is neither scanned nor listed. Run
   `python -m tests.hazards.refusal_census`; add each new site to `configs/gates/hazard_refusals.json` in the
   file's format, classified by what it is (read how the existing `whole_window.py` sites and the two
   `calibration_bracketing.py` sites added on 2026-10-12 are classified: desk-analysis refusals are not
   physical hazards and never stop collection); put `neg8_survivors.py` where the census's rules say a pure
   desk helper belongs (scanned, or `not_scanned` with its reason).
4. `tests.test_analysis_integration`
   `SupersessionAwareCooldownJoinTests.test_campaign_provenance_aggregation_call_site_fence` (`shard5.log`):
   the fence counts call sites of the campaign-catalog reader per file, and
   `joulewise/b5_analysis/sources_replay.py` is a new one. Read what the fence protects and what it requires
   of a call site (the test's comments and the functions it names), check that the new call site meets it (it
   calls the frozen harvest's `claim_neg8_sources`; say exactly which reader it reaches and with what
   authentication), and then add it to the fence's table with a comment. If it does not meet the fence's
   requirement, do not add it: report what `sources_replay.py` must change (that file is not in your scope).
5. `tests.test_repin` `RealTreeTests.test_committed_registry_kind_p_rows_are_current` (`shard6.log`):
   `configs/analysis/b5/seal_pins.json` records digests of `joulewise/whole_window.py` at four pinned
   commits, and the pin registry treats one of them as a pointer to the current file. Those digests are, by
   definition, records at named commits (each pin's `head` is in the same file). The lane already declared
   the sealed inventory an era record this way (`scripts/digest_pin_census.py`, commit `64a094d76`); do the
   same for `seal_pins.json` with each pin's own `head` as the commit, regenerate the registry, and add a
   regression. If the era mechanism cannot express a per-entry commit, report what it would need instead of
   forcing it.

Constraints: edit nothing outside WRITE_SCOPE (in particular no file under `joulewise/b5/`,
`joulewise/b5_analysis/`, `scripts/run_campaign.py`, and no existing test other than the two named).
Interpreter `/opt/homebrew/bin/python3.13`, `PYTHONDONTWRITEBYTECODE=1`, `TMPDIR=/private/tmp`; run modules
under `tests/` the way CI does (`scripts/shard_tests.py`), and `tests.b5_analysis.*` from the repository
root. After your changes `tests.b5_analysis.test_validator_context`, `test_neg8_parity`,
`test_neg8_predicate` and `test_launch_lineage` must still pass. Blinding (binding): do NOT open anything
under `/Users/edr/night-custody/v5-b5-*`, `/Users/edr/night-b5/`, `/Users/edr/night-g2a/`,
`/Users/edr/night-archive/harvest-v5-b5-*`, or any runs root under `/Users/edr/night-custody/measurement/`.

Report: per item, the cause in one sentence, the change, the test results; for items 1 and 2 the list of
every site where a context is read and the differential's result.
