# Freeze blocks by commit, not on main

Status: adopted by Ed 2026-10-30. Phase 0 starts now; phases 1 and 2 follow the block-5 release.
Origin: a senior-engineer review of the repo (Eydono, 2026-10-30) and the repo-trim inventory of the same day.

## The problem

A block is frozen *in place on main* today:
- The block-5 sealed inventory (`configs/campaigns/v5_claim_25g83/sealed_inventory.json`, head `c27485347`) digests
  essentially every file under `joulewise/` and `scripts/`.
- `tests/b5_analysis/test_frozen_files.py` checks main's bytes against those digests.
- Step 5 of the analysis requires HEAD to be contained in `origin/main` (`joulewise/identity_pins.py:858`).
- The live calibration acceptance pins the current bytes of the estimator files
  (`calibration_bracketing.ESTIMATOR_CODE_PATHS`).

So the code that produced a block's numbers has to stay runnable on main indefinitely. Every later change to
anything that code calls has to either duplicate it or stay backwards compatible. In Eydono's words: "That creates
either extreme code duplication or complex and fragile code."

The repo shows both:

| Symptom | Where |
| --- | --- |
| Frozen reducer versions kept alive beside the current one | `reduce.py` 0.5.1 / 0.6.1 next to 0.5.2 / 0.6.2 |
| Old generation as the core of the new | `mint_floor_artifact.py` (v1) loaded by `mint_floor_artifact_generalized.py` |
| Parallel issued versions | `analysis_manifest.py` (v1) and `analysis_manifest_v2.py` |
| Retired code that cannot be deleted | about 31,000 lines of the arm / T-0 chain, plus about 115,000 test lines naming it |
| Edits that move a line break pins | line-number pins over 2,644 test files (`configs/pins/registry.json`) |
| A one-line science fix becoming a mirror | 2026-10-30 prefill clamp: 16 lines in `reduce.py` (sealed, estimator-pinned), so the block-5 fix is a ~440-line analysis-side copy in `whole_window.py` (L9-ENV-3) |
| Copy-pasted verification helpers | about 25 canonical-JSON variants and about 1,570 lines of re-implemented checks (repo-trim §5.2) |

The intent behind the freeze is right: keep every component that produced a science number, so that a defective or
strange number can be re-derived exactly. The mistake is keeping those components *on main*.

## What a freeze must guarantee

1. **Reproducibility.** A block's numbers can be regenerated bit for bit from the exact code, configuration and
   environment that the registration names.
2. **Deliberate change.** Any change to that code after registration is explicit, reviewed and cited to a ruling.
   It never happens silently.
3. **Independence from main.** Development on main cannot disturb a registered block, and a registered block cannot
   constrain development on main.

Git already provides 1 and 2 natively. Our main-bound pins break 3.

## The model

**F1. A block is identified by commits.** The registration records:
- the collection commit sha (H_claim for block 5);
- the analysis commit sha;
- the tree hash of each.

Both commits also get annotated tags:
- `b<N>/collection` and `b<N>/analysis`;
- for a ruled fix, `b<N>/analysis-r<k>`.

The sealed inventory becomes evidence *about that commit's tree*. It is no longer a constraint on main. Tags can be
moved, so the sha recorded in the hashed registration is the authority, and the tag is a convenience.

**F2. Reproduce from a checkout.** Analysis and re-derivation run in a worktree at the block's analysis tag. The
block-5 dry runs already work this way: a detached worktree per attempt. Driver identity checks become "HEAD equals the
registered analysis commit, or descends from it on the block branch through ruled commits". They no longer ask
whether HEAD is in `origin/main`.

**F3. Fix a frozen block on its own branch.** A defect in frozen code is fixed on `block<N>` (branched from the
analysis tag):
- the commit cites the owner's ruling;
- the result is re-tagged `b<N>/analysis-r<k>`;
- the ruling ledger records the old and new tree hashes.

Main gets its own fix independently, with no mirror code and no compatibility layer. That is the "fix the broken
thing" rule (Ed, 2026-10-30) without the blast radius.

**F4. Calibration and estimator pins are commit-scoped.** An acceptance pins `{commit, path: sha256}` and is
evaluated in that commit's checkout. A change to `reduce.py` on main then no longer stales an acceptance that a
registered block uses. New registrations name a new acceptance as usual.

**F5. Data formats are the one real compatibility surface.** New code must still read old bundles, archives and
custody records. Old-format *readers* (or one-way converters with tests against stored samples) stay on main.
Old-format *computation* does not. When in doubt, the test is: does main need this to read data, or only to
reproduce an old number? The second belongs at the tag.

**F6. Pin the environment, not just the code.** Each block tag carries a lock:
- the Python minor version;
- `pyproject` plus a resolved lock file;
- the OS and toolchain notes the registration already records.

Without one, a checkout of an old commit is not truly reproducible.

**F7. Main stays clean.** Once a block is tagged and released, main deletes whatever only that block needed. Test
pins check behaviour, not line numbers.

## Rollout

**Phase 0: now. Additive only; nothing block 5 depends on changes.**
- This note.
- Tag `b5/collection` at `c27485347` (H_claim). Tag `b5/analysis` at the merged commit that official attempt C runs
  on, and re-tag `b5/analysis-r<k>` for any ruled fix after that.
- The block-6 / BYTES registration drafts adopt F1, F4 and F6 from the start. Coordinate with the owning lanes.
- New code is written in the F5 style: readers for old formats, no old computation paths.

**Phase 1: right after the block-5 release.** This is the seam: block 5's own registration was built on the old
model, so it is not amended mid-analysis.
1. Freeze tests switch from "main's bytes equal the seal" to "the tag's tree equals the seal"
   (`git ls-tree` / `git cat-file` against `b5/collection` and `b5/analysis`).
2. The step-5 identity check becomes F2.
3. Calibration acceptance becomes commit-scoped (F4). The D-138 reissue lands with it, together with the parked
   `reduce.py` fixes:
   - A178, the `_anchor_coverage_ok` one-ULP endpoint fix;
   - L9-ENV-2, the corner clamp (`e1b3a0510`).
   One delta refuter tests the two together.
4. Line-number test pins are replaced by behavioural pins, or retired.
5. Block-5 reproduction is rehearsed from a clean clone at `b5/analysis` with the recorded lock. This proves F1, F2
   and F6 before anything is deleted.

**Phase 2: prune.** These run as reviewed PRs grouped by area. Each deletion cites the tag that preserves the code.
- The repo-trim NEEDS-ED list (`TRIM_REPORT.md`): the arm / T-0 chain, the never-live NVIDIA and remote stack, and
  unreachable sealed scripts.
- Frozen reducer versions not needed to *read* data (F5), and analysis manifest v2.
- The L9-ENV-3 `whole_window.py` mirror, which is superseded once main's `reduce.py` carries the clamp.
- Consolidating the duplicated verification helpers onto one canonical implementation each. The independent
  recompute, comparator and twin tools stay separate by design.

## What does not change

- Blinding and custody rules.
- The independent recompute stays independent of L9 code. Redundancy built for independence is not duplication.
- Rulings are still required for changes to registered science. F3 makes them cheaper to apply, not optional.
