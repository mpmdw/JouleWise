```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "clean",
  "completion": "partial",
  "summary": "No code findings; all local suites and three requested mutants bite, but PR-body verification was blocked by GitHub API connectivity.",
  "workspace": {
    "base_requested": "8207364c",
    "base_mode": "exact",
    "head_start": "8207364c8e6c8774b4885fe39959ad85f52917b4",
    "head_end": "8207364c8e6c8774b4885fe39959ad85f52917b4",
    "upstream_end": null,
    "branch": "(detached at 8207364c)"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "label": "CLEAN",
    "findings": [],
    "same_signature": "no"
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_check_gate_ledger tests.test_docs_freshness tests.test_gen_state; printf 'EXPORTED_TMPDIR_SUITE_EXIT=%s\\n' \"$?\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 78 tests in 7.935s",
          "OK",
          "EXPORTED_TMPDIR_SUITE_EXIT=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 78 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "suite",
      "cmd": "env -u TMPDIR PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_check_gate_ledger tests.test_docs_freshness tests.test_gen_state; printf 'UNSET_TMPDIR_SUITE_EXIT=%s\\n' \"$?\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 78 tests in 7.933s",
          "OK",
          "UNSET_TMPDIR_SUITE_EXIT=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 78 tests.*OK"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_check_gate_ledger",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 31 tests in 5.080s",
          "FAILED (failures=2)",
          "DROP_COLON_HASH_MODULE_EXIT=1"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=2\\)"
      }
    },
    {
      "id": "V4",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_check_gate_ledger",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 31 tests in 5.088s",
          "FAILED (failures=2)",
          "DROP_ABSOLUTE_GUARD_MODULE_EXIT=1"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=2\\)"
      }
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_check_gate_ledger",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "Ran 31 tests in 5.083s",
          "FAILED (failures=1)",
          "DROP_URL_GUARD_MODULE_EXIT=1"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=1\\)"
      }
    },
    {
      "id": "V6",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_gate_ledger.py --help >/dev/null",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "HELP_EXIT=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "HELP_EXIT=0"
      }
    },
    {
      "id": "V7",
      "kind": "smoke",
      "cmd": "gh pr view 275 --json body -q .body > \"$TMPDIR/body.md\"; python3 scripts/check_gate_ledger.py --body-file \"$TMPDIR/body.md\" --head-sha \"$(git rev-parse HEAD)\" --repo-root .",
      "cwd": ".",
      "observed": {
        "result": "not_run",
        "exit_code": 1,
        "tail": [
          "error connecting to api.github.com",
          "GH_BODY_EXIT=1",
          "gate-ledger: no '## Gate ledger (D-118 / D-121)' section in the PR body",
          "PR_BODY_CHECK_EXIT=1"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "gate-ledger: item 9: NOT-RUN[\\s\\S]*item 12: NOT-RUN"
      }
    },
    {
      "id": "V8",
      "kind": "inspection",
      "cmd": "git diff --exit-code; printf 'FINAL_DIFF_EXIT=%s\\n' \"$?\"; git status --porcelain; printf 'FINAL_STATUS_EXIT=%s\\n' \"$?\"",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "FINAL_DIFF_EXIT=0",
          "FINAL_STATUS_EXIT=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "FINAL_DIFF_EXIT=0[\\s\\S]*FINAL_STATUS_EXIT=0"
      }
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "gh pr view 275 could not reach api.github.com; the checker ran against an empty body, so the actual PR body and expected NOT-RUN rows 9–12 remain unverified.",
      "needs": "Rerun the exact PR-body fetch and checker when GitHub API connectivity is available."
    }
  ]
}
```

## Findings

### BLOCKER

None.

### SHOULD-FIX

None. No inert refusal probe remains; therefore no Rule-11 trigger.

### NIT

None.

## Contract

