```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "Round-3 behavior is installed and mutation-tested, but D-170 remains dangling and F-9 lacks a biting regression test.",
  "workspace": {
    "base_requested": "5ed6f1e9f380c9c59c8d2923aa5331ed250838d6",
    "base_mode": "exact",
    "head_start": "5ed6f1e9f380c9c59c8d2923aa5331ed250838d6",
    "head_end": "5ed6f1e9f380c9c59c8d2923aa5331ed250838d6",
    "upstream_end": null,
    "branch": null
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "verdict": "BLOCKER 1",
    "counts": {"blocker": 1, "should_fix": 1, "nit": 0},
    "findings": [
      {
        "id": "B1",
        "severity": "blocker",
        "title": "D-170 is absent from docs/decision_log.md",
        "file": ".github/pull_request_template.md:5; .github/workflows/gate-ledger.yml:4; docs/orchestration.md:82",
        "counterfactual": "Following the shipped D-170 authority pointers finds no decision-log entry.",
        "observed": "decision_log_D-170_count=0"
      },
      {
        "id": "SF1",
        "severity": "should_fix",
        "title": "F-9/N6 regression test does not distinguish the reverted implementation",
        "file": "tests/test_check_gate_ledger.py:273",
        "counterfactual": "With a valid numbered row after `  ## Summary`, landed code returns `gate-ledger: 12/12 RUN`; reverted raw-heading termination returns `gate-ledger: item 4: ledger row outside the ledger table`. The existing bold `**1**` probe makes both implementations pass.",
        "observed": "Reverted F-9 mutation: Ran 37 tests; OK; EXIT=0"
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "suite",
      "cmd": "python3 -m unittest tests.test_check_gate_ledger tests.test_docs_freshness",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["Ran 37 tests in 1.576s", "OK"]},
      "expected": {"exit_code": 0, "tail_regex": "Ran 37 tests in [0-9.]+s\\n\\nOK"}
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "python3 scripts/check_gate_ledger.py --root . --body .github/pull_request_template.md; echo EXIT=$?",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["gate-ledger: item 12: NOT-RUN", "EXIT=1"]},
      "expected": {"exit_code": 0, "tail_regex": "gate-ledger: item 12: NOT-RUN\\nEXIT=1"}
    },
    {
      "id": "V3",
      "kind": "inspection",
      "cmd": "python3 -c '<direct _split_table_row probe over all ten ruling rows>'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["10: actual=['a \\\\\\\\| b'] expected=['a \\\\\\\\| b'] match=True"]},
      "expected": {"exit_code": 0, "tail_regex": "10: .*match=True"}
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "python3 -c '<filled ledger with real item-12 SHA and omitted --head-sha>'",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": ["gate-ledger: item 12: sha is not the PR head", "EXIT=1"]},
      "expected": {"exit_code": 0, "tail_regex": "sha is not the PR head\\nEXIT=1"}
    },
    {
      "id": "V5",
      "kind": "test",
      "cmd": "python3 -m unittest tests.test_check_gate_ledger tests.test_docs_freshness",
      "cwd": "$TMPDIR/gate-ledger-reaudit.Stp3Er",
      "observed": {"result": "fail", "exit_code": 1, "tail": ["FAILED (failures=6)", "EXIT=1"]},
      "expected": {"exit_code": 1, "tail_regex": "FAILED \\(failures=[1-9][0-9]*\\)"}
    },
    {
      "id": "V6",
      "kind": "inspection",
      "cmd": "git status --porcelain",
      "cwd": ".",
      "observed": {"result": "pass", "exit_code": 0, "tail": []},
      "expected": {"exit_code": 0, "tail_regex": "^$"}
    }
  ],
  "flags": [
    {
      "id": "FLAG1",
      "kind": "lead_ruling",
      "level": "blocking",
      "text": "D-170 authority is referenced by shipped files but absent from docs/decision_log.md.",
      "needs": "Lead must land or remove the D-170 authority reference."
    },
    {
      "id": "FLAG2",
      "kind": "verification_gap",
      "level": "nonblocking",
      "text": "No live GitHub Actions event was available; workflow safeguards were text-tested.",
      "needs": "Confirm on the first real PR run."
    }
  ]
}
```

## Findings

### BLOCKER

B1 — `D-170` is still a dangling authority reference.

Observed:

```text
decision_log_D-170_count=0
.github/pull_request_template.md:5
.github/workflows/gate-ledger.yml:4
docs/orchestration.md:82
```

The shipped files cite D-170, but `docs/decision_log.md` contains no D-170 body.

### SHOULD-FIX

SF1 — F-9/N6’s test is non-biting.

Production `scripts/check_gate_ledger.py:64` correctly uses the stripped heading. However, `tests/test_check_gate_ledger.py:273` appends an unrecognised `**1**` row, which the old parser silently ignored.

Counterfactual input:

```text
<valid ledger>

  ## Summary
