```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "NEW-01 is cured: inverted exact JSON-integer intervals above 2^53 now fail closed, with a red-then-green regression.",
  "workspace": {
    "base_requested": "2ac94d7ce55eb2a4cd6aeb7cec01a72917e71d0e",
    "base_mode": "exact",
    "head_start": "2ac94d7ce55eb2a4cd6aeb7cec01a72917e71d0e",
    "head_end": "2ac94d7ce55eb2a4cd6aeb7cec01a72917e71d0e",
    "upstream_end": "2ac94d7ce55eb2a4cd6aeb7cec01a72917e71d0e",
    "branch": "feat/2026-09-04-transfer-result-renderer"
  },
  "pathspec": [
    "joulewise/results_fill_transfer.py",
    "tests/test_results_fill_transfer.py",
    "docs/process_traces/2026-09-04-transfer-renderer/05-sol-fix-round-2-report.md"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_results_fill_transfer",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 1 test in 0.028s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test in .*\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 13 tests in 3.112s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 13 tests in .*\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "git diff --check -- joulewise/results_fill_transfer.py tests/test_results_fill_transfer.py docs/process_traces/2026-09-04-transfer-renderer",
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
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "R3 remains fixture-only; the capture producer at d67ee56c remains unreviewed and no live value is issued.",
      "needs": "Keep producer acceptance as a separate gate."
    }
  ]
}
```

## Change

Round-1's only uncured item was distinct `NEW-01`; none of the prior defect
signatures repeated, so the mandatory ruling stop did not trigger. Interval
ordering now compares the already-validated JSON endpoints through exact
`Decimal` projections instead of binary floats. The regression recreates the
reported counterfactual (`lower=9007199254740993`,
`upper=9007199254740992`), freshly reissues every dependent maximum/witness
field and the content ID, and requires nine-site `STOP_FILL`.

Red, after adding the regression and before changing the validator:

```text
FAIL: test_transfer_result_contract_table
AssertionError: False is not true
Ran 1 test in 0.011s
FAILED (failures=1)
```

Green is recorded in V1. No fixture or registry contract change was needed:
the issued numbers and schema are unchanged, and the fix enforces the existing
requirement that the fitted interval's upper endpoint is not below its lower
endpoint.

## Verification notes

The prompt's preflight rule excluded the canonical discovery suite and all
producer/validator tests outside the renderer module and two registry modules.

## Residual risk

This remains fixture-only and does not accept or execute the unreviewed capture
producer at `d67ee56c`.
