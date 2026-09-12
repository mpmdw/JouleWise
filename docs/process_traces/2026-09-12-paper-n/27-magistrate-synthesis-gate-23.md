# Record 27 — magistrate synthesis of cold gate 23 and the round-3 bench landing

Seats: cold Fable judge (record 24, doctrine-free worktree at e3285e67, ~5 min) and Opus contract-lens
refuter (record 25). Both chose Q1 = (a) lead bench edit then land; both found the false-difference
regression real (Q2); both said revert nothing (Q4); both refused the lexicon base-row edit in record 21
SF-5 (rows 65/130 are a generated draft-v1 excerpt). The magistrate accepts all of that.

## Where the seats differed and what was applied

| Item | Judge 24 | Refuter 25 | Applied |
|---|---|---|---|
| NB2-1 term gloss (§3 ~197) | parenthesis, "an energy difference that appears between runs of the same model under the same condition, where the true difference is zero" | parentheses, no new bold | judge's text |
| NB2-1 why (§3 ~218) | "and their spread is enlarged into a threshold…" | "their spread" ambiguous → "the spread of each" | "components; the spread of each is enlarged into a threshold a model comparison must exceed" |
| N-6 (Figure 2 caption) | "distinct from the edge allowance it yields:" | drop N-6 ("edge allowance" collides with "per-edge allowance") | "distinct from the allowance it yields:" — antecedent supplied, no new term |
| N-3 | rejected | dropped | not applied |
| SF-2 (F7 sentence) | same quantity, two computations; "printed below" | same correction | judge's text |
| SF-3 ("centered") | keep the word, gloss it | — | judge's text |
| Q3 clause | ratify with amendment; home = first-use ledger header | amend: mechanical arms (deleted-build grep; rename grep over docs/paper/) + prescribed-text rule | merged text installed in the ledger header (both arms + prescribed-text rule) |

Also applied from record 22 (Astra fact delta 2, outside the packet, same shape): R2-1 — the replay-fence
regex accepts either subtraction prefix with the exactly-one-match check kept, plus a regression test that
extracts the committed frozen `docs/paper/draft-v1.md`; R2-2 — lexicon row 23 split homes (reservation
plan §2; the rest A.4) with the protected tuple updated.

## After-edit text the judge required quoted

- 108: The absolute floor is built from centered repeat energies (each repeat energy taken as its difference from the mean of the repeats), the comparative floor from same-model block differences, and a science contrast is a difference between two models; Section 3 g

- 110: JouleWise bounds each floor separately, and no floor value is published in this paper.

- 150: A pulse must rise at least 10 W above resting power and have pulse height/σ ≥ 10. Its fit loss — the dimensionless score of Appendix A.3.5, which sums Huber scores (squared for small differences, proportional for large ones) of the differences between predicte

- 197: component's source of false difference (an energy difference that appears between runs of the same model under the same condition, where the true difference is zero). Let \(U_{\mathrm{point}}\) be a component bound calculated

- 218: A cell has two false-difference

- 219: components; the spread of each is enlarged into a threshold a model comparison

- 241: energy at its recorded value. The later factor is the **small-sample

- 514: The lower rows apply one shared sign and one local sign per block, enumerate

- 572: onset lags are all positive; 49 of 59 offset lags are negative, eight positive,

- 589: bottom shape legend and notes name those marks and the late/early counts.

- 590: The leader at pulse index 9 marks its +27-ms best-fit onset. The accepted region defined in Section 2

- 658: in the retained a10 sample described below (DG-071). A per-edge allowance of a

- 550 (F7 sentence): - ledger row 95: 105:| false-difference components / false-difference | 3. How the method quantifies assigned-energy sensitivity | glossed-at-first-use | The doubling question glosses a false difference at first use as an energy difference that appears between runs of the same model under the same condition, where the true difference i

## Bench acceptance (lead, venv Python 3.13.1, R7F_CORPUS_ROOT=/Users/edr/code/JouleWise)

- `tests.test_paper_replay_fence tests.test_check_paper_replay_fence`: Ran 23 tests OK (includes the new
  `test_frozen_v1_draft_still_extracts`).
- `check_paper_replay_fence.py --literals-only` on draft-v2-skeleton.md and on draft-v1.md: INTERNAL MISMATCHES 0 (both).
- `select_outcome_branches.py --check-rendered`: METHODS_DIAGNOSTIC validated; abstract_words=245, limit=250.
- `check_markdown.py`: Exit 0.
- `tests.test_paper_first_use_ledger tests.test_paper_terms_lint tests.test_select_outcome_branches
  tests.test_paper_successor_migration tests.test_paper_round7_artifacts tests.test_paper_build
  tests.test_paper_rendering tests.test_paper_comparison_placements`: Ran 143 tests in 466.355s OK.
- `check_paper_replay_fence.py --corpus-root /Users/edr/code/JouleWise`: COMPARED 43 / MISMATCHES 0.
- HTML comments in the draft: 15 (unchanged).
