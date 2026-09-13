```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "D-109 combined CAL-BRACKET implementation is complete and fully verified, but the sandbox prevented creating the requested commit.",
  "workspace": {
    "base_requested": "impl/cal-bracket-d079",
    "base_mode": "exact",
    "head_start": "a14d1fe189734a9a58035736becb75612a85a157",
    "head_end": "a14d1fe189734a9a58035736becb75612a85a157",
    "upstream_end": null,
    "branch": "impl/cal-bracket-d079"
  },
  "pathspec": [
    "joulewise/calibration_ledger.py",
    "joulewise/calibration_bracketing.py",
    "joulewise/whole_window.py",
    "joulewise/floor_extraction.py",
    "joulewise/analysis_engine/claims.py",
    "joulewise/analysis_engine/inputs.py",
    "scripts/validate_powermetrics_fiducial.py",
    "scripts/run_campaign.py",
    "scripts/mint_floor_artifact.py",
    "scripts/calibration_ledger_backfill.py",
    "configs/calibration/calibration_acceptance_d079_v2.json",
    "configs/calibration/calibration_ledger_head.json",
    "tests/test_calibration_ledger.py",
    "tests/test_calibration_bracketing.py",
    "tests/test_reduce.py",
    "tests/test_whole_window_selection.py",
    "tests/verify_calibration_acceptance_corpus.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_calibration_ledger tests.test_calibration_bracketing tests.test_whole_window_selection tests.test_reduce -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 205 tests in 99.601s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 205 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 2449 tests in 644.082s",
          "OK (skipped=85)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2449 tests in .*s\\n\\nOK \\(skipped=85\\)"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 tests/verify_calibration_acceptance_corpus.py --repo-root /Users/edr/code/JouleWise --artifact configs/calibration/calibration_acceptance_d079_v2.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
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
      "id": "V4",
      "kind": "other",
      "cmd": "git add -- joulewise/calibration_ledger.py joulewise/calibration_bracketing.py joulewise/whole_window.py joulewise/floor_extraction.py joulewise/analysis_engine/claims.py joulewise/analysis_engine/inputs.py scripts/validate_powermetrics_fiducial.py scripts/run_campaign.py scripts/mint_floor_artifact.py scripts/calibration_ledger_backfill.py configs/calibration/calibration_acceptance_d079_v2.json configs/calibration/calibration_ledger_head.json tests/test_calibration_ledger.py tests/test_calibration_bracketing.py tests/test_reduce.py tests/test_whole_window_selection.py tests/verify_calibration_acceptance_corpus.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 128,
        "tail": [
          "fatal: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/calbracket/index.lock': Operation not permitted"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": ""
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "blocking",
      "text": "The linked worktree Git index is outside the writable sandbox, so staging and the required single commit could not be created.",
      "needs": "Run V4 with Git-index write access, then commit with a message citing D-109."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "The checked-in acceptance artifact remains explicitly schema_fixture_unissued and cannot license production claims.",
      "needs": "Lead performs the reserved raw-physics/hash verification and production issuance."
    }
  ]
}
```

## Change

Implemented all D-109 R1/R2 clauses in code: reservation-first immutable ledger receipts, anti-rollback head pinning, ledger-only evaluation, single-snapshot threading, prior-set trigger semantics, 38-total counting, F1/F2, backfill tooling, and defect-shaped regressions. No D-109 implementation clause was silently narrowed.

## Verification notes

Focused: 205 tests passed. Full suite: 2,449 tests run, zero failures/errors, 85 expected skips. Corpus primary-byte verification also passed.

The sole incomplete deliverable is the commit. With Git metadata write access, rerun V4 and then:

```bash
git commit -m "Implement D-109 calibration ledger and bracket acceptance"
```

## Residual risk

Production acceptance issuance remains correctly lead-gated; the fixture is explicitly unratified and fail-closed.