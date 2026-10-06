# PR #487 gate record: per-producer floor binding (memo items 4.1 and 4.2)

Branch `feat/2026-10-05-analysis-an1`, off main `e0c738e9`. Implemented by a Sol 6.1 lane in two rounds; the supply-map repin and records are by the interactive orchestrator (Opus 5.5, session 0a4039c8).

## 1. Independent executing review

Reviewer: an Opus 5.5 agent, not the author. It ran attacks against the real v2 mint and `load_analysis_inputs`, plus mutants.

**Verdict: PASS.** Every cross-producer attack bound zero cells or was refused:
- plan bytes, order manifests and evidence roots swapped between producers;
- a real 8B bundle moved into a 1.7B cell and re-tagged;
- the producer set reordered;
- a tampered plan file.

Pre-v2 and folded binding decisions were byte-identical to main across 23 cases.

Findings and dispositions:

| Severity | Finding | Disposition |
|---|---|---|
| MINOR | Several layered v2 checks can each be removed singly without a test failing; another layer still refuses every attack. | Deferred to lane `AN1-TEST-ISOLATION`: one test per link. |
| MINOR | Both fixture producers share bundle and calibration-cell ids. | Deferred to `AN1-TEST-ISOLATION`: distinct ids for the 8B producer. |

Round 1 (`2d3329e0`) regressed folded-artifact binding; two existing `test_analysis_claims` tests bound no cells. That was caught by the orchestrator before review and fixed in round 2 (`9d245b07`): all `tests/test_analysis_*` files pass, 322 tests and 434 subtests.

## 2. CI quick-tier failure and repin

CI's quick tier failed on `stale supply-map receipt digest`. `paper_custody` hashes the claim-side validator source into the test-fixture receipts, and the binder change altered that hash. `e40c8cba` repins only the four fixture `expected_sha256` values. The paper custody, rendering and reported-energy tests pass: 65 tests, 451 subtests. Fable confirmed these are the hashes the custody gate computes with all three analysis PRs present.

## 3. Whole suite on the merged tree

Run on `e40c8cba`; main is still `e0c738e9`. Shard tails: `suite-an1-summary.txt`.
- **Under load:** 3 failures (`suite-an1-failures.txt`), the load-timing tests in `test_sample_quiet_predicate_evidence`, which this PR does not touch.
- **Rerun alone:** `OK`.

## 4. Cold final pass

Fable 5.1, cold, over #485, #486 and #487 together: **FINAL PASS: PASS** (`fable-final-pass-analysis-prs.md`). One LOW item is recorded as a flag: `_floor_producer_plans` lacks type guards on the single-plan path. It is not reachable with an artifact that passed schema validation, and a raise fails closed. Deferred to `AN1-TEST-ISOLATION`.
