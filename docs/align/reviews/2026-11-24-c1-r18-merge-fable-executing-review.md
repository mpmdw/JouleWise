# Executing review: merge 909465f32 (ecf718b4d into PR #896)

**Verdict: ADMIT.** No HIGH or MED findings. Two LOW notes, neither a defect of the merge.

- Reviewer: Fable 5.2, cold non-author executing review, 2026-11-24.
- Merge: `909465f32ac9ca202f8c73f239f0252a87ea1fb6`, tree `30a0233a954ccd1b1d34117fa1607a0b400a736a`.
- Parent 1 (PR #896 head): `f00464dcc919dd9f3dc2a4aa34936e81449407c5`.
- Parent 2 (base tip, ops/2026-11-11-w1-presign): `ecf718b4d954064e3c11ab4477a7ee99ecba309d`.
- Merge base: `b2e01464d6d4fbf2901ff4d4154df9455104a12a` (`git merge-base HEAD^1 HEAD^2`).
- Worktree: detached at the merge, clean before and after (`git status --short` empty).
- Inputs: git objects and synthetic test inputs only. No custody, energy, power, meter,
  transcript, slot, hazard, sealed or restricted data was opened. No git or network writes.

## 1. Pure union, no evil merge

Commands and results:

- `git merge-tree --write-tree HEAD^1 HEAD^2` -> `30a0233a954ccd1b1d34117fa1607a0b400a736a`, exit 0
  (no conflicts). `git rev-parse HEAD^{tree}` -> the same id. The recorded tree is exactly the
  automatic 3-way merge of the two parents.
- `git diff --name-only b2e01464d HEAD^1` -> 46 paths; `... HEAD^2` -> 37 paths; 2 paths in both;
  `git diff --name-only b2e01464d HEAD` -> 81 paths = 46 + 37 - 2, and it equals the union of the
  two lists (no path outside them).
- Full-tree classification from `git ls-tree -r` of base, both parents and the merge
  (16038 paths in the merge; blob id and mode compared):

  | Class | Paths | Merge equals |
  |---|---|---|
  | unchanged on both sides | 15957 | base: all |
  | changed only on PR side | 44 | HEAD^1: all |
  | changed only on base side | 35 | HEAD^2: all |
  | changed identically on both | 0 | - |
  | changed differently on both | 2 | 3-way merge, see below |
  | mismatches | 0 | |

- The two both-changed paths, re-derived per file with `git merge-file -p <p1> <base> <p2>`
  (exit 0, no conflicts) and hashed with `git hash-object`:

  | Path | Re-derived blob | Merge blob |
  |---|---|---|
  | configs/b6/executing_reviews.json | d84be5615c1b7c6f2893555051d8c37f266a557b | d84be5615c1b7c6f2893555051d8c37f266a557b |
  | joulewise/align/apple/v4_registration.py | c1d548966aa0c5ba764408f308a24f774fbab3b8 | c1d548966aa0c5ba764408f308a24f774fbab3b8 |

- `joulewise/align/apple/v4_registration.py`: the PR side adds 1227 lines (hunks at base lines
  3-10, 456, 462); the base side adds 3 lines in `_NAMED_ARTIFACTS` (base line 23, commit
  2cc18a831). The hunks do not overlap. Merge vs HEAD^1 is exactly +3 lines; merge vs HEAD^2 is
  exactly +1227 lines. The file parses (`ast.parse`). No conflict markers in either file.

Result: pure union. No content in the merge that is not attributable to one parent.

## 2. configs/b6/executing_reviews.json

Blobs: base f39c852e6, HEAD^1 ef79621ce, HEAD^2 5d0a17c60, merge d84be5615. Checked with
`python3.13 -I` over `git cat-file blob` extracts.

- Parses: yes, a JSON list of 80 rows; every row has keys `change`, `commit`,
  `executing_reviews`, `number_bearing_paths`; every `commit` is 40 hex characters.
- First 15 rows equal the 15 rows at 9bdcf6c95: yes (`rows[:15] == before`, `len(before) == 15`).
- Every commit appears once: 80 rows, 80 distinct commits, no duplicates.
- Exact union: row counts are base 71, HEAD^1 78, HEAD^2 73, shared 71, union 80. The merge's
  row set (canonical JSON per row) equals HEAD^1 union HEAD^2 exactly. All 71 base rows are
  present unmodified in both parents and in the merge.
- Order: HEAD^1's 78 rows are the merge's first 78 rows verbatim; the two rows only the base
  side has (07ebee6c8, 6093a7454) follow as rows 79-80. Each parent's row order is preserved
  as a subsequence of the merge. Diff of the merge against either parent is insertions only
  (28 lines added vs HEAD^1, none removed).
- The merge has no row for 909465f32 itself, as expected before this review is recorded.

## 3. Review-required paths

Path set: the 16 `number_bearing_paths` in configs/b6/registration/acceptance.json (unchanged
by either side) plus the ten verdict/calibration paths named in the task. Commands:
`git diff --name-only b2e01464d <side> -- <paths>` and `git rev-parse <rev>:<path>`.

| Path | Changed by | base | HEAD^1 | HEAD^2 | merge | Merge equals |
|---|---|---|---|---|---|---|
| joulewise/b5/chain.py | PR side | 5b944e3b7 | a1ec520cc | 5b944e3b7 | a1ec520cc | HEAD^1 |
| joulewise/calibration_ledger.py | PR side | b1b3fdf72 | fcd1bbdcc | b1b3fdf72 | fcd1bbdcc | HEAD^1 |
| joulewise/adapters/mlx_runtime.py | base side | 2fa9d24cd | 2fa9d24cd | 0229ac5d1 | 0229ac5d1 | HEAD^2 |

Commits that changed them since the merge base (`git log b2e01464d..<side> -- <path>`):

- joulewise/b5/chain.py (PR side): 3ae356e81, 949298c7c, e6da6a0be, 88139ebff, 765c4a126.
- joulewise/calibration_ledger.py (PR side): 3ae356e81, bc224942e, fcfc0dee4.
- joulewise/adapters/mlx_runtime.py (base side): 07ebee6c8, 6093a7454.

No review-required path was changed on both sides, and no other review-required path differs
from the merge base. All nine of those commits already have rows in the merged ledger.

Coverage listing, reproducing the CI test's query
(`git log --format=%H fda9b380d..HEAD -- <26 paths>`): 51 commits, of which exactly one has no
ledger row: 909465f32 (this merge, listed because it differs from HEAD^1 on mlx_runtime.py and
from HEAD^2 on chain.py and calibration_ledger.py). Adding one row for it closes the listing.

## 4. Tests

Run from the worktree as
`PYTHONPATH=.:tests python3.13 -B -m unittest <module>`, at most four processes at once, about
45 seconds wall time in total. Every module ran; none was blocked by the environment; no skips.

| Module | Result (verbatim) | Exit |
|---|---|---|
| tests.align.test_rl176 | `Ran 28 tests in 1.004s` / `OK` | 0 |
| tests.align.test_rl182_registration | `Ran 4 tests in 0.198s` / `OK` | 0 |
| tests.align.test_protocol_v4_doc | `Ran 8 tests in 0.325s` / `OK` | 0 |
| tests.align.test_measurement_core_boundary | `Ran 7 tests in 0.361s` / `OK` | 0 |
| tests.align.test_apple_endpoint | `Ran 10 tests in 32.935s` / `OK` | 0 |
| tests.test_mlx_runtime | `Ran 44 tests in 0.310s` / `OK` | 0 |
| tests.align.test_c1_closure.C1ClosureTests.test_c2a_finalizer_cannot_pin_a_stray_present_at_finalization | `Ran 1 test in 2.781s` / `OK` | 0 |

Total: 102 tests, 102 passed, 0 failures, 0 errors, 0 skipped.

These six modules are the complete set of test modules the base side changed or added
(`git diff --name-only b2e01464d HEAD^2 -- tests`; the rest of that list is fixtures and one
twin helper).

Not run, by instruction or by design:

- The whole test tree and tests.align.test_c1_closure in full (CI runs them).
- tests/b6/test_audit_record_fixes.py itself. At this commit its coverage assertion is expected
  to fail on 909465f32 until the ledger row citing this paper is added; section 3 reproduces
  its listing query instead.

## Findings

No HIGH. No MED.

- LOW-1 (expected, action for the ledger owner): 909465f32 is the single commit in the
  coverage listing without a row. It needs a row in configs/b6/executing_reviews.json citing
  this paper, with `number_bearing_paths` and wording to the owner's convention (precedent:
  the c84df94bf row, which uses an empty `number_bearing_paths` list). That row is a later
  commit and is outside what this review examined.
- LOW-2 (inherited from parent 1, not introduced by the merge): relative to the merge base,
  the PR side placed its seven new rows (3ae356e81 ... fcfc0dee4) before the base's last row
  5bb152acc rather than after it, so HEAD^1 is not a strict append over b2e01464d. Row
  contents are unchanged and the CI append-only assertion pins only the first 15 rows
  (9bdcf6c95), which hold. The merge reproduces HEAD^1's order verbatim. Informational only.

## Scope limits

This review establishes that the merge is a faithful, conflict-free union of its parents and
that the base-side test modules plus one PR-side spot check pass on the merged tree. It does
not re-review the content of either parent's own commits; those are covered by their own
ledger rows.
