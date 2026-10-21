# PR #501 gate record: block-6 machine-test r2 fixes (fix/2026-10-17-b6-mt2-fixes into lane/2026-10-16-b6-round2)

Commits: round 1 `0276a3327`, round 2 `021f935c8` (author Sol 6.1 xhigh via codex-run-v3; committed by the lead).
Tier: full. The change decides which block-6 runs count (busy-only runs and references are kept with a flag instead of
being excluded). Block-5 analysis is pinned elsewhere and does not change.

## Gates
1. Independent executing review: two blind executing cold passes on round 1, then an executing Opus 5.5 delta review on
   round 2, all non-authors and all running the code on the real MT-20261017T1735Z archive.
   - `pr501-cold-fable.md`: MERGE-WITH-FIXES.
   - `pr501-cold-opus.md`: MERGE-WITH-FIXES.
   - `pr501-delta-opus.md`: MERGE.
   Decision: the two blind cold passes also serve as the independent executing review (both are non-authors and both
   executed), instead of adding a third seat.
2/3. Whole suite: CI on the PR merge tree (12 shards) at the final head. Lead's local runs at `0276a3327`: 125 focused
   tests OK and 252 block-6 tests OK.
4. Cold passes: Fable 5.1 and Opus 5.5, blind to each other (row 1).
5. Dispositions:
   - Fable F1 (MAJOR, the verdict writer's raw-CPU veto): fixed in `021f935c8`. The writer now uses the shared claim
     barrier. The delta review showed that 16 of 17 constructed cores give identical outcomes; only a marked busy-only
     member changes.
   - Fable F2 / Opus F2 (MINOR, the absence predicate was widened): fixed in `021f935c8` (base predicate restored, and
     only a stage of recorded skips is exempt).
   - Opus F1 (MAJOR, wait-budget skip): fixed in `021f935c8` (`recorded_idle_skip` covers both the cap and the budget
     skip, each as a flag plus its matching skip_reason).
   - CI quick-tier failure (`test_b6_busy_fraction_desk`, a stale expectation): fixed in `021f935c8`.
   - Fable NITs (redundant evidence-condition set; conditions list trusted over watts, as on base): rejected, because
     neither changes an outcome (both cold passes constructed the cases).
   - Opus F3 NIT (an inconsistent GPU shape the evaluator never writes): rejected, because real data cannot reach it.
   - Opus F4 / delta N2 (an unused `files_missing` field; a pending `executing_reviews.json` row): the review row is
     filled at the lane merge; `files_missing` is deferred to the block-6 follow-up lane as cleanup.
   - Delta N1 (the barrier trusts the core's copy of the final attempt; the validator re-reads it from the bundle):
     rejected under D-161, since only an operator-level edit could exploit it.
   - Delta N3 (a skip that also lost its summary stays exempt): accepted as physically correct, no change.

## Machine-test replay (desk only, real archive, fixed code)
Both succeeded members return no admission refusals, acceptance has no structural failure, and the smoke classifies
`physics`. A live re-run of the machine test at the new pin is still required.
