```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Corrected the A292 harness errata and expanded A291 row coverage at the real reduce entry; the focused suite remains RED as requested.",
  "workspace": {
    "base_requested": "51522bee599aa7943b9893702ef83710b8ee8793",
    "base_mode": "exact",
    "head_start": "51522bee599aa7943b9893702ef83710b8ee8793",
    "head_end": "51522bee599aa7943b9893702ef83710b8ee8793",
    "upstream_end": "51522bee599aa7943b9893702ef83710b8ee8793",
    "branch": "test/2026-09-25-a292-reducer-harness"
  },
  "pathspec": ["tests/test_scored_reduce.py"],
  "unowned_dirty": [],
  "verdict": {
    "implementation": "implemented",
    "acceptance": "pending_verification"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_scored_reduce > /private/tmp/a292_red.out 2>&1",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": ["Ran 54 tests in 23.363s", "FAILED (errors=63)"]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(errors=63\\)"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "PYTHONPATH=. python3 /private/tmp/a292_oracle_liveness.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["cell-count cells", "cap-bound cells", "energy cells", "missing-live missing_live_window oracle-live"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "missing-live missing_live_window oracle-live"
      }
    },
    {
      "id": "V3",
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
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "The reducer module is absent. All 63 focused-suite errors were confirmed to be only ModuleNotFoundError for joulewise.scored_reduce.",
      "needs": "Implementation seat adds the reducer and reruns the focused suite."
    }
  ]
}
```

## Change

[tests/test_scored_reduce.py](/Users/edr/code/wt-152c9255-a292h/tests/test_scored_reduce.py:240) now asserts the exact **nine-key** capture-window schema. The CONSUMED constant witness patches `sr.CAP_BOUND_FRACTION` to **0.30** and checks that the 3/10 cell flips from true to false; the unpatched boundary cases remain. The A291 entry matrix now checks that each injected roster has the named independent-checker violation and is refused through `reduce`.

| A291 row ID | Test name |
|---|---|
| INV-01 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-02 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-03 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-04 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-05 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-07 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-08 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-51 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-10 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-11 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-12 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-13 | `test_retry_stage_on_items_and_cells` |
| INV-50 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-14 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-15 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-16 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-17 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-18 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-46 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-19 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-34 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-20 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-21 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-22 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-23 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-24 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-25 | `test_spread_four_vs_five_parents_by_terminal_degradation` |
| INV-49 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-26 | `test_spread_four_vs_five_parents_by_terminal_degradation`; `test_spread_four_vs_five_envelopes` |
| INV-27 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-45 | `test_partial_parent_position_and_null_lever`; `test_drift_equal_vs_above_max_gap` |
| INV-41 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-29 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-47 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-48 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-30 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-31 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-32 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-33/43 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-35 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-36 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-37 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-38 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-39 | `test_every_a291_provisional_R_witness_at_real_reduce` |
| INV-40 | `test_ast_first_statement_is_verifier` |
| INV-44 | `test_cap_bound_fraction_consumed_by_patch_on_sr`; `test_no_cap_literal_and_no_from_import` |
| INV-52 | `test_every_a291_provisional_R_witness_at_real_reduce` |

**Rows judged not applicable to a standalone reduce-entry witness:** INV-06 and INV-09 are registration-construction validations; `reduce` receives an already constructed, frozen `Registration`. INV-28 specifies a pack refusal and a requeue recorded value, with no R form. INV-40 is a source-structure obligation, covered by its AST witness.

## Verification notes

The focused run executed 54 tests and produced 63 errors. A check of the complete captured output found **only** `ModuleNotFoundError: No module named 'joulewise.scored_reduce'`. The independent oracle accepted a valid reduction, detected three independently mutated cell values, and distinguished a missing-live-window refusal. A verifier-only scratch probe also exercised the expanded matrix without adding a reducer module. No commit was made.