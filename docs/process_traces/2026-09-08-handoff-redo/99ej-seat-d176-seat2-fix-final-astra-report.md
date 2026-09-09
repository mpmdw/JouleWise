```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Finding 5 implemented; all 329 requested acceptance tests pass; canonical verification encountered sandbox process-identity failures.",
  "workspace": {
    "base_requested": "4b25d29f",
    "base_mode": "exact",
    "head_start": "4b25d29f8117249d30b4411a2cf9bc23808ccb09",
    "head_end": "4b25d29f8117249d30b4411a2cf9bc23808ccb09",
    "upstream_end": "99a42edbbb08098b7e4a0835e9e2f15cc51cd0b5",
    "branch": "feat/2026-09-08-d176-seat2-producer"
  },
  "pathspec": [
    "scripts/run_night.py",
    "tests/test_run_night.py",
    "docs/contracts/pack_night_go_receipt.md"
  ],
  "unowned_dirty": [
    "docs/contracts/pack_night_go_receipt.md",
    "joulewise/arm_readiness.py",
    "joulewise/night_gate.py",
    "joulewise/t0_rehearsal.py",
    "scripts/run_night.py",
    "tests/test_arm_readiness_schemas.py",
    "tests/test_magistrate_watchdog.py",
    "tests/test_night_gate.py",
    "tests/test_run_night.py"
  ],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "ready"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest tests.test_run_night.PackNightProducerTests.test_pack_standard_refusal_receipt_preserves_each_actual_cause > /tmp/d176-seat2-f5-regression.log 2>&1; result=$?; tail -n 5 /tmp/d176-seat2-f5-regression.log; exit $result",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest tests.test_night_gate tests.test_run_night tests.test_t0_rehearsal tests.test_rehearse_t0_unattended tests.test_arm_readiness_schemas tests.test_night_plan_writer tests.test_install_night_agent tests.test_magistrate_watchdog tests.test_docs_freshness > /tmp/d176-seat2-f5-acceptance.log 2>&1; result=$?; tail -n 14 /tmp/d176-seat2-f5-acceptance.log; exit $result",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 329 tests in 20.675s", "", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^OK"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 /tmp/d176-seat2-f5-inspect.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "PASS only three authorized paths changed since intake; all other tracked bytes preserved",
          "PASS frozen validator, keys, registries and chain-marker functions match HEAD; HEAD unchanged"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^PASS"
      }
    },
    {
      "id": "V5",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest discover -s tests > /tmp/d176-seat2-f5-canonical.log 2>&1; result=$?; tail -n 14 /tmp/d176-seat2-f5-canonical.log; exit $result",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 130,
        "tail": ["KeyboardInterrupt"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^OK"
      }
    },
    {
      "id": "V6",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp python3 -m unittest tests.test_axi_controller_events tests.test_axi_mock_spec tests.test_axi_output_identity > /tmp/d176-seat2-f5-identity-failures.log 2>&1; result=$?; tail -n 65 /tmp/d176-seat2-f5-identity-failures.log; exit $result",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 31 tests in 4.522s", "", "FAILED (failures=4)"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "(?m)^OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Canonical discovery reported four AXI campaign failures, reproduced by V6: campaign start identity unavailable. Direct inspection confirmed /bin/ps raises PermissionError and observe_identity returns UNKNOWN. V5 was interrupted at this environment blocker; no full-suite pass is claimed. Requested acceptance V2 passed.",
      "needs": "Lead to rerun canonical discovery in an environment permitting process-identity inspection."
    }
  ]
}
```

## Change

Finding 5 uses `night_probe_error`, registered at `joulewise/night_gate.py:75`, for driver-only causes. The writer at `scripts/run_night.py:1041` preserves the exact cause as `"<reason>: <detail>"` in receipt `refusal.detail`; `refusal.json` remains authoritative. Existing gate and GO-specific reasons remain unchanged.

The six-cause regression at `tests/test_run_night.py:1968` checks both artifacts agree, validates every receipt, preserves the result cause and confirms GO absence. Contract §10.3 records this representation at `docs/contracts/pack_night_go_receipt.md:1054`.

Previous fixes were preserved. Validator, keys and registries remain frozen. No commit made.

## Verification notes

Canonical discovery was interrupted after confirming four sandbox-dependent AXI failures; see the [focused failure log](/tmp/d176-seat2-f5-identity-failures.log). The next step is lead review and canonical verification where process inspection is permitted.

## Residual risk

Evidence remains fixture-based; integrated consumer and live hardware verification remain lead-owned.