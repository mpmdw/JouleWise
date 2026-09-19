# Record 60 — full sharded replay at the Stage A head `087bf3af` (branch worktree, untouched during the run), lead, 2026-09-19 13:50–14:50 PDT

`shard_tests.py --workers 4 --split`; log `60-full-replay-stagea.log.gz`; rc 1. **6,519 tests, 244 modules, 241 OK, three failures:**

1. `test_arm_readiness_evidence_t0.test_g4_real_ruled_census_pgrep_dialect` — the real-process census parsed a live delegated seat's multi-line argv (this activation's Stage A refuters and the fix seat were alive); environmental, the TEST-PGREP-DIALECT-MULTILINE-01 class; re-run alone passes (records 34/22 precedent).
2. **`test_arm_retry.test_both_document_blocks_are_exact` — REAL.** `docs/process/NIGHT_HANDBACK.md` carries a GENERATED policy block rendered by `joulewise/arm_retry.render_policy()`; seat 46 part 2 hand-edited the refusal row inside that block (`night_refused_registration` | "The registration digest is not in the ruled…" vs the rendered "Required registration did not validate."). Ruled fix (round 2): the refusal row's text belongs in `arm_retry`'s refusal table (source of truth), re-rendered into the handback; the hand edit is reverted; `tests/test_arm_retry.py` pins the new row through the renderer.
3. **`test_git_fixture_maintenance.test_every_test_module_routes_git_initialization_through_shared_helper` — REAL.** `tests/test_gen_evidence_night.py:41` initializes a git repository directly instead of through `tests/git_fixture.init_git_fixture`. Ruled fix (round 2): route it through the shared helper.

Both real findings are what row 9 exists to catch (module-level runs were green; only the full suite sees the cross-module pins). They go to fix round 2 (brief 65) immediately after round 1 lands, and the delta re-audit (brief 64) covers both rounds.
