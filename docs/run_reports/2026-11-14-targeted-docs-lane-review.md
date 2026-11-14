# PR #785 review record: targeted docs CI lane

Date: 2026-11-14. Full tier (CI workflow and script change). Row 1 is an executing review by a non-author seat, run in two rounds: the first on head `9a8b321ce`, then a delta re-check on `266149768` after the builder applied every finding. Row 4 is N/A: no measurement, calibration or claim code.

## Dispositions (gate row 5)

| Round 1 finding | Disposition |
|---|---|
| 1 HIGH: the docs-targeted job was not a required check, so a failing targeted module could not block a merge | Fixed in `266149768`: the modules run as a step inside the required `quick` job, pinned by wiring tests; mutant M17 (swallowing the failure) is killed |
| 2 MEDIUM: readers that build a doc's path in code (scripts/magistrate_watchdog.py) were missed | Fixed: basename grep at both ends of the range, and `docs/*.py` added to the scope; the magistrate case now runs the full suite |
| 3 MEDIUM: mutants M5, M6, M9 and M15 survived | Fixed: tests added for each; the misleading test renamed |
| 4 LOW: dead JW_TEST_TIMEOUT_SECONDS | Fixed: dropped |
| 5 LOW: dotted directory or `py` component gave a bad module name | Fixed: full suite, in both the script and ci.yml |
| 6 INFO: symlinks and gitlinks named like docs | Fixed: modes 120000 and 160000 at either end go to the full suite |
| Mutants M2, M3, M8, M10, M12 survive | Rejected as equivalent or redundant, with the reviewer's reasoning (Note A and the round 2 table) |
| Round 2 R2: no test for a symlink replaced by a regular doc | Fixed in this commit: test_symlink_replaced_by_a_regular_doc_is_full; with the before-side mode check removed, it fails |

## Row 1, round 1

## PR #785 gate-row-1 review (head 9a8b321ced79b4d003b211f8225b112262f656a4), Sat Nov 14 12:19 PST 2026

**Verdict: ADMIT WITH FIXES.** Finding 1 must be fixed before the lane goes live. Findings 2 and 3 are cheap and should land in the same PR.

The classifier holds up well under attack. 52 adversarial ranges went through it, and every case that should go to the full suite did, apart from four that `ci_docs_only.sh` already accepts in exactly the same way. The ci.yml regex re-validation blocks every injection shape I tried. The main problem is in the workflow: a failing `docs-targeted` job does not block a merge.

### Test tails (Python 3.13, PYTHONPATH=.:tests)
- `tests.test_ci_docs_only`: `Ran 44 tests in 7.849s` / `OK`
- `tests.test_git_fixture_maintenance`: `Ran 6 tests in 13.061s` / `OK`

### Findings

**1. HIGH: a failing `docs-targeted` job leaves every required check green, so the PR can merge.**
- **Repro:** `gh api repos/mpmdw/JouleWise/branches/main/protection/required_status_checks` lists gate-ledger, quick, fences, test (3.13, 1..12) and the 3 exclusive contexts. `docs-targeted` is not among them.
- **What happens:** on a targeted range, every required context reports success, because `code=false` means the shards, the exclusives and quick only run an echo step.
  - The one job that actually runs the tests that read the changed doc is advisory. If those modules fail, the run's overall status is red, but branch protection still allows the merge.
  - Anything that merges on "required checks green" merges a regression. That includes our own merge rule.
- **Fix, either of:**
  - (a) Add `docs-targeted` to the required contexts. A job skipped by its `if:` reports "skipped", which counts as passing, so non-targeted runs are unaffected.
  - (b) Better: run the targeted modules inside a job that is already required, for example `quick`, with `if: needs.changes.outputs.targeted != ''`. Then no branch-protection change is needed.
- Add a wiring test that pins whichever is chosen.

**2. MEDIUM: the claim "a range that today runs the full suite only gets cheaper when every referencing file is a test module" is false for readers that build the path in code.**
- **Real-repo repro:** `scripts/magistrate_watchdog.py:76` has `PROMPT_TEMPLATE = REPO_ROOT / "docs" / "process" / "MAGISTRATE_RELAUNCH_PROMPT.md"`, and `render_prompt()` reads it on the real `start_session` path.
  - The literal path appears only in `tests/test_magistrate_watchdog.py`.
  - So an edit to that doc classifies as `targeted tests.test_magistrate_watchdog`. Today it runs the full suite, because the docs-only lane rejects any referenced path.
  - Production code reads the doc, but the reader is invisible to `git grep -F <full path>`.
  - I did not find a test that would actually fail and be skipped here. The point is that the "non-test reader means full suite" rule is bypassed.