| 4 | valid row after summary | RUN evidence.txt |
```

Landed output:

```text
gate-ledger: 12/12 RUN
RC=0
```

Reverted F-9 output:

```text
gate-ledger: item 4: ledger row outside the ledger table
RC=1
```

The full reverted suite nevertheless passed 37 tests.

Nits: none.

## Contract coverage

### Ruling L2/L3

| Clause | Production | Biting test | Verdict | Counterfactual |
|---|---|---|---|---|
| L2 splitter: odd-backslash pipe rule, consume escaping slash, trim framing cells | `scripts/check_gate_ledger.py:19` | `tests/test_check_gate_ledger.py:195` | INSTALLED | `| f\|oo |` gives `['f|oo']`; naive splitting gives `['f\\', 'oo']`. |
| L2 parity: `\\|` splits and `\\\|` does not | `scripts/check_gate_ledger.py:29` | `tests/test_check_gate_ledger.py:205` | INSTALLED | Ten-row table passes both parity cases exactly. |
| L2 no inline syntax model | `scripts/check_gate_ledger.py:20` | `tests/test_check_gate_ledger.py:195` | INSTALLED | `| a \`b | c\` |` gives `['a \`b', 'c\`']`. |
| L2 arity `!= 3` is named, never truncated | `scripts/check_gate_ledger.py:102` | `tests/test_check_gate_ledger.py:140,162,173` | INSTALLED | Extra cell → `row has 4 cells`; short row → `row has 2 cells`. |
| L2 malformed keys skip missing/duplicate/evidence checks | `scripts/check_gate_ledger.py:142` | `tests/test_check_gate_ledger.py:140` | INSTALLED | Malformed item 4 emits exactly one arity defect, not `missing`. |
| L2 escaped/raw/extra/short regressions | `scripts/check_gate_ledger.py:102` | `tests/test_check_gate_ledger.py:140,153,162,173,184` | INSTALLED | Escaped pipe passes; raw pipe, extra, and short rows refuse. |
| L2 plain-text evidence refusal | `scripts/check_gate_ledger.py:154` | `tests/test_check_gate_ledger.py:212` | INSTALLED | `RUN \`evidence.txt\`` → `evidence cell must be plain text (no backticks)`. |
| L3 structural same-class cure | `scripts/check_gate_ledger.py:19` | `tests/test_check_gate_ledger.py:195` | INSTALLED | Restoring code-span awareness fails the raw-pipe row. |
| L3 downstream ambiguity is refused | `scripts/check_gate_ledger.py:102,154` | `tests/test_check_gate_ledger.py:140,212` | INSTALLED | Arity and backtick evidence inputs are rejected, not modeled. |
| L3 ten-row spec table | `scripts/check_gate_ledger.py:19` | `tests/test_check_gate_ledger.py:195` | INSTALLED | All ten exact expected lists match; no row changed or dropped. |
| L3 context divergence uses first contiguous block | `scripts/check_gate_ledger.py:75` | `tests/test_check_gate_ledger.py:227` | INSTALLED | Numbered row after blank → `ledger row outside the ledger table`. |
| L3 fence behavior remains refusal, not modeling | `scripts/check_gate_ledger.py:66` | `tests/test_check_gate_ledger.py:236` | INSTALLED | Fenced template before real section → twelve `NOT-RUN` defects, rc 1. |

