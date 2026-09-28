```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "partial",
  "summary": "The mutation gate has four GREEN R7-freeze mutants; all other valid plants went RED and every production file was restored.",
  "workspace": {
    "base_requested": "8458f797d0a7d9854d3799863ff3b9d1fd06285a",
    "base_mode": "exact",
    "head_start": "8458f797d0a7d9854d3799863ff3b9d1fd06285a",
    "head_end": "8458f797d0a7d9854d3799863ff3b9d1fd06285a",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [
    "joulewise/calibration_bracketing.py",
    "joulewise/arm_readiness.py",
    "scripts/promote_calibration_candidate.py",
    "scripts/issue_calibration_acceptance_generation.py",
    "scripts/epoch_equivalence_check.py",
    "scripts/sim_acc_25g83_rev5.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "M1",
        "severity": "blocker",
        "text": "The R7 predecessor-comparison mutant and all three frozen-default mutants remain GREEN because the live default is R7 at this head."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-mut2-d528efb2/run_mutations.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "restore_verified"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-mut2-d528efb2/run_mutations.py L4_N1 L5 P3_digest",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "restore_verified"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --quiet -- joulewise/calibration_dispositions.py joulewise/calibration_bracketing.py joulewise/arm_readiness.py scripts/promote_calibration_candidate.py scripts/issue_calibration_acceptance_generation.py scripts/epoch_equivalence_check.py scripts/sim_acc_25g83_rev5.py",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The amended all-RED gate is unmet: four R7-freeze counterfactuals are observationally identical to the current R7 default.",
      "needs": "Lead to adjudicate the gate and arrange discriminating tests."
    },
    {
      "id": "F2",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "Closing M1 requires test edits outside this seat's write scope; none were made.",
      "needs": "Lead-owned test changes or a resumed prompt expanding scope."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "tests/test_acc_25g83_rev5.py",
      "tests/test_epoch_equivalence_check.py"
    ],
    "reason": "The existing tests need a simulated non-R7 live default to distinguish the frozen R7 references from the named wrong implementations.",
    "blocked_work": "Showing all four R7-freeze mutants RED.",
    "minimal_change": "Patch the imported ACTIVE_ACCEPTANCE_ID or DEFAULT_ACCEPTANCE_BOUND_PATH to a distinct sentinel within the relevant tests, then rerun the four mutants."
  }
}
```

MUTATION: GAPS

## Findings

**M1 — blocker.** The R7 comparison and three frozen-default mutations stayed GREEN. The addendum keeps `ACTIVE_ACCEPTANCE_ID` and `DEFAULT_ACCEPTANCE_BOUND_PATH` at R7, so each wrong reference currently resolves to the same value as the explicit R7 reference. Replanting the predecessor-comparison mutant also stayed GREEN.

The table gives test method IDs within their named test files. Every row was run with `/opt/homebrew/bin/python3 -B`; each planted file was restored byte-for-byte and passed `git diff --quiet` before the next plant. Individual command output is in [the scratch logs](/tmp/d138-mut2-d528efb2).

