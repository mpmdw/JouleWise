```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented the ruled title, first-use cures, and transfer-note repair with regression coverage; all three mandated tests pass.",
  "workspace": {
    "base_requested": "2542d154",
    "base_mode": "exact",
    "head_start": "2542d154219a1d106d802b1f38cc2c9edaaa4a3c",
    "head_end": "2542d154219a1d106d802b1f38cc2c9edaaa4a3c",
    "upstream_end": "2542d154219a1d106d802b1f38cc2c9edaaa4a3c",
    "branch": "feat/2026-09-04-paper-k"
  },
  "pathspec": [
    "docs/paper/draft-v2-skeleton.md",
    "docs/paper/results-fill-registry.md",
    "tests/test_paper_first_use_ledger.py",
    "tests/test_paper_terms_lint.py",
    "docs/process_traces/2026-09-04-paper-k/03-sol-fix-round-1-report.md"
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
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "..........",
          "----------------------------------------------------------------------",
          "Ran 10 tests in 1.873s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 10 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "lint",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_terms_lint",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "....",
          "----------------------------------------------------------------------",
          "Ran 4 tests in 1.472s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 4 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_select_outcome_branches",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "...",
          "----------------------------------------------------------------------",
          "Ran 3 tests in 0.543s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 3 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V4",
      "kind": "inspection",
      "cmd": "rg -o '\\[FILL:' docs/paper/draft-v2-skeleton.md | wc -l; git show HEAD:docs/paper/draft-v2-skeleton.md | rg '^<!-- OUTCOME-BRANCH' | shasum -a 256; rg '^<!-- OUTCOME-BRANCH' docs/paper/draft-v2-skeleton.md | shasum -a 256; rg -c '^<!-- OUTCOME-BRANCH' docs/paper/draft-v2-skeleton.md; tail -n 1 docs/paper/draft-v2-skeleton.md",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "     131",
          "5a0d0e0374916eaa07dd7e5bb85032827a720842ed4b4011e693e41a90a05b42  -",
          "5a0d0e0374916eaa07dd7e5bb85032827a720842ed4b4011e693e41a90a05b42  -",
          "24",
          "a failure. Terms inventoried: 261; FAILS: 0."
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": " +131\\n([0-9a-f]{64})  -\\n\\1  -\\n24\\na failure\\. Terms inventoried: 261; FAILS: 0\\."
      }
    }
  ],
  "flags": []
}
```

## Change

| Finding | Line | Old | New |
|---|---:|---|---|
| R1 title | draft 17; registry 270–272 | “JouleWise — Measuring Interval-Overlap-Allocated Energy for Large-Language-Model (LLM) Inference Phases on Apple Silicon”; unnamed fixed title | “JouleWise: Timing Sensitivity of Phase-Energy Assignments on Apple Silicon”; registry repeats the exact fixed title |
| F1 registered timing domain | draft 29, 35, 41 | “registered timing domain” | Each Abstract outcome sentence now continues “—the set of edge movements fixed before collection” |
| F1 block-level energy allowances | draft 29 | “a shared sign for block-level energy allowances” | “a shared sign, meaning one direction applied to the nonnegative energy changes allowed in every group of four runs” |
| F1 A/B/B/A construction | draft 113 | Construction appeared only after the source table and later same-model-null use | “An A/B/B/A block is four runs in the order A, B, B, A.” now precedes both |
| F1 floor packs | draft 140–142 | “the floor packs set A = B” before the term's definition | “In the same-model null blocks, A and B are condition-slot labels set equal to each other” |
| F1 ledger | draft 1836, 1868, 1875 | Homes/dispositions described the pre-cure reading order | Rows now bind the moved floor-pack home and the exact registered-domain/shared-sign glosses |
| F2 transfer note | draft 1160–1163 | “BUILD AFTER CAMPAIGN AND TRANSFER FIDUCIAL” and “the headline remains conditional on it” | A campaign-only build note preserves the no-transfer limitation and contains no transfer gate |
| Regression coverage | tests 68–77; 159–224 | First-use and paper-K regression checks did not cover F1/F2 or the ruled title | Checks now bind all three Abstract glosses, the four-run and floor-pack construction, exact title, and retired transfer condition |

All cures are sentence-unit edits. Fill markers remain 131, the 24 outcome markers retain their baseline SHA-256, and the first-use footer remains “Terms inventoried: 261; FAILS: 0.”

## Verification notes

An intermediate first-use run caught the stale floor-pack ledger home after its first use moved from Section 1 to Section 3; the row was corrected before V1. An intermediate selector run caught a 253-word Refusal Abstract; two complete sentences were tightened by three words without changing stop semantics, and the final selector run passed at the 250-word cap.
