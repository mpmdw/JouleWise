```json
{
  "schema": "claude-codex-report/v1",
  "genre": "review",
  "status": "findings",
  "completion": "complete",
  "summary": "REFUTE: the arithmetic is repaired, but R7's documented CLI is non-executable, two R6 anchors are wrong, and the mutation/completeness tests retain material gaps.",
  "workspace": {
    "base_requested": "907f58773584dc28e3ee68d04ee5db7ca0cd269e",
    "base_mode": "descendant",
    "head_start": "35716229f181268407c3e42826540ef080ec17e0",
    "head_end": "35716229f181268407c3e42826540ef080ec17e0",
    "upstream_end": "35716229f181268407c3e42826540ef080ec17e0",
    "branch": "feat/2026-09-01-dependence"
  },
  "pathspec": [],
  "unowned_dirty": [],
  "verdict": {
    "result": "REFUTE",
    "findings": [
      {
        "id": "A1",
        "severity": "blocker",
        "title": "R7's disagreement command exits 2 because its backtick-removal expression is over-escaped, and the golden test does not execute it."
      },
      {
        "id": "A2",
        "severity": "should_fix",
        "title": "DS-SENS-02 and PG-SENS-02 claim draft line 292 while their named insertion sentence is at line 294."
      },
      {
        "id": "A3",
        "severity": "should_fix",
        "title": "The exact R4, R5, R6, and R8 document cures lack regression assertions."
      },
      {
        "id": "B1",
        "severity": "should_fix",
        "title": "Changing a worked-example table value survives all 11 tests."
      },
      {
        "id": "B2",
        "severity": "should_fix",
        "title": "Deleting required refusal rows can survive the completeness meta-test."
      },
      {
        "id": "C1",
        "severity": "should_fix",
        "title": "The three p-values cannot be derived from the sheet alone because it supplies no Student-t tail formula or table."
      },
      {
        "id": "C2",
        "severity": "nit",
        "title": "Holm is used before its procedure is defined."
      },
      {
        "id": "C3",
        "severity": "nit",
        "title": "The new freeze-label vocabulary is not glossed."
      }
    ]
  },
  "verification": [
    {
      "id": "V1",
      "kind": "test",
      "cmd": "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_dependence_sensitivity",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 0,
        "tail": [
          "Ran 11 tests in 13.045s",
          "OK"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "Ran 11 tests.*OK"
      }
    },
    {
      "id": "V2",
      "kind": "smoke",
      "cmd": "python3 scripts/dependence_sensitivity.py --block-deltas '[1,2,3,4,5,6,7,8,9,10]' --floor 1 --se-metrology 1e308 --deterministic-bound-total 0.1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 2,
        "tail": [
          "dependence_sensitivity.py: error: interval is not finite"
        ]
      },
      "expected": {
        "exit_code": 2,
        "tail_regex": "interval is not finite"
      }
    },
    {
      "id": "V3",
      "kind": "smoke",
      "cmd": "python3 scripts/dependence_sensitivity.py --block-deltas '[1e308,1e308,1e308,1e308,1e308,1e308,1e308,1e308,1e308,1e308]' --floor 1 --se-metrology 0.2 --deterministic-bound-total 0.1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 2,
        "tail": [
          "dependence_sensitivity.py: error: intermediate overflow in fsum"
        ]
      },
      "expected": {
        "exit_code": 2,
        "tail_regex": "overflow"
      }
    },
    {
      "id": "V4",
      "kind": "smoke",
      "cmd": "python3 scripts/dependence_sensitivity.py --example --floor 3.5",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 2,
        "tail": [
          "dependence_sensitivity.py: error: --example cannot be combined with input, --floor, --se-metrology, or --deterministic-bound-total"
        ]
      },
      "expected": {
        "exit_code": 2,
        "tail_regex": "cannot be combined"
      }
    },
    {
      "id": "V5",
      "kind": "smoke",
      "cmd": "python3 scripts/dependence_sensitivity.py --floor 1 --se-metrology 0.2 --deterministic-bound-total 0.1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 2,
        "tail": [
          "dependence_sensitivity.py: error: one of --block-deltas or --block-deltas-file is required unless --example is used"
        ]
      },
      "expected": {
        "exit_code": 2,
        "tail_regex": "is required unless --example"
      }
    },
    {
      "id": "V6",
      "kind": "smoke",
      "cmd": "python3 scripts/dependence_sensitivity.py --block-deltas '{\"a\":1}' --floor 1 --se-metrology 0.2 --deterministic-bound-total 0.1",
      "cwd": ".",
      "observed": {
        "result": "pass",
        "exit_code": 2,
        "tail": [
          "dependence_sensitivity.py: error: block_deltas_j must be a JSON list"
        ]
      },
      "expected": {
        "exit_code": 2,
        "tail_regex": "must be a JSON list"
      }
    },
    {
      "id": "V7",
      "kind": "smoke",
      "cmd": "python3 scripts/dependence_sensitivity.py --block-deltas \"$(grep '^| Ordered block deltas' docs/paper/round7/dependence-sensitivity.md | cut -d'|' -f3 | tr -d ' \\\\t' | tr -d '\\\\\\\\140')\" --floor 3.5 --se-metrology 0.2 --deterministic-bound-total 3.5",
      "cwd": ".",
      "observed": {
        "result": "fail",
        "exit_code": 2,
        "tail": [
          "dependence_sensitivity.py: error: --block-deltas is not valid JSON: Expecting value"
        ]
      },
      "expected": {
        "exit_code": 0,
        "tail_regex": "\"direction_gate_outcomes_agree\": false"
      }
    },
    {
      "id": "V8",
      "kind": "lint",
      "cmd": "git diff --check HEAD^ HEAD",
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
      "id": "ENV1",
      "kind": "environment",
      "level": "nonblocking",
      "text": "The sandbox cannot create shell temporary files (heredoc creation returned operation not permitted), so the full repository suite was not attempted; the focused 11-test module ran successfully without a temporary directory.",
      "needs": ""
    }
  ]
}
```