| Ruled ID | Planted defect, exact edit | Test ID | Observed result | Restore verified |
|---|---|---|---|---|
| L2 | Skip rows by non-registration `session_id` instead of disposed `content_id`. | `test_calibration_dispositions.DispositionTests.test_l2_unlisted_foreign_valid_refuses` | **RED**, line 57: `True is not false` | Yes |
| L4 + N1 | Use all `DISPOSITION_DECISIONS` to form `disposed`; delete the declared-decision equality check. | `test_calibration_dispositions.DispositionTests.test_l3_l4_declaration_refuses`; `.test_l10_undeclared_decision_touching_prior_set_refuses` | **RED**, lines 70 and 150: `True is not false` | Yes |
| L5 | Delete `if not disposed.issubset(set(prior_ids)): return False`. | `test_calibration_dispositions.DispositionTests.test_l5_missing_disposed_row_refuses` | **RED by error**: `KeyError` in the next guard, from test line 83 | Yes |
| L6 | Remove the registration-session arm of the disposed-row guard. | `test_calibration_dispositions.DispositionTests.test_l6_disposed_inside_registration_refuses` | **RED**, line 94: `True is not false` | Yes |
| L7, rounds 1 and 2 | Remove `or content_id in member_content_ids` from the disposed-row guard. | `test_calibration_dispositions.DispositionTests.test_l7_member_in_disposition_table_refuses` | **RED twice**, line 124: `disposed member passed the member guard` | Yes, both |
| L8 | Replace the table-derived disposed set with a literal set of the original 11 IDs. | `test_calibration_dispositions.DispositionTests.test_l8_table_missing_row_refuses` | **RED**, line 136: `True is not false` | Yes |
| P3, digest | Delete the candidate SHA-256 guard. | `test_promote_calibration_candidate.PromotionTests.test_p3_changed_member_refuses_both_seals` | **RED**, line 55: expected `candidate digest mismatch`, got `candidate seal or role mismatch` | Yes |
| P3, seal | Delete both candidate derivation-seal comparisons. | Same P3 test | **RED**, line 58: expected `candidate seal`, got `issuance record source candidate mismatch` | Yes |
| H-T1, rounds 1 and 2 | Replace the imported shared hold table with a local empty literal. | `test_arm_readiness_evidence_author.ArmReadinessEvidenceAuthorTests.test_h_t1_new_issuance_is_held_at_arm` | **RED twice**, line 370: `True is not false` | Yes, both |
| Addendum loader gate | Delete the held-ID condition and its `return None`. | `test_claim_hold_routes.ClaimHoldRouteTests.test_hr3_manual_route_cannot_consume_held_file`; `.test_hr5_loader_opt_in_is_explicit` | **RED**, lines 139 and 168: preflight did not raise; loader returned the held artifact | Yes |
| Addendum default | Point both live default constants at the held 25G83 file. | `test_claim_hold_routes.ClaimHoldRouteTests.test_hr7_held_default_import_refuses` | **RED by import error**: `RuntimeError: the default calibration acceptance is claim-held` | Yes |
| Addendum doubling | Delete `and observation.content_id not in disposed_ids` from the valid-row count. | `test_calibration_bracketing.DoublingTriggerDispositionTests.test_dt1_one_new_valid_capture_does_not_double`; `.test_dt2_eleven_new_valid_captures_do_not_double` | **RED**, lines 3020 and 3025: doubling trigger unexpectedly present | Yes |
| Addendum P7 | Delete the issued input-seal STOP comparison. | `test_promote_calibration_candidate.PromotionTests.test_p7_issued_input_seal_drift_stops` | **RED**, line 109: expected STOP message, got `protected field changed: derivation_input_sha256` | Yes |
| R7 predecessor comparison, rounds 1 and 2 | Compare predecessor ID with `ACTIVE_ACCEPTANCE_ID` instead of `ANCHOR_V3_R7_ACCEPTANCE_ID`. | `test_acc_25g83_rev5.RevisionFiveTests.test_issuer_refuses_unsealed_launch_context_and_disposes_exact_ids` | **GREEN twice**, one test `OK` each run | Yes, both |
| R7 preparation default | Set `--predecessor-acceptance` default to `DEFAULT_ACCEPTANCE_BOUND_PATH`. | `test_acc_25g83_rev5.RevisionFiveTests.test_revision_five_predecessor_default_and_simulation_are_frozen_to_r7` | **GREEN**, one test `OK` | Yes |
| R7 epoch-check default | Set `--acceptance` default to `DEFAULT_ACCEPTANCE_BOUND_PATH`. | `test_epoch_equivalence_check.EpochEquivalenceCheckTest.test_cli_default_is_frozen_to_r7` | **GREEN**, one test `OK` | Yes |
| R7 simulation reference | Load `DEFAULT_ACCEPTANCE_BOUND_PATH` instead of the explicit R7 path. | `test_acc_25g83_rev5.RevisionFiveTests.test_revision_five_predecessor_default_and_simulation_are_frozen_to_r7` | **GREEN**, one test `OK` | Yes |

After restoration, the focused baseline ran **18 tests, all OK**. The detached head remained `8458f797`, and `git status --short --branch` showed no changes.

## Residual risk

L5 is red through a `KeyError`, not a failing assertion. P3 and P7 are red because a later guard changes the refusal message; those runs establish that the named guard was detected, but do not show that removing it would allow promotion.