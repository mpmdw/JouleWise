## PROGRESS
- Done: all six findings dispositioned; F1 old-code counterfactual fails at index 12, corrected real-runner regression passes every collection in both modes; independent span/unit/payload/CLI checks pass; original report corrected.
- Done: 4 focused tests, 2 identity/full-path tests, 4 kit tests, 23 refusal-census tests (1 skip), generator --check; diff whitespace clean. Read-only real-H span derivation complete.
- Next: director commits this slice, runs real dry prepare and staged r12 dry-run, then CI/final review.
- Open: import-graph suite has one environment failure (host process-group census unavailable in sandbox); report below. No install, arm, launchctl or real measurement performed. No local task process remains.

## SUMMARY
- r12's local manifest index becomes 1; run_id, rep and config bytes stay r12.
- Only index requires contiguity in load_order_entries; block_index and position_in_block are integer-checked, sentinel_position is string-read, so remain unchanged.
- Removed unrelated 1191 s allowance; post now prints 215 + 20 + 1 s.
- Desk verdict and backup print as 0 s outside the chain span.
- Remainder checks/flags derive four identity units from dispatched config model sources and roster plus NEG-8.
- Explicit remainder-only CLI options without --remainder produce named flags.
- Corrected original report and arm packet; real prepare/CI/arming remain director-owned.

## FIX LOG
1. FIXED in code: local index 1 before manifest write/hash; real runner regression PASS (4-test focused command, both modes). Old-code counterfactual FAIL as required: 1 test, 78.640 s, rc 1; r12 runner rc 2, `indexes must be contiguous 1..1 (found [12])`. Full mode passed before that failure. No other positional-field change required.
2. FIXED: removed fixed_s term, post parts independently asserted [215,20,1], margin remains member-only. Read-only H journal arithmetic below.
3. FIXED operational documentation: lead clears seat TMPDIRs and finished worktrees, then df immediately before prepare; below-P refusal is correct. No cleanup of unrelated files here.
4. FIXED: derive units before session-root creation and reuse for flags. Tests assert four-unit identity/flag equality and missing-payload root absence; PASS in the 4-test focused command; additional real-kit identity/full-path tests PASS (2 tests). Full path retains all units.
5. FIXED: optional --soak-70b defaults None; resolve full at invocation. CLI test covers both ignored options and remainder default; PASS in the 4-test focused command.
6. FIXED documentation: prepare 6–13 s under Mac load (reviewer, 2026-10-22). r12 offered with mandatory director staged-soak dry-run before arm.

## SPAN
Read-only arithmetic from real H journals, not live evidence or a real prepare. Each stage contributes base + margin*member seconds, margin 0.039793375558773825. Prefix short stage/member IDs below with bytes-mac-check-. Six-decimal display; JSON retains precision.

### full