Ten-row exact results:

```text
1  ['f|oo']
2  ['b `|` az']
3  ['b **|** im']
4  ['abc', 'def']
5  ['bar']
6  ['bar', 'baz', 'boo']
7  ['abc', 'def']
8  ['a `b', 'c`']
9  ['a \\\\', 'b']
10 ['a \\\\| b']
```

### Opus S1–S5 and N1–N9

| Item | Production | Biting test | Verdict | Counterfactual |
|---|---|---|---|---|
| S1 | `scripts/check_gate_ledger.py:154` | `tests/test_check_gate_ledger.py:212` | INSTALLED | Backticked evidence emits the plain-text refusal. |
| S2 | `scripts/check_gate_ledger.py:19,102` | `tests/test_check_gate_ledger.py:140,195` | INSTALLED | Raw pipe produces the four-cell arity refusal. |
| S3 | `.github/workflows/gate-ledger.yml:40` | `tests/test_check_gate_ledger.py:363` | INSTALLED | Removing permissions fails the workflow safeguard test. |
| S4 | `.github/workflows/gate-ledger.yml:52` | `tests/test_check_gate_ledger.py:363` | INSTALLED | Removing `head.sha` fails the same test. |
| S5 | `.github/pull_request_template.md:3` | `tests/test_check_gate_ledger.py:372` | INSTALLED | Shipped template emits exactly twelve `NOT-RUN` defects. |
| N1 | `.github/pull_request_template.md:3`; checker `:117` | `tests/test_check_gate_ledger.py:102,279` | INSTALLED | `RUN evidence.txt:12` → `neither a commit nor a path`. |
| N2 | `scripts/check_gate_ledger.py:66,80` | `tests/test_check_gate_ledger.py:236` | INSTALLED | Fenced quoted template → rc 1, twelve `NOT-RUN` lines. |
| N3 | `scripts/check_gate_ledger.py:95` | `tests/test_check_gate_ledger.py:243` | INSTALLED | `**1**` → `unrecognised ledger row: '**1**'`. |
| N4 | `scripts/check_gate_ledger.py:139` | `tests/test_check_gate_ledger.py:252` | INSTALLED | Heading drift → one named no-section refusal. |
| N5 | `scripts/check_gate_ledger.py:163` | `tests/test_check_gate_ledger.py:264` | INSTALLED | `run evidence.txt` → uppercase-`RUN` refusal. |
| N6 | `scripts/check_gate_ledger.py:64` | `tests/test_check_gate_ledger.py:273` | PARTIAL | Production is correct, but the existing test survives reverting it. |
| N7 | `.github/workflows/gate-ledger.yml:34` | `tests/test_check_gate_ledger.py:363` | INSTALLED | Removing `reopened` fails the trigger assertion. |
| N8 | `scripts/check_gate_ledger.py:113` | `tests/test_check_gate_ledger.py:279` | INSTALLED | Fixed pointer set agrees with `gen_state._check_pointer`. |
| N9 | `.github/workflows/gate-ledger.yml:6` | `tests/test_check_gate_ledger.py:363` | INSTALLED | Removing the deliberate-red comment fails the workflow test. |

## Same-signature

Against the ruling’s class definition, “hand-rolled cell model ≠ GFM’s one rule”:

| Closure | Classification |
|---|---|
| F-1 | REMOVES modelling |
| F-2 | ADDS a refusal |
| F-3 | ADDS a refusal |
| F-4 | neither; documents an existing refusal |
| F-5 | ADDS a refusal |
| F-6 | ADDS a refusal |
| F-7 | ADDS a refusal |
| F-8 | ADDS a refusal |
| F-9 | neither; fixes heading boundary handling |
| F-10 | neither |
| F-11 | neither |
| F-12 | neither |
| F-13 | neither |
| F-14 | neither |
| F-15 | neither |

