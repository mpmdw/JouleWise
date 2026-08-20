```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented and verified all in-scope S0 fixes except N4; commit and N4 are blocked by sandbox/write scope.",
  "workspace": {
    "base_requested": "6771924",
    "base_mode": "exact",
    "head_start": "6771924ba244e91379ce76f3d59bdb54a52a920b",
    "head_end": "6771924ba244e91379ce76f3d59bdb54a52a920b",
    "upstream_end": "6771924ba244e91379ce76f3d59bdb54a52a920b",
    "branch": "impl/r2-s0-mint-resolver"
  },
  "pathspec": [
    "joulewise/calibration_bracketing.py",
    "scripts/floor_mint_pinsets/schema_v2.json",
    "scripts/mint_floor_artifact_generalized.py",
    "tests/test_calibration_bracketing.py",
    "tests/test_mint_floor_artifact_generalized.py",
    "tests/test_mint_policy_resolver_guard.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests.test_v2_postcollection_uses_the_declared_n19_acceptance_policy",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["TypeError: _v2_postcollection() got an unexpected keyword argument 'acceptance_id'", "FAILED (errors=1)"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "unexpected keyword argument 'acceptance_id'"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_mint_floor_artifact_generalized.V2PinsetAndMintTests.test_v2_postcollection_uses_the_declared_n19_acceptance_policy",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 0.035s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test.*OK"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_calibration_bracketing",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 46 tests in 0.087s", "OK (skipped=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 46 tests.*OK \\(skipped=1\\)"
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
        "tail": ["Ran 1 test in 0.001s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_floor_mint_estimator",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 37 tests in 2.125s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 37 tests.*OK"
      }
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_mint_floor_artifact_generalized",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 76 tests in 16.168s", "FAILED (failures=7, errors=6, skipped=2)"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=7, errors=6, skipped=2\\)"
      }
    },
    {
      "id": "V7",
      "kind": "smoke",
      "cmd": "inline Python resolver poisoning/crosswire probe",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "OPERATIVES_TYPE=mappingproxy",
          "POISON_ATTEMPT=TypeError: 'mappingproxy' object does not support item assignment",
          "CROSSWIRE_REFUSAL=ValueError: supplied acceptance operatives disagree with the registered generation: bracket_screen_s '0.010818' disagrees with registered bracket_screen_s '0.009724' for acceptance_id 'd079_calibration_acceptance_v2_n17_r4'"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OPERATIVES_TYPE=mappingproxy.*CROSSWIRE_REFUSAL=ValueError"
      }
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "python3 -m json.tool scripts/floor_mint_pinsets/schema_v2.json >/dev/null && git diff --check",
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
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "NEEDS_RULING: N4 is in joulewise/floor_mint_estimator.py:148, but that file is explicitly outside WRITE_SCOPE. It still accepts an empty string while its message says nonempty.",
      "needs": "Approve the scope expansion below or waive N4 for this round."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "blocking",
      "text": "Requested commit failed: Git needs /Users/edr/code/JouleWise/.git/worktrees/wtS0/index.lock, outside writable roots (Operation not permitted). No commit was created.",
      "needs": "Commit from a host-authorized environment or provide writable Git metadata access."
    },
    {
      "id": "F3",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "All 13 generalized-suite reds are the stale-golden chain: six producer-pin mismatch errors, the aggregate mismatch assertion, and six dependent mutation-refusal assertions. The golden block was untouched.",
      "needs": ""
    },
    {
      "id": "F4",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Canonical discovery was attempted twice but the runner returned no final exit status or output; focused required suites completed.",
      "needs": "Rerun discovery in a lead-controlled runner if required."
    }
  ],
  "scope_expansion": {
    "requested_paths": ["joulewise/floor_mint_estimator.py"],
    "reason": "N4 requires changing the acceptance_id guard to reject an empty string.",
    "blocked_work": "Make the nonempty-string validation match its error message.",
    "minimal_change": "Change the guard to reject `not acceptance_id` alongside non-string values."
  }
}
```

## Change

Implemented B1–B2, S1–S4, and N5/F4 within scope. The resolver now returns immutable operatives, rejects malformed supplied operative containers, and emits the ruled crosswire text. Fixture policy now derives from each declared acceptance ID; V2 compatibility shims are removed.

## Verification notes

The n19 regression failed before the code fix and passes afterward. Poisoning and crosswire outputs are transcribed in V7.

## Residual risk

N4 remains unmodified pending scope, and the completed work is uncommitted because the linked-worktree Git metadata is sandbox-blocked.