| Stage / term | Base s | Member s | Margin s | Total s | Source |
|---|---:|---:|---:|---:|---|
| bracket-reservation | 1.000000 | 0.000000 | 0.000000 | 1.000000 | bracket-reservation |
| pre-calibration | 227.000000 | 0.000000 | 0.000000 | 227.000000 | pre-calibration, pre-calibration.screen, pre-calibration.window-calibration-verdict |
| bound-collection | 2442.000000 | 2271.183127 | 90.378043 | 2532.378043 | bound-collection, bound-collection.retry-decision |
| bound-derivation | 719.000000 | 0.000000 | 0.000000 | 719.000000 | bound-derivation.corpus, bound-derivation |
| reference-start | 397.000000 | 379.363332 | 15.096148 | 412.096148 | reference-start |
| test7-llama-70b-start | 807.000000 | 781.371997 | 31.093429 | 838.093429 | test7-llama-70b-start |
| test7-qwen35-122b-start | 649.000000 | 623.024698 | 24.792256 | 673.792256 | test7-qwen35-122b-start |
| test7-qwen3-next-80b-start | 598.000000 | 571.416020 | 22.738572 | 620.738572 | test7-qwen3-next-80b-start |
| reference-midpoint | 128.000000 | 127.715171 | 5.082218 | 133.082218 | reference-midpoint |
| soak-llama-70b | 3331.327781 | 3160.510908 | 125.767398 | 3457.095178 | soak-llama-70b-r01, soak-llama-70b-r02, soak-llama-70b-r03, soak-llama-70b-r04, soak-llama-70b-r05, soak-llama-70b-r06, soak-llama-70b-r07, soak-llama-70b-r08, soak-llama-70b-r09, soak-llama-70b-r10, soak-llama-70b-r11, bound-collection: measured collection residual |
| soak-qwen35-122b | 2372.714790 | 2201.897917 | 87.620951 | 2460.335740 | check-qwen35-122b-r01, check-qwen35-122b-r02, check-qwen35-122b-r03, check-qwen35-122b-r04, check-qwen35-122b-r05, test7-qwen35-122b-start-r01, test7-qwen35-122b-start-r03, bound-collection: measured collection residual |
| test7-llama-70b-end | 807.000000 | 781.371997 | 31.093429 | 838.093429 | test7-llama-70b-start |
| test7-qwen35-122b-end | 649.000000 | 623.024698 | 24.792256 | 673.792256 | test7-qwen35-122b-start |
| test7-qwen3-next-80b-end | 598.000000 | 571.416020 | 22.738572 | 620.738572 | test7-qwen3-next-80b-start |
| reference-end | 397.000000 | 379.363332 | 15.096148 | 412.096148 | reference-start |
| post-calibration | 236.000000 | 0.000000 | 0.000000 | 236.000000 | pre-calibration, joulewise.b5.chain.CALIBRATION_ARM_COUNTDOWN_S['post'] - ['pre'], session-status: upper endpoint of integer shell stamp [0, 1), derive_sizing.py stamp convention |
| whole-window-verdict | 0.000000 | 0.000000 | 0.000000 | 0.000000 | joulewise.b5.chain.DESK_KINDS |
| backup | 0.000000 | 0.000000 | 0.000000 | 0.000000 | joulewise.b5.chain.DESK_KINDS |
| registered settle before pre-calibration and each collection | 0.000000 | 0.000000 | 0.000000 | 780.000000 | joulewise.b5.chain.SETTLE_S |

Programmed span 15635.331989693057 s; printed ceiling 15636 s; window_max_s 33360 s.

### r12

