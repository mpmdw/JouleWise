# Magistrate terminal review — paper desk contracts S1 + S6 + S7 (interactive magistrate, 2026-09-08 ~11:20 PDT)

Merge candidate: integration branch `int/2026-09-08-paper-s1-s6-s7` (main + feat/2026-09-08-paper-S6 +
feat/2026-09-08-paper-S1 + feat/2026-09-08-paper-S7), head named in the PR ledger row 12. Docs and tests only: two
NEW contracts (`docs/contracts/paper_comparison_rendering.md`, `docs/contracts/paper_comparison_placements.md`), a
proposal appendix in `docs/contracts/paper_supply_custody.md` and `docs/paper/results-fill-registry.md` (additions
only; every retired row byte-identical; the live custody-bound census still EMPTY), the successor migration
inventory and refreshed active guidance (S7), and four new test modules with agreement/counterfactual regressions.
No production code, no paper text, no selector, no supply-map role, no grant, no issuing authority.

## Why
Ed's standing order is to run the experiments and finish the COMPARISON paper. The crosswalk scout (trace 75)
mapped every prospective-protocol obligation (X1–X22) to artifacts, producers and windows and found no production
supply role, no successor placements, and stale A/B/REFUSAL guidance. S1/S6/S7 are the desk increments that can
exist before any data: WHERE each comparison result will be placed and under which custody family (S1, 66
proposed placements, non-fillable pending adoption), HOW the renderer must behave and refuse (S6, typed contract
with executable non-issuing fixtures over the D-168 8+4 census), and WHAT active guidance says today (S7:
METHODS_DIAGNOSTIC; migration inventory of every parked obligation).

## Gauntlet record
| Lane | Seat | Reports | Unique catches |
|---|---|---|---|
| S6 | Astra medium (96) → Opus contract (98) → fix (99m) → Astra delta (99v) → bench cures | F1 families unnamed, F2 retired D-165 vocabulary, F3 D-168 census absent, F4 first-use failures (Opus); clearance gloss placement + DS-33 gloss (delta) |
| S1 | Astra medium ×2 (99f, 99l; the crosswalk had to be supplied by absolute path — brief-writer defect, mine) → Opus contract (99o) → fix (99x) → Astra delta (99ab) → bench | O1 stale "incomplete" note, O2 unconstrained safety columns, O3 S6 token families unnamed (Opus); O4 citation unresolvable → trace 75 added to the branch (delta) |
| S7 | Astra medium (97) preparation increment | none; final reconciliation waits on adoption of S1/S6 (recorded NEEDS_RULING, answered: wait) |

Same-signature statement: each delta found only residue of the same finding list; no class survived two rounds.

## Lead triage
- S7's reconciliation NEEDS_RULING: wait for adoption; the preparation increment lands now because it changes only
  active guidance to the true current state and adds an inventory + tests.
- The two contracts are PROPOSALS. Adoption (S1 placements activated, a characterization family, the S3 claim-side
  quantity semantics) needs rulings the brief-writer packaged as packets (trace 90 §ruling packets); those go to a
  cold gate before any issuing renderer or supplier gate exists. Nothing in this PR can issue.
- Ordering for the rest of the paper desk lane: S2 (reported-energy supplier) → S4 → S5, sequential because they
  share supply_map.json, the registry, paper_custody.py and the custody contract.

## Apex reading gate (docs + tests)
1. Custody seam: both contracts route every future empirical input through `open_paper_input` roles; the S1
   appendix and the custody contract's proposal section are outside the live census (test-enforced: an injected
   live row fails). No sixth family; characterization marked as having none.
2. Vocabulary: no "dominance", no "shared-error"; D-165 addendum wording; D-168 8+4 census; D-166 two exhausted-ladder
   refusals; F+B expanded from `planning_sizing_expression`; Holm members named.
3. Tests: three-table agreement (placements ↔ registry appendix ↔ custody projection) with 264 counterfactual
   subtests plus synchronized-deletion/reclassification checks; S6 fixtures are in-memory, `SYNTHETIC_NON_ISSUING`,
   and reject issuance/prose/binding claims; the six counterfactuals use named rules.
4. Overbuild: triple maintenance of the placement table is deliberate (it is the agreement check) and fenced.

## Live verification (lead-owned)
Bench, unpiped on the integration head: `tests.test_paper_comparison_contract tests.test_paper_comparison_placements
tests.test_paper_successor_migration tests.test_docs_freshness` → OK, rc 0; the fallback validator
`select_outcome_branches.py --check-rendered` → METHODS_DIAGNOSTIC validated; `gen_state.py --check` rc 0. Full-suite
replay: ledger row 9 names the log and tail.

## Verdict
LAND after CI is green on the final head and the replay tail is recorded.
