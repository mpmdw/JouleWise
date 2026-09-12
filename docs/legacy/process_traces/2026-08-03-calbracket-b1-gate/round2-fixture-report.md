```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Fixture repair and all verification are complete; the required commit is blocked solely by sandbox denial of the Git worktree index lock.",
  "workspace": {
    "base_requested": "2e61ff96ea80186efa71efb9c9f6f00a16a70019",
    "base_mode": "exact",
    "head_start": "2e61ff96ea80186efa71efb9c9f6f00a16a70019",
    "head_end": "2e61ff96ea80186efa71efb9c9f6f00a16a70019",
    "upstream_end": "2e61ff96ea80186efa71efb9c9f6f00a16a70019",
    "branch": "impl/cal-bracket-d079"
  },
  "pathspec": [
    "tests/test_analysis_integration.py",
    "tests/test_floor_extraction.py",
    "tests/test_whole_window.py"
  ],
  "unowned_dirty": [
    "joulewise/whole_window.py",
    "tests/test_whole_window_selection.py"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TMPDIR=/private/tmp/calbracket-fixture-tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_analysis_integration",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 92 tests in 21.709s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 92 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "TMPDIR=/private/tmp/calbracket-fixture-tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_floor_extraction",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 82 tests in 0.225s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 82 tests.*OK"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "TMPDIR=/private/tmp/calbracket-fixture-tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_whole_window",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 9 tests in 0.022s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 9 tests.*OK"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "TMPDIR=/private/tmp/calbracket-fixture-tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_whole_window_selection",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 56 tests in 42.685s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 56 tests.*OK"
      }
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "TMPDIR=/private/tmp/calbracket-fixture-tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_calibration_bracketing",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 24 tests in 0.024s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 24 tests.*OK"
      }
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "TMPDIR=/private/tmp/calbracket-fixture-tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_calibration_ledger",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 10 tests in 0.012s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 10 tests.*OK"
      }
    },
    {
      "id": "V7",
      "kind": "suite",
      "cmd": "TMPDIR=/private/tmp/calbracket-fixture-tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 2456 tests in 695.381s", "OK (skipped=85)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2456 tests.*OK \\(skipped=85\\)"
      }
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "TMPDIR=/private/tmp/calbracket-fixture-tmp PYTHONDONTWRITEBYTECODE=1 python3 -B -m unittest tests.test_whole_window_selection.MaxBracketConsumptionTests.test_b1_r1_explicit_minted_fresh_valid_session_is_prepared_and_accepted tests.test_whole_window_selection.MaxBracketConsumptionTests.test_minted_semantics_loads_and_refuses_pending_ledger_snapshot tests.test_whole_window_selection.MaxBracketConsumptionTests.test_b1_r3_implicit_minted_without_session_is_refused tests.test_whole_window_selection.MaxBracketConsumptionTests.test_b1_r4_implicit_minted_fresh_valid_session_matches_explicit tests.test_whole_window_selection.MaxBracketConsumptionTests.test_minted_secondary_verifier_refuses_missing_session",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 5 tests in 0.039s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 5 tests.*OK"
      }
    },
    {
      "id": "V9",
      "kind": "inspection",
      "cmd": "TMPDIR=/private/tmp/calbracket-fixture-tmp PYTHONDONTWRITEBYTECODE=1 python3 -B - <<'PY'\nimport inspect\nfrom tests.test_whole_window_selection import MaxBracketConsumptionTests\nfrom joulewise.whole_window import _validate_row, _validate_row_uncached\nouter = inspect.getsource(_validate_row)\nuncached = inspect.getsource(_validate_row_uncached)\nassert 'MINTED_CONSUMPTION_SEMANTICS_ID' not in outer\nassert 'row_semantics == MINTED_CONSUMPTION_SEMANTICS_ID' in uncached\nassert 'declared_semantics' not in outer + uncached\nfor name in ('test_b1_r1_explicit_minted_fresh_valid_session_is_prepared_and_accepted','test_minted_semantics_loads_and_refuses_pending_ledger_snapshot','test_b1_r3_implicit_minted_without_session_is_refused','test_b1_r4_implicit_minted_fresh_valid_session_matches_explicit','test_minted_secondary_verifier_refuses_missing_session'):\n    source = inspect.getsource(getattr(MaxBracketConsumptionTests, name))\n    assert '._prepare(' not in source\n    assert '_validate_row_uncached' not in source\n    assert 'whole_window_refusal_reasons(' in source\nprint('m1 early-placement absent')\nprint('m2 raw-comparison absent')\nprint('R1-R5 enter through whole_window_refusal_reasons without direct _prepare or _validate_row_uncached mocks')\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "m1 early-placement absent",
          "m2 raw-comparison absent",
          "R1-R5 enter through whole_window_refusal_reasons without direct _prepare or _validate_row_uncached mocks"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "m1 early-placement absent.*m2 raw-comparison absent"
      }
    },
    {
      "id": "V10",
      "kind": "inspection",
      "cmd": "git diff --check && git status --short --branch && git diff --name-only && git diff --stat && git rev-list --count 2e61ff96ea80186efa71efb9c9f6f00a16a70019..HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "joulewise/whole_window.py",
          "tests/test_analysis_integration.py",
          "tests/test_floor_extraction.py",
          "tests/test_whole_window.py",
          "tests/test_whole_window_selection.py",
          "0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "tests/test_whole_window_selection.py.*0"
      }
    },
    {
      "id": "V11",
      "kind": "other",
      "cmd": "git add -- joulewise/whole_window.py tests/test_whole_window_selection.py tests/test_analysis_integration.py tests/test_floor_extraction.py tests/test_whole_window.py && git commit -m \"CAL-BRACKET B1: authenticate legacy fixtures\" -m \"Gate: docs/process_traces/2026-08-03-calbracket-b1-gate/\"",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 128,
        "tail": [
          "fatal: Unable to create '/Users/edr/code/JouleWise/.git/worktrees/calbracket/index.lock': Operation not permitted"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\\[impl/cal-bracket-d079 [0-9a-f]+\\]"
      }
    },
    {
      "id": "V12",
      "kind": "inspection",
      "cmd": "git status --short --branch && git diff --cached --name-only && git diff --name-only && git rev-parse HEAD && git rev-list --count 2e61ff96ea80186efa71efb9c9f6f00a16a70019..HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "2e61ff96ea80186efa71efb9c9f6f00a16a70019",
          "0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "2e61ff96ea80186efa71efb9c9f6f00a16a70019.*0"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "blocking",
      "text": "The sandbox denied creation of the main checkout worktree index lock. No files were staged, no commit was created, HEAD remained unchanged, and exactly the five authorized working-tree changes remain.",
      "needs": "Lead should run the exact V11 command outside this sandbox."
    }
  ]
}
```

## Change

Legacy and sessionless fixtures now use valid ledger snapshots and prepared minted-consumption sessions. The missing-bundle sampling fixture authenticates its in-memory session before deleting the bundle, preserving the test’s original four-pair assertion without weakening fresh-session enforcement. No production enforcement or assertion purpose was changed.

## Verification notes

The required commit could not be created because the sandbox cannot write `/Users/edr/code/JouleWise/.git/worktrees/calbracket/index.lock`. The Git index remains clean with no staged files; HEAD is unchanged, and the five authorized modifications remain unstaged for the lead to commit.