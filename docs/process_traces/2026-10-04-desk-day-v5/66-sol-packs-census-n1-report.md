```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "partial",
  "summary": "Both fixes implemented and all requested tests passed; canonical suite interrupted; changes remain uncommitted.",
  "workspace": {
    "base_requested": "ca5f3f11",
    "base_mode": "exact",
    "head_start": "ca5f3f11fea2d9e578a34664687af96e73de0cae",
    "head_end": "ca5f3f11fea2d9e578a34664687af96e73de0cae",
    "upstream_end": "ca5f3f11fea2d9e578a34664687af96e73de0cae",
    "branch": "desk/2026-10-04-v5-pin-and-packs"
  },
  "pathspec": [
    "tests/fixtures/d165_rationale_allowlist.json",
    "tests/test_d117_contrast_v5_pack.py",
    "configs/campaigns/d117_contrast_v5/generate_configs.py",
    "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/0[1-4]*/*.json",
    "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/README.md",
    "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/analysis_manifest_v3.json",
    "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/calibration_plan.json",
    "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/calibration_plan.sha256",
    "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/generate_configs.py",
    "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/order_manifest.json",
    "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/plan_tree.json",
    "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/plan_tree.sha256",
    "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/prefill_prompt_candidate.json"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "build",
      "cmd": "TMPDIR=/tmp/dd5-pkn1 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python configs/campaigns/d117_contrast_v5/generate_configs.py --panel configs/model_panels/qwen3_4bit.json --model-a qwen3-1p7b --model-b qwen3-8b --decode-workload configs/workloads/real_prompts_v1.json --prefill-length 2048 --prefill-prompt-pin configs/campaigns/d117_contrast_v5/prefill_pin/prefill-prompt-pin.json --no-preserve-current-frozen-bytes --output-root /tmp/dd5-pkn1/generated",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "generated D-117 gamma d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5: decode_members=40 prefill_p2048_members=40 plan_sha256=72c776bcb410d103b9ab49991e626f1c4e2ffa4fd6c2a40c67be4a1138b67da6 tree_sha256=995c7ca548c718c96ef2b44b7efa37d356ba82619f391ac6abe2ecb636d0c730"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "generated D-117 gamma.*decode_members=40 prefill_p2048_members=40"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/dd5-pkn1 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/generate_configs.py --no-preserve-current-frozen-bytes --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "checked D-117 gamma d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5: decode_members=40 prefill_p2048_members=40 plan_sha256=72c776bcb410d103b9ab49991e626f1c4e2ffa4fd6c2a40c67be4a1138b67da6 tree_sha256=995c7ca548c718c96ef2b44b7efa37d356ba82619f391ac6abe2ecb636d0c730"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "checked D-117 gamma.*decode_members=40 prefill_p2048_members=40"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/dd5-pkn1/verify_bytes.py > /tmp/dd5-pkn1/byte-proof.log",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "  \"result\": \"PASS\"",
          "}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\"result\": \"PASS\""
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-pkn1 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider -o cache_dir=/tmp/dd5-pkn1/pc tests/test_d165_rationale_census.py tests/test_d117_contrast_v5_pack.py tests/test_d117_decode_contrast_plan.py tests/test_d117_floor_qwen3_v5_generate.py tests/test_identity_pins.py > /tmp/dd5-pkn1/focused-tests.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "146 passed, 1 skipped, 1 warning, 365 subtests passed in 291.90s (0:04:51)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "146 passed, 1 skipped, 1 warning, 365 subtests passed"
      }
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-pkn1 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest discover -s tests > /tmp/dd5-pkn1/canonical-suite.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": [
          "KeyboardInterrupt"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
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
        "tail_regex": "^$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Git staging failed because the sandbox denied creation of the linked worktree index.lock. All 96 modified files remain unstaged; nothing was committed or pushed.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The additional canonical unittest run was interrupted because it substantially exceeded the bounded requested checks. No test failure was reported before interruption; no whole-suite verdict is claimed.",
      "needs": "Lead or CI must complete whole-suite verification before freeze."
    }
  ]
}
```

## Change

Verified all ten census hits reproduce the registered sentence exactly, then added exact allowlist entries at their unchanged final line numbers. Changed `_v5` status to `ISSUED-BY-G2A-PROMPT-PIN` and regenerated from the committed pin.

Member changes are limited to the 40 prefill status tags and 80 plan-hash tags. Workload text, token IDs, lengths and output budgets are byte-identical. Both floor packs’ 123 files each and all 405 historical contrast files are unchanged. [Byte proof](/tmp/dd5-pkn1/byte-proof.json); [all 96 changed paths](/tmp/dd5-pkn1/final-changed-paths.txt).

## Verification notes

No failures remain in the requested tests. No generator-authentication test files or tests containing the old plan hash were present. The warning concerns `cache_dir` with the cache provider disabled.

Whole-suite verification remains incomplete. The next step is lead diff review and a complete suite run before freeze. Changes are uncommitted because sandboxed staging was denied; nothing was pushed.