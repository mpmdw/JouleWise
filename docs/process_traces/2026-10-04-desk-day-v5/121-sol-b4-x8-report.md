```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "partial",
  "summary": "P1 implemented and all 41 target IDs pass; full canonical verification remains incomplete.",
  "workspace": {
    "base_requested": "bda1c180",
    "base_mode": "exact",
    "head_start": "bda1c180cf156ecedcbe01a6010390dcd724c8cc",
    "head_end": "bda1c180cf156ecedcbe01a6010390dcd724c8cc",
    "upstream_end": "e7d13a1706d6352e0b3d9624dcf4c897671393da",
    "branch": "lane/2026-10-05-b4-x8"
  },
  "pathspec": [
    "configs/paper_supply/supply_map.json",
    "joulewise/arm_readiness_evidence_t0.py",
    "joulewise/prewindow.py",
    "scripts/capture_t0_step.py",
    "scripts/prewindow_check.sh",
    "tests/fixtures/custody_read_replay_allowlist.json",
    "tests/test_arm_readiness.py",
    "tests/test_arm_readiness_evidence_t0.py",
    "tests/test_arm_readiness_integration.py",
    "tests/test_arm_readiness_lifecycle.py",
    "tests/test_authentication_io.py",
    "tests/test_battery_float_consumers.py",
    "tests/test_bracket_binding_cli.py",
    "tests/test_capture_t0_step.py",
    "tests/test_install_night_agent.py",
    "tests/test_launch_window.py",
    "tests/test_launch_window_realization_recheck.py",
    "tests/test_night_agent_install.py",
    "tests/test_prewindow_check.py",
    "tests/test_v5_block4_x1.py",
    "tests/test_v5_block4_x2.py",
    "tests/test_v5_s1_desk_closeout.py",
    "tests/test_v5_s1_qualification.py"
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
      "cmd": "TMPDIR=/tmp/dd5-x8 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest -v $(python3 -c 'import json;print(\" \".join(r[\"id\"] for r in json.load(open(\"/tmp/dd5-x8/ids.json\"))))') tests.test_controller_battery_float tests.test_controller_g2b_attachment tests.test_v5_pack_regen",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (failures=35, errors=10)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^OK$"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-x8 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest -v $(python3 -c 'import json;print(\" \".join(r[\"id\"] for r in json.load(open(\"/tmp/dd5-x8/ids.json\"))))') tests.test_prewindow_check tests.test_capture_t0_step tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_authors_exact_fifteen_valid_rows_and_is_byte_idempotent tests.test_battery_float_consumers tests.test_revision6_seal",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "OK",
          "KILLED 130 owner-source mutations and 5 grant-policy mutations: stale receipts refused"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^OK$"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-x8 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest -v tests.test_v5_block4_x1 tests.test_v5_block4_x2 tests.test_v5_s1_desk_closeout tests.test_v5_s1_qualification tests.test_custody_mode_inventory tests.test_authentication_io tests.test_git_fixture_maintenance",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (errors=1)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^OK$"
      }
    },
    {
      "id": "V4",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-x8 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python -m unittest -v tests.test_v5_block4_x1 tests.test_custody_mode_inventory tests.test_authentication_io tests.test_git_fixture_maintenance",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "OK",
          "KILLED 3 renderer AST mutations: wrapper deletion, widened annotation, unregistered renderer"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^OK$"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "TMPDIR=/tmp/dd5-x8 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/dd5-x8/inspect-final.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["PASS: scope, syntax, sealed-shell equality, four estimator pins, and unchanged HEAD"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^PASS: scope, syntax, sealed-shell equality, four estimator pins, and unchanged HEAD$"
      }
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-x8 PYTHONDONTWRITEBYTECODE=1 /Users/edr/code/JouleWise/.venv/bin/python /tmp/dd5-x8/run-canonical.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": ["KeyboardInterrupt"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^OK(?: \\(.*\\))?$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Canonical discovery was interrupted after correcting the X1 fixture already loaded by discovery. 239 completed checks were observed; no completed full-suite result is claimed. Targeted verification is clean.",
      "needs": "Lead must run fresh canonical discovery before acceptance."
    }
  ]
}
```

## Change

P1 and all 41 listed failures are closed. The final focused run passed 109 tests; the corrected X1 and registration run passed 46 checks. Changes remain uncommitted.

The sealed shell matches `origin/main` byte-for-byte. T-0 uses the existing Python module’s `--t0-wait`, with CPU admission, report-only load, 600 seconds of continuous clean time, 30-second polling, and the frozen 45-minute command. Evidence records its module digest and command. The environment switch is removed.

Paper pins came from the repository’s `tests/fixtures/paper_custody/repin.py`, run in scratch. Its four generated digests were transferred while preserving pending roles. Acceptance validators and the four estimator files are untouched.

