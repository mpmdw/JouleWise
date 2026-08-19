```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "B1/B2/S3/S10/NIT-3 and science-neutral D-079 r6 are implemented and verified; two unscoped test updates block full-suite closure.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "1ec5dc4f79e3c197bc4f2a567a2a45e275bd5851",
    "head_end": "1ec5dc4f79e3c197bc4f2a567a2a45e275bd5851",
    "upstream_end": "1ec5dc4f79e3c197bc4f2a567a2a45e275bd5851",
    "branch": "impl/r2-s0-mint-resolver"
  },
  "pathspec": [
    "configs/calibration/calibration_acceptance_d079_v2_n17_r6.json",
    "joulewise/analysis_engine/claims.py",
    "joulewise/arm_readiness.py",
    "joulewise/calibration_bracketing.py",
    "joulewise/controller.py",
    "joulewise/floor_extraction.py",
    "joulewise/reduce.py",
    "joulewise/uncertainty_evidence.py",
    "joulewise/whole_window.py",
    "scripts/floor_mint_pinsets/schema_v2.json",
    "tests/test_analysis_engine.py",
    "tests/test_calibration_exits.py",
    "tests/test_calibration_writer_crash_matrix.py",
    "tests/test_capture_pipeline_era.py",
    "tests/test_floor_extraction.py",
    "tests/test_p2038_production_path.py",
    "tests/test_powermetrics_fiducial.py",
    "tests/test_reduce.py",
    "tests/test_run_campaign.py",
    "tests/test_whole_window_selection.py",
    "tests/verify_calibration_acceptance_corpus.py"
  ],
  "unowned_dirty": [
    "docs/contracts/powermetrics_fiducial.md",
    "joulewise/cli.py",
    "tests/test_calibration_bracketing.py",
    "tests/test_environment_admission.py",
    "tests/test_powermetrics.py"
  ],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_reduce",
      "cwd": ".",
      "observed": { "result": "pass", "exit_code": 0, "tail": ["Ran 131 tests in 473.767s", "OK"] },
      "expected": { "exit_code": 0, "tail_regex": "Ran 131 tests.*OK" }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_run_campaign",
      "cwd": ".",
      "observed": { "result": "pass", "exit_code": 0, "tail": ["Ran 257 tests in 153.321s", "OK"] },
      "expected": { "exit_code": 0, "tail_regex": "Ran 257 tests.*OK" }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_powermetrics_fiducial",
      "cwd": ".",
      "observed": { "result": "pass", "exit_code": 0, "tail": ["Ran 75 tests in 51.557s", "OK"] },
      "expected": { "exit_code": 0, "tail_regex": "Ran 75 tests.*OK" }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_calibration_exits",
      "cwd": ".",
      "observed": { "result": "pass", "exit_code": 0, "tail": ["Ran 31 tests in 338.857s", "OK"] },
      "expected": { "exit_code": 0, "tail_regex": "Ran 31 tests.*OK" }
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_floor_mint_pinsets",
      "cwd": ".",
      "observed": { "result": "pass", "exit_code": 0, "tail": ["Ran 37 tests in 2.272s", "OK"] },
      "expected": { "exit_code": 0, "tail_regex": "Ran 37 tests.*OK" }
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_whole_window_selection",
      "cwd": ".",
      "observed": { "result": "pass", "exit_code": 0, "tail": ["Ran 57 tests in 153.013s", "OK"] },
      "expected": { "exit_code": 0, "tail_regex": "Ran 57 tests.*OK" }
    },
    {
      "id": "V7",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_whole_window",
      "cwd": ".",
      "observed": { "result": "fail", "exit_code": 1, "tail": ["Ran 56 tests in 0.410s", "FAILED (failures=6, errors=2)"] },
      "expected": { "exit_code": 0, "tail_regex": "Ran 56 tests.*OK" }
    },
    {
      "id": "V8",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_p2038_production_path",
      "cwd": ".",
      "observed": { "result": "pass", "exit_code": 0, "tail": ["Ran 8 tests in 226.005s", "OK"] },
      "expected": { "exit_code": 0, "tail_regex": "Ran 8 tests.*OK" }
    },
    {
      "id": "V9",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_powermetrics",
      "cwd": ".",
      "observed": { "result": "pass", "exit_code": 0, "tail": ["Ran 61 tests in 11.157s", "OK"] },
      "expected": { "exit_code": 0, "tail_regex": "Ran 61 tests.*OK" }
    },
    {
      "id": "V10",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_calibration_bracketing",
      "cwd": ".",
      "observed": { "result": "fail", "exit_code": 1, "tail": ["Ran 48 tests in 0.091s", "FAILED (failures=1, skipped=1)"] },
      "expected": { "exit_code": 0, "tail_regex": "Ran 48 tests.*OK" }
    },
    {
      "id": "V11",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_environment_admission",
      "cwd": ".",
      "observed": { "result": "pass", "exit_code": 0, "tail": ["Ran 2 tests", "OK"] },
      "expected": { "exit_code": 0, "tail_regex": "Ran 2 tests.*OK" }
    },
    {
      "id": "V12",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_floor_extraction",
      "cwd": ".",
      "observed": { "result": "pass", "exit_code": 0, "tail": ["Ran 162 tests in 2.851s", "OK"] },
      "expected": { "exit_code": 0, "tail_regex": "Ran 162 tests.*OK" }
    },
    {
      "id": "V13",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_analysis_engine tests.test_capture_pipeline_era",
      "cwd": ".",
      "observed": { "result": "pass", "exit_code": 0, "tail": ["Ran 23 tests in 2.343s", "OK"] },
      "expected": { "exit_code": 0, "tail_regex": "Ran 23 tests.*OK" }
    },
    {
      "id": "V14",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_calibration_writer_crash_matrix",
      "cwd": ".",
      "observed": { "result": "pass", "exit_code": 0, "tail": ["Ran 15 tests in 643.065s", "OK"] },
      "expected": { "exit_code": 0, "tail_regex": "Ran 15 tests.*OK" }
    },
    {
      "id": "R6-BUILD",
      "kind": "build",
      "cmd": "python3 $TMPDIR/r6-issuance/build_r6.py",
      "cwd": ".",
      "observed": { "result": "pass", "exit_code": 0, "tail": ["FILE_SHA256 0227bca3f826edc7f0a1baf98a394df01d8f48e9609966088870d712f765697d", "PIN_MOVED reduce.py", "PIN_MOVED uncertainty_evidence.py"] },
      "expected": { "exit_code": 0, "tail_regex": "FILE_SHA256 0227bca.*PIN_MOVED" }
    },
    {
      "id": "R6-NEUTRALITY",
      "kind": "inspection",
      "cmd": "python3 $TMPDIR/r6-issuance/prove_r6_neutrality.py",
      "cwd": ".",
      "observed": { "result": "pass", "exit_code": 0, "tail": ["MEMBERS 19", "MISMATCHES 0"] },
      "expected": { "exit_code": 0, "tail_regex": "MEMBERS 19.*MISMATCHES 0" }
    },
    {
      "id": "R6-CORPUS",
      "kind": "test",
      "cmd": "python3 tests/verify_calibration_acceptance_corpus.py --repo-root /Users/edr/code/JouleWise --artifact \"$PWD/configs/calibration/calibration_acceptance_d079_v2_n17_r6.json\"",
      "cwd": ".",
      "observed": { "result": "pass", "exit_code": 0, "tail": ["acceptance_id=d079_calibration_acceptance_v2_n17_r6 stored_lexeme_is_member_value=False", "PRIMARY_EVIDENCE_HASH_CROSSCHECK=OK"] },
      "expected": { "exit_code": 0, "tail_regex": "r6.*PRIMARY_EVIDENCE_HASH_CROSSCHECK=OK" }
    },
    {
      "id": "L1",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": { "result": "pass", "exit_code": 0, "tail": [] },
      "expected": { "exit_code": 0, "tail_regex": "^$" }
    }
  ],
  "flags": [
    {
      "id": "SCOPE-1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "B2 makes the shared whole-window synthetic metadata correctly refuse as capture_pipeline_absent, and r6 makes one live-default assertion correctly stale; both affected tests are outside WRITE_SCOPE.",
      "needs": "Grant the two-path scope expansion below, then rerun V7 and V10."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "tests/test_whole_window.py",
      "tests/test_calibration_bracketing.py"
    ],
    "reason": "Update the shared synthetic whole-window fixture to present an active v3 capture anchor, and rebind the live-default test literal from r5 to r6.",
    "blocked_work": "V7 and V10 cannot pass without these fixture/literal updates.",
    "minimal_change": "Add current V3 anchor presentation to the former test's fixture; replace the latter test's three r5 default assertions/imports with r6 while retaining r5 registry-history coverage."
  }
}
```

