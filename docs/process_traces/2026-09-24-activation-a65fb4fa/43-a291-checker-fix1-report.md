```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "clean",
  "completion": "complete",
  "summary": "Corrected planned and executed roster arithmetic and killed all eight surviving checker mutations.",
  "workspace": {
    "base_requested": "b8962fd0",
    "base_mode": "exact",
    "head_start": "b8962fd0d35ec83d382984354674d63300cf1c12",
    "head_end": "b8962fd0d35ec83d382984354674d63300cf1c12",
    "upstream_end": null,
    "branch": "fix/2026-09-24-a291-checker-r1"
  },
  "pathspec": [
    "tests/scored_roster_checker.py",
    "tests/test_scored_roster_checker.py"
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
      "cmd": "python3 -B -m unittest tests.test_scored_roster_checker",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 22 tests in 3.381s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 22 tests in .*s\\s+OK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -B /tmp/a291-checker-mutations.py",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["ALL 8 MUTATIONS KILLED; temp copy: /tmp/a291-checker-mutations-cmis3y1o"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "ALL 8 MUTATIONS KILLED"
      }
    },
    {
      "id": "V3",
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

- **C1:** [_derived](/Users/edr/code/wt-a65fb4fa-a291chk/tests/scored_roster_checker.py:247) and the fixture’s [refresh_derived](/Users/edr/code/wt-a65fb4fa-a291chk/tests/test_scored_roster_checker.py:139) now position partly terminal parents from their live items while keeping the nonterminal count separate for spread and the null rule. `test_refuter_R2_four_envelopes` ([line 730](/Users/edr/code/wt-a65fb4fa-a291chk/tests/test_scored_roster_checker.py:730)) asserts `|(56 + 1 + 2 + 3 + 4)/5 − (5 + 6 + 7 + 8 + 9)/5| = 6.2`.
- **C2:** [check_executed](/Users/edr/code/wt-a65fb4fa-a291chk/tests/scored_roster_checker.py:787) selects the placement live in its own envelope. `test_executed_uses_only_live_reschedule_and_advance_attempts` ([line 615](/Users/edr/code/wt-a65fb4fa-a291chk/tests/test_scored_roster_checker.py:615)) and `test_executed_single_advance_uses_retry_attempt` ([line 654](/Users/edr/code/wt-a65fb4fa-a291chk/tests/test_scored_roster_checker.py:654)) cover rescheduling, whole block advance, single retry, and ignored voided keys.
- **C3:** The executed lever positions a parent with any counted window; spread still requires every item counted. `test_executed_partly_counted_parent_position` ([line 640](/Users/edr/code/wt-a65fb4fa-a291chk/tests/test_scored_roster_checker.py:640)) asserts the partly counted parent’s 5.4 lever.
- **C5:** The [CONTRACT GAPS list](/Users/edr/code/wt-a65fb4fa-a291chk/tests/test_scored_roster_checker.py:3) is unchanged. Magistrate-confirmed gaps 4 and 5 remain.
- **C6:** `test_base_and_row_inventory` ([line 469](/Users/edr/code/wt-a65fb4fa-a291chk/tests/test_scored_roster_checker.py:469)) still compares the parsed 02d IDs with `ROWS ∪ NOT_CHECKABLE`. An independent recount found 50 contract IDs = 46 rows + 4 not checkable, with no missing, extra, or overlapping IDs.

**C4 mutation rerun:** `python3 -B /tmp/a291-checker-mutations.py` copied the current checker and tests into a separate `/tmp` package for each mutation. Every named test failed with one assertion failure; the harness exited 0 only after all eight were killed.

| Mutation | Killing test | Rerun |
|---|---|---|
| M1, remove INV-35(a) | `test_INV_35a_reschedule_without_culprit_code` ([line 769](/Users/edr/code/wt-a65fb4fa-a291chk/tests/test_scored_roster_checker.py:769)) | exit 1, assertion failure |
| M2, remove INV-35(c) | `test_INV_35c_excess_reschedules_code` ([line 781](/Users/edr/code/wt-a65fb4fa-a291chk/tests/test_scored_roster_checker.py:781)) | exit 1, assertion failure |
| M7, allow a whole block envelope | `test_eligibility_excludes_whole_block_and_same_cell_parent` ([line 791](/Users/edr/code/wt-a65fb4fa-a291chk/tests/test_scored_roster_checker.py:791)) | exit 1, assertion failure |
| M8, remove M8-by-parent | Same eligibility test | exit 1, assertion failure |
| M9, change `>` to `>=` | `test_culprit_strict_elapsed_boundary` ([line 803](/Users/edr/code/wt-a65fb4fa-a291chk/tests/test_scored_roster_checker.py:803)) | exit 1, assertion failure |
| M10, remove five-envelope clause | `test_planned_shortfall_requires_five_distinct_envelopes` ([line 809](/Users/edr/code/wt-a65fb4fa-a291chk/tests/test_scored_roster_checker.py:809)) | exit 1, assertion failure |
| M16, replace planned null with zero | `test_planned_lever_null_with_zero_nonterminal_parents` ([line 820](/Users/edr/code/wt-a65fb4fa-a291chk/tests/test_scored_roster_checker.py:820)) | exit 1, assertion failure |
| M17, remove registered-descendant clause | `test_registered_descendant_requires_claim_ready` ([line 832](/Users/edr/code/wt-a65fb4fa-a291chk/tests/test_scored_roster_checker.py:832)) | exit 1, assertion failure |

## Verification notes

Final acceptance ran after the edits:

```text
$ python3 -B -m unittest tests.test_scored_roster_checker
Ran 22 tests in 3.381s

OK
```

`git diff --check` passed. `git status --porcelain` lists only the two `WRITE_SCOPE` paths. No commit was made.

## Residual risk

The magistrate should double-check the packer stress comparison for partly terminal and partly counted parents, and confirm that its `captured_window_keys` input is a set of `(block_id, attempt)` tuples. Gaps 4 and 5 retain the magistrate’s chosen interpretations.