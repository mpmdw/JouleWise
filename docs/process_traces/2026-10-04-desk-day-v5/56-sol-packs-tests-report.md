```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "F1/F2 fixed; 432 tests and 1268 subtests passed across 15 modules, with two existing skips. Patch left uncommitted.",
  "workspace": {
    "base_requested": "196e532c",
    "base_mode": "exact",
    "head_start": "196e532c6b876cf992e8114d32896828e79a93f5",
    "head_end": "196e532c6b876cf992e8114d32896828e79a93f5",
    "upstream_end": "196e532c6b876cf992e8114d32896828e79a93f5",
    "branch": "desk/2026-10-04-v5-pin-and-packs"
  },
  "pathspec": [
    "tests/test_d117_floor_qwen25_1p5b_plan.py",
    "tests/test_campaign_generator_core.py"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-pktests/runtime:. TMPDIR=/tmp/dd5-pktests/tmp /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider -o cache_dir=/tmp/dd5-pktests/pc tests/test_d117_floor_qwen25_1p5b_plan.py tests/test_campaign_generator_core.py tests/test_d117_contrast_v5_pack.py tests/test_d117_floor_qwen3_v5_generate.py tests/test_paper_reported_energy.py tests/test_generator_head_pin_relation.py tests/test_paper_custody.py --basetemp=/tmp/dd5-pktests/pytest-primary --junitxml=/tmp/dd5-pktests/primary.xml > /tmp/dd5-pktests/primary.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "170 passed, 1 warning, 709 subtests passed in 438.49s (0:07:18)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "170 passed, 1 warning, 709 subtests passed"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/tmp/dd5-pktests/runtime:. TMPDIR=/tmp/dd5-pktests/tmp /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider -o cache_dir=/tmp/dd5-pktests/pc -p dd5_progress tests/test_arm_readiness_dry_run.py tests/test_arm_readiness_evidence_author.py tests/test_arm_readiness_integration.py tests/test_arm_readiness_lifecycle.py tests/test_arm_readiness_registry.py tests/test_family_marker.py tests/test_launch_window.py tests/test_receipt_histsem.py --basetemp=/tmp/dd5-pktests/pytest-readers --junitxml=/tmp/dd5-pktests/readers.xml > /tmp/dd5-pktests/readers.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "262 passed, 2 skipped, 41 warnings, 559 subtests passed in 4910.21s (1:21:50)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "262 passed, 2 skipped, 41 warnings, 559 subtests passed"
      }
    },
    {
      "id": "V3",
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
      "kind": "environment",
      "level": "nonblocking",
      "text": "Git staging failed with exit 128 because the sandbox denied creation of the worktree index.lock. The verified changes remain unstaged and uncommitted; no repository push was attempted.",
      "needs": ""
    }
  ]
}
```

## Change

Replaced the absence sentinel with committed registration-ordering verification at the declared pack length, retaining mutation checks. Added the emitted contrast generator to the live census and shared-core checks. No additional tests needed changes.

## Verification notes

The existing skips cover a synthetic fixture missing its publication marker and an unminted successor pinset. Warnings concern the prescribed cache option and existing tar-extraction deprecation.

Scratch artifacts remain under `/tmp/dd5-pktests/`. The sandbox blocked Git staging; the two-file patch is ready for lead review and commit.