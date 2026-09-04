```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NOT LANDABLE: the guard trusts a standalone two-entry role list that is not structurally bound to authenticator implementations or their paths, so the ruled novel-name bypass remains.",
  "workspace": {
    "base_requested": "b0ed6991c11f3a515ad293760c6dfc031adda8e1",
    "base_mode": "exact",
    "head_start": "b14881d9e247293b168a06fa5954899aa37cde06",
    "head_end": "b14881d9e247293b168a06fa5954899aa37cde06",
    "upstream_end": "ec8f780337326f82feb1848a972c4746612da6cc",
    "branch": "feat/2026-09-04-fan-AUTHENTICATOR-ALLOWLIST-GUARD-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/AUTHENTICATOR-ALLOWLIST-GUARD-01/02-refuter-merge-base.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "NOT LANDABLE",
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "location": "joulewise/arm_readiness.py:564-569,1674-1685; tests/test_arm_readiness_schemas.py:532-573",
        "text": "R1_AUTHENTICATOR_PATH_REGISTRY is not an owning authenticator registry: production reads it only inside the new allowlist detector, ignores its family/type fields, and does not require authenticator producers or consumers to declare themselves through it or bind role spelling to path spelling. This relocates the two known names into an independently maintained list. The novel-name test co-mutates that list and the candidate path to matching spellings, assuming the binding the row must enforce.",
        "counterfactual": "Register ('FUTURE','CUSTODY','FUTURE_AUTHENTICATOR') while proposing configs/arm_readiness/future-confirmation-token.json (or add the authenticator without editing this guard-only list): validate_registry accepts the path. The replay printed 'trusted-role bypass: ACCEPTED future-confirmation-token.json'."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git rev-parse HEAD && git branch --show-current",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "b14881d9e247293b168a06fa5954899aa37cde06",
          "feat/2026-09-04-fan-AUTHENTICATOR-ALLOWLIST-GUARD-01"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^b14881d9e247293b168a06fa5954899aa37cde06\\nfeat/2026-09-04-fan-AUTHENTICATOR-ALLOWLIST-GUARD-01$"
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
          "Ran 38 tests in 0.140s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 38 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 - <<'PY'\nimport unittest\nfrom unittest import mock\nimport joulewise.arm_readiness as readiness\nfrom tests.test_arm_readiness_schemas import ArmReadinessSchemaTests\nnames = ('test_registry_refuses_every_registered_authenticator_path_class', 'test_newly_registered_authenticator_name_is_refused_in_allowlist')\nresult = unittest.TestResult()\nwith mock.patch.object(readiness, '_r1_authenticator_allowlist_conflicts', return_value=[]):\n    unittest.TestSuite(ArmReadinessSchemaTests(name) for name in names).run(result)\nobserved = [detail.splitlines()[-1] for _case, detail in result.failures + result.errors]\nif len(observed) != 3 or any(detail != 'AssertionError: ArmReadinessError not raised' for detail in observed):\n    raise SystemExit(f'expected three failing regression cases; observed {observed!r}')\nprint('counterfactual guard disabled: 3 expected regression failures observed')\nfor detail in observed:\n    print(detail)\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "counterfactual guard disabled: 3 expected regression failures observed",
          "AssertionError: ArmReadinessError not raised",
          "AssertionError: ArmReadinessError not raised",
          "AssertionError: ArmReadinessError not raised"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "counterfactual guard disabled: 3 expected regression failures observed(\\nAssertionError: ArmReadinessError not raised){3}"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 - <<'PY'\nimport copy\nfrom unittest import mock\nimport joulewise.arm_readiness as readiness\nregistry, _ = readiness.load_registry('.')\nmutated = copy.deepcopy(registry)\nmutated['freeze_evidence_lifecycle']['irrelevant_path_allowlist'].append('configs/arm_readiness/future-confirmation-token.json')\nmutated['freeze_evidence_lifecycle']['irrelevant_path_allowlist'].sort()\nfuture_class = ('FUTURE', 'CUSTODY', 'FUTURE_AUTHENTICATOR')\nwith mock.patch.object(readiness, 'R1_AUTHENTICATOR_PATH_REGISTRY', readiness.R1_AUTHENTICATOR_PATH_REGISTRY | {future_class}):\n    readiness.validate_registry(mutated)\nprint('trusted-role bypass: ACCEPTED future-confirmation-token.json')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "trusted-role bypass: ACCEPTED future-confirmation-token.json"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^trusted-role bypass: ACCEPTED future-confirmation-token.json$"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "base=$(git merge-base origin/main HEAD); git diff --quiet \"$base\"..HEAD -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json docs/decision_log.md && git diff --check \"$base\"..HEAD",
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

### F1 — blocker — standalone role spellings do not close the authenticator class

The mission requires the forbidden set to come from registered authenticator roles/classes so a new authenticator cannot evade the fixed-point guard merely by using another name. The new `R1_AUTHENTICATOR_PATH_REGISTRY` is consumed only by `_r1_authenticator_allowlist_conflicts`; it does not own, enable, or validate any authenticator implementation. Its `family` and `reason_type` fields are discarded, and the claimed role-to-path relationship exists only in a comment.

The regression at lines 556-573 patches the guard-only registry and adds a path deliberately spelled from the same token. That proves the substring detector executes, but not the required structural closure. V4 registers a semantic role `FUTURE_AUTHENTICATOR` and proposes its authenticator at `future-confirmation-token.json`; the tracked registry otherwise remains valid and accepts the path. Adding the authenticator without touching the guard-only list is an even simpler survival. The smallest cure is to derive path classes from declarations that authenticator consumers/producers must actually use, with a validated path-class field rather than an assumed role/filename spelling convention.

## Evidence

- The required HEAD was exact. The mission range was `b0ed6991c11f3a515ad293760c6dfc031adda8e1..b14881d9e247293b168a06fa5954899aa37cde06` using `git merge-base origin/main HEAD`.
- Delta paths exactly matched the implementation report's scope of record: `01-sol-report.md`, `joulewise/arm_readiness.py`, and `tests/test_arm_readiness_schemas.py`. No delta exists in `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`, or `docs/decision_log.md`.
- The claimed focused module passed 38/38. Disabling the detector produced the expected three failures across the two new test methods, so the local detector counterfactual is genuine; it is insufficient for the row goal because the tests supply the unproven role/path binding themselves.
- No previous refuter verdict was present in the mission directory or its Git history. The applicable non-staleness shapes were nevertheless re-tested: the independently trusted role identifier remains open (F1); the mutation kill itself is real; no CLI-check or occupied-root behavior exists in this delta.

## Residual risk

No additional coverage limitation beyond F1. Per preflight, only the touched schema test module was run; the whole suite was not run.
