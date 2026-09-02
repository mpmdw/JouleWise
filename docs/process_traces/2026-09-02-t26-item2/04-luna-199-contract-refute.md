```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Review complete: the ledger is present and advisory, but PR-head checkout, label fidelity, path-rule parity, pointer shape, and two test branches need fixes.",
  "workspace": {
    "base_requested": "6075389a",
    "base_mode": "exact",
    "head_start": "6075389a13df206205651175a7a9d52135df6fde",
    "head_end": "b36d6c2d995097d45bad2cee4bb369c223c2b071",
    "upstream_end": "3e6243df8943f6a4ec152cab7ea791a8a161efea",
    "branch": "feat/2026-09-02-t26-gateledger"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "clauses": {
      "(a)": "Twelve keyed rows exist, but F2-F6 identify omitted operative obligations in labels.",
      "(b)": "Named refusal classes, triggers, ADVISORY header, item-12 comparison, and unchanged ci.yml are present; F1 and F7 remain.",
      "(c)": "Pass: the checker validates ledger structure and references, not evidence truth or pasted-block content.",
      "orchestration_pointer": "F8: the line restates the rule instead of being only a pointer.",
      "tests": "F9-F10: malformed RUN and item-12 non-SHA refusal branches are uncovered.",
      "freshness": "Pass."
    },
    "findings": [
      {
        "id": "F1",
        "severity": "blocker",
        "file:line": ".github/workflows/gate-ledger.yml:42",
        "ruled_text": "any RUN path does not resolve at the PR head",
        "landed_text": "actions/checkout@v4 with only fetch-depth: 0; the checker is invoked with --repo-root .",
        "why_they_differ": "For pull_request events, checkout defaults to the synthetic merge ref unless ref is overridden. The checker therefore can validate a path present in the merge tree but absent at the PR head."
      },
      {
        "id": "F2",
        "severity": "should_fix",
        "file:line": ".github/pull_request_template.md:9",
        "ruled_text": "Lead-written FIX contract with dictated closure shapes; findings are triaged and dispositioned, never silently applied.",
        "landed_text": "Lead-written FIX contract; findings triaged and dispositioned",
        "why_they_differ": "The label drops the dictated-closure-shapes and never-silently-applied obligations, so it is not a faithful paraphrase of item 3."
      },
      {
        "id": "F3",
        "severity": "should_fix",
        "file:line": ".github/pull_request_template.md:11",
        "ruled_text": "Same-signature statement required from every delta. A surviving class fires the escalation trigger: the next spend is a consult, not another fix round.",
        "landed_text": "Same-signature statement from every delta",
        "why_they_differ": "The escalation-trigger obligation is omitted from item 5's label."
      },
      {
        "id": "F4",
        "severity": "should_fix",
        "file:line": ".github/pull_request_template.md:13",
        "ruled_text": "A Fable-class judgment pass that READS THE CODE and answers design-level questions ... What may never happen is the gate being skipped or downgraded to a cheaper model tier.",
        "landed_text": "Apex Fable code-reading diff gate; magistrate adjudication",
        "why_they_differ": "The label does not preserve the required design-level judgment or the prohibition on skipping or downgrading the gate."
      },
      {
        "id": "F5",
        "severity": "should_fix",
        "file:line": ".github/pull_request_template.md:15",
        "ruled_text": "Lead full-suite replay, unpiped, on the INTEGRATION tree (not the stale branch), with the exact tail recorded.",
        "landed_text": "Lead unpiped full-suite replay on the integration tree",
        "why_they_differ": "The label omits the not-stale-branch constraint and exact-tail recording obligation."
      },
      {
        "id": "F6",
        "severity": "should_fix",
        "file:line": ".github/pull_request_template.md:18",
        "ruled_text": "after EVERY other pass ... the magistrate itself — WITH full session context — reviews the exact merge candidate last; no delegation of this terminal slot",
        "landed_text": "Magistrate terminal review on the final head sha",
        "why_they_differ": "The label omits full session context, exact merge-candidate review, and the no-delegation requirement."
      },
      {
        "id": "F7",
        "severity": "should_fix",
        "file:line": "scripts/check_gate_ledger.py:40",
        "ruled_text": "reuse gen_state.py _check_pointer path rules",
        "landed_text": "_valid_path checks startswith/escape conditions, joins the path, and calls isfile; it lacks _check_pointer's not isinstance(path, str) or not path condition.",
        "why_they_differ": "The four path predicates are not reproduced exactly: the explicit nonempty-string/type condition at scripts/gen_state.py:134 is dropped. No fifth condition was added."
      },
      {
        "id": "F8",
        "severity": "should_fix",
        "file:line": "docs/orchestration.md:81",
        "ruled_text": "docs/orchestration.md ... gets a one-line pointer",
        "landed_text": "The gate ledger has a tracked form (template + gate-ledger job, D-170); fill all twelve rows before self-merge.",
        "why_they_differ": "This restates operative doctrine instead of only pointing to the ruling/D-170, creating a second source that can drift."
      },
      {
        "id": "F9",
        "severity": "should_fix",
        "file:line": "scripts/check_gate_ledger.py:82",
        "ruled_text": "CI ... fails when any of the twelve keys is missing, any row reads NOT-RUN or is empty, or any RUN path does not resolve",
        "landed_text": "if not match: ... evidence must be RUN <path-or-sha>",
        "why_they_differ": "This refusal branch has no defect-shaped test. Existing tests cover missing, duplicate, empty, NOT-RUN, bad SHA, mismatch, and path failures, but not malformed evidence such as arbitrary text."
      },
      {
        "id": "F10",
        "severity": "should_fix",
        "file:line": "scripts/check_gate_ledger.py:92",
        "ruled_text": "item 12 names the final head sha",
        "landed_text": "elif key == 12: defects.append('gate-ledger: item 12: final-head evidence must be a commit sha')",
        "why_they_differ": "The item-12 RUN-path/non-SHA refusal branch has no corresponding test."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "inspection",
      "cmd": "git status --short --branch; git rev-parse HEAD^; git rev-parse HEAD; git rev-parse main; git diff --quiet 6075389a..HEAD -- .github/workflows/ci.yml; echo ci_unchanged_exit=$?",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "## HEAD (no branch)",
          "6075389a13df206205651175a7a9d52135df6fde",
          "b36d6c2d995097d45bad2cee4bb369c223c2b071",
          "3e6243df8943f6a4ec152cab7ea791a8a161efea",
          "ci_unchanged_exit=0"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "ci_unchanged_exit=0"
      }
    },
    {
      "id": "V2",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_docs_freshness",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK$"
      }
    },
    {
      "id": "V3",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_check_gate_ledger",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "OK$"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "python3 - <<'PY'\nfrom pathlib import Path\nfrom scripts.check_gate_ledger import check\nhead = 'b36d6c2d995097d45bad2cee4bb369c223c2b071'\nrows = [f'| {n} | x | RUN README.md |' for n in range(1, 12)]\nrows.append('| 12 | x | RUN b36d6c2 |')\nbody = '## Gate ledger (D-118 / D-121)\\n\\n' + '\\n'.join(rows) + '\\n'\nprint(check(body, head, Path('.')))\nPY",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "[]"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "^\\[\\]$"
      }
    }
  ],
  "flags": [
    {
      "id": "FL1",
      "kind": "baseline_drift",
      "level": "nonblocking",
      "text": "Local main/origin/main is 3e6243df, ahead of the explicitly requested 6075389a baseline; HEAD's parent is the requested baseline and this review used it.",
      "needs": ""
    },
    {
      "id": "FL2",
      "kind": "residual_risk",
      "level": "nonblocking",
      "text": "The workflow correctly remains ADVISORY until Ed completes the external branch-protection E1 action.",
      "needs": "Ed must require gate-ledger on main for hosted CI to block merges."
    }
  ],
  "same_signature": "n/a (first round)"
}
```

## Findings

1. F1 is a blocker: checkout must explicitly use `github.event.pull_request.head.sha`.
2. F2–F6 are material label omissions.
3. F7 identifies incomplete `_check_pointer` parity.
4. F8 is a pointer-shape violation.
5. F9–F10 are uncovered refusal branches.

## Residual risk

Branch protection remains an external, advisory-only dependency until Ed completes E1.