```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NOT-CLOSED: constructor aliasing plus a renamed readiness shortcut lets fabricated execution evidence pass both FIX-14 gates while the corrected writer is broken.",
  "workspace": {
    "base_requested": "bc01908",
    "base_mode": "exact",
    "head_start": "4495609c7eca5efd06e886f85bd857d9f80c2f53",
    "head_end": "4495609c7eca5efd06e886f85bd857d9f80c2f53",
    "upstream_end": "4495609c7eca5efd06e886f85bd857d9f80c2f53",
    "branch": "impl/d117-ledger-recovery"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "decision": "NOT-CLOSED",
    "classes": {
      "unexecuted-proof": "ALIVE (count 3)"
    },
    "findings": [
      {
        "id": "G1-1",
        "severity": "blocker",
        "title": "Aliased evidence construction defeats the FIX-14 provenance and execution gates",
        "site": "tests/test_calibration_exits.py:543,645-648,660-680; tests/owned_process_runner.py:42",
        "scenario": "In a temporary copy, EvidenceAlias = PublicExecutionEvidence was used to fabricate complete-looking writer records while _execute_valid_writer called ledger_module.calibration_readiness directly and never launched the capture writer. The real writer was additionally mutated to refuse every corrected --allow-live plus power-policy capture. Both the AST gate and test_correct_preflight_registry_executes_every_correction_surface still passed: Ran 2 tests in 27.327s, OK."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_exits.RefusalInventoryTests.test_correct_preflight_registry_executes_every_correction_surface tests.test_calibration_exits.RefusalInventoryTests.test_public_witness_ast_requires_owned_registered_executions tests.test_calibration_exits.PublicGovernedExitWitnessTests.test_parameterized_durable_public_cli_witnesses",
      "cwd": "$TMPDIR/joulewise-g1-delta2.pavvu5/base",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 3 tests in 392.638s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 3 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -c 'from joulewise.calibration_exits import RefusalCode; from tests.test_calibration_exits import PublicGovernedExitWitnessTests; PublicGovernedExitWitnessTests.execute_cases({RefusalCode.QUIET_MAC_AUTH_REQUIRED})'",
      "cwd": "$TMPDIR/joulewise-g1-delta2.pavvu5/delta1_allowlive",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": [
          "AssertionError: 2 != 0 : correction=calibration_quiet_mac_auth_required",
          "\"status\": \"refused\""
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "correction=calibration_quiet_mac_auth_required.*status.*refused"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_exits.RefusalInventoryTests.test_public_witness_ast_requires_owned_registered_executions",
      "cwd": "$TMPDIR/joulewise-g1-delta2.pavvu5/renamed_readiness",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 0.574s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test.*OK"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_exits.RefusalInventoryTests.test_correct_preflight_registry_executes_every_correction_surface",
      "cwd": "$TMPDIR/joulewise-g1-delta2.pavvu5/renamed_readiness",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": [
          "Items in the second set but not the first:",
          "calibration_quiet_mac_auth_required",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "calibration_quiet_mac_auth_required.*FAILED"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_exits.RefusalInventoryTests.test_public_witness_ast_requires_owned_registered_executions",
      "cwd": "$TMPDIR/joulewise-g1-delta2.pavvu5/fabricate_evidence",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": [
          "Lists differ: ['test_calibration_exits.py:82'] != []",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "test_calibration_exits.py:82.*FAILED"
      }
    },
    {
      "id": "V6",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_exits.RefusalInventoryTests.test_public_witness_ast_requires_owned_registered_executions",
      "cwd": "$TMPDIR/joulewise-g1-delta2.pavvu5/raw_launch",
      "observed": {
        "result": "pass",
        "exit_code": 1,
        "tail": [
          "test_calibration_exits.py:52:subprocess.run",
          "validate_powermetrics_fiducial.py",
          "FAILED (failures=1)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "subprocess.run.*validate_powermetrics_fiducial.py.*FAILED"
      }
    },
    {
      "id": "V7",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_calibration_exits.RefusalInventoryTests.test_public_witness_ast_requires_owned_registered_executions tests.test_calibration_exits.RefusalInventoryTests.test_correct_preflight_registry_executes_every_correction_surface",
      "cwd": "$TMPDIR/joulewise-g1-delta2.pavvu5/alias_fabrication",
      "observed": {
        "result": "fail",
        "exit_code": 0,
        "tail": [
          "Ran 2 tests in 27.327s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED|AssertionError"
      }
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "git rev-parse bc01908 && git diff --check bc01908..4495609 && git status --porcelain=v1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "bc01908d642663b00dfe4b5b46f1eb57d5fc3901"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "bc01908d642663b00dfe4b5b46f1eb57d5fc3901"
      }
    }
  ],
  "flags": []
}
```

## Findings

G1-1 — blocker — Verdict: NOT-CLOSED.

The literal AST probes work: raw `subprocess.run` and direct `PublicExecutionEvidence(...)` mutations were rejected. A renamed readiness-only helper also passed the AST gate but was rejected by the corpus exact-set gate.

However, the combined alias-fabrication mutation survived. The evidence AST check only recognizes calls whose callee is literally named `PublicExecutionEvidence` at `tests/test_calibration_exits.py:645-648`. The readiness check inspects only `_execute_case` and only two literal call forms at lines 660-680. The runtime gate at lines 543-598 trusts the supplied evidence fields without runner-origin provenance.

Thus `EvidenceAlias = PublicExecutionEvidence`, an indirect `ledger_module.calibration_readiness(...)`, and fabricated records satisfied both gates. The corpus remained green even after the real corrected capture path was mutated to refuse.

No collateral findings.

## Residual risk

This lens covered G1/FIX-14 only; FIX-15 through FIX-18 and the canonical suite were outside this fan-out item.

Checks performed: baseline three-test FIX-14 execution suite; delta-1 always-refuse replay; renamed-readiness evasion; literal constructor and raw-launch AST mutations; aliased-constructor plus broken-writer survivor probe; diff integrity and clean-worktree checks.

CLASS unexecuted-proof: ALIVE (count 3)