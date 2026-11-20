# 2026-11-20 · Dated transfer authority and accounting

Tier 2, fixture-only. Signing target none. Draft PR [#911](https://github.com/mpmdw/JouleWise/pull/911) targets `audit/2026-11-10-fable`. Mission M0 selected this lane from the direct brief. The state kernel had no active stop card. Item 481 and the current pointer authorize separate magistrate work.

| Ref | Commit |
| --- | --- |
| Untouched audit base | `eaaa1fd560cd457f4e4ccef316be62af920d08e1` |
| Original executable acceptance freeze | `5e43ddc25c6e2e8485d540c580449214e6a6e117` |
| Original authority-order implementation | `cc51b0d84b86f32f18028f62db9d9bf678f601e3` |
| RL-193 acceptance freeze | `f7a318ac1eb73d495ee6a09cde01b538812200f4` |
| RL-193 implementation | `ea754a861d9e1c0154fe43d66bd99c50ba362a37` |

The published head includes this report as its last commit. Resolve that commit with `git log -1 --format=%H -- docs/run_reports/2026-11-20-transfer-date-authority-order.md`. PR #911 records the published head and links to its CI.

## Acceptance freeze and implementation

The freeze commit added only `tests/test_dated_issue.py`, with the two implementation paths absent on the untouched audit base. The audit-head command therefore failed to import `date_rules`. Repeating it with the exact historical `date_rules.py` from `4e5c2ad1d` on `PYTHONPATH` exercised the defect. With the invented 00:05 transfer stamp, effective freeze at 00:10 and W1 t0 at 01:00, the historical reader returned place 1 as **served**. It also returned date maps for both crossing fixtures. Those three tests failed their assertions. Four historical date tests passed, and the remaining test cases reported 57 errors (including subtests) because `issue_gates` was absent. The freeze commit message records those results.

All rows below map to implementation commit `cc51b0d84`. Every test name refers to the frozen `test_dated_issue.py`.

| Finding or settled rule | Frozen regression | Result |
| --- | --- | --- |
| Early or refused transfer spent a place after later same-date W1 | `test_0005_refusal_cannot_be_served_by_0100_w1`, `test_early_and_refused_child_records_spend_no_place` | PASS |
| Structural W1/C/T actual starts, post-t0 abort, shared same-date starts, before-freeze filter and proven next-date substitution | `test_actual_w1_c_t_starts_and_post_t0_abort_supply_distinct_dates`, `test_same_date_closed_windows_share_a_place`, `test_wholly_pre_freeze_date_is_excluded`, `test_unserved_rollover_needs_close_and_deduplicates_close_date`, `test_validated_start_on_original_date_prevents_rollover` | PASS |
| Both public freeze routes and fresh registration, ledger and single-issue date authority | `test_both_public_freeze_routes`, `test_unknown_or_ineffective_public_freeze_refuses`, `test_fresh_registration_and_its_main_ledger_are_required`, `test_fresh_date_authority_and_single_issue_identity_are_required` | PASS |
| Exact predecessor and proven close, queue digest and issue binding, immutable child identity and bounds | `test_known_latest_predecessor_and_exact_close_are_required`, `test_queue_digest_and_selected_span_binding`, `test_original_child_bounds_and_started_stamp_are_required`, `test_receipt_must_match_the_issued_span_kit_pin_and_order`, `test_all_lower_authorities_apply` | PASS |
| Inclusive exact lower and exclusive midnight, with a late transfer close allowed | `test_child_exact_lower_is_inclusive`, `test_last_nanosecond_serves_even_with_post_t0_abort_and_late_close` | PASS |
| Duplicate starts, original ordinal after a miss, final-place rollover and refusal of place 21 | `test_duplicates_refuse_in_verifier_and_both_accounting_readers`, `test_miss_does_not_reseed_next_place`, `test_final_place_rolls_forward_with_one_miss_and_no_place_21`, `test_final_place_can_take_t0_on_its_verified_close_date` | PASS |

The later stage-1 owner can call `issue_gates.verify_transfer_start` with structural windows, previous verified starts, the original issue, its arm snapshot, the committed queue bytes and the pinned child's receipt projection. The frozen test's `snapshot` shows the input fields. Refresh registration and date authority at the arm observation, and supply the same resolved main commit for the public freeze and registration projections. Authenticate the public inputs, any naming ruling and the exact predecessor proof before calling. The verifier checks their bindings without I/O. The caller records a refusal on `ValueError` and passes only successful `VerifiedTransferStart` values to `date_places` and `date_dispositions`. The exact child stamp and its original bounds retain nanosecond precision. A started attempt can serve even when the receipt carries a post-t0 abort.

## RL-193 §8 resolves both held fixtures

The original freeze expected `NEEDS_SPEC` for both cases. The research lead ruled that eligibility is decided window by window and the freeze-date filter applies after close-date substitution. [RL-193 §8](https://github.com/mpmdw/JouleWise/blob/bceb204a1ec65d7ef2e815e4f929135ede868a80/docs/research-audits/2026-11-10-fable/RESEARCH-LEAD-DECISIONS.md#L23219-L23230)

The two ruled expectations were frozen at `f7a318ac1` before implementation. Both errored with `UnresolvedDateRule` on the previous draft code at `3077c689a`. The other 22 tests passed. The checker change at `ea754a861` removes the two holds and runs the existing substitution independently for each window. The remaining original expectations stayed byte-for-byte intact.

| Ruled result | Regression | Result |
| --- | --- | --- |
| W1 starts before the effective freeze date. Its verified close on the freeze date supplies place 1. An unused place 1 becomes a miss, and a transfer start must follow effective freeze. | `test_pre_freeze_w1_close_on_freeze_date_is_place_one` | PASS |
| W1 and C1 start on D, W1 closes on D, C1 holds the host at midnight, and no transfer starts on D. D spends its ordinal as a miss. C1 supplies the next ordinal on verified close on D+1, which can serve or expire as a miss. | `test_shared_start_date_misses_before_crossing_close_takes_next_place` | PASS |

Both ruling questions are closed. The existing regression for a transfer already served on D still passes. Tier 2 independent review is pending on this draft.

## Verification

The paths below are relative to the repo unless absolute. `dated` abbreviates the dated-transfer directory for these command examples.

```sh
dated=docs/research-audits/2026-11-10-fable/evidence/align-v4-campaign/dated-transfer
seat=/Volumes/JW-EXT/scratch/d-transfer-date-authority-order
git show "4e5c2ad1d:$dated/date_rules.py" > "$seat/historical/date_rules.py"
python3.13 -B -m unittest discover -s "$dated/tests" -p test_dated_issue.py -v
PYTHONPATH="$seat/historical" python3.13 -B -m unittest discover -s "$dated/tests" -p test_dated_issue.py -v
python3 -B -m unittest discover -s "$dated/tests" -p test_dated_issue.py
PYTHONPATH="$dated/tests" python3.13 -B "$seat/check_pin.py"
git diff --check eaaa1fd56...HEAD
git diff --exit-code 5e43ddc25 3077c689a -- "$dated/tests/test_dated_issue.py"
git diff --exit-code f7a318ac1 HEAD -- "$dated/tests/test_dated_issue.py"
gh pr checks 911 --repo mpmdw/JouleWise
```

The original first unittest command was red against the untouched audit base. The historical command ran before original implementation. The full 24-test focused suite passed after RL-193 on Python 3.13 and 3.14. The pinned check extracted only `runner_argv`, `validate_t0_authority` and `_authorized_start` from public source at `6e9d42f1d` into the seat scratch directory. It passed launcher argument forwarding and five invented clock boundaries without loading or running either host entry point. The audit PR runs repository CI. The focused suite runs directly because its path is outside the root test discovery directory. The full local suite was left to CI under the fixture-only input restriction.
