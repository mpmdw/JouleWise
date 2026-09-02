```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "The F-9 repair bites, but two path-policy tests remain non-discriminating and the trace overstates the original landing report.",
  "workspace": {
    "base_requested": "d14a818da9f1d163c889812e24a4639561b0e9dc",
    "base_mode": "exact",
    "head_start": "d14a818da9f1d163c889812e24a4639561b0e9dc",
    "head_end": "d14a818da9f1d163c889812e24a4639561b0e9dc",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "verdict": "SHOULD-FIX 3",
    "findings": [
      {
        "id": "SF1",
        "severity": "should_fix",
        "title": "The no-:N/no-#anchor contract is not enforced when such a literal file exists",
        "file": ".github/pull_request_template.md:3; scripts/check_gate_ledger.py:113; tests/test_check_gate_ledger.py:102",
        "counterfactual": "Create committed-path candidates named evidence.txt:12 or evidence.txt#anchor; both syntactically forbidden forms pass _valid_path because only existence is checked.",
        "observed": "Both complete ledgers exited 0 with gate-ledger: 12/12 RUN."
      },
      {
        "id": "SF2",
        "severity": "should_fix",
        "title": "Absolute-path and URL parity probes survive deletion of their syntax guards",
        "file": "scripts/check_gate_ledger.py:117; tests/test_check_gate_ledger.py:108; tests/test_check_gate_ledger.py:282",
        "counterfactual": "Delete path.startswith('/') or delete '://' in path; the supplied nonexistent probes still fail at os.path.isfile, so the tests remain green.",
        "observed": "Absolute-guard mutant: Ran 2 tests, OK, exit 0. URL-guard mutant: Ran 1 test, OK, exit 0."
      },
      {
        "id": "SF3",
        "severity": "should_fix",
        "title": "The landing trace outcome is not supported by its cited seat report",
        "file": "docs/process_traces/2026-09-02-t26-item2/MAGISTRATE-NOTES.md:12; docs/process_traces/2026-09-02-t26-item2/02-terra-195-landing-report.md:5",
        "counterfactual": "Following the row's 01/02 citation should produce a final landing report covering the advisory workflow.",
        "observed": "The row says advisory workflow landed, while report 02 is status blocked, completion partial, says the CI job awaits scope, and states NOT DONE at line 147."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_check_gate_ledger tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 37 tests in 5.096s",
          "OK",
          "FINAL_SUITE_EXIT=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 37 tests in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_check_gate_ledger.CheckGateLedgerTests.test_indented_summary_terminates_the_ledger_section",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 1,
        "tail": [
          "AssertionError: 1 != 0 : gate-ledger: item 4: ledger row outside the ledger table",
          "FAILED (failures=1)",
          "NUMBERED_MUTANT_EXIT=1"
        ]
      },
      "expected": {
        "exit_code": 1,
        "tail_regex": "FAILED \\(failures=1\\)"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_check_gate_ledger.CheckGateLedgerTests.test_indented_summary_terminates_the_ledger_section",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 1 test in 0.212s",
          "OK",
          "BOLD_MUTANT_EXIT=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 1 test in [0-9.]+s\\n\\nOK"
      }
    },
    {
      "id": "V4",
      "kind": "lint",
      "cmd": "git diff --check 5ed6f1e9 55bf9f73; git diff --check 55bf9f73 d14a818d",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "FINAL_DIFF_5ed6_55bf_EXIT=0",
          "FINAL_DIFF_55bf_d14a_EXIT=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "FINAL_DIFF_55bf_d14a_EXIT=0"
      }
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_gate_ledger.py --help >/dev/null",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "FINAL_HELP_EXIT=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "FINAL_HELP_EXIT=0"
      }
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git status --porcelain",
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
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "No live GitHub pull_request workflow was executed; review was source-, fixture-, and mutation-based.",
      "needs": ""
    }
  ]
}
```

## Findings

### SHOULD-FIX

SF1 — The documented no-`:N`/no-`#anchor` policy is not enforced.

The template forbids these forms at `.github/pull_request_template.md:3`, but `_valid_path` at `scripts/check_gate_ledger.py:113-120` only applies the copied path predicates and then tests literal file existence. The regression at `tests/test_check_gate_ledger.py:102-106` omits the suffixed file, so it refuses for nonexistence rather than syntax.

Observed:

```text
evidence.txt:12: rc=0 stdout='gate-ledger: 12/12 RUN'
evidence.txt#anchor: rc=0 stdout='gate-ledger: 12/12 RUN'
SUFFIX_EXISTING_PROBE_EXIT=0
```

SF2 — Two `_valid_path` parity probes remain non-biting.

At `tests/test_check_gate_ledger.py:282-314`, deleting either the absolute-path guard or URL guard still leaves the corresponding fixture nonexistent after joining beneath the test repository. The expected `False` therefore survives for the wrong reason. The `test_escaping_path_is_refused` absolute subcase has the same issue; its `..` and `~` subcases do bite because real targets are created.

Observed:

```text
Ran 2 tests in 0.525s
OK
ABSOLUTE_GUARD_MUTANT_EXIT=0

Ran 1 test in 0.068s
OK
URL_GUARD_MUTANT_EXIT=0
```

SF3 — `MAGISTRATE-NOTES.md:12` overstates what files 01/02 record.

The row reports “template + checker + tests + advisory workflow,” and commit `b36d6c2d` does contain all of those. However, the cited terra-195 report says `status: blocked`, `completion: partial`, “CI job awaits a trigger/scope ruling,” and at line 147 explicitly says the workflow is “NOT DONE.” A resumed/final terra-195 report is absent, so the committed implementation is true but the cited trace evidence is incomplete.

