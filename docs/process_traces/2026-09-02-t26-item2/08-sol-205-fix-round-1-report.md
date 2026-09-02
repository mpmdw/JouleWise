```json
{
  "schema": "claude-codex-report/v1",
  "genre": "implementation",
  "status": "findings",
  "completion": "complete",
  "summary": "Applied all nine dictated gate-ledger closures; focused acceptance and three locally testable mutations pass.",
  "workspace": {
    "base_requested": "b36d6c2d995097d45bad2cee4bb369c223c2b071",
    "base_mode": "exact",
    "head_start": "b36d6c2d995097d45bad2cee4bb369c223c2b071",
    "head_end": "b36d6c2d995097d45bad2cee4bb369c223c2b071",
    "upstream_end": null,
    "branch": "feat/2026-09-02-t26-gateledger"
  },
  "pathspec": [
    ".github/pull_request_template.md",
    ".github/workflows/gate-ledger.yml",
    "scripts/check_gate_ledger.py",
    "tests/test_check_gate_ledger.py",
    "docs/orchestration.md"
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
      "cmd": "python3 -m unittest tests.test_check_gate_ledger tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "....................",
          "----------------------------------------------------------------------",
          "Ran 20 tests in 1.015s",
          "",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 20 tests in [0-9.]+s\\n\\nOK$"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "python3 scripts/check_gate_ledger.py --body-file /private/tmp/claude-501/-Users-edr-code-JouleWise/540125d5-d8ee-49d1-8e6e-17050e77212d/scratchpad/tmp205/gate-ledger-body.8LPJFm --head-sha \"$(git rev-parse HEAD)\" --repo-root .",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "gate-ledger: 12/12 RUN"
        ]
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
    },
    {
      "id": "V4",
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
    }
  ],
  "flags": [
    {
      "id": "F1",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "M1 cannot be killed locally because actions/checkout synthetic-merge versus pull-request-head behavior exists only in a GitHub pull_request run.",
      "needs": "Confirm the workflow checks out github.event.pull_request.head.sha in PR CI."
    },
    {
      "id": "F2",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "The branch cites D-170, but docs/decision_log.md contains no D-170 entry; the installed cold-gate ruling and dictated prompt supplied the controlling text.",
      "needs": "Lead should ensure the D-170 decision-log entry is present on the integration lineage."
    }
  ]
}
```

## Change

Implemented F-A through F-I within the exhaustive write scope. The checker now handles GFM pipes, accepts item 1–11 evidence as either a commit or valid path, preserves item 12’s SHA-only rule, matches all pointer path predicates, and converts input I/O failures into one-line refusals.

The template labels and orchestration pointer now follow the dictated doctrine boundary. The workflow explicitly checks out the PR head SHA.

Same-signature statement: no defect class reported by luna 199 or sol 200 survives this fix round.

`git diff --stat`:

    .github/pull_request_template.md  | 12 +++---
    .github/workflows/gate-ledger.yml |  2 +
    docs/orchestration.md             |  4 +-
    scripts/check_gate_ledger.py      | 59 ++++++++++++++++++++++++----
    tests/test_check_gate_ledger.py   | 81 +++++++++++++++++++++++++++++++++++----
    5 files changed, 136 insertions(+), 22 deletions(-)

No files outside `WRITE_SCOPE` were touched. No commit or rebase was performed.

## Clause map

