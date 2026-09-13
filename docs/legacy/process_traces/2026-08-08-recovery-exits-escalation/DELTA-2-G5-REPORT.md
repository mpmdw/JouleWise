```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "NOT-CLOSED: FIX-18 misses keyword-only helper indirection and nested-comprehension laundering.",
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
    "item": "G5 / FIX-18",
    "findings": [
      {
        "id": "G5-1",
        "severity": "should_fix",
        "title": "Keyword-only helper arguments lose receipt provenance",
        "location": "tests/receipt_provenance_analyzer.py:259",
        "scenario": "relay(*, value) returned value unannotated; relay(value=snapshot.receipts) followed by opaque[0] produced zero findings."
      },
      {
        "id": "G5-2",
        "severity": "should_fix",
        "title": "Nested comprehensions launder receipt collections",
        "location": "tests/receipt_provenance_analyzer.py:181",
        "scenario": "opaque = [item for batch in (snapshot.receipts,) for item in batch] followed by opaque[0] produced zero findings."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v tests.test_receipt_provenance_analyzer tests.test_calibration_exits.RefusalInventoryTests.test_calibration_tests_pass_receipt_provenance_gate",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 7 tests",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 7 tests[\\s\\S]*OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "In a git-cloned temporary copy under $TMPDIR, analyze bc01908:test_calibration_live_three_window.py, repeat after renaming business_rows/marker_removed, and analyze safe row-key/iteration/next/one/non-receipt-index operations.",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "{'delta': True, 'renamed': True, 'safe': True}"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\\{'delta': True, 'renamed': True, 'safe': True\\}"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "In a git-cloned temporary copy under $TMPDIR, run inline analyzer cases helper=keyword-only relay, tuple=tuple(snapshot.receipts), nested=two-generator comprehension; exit nonzero when any positional access is missed.",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "MISSED=helper,nested"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "MISSED=$"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "In a git-cloned temporary copy under $TMPDIR, replace analyze_sources in-memory with the legacy-equivalent blind result and execute the renamed and deepcopy analyzer self-tests.",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "LEGACY_EQUIVALENT_MUTATION failures=2 errors=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "LEGACY_EQUIVALENT_MUTATION failures=2 errors=0"
      }
    },
    {
      "id": "V5",
      "kind": "inspection",
      "cmd": "set -eu; reject test_calibration_tests_have_no_literal_positional_receipt_indexing at 4495609; require test_calibration_tests_pass_receipt_provenance_gate; inspect bc01908..4495609 replacement diff",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "legacy substring lint removed",
          "provenance gate present"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "test_calibration_tests_pass_receipt_provenance_gate"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git status --short --branch && git rev-parse HEAD && git rev-parse @{upstream} && git diff --check bc01908..4495609",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## impl/d117-ledger-recovery...origin/impl/d117-ledger-recovery",
          "4495609c7eca5efd06e886f85bd857d9f80c2f53",
          "4495609c7eca5efd06e886f85bd857d9f80c2f53"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "4495609c7eca5efd06e886f85bd857d9f80c2f53"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "This narrow G5 lens ran the focused analyzer and corpus gates, not the canonical repository suite.",
      "needs": "Runner/lead should retain the separate canonical-suite result from the parallel delta gate."
    }
  ]
}
```

## Findings

G5-1 — should_fix: `tests/receipt_provenance_analyzer.py:259-270` propagates only positional `call.args` into positional parameters. It ignores `call.keywords` and keyword-only parameters. The reproduced keyword-only helper returned a receipt collection unannotated, yet neither the helper return nor subsequent `opaque[0]` was flagged.

G5-2 — should_fix: `tests/receipt_provenance_analyzer.py:181-201` misclassifies the outer variable of a nested comprehension as a receipt row. Consequently, the inner iteration and resulting collection lose provenance. The reproduced nested comprehension’s `opaque[0]` was not flagged.

Positive controls passed: both exact delta-1 sites were detected; renaming and deepcopy did not evade; `tuple()` laundering was detected; safe row-key, iteration, `next`, `ReceiptCorpus.one`, and non-receipt indexing patterns were accepted. The old substring lint is gone, and its equivalent mutation fails both renamed/deepcopy self-tests.

## Residual risk

No additional collateral finding. The canonical suite was outside this focused lens.

Checks performed: 7 focused tests; exact delta-site and rename probes; three new evasion probes; safe-pattern controls; legacy-lint discrimination; old-lint removal inspection; diff integrity and clean-worktree checks.