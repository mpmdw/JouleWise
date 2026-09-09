```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Completed the census cure and relocation-fixture correction; all 260 named acceptance tests pass.",
  "workspace": {
    "base_requested": "93870527",
    "base_mode": "exact",
    "head_start": "93870527d608fa8ea7a15a45395e564ef7c62b2e",
    "head_end": "93870527d608fa8ea7a15a45395e564ef7c62b2e",
    "upstream_end": "93870527d608fa8ea7a15a45395e564ef7c62b2e",
    "branch": "int/2026-09-08-d176-seats-2-3"
  },
  "pathspec": [
    "joulewise/arm_readiness.py",
    "joulewise/night_gate.py",
    "configs/production_custody_inventory.json",
    "scripts/rehearse_t0_unattended.py",
    "tests/test_arm_readiness.py",
    "tests/test_arm_readiness_schemas.py",
    "tests/test_rehearse_t0_unattended.py",
    "docs/contracts/pack_night_go_receipt.md",
    "tests/test_launch_window.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness tests.test_arm_readiness_schemas tests.test_night_gate tests.test_rehearse_t0_unattended tests.test_t0_rehearsal tests.test_launch_window tests.test_docs_freshness > /private/tmp/d176-census-cure-acceptance-resumed.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 260 tests in 451.007s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^OK$"
      }
    },
    {
      "id": "V2",
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
    }
  ],
  "flags": []
}
```

## Change

GO fixture authoring now runs inside the temporary launcher checkout. Both identity checks remain real, and the relocation/content-change assertions remain intact. No commit.

| Item | Implementation | Tests | Counterfactual |
|---|---|---|---|
| 1 | `arm_readiness.py:237,279`; inventory `:6` | `test_arm_readiness_schemas.py:1724,1740` — census kinds and non-null locators | Own runs self-collide or retained custody disappears |
| 2 | `arm_readiness.py:9863`; `night_gate.py:849`; fixture `test_launch_window.py:907` | `test_arm_readiness.py:2622`; `test_launch_window.py:976` | Wrong checkout launches, or valid original-root launch fails |
| 3 | `arm_readiness.py:9876`; `night_gate.py:849` | `test_arm_readiness.py:2614,2631` — containment and prefix refusals | Inventoried or improperly named clone rehearses |
| 4 | `arm_readiness.py:253`; preparation `night_gate.py:698`; loader `rehearse_t0_unattended.py:108` | `test_rehearse_t0_unattended.py:36,52,85`; `test_arm_readiness.py:2539` | Local HEAD replaces reviewed inventory or measurement pin is ignored |
| 5 | Shared resolver and consumer census | `test_arm_readiness.py:2611,2440`; `test_rehearse_t0_unattended.py:21` | Existing rehearsal runs self-collide, or incomplete census passes |
| 6 | Existing shared-prefix and missing-pack branches | `test_arm_readiness.py:2502,2522` | Gate/consumer prefix or refusal details diverge |

The full named-test clause map is in contract §9.2.

## Verification notes

The previous fixture failure is resolved. [Acceptance log](/private/tmp/d176-census-cure-acceptance-resumed.log).

The §6 amendment and replacement census table remain within §10.4, respecting the section restriction. No G6 derivation edit to `joulewise/t0_rehearsal.py` was needed. Ready for lead review; live gates remain lead-owned.