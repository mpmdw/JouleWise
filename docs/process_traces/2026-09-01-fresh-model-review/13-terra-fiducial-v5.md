```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Implemented the fail-closed V2 generator and pre-data receipt; a real V2 plan awaits the G2-a record and prompt pin.",
  "workspace": {
    "base_requested": "main",
    "base_mode": "informational",
    "head_start": "cb9371aa634129afb2fd5dab43deebc69ec5233d",
    "head_end": "cb9371aa634129afb2fd5dab43deebc69ec5233d",
    "upstream_end": "cb9371aa634129afb2fd5dab43deebc69ec5233d",
    "branch": "feat/transfer-fiducial-01"
  },
  "pathspec": [
    "configs/diagnostics/transfer_fiducial_v2/generate_plan.py",
    "docs/contracts/transfer_fiducial.md",
    "joulewise/transfer_fiducial.py",
    "scripts/fit_transfer_fiducial.py",
    "tests/test_transfer_fiducial.py",
    "tests/test_transfer_fiducial_v2_plan.py",
    "tests/fixtures/transfer_fiducial_v2/synthetic-g2a-summary.json",
    "tests/fixtures/transfer_fiducial_v2/synthetic-selected-g2a-record.json"
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
      "cmd": "python3 -m unittest tests.test_transfer_fiducial tests.test_mlx_runtime tests.test_schemas tests.test_transfer_fiducial_v2_plan",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 94 tests",
          "OK (skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^OK( \\(skipped=1\\))?$"
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
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "The G2-a selection record contains only the rung and a summary digest; it contains no prompt text or token identifiers. The generator therefore requires the existing V5-style hash-bound prompt-pin file as a third input.",
      "needs": "Confirm that requiring the prompt pin is the intended permanent V2 interface."
    },
    {
      "id": "F2",
      "kind": "residual_risk",
      "level": "blocking",
      "text": "No authenticated G2-a record or matching real prompt pin is present, so no real plan.json or ten committed V2 configurations were generated.",
      "needs": "Supply the authenticated record and matching prompt pin, generate the committed set, then run --check."
    }
  ]
}
```

## Change

Added the Qwen3-small successor generator, including strict G2-a selection validation, V5-imported identity pins, a hash-bound prompt pin, ten-config generation, and byte-for-byte `--check`.

Added `--issue-receipt` to the fitter. Fitting now returns `inconclusive` with named reasons for missing or changed receipt inputs, changed source configurations, changed fitter or estimator files, changed calibration identity, calibration captured after a run begins, and plan constants that differ from the fitter’s actual rules.

Updated the operator procedure for `_v5`, retaining V1 unchanged.

## Verification notes

The selection record alone cannot bind the requested prompt. I disagree with treating it as sufficient input: the separate prompt-pin input is required to make the workload reproducible and fail closed.

## Residual risk

The real G2-a artifacts are still required before the committed V2 plan and configurations can exist.