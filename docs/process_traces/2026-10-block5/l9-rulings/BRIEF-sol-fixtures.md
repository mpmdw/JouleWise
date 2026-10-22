SESSION_MODE: delegated
BRIDGE_ORIGIN: claude
BRIDGE_HOPS_REMAINING: 0
WRITE_SCOPE: ["tests/b5_analysis/fixtures.py", "tests/b5_analysis/fixtures_s1.py", "tests/b5_analysis/fixtures_s2.py", "tests/b5_analysis/fixtures_s3.py", "tests/b5_analysis/fixtures_s3b.py", "tests/b5_analysis/test_fixture_shapes.py", "tests/fixtures/b5_analysis/**", ".scratch-fixtures/**"]

For the report envelope: genre implementation; keep the JSON header under 4,000 bytes and put all evidence in the markdown body. End your turn only after the work is complete and the report is written. Start no background task and no other agent. Commit nothing. **You have 100 minutes of wall time; write the report by minute 90 whatever is unfinished.**

# Lane L9: synthetic windows of the pinned harvest program must not depend on the tree's `whole_window.py`

You work in the worktree and branch the launcher names (clean tree). Stage S0's fixture builder
(`tests/b5_analysis/fixtures.py`, `build_window`) builds a "pin4" synthetic window by running the in-tree
harvest program, and refuses when the tree's program files are not the pinned commit's bytes
(`exported program hash differs`). That refusal is right and stays: a window must be written by the real
pinned program (`b039c0257d1b1d407ee9598222db3f78f6ad7beb`). But stage S3 now edits
`joulewise/whole_window.py`, one of the four pinned files, so on this tree:

- `tests.b5_analysis.test_kept_units`, `test_bracket`, `test_fixture_shapes` (stages S0 to S2) error at
  fixture build;
- stage S3's `fixtures_s3.py` builds its windows in a `git archive HEAD` export, which is the pinned program
  only while HEAD's `whole_window.py` is unedited, and keeps a 3.9 GiB cache under `.scratch-s3/`;
- nothing of this would run in CI, where there is no scratch cache.

## What to build

One mechanism, in `tests/b5_analysis/fixtures.py`, used by every stage's fixtures: a pin4 window is obtained
exactly as a pin2 window already is (`load_exported_window` and the committed archives under
`tests/fixtures/b5_analysis/pin2/`, built once by the program at that commit in a `git archive` export, with
`PROVENANCE.md` giving the command): committed, compressed archives under `tests/fixtures/b5_analysis/pin4/`,
built by the program at `b039c0257` in an export, loaded at test time with no dependence on the tree's
program files and no call to `git`. Then:

1. Commit-ready pin4 archives for exactly the base windows the test modules use (find them: every
   `build_window`, `build_named`, `cached(...)` call in `tests/b5_analysis/`), for the packs and variants
   used. Keep the set minimal: where a test derives a variant by editing a loaded base window in memory, keep
   doing that. Report the total size added; if it would exceed about 40 MB, stop and report the list and
   sizes instead of committing more.
2. `build_window(..., shape="pin4")` loads the committed archive whenever the tree's pinned files differ from
   the pin (and may still build in-tree when they are identical, if you keep that path, but then a test must
   show both paths give byte-identical archives for one window). The hash fence stays for any in-tree build.
3. `fixtures_s1.py`, `fixtures_s2.py`, `fixtures_s3.py`, `fixtures_s3b.py` use that one mechanism; the
   `git archive HEAD` export and the `.scratch-s3` cache go away. In-memory caches per test module stay.
4. `test_fixture_shapes.py` keeps every assertion. Its assertions about what the pinned program writes are
   now made on the committed pin4 archives; add one test that each committed pin4 archive's recorded
   `harvest_checkout.head` and file digests are the pin's (so a fixture built by the wrong program cannot be
   committed), and one that `PROVENANCE.md` names the commit.
5. Run, at the end, on this tree (where `whole_window.py` is edited): `tests.b5_analysis.test_kept_units`,
   `test_bracket`, `test_fixture_shapes`, `test_validator_context`, `test_neg8_parity`, `test_neg8_predicate`,
   `test_launch_lineage`, and part B's modules if present (`test_context`, `test_tripwires`,
   `test_sources_replay`). All must pass with `.scratch-s3` moved away. Report each result and its wall time.

## Constraints

- Production code is not yours: nothing under `joulewise/`, `scripts/`, `configs/`. No test's meaning
  changes; no expected refusal code changes; no test is deleted.
- Build exports with `git archive <commit> | tar -x -C .scratch-fixtures/<pin>/` (no `git worktree`, no
  `git checkout`), as `tests/fixtures/b5_analysis/pin2/PROVENANCE.md` records for pin2.
- Interpreter `/opt/homebrew/bin/python3.13`, `PYTHONDONTWRITEBYTECODE=1`, a `TMPDIR` without "claude" or
  "codex" in its path.
- Blinding (binding): do NOT open anything under `/Users/edr/night-custody/v5-b5-*`, `/Users/edr/night-b5/`,
  `/Users/edr/night-g2a/`, `/Users/edr/night-archive/harvest-v5-b5-*`, or any runs root under
  `/Users/edr/night-custody/measurement/`. Synthetic fixtures only.

Report: the mechanism in five lines; the committed archives with sizes and the commit that wrote each; per
module the result and wall time; anything that needs a change outside your scope.
