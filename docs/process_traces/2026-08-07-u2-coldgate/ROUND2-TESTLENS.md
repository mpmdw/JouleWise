# Verdict: FAIL — coverage gaps block U2 landing credit

All tests pass, but the requested four failure families are gaps. The suite strongly covers ordinary arithmetic, trigger classification, deterministic building, and happy-path publication; it does not establish crash-safe publication, rollback, durability-uncertain handling, or receipt authenticity against forgery.

## P1 findings

1. Torn publication is untested. The publication portfolio contains only a precondition failure before mutation and an uninterrupted success path: [test_calibration_acceptance_successor.py:1058](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/tests/test_calibration_acceptance_successor.py:1058), [test_calibration_acceptance_successor.py:1082](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/tests/test_calibration_acceptance_successor.py:1082).

   Admitted broken implementation: replace the registry before the artifact, or crash after the registry replacement but before `update-ref`; the tests never interrupt at either replacement. No assertion proves the prior committed registry remains selectable after a torn worktree publication.

2. Rollback after a partially executed publication is untested. The rollback code at [build_calibration_acceptance_successor.py:837](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/scripts/build_calibration_acceptance_successor.py:837) is never reached by an injected failure after either visible replacement, `commit-tree`, commit inspection, or failed `update-ref`.

   Admitted broken implementation: change line 839 to restore `build.registry_bytes` instead of `initial_registry_bytes`, or delete the artifact cleanup at line 841. Existing tests remain green because their only failed publication exits before staging.

3. Durability-uncertain behavior is asserted, not exercised. No test observes `os.fsync`, directory fsync, or the post-`update-ref` failure branch at [build_calibration_acceptance_successor.py:808](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/scripts/build_calibration_acceptance_successor.py:808). `SuccessorDurabilityUncertain` and CLI exit 3 have zero coverage here.

   Admitted broken implementations:

   - Delete file fsync or either directory fsync at lines 561, 712, or 714.
   - Leave `ref_advanced=False` after successful `update-ref`; a later verification failure would restore old worktree bytes while `HEAD` points to the successor. The happy test still passes.

4. Receipt authentication has no forgery discriminator. Successor tests synthesize `CalibrationLedgerSnapshot` and arbitrary receipt digests directly, then almost universally set `verify_custody=False`: [test_calibration_acceptance_successor.py:39](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/tests/test_calibration_acceptance_successor.py:39), [test_calibration_acceptance_successor.py:181](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/tests/test_calibration_acceptance_successor.py:181). The “authenticated terminal” test is synthetic; its negative twin merely removes `attempt_id`: [test_calibration_acceptance_successor.py:439](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/tests/test_calibration_acceptance_successor.py:439).

   The real 76-receipt test is a useful positive path but has no self-consistent forged-chain twin: [test_calibration_bracketing.py:616](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/tests/test_calibration_bracketing.py:616).

   Admitted broken implementation: remove the receipt-digest equality at [calibration_bracketing.py:1954](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/joulewise/calibration_bracketing.py:1954). The malformed-receipt test still refuses because `attempt_id` is missing, while a well-formed forged receipt is untested.

5. Fixture cadence is synthetic and position-coupled. Parent observations are assigned `sequence=index*2`, new observations `77+index`, while new fixture receipts consume only one sequence each: [test_calibration_acceptance_successor.py:67](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/tests/test_calibration_acceptance_successor.py:67), [test_calibration_acceptance_successor.py:101](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/tests/test_calibration_acceptance_successor.py:101), [test_calibration_acceptance_successor.py:125](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/tests/test_calibration_acceptance_successor.py:125).

   Admitted broken implementation: derive cutoff as `parent_cutoff + len(new_content_ids) + len(noncontent_rows)` rather than using the authenticated ledger head. It matches every synthetic cadence here but fails when real captures add reservation and finalization receipts. The successor portfolio needs at least one builder test fed by `load_calibration_ledger_snapshot`.

## P2 findings

6. The two-site boundary freeze lacks a second-generation discriminator. Tests cover helper recomputation and loading one v2→v3 child: [test_calibration_acceptance_successor.py:926](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/tests/test_calibration_acceptance_successor.py:926).

   Admitted one-line mutation: make `_artifact_count_boundary` return `76` for every v3 artifact at [calibration_bracketing.py:1859](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/joulewise/calibration_bracketing.py:1859). Current cases still pass: 31 observations do not cross either 38 or 76, and the 38-trigger successor already records 76. A generation-2 artifact recording boundary 38 would silently be treated as 76.

7. Window-B exclusion verifies only cardinality and two named IDs, not the exact parent basis: [test_calibration_acceptance_successor.py:820](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/tests/test_calibration_acceptance_successor.py:820).

   Admitted one-line mutation: in `_artifact_derivation_content_ids`, swap legitimate basis ID `c2a441…e2e9` for unasserted valid nonbasis ID `887286…a8f8`. The result still has 19 members and excludes the two asserted Window-B IDs; builder and loader consume the same wrong helper result. Assert the entire basis equals the parent artifact’s 19 mapped member content IDs.

8. Trigger/basis decoupling is calibrated to one fixed 11-member gap. The only builder cases are `20+11=31` and `27+11=38`: [test_calibration_acceptance_successor.py:854](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/tests/test_calibration_acceptance_successor.py:854), [test_calibration_acceptance_successor.py:913](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/tests/test_calibration_acceptance_successor.py:913).

   Admitted one-line mutation: pass `trigger_count=derivation_count + 11` at [build_calibration_acceptance_successor.py:404](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/scripts/build_calibration_acceptance_successor.py:404). Every current decisive assertion passes, but later generations or a changed valid/nonbasis population compute the wrong boundary. Add a fixture where the gap is not 11.

