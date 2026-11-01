VERDICT: ACCEPT_WITH_FIXES

# L9-ENV-6-OPUS-REV: delta review of lead-authored lane L9-ENV-6 (Opus family, non-author)

Seat L9-ENV-6-OPUS-REV. Code reviewed at `555661945` on `lane/2026-10-30-l9-env-analysis-clamp-l6`.
Delta: `9553fe2f2..555661945`, excluding the merges of origin/main. That leaves the lane commits
`18b42aea4` (literal opt-in), `9f91cb4a6` (omitted-pointer guard) and `0faef4c25` (tests and report).
Merge `640c29e40` only brings in L9-ENV-5's report files on top of `9553fe2f2`.
`.codex-report/L9-ENV-6.md` was read as claims. The prior reviews were read from
`origin/review/2026-10-30-l9-env5-opus-rev` and `origin/review/2026-10-30-l9-env-final-fable` (both
`a3a85a6e9` and its final `0f5c3f546`).

`555661945` already contains current origin/main (`fb14d26a9`; `git merge-base --is-ancestor`
holds), so "555661945 merged with current origin/main" is `555661945` itself. Every run below is on
that tree. Setup: Linux, Python 3.13 `unittest`, `TMPDIR=/tmp/lnineenvrev/tmp`,
`JOULEWISE_CUSTODY_PARENT=/tmp/lnineenvrev/custody`. I used synthetic data only. I did not open or
search for real block-5/6/BYTES data. Evidence is in `.codex-report/l9-env-6-opus-rev/`.

## Bottom line

The three code changes are correct and do what L9-ENV-6.md says:

- The merge blocker is gone. Both call sites pass `analysis_clamp=True` literally. No string
  constant equal to `analysis_clamp` remains in any generator module. The registered step-4 table is
  byte-unchanged, and R1 passes.
- The omitted-pointer guard is strictly fail-closed.
- The edited out-of-scope tests still test what they tested before. The floor-mint test is stronger
  than before.

All four lead mutants are killed. All three of my own mutants survive:

- One is a gap in the guard test (F2).
- Two are gaps in the F2 selection pin (F1). The pin binds the text of the `IfExp` but not the
  flag's meaning.

None of the three is a defect in the shipped code, so the verdict is ACCEPT_WITH_FIXES (test
hardening plus report bookkeeping), not REJECT.

## Answers to the questions

**(1) Literal opt-in, no `'analysis_clamp'` constant, registered table unchanged.** Yes, on all
three counts.

- `joulewise/analysis_engine/inputs.py:3805` and `joulewise/floor_mint_estimator.py:490` now pass
  `analysis_clamp=True` as an `ast.keyword`. The other analysis sites (`inputs.py:2031`, `:2135`)
  were already literal.
- I ran an AST scan over the 11 modules in `configs/analysis/b5/step4_reason_classes.json`
  `modules`. It finds no `ast.Constant` whose value equals `"analysis_clamp"`.
- The only constants that *contain* the substring are two docstrings in `joulewise/whole_window.py`
  (`:951`, `:1372`). They were already present at L9-ENV-5. They are not snake_case-token constants,
  so the generator ignores them, and R1 passes.
- `git diff origin/main 555661945 -- configs/analysis/b5/step4_reason_classes.json` is empty.
- `tests.b5_analysis.test_step4_reason_table` alone: `Ran 8 tests in 5.667s` / `OK`
  (`l9-env-6-opus-rev/step4_reason_table.txt`).
- The `inspect` imports are still used elsewhere (`inputs.py:3793`, `floor_mint_estimator.py:110`),
  so no import was orphaned.

**(2) Is the guard strictly fail-closed?** Yes.

- The only change is a new `return summary` at `joulewise/whole_window.py:1271-1277`, reached only
  for a group pointer that reduce *omitted*. `summary` is reduce's own unchanged re-derivation, the
  same object the flag-off session uses. So the guard can only replace a clamped operative copy with
  reduce's output.
- It cannot make a session more permissive. L9-ENV-4 F1 still guarantees that every clamped member
  stays ineligible, and the guard only removes clamped envelopes.
- It cannot change a point estimate. Neither path touches point fields.
- It cannot change output where reduce defines every pointer, because the branch is never reached
  then. For recorded pointers the existing reproduction check (`:1264-1270`) runs first and is
  untouched.
- The guard's premise is that reduce omits a current-wire member pointer only when its mint function
  returns `None`. I checked it in `reduce.py`:
  - `:2578-2597`: phase/item/block/level are recorded `if env is not None`, with `envelope()` =
    `_corner_composed_anchor_shift_envelope` on current wire (`:2539-2546`);
  - `:3221-3235`: the 0.6.2 phase envelopes, same pattern.
