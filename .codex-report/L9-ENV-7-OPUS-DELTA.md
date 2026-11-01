VERDICT: ACCEPT_WITH_FIXES

# L9-ENV-7-OPUS-DELTA: delta re-check of fix round L9-ENV-7 (Opus family, non-author)

Seat L9-ENV-7-OPUS-DELTA. This is a re-check of the lead's fixes for my review L9-ENV-6-OPUS-REV
(`f51de944b`, ACCEPT_WITH_FIXES). Delta under review: `555661945..97ba14d2e` on
`lane/2026-10-30-l9-env-analysis-clamp-l6`. It has two commits: `a1f63a137` (tests) and `97ba14d2e`
(reports). I read `.codex-report/L9-ENV-7.md` as claims.

Setup: Linux, Python 3.13 `unittest`, `TMPDIR=/tmp/lninedelta/tmp`,
`JOULEWISE_CUSTODY_PARENT=/tmp/lninedelta/custody`. Mutants ran one at a time in a single detached
worktree at `97ba14d2e`, which I deleted afterwards. I used synthetic data only and did not open or
search for any real block-5/6/BYTES data. Evidence is in `.codex-report/l9-env-7-opus-delta/`.

## Bottom line

- There is no production change.
- My F1 and F2 survivors (R1, R2, R3) are all killed now. My new F2 mutant (R5) is killed, and so is
  a mode-at-call-site variant (R6).
- One new F1-class mutant survives: R4. It narrows the selection on `archive_context` at the
  **call site** rather than in the flag or the `IfExp`. The runtime read_replay test has no archive
  context, and the static pin counts only `_rederive_operative_summary`, so neither catches it. The
  shipped code is correct, so this is test hardening only. It is new finding F1 below, with a fix I
  validated.
- F3 and F4 are accurate.

## Answers

**(1) No production change.** Confirmed. `git diff 555661945 97ba14d2e -- joulewise scripts configs`
is empty: `--stat` printed nothing and the exit code was 0 (`q1_production_diff.txt`). The full delta
touches only four files: `.codex-report/L9-ENV-6.md`, `.codex-report/L9-ENV-7.md`,
`tests/test_whole_window_analysis_clamp_flag.py` (+45) and
`tests/test_whole_window_inverted_corner_clamp.py` (+55/−3).

**(2) Do the new tests close F1 and F2?** F2 is closed. F1 is closed for R2 and R3, with the residual
gap R4. I ran each mutant with the same `mutate.py` substitution as in my report (copied as
`mutants/mutate_orig.py`) and the same test target. Tails are verbatim from `mutants/*.log.txt`:

| Mutant | Change | Tests | Result |
|---|---|---|---|
| R1 (mine, F2) | guard fires only if the minted `lower_j > 0.0` | `tests.test_whole_window_inverted_corner_clamp` | **killed**: `Ran 34 tests in 106.709s` / `FAILED (failures=1)`, by `test_mirror_disagreement_with_a_zero_lower_bound_also_fails_closed` |
| R2 (mine, F1) | `if self.mode == "read_replay": rederive = _rederive_summary_for_authenticated_fiducial_bound` after the `IfExp` | `tests.test_whole_window_analysis_clamp_flag` | **killed**: `Ran 14 tests in 67.599s` / `FAILED (failures=1, errors=1)`, by `test_rederive_selection_reads_the_flag_alone` (F) and `test_clamp_runs_in_read_replay_mode` (E) |
| R3 (mine, F1) | `self.analysis_clamp = analysis_clamp is True and archive_context is None` | `tests.test_whole_window_analysis_clamp_flag` | **killed**: `Ran 14 tests in 73.826s` / `FAILED (failures=3)`, by `test_flag_holds_…` (subtests `archive=True, flag=True` in both modes) and `test_rederive_selection_reads_the_flag_alone` |
| R4 (new, F1) | at the call site (`whole_window.py:1877`): `(rederive if self._archive_context is None else _rederive_summary_for_authenticated_fiducial_bound)(path, …)` | `tests.test_whole_window_analysis_clamp_flag` | **survives**: `Ran 14 tests in 76.293s` / `OK` |
| R6 (new, F1 variant) | same as R4, keyed on `self.mode != "read_replay"` | `tests.test_whole_window_analysis_clamp_flag` | **killed**: `Ran 14 tests in 69.017s` / `FAILED (errors=1)`, by `test_clamp_runs_in_read_replay_mode` |
| R5 (new, F2) | truthiness slip: `if _probe is not None and _probe.get("lower_j"):` | `tests.test_whole_window_inverted_corner_clamp.PermanentWideningCaseTests` | **killed**: `Ran 11 tests in 56.395s` / `FAILED (failures=1)`, by the new zero-lower test |
| L3 (lead's, re-aimed) | guard removed entirely | the new zero-lower test alone | **killed**: `Ran 1 test in 24.384s` / `FAILED (failures=1)` |

These counts match L9-ENV-7.md's mutant table for R1, R2 and R3 (34/14/14 tests; failures=1;
failures=1, errors=1; failures=3).

