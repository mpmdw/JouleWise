```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented Erratum 2 recovery checks; focused regressions and the real rehearsal screen comparison passed.",
  "workspace": {
    "base_requested": "0b23cf491c928c7d6fb38aa4e5674550d0700dce",
    "base_mode": "exact",
    "head_start": "0b23cf491c928c7d6fb38aa4e5674550d0700dce",
    "head_end": "0b23cf491c928c7d6fb38aa4e5674550d0700dce",
    "upstream_end": "0b23cf491c928c7d6fb38aa4e5674550d0700dce",
    "branch": "lane/2026-10-10-harvest-screen-sources"
  },
  "pathspec": [
    "joulewise/b5/harvest.py",
    "joulewise/whole_window.py",
    "tests/test_harvest_b5_sources.py",
    "tests/test_harvest_b5_window.py",
    "tests/test_neg8_survivors.py",
    "tests/test_harvest_b5_rehearsal_compare.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The broad targeted run was not repeated in full after its four failure sites were corrected; the final focused rerun passed.",
      "needs": "Lead final diff review and remaining suite, CI, cold-review and pin gates."
    }
  ]
}
```

## Change

Implemented the frozen recovery checks and disclosure. Recorded-source handling retains its existing path. No estimator, verdict writer, catalog, registration, or CLI script changed.

Changes remain uncommitted. `.scratch-fix/` was deleted. No claim-window files were opened or processed.

## Item-by-item table

H = [joulewise/b5/harvest.py](/Users/edr/code/JouleWise-wt-harvest-sources/joulewise/b5/harvest.py); WW = [joulewise/whole_window.py](/Users/edr/code/JouleWise-wt-harvest-sources/joulewise/whole_window.py). Tests below are methods of `SourceRecoveryTests` in [test_harvest_b5_sources.py](/Users/edr/code/JouleWise-wt-harvest-sources/tests/test_harvest_b5_sources.py).

| Item | Implementation | Covering test(s) | Agreement |
|---|---|---|---|
| 0(a) | H:5217 — absent field or empty list enters recovery; recorded descriptors bypass it | `test_missing_source_field_and_absent_bracket_use_authenticated_catalog`; `test_malformed_present_source_list_never_enters_recovery`; `test_recorded_sources_are_byte_identical_to_the_sealed_harvest` | exact |
| Program gate | H:87, H:5222 — constants and strict `t0_epoch_s` comparison; unreadable t0 fails | `test_program_gate_constants_and_order`; `test_ungoverned_t0_discloses_cannot_run` | exact |
| 0(b) | H:1190 — hazard-root predicate | `test_non_hazard_root_is_first_item_zero_failure` | exact |
| 0(c) | H:1192 — unresolved required; ambiguity and occurrence refusal excluded | `test_stored_membership_must_be_unresolved_without_ambiguity_or_refusal` | exact |
| 0(d) | H:1207 — all invoked members resolved through `ordinary_present_bundle_paths`; absence required | `test_no_absent_invoked_member_precedes_ambiguity_and_supersession` | exact |
| 0(e) | H:1212 — multiple directories rejected | `test_ambiguous_second_directory_precedes_supersession` | exact |
| 0(f) | H:1214 — recognizable supersession rows rejected, including malformed rows without an id | `test_occurrence_supersession_row_even_without_id_blocks_recovery` | exact |
| 1 | H:1198 — complete authentication, nonempty catalog, schema v2 | `test_unauthenticated_manifest_still_fails`; `test_empty_catalog_is_unrecorded`; `test_v1_manifest_cannot_supply_recovery`; `test_all_v1_catalog_without_log_is_schema_v1` | exact |
| 2 | H:1219, H:1229 — registered policy, matching manifest policy, safe paths, occurrence duplicates | `test_policy_unregistered_cannot_run`; `test_policy_difference_still_fails`; `test_authenticated_manifest_path_outside_root_cannot_run`; `test_unsafe_bundle_id_cannot_run`; `test_duplicate_absent_id_in_one_manifest_cannot_run` | exact |
| 3 | H:1243; WW:4982 — invoked references checked against roster slots; invalid reference roles fail the screen | `test_reference_outside_roster_or_at_wrong_slot_cannot_run`; `test_noninvoked_references_never_count`; `test_role_position_disagreement_fails_the_screen`; `test_roster_reference_with_unrecognized_role_fails_the_screen` | exact |
| 4 | H:5101, H:5211; WW:5030, WW:5076 — existing losses retained; absent reference reason overrides other reasons; losses precede reduction | `test_bundleless_spare_and_empty_sources_screen_survivors`; `test_absent_spare_reason_and_retry_counts`; `test_strict_and_custody_invalid_references_are_lost`; `test_summary_unreadable_is_lost_before_reduction`; `test_unreadable_energy_reference_is_lost_before_reduction` | exact |
| 5 | H:5418 — clean bound required; no fallback bound on recovery | `test_recovery_requires_a_clean_bound`; `test_missing_clean_bound_disclosure_is_exact` | exact |
| 6 | H:5463; WW:5196, WW:5223 — registered evaluator, required arguments, endpoint minimum and realised midpoint loss | `test_fewer_than_two_survivors_still_fail`; `test_more_references_than_planned_still_fail`; `test_statistic_exceeding_bound_still_fails`; `test_legacy_pair_cannot_pass_catalog_recovery`; `test_insufficient_shape_midpoint_lost_matches_survivors`; `test_no_surviving_reference_still_runs_current_shape_evaluator` | exact |
| 7 | H:1224, H:5244, H:5484; WW:5098 — validated basis, survivor-only membership and three fresh hashes; stored bracket comparison bypassed only for recovery | `test_invalid_evaluation_basis_is_not_rescued`; `test_missing_basis_cannot_run`; `test_surviving_reference_outside_basis_cannot_run`; `test_survivor_hash_mismatch_against_valid_basis_cannot_run`; `test_changed_bytes_at_basis_path_are_evaluation_basis_invalid`; `test_lost_reference_need_not_be_in_basis`; `test_stored_neg8_conditions_decide_nothing_on_recovery` | exact |
| 8 | H:5053, H:5085, H:5409, H:5503 — identical source objects in screen, failed flag and allowance; closed problem word retained | `test_recovery_disclosure_in_allowance_is_exact`; `test_missing_clean_bound_disclosure_is_exact`; `cannot_run` assertions used by negative cases; `test_absent_spare_reason_and_retry_counts` | exact |

