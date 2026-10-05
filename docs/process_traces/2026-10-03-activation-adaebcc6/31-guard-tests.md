```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Added nine mutation-proven regressions and F3/F4/F6 corrections; requested 80-test suite passes.",
  "workspace": {
    "base_requested": "313a9da0",
    "base_mode": "exact",
    "head_start": "313a9da07f6a9f2115f99c16018db49f917cf29b",
    "head_end": "313a9da07f6a9f2115f99c16018db49f917cf29b",
    "upstream_end": null,
    "branch": "tests/2026-10-03-g2a-attach-guard-tests"
  },
  "pathspec": [
    "tests/test_harvest_g2a_window.py",
    "tests/test_g2a_calibration_attachment.py",
    "tests/test_battery_float_sweep.py",
    "joulewise/controller.py",
    "scripts/recover_calibration_ledger.py"
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
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B -m unittest tests.test_g2a_calibration_attachment tests.test_harvest_g2a_window tests.test_battery_float_sweep tests.test_gen_g2a_window",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 80 tests in 47.531s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 80 tests in [0-9.]+s\\s+OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B /tmp/adae-tests/sol-g2a-guards-0822qkgy/prove_mutations.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Killed 9/9 mutations; all scratch mutations reverted"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Killed 9/9 mutations; all scratch mutations reverted"
      }
    },
    {
      "id": "V3",
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
      "id": "V4",
      "kind": "other",
      "cmd": "/Users/edr/code/JouleWise/.venv/bin/python -B scripts/fixture_orphan_census.py --fail-on-orphans",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": ["{\"error\": \"PermissionError: [Errno 1] Operation not permitted: 'ps'\"}"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": ""
      }
    }
  ],
  "flags": [
    {
      "id": "ENV1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The sandbox denied ps, preventing the session-end orphan census. This is not a clean census result.",
      "needs": "Lead rerun V4 in an environment permitting ps."
    }
  ]
}
```

## Change

Added these tests. Each mutation was applied only in scratch, executed, and reverted. Every mutated test exited **1**; all nine unmutated tests passed.

| New test | Mutation killed | Executed failure |
|---|---|---|
| `test_crash_after_pre_with_uncommitted_seed_pin_refuses_first_ledger_load` | Remove first-load committed-pin requirement | RECOVER instead of REFUSED |
| `test_crash_after_pre_with_foreign_tail_refuses_first_ledger_load` | Remove harvest’s governed-tail check | RECOVER instead of REFUSED |
| `test_read_only_sources_recovery_rechecks_foreign_tail_before_creating_copies` | Remove recovery’s governed-tail check | CLI exit 0 instead of 3 |
| `test_member_config_content_must_equal_running_config_even_with_matching_sha` | Remove member-config equality | Expected ValueError absent |
| `test_byte_identical_pre_capture_at_another_path_is_not_the_finalized_slot` | Remove slot-locator equality | Expected ValueError absent |
| `test_attachment_bytes_must_match_each_finalized_slot_artifact_hash` | Remove slot artifact-hash comparisons | Five expected ValueErrors absent |
| `test_claim_eligible_plan_cannot_use_explicit_diagnostic_path` | Remove `claim_eligible is False` | Expected ValueError absent |
| `test_other_night_window_cannot_use_explicit_diagnostic_path` | Remove window/environment equality | Expected ValueError absent |
| `test_read_only_harvest_removes_terminal_lock_without_changing_ledger_bytes` | Remove lock cleanup | Terminal lock remained |

Exact mutations, commands, and failure tails are in [mutation evidence](/private/tmp/adae-tests/sol-g2a-guards-0822qkgy/mutation-evidence.json).

- **F3:** Corrected the docstring to describe the recorded fiducial bound and telemetry-owned `clock_anchor.status`. Controller executable AST is unchanged.
- **F4:** Named the G2-a explicit opt-in exception and its attachment tests.
- **F6:** Removed the derived lock after governed operations release their leases. Tests verify source preservation, reproducible terminal-ledger bytes, and lock absence from files and outputs.

Only the five authorized paths changed. No commit made; ready for lead diff review and pathspec commit.

## Verification notes

An initial helper test needed a resolved macOS temporary path. The first scratch proof attempt lacked Git HEAD metadata. Both were corrected; setup errors were excluded from mutation-kill evidence.

## Residual risk

The orphan census remains unverified because the sandbox denied `ps`; the lead must rerun V4.