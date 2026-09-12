```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "One D-109 blocker remains: the new guard breaks legitimate minted consumers while implicit minted rows still bypass it; B2 and S1 repairs hold.",
  "workspace": {
    "base_requested": "83831134492d463bc7dc7408a7162ee39a07692e",
    "base_mode": "exact",
    "head_start": "2e61ff96ea80186efa71efb9c9f6f00a16a70019",
    "head_end": "2e61ff96ea80186efa71efb9c9f6f00a16a70019",
    "upstream_end": null,
    "branch": "impl/cal-bracket-d079"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "B1",
        "severity": "blocker",
        "clauses": ["D-109 R1.2", "D-109 R1.4"],
        "title": "The minted verifier checks readiness before preparation and does not cover implicit minted semantics",
        "evidence": [
          "joulewise/whole_window.py:3567",
          "joulewise/whole_window.py:3468",
          "joulewise/whole_window.py:4073",
          "joulewise/floor_extraction.py:1616",
          "joulewise/floor_extraction.py:1877",
          "scripts/mint_floor_artifact.py:520",
          "scripts/mint_floor_artifact.py:529",
          "joulewise/analysis_engine/inputs.py:2815",
          "joulewise/analysis_engine/inputs.py:2820",
          "tests/test_whole_window_selection.py:1055"
        ]
      }
    ],
    "audit": [
      {
        "question": "B1",
        "result": "Partial only: a manually prepared minted session refuses pending and accepts a valid snapshot, and an explicit minted row refuses a missing session. Normal fresh minted sessions are rejected before their established preparation seam, while semantics-absent rows that normalize to minted still reach the uncached verifier without a session."
      },
      {
        "question": "B2 / D-109 R2.6",
        "result": "Closed: abandoned remains the immutable writer disposition, maps only to R2 unresolved, and new content-bearing and contentless abandoned observations refuse. The unchanged atexit writer hashes whatever custody exists; failed finalization leaves pending, partial finalization produces a null-content unresolved observation, and complete primary bytes produce a content-bearing unresolved observation."
      },
      {
        "question": "S1 fences",
        "result": "Closed: caller-root enumeration, omitted prior subtraction, and 38-new-only mutants each failed their rewritten test. Removing only predecessor checking from the sibling-fork parser eliminates chain_conflict while leaving pending, and the fence specifically requires chain_conflict."
      },
      {
        "question": "Scope",
        "result": "Exactly the declared six files changed; diff SHA-256 is eeccea3e0436dad024e3060c0598e3fbd54e8ee66577b0b692ad80903e94b867. validate_powermetrics_fiducial.py is untouched. No whitespace errors or dirty paths were observed."
      },
      {
        "question": "Preserved D-109 clauses",
        "result": "Aside from B1, spot checks retained reservation-first ordering, sequence/predecessor/digest chaining, committed-head/baseline refusal predicates, total-38 counting, prior-set subtraction, F1 six-field epoch, F2 exact four-module digest closure, T1/candidate authentication, Window-A refusal and budget boundaries."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_calibration_bracketing.CalibrationBracketingTests.test_unissued_fixture_cannot_license_default_claim_evaluation tests.test_calibration_bracketing.CalibrationBracketingTests.test_d079_budgeted_drift_above_obsolete_cliff_passes_with_allowance tests.test_calibration_bracketing.CalibrationBracketingTests.test_d079_drift_beyond_budget_refuses_with_recorded_basis tests.test_calibration_bracketing.CalibrationBracketingTests.test_t1_mismatched_candidate_remains_ineligible_under_d079_v2 tests.test_calibration_bracketing.CalibrationBracketingTests.test_window_a_t1_mismatch_shape_still_cannot_form_bracket tests.test_calibration_bracketing.CalibrationBracketingTests.test_unselected_same_identity_range_expander_stales_artifact tests.test_calibration_bracketing.CalibrationBracketingTests.test_off_ledger_candidate_refuses_even_beside_registered_pair tests.test_calibration_bracketing.CalibrationBracketingTests.test_prior_set_subtraction_does_not_treat_known_holdout_as_new tests.test_calibration_bracketing.CalibrationBracketingTests.test_corpus_doubling_counts_38_total_valid_distinct_observations tests.test_calibration_bracketing.CalibrationBracketingTests.test_new_abandoned_observation_refuses_with_or_without_content",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 10 tests in 0.009s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 10 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -c \"read-only minted-session control-flow probe using a valid CalibrationLedgerSnapshot and mocked _validate_row_uncached\"",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "explicit-valid-unprepared (False, ('whole_window_verdict_provenance_invalid',)) uncached 0",
          "implicit-minted-missing d078_minted_envelopes_v1 (True, ()) uncached 1"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "explicit-valid-unprepared \\(True, \\(\\)\\).*uncached 1.*implicit-minted-missing.*\\(False,"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -c \"compile the six changed Python files from read-only source bytes\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["COMPILE_OK 6"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "COMPILE_OK 6"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "shasum -a 256 configs/calibration/calibration_acceptance_d079_v2.json joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/adapters/powermetrics.py joulewise/reduce.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "9a264c57fdc007de473872870f19a5e1c9bd9b11256c25266b0e3e50ebba0ceb  configs/calibration/calibration_acceptance_d079_v2.json",
          "5118849dda9dcb36b4f3c5fa66f017676c6c416bc40622a2fd63052f31114615  joulewise/reduce.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "5118849dda9dcb36b4f3c5fa66f017676c6c416bc40622a2fd63052f31114615  joulewise/reduce.py"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_whole_window_selection.MaxBracketConsumptionTests.test_minted_semantics_loads_and_refuses_pending_ledger_snapshot tests.test_whole_window_selection.MaxBracketConsumptionTests.test_minted_secondary_verifier_refuses_missing_session tests.test_calibration_ledger.CalibrationLedgerTests.test_true_sibling_fork_refuses_on_predecessor_conflict tests.test_calibration_ledger.CalibrationLedgerTests.test_content_bearing_abandoned_receipt_is_unresolved_evidence",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FileNotFoundError: No usable temporary directory found"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 4 tests.*OK"
      }
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 1354 tests in 18.482s", "FAILED (errors=671, skipped=77)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Filesystem-backed focused tests and the canonical suite were dominated by FileNotFoundError because the sandbox has no writable temporary directory.",
      "needs": "After repairing B1, replay V5 and V6 with a writable TMPDIR."
    }
  ]
}
```