| Stage / term | Base s | Member s | Margin s | Total s | Source |
|---|---:|---:|---:|---:|---|
| bracket-reservation | 1.000000 | 0.000000 | 0.000000 | 1.000000 | bracket-reservation |
| pre-calibration | 227.000000 | 0.000000 | 0.000000 | 227.000000 | pre-calibration, pre-calibration.screen, pre-calibration.window-calibration-verdict |
| bound-collection | 2442.000000 | 2271.183127 | 90.378043 | 2532.378043 | bound-collection, bound-collection.retry-decision |
| bound-derivation | 719.000000 | 0.000000 | 0.000000 | 719.000000 | bound-derivation.corpus, bound-derivation |
| reference-start | 397.000000 | 379.363332 | 15.096148 | 412.096148 | reference-start |
| test7-llama-70b-start | 807.000000 | 781.371997 | 31.093429 | 838.093429 | test7-llama-70b-start |
| test7-qwen35-122b-start | 649.000000 | 623.024698 | 24.792256 | 673.792256 | test7-qwen35-122b-start |
| test7-qwen3-next-80b-start | 598.000000 | 571.416020 | 22.738572 | 620.738572 | test7-qwen3-next-80b-start |
| reference-midpoint | 128.000000 | 127.715171 | 5.082218 | 133.082218 | reference-midpoint |
| soak-llama-70b | 434.192782 | 263.375909 | 10.480616 | 444.673398 | soak-llama-70b-r01, soak-llama-70b-r02, soak-llama-70b-r03, soak-llama-70b-r04, soak-llama-70b-r05, soak-llama-70b-r06, soak-llama-70b-r07, soak-llama-70b-r08, soak-llama-70b-r09, soak-llama-70b-r10, soak-llama-70b-r11, bound-collection: measured collection residual |
| soak-qwen35-122b | 2372.714790 | 2201.897917 | 87.620951 | 2460.335740 | check-qwen35-122b-r01, check-qwen35-122b-r02, check-qwen35-122b-r03, check-qwen35-122b-r04, check-qwen35-122b-r05, test7-qwen35-122b-start-r01, test7-qwen35-122b-start-r03, bound-collection: measured collection residual |
| test7-llama-70b-end | 807.000000 | 781.371997 | 31.093429 | 838.093429 | test7-llama-70b-start |
| test7-qwen35-122b-end | 649.000000 | 623.024698 | 24.792256 | 673.792256 | test7-qwen35-122b-start |
| test7-qwen3-next-80b-end | 598.000000 | 571.416020 | 22.738572 | 620.738572 | test7-qwen3-next-80b-start |
| reference-end | 397.000000 | 379.363332 | 15.096148 | 412.096148 | reference-start |
| post-calibration | 236.000000 | 0.000000 | 0.000000 | 236.000000 | pre-calibration, joulewise.b5.chain.CALIBRATION_ARM_COUNTDOWN_S['post'] - ['pre'], session-status: upper endpoint of integer shell stamp [0, 1), derive_sizing.py stamp convention |
| whole-window-verdict | 0.000000 | 0.000000 | 0.000000 | 0.000000 | joulewise.b5.chain.DESK_KINDS |
| backup | 0.000000 | 0.000000 | 0.000000 | 0.000000 | joulewise.b5.chain.DESK_KINDS |
| registered settle before pre-calibration and each collection | 0.000000 | 0.000000 | 0.000000 | 780.000000 | joulewise.b5.chain.SETTLE_S |

Programmed span 12622.910209347223 s; printed ceiling 12623 s; window_max_s 30360 s.

Post parts: H stage_id exactly bytes-mac-check-pre-calibration: 215 s; chain.CALIBRATION_ARM_COUNTDOWN_S['post'] - ['pre']: 20 s; session-status: 1 s from integer shell stamp [0,1) upper endpoint (derive_sizing.py stamp convention). No pre screen/verdict in post. Director cross-check of B6 r1-alpha/beta/gamma, r2-beta/gamma, r3-alpha: post capture 236–238 s plus session-status 0–1 s versus pre capture 215–217 s. Cross-check only, not code input.
Settles: 13 * chain.SETTLE_S = 780 s. Table settle row's base/member columns are inapplicable. Margin and residual derivations unchanged: max(max/min-1) identical-config cohorts, and max(stage wall - member sum) = 170.81687259674072 s (H bound collection).
Full-kit registered sizing and generated bytes remain untouched.

## TESTS RUN
Every test command used its own fresh TMPDIR, repository cwd, and JW_B5_SYNTHETIC_ONLY=1. Exact commands:

```sh
JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byh2f1.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_h_session.SessionTests.test_remainder_every_staged_directory_real_runner_dry_run
```
Old code (test added before implementation): 1 test, 78.640 s, exit 1, one expected r12 subtest failure. Full mode passed; r12 soak runner rc 2 with contiguous-index error. This run imported the old implementation before it was edited.

```sh
JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byh2f1.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_h_session.SessionTests.test_remainder_every_staged_directory_real_runner_dry_run tests.test_bytes_h_session.SessionTests.test_remainder_missing_payload_leaves_session_root_absent tests.test_bytes_h_session.SessionTests.test_cli_remainder_options_flagged_without_remainder tests.test_bytes_h_session.SessionTests.test_prepare_uses_real_writer_without_install_or_loop_registration
```
4 tests, 93.866 s, exit 0, OK, no skips. Includes independent term-by-term math, both modes' real plan/chain, ledger hashes, all 24 staged collection runner subprocesses, exact counts, flags and payload hazard.

