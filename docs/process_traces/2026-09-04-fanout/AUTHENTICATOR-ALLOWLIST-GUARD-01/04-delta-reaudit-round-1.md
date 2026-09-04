```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NOT LANDABLE: fix round 1 binds registered implementations, but an added authenticator can still bypass the registry and place its path in the allowlist.",
  "workspace": {
    "base_requested": "6f4eee6523878add9811b00fa6d91e573dec797d",
    "base_mode": "exact",
    "head_start": "6f4eee6523878add9811b00fa6d91e573dec797d",
    "head_end": "6f4eee6523878add9811b00fa6d91e573dec797d",
    "upstream_end": "6f4eee6523878add9811b00fa6d91e573dec797d",
    "branch": "feat/2026-09-04-fan-AUTHENTICATOR-ALLOWLIST-GUARD-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/AUTHENTICATOR-ALLOWLIST-GUARD-01/04-delta-reaudit-round-1.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "disposition": "NOT CURED",
        "location": "joulewise/arm_readiness.py:572-621,1728-1755; tests/test_arm_readiness_schemas.py:532-602",
        "text": "The new decorator makes declarations load-bearing only for callables that elect to use it; no producer, consumer, dispatcher, or validation edge requires every authenticator implementation to register. The regression co-mutates the registry and candidate path, so it does not exercise the refuter's simpler unregistered-authenticator path. An added authenticator can execute directly while validate_registry accepts its allowlisted path.",
        "counterfactual": "The named regression passes with the cure and fails when the conflict function is reverted in memory to role-spelling derivation, proving the local cure is load-bearing. Independently, an undecorated future_authenticator executes and configs/arm_readiness/future-confirmation-token.json is accepted, preserving the original same-signature bypass."
      }
    ],
    "new_defects": [],
    "same_signature": "YES: adding and consuming an authenticator without editing the guard registry still permits its path into the allowlist; only the names and registry representation changed."
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD && git branch --show-current && git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "6f4eee6523878add9811b00fa6d91e573dec797d",
          "feat/2026-09-04-fan-AUTHENTICATOR-ALLOWLIST-GUARD-01",
          "## feat/2026-09-04-fan-AUTHENTICATOR-ALLOWLIST-GUARD-01...origin/feat/2026-09-04-fan-AUTHENTICATOR-ALLOWLIST-GUARD-01"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^6f4eee6523878add9811b00fa6d91e573dec797d\\nfeat/2026-09-04-fan-AUTHENTICATOR-ALLOWLIST-GUARD-01\\n## feat/2026-09-04-fan-AUTHENTICATOR-ALLOWLIST-GUARD-01\\.\\.\\.origin/feat/2026-09-04-fan-AUTHENTICATOR-ALLOWLIST-GUARD-01$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_arm_readiness_schemas",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 39 tests in 0.131s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 39 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_arm_readiness_schemas.ArmReadinessSchemaTests.test_newly_registered_authenticator_name_is_refused_in_allowlist",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 0.004s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 - <<'PY'\nimport re\nimport unittest\nfrom unittest import mock\nimport joulewise.arm_readiness as readiness\nfrom tests.test_arm_readiness_schemas import ArmReadinessSchemaTests\n\ndef reverted_role_spelling_guard(allowlist):\n    roles = {re.sub(r'[^a-z0-9]+', '_', declaration.role.lower()).strip('_') for declaration in readiness.R1_AUTHENTICATOR_REGISTRY.values()}\n    return sorted(path for path in allowlist if any(role in re.sub(r'[^a-z0-9]+', '_', path.lower()).strip('_') for role in roles))\n\nresult = unittest.TestResult()\ncase = ArmReadinessSchemaTests('test_newly_registered_authenticator_name_is_refused_in_allowlist')\nwith mock.patch.object(readiness, '_r1_authenticator_allowlist_conflicts', reverted_role_spelling_guard):\n    case.run(result)\ndetails = [detail.splitlines()[-1] for _case, detail in result.failures + result.errors]\nif details != ['AssertionError: ArmReadinessError not raised']:\n    raise SystemExit(f'expected one failing regression under reverted cure; observed {details!r}')\nprint('reverted cure: named regression failed as expected')\nprint(details[0])\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "reverted cure: named regression failed as expected",
          "AssertionError: ArmReadinessError not raised"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "reverted cure: named regression failed as expected\\nAssertionError: ArmReadinessError not raised"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "python3 - <<'PY'\nimport copy\nimport joulewise.arm_readiness as readiness\nregistry, _ = readiness.load_registry('.')\nmutated = copy.deepcopy(registry)\nallowlist = mutated['freeze_evidence_lifecycle']['irrelevant_path_allowlist']\nallowlist.append('configs/arm_readiness/future-confirmation-token.json')\nallowlist.sort()\ndef future_authenticator():\n    return 'authenticated'\nassert future_authenticator() == 'authenticated'\nreadiness.validate_registry(mutated)\nprint('same-signature unregistered-authenticator bypass: ACCEPTED future-confirmation-token.json')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "same-signature unregistered-authenticator bypass: ACCEPTED future-confirmation-token.json"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^same-signature unregistered-authenticator bypass: ACCEPTED future-confirmation-token\\.json$"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --check HEAD^ HEAD",
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

## Findings

### F1 — blocker — NOT CURED: registration remains opt-in

The fix does improve the registered path: both current authenticators are decorated, their declarations carry explicit path classes, the wrappers refuse after declaration removal, and the named novel-role regression passes. Replacing the conflict function in memory with the pre-fix role-spelling behavior makes that regression fail, so this part of the change is genuinely load-bearing.

It does not close the class required by the refuter. `_r1_authenticator` is an optional decorator; no owning dispatcher or validation edge requires an authenticator implementation to pass through it. The new regression decorates its stub before validating the candidate, which assumes the exact registration obligation at issue. V5 exercises the refuter's simpler branch: an undecorated `future_authenticator` executes, then lifecycle validation accepts `configs/arm_readiness/future-confirmation-token.json` because that class never entered `R1_AUTHENTICATOR_REGISTRY`.

Same-signature statement: **the original bypass survives unchanged in mechanism** — add and consume an authenticator without editing the guard registry, then allowlist its differently named path. The fix binds entries that opt in; it does not make opt-in structurally unavoidable.

No NEW defect distinct from this surviving blocker was found in the fix-round delta.

## Residual risk

Per the preflight rule, only the test module touched by fix round 1 was run. No whole-suite or other test module was executed.
