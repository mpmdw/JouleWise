```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Night-chain launch failures are durably refused and reported, dead-man recovery is null-safe, courier waits respect hand-off time, and all required mutation guards execute.",
  "workspace": {
    "base_requested": "224b22955fad2bda2618ec484e5a3e00812eb35b",
    "base_mode": "exact",
    "head_start": "224b22955fad2bda2618ec484e5a3e00812eb35b",
    "head_end": "224b22955fad2bda2618ec484e5a3e00812eb35b",
    "upstream_end": "224b22955fad2bda2618ec484e5a3e00812eb35b",
    "branch": "feat/2026-09-01-night-driver"
  },
  "pathspec": [
    "joulewise/night_gate.py",
    "scripts/run_night.py",
    "tests/test_night_gate.py",
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
      "cmd": "env TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/codex-night-round-three python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 88 tests in [0-9.]+s[\\s\\S]*OK"
      }
    }
  ],
  "flags": []
}
```

## Change

`night_chain_launch_failed` is the new registered driver code. Launch failure uses `EXIT_REFUSED` because no child process started; an unsuccessful courier can still return the existing `EXIT_COURIER_FAILED`.

| Item | Cure/guard | Test | Executed failure |
|---|---|---|---|
| F3 launch | `scripts/run_night.py:301,373,418,1195` | `test_chain_spawn_failure_records_refusal_and_finishes_reporting` | `AssertionError: chain launch failure escaped instead of becoming a refusal: chain executable missing` |
| F3 empty marker | `scripts/run_night.py:1283` | `test_dead_man_couriers_after_an_empty_start_marker_without_killpg` | `AssertionError: 3 != 0` |
| F3 null pgid | `scripts/run_night.py:1283` | `test_dead_man_couriers_after_a_null_pgid_marker_without_killpg` | `AssertionError: 3 != 0` |
| F1 `>` mutant | `scripts/run_night.py:1040` | `test_deadman_boundary_refuses_equality_and_allows_one_second_before` | `AssertionError: 0 != 3` |
| F1 inverse-`<=` mutant | `scripts/run_night.py:1040` | same | `AssertionError: 0 != 3` |
| F4 | `scripts/run_night.py:608` | `test_courier_wait_caps_sleep_at_the_dead_man_epoch` | `AssertionError: 1 not less than or equal to 0.3` |
| F2 reconstruction guard | `tests/test_gen_g2_phase_d.py:59` (unchanged) | `test_identity_date_equals_the_full_reviewed_reconstruction` | `AssertionError: ... '# mutant line\n' != ...` |
| F2 publish-order guard | `tests/test_run_night.py:766` (unchanged) | `test_chain_exit_is_recorded_before_the_first_durable_publish` | `AssertionError: 1 not less than 0` |
| F2 census guard | `tests/test_run_night.py:780` (unchanged) | `test_living_chain_records_a_thirty_second_census` | `AssertionError: 0 not greater than 0` |

Registry declaration is at `joulewise/night_gate.py:73`; exact-set coverage is at `tests/test_night_gate.py:786`.

## Verification notes

Test count: **84 → 88**. Baseline and final used the exact command recorded in V1: baseline `Ran 84 tests … OK`; final `Ran 88 tests … OK`.

Base-copy construction used `git archive 224b2295 | tar -x -C <prefix>` and copied the new test files over. Because archives omit Git metadata required by three pre-existing installer tests, each copy received the worktree’s read-only `.git` indirection before execution.

The same three-module command was executed from `base-regressions`, `gen-extra`, `exit-order`, `census-gap`, `boundary-strict`, and `boundary-inverse`. All intended pre-fix/mutant assertions failed. `git diff --check` passes; only the four reported files are dirty. No commit was created.