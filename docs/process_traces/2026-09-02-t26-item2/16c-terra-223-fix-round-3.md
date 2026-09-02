```json
{"schema":"claude-codex-report/v1","genre":"implementation","status":"clean","completion":"complete","summary":"Implemented all dictated gate-ledger splitter, refusal, workflow, template, and regression-test closures.","workspace":{"base_requested":"ec6f97ea","base_mode":"exact","head_start":"ec6f97ea1f77dff1cdfa7d19d6e9339a4dfd511d","head_end":"ec6f97ea1f77dff1cdfa7d19d6e9339a4dfd511d","upstream_end":null,"branch":null},"pathspec":["scripts/check_gate_ledger.py","tests/test_check_gate_ledger.py",".github/workflows/gate-ledger.yml",".github/pull_request_template.md"],"unowned_dirty":[],"verdict":{"implementation":"implemented","acceptance":"ready"},"verification":[{"id":"V1","kind":"suite","cmd":"python3 -m unittest tests.test_check_gate_ledger tests.test_docs_freshness","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[".....................................","----------------------------------------------------------------------","Ran 37 tests in 1.581s","","OK"]},"expected":{"exit_code":0,"tail_regex":"Ran 37 tests in [0-9.]+s\\n\\nOK"}},{"id":"V2","kind":"smoke","cmd":"python3 scripts/check_gate_ledger.py --root . --body .github/pull_request_template.md","cwd":".","observed":{"result":"pass","exit_code":1,"tail":["gate-ledger: item 1: NOT-RUN","gate-ledger: item 2: NOT-RUN","gate-ledger: item 3: NOT-RUN","gate-ledger: item 4: NOT-RUN","gate-ledger: item 5: NOT-RUN","gate-ledger: item 6: NOT-RUN","gate-ledger: item 7: NOT-RUN","gate-ledger: item 8: NOT-RUN","gate-ledger: item 9: NOT-RUN","gate-ledger: item 10: NOT-RUN","gate-ledger: item 11: NOT-RUN","gate-ledger: item 12: NOT-RUN"]},"expected":{"exit_code":1,"tail_regex":"gate-ledger: item 12: NOT-RUN"}},{"id":"V3","kind":"lint","cmd":"git diff --check","cwd":".","observed":{"result":"pass","exit_code":0,"tail":[]},"expected":{"exit_code":0,"tail_regex":"^$"}},{"id":"V4","kind":"inspection","cmd":"git status --porcelain && git diff --stat","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["4 files changed, 303 insertions(+), 53 deletions(-)"]},"expected":{"exit_code":0,"tail_regex":"4 files changed"}}],"flags":[]}
```

## Change

Implemented F-1 through F-15 in the four authorized paths. The splitter now models only GFM backslash-parity pipe handling; ambiguous structure and inline-shaped evidence are refused. Added `--body`/`--root` aliases so the specified acceptance command is supported.

## Verification notes

Mutation checks:

- M1 restore code-span tracking: KILLED by `test_split_table_row_matches_gfm_cell_rule`.
- M2 silent malformed-row continue: KILLED by `test_extra_cell_in_numbered_row_is_named_malformed`.
- M3 remove head SHA checkout ref: KILLED by `test_workflow_text_pins_round1_fixes`.
- M4 remove permissions: KILLED by `test_workflow_text_pins_round1_fixes`.
- M5 revert to `line.split("|")`: KILLED by the `f\|oo` case in `test_split_table_row_matches_gfm_cell_rule`.

## Same-signature statement

Under L3, F-1 removes the hand-rolled inline model. F-2 through F-9 add or tighten refusal boundaries rather than model Markdown; F-10 through F-15 cover workflow, predicate-drift, template, and documentation behavior outside the cell model. Nothing remains modelled but the pipe rule: an odd backslash run escapes a pipe and consumes one backslash.

## Clause map

