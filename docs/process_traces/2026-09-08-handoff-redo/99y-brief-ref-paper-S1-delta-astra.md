WRITE_SCOPE: []

# DELTA RE-AUDIT — fix round 1 on the PAPER-S1 placements spec (gpt-6-astra, read-only)
HEAD = fix-round commit; HEAD~1 = 37e5a429 (Opus review O1-O6: stale "incomplete" registry note; Applicability /
Missing-evidence columns unconstrained; S6's four floor-slot token families unnamed; unresolvable provenance
citation; X1 candidate family entrenched in the test; literal [FILL:…] tokens in the registry appendix). Packet:
`git diff HEAD~1 HEAD`. Verify each cure against the source: (1) registry lines ~56-60 now say COMPLETE and
NON-FILLABLE with a date; no contradictory sentence remains (`grep -n "incomplete\|await" docs/paper/results-fill-registry.md`
around the proposal note); (2) the closed vocabulary: extract the distinct `Applicability` and `Missing evidence`
cell values from the placements table and confirm the test enumerates exactly them; flip one row's value to
permissive wording in a $TMPDIR copy → the test must fail; confirm the custody mirror projection includes both
columns and the three-table agreement still holds; (3) the four token families (`TERMINAL_REFUSAL_REASON_*`,
`NO_EXACT_FLOOR_REASON_*`, `AVAILABLE_DIAGNOSTIC_CLAUSE_*`, `POINT_DIAGNOSTIC_CLAUSE_*`) appear in the X4 site cells
or an explicit deferral statement appears in BOTH the X4 rows and the reading rules; compare with the S6 contract
(`git show feat/2026-09-08-paper-S6:docs/contracts/paper_comparison_rendering.md`) for agreement; (4) provenance path
resolves (`ls` it); (5) the X1 candidate family is asserted as a candidate with an UNRESOLVED grant, not as adopted;
(6) `grep -o '\[FILL:[A-Z0-9-]*\]' docs/paper/results-fill-registry.md | sort | uniq -c` shows each token exactly
once (the original), i.e. appendix occurrences escaped; and the retired rows remain byte-identical vs main (`git diff
main -- docs/paper/results-fill-registry.md` shows additions only); (7) `tests.test_paper_comparison_placements
tests.test_docs_freshness` rc 0; anything HEAD~1 had right that HEAD broke. Report (genre review): `verdict` =
{counts, findings}; header < 8192 bytes.
