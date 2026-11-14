# PR #771, gate-ledger row 4 (cold final pass): research lead (Fable 5.2)

Written 2026-11-13 19:23 PST. Head `93f30c3d87c2735088439a2b1b03cbe98046d500`, base `origin/main` `dbd416e19`.

## Verdict: ADMIT WITH FIXES

The content of the PR is right and I would change none of it. It cannot merge at this head, because `quick` is red on four Linux-only failures that this PR brings to `main` (finding 6). One small test-file fix, then a green full run, then merge with a merge commit.

**Read.** RL-144 and its addendum, RL-146, and the runbook's step 17 and §18 (`/Volumes/JW-EXT/scratch/fable-b6-post-pin-runbook.md`; the ruling log at `origin/audit/2026-11-10-fable` `96cc96552`). The row 1 report. In the worktree: the diff of the five M1/M2 test files against `6e6d1b18a`, the diff of `exclusions.py`, `DEVIATION-LOG.md`, the battery reader map and the two pin files against `origin/main`; `test_frozen_files.py` lines 36-110; `b6_r12_runtime.py` lines 520-560; `BootstrapTests` lines 29-140. `gh pr view` and `gh pr checks` for #771. **Ran:** `git`, `shasum`, `gh` reads, one `git merge-tree`, and one line of Python 3.13 printing two `subprocess` attributes. No test, no program. **Not read:** `/Volumes/JW-EXT/b6-custody*`. I edited, committed and commented nothing.

## Findings

1. **M1 does what addendum §3 asked.** [verified]
   - Exempt by name: `PINNED_LITERAL_FILES` holds two full relative paths and the test is `not in` that dict. No prefix, no glob. The second banned literal (`0.009724`) still applies to both files.
   - Each literal equals the registry constant: one captured literal per file, `source.count("0.010818") == 1`, compared with `D125_SCREEN_FLOOR_S` (`calibration_bracketing.py:294`, `Decimal("0.010818")`).
   - The literals are where I read them: `b6_analysis_check.py:50` and `independent_recompute_b6.py:81`. No other copy under `joulewise/` or `scripts/` except the registry's own home and the mint pinset schema, which the guard already handled.
   - No pinned byte changes (finding 4).
   - The registration states it: `block6_replication_DRAFT.md` lines 53 and 386-387 give s_bracket = 10.818 ms, the D-125 floor binding. That closes the one check I left to the lead.

2. **M2 does what addendum §3 asked.** [verified]
   - Deviation row: DLE-13.
   - `EVOLVED_ON_MAIN` and `REBOUND_WORKING_TREE` entries: present, with `ebe1678c…f0ad6`, which is the working-tree hash and a row of the 24.
   - With the file in `EVOLVED_ON_MAIN`, the seal check now reads the Block 5 commit's bytes by `git show`, and the working tree is held to the rebound hash. Both halves bind.
   - The equivalence test is not vacuous. It runs the Block 5 commit's `compute` beside today's on GAMMA, BETA and no pack, with and without `neg8.midpoint_lost`; it asserts the GAMMA case really produces `neg8.midpoint_lost_primary`, and that `pack_scoped=False` differs there and nowhere else.
   - `exclusions.py` differs from `b13a510dc` by exactly the signature lines and the one expression (3 insertions, 1 deletion). No other file under `joulewise/flags/` differs from Block 5.
   - `FROZEN_FILES_TEST_SHA256` is `f6253913…192d`, which is the hash of `test_frozen_files.py` at the head.
   - The release record's one line is on `main` already (record line 161 onward).

3. **DLE-13's text is right.** [verified] The number is correct: `main` ends at DLE-12 and no other remote branch carries a DLE-13. Each factual claim checks against the tree: the commit, the changed expression as quoted, the default's reduction, the single `pack_scoped=False` caller at line 323, the hash, "a row of the 24-file closure", the test's description. "Effect on estimands: none" is correct, and it rightly leaves the pack-scoping question to RL-134's comparator. No edit asked.

4. **Runbook §18 is satisfied at this head, and the merge cannot change that.** [verified]
   - All 24 rows of `closure_sha256` in `main`'s release record: working tree = `HEAD` blob = `b6/analysis-r2` (`6e6d1b18a`) blob = recorded hash. 0 of 24 differ.
   - `origin/main` is an ancestor of the head, so the merge result is the head's tree: `git merge-tree origin/main HEAD` gives `d43120f5b…`, equal to `HEAD^{tree}`. The 24 hashes on `main` after the merge are these, as long as `main` does not move first.
   - The tag is on the remote and peels to `6e6d1b18a`, which is an ancestor of the head.
   - **Two conditions on the merge itself:** use a merge commit, not a squash or rebase, so that `6e6d1b18a` becomes reachable from `main` (the release record says it is not yet, and item 18 is about that). After the merge, re-take the 24 hashes on `main` and put the result in `RUN_STATE.md`.

