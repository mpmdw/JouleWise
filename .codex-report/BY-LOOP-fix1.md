## PROGRESS

- Done: intake (no active stop card), clean baseline 270705580; F1 production-row regression and status correction implemented.
- Done: F3a replication pack_ids and scratch-root resume regression; F3b resolved-root environment export and explicit commands in wake brief.
- Done: F2 labels/bootstrap rc and regression; F5 pass-order equality test; F4/F6/F7 records.
- Done: all requested module commands completed; smoke 22, loop 64, lane_adapters 21, bytes_packs 9, bytes_mac_kit 4, bytes_h_session 32, refusal_allowlist 23 (1 skip), rehearsal 1 pass; bytes_plan_trees --check passes.
- Done (director): import_graph re-run outside the sandbox (6 OK), diff reviewed, fails-before re-checked on 270705580, real-data replay of F1; committed and pushed. See DIRECTOR VERIFICATION.
- Open: none for the seat. No scope request.

## SUMMARY

Findings 1–3 implemented with baseline failures and post-fix passes; findings 4–6 fixed in records/tests; finding 7 rejected per binding report-path rule. Smoke, loop, lanes, pack and Mac-kit readers, refusal allowlist and stub-launch rehearsal pass. H-session reader passes (32 tests). Import-graph sandbox failure needs director rerun. No sealed file changed; no measurement, real launchctl, commit, or network operation run.

## FIX LOG

1. Fixed: smoke.py uses campaign row statuses ok/failed/skipped; no production campaign-row writer of succeeded was found (member status succeeded is distinct). New anchor_ok_companion passes only after fix; explicit nonproduction succeeded companion is a negative case. Existing usable-companion rows did not exist in this regression. Full module passes (22 tests).

2. Fixed: lanes.py labels include sanitized resolved-root basename, path digest, and sequence; bootstrap_rc and job_label are persisted. Nonzero bootstrap remains a record, never a refusal. Tests use only injected runners. Machine-test wake labels updated.
3. Fixed: loop.json restricts discovery to alpha/beta/gamma; new scratch-root CLI resume regression rejects BYTES while DONE and still resumes alpha. b6_wake.zsh exports resolved JW_B6_LOOP_ROOT before exec; every wake-brief loop command names the root.
4. Fixed records: lane report SUMMARY/REHEARSAL and round_support stub comment disclose stubbed launch and blocking BY-SLOTS/BY-PIN launch bindings plus required real-launch rehearsal before arm.
5. Fixed: loop bytes base_order and pack_ids checked against registered passes 1 then 2.
6. Fixed records: wake brief close row states registered-pack closure and explicit resume after later pass-2 registration.
7. Rejected with reason: report path .codex-report/BY-LOOP.md follows binding brief rule 1/harness path. Earlier director grants for tests/hazards/test_monitor.py and tests/fixture_signatures.json remain recorded. BY-MERGE: reviewer reports no lane changes to 682 sealed paths/all hashes equal bda481d5a; BY-INT base already differs on 30 sealed files versus 5 on main, predating this lane. Independent diff check confirms 682 paths unchanged from BY-INT, including working tree; 30 existing inventory-digest mismatches.

## TESTS RUN

All commands use repository cwd and fresh scratch TMPDIR.

- Initial mistaken SmokeTests selector used DeskTests: 1 loader error, exit 1; corrected immediately.
- Before changing smoke.py (still 270705580 code): `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /private/tmp/jwtmp-byloop.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.b6.test_smoke.SmokeTests.test_desk_idle_loss_requires_exact_dispatch_records_and_campaign_exit`: 1 test / 21 subcases, exit 1. anchor_ok_companion: fail != pass; nonproduction succeeded companion: pass != fail; all other subcases behaved as expected.

- F1 after fix: same corrected focused command, 1 test / 21 subcases, 0.324s, exit 0.
- F3a before config fix: `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /private/tmp/jwtmp-byloop.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_b6_loop.LoopTests.test_replication_resume_rejects_bytes_without_reopening_done_root`: 1 test, exit 1, ValueError not raised on baseline config.

- F3a after fix: same focused command, 1 test / 0.007s, exit 0.
- F2 before lanes.py fix: `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /private/tmp/jwtmp-byloop.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest tests.test_b6_loop.LoopTests.test_wake_labels_are_root_unique_and_bootstrap_failure_is_recorded`: 1 test, exit 1 (missing bootstrap_rc).

### Module commands and current results

Each row is the exact command `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /private/tmp/jwtmp-byloop.XXXXXX) /opt/homebrew/bin/python3.13 -B -m unittest MODULE`, with MODULE below; fresh TMPDIR per module:

| MODULE | Tests | Result |
| --- | ---: | --- |
| tests.test_b6_loop | 64 | exit 0, 5.085s |
| tests.b6.test_lane_adapters | 21 | exit 0, 0.271s; placeholder test passes |
| tests.b6.test_bytes_packs | 9 | exit 0, 1.548s |
| tests.test_bytes_mac_kit | 4 | exit 0, 0.184s |
| tests.test_bytes_h_session | 32 | exit 0, 100.896s |
| tests.b6.test_smoke | 22 | exit 0, 52.787s |
| tests.hazards.test_refusal_allowlist | 23 | exit 0, 14.859s; 1 skip: absent block-5 design branch |
| tests.b6.test_loop_round_desk.RoundTests.test_bytes_guard_shaped_rehearsal | 1 | exit 0, 12.090s; stub launch, scratch only |
| tests.hazards.test_import_graph | 6 | exit 1, 3.080s; one NULL vs GO, pending director re-run |

`JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /private/tmp/jwtmp-byloop.XXXXXX) /opt/homebrew/bin/python3.13 -B scripts/bytes_plan_trees.py --check`: exit 0, verified 12 draft registrations and 12 fixed pass trees.

