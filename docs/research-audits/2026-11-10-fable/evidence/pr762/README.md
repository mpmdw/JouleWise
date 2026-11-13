# PR #762 (b6 S-14 r2, head aaa2f3086): merge evidence under the RL-144 addendum §1

Lead (Opus 5.5), 2026-11-13 15:56 PST. RL-142 §2 item 5's "merge on both green" is replaced by the RL-144 addendum §1's four conditions (base 3551e1a7d cannot be green).

| Addendum §1 | Evidence |
|---|---|
| 1. mint guard + frozen_files: head ids = base ids | reproduced locally on 3551e1a7d before the pause (s14 owed list 14:58) |
| 2. test_b6_r12_session_fixture | macOS at head aaa2f3086, clean worktree, py3.13: 86 OK, 14 skipped (= base); hosted tracebacks are posix_spawn PermissionError with no frame in RC-B6-1 |
| 3. tests of the changed file green at head on macOS | premerge-macos.log §A: tests.independent_recompute.test_block6 + test_b6_production, Ran 62, OK. Mutant (fix reverted): both new tests fail (PR body). Kit e2e at r2: 8 OK (rl144-premerge step 3, before the pause). Release tools at f19f36081 (§B): test_b6_release_record + test_b6_structure_probe, Ran 40, OK |
| 4. Opus delta check, no blocker | opus-delta-review.md: PASS-WITH-NITS (finding 9 closed by the RL-142 comparer + J-item rulings) |

## Full hosted run 43521257617 (failure): every failing id classified (addendum §2 item 2)

| Module | CI ids | Class | Evidence |
|---|---|---|---|
| b5_analysis.test_frozen_files | 2 | base-inherent, reproduced on 3551e1a7d | addendum §3 M2 |
| test_mint_policy_resolver_guard | 4 | base-inherent, reproduced on 3551e1a7d | addendum §3 M1 |
| test_b6_r12_session_fixture | 8 | platform (passes on macOS at r2, 86 OK/14 skipped) | addendum §1 item 2 |
| test_git_fixture_maintenance | 1 | base-inherent, reproduced on 3551e1a7d (macOS: same 1 FAIL at head and base) | premerge-macos.log §C |
| test_install_night_agent | 55 | platform (macOS at r2: Ran 67, OK; base same) | premerge-macos.log §C |
| test_run_night (NightDriverTests installer ids) | 8 | platform (none of the 8 fails on macOS at r2) | premerge-macos.log §C |

Unexplained: none. Named set (test_block6, b6_analysis_check/production, b6_release_record, structure probe, kit e2e): no failing id.

Side note, not a CI id: on macOS under taskpolicy -b, test_run_night has 7 failures (BindSupervisionProcessTests x6, QuietDriverIntegrationTests x1), identical at head and base: base-inherent, outside the diff; routed to the CI owed list.

Comparer test section §D errored on the runner's invocation (-I drops cwd); the comparer of record (v2, eb82b6e2…) passed 18/18 with discover (rl142-r2-records.md §F).