- `git ls-files | grep '[:#]'` produced no paths. Current legitimate repo-relative targets therefore contain neither character.
- Commit targets are constrained to 7–40 hexadecimal characters; current HEAD is `8207364c8e6c8774b4885fe39959ad85f52917b4`. Item 12 uses the same hexadecimal SHA/prefix form. The new guard cannot false-positive on these.
- `https://example.invalid/evidence.txt` now produces:  
  `gate-ledger: item 1: :N line suffix or #anchor is not a path: https://example.invalid/evidence.txt`
- No test asserts the former URL “neither a commit nor a path” message.
- `_valid_path` at `scripts/check_gate_ledger.py:113-120` remains a verbatim copy of `_check_pointer`’s path predicate and existence check at `scripts/gen_state.py:131-140`. The new syntax guard is outside `_valid_path`, before existence checking.

Mutant audit: “yes” means the named mutant was detected; “no” would mean an inert probe. Every probe is yes.

| Test | Mutant detected? |
|---|---|
| `test_missing_key_is_refused` | yes |
| `test_duplicate_key_is_refused` | yes |
| `test_empty_evidence_is_refused` | yes |
| `test_not_run_is_refused` | yes |
| `test_unresolvable_path_is_refused` | yes |
| `test_line_suffix_is_refused_as_a_path` | yes |
| `test_escaping_path_is_refused` | yes |
| `test_hex_string_that_is_neither_commit_nor_path_is_refused` | yes |
| `test_unescaped_pipe_inside_backticked_gate_item_is_named_malformed` | yes |
| `test_extra_cell_in_numbered_row_is_named_malformed` | yes |
| `test_missing_cell_in_numbered_row_is_named_malformed` | yes |
| `test_code_spanned_evidence_is_refused_as_not_plain_text` | yes |
| `test_numbered_row_after_blank_is_outside_ledger_table` | yes |
| `test_fenced_ledger_before_real_section_fails_closed` | yes |
| `test_unrecognised_ledger_row_is_named` | yes |
| `test_heading_drift_has_one_named_refusal` | yes |
| `test_lowercase_run_is_refused_as_not_uppercase` | yes |
| `test_indented_summary_terminates_the_ledger_section` | yes |
| `test_valid_path_matches_gen_state_check_pointer` | yes |
| `test_unstructured_evidence_is_refused_with_one_message` | yes |
| `test_item_twelve_path_is_refused_even_when_it_exists` | yes |
| `test_item_twelve_sha_must_match_head` | yes |
| `test_missing_repo_root_is_an_input_error_without_traceback` | yes |
| `test_shipped_template_is_refused_until_filled` | yes |
| `test_acceptance_command_aliases_refuse_the_template` | yes |

## Same-signature

No new finding has the “regression that does not bite” signature. The prior Sol 233 SF2 class is cured: the absolute-path and URL fixtures now exist at their join-under-root spellings, and dropping either syntax guard fails the parity test. Dropping the new `:`/`#` guard fails both literal filename subtests.

## Executed evidence

Exported `TMPDIR`:

```text
Ran 78 tests in 7.935s

OK
EXPORTED_TMPDIR_SUITE_EXIT=0
```

Unset `TMPDIR`:

```text
Ran 78 tests in 7.933s

OK
UNSET_TMPDIR_SUITE_EXIT=0
```

Mutants, each restored afterward:

```text
drop :/# refusal:
Ran 31 tests in 5.080s
FAILED (failures=2)
DROP_COLON_HASH_MODULE_EXIT=1

drop path.startswith("/"):
Ran 31 tests in 5.088s
FAILED (failures=2)
DROP_ABSOLUTE_GUARD_MODULE_EXIT=1

drop "://":
Ran 31 tests in 5.083s
FAILED (failures=1)
DROP_URL_GUARD_MODULE_EXIT=1
```

CLI and PR-body check:

```text
HELP_EXIT=0
error connecting to api.github.com
GH_BODY_EXIT=1
gate-ledger: no '## Gate ledger (D-118 / D-121)' section in the PR body
PR_BODY_CHECK_EXIT=1
```

Restoration:

```text
FINAL_DIFF_EXIT=0
FINAL_STATUS_EXIT=0
```

`git status --porcelain` is empty.