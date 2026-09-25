```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Added A292 witnesses and corrected the independent oracle; the 200-night differential passes, with four focused methods RED on the known reducer defects.",
  "workspace": {
    "base_requested": "8d06633e",
    "base_mode": "exact",
    "head_start": "8d06633ea6ea3591ac78cb8da400ea6ac26e109c",
    "head_end": "8d06633ea6ea3591ac78cb8da400ea6ac26e109c",
    "upstream_end": "8d06633ea6ea3591ac78cb8da400ea6ac26e109c",
    "branch": "feat/2026-09-25-a292-scored-reduce"
  },
  "pathspec": [
    "tests/test_scored_reduce.py",
    "tests/scored_reduce_checker.py"
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
      "cmd": "python3 -B /tmp/152c9255/a292-lens-astra/run_focused.py",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 61 tests in 59.864s",
          "FAILED (failures=3, errors=3)",
          "FOCUSED_53=FAIL"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=3, errors=3\\)"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B -m unittest tests.test_scored_reduce.ScoredReduceTests.test_differential_oracle_200_nights",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 2137.828s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "python3 -B - <<'PY'\nfrom copy import deepcopy\nfrom tests.test_scored_reduce import _night, _inputs\nfrom tests.scored_reduce_checker import check_reduction, _sha\nfrom joulewise.scored_reduce import reduce\ng, reg, roster, predictions = _night()\nrows, windows = _inputs(g, reg, roster)\naccepted = reduce(reg, roster, predictions, rows, windows)\nassert check_reduction(g, roster, predictions, rows, windows, accepted) == []\nfor mutation, expected in ((\"cell\", \"cells\"), (\"item\", \"items\")):\n    forged = deepcopy(accepted)\n    if mutation == \"cell\":\n        forged[\"cells\"][\"large:1\"][\"gross_j\"] += 1\n    else:\n        forged[\"items\"][0][\"malformed\"] = not forged[\"items\"][0][\"malformed\"]\n    forged[\"sha256\"] = _sha({k: v for k, v in forged.items() if k != \"sha256\"})\n    errors = check_reduction(g, roster, predictions, rows, windows, forged)\n    assert errors and errors[0][\"code\"] == expected, errors\n    print(f\"oracle_liveness_{mutation}={errors[0]['code']}\")\nmissing = windows[1:]\nassert check_reduction(g, roster, predictions, rows, missing, {\"refusal_code\": \"row_missing\", \"detail\": \"\"})[0][\"code\"] == \"refusal_mismatch\"\nprint(\"oracle_liveness_refusal=refusal_mismatch\")\nprint(\"ORACLE_LIVENESS=PASS\")\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "oracle_liveness_cell=cells",
          "oracle_liveness_item=items",
          "oracle_liveness_refusal=refusal_mismatch",
          "ORACLE_LIVENESS=PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "ORACLE_LIVENESS=PASS"
      }
    },
    {
      "id": "V4",
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
        "tail_regex": ""
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The instruction to refuse positive 10**1000 gross_j and anchor values conflicts with E2, which admits positive finite integers, and with the prescribed oracle numeric check.",
      "needs": "Rule whether positive 10**1000 values are accepted under E2 or refused under a new domain limit."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "Aggregate math.fsum overflow remains the separately registered, unruled follow-up; no aggregate-overflow test was added.",
      "needs": ""
    }
  ]
}
```

## Change

Added the requested domain, binding, answer, completeness, and spread witnesses. The oracle now uses the window’s declared index for digest binding, checks completeness in three ordered passes, and handles large integers without `math.isfinite` overflow. Only the two authorized test files changed; no commit was made.

## Verification notes

The 200-night differential and oracle liveness check pass. The focused run is RED in exactly four test methods:

- `test_window_binding_uses_declared_index_before_envelope_mismatch` and `test_window_envelope_mismatch`: the reducer binds against the placement index. Both cross-boundary subcases return the opposite refusal.
- `test_window_domain_zero_negative_nonfinite_bool_anchor`: negative `10**1000` gross and anchor values raise `OverflowError` instead of `window_domain`.
- `test_positive_zero_and_large_integer_anchor`: positive `10**1000` anchor raises `OverflowError` instead of being accepted under E2.

All other focused tests pass. The positive `10**1000` expectation remains **NEEDS_RULING**: E2 admits it, while this round’s instruction says to refuse it. I recommend following E2 for positive integers.