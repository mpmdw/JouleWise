```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "partial",
  "summary": "Implemented D-138 fix round 2 within WRITE_SCOPE; the RED record passes, with sandbox verification left to the lead.",
  "workspace": {
    "base_requested": "6ed6c1d5dd423b3552b33829116c9d50dbae43d5",
    "base_mode": "exact",
    "head_start": "6ed6c1d5dd423b3552b33829116c9d50dbae43d5",
    "head_end": "6ed6c1d5dd423b3552b33829116c9d50dbae43d5",
    "upstream_end": "6ed6c1d5dd423b3552b33829116c9d50dbae43d5",
    "branch": "feat/2026-09-27-d138-25g83-issuance"
  },
  "pathspec": [
    "configs/calibration/calibration_acceptance_d079_v2_n12_25g83_r1.json",
    "joulewise/arm_readiness.py",
    "joulewise/calibration_bracketing.py",
    "joulewise/calibration_dispositions.py",
    "scripts/promote_calibration_candidate.py",
    "tests/test_acc_25g83_rev5.py",
    "tests/test_calibration_bracketing.py",
    "tests/test_calibration_dispositions.py",
    "tests/test_calibration_exits.py",
    "tests/test_calibration_live_three_window.py",
    "tests/test_calibration_writer_crash_matrix.py",
    "tests/test_claim_hold_routes.py",
    "tests/test_epoch_continuation.py",
    "tests/test_epoch_equivalence_check.py",
    "tests/test_issue_calibration_acceptance_generation.py",
    "tests/test_issuer_corpus_root.py",
    "tests/test_mint_floor_artifact_generalized.py",
    "tests/test_powermetrics_fiducial.py",
    "tests/test_promote_calibration_candidate.py",
    "tests/test_validate_powermetrics_fiducial_derivation_only.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "/tmp/d138-fix2-d528efb2/red_record.sh > /tmp/d138-fix2-d528efb2/red_record_final.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["P6 GREEN PASS", "RED_RECORD=PASS"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "RED_RECORD=PASS"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B -m unittest tests.test_claim_hold_routes tests.test_calibration_bracketing tests.test_calibration_dispositions tests.test_promote_calibration_candidate tests.test_acc_25g83_rev5 tests.test_calibration_exits tests.test_calibration_live_three_window tests.test_calibration_writer_crash_matrix tests.test_epoch_continuation tests.test_epoch_equivalence_check tests.test_floor_mint_pinsets_schema tests.test_issue_calibration_acceptance_generation tests.test_issuer_corpus_root tests.test_mint_floor_artifact_generalized tests.test_powermetrics_fiducial tests.test_validate_powermetrics_fiducial_derivation_only > /tmp/d138-fix2-d528efb2/scoped_without_arm.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 681 tests in 2913.522s", "FAILED (failures=1, skipped=6)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B -m unittest tests.test_arm_readiness_evidence_author.ArmReadinessEvidenceAuthorTests.test_h_t1_new_issuance_is_held_at_arm tests.test_arm_readiness_evidence_author.ArmReadinessEvidenceAuthorTests.test_h_t2_r7_stays_admitted tests.test_arm_readiness_evidence_author.ArmReadinessEvidenceAuthorTests.test_h_t3_registry_and_admission_sets_match",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 3 tests in 0.011s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
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
        "tail": ["issued sha256=d6de84b854a4c5d7f6d73dfde2ae0f14d71a483355c7289a36882e0dfcccd5ea"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "issued sha256=d6de84b854a4c5d7f6d73dfde2ae0f14d71a483355c7289a36882e0dfcccd5ea"
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
        "tail_regex": ""
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The sole V2 failure is the known sandbox machine probe: test_live_probes_report_this_machine_against_the_active_epoch observed os_build=None. Its test file is byte-identical to main 9eab16f8.",
      "needs": "Lead reruns the scoped module and whole suite outside the sandbox."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The full arm_readiness_evidence_author module invokes the production suite internally. I stopped that attempt to honor the lead-only whole-suite instruction; H-T1 through H-T3 passed separately.",
      "needs": "Lead runs the full arm module outside the sandbox."
    },
    {
      "id": "F3",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The issued design addendum is absent from this branch checkout. I read its complete Git object at b61602da; no document was edited.",
      "needs": "Lead ensures the addendum is present in the merge candidate."
    }
  ]
}
```

## Change

- **R-1–R-5:** R7 remains the default. The new generation stays issued, pinned, and held; the loader returns it only with `allow_claim_held=True`. The arm admission list uses the same hold table. An explicitly requested held artifact produces the ruled freshness reason and hold name.
- **Doubling trigger:** declared disposed rows no longer count toward corpus doubling. DT-1 through DT-5 cover the new generation and R7.
- **S2:** promotion checks cited file digests, the decompressed preserved-log digest, D8 text equality, and the claim-eligibility sentence. P6 rejects all six altered texts.
- **N1, N2, N4, N5, N7:** added L10 and P7; added the rule-(f), table-authority, and self-check comments; widened L9 to guard `open`, `os.open`, and `Path.read_bytes`.
- Restored tests changed for the moved default to main’s R7 expectations, retaining added generation and freeze checks. No change requires a scope expansion or ruling.

The regenerated issued file has SHA-256 `d6de84b854a4c5d7f6d73dfde2ae0f14d71a483355c7289a36882e0dfcccd5ea`, input seal `e7363bdd83af94cad15f0554043d35b646168e005125d3d770e7ba91dc9fb011`, and whole-file seal `8726a11bd4da79fe20cdca5321bf554cd11f6903a39b0710af6db2fd93de3333`.

## Verification notes

[RED record](/tmp/d138-fix2-d528efb2/red_record_final.log): HR-1, HR-2, HR-3, HR-5, DT-1, DT-2, and P6 each **failed on `325d9f77` and passed on the fix tree**; `RED_RECORD=PASS`. P6 failed all six altered-text subtests on the old tree.

The 681-test scoped run had one sandbox-only machine-probe failure and six skips. The lead’s next verification is the full arm module and canonical suite outside the sandbox, followed by the ruled independent replay and final review.

## Residual risk

The arm module’s full run and the lead-owned merge gates remain pending.