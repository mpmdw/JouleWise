```json
{
 "schema": "claude-codex-report/v1",
 "genre": "implementation",
 "status": "clean",
 "completion": "complete",
 "summary": "Three v5 packs regenerated at 75 s; GAMMA reference IDs fixed; requested checks passed. Uncommitted.",
 "workspace": {
  "base_requested": "b2ff2f36",
  "base_mode": "exact",
  "head_start": "b2ff2f3632e916bc4b7d3cccd037b52e19c34c01",
  "head_end": "b2ff2f3632e916bc4b7d3cccd037b52e19c34c01",
  "upstream_end": "b2ff2f3632e916bc4b7d3cccd037b52e19c34c01",
  "branch": "feat/2026-10-05-v5-packs-idle75"
 },
 "pathspec": [
  "configs/campaigns/d117_floor_qwen3-1p7b_v5/calibration_plan.json",
  "configs/campaigns/d117_floor_qwen3-1p7b_v5/calibration_plan.sha256",
  "configs/campaigns/d117_floor_qwen3-1p7b_v5/extraction_spec.json",
  "configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py",
  "configs/campaigns/d117_floor_qwen3-1p7b_v5/order_manifest.json",
  "configs/campaigns/d117_floor_qwen3-1p7b_v5/plan_tree.json",
  "configs/campaigns/d117_floor_qwen3-1p7b_v5/plan_tree.sha256",
  "configs/campaigns/d117_floor_qwen3-1p7b_v5/producer_contract.json",
  "configs/campaigns/d117_floor_qwen3-1p7b_v5/0[1-6]*/*.json",
  "configs/campaigns/d117_floor_qwen3-8b_v5/calibration_plan.json",
  "configs/campaigns/d117_floor_qwen3-8b_v5/calibration_plan.sha256",
  "configs/campaigns/d117_floor_qwen3-8b_v5/extraction_spec.json",
  "configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py",
  "configs/campaigns/d117_floor_qwen3-8b_v5/order_manifest.json",
  "configs/campaigns/d117_floor_qwen3-8b_v5/plan_tree.json",
  "configs/campaigns/d117_floor_qwen3-8b_v5/plan_tree.sha256",
  "configs/campaigns/d117_floor_qwen3-8b_v5/producer_contract.json",
  "configs/campaigns/d117_floor_qwen3-8b_v5/0[1-6]*/*.json",
  "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/analysis_manifest_v3.json",
  "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/calibration_plan.json",
  "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/calibration_plan.sha256",
  "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/generate_configs.py",
  "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/order_manifest.json",
  "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/plan_tree.json",
  "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/plan_tree.sha256",
  "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/0[1-4]*/*.json",
  "configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/references/*/*.json",
  "configs/campaigns/neg8_reference_corpus/neg8-refcorpus-r*.json",
  "configs/campaigns/window_references/*/neg8-window-*.json",
  "configs/campaigns/d117_contrast_v5/generate_configs.py",
  "tests/test_d117_contrast_v5_pack.py",
  "tests/test_d117_decode_contrast_plan.py",
  "tests/test_d117_floor_qwen3_v5_generate.py",
  "tests/test_gen_g2_phase_d.py",
  "tests/test_v5_pack_regen.py"
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
   "cmd": "TMPDIR=/tmp/dd5-regen PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_d117_*v5*.py tests/test_d165_rationale_census.py tests/test_gen_g2_phase_d.py tests/test_d117_decode_contrast_plan.py tests/test_v5_pack_regen.py > /tmp/dd5-regen/stable-focused-tests.log 2>&1",
   "cwd": ".",
   "observed": {
    "result": "pass",
    "exit_code": 0,
    "tail": ["121 passed, 1 skipped, 364 subtests passed in 433.70s (0:07:13)"]
   },
   "expected": {
    "exit_code": 0,
    "tail_regex": "121 passed, 1 skipped.*364 subtests passed"
   }
  },
  {
   "id": "V2",
   "kind": "inspection",
   "cmd": "python3 -B /tmp/dd5-regen/verify_delta.py",
   "cwd": ".",
   "observed": {
    "result": "pass",
    "exit_code": 0,
    "tail": ["PASS 299 existing members, 3 distinct interior reference run IDs, all pin bytes and 4 estimator files unchanged; only idle, reference identities/dispatch and covering hashes differ"]
   },
   "expected": {
    "exit_code": 0,
    "tail_regex": "PASS 299 existing members"
   }
  },
  {
   "id": "V3",
   "kind": "test",
   "cmd": "TMPDIR=/tmp/dd5-regen PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python configs/campaigns/d117_floor_qwen3-1p7b_v5/generate_configs.py --no-preserve-current-frozen-bytes --check",
   "cwd": ".",
   "observed": {
    "result": "pass",
    "exit_code": 0,
    "tail": ["verified d117_floor_qwen3-1p7b_v5 unfrozen draft: 100 science configs; calibration_plan_sha256=9128800eb9fe14bbc1335f07df406b2d7781b2a9b6704543a249387645d2ab07; plan_tree_sha256=6a609c8616796a8142285a4117b76a477075591482884d393619589c88d14510"]
   },
   "expected": {
    "exit_code": 0,
    "tail_regex": "verified.*100 science configs"
   }
  },
  {
   "id": "V4",
   "kind": "test",
   "cmd": "TMPDIR=/tmp/dd5-regen PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python configs/campaigns/d117_floor_qwen3-8b_v5/generate_configs.py --no-preserve-current-frozen-bytes --check",
   "cwd": ".",
   "observed": {
    "result": "pass",
    "exit_code": 0,
    "tail": ["verified d117_floor_qwen3-8b_v5 unfrozen draft: 100 science configs; calibration_plan_sha256=246af3753007fddbd14f655acfd7f3149e918edc93cd9a7392368ecf93887594; plan_tree_sha256=29b756f6cb2f18c13ab1e72824559ae33ad6a7154b6a6e4da9518ec5c5cb6351"]
   },
   "expected": {
    "exit_code": 0,
    "tail_regex": "verified.*100 science configs"
   }
  },
  {
   "id": "V5",
   "kind": "test",
   "cmd": "TMPDIR=/tmp/dd5-regen PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python configs/campaigns/d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5/generate_configs.py --no-preserve-current-frozen-bytes --check",
   "cwd": ".",
   "observed": {
    "result": "pass",
    "exit_code": 0,
    "tail": ["checked D-117 gamma d117_contrast_qwen3-1p7b_vs_qwen3-8b_v5: decode_members=40 prefill_p2048_members=40 plan_sha256=75fe8d58462ebdd1a258ec6dad2784d384588b5a42f5a8dc567d539cc9c4ec40 tree_sha256=fa88a09cb5b69ca61fdbb55b3b77d7116f02b416d2b1e9fcd8da4c311b1f68ad"]
   },
   "expected": {
    "exit_code": 0,
    "tail_regex": "checked D-117 gamma.*decode_members=40 prefill_p2048_members=40"
   }
  },
  {
   "id": "V6",
   "kind": "test",
   "cmd": "PATH=/Users/edr/code/JouleWise/.venv/bin:$PATH python -B scripts/gen_g2_phase_d.py --check",
   "cwd": ".",
   "observed": {
    "result": "pass",
    "exit_code": 0,
    "tail": ["PASS generated Phase D matches pinned runbook bytes"]
   },
   "expected": {
    "exit_code": 0,
    "tail_regex": "PASS generated Phase D matches pinned runbook bytes"
   }
  },
  {
   "id": "V7",
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
  },
  {
   "id": "V8",
   "kind": "test",
   "cmd": "TMPDIR=/tmp/dd5-regen PYTHONPATH=. PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -B /tmp/dd5-regen/mutate_idle.py",
   "cwd": ".",
   "observed": {
    "result": "pass",
    "exit_code": 0,
    "tail": ["PASS mutation: the generation regression rejects idle_seconds=30"]
   },
   "expected": {
    "exit_code": 0,
    "tail_regex": "PASS mutation"
   }
  }
 ],
 "flags": []
}
```

## Change

Set idle to 75 at the generators and committed reference sources, then regenerated all three packs from the committed p2048 pin. GAMMA retains the s1 midpoint route and generates distinct arm-boundary and prefill-midpoint references.

The rendered s1 roster has 23 unique IDs; full GAMMA has 101. [Diff proof](/tmp/dd5-regen/delta-proof.json) confirms unchanged workload text, token IDs, lengths, output budgets, model IDs, pin bytes, and estimator files. [Expanded changed paths](/tmp/dd5-regen/modified-paths.txt).

Changes remain uncommitted; nothing was pushed. Next: lead diff review.

## Verification notes

The historical v1 test reconstructs only the old idle field to verify its frozen source hashes. D-165 allowlist lines did not move.

This config/generator task used the requested focused checks under the tooling-only exception; canonical unittest discovery was not run.