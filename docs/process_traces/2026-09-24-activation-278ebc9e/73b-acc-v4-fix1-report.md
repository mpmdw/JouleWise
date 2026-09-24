```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented all six cures; the replay passes, and the remaining focused-suite failures exactly match the documented r8 re-pin list.",
  "workspace": {
    "base_requested": "53e6d23d91068e4c51b38f39a4ad391d1a268c28",
    "base_mode": "exact",
    "head_start": "53e6d23d91068e4c51b38f39a4ad391d1a268c28",
    "head_end": "53e6d23d91068e4c51b38f39a4ad391d1a268c28",
    "upstream_end": null,
    "branch": "feat/2026-09-24-acc-25g83-v4-rev4"
  },
  "pathspec": [
    "joulewise/calibration_bracketing.py",
    "scripts/issue_calibration_acceptance_generation.py",
    "configs/calibration/preregistration_d079_epoch_25g83_rev1.md",
    "docs/process_traces/2026-09-24-activation-278ebc9e/37-acc-stale-number-audit.md",
    "tests/test_calibration_bracketing.py",
    "tests/test_acc_25g83_v4_rev4.py",
    "tests/test_issue_calibration_acceptance_generation.py",
    "tests/test_reissue_calibration_acceptance.py"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_issue_calibration_acceptance_generation tests.test_calibration_ledger tests.test_calibration_exits tests.test_reduce tests.test_run_campaign tests.test_generate_g2a_probe_inputs tests.test_calibration_custody_store tests.test_calibration_writer_crash_matrix tests.test_powermetrics_fiducial tests.test_validate_powermetrics_fiducial tests.test_validate_powermetrics_fiducial_derivation_only tests.test_preregistration_chain_digest tests.test_reissue_calibration_acceptance tests.test_arm_readiness tests.test_acc_25g83_v4_rev4 tests.test_calibration_bracketing",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 1032 tests in 931.432s",
          "FAILED (failures=71, errors=9, skipped=4)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest -q tests.test_calibration_bracketing.GenerationKeyedIssuanceValidationTests.test_only_r8_v3_identity_admits_v4_protocol_pin tests.test_acc_25g83_v4_rev4.RevisionFourIssuerTests.test_w1_futility_counts_valid_including_anchor_exclusion tests.test_issue_calibration_acceptance_generation.PrepareCandidateTest.test_revision_four_dry_run_reports_valid_count_before_exclusions tests.test_acc_25g83_v4_rev4.RevisionFourIssuerTests.test_historical_rule_outcomes_shape_excludes_revision_four_keys tests.test_issue_calibration_acceptance_generation.PrepareCandidateTest.test_only_the_candidate_label_stops_the_candidate_authenticating tests.test_reissue_calibration_acceptance.ReissueCalibrationAcceptanceTests.test_two_runs_emit_byte_identical_candidates tests.test_reissue_calibration_acceptance.ReissueCalibrationAcceptanceTests.test_upstream_member_science_delta_forces_stop_verdict",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 7 tests in 21.529s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "lint",
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
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/wt-278ebc9e-accv4 PYTHONDONTWRITEBYTECODE=1 python3 -B -c 'import sys, runpy; from joulewise import powermetrics_fiducial as detector; assert detector.PULSE_DURATION_S == 2.0; sys.argv = [\"replay.py\", \"--output\", \"/tmp/accv4-fix1-replay-final.json\"]; runpy.run_path(\"/Users/edr/code/wt-278ebc9e-bk/docs/process_traces/2026-09-24-activation-278ebc9e/34-acc-replay-gate/replay.py\", run_name=\"__main__\")' | tail -n 2",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "n2-d12  fitted=True recorded=[] v3=[] comparison=exact_match v4=[]",
          "R-ACC-1(b): PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "R-ACC-1\\(b\\): PASS"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The 70 distinct remaining failing tests are downstream of the stale r7 protocol or estimator digest pins. The failure set exactly matches the r8 audit list.",
      "needs": "Lead performs the ruled science-neutral r8 reissue, then reruns every listed test before G2-a arm."
    }
  ]
}
```

## Change

- **C1:** Restricted the v3-identity/v4-pin exception to the named r8 acceptance ID in [calibration_bracketing.py](/Users/edr/code/wt-278ebc9e-accv4/joulewise/calibration_bracketing.py:142). A regression proves r1, r6, and r7 reject a substituted v4 pin in [test_calibration_bracketing.py](/Users/edr/code/wt-278ebc9e-accv4/tests/test_calibration_bracketing.py:3274). The historical issuer now pins the protocol named by its candidate identity at [issue_calibration_acceptance_generation.py](/Users/edr/code/wt-278ebc9e-accv4/scripts/issue_calibration_acceptance_generation.py:1719).
- **C2:** Revision 4 counts W1 **VALID** observations for futility at [preregistration_d079_epoch_25g83_rev1.md](/Users/edr/code/wt-278ebc9e-accv4/configs/calibration/preregistration_d079_epoch_25g83_rev1.md:618). The dry run reports that count, and the issuer checks only the W2 procedure violation before reading B values at [issue_calibration_acceptance_generation.py](/Users/edr/code/wt-278ebc9e-accv4/scripts/issue_calibration_acceptance_generation.py:227). Regressions cover an eight-VALID W1 with one later anchor exclusion and a seven-VALID W1 with W2 present at [test_acc_25g83_v4_rev4.py](/Users/edr/code/wt-278ebc9e-accv4/tests/test_acc_25g83_v4_rev4.py:169).
- **C3:** Ran `tests.test_calibration_bracketing` in full. The final V1 run has 80 failure/error outcomes across exactly 70 distinct r7-pin-effect tests; all 70 are named in [37-acc-stale-number-audit.md](/Users/edr/code/wt-278ebc9e-accv4/docs/process_traces/2026-09-24-activation-278ebc9e/37-acc-stale-number-audit.md:15). Three other failures were real historical issuer/reissue test mismatches; they were fixed and pass V2.
- **C4:** Revision 4 alone emits the new `rule_outcomes` keys at [issue_calibration_acceptance_generation.py](/Users/edr/code/wt-278ebc9e-accv4/scripts/issue_calibration_acceptance_generation.py:1659); the historical shape regression passes at [test_acc_25g83_v4_rev4.py](/Users/edr/code/wt-278ebc9e-accv4/tests/test_acc_25g83_v4_rev4.py:188).
- **C5:** Added ruling 2(k)’s n ≥ 19 and three-window fallback and recorded the simulation’s zero admissions at [preregistration_d079_epoch_25g83_rev1.md](/Users/edr/code/wt-278ebc9e-accv4/configs/calibration/preregistration_d079_epoch_25g83_rev1.md:647).
- **C6:** Marked the Revision 4 substring check as advisory and the digest pin as the seal at [issue_calibration_acceptance_generation.py](/Users/edr/code/wt-278ebc9e-accv4/scripts/issue_calibration_acceptance_generation.py:1205).

## Verification notes

V1 included all of `CalibrationBracketingTests`. Its 70 distinct failing test identifiers exactly equal the audit list, with no unlisted failures. V4’s replay summary reports 22 fitted captures with exact v3 matches, two unfitted captures, and zero v4 misses across 1,416 pulses.

## Residual risk

The ruled r8 reissue remains outstanding. The lead’s next step is to re-pin r8 and rerun the 70 tests listed in the audit before G2-a arm.