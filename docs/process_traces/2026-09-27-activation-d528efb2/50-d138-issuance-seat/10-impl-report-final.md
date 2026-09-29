```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "The private 25F84 checkout now uses R7; two repository-root preflight tests need a ruling on the amended test scope.",
  "workspace": {
    "base_requested": "a7b347d21a0e136f5734ba9661652c8ce34dd7a3",
    "base_mode": "exact",
    "head_start": "a7b347d21a0e136f5734ba9661652c8ce34dd7a3",
    "head_end": "a7b347d21a0e136f5734ba9661652c8ce34dd7a3",
    "upstream_end": "a7b347d21a0e136f5734ba9661652c8ce34dd7a3",
    "branch": "feat/2026-09-27-d138-25g83-issuance"
  },
  "pathspec": [
    "tests/test_validate_powermetrics_fiducial_derivation_only.py"
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
      "cmd": "/opt/homebrew/bin/python3 -B -m unittest -v tests.test_validate_powermetrics_fiducial_derivation_only",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 27 tests in 244.784s", "FAILED (failures=2)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 27 tests.*\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B -m unittest tests.test_calibration_dispositions",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 9 tests in 0.027s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 9 tests.*\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B -m unittest tests.test_acc_25g83_rev5",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 13 tests in 26.173s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 13 tests.*\\n\\nOK"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "/opt/homebrew/bin/python3 -B scripts/promote_calibration_candidate.py --check configs/calibration/calibration_acceptance_d079_v2_n12_25g83_r1.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["issued sha256=9e5c735bf7b4d27604bfadd87809750974322258b943fd1afb04d1873e824c06"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "issued sha256=9e5c735bf7b4d27604bfadd87809750974322258b943fd1afb04d1873e824c06"
      }
    },
    {
      "id": "V5",
      "kind": "other",
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
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The amended grant names the private 25F84 checkout. Two remaining failures are repository-root preflight tests in the same file that assume R7 is still the active default.",
      "needs": "Rule whether this grant also permits re-pointing those two root preflight expectations to active 25G83. No assertion needs weakening."
    }
  ]
}
```

## Change

In the newly allowlisted test file, the private 25F84 checkout now points its copied calibration default to R7 before committing that fixture. This cured its former checkout failures. No production file or assertion changed in this turn.

**NEEDS_RULING:** The whole module now has two remaining failures:

- `DerivationOnlyPreflightRefusalTests.test_matching_identity_epoch_refuses_because_derivation_only_would_bypass_the_screen` supplies R7’s 25F84 epoch to the repository-root script, whose active default is now 25G83. It receives `calibration_derivation_only_session_kind_required` instead of the expected epoch-unchanged refusal.
- `DerivationOnlyPreflightRefusalTests.test_standalone_derivation_only_refuses_without_a_declared_session_slot` supplies `25G83` as its supposedly *differing* epoch. It now receives the epoch-unchanged refusal instead of the expected session-kind refusal.

I recommend using the active 25G83 epoch **only in this preflight test class**, changing its differing-epoch fixture to 25F84, and updating the first test’s expected acceptance ID to 25G83. The shared R7 helper and private 25F84 checkout would stay as they are. This preserves both refusal assertions. The amendment specifically described re-pointing the *private checkout*, so I have not made the additional repository-root test edits without the lead’s ruling.

## Verification notes

The amended module ran whole: **27 tests, 2 failures**, down from 11 failures in the round-one suite. The two failing IDs are named above. The 25G83 promotion check passes; the issued file still has file SHA-256 `9e5c735bf7b4d27604bfadd87809750974322258b943fd1afb04d1873e824c06`, input seal `e7363bdd83af94cad15f0554043d35b646168e005125d3d770e7ba91dc9fb011`, and whole-file seal `2e0d88b5e0186f43a6d7fc45810e5ca78cb7aa8c75fafce78710e282d5de017b`.

The round-one whole-suite summary was `WORKERS SUMMARY shards=4 modules=269 tests=7540 failures=242 errors=2 skipped=131 failed_shards=1,2,3,4 result=FAIL`. I did not rerun it, as directed. The previously reported whole-module reruns after round-one fixture edits remain the verification for those unchanged files: dry run 12 pass, bracket binding 19 pass, evidence author 27 pass, calibration exits 48 pass, epoch continuation 68 pass, and powermetrics fiducial 75 pass. Issuance generation’s rerun retained only the sandbox live-`sysctl` failure.

The committed round-one tests still cover L1–L9 (loader admission, declaration, disposed-row and older-generation counterfactuals), P1–P5 (byte pin, protected fields, seals, disclosures and row agreement), H-T1–H-T3 (25G83 hold, retained R7 admission and registry coverage), and the three R7 consumer freezes. Their code was unchanged in this turn. The two census-added re-points remain the previously reported explicit R7 selections in `test_issuer_corpus_root.py` and `test_calibration_live_three_window.py`.

## Residual risk

The lead’s out-of-sandbox whole-suite rerun remains the acceptance gate after the ruling and the two remaining test corrections.