| Clause | Production site | Biting test | Counterfactual |
|---|---|---|---|
| F-A | [gate-ledger.yml:15](/Users/edr/code/JouleWise-wt-t26-c/.github/workflows/gate-ledger.yml:15), [gate-ledger.yml:47](/Users/edr/code/JouleWise-wt-t26-c/.github/workflows/gate-ledger.yml:47) | CI-only; no local test can reproduce checkout’s synthetic PR merge ref | Removing `ref:` validates paths against the merge tree rather than the PR head |
| F-B | [pull_request_template.md:5](/Users/edr/code/JouleWise-wt-t26-c/.github/pull_request_template.md:5), rows 3/5/7/9/12 at lines 11–20 | Inspection; parser independence is exercised at [test_check_gate_ledger.py:121](/Users/edr/code/JouleWise-wt-t26-c/tests/test_check_gate_ledger.py:121) | Keys still parse, but abbreviated labels silently misstate authoritative doctrine |
| F-C | [check_gate_ledger.py:77](/Users/edr/code/JouleWise-wt-t26-c/scripts/check_gate_ledger.py:77) | [test_check_gate_ledger.py:89](/Users/edr/code/JouleWise-wt-t26-c/tests/test_check_gate_ledger.py:89) | Empty/non-string or escaped pointers diverge from `_check_pointer` |
| F-D | [check_gate_ledger.py:19](/Users/edr/code/JouleWise-wt-t26-c/scripts/check_gate_ledger.py:19), [check_gate_ledger.py:68](/Users/edr/code/JouleWise-wt-t26-c/scripts/check_gate_ledger.py:68) | [test_check_gate_ledger.py:121](/Users/edr/code/JouleWise-wt-t26-c/tests/test_check_gate_ledger.py:121) | A pipe inside the code span splits the table row and item 4 becomes missing |
| F-E | [check_gate_ledger.py:125](/Users/edr/code/JouleWise-wt-t26-c/scripts/check_gate_ledger.py:125) | [test_check_gate_ledger.py:106](/Users/edr/code/JouleWise-wt-t26-c/tests/test_check_gate_ledger.py:106), [test_check_gate_ledger.py:115](/Users/edr/code/JouleWise-wt-t26-c/tests/test_check_gate_ledger.py:115) | A hex filename is forced into commit-only validation, or an invalid short ref receives the wrong refusal |
| F-F | [check_gate_ledger.py:79](/Users/edr/code/JouleWise-wt-t26-c/scripts/check_gate_ledger.py:79) | [test_check_gate_ledger.py:89](/Users/edr/code/JouleWise-wt-t26-c/tests/test_check_gate_ledger.py:89) | Removing the traversal guard accepts an existing `../outside-evidence.txt` |
| F-G | [orchestration.md:81](/Users/edr/code/JouleWise-wt-t26-c/docs/orchestration.md:81) | Broad freshness coverage begins at [test_docs_freshness.py:81](/Users/edr/code/JouleWise-wt-t26-c/tests/test_docs_freshness.py:81); doctrine fidelity is inspection-based | Orchestration restates operative merge doctrine instead of pointing to D-170 |
| F-H | [check_gate_ledger.py:120](/Users/edr/code/JouleWise-wt-t26-c/scripts/check_gate_ledger.py:120), [check_gate_ledger.py:131](/Users/edr/code/JouleWise-wt-t26-c/scripts/check_gate_ledger.py:131) | [test_check_gate_ledger.py:130](/Users/edr/code/JouleWise-wt-t26-c/tests/test_check_gate_ledger.py:130), [test_check_gate_ledger.py:140](/Users/edr/code/JouleWise-wt-t26-c/tests/test_check_gate_ledger.py:140) | Free-form evidence or a path in item 12 avoids the exact fail-closed message |
| F-I | [check_gate_ledger.py:146](/Users/edr/code/JouleWise-wt-t26-c/scripts/check_gate_ledger.py:146) | [test_check_gate_ledger.py:168](/Users/edr/code/JouleWise-wt-t26-c/tests/test_check_gate_ledger.py:168) | A missing repository root produces a traceback |

## Mutation check

- M1 — not locally killable. Local tests invoke the checker against an explicit repository root and cannot reproduce GitHub’s synthetic merge checkout. The explicit head `ref:` must be confirmed in PR CI.
- M2 — KILLED. Removing the `..` predicate makes the existing outside target pass; the focused mutant test exited 1.
- M3 — KILLED. Removing code-span awareness makes item 4 disappear; the focused mutant test exited 1.
- M4 — KILLED. Refusing item 1–11 evidence solely on `not _is_commit` rejects the valid `deadbee` filename; the focused mutant test exited 1.

## Verification notes

The canonical discovery suite was intentionally not run, per the task’s explicit restriction. Only the named acceptance suite and checks were run.

## Residual risk

D-170 is absent from this branch’s `docs/decision_log.md`, although the template, workflow, and orchestration document reference it. That path was outside this delegated write scope.