9. `invalid_acceptance_arithmetic` mutates only the cap. The test at [test_calibration_bracketing.py:1459](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/tests/test_calibration_bracketing.py:1459) does not independently corrupt screen sign, screen/ceiling ordering, missing fields, or nonfinite values.

   Admitted one-line mutation: remove `screen >= 0` from [calibration_bracketing.py:709](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/joulewise/calibration_bracketing.py:709). The cap-zero fixture still refuses, while a coherent negative-screen artifact passes the runtime guard.

10. The half-even test shares the implementation’s rounding constant: [test_calibration_acceptance_successor.py:604](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/tests/test_calibration_acceptance_successor.py:604). It computes its oracle with `bracketing.ROUND_HALF_EVEN` instead of an independent literal.

    Admitted broken implementation: alias `ROUND_UP` as `ROUND_HALF_EVEN`; the implementation and test oracle move together. Assert the literal tie result `0.000000000000000`.

11. Registry negative tests conflate independent invariants. The multiple-active fixture is also self-cyclic, so omitting either validator independently does not make the test fail: [test_calibration_acceptance_successor.py:298](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/tests/test_calibration_acceptance_successor.py:298). The “duplicate paths” test contains only traversal paths and no duplicate: [test_calibration_acceptance_successor.py:311](/private/tmp/claude-501/-Users-edr-code-JouleWise/377d50a5-4fb9-4f74-b609-0a370965fdf2/scratchpad/u2rework/tests/test_calibration_acceptance_successor.py:311).

    Admitted broken implementations: delete the exactly-one-active check or duplicate-artifact-path check; these tests remain green.

## Required family verdicts

| Family | Verdict | Missing evidence |
|---|---|---|
| Torn publication | **GAP** | Kill/fault after artifact replacement, after registry replacement, before/after commit creation, and before `update-ref`; assert prior committed selection remains authoritative. |
| Rollback | **GAP** | Inject failures after every visible mutation and assert exact old registry bytes, artifact absence/preservation, old `HEAD`, and old active selection. |
| Durability uncertain | **GAP** | Assert file/directory fsync ordering; inject post-`update-ref` verification failure; assert successor `HEAD` remains authoritative and CLI returns 3. |
| Receipt authentication | **GAP** | Pair the real positive loader test with a well-formed, internally rehashed forged receipt/chain or wrong committed pin and require refusal before successor logic. |

## Decisive mutation check

| Decisive test | Escaping single-line mutation |
|---|---|
| No-clamp issuance refusal | Change `bracket_screen >= ceiling` to `bracket_screen == ceiling`; current fixture creates equality, so true `screen > ceiling` is untested. |
| `invalid_acceptance_arithmetic` | Remove `screen >= 0`; cap-zero still refuses. |
| Two-site freeze | Return `76` for every v3 `_artifact_count_boundary`; current first-generation cases pass. |
| Window-B exclusion | Swap one legitimate basis ID for an unasserted valid nonbasis ID while retaining 19 and excluding the two named IDs. |
| Trigger/basis decoupling | Use `derivation_count + 11` as the trigger count; current 20/31 and 27/38 fixtures pass. |

## Tests judged discriminating

Credit these for the specific branches they exercise:

- Registry: `test_registry_requires_committed_bytes_when_requested`, `test_current_selection_is_plain_committed_registry_load`, `test_registry_rejects_symlink_artifact_substitution`, `test_uncommitted_registry_replacement_names_missing_commit_everywhere`.
- Trigger classification: `test_range_expansion_below_and_above_require_successor`, `test_in_range_observation_does_not_trigger_before_boundary`, `test_counts_37_and_38_are_distinct`, `test_systematic_classification_and_above_screen_both_refuse`, `test_ordinary_invalid_is_recorded_but_does_not_trigger`, `test_same_content_alias_does_not_increment_count`, `test_same_content_conflicting_disposition_epoch_bound_or_hash_refuses`, `test_other_epoch_valid_is_excluded_without_self_fit`, `test_observed_epoch_and_estimator_bytes_refuse_before_science`, `test_probe_does_not_consult_writer_copied_scalar`, `test_prefix_omission_and_physical_pin_mismatch_refuse`.
- Numerical kernel: `test_n19_issued_pin_and_successor_kernel_split_are_exact`, `test_negative_nonfinite_and_binary_float_inputs_refuse`, `test_quantile_algorithm_and_d102_pin_are_stable`, `test_nonpinned_df37_matches_checked_in_independent_reference`, `test_quantile_continued_fraction_nonconvergence_is_governed`, `test_ratified_minimum_refuses_derivation_basis_below_19`, `test_degraded_n30_worked_arithmetic_grows_both_envelopes`, `test_zero_variance_inherits_strictly_ordered_parent_envelope`.
- Builder/runtime: `test_repeated_and_shuffled_builds_are_byte_identical`, `test_real_successor_probe_rejection_blocks_build`, `test_nonterminal_or_uncommitted_head_refuses`, `test_no_content_closure_does_not_brick_range_successor`, `test_d079_drift_beyond_budget_refuses_with_recorded_basis`, `test_d102_decimal_boundary_sweep_is_exact_and_inclusive`.
- Authentication positives/negative artifacts: `test_production_path_authenticates_real_76_receipt_import_prefix`, `test_rekeyed_self_consistent_artifact_is_not_authenticated`, `test_hash_rekeyed_candidate_cannot_bypass_binding_authentication`.

The no-clamp, invalid-arithmetic, two-site-freeze, Window-B, and trigger/basis tests deserve only branch-specific partial credit because each has the mutation escape above.

Checks performed: branch/head verified at `e5cf244`; focused audit suite `86/86 OK`; canonical suite `2736 OK (skipped=87)`; `git diff --check` clean; final worktree clean; no files edited.