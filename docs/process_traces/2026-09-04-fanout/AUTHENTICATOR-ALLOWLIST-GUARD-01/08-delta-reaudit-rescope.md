```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NOT LANDABLE: the exact-set guard is opt-in on the current lifecycle ID, so a future ID admits an unexplained extra allowlist path.",
  "workspace": {
    "base_requested": "ab6885559266614d99e4bec0e26485b724d8f2d1",
    "base_mode": "exact",
    "head_start": "ab6885559266614d99e4bec0e26485b724d8f2d1",
    "head_end": "ab6885559266614d99e4bec0e26485b724d8f2d1",
    "upstream_end": "ab6885559266614d99e4bec0e26485b724d8f2d1",
    "branch": "feat/2026-09-04-fan-AUTHENTICATOR-ALLOWLIST-GUARD-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/AUTHENTICATOR-ALLOWLIST-GUARD-01/08-delta-reaudit-rescope.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "landability": "NOT LANDABLE",
    "same_signature": "THIRD OCCURRENCE",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "location": "joulewise/arm_readiness.py:1955-1962; tests/test_arm_readiness_schemas.py:531-550",
        "text": "The positive exact-set mechanism runs only when registry_id equals d117-r1-lifecycle-v1. Changing a resolved lifecycle to a future nonempty ID and adding future-confirmation-token.json makes validate_registry accept the unexplained extra path. The acceptance test exercises only the current ID. This is a new implementation defect and the third occurrence of the same opt-in/closure signature.",
        "counterfactual": "Set freeze_evidence_lifecycle.registry_id to d117-r1-lifecycle-v2, append configs/arm_readiness/future-confirmation-token.json, and validate_registry returns normally."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_arm_readiness_schemas",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": [".....................................", "Ran 37 tests in 0.097s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 37 tests in [0-9.]+s[\\s\\S]*OK"}
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_arm_readiness_schemas.ArmReadinessSchemaTests.test_allowlist_refuses_novel_entry_absent_from_governed_artifact_provenance",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 1 test in 0.002s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 1 test in [0-9.]+s[\\s\\S]*OK"}
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 - <<'PY'\nimport inspect\nimport unittest\nfrom unittest import mock\nimport joulewise.arm_readiness as readiness\nfrom tests.test_arm_readiness_schemas import ArmReadinessSchemaTests\nsource = inspect.getsource(readiness.validate_r1_lifecycle_registry)\nneedle = 'if allowlist != derived_manifest[\"paths\"]:'\nassert source.count(needle) == 1\nnamespace = dict(readiness.__dict__)\nexec(source.replace(needle, 'if False and allowlist != derived_manifest[\"paths\"]:'), namespace)\ncase = ArmReadinessSchemaTests('test_allowlist_refuses_novel_entry_absent_from_governed_artifact_provenance')\nresult = unittest.TestResult()\nwith mock.patch.object(readiness, 'validate_r1_lifecycle_registry', namespace['validate_r1_lifecycle_registry']):\n    case.run(result)\nfailures = result.failures + result.errors\nassert len(failures) == 1, failures\nassert failures[0][1].splitlines()[-1] == 'AssertionError: ArmReadinessError not raised'\nprint('exact-set mutation killed: acceptance test failed as expected')\nprint(failures[0][1].splitlines()[-1])\nPY",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["exact-set mutation killed: acceptance test failed as expected", "AssertionError: ArmReadinessError not raised"]},
      "expected": {"exit_code": 0, "tail_regex": "^exact-set mutation killed: acceptance test failed as expected\\nAssertionError: ArmReadinessError not raised$"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "python3 - <<'PY'\nfrom pathlib import Path\nimport joulewise.arm_readiness as readiness\nregistry, _ = readiness.load_registry(Path('.'))\ntry:\n    readiness._require_confirmed_conditional_path(Path('.').resolve(), 'ab6885559266614d99e4bec0e26485b724d8f2d1', readiness.RECEIPT_HISTSEM_PINSET_RELATIVE_PATH[1].as_posix(), registry['freeze_evidence_lifecycle'], None, expected_confirmation_digest=None, evidence_id='delta-reaudit')\nexcept readiness.EvidenceLifecycleError as exc:\n    assert exc.role == 'DEPENDENCY_CHANGED_SET'\n    assert 'no expected confirmation digest supplied' in str(exc)\n    print('kept evidence fence: REFUSED DEPENDENCY_CHANGED_SET')\nelse:\n    raise AssertionError('kept evidence fence accepted without confirmation')\nPY",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["kept evidence fence: REFUSED DEPENDENCY_CHANGED_SET"]},
      "expected": {"exit_code": 0, "tail_regex": "^kept evidence fence: REFUSED DEPENDENCY_CHANGED_SET$"}
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "if rg -n 'R1_AUTHENTICATOR_REGISTRY|_R1AuthenticatorRegistration|_r1_authenticator|_r1_path_class_token|_r1_authenticator_allowlist_conflicts|registered authenticator path class' joulewise/arm_readiness.py tests/test_arm_readiness_schemas.py; then exit 1; else test $? -eq 1; fi",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "python3 - <<'PY'\nimport copy\nfrom pathlib import Path\nfrom joulewise.arm_readiness import load_registry, validate_registry\nregistry, _ = load_registry(Path('.'))\nmutated = copy.deepcopy(registry)\nlifecycle = mutated['freeze_evidence_lifecycle']\nlifecycle['registry_id'] = 'd117-r1-lifecycle-v2'\nlifecycle['irrelevant_path_allowlist'].append('configs/arm_readiness/future-confirmation-token.json')\nlifecycle['irrelevant_path_allowlist'].sort()\nvalidate_registry(mutated)\nprint('future-registry-id bypass: ACCEPTED unexplained extra path')\nPY",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["future-registry-id bypass: ACCEPTED unexplained extra path"]},
      "expected": {"exit_code": 0, "tail_regex": "^future-registry-id bypass: ACCEPTED unexplained extra path$"}
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "base=$(git merge-base origin/main HEAD); git diff --check \"$base\"..HEAD; git diff --quiet \"$base\"..HEAD -- RUN_STATE.md TASK_QUEUE.md PROJECT_STATUS.md docs/process/state_kernel.json docs/decision_log.md; unexpected=$(git diff --name-only \"$base\"..HEAD | awk '$0 != \"joulewise/arm_readiness.py\" && $0 != \"tests/test_arm_readiness_schemas.py\" && $0 !~ /^docs\\/process_traces\\/2026-09-04-fanout\\/AUTHENTICATOR-ALLOWLIST-GUARD-01\\//'); test -z \"$unexpected\"; printf 'landing scope: only mission code/test plus traces; state docs untouched\\n'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["landing scope: only mission code/test plus traces; state docs untouched"]},
      "expected": {"exit_code": 0, "tail_regex": "^landing scope: only mission code/test plus traces; state docs untouched$"}
    }
  ],
  "flags": []
}
```

## Findings

### F1 — blocker — future lifecycle IDs bypass the positive manifest

The retired decorator/registry names are gone, and the named acceptance test is a real mutation kill. But the replacement exact-set check is itself opt-in: `registry_id == "d117-r1-lifecycle-v1"` is the only edge into it. V6 changes only that valid nonempty identifier and adds the consult's novel path; `validate_registry` accepts. This is the third occurrence of the same closure signature, now under a new name, so the re-scope does not end the class. Apply the exact-set check to every resolved lifecycle registry independently of identifier and add the future-ID counterfactual to the acceptance regression.

## Residual risk

Per preflight, only `tests.test_arm_readiness_schemas` was run. The retained conditional evidence fence was executed directly through production code, but the untouched `tests.test_receipt_histsem` module and repository-wide suite were not run.
