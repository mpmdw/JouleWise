```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented the build-keyed claim hold and RED gates; three unchanged ARM lifecycle assertions need a lead ruling on the legacy d079 fixture identifier.",
  "workspace": {
    "base_requested": "5decbe6b960395dce8fcfc5609b88bfcc27b8b26",
    "base_mode": "exact",
    "head_start": "5decbe6b960395dce8fcfc5609b88bfcc27b8b26",
    "head_end": "5decbe6b960395dce8fcfc5609b88bfcc27b8b26",
    "upstream_end": "5decbe6b960395dce8fcfc5609b88bfcc27b8b26",
    "branch": "feat/2026-09-27-d138-25g83-issuance"
  },
  "pathspec": [
    "configs/calibration/calibration_acceptance_d079_v2_n12_25g83_r1.json",
    "joulewise/arm_readiness.py",
    "joulewise/calibration_bracketing.py",
    "joulewise/calibration_epoch_continuation.py",
    "joulewise/claim_hold.py",
    "scripts/promote_calibration_candidate.py",
    "scripts/run_campaign.py",
    "scripts/validate_powermetrics_fiducial.py",
    "tests/test_acc_25g83_rev5.py",
    "tests/test_arm_readiness_evidence_author.py",
    "tests/test_arm_readiness_lifecycle.py",
    "tests/test_calibration_bracketing.py",
    "tests/test_calibration_dispositions.py",
    "tests/test_claim_hold_census.py",
    "tests/test_claim_hold_routes.py",
    "tests/test_epoch_equivalence_check.py",
    "tests/test_promote_calibration_candidate.py"
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
      "cmd": "/opt/homebrew/bin/python3 -B -m unittest tests.test_claim_hold_routes tests.test_claim_hold_census tests.test_calibration_bracketing tests.test_calibration_dispositions tests.test_arm_readiness_evidence_author tests.test_epoch_continuation tests.test_promote_calibration_candidate tests.test_acc_25g83_rev5 tests.test_epoch_equivalence_check tests.test_arm_readiness_lifecycle",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 350 tests in 285.834s", "FAILED (failures=3, skipped=2)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B -m unittest tests.test_claim_hold_routes tests.test_claim_hold_census tests.test_calibration_dispositions tests.test_promote_calibration_candidate",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 46 tests in 2.105s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B -m unittest tests.test_acc_25g83_rev5 tests.test_epoch_equivalence_check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 42 tests in 27.448s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "/tmp/d138-fix3-d528efb2/red_record.sh > /tmp/d138-fix3-d528efb2/red_record.out",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["C-plant-inspection-alias FAIL 1 'joulewise/whole_window.py'", "RED_RECORD_COMPLETE scratch_removed=true"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "RED_RECORD_COMPLETE"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B tests/verify_calibration_acceptance_corpus.py --repo-root . --corpus-root /Users/edr/night-custody --artifact configs/calibration/calibration_acceptance_d079_v2_n12_25g83_r1.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PRIMARY_EVIDENCE_HASH_CROSSCHECK=OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PRIMARY_EVIDENCE_HASH_CROSSCHECK=OK"
      }
    },
    {
      "id": "V6",
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
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Three ARM lifecycle tests use the synthetic issued identifier d079. The ruled claim_hold_for_acceptance_id fails closed because d079 has no registered build; changing those fixture declarations is outside the lifecycle amendment, which permits only machine-build-reader patches.",
      "needs": "Rule whether to authorize replacing the two synthetic d079 fixture declarations with a registered 25F84 identifier, or amend the production alias and build-table contract."
    }
  ]
}
```

## Change

Implemented G1 and its identifier gate, default guard, and frozen governance inspection; G2; S1; the single-identifier admission rule; S2 and S3; and the capture identity seam. Removed the loader’s hold bypass. Added route tests E-1 through E-11, census tests C-1 through C-7, promotion completeness test P8, and the R7 freeze controls. The issued file was regenerated with the promotion tool from the committed issuance text.

The issued file’s **input seal** is `e7363bdd83af94cad15f0554043d35b646168e005125d3d770e7ba91dc9fb011`. Its **whole-file SHA-256 and registry pin** are `d7076c78ddab564c9b7eefa9a24b658bdbbdd29b685373de7cb66cf48c565c2e`. Its derivation SHA-256 is `d3e4da75cdd99b36caeef8a0145c8a0ea430d08604abad6faeb69a0dd3ad420a`.

## Verification notes

The [RED record](/tmp/d138-fix3-d528efb2/red_record.out) was produced by [red_record.sh](/tmp/d138-fix3-d528efb2/red_record.sh). Every required old-commit RED and every planted mutation below was an assertion failure; fix-tree route tests passed.

```text
RED_RECORD fix_base=5decbe6b old1=325d9f77 old2=8458f797
E-1@325d9f77 FAIL 1
E-2@325d9f77 FAIL 1
E-3@325d9f77 FAIL 1
E-4@8458f797 FAIL 1
E-5@8458f797 FAIL 1
E-6@8458f797 FAIL 1
E-6b@8458f797 FAIL 1
E-6c@8458f797 FAIL 1
E-6d@8458f797 FAIL 1
E-6e@8458f797 FAIL 1
E-9@8458f797 FAIL 1
E-1,E-2,E-3,E-4,E-5,E-5c,E-6,E-6b,E-6c,E-6d,E-6e,E-7,E-8,E-9,E-10,E-11@fix PASS
P8@8458f797 FAIL 1; P8@fix PASS 1
M-G1,M-G2,M-S1,M-single-id,M-operatives,M-S2,M-S3,M-build-entry FAIL 1 each
M-R7-predecessor,M-R7-prepare-default,M-R7-epoch-default,M-R7-simulation FAIL 1 each
C-plant-new-reader,C-plant-unchecked-alias,C-plant-second-pass,C-plant-inspection-alias FAIL 1 each
RED_RECORD_COMPLETE scratch_removed=true
```

The full scoped run had three failures, all in `tests/test_arm_readiness_lifecycle.py`. The two dry-run failures name `desk.acceptance_successor`; the freeze failure cascades from the same fixture. A read-only diagnostic that treated synthetic `d079` as unheld made each focused failing test pass.

## Residual risk

**NEEDS_RULING.** The fixture declares `issued: "d079"` twice, while the ruled build map covers registered generation identifiers and must fail closed on an unknown identifier. I recommend authorizing a fixture update to a registered 25F84 identifier, preserving production’s fail-closed rule and the existing test assertions. The alternative is an explicit ruling that registers or exempts the legacy alias, with a corresponding census amendment. No fixture identifier was changed.