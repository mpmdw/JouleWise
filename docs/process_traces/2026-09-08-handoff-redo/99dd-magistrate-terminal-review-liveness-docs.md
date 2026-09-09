# Magistrate terminal review — WINDOW-LIVENESS-DOCS-01 (interactive magistrate, 2026-09-08 ~14:35 PDT)

Merge candidate: `docs/2026-09-08-window-liveness-docs`, head named in the PR ledger row 12 (docs head bb7b6ce0 + trace
commit). DOCS ONLY: a new contract docs/contracts/window_liveness.md (the registry, the chain.started marker sequence,
the identity probe, stale semantics and operator repair, the census, a complete 50-row publish decision table, a worked
example and a code map), plus pointer paragraphs in MAGISTRATE_WATCHDOG.md, NIGHT_HANDBACK.md and the G2 runsheet, and
the TASK_QUEUE row. Closes the R4 follow-up from the WINDOW-STATUS-GUARD-CENSUS-01 landing (PR #302).

## Gauntlet record (writing standard applied as its own review dimension)
| Round | Seat | Report | Unique catches |
|---|---|---|---|
| Draft (655b3368) | Astra medium | 99cg | — |
| Pedagogy + fidelity review 1 | Astra medium | 99ci | ~60 first-use failures; not rebuildable from the example; incomplete decision table; two code-fidelity overclaims (exit precedence, traversal stop) |
| Rewrite (5cf1660f) | Astra high | 99cx | self-run 79-term first-use audit |
| Pedagogy + fidelity delta | Astra medium | 99da | reconstruction PASS, 50 combinations consistent; one overbroad sentence (C5), five code-map pins, three glosses |
| Final fix (bb7b6ce0) | Astra medium | 99dc | — |

Diff ritual (Ed 2026-08-19): the original-vs-final diff shows the reader's asks forced in: physical facts before
mechanism, a real ps line, every marker state named in a timeline, the table enumerated instead of gestured at, and the
code map. The next first draft of an explainer starts from that shape.

## Lead verification
Bench rc-gated: tests.test_docs_freshness (31) OK at each commit. Lead read: the C5 sentence now matches
measurement_liveness.py:189–198 precedence; the code-map pins were re-read by the seat and spot-checked.

## Verdict
LAND after CI is green on the final head and the replay tail is recorded.
