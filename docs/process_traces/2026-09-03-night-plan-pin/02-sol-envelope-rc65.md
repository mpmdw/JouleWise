```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Night plans now pin the measurement checkout under schema v2; implementation is green, but cleanup of one accidentally generated out-of-scope bytecode file needs scope.",
  "workspace": {
    "base_requested": "2f59e791b166c6ec9f99cebdca315a8871678b2f",
    "base_mode": "exact",
    "head_start": "2f59e791b166c6ec9f99cebdca315a8871678b2f",
    "head_end": "2f59e791b166c6ec9f99cebdca315a8871678b2f",
    "upstream_end": "46eaf18c279edc76d0f1036abcbccc687ec85636",
    "branch": "feat/2026-09-03-night-plan-pin"
  },
  "pathspec": [
    "joulewise/night_gate.py",
    "scripts/run_night.py",
    "scripts/install_night_agent.sh",
    "tests/test_run_night.py",
    "tests/test_night_gate.py",
    "tests/test_install_night_agent.py",
    "docs/process_traces/2026-09-03-night-plan-pin/01-sol-landing-report.md",
    "joulewise/__pycache__/night_gate.cpython-314.pyc"
  ],
  "unowned_dirty": [],
  "verdict": {
    "counts": {
      "implementation_completed": 1,
      "tests_passed": 104,
      "mutation_probes_passed": 2,
      "blocking_scope_deviations": 1
    },
    "findings": [
      {
        "id": "NEEDS_SCOPE",
        "severity": "blocking",
        "summary": "Cleanup of one ignored bytecode file requires prospective scope."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_run_night tests.test_night_gate tests.test_install_night_agent",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 104 tests in 9.774s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 104 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "zsh -n scripts/install_night_agent.sh",
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
      "id": "V3",
      "kind": "inspection",
      "cmd": "git -C /Users/edr/JouleWise-measurement-20260813 rev-parse HEAD",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "eeb4e133815d0c12486d597d9434a2c18c83c1c4"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^[0-9a-f]{40}$"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": [
          "Ran 45 tests in 0.534s",
          "",
          "FAILED (failures=1, errors=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=1, errors=1\\)"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 45 tests in 0.533s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 45 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_install_night_agent",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": [
          "Ran 4 tests in 1.734s",
          "",
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_install_night_agent",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 4 tests in 2.141s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 4 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "git status --porcelain",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " M tests/test_run_night.py",
          "?? docs/process_traces/2026-09-03-night-plan-pin/",
          "?? tests/test_install_night_agent.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "tests/test_install_night_agent.py"
      }
    },
    {
      "id": "V9",
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
  "flags": [
    {
      "id": "NEEDS_SCOPE",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "NEEDS_SCOPE\nQuestion: May the resumed scope include joulewise/__pycache__/night_gate.cpython-314.pyc so it can be deleted?\nOptions considered: (1) grant the exact path for deletion; (2) leave the ignored bytecode in place and accept the recorded deviation.\nRecommendation: grant option 1 and delete only that generated bytecode file.\nCompleted authorized work: all v2 implementation, tests, mutation probes, named verification, and the landing report.\nBlocked work: cleanup of that one ignored generated bytecode file only.",
      "needs": "Add joulewise/__pycache__/night_gate.cpython-314.pyc to resumed WRITE_SCOPE for deletion."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "joulewise/__pycache__/night_gate.cpython-314.pyc"
    ],
    "reason": "An early py_compile invocation accidentally wrote this ignored generated file outside WRITE_SCOPE.",
    "blocked_work": "Delete the single ignored generated bytecode file and rerun the final scope inspection.",
    "minimal_change": "Delete only joulewise/__pycache__/night_gate.cpython-314.pyc."
  }
}
```

## Change

Night-plan schema v2 now requires an absolute measurement root and measurement HEAD.  
R-6 staleness compares the measurement checkout; dev HEAD movement is informational.  
Installation verifies both pins, while uninstall verifies neither.  
The focused suite passes 104 tests and both requested mutants were killed.  
The complete evidence and clause map are in [01-sol-landing-report.md](/Users/edr/code/JouleWise-wt-planpin/docs/process_traces/2026-09-03-night-plan-pin/01-sol-landing-report.md).

Files changed within scope:

- `joulewise/night_gate.py`
- `scripts/run_night.py`
- `scripts/install_night_agent.sh`
- `tests/test_run_night.py`
- `tests/test_night_gate.py`
- `tests/test_install_night_agent.py`
- `docs/process_traces/2026-09-03-night-plan-pin/01-sol-landing-report.md`

## Verification notes

Final suite tail:

```text
----------------------------------------------------------------------
Ran 104 tests in 9.774s

OK
```

Mutation tails:

```text
Ran 45 tests in 0.534s

FAILED (failures=1, errors=1)
```

```text
Ran 4 tests in 1.734s

FAILED (failures=1)
```

Both mutations were restored and their modules returned `OK`.

## Residual risk

The armed 2026-09-03 v1 plan must be re-authored under v2 before firing. Upstream also advanced to `46eaf18c…` during this session. Cleanup of the ignored bytecode artifact awaits the exact scope expansion above.