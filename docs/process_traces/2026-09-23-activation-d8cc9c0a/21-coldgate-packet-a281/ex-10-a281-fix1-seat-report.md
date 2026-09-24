```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Implemented X1–X14; 30 named tests pass and all 234 file-level operand-collapse mutants are killed.",
  "workspace": {
    "base_requested": "e63fb5418b8c8b28469478a101261019521dec94",
    "base_mode": "exact",
    "head_start": "e63fb5418b8c8b28469478a101261019521dec94",
    "head_end": "e63fb5418b8c8b28469478a101261019521dec94",
    "upstream_end": null,
    "branch": "feat/2026-09-23-headline-pure-modules"
  },
  "pathspec": [
    "joulewise/scored_packer.py",
    "joulewise/scored_reduce.py",
    "joulewise/energy_per_correct.py",
    "tests/test_scored_packer.py",
    "tests/test_scored_reduce.py",
    "tests/test_energy_per_correct.py"
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
      "cmd": "python3 -B -m unittest tests.test_scored_packer tests.test_scored_reduce tests.test_energy_per_correct",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 30 tests in 1.107s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 30 tests in .*s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B /tmp/a281_mutate_packer_complete.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["joulewise/scored_packer.py generated 86 killed 86 survived 0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "generated 86 killed 86 survived 0"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -B /tmp/a281_mutate_reducer_complete.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["joulewise/scored_reduce.py generated 34 killed 34 survived 0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "generated 34 killed 34 survived 0"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "python3 -B /tmp/a281_mutate_estimator_complete.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["joulewise/energy_per_correct.py generated 114 killed 114 survived 0"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "generated 114 killed 114 survived 0"
      }
    },
    {
      "id": "V5",
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
      "level": "nonblocking",
      "text": "X2's equality is implemented for the point estimate; the split interval widens because 08 requires one floor-plus-anchor bound per single window.",
      "needs": "Magistrate to verify this reading during final review."
    }
  ]
}
```

## Change

Only the six allowed files changed. No commit was made.

| Clause | Implementation | Named regression |
|---|---|---|
| X1 | [Pooled Holm decisions and L*](/Users/edr/code/wt-1d3796d5-pure/joulewise/energy_per_correct.py:202) | [test_x1_crossover_direction_and_merged_boundary](/Users/edr/code/wt-1d3796d5-pure/tests/test_energy_per_correct.py:143), [test_x14_crossover_merge_licensing_and_fallback](/Users/edr/code/wt-1d3796d5-pure/tests/test_energy_per_correct.py:283) |
| X2 | [Parent pairing and per-window bounds](/Users/edr/code/wt-1d3796d5-pure/joulewise/energy_per_correct.py:13) | [test_x2_requeue_reduce_pairing](/Users/edr/code/wt-1d3796d5-pure/tests/test_energy_per_correct.py:94) |
| X3 | [Terminal ceiling violation](/Users/edr/code/wt-1d3796d5-pure/joulewise/scored_packer.py:233) | [test_x3_x4_single_retry_terminal_and_worst_case_packing](/Users/edr/code/wt-1d3796d5-pure/tests/test_scored_packer.py:87) |
| X4 | [Worst-case packed, append-only singles](/Users/edr/code/wt-1d3796d5-pure/joulewise/scored_packer.py:217) | `test_x3_x4_single_retry_terminal_and_worst_case_packing` |
| X5 | [Measured-cell balance and idle slots](/Users/edr/code/wt-1d3796d5-pure/joulewise/scored_packer.py:59) | [test_x5_cell_balance_grid_and_idle_kind](/Users/edr/code/wt-1d3796d5-pure/tests/test_scored_packer.py:114) |
| X6 | [Estimability and four statuses](/Users/edr/code/wt-1d3796d5-pure/joulewise/energy_per_correct.py:202) | [test_x6_x7_family_roles_estimability](/Users/edr/code/wt-1d3796d5-pure/tests/test_energy_per_correct.py:171) |
| X7 | [Arm, family, role, and bound validation](/Users/edr/code/wt-1d3796d5-pure/joulewise/energy_per_correct.py:146) | `test_x6_x7_family_roles_estimability` |
| X8 | [Typed floor refusal](/Users/edr/code/wt-1d3796d5-pure/joulewise/energy_per_correct.py:80) | [test_x8_floor_gate](/Users/edr/code/wt-1d3796d5-pure/tests/test_energy_per_correct.py:127) |
| X9 | [Digest chain and bound inputs](/Users/edr/code/wt-1d3796d5-pure/joulewise/scored_packer.py:188) | [test_x9_x10_digest_bounds_and_registered_levels](/Users/edr/code/wt-1d3796d5-pure/tests/test_scored_packer.py:136) |
| X10 | [Registered-level refusal](/Users/edr/code/wt-1d3796d5-pure/joulewise/scored_packer.py:159) | `test_x9_x10_digest_bounds_and_registered_levels` |
| X11 | [Capped/outcome check and retry counts](/Users/edr/code/wt-1d3796d5-pure/joulewise/scored_reduce.py:50) | [test_x11_capped_correct_refused_and_retry_stage_counts](/Users/edr/code/wt-1d3796d5-pure/tests/test_scored_reduce.py:50) |
| X12 | [Holm stop and exact cutoff](/Users/edr/code/wt-1d3796d5-pure/joulewise/energy_per_correct.py:218) | [test_x12_holm_stop_and_exact_cutoff](/Users/edr/code/wt-1d3796d5-pure/tests/test_energy_per_correct.py:165) |
| X13 | [Even zero-token allocation](/Users/edr/code/wt-1d3796d5-pure/joulewise/energy_per_correct.py:60) | [test_x13_zero_token_allocation](/Users/edr/code/wt-1d3796d5-pure/tests/test_energy_per_correct.py:133) |
| X14 | Independent roster signatures and file-level gate | [packer signatures](/Users/edr/code/wt-1d3796d5-pure/tests/test_scored_packer.py:161), [reducer cases](/Users/edr/code/wt-1d3796d5-pure/tests/test_scored_reduce.py:60), [estimator cases](/Users/edr/code/wt-1d3796d5-pure/tests/test_energy_per_correct.py:193) |

