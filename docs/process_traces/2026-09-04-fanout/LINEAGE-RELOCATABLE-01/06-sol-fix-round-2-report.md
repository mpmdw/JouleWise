```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Cured DR-01 by refusing raw relocation carriers at the direct lineage API and requiring the locator-authenticated bundle path.",
  "workspace": {
    "base_requested": "68ae0b7ba82c83b2ab3d1b2e8e3687bcab99fe2a",
    "base_mode": "exact",
    "head_start": "68ae0b7ba82c83b2ab3d1b2e8e3687bcab99fe2a",
    "head_end": "68ae0b7ba82c83b2ab3d1b2e8e3687bcab99fe2a",
    "upstream_end": "68ae0b7ba82c83b2ab3d1b2e8e3687bcab99fe2a",
    "branch": "feat/2026-09-04-fan-LINEAGE-RELOCATABLE-01"
  },
  "pathspec": [
    "joulewise/arm_readiness.py",
    "tests/test_arm_readiness.py",
    "docs/process_traces/2026-09-04-fanout/LINEAGE-RELOCATABLE-01/06-sol-fix-round-2-report.md"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-04-fanout/LINEAGE-RELOCATABLE-01/05-delta-reaudit-round-1.md"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_arm_readiness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 57 tests in 14.373s",
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_arm_readiness.LaunchLineageRelocationTests.test_direct_relocation_refuses_carrier_without_locator_authentication",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 1.347s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test in [0-9.]+s[\\s\\S]*OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'\nfrom joulewise import arm_readiness as readiness\nfrom tests.test_arm_readiness import LaunchLineageRelocationTests\ncase = LaunchLineageRelocationTests('test_direct_relocation_refuses_carrier_without_locator_authentication')\ncase.setUp()\ntry:\n    case.carrier['source_locator_sha256'] = '0' * 64\n    case._rewrite_carrier()\n    try:\n        readiness.authenticate_launch_lineage(case.lineage, require_completion=False, relocation_carrier=case.carrier_path)\n    except readiness.LaunchLineageError as exc:\n        assert exc.reason_code == 'launch_binding_mismatch'\n        print('DIRECT_BYPASS_REFUSED')\n        print(exc.reason_code)\n        print(str(exc))\n    else:\n        raise AssertionError('wrong locator digest authenticated through direct API')\nfinally:\n    case.doCleanups()\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "DIRECT_BYPASS_REFUSED",
          "launch_binding_mismatch",
          "direct lineage relocation requires an authenticated root locator"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^DIRECT_BYPASS_REFUSED[\\s\\S]*launch_binding_mismatch[\\s\\S]*authenticated root locator$"
      }
    },
    {
      "id": "V4",
      "kind": "lint",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m py_compile joulewise/arm_readiness.py tests/test_arm_readiness.py && git diff --check",
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

| Finding | Cure | File:line | Named counterfactual regression |
|---|---|---|---|
| DR-01 | `authenticate_launch_lineage` now refuses every raw `relocation_carrier` with the established `launch_binding_mismatch` code. Relocation replay remains reachable only when `authenticate_bundle_launch_lineage` has first authenticated the fixed root locator, compared its digest with both bundle metadata and `source_locator_sha256`, and passed the private relocation context. | `joulewise/arm_readiness.py:10294` | `tests/test_arm_readiness.py:1909` replaces the carrier's locator digest with a deliberately wrong digest and proves the direct API refuses it. Under the refuted formulation, the same call authenticated the relocated lineage. |

DR-01 was new in delta re-audit round 1, not the same signature as the cured
LR-01 authority finding. No round-1 `NOT CURED`, `REGRESSED`, or other `NEW`
blocker/should-fix finding remains.

## Verification notes

Per the runner's preflight rule, only the touched test module was run; the
repository-wide suite and untouched test modules were intentionally not run.

## Residual risk

The private `_relocation` parameter remains an internal trust boundary. Its only
production caller is the bundle authenticator after locator/digest comparison;
Python callers that deliberately invoke underscored internals remain outside the
exported API contract.
