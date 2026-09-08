WRITE_SCOPE: ["docs/contracts/paper_comparison_placements.md","docs/contracts/paper_supply_custody.md","docs/paper/results-fill-registry.md","tests/test_paper_comparison_placements.py"]

# Fix-round brief — PAPER-S1 placements spec, Opus review findings (gpt-6-astra, medium)
HEAD = 37e5a429. Opus review (read it at the absolute path
/Users/edr/code/JouleWise/docs/process_traces/2026-09-08-handoff-redo/99o-ref-paper-S1-opus-contract-review.md):
LAND-WITH-FIXES. Cure O1-O3 (required) and O4-O6 (cheap):
O1 `docs/paper/results-fill-registry.md:56-60` — the part-1 note still says the proposal is "incomplete" and
"X1-X22 mappings await the lead's authoritative crosswalk"; rewrite it (dated) to state the proposal is COMPLETE
(66 rows, appendix at line ~1156) and NON-FILLABLE pending adoption.
O2 `tests/test_paper_comparison_placements.py:110-138` — constrain the `Applicability` and `Missing evidence`
columns to a closed vocabulary (enumerate the exact strings used today; any other value fails), and add them to
the custody-mirror projection so a permissive rewording of 49 rows cannot pass; counterfactual: flip one row's
"STOP_FILL; …" to permissive wording → fail.
O3 `docs/contracts/paper_comparison_placements.md:59-63` — the S6 contract (sibling branch: `git show
feat/2026-09-08-paper-S6:docs/contracts/paper_comparison_rendering.md`) names four floor-slot token families
(`TERMINAL_REFUSAL_REASON_*`, `NO_EXACT_FLOOR_REASON_*`, `AVAILABLE_DIAGNOSTIC_CLAUSE_*`, `POINT_DIAGNOSTIC_CLAUSE_*`)
and declares S1 the owner of successor token names; name them in the X4 site cells (or state explicitly, in both
the X4 rows and the reading rules, that S1 defers them to S6's adoption step — choose the option that keeps the
two contracts in agreement and say why).
O4 replace the unresolvable provenance citation with the repo path
docs/process_traces/2026-09-08-handoff-redo/75-scout-paper-crosswalk-astra-report.md. O5 do not hard-code the X1
candidate family in the test as if adopted (assert it is marked UNRESOLVED-grant/candidate). O6 escape the literal
`[FILL:…]` tokens in the registry appendix so no fill-pattern scanner can trip on them.
Acceptance = `tests.test_paper_comparison_placements tests.test_docs_freshness` to a log with rc; no `git commit`;
never the repository-wide suite; header < 8192 bytes; genre implementation verdict keys.