`_split_table_row` models nothing beyond the ruled GFM pre-pass: pipe splitting, odd-backslash escape consumption, and prescribed framing normalization. It contains no code-span, fence, entity, inline, or independent whitespace model.

## Residual risk

No live GitHub Actions event was available; workflow behavior was validated by source inspection and regression tests.

## Executed evidence

Required suite:

```text
$ python3 -m unittest tests.test_check_gate_ledger tests.test_docs_freshness
.....................................
----------------------------------------------------------------------
Ran 37 tests in 1.576s

OK
EXIT=0
```

Template smoke:

```text
$ python3 scripts/check_gate_ledger.py --root . --body .github/pull_request_template.md; echo EXIT=$?
gate-ledger: item 1: NOT-RUN
...
gate-ledger: item 12: NOT-RUN
EXIT=1
```

GFM probe rows:

```text
row 1: actual=['1', 'gate `a', 'b`', 'RUN evidence.txt'] actual_count=4 gfm=['1', 'gate `a', 'b`'] gfm_count=3
row 2: actual=['2', 'gate `a | b`', 'RUN evidence.txt'] actual_count=3 gfm=['2', 'gate a | b', 'RUN evidence.txt'] gfm_count=3
row 3: actual=['3', 'gate 3', 'RUN evidence.txt', 'extra'] actual_count=4 gfm=['3', 'gate 3', 'RUN evidence.txt'] gfm_count=3
row 4: actual=['4', 'gate \\`tick', 'RUN evidence.txt'] actual_count=3 gfm=['4', 'gate `tick', 'RUN evidence.txt'] gfm_count=3
EXIT=0
```

Omitted `--head-sha`:

```text
gate-ledger: item 12: sha is not the PR head
EXIT=1
```

Workflow still passes `--head-sha`:

```text
52: ref: ${{ github.event.pull_request.head.sha }}
59: PR_HEAD_SHA: ${{ github.event.pull_request.head.sha }}
64: --head-sha "$PR_HEAD_SHA"
EXIT=0
```

Mutations, all run in the `$TMPDIR` archive and restored with `cp` plus `cmp`:

| Mutant | Result |
|---|---|
| M1 restore code-span tracking | KILLED by `test_split_table_row_matches_gfm_cell_rule` and `test_unescaped_pipe_inside_backticked_gate_item_is_named_malformed`; `FAILED (failures=6)`, EXIT=1 |
| M2 silent arity `continue` | KILLED by the three arity tests; `FAILED (failures=3)`, EXIT=1 |
| M3 delete `head.sha` ref | KILLED by `test_workflow_text_pins_round1_fixes`; `FAILED (failures=1)`, EXIT=1 |
| M4 delete permissions | KILLED by `test_workflow_text_pins_round1_fixes`; `FAILED (failures=1)`, EXIT=1 |
| M5 naive `split("|")` | KILLED by escaped-pipe tests; `FAILED (failures=5)`, EXIT=1 |
| Own O1: disable first-block context refusal | KILLED by `test_numbered_row_after_blank_is_outside_ledger_table`; `FAILED (failures=1)`, EXIT=1 |
| Own O2: remove backtick evidence refusal | KILLED by `test_code_spanned_evidence_is_refused_as_not_plain_text`; `FAILED (failures=2)`, EXIT=1 |
| Own O3: remove no-section refusal | KILLED by `test_heading_drift_has_one_named_refusal`; `FAILED (failures=1)`, EXIT=1 |
| F-9 audit mutation: revert stripped heading termination | SURVIVED; `Ran 37 tests`, `OK`, EXIT=0 |

Final authority scan:

```text
decision_log_D-170_count=0
```

VERDICT: `BLOCKER 1`

Final `git status --porcelain`:

```text
$ git status --porcelain
```