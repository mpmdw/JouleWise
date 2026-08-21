```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "All four fix-round defect classes and the missing-root guard pass execution probes, but the requested 16-test module gate runs only 15 tests.",
  "workspace": {
    "base_requested": "d3278306041290c32a05924adfca86cee23c47bb",
    "base_mode": "exact",
    "head_start": "d3278306041290c32a05924adfca86cee23c47bb",
    "head_end": "d3278306041290c32a05924adfca86cee23c47bb",
    "upstream_end": "d3278306041290c32a05924adfca86cee23c47bb",
    "branch": "impl/receipt-histsem"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "NO-GO",
    "basis": "NO-GO only for the explicit 16-test acceptance criterion; executed behavioral probes are clean.",
    "same_signature_prior_defect_survival": {
      "answer": "no",
      "evidence": "B1, S1, S2, and S3 all exercised their corrected paths with the required outcomes."
    },
    "findings": [
      {
        "id": "F1",
        "severity": "should_fix",
        "title": "Receipt-histsem module contains and runs 15 tests, not the required 16",
        "evidence": "The captured full-module run reports 'Ran 15 tests ... OK'; the source contains 15 test methods.",
        "impact": "The strict-resolve bench guard is manually proven in this audit but lacks the requested permanent regression-count coverage.",
        "recommendation": "Add one focused regression covering relative, '..', and nonexistent-root gate inputs, then rerun the module expecting 16 tests."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "smoke",
      "cmd": "python3 /tmp/receipt_histsem_r4_delta_probes.py > /tmp/receipt_histsem_r4_delta_probes.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "B1_PREDECESSOR_SYMLINK=histsem_pinset_mismatch",
          "STRICT_RESOLVE=relative_ok,dotdot_ok,nonexistent_returns",
          "S2_WORKTREE_PINSET_DIRECT=PASS",
          "S2_GATE_HEAD_PINSET=histsem_pinset_mismatch",
          "S1_LS_TREE_PRESENT=verifier_invoked_once",
          "S1_LS_TREE_ABSENT=ordinary_return",
          "S1_LS_TREE_NONZERO=histsem_history_unavailable",
          "S1_LC_ALL_fr_FR_UTF_8=ordinary_return",
          "S3_PRODUCER_CODE=readiness_pack_not_committed",
          "S3_BRANCHES=histsem_history_unavailable,histsem_git_unavailable",
          "DELTA_PROBES=PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "DELTA_PROBES=PASS"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest discover -s tests -p 'test_receipt_histsem.py' > /tmp/receipt_histsem_r4_full_module.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "Ran 15 tests in 106.206s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 16 tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --no-ext-diff --exit-code HEAD -- configs/calibration/calibration_acceptance_d079_v2_n17_r6.json configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json && git show HEAD:configs/calibration/calibration_acceptance_d079_v2_n17_r6.json | shasum -a 256 && shasum -a 256 configs/calibration/calibration_acceptance_d079_v2_n17_r6.json && git show HEAD:configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json | shasum -a 256 && shasum -a 256 configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "0227bca3f826edc7f0a1baf98a394df01d8f48e9609966088870d712f765697d",
          "d81515505d677c2ca045238e721c87eae8f38439a89a5377e58fa9064eaf2f21"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "0227bca3.*d8151550"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "The behavioral audit is clean, but the stated full-module requirement was 16 tests and the captured module run has 15.",
      "needs": "Add the missing focused strict-resolve regression and rerun the captured module test."
    }
  ]
}
```

## Findings

### F1 — should_fix

The full module passed, but ran 15 rather than 16 tests. This makes the verdict **NO-GO** against the stated acceptance gate.

Executed probes otherwise passed:

- B1: a symlink alias supplied through `generate_freeze_receipt(... predecessor_pack_root=alias)` refused with `histsem_pinset_mismatch`; relative paths, `..` paths, and a missing root returned normally.
- S2: a forged worktree pinset let direct verification pass, while the gate refused it using the committed HEAD row (`histsem_pinset_mismatch`).
- S1: real present and absent `ls-tree` paths proceeded/returned correctly; an injected nonzero `ls-tree` returned `histsem_history_unavailable`; the absent-path probe also returned normally under `LC_ALL=fr_FR.UTF-8`.
- S3: the real non-repository producer raised `readiness_pack_not_committed`, mapping to `histsem_history_unavailable`; the missing-root direct helper route remained reachable as `histsem_git_unavailable`.
- Same-signature statement: **No**, none of B1/S1/S2/S3 survives in a new form under the executed probes.
- The r6 acceptance artifact and histsem pinset are byte-identical to HEAD.

## Residual risk

None beyond F1’s missing permanent regression coverage.