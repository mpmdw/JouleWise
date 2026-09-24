```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Bound night_kinds.py into the idle manifest, removed the gate import fallback, and proved the fixed-fixture artifact delta.",
  "workspace": {
    "base_requested": "55a1e87d",
    "base_mode": "exact",
    "head_start": "55a1e87da633c3bf62493a7196a49ec13acac6bc",
    "head_end": "55a1e87da633c3bf62493a7196a49ec13acac6bc",
    "upstream_end": "55a1e87da633c3bf62493a7196a49ec13acac6bc",
    "branch": "feat/2026-09-23-a280-kind-table"
  },
  "pathspec": [
    "joulewise/night_gate.py",
    "joulewise/quiet_predicate_campaign.py",
    "tests/test_evidence_night.py",
    "tests/test_night_kinds.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -B -m unittest tests.test_night_kinds tests.test_evidence_night tests.test_night_gate tests.test_quiet_predicate_campaign tests.test_arm_retry tests.test_night_plan_writer tests.test_launch_window tests.test_magistrate_watchdog_cli tests.test_run_night tests.test_evidence_arm_sequence tests.test_arm_census tests.test_quiet_admission tests.test_sample_quiet_predicate_evidence tests.test_night_agent_install tests.test_gen_evidence_night tests.test_install_night_agent tests.test_gen_derivation_night tests.test_agent_census_concurrency tests.test_arm_readiness",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 1101 tests in 1700.342s",
          "FAILED (failures=3, errors=1, skipped=12)"
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
      "cmd": "python3 -B -m unittest tests.test_night_kinds",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 3 tests in 0.448s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_evidence_night.LifecycleTests.test_b6_clone_old_census_literal_is_reported",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 0.459s",
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
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_sample_quiet_predicate_evidence.LoadTests.test_load_join_ladder_accepts_slow_exit_and_escalates_a_stuck_child",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 1.662s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "git diff 55a1e87d --check",
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
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The composition fixture clones committed HEAD 55a1e87d. Its old generator writes the old manifest, while the working-tree installer expects the new entry.",
      "needs": "Magistrate commits the allowed diff, then reruns the composition test and named acceptance command."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The two process-list cases still fail inside this sandbox; the magistrate already reran both outside it and reported Ran 2, OK.",
      "needs": ""
    },
    {
      "id": "F3",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "A sampler SIGTERM timing assertion failed in the long combined run and passed alone on immediate rerun.",
      "needs": "Magistrate checks the timing case during postcommit acceptance."
    },
    {
      "id": "F4",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Static import survey finds 82 reachable in-repo Python files outside MANIFEST_PATHS, including joulewise.corecaptured_loop.",
      "needs": "Route manifest completeness to the separate lane under R3."
    }
  ]
}
```

## Change

**R1 — manifest binding.** [quiet_predicate_campaign.py](/Users/edr/code/wt-d8cc9c0a-a280a/joulewise/quiet_predicate_campaign.py:84) now includes `joulewise/night_kinds.py` in `MANIFEST_PATHS`. In the fixed base-archive fixture, the manifest’s only map change is:

| Entry | SHA-256 |
|---|---|
| Added `joulewise/night_kinds.py` | `f3433bfb505f608c032a1493ee83c484f92a2dd63bd1f6777ae8a486070c18f3` |

The manifest digest changes from `3f6b0039c0799be4f79e5c4ab2c21e1aa10aa9db8e3c77ded00dd85b5330f9bb` to `ff865fe5d933b92b185189d6e6f9c06cd92b7f5f0ad08cccd48fe606fd37f995`. Its wrapper checksum changes from `b0cae3484ccbd33be7c3f3a981cb1df3c55eac6cc80777464b5e6bff10c0d0f2` to `4ae0b2f63af2d60dd9a01bf82570a8028a53b0cf59d7e97c0a0a97b60cf0c5dc`.

The [K3 test](/Users/edr/code/wt-d8cc9c0a-a280a/tests/test_night_kinds.py:203) compares all manifest fields, asserts `old files ∪ {night_kinds} == new files`, checks canonical manifest bytes, and substitutes the old manifest and wrapper digests with the new ones before comparing every other text artifact byte for byte. The eight stored goldens were regenerated with the same fixture module against the `git archive cdc05e9b` copy under `/tmp`; all eight matched exactly. The fixed base H lacks `night_kinds.py`, so this comparison supplies that one file’s bytes to manifest authoring. Current-H sealed-candidate verification remains a postcommit check.

