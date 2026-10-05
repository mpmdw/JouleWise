```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Adapted G10 fixtures and placement coverage; all 154 tests in the ten requested modules pass.",
  "workspace": {
    "base_requested": "57944785",
    "base_mode": "exact",
    "head_start": "57944785a609ae78717b14ae98812333087f23fe",
    "head_end": "57944785a609ae78717b14ae98812333087f23fe",
    "upstream_end": "e7d13a1706d6352e0b3d9624dcf4c897671393da",
    "branch": "lane/2026-10-05-b4-x9"
  },
  "pathspec": [
    "tests/test_t0_anchor_positive_control.py",
    "tests/test_v5_block4_x1.py"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_t0_anchor_positive_control tests.test_v5_block4_x1 > /tmp/dd5-x9/baseline.log 2>&1",
      "cwd": "/tmp/dd5-x9/base",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["FAILED (failures=8)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/dd5-x9 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_t0_anchor_positive_control tests.test_v5_block4_x1 tests.test_v5_block4_x9 tests.test_capture_t0_anchor_positive_control tests.test_capture_t0_anchor_positive_control_g10 tests.test_v5_qualification_plan tests.test_v5_s1_qualification tests.test_harvest_v5_qualification tests.test_v5_block4_composed tests.test_v5_block4_clock > /tmp/dd5-x9/round2-required.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 154 tests in 173.754s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK$"
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
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "At bda1c180, the two modules ran 44 tests with eight existing PositiveControlTests failures and no errors. X1 passed. The stale sizing fixture caused input_not_regular instead of the exact anchor refusal; fixture support now repairs these failures.",
      "needs": ""
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The original a1-placement custody test resides in tests/test_v5_block4_x4.py, outside WRITE_SCOPE. It remains untouched; equivalent adapted placement and support-mutation coverage was added to authorized X1.",
      "needs": "Lead should adapt the original X4 fixture before canonical verification."
    }
  ]
}
```

## Change

Added a schema-true collector response inside the offset band, sizing fixture support, and corrected polling stamps. X1 now checks strict `a2 expiry → G10 → s1` placement, rejects both boundary violations, and retains support-mutation refusal coverage.

Changes remain uncommitted; nothing was pushed.

## Verification notes

The stash-free parent copy at `bda1c180` already failed these eight `PositiveControlTests`:

- `test_custody_verifier_binds_supports_boot_code_and_order`
- `test_first_sigterm_during_off_cannot_interrupt_the_setter`
- `test_imported_on_vector_and_single_off_through_shared_producer`
- `test_negative_step_above_bound_also_discharges`
- `test_polling_waits_for_movement_without_repeating_on`
- `test_real_author_refusal_and_record_validate_under_evaluate_g10`
- `test_real_resync_shape_after_1600_seconds_of_drift_still_discharges`
- `test_residual_control_discharges_when_steady_drift_cancels_raw_movement`

The canonical suite was not started, as requested.

## Residual risk

Sizing replay uses an explicitly injected seam. Evidence remains fixture-only. The original X4 fixture still needs lead-side adaptation.