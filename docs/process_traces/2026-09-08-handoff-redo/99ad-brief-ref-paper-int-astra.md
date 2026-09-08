WRITE_SCOPE: []

# Final-head fresh-eyes review — paper desk contracts integration (S1 + S6 + S7) (gpt-6-astra, read-only)
HEAD = int/2026-09-08-paper-s1-s6-s7 (main + three branches). The reviewed heads were S6 89384243 and S1 b6d700e5;
AFTER those reviews two small commits landed: S6 98c9c0f9 (bench: clearance/shortfall glossed at first use in the
S3-dependency paragraph; DS-33 glossed as "the prefill claim-floor slot whose token stays unresolved until its G2-a
binding exists") and S1 d28b760b (trace files 75 and 90 added so the provenance citation resolves). Also the three
branches were MERGED here for the first time. Check: (1) `git diff 89384243 98c9c0f9` and `git diff b6d700e5 d28b760b`
are exactly the described changes, nothing else; the DS-33 gloss agrees with `grep -n '^| DS-33' docs/paper/results-fill-registry.md`;
(2) merge integrity: the three branches touch disjoint files except docs/paper/round7/fill-checklist.md (S7) vs
main (iCloud lane addendum) — confirm no conflict residue (`grep -rn '^<<<<<<<\|^=======$\|^>>>>>>>' docs`) and that
both S7's guidance edit and main's dated addendum survive; (3) run `tests.test_paper_comparison_contract
tests.test_paper_comparison_placements tests.test_paper_successor_migration tests.test_docs_freshness
tests.test_paper_terms_lint` and the fallback validator; (4) S1↔S6 agreement after both fix rounds: the four floor-slot
token families named identically in both; the D-168 census wording identical; (5) any [FILL:…] token or retired-row
byte change vs main (`git diff main -- docs/paper/results-fill-registry.md | grep '^-'` must be empty). Report
(genre review): `verdict` = {counts, findings}; header < 8192 bytes.
