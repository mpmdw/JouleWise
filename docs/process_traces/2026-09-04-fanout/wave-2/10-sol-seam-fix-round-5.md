```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Re-homed registry-extensible AP-2 validation in a fail-closed v2 sibling, preserved frozen v1 bytes, and aligned advisor site wording with D-136.",
  "workspace": {
    "base_requested": "d8c5213d35f4e8a974e8d0cdb440ff097b73dd28",
    "base_mode": "exact",
    "head_start": "d8c5213d35f4e8a974e8d0cdb440ff097b73dd28",
    "head_end": "d8c5213d35f4e8a974e8d0cdb440ff097b73dd28",
    "upstream_end": "d8c5213d35f4e8a974e8d0cdb440ff097b73dd28",
    "branch": "int/2026-09-04-fan-wave-2"
  },
  "pathspec": [
    "PROJECT_STATUS.md",
    "docs/process_traces/2026-09-04-fanout/wave-2/10-sol-seam-fix-round-5.md",
    "joulewise/analysis_manifest_v2.py",
    "tests/test_analysis_manifest_v2.py",
    "tests/test_modularity.py"
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
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_modularity.ClosedSetRegistryTests.test_analysis_condition_pairs_are_validated_as_registry_declarations tests.test_modularity.ClosedSetRegistryTests.test_frozen_ap2_row_requires_all_pairs_from_its_four_profiles",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 2 tests in 0.001s",
          "FAILED (failures=2)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 2 tests[\\s\\S]*OK$"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_analysis_manifest_v2 tests.test_modularity",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 14 tests in 1.246s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 14 tests[\\s\\S]*OK$"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "env PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_modularity tests.test_analysis_manifest_v3 tests.test_analysis_manifest_v2 tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 64 tests in 3.356s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 64 tests[\\s\\S]*OK$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The repository-wide suite was not run because this seat's preflight permits only four named test modules.",
      "needs": "The magistrate owns any broader final verification."
    }
  ]
}
```

## Change

The frozen v1 analysis-manifest module remains byte-identical to main. A new
v2 validator delegates exact v1 declarations unchanged, retains v1's non-
enumeration checks, and admits generalized metric rows only when their metric
and window-class identities come from the authenticated detection-floor
registry. The stale MODULARITY condition-pair tests now target that sibling.

Dedicated v2 regressions pin v1 bytes and equivalence, accept all nine frozen
detection-floor rows, reject an unregistered metric, and prove registry
authentication failure propagates closed. The advisor status page now calls
the retired site drift file reference-only and describes regeneration and
deployment as Ed's optional manual dispatch under D-136.

## Verification notes

V1 is the required red baseline at the issued head. V2 and V3 are the green
replays after the seam fix. No tests outside the preflight allowlist ran.

## Residual risk

Broader final-suite verification remains magistrate-owned.
