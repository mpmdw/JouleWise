```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "The ruled re-scope is complete: generic freeze/arm roster machinery is retired and one generator-boundary mutation proves the retained active-gamma fence.",
  "workspace": {
    "base_requested": "f545908c",
    "base_mode": "exact",
    "head_start": "f545908c3f3a6d47a79fc6a6cc4f1f6189486680",
    "head_end": "f545908c3f3a6d47a79fc6a6cc4f1f6189486680",
    "upstream_end": "f545908c3f3a6d47a79fc6a6cc4f1f6189486680",
    "branch": "feat/2026-09-04-fan-GAMMA-UNIT-ROSTER-GUARD-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/GAMMA-UNIT-ROSTER-GUARD-01/07-sol-rescope-report.md",
    "joulewise/arm_readiness.py",
    "joulewise/identity_pins.py",
    "tests/test_gamma_unit_roster_guard.py"
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
      "cmd": "python3 - <<'PY'\nimport unittest\nfrom unittest import mock\nfrom tests import test_d117_contrast_v5_pack as v5\nfrom tests import test_gamma_unit_roster_guard as roster\n\ngenerator = v5.load_generator()\ncase = roster.GammaUnitRosterGuardTests(\n    \"test_generate_refuses_coherent_roster_rewrite_before_tree_publish\"\n)\nwith (\n    mock.patch.object(generator, \"validate_gamma_identity_unit_roster\", return_value=None),\n    mock.patch.object(v5, \"load_generator\", return_value=generator),\n):\n    result = unittest.TestResult()\n    case.run(result)\nprint(\n    f\"counterfactual_result={'fail' if result.failures else 'pass'} \"\n    f\"testsRun={result.testsRun} failures={len(result.failures)} errors={len(result.errors)}\"\n)\nif result.testsRun != 1 or len(result.failures) != 1 or result.errors:\n    raise SystemExit(1)\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "counterfactual_result=fail testsRun=1 failures=1 errors=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "counterfactual_result=fail testsRun=1 failures=1 errors=0"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_gamma_unit_roster_guard",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 0.353s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test in .*s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --check && git diff --quiet -- configs/campaigns/d117_contrast_qwen25_1p5b_vs_7b_v3/generate_configs.py && ! rg -n 'D131_GAMMA_IDENTITY_UNIT_ROSTER|validate_d131_gamma_identity_unit_roster|ordered D-131 gamma unit roster' joulewise/identity_pins.py joulewise/arm_readiness.py tests/test_gamma_unit_roster_guard.py",
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

The adopted Q4 ruling maps to the final tree as follows:

| Ruling clause | File:line installation |
|---|---|
| D-131 roster completeness stays a pre-registration/evidence invariant; coherent trusted-operator rewrites are outside D-161. | `configs/campaigns/d117_contrast_v5/generate_configs.py:2825` owns the exact ordered-roster and directional producer check. |
| Remove generic runtime D-131 dispatch. | `joulewise/identity_pins.py:500` is family-neutral again and returns after generic projection checks at `joulewise/identity_pins.py:574`; the D-131 constant, dispatcher, and call are removed. |
| Remove freeze/arm hooks; arm authenticates receipt against reviewed pack. | `joulewise/identity_pins.py:2400` verifies the frozen pack/receipt binding without a roster hook; `joulewise/arm_readiness.py:5645` and `joulewise/arm_readiness.py:5779` compare authenticated receipt fields to the pack and reviewed HEAD without a duplicated roster constant. |
| Keep the active gamma generator's unconditional exact-roster fence. | `configs/campaigns/d117_contrast_v5/generate_configs.py:3232` calls the exact check immediately after `build_tree` and before serialization/publication at `:3233`. |
| Acceptance is one C/D rename plus complete A/B producer-pair swap that refuses before publishing `plan_tree.json`. | `tests/test_gamma_unit_roster_guard.py:13` contains the sole acceptance test; mutation is at `:24`, refusal at `:41`, and pre-publication assertion at `:51`. |
| On green, retire GAMMA-UNIT-ROSTER-GUARD-01 as superseded by the generator-owned check. | The mission-only runtime machinery and its five retired tests are removed; this report records green acceptance. Magistrate-owned state installation remains with the lead. |

The historical v3 generator remains byte-untouched, as required by the consult; it has no worktree diff.

## Verification notes

Per the mission preflight rule, only `tests.test_gamma_unit_roster_guard` was run. V1 disables the active generator fence in memory and observes the acceptance test fail; V2 restores production behavior and passes. No hardware or quiet-machine work was performed.
