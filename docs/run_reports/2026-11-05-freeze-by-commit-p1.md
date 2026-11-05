# A346 FREEZE-BY-COMMIT-01 — Phase-1 preparation, 2026-11-05

Status: APPLIED_UNVERIFIED / LOCAL_ONLY. Requested branch and commits could
not be created because the session policy makes `.git` read-only. No push,
network operation, release, merge, pipeline invocation or data access.
Base: `92026c1849c0f053e56bdac6110c079211db2c31` (detached HEAD).
Requested branch: `lane/2026-11-05-freeze-by-commit-p1`.

## Intake and authority

Read AGENTS.md, CLAUDE.md, Mission M0, the generated restart region (no active
stop card), current status/workspace notes, the A346 queue/kernel row and
Do-Not-Do-Yet list. Read the F1–F7 rollout, TRIM_REPORT, RUN_STATE 145–146,
D-138 and its implementation notes, and the D-188–D-190 release/rebind context.
The user's brief authorizes preparation before release; landing remains after
release. No Phase-2 pruning is performed.

## Changes

- New `joulewise/freeze_by_commit.py` and
  `configs/analysis/b5/freeze_commits.json`: annotated tag objects, peeled
  commit IDs and trees; batch Git-blob hashing; exact r2 or completely ruled
  descendant identity. Side-branch commits are included. A clean ruled
  checkout can load its ledger from a separately pinned later registration
  commit, avoiding a self-reference in its own tree. Missing history,
  malformed rulings and moved/lightweight tags fail closed. No remote query
  is needed.
- `tests/b5_analysis/test_frozen_files.py`: full sealed inventory at collection,
  each historical harvest pin at its own commit, and sealed documents at the
  original analysis and r2 trees. A regression forbids source worktree reads.
- `joulewise/identity_pins.py`, `joulewise/paper_custody.py`: custody requests
  registered analysis identity through the mint's existing clean-tree gate.
  No estimator or result arithmetic changes. The old keyword is an F2 alias.
- `scripts/digest_pin_census.py`, `scripts/repin.py`,
  `configs/pins/registry.json`: 335 Python test locations in 77 holders become
  content locations, preserving target methods, all counts and all families.
  Migrated from existing registry plus explicit test-source blobs; **did not
  run the whole-tree census**, which can read evidence forbidden by the brief.
- `tests/test_freeze_by_commit.py`, `tests/test_digest_pin_census.py`,
  `tests/test_repin.py`: constructed-Git and line-motion regressions.
  `tests/b5_analysis/joined_s10.py`: fixture annotated tag/registration feeds
  the real predicate. No joined driver or pipeline ran in this session.
- `docs/process/freeze_p1_rebind.md`: authority, exact per-file release/new
  digests, calibration stub and remaining gates. Kernel/generated queue and
  restart views carry partial preparation status. PLAN.md content moves into
  `.pr/freeze-p1.md`; PLAN.md is removed at handoff.

## Calibration: explicitly incomplete

A178 remains staged in the kernel and the reducer's endpoint comparisons are
unchanged. The combined D-138/A178/L9-ENV-2 reissue was not found in the
inspected repository authorities. F4 has null acceptance and an explicit
`STUB_REISSUE_REQUIRED` status; its callable always refuses. No production
consumer is switched to the stub, and no issued acceptance, estimator byte,
scientific threshold or staleness predicate is changed. The combined refuter,
reissue and commit-scoped loader/trigger wiring belong to the owning D-138
transaction. No scientific acceptance is inferred from historical hashes.

## Verification ledger

- `git switch -c lane/2026-11-05-freeze-by-commit-p1`: FAILED, cannot create
  `.git/refs/heads/lane/...` under read-only Git metadata. No branch or commit.
- Git `for-each-ref`, `rev-parse`, `cat-file`: observed annotated tags locally.
  Collection: `c27485347c9629b857df81665b5b1b8d10dcd36a`, tree
  `30dc0681fbea919338f639075389bde0161f7c21`.
  Original analysis: `2fdc0929d5c214505617145893df2e71ab8a83b5`, tree
  `ea994f30a109123cffe19e1b064e1593928f16b3`.
  Release r2: `929fc65c9ce3ff82f0311d28acf76a682edd466f`, tree
  `9e89d7ff48999416467129c03ea171fc3a1f3f83`.