- **Scan:** `scan.py` checks every `ROOT / "docs" / ...` chain in the repo. It also flags `docs/process/NIGHT_HANDBACK.md`: the targeted set leaves out `tests/test_run_night.py`, which only asserts on the path string, so that one is harmless.
- **Fix:** add a second grep for the basename (e.g. `MAGISTRATE_RELAUNCH_PROMPT.md`, or `${path##*/}`) over the same scope.
  - A basename hit in any file that is not a `test_*.py` module means the full suite.
  - Basename hits in test modules join the targeted set.
  - This is conservative, and it catches the `ROOT / "docs" / ... / "name.md"` pattern, because the filename is always a literal.
- Also correct the safety paragraph in the PR body.

**3. MEDIUM: test gaps. Five safety-relevant mutants survive (table below).**
- **M5, M6:** neither regex layer has a test. Each layer covers for the other, but no test proves either one works.
  - Fix: add a classifier test with a file named `tests/test_$(id).py` that references a doc, and expect exit 1.
  - Add a wiring test that runs the extracted case/regex block (like `ymlsim.sh`) on hostile verdicts.
- **M9:** dropping `-F` is not caught.
  - Fix: add a test where a script references `docs/a*[x].md` and that exact doc changes.
- **M15:** the `changes` job can set `code=false` while dropping `targeted` from the `GITHUB_OUTPUT` printf. Then shards skip and no tests run, and the test suite still passes.
  - Fix: assert the printf line in the wiring test, or better, assert that `code=false` and an empty `targeted` occur only together with a docs-only verdict.
- **Misleading test:** `test_reference_that_exists_only_at_the_before_end_is_found` really tests "a .py in the range means full". See note A.

**4. LOW: the `docs-targeted` setup does not quite match the shards.**
- It runs plain `python -m unittest`, not `shard_tests`.
- `JW_TEST_TIMEOUT_SECONDS` is dead config there: only `scripts/shard_tests.py` reads it, so there is no per-test watchdog, only the 30-minute job timeout.
- The host-command guard is still installed, through `tests/__init__.py`.
- Only `pythons[0]` is used. Today that is the same as the matrix, which is `["3.13"]`.
- Fix: either drop the env var, or call `shard_tests.run_units` on the module list.

**5. LOW, fails closed: a dotted test directory gives a bad module name.**
- **Repro:** a doc referenced from `tests/x.py/test_y.py` produces `targeted tests.x.py.test_y`, which passes both regexes. unittest then gets an ImportError, rc=1, and the job goes red.
- It is red but non-blocking until Finding 1 is fixed. Both regexes could reject a component equal to `py`.

**6. INFO, same exposure as the docs-only lane, no new risk:**
- **Symlinks:** a symlink `docs/link.md` or `docs/assets/l.svg` pointing at code classifies as `docs-only`, and `ci_docs_only.sh` also exits 0 on it. A gitlink named `docs/sub.md` gives `docs-only` too. Optional fix: run `git diff --raw` and refuse modes 120000 and 160000.
- **Readers outside the grep scope:**
  - `docs/analysis/b5/RESULTS.md` and `REDERIVATION.md` are read by `docs/analysis/b5/hand_check_phase2.py` and `fill_coverage_b5.py`. Those are code under `docs/`, outside the grep scope, and `tests/b5_analysis/test_hand_check_phase2.py` executes them. Both lanes say `docs-only`.
  - `docs/paper/round7/fill-checklist.md`, `built-terms-lexicon.md` and `docs/phase_4/related_work_draft.md` are read only through constructed paths, and both lanes say `docs-only`.
  - `test_docs_freshness` reads `docs/**/*.md` by glob. That is covered, because fences always runs it.
  - So the targeted lane is no weaker than docs-only on these. The basename fix from Finding 2, plus adding `docs/**/*.py` to the grep scope, would close part of this for both lanes.