**R2 — unconditional import.** [night_gate.py](/Users/edr/code/wt-d8cc9c0a-a280a/joulewise/night_gate.py:28) imports the table directly. The import-time Git check and duplicate legacy rows are gone. The isolated A277 fixture now copies its sibling at [tests/test_evidence_night.py:877](/Users/edr/code/wt-d8cc9c0a-a280a/tests/test_evidence_night.py:877); that is the only change in that test file.

**R3 — report-only import survey.** I followed static `import`/`from` statements, relative imports, package initializers, and literal `import_module` calls. All seven Python files in `MANIFEST_PATHS` reach the same cycle. In the table, **M** is the seven manifested Python files named in its rows; **U** is the 82 **NOT manifested** files listed below. Each row reaches the other six members of M and every member of U.

| Manifested module | Transitive manifested imports | Transitive NOT manifested imports |
|---|---|---|
| `joulewise.night_agent_install` | M minus self | U |
| `joulewise.night_gate` | M minus self | U |
| `joulewise.night_kinds` | M minus self | U |
| `joulewise.quiet_admission` | M minus self | U |
| `joulewise.quiet_predicate_campaign` | M minus self | U |
| `scripts.run_night` | M minus self | U |
| `scripts.sample_quiet_predicate_evidence` | M minus self | U |

**U — NOT manifested** (names in each line use the stated prefix):

- `joulewise.`: `__init__`, `aggregate`, `analysis_manifest`, `analysis_manifest_v3`, `arm_readiness`, `arm_readiness_evidence`, `arm_readiness_evidence_t0`, `arm_retry`, `authentication_io`, `axi_decode_config`, `bundle`, `bundle_read`, `calibration_bracketing`, `calibration_custody_worker`, `calibration_epoch_continuation`, `calibration_exits`, `calibration_ledger`, `campaign_provenance`, `cli`, `clock`, `clock_reference`, `controller`, `cooldown`, `cooldown_anchor`, **`corecaptured_loop`**, `detection_floor`, `detection_floor_registry`, `determinism_gate`, `doctor`, `dominance_closeout`, `envelope_gate`, `environment`, `environment_admission`, `floor_extraction`, `identity_pins`, `idle_admission`, `idle_dependence`, `interfaces`, `kv_size`, `measurement_liveness`, `output_identity`, `powermetrics_fiducial`, `provenance`, `publication_privacy`, `receipt_oracle`, `reduce`, `report`, `salvage_dangler`, `sampler_teardown`, `schemas`, `suite`, `t0_rehearsal`, `uncertainty_evidence`, `validation`, `whole_window`, `zero_capture_facts`.
- `joulewise.adapters.`: `__init__`, `local_transport`, `mlx_runtime`, `mock_runtime`, `mock_spec_runtime`, `mock_telemetry`, `node_client`, `nvidia_smi`, `powermetrics`, `ssh_transport`, `suite_control`, `vllm_runtime`.
- `joulewise.analysis_engine.`: `__init__`, `artifact`, `claims`, `distributions`, `estimators`, `inputs`, `multiplicity`, `ratio`, `registry`, `sensitivity`.
- `scripts.`: `fixture_orphan_census`, `magistrate_watchdog`, `reserve_calibration_window_bracket`, `validate_powermetrics_fiducial`.

This is a static reachability survey, including imports inside functions and conditional paths; it does not claim every module executes in an idle night. The protocol JSON and zsh chain entries in `MANIFEST_PATHS` are not Python modules. No R3 files were added to the manifest.

## Verification notes

The exact named acceptance command is V1 in the envelope. It ran **1,101 tests in 1700.342s** and ended `FAILED (failures=3, errors=1, skipped=12)`:

- The composition error is the precommit H mismatch described in F1. Its fixture clones HEAD before the working-tree manifest addition exists there.
- `test_real_collect_no_power_reaps_all_recorded_workers` and `test_cleanup_refusal_reports_the_failure_it_interrupted` encountered this sandbox’s unavailable process list. The magistrate’s outside-sandbox rerun passed both: **Ran 2, OK**.
- `test_load_join_ladder_accepts_slow_exit_and_escalates_a_stuck_child` observed SIGKILL instead of SIGTERM in the combined run; its exact named rerun passed (**Ran 1, OK**).

The R2 isolated fixture test passed (**Ran 1, OK**), the K3 module passed (**Ran 3, OK**), and `git diff 55a1e87d --check` passed. `git diff 55a1e87d --stat` names only the four `pathspec` files above. No commit was made.

## Residual risk

The magistrate should double-check the manifest and sealed-candidate path against the **committed new H**, then rerun the composition test and named acceptance command. The separate manifest-completeness lane should decide how to handle U, especially `joulewise.corecaptured_loop`.