## Findings

### A. CONTRACT

| ID | Severity | File:line | What fails | Cure |
|---|---|---|---|---|
| A1 | blocker | `docs/paper/round7/dependence-sensitivity.md:97`; `tests/test_dependence_sensitivity.py:351-361` | The documented R7 command uses `tr -d '\\140'`, which leaves the backticks around the extracted JSON. Executing the line gives exit 2 and `not valid JSON`. The golden test calls `analyze_deltas` directly, so it certified the desired outcome without exercising the promised CLI. | Change the expression to `tr -d '\140'` and make the golden test execute the documented CLI path and parse its JSON output. The single-backslash form was verified to exit 0 with `direction_gate_outcomes_agree: false`. |
| A2 | should-fix | `docs/paper/round7/dependence-sensitivity.md:112,114`; `docs/paper/draft-v1.md:292,294` | Both disagreement rows say “insertion before … line 292” while naming the Limitation 1 sentence at line 294 as the sentence they precede. Line 292 is the section heading. DS-SENS-01 and PG-SENS-01 correctly resolve to line 285. | Change both disagreement insertion sites to frozen draft line 294, or deliberately anchor line 292 and name the section heading. |
| A3 | should-fix | `tests/test_dependence_sensitivity.py:363-426` | The tests do not lock R4’s first-use fence, DS-31/PG-07 supplier rule, named STOP_FILL reasons, R5’s interval sentence, R6’s draft anchors/seven-column contract, or R8’s exact wording and generator citations. A2 escaped through this gap. | Add exact document-contract assertions and resolve every claimed draft line against the named frozen-draft sentence. |

Ruling trace:

| Ruling | Cure hunk(s) | Test | Result |
|---|---|---|---|
| R1 | Script `42-55`; sheet `69-99` | Test `271-350` | PASS. Exactly one delta list exists. It is parsed from the sheet and equals the constant. Manual comparison found every current prose/table number equal to the script-derived `%.6f` rendering, with p-values at `%.9f`. |
| R2 | Script `58-90,140,147-151,161-162,201-205,363-451`; tests `89-245,552-568` | Refusal-table and AST tests | PARTIAL. All named refusal cases execute correctly; the `V>0` guard is gone and the one-line positive-definite explanation remains. Reverse completeness fails under row deletion (B2). |
| R3 | Script `438,450`; refusal row `214-218` | Test `552-559` | PASS. Overflow converts to exit 2 with empty stdout and an `overflow` reason. |
| R4 | Sheet `13,55-57,107-115` | Only partial artifact/document checks at `363-426` | Content PASS: DS-31/PG-07 supply the bracketed word; the sensitivity outcome field is `comparison.direction_gate_outcomes_agree`; named disagreement STOP_FILL reasons exist. Exact regression coverage is absent (A3). |
| R5 | Sheet `11` | No exact assertion | Content PASS; coverage gap A3. |
| R6 | Sheet `109-114` | No anchor-resolution test | FAIL for DS-SENS-02 and PG-SENS-02 (A2). All four rows otherwise have seven columns, DERIVE rules with reasons, freeze labels, and sources. |
| R7 | Sheet `95-99`; test `351-361` | Direct API only | FAIL (A1). |
| R8 | Sheet `9,11,47` | Only generic first-use checks at `420-425` | Content PASS: corrected square-root scope, cited field names/lines, and floor-symbol gloss are present. Exact coverage is absent (A3). |