| Closure | Treatment | Production | Biting test | Counterfactual |
|---|---|---|---|---|
| F-1 | Removes inline modelling | [checker:19](/Users/edr/code/JouleWise-wt-t26-c2/scripts/check_gate_ledger.py:19) | [tests:195](/Users/edr/code/JouleWise-wt-t26-c2/tests/test_check_gate_ledger.py:195) | Backtick-aware splitting |
| F-2 | Refuses malformed arity | [checker:102](/Users/edr/code/JouleWise-wt-t26-c2/scripts/check_gate_ledger.py:102) | [tests:140](/Users/edr/code/JouleWise-wt-t26-c2/tests/test_check_gate_ledger.py:140) | Silent skip or truncation |
| F-3 | Refuses inline-shaped evidence | [checker:154](/Users/edr/code/JouleWise-wt-t26-c2/scripts/check_gate_ledger.py:154) | [tests:212](/Users/edr/code/JouleWise-wt-t26-c2/tests/test_check_gate_ledger.py:212) | Backticked path/SHA accepted |
| F-4 | Documents and pins pointer refusal | [template:3](/Users/edr/code/JouleWise-wt-t26-c2/.github/pull_request_template.md:3) | [tests:102](/Users/edr/code/JouleWise-wt-t26-c2/tests/test_check_gate_ledger.py:102) | `:N` suffix accepted |
| F-5 | Refuses rows outside first table block | [checker:75](/Users/edr/code/JouleWise-wt-t26-c2/scripts/check_gate_ledger.py:75) | [tests:227](/Users/edr/code/JouleWise-wt-t26-c2/tests/test_check_gate_ledger.py:227) | Numbered post-blank row accepted |
| F-6 | Refuses unrecognised keys | [checker:95](/Users/edr/code/JouleWise-wt-t26-c2/scripts/check_gate_ledger.py:95) | [tests:243](/Users/edr/code/JouleWise-wt-t26-c2/tests/test_check_gate_ledger.py:243) | `**1**` silently becomes missing |
| F-7 | Names absent ledger section | [checker:139](/Users/edr/code/JouleWise-wt-t26-c2/scripts/check_gate_ledger.py:139) | [tests:252](/Users/edr/code/JouleWise-wt-t26-c2/tests/test_check_gate_ledger.py:252) | Heading drift produces twelve missing rows |
| F-8 | Refuses non-uppercase `RUN` | [checker:163](/Users/edr/code/JouleWise-wt-t26-c2/scripts/check_gate_ledger.py:163) | [tests:264](/Users/edr/code/JouleWise-wt-t26-c2/tests/test_check_gate_ledger.py:264) | `run evidence.txt` gets generic error |
| F-9 | Uses stripped headings | [checker:64](/Users/edr/code/JouleWise-wt-t26-c2/scripts/check_gate_ledger.py:64) | [tests:273](/Users/edr/code/JouleWise-wt-t26-c2/tests/test_check_gate_ledger.py:273) | Indented summary remains ledger input |
| F-10 | Covers reopen lifecycle | [workflow:34](/Users/edr/code/JouleWise-wt-t26-c2/.github/workflows/gate-ledger.yml:34) | [tests:363](/Users/edr/code/JouleWise-wt-t26-c2/tests/test_check_gate_ledger.py:363) | `reopened` trigger removed |
| F-11 | Pins shared pointer predicate | [checker:113](/Users/edr/code/JouleWise-wt-t26-c2/scripts/check_gate_ledger.py:113) | [tests:279](/Users/edr/code/JouleWise-wt-t26-c2/tests/test_check_gate_ledger.py:279) | `_valid_path` drifts from `_check_pointer` |
| F-12 | Restricts token permissions | [workflow:40](/Users/edr/code/JouleWise-wt-t26-c2/.github/workflows/gate-ledger.yml:40) | [tests:363](/Users/edr/code/JouleWise-wt-t26-c2/tests/test_check_gate_ledger.py:363) | `permissions` removed |
| F-13 | Pins workflow safeguards | [workflow:52](/Users/edr/code/JouleWise-wt-t26-c2/.github/workflows/gate-ledger.yml:52) | [tests:363](/Users/edr/code/JouleWise-wt-t26-c2/tests/test_check_gate_ledger.py:363) | Head SHA checkout ref removed |
| F-14 | Pins template’s deliberate refusal | [template:3](/Users/edr/code/JouleWise-wt-t26-c2/.github/pull_request_template.md:3) | [tests:372](/Users/edr/code/JouleWise-wt-t26-c2/tests/test_check_gate_ledger.py:372) | Template no longer yields twelve `NOT-RUN` defects |
| F-15 | Documents deliberate initial red state | [workflow:6](/Users/edr/code/JouleWise-wt-t26-c2/.github/workflows/gate-ledger.yml:6) | [tests:363](/Users/edr/code/JouleWise-wt-t26-c2/tests/test_check_gate_ledger.py:363) | Rationale comment removed |