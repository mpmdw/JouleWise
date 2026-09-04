```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Re-scoped the allowlist guard to an exact code-authenticated governed-artifact manifest and removed the retired authenticator registry.",
  "workspace": {
    "base_requested": "df1fb386253b04b37546b85899e9a4eeb7f7e9fd",
    "base_mode": "exact",
    "head_start": "df1fb386253b04b37546b85899e9a4eeb7f7e9fd",
    "head_end": "df1fb386253b04b37546b85899e9a4eeb7f7e9fd",
    "upstream_end": "df1fb386253b04b37546b85899e9a4eeb7f7e9fd",
    "branch": "feat/2026-09-04-fan-AUTHENTICATOR-ALLOWLIST-GUARD-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/AUTHENTICATOR-ALLOWLIST-GUARD-01/07-sol-rescope-report.md",
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
      "cmd": "python3 -m unittest tests.test_arm_readiness_schemas.ArmReadinessSchemaTests.test_allowlist_refuses_novel_entry_absent_from_governed_artifact_provenance",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: ArmReadinessError not raised",
          "Ran 1 test in 0.004s",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "ArmReadinessError not raised[\\s\\S]*FAILED \\(failures=1\\)"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_arm_readiness_schemas.ArmReadinessSchemaTests.test_allowlist_refuses_novel_entry_absent_from_governed_artifact_provenance",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 0.002s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test[\\s\\S]*OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_arm_readiness_schemas.ArmReadinessSchemaTests.test_allowlist_refuses_novel_entry_absent_from_governed_artifact_provenance",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": [
          "AssertionError: ArmReadinessError not raised",
          "Ran 1 test in 0.003s",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "ArmReadinessError not raised[\\s\\S]*FAILED \\(failures=1\\)"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_arm_readiness_schemas",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          ".....................................",
          "Ran 37 tests in 0.109s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 37 tests[\\s\\S]*OK"
      }
    },
    {
      "id": "V5",
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
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "Implemented the magistrate-adopted Q4 re-scope verbatim; no third-round registry mechanism remains.",
      "needs": ""
    }
  ]
}
```

## Change

The candidate allowlist is now checked against a positive 112-path manifest derived from the three governed successor packs, the eleven independently replayed generic source/receipt pairs and receipt sidecars per pack, each pack's PASS freeze and plan-tree bindings, and the digest-conditional successor pinset. The canonical rendering is SHA-256 pinned in code outside the subtraction set. Any missing or additional literal path refuses before policy use.

The mutable callable registry, decorator, path-class normalizer, name-substring rejection, decorators on the two authenticators, public export, and all three tests of that retired mechanism were removed. The D-151 conditional pinset gate was preserved unchanged.

## Clause map

| Ruling clause | Production site | Biting assertion | Counterfactual |
|---|---|---|---|
| “allowlist membership is derived positively from independently authenticated governed-artifact provenance” (`06-consult-sol-structural.md:113`) | `joulewise/arm_readiness.py:637-653,1672-1715` | `tests/test_arm_readiness_schemas.py:534,542-550` | Change one governed output stem without updating the external code digest pin; registry load refuses instead of accepting a self-redefined set. |
| “any unexplained extra path refuses without classifying it by name or callable” (`06-consult-sol-structural.md:113`) | `joulewise/arm_readiness.py:1955-1962` | `tests/test_arm_readiness_schemas.py:539-550` | Replace the exact-set predicate with `if False and allowlist != derived_manifest["paths"]`; the named test fails because no exception is raised. |
| “Remove the decorator/registry landing” (`06-consult-sol-structural.md:113`) | Removed from `joulewise/arm_readiness.py`; the authenticators are plain definitions at `:11599` and `:11647` | Inspection: no `R1_AUTHENTICATOR_REGISTRY`, `_r1_authenticator`, path class, or registered-authenticator reference remains in either touched source file. | Reintroducing any retired identifier makes the inspection nonempty. |
| “D-151 clause 7 remains a fail-closed evidence and pre-registration fence under D-161” (`06-consult-sol-structural.md:113`) | Existing conditional set and out-of-band digest gate preserved at `joulewise/arm_readiness.py:2952-2962,4701-4756` | Existing `tests/test_receipt_histsem.py:1872-1884,1891-1901` (not run under the touched-module-only preflight rule) | Remove the conditional digest check; membership alone would subtract the successor path and those assertions would stop refusing. |

## Verification notes

V1 records the acceptance regression red before the new mechanism. V3 records the required mutation kill: disabling only the exact-set predicate made that same test fail, after which the predicate was restored. V4 is the complete touched-module tail. No other test module was run, per the preflight rule.
