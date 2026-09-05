```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "complete",
  "summary": "The merge-base mission delta is scope-clean, its touched module passes, and old-behavior mutation kills the new regressions; the landing is LANDABLE.",
  "workspace": {
    "base_requested": "origin/main merge-base b0ed6991c11f3a515ad293760c6dfc031adda8e1",
    "base_mode": "exact",
    "head_start": "05c443758693779fc3445d83f46ca653fbab4793",
    "head_end": "05c443758693779fc3445d83f46ca653fbab4793",
    "upstream_end": "b0ed6991c11f3a515ad293760c6dfc031adda8e1",
    "branch": "feat/2026-09-04-fan-PINSET-GRAMMAR-EXCLUSION-01"
  },
  "pathspec": [
    "docs/process_traces/2026-09-04-fanout/PINSET-GRAMMAR-EXCLUSION-01/02-refuter-merge-base.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "gauntlet": "LANDABLE",
    "findings": []
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git diff --check b0ed6991c11f3a515ad293760c6dfc031adda8e1..HEAD && test -z \"$(git diff --name-only b0ed6991c11f3a515ad293760c6dfc031adda8e1..HEAD -- RUN_STATE.md TASK_QUEUE.md docs/process/state_kernel.json docs/decision_log.md)\" && python3 - <<'PY'\nfrom joulewise import arm_readiness as readiness\nrows = readiness._load_histsem_pinset('.')\nrefused = [row['pack_id'] for row in rows if readiness._histsem_tree_has_authoring_custody(readiness._historical_pack_tree('.', row['pack_path'], row['head_commit'])[1])]\nassert not refused, refused\nprint(f\"PASS: mission diff clean; magistrate-owned state delta empty; governed historical trees admitted={len(rows)}\")\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PASS: mission diff clean; magistrate-owned state delta empty; governed historical trees admitted=9"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "PASS: mission diff clean; magistrate-owned state delta empty; governed historical trees admitted=9$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_receipt_histsem.PreAuthoringProjectionCustodyTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "........",
          "----------------------------------------------------------------------",
          "Ran 8 tests in 20.326s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 8 tests in [0-9.]+s\\n\\nOK$"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_receipt_histsem",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 67 tests in 2145.637s",
          "",
          "OK (skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 67 tests in [0-9.]+s\\n\\nOK \\(skipped=1\\)$"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 - <<'PY'\nimport unittest\nfrom pathlib import PurePosixPath\nfrom joulewise import arm_readiness as readiness\nclass QuietResult(unittest.TestResult): pass\noriginal = readiness._histsem_tree_has_authoring_custody\nreadiness._histsem_tree_has_authoring_custody = lambda paths: any(PurePosixPath(path).parts and PurePosixPath(path).parts[0] in readiness._HISTSEM_AUTHORING_CUSTODY_DIRECTORIES for path in paths)\ntry:\n    names = ('tests.test_receipt_histsem.PreAuthoringProjectionCustodyTests.test_nested_projection_path_refuses_at_the_pre_authoring_gate', 'tests.test_receipt_histsem.PreAuthoringProjectionCustodyTests.test_projection_exclusion_is_exactly_the_freeze_path_grammar')\n    result = QuietResult(); unittest.defaultTestLoader.loadTestsFromNames(names).run(result)\nfinally:\n    readiness._histsem_tree_has_authoring_custody = original\nassert result.testsRun == 2 and not result.errors and len(result.failures) == 5\nassert readiness._histsem_tree_has_authoring_custody is original\nprint('COUNTERFACTUAL PASS: old whole-directory exclusion killed 2/2 tests (5 assertion records); mutation restored')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "COUNTERFACTUAL PASS: old whole-directory exclusion killed 2/2 tests (5 assertion records); mutation restored"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "COUNTERFACTUAL PASS: old whole-directory exclusion killed 2/2 tests \\(5 assertion records\\); mutation restored$"
      }
    }
  ],
  "flags": []
}
```

## Findings

None.

## Evidence

- Scope: `git diff $(git merge-base origin/main HEAD)..HEAD` resolves to `b0ed6991c11f3a515ad293760c6dfc031adda8e1..05c443758693779fc3445d83f46ca653fbab4793` and contains only `joulewise/arm_readiness.py`, `tests/test_receipt_histsem.py`, and `docs/process_traces/2026-09-04-fanout/PINSET-GRAMMAR-EXCLUSION-01/01-sol-report.md`, exactly the implementation report's scope of record. `RUN_STATE.md`, `TASK_QUEUE.md`, `docs/process/state_kernel.json`, and `docs/decision_log.md` have no mission delta.
- Grammar: the new predicate admits only direct `identity_pin_projection.receipts/projection-NNNN.json` and `.sha256` paths with at least four digits. This is the same anchored grammar enforced by `joulewise/identity_pins.py`; the post-authoring custody-directory set remains unchanged.
- Counterfactual 1: `identity_pin_projection.receipts/arm_readiness.evidence/x.json` is refused at the pre-authoring gate now. Under the restored old predicate, `test_nested_projection_path_refuses_at_the_pre_authoring_gate` advances incorrectly to `plan tree has no pinned freeze receipt` and fails.
- Counterfactual 2: `evil.bin`, `projection-001.json`, `projection-0001.json.sha256`, and `nested/projection-0001.json` below the projection directory are refused now. Under the restored old predicate, all four refused subcases in `test_projection_exclusion_is_exactly_the_freeze_path_grammar` fail. The mutation was restored in `finally` and identity-checked afterward.
- Compatibility: all nine governed historical trees remain admissible. The focused class passed 8/8, and the complete touched `tests.test_receipt_histsem` module passed 67 tests with one expected skip. No repository-wide suite was run.
- Previous round: no previous refuter verdict file exists in this mission directory, so there is no non-staleness blocker of record to carry. The mission's substantive whole-directory-exclusion defect was nevertheless re-tested directly by the old-behavior mutation and is closed.

## Residual risk

None identified within the mission delta.
