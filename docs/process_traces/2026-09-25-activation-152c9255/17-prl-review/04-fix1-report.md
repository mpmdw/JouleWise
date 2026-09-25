```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented the scoped PR-L fixes; two required verification failures need write-scope expansion.",
  "workspace": {
    "base_requested": "26c52306e7a8886f47ae0b3875228a9de3f135ec",
    "base_mode": "exact",
    "head_start": "26c52306e7a8886f47ae0b3875228a9de3f135ec",
    "head_end": "26c52306e7a8886f47ae0b3875228a9de3f135ec",
    "upstream_end": "26c52306e7a8886f47ae0b3875228a9de3f135ec",
    "branch": "feat/2026-09-25-acc-launch-context"
  },
  "pathspec": [
    "joulewise/arm_retry.py",
    "docs/process/NIGHT_HANDBACK.md",
    "joulewise/night_gate.py",
    "joulewise/night_agent_install.py",
    "scripts/run_night.py",
    "tests/test_arm_retry.py",
    "tests/test_night_gate.py",
    "tests/test_night_agent_install.py",
    "tests/test_run_night.py",
    "tests/test_run_night_probe_cadence.py"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "partial",
    "acceptance": "needs_ruling"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_night_gate tests.test_night_agent_install tests.test_run_night tests.test_run_night_probe_cadence tests.test_launch_context_no_qos_override tests.test_install_night_agent tests.test_evidence_arm_sequence tests.test_evidence_night -q > /tmp/152c9255/prl-fix-requested.log 2>&1; rc=$?; tail -60 /tmp/152c9255/prl-fix-requested.log; exit $rc",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 646 tests in 1114.459s",
          "FAILED (failures=3, errors=5, skipped=9)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_run_night tests.test_install_night_agent -q > /tmp/152c9255/prl-fix-calibration-rerun.log 2>&1; rc=$?; tail -35 /tmp/152c9255/prl-fix-calibration-rerun.log; exit $rc",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 298 tests in 174.156s",
          "OK (skipped=9)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=9\\)"
      }
    },
    {
      "id": "V3",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_night_gate tests.test_run_night_probe_cadence tests.test_night_agent_install.RenderedProcessTypeTests -q > /tmp/152c9255/prl-fix-final-fast.log 2>&1; rc=$?; tail -12 /tmp/152c9255/prl-fix-final-fast.log; exit $rc",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 110 tests in 6.395s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK$"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_arm_retry -q > /tmp/152c9255/prl-fix-arm-retry-final.log 2>&1; rc=$?; tail -16 /tmp/152c9255/prl-fix-arm-retry-final.log; exit $rc",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 35 tests in 0.424s",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK$"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_evidence_arm_sequence -q > /tmp/152c9255/prl-fix-evidence-arm-final.log 2>&1; rc=$?; tail -20 /tmp/152c9255/prl-fix-evidence-arm-final.log; exit $rc",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 1 test in 4.399s",
          "FAILED (errors=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK$"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
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
      "id": "V7",
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
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "test_arm_retry requires the new policy row in the mirrored generated block of docs/phase_2/derivation_night_runbook.md.",
      "needs": "Lead-issued WRITE_SCOPE expansion for that file."
    },
    {
      "id": "F2",
      "kind": "scope_deviation",
      "level": "blocking",
      "text": "test_evidence_arm_sequence directly creates a probe receipt without launch_context, then expects validate_install to accept it. The new required equality check correctly refuses it.",
      "needs": "Lead-issued WRITE_SCOPE expansion for tests/test_evidence_arm_sequence.py."
    },
    {
      "id": "F3",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "The T0_REHEARSAL R16 exemption is marked as the magistrate's provisional reading pending the cold Fable final pass.",
      "needs": "Carry the provisional reading to that pass."
    },
    {
      "id": "F4",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Nine process-census tests skipped in the sandbox; no live launchd or hardware validation was run.",
      "needs": "Lead retains live verification."
    }
  ],
  "scope_expansion": {
    "requested_paths": [
      "docs/phase_2/derivation_night_runbook.md",
      "tests/test_evidence_arm_sequence.py"
    ],
    "reason": "Both are required to make the requested verification green under the new reason registry and receipt-binding contract.",
    "blocked_work": "Synchronize the mirrored runbook policy row, update the direct evidence-probe fixture, and rerun their failing tests.",
    "minimal_change": "Add the exact measurement_root_outside_custody policy row to the runbook block; have the evidence-arm test supply the rendered launch context before expecting install acceptance."
  }
}
```

## Change

Registered the R16 cold-gate reason, added the provisional T0 rehearsal exemption and filesystem-identity custody check, bound install to the probe receipt’s night and dead-man digests, and improved timeout cleanup and partial-frame diagnostics. Added scoped regressions. No commit was made.

## Verification notes

The broad run’s seven in-scope failures were fixed; the subsequent 298-test rerun passed. The two remaining failures require the exact scope expansion above. The sandbox skipped nine process-census tests.

## Residual risk

The T0 rehearsal exemption remains provisional until the cold Fable final pass.