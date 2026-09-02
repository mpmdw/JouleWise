```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Added regression tests killing EXE-01 and EXE-03 while preserving the exactly-once projection lifecycle contract.",
  "workspace": {
    "base_requested": "01a94592",
    "base_mode": "exact",
    "head_start": "01a94592ad06efe7947b2abfedf63e93836227f3",
    "head_end": "01a94592ad06efe7947b2abfedf63e93836227f3",
    "upstream_end": "01a94592ad06efe7947b2abfedf63e93836227f3",
    "branch": null
  },
  "pathspec": [
    "tests/test_identity_pins.py"
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
      "cmd": "TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_identity_pins.PromptRealizationProjectionTests.test_digit_string_token_count_refused_at_freeze_and_arm_reverification tests.test_identity_pins.PromptRealizationProjectionTests.test_runtime_probe_prepares_and_cleans_up_once_for_two_configs",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 2 tests in 0.403s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_identity_pins.PromptRealizationProjectionTests.test_digit_string_token_count_refused_at_freeze_and_arm_reverification",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/EXE-01.WDMbbz",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 1 test in 0.324s",
          "",
          "FAILED (failures=2)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=2\\)"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_identity_pins.PromptRealizationProjectionTests.test_runtime_probe_prepares_and_cleans_up_once_for_two_configs",
      "cwd": "/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/EXE-03.fq6RYH",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: 2 != 1",
          "",
          "Ran 1 test in 0.105s",
          "",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "AssertionError: 2 != 1.*FAILED \\(failures=1\\)"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad /Users/edr/code/JouleWise/.venv/bin/python -m unittest tests.test_identity_pins tests.test_mlx_runtime",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 78 tests in 5.833s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 78 tests.*OK"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git status --porcelain",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " M tests/test_identity_pins.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^ M tests/test_identity_pins\\.py$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "After the named suite reported OK and exited 0, nanobind emitted an ignored atexit warning because no Metal device was available in the sandbox.",
      "needs": ""
    }
  ]
}
```

## Change

- `test_digit_string_token_count_refused_at_freeze_and_arm_reverification`, lines 1422–1492: pins freeze and arm refusal as `readiness_identity_artifact_unreadable`.
- `test_runtime_probe_prepares_and_cleans_up_once_for_two_configs`, lines 1494–1554: pins one prepare, one cleanup, and projections for both configs.

## Verification notes

EXE-01 mutant tail:

```text
AssertionError: IdentityPinProjectionError not raised
AssertionError: Lists differ: ['readiness_identity_environment_dirty'] != ['readiness_identity_artifact_unreadable']
FAILED (failures=2)
```

EXE-03 mutant tail:

```text
AssertionError: 2 != 1
FAILED (failures=1)
```

Named suite: 78 tests, OK. `git diff --check` passed; status contains only the authorized test file.