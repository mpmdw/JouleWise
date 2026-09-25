```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Completed the A292 harness round; the new tests are red only where the unchanged reducer needs the ruled input bounds.",
  "workspace": {
    "base_requested": "660b32d7",
    "base_mode": "exact",
    "head_start": "660b32d7b567abcc5bd4b98533c1c05937c14893",
    "head_end": "660b32d7b567abcc5bd4b98533c1c05937c14893",
    "upstream_end": "660b32d7b567abcc5bd4b98533c1c05937c14893",
    "branch": "feat/2026-09-25-a292-scored-reduce"
  },
  "pathspec": [
    "tests/test_scored_reduce.py",
    "tests/scored_reduce_checker.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_scored_reduce > /tmp/a292-harness-round2-unittest.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": ["KeyboardInterrupt"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran .* tests"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_scored_reduce.ScoredReduceTests.test_domain_boundaries_accept tests.test_scored_reduce.ScoredReduceTests.test_extreme_values_refuse_not_crash tests.test_scored_reduce.ScoredReduceTests.test_generated_one_fault_domain_witnesses > /tmp/a292-harness-round2-targeted.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 3 tests in 7.800s", "FAILED (failures=12, errors=13)"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=12, errors=13\\)"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B - <<'PY' > /tmp/a292-harness-round2-no-differential.log 2>&1\nimport unittest\nfrom tests.test_scored_reduce import ScoredReduceTests\nsuite = unittest.defaultTestLoader.loadTestsFromTestCase(ScoredReduceTests)\nfiltered = unittest.TestSuite(test for test in suite if test._testMethodName != 'test_differential_oracle_200_nights')\nresult = unittest.TextTestRunner().run(filtered)\nraise SystemExit(not result.wasSuccessful())\nPY",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 63 tests in 67.694s", "FAILED (failures=12, errors=13)"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=12, errors=13\\)"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The full focused run was stopped before the runner's 400-second limit while in the unchanged 200-night differential test.",
      "needs": "After the reducer bound change, rerun the complete focused module."
    }
  ]
}
```

## Change

Added `domain_witnesses()` with 195 cases and a coverage lock, accepted boundary tests, and extreme value refusal tests in [test_scored_reduce.py](/Users/edr/code/wt-152c9255-a292i/tests/test_scored_reduce.py). Updated the independent oracle with the two A292-ESC-01 literals and bounds in [scored_reduce_checker.py](/Users/edr/code/wt-152c9255-a292i/tests/scored_reduce_checker.py). Removed the superseded large-integer anchor acceptance test. No commit was made.

## Verification notes

The 63 tests outside the slow differential test produced failures only in the two intended red tests: 12 above-bound values were accepted or reached later refusal codes, and 13 extreme inputs caused uncaught exceptions. The accepted boundary test passed. The oracle agreed with the expected code for all 195 generated witnesses. Temporarily applying the ruled `_int` and `_num` behavior in process made all three new tests pass.

## Residual risk

The complete 200-night differential run remains pending; the magistrate’s M8 sweep follows the reducer round.