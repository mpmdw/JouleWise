```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented D-107 C-A′ closure; all three custody subjects license, 769/769 metadata files admit, and 2411 canonical tests pass.",
  "workspace": {
    "base_requested": "a6ce7af plus the pre-existing fix-round-1 worktree diff",
    "base_mode": "exact",
    "head_start": "a6ce7af7c6c4e1119d6c4365fb63ce4482f9e246",
    "head_end": "a6ce7af7c6c4e1119d6c4365fb63ce4482f9e246",
    "upstream_end": "a6ce7af7c6c4e1119d6c4365fb63ce4482f9e246",
    "branch": "impl/d100-bii-binding"
  },
  "pathspec": [
    "joulewise/salvage_dangler.py",
    "tests/test_salvage_dangler.py",
    "tests/fixtures/salvage_dangler/window_b_idle_abort_byte_faithful/**"
  ],
  "unowned_dirty": [
    "BRIEF.md",
    "tests/test_run_campaign.py (pre-existing fix-round-1 diff, preserved unchanged by this session)"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_salvage_dangler",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 32 tests in 1.997s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 32 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_run_campaign",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 203 tests in 178.410s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 203 tests.*OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_run_campaign.D100MembershipRepairTests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 8 tests in 0.036s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 8 tests.*OK"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python - <<'PY'\nfrom pathlib import Path\nfrom joulewise.salvage_dangler import inspect_salvage_attempt\nroot = Path.home() / 'JouleWise-window-custody/window_metrologyB_20260801/quarantine'\nsubjects = sorted(path for path in root.iterdir() if path.is_dir())\nfor subject in subjects:\n    result = inspect_salvage_attempt(subject)\n    print(subject.name, 'LICENSED', result['licensed'])\nprint('LICENSED_COUNT', sum(inspect_salvage_attempt(path)['licensed'] for path in subjects))\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "mtadd-p2048o0128-r08__20260801T131705Z LICENSED True",
          "mtadd-p2048o0128-r08__20260801T133315Z LICENSED True",
          "mtnull-o0512-b04-b2__20260801T113258Z LICENSED True",
          "LICENSED_COUNT 3"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "LICENSED_COUNT 3"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python - <<'PY'\nfrom pathlib import Path\nimport json\nfrom joulewise.salvage_dangler import _validate_nested_metadata_classification\npaths = sorted(Path('/Users/edr/code/JouleWise').glob('runs_window_*/**/metadata.json'))\nrefused = []\nfor path in paths:\n    try:\n        _validate_nested_metadata_classification(json.loads(path.read_text(encoding='utf-8')))\n    except Exception as exc:\n        refused.append((path, exc))\nprint('CORPUS_METADATA', len(paths), 'ADMITTED', len(paths) - len(refused), 'REFUSED', len(refused))\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["CORPUS_METADATA 769 ADMITTED 769 REFUSED 0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "CORPUS_METADATA 769 ADMITTED 769 REFUSED 0"
      }
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 2411 tests in 710.771s", "OK (skipped=25)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2411 tests.*OK \\(skipped=25\\)"
      }
    },
    {
      "id": "V7",
      "kind": "inspection",
      "cmd": "python3 -c '<AST source-segment SHA-256 comparison for all three test_d106_* methods against the round-start hashes>'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "test_d106_early_telemetry_substitution_refuses=True",
          "test_d106_nested_metadata_workload_evidence_refuses=True",
          "test_d106_quarantine_digest_freeze_rejects_sibling_copy=True"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "True"
      }
    },
    {
      "id": "V8",
      "kind": "lint",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["no output"]
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
      "text": "D-107 records 24 bundles satisfying the full abort+claim_reason predicate; the materialized corpus has 24 decision=abort bundles but only 23 with claim_reason=environment_admission_failed.",
      "needs": "Lead should inspect runs_window_a7_20260723/p2015-df-rq-mid-abs-r01, whose abort has claim_reason null."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Variable node-cleanup path/error and telemetry argv leaves use documented decidable D-105 supersets; they never admit on bare isinstance(str).",
      "needs": "Lead should confirm this D-107 clause-2 interpretation during the fresh focused audit."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The mandatory byte-faithful fixture contains 22 files and is approximately 154 MiB.",
      "needs": "Lead should confirm repository storage/LFS disposition before committing."
    }
  ]
}
```

## Change

Implemented the producer-derived grammar as:

- Metadata: 32 admitted top-level fields and 108 closed nested container sets, derived from `bundle.py:943-975` and `controller.py:2037-2168`.
- `environment_admission`: closed controller fields, attempt rows, guard observations, seven reachable failure literals, dynamic `before_attempt_N`/`after_attempt_N`, and schema enum domains.
- Events: five closed row keys, the exact eight-row idle-abort sequence, identity-specific metadata sets, closed messages, and `FailureReason` values.
- Summary: 23 closed fields plus closed `idle_baseline`, `measurement_quality`, and provenance containers.
- `metadata.extra`: six producer scalars plus `node_cleanup`; cleanup rows have ten producer-derived keys.
- Inventory: closed 6-file compact, 8-file complete, and 22-file two-attempt production sets.
- Depth: iterative cap at 32, raising `SalvageAuthorizationError`; no `RecursionError` conversion.
- D-106 interval containment and digest-freeze blocks remain untouched; the marker now also cites D-107.

Acceptance status:

- (i) PASS — three real subjects LICENSED; 22-file fixture byte hashes match the custody subject.
- (ii) PASS — all four value channels VOID.
- (iii) PASS — all four delta-V4 shapes VOID.
- (iv) PASS — all eight refusals remain with the spelling list neutralized.
- (v) PASS — 995-deep input raises the named bound error.
- (vi) PASS — 769/769 materialized metadata files admitted.
- (vii) PASS — focused suites, runner consumers, manifest-less refusal, protected D-106 hashes, and full suite are green.

Session-owned changes are the validator, its regression module, and the 22-file fixture subtree. The pre-existing `tests/test_run_campaign.py` fix-round-1 change remains in the resulting worktree but was not altered this session. No commit was created.

## Verification notes

No D-107 versus C-A′ implementation conflict required a ruling. The only evidence conflict is the recorded 24-bundle full-predicate count versus the current 23-bundle result described in F1.

## Residual risk

The lead should double-check the variable-text D-105 supersets, the 154 MiB fixture storage policy, the corpus-count discrepancy, and the final diff under the required fresh audit.