**(3) Are the new tests sound?** Yes. No assertion is vacuous.

- `test_mirror_disagreement_with_a_zero_lower_bound_also_fails_closed`:
  - `assertTrue(zero_lower)` proves the patched mint really returned a defined `lower_j == 0.0`
    envelope for the stretched row.
  - The row is matched by identity: `contributions is row`, where `row` is the object yielded by
    `rows`, which is what the guard receives.
  - So `assertIs(result, old)` cannot pass because the probe was never reached.
  - If the clamp were a no-op that returned before the loop, `zero_lower` would stay empty and the
    test would fail.
  - With the guard removed (L3), it fails.
- `test_clamp_runs_in_read_replay_mode`:
  - asserts `clamp.call_count == 1` through `wraps=`, and asserts the clamped prefill `lower_j ==
    0.0` in the session's provenance;
  - with the clamp bypassed (R2, R6), it errors or fails;
  - with the clamp body removed, the `lower_j` assertion and readiness would fail.
- `test_flag_holds_in_every_mode_and_archive_context`:
  - covers 2 modes × {no context, `ArchiveContext`} × {True, False} as subtests, with `assertIs`
    against a bool;
  - it is construction-only (`calibration_ledger_snapshot=object()` skips `archive_snapshot`), which
    is enough for the attribute claim.
- The static extension:
  - counts `Store` contexts of `rederive` in `_prepare` (1);
  - rules out `rederive` as a parameter;
  - requires exactly one `self.analysis_clamp` store anywhere in the module, unparsing to
    `analysis_clamp is True`;
  - R2 and R3 show it binds.
- The `run_session(..., session_kwargs=None)` extension appends `**(session_kwargs or {})` after the
  existing keyword splat. Existing callers pass nothing, so their construction is byte-identical. A
  caller that passes `analysis_clamp` both ways would get a `TypeError`, not a silent override. All 34
  tests in the guard module and all 14 in the flag module pass at head (Q5), so no existing test was
  weakened.

**(4) Are F3 and F4 bookkeeping accurate?** Yes.

- F3:
  - `L9-ENV-6.md` now names the interim `a3a85a6e9` and the review of record `0f5c3f546`
    (ACCEPT_WITH_FIXES, `Ran 1035 tests … FAILED (failures=1, skipped=13)`). Its F2 is change 2.
  - Heading 2 reads "L9-ENV-FINAL-FABLE F2 at `0f5c3f546`; F1 in the interim `a3a85a6e9`".
  - The guard-test docstring carries the same parenthetical.
  - I checked these against `origin/review/2026-10-30-l9-env-final-fable` at `0f5c3f546`.
  - The comment at `whole_window.py:1271` still says "final-pass F1". That is permitted, and it keeps
    production byte-identical.
- F4:
  - `L9-ENV6-FINAL-FABLE` `0e7530876` exists on `origin/review/2026-10-31-l9-env6-final-fable`, and
    its VERIFICATION lists `b5_analysis_discover.log | Ran 1035 tests in 3237.339s | OK
    (skipped=13)` and `test_whole_window_inverted_corner_clamp.log | Ran 33 tests in 107.550s | OK`
    at `555661945`. Those are the tails L9-ENV-6.md now cites.
  - PR #615 (draft, head `lane/2026-10-30-l9-env-analysis-clamp-l6` at `97ba14d2e`) records "466 of
    466 modules exit 0" at `555661945`, as L9-ENV-6.md says.
  - The "13 constructor calls in the 10 analysis consumer files" correction matches Fable F4.
  - Nit, no action: L9-ENV-6.md calls those tails "on this head". They are at `555661945`, the
    L9-ENV-6 head. That is right in the context of L9-ENV-6.md, but it is not the current branch tip
    `97ba14d2e`. Because the delta is tests-only, the distinction does not matter.

**(5) Runs at `97ba14d2e`.** Full log: `baseline_clamp_flag_and_inverted_corner.txt`.

`python3.13 -m unittest -v tests.test_whole_window_analysis_clamp_flag tests.test_whole_window_inverted_corner_clamp`:

```
----------------------------------------------------------------------
Ran 48 tests in 165.953s

OK
```

That is 14 + 34 tests, matching L9-ENV-7.md's `Ran 48 tests … OK` on macOS. Each of the four new or
extended tests reports `... ok` in the verbose log. I did not rerun `tests/b5_analysis`, as
instructed.

## Findings (ranked)

### F1 (Low, test binding). Call-site narrowing on the archive context survives (R4)

- **Where.**
  - The call site is `joulewise/whole_window.py:1876-1877` (`operative_summary = (rederive(...`).
  - The pins are in `tests/test_whole_window_analysis_clamp_flag.py:170-201`
    (`test_rederive_selection_reads_the_flag_alone`) and `:217`
    (`test_clamp_runs_in_read_replay_mode`).
- **Evidence.**
  - R4 leaves the `IfExp`, the single `rederive` store and the flag store untouched. It bypasses
    `rederive` at the call when `self._archive_context is not None`, which is exactly the block-5
    dry-run shape (read_replay *with* an archive context).
  - Result: `Ran 14 tests in 76.293s` / `OK` (`mutants/R4.log.txt`).
  - The runtime test builds a read_replay session without an archive context, so it cannot see
    this mutant.
  - The static pin counts only `_rederive_operative_summary` names, not the second reference to
    `_rederive_summary_for_authenticated_fiducial_bound` that R4 adds.
  - The mode-keyed twin R6 is killed by the runtime test, so the remaining gap is specifically the
    archive-context axis that my F1 named.
  - Shipped code is correct: `rederive(` at `:1877` is called directly, and `_prepare` holds one
    reduce reference.
- **Fix (validated).** Add three checks to `test_rederive_selection_reads_the_flag_alone`, inside
  `_prepare`:
  - exactly one `Name` `_rederive_summary_for_authenticated_fiducial_bound` (the `IfExp` orelse);
  - exactly one `Load` of `rederive`;
  - that `Load` is the `func` of the only `ast.Call` whose func is `Name('rederive')`.

  This is `mutants/pin_check.py`. Results (`mutants/pin_check_results.txt`):

  | Tree | Result |
  |---|---|
  | head | `PIN PASS` |
  | R2 | `PIN FAIL` (reduce_refs 2) |
  | R4 | `PIN FAIL` (reduce_refs 2, direct_calls 0) |
  | R6 | `PIN FAIL` (reduce_refs 2, direct_calls 0) |

  A runtime alternative would be `test_clamp_runs_in_read_replay_mode` with a real `ArchiveContext`
  through `session_kwargs`. That needs a window bracket fixture (`_prepare` consults
  `self.archive_context` at `:1660`/`:1672`), so the static pin is cheaper.

### Observations (no action required)

- **O1.** The L9-ENV-6.md "on this head" wording for the Fable tails refers to `555661945`; see Q4.
- **O2.** L9-ENV-7.md's verification is at `a1f63a137` on macOS. My run at `97ba14d2e` on Linux gives
  the same 48 OK. `97ba14d2e` changes only reports.

## VERIFICATION

All runs used `python3.13 -m unittest` with `TMPDIR=/tmp/lninedelta/tmp` and
`JOULEWISE_CUSTODY_PARENT=/tmp/lninedelta/custody`, at `97ba14d2e` (unmutated unless named). Every
run listed completed.

```
baseline  tests.test_whole_window_analysis_clamp_flag tests.test_whole_window_inverted_corner_clamp
          Ran 48 tests in 165.953s   OK
R1        tests.test_whole_window_inverted_corner_clamp                       Ran 34 tests in 106.709s  FAILED (failures=1)
R2        tests.test_whole_window_analysis_clamp_flag                         Ran 14 tests in 67.599s   FAILED (failures=1, errors=1)
R3        tests.test_whole_window_analysis_clamp_flag                         Ran 14 tests in 73.826s   FAILED (failures=3)
R4        tests.test_whole_window_analysis_clamp_flag                         Ran 14 tests in 76.293s   OK
R6        tests.test_whole_window_analysis_clamp_flag                         Ran 14 tests in 69.017s   FAILED (errors=1)
R5        tests.test_whole_window_inverted_corner_clamp.PermanentWideningCaseTests
                                                                              Ran 11 tests in 56.395s   FAILED (failures=1)
L3        ...PermanentWideningCaseTests.test_mirror_disagreement_with_a_zero_lower_bound_also_fails_closed
                                                                              Ran 1 test in 24.384s     FAILED (failures=1)
```

Not run, as instructed: `tests/b5_analysis` and the rest of the suite.
