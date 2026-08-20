```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "S1 delta is clean; all requested S1 suites pass, with only the pre-existing S2 generalized-artifact chain red.",
  "workspace": {
    "base_requested": "1ec5dc4",
    "base_mode": "exact",
    "head_start": "1ec5dc4f79e3c197bc4f2a567a2a45e275bd5851",
    "head_end": "3038eeb693a15d2f6db80fb9da6dae1a52fb90d7",
    "upstream_end": "3038eeb693a15d2f6db80fb9da6dae1a52fb90d7",
    "branch": "HEAD (detached)"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": [],
    "scope": {
      "delta_files": 27,
      "unlicensed_hunks": 0
    },
    "suite_totals": {
      "s1_modules": 14,
      "s1_tests": 948,
      "s1_pass": 947,
      "s1_skipped": 1,
      "s2_tests": 76,
      "s2_pass": 61,
      "s2_failures": 7,
      "s2_errors": 6,
      "s2_skipped": 2
    },
    "checks": {
      "B1": "3/3 lane-barrier mutation deaths reproduced",
      "B2": "absent, malformed, crossed, and superseded presentations verified; four registry sites present",
      "SF-2": "attack line is load-bearing; removal fails the named test",
      "SF-3": "8018a4b fresh-reduction mismatch reproduced; current strict_valid passes while attempt 2 remains absent and rejected",
      "SF-6": "no candidate_discovery artifact key; verdict-conflict surfaces byte-stable",
      "SF-7": "v1/v2 observations classify as superseded; custody count remains balanced",
      "SF-9": "real-shaped v2 empty versus v3 bounded admission arm passes",
      "SF-10": "stored v2 strict-retention regression passes",
      "S10": "campaign-positive gate passes; emitted 24-file and JSON key sets match 1ec5dc4",
      "r6": "registry SHA 0227bca3; science leaves unchanged; four pins match head; neutrality 19/0",
      "NIT-2-5": "schema row and requested NIT regressions pass"
    }
  },
  "verification": [
    {"id":"V1","kind":"suite","cmd":"python3 -m unittest tests.test_reduce","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V2","kind":"suite","cmd":"python3 -m unittest tests.test_whole_window","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V3","kind":"suite","cmd":"python3 -m unittest tests.test_whole_window_selection","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V4","kind":"suite","cmd":"python3 -m unittest tests.test_run_campaign","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V5","kind":"suite","cmd":"python3 -m unittest tests.test_powermetrics_fiducial","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V6","kind":"suite","cmd":"python3 -m unittest tests.test_calibration_bracketing","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK (skipped=1)"]},"expected":{"exit_code":0,"tail_regex":"OK"}},
    {"id":"V7","kind":"suite","cmd":"python3 -m unittest tests.test_calibration_exits","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V8","kind":"suite","cmd":"python3 -m unittest tests.test_floor_extraction","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V9","kind":"suite","cmd":"python3 -m unittest tests.test_analysis_engine","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V10","kind":"suite","cmd":"python3 -m unittest tests.test_capture_pipeline_era","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V11","kind":"suite","cmd":"python3 -m unittest tests.test_p2038_production_path","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V12","kind":"suite","cmd":"python3 -m unittest tests.test_environment_admission","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V13","kind":"suite","cmd":"python3 -m unittest tests.test_powermetrics","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V14","kind":"suite","cmd":"python3 -m unittest tests.test_floor_mint_estimator","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V15","kind":"suite","cmd":"python3 -m unittest tests.test_mint_floor_artifact_generalized","cwd":".","observed":{"result":"fail","exit_code":1,"tail":["FAILED (failures=7, errors=6, skipped=2)"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V16","kind":"test","cmd":"python3 -m unittest tests.test_capture_pipeline_era.CapturePipelineEraTests.test_claim_barrier_distinguishes_absent_from_superseded_presentation tests.test_capture_pipeline_era.CapturePipelineEraTests.test_crossed_schema_method_pairs_refuse_before_rederivation","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V17","kind":"test","cmd":"python3 -m unittest tests.test_calibration_bracketing.CalibrationBracketingTests.test_v2_ledger_candidate_reports_era_rejection_not_custody_failure tests.test_calibration_bracketing.CalibrationBracketingTests.test_v1_ledger_candidate_reports_era_rejection_not_custody_failure","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V18","kind":"test","cmd":"python3 -m unittest tests.test_environment_admission.EnvironmentAdmissionAnchorEraTests.test_rate_aware_knife_edge_resolves_real_v3_shape","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V19","kind":"test","cmd":"python3 -m unittest tests.test_run_campaign.IdleAdmissionCoreVerdictTests.test_missing_final_attempt_telemetry_fails_closed","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V20","kind":"test","cmd":"python3 -m unittest tests.test_p2038_production_path.P2038ProductionPathTests.test_retained_v2_production_fixture_is_a_refusal_arm tests.test_p2038_production_path.P2038ProductionPathTests.test_real_powermetrics_evidence_path_passes_p2029_p2040_gates","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V21","kind":"test","cmd":"python3 -m unittest tests.test_whole_window.ProspectiveMemberFailureValidationTests.test_same_basis_legacy_and_enriched_rows_do_not_conflict","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["OK"]},"expected":{"exit_code":0,"tail_regex":"OK$"}},
    {"id":"V22","kind":"test","cmd":"python3 tests/verify_calibration_acceptance_corpus.py --repo-root /Users/edr/code/JouleWise --artifact \"$PWD/configs/calibration/calibration_acceptance_d079_v2_n17_r6.json\"","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["PRIMARY_EVIDENCE_HASH_CROSSCHECK=OK"]},"expected":{"exit_code":0,"tail_regex":"PRIMARY_EVIDENCE_HASH_CROSSCHECK=OK"}},
    {"id":"V23","kind":"inspection","cmd":"git diff --check 1ec5dc4..3038eeb","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}}
  ],
  "flags": [
    {"id":"S2-CHAIN","kind":"baseline_drift","level":"nonblocking","text":"The generalized mint-artifact suite has 7 failures, 6 errors, and 2 skips; the same red count reproduces at 1ec5dc4 and is caused by stale v2 producer pin/closed-pinset validation.","needs":""},
    {"id":"FIXTURE-ONLY","kind":"environment","level":"nonblocking","text":"S10 positive evidence is committed fixture/mock-runtime coverage, not live quiet-machine validation.","needs":""}
  ]
}
```

## Findings

None. The 27-file delta is covered by the granted fix scopes plus the two explicit lead bench edits.

Mutation evidence: all three B1 barrier removals caused their named tests to fail; removing the SF-2 attack line caused the attack/control distinction to disappear.

r6 authenticates at `0227bca3f826…`; r5 remains registered history. All four estimator pins match head bytes, the schema contains both r5 and r6, and the neutrality replay matched all 19 members with zero mismatches. Spot checks against r4 record `ad9235065df9…` matched.

## Residual risk

The only red suite is the pre-existing S2 generalized-artifact chain described in `S2-CHAIN`; it is not introduced by this S1 delta.