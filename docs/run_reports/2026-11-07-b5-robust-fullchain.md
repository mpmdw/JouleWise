# Block-5 robust head: full-chain synthetic equality gate before r3

2026-11-07, M4 Air (10 cores, Python 3.13.18). Branch `lane/2026-11-07-b5-r3-speed-fix`
= `lane/2026-11-06-b5-robust` (`4b0781b04`) + `70d32a878`. Synthetic data only: the
committed S10 fixtures through `scripts/b5_e2e_synthetic.py` (`/private/tmp/jwb5u90-tmp/local-e2e.zsh`,
10 workers, nice 5, 18 GB memory guard, release-dir stop). No real data, restricted
custody or real driver run was touched. Another lane's probe process held one core
throughout, so absolute walls carry about 10% noise.

## Verdict

**EQUAL over the full chain (steps 0-11), for both the robust head and the fix head.**
All three runs exit 0 with identical step statuses (every step `ok`, 4 and 10 per pack).

| Run | Code | Record sha256 | Custody files identical | Wall |
|---|---|---|---:|---:|
| r2 | `929fc65c9` (b5/analysis-r2) | `dfd1f5b980ae1bfbe29968e996f897cd59343ddd5e7c9a03a3c34b542349b7f8` | reference (1,543 files) | 903 s |
| robust | `4b0781b04`, cProfile on 8,6,9,9b,10,11 | `dfd1f5b9...49b7f8` | 1,540 / 1,543 | 964 s |
| fix | `70d32a878`, unprofiled | `dfd1f5b9...49b7f8` | 1,540 / 1,543 | **401 s** |

The three differing files are, in both comparisons, exactly the timing/audit logs:
`restricted/logs/runtime-phases.jsonl`, `restricted/logs/runtime-vdl-counters.json`
and the pid-named `restricted/logs/runtime-stack-<pid>.txt`. No `resume/` files appear
in an uninterrupted run.

## Defect found and fixed: the step-3b prefetch refitted 13x too many candidates

On the robust head, step 3b took **408.7 s against r2's 83.8 s** (equal outputs). The
3b profile (steps 0-3b, `--cprofile-steps 3b`) showed `_prefetch_one_candidate`
called 153 times, against 12 `_candidate_from_observation` calls. The prefetch from
`13af1baa8` refitted every valid ledger row (51 per pack). The frozen
`discover_calibration_candidates` authenticates only rows in no bracket session or a
finalized one that are neither derivation-kind nor superseded-capture (4 per pack). The
other 141 refits were pure waste and saturated the pool for about 5 minutes. Item 2 was measured
in the cloud at 3 workers with serial packs, against a different baseline, so the waste
was not visible there.

Fix `70d32a878`: the prefetch applies discovery's predicates in discovery's order, and
calls the frozen functions themselves (`_is_derivation_kind_observation`,
`_capture_pipeline_refusal_for_observation`, finalized-session set). Only the prefetch
row set changes. The frozen evaluator still authenticates and refits as before. A new
test (`test_prefetch_refits_exactly_the_rows_discovery_authenticates`) drives
`discover_calibration_candidates` and the prefetch over the same synthetic snapshot,
with open, finalized, missing-session, derivation, superseded and historical rows, and
asserts the identical ordered locator list. It fails on `4b0781b04` and passes on the fix.
Profiled 3b after the fix: 12 prefetch refits, 1,499.5 s -> 123.6 s under cProfile.
Unprofiled full chain: 3b 37.3 s.

Tests on the fix head: `test_candidate_physics_memo` 6, `test_bracket` 48,
`test_l4_custody_probe` 6, `test_frozen_files` 3, `tests.test_custody_mode_inventory` 7: all OK.

## Per-step wall (s), 10 workers, synthetic S10

| Step | r2 | robust (late steps profiled) | fix (unprofiled) | fix / r2 |
|---|---:|---:|---:|---:|
| 0 | 4.2 | 3.7 | 3.3 | 0.79 |
| 1 | 29.6 | 29.5 | 30.3 | 1.02 |
| 2 | 3.5 | 3.4 | 3.4 | 0.97 |
| 3 | 0.3 | 0.2 | 0.2 | |
| 3b | 83.8 | **408.7** | 37.3 | 0.45 |
| 4 | 41.3 | 30.8 | 29.0 | 0.70 |
| 5 | 204.1 | 134.7 | 138.9 | 0.68 |
| 8 | 44.0 | 39.5* | 15.7 | 0.36 |
| 6 | 36.1 | 9.5* | 4.4 | 0.12 |
| 9 | 81.5 | 50.1* | 22.6 | 0.28 |
| 9b | 130.1 | 98.1* | 37.2 | 0.29 |
| 10 | 81.9 | 16.1* | 11.4 | 0.14 |
| 11 | 162.4 | 137.9* | 65.5 | 0.40 |
| **Total** | **903** | **964** | **401** | **0.44** |