## Change

Implemented positive capture-pipeline presentation and additive `capture_pipeline_absent` handling in claims, whole-window, and floor lanes. Added independent lane regressions and restored the native-anchor constant hoist.

S3 now reports `instrument_calibration_capture_time_mismatch` before calibration staleness for the relabelled v3 capture-time attack; its control arm remains stale. S10 records post-run environment/admission evidence before stored reduction, allowing the strict campaign-positive v3 fixture to pass while preserving v2 refusal coverage.

Issued D-079 r6 with only `reduce.py` and `uncertainty_evidence.py` pin moves. r6 SHA is `0227bca3f826edc7f0a1baf98a394df01d8f48e9609966088870d712f765697d`; r5 remains registered history.

## Verification notes

Barrier mutation proofs were performed and restored:

- Floor lane: removing its local barrier made `test_v2_anchor_member_refuses_capture_pipeline_superseded` fail because the superseded refusal vanished.
- Window-precheck lane: removing its local barrier made the presentation test fail with only `campaign_cooldown_evidence_missing`.
- Whole-window lane: removing its local barrier made both expected presentation refusals vanish.

The r6 replay artifacts are in `$TMPDIR/r6-issuance/`; replay of the r4 derivation record (`ad923506…`) reported 19 members and zero mismatches.

V7 requires the unscoped fixture anchor update. V10 requires the unscoped r6 live-default literal update. No commit was created; all source and r6 changes remain together in the working tree.