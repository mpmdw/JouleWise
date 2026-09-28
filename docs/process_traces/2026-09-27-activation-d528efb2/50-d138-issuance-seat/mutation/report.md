```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "partial",
  "summary": "Mutation evidence has an L7 survivor and one freeze outside write scope.",
  "workspace": {
    "base_requested": "c81f65b8b703f348c0e2375407782028a5d3057b",
    "base_mode": "exact",
    "head_start": "c81f65b8b703f348c0e2375407782028a5d3057b",
    "head_end": "c81f65b8b703f348c0e2375407782028a5d3057b",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [
    "joulewise/calibration_dispositions.py",
    "joulewise/calibration_bracketing.py",
    "joulewise/arm_readiness.py",
    "scripts/promote_calibration_candidate.py",
    "scripts/issue_calibration_acceptance_generation.py",
    "scripts/epoch_equivalence_check.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "findings": [
      {
        "id": "F-SCOPE",
        "severity": "blocker",
        "text": "The §6.3 simulation freeze could not be mutated within WRITE_SCOPE."
      },
      {
        "id": "F-L7",
        "severity": "should_fix",
        "text": "Removing the disposed-member guard stays GREEN across all nine disposition tests."
      },
      {
        "id": "F-R7",
        "severity": "should_fix",
        "text": "The named Revision 5 freeze test stays GREEN when the predecessor comparison reads the active ID; other Revision 5 tests fail indirectly."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "/opt/homebrew/bin/python3 -B /tmp/d138-mut-d528efb2/run_mutations.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["R7-epoch-default mutant: exit 1; restore true"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "restore.*true"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONPATH=tests:. /opt/homebrew/bin/python3 -B -m unittest test_acc_25g83_rev5",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 13 tests in 44.249s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 13 tests.*OK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --quiet -- joulewise/calibration_dispositions.py joulewise/calibration_bracketing.py joulewise/arm_readiness.py scripts/promote_calibration_candidate.py scripts/issue_calibration_acceptance_generation.py scripts/epoch_equivalence_check.py",
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
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "The third §6.3 freeze requires a mutation to scripts/sim_acc_25g83_rev5.py, outside WRITE_SCOPE.",
      "needs": "Lead-issued scope expansion for that exact path."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "L7's named test and the full disposition module remain GREEN under the member-arm mutant.",
      "needs": "Strengthen the L7 test so removal of that guard fails."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The named Revision 5 freeze test does not exercise its predecessor comparison.",
      "needs": "Add a direct R7 predecessor comparison assertion."
    }
  ],
  "scope_expansion": {
    "requested_paths": ["scripts/sim_acc_25g83_rev5.py"],
    "reason": "§6.3 names this tool as the third R7-frozen consumer, but it is outside the exhaustive write allowlist.",
    "blocked_work": "Planting and testing the simulation freeze mutant.",
    "minimal_change": "Temporarily change its R7 load path to the active default, run the existing freeze test, then restore and verify the file."
  }
}
```

MUTATION: GAPS

| Ruled ID | Planted defect (exact edit) | Test ID and observed result | Restore |
|---|---|---|---|
| L2 | Skip rows by registration session instead of disposed content ID. | `test_l2_unlisted_foreign_valid_refuses` **RED**, line 53: `True is not false`. | Verified |
| L4 | Set `declared = decisions_disposing(set(prior_ids))`, ignoring the file declaration. | `test_l3_l4_declaration_refuses` **RED**, line 66: `True is not false`. | Verified |
| L5 | Intersect `disposed` with `prior_ids` before rule (c). | `test_l5_missing_disposed_row_refuses` **RED**, line 79: `True is not false`. | Verified |
| L6 | Remove the registration-session arm of rule (d). | `test_l6_disposed_inside_registration_refuses` **RED**, line 90: `True is not false`. | Verified |
| L7 | Remove `or content_id in member_content_ids` from rule (d). | `test_l7_member_in_disposition_table_refuses` **GREEN**; all nine disposition tests GREEN. | Verified |
| L8 | Replace one table content ID with `ffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff`. | `test_d1_registry_and_table_agree` **ERROR** on table mismatch; `test_l8_table_missing_row_refuses` **RED**, line 115: `False is not true`. | Verified |
| P3 | Bypass candidate digest, both candidate seals, issuance source binding, issued input seal, and the recomputed seal’s protected-field comparison. | `test_p3_changed_member_refuses_both_seals` **RED**, line 54: `ValueError not raised`. Separate digest and seal bypasses also RED on their expected refusal messages. | Verified |
| H-T1 | Empty `_CLAIM_HELD_ACCEPTANCE_IDS`. | `test_h_t1_new_issuance_is_held_at_arm` **RED**, line 370: `True is not false`. | Verified |
| §6.3 preparation | Change predecessor comparison from R7 ID to active ID. Separately change `--predecessor-acceptance` default from R7 path to default path. | Comparison: named freeze test **GREEN**, but six other `test_acc_25g83_rev5` assertions **RED** on premature “requires r7 predecessor” refusal. Default: named freeze test **RED**, line 431, 25G83 path differs from R7. | Verified after each |
| §6.3 epoch check | Change `--acceptance` default from R7 path to active default path. | `test_default_acceptance_remains_r7` **RED**, line 78, 25G83 path differs from R7. | Verified |
| §6.3 simulation | No edit: `scripts/sim_acc_25g83_rev5.py` is outside WRITE_SCOPE. | **Not run.** | Unchanged |

## Findings

**F-SCOPE — blocker.** The simulation freeze needs the scope expansion specified in the envelope.

**F-L7 — should fix.** The L7 test does not kill removal of its named member guard. The [mutation logs](/tmp/d138-mut-d528efb2/results.json) record the GREEN result; the full disposition module was also GREEN under that mutant.

**F-R7 — should fix.** The named freeze test checks the preparation default and simulation path, but stays GREEN when the preparation predecessor comparison is changed to the active ID. Broader Revision 5 tests fail indirectly under that mutation.

## Residual risk

All six in-scope files were restored byte for byte and passed `git diff --quiet`. No production change remains in this scratch worktree.