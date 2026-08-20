```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Resolved D-078 R-01 via the earlier v2-era invalidity refusal, pinned v3 stale-calibration behavior, and killed all 18 D-146 era mutations.",
  "workspace": {
    "base_requested": "b7e5730",
    "base_mode": "exact",
    "head_start": "b7e5730feccf221f1fd949c396f428c45d364751",
    "head_end": "b7e5730feccf221f1fd949c396f428c45d364751",
    "upstream_end": "b7e5730feccf221f1fd949c396f428c45d364751",
    "branch": "impl/r2-s0-mint-resolver"
  },
  "pathspec": [
    "tests/test_reduce.py",
    "tests/test_capture_pipeline_era.py"
  ],
  "unowned_dirty": [
    "tests/test_reduce.py",
    "tests/test_p2038_production_path.py",
    "tests/test_powermetrics_fiducial.py",
    "tests/test_run_campaign.py",
    "tests/test_whole_window_selection.py",
    "tests/fixtures/p2038_v3_production/"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_reduce -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 131 tests in 405.017s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran \\\\d+ tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_capture_pipeline_era -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 8 tests in 2.344s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran \\\\d+ tests.*OK"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_floor_mint_estimator -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 37 tests in 2.151s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 37 tests.*OK"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests.test_default_only_v2_output_remains_byte_identical_to_golden_oracle tests.test_mint_floor_artifact_generalized.GeneralizedMintTests.test_mint1_builder_path_is_byte_identical tests.test_mint_floor_artifact_generalized.FullPathTests.test_mint1_full_path_is_byte_identical_to_review_pinned_mint_core -v",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 3 tests in 0.485s",
          "FAILED (errors=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 3 tests.*OK"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The requested stale-golden chain is 2/3 passing; the legacy v2 golden-oracle case errors because its explicit pinset no longer matches the closed final pinset schema.",
      "needs": "Decide whether to refresh or rebind that stale v2 golden in a separately scoped follow-up."
    }
  ]
}
```

## Change

Took branch (a). The relabelled D-078 fixture remains `p2-038.1` / v2-era measurement evidence, while regenerated calibration uses current-v3 anchor physics. Direct verification returned `instrument_calibration_invalid` before the freshness check, so `test_052` now pins that era-consistent refusal with an explanatory comment.

Added a real v3 stale-only regression: a succeeded `p2-038.3` production measurement with calibration age `86498.05s` (`MAX_AGE_S + 98.05s`) directly verifies as `instrument_calibration_stale`. The full reducer’s refusal also contains `clock_anchor_unresolved`, as expected once stale calibration is unavailable, but the calibration verification itself is unambiguously stale.

Added five A9 kill tests for previously surviving mutations: unresolved v3 CLI fallback, empty capture, bracket rederivation, drain-probe method propagation, and r5 arm-readiness recognition.

The inherited working tree contains:

- `tests/test_p2038_production_path.py` plus `tests/fixtures/p2038_v3_production/`: real v3 production fixture, paired clock records, whole-window v3 conversion, and retained v2 negative coverage.
- `tests/test_whole_window_selection.py`: current-v3 selector/reducer path with matching calibration and retained v2 barrier refusal.
- `tests/test_powermetrics_fiducial.py`: legacy detector/fiducial fixture era repairs and corresponding frozen identity updates.
- `tests/test_run_campaign.py`: preflight-r5 strict-admission rebind.
- `tests/test_reduce.py`: predecessor `reducer_0_6_2`/anchor-fixture repairs plus this session’s D-078 adjudication and v3 stale pin.
- `tests/test_capture_pipeline_era.py`: this session’s five mutation-kill regressions.

A9 scratch-copy transcript; all source files were byte-identical to the workspace after the sweep:

- Adapter empty-capture method → `test_adapter_empty_capture_emits_the_active_v3_method`
- Adapter primary capture method → `PowermetricsAdapterTests.test_run_bundle_metadata_records_dropped_powermetrics_tail_diagnostic`
- Adapter bracket rederivation → `test_adapter_bracket_rederivation_emits_the_active_v3_method`
- Adapter drain probe → `test_adapter_drain_probe_emits_the_active_v3_method`
- CLI schema allowlist → `P2038ProductionPathTests.test_real_powermetrics_evidence_path_passes_p2029_p2040_gates`
- CLI schema/method pairing predicate → `test_crossed_schema_method_pairs_are_rejected`
- CLI stored-method resolver → `P2038ProductionPathTests.test_real_powermetrics_evidence_path_passes_p2029_p2040_gates`
- CLI fallback-era set → `P2038ProductionPathTests.test_real_path_exercises_fail_closed_gate_reasons_without_scalar_edits`
- CLI rich-telemetry endpoint set → `test_v3_unresolved_rich_telemetry_uses_its_fallback_endpoint`
- CLI rich-telemetry guard → `test_v3_corrupt_rich_telemetry_is_not_fail_open`
- `run_campaign` active-schema derivation → `ProductionUncertaintyAssertionTests.test_current_p2038_3_with_composed_margin_and_envelope_passes`
- `run_campaign` schema comparator → same test
- `run_campaign` active-method equality → same test
- Environment-admission resolver → `EnvironmentAdmissionAnchorEraTests.test_v3_stored_method_drives_thermal_window_reconstruction`
- Fiducial missing-method fail-closed branch → `AnchorMethodDispatchTests.test_evidence_author_refuses_absent_detection_method`
- Controller current-schema capture absence → `HappyPathTests.test_powermetrics_thermal_coverage_is_continuous_across_admission_handoff`
- Claim-barrier v3 method predicate → `test_claim_barrier_rejects_every_non_v3_stored_method`
- Arm-readiness r5 issued set → `test_arm_readiness_recognizes_the_r5_v3_acceptance_generation`

## Verification notes

The stale-golden chain ran 3 checks: 2 passed; `test_default_only_v2_output_remains_byte_identical_to_golden_oracle` errored with `MintError` because the explicit legacy pinset no longer matches the closed final pinset schema. No out-of-scope changes were made.