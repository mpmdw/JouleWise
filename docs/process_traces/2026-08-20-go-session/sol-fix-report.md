```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Seeded committed MINT-custody fixtures for post-mint successor checks and added a fail-closed missing-output regression.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "afb7d5705add3475cd016177a8f8fa1dd02a814e",
    "head_end": "afb7d5705add3475cd016177a8f8fa1dd02a814e",
    "upstream_end": "afb7d5705add3475cd016177a8f8fa1dd02a814e",
    "branch": "impl/r2-s0-mint-resolver"
  },
  "pathspec": [
    "tests/test_d117_v3_family.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d117_v3_family -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 5 tests in 8.189s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 5 tests in .*s[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p \"test_arm_readiness*.py\" -v > /private/tmp/joulewise-arm-readiness-neighborhood-20260820.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 181 tests in 250.524s",
          "OK (skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 181 tests in .*s[\\s\\S]*OK \\(skipped=1\\)"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Finalized-pack custody traversal is duplicated inside three frozen generators, coupling generator-output checks to later MINT artifacts.",
      "needs": ""
    }
  ]
}
```

## Change

Root cause: [`plan_arm_readiness_attachment()`](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/wtGO/joulewise/arm_readiness.py:2849) scans the canonical `_v3` pack with `allow_absent=True`. Since freeze-0003 now exists, regenerated plan trees correctly contain its committed pin. The frozen checkers then unconditionally dereference that pin under the bare `check_root`:

- [1.5B checker](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/wtGO/configs/campaigns/d117_floor_qwen25_1p5b_v2/generate_configs.py:2574)
- [7B checker](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/wtGO/configs/campaigns/d117_floor_qwen25_7b_v2/generate_configs.py:2813)
- [contrast checker](/private/tmp/claude-501/-Users-edr-code-JouleWise/36a806b2-a55e-4823-9a50-f8bbe26e8f31/scratchpad/wtGO/configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v2/generate_configs.py:2223)

The test now explicitly overlays the four committed MINT-custody directories after generator emission and before finalized-pack checking. It first asserts those directories were not emitted, proving receipt ownership remains outside the generator.

This was chosen over changing `arm_readiness.py`: suppressing an existing committed receipt would produce a false plan attachment and weaken authenticated regeneration. Editing the inline checker would be cleaner structurally but would violate the frozen, byte-pinned pack constraint.

The attack regression deletes generator-owned `order_manifest.json` after custody seeding and verifies `--check` still fails with `missing=order_manifest.json`. Existing r6 assertions, generator hashes, and committed v2 tree-digest checks remain intact.

## Verification notes

No failures or deviations. The complete 202-line neighborhood output is preserved in [joulewise-arm-readiness-neighborhood-20260820.log](/private/tmp/joulewise-arm-readiness-neighborhood-20260820.log). `git diff --check` also passed.

## Residual risk

The three frozen generators contain near-duplicate finalized-inventory logic. That duplication is the seam smell, but changing it would require modifying prohibited frozen pack content; it is not a blocker for this repair.