```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "DR1-F1 is closed by a shared-owner mutation test that reaches both committed-history and ARM pre-authoring consumers and kills a crash-mutant of _committed_successor.",
  "workspace": {
    "base_requested": "3ad90a34",
    "base_mode": "exact",
    "head_start": "3ad90a34c83c9283313f3d19baf80018a4e3630c",
    "head_end": "3ad90a34c83c9283313f3d19baf80018a4e3630c",
    "upstream_end": "3ad90a34c83c9283313f3d19baf80018a4e3630c",
    "branch": "int/2026-09-04-fan-wave-1"
  },
  "pathspec": [
    "tests/test_receipt_histsem.py",
    "docs/process_traces/2026-09-04-fanout/wave-1/05-sol-fix-round-2-report.md"
  ],
  "unowned_dirty": [
    "docs/process_traces/2026-09-04-fanout/wave-1/04a-magistrate-ruling-dr1-f1.md"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_receipt_histsem.PreAuthoringProjectionCustodyTests.test_projection_grammar_owner_mutation_reaches_both_consumers",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 0.332s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test in [0-9.]+s[\\s\\S]*OK$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -c 'import io,unittest; from unittest import mock; import joulewise.identity_pins as p; n=\"tests.test_receipt_histsem.PreAuthoringProjectionCustodyTests.test_projection_grammar_owner_mutation_reaches_both_consumers\"; s=unittest.defaultTestLoader.loadTestsFromName(n); b=io.StringIO(); m=mock.patch.object(p,\"_committed_successor\",side_effect=AssertionError(\"CRASH MUTANT\")); m.start(); r=unittest.TextTestRunner(stream=b).run(s); m.stop(); bad=r.failures+r.errors; assert r.testsRun==1 and not r.wasSuccessful() and len(bad)==1; print(\"_committed_successor crash-mutant: KILLED\"); print(\"test result: FAIL as expected\"); print(bad[0][1].strip().splitlines()[-1])'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "_committed_successor crash-mutant: KILLED",
          "test result: FAIL as expected",
          "AssertionError: CRASH MUTANT"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "_committed_successor crash-mutant: KILLED[\\s\\S]*AssertionError: CRASH MUTANT$"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_receipt_histsem tests.test_arm_readiness_schemas",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 104 tests in 2137.203s",
          "OK (skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 104 tests in [0-9.]+s[\\s\\S]*OK \\(skipped=1\\)$"
      }
    }
  ],
  "flags": []
}
```

## Change

Replaced the incomplete grammar-owner test with one that first proves a projection JSON coordinate is accepted by `_committed_successor` and excluded from authoring custody by `_histsem_tree_has_authoring_custody`, then removes JSON from the shared owner literal and proves that same coordinate is refused by both consumers. Both production consumers already route through the owner, so no production change was required.

## Verification notes

The required preflight was restricted to `tests.test_receipt_histsem` and `tests.test_arm_readiness_schemas`. The injected `_committed_successor` crash-mutant makes the named regression test fail, and the meta-check passes only when that failure is observed.
