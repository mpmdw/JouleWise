```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented the scoped v4 and Revision 4 changes; production validation requires an expanded write scope.",
  "workspace": {
    "base_requested": "main",
    "base_mode": "exact",
    "head_start": "bce0d7dfd38ca1ff160ae9b29a685f6c3a61d9b1",
    "head_end": "bce0d7dfd38ca1ff160ae9b29a685f6c3a61d9b1",
    "upstream_end": "bce0d7dfd38ca1ff160ae9b29a685f6c3a61d9b1",
    "branch": "feat/2026-09-24-acc-25g83-v4-rev4"
  },
  "pathspec": [
    "joulewise/powermetrics_fiducial.py",
    "joulewise/reduce.py",
    "joulewise/arm_readiness.py",
    "configs/calibration/powermetrics_fiducial/protocol_v4.json",
    "configs/calibration/preregistration_d079_epoch_25g83_rev1.md",
    "docs/contracts/run_bundle_layout.md",
    "docs/contracts/powermetrics_fiducial.md",
    "docs/decision_log.md",
    "scripts/issue_calibration_acceptance_generation.py",
    "scripts/validate_powermetrics_fiducial.py",
    "tests/test_calibration_exits.py",
    "tests/test_powermetrics_fiducial.py",
    "tests/test_preregistration_chain_digest.py",
    "tests/test_reduce.py",
    "tests/test_validate_powermetrics_fiducial_derivation_only.py",
    "tests/test_acc_25g83_v4_rev4.py",
    "docs/process_traces/2026-09-24-activation-278ebc9e/37-acc-stale-number-audit.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_issue_calibration_acceptance_generation tests.test_calibration_ledger tests.test_calibration_exits tests.test_reduce tests.test_run_campaign tests.test_generate_g2a_probe_inputs tests.test_calibration_custody_store tests.test_calibration_writer_crash_matrix tests.test_powermetrics_fiducial tests.test_validate_powermetrics_fiducial tests.test_validate_powermetrics_fiducial_derivation_only tests.test_preregistration_chain_digest tests.test_reissue_calibration_acceptance tests.test_arm_readiness tests.test_acc_25g83_v4_rev4",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 932 tests in 868.783s",
          "FAILED (failures=95, errors=15, skipped=2)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_acc_25g83_v4_rev4 tests.test_preregistration_chain_digest",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 13 tests in 9.280s",
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
      "kind": "inspection",
      "cmd": "python3 -B - <<'PY'\nfrom pathlib import Path\np=Path('docs/process_traces/2026-09-24-activation-278ebc9e/37-acc-stale-number-audit.md')\ns=p.read_text()\nneed=['0.032898','0.009724','0.010165','0.010818','calibration_bracket_max_drift_s']\nprint('AUDIT_PRESENT',p.is_file(),'COVERED',all(x in s for x in need),'ROWS',sum(line.startswith('|') for line in s.splitlines())-2)\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "AUDIT_PRESENT True COVERED True ROWS 5"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "AUDIT_PRESENT True COVERED True ROWS 5"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "The out-of-scope production validator still requires n >= 17 and S < C, recomputes C without S, and excludes historical v3 evidence after the live ID moves to v4.",
      "needs": "Lead-issued scope expansion for joulewise/calibration_bracketing.py and its tests."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "V1 failed against the stale r7 code pin and validator paths; it began before the final focused test adjustments. The later V2 run passed.",
      "needs": "Complete the validator change, perform the separate replay and simulation gates, then rerun V1 and the lead's full gate."
    },
    {
      "id": "F3",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The required fixture-orphan census exited 2 because the sandbox denied ps: PermissionError [Errno 1] Operation not permitted.",
      "needs": "Lead reruns the census in its permitted environment."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "joulewise/calibration_bracketing.py",
      "tests/test_calibration_bracketing.py"
    ],
    "reason": "The production validator must admit the registered 25G83/v4 n=12 and C=S case while retaining historical generation and v3 evidence validation.",
    "blocked_work": "A Revision 4 candidate cannot become a production-valid issued acceptance.",
    "minimal_change": "Epoch-scoped validator branches for the n floor and C=max(predecessor C,Q99,S), with historical v3 protocol admission and focused regression tests."
  }
}
```

## Change

