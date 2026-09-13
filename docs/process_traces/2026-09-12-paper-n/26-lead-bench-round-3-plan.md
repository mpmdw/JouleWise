# Lead bench plan — round 3 candidates (pending cold-gate ruling 24 + Opus refuter 25)

Applied ONLY if the cold gate rules Q1 = (a). Each item is one sentence/clause or one regex; no new
numeral, no move, no SVG edit. Source: record 21 §4 (Opus pedagogy delta 2) and record 22 (Astra fact
delta 2). Replacement texts are taken from the ruling where it corrects them.

| # | Source | Site | Edit |
|---|---|---|---|
| 1 | 21 NB2-1 | §3 ~197 | "…at least doubles each component's source of false difference — the apparent energy difference produced by runs that differ in no condition" |
| 2 | 21 NB2-1 | §3 ~218 | "A cell has two false-difference components, and their spread is enlarged into a threshold a model comparison must exceed." |
| 3 | 21 SF-1 | Figure A4 caption ~514 | "the cases in Table A4 (Appendix A.3.10; the figure's note calls it Table 4)" |
| 4 | 21 SF-2 | §4 ~550 F7 sentence | "…; the separately retained largest pulse residual is a different quantity, computed and stored separately (Appendix A.3.6) and given below." (literals untouched; checker regex must still match) |
| 5 | 21 SF-3 | §1 ~108 | "built from repeat energies after each is expressed as its difference from their mean" |
| 6 | 21 SF-4 | §2 ~150 | Huber gloss parenthesised: "sums Huber scores (squared for small differences, proportional for large ones) of the differences…" |
| 7 | 21 SF-5 | first-use ledger row 95; lexicon rows 65/130 | gloss column quotes the restored text; lexicon build quotations refreshed to the draft's wording |
| 8 | 21 N-1 | §4 ~658 | "(a worked example, not a measured window bound)" |
| 9 | 21 N-2 | §4 ~572 | "Their medians are +13.0 ms and −5.5 ms" |
| 10 | 21 N-3 | §1 ~41 | "That sampler emits one record reporting average power between recorded start and end times." (optional) |
| 11 | 21 N-4 | §3 ~241 | "linked at the end of this section" |
| 12 | 21 N-5 | §1 ~110 | "JouleWise bounds each floor separately" |
| 13 | 21 N-6 | Figure 2 caption ~589 | "…is distinct from the edge allowance — the largest endpoint displacement in an accepted region, …" |
| 14 | 22 R2-1 | scripts/check_paper_replay_fence.py ~174 + tests/test_check_paper_replay_fence.py | regex accepts EITHER prefix ("largest pulse residual before the anchor term is " OR "Subtracting the two printed bounds gives ") with the exactly-one-match check kept; regression test extracts the committed docs/paper/draft-v1.md alongside the current draft |
| 15 | 22 R2-2 | lexicon row 23 + protected tuple | split homes inside the row: reservation plan §2; the remaining constructions A.4 |

Acceptance after the edits: the round-1 acceptance list (record 12) + `tests.test_check_paper_replay_fence`
+ `scripts/check_paper_replay_fence.py --literals-only` on BOTH drafts + first-use ledger test + terms lint;
abstract ≤ 250; HTML comments 15/15 identical; replay-fence and round-7 census unchanged.