```sh
JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byh2f1.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_h_session.RealKitStagingTests.test_remainder_view_preserves_order_member_bytes_and_reference_roles tests.test_bytes_h_session.SessionTests.test_prepare_uses_real_writer_without_install_or_loop_registration
```
2 tests, 1.301 s, exit 0, OK. Added exact index/rep/config hash/positional-field preservation and full path's 11 runtime flags assertions.

```sh
JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byh2f1.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_bytes_mac_kit
JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byh2f1.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.hazards.test_refusal_allowlist
JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byh2f1.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.hazards.test_import_graph
JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byh2f1.XXXXXX) /opt/homebrew/bin/python3.13 -B scripts/bytes_mac_kit.py --check
git diff --check
```
Kit: 4 tests, 1.230 s, exit 0, OK. Refusal census: 23 tests, 82.543 s, exit 0, OK (1 existing skip: the block-5 design branch is not in this clone). Import graph: 6 tests, 6.833 s, exit 1, 5 pass / 1 environment failure: `test_a_complete_arm_and_monitor_run_load_no_retired_module` expects GO but gets NULL. Isolated synthetic Rig inspection confirmed `instrument REFUSE: the capture's process group was not proven gone: census_exit_3: sysmon request failed with error: sysmond service not found; pgrep: Cannot get process list`. Hardware seams are fake; no real arm occurs. Per local environment instructions this macOS process-group failure is reported, not chased or bypassed. Generator: exit 0, `verified non-claim Mac kit`. Diff check: exit 0.
No full module/repository suite or harvest rerun: slice instructions forbid the long module; desk/harvest code is unchanged. Director/CI own remaining coverage. Tests.test_bytes_gates not required because desk did not change.

Read-only real-H arithmetic command: `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /tmp/jwtmp-byh2f1.XXXXXX) /opt/homebrew/bin/python3.13 -B -` with Python loading original plan tree, removing check stages, selecting soak expected_count 12/1, and calling `h.remainder_span(h.ROOT, subset, Path('/Users/edr/night-bytes/h-20261021T185555Z'))`; exit 0, full 15635.331989693057 / 33360; r12 12622.910209347223 / 30360. No files read under the forbidden custody root.

## END-TO-END
Production-shaped appendix fixture passes through real plan writer and chain.stage_plan in both modes; synthetic identity producer and ledger-head seam only. Runner subprocess regression checks every staged collection directory, rc and exact member count (73 full / 62 r12). PASS: STAGED in both modes; all 12 collection directories per mode returned rc 0 and exact counts [18,3,4,4,4,1,12-or-1,12,4,4,4,3]. No fallback to loader APIs needed. P remained 63878576237 B full / 56122258559 B r12, identity units exactly {llama-70b,qwen35-122b,qwen3-next-80b,neg8_reference}, session prefix bytes-h2-. Independent hand arithmetic checks every span term and window_max_s; printed stage list order/counts and source ledger hashes match. Ledger hash assertions remain in place; no real ledger writes.

## DECISIONS I MADE
- Leave non-index positional fields unchanged because runner requires no contiguity for them.
- Separate fast prepare/runner regression from the existing prepare/harvest regression using a common fixture helper, so focused slices can verify production parsing without repeating harvest.
- No generator, committed kit, registry or desk change needed.

## OPEN ISSUES
Director must rerun real dry prepare and staged r12 runner dry run, confirm disk >= P immediately before prepare, run CI and own final verification/arm decision. No real prepare/install performed here. No commits or pushes attempted (.git read-only).

## NEEDS_RULING
none
