```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented ruled C1-C3 night-driver cures with 95 scoped tests passing and all five required mutants killed.",
  "workspace": {
    "base_requested": "66e496a534baa4d523164647023587d978ca663e",
    "base_mode": "exact",
    "head_start": "66e496a534baa4d523164647023587d978ca663e",
    "head_end": "66e496a534baa4d523164647023587d978ca663e",
    "upstream_end": "66e496a534baa4d523164647023587d978ca663e",
    "branch": "feat/2026-09-01-night-driver"
  },
  "pathspec": [
    "scripts/run_night.py",
    "scripts/install_night_agent.sh",
    "tests/test_run_night.py"
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
      "cmd": "python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "cd /private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/night-driver-d1/prefix && TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/night-driver-d1/tmp python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FAILED (failures=5)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=5\\)"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/night-driver-d1/tmp python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
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
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "cd /private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/night-driver-d1/mut-a && TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/night-driver-d1/mut-a/tmp python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FAILED (failures=3)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "cd /private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/night-driver-d1/mut-b && TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/night-driver-d1/mut-b/tmp python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FAILED (failures=1, errors=6)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED"
      }
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "cd /private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/night-driver-d1/mut-c && TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/night-driver-d1/mut-c/tmp python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FAILED (failures=3)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED"
      }
    },
    {
      "id": "V8",
      "kind": "test",
      "cmd": "cd /private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/night-driver-d1/mut-d && TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/night-driver-d1/mut-d/tmp python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED"
      }
    },
    {
      "id": "V9",
      "kind": "test",
      "cmd": "cd /private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/night-driver-d1/mut-e && TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/night-driver-d1/mut-e/tmp python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FAILED (failures=2)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The initial 88-test command failed one pre-existing installer PATH assertion because this environment aliases the temporary directory as /private in zsh but /var in Python. The prescribed TMPDIR run passes.",
      "needs": ""
    }
  ]
}
```

## Change

Implemented C1 shared completion-epoch guard, C2 dead-man-hour installer refusal, and C3 fresh-custody record refusal. Existing post-night dead-man tests now explicitly run at the completion epoch.

## Verification notes

Test count: 88 → 95. The pre-fix archive used `git archive 66e496a5`, the updated test file, and a read-only `.git` link for installer head validation.

| Item | Cure | Test | Executed pre-fix result |
|---|---|---|---|
| C1 immediate | `scripts/run_night.py:1271` | `test_dead_man_stands_down_immediately_after_t0_on_empty_night` | `:375 self.assertEqual(set(night.iterdir()), entries_before)`; unexpected census/courier files |
| C1 pre-epoch | `scripts/run_night.py:1271` | `test_dead_man_stands_down_one_second_before_completion_epoch` | `:400 self.assertEqual(set(night.iterdir()), entries_before)`; unexpected census/courier files |
| C1 D1 fixture | `scripts/run_night.py:1271` | `test_dead_man_empty_start_marker_waits_until_completion_epoch` | `:436 self.assertFalse((night / "chain.exited").exists())`; `True is not false` |
| C2 | `scripts/install_night_agent.sh:58` | `test_installer_refuses_the_dead_man_hour_before_rendering` | `:1146 self.assertEqual(completed.returncode, 2)`; `0 != 2` |
| C3 | `scripts/install_night_agent.sh:123` | `test_installer_refuses_a_stale_courier_sent_before_bootstrap` | `:1190 self.assertEqual(completed.returncode, 3)`; `0 != 3` |

The completion-boundary and stale-uninstall continuation tests passed pre-fix as expected.

## Mutants

| Mutant | Killed by |
|---|---|
| Remove C1 guard | Three C1 stand-down tests |
| `<` → `<=` | `test_dead_man_absent_marker_at_completion_epoch_couriers` |
| Guard on `t0` | Three C1 stand-down tests |
| Remove C2 | `test_installer_refuses_the_dead_man_hour_before_rendering` |
| Remove C3 | `test_installer_refuses_a_stale_courier_sent_before_bootstrap` |