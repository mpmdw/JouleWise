```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Fixed all 12 reported failures; requested tests have only the exempt watchdog timeout; canonical verification needs fixture scope.",
  "workspace": {
    "base_requested": "2c1f64de",
    "base_mode": "exact",
    "head_start": "2c1f64de7ebbe915abf38ed2c51fb07f9ef919a8",
    "head_end": "2c1f64de7ebbe915abf38ed2c51fb07f9ef919a8",
    "upstream_end": "2c1f64de7ebbe915abf38ed2c51fb07f9ef919a8",
    "branch": "feat/2026-10-05-v5-qualification-code"
  },
  "pathspec": [
    "joulewise/night_gate.py",
    "tests/test_capture_t0_step.py",
    "tests/test_v5_block4_x1.py",
    "tests/test_v5_block4_x10.py",
    "tests/test_v5_block4_x2.py",
    "tests/test_v5_block4_x4.py"
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
      "cmd": "TMPDIR=/tmp/dd5-x11 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_v5_block4_x7 tests.test_v5_block4_x9 tests.test_v5_block4_x10 tests.test_v5_block4_x6 tests.test_v5_block4_x4 tests.test_v5_block4_x1 tests.test_v5_block4_x2 tests.test_v5_qualification_plan tests.test_v5_s1_qualification tests.test_v5_s1_desk_closeout tests.test_harvest_v5_g2b_window tests.test_harvest_v5_qualification tests.test_v5_block4_replay tests.test_v5_block4_clock tests.test_v5_block4_composed tests.test_t0_anchor_positive_control tests.test_capture_t0_anchor_positive_control tests.test_capture_t0_anchor_positive_control_g10 tests.test_prewindow_check tests.test_capture_t0_step tests.test_revision6_seal tests.test_battery_float_consumers tests.test_git_fixture_maintenance tests.test_authentication_io tests.test_custody_mode_inventory tests.test_run_night tests.test_night_gate > /tmp/dd5-x11/focused.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FAILED (failures=1, skipped=13)",
          "KILLED 3 renderer AST mutations: wrapper deletion, widened annotation, unregistered renderer"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^OK(?: \\(skipped=\\d+\\))?$"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-x11 PYTHONDONTWRITEBYTECODE=1 python3 /tmp/dd5-x11/run_night_without_exempt_watchdog.py > /tmp/dd5-x11/run-night.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK (skipped=10)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^OK \\(skipped=10\\)$"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/dd5-x11 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_authors_exact_fifteen_valid_rows_and_is_byte_idempotent > /tmp/dd5-x11/shared-fixture.log 2>&1",
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
      "cmd": "TMPDIR=/tmp/dd5-x11 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests > /tmp/dd5-x11/canonical.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": 130,
        "tail": ["KeyboardInterrupt"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^OK(?: \\(skipped=\\d+\\))?$"
      }
    },
    {
      "id": "V5",
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
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "V1 ran 787 tests; its sole failure was BindSupervisionProcessTests.test_blocked_journal_never_blocks_deadline_or_grants_go hitting the 8-second sandbox watchdog. The prompt explicitly exempts these timing failures. V2 passed 283 driver tests with only this case additionally skipped.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "NEEDS_SCOPE: the existing shared install_clock_sizing_inputs fixture omits X10 t0_stage_cap and makes the out-of-scope authoring test fail with fixed.keys. It was preserved unchanged. Canonical discovery was started, then stopped after the blocker was independently reproduced; its full result is unavailable.",
      "needs": "Expand WRITE_SCOPE to tests/test_arm_readiness_evidence_t0.py, modernize the shared fixture, and rerun canonical discovery."
    }
  ],
  "scope_expansion": {
    "requested_paths": ["tests/test_arm_readiness_evidence_t0.py"],
    "reason": "The shared synthetic sizing helper predates ruling 76 addendum E and omits its required source-bound stage cap.",
    "blocked_work": "Shared authoring regressions and complete green canonical verification; all 12 reported integration failures are fixed.",
    "minimal_change": "Add the source-bound 3300-second stage allowance to install_clock_sizing_inputs and rebind sizing, chain, authorization, plan and clock-binding digests; consolidate the capture-local fixture refresh."
  }
}
```

## Change

All twelve reported failures are fixed. The production gate now applies authenticated stage sizing to both `s1` and `s2`. The remaining fixes update stale fixtures; no validator thresholds were relaxed. Changes remain uncommitted, and the pinned estimator files were untouched.

Authority below is the registration draft and ruling 76 A–E on `origin/design/2026-10-04-v5-qualification-block`. `Xn` abbreviates `tests.test_v5_block4_xn`.

| Test | Cause | Contract that wins | Change |
|---|---|---|---|
| X7 `test_fresh_attempt_go_uses_frozen_calibration_identity` | `s2` fell into the 2700-second fallback | X10 / E.2, with X7 history | Apply authenticated stage cap to `s2` |
| X7 `test_s2_assembly_and_desk_consume_authenticated_occurrence` | Same cap mismatch | X10 / E.2 | Same production fix |
| X7 `test_s2_runtime_observation_and_control_order_bind_the_written_chain` | Same cap mismatch | X10 / E.2 | Same production fix |
| X7 `test_tooling_recover_to_s2_writer_and_authenticated_plan_replay` | Same cap mismatch | X10 / E.2 | Same production fix |
| X2 `test_external_events_census_is_identical_across_reharvest` | Missing pinned occurrence and history binding | X7 / D.1 | Bind static authority and canonical re-harvest layout |
| X2 `test_pack_off_only_at_producer_path_and_pack_window_identity` | Missing occurrence; bad-witness case mutated archived bytes | X7 / D.1; immutable re-harvest contract | Bind history; use a separate bad-witness fixture |
| X2 `test_prepare_fault_publishes_refusal_without_escaping` | Missing pinned occurrence/history | X7 / D.1 | Bind authority and attempt archive |
| X2 `test_prepared_events_survive_refusal_before_launch_authentication` | Missing occurrence/history and stale archive layout | X7 / D.1 | Bind authority and canonical re-harvest path |
| X1 `test_driver_stages_native_sequence_unattended_before_arm_and_refuses_partial_retry` | Fixture lacked authenticated sizing inputs | X10 / E.2 | Use real writer fixture; assert 3300-second cap |
| X1 `test_capture_timeout_preserves_partial_output_and_refuses_cleanly` | Same missing binding prevented reaching timeout | X10 / E.2 | Supply authenticated plan/sizing; retain partial-output assertions |
| X4 `test_assembler_authenticates_native_phase_plan_and_raw_bytes` | Raw readings lacked lifecycle bindings | X6; registration §3.7 | Bind plan, prepare, check, install and native T-0 receipt |
| Capture `test_produces_all_eight_inputs_then_author_reaches_normal_derivation` | Shared fixture omitted `t0_stage_cap` | X10 / E.2 | Add source-bound cap locally and refresh dependent digests |

## Verification notes

The required 787-test run had only the explicitly exempted watchdog timeout. The driver rerun skipped that single case.

Canonical verification remains blocked by the unchanged, out-of-scope shared fixture’s [`fixed.keys` failure](/tmp/dd5-x11/shared-fixture.log). The runner’s exhaustive `WRITE_SCOPE` excludes its owning file. The next step is a lead-issued scope expansion for `tests/test_arm_readiness_evidence_t0.py`, followed by the shared-fixture repair and canonical rerun.