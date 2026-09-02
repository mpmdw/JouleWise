```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Cured F1–F7 with authenticated V2 inputs, byte-bound exclusive receipts, preserved V1 behavior, executable operator documentation, and attack-shaped tests.",
  "workspace": {
    "base_requested": "285aaefeeaac5373540cd7f9756c734fd6c703e7",
    "base_mode": "exact",
    "head_start": "285aaefeeaac5373540cd7f9756c734fd6c703e7",
    "head_end": "285aaefeeaac5373540cd7f9756c734fd6c703e7",
    "upstream_end": "285aaefeeaac5373540cd7f9756c734fd6c703e7",
    "branch": "feat/transfer-fiducial-01"
  },
  "pathspec": [
    "configs/diagnostics/transfer_fiducial_v2/generate_plan.py",
    "docs/contracts/transfer_fiducial.md",
    "joulewise/transfer_fiducial.py",
    "scripts/fit_transfer_fiducial.py",
    "tests/test_transfer_fiducial.py",
    "tests/test_transfer_fiducial_v2_plan.py"
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
      "cmd": "python3 -m unittest tests.test_transfer_fiducial tests.test_transfer_fiducial_v2_plan tests.test_mlx_runtime tests.test_schemas",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 106 tests in 345.512s",
          "",
          "OK (skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 106 tests in .*s\\n\\nOK \\(skipped=1\\)"
      }
    },
    {
      "id": "V2",
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
  "flags": []
}
```

## Change

| Finding | Cure location | Regression test |
|---|---|---|
| F1 | [generate_plan.py:99](/Users/edr/code/JouleWise-wt-fiducial/configs/diagnostics/transfer_fiducial_v2/generate_plan.py:99) authenticates exact summary bytes and refuses digest mismatch. | `test_selection_summary_exact_bytes_are_authenticated` |
| F2 | [generate_plan.py:167](/Users/edr/code/JouleWise-wt-fiducial/configs/diagnostics/transfer_fiducial_v2/generate_plan.py:167) uses runtime tokenization; authority, path, method, and identifier checks follow at line 228. | `test_generates_ten_configs_after_runtime_retokenization`, `test_synthetic_self_hashed_prompt_pin_is_refused`, and both prompt-pin mismatch tests |
| F3 | [transfer_fiducial.py:883](/Users/edr/code/JouleWise-wt-fiducial/joulewise/transfer_fiducial.py:883) hashes raw config bytes; [transfer_fiducial.py:985](/Users/edr/code/JouleWise-wt-fiducial/joulewise/transfer_fiducial.py:985) checks canonical receipt bytes, sidecar, both fitter sources, estimator, plan, and calibration. | `test_receipt_binds_exact_config_and_receipt_bytes`, `test_receipt_binds_actual_wrapper_core_and_estimator_bytes`, `test_receipt_binds_plan_calibration_and_rule_bytes` |
| F4 | [fit_transfer_fiducial.py:25](/Users/edr/code/JouleWise-wt-fiducial/scripts/fit_transfer_fiducial.py:25) publishes with `O_CREAT\|O_EXCL` and preserves the named duplicate refusal. | `test_duplicate_and_concurrent_receipt_issuance_refuse` |
| F5 | [transfer_fiducial.py:1185](/Users/edr/code/JouleWise-wt-fiducial/joulewise/transfer_fiducial.py:1185) dispatches V2-only behavior by schema/kind; V1 never evaluates receipts, dwell, or calibration order. | Six original `TransferFiducialTests` retained unchanged, plus `test_v1_invalid_planned_config_still_raises` and `test_v2_requires_receipt_while_v1_remains_receipt_free` |
| F6 | [transfer_fiducial.md:3](/Users/edr/code/JouleWise-wt-fiducial/docs/contracts/transfer_fiducial.md:3) carries the D-167 gate; [transfer_fiducial.md:231](/Users/edr/code/JouleWise-wt-fiducial/docs/contracts/transfer_fiducial.md:231) builds the producer, readiness, calibration-selection, verification, backup, and clock path. | `test_operator_contract_names_ruled_producers_and_calibration_selector` |
| F7 | [test_transfer_fiducial_v2_plan.py:185](/Users/edr/code/JouleWise-wt-fiducial/tests/test_transfer_fiducial_v2_plan.py:185) and [test_transfer_fiducial.py:534](/Users/edr/code/JouleWise-wt-fiducial/tests/test_transfer_fiducial.py:534) contain the requested CLI refusals and byte-mutation matrix. | All tests named above, including collect-at-4096, pin mismatch, dwell, temporal order, duplicate issuance, and invalid V2 config |

## Verification notes

For the required V1 audit, I inspected `git diff HEAD~ -- joulewise/transfer_fiducial.py` and compared syntax trees—the parsed structural form of the code. All 20 original functions were unchanged except the deliberately dispatched `build_capture`.

I then executed both the `HEAD~` and current V1 builders against the same fixture. Their capture objects were exactly equal, and an invalid planned configuration raised the same exception type and message. All six original V1 test methods also matched their `HEAD~` syntax trees unchanged.