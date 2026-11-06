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
| 1 | Independent review by a non-author, with a lens that executes the code (light tier: N/A (light tier)) | NOT-RUN |
| 2 | Whole suite on the merged tree (current main merged into the head), exact tail recorded (light tier, docs only: N/A (docs only)) | NOT-RUN |
| 3 | CI green on the final head; evidence is that head's sha | NOT-RUN |
| 4 | Cold Fable final pass on merge code that touches measurement, calibration or claims (otherwise: N/A (no measurement, calibration or claim code); light tier: N/A (light tier)) | N/A (no measurement, calibration or claim code) |
| 5 | Findings dispositioned: each fixed, deferred to a named lane, or rejected with a reason (light tier: N/A (light tier)) | NOT-RUN |

## Summary

This PR moves the CI shard-balance and flake fixes from lane/2026-11-06-sol-ci-flaky-timings (head d0f7a8a1e) onto main. It does not carry that lane's b5 base. The lane was stacked on lane/2026-11-05-b5-post-release-fixes (PR #651, head a33860c4d). PR #651 is marked "do not merge before the block-5 release" and still has open NEEDS-LEAD and NEEDS-ED items, including a DRAFT decision-log entry. A plain merge of the lane would have landed all eight #651 commits on main under a CI title. So the branch is origin/main 284867530 plus the lane's five CI commits, cherry-picked in order. Each commit message names its source sha. The last commit is new.

The CI files (scripts/shard_tests.py, scripts/test_timings.json, tests/test_shard_split.py, tests/test_shard_tests.py, tests/git_fixture.py, tests/test_receipt_histsem.py, tests/test_harvest_v5_qualification.py) are byte-identical to a local merge of the whole lane into main. None of those paths depends on the #651 commits. The five tests.b5_analysis.test_postrelease_* weights in seconds_by_module are inert until #651 lands. Like the 190 cross-lane entries, they name modules this tree does not have yet.

From the lane (see each commit for its evidence):

- test(harvest-v5): the hex-boundary blindness scan exempts an all-decimal secret only inside a maximal hex digest run, and field names keep plain substring matching (2 commits; the first was a cloud Sol 6.1 xhigh task applied by the lead and is unreviewed).
- test(histsem): clone_git_fixture disables detached git maintenance at all eight clone sites. This fixes the "[Errno 39] Directory not empty" teardown flake on hosted run 42000523184.
- ci(timings): the invented 20 s/method estimates are replaced with hosted observations. 190 cross-lane modules (PR #682, main, qwen4/qwen4exp lanes) get hosted medians. The tests.test_bytes_analysis 60-campaign method is split out (5,742 s plus a 3,380 s remainder). PR #682's tests.b6.test_cold_pass_fixes split is ported with hosted per-test seconds, which run 1.3x to 6x above #682's local estimates. untimed_module_allowance admits small new tests.align. and tests.test_qwen4 modules.

New on this branch (verifier LOW on d0f7a8a1e):

- awaiting_lane now expires. scripts/shard_tests.forward_declaration_problems() reports two states: a split for an absent module with no awaiting_lane, and a split for a present module that still carries awaiting_lane. The checked-in guard in tests/test_shard_split.py asserts the list is empty. When tests.test_bytes_analysis or tests.b6.test_cold_pass_fixes reaches main, the guard fails until that one key is deleted. The hosted declared weights stay. Scheduling still never reads the key.
- scripts/test_timings.json is now a key superset of every lane/2026-11-0* timing map (48 checked, lane/2026-11-05-align-pilot10-benign included). That lane carries PR #682's local cold_pass_fixes split. Three provenance keys only the lanes had are added and marked SUPERSEDED with the hosted value now in force. Every seconds_by_module and split_modules key on those lanes was already present. A MERGE RULE sentence in _hosted_observations_2026_11_06_cross_lane says to keep this file's (hosted) values when an align lane reaches main.

## Verification

All runs are local: Python 3.13.18 (/private/tmp/jwsol/venv-both), TMPDIR=/private/tmp/jwwf-tmp, under nice -n 19 taskpolicy -b. These are targeted modules only, not the whole suite.

- python -m unittest tests.test_shard_split tests.test_shard_tests tests.test_harvest_v5_qualification: Ran 58 tests, OK.
- python -m unittest tests.test_receipt_histsem: OK (skipped=1). This is the module whose clone-teardown flake the histsem commit fixes; it took about 30 min under background QoS.
- Mutation check: with the present-and-marked branch of forward_declaration_problems disabled, tests.test_shard_split.SplitDeclarationLoadingTests.test_awaiting_lane_expires_once_the_module_is_discovered fails (FAILED (failures=1)).
- CI plan self-check (the ci.yml ordinary-shard planning code, SHARD_COUNT=12, no units run): 488 modules discovered, none untimed, forward_declaration_problems empty, ORDINARY SHARD ESTIMATES 1404.178 s x 12.
- Projection onto lane/2026-11-05-align-pilot10-benign's 567 test modules with this map: no module is untimed. forward_declaration_problems flags exactly tests.b6.test_cold_pass_fixes and tests.test_bytes_analysis, which is the intended expiry.
- On the full-lane merge variant (which includes #651), these also passed: tests.b5_analysis.test_postrelease_{step4,g9,step11_codes,bracket_copies,bracket_snapshot} and tests.b5_analysis.test_sensitivity_guard, plus tests.test_harvest_v5_qualification. Ran 47 tests, OK.

Gate rows 1, 2, 3 and 5 are unclaimed. Row 3 needs this branch's final head sha after CI.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

https://claude.ai/code/session_01JActAZFNBsamTNawK8HS2S
