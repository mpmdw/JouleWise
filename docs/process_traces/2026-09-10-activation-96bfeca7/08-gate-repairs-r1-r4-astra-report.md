```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented R1–R4 with 16 passing regressions; combined verification exposes a D-138 issued-pin conflict and a confirmed baseline controller failure.",
  "workspace": {
    "base_requested": "ee25c47f",
    "base_mode": "descendant",
    "head_start": "190e11b630700a611aa07f8971c99ed8a1ed768e",
    "head_end": "190e11b630700a611aa07f8971c99ed8a1ed768e",
    "upstream_end": "190e11b630700a611aa07f8971c99ed8a1ed768e",
    "branch": "feat/2026-09-10-gate-sensibility-sweep"
  },
  "pathspec": [
    "joulewise/environment_admission.py",
    "joulewise/reduce.py",
    "joulewise/controller.py",
    "joulewise/load_transition_alignment.py",
    "tests/test_gate_sensibility_rounding.py",
    "docs/contracts/measurement_methodology.md",
    "docs/contracts/run_bundle_layout.md",
    "docs/contracts/load_transition_alignment.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_environment_admission tests.test_reduce tests.test_controller tests.test_load_transition_alignment tests.test_gate_sensibility_rounding tests.test_docs_freshness -v",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 264 tests in 365.176s",
          "FAILED (failures=2)",
          "UNITTEST_PROCESS_RC=1"
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
      "cmd": "python3 -m unittest tests.test_gate_sensibility_rounding -v",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 16 tests in 0.008s",
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
      "kind": "other",
      "cmd": "python3 scripts/gen_state.py --check",
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
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: R2 changes the reduce.py source bytes pinned by test_d138_reduce_source_bytes_remain_at_issued_pin and configs/calibration/calibration_acceptance_d079_v2_n17_r6.json. D-138 reserves acceptance reissue and dependent pin updates for the lead-owned atomic re-freeze. Neither the pin test nor the acceptance artifact was changed.",
      "needs": "Confirm the D-138 staging/reissue route for R2 and provide the exact successor scope if further worker implementation is required."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "test_powermetrics_retry_promotes_admitted_attempt_for_strict_reduce fails on idle_drift and idle_drift_bound_w reconstruction. Replaying it with all four production modules restored to original HEAD reproduced the same failure; the issued-pin test passed on that baseline.",
      "needs": "Lead triage of the pre-existing controller failure before final verification."
    }
  ]
}
```

## Change

Implemented the specified arithmetic repairs and contract sentences without deviations from seat A. All regressions are in `tests/test_gate_sensibility_rounding.py`.

Per-repair test names:

- **R1 ADMIT:** `test_r1_admits_interval_sum_rounded_out_of_epoch_duration`, `test_r1_admits_one_epoch_ulp_at_either_capture_endpoint`. **REFUSE:** `test_r1_refuses_ten_microsecond_duration_excess`, `test_r1_refuses_capture_outside_attempt_by_one_sample`.
- **R2 ADMIT:** `test_r2_admits_one_endpoint_ulp_at_both_shifted_edges`. **REFUSE:** `test_r2_refuses_two_endpoint_ulps_at_either_edge`, `test_r2_refuses_one_missing_sample_at_either_edge`. `test_r2_tail_gate_and_later_coverage_agree_on_epoch_endpoint` exercises both actual gates.
- **R3 ADMIT:** `test_r3_admits_thirty_second_span_rounded_inward_one_epoch_ulp`, `test_r3_admits_six_four_second_contributions_with_inward_epoch_rounding`. **REFUSE:** `test_r3_refuses_ten_microsecond_span_deficit`, `test_r3_refuses_ten_microsecond_coverage_deficit`, `test_r3_refuses_one_missing_sample_of_coverage`, `test_r3_refuses_first_recovery_at_or_after_three_hundred_second_cap`.
- **R4 ADMIT:** `test_r4_admits_eight_epoch_markers_using_endpoint_offset_midpoints`. **REFUSE:** `test_r4_refuses_one_microsecond_offset_mutation_with_unchanged_support`.

## Verification notes

Each repair was temporarily reverted independently:

- R1: duration and both endpoint ADMIT cases failed.
- R2: both edge cases failed; the later gate contradicted the earlier tail gate.
- R3: span recovery slipped to probe seven; coverage recovery became `cap_hit`.
- R4: artifact construction refused all eight support midpoints.

All repaired modules were restored byte-for-byte, including after baseline diagnosis. The final regression replay passed.

Combined verification preserved the unittest process’s exit code while displaying its final 30 lines. No full suite or hardware measurements ran.

**NEEDS_RULING:** Stage R2 for the D-138 atomic re-freeze, or authorize another integration route? Recommendation: retain the implemented diff and stage it for the lead-owned reissue. Weakening the pin test or blindly replacing the issued digest would violate D-138. Green combined verification remains blocked; successor naming and write scope belong to the lead.

No contract-document pin failure was found. No out-of-scope files were edited, and no commit was created.