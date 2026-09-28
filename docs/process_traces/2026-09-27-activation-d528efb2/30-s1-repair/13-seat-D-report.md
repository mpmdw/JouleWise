```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Repaired 14 of 33 scouted outcomes in seat D; 19 legacy-identity outcomes need a ruling.",
  "workspace": {
    "base_requested": "4b4660dec4948f8b6d1f43a4d1e03569f886657b",
    "base_mode": "exact",
    "head_start": "4b4660dec4948f8b6d1f43a4d1e03569f886657b",
    "head_end": "4b4660dec4948f8b6d1f43a4d1e03569f886657b",
    "upstream_end": "e7c8bcc68d9a1c4f20e11c1904e49552c81ffcd1",
    "branch": "fix/2026-09-27-s1-regress-D"
  },
  "pathspec": [
    "tests/test_cli_run.py",
    "tests/test_cli.py",
    "tests/test_audit_amplification.py",
    "tests/test_powermetrics.py",
    "tests/test_package_bundle_pack.py",
    "tests/test_partial_record_enclosure.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_cli_run tests.test_cli tests.test_audit_amplification tests.test_powermetrics tests.test_package_bundle_pack tests.test_partial_record_enclosure -q > /tmp/s1-seat-d-final-modules.log 2>&1; result=$?; tail -n 50 /tmp/s1-seat-d-final-modules.log; exit $result",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 242 tests in 341.433s",
          "FAILED (failures=19)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 242 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_partial_record_enclosure -q",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 14 tests in 29.040s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 14 tests.*OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_capture_pipeline_era tests.test_environment_admission tests.test_idle_admission -q > /tmp/s1-seat-d-importers-small.log 2>&1; result=$?; tail -n 20 /tmp/s1-seat-d-importers-small.log; exit $result",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 44 tests in 11.684s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 44 tests.*OK"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONPATH=/Users/edr/code/JouleWise-wt-bk-77b1bee2/docs/process_traces/2026-09-27-activation-d528efb2/30-s1-repair/guard /opt/homebrew/bin/python3 -B -m unittest tests.test_capture_pipeline_era tests.test_environment_admission tests.test_idle_admission tests.test_run_campaign -q > /tmp/s1-seat-d-importers.log 2>&1; result=$?; tail -n 45 /tmp/s1-seat-d-importers.log; exit $result",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": 130,
        "tail": []
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran .* tests.*OK"
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
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "Eleven legacy-identity test IDs still fail in 19 outcomes. Their mock bundles spoof historical config digests or run IDs; rebinding and pairing exposes missing raw telemetry or changes the legacy raw verifier path.",
      "needs": "Rule the expectation and sibling-coverage treatment for the IDs listed below."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The whole test_run_campaign importer run was interrupted during a second extended AXI campaign and has no suite summary.",
      "needs": "Lead or seat A reruns tests.test_run_campaign under the battery guard."
    },
    {
      "id": "F3",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The importer process and a child attempted guarded ioreg probes; the owned six-module process made none.",
      "needs": "Seat A identifies and injects the runner at the affected test_run_campaign call sites."
    }
  ]
}
```

## Change

Evidence-bearing copied bundles now rebind their config before helper H writes an authenticated pair. Generated powermetrics runs use the injected battery runner, including every owned G10 test. The settled marker fixture now updates its config digest after editing the config. No assertions changed; **R-list: empty**.

| File | Scouted failures → passing |
|---|---:|
| `test_cli_run.py` | 25 → 8 |
| `test_cli.py` | 1 → 1 |
| `test_audit_amplification.py` | 4 → 2 |
| `test_powermetrics.py` | 1 → 1 |
| `test_package_bundle_pack.py` | 1 → 1 |
| `test_partial_record_enclosure.py` | 1 → 1 |

## NEEDS_RULING

**Question:** How should the legacy compatibility tests retain their downstream coverage when their forged historical identity is refused by S1’s battery gate?

**Options considered:** A rebound non-mock bundle with a pair reaches missing raw telemetry or a different legacy raw verifier failure. Keeping a mock config and adding a pair violates A1. Replacing the asserted result with battery refusal would require an approved R-list and evidence-bearing sibling tests.

**Recommendation:** Rule the refusal expectations and the sibling tests that preserve each legacy validator assertion. The blocked IDs are:

- `tests.test_cli_run.StrictValidateTests`: `test_all_six_allowlisted_legacy_bundles_keep_dispatch_semantics`, `test_allowlisted_legacy_fresh_idle_metadata_mismatch_fails_strict`, `test_allowlisted_legacy_present_non_object_provenance_fails_strict`, `test_allowlisted_legacy_present_null_provenance_fails_strict`, `test_allowlisted_legacy_recorded_value_mutations_fail_strict`, `test_current_bundle_spoofed_as_legacy_with_absent_provenance_passes`, `test_legacy_dispatch_tolerates_governed_additive_absence`, `test_legacy_summary_missing_additive_null_keys_passes_strict`, `test_legacy_summary_missing_honesty_fields_keeps_strict_tolerance`.
- `tests.test_audit_amplification.StrictGateInteractionAmplification`: `test_allowlisted_legacy_identity_allows_missing_workload_provenance`, `test_legacy_summary_tolerance_does_not_hide_raw_to_trace_order_drift`.

## Verification notes

V1’s 19 failures are confined to those 11 IDs. V4 was interrupted with Ctrl-C after more than ten minutes; no test summary was produced, and no process was left running. The guard blocked its `ioreg` attempts. No full suite, commit, or out-of-scope edit was made.