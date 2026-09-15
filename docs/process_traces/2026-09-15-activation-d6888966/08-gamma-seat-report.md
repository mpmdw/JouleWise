```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Repaired GAMMA root keys; both defect regressions pass after failing before the fix; combined verification has two sandbox-related census failures.",
  "workspace": {
    "base_requested": "664b3f6c",
    "base_mode": "exact",
    "head_start": "664b3f6c3a9559bc120f34e1fd76778598f5275a",
    "head_end": "664b3f6c3a9559bc120f34e1fd76778598f5275a",
    "upstream_end": "e42949dc61f8d6ffe45cd3b42216768e31166030",
    "branch": "fix/2026-09-15-gamma-root-keys"
  },
  "pathspec": [
    "configs/campaigns/d117_contrast_v5/generate_configs.py",
    "tests/test_d117_contrast_v5_pack.py",
    "tests/test_arm_readiness_evidence_t0.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1-before-fix",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_generated_plan_tree_uses_canonical_root_leaf_keys tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_generated_gamma_roots_pass_and_legacy_keys_are_refused",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 2 tests in 0.879s",
          "",
          "FAILED (failures=1, errors=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=1, errors=1\\)"
      }
    },
    {
      "id": "V2-after-fix",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_d117_contrast_v5_pack.D117ContrastV5PackTests.test_generated_plan_tree_uses_canonical_root_leaf_keys tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_generated_gamma_roots_pass_and_legacy_keys_are_refused",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 2 tests in 0.890s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V3-requested-modules",
      "kind": "suite",
      "cmd": "export TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1\nset -o pipefail\npython3 -B -m unittest tests.test_d117_contrast_v5_pack tests.test_arm_readiness_evidence_t0 2>&1 | tail -3",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 121 tests in 372.446s",
          "",
          "FAILED (failures=2, skipped=1)"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V4-pack-module-isolation",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest -f tests.test_d117_contrast_v5_pack",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 45 tests in 12.213s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V5-t0-failure-isolation",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest -f tests.test_arm_readiness_evidence_t0",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 21 tests in 123.195s",
          "",
          "FAILED (failures=1, skipped=1)"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V6-census-failure-reproduction",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_g4_real_ruled_census_pgrep_dialect",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: 3 != 0 : sysmon request failed with error: sysmond service not found",
          "pgrep: Cannot get process list",
          "Ran 1 test in 1.315s",
          "",
          "FAILED (failures=2)"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V7-small-floor-generator-pins",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_d117_floor_qwen25_1p5b_plan.D117FloorQwen251p5BPlanTests.test_exact_inventory_and_content_hashes tests.test_d117_floor_qwen25_1p5b_plan.D117FloorQwen251p5BPlanTests.test_plan_sidecars_and_embedded_hashes_recompute",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 2 tests in 0.017s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V8-large-floor-generator-pins",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_d117_floor_qwen25_7b_plan.D117Qwen25SevenBPlanTests.test_exact_inventory_hashes_and_sidecars",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 0.005s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V9-historical-gamma-generator-pins",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_d117_decode_contrast_plan.D117GammaPlanTest.test_exact_inventory_and_exact_primary_hashes tests.test_d117_decode_contrast_plan.D117GammaPlanTest.test_all_configs_and_embedded_hashes_recompute",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 2 tests in 0.015s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V10-gamma-registration-bytes",
      "kind": "test",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_d165_dominance_closeout.D165DominanceCloseoutTests.test_generator_imports_shared_core_and_registration_bytes_match_v2",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 0.000s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    },
    {
      "id": "V11-inventory",
      "kind": "smoke",
      "cmd": "TMPDIR=/tmp PYTHONDONTWRITEBYTECODE=1 python3 -B configs/campaigns/d117_contrast_v5/generate_configs.py --panel configs/model_panels/qwen3_4bit.json --model-a qwen3-1p7b --model-b qwen3-8b --prefill-length 512 --output-root /tmp/magistrate-d6888966/gamma-inventory",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "generation failed: prefill_prompt_pin_unresolved: the selected G2-a length needs an explicit hash-bound prompt pin"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "prefill_prompt_pin_unresolved"
      }
    },
    {
      "id": "V12-diff",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The combined run has two failures. The existing G4 census test reproduces two failing subcases because sandboxed pgrep cannot obtain the process list. No bypass or census-test change was attempted.",
      "needs": "Lead verification of the requested modules in the approved environment where the real process-census probe functions."
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "origin/main advanced two commits during this session; this worktree HEAD remained at the exact requested base.",
      "needs": "Lead integration review against the current target."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Inventory generation still refuses without an explicit hash-bound prefill prompt pin. Fixture checks do not establish live pack readiness.",
      "needs": ""
    }
  ]
}
```

## Change

Renamed the GAMMA plan-tree root keys and added exact-mapping and real `_root_observation` regressions. Only authorized files changed; no commit.

**Pre-edit census:** `rg -n 'claim_leaf|bound_leaf' joulewise scripts tests configs` found **no production reader of old keys under `roots`**. Each relevant hit:

- `joulewise/arm_readiness.py:8506–8521`: local variables and canonical `roots` reads; old-key reads at 8513–8514 belong to **`root_namespace`**.
- `configs/campaigns/d117_contrast_v5/generate_configs.py:2697`: defective emitter, now repaired.
- `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v1/generate_configs.py:1708`: historical emitter.
- `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v2/generate_configs.py:1708`: historical emitter.
- `configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py:1852`: historical emitter.
- Each corresponding v1, v2, and v3 `plan_tree.json:938–939`: stored old-key mappings.
- No pre-edit hits in `scripts/` or `tests/`.

## Verification notes

Before the fix, the exact-mapping assertion failed and T-0 raised the expected frozen-leaf error. Afterward, both passed, including explicit rejection of the legacy mapping.

No fixed SHA pin for the v5 generator source was found. All six targeted historical hash/registration checks passed.

The combined run remains non-green: the isolated existing G4 test reproduces both browser/monitor failures because `pgrep` cannot access the process list. The cited scout report was absent from this checkout.

## Residual risk

Full pack readiness still requires the prompt pin and lead-owned verification. Next step: lead reviews the three-file diff and reruns the requested modules where the census probe functions.