| Test ID | Classification | Change | Final result |
|---|---|---|---|
| #3 `tests.test_arm_readiness_lifecycle.ArmReadinessLifecycleTests.test_atomic_launch_capability_race_exactly_one_consumer_and_replay_refuses` | Stale fixture: roots | Canonical roots and context chain pin | PASS |
| #4 `tests.test_arm_readiness_lifecycle.ArmReadinessLifecycleTests.test_atomic_launch_capability_race_recheck_refuses_without_exec` | Stale fixture: roots | Canonical roots and context chain pin | PASS |
| #6 `tests.test_arm_readiness_lifecycle.ArmReadinessLifecycleTests.test_boot_session_change_voids_verification_and_consumption` | Stale fixture: roots | Canonical roots and context chain pin | PASS |
| #8 `tests.test_arm_readiness_lifecycle.ArmReadinessLifecycleTests.test_dry_run_is_rejected_by_launcher` | Stale fixture: roots | Canonical roots and context chain pin | PASS |
| #9 `tests.test_night_agent_install.RenderedProcessTypeTests.test_each_label_requires_parsed_interactive_value` | Stale fixture: plan schema | Add `receipt_class` | PASS |
| #12 `tests.test_arm_readiness.PackNightConsumerTests.test_four_case_purpose_root_table_through_consumer` | Stale fixture: roots | Refresh rehearsal context, chain, ARM and GO hashes together | PASS |
| #14 `tests.test_night_agent_install.RenderedProcessTypeTests.test_install_context_binds_both_labels_and_changed_template_bytes` | Stale fixture: plan schema | Add `receipt_class` | PASS |
| #15 `tests.test_launch_window.OperatorConfirmationDigestCliTests.test_launch_cli_real_chain_reaches_confirmation_authenticator` | Stale fixture: roots | Canonicalize ARM roots | PASS |
| #28 `tests.test_arm_readiness_integration.ArmReadinessIntegrationClockPortabilityTests.test_census_transaction_ignores_host_uptime` | Stale fixture: clock inputs | Native authenticated sizing and specified residual frequency | PASS |
| #29 `tests.test_paper_custody.RoundFiveTests.test_claim_gate_per_contrast` | Registration: paper supply receipt | Generated supply pins | PASS |
| #30 `tests.test_paper_custody.RoundFiveTests.test_closed_gate_registry` | Registration: paper supply receipt | Generated supply pins | PASS |
| #31 `tests.test_paper_custody.RoundFiveTests.test_contract_threat_model_matches_capability_wire` | Registration: paper supply receipt | Generated supply pins | PASS |
| #32 `tests.test_paper_custody.RoundFiveTests.test_d165_gate_branches_and_floor_acceptance` | Registration: paper supply receipt | Generated supply pins | PASS |
| #33 `tests.test_paper_rendering.PaperRenderingTests.test_d165_issued_control_and_subject_grants` | Registration: paper supply receipt | Generated supply pins | PASS |
| #34 `tests.test_launch_window_realization_recheck.LaunchRealizationRecheckTests.test_driver_barrier_does_not_collide_with_reserved_capability_fd198` | Stale fixture: started record | Current five-field record, including `monotonic_ns` | PASS |
| #35 `tests.test_launch_window_realization_recheck.LaunchRealizationRecheckTests.test_driver_clean_recheck_claims_once_before_real_exec_and_bundle` | Stale fixture: started record | Current five-field record, including `monotonic_ns` | PASS |
| #36 `tests.test_paper_custody.PaperCustodyCensusTests.test_every_family_actual_read_census_refuses_all_three_attack_arms` | Registration: paper supply receipt | Generated supply pins | PASS |
| #37 `tests.test_git_fixture_maintenance.GitFixtureMaintenanceTests.test_every_test_module_routes_git_initialization_through_shared_helper` | Registration: git fixture helper | Route all four initializers through the shared helper | PASS |
| #39 `tests.test_bracket_binding_cli.BracketBindingCliTests.test_finalizer_refuses_each_tampered_binding_without_output` | Stale assertion: refusal ordering | Assert the current endpoint refusal | PASS |
| #40 `tests.test_paper_custody.RoundFiveTests.test_fixture_results_never_enter_any_renderer` | Registration: paper supply receipt | Generated supply pins | PASS |
| #41 `tests.test_paper_custody.RoundFiveTests.test_gate_sources_change_receipt_digest` | Registration: paper supply receipt | Generated supply pins | PASS |
| #42 `tests.test_revision6_seal.RevisionSixSealTests.test_historical_bytes_and_shipped_pins_are_preserved` | Pin drift: lead ruling | Restore sealed bytes; separately pin T-0 dwell | PASS |
| #43 `tests.test_install_night_agent.InstallNightAgentTests.test_installer_refuses_outside_a_listed_install_span` | Stale fixture: battery time | Stamp reading with synthetic wall time | PASS |
| #44 `tests.test_launch_window.PackNightLaunchBoundaryTests.test_integrated_driver_arm_go_launcher_consumption_and_replay` | Stale fixture: roots | Preserve independent ARM/night custody and context pin | PASS |
| #45 `tests.test_paper_custody.RoundFiveTests.test_issuing_fixture_type_matrix` | Registration: paper supply receipt | Generated supply pins | PASS |
| #46 `tests.test_custody_mode_inventory.CustodyModeInventoryTests.test_line_shift_does_not_require_allowlist_edit` | Registration: read replay | Exact call, function and ordinal registrations | PASS |
| #47 `tests.test_paper_custody.PaperCustodyApiTests.test_malformed_pending_roles_refuse_every_fixture_family` | Registration: paper supply receipt | Generated supply pins | PASS |
| #48 `tests.test_authentication_io.AuthenticationSurfaceGuardTests.test_marked_v2_surface_has_no_direct_readable_io` | Registration: classified writer IO | Exact sites: 4024, 4042 and 4048 | PASS |
| #49 `tests.test_battery_float_consumers.ConsumerGuardTests.test_no_consumer_references_a_verdict_primitive` | Registration: battery consumers | Two exact raw-boundary calls; retain verdict restrictions | PASS |
| #50 `tests.test_paper_rendering.PaperRenderingTests.test_non_admission_carrier_is_deferred` | Registration: paper supply receipt | Generated supply pins | PASS |
| #52 `tests.test_custody_mode_inventory.CustodyModeInventoryTests.test_read_replay_inventory` | Registration: read replay | Exact call, function and ordinal registrations | PASS |
| #55 `tests.test_launch_window.ProductionArmRelocationLaunchTests.test_real_minted_v4_go_binds_root_and_refuses_content_change` | Stale fixture: clock inputs | Refresh native sizing after pack/head changes | PASS |
| #56 `tests.test_paper_custody.RoundFiveTests.test_refusal_condition_controls` | Registration: paper supply receipt | Generated supply pins | PASS |
| #57 `tests.test_paper_rendering.PaperRenderingTests.test_reported_energy_absent_projection_refuses_with_closed_code` | Registration: paper supply receipt | Generated supply pins | PASS |
| #58 `tests.test_paper_rendering.PaperRenderingTests.test_reported_energy_fixture_projection_renders_through_typed_field` | Registration: paper supply receipt | Generated supply pins | PASS |
| #59 `tests.test_paper_rendering.PaperRenderingTests.test_reported_energy_missing_or_malformed_cells_refuses_with_closed_code` | Registration: paper supply receipt | Generated supply pins | PASS |
| #60 `tests.test_custody_mode_inventory.CustodyModeInventoryTests.test_second_call_requires_its_own_allowlist_row` | Registration: read replay | Exact call, function and ordinal registrations | PASS |
| #61 `tests.test_arm_readiness_integration.ArmReadinessIntegrationTests.test_specified_census_observations_refuse_before_publication` | Stale fixture: clock inputs | CPU samples, native sizing and residual-frequency inputs | PASS |
| #63 `tests.test_battery_float_consumers.ConsumerGuardTests.test_test_files_use_no_primitive_outside_the_permitted_four` | Registration/fixture: battery primitive | Replay through `observe` with recorded bytes and clocks | PASS |
| #64 `tests.test_paper_rendering.PaperRenderingTests.test_tokenless_wrong_family_and_mixed_subjects_cannot_render` | Registration: paper supply receipt | Generated supply pins | PASS |
| #65 `tests.test_paper_custody.RoundFiveTests.test_unmapped_transitive_reads_and_root_aliases_refuse` | Registration: paper supply receipt | Generated supply pins | PASS |
| `tests.test_controller_battery_float` | Additional regression | Baseline rerun | PASS: 13 tests |
| `tests.test_controller_g2b_attachment` | Additional regression | Baseline rerun | PASS: 23 tests |
| `tests.test_v5_pack_regen` | Additional regression | Baseline rerun | PASS: 4 tests |
| `tests.test_capture_t0_step.CaptureT0StepTests.test_produces_all_eight_inputs_then_author_reaches_normal_derivation` | Additional fixture failure: clock inputs | Retain ancillary authenticated sizing inputs | PASS |
| `tests.test_v5_block4_x1.DwellTests.test_recovered_dwell_and_both_consumers_share_the_final_run` | Additional fixture failure: dwell pin | Supply repository identity and assert recorded module pin | PASS |

## Verification notes

V1 is the baseline: all 41 listed IDs reproduced their failures; the three additional modules introduced no new failure. Its 35 failures and 10 errors include repeated subtest failures. Rows 25, 26 and 62 were excluded and untouched.

For row 39, endpoint tampering now reaches `analysis_finalization_ledger_head_mismatch`. The digest and root mutations in the same test still reach `analysis_finalization_bracket_binding_mismatch`.

V3’s sole additional error was the minimal X1 fixture, corrected and covered by V4.

**FLAG F1:** Full canonical verification is unfinished. That attempt was interrupted after the X1 fixture correction; it had completed 239 checks without a reported test failure. Next step: lead reviews the diff and runs fresh canonical discovery before acceptance.