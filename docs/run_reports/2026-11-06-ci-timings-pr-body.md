Tier: full

Impact statement (start each answer with Yes or No, then say why; any Yes makes this PR full tier):
(i) Raw-bundle byte or recorded timestamp: No; no raw evidence is read, written or re-stamped. Only CI shard scheduling and test fixtures change.
(ii) Reduced energy, time, token count or correctness score: No; no reducer, estimator or scorer is touched. The seconds in scripts/test_timings.json are CI packing hints, and no step asserts them.
(iii) Admit, refuse, select or exclude decision over bundles, nights, blocks, envelopes or items: No; every test still runs exactly once. Splits change which shard runs a test, not whether it runs, and the coverage guards are unchanged or stricter.
(iv) Unit or uncertainty: No; no unit or bound computation changes.
(v) Registration, prospective manifest, analysis plan or estimator constant: No; no registration, manifest, plan or constant is edited.
(vi) Published number or sentence in the paper, README claims or claim renderers: No; no renderer or claim text changes.

## Gate ledger

| # | Gate | Evidence |
| --- | --- | --- |
| 1 | Independent review by a non-author, with a lens that executes the code (light tier: N/A (light tier)) | RUN 19cbb28ff |
| 2 | Whole suite on the merged tree (current main merged into the head), exact tail recorded (light tier, docs only: N/A (docs only)) | NOT-RUN |
| 3 | CI green on the final head; evidence is that head's sha | NOT-RUN |
| 4 | Cold Fable final pass on merge code that touches measurement, calibration or claims (otherwise: N/A (no measurement, calibration or claim code); light tier: N/A (light tier)) | N/A (no measurement, calibration or claim code) |
| 5 | Findings dispositioned: each fixed, deferred to a named lane, or rejected with a reason (light tier: N/A (light tier)) | RUN fafc45368 |

## Gate evidence

- Row 1: Opus 5.5 cold review, commit `19cbb28ff` on `perf/2026-11-08-opus-review-ci-timing`, Branch 1 section of `docs/perf/2026-11-08-opus-review-ci-timing.md` (read with `git show origin/perf/2026-11-08-opus-review-ci-timing:docs/perf/2026-11-08-opus-review-ci-timing.md`). It executed the code: it replayed test discovery on both trees and ran the targeted modules one per process. Verdict: HOLD on the old head `858d9f91b`, ADMIT_WITH_FIXES for Sol's `eaf3143f7`. It proved no test is lost: 12,217 test ids on main versus 12,227 on Sol's tree merged with main.
- Row 2: pending the CI pull_request run on the final head (RUN_STATE item 165 counts it as row 2).
- Row 3: pending CI on the final head.
- Row 5: see Dispositions.

## Summary

The old PR head (`858d9f91b`) was stale: it conflicted with main, so GitHub ran no CI on it, and its own new guard `test_every_discovered_module_has_timing_or_documented_exemption` failed once main was merged (15 modules main added after the timing harvest). This update replaces it with Sol's finished work from `perf/2026-11-08-eng-ci` (`eaf3143f7`), merged without rebase, then merges current `origin/main`.

What the PR now does:

- **Timing repair.** The 15 modules added on main after the 2026-11-06 harvest, plus the new BYTES regression, get explicit `timing_exemptions` entries ("pending hosted timing"). They still run, packed at the conservative 26.98 s unknown weight. No hosted measurement was invented. Main deleted `tests/test_harvest_v5_qualification.py`, so its timing entries and the lane's harvest-v5 hex-boundary change are dropped.
- **Exemptions expire both ways.** The guard already rejected an exemption for a module that has gained a weight. It now also rejects one for a module that no longer exists (Opus LOW-3), so stale exemptions cannot pile up.
- **Git fixture maintenance at clone time.** `clone_git_fixture` installs the maintenance controls during the clone, before checkout hooks run, and `tests/test_receipt_histsem.py` uses it at its clone sites (the "[Errno 39] Directory not empty" teardown flake). A checkout-hook regression fails before the fix and passes after it.
- **Fail-fast off.** The ordinary CI matrix has `fail-fast: false`, so one failing shard no longer cancels the timing observations and tests on the others.
- **Independent BYTES worlds.** `docs/perf/2026-11-08-bytes-world-split.patch` splits the 60-campaign `test_bytes_analysis` method into three independent 20-campaign world methods, for the ALIGN lane. It is a patch only. Main has no BYTES module, and no BYTES implementation is backported here. `tests/test_bytes_campaign_split.py` pins the split semantics. The log format changes from one three-world `BYTES_SIMULATION_REPORT=` line to three one-world lines (Opus LOW-2). Anyone harvesting that line by hand must concatenate the three lines in world order.

**What the savings are, honestly.** They apply only to lanes that carry `tests.test_bytes_analysis`, which is not on main. On main this PR gives previously untimed modules weights (tighter LPT packing) and turns fail-fast off. Main's slowest shard is already about 31 min (last green main run 42457786443), so do not read this as a main CI saving. The headline 152.0 min to 56.3 min figure is a static projection for the ALIGN lane (`align/2026-11-08-v4-r11` or later), and needs two steps there: this timing map reaches ALIGN, then the BYTES patch is applied. The three world weights are equal shares (5,741.949 / 3 = 1,913.983 s each), not measurements. Up to 16 modules are packed at the fallback weight, so the planner's balance (1,386.9 s x 12 on the main-based tree) is a lower bound until the next hosted harvest.

Opus cold review: `git show origin/perf/2026-11-08-opus-review-ci-timing:docs/perf/2026-11-08-opus-review-ci-timing.md`, Branch 1 (commit `19cbb28ff`). Sol's report: `docs/perf/2026-11-08-eng-ci.md`, shard map `docs/perf/2026-11-08-eng-ci-shards.json`.

## Dispositions

- HIGH-1 (PR cannot merge; guard fails on merged tree): fixed. Sol's `eaf3143f7` is now the base, main is merged, and the guard passes.
- MED-1 (152 to 56.3 min is not a main effect): accepted and stated above. The BYTES patch stays an ALIGN-lane step after this map lands there.
- LOW-1 (no assertion weakened): confirmed by the review; no action.
- LOW-2 (BYTES log format): documented above; no code consumer exists outside the test.
- LOW-3 (exemptions never expire for deleted modules): fixed in `fafc45368`.
- LOW-4 (optimistic balance from fallback weights): deferred to the next hosted harvest, which replaces the exemptions with measured weights.
- `docs/run_reports/2026-11-06-ci-timings-pr-body.md` (stale body describing the old lane): refreshed.

## Verification

Local, Python 3.14 (homebrew), `python -m unittest`, one module per process, `TMPDIR=/private/tmp/pr685`, on the merged tree:

| Module | Result |
| --- | --- |
| tests.test_shard_split | 36 tests, OK |
| tests.test_shard_tests | 8 tests, OK |
| tests.test_git_fixture_maintenance | 6 tests, OK |
| tests.test_git_fixture_hygiene | 7 tests, OK |
| tests.test_bytes_campaign_split | 4 tests, OK |
| tests.test_receipt_histsem | 74 tests, OK (skipped=1), 980 s |

The whole suite was not run locally; row 2 is the CI pull_request run on the final head.

🤖 Generated with [Claude Code](https://claude.com/claude-code)