\* under cProfile (inflated). Peak tree RSS: r2 2.9 GB, robust 6.9 GB (the 153-refit
prefetch), fix 3.8 GB.

## Projected real-data wall (r3 on the fix head)

Method of the under-90 report section 5: dry-j r2 per-step walls (7 workers, loaded
machine) times the synthetic fix/r2 ratio.
- **Naive** (every ratio above): about 4,560 s, **about 76 min**.
- **Conservative** (ratio 1.0 for steps 8, 6, 9 and 10, 0.95 for step 11; their synthetic
  gains come mostly from L4/VDL hits whose real-data hit rate is unmeasured): about
  7,430 s, **about 124 min**.

The real r3 dry run measures which end holds; ten workers on a quiet machine should land
nearer the low end. Ordered by size, the remaining real-data mass under this projection is
step 5 (about 970 s), step 1 (about 920 s, frozen CPU), step 3b (about 740 s) and step 4
(about 590 s).

## Late-step profile notes (robust, cProfile)

- Step 8: `_preflight_other_inputs` is 20 of 39 s. It is a full finalization pass whose only
  purpose is to guard a sidecar write, and that write cannot happen when the sidecar is
  already in custody. This is what `sol/burn-s8` removes.
- Step 9b: 98 s are driver-serial in `paper_custody` claim-verdict replay, of which 65 s are 3
  VDL fills of `verify_instrument_calibration` (refits). On real data step 9b was 0 s in dry-j,
  so this is low priority.
- Step 11: `load_analysis_inputs` x3 = 53 s; the sensitivity passes take 85 s, 59 s of it in the
  pack pool.

## Triage of unreviewed drafts (none integrated; r3 does not wait on them)

| Branch | What | Verdict |
|---|---|---|
| `sol/burn-s8` | Skip the duplicate finalization preflight when the sidecar is already in custody (the predicate mirrors `stage_dominance_replay_sidecar`'s own no-write branch) | **Worth integrating next.** About half of step 8 (real step 8: 537 s). The success path is unchanged. Behaviour change on defect paths only: when the sidecar and another input are both bad, the sidecar refusal now fires first. Needs a ruling plus an e2e. |
| `sol/burn-s5` | Mint producer authentication via `pack_map`; ships the `grammar_ok` memo (also with VDL off); memoizes `Path.resolve` per auth session | **Worth it, after reconciling with item5** (they duplicate each other). Risks: `vdl_context` now returns a truthy dict when the store is off (every caller's `if context:` changes meaning); it mutates the global `BLOCK5_PRODUCERS` in the serial fallback. The resolve memo is a small TOCTOU relaxation on authenticated paths and needs review. Step 5 is the largest real step. |
| `lane/...-under-90-item5` | Same goal as burn-s5, with a 531-line refactor of the mint into `_authenticate_v2_producer` | Never run (sandbox-blocked); its cloud digest check is unknown here. Pick **one** of item5 and burn-s5; burn-s5 is the smaller diff. |
| `lane/...-under-90-item3` | Run step 11's two bound passes ahead | 1 of 7 tests failing, not debugged. Its value is now small (step 11 is 65 s synthetic, after the per-pack overlap). **Defer.** |
| `sol/burn-s10` | Ship only the pack's physics partitions to step-10 pack workers | Low value now (step 10 is 11 s synthetic). The call-graph walk is heuristic, with a whole-store fallback. **Defer.** |
| `sol/burn-s9` | Cache `RunState.evidence_roots` across 9/9b/11; frozenset lookup in 9b | Small gain. The cache drops two re-reads of sealed custody inputs (a trust-boundary choice). **Skip** unless a real profile shows it. |
| `sol/burn-s11` | Tests only: byte equality at both bounds, plus a two-party overlap barrier | Harmless. The barrier test is timing-based (5 s), so it may flake under load. **Optional.** |
| `sol/burn-tests` | `shard_tests.py --start-directory`; `setUpClass` in the windows-index test | Tooling only, safe. **Integrate at any time** (not analysis code). |

## Artifacts (scratch)

Summaries and custody trees are in `/private/tmp/jwb5u90-e2e/out-{r2,robust,fix}/`. Profiles are in
`/private/tmp/jwb5u90-e2e/prof-robust/` (late steps), `prof-3b-robust/` and `prof-3b-fix/`.
