```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Cured the refuter blocker by binding explicit authenticator path classes to the production authenticator implementations and killing the named novel-role bypass.",
  "workspace": {
    "base_requested": "b14881d9e247293b168a06fa5954899aa37cde06",
    "base_mode": "exact",
    "head_start": "b14881d9e247293b168a06fa5954899aa37cde06",
    "head_end": "bd3129fbd62e358795e8442ba5f6dff1282fb846",
    "upstream_end": "bd3129fbd62e358795e8442ba5f6dff1282fb846",
    "branch": "feat/2026-09-04-fan-AUTHENTICATOR-ALLOWLIST-GUARD-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/AUTHENTICATOR-ALLOWLIST-GUARD-01/03-sol-fix-round-1-report.md",
    "joulewise/arm_readiness.py",
    "tests/test_arm_readiness_schemas.py"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-04-fanout/AUTHENTICATOR-ALLOWLIST-GUARD-01/02-refuter-merge-base.md"
  ],
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
          "Ran 39 tests in 0.127s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 39 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "rg -l '(from joulewise( import arm_readiness|\\.arm_readiness import)|import joulewise\\.arm_readiness)' tests --glob '*.py' | sort | sed 's#/#.#g; s#\\.py$##' | xargs python3 -m unittest",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1293 tests in 4084.908s",
          "OK (skipped=23)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1293 tests in [0-9.]+s\\n\\nOK \\(skipped=23\\)"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 - <<'PY'\nimport re\nimport unittest\nfrom unittest import mock\nimport joulewise.arm_readiness as readiness\nfrom tests.test_arm_readiness_schemas import ArmReadinessSchemaTests\ndef old_role_spelling_guard(allowlist):\n    roles = {re.sub(r'[^a-z0-9]+', '_', declaration.role.lower()).strip('_') for declaration in readiness.R1_AUTHENTICATOR_REGISTRY.values()}\n    return sorted(path for path in allowlist if any(role in re.sub(r'[^a-z0-9]+', '_', path.lower()).strip('_') for role in roles))\nresult = unittest.TestResult()\ncase = ArmReadinessSchemaTests('test_newly_registered_authenticator_name_is_refused_in_allowlist')\nwith mock.patch.object(readiness, '_r1_authenticator_allowlist_conflicts', old_role_spelling_guard):\n    case.run(result)\ndetails = [detail.splitlines()[-1] for _case, detail in result.failures + result.errors]\nif details != ['AssertionError: ArmReadinessError not raised']:\n    raise SystemExit(f'expected refuter counterfactual kill; observed {details!r}')\nprint('old role-spelling guard: refuter counterfactual killed')\nprint(details[0])\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "old role-spelling guard: refuter counterfactual killed",
          "AssertionError: ArmReadinessError not raised"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "old role-spelling guard: refuter counterfactual killed\\nAssertionError: ArmReadinessError not raised"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --check && git diff --quiet b14881d9e247293b168a06fa5954899aa37cde06..HEAD -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json docs/decision_log.md",
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
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "HEAD advanced during verification from the exact requested start b14881d9 to descendant bd3129fb by a concurrent lead-authored commit that only custodied 02-refuter-merge-base.md; code and test inputs were unchanged.",
      "needs": "Lead should retain the descendant trace-custody commit when harvesting this uncommitted fix."
    }
  ]
}
```

## Change

The former guard-only role set was replaced by an implementation registry. Each declaration now owns a family/type/role key, an explicit normalized `path_class`, and the actual callable consumers execute. The callable refuses if detached from that declaration, while lifecycle validation derives forbidden allowlist classes from the same records. Role spelling is no longer treated as a filename contract, and the ruled 112-entry allowlist remains byte-unchanged.

| Finding | Cure | File:line |
|---|---|---|
| Refuter F1: the standalone two-role set did not own authenticator implementations and discarded family/type. | Added complete family/type/role declarations whose entries hold and runtime-bind the actual authenticator callables. | `joulewise/arm_readiness.py:561`, `joulewise/arm_readiness.py:577`, `joulewise/arm_readiness.py:11639`, `joulewise/arm_readiness.py:11693` |
| Refuter F1: role-to-path spelling was assumed, so `FUTURE_AUTHENTICATOR` at `future-confirmation-token.json` passed. | Added an explicit validated path-class field and derive collision checks from it. | `joulewise/arm_readiness.py:595`, `joulewise/arm_readiness.py:1728` |
| Refuter counterfactual: register `FUTURE_AUTHENTICATOR` while proposing `configs/arm_readiness/future-confirmation-token.json`. | Regression registers a real decorated stub with independently spelled `future_confirmation_token`, proves the candidate is refused, and V3 proves the old role-spelling implementation makes that exact test fail. | `tests/test_arm_readiness_schemas.py:576` |
| Structural load-bearing requirement. | Regressions pin both current authenticator implementations to their declarations and prove each refuses execution when its declaration is absent. | `tests/test_arm_readiness_schemas.py:532`, `tests/test_arm_readiness_schemas.py:564` |

## Verification notes

Per the prompt, no whole-suite discovery was run. V2 selected only test modules that directly import the changed production module; its expected argparse diagnostics came from passing CLI-negative tests. During V2, the lead concurrently committed the previously untracked refuter report, advancing the branch by one trace-only descendant commit; this session made no commit.