## Findings

B1 — blocker: the repair’s readiness check sits on the wrong side of session preparation.

A newly constructed minted session has a valid ledger snapshot but is not `ready` until `_validate_row_uncached()` reaches `_current_core_rederivation_reasons()` and calls `_prepare()` at `joulewise/whole_window.py:3468`. The new early return at lines 4073–4083 runs first, so legitimate production consumers in floor extraction, floor minting, and analysis input loading reject valid minted rows without ever attempting preparation.

The read-only probe showed:

- Explicit minted row + valid but fresh/unprepared session → provenance-invalid; uncached verifier called zero times.
- Implicit minted row + missing session → accepted by the mocked uncached verifier.

The second result occurs because `_row_consumption_semantics_id()` defaults a missing declaration to `d078_minted_envelopes_v1`, while the new guard compares only the raw declaration. Consequently, the fix is simultaneously fail-closed for the legitimate explicit path and still fail-open for implicit/default minted rows.

The new tests miss this interaction: the pending-snapshot test manually invokes `_prepare()` before asserting, and the secondary-verifier test covers only an explicitly declared minted row with no session.

## Residual risk

The B2 writer-to-receipt-to-evaluator story and all four S1 mutants were covered read-only, but filesystem-backed regressions and the full suite require replay with writable temporary storage.