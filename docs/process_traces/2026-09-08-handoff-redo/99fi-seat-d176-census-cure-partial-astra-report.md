```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Installed the census cure; named acceptance found one out-of-scope launcher-fixture mismatch.",
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
    "docs/contracts/pack_night_go_receipt.md"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness tests.test_arm_readiness_schemas tests.test_night_gate tests.test_rehearse_t0_unattended tests.test_t0_rehearsal tests.test_launch_window tests.test_docs_freshness > /private/tmp/d176-census-cure-acceptance.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 260 tests in 438.222s",
          "FAILED (failures=1)"
        ]
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
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "Required acceptance failed at tests/test_launch_window.py:1015: test_real_minted_v4_go_binds_root_and_refuses_content_change expected success but received launch_go_receipt_invalid with detail measurement_root: launcher is not the planned clone. This test is outside WRITE_SCOPE and was preserved.",
      "needs": "Authorize the fixture correction in tests/test_launch_window.py or assign it to the lead, then rerun named acceptance."
    }
  ],
  "scope_expansion": {
    "requested_paths": ["tests/test_launch_window.py"],
    "reason": "The production relocation fixture must satisfy the newly required launcher identity.",
    "blocked_work": "Repair the failing fixture and obtain passing named acceptance.",
    "minimal_change": "Align the fixture's planned measurement_root with the checkout executing its launcher and refresh the affected GO bindings."
  }
}
```

## Change

Installed items 1–6 and their detailed clause map in contract §9.2/§10.4. No commit.

| Item | Implementation | Regression | Counterfactual |
|---|---|---|---|
| 1 | `arm_readiness.py:237,279`; inventory `:6` | No process-derived census; every non-null locator retained | Own runs self-collide or deployment custody disappears |
| 2 | `arm_readiness.py:9863`; `night_gate.py:849` | Launcher mismatch at both sites | Another checkout launches the plan |
| 3 | Both purpose/root validators | Inventoried containment and prefix refusals | Production or improperly named clone rehearses |
| 4 | `arm_readiness.py:253`; gate preparation; loader | Real-Git local-deletion attack; pre-ARM pin check | Local HEAD replaces reviewed inventory |
| 5 | Updated census and launch tests | Real resolver, shipped inventory, existing rehearsal runs | Mocked census conceals self-collision |
| 6 | Existing shared prefix and missing-pack branches | Both existing nit regressions retained | Gate/consumer reason or prefix diverges |

## Verification notes

Acceptance finished with **259 passing tests and one failure**, documented above. Stopped after acceptance as requested. [Full log](/private/tmp/d176-census-cure-acceptance.log).

The §6 amendment and replacement census table reside within §10.4 to respect the final section restriction. No G6 derivation change required editing `joulewise/t0_rehearsal.py`.

Next step: authorize or apply the out-of-scope launcher-fixture correction, then repeat named acceptance.