- The guard adds no new exception type. It calls the same function that
  `_clamped_corner_composed_anchor_shift_envelope` calls first (`:968`).
- Liveness side effect, by design: when the guard fires it discards the whole bundle's clamp, not
  just one pointer. At L9-ENV-5 an unclamped envelope whose gate reasons were empty was dropped
  silently while the other clamps stayed. Now the bundle falls back to reduce's `unrecorded`
  refusals. Both outcomes are ineligible, so this is conservative.
- Existing oracle-sweep results are unchanged. `tests/test_whole_window_inverted_corner_clamp.py`
  in full: `Ran 33 tests in 209.797s` / `OK`. That is 32 tests at L9-ENV-5 plus the new one. The
  diff to that file only adds `ENV5_COMMIT` and the new test, so no existing assertion was edited.

**(3) Do the new tests bind behaviour?** Partly. The lead's four mutants are killed; my three
survive. Diffs and tails are in `l9-env-6-opus-rev/mutants/`.

| Mutant | Change | Tests run | Result |
|---|---|---|---|
| L1 | drop `analysis_clamp=True` at `inputs.py:3805` | `CallSiteTests` + `test_analysis_integration` | killed: `Ran 119 tests in 179.850s` / `FAILED (failures=1, errors=1)` |
| L2 | drop it at `floor_mint_estimator.py:490` | `CallSiteTests` + `test_floor_mint_estimator` | killed: `Ran 41 tests in 51.248s` / `FAILED (failures=2)` |
| L3 | remove the guard | the new omitted-pointer test | killed: `Ran 1 test in 56.651s` / `FAILED (failures=1)` |
| L4 | R-M2: `self.analysis_clamp and self.mode != "read_replay"` | `test_whole_window_analysis_clamp_flag` | killed: `Ran 12 tests in 106.633s` / `FAILED (failures=1)` |
| R1 | guard fires only if the minted envelope has `lower_j > 0.0` | `test_whole_window_inverted_corner_clamp` (all) | **survives**: `Ran 33 tests in 118.544s` / `OK` |
| R2 | keep the `IfExp`, then add `if self.mode == "read_replay": rederive = _rederive_summary_for_authenticated_fiducial_bound` | `test_whole_window_analysis_clamp_flag` | **survives**: `Ran 12 tests in 76.728s` / `OK` |
| R3 | `self.analysis_clamp = analysis_clamp is True and archive_context is None` (`whole_window.py:1433`) | `test_whole_window_analysis_clamp_flag` | **survives**: `Ran 12 tests in 75.342s` / `OK` |

R2 and R3 each disable the clamp exactly in the block-5 dry-run shape (`read_replay`, or with an
archive context) and leave the `IfExp` text intact. That is the class of defect L9-ENV-5-OPUS-REV F2
asked to bind (F1 below). R1 survives because the single new test case has `lower_j > 0` (asserted
at `tests/test_whole_window_inverted_corner_clamp.py:776`) (F2 below).

**(4) Are the edited out-of-scope tests still testing the same thing?** Yes.

- `tests/test_analysis_integration.py:2643`: before, the fake's signature lacked `analysis_clamp`,
  so the signature gate never passed it. Now the fake *requires* it, or construction raises
  `TypeError`.
  - The test still asserts the same observed modes, the stored-bytes invariance and the widened
    envelopes. The fake is a stand-in, so the clamp is never applied in that test.
  - The value is not asserted at runtime, only statically by `CallSiteTests`. Note O1 below.
  - Full module: `Ran 116 tests in 241.688s` / `OK`.
- `tests/test_floor_mint_estimator.py:411`: before, `inspect.signature(MagicMock)` has no
  `analysis_clamp`, so the exact-kwargs assertion pinned its absence. It now pins
  `analysis_clamp=True` exactly. That is strictly stronger, and L2 shows it binds.
  - Full module: `Ran 38 tests in 39.207s` / `OK`.

**(5) Gate runs at `555661945` (= merged with current origin/main `fb14d26a9`).**