The AST walker extracts 20 literal fragments, 18 unique, and every current fragment matches at least one of the 32 refusal rows. Adding the distinct literal `new_reason` fails as intended. It does not, however, establish that every required row remains present.

### B. EXECUTION

| ID | Severity | File:line | What fails | Cure |
|---|---|---|---|---|
| B1 | should-fix | `tests/test_dependence_sensitivity.py:301-347` | The golden test searches only the prose before `\| Model \|`. Changing the AR table’s `5.764703` to `5.764704` leaves all 11 tests green because the correct string remains in the prose. Thus it does not protect every printed number. | Parse the three worked-example table rows and compare each field semantically to the rendered model output, including occurrence and model identity. |
| B2 | should-fix | `tests/test_dependence_sensitivity.py:561-568` | Deleting either the required `overflow` row or `finite_string` row leaves the meta-test green. Regex overlap covers `finite_string`; overflow is a runtime reason rather than an AST literal. | Add two-way coverage: bind required source sites/path variants to row names and assert the exact mandated row-name set, while retaining the new-literal AST check. |

## Mutation table

| Mutation/execution | Catching test or result | Outcome |
|---|---|---|
| Sheet delta `5.0 → 5.1` | Golden test line 287: `AssertionError: Lists differ … First differing element 0: 5.1 / 5.0` | KILLED |
| Worked table AR \(n_{\mathrm{eff}}\) `5.764703 → 5.764704` | Full focused suite: `testsRun=11 failures=0 errors=0` | **UNCOVERED** |
| Control: unique prose p-value `0.000002814 → 0.000002815` | Golden line 347: `'0.000002814' not found` | KILLED |
| Add `raise ValueError("new_reason")` | Meta-test line 565: `no refusal row matches source literal: 'new_reason'` | KILLED |
| Delete `overflow` refusal row | Meta-test remains green | **UNCOVERED** |
| Delete `finite_string` refusal row | Meta-test remains green | **UNCOVERED** |
| `--se-metrology 1e308` | Exit 2; stdout empty; `interval is not finite` | PASS |
| `[1e308]*10` | Exit 2; stdout empty; `intermediate overflow in fsum` | PASS |
| `--example --floor 3.5` | Exit 2; stdout empty; `cannot be combined` | PASS |
| Metrology arguments without source | Exit 2; stdout empty; `is required unless --example` | PASS |
| `'{"a":1}'` | Exit 2; stdout empty; `must be a JSON list` | PASS |
| Sheet’s disagreement CLI | Exit 2; `not valid JSON: Expecting value` | **BASELINE FAILURE** |

### C. REGRESSION + PEDAGOGY

| ID | Severity | File:line | What fails | Cure |
|---|---|---|---|---|
| C1 | should-fix | `docs/paper/round7/dependence-sensitivity.md:9,79-83` | The sheet defines a p-value conceptually but gives no Student-*t* tail formula or lookup table. The three printed p-values cannot be obtained from the sheet alone. | Supply the two-sided Student-*t* tail formula, including the regularized incomplete-beta definition or enough tabulated values to reproduce the three examples. |
| C2 | nit | `docs/paper/round7/dependence-sensitivity.md:11,13,51` | Holm first appears in the generator field and “Holm rejection”; the actual ordered-p procedure is not explained until line 51. | Move or summarize the two-step Holm rule at first use. |
| C3 | nit | `docs/paper/round7/dependence-sensitivity.md:109-114` | `KEY_FROZEN` and `VALUE_UNISSUED` appear as new freeze labels without explanation. “Insertion anchor” is operationally demonstrated but the exact term is absent. | Add one sentence defining an insertion anchor and the two freeze labels. |

No untraceable delta hunks were found:

