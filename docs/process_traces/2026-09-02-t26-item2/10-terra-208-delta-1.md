```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "All dictated closures land, but the new GFM splitter falsely rejects a row containing an escaped literal backtick.",
  "workspace": {
    "base_requested": "b36d6c2d995097d45bad2cee4bb369c223c2b071",
    "base_mode": "exact",
    "head_start": "1529b09a9fc0f11216b2a6b6e5c91c2cbbc190fc",
    "head_end": "1529b09a9fc0f11216b2a6b6e5c91c2cbbc190fc",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "verdict": "NOT CLEAN",
    "closures": {
      "F-A": {
        "status": "CONFIRMED",
        "site": ".github/workflows/gate-ledger.yml:15,47",
        "counterfactual": "M1 removing ref remains YAML-valid; this is CI-only, so no local named test can kill it."
      },
      "F-B": {
        "status": "CONFIRMED",
        "site": ".github/pull_request_template.md:5,11,13,15,17,20",
        "counterfactual": "Restoring generic labels loses the dictated D-118/D-121/D-170 fidelity; no executable test was prescribed. Exact dictated literals landed (their supplied lengths are 95-114 characters despite the approximate ~90 qualifier)."
      },
      "F-C": {
        "status": "CONFIRMED",
        "site": "scripts/check_gate_ledger.py:77-84; tests/test_check_gate_ledger.py:89-104",
        "counterfactual": "M2 deletion of the .. guard accepts an existing ../ route (defects=[]); test_escaping_path_is_refused would fail."
      },
      "F-D": {
        "status": "CONFIRMED",
        "site": "scripts/check_gate_ledger.py:19-53; tests/test_check_gate_ledger.py:121-128",
        "counterfactual": "M3 naive splitting reports item 4 missing for the backticked-pipe row; the named test expects 12/12 RUN and fails."
      },
      "F-E": {
        "status": "CONFIRMED",
        "site": "scripts/check_gate_ledger.py:125-134; tests/test_check_gate_ledger.py:106-119",
        "counterfactual": "M4 SHA-only logic rejects path-only deadbee as an unresolved commit; the path test expects success and fails. A 7-char target that is both a commit prefix and filename accepts; is_commit is evaluated first, but OR acceptance is correct."
      },
      "F-F": {
        "status": "CONFIRMED",
        "site": "tests/test_check_gate_ledger.py:89-104",
        "counterfactual": "The outside target exists; a no-.. mutant accepts it, so the test's required refusal fails."
      },
      "F-G": {
        "status": "CONFIRMED",
        "site": "docs/orchestration.md:81-82",
        "counterfactual": "The replaced sentence is a pointer only; restoring the prior fill-before-self-merge directive is a static doctrine regression, with no named executable test."
      },
      "F-H": {
        "status": "CONFIRMED",
        "site": "tests/test_check_gate_ledger.py:130-148",
        "counterfactual": "The tests kill removal of their respective refusal branches. b36 already produced both specified messages, so this closure adds missing regression coverage rather than changing production behavior."
      },
      "F-I": {
        "status": "CONFIRMED",
        "site": "scripts/check_gate_ledger.py:146-160; tests/test_check_gate_ledger.py:168-176",
        "counterfactual": "b36 raises FileNotFoundError for a missing repo root; current code returns one input-error line. A defect list remains ordinary output, not an input error."
      }
    },
    "findings": [
      {
        "id": "I1",
        "severity": "should_fix",
        "file": "scripts/check_gate_ledger.py:28",
        "input": "| 4 | gate \\` literal tick | RUN scripts/check_gate_ledger.py |",
        "observed": "The escaped literal backtick is treated as a code-span opener; _split_table_row returns two cells and check() emits `gate-ledger: item 4: missing`. The row is otherwise valid GFM table syntax."
      }
    ],
    "tests": {
      "named_modules": {
        "cmd": "python3 -m unittest tests.test_check_gate_ledger tests.test_docs_freshness",
        "exit_code": 0,
        "tail": [
          "....................",
          "----------------------------------------------------------------------",
          "Ran 20 tests in 1.046s",
          "",
          "OK"
        ]
      },
      "synthetic_12_rows": {
        "cmd": "python3 scripts/check_gate_ledger.py --body-file \"$TMPDIR/t26-synthetic-ledger.md\" --head-sha \"$(git rev-parse HEAD)\" --repo-root .",
        "exit_code": 0,
        "output": "gate-ledger: 12/12 RUN"
      },
      "input_edges": {
        "repo_root_file": "gate-ledger: input error: repository root does not exist: scripts/check_gate_ledger.py",
        "body_directory": "gate-ledger: input error: [Errno 21] Is a directory: '.../scratchpad/tmp208'",
        "defect_list": "Eleven NOT-RUN refusals printed with exit 1; no input-error wrapper."
      },
      "parser_probes": {
        "unequal_backtick_runs": "pass",
        "CRLF": "pass",
        "no_leading_or_trailing_pipes": "pass",
        "unclosed_code_span": "fail-closed as item 4 missing",
        "escaped_backtick": "I1"
      }
    },
    "same_signature": {
      "merge-ref checkout": "KILLED — explicit head ref at workflow:47; M1 remains CI-only.",
      "label fidelity": "KILLED — exact dictated labels and key/doctrine notice landed.",
      "pointer parity": "KILLED — all gen_state path predicates, including nonempty-string refusal, are copied.",
      "malformed evidence untested": "KILLED — exact-output tests now cover both requested forms.",
      "path-branch misclassification": "KILLED — path-only hex filename and neither-target cases covered.",
      "traversal test vacuity": "KILLED — test creates an existing outside target and kills M2.",
      "traceback on bad input": "KILLED — missing root and unreadable body produce one-line input errors.",
      "F-D GFM cell-splitting family": "SURVIVES in adjacent form — I1 mishandles an escaped backtick outside a code span."
    }
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_check_gate_ledger tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["Ran 20 tests in 1.046s", "OK"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 20 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "python3 scripts/check_gate_ledger.py --body-file \"$TMPDIR/t26-synthetic-ledger.md\" --head-sha \"$(git rev-parse HEAD)\" --repo-root .",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": ["gate-ledger: 12/12 RUN"]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^gate-ledger: 12/12 RUN$"
      }
    },
    {
      "id": "V3",
      "kind": "lint",
      "cmd": "ruby -ryaml -e 'YAML.load_file(\".github/workflows/gate-ledger.yml\")'",
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
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "M1 checkout-ref removal cannot be killed locally; only a PR workflow run distinguishes merge-ref from head checkout.",
      "needs": "Run the workflow on a PR after the I1 repair."
    }
  ]
}
```

## Findings

I1 is the new defect: a backslash-escaped backtick outside code must stay literal, but the scanner starts a code span and suppresses the evidence-cell separator.

## Residual risk

The workflow use of `github.event.pull_request.head.sha` is valid for `pull_request` workflows, including the `edited` activity; GitHub specifically documents it for head-only checkout, while default checkout uses the merge branch. [GitHub Actions documentation](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)