- `tests/test_whole_window.py`: `Ran 26 tests in 2.011s` / `OK`
- `tests/test_whole_window_analysis_clamp_flag.py`: `Ran 12 tests in 137.093s` / `OK`
- `tests/test_whole_window_inverted_corner_clamp.py`: `Ran 33 tests in 209.797s` / `OK`
- `tests/test_whole_window_parallel_strict.py`: `Ran 8 tests in 1.336s` / `OK`
- `tests/test_whole_window_selection.py`: `Ran 57 tests in 278.780s` / `OK`
- `tests/test_floor_mint_estimator.py`: `Ran 38 tests in 39.207s` / `OK`
- `tests/test_analysis_integration.py`: `Ran 116 tests in 241.688s` / `OK`
- `tests/b5_analysis` (whole directory): whole-directory run **did not finish clean**: `Ran 1035 tests in 3826.256s` / `FAILED (errors=10, skipped=13)`. All 10 errors are `shutil.Error` with `[Errno 28] No space left on device` while fixtures were copied (the disk allowance was used up by my mutant worktrees and a killed earlier run). They are not test failures. After I freed disk, the two affected modules passed: `tests.b5_analysis.test_mint_kept_units` + `tests.b5_analysis.test_validator_context`: `Ran 134 tests in 402.746s` / `OK (skipped=2)`. There were no `FAIL:` results. The other 1025 tests passed or were skipped in the whole-directory run. I did **not** complete a single error-free whole-directory run, so I do not claim one

Exact tails are in VERIFICATION.

## Findings (ranked)

### F1 (Medium, test binding). The F2 selection pin binds the expression's text, not the flag's meaning; R2 and R3 survive

- **Where.**
  - `tests/test_whole_window_analysis_clamp_flag.py:170-186` pins `ast.unparse(IfExp.test) ==
    "self.analysis_clamp"` and a single use of the name `_rederive_operative_summary`.
  - `joulewise/whole_window.py:1433` derives the flag; `:1860-1864` selects.
- **Evidence.**
  - R2 rebinds `rederive` to reduce's function after the `IfExp`. The name it adds is
    `_rederive_summary_for_authenticated_fiducial_bound`, which the test does not count.
  - R3 narrows the attribute itself at construction.
  - Both pass all 12 tests. The runtime clamp tests all build `mode="issuing"` sessions without an
    archive context, and the dry-run tests spy only on constructor kwargs. That is exactly what
    L9-ENV-5-OPUS-REV F2 described, and the AST pin closes only the literal-`IfExp` variants (R-M1,
    R-M2).
  - The shipped code is correct: `:1433` reads `analysis_clamp is True` and nothing rebinds
    `rederive`.
- **Fix.** Bind the behaviour at runtime in the dry-run shape rather than adding more AST text pins.
  - Construct a session on the existing synthetic fixture with `analysis_clamp=True,
    mode="read_replay"` and an archive context. `BlockFiveDryRunPathTests` already builds one.
  - Patch `whole_window._clamp_inverted_operative_envelopes` with `wraps=` and assert it is called
    once per re-derived bundle.
  - Also assert `session.analysis_clamp is True` after construction with `archive_context`, which
    kills R3.
  - If a static pin is preferred, add two checks:
    - `rederive` is assigned exactly once in `_prepare`, which kills R2;
    - the `self.analysis_clamp = ...` assignment unparses exactly to `analysis_clamp is True`, which
      kills R3.

### F2 (Low, test binding). The omitted-pointer test covers only a disagreement with `lower_j > 0`; R1 survives

- **Where.** The test is `tests/test_whole_window_inverted_corner_clamp.py:732-783`. The guard is
  `joulewise/whole_window.py:1274-1277`.
- **Evidence.**
  - R1 (fire only when the minted envelope has `lower_j > 0.0`) passes the whole module.
  - A disagreeing omitted pointer whose unclamped mint has `lower_j == 0` (for example a zero-power
    stretch) would then be added at L9-ENV-5 semantics.
  - That is reachable only under a simulated mirror discrepancy, as the Fable pass noted. Hence Low.
- **Fix.** Add a second case to the same test:
  - stretch the mirror's prefill row to a window whose reduce mint is defined with `lower_j == 0.0`,
    for example over a zero-power stretch of the synthetic curve, or by patching
    `_corner_composed_anchor_shift_envelope` to return a defined envelope with `lower_j=0.0` for
    that pointer only;
  - assert `result is old`.

  The guard condition is `is not None`, so any defined envelope must trip it.

### F3 (Low, bookkeeping). L9-ENV-6.md cites the superseded interim Fable report

- **Where.** `.codex-report/L9-ENV-6.md:50-54` ("L9-ENV-FINAL-FABLE (`a3a85a6e9`) returned ACCEPT,
  … still holds `TAILS_PLACEHOLDER` … Its Q5 is therefore unverified"), plus the "final-pass F1"
  labels at `:22`, at `joulewise/whole_window.py:1271` and in the test docstring.
- **Evidence.** `origin/review/2026-10-30-l9-env-final-fable` was updated to `0f5c3f546`
  (2026-10-30 13:25 UTC), before `9f91cb4a6` and `0faef4c25` were committed.
  - That final report is `VERDICT: ACCEPT_WITH_FIXES`. Its F1 *is* the step-4 R1 merge failure,
    with recorded tails (`Ran 1035 tests … FAILED (failures=1, skipped=13)`), and it has no
    `TAILS_PLACEHOLDER`.
  - The omitted-pointer finding is its **F2**, not F1.
  - So the critique is accurate about `a3a85a6e9` but stale about the review of record. The
    finding IDs in the code comment and the test docstring point to the wrong number in the final
    report.
- **Fix.** In L9-ENV-6.md, cite `0f5c3f546` as the review of record. Say that it corrected its own
  Q5, and refer to the omitted-pointer issue as "L9-ENV-FINAL-FABLE F2 (`0f5c3f546`; F1 in interim
  `a3a85a6e9`)". The code comment can stay as is, or take the same parenthetical.

