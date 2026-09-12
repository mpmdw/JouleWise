```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented and regression-tested the authorized B1 repair, but canonical verification requires fixture updates in three out-of-scope test files.",
  "workspace": {
    "base_requested": "2e61ff96ea80186efa71efb9c9f6f00a16a70019",
    "base_mode": "exact",
    "head_start": "2e61ff96ea80186efa71efb9c9f6f00a16a70019",
    "head_end": "2e61ff96ea80186efa71efb9c9f6f00a16a70019",
    "upstream_end": null,
    "branch": "impl/cal-bracket-d079"
  },
  "pathspec": [
    "joulewise/whole_window.py",
    "tests/test_whole_window_selection.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "TASK_TMPDIR=$(mktemp -d /private/tmp/calbracket-baseline.XXXXXX) && TMPDIR=\"$TASK_TMPDIR\" python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 2453 tests in 589.082s",
          "OK (skipped=85)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2453 tests.*OK \\(skipped=85\\)"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_whole_window_selection",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 56 tests in 43.841s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 56 tests.*OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_calibration_bracketing",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 24 tests in 0.023s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 24 tests.*OK"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_calibration_ledger",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 10 tests in 0.014s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 10 tests.*OK"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "git archive 2e61ff96ea80186efa71efb9c9f6f00a16a70019 into a temporary directory; overlay only tests/test_whole_window_selection.py; run R1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: ('whole_window_verdict_provenance_invalid',) != ()",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=1\\)"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "git archive 2e61ff96ea80186efa71efb9c9f6f00a16a70019 into a temporary directory; overlay only tests/test_whole_window_selection.py; run R3",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: 'whole_window_verdict_provenance_invalid' not found in ()",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=1\\)"
      }
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "Apply transient m1 early-placement mutant; run R1; revert mutant",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: ('whole_window_verdict_provenance_invalid',) != ()",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=1\\)"
      }
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "Apply transient m2 raw-comparison mutant; run R3; revert mutant",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: 'whole_window_verdict_provenance_invalid' not found in ()",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=1\\)"
      }
    },
    {
      "id": "V9",
      "kind": "suite",
      "cmd": "FINAL_TMPDIR=$(mktemp -d /private/tmp/calbracket-final.XXXXXX) && TMPDIR=\"$FINAL_TMPDIR\" python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 2456 tests in 586.720s",
          "FAILED (failures=44, errors=4, skipped=85)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2456 tests.*OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "The fail-closed implicit-row ruling breaks legacy/sessionless fixtures in tests/test_analysis_integration.py, tests/test_floor_extraction.py, and tests/test_whole_window.py; those paths are outside WRITE_SCOPE.",
      "needs": "Resume with the three test paths added to WRITE_SCOPE so their fixtures can supply prepared sessions or explicit non-minted semantics."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "Post-fix canonical suite is not green: 44 failures and 4 errors, comprising analysis integration 39 failures/4 errors, floor extraction 4 failures, and whole-window authentication 1 failure.",
      "needs": "Update the out-of-scope fixtures, rerun all required suites, then create the single authorized commit."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "tests/test_analysis_integration.py",
      "tests/test_floor_extraction.py",
      "tests/test_whole_window.py"
    ],
    "reason": "Binding fail-closed treatment of undeclared rows invalidates legacy/sessionless test fixtures in these files.",
    "blocked_work": "Green canonical suite and the exactly-one landing commit.",
    "minimal_change": "Adjust affected shared fixtures or calls to provide a prepared valid-snapshot session, or declare explicit non-minted semantics where contract-correct; do not weaken production enforcement."
  }
}
```

## Change

Removed the round-one raw pre-flight guard and added normalized minted-session readiness enforcement immediately after the sole preparation seam. R1–R5, both rewritten round-one tests, overlay proofs, and both mutants are implemented.

No commit was created: doing so before the scope expansion would prevent landing the completed repair as exactly one commit.

## Verification notes

`NEEDS_SCOPE`: the canonical failures are confined to:

- `tests/test_analysis_integration.py`: 39 failures, 4 errors
- `tests/test_floor_extraction.py`: 4 failures
- `tests/test_whole_window.py`: 1 failure

The authorized focused suites are green. The final tree contains neither mutant and modifies only the two authorized paths.

## Residual risk

The repair remains uncommitted until the three legacy fixture files can be updated and the canonical suite passes.