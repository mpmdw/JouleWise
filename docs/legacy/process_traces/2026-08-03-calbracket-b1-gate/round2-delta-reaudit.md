```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "B1 is closed in both placement and normalization dimensions at c2f81d4; regressions, mutants, fixture audit, focused checks, and the 2456-test canonical suite all pass.",
  "workspace": {
    "base_requested": "c2f81d48e55d7c19709cc740640001b351237aa1",
    "base_mode": "exact",
    "head_start": "c2f81d48e55d7c19709cc740640001b351237aa1",
    "head_end": "c2f81d48e55d7c19709cc740640001b351237aa1",
    "upstream_end": null,
    "branch": "impl/cal-bracket-d079"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [],
    "b1": {
      "status": "CLOSED",
      "dynamic_probe": [
        "explicit minted + fresh valid snapshot: reasons=(), prepared=True, ready=True",
        "implicit/undeclared + None session: whole_window_verdict_provenance_invalid",
        "pending snapshot + fresh session: calibration_ledger_pending present, prepared=True, ready=False, supplied snapshot identity retained"
      ],
      "evidence": [
        "joulewise/whole_window.py:4064",
        "joulewise/whole_window.py:4098",
        "joulewise/whole_window.py:4132",
        "joulewise/whole_window.py:4320",
        "joulewise/whole_window.py:4333",
        "joulewise/whole_window.py:4358"
      ]
    },
    "ruled_shape": {
      "status": "PASS",
      "details": [
        "The round-1 preflight guard was deleted rather than relocated or shadowed.",
        "Minted enforcement uses normalized row_semantics after _current_core_rederivation_reasons.",
        "The minted clause tests only absent/unready session; basis=None is accepted by R1.",
        "No row-semantics/session-semantics equality requirement was introduced; R1 accepts an explicit minted row with the default-constructed session.",
        "No repair-side consumer _prepare call was added. scripts/run_campaign.py:5220 is the pre-existing direct-runner path expressly treated as conformant by both sealed rulings.",
        "The only raw declaration consistency check on this path remains the pre-existing MAX_BRACKET/SALVAGE basis check at whole_window.py:4139-4147; minted readiness does not use it."
      ],
      "evidence": [
        "joulewise/whole_window.py:465",
        "joulewise/whole_window.py:487",
        "joulewise/whole_window.py:504",
        "joulewise/whole_window.py:3468",
        "joulewise/whole_window.py:4139",
        "joulewise/whole_window.py:4333",
        "scripts/run_campaign.py:5220"
      ]
    },
    "regression_contract": {
      "status": "PASS",
      "details": [
        "R1-R5 all enter through whole_window_refusal_reasons.",
        "AST audit found no _prepare, _validate_row, or _validate_row_uncached call in any R1-R5 test.",
        "Both round-1 test names remain and were rewritten.",
        "In-memory m1 early-placement mutant: Ran 5, FAILED (failures=2), killing R1 and R2.",
        "In-memory m2 raw-comparison mutant: Ran 5, FAILED (failures=1), killing R3."
      ],
      "evidence": [
        "tests/test_whole_window_selection.py:1122",
        "tests/test_whole_window_selection.py:1146",
        "tests/test_whole_window_selection.py:1177",
        "tests/test_whole_window_selection.py:1188",
        "tests/test_whole_window_selection.py:1200"
      ]
    },
    "snapshot_identity": {
      "status": "PASS",
      "details": [
        "Supplied snapshots bypass constructor loading and retain object identity.",
        "floor_extraction uses one session for primary verification, member consumption, and allowance pass.",
        "mint_floor_artifact loads once and threads the same object through both component authentications, allowance re-derivation, and post-bind.",
        "analysis inputs load once, pass the same object into floor binding and the analysis session, then reuse that session for allowances and secondary passes."
      ],
      "evidence": [
        "joulewise/whole_window.py:412",
        "joulewise/whole_window.py:416",
        "joulewise/floor_extraction.py:1616",
        "joulewise/floor_extraction.py:1691",
        "scripts/mint_floor_artifact.py:1959",
        "scripts/mint_floor_artifact.py:1980",
        "scripts/mint_floor_artifact.py:2025",
        "joulewise/analysis_engine/inputs.py:2677",
        "joulewise/analysis_engine/inputs.py:2752",
        "joulewise/analysis_engine/inputs.py:2812",
        "joulewise/analysis_engine/inputs.py:2851"
      ]
    },
    "preserved_fences": {
      "status": "PASS",
      "details": [
        "Protected B2/S1, writer, ledger, bracketing, runner, F1/F2 and policy paths have zero diff from 2e61ff9.",
        "Constructor loading and _prepare snapshot refusal are unchanged.",
        "Reservation-first, chain/head pins, F1 six-field epoch, F2 four-module closure, T1, Window-A, prior-set subtraction, total-38 and budget fences passed focused checks."
      ],
      "evidence": [
        "joulewise/whole_window.py:416",
        "joulewise/whole_window.py:487",
        "tests/test_calibration_ledger.py:105",
        "tests/test_calibration_ledger.py:127",
        "tests/test_calibration_ledger.py:142",
        "tests/test_calibration_ledger.py:158",
        "tests/test_calibration_bracketing.py:291",
        "tests/test_calibration_bracketing.py:397",
        "tests/test_calibration_bracketing.py:416",
        "tests/test_calibration_bracketing.py:460",
        "tests/test_calibration_bracketing.py:477",
        "tests/test_calibration_bracketing.py:647",
        "tests/test_calibration_bracketing.py:667"
      ]
    },
    "fixture_audit": {
      "status": "PASS",
      "details": [
        "No assertion statement was removed from the three fixture files.",
        "Changed existing tests retained assertion counts: analysis 3->3 and 7->7; floor extraction 1->1 in each changed test.",
        "Changes supply prepared fixture sessions while preserving the original authentication, conflict, frozen-replay, incomplete-pair, and claim-consumption assertions.",
        "No production defect was hidden: the dedicated public-path R1-R5 tests independently cover the newly binding preparation behavior."
      ],
      "evidence": [
        "tests/test_analysis_integration.py:124",
        "tests/test_analysis_integration.py:517",
        "tests/test_analysis_integration.py:1271",
        "tests/test_analysis_integration.py:3500",
        "tests/test_floor_extraction.py:100",
        "tests/test_floor_extraction.py:988",
        "tests/test_floor_extraction.py:1076",
        "tests/test_floor_extraction.py:1397",
        "tests/test_floor_extraction.py:1527",
        "tests/test_whole_window.py:149"
      ]
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git rev-parse HEAD^ && git diff --check 2e61ff9..c2f81d4",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## impl/cal-bracket-d079",
          "c2f81d48e55d7c19709cc740640001b351237aa1",
          "2e61ff96ea80186efa71efb9c9f6f00a16a70019"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "c2f81d48e55d7c19709cc740640001b351237aa1.*2e61ff96ea80186efa71efb9c9f6f00a16a70019"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=/private/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_whole_window_selection.MaxBracketConsumptionTests.test_b1_r1_explicit_minted_fresh_valid_session_is_prepared_and_accepted tests.test_whole_window_selection.MaxBracketConsumptionTests.test_minted_semantics_loads_and_refuses_pending_ledger_snapshot tests.test_whole_window_selection.MaxBracketConsumptionTests.test_b1_r3_implicit_minted_without_session_is_refused tests.test_whole_window_selection.MaxBracketConsumptionTests.test_b1_r4_implicit_minted_fresh_valid_session_matches_explicit tests.test_whole_window_selection.MaxBracketConsumptionTests.test_minted_secondary_verifier_refuses_missing_session",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 5 tests in 0.041s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 5 tests.*OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=/private/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_calibration_ledger.CalibrationLedgerTests.test_crash_between_reservation_and_finalization_refuses tests.test_calibration_ledger.CalibrationLedgerTests.test_reservation_requires_complete_epoch_and_full_t1 tests.test_calibration_ledger.CalibrationLedgerTests.test_production_writer_reserves_before_capture_state_or_sampler tests.test_calibration_ledger.CalibrationLedgerTests.test_proper_prefix_of_pinned_head_refuses_as_rollback tests.test_calibration_ledger.CalibrationLedgerTests.test_unpinned_physical_extension_refuses_stale_head tests.test_calibration_ledger.CalibrationLedgerTests.test_true_sibling_fork_refuses_on_predecessor_conflict tests.test_calibration_ledger.CalibrationLedgerTests.test_finalization_is_single_transition tests.test_calibration_bracketing.CalibrationBracketingTests.test_f1_freshness_uses_six_field_epoch_not_full_t1 tests.test_calibration_bracketing.CalibrationBracketingTests.test_f2_estimator_digest_closure_is_exactly_four_modules",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 9 tests in 0.010s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 9 tests.*OK"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "TMPDIR=/private/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_analysis_integration tests.test_floor_extraction tests.test_whole_window tests.test_whole_window_selection",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 239 tests in 67.667s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 239 tests.*OK"
      }
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "TMPDIR=/private/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 2456 tests in 699.301s",
          "OK (skipped=85)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2456 tests.*OK \\(skipped=85\\)"
      }
    }
  ],
  "flags": []
}
```

## Findings

None. B1 is closed; the same-signature escalation trigger does not fire.

## Residual risk

None identified within the requested read-only audit scope. No repository files were modified and no `[QUIET-MAC]` activity was performed.