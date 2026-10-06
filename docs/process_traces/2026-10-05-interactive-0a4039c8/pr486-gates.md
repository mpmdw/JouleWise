# PR #486 gate record: D-165 sidecar in finalize, pinset emitter, per-cell config binding (memo items 4.3 and 4.4)

Branch `feat/2026-10-05-analysis-an3`, off main `e0c738e9`. Implemented by a Sol 6.1 lane in four rounds; commits and records by the interactive orchestrator (Opus 5.5, session 0a4039c8).

## Orchestrator ruling (round 2)

The v2 floor mint required one scientific config hash per producer. A `_v5` producer runs two workloads with different configs (decode and p2048), so the real floor could never be minted.

Ruling: each cell is checked against the pinned config of its own workload, and the producer pin is the canonical hash of the sorted per-cell set. A cell whose observed config differs from its own pin is still refused; that check is physical. Implemented in `c5e6dc39`. It needed `joulewise/detection_floor.py` in scope, which the orchestrator approved: it is not a pinned estimator file.

## 1. Independent executing review

Reviewer: an Opus 5.5 agent, not the author, with mutants and probes, run on `8c6dd2c2` (round 1).

**Verdict: FAIL.**

| Severity | Finding | Disposition |
|---|---|---|
| MAJOR | Finalize staged and sealed a sidecar from another floor, or a near-empty one, at rc 0. Append-only custody then refused the correct re-run. | Fixed in `2f42248c`. Before anything is staged, finalize requires a valid replay sidecar whose id matches the floor, whose cells align with it and whose member census matches. |
| MAJOR | The emitter's `main` and the success path of `_bootstrap_producer` were never run. | Fixed in `2f42248c`. Tests run them on a real `_v5` pack with one byte altered in the spec or order manifest, and with the wrong `--prefill-role`. |
| MINOR | No test placed an existing file at the staged path. | Fixed in `2f42248c`. |
| MINOR | A refused run still left a staged sidecar in custody. | Fixed in `2f42248c`: staging happens only after every input passes. |

The reviewer's mutants of the removed pin checks and of the overwrite and no-stage paths now fail the tests. The floor, mint, emitter, finalize and claim suites pass: 170 tests, 4 skipped, 224 subtests.

## 2. Whole suite on the merged tree

Run on `2f42248c`; main is still `e0c738e9`. Shard tails: `suite-an3-summary.txt`.
- **Under load:** 3 failures (`suite-an3-failures.txt`), the load-timing tests in `test_sample_quiet_predicate_evidence`, which this PR does not touch.
- **Rerun alone:** `OK`.

## 3. Cold final pass

Fable 5.1, cold, over #485, #486 and #487 together: **FINAL PASS: PASS** (`fable-final-pass-analysis-prs.md`). Fable executed the cross-workload swap tests and the legacy single-config paths, and found no defect. The two JSON-schema tests skip because `jsonschema` is absent; the Python validators that gate the mint were executed. That gap is recorded as a flag.
