# Paper H — Sol fix round 1

Date: 2026-09-04. Branch: `feat/2026-09-04-paper-h`. Exact starting HEAD:
`f115b00a`. The worktree started clean. No commit was requested or made.

## Finding → cure → line

| Finding | Cure | Final line |
|---|---|---:|
| FACT-01 | Replaced the unsupported claim that JouleWise controls physical edge times. The paper now says what the harness records: command timestamps for GPU pulses whose physical onset is observed in the power record. The following sentences continue to distinguish commanded times from the edge positions allowed by the pulse records. | 74–80 |
| PED-01 | Built the monotonic clock at its first reader-facing use as a counter that advances but is never corrected to civil time. | 87–90 |
| PED-02 | Built a component from observations before naming it: repeated phase-energy measurements of one model yield spread after subtraction of their mean; a four-run comparison subtracts the A-run phase energies from the B-run phase energies and divides by two; JouleWise bounds each source separately, and only then calls each source a component. | 96–106 |
| PED-03 | Assigned both symbols when introduced: `U_cmp,point` is the four-run comparison's recorded-edge limit, while `U_cmp,shared` is its largest limit after replaying one calibration-error sign across all blocks and choosing one local sign per block. The quotient is then named the shared-error ratio. | 116–128 |

## Preservation checks

- The skeleton retains all 140 `[FILL:...]` markers.
- Every Abstract, Discussion, and Conclusion `OUTCOME-BRANCH` group is outside
  the changed hunks and remains untouched.
- The first-use ledger remains exact at `Terms inventoried: 266; FAILS: 0.`
- No result value or outcome-dependent prose was changed.

## Verification

Only the two preflight-authorized modules were run. The first ledger attempt
identified that the rewrite had dropped its exact required phrase, “shared
movement uses a different numerator.” The phrase was restored in the physical
definition sentence before the final passing replay.

```text
$ R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_first_use_ledger
..........
----------------------------------------------------------------------
Ran 10 tests in 1.732s

OK
```

```text
$ R7F_CORPUS_ROOT=/Users/edr/code/JouleWise PYTHONDONTWRITEBYTECODE=1 python3 -m unittest tests.test_paper_terms_lint
...
----------------------------------------------------------------------
Ran 3 tests in 1.389s

OK
```

## Residual risk

The two authorized modules enforce ledger placement and the standing terms-lint
contract; the lead still owns the final prose review and any broader suite.
