# DOC-008 Sol Terms Restore Report

Date: 2026-09-04  
Branch: `feat/2026-09-04-fan-doc008`  
Required starting commit: `01e4730226f3e39ccc29c0808e39187da80ec8b8`

## Authority And Scope

The starting commit matched exactly. The final section of
`docs/process_traces/2026-09-04-fanout/01-magistrate-rulings.md` withholds
DOC-008 sign-off only until plain-language definitions return to the compacted
advisor page; it accepts the compaction itself. This seat changed only
`PROJECT_STATUS.md` and this authorized trace file. The pre-existing untracked
`docs/process_traces/2026-09-04-fanout/doc008/05-delta-reaudit-round-1.md` was
preserved without modification.

## Change

Restored a compact “Terms used on this page” block near the top of
`PROJECT_STATUS.md`, drawing its meanings from the pre-compaction glossary and
adjusting them to the current campaign state. The block defines frozen,
prospective, admitted, gate, governed, measurement window, run bundle, pack,
detection floor, and the other specialist terms still used on the page.

The glossary is plain text rather than an additional level-two section, so the
accepted seven-section compaction remains intact. Nearby insider shorthand was
also expanded: the four-run model order and transaction-opening rule are now
stated in plain words, decision identifiers are labeled by purpose, and the
Apple model and measurement-tool names are explained. The page uses capstone
terminology throughout. Its non-table prose contains 1,392 words under the
contract's 1,400-word ceiling.

## Verification

Command:

```text
python3 -m unittest tests.test_docs_freshness
```

Green output:

```text
.............................
----------------------------------------------------------------------
Ran 29 tests in 0.860s

OK
```

No commit was created.
