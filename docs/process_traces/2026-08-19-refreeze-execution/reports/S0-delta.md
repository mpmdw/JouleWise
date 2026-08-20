```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "S0 delta audit is clean: all requested fixes land, with only the expected stale-golden and known whole-window reds.",
  "workspace": {
    "base_requested": "6771924",
    "base_mode": "exact",
    "head_start": "6771924ba244e91379ce76f3d59bdb54a52a920b",
    "head_end": "8018a4b47bdf9ae761e8924947ce4dd301b632f9",
    "upstream_end": "8018a4b47bdf9ae761e8924947ce4dd301b632f9",
    "branch": "detached HEAD (impl/r2-s0-mint-resolver)"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_floor_mint_estimator",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 37 tests", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 37 tests.*\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_calibration_bracketing",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 46 tests", "OK (skipped=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 46 tests.*OK \\(skipped=1\\)"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_detection_floor",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 159 tests", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 159 tests.*OK"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_mint_policy_resolver_guard",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test.*OK"
      }
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_mint_floor_artifact_generalized",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (failures=7, errors=6, skipped=2)"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=7, errors=6, skipped=2\\)"
      }
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_whole_window_selection",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (failures=1)"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=1\\)"
      }
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests.test_v2_postcollection_uses_the_declared_n19_acceptance_policy",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test.*OK"
      }
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "temporary in-memory revert of synthetic_v2_fixture acceptance_id threading",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "TypeError: _v2_postcollection() missing 1 required keyword-only argument: 'acceptance_id'",
          "RESTORED_WORKTREE=clean"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "missing 1 required keyword-only argument.*RESTORED_WORKTREE=clean"
      }
    },
    {
      "id": "V9",
      "kind": "inspection",
      "cmd": "read-only inline invariant probe for B1/B2/S2/S3/N4/N5/F4 and scope",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "GOLDEN_BLOCK_IDENTICAL sha256=0e4da6a75d2c99451d7c91adf2f940f5b05ea3d1c40f09b0e3d9cc3990cc99f9",
          "F4_DIFF_CHECK pass eof_blank=false",
          "SCOPE_EXACT files=7"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "SCOPE_EXACT files=7"
      }
    },
    {
      "id": "V10",
      "kind": "lint",
      "cmd": "git diff --check 6771924..8018a4b",
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
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "All 13 generalized-suite reds are the stale-golden chain: 6 producer-pin/hash errors plus 7 dependent assertion failures.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Whole-window retains exactly the known embeds_allowance_once failure; canonical discovery was not part of this focused delta audit.",
      "needs": ""
    }
  ]
}
```

## Findings

No blocker, should-fix, or nit findings.

## Residual risk

- Generalized reds: six named errors plus `test_aggregate_and_component_hash_mismatches_refuse` and six mutation subtests (`acceptance`, `binding`, `verdict-basis`, `member-bytes`, `report-bytes`, `ledger-head`); all stop on stale producer hashes.
- Whole-window: only `test_d079_real_selector_to_real_reducer_embeds_allowance_once` is red.