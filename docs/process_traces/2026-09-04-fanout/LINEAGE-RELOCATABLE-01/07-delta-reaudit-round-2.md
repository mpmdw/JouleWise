```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "DR-01 is cured, no round-1 finding regressed, no new defect was found, and fix round 2 is landable.",
  "workspace": {
    "base_requested": "b420a45a58ecba69b8fb7a121eb27b864ba39325",
    "base_mode": "exact",
    "head_start": "b420a45a58ecba69b8fb7a121eb27b864ba39325",
    "head_end": "b420a45a58ecba69b8fb7a121eb27b864ba39325",
    "upstream_end": "b420a45a58ecba69b8fb7a121eb27b864ba39325",
    "branch": "feat/2026-09-04-fan-LINEAGE-RELOCATABLE-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/LINEAGE-RELOCATABLE-01/07-delta-reaudit-round-2.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "LANDABLE",
    "findings": [],
    "refuter_dispositions": [
      {
        "id": "DR-01",
        "status": "CURED",
        "evidence": "Raw carriers now fail at authenticate_launch_lineage before carrier loading; the locator-authenticated bundle path still accepts the valid moved-source fixture and rejects a wrong source-locator digest. The full touched module passed 57 tests, and the focused boundary probe passed."
      },
      {
        "id": "LR-01",
        "status": "CURED",
        "evidence": "Round 2 did not alter the governing ruling or bundle relocation checks; the touched module again passed the positive relocation leg and all named tamper, committed-pack-change, repository-relative-move, swapped-chain, traversal, and symbolic-link refusal legs."
      }
    ],
    "regressed": [],
    "new_defects": [],
    "same_signature": "NO — no round-1 finding survives: DR-01 is cured, LR-01 remains cured, and no NOT CURED, REGRESSED, or NEW defect has a surviving signature to route."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_arm_readiness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 57 tests in 15.811s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 57 tests in [0-9.]+s[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nimport io\nimport unittest\nfrom unittest import mock\nfrom joulewise import arm_readiness as readiness\nfrom tests.test_arm_readiness import LaunchLineageRelocationTests\n\ncase = LaunchLineageRelocationTests('test_direct_relocation_refuses_carrier_without_locator_authentication')\ncase.setUp()\ntry:\n    try:\n        readiness.authenticate_launch_lineage(case.lineage, require_completion=False, relocation_carrier=case.carrier_path)\n    except readiness.LaunchLineageError as exc:\n        assert exc.reason_code == 'launch_binding_mismatch'\n        assert str(exc) == 'direct lineage relocation requires an authenticated root locator'\n    else:\n        raise AssertionError('valid raw direct carrier authenticated')\n    assert readiness.authenticate_bundle_launch_lineage(case.relocated_bundle, require_completion=False, relocation_carrier=case.carrier_path) is not None\n    case.carrier['source_locator_sha256'] = '0' * 64\n    case._rewrite_carrier()\n    try:\n        readiness.authenticate_bundle_launch_lineage(case.relocated_bundle, require_completion=False, relocation_carrier=case.carrier_path)\n    except readiness.LaunchLineageError as exc:\n        assert exc.reason_code == 'launch_binding_mismatch'\n    else:\n        raise AssertionError('wrong locator digest authenticated through bundle API')\n    print('BOUNDARY_OK direct_valid=REFUSED bundle_valid=ACCEPTED bundle_wrong_digest=REFUSED')\nfinally:\n    case.doCleanups()\n\noriginal = readiness.authenticate_launch_lineage\ndef prior_dispatch(value, *, relocation_carrier=None, **kwargs):\n    relocation = readiness._load_launch_lineage_relocation(relocation_carrier) if relocation_carrier is not None else kwargs.pop('_relocation', None)\n    return original(value, relocation_carrier=None, _relocation=relocation, **kwargs)\ncase = LaunchLineageRelocationTests('test_direct_relocation_refuses_carrier_without_locator_authentication')\nwith mock.patch.object(readiness, 'authenticate_launch_lineage', side_effect=prior_dispatch):\n    result = unittest.TextTestRunner(stream=io.StringIO()).run(case)\nassert result.testsRun == 1 and len(result.failures) == 1 and not result.errors\nassert 'LaunchLineageError not raised' in result.failures[0][1]\nprint('COUNTERFACTUAL_BITES testsRun=1 failures=1 errors=0')\nprint('prior raw-carrier dispatch => named round-2 regression fails')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "BOUNDARY_OK direct_valid=REFUSED bundle_valid=ACCEPTED bundle_wrong_digest=REFUSED",
          "COUNTERFACTUAL_BITES testsRun=1 failures=1 errors=0",
          "prior raw-carrier dispatch => named round-2 regression fails"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^BOUNDARY_OK direct_valid=REFUSED bundle_valid=ACCEPTED bundle_wrong_digest=REFUSED[\\s\\S]*COUNTERFACTUAL_BITES testsRun=1 failures=1 errors=0[\\s\\S]*named round-2 regression fails$"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "rg -n \"_relocation=|_load_launch_lineage_relocation\\(\" joulewise --glob '*.py'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "joulewise/arm_readiness.py:9171:def _load_launch_lineage_relocation(",
          "joulewise/arm_readiness.py:10980:        _load_launch_lineage_relocation(relocation_carrier)",
          "joulewise/arm_readiness.py:11033:        _relocation=relocation,"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "arm_readiness.py:9171:[\\s\\S]*arm_readiness.py:10980:[\\s\\S]*arm_readiness.py:11033:"
      }
    },
    {
      "id": "V4",
      "kind": "lint",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile joulewise/arm_readiness.py tests/test_arm_readiness.py && git diff --check HEAD^..HEAD",
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
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Per the runner's touched-module preflight rule, the repository-wide suite and untouched test modules were intentionally not run.",
      "needs": ""
    }
  ]
}
```

## Findings

None. DR-01 is **CURED** and LR-01 remains **CURED**; no round-1 finding is
**NOT CURED** or **REGRESSED**, and no **NEW** defect was found.

Same-signature statement: **NO** — no round-1 finding survives, so there is no
repeated signature to route to consult.

## Residual risk

Only `tests.test_arm_readiness`, the test module touched by fix round 2, was
run. The repository-wide suite and untouched test modules were excluded by the
runner's preflight rule.
