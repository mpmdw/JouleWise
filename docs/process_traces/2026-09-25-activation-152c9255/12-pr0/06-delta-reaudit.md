# Fix round 1 re-audit: PR-0 (WR-7), delta `ab48c5d3..7929a7ec`

**Verdict: not ready to merge. 2 new BLOCKERs, 3 SHOULD-FIX.** The prior blockers B-1 and B-2 close as written, but the fix introduced one counterfactual scenario and exposed a conflict with the WR-6 ruling. The worktree is untouched (clean at `7929a7ec`). All work ran in `/tmp/152c9255/pr0-delta/repo`, with its `origin/main` pinned to `c034a56f`. No sudo, launchctl, powermetrics or full test discovery.

## A confound in the mutation evidence (read this first)

**The fix seat's "all nine mutations killed" was confounded.** Any byte change to `claims.py`, `artifact.py` or `paper_custody.py` already fails the golden test, even a comment. The failure comes from the imported custody fixture, not from the golden comparison: `AssertionError: stale supply-map receipt digest` at `tests/test_paper_custody.py:175`. The fixture pins a hash of the validator source files.

I turned that assertion into a no-op in a clone branch, confirmed the golden still passes, and confirmed a comment-only edit is then OK. After that change:
- **The lens's M1–M9 are still all killed**, genuinely this time.
- **My 10 new mutations: 3 killed, 7 survived.**

| # | New mutation | Result |
|---|---|---|
| N1 | Holm `(m-rank+1)` → `(m-rank)` | killed |
| N2 | Holm running maximum dropped (`running_maximum = candidate`) | **SURVIVED** |
| N3 | `estimators.py:228` t quantile `.975` → `.95` (confidence level of the v1 interval) | killed (error) |
| N4 | Equivalence ignores `adjusted_rejected` (`claims.py:363`) | **SURVIVED** |
| N5 | Decision interval obscures direction → `unresolved` instead of `not_resolvable` | **SURVIVED** |
| N6 | Decision-interval zero check dropped (`claims.py:371`) | **SURVIVED** |
| N7 | `floor < 0` → `floor <= 0` | **SURVIVED** |
| N8 | `_inside_equivalence` strict → non-strict | **SURVIVED** |
| N9 | Floor selector ignores `window_class` (`__init__.py:409`) | **SURVIVED** |
| N10 | Validator t critical `.975` → `.95` (`artifact.py:2094`) | killed (error) |

Without the no-op change, N4–N8 also show as "killed", but only by the digest assertion.

## BLOCKER

**D-1: The "admitting_v1_wire" issuance scenario can't happen in production, and it hides a live defect in the production gate.** `scripts/capture_claim_replay_golden.py:317,334`
- The capture adds a top-level `evidence_class` to the artifact. The real validator rejects that key (`artifact: unrecognized key(s): evidence_class`), so the capture then mocks `validate_claim_verdicts` to get an admit.
- I checked the real path on the unmodified builder artifact. `validate_claim_verdicts(art, frozen_manifest=splitwise)` returns `[]`. Then `_claim_issuance_gate` raises **`KeyError: 'evidence_class'`** at `joulewise/paper_custody.py:632`, because it reads `artifact["evidence_class"]` while the v1 wire carries `inputs.evidence_class`.
- So no v1 artifact that passes the validator can reach the admit branch. The golden records `admitted: true` for a state production can't reach. The brief said to state this outright, not hide it.
- The manifest in the finalized-manifest slot is also plain `v3`, not `v3.finalized`, and its finalized validator is mocked.
- The "invalid" case is rejected only for the key the capture itself added, not for `cv-invalid`. That is the only reason M9 is killed.
- **Fix:**
  - Remove the injected `evidence_class` and the verdict-validator mock.
  - Record the real outcome as `{"raised": "KeyError", "key": "evidence_class"}`.
  - Make the invalid case invalid only by `claim_verdicts_id`. M9 stays killed: a skipped validator produces the KeyError, not a refusal.
  - Add to `selection_rules`: "no unmocked admitting v1 path exists at PR-0".
  - Escalate `paper_custody.py:632,643` as a separate defect. PR-0 can't touch `joulewise/`.

**D-2 (contract; needs a ruling): the golden can't survive WR-6 as ruled.** WR-6 admits a v1 contrast in `analyze_claims` and `_claim_issuance_gate` only if its manifest is in the golden set (or its `collection_manifest_id` is a front-registry planned id). Otherwise it adds `claim_rule_version_v1_closed` and sets ready to false.
- `v1_golden_manifest_ids = []`, yet `window_engine.v3_window_clean` (`direction_supported`, ready) and `issuance_gate` both run on `am-5e97…` (splitwise).
- CG-4's commit (7) therefore must change the golden, and `test_golden_refresh_isolated` forbids refreshing it in that PR. That is a deadlock.
- **Options for the magistrate:**
  - (a) Split the golden into a WR-6-invariant part (`claim_matrix`, `claim_verdicts`, validators, epoch) and a closure-expected part pinned to post-WR-6 outcomes.
  - (b) Rule whether `am-5e97…` joins the v1 set.
  - (c) Run the v1 scenarios through a front-registry `collection_manifest_id`.