### F4 (Low, bookkeeping). L9-ENV-6.md's verification omits two gates and defers to an unlinked PR

- **Where.** `.codex-report/L9-ENV-6.md:56-60`.
- **Evidence.**
  - The targeted list does not include `tests/test_whole_window_inverted_corner_clamp.py`, the
    module holding the new guard test, or the whole `tests/b5_analysis` directory, the gate that
    caught the original blocker.
  - It gives counts, not tails.
  - "The whole-suite sweep on this head is recorded in the PR" names no PR, and `list_pull_requests` with head
    `mpmdw:lane/2026-10-30-l9-env-analysis-clamp-l6` and state `all` returns none.
- **Fix.** Add exact tails for those two runs on this head, or cite this report's VERIFICATION, and
  link the PR or drop the sentence.

### Observations (no action required)

- **O1.** The fake session in `tests/test_analysis_integration.py:2643` could record
  `analysis_clamp` and the test could assert it `is True`. That would give the opt-in a runtime
  check through `load_analysis_inputs`. This is optional: `CallSiteTests` already pins the literal
  `True`, and L1 is killed.
- **O2.** For an omitted pointer, `_clamped_corner_composed_anchor_shift_envelope`'s first branch
  (`whole_window.py:968-975`, "return reduce's mint if defined") is now unreachable from
  `_clamp_inverted_operative_envelopes`, because the guard has already returned. Each omitted pointer
  therefore evaluates reduce's mint twice. This is harmless. Keep it: the helper's contract stays
  self-contained.

## VERIFICATION

All runs used `python3.13 -m unittest` at `555661945` (it contains origin/main `fb14d26a9`), with
`TMPDIR=/tmp/lnineenvrev/tmp` and `JOULEWISE_CUSTODY_PARENT=/tmp/lnineenvrev/custody`. Full logs are
in `.codex-report/l9-env-6-opus-rev/`.

```
tests.test_whole_window                        Ran 26 tests in 2.011s     OK
tests.test_whole_window_analysis_clamp_flag    Ran 12 tests in 137.093s   OK
tests.test_whole_window_inverted_corner_clamp  Ran 33 tests in 209.797s   OK
tests.test_whole_window_parallel_strict        Ran 8 tests in 1.336s      OK
tests.test_whole_window_selection              Ran 57 tests in 278.780s   OK
tests.test_floor_mint_estimator                Ran 38 tests in 39.207s    OK
tests.test_analysis_integration                Ran 116 tests in 241.688s  OK
tests.b5_analysis.test_step4_reason_table      Ran 8 tests in 5.667s      OK
```

`tests/b5_analysis` (whole directory, `python3.13 -m unittest discover -s tests/b5_analysis -t .`):

First run: started together with the other gate modules, and stopped by the 30-minute background
limit before it finished. It has no result (`b5_analysis_first_killed.txt`).

Second run, whole directory (`b5_analysis_whole.txt`):

```
----------------------------------------------------------------------
Ran 1035 tests in 3826.256s

FAILED (errors=10, skipped=13)
```

The errors are 6 subtests of `test_catalog_replay_problem_and_preconditions`, plus
`test_catalog_empty_manifest_list_refuses`, `test_catalog_endpoint_disagreement_refuses`,
`test_catalog_recovery_feeds_both_rederivations` (`test_validator_context.CatalogContextTests`) and
`test_guard_setup_after_s4_preserves_the_cached_source`
(`test_mint_kept_units.SensitivityFixtureIsolationTests`). Every one ends in `shutil.Error:
[... "[Errno 28] No space left on device" ...]` from `joulewise/b5/harvest.py:1850` (`clone_tree`).
There is no `FAIL:` line. `test_step4_reason_table` R1, the original blocker, passed in this run.

Rerun of the two affected modules after freeing disk (`b5_analysis_enospc_rerun.txt`):

```
----------------------------------------------------------------------
Ran 134 tests in 402.746s

OK (skipped=2)
```

So every `tests/b5_analysis` test has a passing or skipped result on `555661945`, but across two runs.
An uninterrupted, error-free whole-directory run was not completed by this seat.
