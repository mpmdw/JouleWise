# Fable cold review: `w1-finality-tests` (RL-53 W-7, RL-54)

Reviewer: Fable 5.2, state-machine lane lead, 2026-11-11 04:20 PST. Reviewed head `ae84138a6`
(`test/2026-11-11-w1-finality-tests`, base the W1 line `b4a6c217f`). Builder: Sol xhigh, two rounds.

**Verdict: ADMIT.** Tests only, plus my correction of the harvest-off runbook. No bound file changes.

## What I did

- Read the test module (406 lines, 8 tests) against the two rulings.
- Ran `python3.13 -B -m unittest tests.align.test_v4_finality_paths` on the Air after each round: 6 tests OK,
  then 8 tests OK (79 s).
- Checked scope: `tests/align/test_v4_finality_paths.py`, one inserted line in `scripts/test_timings.json`,
  reports, and the runbook. None is in `ARTIFACTS` or the registration receipt.
- Compared each result with my own reading of `scripts/align_v4_next_arm_packet.py` recorded in the lane plan
  before the seat ran. They agree.

## Answers for the research lead

Here k is C1, k+1 is C2, k+2 is C3. "Accepted" means the packet build, the rebuild comparison, the
latest-record check, cadence triage and the series binding all accept, on synthetic records.

| Question | Answer | Test |
|---|---|---|
| A late final exclusion in window k: does the arm of k+2 deadlock? | No. Replay recovers: k is `final` and its count drops by exactly the excluded member. | `test_order1_...` |
| May a final desk raise a count above the provisional one? | No. The series binding refuses (`align_v4_series.py:611-614`). | `test_final_counts_above_desk_ceiling_...` |
| Can a record later than k+1 carry k's final sources? | No. It is refused, and k stays non-final. | `test_ACTUAL_non_successor_final_...`, `test_missing_successor_final_...` |
| Order 1: desk for k final before record k+1 is committed | Accepted. | `test_order1_...` |
| Order 2: desk final after; record k+1 re-issued while it is the chain tail | Accepted, after the series ledger is re-committed. Before that the builder refuses `series previous record binding mismatch`. The test asserts the old and new records differ only in `previous_final`. | `test_order2_...` |
| Order 3: record k+1 held until the desk for k is final | Accepted. Nothing in k+1's own triage, final receipt or arm path needs record k+1 earlier. | `test_order3_...` |
| Does any analysis-side reader take pool membership from a stored list? | None found on this ref. The four mentions of `pool_members` are one diagnostic writer, one template and the two packet checks. The counting readers use the roster's pool role and the exclusions; with a stale stored list they still drop the late-excluded member. | `test_final_receipt_and_desk_counts_recompute_despite_stale_stored_pool` |
| Can an anchor appear in the pool list? (my reading) | No. Anchors carry `role='anchor'`; the cohort check admits only `role == 'D'` ids (`align_v4_next_arm_packet.py:842-847`). | reading |

So no deadlock was found on any of the paths the audit named, and no code change is owed before signing.

## The runbook

`docs/align/v4/HARVEST-OFF-MAGISTRATE-RUNBOOK.md` section 4 said a later record may carry `previous_final`.
It now says only record k+1 can, gives the two accepted orders (hold, preferred; or re-issue), and states
RL-54's condition for a re-issue: the records are compared, the only differing key is `previous_final`, and the
commit message says so. Section 6 gains the `series previous record binding mismatch` row.

## Limits

- Synthetic records and a synthetic git repository. No installer, host, harvest or analysis pipeline ran.
- Re-issuing record k+1 after record k+2 exists was not tested and is not offered by the runbook.
- The pool-reader census covers `joulewise/align` and `scripts/align_v4_*` on the W1 line. The v4 release tools
  live on another branch and were not searched.