## SHOULD-FIX

**SF-A: Seven decision branches are still unpinned (N2, N4–N9).**
- **Fix:** add these `claim_matrix` rows:
  - equivalence inside the margin with `adjusted_rejected=False`;
  - metrology interval straddling zero;
  - decision interval straddling zero with metrology clear of zero;
  - `floor_gate_j=0.0`;
  - interval edge exactly at ±margin.
- Add `window_class` and `condition_family` mismatch rows beside `metric_selector_mismatch` (`:295-300`).
- Add a direct `holm_adjust` call on a non-monotone family, e.g. `{a:.01, b:.04, c:.03}`, m=3.

**SF-B: The issuance section uses `RoundFiveTests` as a fixture factory** (`:320-321`).
- It couples the golden to the supply-map receipt digests, which is the confound above: any comment edit to three CG-4 files fails the golden until WR-8 repins.
- It also couples the golden to `tests/test_paper_custody.py`, which WR-5, WR-6 and WR-8 all edit (WR-8 moves the receipt builder out of it).
- Each capture runs `git init` and `git commit` in a temp directory, so it depends on global git config (gpgsign, hooksPath).
- Its `addCleanup` never runs: 3 temp directories leak and `ResourceWarning` fires at exit.
- **Fix:** build `_GateContext` directly, as `_families()` already does. At minimum, call `case.doCleanups()` in a `finally`.

**SF-C: `main()` refuses on `joulewise/` only** (`:384-387`). The isolation test also covers `scripts/epoch_equivalence_check.py`. I confirmed that editing that file lets `main()` write.
- **Fix:** add `scripts/epoch_equivalence_check.py` to all three git calls.
- When `origin/main` is absent, `main()` stops with a `CalledProcessError` traceback. Print a clear refusal instead.

## NIT
- **N-a:** A stale local `origin/main` causes a false failure on an unrelated branch (scenario S6). CI is safe because it uses `fetch-depth: 0`. Say so in the skip/fail message.
- **N-b:** `--allow-dirty-for-tests` is used by no test. Either add the tmp-copy test the brief described or delete the flag. It can't be reached without typing it, so it isn't an accidental bypass.
- **N-c:** At `:350`, `capture()` reads its path list from the file under test, and `selected_paths == []` silently falls back to the old key-union. Keep a `SELECTED_PATHS` constant in the script and assert that the golden echoes it.
- **N-d:** The `selection_rules` text says "finalized v1", but the code counts any error-free `analysis_manifest.v1`. Pick one.

## Prior findings: closure

| Finding | Status | Evidence |
|---|---|---|
| **B-1** | **CLOSED** as specified; coverage gaps remain (SF-A, D-1) | M1–M9 killed after removing the confound |
| **B-2** | **CLOSED**: `[]` is honest | No tracked `v1` or `v3.finalized` manifest in the repo, and none under `~/night-custody`. The tracked set is 3 × v3.prospective drafts, 1 × v3 (splitwise) and 3 × v2 fixtures. The WR-6 consequence is D-2. |
| **SF-1** | **CLOSED**; part 2 incomplete (SF-C) | Test scenarios below; indent=1 output confirmed |
| **SF-2** | **CLOSED** | See check (3) below |
| **SF-3** | **PARTIAL** | New files are only reported (`[]` today). But the golden now depends on 3 test-module builders and the supply-map digests (SF-B), and edits to pinned files still force a refresh. |
| **SF-4** | **CLOSED** | Residual documented in `selection_rules.fixture_families` |
| **N-1..N-5** | Applied | Includes s9 PASS/fail replays and disagreement raises |

**Check (1): `test_golden_refresh_isolated` scenarios**

| Scenario | Result |
|---|---|
| S1: golden + `claims.py` in one commit | FAIL (correct) |
| S2: the same change split over 2 commits | FAIL (correct) |
| S3: golden + epoch script | FAIL (correct) |
| S4: after PR-0 merges, a `joulewise/`-only change | OK (correct) |
| S5: after PR-0 merges, a docs-only change | OK (correct) |
| S6: stale `origin/main`, unrelated branch | FAIL (false positive, N-a) |
| S7: no `origin/main` | skipped (correct) |

**Check (2): `main()` refusal**
- It refuses on a working-tree edit and on a committed edit under `joulewise/`.
- Passing the flag skips the refusal. On my working-tree `claims.py` edit the capture then crashed on the stale supply-map digest (SF-B).

**Check (3): mutation test.** `test_golden_detects_one_number_mutation` patches the real `_resolve_contrast_floor`. The `_assert_matches_golden` helper is what raises, so a broken helper would fail this test. It checks the helper genuinely.

**Check (5): importing test builders from a script.** There is no network access. Two captures are byte-identical, and the blob `e5e84930…` also reproduces from a clean clone. The side effects are listed under SF-B.

**Check (6): empty manifest set.** Honest; see B-2 above.