Supplemental combined loop + lane_adapters invocation with the same environment/prefix: 85 tests, 5.170s, exit 0. This preliminary run shared one TMPDIR; canonical individual module reruns above each used their own fresh TMPDIR.


F2 post-fix regression passes within the 64-test loop module; root labels differ even with the same basename; neither label matches the legacy-label regex, and rc 7 is persisted. `git diff --check` and `/bin/zsh -n scripts/b6_wake.zsh` exit 0. No measured threshold or tolerance introduced. Refusal allowlist passes unchanged; no refusal-census arrays or entries were changed. `JW_B5_SYNTHETIC_ONLY=1 TMPDIR=$(mktemp -d /private/tmp/jwtmp-byloop.XXXXXX) /opt/homebrew/bin/python3.13 -B -m tests.hazards.refusal_census` exits 0 with unlisted=[], stale=[], miscounted=[], guard_changed=[], scope_gaps=[].

## SEALED INVENTORY

`git diff --name-only bda481d5a HEAD`, `git diff --name-only bda481d5a` (including working tree), and `git diff --name-only 270705580` each intersect the 682-path inventory in zero paths. Independent Git-blob hashes of every current sealed file equal bda481d5a (682 checked, zero mismatches). Current SHA-256 versus frozen inventory has 30 mismatches, all inherited from BY-INT. The reviewer reports main had 5, recorded as reviewer evidence rather than reinterpreting this lane's delta.

Check used /opt/homebrew/bin/python3.13 -B with json inventory files, subprocess git diff and git ls-tree -r bda481d5a, SHA-1 of Git blob headers/current bytes, and SHA-256 current bytes. An unrelated attempted import of nonexistent refusal_census.census then failed; inventory output above had completed.

## DECISIONS I MADE

- Replace the nonexistent campaign-row success status succeeded with production ok, rather than retaining succeeded as usable. Retain succeeded only as a deliberately invalid negative fixture and for actual member statuses.

- Wake labels use a basename sanitized to ASCII alphanumerics/underscore/hyphen (40 characters for readability), SHA-256 path digest (16 hex characters to distinguish roots), and sequence. These are identity formatting choices, not measured tolerances. Existing integer-only labels cannot collide.

## OPEN ISSUES

- Lead may boot out stale com.joulewise.b6wake.1/.2 at BYTES install (machine-test precondition 5); new labels make them harmless.
- BYTES launch blocked until BY-SLOTS/BY-PIN bindings land and a real-launch scratch rehearsal passes.
- BYTES close covers registered packs; later pass-2 registration requires explicit root-specific resume.
- import_graph: sandbox-only failure (NULL instead of GO, process list denied); director re-run outside the sandbox passes 6/6.
- (Director.) run_campaign.py also writes row status "waived" (and "timeout", "incomplete_existing"); smoke.py does not count a waived companion as usable, so an anchor-only rc 1 beside a waived companion still holds the smoke (a possible false hold, never a false pass). Not changed here; the reviewer did not raise it, and none of the 26 block-6 smoke campaign_log.jsonl files under /Users/edr/night-b6 has a "status": "waived" value (director grep, read-only).
- All local requested checks completed; no other implementation or scope blocker. Director owns final verification/commit/push. Branch by-loop, HEAD remains 270705580091c31472d9ff8452705ca564829c1b; existing draft PR #542 not accessed (no network).

## NEEDS_RULING

none

## DIRECTOR VERIFICATION (lead, Opus 5.5, outside the sandbox, 2026-10-22 ~18:20Z)

- Diff reviewed file by file; every changed path is in this round's WRITE_SCOPE (the round's grants: lanes.py,
  test_lane_adapters.py, b6_wake.zsh, b6_wake_brief.md, block6_machine_test.md, BY-LOOP-fix1.md).
- Module re-runs from the clone, fresh /private/tmp TMPDIR each, JW_B5_SYNTHETIC_ONLY=1: tests.hazards.test_import_graph
  6 OK (the seat's sandbox NULL-vs-GO failure does not reproduce); tests.test_b6_loop 64 OK; tests.b6.test_lane_adapters
  21 OK; the smoke anchor test (21 subcases) OK; RoundTests.test_bytes_guard_shaped_rehearsal OK (10.0 s).
- Fails-before, re-checked in a scratch worktree at 270705580 with only the new test files copied in:
  smoke anchor test FAILS (anchor_ok_companion 'fail' != 'pass'; anchor_nonproduction_status 'pass' != 'fail');
  test_replication_resume_rejects_bytes_without_reopening_done_root FAILS (ValueError not raised);
  test_wake_labels_are_root_unique_and_bootstrap_failure_is_recorded and test_waker_binds_record_path_without_starting_a_job
  ERROR (KeyError 'bootstrap_rc'). All pass on the fixed tree.
- F1 on real data: the reviewer's read-only replay (statuses and classes only, no energies) over the block-6 smoke
  directories with the fixed smoke.py: r2-alpha-smoke-0 campaign classes are now {usable: 3, anchor: 1} (the reviewer
  saw the 3 `ok` members classed failed before the fix) and stages_succeeded is True; the other nine sessions have no
  failed stage. (The replay script then stopped on a machine-test directory with no smoke-result.json, a script
  limit, not a code fault.)
- b6_wake.zsh: session_argv (scripts/magistrate_watchdog.py:2204) builds a plain argv and os.execv inherits
  os.environ, so the woken claude session gets JW_B6_LOOP_ROOT; scripts/b6_loop.py:33 reads it as the --loop-root
  default. live_run returns a CompletedProcess, so bootstrap_rc is a real integer in production.
- No new tolerance or threshold on a measured quantity; refusal census unchanged (seat run: all arrays empty).

