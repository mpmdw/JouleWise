```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented the PR-L fix round; all 681 requested tests pass with nine sandbox skips.",
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
    "tests/test_run_night_probe_cadence.py",
    "docs/phase_2/derivation_night_runbook.md",
    "tests/test_evidence_arm_sequence.py"
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
      "cmd": "python3 -m unittest tests.test_arm_retry tests.test_night_gate tests.test_night_agent_install tests.test_run_night tests.test_run_night_probe_cadence tests.test_launch_context_no_qos_override tests.test_install_night_agent tests.test_evidence_arm_sequence tests.test_evidence_night -q > /tmp/152c9255/prl-fix-final-all-nine.log 2>&1; rc=$?; tail -35 /tmp/152c9255/prl-fix-final-all-nine.log; exit $rc",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "WARNING: runway below the 40-minute planning default",
          "----------------------------------------------------------------------",
          "Ran 681 tests in 1034.143s",
          "",
          "OK (skipped=9)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK \\(skipped=9\\)"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_arm_retry -q > /tmp/152c9255/prl-fix-arm-retry-expanded.log 2>&1; rc=$?; tail -12 /tmp/152c9255/prl-fix-arm-retry-expanded.log; exit $rc",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 35 tests in 0.418s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK$"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_evidence_arm_sequence -q > /tmp/152c9255/prl-fix-evidence-arm-expanded.log 2>&1; rc=$?; tail -25 /tmp/152c9255/prl-fix-evidence-arm-expanded.log; exit $rc",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 4.282s",
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
      "level": "nonblocking",
      "text": "The T0_REHEARSAL R16 exemption remains the magistrate's provisional reading.",
      "needs": "Include it in the cold Fable final pass."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Nine process-census tests skipped in the sandbox; no live launchd or hardware run was performed.",
      "needs": "Lead retains live verification."
    }
  ]
}
```

## Change

Added the R16 reason to both policy tables, preserved the T0 rehearsal disjointness rule, bound install to the receipt’s rendered night and dead-man plists, and improved probe timeout cleanup and partial-frame diagnostics. The direct evidence-probe test now supplies the launch context that the normal probe publisher adds. No commit was made.

## Verification notes

The earlier run’s three failures and five errors were accounted for: three fixture calendar errors, three install-fixture digest mismatches, one test bound that predated the two-second TERM grace, and one direct evidence receipt missing launch context. The final combined run passed.

## Residual risk

The rehearsal exemption awaits the cold Fable final pass. Live process-group cleanup remains unverified in this sandbox.