5. **The two row 1 findings: accept both, no fix.**
   - *String compare in M1.* Both sides are held by a hash already: the two programs are closure rows, and `calibration_bracketing.py` is in `REBOUND_WORKING_TREE`. Neither spelling can change without a cited rebind, and a mismatch fails the test, it does not pass it. A `Decimal` compare would buy nothing.
   - *`git show` in the M2 test.* `test_frozen_files.py` has done the same for the same commit since DLE-3. `b13a510dc` is an ancestor of `main`, so any full clone has it; CI checks out with full history; a shallow clone errors, it does not pass.
   - Row 1's finding 7 (deleting the `REBOUND_WORKING_TREE` row survives `test_frozen_files` and is caught by the clamp pin) is the existing design for the `calibration_bracketing.py` row. Accepted as is.

6. **HOLDS THE MERGE: `quick` is red on four `BootstrapTests` in `tests.test_b6_r12_session_fixture` (Linux). Ruling: skip those four off macOS, in this PR. Do not change the guard.**
   - **Cause, by reading, not by the log** (the job log is not served while the run is in progress; the error text is the lead's account). `b6_r12_runtime.py:543-545` denies the audit event `os.posix_spawn`. CPython 3.13's `subprocess.Popen` goes through `os.posix_spawn` when `os.POSIX_SPAWN_CLOSEFROM` exists, which is the case on current Linux and not on macOS (checked on the Air: `_USE_POSIX_SPAWN` True, `POSIX_SPAWN_CLOSEFROM` absent). So on Linux an allow-listed `Popen` from a guarded child raises a second event that the guard refuses. The guard is too strict there. It is not lax anywhere.
   - **This is not about the 24.** Neither the test module nor `b6_r12_runtime.py` is a closure row, and no test pins the hash of either. The evidence on the audit branch (`evidence/pr762/README.md`) already records that these tracebacks have no frame in the recompute program. §18's "told to me at once" is met by this message; it changes nothing about the release.
   - **Why a skip and not a guard fix.** The R12 fixture simulates a macOS measurement chain and has only ever been run on the two Macs; the module already skips off macOS in four places for the same kind of reason. A Linux pass is evidence of nothing we use. Teaching the guard to tell an allow-listed `Popen`'s spawn from a direct one is new logic in a deny rule, and it would change `b6_r12_runtime.py`, whose hash (`a737c674…`) the R12 run reports cite as the generator of the closed nine. That is more risk and more review than the gain is worth.
   - **The fix, exactly.** `@unittest.skipUnless(sys.platform == "darwin", "<reason>")` on the four failing methods only. `BootstrapTests` has 25 tests; do not skip the class. The reason string says what is true: the R12 guard denies `os.posix_spawn`, which Python 3.13's `Popen` uses on Linux; the fixture runs on macOS only. Key the skip to the platform, not to `POSIX_SPAWN_CLOSEFROM`: if a later macOS Python takes that path, the tests must fail on the Mac, not skip.
   - **Not chosen:** setting `_PYTHON_SUBPROCESS_USE_POSIX_SPAWN=0` for the children. It would work with no skip, but it is a private CPython switch and makes the Linux run test a path nobody uses.
   - **No deviation row.** This is a test-platform matter, not an analysis change. One line in the PR body, citing this report.
   - **After the fix:** run `tests.test_b6_r12_session_fixture` on macOS at the new head, on a host with no live run, and keep the log. Expect the r2 counts (86 OK, 14 skipped). That run is now the only evidence for those four.

7. **The other 37 of the 41 ids: I expect them green, and the full run decides.** `test_install_night_agent.py`, `test_run_night.py` and `test_git_fixture_maintenance.py` are the same blobs as on `main`, and the head contains `main`, so they should behave as they do there. The M1 and M2 ids are fixed by this PR. Shards 7-12 are green; 1-6 were still running when I looked. **Any failing id in the finished run other than the four of finding 6 comes back to me before the merge.** I have not seen the complete list.

8. **Gates.** This PR is class C under RL-144 term 2: the full suite green on the head that merges. `gate-ledger` is red only because the PR body's rows are unfilled. `main`'s own run at `dbd416e19` was still in progress; the run before it was green.

9. **Row 4 on the new head.** This report stands as row 4 for a head whose diff from `93f30c3d8` is only the four skip decorators in `tests/test_b6_r12_session_fixture.py`. Anything wider, or a move of `main` that needs another merge, comes back to me with the diff.

## Merge conditions, in order

1. The four skips (finding 6), pushed.
2. Full suite green on that head, and the macOS run of the fixture module with a kept log.
3. Ledger rows filled; merge by merge commit.
4. The 24 hashes re-taken on `main`, recorded in `RUN_STATE.md`. If one differs, the merge is redone (§18).

## Not verified by me

- The failing tracebacks themselves and the names of the four methods.
- Any test result. Row 1's test tails and mutant table are taken as reported.
- The S-14 line's own files beyond the 24 hashes and row 1's statement that every other differing file is blob-equal to `6e6d1b18a`.
- The PR body.

**Owner.** The lead: the fix, the runs, the merge and the record. Research lead: finding 7's list if it is not empty.