| Ruled item | Implementation |
|---|---|
| 1(a) | v4 identity, 2.0 s pulses, 1.8–2.2 s authentication, and historical v3 dispatch: [powermetrics_fiducial.py:45](/Users/edr/code/wt-278ebc9e-accv4/joulewise/powermetrics_fiducial.py:45). Added [protocol_v4.json:1](/Users/edr/code/wt-278ebc9e-accv4/configs/calibration/powermetrics_fiducial/protocol_v4.json:1) and updated the live loader, contracts, and arm rehearsal. |
| 2(a) | Registered the 25G83/v4 epoch and powermetrics pin: [preregistration_d079_epoch_25g83_rev1.md:610](/Users/edr/code/wt-278ebc9e-accv4/configs/calibration/preregistration_d079_epoch_25g83_rev1.md:610). |
| 2(b) | Registered two 12-slot windows, ≥6 h apart, with settle, cadence, and 9000 s limit: [preregistration_d079_epoch_25g83_rev1.md:616](/Users/edr/code/wt-278ebc9e-accv4/configs/calibration/preregistration_d079_epoch_25g83_rev1.md:616). |
| 2(c) | Added the dated D-126 text and epoch-scoped issuer floor of 12: [decision_log.md:8485](/Users/edr/code/wt-278ebc9e-accv4/docs/decision_log.md:8485), [issue_calibration_acceptance_generation.py:372](/Users/edr/code/wt-278ebc9e-accv4/scripts/issue_calibration_acceptance_generation.py:372). |
| 2(d) | Registered count-only W3 and W1 futility; issuer checks both session outcomes: [preregistration_d079_epoch_25g83_rev1.md:618](/Users/edr/code/wt-278ebc9e-accv4/configs/calibration/preregistration_d079_epoch_25g83_rev1.md:618), [issue_calibration_acceptance_generation.py:1338](/Users/edr/code/wt-278ebc9e-accv4/scripts/issue_calibration_acceptance_generation.py:1338). |
| 2(e) | Preserved the terminal-session blindness fence: [preregistration_d079_epoch_25g83_rev1.md:620](/Users/edr/code/wt-278ebc9e-accv4/configs/calibration/preregistration_d079_epoch_25g83_rev1.md:620). |
| 2(f) | Disclosed all eleven seen B values, the frame distribution, and r6 decimation as design inputs: [preregistration_d079_epoch_25g83_rev1.md:624](/Users/edr/code/wt-278ebc9e-accv4/configs/calibration/preregistration_d079_epoch_25g83_rev1.md:624). |
| 2(g) | Made the r6 screen challenge diagnostic for v4: [issue_calibration_acceptance_generation.py:1399](/Users/edr/code/wt-278ebc9e-accv4/scripts/issue_calibration_acceptance_generation.py:1399). |
| 2(h) | Added excursion count and label, plus the named >0.25 s refusal: [issue_calibration_acceptance_generation.py:1389](/Users/edr/code/wt-278ebc9e-accv4/scripts/issue_calibration_acceptance_generation.py:1389). |
| 2(i) | Added D-125’s dated text and issuer zero-headroom arithmetic: [decision_log.md:8457](/Users/edr/code/wt-278ebc9e-accv4/docs/decision_log.md:8457), [issue_calibration_acceptance_generation.py:1427](/Users/edr/code/wt-278ebc9e-accv4/scripts/issue_calibration_acceptance_generation.py:1427). Production validation remains blocked by scope. |
| 2(j) | Audited all five named constants: [37-acc-stale-number-audit.md:5](/Users/edr/code/wt-278ebc9e-accv4/docs/process_traces/2026-09-24-activation-278ebc9e/37-acc-stale-number-audit.md:5). |
| 2(l) | Recorded the physical barrier basis and n = 12 rationale: [preregistration_d079_epoch_25g83_rev1.md:649](/Users/edr/code/wt-278ebc9e-accv4/configs/calibration/preregistration_d079_epoch_25g83_rev1.md:649). |
| 3(c) | Added measured-interior median/max frame lengths, corpus comparison, and a flag-only 0.75 s trigger: [reduce.py:441](/Users/edr/code/wt-278ebc9e-accv4/joulewise/reduce.py:441). |
| 7 | Described the registration and protocol digest seal and arm-notice quotation: [preregistration_d079_epoch_25g83_rev1.md:612](/Users/edr/code/wt-278ebc9e-accv4/configs/calibration/preregistration_d079_epoch_25g83_rev1.md:612). |

Revisions 1–3 remain a byte-identical prefix. No r8 artifact was created, and all changes remain uncommitted.

## Verification notes

V1’s exact summary is in the envelope. Its stale-pin failures cannot be cleared by editing issued evidence. V2 passed the v4 geometry, n = 12 and n < 12, zero-headroom, excursion, >0.25 s, historical v3, cadence-flag, and preregistration tests. **NEEDS_RULING items: none. NEEDS_SCOPE:** the two validator paths in `scope_expansion`.

## Residual risk

The separate deterministic replay gate and n = 12 simulation gate remain outstanding by assignment. The magistrate must seal the final digests and perform the later r8 reissue before W1.