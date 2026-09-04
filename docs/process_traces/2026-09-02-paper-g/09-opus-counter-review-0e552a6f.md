# Opus counter-review — paper-g (gate ledger item 6)

Head `0e552a6f` on `feat/2026-09-02-paper-g`. Object: diff vs `33290b8b` over
the skeleton, fill-rehearsal/, retensing-plan.md, results-fill-registry.md.
Prior gate audited `e8f6b7ef`; the only later commit (`0e552a6f`) touches no
paper file (`git diff --stat e8f6b7ef..HEAD -- docs/paper/` is empty), so the
prior closures apply to this text.

## Executed evidence (this session)

- Selector run for all three outcomes into temp copies: `selected A:
  transfer_slots=3, failed_component_slots=0, verdict_slots=4,
  refusal_reason_slots=1` / `B: ... 3, 3, 4, 1` / `REFUSAL: ... 3, 0, 1, 4`.
- Documented post-selection assertions re-run on each copy: branch markers 0;
  each of the three bold forms present exactly once; `TR-01` = 3 in all three;
  `OB-01` 0/3/0; `OR-01` 1/1/4; `DS-32` and `PG-08` 4/4/1.
- Predicate byte-identity: `cmp -s` of skeleton:771 against retensing-plan
  lines 26, 103, 395 → all three IDENTICAL (493 bytes).
- `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest
  tests.test_paper_first_use_ledger tests.test_paper_terms_lint` →
  `Ran 6 tests in 4.103s` / `OK`.
- Abstract word counts on the selected copies: A 200, B 209, REFUSAL 195.

## Findings

| # | Sev | Site | Evidence |
|---|---|---|---|
| 1 | **BLOCKER** | skeleton:987 (§7 Refusal), skeleton:1225 (§10 Refusal) | Both carriers state the two stop stages in the **past indicative**, asserting that both happened: "The result stopped before comparison because a model-specific measurement window was excluded or an authenticated … verdict **was** absent. **It stopped at close-out because** a required ratio **was** missing, unauthenticated, or **had** a zero denominator." A run that stops before comparison never reaches close-out, so the published text asserts a contradiction, and it asserts specific reasons that only `[FILL:OR-01]` is authorized to issue. The governed form (§4:771) and the plan carriers (26/103/395) are conditional — "Refusal applies **when** …" — and the Abstract carrier is correctly conditional ("JouleWise stopped at one of two points. Before comparison, it stopped **if** …"). §7/§10 are the only two sites that drop the conditional. The plan's own §7 row (retensing-plan:395) supplies the conditional sentence for this carrier; the skeleton diverges from it. Prior gate `08` checked only that each carrier *names* "before comparison", "at close-out" and `[FILL:OR-01]` (a presence check) — the truth conditions were never read. Cure: restore the conditional mood at both sites (e.g. "The result stopped at one of two stages. Before comparison it stops when …; at close-out it stops when …"), leaving `[FILL:OR-01]` to name which. |
| 2 | SHOULD-FIX | skeleton:43 (Abstract Refusal) | The Refusal Abstract never says what JouleWise *is or did*. A and B both carry the method sentence ("JouleWise first used deliberately started graphics-processor work to measure how far the dividing time could be wrong, then recalculated …"); §10's Refusal carrier keeps its own version ("it corrects clock placement inside each collection, measures allowed edge movement …"). The Abstract Refusal goes from the physical problem straight to "JouleWise stopped at one of two points." A PC member reading only this branch learns a problem exists and that something stopped, and never learns the contribution that survives a stop. At 195 words there are ~55 words of budget. Cure: port the §10 Refusal method clause ahead of the stop sentences. |
| 3 | SHOULD-FIX | skeleton:973 (§7 branch A) | "**Because** every independent-edge ratio and every required shared-error ratio was at least 2, measurement practice **must change** before collection: …". §4's governed A form (skeleton:759) grounds that headline conditionally — it "supports the headline that boundary placement dominates point-only variation **only if** the post-campaign inserted-gap check … supports applying the pulse-derived timing bound to inference" — and §7's own Further limitations opens "the pulse-to-inference transfer is untested." The ratios are computed from the pulse-derived bound, so the unconditional imperative is exactly the claim §4 reserves. §10's A branch stays descriptive and does not repeat the error. Cure: carry §4's conditional clause into the §7 A branch. |
| 4 | SHOULD-FIX | sel-REFUSAL.md (Table 3 row 289/290); branch-selection.md; registry:882, 891 | A REFUSAL selection retains one `[FILL:DS-32]` and one `[FILL:PG-08]` (measured: `DS32=1 PG08=1`) — the Table 3 verdict cells. Neither `branch-selection.md` nor the amended DS-32/PG-08 rows say what those cells render when the stop reason *is* the absence of that verdict; both rows are `STOP_FILL`, so a downstream fill leaves two unfillable markers inside a published table. `branch-selection.md` only says a REFUSAL "carries neither verdict slot **in its three selected paragraphs**", never mentioning the surviving table slot. Cure: add the refusal-time rendering rule to both rows and name the retained table slot in the procedure. |
| 5 | NIT | branch-selection.md | No word-budget guard on the Abstract. A is 200 words with six markers; the 250-word cap breaks if the bound renderings average more than ~8 words each. Add a post-fill word check to the assertion block. |
| 6 | NIT | registry:882, 891 | DS-32/PG-08 were amended in place inside the frozen-draft census table to also govern successor-skeleton paragraphs, while the new section declares successor rows "outside the frozen-draft marker census above". Census provenance is now mixed across two regimes. |
| 7 | NIT | select_outcome_branches.py:106-131 | The global slot counts run over the whole file, HTML comments included. A future build comment mentioning `[FILL:TR-01]`/`[FILL:DS-32]` would fail selection with a misleading "selected draft lost …" message. Count over non-comment text or say so in the docstring. |

## Verified sound (no finding)

Selector determinism and refusal behavior: exactly one complete group per
section is required, the three branches must appear in order, any residue
outside branch blocks raises, both unselected branches and all markers are
deleted, and the post-run global counts are asserted — it cannot leave two
branches or none. Every `[FILL]` introduced by this diff (`OB-01`, `TR-01`,
`OR-01`, `DS-32`, `PG-08`, `DG-099/100/101`, `DG-067/068/069`) maps to a
registry row naming a supplier. `DS-32`/`PG-08` appear only as slots, each
guarded by an explicit "Independently of the ratio disposition" so no carrier
infers a verdict from the ratio outcome.

## Verdict

**FIX FIRST** — one blocker (§7/§10 Refusal carriers assert both stop stages as
past fact, contradicting themselves and the governed conditional predicate)
plus three should-fixes.
