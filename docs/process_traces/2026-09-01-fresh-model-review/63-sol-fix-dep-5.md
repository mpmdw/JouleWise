```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Applied all dictated pedagogy glosses and both code-verified clarifications, then regenerated and verified the dependence sheet.",
  "workspace": {
    "base_requested": "1f6182bd",
    "base_mode": "exact",
    "head_start": "1f6182bd9a0b54158c4bce1ca81a849ebc3f481f",
    "head_end": "1f6182bd9a0b54158c4bce1ca81a849ebc3f481f",
    "upstream_end": "1f6182bd9a0b54158c4bce1ca81a849ebc3f481f",
    "branch": "feat/2026-09-01-dependence"
  },
  "pathspec": [
    "docs/paper/round7/dependence-sensitivity.md.in",
    "docs/paper/round7/dependence-sensitivity.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "build",
      "cmd": "python3 scripts/dependence_sensitivity.py --render-sheet > docs/paper/round7/dependence-sensitivity.md",
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
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "python3 scripts/dependence_sensitivity.py --check-sheet; echo rc=$?",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "rc=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "rc=0"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_dependence_sensitivity tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 25 tests in 3.121s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --stat",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " docs/paper/round7/dependence-sensitivity.md    | 24 ++++++++++++------------",
          " docs/paper/round7/dependence-sensitivity.md.in | 24 ++++++++++++------------",
          " 2 files changed, 24 insertions(+), 24 deletions(-)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "2 files changed"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git status --short",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " M docs/paper/round7/dependence-sensitivity.md",
          " M docs/paper/round7/dependence-sensitivity.md.in"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "dependence-sensitivity.md.in"
      }
    },
    {
      "id": "V6",
      "kind": "lint",
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
  "flags": []
}
```

## Change

- Item 1 → line 3 → defined a contrast as one A-versus-B energy comparison and named decode/prefill phases.
- Item 2 → line 3 → explained metrology inputs as pre-issued uncertainty values.
- Item 3 → line 9 → defined total SE as repeat and metrology SE combined.
- Item 4 → line 11 → stated that cutoff equality rejects because comparison is inclusive.
- Item 5 → line 11 → defined the registered engine and distinguished its arithmetic from the sheet script.
- Item 6 → line 13 → explained that the energy-resolution floor comes from prior calibration and is fixed.
- Item 7 → line 19 → explained admission as registered member-run validity checking.
- Item 8 → lines 21 and 41 → defined composition and clarified the no-adjustment registered model.
- Item 9 → line 41 → defined rho as successive-block correlation.
- Item 10 → line 57 → glossed decode, prefill, and their registry-row suppliers.
- Item 11 → line 65 → connected pulse-shared calibration bounds to the sheet’s dependence question and explained H30.
- Item 12 → line 111 → defined gamma, DERIVE, binding token, AUTH, and DRAFT.
- Replication point → line 35 → explicitly states both intermediate and metrology-aware intervals use the same rounded critical value.
- Replication point → line 49 → states refusal compares computed degrees of freedom with one after flooring effective sample size.

## Verification notes

The existing contract test requires the literal substring “equality passes.” It remains only in the clarified wording “equality passes the rejection test,” immediately followed by the dictated inclusive-rejection explanation.