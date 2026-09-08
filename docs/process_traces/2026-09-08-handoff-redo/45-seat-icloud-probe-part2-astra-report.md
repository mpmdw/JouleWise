```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Scope expansion completed; all 110 tests pass without skips, including complete golden replay with XD, F4, and AQ byte-identical to HEAD.",
  "workspace": {
    "base_requested": null,
    "base_mode": "informational",
    "head_start": "2e2f528a520466b99330a5c930e1b69a2b9f8227",
    "head_end": "2e2f528a520466b99330a5c930e1b69a2b9f8227",
    "upstream_end": null,
    "branch": "fix/2026-09-08-icloud-backup-probe"
  },
  "pathspec": [
    "scripts/paper_anchor_correction_quantified.py",
    "scripts/check_paper_replay_fence.py",
    "scripts/paper_excursion_decomposition.py",
    "tests/test_paper_round7_artifacts.py",
    "tests/test_paper_excursion_decomposition.py",
    "tests/test_paper_anchor_correction_quantified.py",
    "tests/test_check_paper_replay_fence.py",
    "docs/paper/results-fill-registry.md",
    "tests/test_paper_replay_fence.py"
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
      "cmd": "PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest -v tests.test_paper_replay_fence > /private/tmp/icloud-part2-resume-fence.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 10 tests in 26.523s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 10 tests in [0-9.]+s\\s+OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 R7F_CORPUS_ROOT=/Users/edr/code/JouleWise python3 -B -m unittest -v tests.test_paper_excursion_decomposition tests.test_paper_anchor_correction_quantified tests.test_check_paper_replay_fence tests.test_paper_round7_artifacts > /private/tmp/icloud-part2-resume-acceptance.log 2>&1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 100 tests in 618.312s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 100 tests in [0-9.]+s\\s+OK"
      }
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 -B /private/tmp/icloud-part2-final-inspection.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "HELPERS_VERBATIM_EQUAL; XS_AS_PINS_MATCH",
          "docs/paper/round7/excursion-decomposition.json HEAD_BYTES_EQUAL 33765",
          "docs/paper/figures/fig4_edge_excursions.svg HEAD_BYTES_EQUAL 10568",
          "docs/paper/round7/anchor-correction-quantified.json HEAD_BYTES_EQUAL 54280",
          "DIFF_CHECK_PASS"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "DIFF_CHECK_PASS"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "Historical deviation from the preceding turn: initial pre-fix locator tests attempted default iCloud directory checks despite the override. Subsequent counterfactuals mocked those checks. No such attempt was made during this resumed work.",
      "needs": ""
    }
  ]
}
```

## Change

All three scripts use a verbatim-identical helper with a 2-second daemon-thread discovery budget, the path-separated override, and zero candidates for unavailable roots. XS and RF preserve candidate order; AS preserves sorted discovery for each capture ID.

The helper remains duplicated to preserve individually pinned producer files and self-contained scratch replays. XS and AS source pins carry the dated correction note.

Every identified test module now establishes scratch overrides during imports and execution. The approved scope expansion is complete.

The complete golden replay passed without skips:

| Retained artifact | Bytes | Fresh output against HEAD |
|---|---:|---|
| XD | 33,765 | Byte-identical |
| F4 | 10,568 | Byte-identical |
| AQ — AS’s retained output | 54,280 | Byte-identical |

## Verification notes

The earlier guarded counterfactuals failed against both old consumers: `FAILED (failures=2)`, rc 1. The same override regressions passed after the cure: `OK`, rc 0. Tests also cover blocked checks/enumeration, partial-discovery errors, both search depths, hash verification, and absent-root equivalence.

Logs and exit-code records: [replay-fence log](/private/tmp/icloud-part2-resume-fence.log), [rc](/private/tmp/icloud-part2-resume-fence.rc); [four-module acceptance log](/private/tmp/icloud-part2-resume-acceptance.log), [rc](/private/tmp/icloud-part2-resume-acceptance.rc).

No repository-wide suite or commit was performed. Ready for lead review.

## Residual risk

The preceding turn’s unintended pre-fix iCloud directory checks remain a recorded execution deviation; they were not repeated during this resume.