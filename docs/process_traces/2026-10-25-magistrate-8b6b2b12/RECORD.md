# Magistrate activation 8b6b2b12 (Opus 5.5, headless, 2026-10-25 from 13:36 PDT)

Launched with nine pending `yield.stage_zero` notices, all plan r1-bytes-s1-p1. No unread mail from Ed; open directive issues are the standing ones (#405, #408, #416, #417, #421, #422), nothing new.

## What happened to r1-bytes-s1-p1

1. **The first BYTES pass-1 session collected zero data.** t0 07:55 PDT, chain rc 0, every collection stage rc 1. All 143 member runs refused within about 0.4 s with the same error (tallied from `custody/operator-logs/member-stderr/`, 143 of 143):
   `ArmReadinessError: cannot read plan-tree sidecar: ... configs/campaigns/bytes-s1-p1/plan_tree.sha256`
   raised in `controller._authenticate_g2b_pre_slot_attachment` -> `arm_readiness._plan_tree`. Bound derivation then failed on the empty corpus ("NEG-8 reference corpus requires n >= 10"), as expected.
2. **Cause.** `scripts/bytes_plan_trees.py` writes `plan_tree.json` but no `plan_tree.sha256`. All 12 BYTES packs (and `bytes_mac_check`) lacked it; block-6 and D-117 packs have it.
3. **Why the smoke passed.** `joulewise/b6/smoke.py` (line ~283) reduces the tree in its staged clone and writes a fresh sidecar for the reduced tree, so smoke members authenticated against a file the committed pack never had. The smoke also skips the bound-collection stage. Smoke r1-bytes-s1-p1-smoke-0 yielded present 1 per kept stage, rc 0.

## Actions

4. **Loop held (13:4x).** `b6_loop.py --loop-root /Users/edr/night-b6/loop-bytes hold --pack bytes-sN-p1` for N=1..6 (rc 0 each). Loop state stays SESSION_DESK so the s1 desk can record the attempt; with all packs held, NEXT goes idle instead of spending s2.
5. **Email to Ed** with all nine notices, the cause and the plan: Gmail 1a174cad9022cac9. `notice.ack` written after it was accepted.
6. **Fix** on `fix/2026-10-25-bytes-plan-tree-sidecar` at 991358f73 (parent 537180b78), draft PR #581 into work/2026-10-23-by-slots-draft:
   - the twelve sidecars, made with `shasum -a 256 plan_tree.json` in each pack directory, over the registered bytes, which stay unchanged. Regenerating through the generator would have rewritten each tree's embedded generator digest, so the generator is left as is; `bytes_plan_trees.py --check` still passes;
   - one test, `test_every_loop_pack_tree_authenticates_through_its_sidecar`: every `plan_tree_ref` under `configs/b6/packs/*/registration.json` (15 trees, 12 BYTES) read through `_plan_tree`. Counterfactual: with the sidecars moved aside it errors on bytes-s1-p1; restored, the module passes (7 tests).
   - Tier: light (data authenticators plus a test). No number, rule, registered byte or estimator changes.
7. **Slip, contained.** A `git stash -- configs/campaigns` with only untracked files created no stash, and the following `stash pop` applied the repository's unrelated stash@{0} ("pr0-r3-partial-stopped") into the fix worktree. The four files it added were removed by literal path before any commit; stash@{0} is still in the list. Lesson: never use stash for a counterfactual; move files aside into a temp directory.
8. Canonical root fast-forwarded 24cf856f9 -> b9fa260b5 (no `com.joulewise.night*` label loaded or plist on disk).

## Decisions I made

- Smoke code unchanged. The new test makes CI refuse any commit where a loop pack's committed tree does not authenticate, and measurement checkouts are cut from CI-green heads, so a smoke-side guard would duplicate it.
- The measurement checkout is not re-cloned: it gets the two commits cherry-picked onto its local pin commit (item 10). The delta is 12 data files and tests, and the venv and the ledger (now 412 rows) stay as they are.
- The controller refusing on a missing sidecar is a records check that, under the 10-05 doctrine, should be a flag. Changing it is claim-path code with full gates; it goes to the pruning list, not to this fix.

9. **CI on 991358f73 (PR #581): success**, 20 of 20 (shard 10 takes about 150 min).
10. **Measurement checkout:** `git cherry-pick 537180b78 991358f73` onto its local pin commit 786ecd968 (the s1 session's post-calibration pin, ledger sequence 412). HEAD 8e097d020; `git diff 991358f73 HEAD` is the pin file only; tree clean. In the checkout: `tests.test_bytes_plan_trees` and `tests.b6.test_code_check` pass (16 tests), and `_plan_tree` authenticates all six pass-1 packs. The changed paths are not in the registered number-bearing list, so sessions add only `code.changed_since_registration` (DISCLOSE).

11. The loop's own desk ran at 13:48 while packs were held: attempt r1-bytes-s1-p1 recorded `not_counting`, cause `NEG8,ROSTER` (`attempts.jsonl`); its loop_hold mail went to issue #509. The previous-session flags include `pack.identity_mismatch` and `code.executed_differs_from_sealed` (disclosed); watch whether s2 repeats them.
12. No unread mail from Ed, no new directive, no stand-down request. **Resumed 16:06 PDT:** `b6_loop.py --loop-root /Users/edr/night-b6/loop-bytes resume` rc 0; state NEXT, all six pass-1 packs open, attempts reset. Next selection is s2-p1 (round 1); the loop smokes it and sends its arm notice. Email to Ed: Gmail 1a17551176dc0048 (same thread). Session exits so the pre-check can run.

## Pruning tally (gates that ran this session)

- Yield alerts (`yield.stage_zero`): caught the zero-yield session. Keep.
- Smoke: did not catch it, because it writes its own sidecar into its staged copy. The catch now sits with the new test. Smoke's other checks are unchanged.
- Controller sidecar refusal: cost one whole session (265 min of quiet machine time) and protected no number. It is a pruning candidate.

## Next

See RUN_STATE item 71.
