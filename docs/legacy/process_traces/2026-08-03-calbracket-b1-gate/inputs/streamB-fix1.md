```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "B1/B2/S1 are implemented and fully verified, but the sandbox prevented the required commit by denying access to the external Git worktree index.",
  "workspace": {
    "base_requested": "83831134492d463bc7dc7408a7162ee39a07692e",
    "base_mode": "exact",
    "head_start": "83831134492d463bc7dc7408a7162ee39a07692e",
    "head_end": "83831134492d463bc7dc7408a7162ee39a07692e",
    "upstream_end": null,
    "branch": "impl/cal-bracket-d079"
  },
  "pathspec": [
    "joulewise/calibration_bracketing.py",
    "joulewise/calibration_ledger.py",
    "joulewise/whole_window.py",
    "tests/test_calibration_bracketing.py",
    "tests/test_calibration_ledger.py",
    "tests/test_whole_window_selection.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_calibration_ledger tests.test_calibration_bracketing tests.test_whole_window_selection tests.test_reduce",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 209 tests in 102.062s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 209 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 2453 tests in 640.474s",
          "OK (skipped=85)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2453 tests.*OK \\(skipped=85\\)"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "Overlay the three changed test modules on a git archive of 8383113, run the four B1/B2 regressions, and require the unittest command to exit nonzero.",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 4 tests in 0.006s",
          "FAILED (failures=4, errors=1)",
          "EXPECTED_PRE_FIX_RED rc=1"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "EXPECTED_PRE_FIX_RED rc=1"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "Run the four named S1 tests under isolated in-memory mutants restoring caller-root enumeration, treating prior content as new, counting only new valid observations, and removing predecessor-conflict reporting.",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "cross_root failures=1 errors=0",
          "prior_set failures=1 errors=0",
          "total_38 failures=1 errors=0",
          "fork failures=1 errors=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "cross_root failures=1.*prior_set failures=1.*total_38 failures=1.*fork failures=1"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff --check",
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
      "kind": "environment",
      "level": "blocking",
      "text": "git commit failed before staging because the sandbox cannot create /Users/edr/code/JouleWise/.git/worktrees/calbracket/index.lock; verified HEAD therefore remains 8383113.",
      "needs": "Lead must stage the six pathspec files and create the single audit-citing commit."
    }
  ]
}
```

## Change

B1 now loads and enforces the canonical ledger snapshot for minted sessions and refuses explicit minted secondary verification without a ready session.

B2 preserves `abandoned` as the immutable receipt state while classifying it as R2 `unresolved`, retaining authenticated content identity and refusing new abandoned attempts with or without content.

All four S1 tests now discriminate their exact narrow defects. Audit-passing structures were left untouched.

## Verification notes

The pre-fix blocker replay was red exactly as required. Each S1 single-defect mutant also made only its corresponding regression red.

The verified diff SHA-256 is `eeccea3e0436dad024e3060c0598e3fbd54e8ee66577b0b692ad80903e94b867`.

## Residual risk

The sole incomplete requirement is the commit. Run:

```sh
git add joulewise/calibration_ledger.py joulewise/calibration_bracketing.py joulewise/whole_window.py tests/test_calibration_ledger.py tests/test_calibration_bracketing.py tests/test_whole_window_selection.py
git commit -m "D-109: close cal-bracket audit B1/B2/S1" -m "Close independent audit blockers B1 and B2 plus should-fix S1: enforce the ledger snapshot for minted consumption, classify abandoned attempts as unresolved, and make the four regression fences defect-shaped."
```