- Sheet line 9 maps to R8; line 11 to R5/R8; line 13 and lines 55/107-115 to R4/R6; line 47 to R8; lines 69-101 to R1/R7.
- Script lines 42-55 map to R1; lines 140, 204-205, 363-368 to R2; lines 438/450 to R3.
- Test imports/helpers/refusal restructuring map to R2/R3; the golden rewrite to R1/R7; the floor-boundary adjustment to R2.

First-use audit:

| Term | Result |
|---|---|
| \(n_{\mathrm{eff}}\) | Defined at line 11. |
| \(\hat\rho\) | Built by the description and formula at lines 41-45. |
| AR(1) | Expanded and explained at line 41. |
| halving | Named and operationally defined at line 49. |
| \(V\) | Defined at line 11. |
| Holm | Late definition; C2. |
| \(m=2\) | Glossed as a two-comparison family at line 11. |
| direction gate | Defined and fenced at line 13. |
| STOP_FILL | Defined at line 107. |
| DERIVE | Explained in each row at first use. |
| freeze label | Labels present but unglossed; C3. |
| insertion anchor | Exact term absent; mechanism present, with A2’s two wrong lines. |
| \(\lfloor x\rfloor\) | Correctly glossed at line 47. |

## Replication attempt

From the displayed deltas, the mean is \(50/10=5\). The centred values are:

\(0,\ 2.6,\ 0.5,\ -0.8,\ -0.3,\ 1.8,\ 0.5,\ -1.4,\ -1.1,\ -1.8\).

Their squared sum is:

\(0+6.76+0.25+0.64+0.09+3.24+0.25+1.96+1.21+3.24=17.64\).

Therefore:

\(s=\sqrt{17.64/(10-1)}=\sqrt{1.96}=1.4\).

The nine adjacent products are:

\(0+1.30-0.40+0.24-0.54+0.90-0.70+1.54+1.98=4.32\).

The preceding-value squared sum is:

\(0+6.76+0.25+0.64+0.09+3.24+0.25+1.96+1.21=14.40\).

Hence:

\(\hat\rho=4.32/14.40=0.3\).

Using the sheet’s finite-\(n\) formula, the unrounded AR terms are:

\(0.27,\ 0.072,\ 0.0189,\ 0.00486,\ 0.001215,\ 0.0002916,\ 0.00006561,\ 0.000013122,\ 0.0000019683\).

Their sum is \(0.3673473003\), so:

\(V=1+2(0.3673473003)=1.7346946006\rightarrow1.734695\),

and:

\(n_{\mathrm{eff}}=10/1.7346946006=5.7647034795\rightarrow5.764703\).

The three statistics follow from the sheet:

- Independent:  
  \(\mathrm{SE}_{total}=\sqrt{1.4^2/10+0.2^2}=\sqrt{0.236}=0.4857983121\);  
  \(t=5/0.4857983121=10.292337120\rightarrow10.292337\).

- AR(1):  
  \(\mathrm{SE}_{repeat}^2=1.4^2V/10=0.3400001417\);  
  \(\mathrm{SE}_{total}=\sqrt{0.3400001417+0.04}=0.6164415152\);  
  \(t=5/0.6164415152=8.111069544\rightarrow8.111070\).

- Halving:  
  \(\mathrm{SE}_{total}=\sqrt{1.4^2/5+0.2^2}=\sqrt{0.432}=0.6572670690\);  
  \(t=5/0.6572670690=7.607257743\rightarrow7.607258\).

To obtain the printed p-values I had to import a formula absent from the sheet:

\(p=I_x(\nu/2,1/2)\), where \(x=\nu/(\nu+t^2)\).

That external step gives:

- \(\nu=9,\ x=0.078307034361\): \(p=0.000002813760\rightarrow0.000002814\).
- \(\nu=4,\ x=0.057315253936\): \(p=0.001256213762\rightarrow0.001256214\).
- \(\nu=4,\ x=0.064651302005\): \(p=0.001602484162\rightarrow0.001602484\).

Thus \(s\), \(\hat\rho\), \(V\), \(n_{\mathrm{eff}}\), and all three \(t\) statistics are reproducible from the sheet alone; the p-values are not.

## Residual risk

The full repository suite was not run because the read-only sandbox has no writable shell temporary directory. The focused module completed all 11 tests successfully. The worktree remained clean; no measurement ran and Claude was not called.

VERDICT: **REFUTE** — R7’s promised replication command is broken at the committed head, and the surviving anchor and mutation gaps show that the round does not yet enforce R1–R8 structurally.