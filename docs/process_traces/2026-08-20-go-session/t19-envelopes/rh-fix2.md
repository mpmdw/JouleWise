```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented fail-closed committed-pinset lookup classification with three defect-shaped regressions.",
  "workspace": {
    "base_requested": "60ba2e925cd8d842c99030e1d0279681cc493530",
    "base_mode": "exact",
    "head_start": "60ba2e925cd8d842c99030e1d0279681cc493530",
    "head_end": "60ba2e925cd8d842c99030e1d0279681cc493530",
    "upstream_end": "60ba2e925cd8d842c99030e1d0279681cc493530",
    "branch": "impl/receipt-histsem"
  },
  "pathspec": [
    "joulewise/arm_readiness.py",
    "tests/test_receipt_histsem.py",
    "docs/contracts/receipt_histsem_verifier.md"
  ],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V0",
      "kind": "test",
      "cmd": "python3 -m unittest -v tests.test_receipt_histsem.ReceiptHistoricalSemanticsTests.test_gate_refuses_when_governed_clone_object_store_is_unreadable tests.test_receipt_histsem.ReceiptHistoricalSemanticsTests.test_committed_pinset_deletion_refuses_before_arm_custody tests.test_receipt_histsem.ReceiptHistoricalSemanticsTests.test_synthetic_pack_without_pinset_or_legacy_receipts_stays_ordinary > /tmp/receipt-histsem-fix2-regressions-round1.txt 2>&1; test_exit=$?; cat /tmp/receipt-histsem-fix2-regressions-round1.txt; exit $test_exit",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 3 tests in 7.589s",
          "FAILED (failures=2)"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=2\\)"
      }
    },
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_receipt_histsem -v > /tmp/receipt-histsem-fix2-unittest.txt 2>&1; test_exit=$?; printf '\\nCOMMAND_EXIT=%s\\n' \"$test_exit\" >> /tmp/receipt-histsem-fix2-unittest.txt; exit $test_exit",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 14 tests in 97.051s",
          "OK",
          "COMMAND_EXIT=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 14 tests in [0-9.]+s"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "python3 /tmp/receipt_histsem_round1_probe.py . current > /tmp/receipt-histsem-fix2-probe.txt 2>&1; test_exit=$?; cat /tmp/receipt-histsem-fix2-probe.txt; exit $test_exit",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "HEAD_PINSET_FAILURE_REFUSED_histsem_history_unavailable",
          "OBJECT_STORE_FAILURE_REFUSED_histsem_history_unavailable",
          "COMMITTED_PINSET_ABSENCE_REFUSED_histsem_pinset_absent",
          "COMMITTED_PINSET_ABSENCE_ARM_RETURNED",
          "COMMITTED_ROW_ABSENCE_GATE_SKIPPED",
          "COMMITTED_PINSET_MALFORMATION_OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "COMMITTED_PINSET_ABSENCE_REFUSED_histsem_"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 /tmp/receipt_histsem_contract_probe.py . > /tmp/receipt-histsem-fix2-contract-probe.txt 2>&1; test_exit=$?; cat /tmp/receipt-histsem-fix2-contract-probe.txt; exit $test_exit",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "CONTRACT_D16_PROBE_OK vocabulary=16"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "CONTRACT_D16_PROBE_OK vocabulary=16"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "python3 scripts/verify_receipt_histsem.py --repository-root . --require-published > /tmp/receipt-histsem-fix2-cli.txt 2>&1; test_exit=$?; printf '\\nCOMMAND_EXIT=%s\\n' \"$test_exit\" >> /tmp/receipt-histsem-fix2-cli.txt; cat /tmp/receipt-histsem-fix2-cli.txt; exit $test_exit",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "\"receipt_count\": 99,",
          "\"status\": \"PASS\"",
          "COMMAND_EXIT=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\"status\": \"PASS\""
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "r6_files=(configs/arm_readiness/legacy_receipt_histsem_pinset_v1.json joulewise/powermetrics_fiducial.py joulewise/uncertainty_evidence.py joulewise/adapters/powermetrics.py joulewise/reduce.py); git diff --quiet HEAD -- \"${r6_files[@]}\" && printf 'r6_pins=UNCHANGED\\n'",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "r6_pins=UNCHANGED"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "r6_pins=UNCHANGED"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git diff --check -- joulewise/arm_readiness.py tests/test_receipt_histsem.py docs/contracts/receipt_histsem_verifier.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "diff_check_exit=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "diff_check_exit=0"
      }
    },
    {
      "id": "V7",
      "kind": "suite",
      "cmd": "python3 -m unittest discover -s tests > /tmp/receipt-histsem-fix2-canonical-suite.txt 2>&1; test_exit=$?; printf '\\nCOMMAND_EXIT=%s\\n' \"$test_exit\" >> /tmp/receipt-histsem-fix2-canonical-suite.txt; exit $test_exit",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": 130,
        "tail": [
          "KeyboardInterrupt"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran .* tests.*OK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "Canonical discovery produced unrelated failures and stalled in an r6-pinned powermetrics test; it was interrupted with exit 130 after preserving the full output file.",
      "needs": "Lead should rerun or triage the canonical suite separately."
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "Round-1 uncommitted edits were present in all three scoped paths and were preserved.",
      "needs": "Review the combined round-1 plus round-2 diff before committing by pathspec."
    },
    {
      "id": "F3",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Only exact Git path-not-in-HEAD diagnostics enter case (b); all other nonzero lookups refuse as histsem_history_unavailable.",
      "needs": "Confirm the target Git diagnostic wording if portability beyond this environment is required."
    }
  ]
}
```

## Change

Implemented the fail-closed gate and R1–R3 regressions in the three scoped files. Added the eligibility-lookup semantics paragraph. No commit made.

`git show` path absence is matched exactly; execution failures use `histsem_git_unavailable`, other unreadable/ambiguous history uses `histsem_history_unavailable`, and receipt-shaped absent-pinset packs use `histsem_pinset_absent`.

## Verification notes

The requested 14-test suite, delta probe, contract probe, CLI verifier, diff check, and `r6_pins=UNCHANGED` inspection passed. No out-of-scope files changed.

## Residual risk

The full discovery suite needs a separate lead-controlled rerun/triage due unrelated failures and a long-running pinned powermetrics test.