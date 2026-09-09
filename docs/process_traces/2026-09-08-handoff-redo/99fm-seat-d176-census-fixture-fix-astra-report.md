```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Corrected the rehearsal fixture and added wrong-checkout refusal coverage; all 128 named-module tests pass.",
  "workspace": {
    "base_requested": "93870527",
    "base_mode": "exact",
    "head_start": "93870527d608fa8ea7a15a45395e564ef7c62b2e",
    "head_end": "93870527d608fa8ea7a15a45395e564ef7c62b2e",
    "upstream_end": "93870527d608fa8ea7a15a45395e564ef7c62b2e",
    "branch": "int/2026-09-08-d176-seats-2-3"
  },
  "pathspec": ["tests/test_run_night.py"],
  "unowned_dirty": [
    "configs/production_custody_inventory.json",
    "docs/contracts/pack_night_go_receipt.md",
    "joulewise/arm_readiness.py",
    "joulewise/night_gate.py",
    "scripts/rehearse_t0_unattended.py",
    "tests/test_arm_readiness.py",
    "tests/test_arm_readiness_schemas.py",
    "tests/test_launch_window.py",
    "tests/test_rehearse_t0_unattended.py"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night tests.test_night_gate > /private/tmp/d176-night-fixtures-acceptance.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 128 tests in 8.839s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "(?m)^OK$"}
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": []
}
```

## Change

Corrected `test_rehearsal_plan_and_arm_context_roots_follow_sibling_child_rule`:

| Fixture case | Before | After |
|---|---|---|
| Valid measurement root | Synthetic checkout | Running checkout derived from `arm_readiness.__file__` |
| Measurement DISJOINT | Changed planned checkout | Varies production inventory, preserving equality and both containment directions |
| Measurement/custody overlap | Changed measurement root | Changes custody root to the authenticated measurement root |
| Claim at custody parent | Expected field-specific refusal | Expects DISJOINT refusal |

Sibling-child and symlink assertions remain. Added `test_pack_rehearsal_gate_refuses_another_measurement_checkout`, requiring “launcher is not the planned clone.”

Both modules were swept; no other affected fixture needed correction. Pre-existing edits preserved; no commit. Ready for lead review.

## Verification notes

The first run exposed the stale claim-parent expectation; the corrected rerun passed. The root-predicate fixture locally patches the rehearsal prefix to accommodate this worktree’s name. Launcher identity remains real and unmocked.