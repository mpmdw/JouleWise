# Review of PR #771 (gate-ledger row 1, lens: execute) -- head 93f30c3d8

## Verdict: ADMIT

No blocking or must-fix finding. Two low observations and one informational note below (none need a code change before merge).

## Findings
1. [info, verified] The 24 pinned files are byte-identical. For all 24 rows of `closure_sha256` (origin/main `docs/registrations/block6_release_record.json`), sha256 of the head working-tree file == recorded hash == sha256 of `git show 6e6d1b18a:<path>`. 0 differ. 6e6d1b18a is an ancestor of HEAD.
2. [info, verified] Nothing crept in. Every file that differs from origin/main (dbd416e19) and is not blob-equal to 6e6d1b18a is one of exactly 7: DEVIATION-LOG.md, scripts/test_timings.json, test_frozen_files.py, test_flags_exclusions.py, test_battery_float_sweep.py, test_mint_policy_resolver_guard.py, test_whole_window_inverted_corner_clamp.py. The first two are the merge/DLE-13 and the S-14 line's timing hints, merged with main's keys (additive only); the rest are the M1/M2 test files. `git diff origin/main...HEAD` non-additive entries: only `M` on those 8 paths incl. exclusions.py, no deletes.
3. [info, verified] Conflict resolutions drop nothing. DEVIATION-LOG: HEAD = main's DLE-10/11/12 intact plus the new entry renumbered DLE-13 (diff vs main is +22 lines, additions only); RL-66 F05 paragraph from main kept. Battery reader map: HEAD diff vs main = +3 lines (the S-14 `independent_recompute_b6.py` entry); diff vs the PR's first parent = +7 lines (main's `b5_edge_check.py` entry). Both entries present, so the union is intact.
4. [info, verified] M1 exemption is by exact path. `relative.as_posix() not in PINNED_LITERAL_FILES` (dict of two full relative paths), no glob or prefix. Mutant e2 (same basename in scripts/sub/) was killed.
5. [info, verified] M2 text is accurate against the code. The one changed expression, default reduction, keyword-only signature, sole `pack_scoped=False` caller at `scripts/independent_recompute_b6.py:323`, exclusions.py sha `ebe1678c...` (computed from the tree: matches), and the "24-row closure" claim (it is a closure row; finding 1). The hash of the Block 5 commit's file is different (0902c8af...), as expected for a rebind.
6. [low] M1 equality is a string compare: `str(D125_SCREEN_FLOOR_S) == literal_text`. The Decimal("0.010818") renders "0.010818", so it works today, but a harmless reformat of either side (0.0108180, 1.0818e-2) fails the test even though the value is equal. Not a defect; fails safe. Optional: compare `Decimal(literal)`.
7. [low] `test_frozen_files` alone does not detect deleting the `exclusions.py` row from `REBOUND_WORKING_TREE` (mutant e7: SURVIVED there). It is caught one layer up, because the clamp test pins `test_frozen_files.py`'s own sha (FAILED, 1 failure). Same structure as the existing calibration_bracketing row (DLE-3), so this matches the repo's convention; I note it only because the guard's strength depends on that outer pin.
8. [info] The M2 equivalence test shells out to `git show b13a510dc:...`; it needs full history. All `ci.yml` jobs and gate-ledger use `fetch-depth: 0`, so CI is fine; a shallow local clone would error (CalledProcessError), not pass silently.

## RL-144 addendum §3, item by item
- M1 (after release): guard exempts the two files by name -- done (exact path). Asserts each literal equals the registry constant -- done (`D125_SCREEN_FLOOR_S`, one literal per file, `count("0.010818")==1`). No pinned byte changes -- confirmed (finding 1). "Registration §3.3 states 0.010818" check -- lead's pre-release check; RL-146 records it ("10.818 ms"); I did not open the registration.
- M2: row in DEVIATION-LOG.md -- DLE-13 (renumbered, correct vs main's DLE-11/12). `EVOLVED_ON_MAIN` entry -- done. `REBOUND_WORKING_TREE` entry with sha `ebe1678c...` -- done. One test that default `compute` equals the Block 5 commit's result on a fixture -- done (`Block5DefaultEquivalenceTests`: GAMMA/BETA/None x flag/no flag, default and explicit True; also pins that `False` differs only on GAMMA with the lost flag). Clamp-test pin `FROZEN_FILES_TEST_SHA256` rebound to f6253913 -- done and it passes. Release record carrying "one line saying so" -- already present in RL-146 item 4 text; not part of this PR. Closure-row check for exclusions.py -- done (finding 1).
- Not asked, and left alone: whether recompute and first program should differ in pack scoping (RL-134 comparator).

## Mutant kill table (throwaway worktree, removed afterward; unit modules of the guard under test)
| id | mutation | result |
|---|---|---|
| a1 | `S_BRACKET_S = 0.010819` in independent_recompute_b6.py | KILLED (mint guard) |
| a2 | `0.010819` in b6_analysis_check.py | KILLED (mint guard) |
| b1 | new non-exempt `joulewise/zz_copy.py` with 0.010818 | KILLED |
| b2 | 0.010818 comment added to non-exempt scripts/b5_edge_check.py | KILLED |
| e1 | second 0.010818 inside an exempt file | KILLED (count==1) |
| e2 | `scripts/sub/independent_recompute_b6.py` with 0.010818 (same basename) | KILLED (exact-path) |
| e3 | 0.009724 added to an exempt file | KILLED (second ban still applies) |
| c1 | invert `pack_scoped` condition | KILLED (equivalence test) |
| c2 | default `pack_scoped=False` | KILLED |
| e4 | parameter ignored, always scoped | KILLED (the False-differs assertion) |
| e5 | parameter ignored, never scoped | KILLED |
| d1 | append one line to exclusions.py | KILLED (test_frozen_files) |
| d2 | append one space byte to exclusions.py | KILLED (test_frozen_files) |
| e6 | corrupt the pin hash in test_frozen_files.py | KILLED (clamp test pin; also frozen test) |
| e7 | delete the exclusions.py `REBOUND_WORKING_TREE` row | SURVIVED test_frozen_files; KILLED by clamp test (finding 7) |
Mutants a1,a2,c1,e* were verified to have applied (diff stat nonzero where checked). The first e7 attempt had a non-matching sed (no change); redone with a verified 1-line deletion.
Runner: /Volumes/JW-EXT/scratch/mut771.sh.

## Test tails (head 93f30c3d8, `taskpolicy -b`, python3.13 -B, PYTHONPATH=.:tests)
- b5_analysis.test_frozen_files: Ran 4 tests in 0.871s -- OK
- tests.test_mint_policy_resolver_guard: Ran 2 tests in 0.055s -- OK
- tests.flags.test_flags_exclusions: Ran 35 tests in 0.716s -- OK
- tests.test_whole_window_inverted_corner_clamp: Ran 34 tests in 138.821s -- OK
- tests.test_battery_float_sweep: Ran 5 tests in 7.541s -- OK

## Not checked
- Registration §3.3 text itself (read RL-146 and the code only).
- No full suite, no CI logs, no other modules importing the touched files beyond the grep of `0.010818`/`pack_scoped` under joulewise/ and scripts/ (only the expected sites).
- Did not read /Volumes/JW-EXT/b6-custody*; no ssh; no GitHub writes. Source worktree untouched (status clean). Mutant worktree rev-pr771-mut removed.
