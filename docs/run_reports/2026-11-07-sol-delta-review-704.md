# PR #704 Sol delta-review handoff — 2026-11-07 PST

Branch: `b5rel/2026-11-08-sol-delta-704` (already selected and clean at intake).
Reviewed code head: `bea480f296e5c7bc77ad1684936f2b257801f597`.
Range: `337e74b59..bea480f29`; no production edits.

Verdict: **ADMIT_WITH_FIXES**. The full findings, authority comparisons,
uncertainties, test commands/counts and next steps are in
[the delta review](../analysis/b5/reviews/sol-delta-review-704.md).

- The mapped diagnostic-copy fix and original refusal witnesses pass.
- Exempt metadata copies can still diverge with comparator exit 0.
- The comparator requires aggregate metadata that the actual producer correctly
  omits on a refused combined floor, using synthetic inputs.
- Exact threshold equality can accept an incorrect label; the lead must resolve
  the broader DLE-5 permission against the existing RC-CMP-11 rule.
- All 336 requested tests pass. Added synthetic witnesses record the remaining
  issues with expected-failure annotations; the mapped-leaf mutation sweep passes.
- Standard-library/hash independence holds. The real recompute emits the four
  required terms on its computed records. No native/Metal check is added.

Only the review, this handoff pointer, and the new review-test module are written.
The explicit brief overrides normal coordination bookkeeping: no `RUN_STATE.md`,
`TASK_QUEUE.md`, state kernel, or `tests/test_gen_state.py` edit and no kernel task.
No real custody, external data, network, measurement pipeline, model download,
full suite or running job was accessed. Local commit only; no push.

Lead next step: disposition and fix the two implementation gaps, rule on the
threshold exception, audit the witnesses, rerun targeted checks and obtain the
required delta review before any separately authorized release action.
