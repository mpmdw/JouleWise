# PR #485 gate record: paper renderers and the results-fill adapter

Branch `feat/2026-10-05-analysis-an2`, off main `e0c738e9`. Implemented by a Sol 6.1 lane; review fixes and records by the interactive orchestrator (Opus 5.5, session 0a4039c8).

## 1. Independent executing review

Reviewer: an Opus 5.5 agent, not the author. It ran the code in a copy, with 22 mutants.

- **Verdict: PASS.** Nothing in `5530fc87` prints a wrong number or a wrongly worded claim.
- **Checks run:**
  - Outward rounding was checked on 200,000 random intervals against exact binary values: no printed interval was narrower than the computed one.
  - The adapter refused every tampered or malformed verdict tried.
  - The renderers read the right fields.
- **Findings and dispositions:**

| Severity | Finding | Disposition |
|---|---|---|
| MAJOR | Printing the decision interval in the metrology slot passed the tests: the fixtures' two intervals were equal. | Fixed in `46083f7c`. The unresolved fixture, where the two differ, asserts both exactly. A mutation check confirms the swap now fails. |
| MINOR | Outward rounding on negative bounds, negative-zero normalisation and reversed intervals were untested. | Fixed in `46083f7c` with unit checks. |
| MINOR | The adapter's widening total, floor and multiplicity copies were not asserted. | Fixed in `46083f7c`. |
| MINOR | An "equivalent" outcome printed without its margin. | Fixed in `46083f7c`: prints `equivalence margin = ±m unit`. |

## 2. Whole suite on the merged tree

Main had not moved past `e0c738e9`, so the head is the merged tree. Run on `46083f7c` with the shard method (six shards plus the two exclusive modules, `/opt/homebrew/bin/python3.13`). Shard tails: `suite-an2-summary.txt`.

- **Under load:** 4 failures (`suite-an2-failures.txt`): three load-timing tests in `test_sample_quiet_predicate_evidence`, and one error in `test_arm_readiness_evidence_author`. Neither module is touched by this PR.
- **Rerun alone:** both modules, 120 tests, `OK`. The failures were contention.

## 3. Cold final pass

Fable 5.1, cold, over #485, #486 and #487 together: **FINAL PASS: PASS** (`fable-final-pass-analysis-prs.md`).

Two LOW test gaps are recorded as flags (doctrine: representation and test-gap findings are flags, not fix rounds):
- a `repeat_point_CI95` slot swap survives, because the fixtures have zero metrology error;
- floor-rounding of the claim estimate survives, because the estimates are exact at three decimals.

The head reads the correct field and rounding in both places.

## 4. Deferred

The two Fable LOW test gaps go to lane `RENDER-TEST-NONZERO-METROLOGY`, which adds a fixture with nonzero metrology error and a non-grid claim estimate.
