```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented the D-165 dominance core, replay and close-out contracts, hash-bound builder, CLI, strict validators, and acceptance tests.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "3935bf15b7e55fcf5b1e2e89bd9028ca8ab38181",
    "head_end": "3935bf15b7e55fcf5b1e2e89bd9028ca8ab38181",
    "upstream_end": "f68ca1efdea9fddbe34a008f812dac822ed9b2f6",
    "branch": "feat/d165-dominance-closeout-core"
  },
  "pathspec": [
    "configs/campaigns/d117_contrast_v5/generate_configs.py",
    "docs/contracts/d165_dominance_closeout.md",
    "joulewise/dominance_closeout.py",
    "joulewise/floor_extraction.py",
    "scripts/build_d165_dominance_closeout.py",
    "tests/test_d165_dominance_closeout.py"
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
      "cmd": "python3 -m unittest tests.test_d165_dominance_closeout tests.test_d117_contrast_v5_pack tests.test_detection_floor tests.test_floor_extraction",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 354 tests in 6.476s",
          "",
          "OK (skipped=1)"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 354 tests in .*\\n\\nOK \\(skipped=1\\)"
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
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "origin/main advanced by three documentation-only commits during implementation; none overlaps the authorized paths.",
      "needs": ""
    }
  ]
}
```

## Change

The D-165 predicate now has one production home. The generator imports the ordinary ratio, shared/local block split, and comparative shared-error replay; its frozen registration bytes remain identical. Extraction now calls the shared split and preserves its original outward-rounded total exactly.

The contract defines every sidecar and close-out field, including the stage-2 `build_d165_replay_record(...)` signature. Absolute shared-error ratio is always `not_applicable`; the close-out contains exactly eight ordinary slots and four comparative shared-error slots.

The builder uses the existing detection-floor point diagnostic instead of copying its maximum calculation. Validators reject closed-key violations, non-finite values, incorrect censuses, unauthenticated bounds, replay drift, zero denominators, and source-hash changes.

For the one-cell fixture test, fixture-only member and corpus diagnostics were removed. The seven registered raw block inputs and `block_id` were retained, shared/local splits were added, an authenticated calibration bracket was embedded and hashed, and synthetic independent records were added because the fixture contains only comparative replay evidence.

Narrow disagreement with the scout: the four-cell census belongs to close-out validation, not standalone sidecar validation. A one-cell diagnostic sidecar can validate on its own, while production close-out still requires exact agreement with all four floor cells.

The existing private window-domain helper remains reused unchanged. No mint, renderer, finalization, frozen-paper, retained-corpus, or measurement path was touched.

## Verification notes

The single skip is the existing targeted-suite skip. Verification ran at the local implementation head; concurrent upstream changes were confined to process-trace documentation.