For the F1 worked roster, the 11 grid positions are:

`1.7B, 8B, 1.7B, idle(1.7B), 8B, 8B, 1.7B, 8B, 1.7B, 8B, 1.7B`

Each model’s five measured blocks has mean index **5.2**; the level’s recorded gap is **0.0**.

The requested grid gaps are shown as **Level 1 / Level 2**, in slots:

| Items | Block size | Speed 1:5 | Speed 1:1.5 |
|---:|---:|---:|---:|
| 10 | 1 | 0.0 / 0.0 | 0.0 / 0.0 |
| 10 | 2 | 0.0 / 0.0 | 0.0 / 0.0 |
| 10 | 3 | refused | refused |
| 10 | 4 | refused | refused |
| 11 | 1 | 0.0 / 0.0 | 0.0 / 0.0 |
| 11 | 2 | 0.0 / 0.0 | 0.0 / 0.0 |
| 11 | 3 | refused | refused |
| 11 | 4 | refused | refused |
| 13 | 1 | 0.0 / 0.0 | 0.0 / 0.0 |
| 13 | 2 | 0.0 / 0.0 | 0.0 / 0.0 |
| 13 | 3 | 0.0 / 0.0 | 0.0 / 0.0 |
| 13 | 4 | refused | refused |
| 17 | 1 | 0.0 / 0.0 | 0.0 / 0.0 |
| 17 | 2 | 0.0 / 0.0 | 0.0 / 0.0 |
| 17 | 3 | 0.0 / 0.0 | 0.0 / 0.0 |
| 17 | 4 | 0.2 / 0.4 | 0.0 / 0.0 |

The worked reduction remains `(120 + 80) / 1 = 200 J/correct`. Five paired correct blocks at 100 J versus 50 J give `R = 2`; with 1 J floor and 1 J anchor per window, the seeded interval is **(1.5, 2.75)** and the two-sided p-value is **0.02**. The Holm regression checks stop-after-failure and equality at the first two cutoffs, **0.010** and **0.0125**.

## Verification notes

The mutation gate used a `git archive HEAD` scratch copy, overlaid the six current files, asserted that its unmutated named suite passed, then replaced each comparison or `min`/`max` expression with each operand in turn. Each mutant ran the same three named unittest modules.

| Module | Generated | Killed | Survived | Survivor disposition |
|---|---:|---:|---:|---|
| `scored_packer.py` | 86 | 86 | 0 | None |
| `scored_reduce.py` | 34 | 34 | 0 | None |
| `energy_per_correct.py` | 114 | 114 | 0 | None |

Final named acceptance: `Ran 30 tests in 1.107s`, `OK`. `git diff --check` also passed.

## Residual risk

### Open rulings

X2 says the split ratio should equal the unsplit result, while ruling 08 requires an added floor-plus-anchor bound for each single window. The implementation keeps the **point estimate equal** when gross joules sum to the parent and widens the split interval. The magistrate should confirm that interpretation.

### What the magistrate should double-check

The balance search is deterministic and meets the specified grid, but it is a search rather than a general proof of a 0.5-slot bound for every future roster. The downstream runner should also consume pooled decisions from `groups`, capture `idle_slot` envelopes, and enforce the registered retry sensitivity rule; those runner changes are outside this write scope.