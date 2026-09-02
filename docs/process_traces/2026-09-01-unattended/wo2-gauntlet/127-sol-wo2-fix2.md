```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented all ruled WO-2 round-2 night-driver cures; 84 focused tests pass.",
  "workspace": {
    "base_requested": "8510e6dc",
    "base_mode": "exact",
    "head_start": "8510e6dc3365c7864524fd504df7efad59e58bd4",
    "head_end": "8510e6dc3365c7864524fd504df7efad59e58bd4",
    "upstream_end": "98ef40151c43e7511cca5bb99cf9a58ff0dafc68",
    "branch": "feat/2026-09-01-night-driver"
  },
  "pathspec": [
    "configs/launchd/com.joulewise.night.plist.template",
    "docs/process/NIGHT_COURIER_PROMPT.md",
    "joulewise/night_gate.py",
    "scripts/install_night_agent.sh",
    "scripts/run_night.py",
    "tests/test_gen_g2_phase_d.py",
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
      "cmd": "TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/night-driver.9CpV8b python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 59 tests in 0.039s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 59 tests in .*s[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "TMPDIR=/private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/night-driver.9CpV8b python3 -m unittest tests.test_run_night tests.test_gen_g2_phase_d tests.test_night_gate",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 84 tests in 1.076s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 84 tests in .*s[\\s\\S]*OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "origin/main advanced externally from d9357404 to 98ef4015 while session HEAD remained unchanged.",
      "needs": "Lead should review the final diff against current main before integration."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "No bridge BASELINE_MANIFEST or BASELINE_DIGEST was supplied; the requested exact HEAD and clean initial status were used.",
      "needs": "Runner or lead may perform its final scope-attribution check."
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Per instructions, no real chain, Claude courier, launchctl, or push was invoked.",
      "needs": "Stage-2 installed LaunchAgent rehearsal remains lead-owned."
    }
  ]
}
```

## Change

| Item | Cure | Regression test | Why it fails on `8f3d4adf` |
|---|---|---|---|
| B-A | `scripts/run_night.py:23,531,639`; plist `:18`; installer `:47`; prompt `:7` | `test_absolute_script_help_works_from_root_with_launchd_path`, `test_missing_courier_is_a_durable_driver_refusal`, `test_courier_spawn_failure_records_outcome_and_second_publish`, `test_installer_renders_working_directory_path_binary_and_distinct_logs` | Old import preceded `REPO_ROOT`, plist lacked environment/working directory, courier was PATH-only, boolean outcome was discarded, and no second publish existed. |
| B-B | `scripts/run_night.py:60,816` | `test_write_once_rerun_preserves_the_first_nights_records` | Old `_write_json` used overwriting `Path.write_bytes`; second invocation replaced evidence. |
| B-C | `scripts/run_night.py:41,172` | `test_driver_refusal_schema_is_exact_and_not_a_gate_receipt` | Old driver emitted the gate `SCHEMA` and had no refusal validator. |
| B-D | `scripts/run_night.py:314,367,1194` | `test_unproven_chain_termination_records_unkilled_and_spawns_no_courier`, `test_dead_man_reaps_a_gone_group_then_censuses_and_couriers`, `test_dead_man_refuses_a_proven_live_process_group` | Old termination returned `poll()` without proof and dead-man inferred liveness solely from marker existence. |
| B-E | `scripts/run_night.py:771,940` | `test_empty_non_json_and_missing_plans_refuse_and_attempt_courier` | Old `run_night` called `_load_plan` unguarded, producing a traceback. |
| B-F | `scripts/run_night.py:1033,1126` | `test_rehearsal_census_hits_are_observed_without_killing_the_stub` | Old census always aborted; a stub passed through `run` was treated as a refusal. |
| S-a | `scripts/run_night.py:44` | `test_courier_deadline_is_derived_from_the_measured_artifact` | Old constant was 600 rather than the ruled formula’s 300. |
| S-b | `scripts/run_night.py:618,639,984` | `test_courier_uses_one_launch_three_retries_and_every_backoff`, `test_courier_backoffs_do_not_enter_the_overrun_predicate`, `test_run_path_courier_hands_off_at_the_dead_man_epoch` | Old loop launched three times, slept only twice, had no lock/handoff, and added backoffs to the predicate. |
| S-c | `tests/test_gen_g2_phase_d.py:59` | `test_identity_date_equals_the_full_reviewed_reconstruction` | Old assertions used substring membership, so an appended mutant line passed. |
| S-d | `scripts/run_night.py:390,430,472` | `test_chain_exit_is_recorded_before_the_first_durable_publish`, `test_living_chain_records_a_thirty_second_census`, `test_durable_publish_uses_shallow_clone_and_named_results_branch_twice` | Old tests did not bind ordering, census count/interval, or exact clone/push argv. |
| S-e | `scripts/install_night_agent.sh:119,132` | `test_installer_refuses_active_chain_and_rolls_back_partial_bootstrap` | Old installer had no active-chain guard and its `set -e` loop could leave only the first plist bootstrapped. |
| S-f | `scripts/run_night.py:69,467,1194`; plist `:33` | `test_code_map_rejects_a_non_night_registry_member`, `test_night_date_uses_the_same_local_civil_day_as_dead_man`, `test_exclusive_record_writers_and_markers_are_fsynced` | Old code lacked prefix validation/fsync, used UTC for branch dates, skipped dead-man durable publication, and shared log names. |

New registered driver codes: `night_courier_running`, `night_courier_unavailable`, and `night_record_exists`.

## Verification notes

Regression failures against `8f3d4adf` were established from the cited pre-fix code rather than executing an extra test command. Test count increased from 59 to 84; the only permitted suite is green.