The program gate is tested **after 0(a) and before 0(b)**. Conditions 0(b) through 0(f) retain their stated relative order. Catalog authentication and schema validation precede enumeration for 0(d)–0(f).

Item 9 was not implemented.

## Tests

Replay preparation:

```sh
mkdir -p .scratch-fix
```

Final focused command:

```sh
PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.scratch-fix" /opt/homebrew/bin/python3.13 -c 'import tempfile, unittest; from pathlib import Path; tempfile.tempdir = str(Path(".scratch-fix").resolve()); names=("tests.test_harvest_b5_sources", "tests.test_neg8_survivors.HarvestSurvivorTests.test_the_audit_strict_trigger_rescreens_the_survivors", "tests.test_neg8_survivors.ReplaySurvivorTests", "tests.test_neg8_survivors.SurvivorScreenEvaluatorTests", "tests.test_neg8_survivors.RosterNamedReferenceLossTests", "tests.test_harvest_b5_window.Neg8ScreenTests", "tests.test_harvest_b5_window.HarvestCheckoutTests"); result=unittest.TextTestRunner().run(unittest.defaultTestLoader.loadTestsFromNames(names)); raise SystemExit(not result.wasSuccessful())'
```

Result: **81 tests, `OK`, exit 0**.

Earlier broader targeted command:

```sh
PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.scratch-fix" /opt/homebrew/bin/python3.13 -c 'import tempfile, unittest; from pathlib import Path; tempfile.tempdir = str(Path(".scratch-fix").resolve()); names = ("tests.test_harvest_b5_sources", "tests.test_neg8_survivors", "tests.test_neg8_corpus_cap", "tests.test_harvest_b5_window"); suite=unittest.defaultTestLoader.loadTestsFromNames(names); result=unittest.TextTestRunner().run(suite); raise SystemExit(not result.wasSuccessful())'
```

Result: **361 tests, `FAILED (failures=4)`, exit 1**. All four failure sites were corrected and included in the passing focused rerun:

- A mocked recorded-source probe now explicitly identifies recorded sources.
- Checkout provenance compares Git status captured at the harvest boundary; scratch files created afterward can change the later count.
- Two source-less fixtures now expect `recovery_predates_erratum`.
- Recovery entry failure suppresses secondary evaluation-time problems.

`git diff --check`: exit 0. HEAD and upstream remain unchanged. Outside tests, the diff against `224a264c5` names only the two authorized implementation files.

Neither `unittest discover` nor `shard_tests.py` ran.

## Rehearsal comparison

Command:

```sh
B5_REHEARSAL_COMPARE=1 PYTHONDONTWRITEBYTECODE=1 TMPDIR="$PWD/.scratch-fix" /opt/homebrew/bin/python3.13 -m unittest tests.test_harvest_b5_rehearsal_compare
```

Result: **one test, `OK`, exit 0**:

```text
rehearsal_derived_byte_identity PASS
rehearsal_withheld_byte_identity PASS
rehearsal_emitted_flags_equal PASS
rehearsal_archived_derived_byte_identity PASS
rehearsal_derived_records 4
rehearsal_recorded_reductions 7
```

The test loaded pinned harvest and whole-window modules using `git show`, then ran `neg8_corpus_physics`, `neg8_screen` and `neg8_allowance` under both programs over scratch copies of the completed rehearsal archive.

It compared:

- Exact bytes of `neg8-clean-corpus.json`, `neg8-corpus-physics.json`, `neg8-screen.json` and `neg8-allowance.json`.
- Exact bytes of both emitted withheld bracket/bound records.
- Complete emitted flag records with identical deterministic clocks.
- The four derived records against the archive’s existing pinned outputs.

The comparison reused the archive’s seven recorded re-reductions, checking their digests against the member assessments. The ordinary screen validation remained active. An initial fresh-reduction attempt was interrupted with exit 130 because the pinned uncertainty calculation exceeded the intended bounded check. No full harvest completed.

## Admitted-text ambiguities or deviations

No blocking ambiguity or unimplemented item was identified within items 0–8 and the program gate.

A mutation at a basis entry’s own path gives `evaluation_basis_invalid`, as required by `_validated_evaluation_basis`. A survivor absent from an otherwise validated basis, or differing from its listed bytes, gives `reference_not_in_verdict_basis`. Both cases are tested.

## Residual risk

The complete broader targeted run was not repeated after the fixes; the focused rerun covered every failure site. The rehearsal comparison does not independently repeat the expensive pinned estimator or all member assessments.

The next step is lead diff review and the remaining suite, CI, cold-review and pin gates. Item 9 remains the later claim-consumer lane’s responsibility.