- **Quick:** on a targeted range, `quick` runs only its echo step, the same as on docs-only.

**Note A: the before-rev and after-rev checks are effectively equivalent mutants.**
- Every changed path must be a docs path, and docs paths are never inside the grep scope. So the scope trees are identical at both ends of any range that gets as far as the grep.
- Any reference that exists at only one end needs a non-doc path change, and that already exits 1. This holds for force-pushes from a non-ancestor and for PR base-tip ranges too; I tested both.
- Keeping the checks is harmless defense in depth, but no test can kill these mutants.

### Attack results (52 ranges, `attack.sh`)
**Full suite, as intended, for:**
- **Doc referenced from:** scripts/, a test helper, tests/fixtures/*.json, tests/__init__.py, tests/test_x.txt, .github, pyproject.toml, joulewise/, configs/.
- **Bad or odd test file names:** test-dash.py, test_x.py.bak, `test_x y.py`, `test_$(id).py`, `test_é.py`, `test_a;b.py`.
- **References changing within the range:** reference only in the AFTER rev, only in the BEFORE rev, and a before-only reference with a non-ancestor before.
- **Renames and deletes:** rename and delete of a doc referenced by a script.
- **Odd path characters** (all referenced by a script): a space, regex specials, a leading dash, unicode, and a newline in the path.
- **Paths outside the docs rules:** docs/site/, docs/registrations/, svg outside docs/assets, svg in docs/, .md under tests/, scripts/ and .github/, docs/assets/x.svg.py and x.md.py, uppercase .SVG.
- **Bad ranges:** empty range, empty commit, bad, uppercase, zero and unknown shas.

**Correct non-full verdicts:**
- A rename of a doc referenced by a test gives `targeted tests.test_r`, because the old name is caught through `--no-renames`.
- An unreferenced doc or svg deletion gives docs-only, as intended.
- A reversed range gives docs-only, which is fine.

**Mismatches against my expectations:**
- the dotted test directory (Finding 5);
- the two symlinks and the gitlink (Finding 6);
- the two constructed-path readers (Finding 6, shared with docs-only).

**ci.yml re-validation (`ymlsim.sh`).** Every one of these hostile verdicts gives `code=true` and an empty `targeted`, i.e. the full suite:
- `$(id)`
- a space inside a module name
- an embedded `\ntargeted=evil` line
- a trailing newline
- a double space
- a trailing `tests.`
- `tests..x`
- `;id`
- `docs-only ` with a trailing space
- an empty string

A newline cannot reach `GITHUB_OUTPUT`, because git quotes such names and the quoted name fails the `tests/*.py` match. The modules reach the job through `env:` rather than `${{ }}` in `run:`, so even with both regexes removed `$(...)` would not run.

**Workflow, other checks, all OK:**
- **Push to main:** uses `GITHUB_EVENT_BEFORE..GITHUB_SHA`. A zero sha (new branch) or a force push falls back safely.
- **Classifier source:** the classifier is read from the base rev, so a range cannot rewrite its own gate.
- **Classifier errors:** a script exit 1 or an empty verdict leaves `code=true`.
- **Failing modules:** they make the job red, but see Finding 1.
- **Fences, build, installed-wheel:** they still run.

### Mutant table (tests.test_ci_docs_only, script/workflow mutated in place, restored after each)
| Mutant | Result |
|---|---|
| M1a helper rule: accept any tests/*.py | KILLED (2 fail) |
| M1b drop the non-test/full-rule line | KILLED (2) |
| M1c drop full rule + script module regex | KILLED (3) |
| M2 drop before-rev check | SURVIVED (equivalent, see Note A) |
| M3 drop after-rev check | SURVIVED (equivalent, see Note A) |
| M4a svg anywhere (pattern) | KILLED (2) |
| M4b svg anywhere (extra case arm) | KILLED (2) |
| M5 drop script module regex | SURVIVED (Finding 3) |
| M6 drop ci.yml regex re-validation | SURVIVED (Finding 3) |
| M7 drop glob-read dirs arm | KILLED (5) |
| M8 drop grep-error check | SURVIVED (equivalent: empty hits still exit 1 by accident) |
| M9 drop `-F` | SURVIVED (Finding 3) |
| M10 drop empty-range check | SURVIVED (equivalent: an empty line hits `*) exit 1`) |
| M11 any .md anywhere | KILLED (1) |
| M12 drop zero-sha check | SURVIVED (equivalent: cat-file fails) |
| M13 docs-targeted gated on code | KILLED (1) |
| M14 ci.yml ignores the docs-only verdict | SURVIVED (safe direction, only less savings) |
| M15 code=false but targeted not exported (no tests at all) | SURVIVED (Finding 3, safety-relevant) |
| M16 no sort -u | KILLED (3) |

### Housekeeping
- The branch was left untouched: no commits, no pushes. The clone was clean at 9a8b321 before deletion, and I deleted it.
- Everything is in ci-lane-review/ (lead's scratch directory):
  - `attack.sh`
  - `mutate.py`
  - `scan.py`
  - `ymlsim.sh`

  To re-run them, re-clone the branch into `repo/` under that folder.

## Row 1, round 2 (delta re-check)

## PR #785 re-check, 9a8b321..2661497 (Sat Nov 14 12:35 PST 2026)

**Verdict: ADMIT.** All six earlier findings are fixed. One small test gap remains, and it is optional to close.

**Tests:** `tests.test_ci_docs_only` and `tests.test_git_fixture_maintenance` both pass: `Ran 62 tests in 22.564s`, `OK`.

### Your four checks
1. **A failing targeted module makes `quick` fail.**
   - The modules now run as the step "Targeted docs test modules" inside `quick`, which is a required check. The step only runs when `targeted` is set. `quick` itself has no job-level `if`, so it is never skipped.
   - On a targeted verdict, the quick tier and the "skipped" echo step don't run. Checkout, setup-python and zsh do.
   - I simulated the step under `bash -e`:

     | Modules | Step exit code |
     |---|---|
     | ok module | 0 |
     | failing module | 1 |
     | ok + failing | 1 |
     | module that can't be imported | 1 |

   - Nothing swallows a failure: mutant M17 (`|| true`) is killed.
2. **The magistrate_watchdog case now runs the full suite.** I copied the real files into a temp repo and changed `MAGISTRATE_RELAUNCH_PROMPT.md`. The new script exits 1 with no output (full suite). The old 9a8b321 script gave `targeted tests.test_magistrate_watchdog`.
3. **Both reproduce.**
   - `attack.sh` gives 54 ok. The two "mismatch" lines are cases I had labelled as expected misses, and they are now fixed. A test that builds the path in code now gives `targeted tests.test_d`. A script that builds it now gives the full suite.
   - The builder's mutant table reproduces. `mutate2.py` killed M1a–c, M4a/b, M5, M6, M7, M9, M11, M13 and M17–M20, then hit an assert error at M21 because of a quoting mismatch. `mutate3.py` killed M21, M14, M15 and M16.
   - The survivors are M2, M3, M8, M10 and M12. These are the ones already judged equivalent or redundant.
   - I added five mutants of my own:
     - R1 (drop the whole symlink/gitlink guard): killed.
     - R3 (drop the ci.yml check that rejects a `py` module component): killed.
     - R4 (drop the script's `/py/` path check): killed.
     - R5 (search only the basename, not the full path): survives, but it is equivalent. The basename is part of the full path, so its matches already include every full-path match.
     - R2 (drop the check on a file's mode before the change): survives. See the remaining item.
4. **Runs that are not targeted are unchanged.**
   - Every edited `if:` in `quick` gains only a `targeted` term. That term is false when `targeted` is empty, so these runs see the same conditions as before.
   - `targeted` is only set in the branch that also sets `code=false`, so it can never be non-empty on a full-suite run.
   - The new `py`-component check in ci.yml can only send a run to the full suite, never away from it.
   - Shards, exclusive jobs, fences and build are untouched.

### Remaining (low, optional)
- **R2:** nothing tests the case where a doc path was a symlink before the range and is a regular file after it. The awk guard does handle it: `$1 == ":120000"` catches it, and with that check removed the run is wrongly classed docs-only. A fix is one test: a symlink `docs/l.md` replaced by a regular file must go to the full suite.

The clone and attack directories are deleted. My scripts are still in ci-lane-review/ (lead's scratch directory).