- Final before/after digest check for all nine existing source/test/registry
  files in the rebind table: PASS against r2 Git blobs and current files.
- AST parsing of the ten changed/new Python files: PASS.
- PLAN.md-to-PR transfer check: PASS; PLAN.md is removed and its original
  contents are preserved in `.pr/freeze-p1.md`.
- Registry structural migration check: PASS; target array and summary exactly
  equal to base; zero Python-test `#L` pointers remain. No measurement files
  opened to perform this migration.
- `git diff --check`: PASS at implementation review.
- Additional restrictive `sandbox-exec -f .../blind.sb python3 -m pytest
  tests/test_freeze_by_commit.py -q -x`: NOT STARTED; macOS returned
  `sandbox_apply: Operation not permitted`. No weaker sandbox flags were used.
- `python3 -m pytest tests/test_freeze_by_commit.py -q -x`: NOT STARTED;
  default Python 3.14 has no pytest. Python 3.13 also has no pytest. No install
  or network attempted. A question about runner preference received no reply;
  the same authorized targeted scope was checked serially with stdlib unittest.
  This is a runner substitution, not evidence that the requested pytest ran.
- Serial stdlib fallback (no workers; common environment:
  `HOME=/private/tmp/jwsol/freeze-p1/tmp/home`, `GIT_CONFIG_GLOBAL=/dev/null`,
  `GIT_CONFIG_NOSYSTEM=1`, `PYTHONDONTWRITEBYTECODE=1`,
  `JW_B5_SYNTHETIC_ONLY=1`):

  ```text
  python3 -m unittest tests.test_freeze_by_commit -q -f
  Ran 10 tests in 4.659s — OK (final rerun; prior 8/9-test runs also passed)

  python3 -m unittest tests.b5_analysis.test_frozen_files -q -f
  Ran 4 tests in 2.266s — OK (final rerun; initial run also passed)

  python3 -m unittest tests.test_digest_pin_census -q -f
  Ran 23 tests in 106.082s — OK

  python3 -m unittest tests.test_repin.RegistryCheckTests tests.test_repin.CommandFamilyTests tests.test_repin.EraRecordTests tests.test_repin.Block5EraRecordTests tests.test_repin.SealedInventoryEraRecordTests tests.test_repin.SealPinsEraRecordTests -q -f
  Ran 44 tests in 31.155s — OK
  ```

  81 tests in the final targeted set passed. Including the earlier 8/9-test
  and freeze-test runs, runner-reported test time totals about 167 seconds;
  only one test process
  ran at a time. `RealTreeTests` in test_repin.py was deliberately excluded:
  it invokes broader evidence/registry/generator checks outside this lane.
  The joined pipeline harness was syntax-checked but not executed.
- `python3 scripts/gen_state.py --check`: PASS after generation.
- All 335 migrated literal values are still present in their current Python
  holder sources: PASS. All target IDs/families/multiplicities are preserved.
- `python3 scripts/fixture_orphan_census.py --fail-on-orphans`: exit 2,
  `PermissionError: [Errno 1] Operation not permitted: 'ps'`. Observation is
  unavailable; no clean fixture census is claimed. No processes were signalled.
- Full suite: NOT RUN, explicitly prohibited by the user while the seven-worker
  analysis runs. Independent review, cold pass, CI, locked-environment tag
  reproduction and real-data equivalence: NOT RUN in this offline blind lane.

## Findings, uncertainty and next action

No claim of merge readiness: targeted checks passed, but branch creation,
commits, independent review and CI remain open. The reissue's absence is
based on the kernel, authority records and reducer source, not off-repo lane inspection. Existing tag availability and
identity are verified; reproducibility of its scientific outputs is not.
No delegation or model consult was used (offline; final authority retained).
The static checks caught no number-bearing defect; they establish syntax and
migration shape only. No mechanism is proposed for deletion on this one-run
sample.

Next: provide a session with writable Git metadata; create the requested branch
at the recorded base; run the focused pytest files in a pytest-equipped offline
environment (serial, under the user's blinding rules), review, and commit the
prepared diff. Keep A346 partial and the F4 dependency open. Land Phase 1 only
after the release and the owning lead's remaining gates; Phase 2 stays closed.