No SHA or seat-number mismatch was found. Commits `1529b09a`, `2983cdd4`, `5ed6f1e9`, and `55bf9f73` all resolve. Files 01–17 cited by the ledger exist. The archived 223 and 227 files are byte-identical to their scratchpad originals. Luna 215’s `CLEAN`/`NEW` and luna 227’s `BLOCKER 1` verdicts are accurately present in their seat files; the delta-3 table row records the latter’s two findings plus subsequent bench disposition rather than falsely quoting another verdict.

## Contract audit

Production behavior is at `scripts/check_gate_ledger.py:57-110`: `_ledger_rows` strips each input line at line 64, terminates on a stripped `## ` heading at line 73, starts at the first pipe line, and marks that first contiguous pipe block ended at lines 75-90.

The repaired test at `tests/test_check_gate_ledger.py:273-280` now proves that an indented summary terminates the ledger section. Under the reverted `line.startswith("## ")` mutant, the numbered row reaches the post-table detector and produces:

```text
gate-ledger: item 4: ledger row outside the ledger table
FAILED (failures=1)
NUMBERED_MUTANT_EXIT=1
```

Under that same production mutant, restoring the former `**1**` probe passes because the post-table detector only recognizes digit-string keys:

```text
Ran 1 test in 0.212s
OK
BOLD_MUTANT_EXIT=0
```

Rejection/ignore test audit:

| Test | Permissive mutant | Notices? |
|---|---|---|
| `test_missing_key_is_refused` | Permit absent keys | Yes |
| `test_duplicate_key_is_refused` | Keep only the first/last duplicate | Yes |
| `test_empty_evidence_is_refused` | Accept empty evidence | Yes |
| `test_not_run_is_refused` | Treat `NOT-RUN` as complete | Yes |
| `test_unresolvable_path_is_refused` | Accept nonexistent targets | Yes |
| `test_line_suffix_is_refused_as_a_path` | Normalize `:N` to the underlying path | Yes, but not a literal existing `:N` filename; SF1 |
| `test_escaping_path_is_refused` | Remove `..`, `~`, or `/` guard | `..`/`~`: yes; `/`: no, SF2 |
| `test_hex_string_that_is_neither_commit_nor_path_is_refused` | Treat regex-shaped hex as a resolving commit | Yes |
| `test_unescaped_pipe_inside_backticked_gate_item_is_named_malformed` | Restore code-span-aware splitting | Yes |
| Extra/missing-cell malformed tests | Truncate excess or accept/pad short rows | Yes |
| `test_code_spanned_evidence_is_refused_as_not_plain_text` | Normalize backticks and accept the target | Yes |
| `test_numbered_row_after_blank_is_outside_ledger_table` | Ignore or parse the later row | Yes |
| `test_fenced_ledger_before_real_section_fails_closed` | Ignore the fenced ledger and accept the real one | Yes |
| `test_unrecognised_ledger_row_is_named` | Silently ignore `**1**` | Yes |
| `test_heading_drift_has_one_named_refusal` | Accept the drifted heading | Yes |
| `test_lowercase_run_is_refused_as_not_uppercase` | Accept case-insensitive `RUN` | Yes |
| `test_indented_summary_terminates_the_ledger_section` | Use raw-heading termination | Yes, after `55bf9f73` |
| `test_valid_path_matches_gen_state_check_pointer` | Delete absolute or URL syntax guard | No, SF2 |
| `test_unstructured_evidence_is_refused_with_one_message` | Accept arbitrary nonempty evidence | Yes |
| `test_item_twelve_path_is_refused_even_when_it_exists` | Permit item-12 paths | Yes |
| `test_item_twelve_sha_must_match_head` | Skip resolution or head comparison | Yes |
| Template-refusal tests | Accept `NOT-RUN` rows | Yes |

## Same-signature

“Regression that does not bite” is not the same signature as terra 208 I1 or luna 215. Terra 208 I1 was a production scanner defect; luna 215 verified that the new escaped-backtick regression actively failed when its guard was removed.

A rule-11 same-signature trigger nevertheless did fire on this lane for a different class: round 1 (`1529b09a`) invented the code-span cell model, and round 2 (`2983cdd4`) patched a defect internal to that invention. `MAGISTRATE-NOTES.md:24-35` correctly supersedes the prior `NEW` classification and names their shared class as “hand-rolled cell model ≠ GFM’s one rule.”

For the test-quality class “regression does not bite,” there is not yet a two-consecutive-round trigger: luna 227 SF1 is the first such round among terra 208/luna 215/luna 227.

## Executed evidence

```text
$ PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_check_gate_ledger tests.test_docs_freshness
.....................................
----------------------------------------------------------------------
Ran 37 tests in 5.096s

OK
FINAL_SUITE_EXIT=0
```

```text
$ git diff --check 5ed6f1e9 55bf9f73
FINAL_DIFF_5ed6_55bf_EXIT=0
$ git diff --check 55bf9f73 d14a818d
FINAL_DIFF_55bf_d14a_EXIT=0
```

```text
$ PYTHONDONTWRITEBYTECODE=1 python3 scripts/check_gate_ledger.py --help >/dev/null
FINAL_HELP_EXIT=0
```

All transient production/test mutations were reversed:

```text
$ git diff --exit-code
RESTORE_DIFF_EXIT=0
```

## Residual risk

No live GitHub Actions event was available; workflow execution remains outside this local review.

VERDICT: `SHOULD-FIX 3`

Final `git status --porcelain`:

```text
$ git status --porcelain
```