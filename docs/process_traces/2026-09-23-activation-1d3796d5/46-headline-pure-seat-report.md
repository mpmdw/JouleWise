```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Implemented the six scoped pure-module and test files; the named acceptance suite passes.",
  "workspace": {
    "base_requested": "64d4c034",
    "base_mode": "exact",
    "head_start": "64d4c034a79693be005e812eeaff2ed52a385527",
    "head_end": "64d4c034a79693be005e812eeaff2ed52a385527",
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
        "tail": [
          "Ran 15 tests in 2.781s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 15 tests in .*s\\n\\nOK"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "An odd block-envelope count for both models requires an empty model slot to make the initial schedule palindromic.",
      "needs": "Confirm that the scored-night runner captures the empty slot as an envelope."
    },
    {
      "id": "F2",
      "kind": "lead_ruling",
      "level": "nonblocking",
      "text": "Overrun retries append after existing capture indices, so a revised roster need not retain the initial palindrome.",
      "needs": "Confirm that append-only overrun tails are the intended ordering exception."
    }
  ]
}
```

## Change

| Clause | Implementation and evidence |
|---|---|
| P1 | [Packer](/Users/edr/code/wt-1d3796d5-pure/joulewise/scored_packer.py:105) makes paired block slices, enforces capacity and five distinct envelopes per cell, applies Williams rows and a palindromic initial model schedule, then hashes canonical JSON. [Tests](/Users/edr/code/wt-1d3796d5-pure/tests/test_scored_packer.py:20) cover pairing, spread, ordering, refusal and capacity. |
| P2 | [Overrun requeue](/Users/edr/code/wt-1d3796d5-pure/joulewise/scored_packer.py:143) appends one whole-block retry, then single-problem envelopes; voided assignments remain recorded. [Test](/Users/edr/code/wt-1d3796d5-pure/tests/test_scored_packer.py:57). |
| P3 | [Reducer](/Users/edr/code/wt-1d3796d5-pure/joulewise/scored_reduce.py:30) sums gross block windows and reports counts, accuracy, tokens, descriptive J/token, J/correct and cap status. [Tests](/Users/edr/code/wt-1d3796d5-pure/tests/test_scored_reduce.py:12) show idle padding changes J/correct by exactly **0 J**, zero-correct is undefined, and cap-bound begins above 20%. |
| P4 | [Estimator](/Users/edr/code/wt-1d3796d5-pure/joulewise/energy_per_correct.py:48) resamples paired blocks within level and paired problems within blocks, then widens by the supplied per-block floor and anchor bounds. [Tests](/Users/edr/code/wt-1d3796d5-pure/tests/test_energy_per_correct.py:18) cover seed determinism, block variation and exact widening. |
| P5 | [Decision rule](/Users/edr/code/wt-1d3796d5-pure/joulewise/energy_per_correct.py:121) applies count-only sparse merges and Holm with family size fixed at five; only significant, directed results define a crossover. [Tests](/Users/edr/code/wt-1d3796d5-pure/tests/test_energy_per_correct.py:50). |
| P6 | The three named test modules pass. The [operand-collapse test](/Users/edr/code/wt-1d3796d5-pure/tests/test_scored_packer.py:82) mutates each packer comparison to each operand. |

**Worked example.** Ten problems at one level, block size 2, and 11 predicted seconds per problem produce five 22-second blocks per model under a 60-second capacity. The palindrome uses 11 envelope slots, including one empty slot. In the reducer fixture, 120 + 80 = **200 gross J** and one correct answer gives **200 J/correct**; changing offset, tail and idle fields changes it by 0 J.

For five correct answers per model, 8B uses 100 J and 1.7B uses 50 J: **R = 2**. With 99 bootstrap draws and floor and anchor bounds of 1 J each per block, the exact widened interval is **[1.5, 2.75]**; `p_above = 0.01` and `p_below = 1`.

| Level | Two-sided p | Holm cutoff | Decision |
|---|---:|---:|---|
| 1 | .001 | .0100 | 8B cheaper |
| 2 | .006 | .0125 | 8B cheaper |
| 3 | .011 | .0167 | 1.7B cheaper |
| 4 | .020 | .0250 | 1.7B cheaper |
| 5 | .040 | .0500 | 1.7B cheaper |

The worked table’s crossover is **Level 3**.

| Operand-collapse cuts | Generated | Killed |
|---|---:|---:|
| Comparison → left operand | 25 | 25 |
| Comparison → right operand | 25 | 25 |
| `min`/`max` calls in packer | 0 | Not applicable |

## Verification notes

The sole acceptance command and its result tail are in V1. No commit was made. All six changed paths are within `WRITE_SCOPE`.

## Residual risk

**Open rulings:** The magistrate should confirm whether an empty model slot is captured as a full envelope, and whether append-only overrun tails are exempt from the initial palindrome. The magistrate should also double-check the estimator’s within-block token allocation against the eventual AP-5M registration before claim use.