# PR #488 gate record: rebalance CI shards from hosted timings, 6 to 12 shards

Branch `ci/2026-10-05-rebalance-12-shards`, off main `1b4eadc6`. Approved by Ed on 2026-10-05 ("approve"); built by an Opus 5.5 agent; records by the interactive orchestrator (session 0a4039c8).

## What it fixes

One ordinary CI shard kept taking about 39 minutes. `tests.test_controller_g2b_attachment` costs about 875 s on the hosted runners but had no timing weight, so the scheduler priced it at 40.5 s. This PR:
- re-weights every module from the median of five hosted runs;
- splits that module into its heavy test plus a remainder unit;
- goes from 6 to 12 ordinary shards;
- removes the CI steps that only asserted the exclusive jobs' own timing numbers.

CI wall time on this head was 17 minutes, against 26-45 minutes on today's main runs.

## 1. Independent executing review

Reviewer: an Opus 5.5 agent, not the author. **REVIEW: PASS.**
- It ran the CI shard step's own code for the old 6-shard and new 12-shard layouts and resolved every unit to test ids. Both layouts execute the same 7,769 tests: none missing, none duplicated.
- The g2b split's two halves passed when run concurrently.
- Deleting the removed timing loop leaves all six old partitions byte-identical.

| Severity | Finding | Disposition |
|---|---|---|
| Medium (outside the diff) | Branch protection requires only shards 1-6, so after merge a red shard 7-12 would not block a merge. | Fixed at merge: `test (3.13, 7)` to `test (3.13, 12)` are added to the required checks right after the merge. Not before, because open PRs branched earlier would wait forever on checks they never run. |
| Low | The split changes in-process test order within the module. | Accepted: no class- or module-level state found, and module order inside a shard changes with every rebalance anyway. |

## 2. Whole suite on the merged tree

Main had not moved past `1b4eadc6`, so the head is the merged tree. Run locally with the shard method on `6f3218a2`; tails in `suite-ci12-summary.txt`.
- **Under load:** 3 failures, the load-timing tests in `test_sample_quiet_predicate_evidence`, which this PR does not touch.
- **Rerun alone:** `OK`.

## 3. Cold final pass

N/A: no measurement, calibration or claim code changes.
