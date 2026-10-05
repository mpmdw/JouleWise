```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Modernized the shared sizing fixture; requested modules ran, with one remaining refusal-code conflict requiring lead ruling.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "6796b8e033b8515e12b8c1e6a8da3b94014f7266",
    "head_end": "6796b8e033b8515e12b8c1e6a8da3b94014f7266",
    "upstream_end": "6796b8e033b8515e12b8c1e6a8da3b94014f7266",
    "branch": "feat/2026-10-05-v5-qualification-code"
  },
  "pathspec": [
    "tests/test_arm_readiness_evidence_t0.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "rg -l 'install_clock_sizing_inputs' tests/",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "tests/test_arm_readiness_evidence_t0.py",
          "tests/test_launch_window.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "tests/test_arm_readiness_evidence_t0.py\\ntests/test_launch_window.py"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "TMPDIR=/tmp/dd5-x11 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_evidence_t0 tests.test_arm_readiness_integration tests.test_launch_window tests.test_capture_t0_step > /tmp/dd5-x11/round2-requested.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "FAILED (failures=5, skipped=5)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^OK(?: \\(skipped=\\d+\\))?$"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/dd5-x11 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_authors_exact_fifteen_valid_rows_and_is_byte_idempotent tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_arm_consumes_volatile_receipts_within_short_horizon tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_clock_probe_publishes_exact_ruled_value_dictionary tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_versioned_receipts_author_steady_negative_drift_at_long_spans > /tmp/dd5-x11/round2-final-delta.log 2>&1",
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
        "tail_regex": "(?m)^OK$"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "TMPDIR=/tmp/dd5-x11 PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_arm_readiness_evidence_t0.ArmReadinessEvidenceT0Tests.test_each_absent_runbook_artifact_class_has_one_named_refusal > /tmp/dd5-x11/round2-diagnose-absent.log 2>&1",
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
        "tail_regex": "(?m)^OK$"
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
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "TMPDIR=/tmp/dd5-x11 PYTHONDONTWRITEBYTECODE=1 python3 scripts/fixture_orphan_census.py --fail-on-orphans > /tmp/dd5-x11/round2-orphan-census.json 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": [
          "{\"error\": \"PermissionError: [Errno 1] Operation not permitted: 'ps'\"}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": ".*"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: Should a missing window chain retain evidence_author_t0_window_chain_missing, or should the test accept evidence_author_t0_clock_attestation_underivable from the earlier authenticated-sizing replay? Options are preserving the named missing-artifact refusal through a production preflight repair, or changing the test's expected code. Recommend preserving the named refusal. Fixture modernization and independent test repairs are complete; green acceptance remains blocked. The assertion and production files were preserved.",
      "needs": "Rule refusal precedence. If preserving the named refusal, authorize the necessary production repair through a resumed WRITE_SCOPE."
    },
    {
      "id": "F2",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The required fixture-orphan census could not observe processes because the sandbox denies ps; no bypass was attempted.",
      "needs": "Run the fixture-orphan census in the lead's permitted environment."
    }
  ]
}
```

## Change

Added source-bound `t0_stage_cap` 3300 and `pack_t0` 360 allowances, derived the plan window through the writer, and updated consumer replay and clock-binding assertions. The writer’s exact-key check remains unchanged. Changes are uncommitted; nothing was pushed.

## Verification notes

The four-module run completed 167 tests. It began before the final test corrections and reported five failed assertions; four now pass in the final focused replay.

The remaining failure is the missing-chain refusal-code conflict described in F1. Next step: lead ruling on refusal precedence, followed by any authorized repair. The canonical suite was not run.