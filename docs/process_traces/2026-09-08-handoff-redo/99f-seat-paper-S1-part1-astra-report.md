```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "blocked",
  "completion": "partial",
  "summary": "Independent proposal boundaries and retirement safeguards implemented; X1–X22 mapping requires the missing authoritative crosswalk.",
  "workspace": {
    "base_requested": null,
    "base_mode": null,
    "head_start": "e9318fdf5900270b234f6db7316d03c5b40d97dc",
    "head_end": "e9318fdf5900270b234f6db7316d03c5b40d97dc",
    "upstream_end": null,
    "branch": "feat/2026-09-08-paper-S1"
  },
  "pathspec": [
    "docs/contracts/paper_comparison_placements.md",
    "docs/contracts/paper_supply_custody.md",
    "docs/paper/results-fill-registry.md",
    "tests/test_paper_comparison_placements.py"
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
      "cmd": "python3 -B -m unittest tests.test_paper_comparison_placements",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 3 tests in 0.013s", "", "OK"]
      },
      "expected": {"exit_code": 0, "tail_regex": "Ran 3 tests.*\\n\\nOK"}
    },
    {
      "id": "V2",
      "kind": "inspection",
      "cmd": "git diff --check",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "NEEDS_RULING: The prompt references X1–X22 but supplies neither their definitions nor a source pointer. Repository searches did not locate that crosswalk.",
      "needs": "Supply the authoritative X1–X22 crosswalk text or readable source path."
    },
    {
      "id": "F2",
      "kind": "verification_gap",
      "level": "blocking",
      "text": "Tests cover retirement preservation and reactivation, deletion and duplication counterfactuals only. Full obligation and supplier table-agreement regressions remain unimplemented.",
      "needs": "Resume implementation after the crosswalk is supplied."
    }
  ]
}
```

## Change

Added explicit schematic/synthetic dispositions, unresolved empirical routes, and archive/availability boundaries. Preserved retirement history and the empty live custody census.

## Verification notes

Three focused tests pass. No repository-wide suite, measurement collection, or commit occurred.

## Residual risk

**NEEDS_RULING:** Which authoritative source defines X1–X22?

Options considered: infer IDs from protocol sections, or obtain the source crosswalk. Recommend obtaining the source to avoid inventing obligation semantics, as the delegated authority rules require.

Blocked work: complete placement rows, mirrored supplier bindings, and agreement counterfactuals.