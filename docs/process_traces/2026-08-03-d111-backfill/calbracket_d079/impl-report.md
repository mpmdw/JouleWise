```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented D-079 calibration acceptance v2 with a verified n=19 artifact, decimal-screen budgeting, freshness refusal, single-count allowance propagation, and defect-shaped regressions.",
  "workspace": {
    "base_requested": "a14d1fe",
    "base_mode": "exact",
    "head_start": "a14d1fe189734a9a58035736becb75612a85a157",
    "head_end": "a14d1fe189734a9a58035736becb75612a85a157",
    "upstream_end": "a14d1fe189734a9a58035736becb75612a85a157",
    "branch": "impl/cal-bracket-d079"
  },
  "pathspec": [
    "configs/calibration/calibration_acceptance_d079_v2.json",
    "joulewise/analysis_engine/claims.py",
    "joulewise/calibration_bracketing.py",
    "joulewise/whole_window.py",
    "tests/test_calibration_bracketing.py",
    "tests/test_whole_window_selection.py",
    "tests/verify_calibration_acceptance_corpus.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_calibration_bracketing.CalibrationBracketingTests.test_d079_budgeted_drift_above_obsolete_cliff_passes_with_allowance tests.test_calibration_bracketing.CalibrationBracketingTests.test_d079_drift_beyond_budget_refuses_with_recorded_basis tests.test_calibration_bracketing.CalibrationBracketingTests.test_t1_mismatched_candidate_remains_ineligible_under_d079_v2 tests.test_calibration_bracketing.CalibrationBracketingTests.test_identity_epoch_violation_refuses_stale_acceptance_bound",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FEEF",
          "Ran 4 tests in 0.001s",
          "FAILED (failures=2, errors=2)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=2, errors=2\\)"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python tests/verify_calibration_acceptance_corpus.py --repo-root /Users/edr/code/JouleWise --artifact configs/calibration/calibration_acceptance_d079_v2.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "n=19 min=0.022741007370546462 (20260722T215127-eeef661a)",
          "max=0.03355875667989999 (20260722T222332-901c5c13) range=0.010817749309353528",
          "mean=0.026950033977532761 sample_sd=0.002970761365307205",
          "PRIMARY_EVIDENCE_HASH_CROSSCHECK=OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PRIMARY_EVIDENCE_HASH_CROSSCHECK=OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_calibration_bracketing tests.test_whole_window_selection.MaxBracketConsumptionTests tests.test_d078_reason_registry",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 45 tests in 6.785s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 45 tests.*OK"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_calibration_bracketing tests.test_whole_window_selection tests.test_whole_window tests.test_analysis_integration tests.test_analysis_claims tests.test_floor_extraction tests.test_d078_reason_registry",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 314 tests in 33.902s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 314 tests.*OK"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_run_campaign tests.test_detection_floor tests.test_mint_floor_artifact tests.test_p2038_production_path",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 331 tests in 266.892s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 331 tests.*OK"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_nvidia_node_integration.NvidiaNodeIntegrationTests.test_generated_id_multi_rep_experiment_executes_cooldown tests.test_nvidia_node_integration.NvidiaNodeIntegrationTests.test_surviving_sampler_process_demotes_run_to_cleanup_failed",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 2 tests in 3.560s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2 tests.*OK"
      }
    },
    {
      "id": "V7",
      "kind": "suite",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 2426 tests in 572.404s",
          "OK (skipped=85)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2426 tests.*OK \\(skipped=85\\)"
      }
    },
    {
      "id": "V8",
      "kind": "lint",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -m json.tool configs/calibration/calibration_acceptance_d079_v2.json >/dev/null && shasum -a 256 configs/calibration/calibration_acceptance_d079_v2.json && git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "ade322ab485813c39dfb5f5ffb3c8bfe89c86d23b94a4d858238bf1b9af4e8f2  configs/calibration/calibration_acceptance_d079_v2.json"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "ade322ab485813c39dfb5f5ffb3c8bfe89c86d23b94a4d858238bf1b9af4e8f2"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "docs/contracts/powermetrics_fiducial.md still describes the superseded 0.010 hard comparator; D-102 was followed and documentation was explicitly outside WRITE_SCOPE.",
      "needs": "Lead should update the stale contract prose in a separately authorized bookkeeping change."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The first final-suite attempt encountered two unrelated NVIDIA fixture failures caused by stale deterministic custody directories left by prior test invocations. The exact test-owned directory was moved aside recoverably; both tests and the clean-state full suite then passed.",
      "needs": "Temporary backups under /private/tmp/joulewise-node-custody-stale.edusL6 and /private/tmp/joulewise-node-custody-stale.Hrw18Q may be discarded after review."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Cross-root corpus-doubling and estimator-byte-change triggers remain prospective operational events: the selector records all mandatory triggers, detects those visible in its supplied candidate set, checks protocol bytes, and binds estimator_revision, but it does not globally scan unrelated runs roots.",
      "needs": "Lead should confirm this matches the intended prospective re-derivation workflow."
    }
  ]
}
```

## Change

D-079 v2 is implemented without weakening candidate authentication, T1 exact matching, or latest-pre/earliest-post selection.

The selector now:

- Loads and hash-pins the n=19 D-102 artifact.
- Uses decimal comparisons for the `0.010818` screen, `0.001275166090593858` excess budget, `0.012093166090593858` ceiling, and `0.033558756679900` pre-flight screen.
- Refuses stale identity epochs as `calibration_acceptance_bound_stale`.
- Computes `A_s = max(drift, screen)` and embeds it once in `b_fiducial_s`.
- Records the artifact, decimal inputs, freshness, pre-flight result, budget result, triggers, allowance, and binary64 reducer-boundary conversion.
- Carries that record into the hashed whole-window evaluation basis and member consumption provenance.
- Consumes the widened operative bound through authenticated anchor-envelope re-reduction; no second calibration-drift energy term was added downstream.

The window-A regression still returns both endpoints null because its post-calibration power-policy binding is T1-incompatible.

## Verification notes

The required pre-fix redness was `FEEF`: the 11 ms case hit the obsolete hard refusal, the beyond-budget and T1 cases lacked an acceptance basis, and an OS-build epoch change incorrectly passed.

All 19 artifact rows were re-read from primary evidence, including both hashes and source decimal lexemes. Every mandated banked statistic matched exactly.

D-102 correctly superseded D-079’s coarser presentation values and the still-stale contract’s `0.010` hard-cliff wording. The prompt’s numeric pins did not conflict with D-102.

## Residual risk

The lead should independently spot-check the artifact’s pinned SHA and the single-count provenance validator, then perform the normal final diff audit. No commit was created.