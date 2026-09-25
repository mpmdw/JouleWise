```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Corrected planned and executed parent positions; both 300-registration stress seeds pass the fixed checker.",
  "workspace": {
    "base_requested": "01badd6a",
    "base_mode": "exact",
    "head_start": "01badd6a58971f1b6b55af4d62c30f2b2a6f5d8c",
    "head_end": "01badd6a58971f1b6b55af4d62c30f2b2a6f5d8c",
    "upstream_end": null,
    "branch": "feat/2026-09-24-a291-packer-recut"
  },
  "pathspec": [
    "joulewise/scored_packer.py",
    "tests/test_scored_packer.py",
    "tests/test_scored_packer_stress.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_scored_registration tests.test_scored_packer tests.test_scored_packer_stress tests.test_scored_roster_checker tests.test_git_fixture_maintenance",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 57 tests in 189.522s",
          "OK",
          "STRESS seed=291013 registrations=300 calls=4263 checker_calls=4863 violations=0 edges={'E1': 262, 'E10': 76, 'E11': 37, 'E2': 1027, 'E3': 186, 'E4': 224, 'E5': 38, 'E6': 260, 'E7': 74, 'E8': 223, 'E9': 37}",
          "STRESS seed=291014 registrations=300 calls=4253 checker_calls=4853 violations=0 edges={'E1': 262, 'E10': 76, 'E11': 37, 'E2': 1028, 'E3': 186, 'E4': 224, 'E5': 38, 'E6': 260, 'E7': 74, 'E8': 223, 'E9': 37}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 57 tests in .*s\\s+OK[\\s\\S]*violations=0"
      }
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git status --porcelain",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " M joulewise/scored_packer.py",
          " M tests/test_scored_packer.py",
          " M tests/test_scored_packer_stress.py"
        ]
      },
      "expected": {"exit_code": 0, "tail_regex": "only WRITE_SCOPE paths"}
    }
  ],
  "flags": []
}
```

## Change

- **F1:** [_derived](/Users/edr/code/wt-a65fb4fa-a291/joulewise/scored_packer.py:77) now positions a parent from its live, non-terminal items. It counts fully non-terminal parents separately for spread and the lever’s null rule. The [R2 regression](/Users/edr/code/wt-a65fb4fa-a291/tests/test_scored_packer.py:254) pins the 02d arithmetic: `|(56 + 1 + 2 + 3 + 4)/5 − (5 + 6 + 7 + 8 + 9)/5| = 6.199999999999999` (6.2).
- **F2:** [executed_status](/Users/edr/code/wt-a65fb4fa-a291/joulewise/scored_packer.py:418) differed from M1. It now positions a parent with any counted window, while spread and the null rule use fully counted parents. [_live](/Users/edr/code/wt-a65fb4fa-a291/joulewise/scored_packer.py:72) selects placements live in their own envelopes.
- **F3:** The [partly counted regression](/Users/edr/code/wt-a65fb4fa-a291/tests/test_scored_packer.py:268) checks the executed lever against explicit arithmetic and the fixed checker. The [voided-attempt regression](/Users/edr/code/wt-a65fb4fa-a291/tests/test_scored_packer.py:228) now asserts packer–checker agreement.
- **F4:** The [stress test](/Users/edr/code/wt-a65fb4fa-a291/tests/test_scored_packer_stress.py:108) runs 300 registrations per seed and compares executed status with the checker. Both seeds had zero violations.

| Seed | E1 | E2 | E3 | E4 | E5 | E6 | E7 | E8 | E9 | E10 | E11 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 291013 | 262 | 1027 | 186 | 224 | 38 | 260 | 74 | 223 | 37 | 76 | 37 |
| 291014 | 262 | 1028 | 186 | 224 | 38 | 260 | 74 | 223 | 37 | 76 | 37 |

The exact acceptance command was `python3 -B -m unittest tests.test_scored_registration tests.test_scored_packer tests.test_scored_packer_stress tests.test_scored_roster_checker tests.test_git_fixture_maintenance`. Its result tail was `Ran 57 tests in 189.522s` and `OK`, followed by the two zero-violation stress lines recorded above.

## Residual risk

The magistrate should double-check the separate null and spread populations for partly terminal and partly counted parents. The R2 arithmetic test uses the checker’s hand-built roster; the executed regression and stress cases exercise production rosters. No commit was made.