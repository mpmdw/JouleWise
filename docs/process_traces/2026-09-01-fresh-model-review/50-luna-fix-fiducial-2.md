```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented the amended receipt inventory, regressions, suite-cost reduction, and contract corrections.",
  "workspace": {
    "base_requested": "aa2a7d89",
    "base_mode": "exact",
    "head_start": "aa2a7d89fe40b3f8a7c84d347ddb56c28954c5da",
    "head_end": "aa2a7d89fe40b3f8a7c84d347ddb56c28954c5da",
    "upstream_end": "aa2a7d89fe40b3f8a7c84d347ddb56c28954c5da",
    "branch": "feat/transfer-fiducial-01"
  },
  "pathspec": [
    "joulewise/transfer_fiducial.py",
    "tests/test_transfer_fiducial.py",
    "tests/test_transfer_fiducial_v2_plan.py",
    "docs/contracts/transfer_fiducial.md"
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
      "cmd": "python3 -m unittest tests.test_transfer_fiducial tests.test_transfer_fiducial_v2_plan",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 25 tests in 33.085s",
          "",
          "OK",
          "python3 -m unittest tests.test_transfer_fiducial   32.74s user 0.46s system 99% cpu 33.238 total"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK$"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_powermetrics_fiducial tests.test_calibration_bracketing tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 126 tests in 59.292s",
          "",
          "OK (skipped=1)",
          "python3 -m unittest tests.test_powermetrics_fiducial    59.08s user 0.35s system 99% cpu 59.473 total"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=1\\)$"
      }
    },
    {
      "id": "V3",
      "kind": "lint",
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
      "kind": "inspection",
      "cmd": "git status --short",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " M docs/contracts/transfer_fiducial.md",
          " M joulewise/transfer_fiducial.py",
          " M tests/test_transfer_fiducial.py",
          " M tests/test_transfer_fiducial_v2_plan.py"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^ M docs/contracts/transfer_fiducial\\.md\\n M joulewise/transfer_fiducial\\.py\\n M tests/test_transfer_fiducial\\.py\\n M tests/test_transfer_fiducial_v2_plan\\.py$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The required review artifacts were absent as working-tree files; exact reachable Git blobs were read from ad0a50b7 and 49cc86d0.",
      "needs": ""
    }
  ]
}
```

## Change

| Item | Changed | Regression | Observed |
|---|---|---|---|
| A2 | Curated 24-path inventory, canonical digest, v2 schema, named mismatches: `joulewise/transfer_fiducial.py:47-83,205-243,1036-1135` | Trace drift test, old-schema test, 24 mutation cases | 25 tests pass |
| B1 | Stderr assertion: `tests/test_transfer_fiducial_v2_plan.py:386-404` | `test_prompt_pin_authority_and_runtime_mismatches_refuse` | Named runtime mismatch captured |
| C2 | One real traced fit; receipt tests use fixture fits: `tests/test_transfer_fiducial.py:339-474,574-783` | Focused suite wall time 33.238s | Under 60s |
| C1 | Producer flags and absent-branch status: `docs/contracts/transfer_fiducial.md:302-316` | Contract parser-text regression | Pass |
| A1 | Sequencing note and regex SHAPE correction: `docs/contracts/transfer_fiducial.md:53-83` | Contract regression | Pass |
| A3 | Record-only; trace files untouched | Inspection | No trace changes |

All eight starting inventory modules existed at HEAD; none were dropped. The trace added these 16 modules: `adapters/__init__.py`, `adapters/local_transport.py`, `adapters/mock_runtime.py`, `adapters/mock_spec_runtime.py`, `adapters/mock_telemetry.py`, `adapters/suite_control.py`, `arm_readiness.py`, `authentication_io.py`, `axi_decode_config.py`, `bundle.py`, `clock_reference.py`, `cooldown_anchor.py`, `identity_pins.py`, `interfaces.py`, `provenance.py`, and `suite.py`.

Mutation refusal reasons:

| Module | Exact reason |
|---|---|
| `joulewise/transfer_fiducial.py` | `pre_data_receipt_joulewise/transfer_fiducial.py_source_sha256_mismatch` |
| `joulewise/powermetrics_fiducial.py` | `pre_data_receipt_joulewise/powermetrics_fiducial.py_source_sha256_mismatch` |
| `joulewise/uncertainty_evidence.py` | `pre_data_receipt_joulewise/uncertainty_evidence.py_source_sha256_mismatch` |
| `joulewise/clock.py` | `pre_data_receipt_joulewise/clock.py_source_sha256_mismatch` |
| `joulewise/schemas.py` | `pre_data_receipt_joulewise/schemas.py_source_sha256_mismatch` |
| `joulewise/validation.py` | `pre_data_receipt_joulewise/validation.py_source_sha256_mismatch` |
| `joulewise/adapters/powermetrics.py` | `pre_data_receipt_joulewise/adapters/powermetrics.py_source_sha256_mismatch` |
| `joulewise/bundle_read.py` | `pre_data_receipt_joulewise/bundle_read.py_source_sha256_mismatch` |
| `joulewise/adapters/__init__.py` | `pre_data_receipt_joulewise/adapters/__init__.py_source_sha256_mismatch` |
| `joulewise/adapters/local_transport.py` | `pre_data_receipt_joulewise/adapters/local_transport.py_source_sha256_mismatch` |
| `joulewise/adapters/mock_runtime.py` | `pre_data_receipt_joulewise/adapters/mock_runtime.py_source_sha256_mismatch` |
| `joulewise/adapters/mock_spec_runtime.py` | `pre_data_receipt_joulewise/adapters/mock_spec_runtime.py_source_sha256_mismatch` |
| `joulewise/adapters/mock_telemetry.py` | `pre_data_receipt_joulewise/adapters/mock_telemetry.py_source_sha256_mismatch` |
| `joulewise/adapters/suite_control.py` | `pre_data_receipt_joulewise/adapters/suite_control.py_source_sha256_mismatch` |
| `joulewise/arm_readiness.py` | `pre_data_receipt_joulewise/arm_readiness.py_source_sha256_mismatch` |
| `joulewise/authentication_io.py` | `pre_data_receipt_joulewise/authentication_io.py_source_sha256_mismatch` |
| `joulewise/axi_decode_config.py` | `pre_data_receipt_joulewise/axi_decode_config.py_source_sha256_mismatch` |
| `joulewise/bundle.py` | `pre_data_receipt_joulewise/bundle.py_source_sha256_mismatch` |
| `joulewise/clock_reference.py` | `pre_data_receipt_joulewise/clock_reference.py_source_sha256_mismatch` |
| `joulewise/cooldown_anchor.py` | `pre_data_receipt_joulewise/cooldown_anchor.py_source_sha256_mismatch` |
| `joulewise/identity_pins.py` | `pre_data_receipt_joulewise/identity_pins.py_source_sha256_mismatch` |
| `joulewise/interfaces.py` | `pre_data_receipt_joulewise/interfaces.py_source_sha256_mismatch` |
| `joulewise/provenance.py` | `pre_data_receipt_joulewise/provenance.py_source_sha256_mismatch` |
| `joulewise/suite.py` | `pre_data_receipt_joulewise/suite.py_source_sha256_mismatch` |

No `NEEDS_SCOPE` items. The tree is intentionally left dirty and uncommitted.