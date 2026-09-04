```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented a registry-derived D-151 authenticator-path guard with current-class and novel-name counterfactual regressions.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "head_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "upstream_end": "849915bc1393a6c1cb962a4dc12b25c33dad1f74",
    "branch": "feat/2026-09-04-fan-AUTHENTICATOR-ALLOWLIST-GUARD-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/AUTHENTICATOR-ALLOWLIST-GUARD-01/01-sol-report.md",
    "joulewise/arm_readiness.py",
    "tests/test_arm_readiness_schemas.py"
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
      "cmd": "python3 -m unittest tests.test_arm_readiness_schemas",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 38 tests in 0.161s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 38 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 - <<'PY'\nimport unittest\nfrom unittest import mock\n\nimport joulewise.arm_readiness as readiness\nfrom tests.test_arm_readiness_schemas import ArmReadinessSchemaTests\n\ncase = ArmReadinessSchemaTests(\n    \"test_newly_registered_authenticator_name_is_refused_in_allowlist\"\n)\nresult = unittest.TestResult()\nwith mock.patch.object(\n    readiness, \"_r1_authenticator_allowlist_conflicts\", return_value=[]\n):\n    case.run(result)\nfailures = result.failures + result.errors\nif len(failures) != 1:\n    raise SystemExit(\n        f\"counterfactual expected one failing regression, observed {len(failures)}\"\n    )\nprint(\"counterfactual_guard_disabled: expected regression failure observed\")\nprint(failures[0][1].splitlines()[-1])\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "counterfactual_guard_disabled: expected regression failure observed",
          "AssertionError: ArmReadinessError not raised"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "counterfactual_guard_disabled: expected regression failure observed\\nAssertionError: ArmReadinessError not raised"
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
  "flags": []
}
```

## Change

The forcing problem was that the schema test named the known confirmation-table and family-publication path fragments directly. That proved only those spellings absent; a later authenticator role could enter the irrelevant-path allowlist without tripping the test.

The implementation adds one code-side registry whose records carry family, type, and role. Registry validation normalizes each registered role and each candidate repository path, then refuses a collision with `readiness_row_registry_mismatch`. Punctuation normalization makes an underscore-delimited role cover an equivalent hyphen-delimited filename. The tracked 112-path allowlist ruled by D-151 condition 1 is byte-unchanged.

| ID | Finding or decision | Evidence | Disposition |
|---|---|---|---|
| F1 | The prior guard was two literal substring assertions. | S9-09 and the removed assertions in `tests/test_arm_readiness_schemas.py`. | Replaced by registry-derived production validation. |
| D1 | Changing `d117_row_registry_v2.json` would alter campaign registry bytes even though the row authorizes guard strength only. | Kernel fence and D-151 clause 7. | Kept the authenticator-class registry in code; no allowlist or campaign configuration entry changed. |
| D2 | A role, rather than a filename, is the stable class identifier. | The R1 family/type/role convention and D-151's all-future-transactions rule. | Normalize role and path punctuation before substring comparison. |
| T1 | A new spelling must fail without adding another named assertion. | The regression registers `FUTURE_CONFIRMATION_TOKEN` and proposes `future-confirmation-token.json`. | Validation refuses it; disabling the guard makes that regression fail with `ArmReadinessError not raised`. |
| H1 | No hardware, operator action, or pending dependency is part of this row. | Kernel dependencies are empty and the acceptance is a schema guard plus tests. | Desk acceptance is complete. |
| B1 | Kernel and generated queue/run-state closure are magistrate-owned by the prompt. | Explicit preflight prohibition. | Magistrate next marks `AUTHENTICATOR-ALLOWLIST-GUARD-01` complete in the state kernel and regenerates its projections after harvest. |

Worked example: if a later transaction registers role `FUTURE_CONFIRMATION_TOKEN`, a proposed path ending in `future-confirmation-token.json` normalizes to the same class spelling and is refused before the lifecycle registry can load.

## Verification notes

The repository-wide suite was intentionally not run under the preflight rule. V2 is an expected-red mutation check wrapped as a successful verification command: it disables the new conflict detector in memory and confirms the novel-name regression fails for the intended reason.
