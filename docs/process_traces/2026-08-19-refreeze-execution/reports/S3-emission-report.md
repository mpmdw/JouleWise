```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Emitted all three D-117 v3 drafts bound to r6; focused S3 checks pass and v1/v2 bytes are preserved.",
  "workspace": {
    "base_requested": "6f00d05",
    "base_mode": "exact",
    "head_start": "6f00d0545d986370b9c4bc73619d727989d42af5",
    "head_end": "6f00d0545d986370b9c4bc73619d727989d42af5",
    "upstream_end": "6f00d0545d986370b9c4bc73619d727989d42af5",
    "branch": "impl/r2-s0-mint-resolver"
  },
  "pathspec": [
    "configs/campaigns/d117_floor_qwen25_1p5b_v3/**",
    "configs/campaigns/d117_floor_qwen25_7b_v3/**",
    "configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/**",
    "configs/floor_mint/d117_qwen25_1p5b_v3_extraction_spec.json",
    "configs/floor_mint/d117_qwen25_7b_v3_extraction_spec.json",
    "tests/test_d117_v3_family.py"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d117_v3_family",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 4 tests in 9.491s", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 4 tests.*OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d117_floor_qwen25_1p5b_plan",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 21 tests in 11.842s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 21 tests.*OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d117_floor_qwen25_7b_plan",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 20 tests in 11.676s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 20 tests.*OK"}
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_d117_decode_contrast_plan",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 22 tests in 77.752s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 22 tests.*OK"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_floor_mint_estimator",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 37 tests in 2.184s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 37 tests.*OK"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_mint_floor_artifact_generalized",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 76 tests in 26.534s", "OK (skipped=2)"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 76 tests.*OK"}
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_evidence_author",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 24 tests in 49.248s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 24 tests.*OK"}
    },
    {
      "id": "V8",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 sh -c 'python3 configs/campaigns/d117_floor_qwen25_1p5b_v3/generate_configs.py --check; python3 configs/campaigns/d117_floor_qwen25_7b_v3/generate_configs.py --check; python3 configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py --check'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["alpha verified: 100 science configs", "beta check passed: 100 science configs, 6 floor cells, 3 reporting cells", "gamma checked: decode_members=40 prefill_p256_members=40"]},
      "expected": {"exit_code": 0, "tail_regex": "verified|check passed|checked"}
    },
    {
      "id": "V9",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 sh -c 'python3 configs/campaigns/d117_floor_qwen25_1p5b_v2/generate_configs.py --check --preserve-current-frozen-bytes; python3 configs/campaigns/d117_floor_qwen25_7b_v2/generate_configs.py --check --preserve-current-frozen-bytes; python3 configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v2/generate_configs.py --check --preserve-current-frozen-bytes'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["alpha frozen by d134 receipt", "beta frozen by d134 receipt", "gamma checked"]},
      "expected": {"exit_code": 0, "tail_regex": "frozen by d134 receipt|checked"}
    },
    {
      "id": "V10",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 sh -c 'python3 configs/campaigns/d117_floor_qwen25_1p5b_v1/generate_configs.py --check; python3 configs/campaigns/d117_floor_qwen25_7b_v1/generate_configs.py --check; python3 configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/generate_configs.py --check'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["alpha verified", "beta check passed", "gamma checked"]},
      "expected": {"exit_code": 0, "tail_regex": "verified|check passed|checked"}
    },
    {
      "id": "V11",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["clean"]},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The requested two evidence-author reds were not observed: tests.test_arm_readiness_evidence_author is 24/24 OK. No v3 evidence or freeze artifacts were authored.",
      "needs": "Confirm only if the expected reds referred to a separate S4 production-authoring invocation."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The canonical 2770-test suite was not accepted in this S3 run; it belongs to the later S6 full-green gate and includes known long exclusive modules.",
      "needs": "Lead runs the canonical suite at the integration/S6 gate."
    }
  ]
}
```

## Change

Emitted and self-regenerated the r6-bound `_v3` family. Both floor generators derive their allowance from `acceptance_pin()` through `acceptance_allowance_rule`; no r2 binding or `0.010818` allowance residue remains in `_v3`.

| Emitted output | Files |
|---|---:|
| `d117_floor_qwen25_1p5b_v3` | 117 |
| `d117_floor_qwen25_7b_v3` | 117 |
| `d117_contrast_qwen25_1p5b_vs_7b_v3` | 98 |
| Two floor extraction specs | 2 |
| Total | 334 |

Added [test_d117_v3_family.py](/private/tmp/claude-501/-Users-edr-code-JouleWise/cbd9b7b5-8119-4431-a348-15141e0afab9/scratchpad/wtS0/tests/test_d117_v3_family.py), covering v2→v3 emission, r6 plan/spec pins, resolver-derived allowance rules, v1/v2 replay values, and committed v2 tree digests.

## Verification notes

The evidence-author module is green, rather than retaining the two reds described in the request. This is classified as baseline drift; no production evidence-authoring command was run.

## Residual risk

All `_v3` packs remain unfrozen and have no authored evidence or freeze receipts, as required. The next route is S4 evidence re-authoring at the measurement checkout.