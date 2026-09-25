```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented the A291 packer fix-round-2 changes and named regressions within the two-file write scope.",
  "workspace": {
    "base_requested": "20cd29de",
    "base_mode": "exact",
    "head_start": "20cd29de4cd8c177ab4f9c12c998cbbb32babac2",
    "head_end": "20cd29de4cd8c177ab4f9c12c998cbbb32babac2",
    "upstream_end": null,
    "branch": "fix/2026-09-24-a291-fix2-packer"
  },
  "pathspec": ["joulewise/scored_packer.py", "tests/test_scored_packer.py"],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_scored_registration tests.test_scored_packer",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 29 tests in 4.026s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 29 tests.*OK"}
    },
    {
      "id": "V2-base",
      "kind": "test",
      "cmd": "python3 -B -m unittest -v tests.test_scored_packer.ScoredPackerTests",
      "cwd": "/tmp/278ebc9e/seatP/base",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["Ran 37 tests in 4.297s", "FAILED (failures=5, errors=6)"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=5, errors=6\\)"}
    },
    {
      "id": "V2-head",
      "kind": "test",
      "cmd": "python3 -B -m unittest -v tests.test_scored_packer.ScoredPackerTests",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 37 tests in 9.860s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 37 tests.*OK"}
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_scored_registration tests.test_scored_packer tests.test_scored_roster_checker tests.test_scored_packer_stress",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 63 tests in 432.209s", "OK", "STRESS seed=291013 registrations=300 calls=4263 checker_calls=4863 violations=0", "STRESS seed=291014 registrations=300 calls=4253 checker_calls=4853 violations=0"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 63 tests.*OK"}
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --check; git status --short",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["diff check: no output", " M joulewise/scored_packer.py", " M tests/test_scored_packer.py"]},
      "expected": {"exit_code": 0, "tail_regex": "only the two write-scope paths"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_scored_packer.ScoredPackerTests.test_r4c_derived_structure_ast tests.test_scored_packer.ScoredPackerTests.test_r5b_no_trusted_mutable_cache_ast",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 2 tests in 7.197s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 2 tests.*OK"}
    },
    {
      "id": "C1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest discover -s tests",
      "cwd": ".",
      "observed": {"result": "fail", "exit_code": 130, "tail": ["Interrupted after about 604 of 7092 discovered tests; no failure marker before interruption", "KeyboardInterrupt"]},
      "expected": {"exit_code": 0, "tail_regex": "OK"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The broader canonical suite was interrupted after slow arm-readiness tests; the requested scored-module suite passed.",
      "needs": "Magistrate reruns the canonical suite on the integrated P/K head."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Replay at requeue entry has quadratic night-length cost; the pinned measurements are at most 47 ms at 15 events, 729 ms at 67, and 2.8 s at 131.",
      "needs": "Before a registration whose pack root has more than 60 loaded envelopes, remeasure per-call requeue cost and record it in the arm record."
    }
  ]
}
```

## Change

A291-POP-1 and the shared planned/executed fact calculation are in [_parent_facts](/Users/edr/code/wt-7370d0fb-a291p/joulewise/scored_packer.py:80), [_lever](/Users/edr/code/wt-7370d0fb-a291p/joulewise/scored_packer.py:106), and the single-return [_derived](/Users/edr/code/wt-7370d0fb-a291p/joulewise/scored_packer.py:130). The three-handler boundary is in [_checked_derived](/Users/edr/code/wt-7370d0fb-a291p/joulewise/scored_packer.py:134); `pack`, `requeue_overrun`, `_seal`, and [executed_status](/Users/edr/code/wt-7370d0fb-a291p/joulewise/scored_packer.py:476) use it.

The renamed [_live_index](/Users/edr/code/wt-7370d0fb-a291p/joulewise/scored_packer.py:70) refuses duplicate live placements. [_structure](/Users/edr/code/wt-7370d0fb-a291p/joulewise/scored_packer.py:145) now checks empty blocks and the ruled INV-11/INV-12 rows before derived arithmetic. [_seal](/Users/edr/code/wt-7370d0fb-a291p/joulewise/scored_packer.py:251) checks an input digest before structure and derived values; [requeue_overrun](/Users/edr/code/wt-7370d0fb-a291p/joulewise/scored_packer.py:390) always replays outside replay recursion. The trusted-output cache is removed. The contract’s FT/key/role/cell scope predicate was preserved.

The test-side [reseal and detail helpers](/Users/edr/code/wt-7370d0fb-a291p/tests/test_scored_packer.py:16) and all named regressions are in the allowed test file. These are the per-regression base/head tail outcomes from the archived `20cd29de` copy and this worktree:

| Regression | Base tail | Head tail | Test |
|---|---|---|---|
| R1 | `FAIL`; `stale_derived != inv_11` | `ok` | [R1](/Users/edr/code/wt-7370d0fb-a291p/tests/test_scored_packer.py:414) |
| R2 | `ERROR`; `ZeroDivisionError: division by zero` | `ok` | [R2](/Users/edr/code/wt-7370d0fb-a291p/tests/test_scored_packer.py:439) |
| R2b | `FAIL`; `stale_derived != inv_12` | `ok` | [R2b](/Users/edr/code/wt-7370d0fb-a291p/tests/test_scored_packer.py:446) |
| R3 | `ERROR`; `ZeroDivisionError: division by zero` | `ok` | [R3](/Users/edr/code/wt-7370d0fb-a291p/tests/test_scored_packer.py:433) |
| R4a | `ERROR`; `_parent_facts` absent | `ok` | [R4a](/Users/edr/code/wt-7370d0fb-a291p/tests/test_scored_packer.py:459) |
| R4b | `ERROR`; `_parent_facts` absent | `ok` | [R4b](/Users/edr/code/wt-7370d0fb-a291p/tests/test_scored_packer.py:500) |
| R4c | `FAIL`; `AssertionError: 9 != 1` | `ok` | [R4c](/Users/edr/code/wt-7370d0fb-a291p/tests/test_scored_packer.py:543) |
| R4d | `ERROR`; `ZeroDivisionError: division by zero` | `ok` | [R4d](/Users/edr/code/wt-7370d0fb-a291p/tests/test_scored_packer.py:506) |
| R4d-facts | `ERROR`; `_parent_facts` absent | `ok` | [R4d-facts](/Users/edr/code/wt-7370d0fb-a291p/tests/test_scored_packer.py:503) |
| R5a | `FAIL`; `PackingRefusal not raised` | `ok` | [R5a](/Users/edr/code/wt-7370d0fb-a291p/tests/test_scored_packer.py:530) |
| R5b | `FAIL`; `_TRUSTED_OUTPUTS` found | `ok` | [R5b](/Users/edr/code/wt-7370d0fb-a291p/tests/test_scored_packer.py:569) |

## Verification notes

V1–V5 passed as specified. The old checker and stress modules also passed in V3. The canonical suite was started but interrupted after about 604 tests because its early arm-readiness section was progressing slowly; it has no completed verdict for this head. Changes remain uncommitted for the magistrate.

## Residual risk

The replay cost measurement and over-60-envelope remeasurement duty are recorded in flag F2. No `NEEDS_RULING` item arose.