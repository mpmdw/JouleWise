```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Completed and verified the in-scope fixes; B1/B2, S3, S10, and NIT-3 require unlisted source or governed-artifact scope.",
  "workspace": {
    "base_requested": "1ec5dc4",
    "base_mode": "exact",
    "head_start": "1ec5dc4f79e3c197bc4f2a567a2a45e275bd5851",
    "head_end": "1ec5dc4f79e3c197bc4f2a567a2a45e275bd5851",
    "upstream_end": "1ec5dc4f79e3c197bc4f2a567a2a45e275bd5851",
    "branch": "impl/r2-s0-mint-resolver"
  },
  "pathspec": [
    "docs/contracts/powermetrics_fiducial.md",
    "joulewise/calibration_bracketing.py",
    "joulewise/cli.py",
    "scripts/floor_mint_pinsets/schema_v2.json",
    "tests/test_analysis_engine.py",
    "tests/test_calibration_bracketing.py",
    "tests/test_capture_pipeline_era.py",
    "tests/test_environment_admission.py",
    "tests/test_floor_extraction.py",
    "tests/test_p2038_production_path.py",
    "tests/test_powermetrics.py",
    "tests/test_run_campaign.py"
  ],
  "unowned_dirty": [],
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
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 131 tests in 406.416s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_run_campaign",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 257 tests in 140.589s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_powermetrics_fiducial",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 75 tests in 51.907s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_calibration_exits",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 31 tests in 337.586s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_floor_mint_estimator",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 37 tests in 2.231s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_whole_window_selection",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 57 tests in 139.753s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V7",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_whole_window",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 56 tests in 0.436s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V8",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_p2038_production_path",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 8 tests in 223.839s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V9",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_powermetrics",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 61 tests in 11.092s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V10",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_calibration_bracketing",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 48 tests in 0.091s", "OK (skipped=1)"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V11",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_environment_admission",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 2 tests in 0.188s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V12",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_floor_extraction",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 161 tests in 2.571s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V13",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_analysis_engine",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 13 tests in 0.031s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V14",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_capture_pipeline_era",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 9 tests in 2.345s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V15",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "B1 mutation proof and B2's four-site absent-reason registry need unlisted analysis/floor/whole-window source and the whole-window regression file.",
      "needs": "Grant the listed scope expansion."
    },
    {
      "id": "F2",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "S3's v3 relabelled-capture attack reaches instrument_calibration_stale before event-time disagreement; correcting that taxonomy requires reduce.py. S10 requires controller ordering so post-run environment evidence exists before stored reduction.",
      "needs": "Grant the listed scope expansion."
    },
    {
      "id": "F3",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NIT-3's shared native-method constant invalidates the governed n17-r5 estimator hash. I reverted that otherwise-local refactor rather than mutate the acceptance artifact.",
      "needs": "Authorize reissue of the exact governed artifact or waive/defer NIT-3."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "joulewise/analysis_engine/inputs.py",
      "joulewise/floor_extraction.py",
      "joulewise/whole_window.py",
      "tests/test_whole_window_selection.py",
      "joulewise/reduce.py",
      "joulewise/controller.py",
      "configs/calibration/calibration_acceptance_d079_v2_n17_r5.json"
    ],
    "reason": "Required respectively for B1 mutation proof/B2 registries and lane test, S3 refusal ordering, S10 post-run evidence ordering, and NIT-3's governed estimator hash.",
    "blocked_work": "B1 mutation proofs; B2 capture_pipeline_absent; S3 v3 attack; S10 campaign-positive fixture; NIT-3 constant.",
    "minimal_change": "Register absent at the remaining two consumers and test it; split calibration event-time invalidity from stale age; record post-run admission before reduction; reissue only n17-r5 estimator/derivation pins."
  }
}
```

## Change

Implemented the independent fixes: r5 schema acceptance, fiducial binding wording, strict both-missing era refusal, dead CLI parameter removal, calibration diagnostics outside the governed artifact, active-era allowlist with v1 regression, real v2→v3 environment reconstruction, v2 strict-retention assertion, floor/analysis v2 lane regressions, and powermetrics test corrections.

For S4, reproduced the `8018a4b` strict failure as a fresh-reduction mismatch: stored prechecks omitted `environment_admission_missing`. The existing stored-method environment-anchor dispatch hunk makes replay agree; the regression now proves strict validity while the attempt-2 file is absent and still rejected by the whole-window admission verdict.

## Verification notes

B1 mutation proofs, B2, S3, S10, and NIT-3 were not attempted out of scope. NIT-7 was skipped as directed.

## Residual risk

The current tree remains unable to refuse absent capture-pipeline evidence in every consumer lane until the requested scope is granted.