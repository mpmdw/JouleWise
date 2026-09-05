```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "All three refuter blockers are cured, the reviewed XS producer pin is current, and the complete touched module passes its retained-corpus replay.",
  "workspace": {
    "base_requested": "89877419e1fe3703632cebc50f0296c71488e574",
    "base_mode": "exact",
    "head_start": "89877419e1fe3703632cebc50f0296c71488e574",
    "head_end": "89877419e1fe3703632cebc50f0296c71488e574",
    "upstream_end": "36e7d539c795cf8a60f2bace8d640ff81499c336",
    "branch": "feat/2026-09-04-fan-R7F-EXIT3-SEMANTICS-01"
  },
  "pathspec": [
    "docs/paper/results-fill-registry.md",
    "docs/process_traces/2026-09-04-fanout/R7F-EXIT3-SEMANTICS-01/04-sol-fix-round-1-resume-report.md",
    "scripts/check_paper_round7_artifacts.py",
    "tests/test_paper_round7_artifacts.py"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 -m unittest -q tests.test_paper_round7_artifacts",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "----------------------------------------------------------------------",
          "Ran 51 tests in 624.691s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 51 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 TMPDIR=/private/tmp python3 scripts/check_paper_round7_artifacts.py --literals-only",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "R7F PLACED 0/16",
          "R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "R7F LITERALS-ONLY COMPARED 181 / MISMATCHES 0"
      }
    },
    {
      "id": "V3",
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
        "tail_regex": "^$"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "git diff --name-only; git status --short --branch",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          " M docs/paper/results-fill-registry.md",
          " M scripts/check_paper_round7_artifacts.py",
          " M tests/test_paper_round7_artifacts.py",
          "?? docs/process_traces/2026-09-04-fanout/R7F-EXIT3-SEMANTICS-01/04-sol-fix-round-1-resume-report.md"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "04-sol-fix-round-1-resume-report\\.md$"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "At resumed HEAD 89877419, the checker and test cures recorded by committed report 03 were still working-tree modifications despite the handoff saying prior edits were committed; they were preserved and verified as mission-owned carryover.",
      "needs": "Include the three modified implementation/registry files and this report in the lead's landing diff review."
    }
  ]
}
```

## Change

Finding-to-cure map:

| Finding | Cure | File:line |
| --- | --- | --- |
| B1 — stale tracked XS identity | Re-pinned XS to the reviewed producer digest `12d0293b2615eaeb872aa5885cad1ac57b853dc975fb5f376a5ce36ef6000688` and recorded that it supersedes the prior `8733ff03...` / `49b258d2` provenance. No value, status, or census count changed. | `docs/paper/results-fill-registry.md:739` |
| B2 — help-table regression was self-referential | The disposition row now owns a clause without a duplicated numeral; help renders `row.exit_code`, while the regression independently pins all codes, tokens, and clauses. The refuter's `2 when` → `7 when` counterfactual therefore has no production literal to mutate and changing the rendered code fails the independent expectation. | `scripts/check_paper_round7_artifacts.py:180`, `scripts/check_paper_round7_artifacts.py:1033`, `tests/test_paper_round7_artifacts.py:870` |
| B3a — wrong raw digest lacked the named regression | The existing-raw/wrong-digest input reaches `ArtifactIntegrityMismatch`; the new direct producer-and-driver regression requires exit 2 and mismatch output. | `scripts/paper_excursion_decomposition.py:140`, `scripts/paper_excursion_decomposition.py:817`, `tests/test_paper_round7_artifacts.py:753` |
| B3b — absent events input lacked the named regression | The absent `events.jsonl` input reaches `ArtifactsUnavailable`; the new direct producer-and-driver regression requires exit 3 and the exact incomplete-replay terminal record. | `scripts/paper_excursion_decomposition.py:178`, `scripts/paper_excursion_decomposition.py:814`, `tests/test_paper_round7_artifacts.py:817` |

No magistrate-owned state document changed, and no state-row text is required for these cures.

## Verification notes

The preflight restriction was honored: only the touched test module was run, not the repository-wide suite. Its corpus-gated replay executed rather than skipping and passed after approximately ten minutes. The tracked literals-only checker also passed with zero mismatches.
