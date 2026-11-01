STATUS: DONE (lead-authored; tests and reports only, no production code changed)

# L9-ENV-7: fixes from L9-ENV-6-OPUS-REV (`f51de944b`, ACCEPT_WITH_FIXES)

Author: lead joulewise-28, on `lane/2026-10-30-l9-env-analysis-clamp-l6`, from `555661945`.
Synthetic data only. `joulewise/` and `scripts/` are byte-identical to `555661945`.

## Dispositions

- **F1 (Medium, fixed).** The selection pin bound the `IfExp` text, not what the flag means. The
  reviewer's mutants R2 (a read_replay rebind after the `IfExp`) and R3 (narrowing the flag when
  an archive context is set) survived. Added to `tests/test_whole_window_analysis_clamp_flag.py`:
  - `test_flag_holds_in_every_mode_and_archive_context` (runtime): `analysis_clamp` is True or
    False as passed, for both modes and with or without an `ArchiveContext`.
  - `test_clamp_runs_in_read_replay_mode` (runtime): a read_replay session reaches
    `_clamp_inverted_operative_envelopes` once and is ready with the clamped prefill `lower_j == 0.0`.
  - `test_rederive_selection_reads_the_flag_alone` (static, extended): `_prepare` stores `rederive`
    exactly once. `self.analysis_clamp` has exactly one assignment in the module, and its value is
    `analysis_clamp is True`.
- **F2 (Low, fixed).** The guard test covered only a disagreement with `lower_j > 0`, so R1 survived.
  Added `test_mirror_disagreement_with_a_zero_lower_bound_also_fails_closed`, in which reduce's mint
  defines the stretched prefill row at `lower_j == 0.0` and the summary must be returned unchanged.
- **F3 (Low, fixed).** `L9-ENV-6.md` and the guard test's docstring now cite `0f5c3f546` as the
  review of record, with the omitted-pointer issue as its F2. The code comment in `whole_window.py`
  is left as it is, as the reviewer allowed, so no production file changes.
- **F4 (Low, fixed).** `L9-ENV-6.md` verification now names PR #615 and points to exact tails for
  `tests/b5_analysis` and the guard module on this head.
- **O1 (optional, not taken).** `CallSiteTests` already pins the literal, `test_floor_mint_estimator`
  pins the exact kwargs, and the reviewer's L1 is killed. **O2:** kept as is, as the reviewer
  recommended.
- **L9-ENV6-FINAL-FABLE** (`0e7530876`, ACCEPT): F1 (step-4 tooling to R3 class move) is recorded in
  PR #615. F2 is accepted as is. F3 (a provenance marker) is deferred to L9-STEP4-FOLLOWUP. F4 is
  fixed above.

## Mutants (reviewer's survivors, rerun at `a1f63a137`, each in its own worktree)

| Mutant | Tests | Result |
|---|---|---|
| R1 guard fires only if minted `lower_j > 0.0` | `tests.test_whole_window_inverted_corner_clamp` | `Ran 34 tests` / `FAILED (failures=1)` |
| R2 `if self.mode == "read_replay": rederive = <reduce's>` after the IfExp | `tests.test_whole_window_analysis_clamp_flag` | `Ran 14 tests` / `FAILED (failures=1, errors=1)` |
| R3 `analysis_clamp is True and archive_context is None` | `tests.test_whole_window_analysis_clamp_flag` | `Ran 14 tests` / `FAILED (failures=3)` |

## Verification

At `a1f63a137` (macOS, Python 3.13, `JOULEWISE_CUSTODY_PARENT` and `TMPDIR` set to temp dirs):
`tests.test_whole_window_analysis_clamp_flag tests.test_whole_window_inverted_corner_clamp`:
`Ran 48 tests in 96.494s` / `OK`.

## L9-ENV-8: L9-ENV-7-OPUS-DELTA (`7b0df1fe8`, ACCEPT_WITH_FIXES)

The delta re-check confirmed the earlier fixes:
- R1, R2 and R3 are killed;
- its new R5 and R6 are killed;
- F3 and F4 are accurate;
- there is no production change.

One new low-severity survivor remained:
- **R4:** the call site bypasses `rederive` when an archive context is set.

**F1 (fixed with the reviewer's validated pin):**
- `test_rederive_selection_reads_the_flag_alone` now also requires, inside `_prepare`, one
  reference to `_rederive_summary_for_authenticated_fiducial_bound`;
- one `Load` of `rederive`;
- that `Load` to be the `func` of the only direct `rederive(...)` call.

Results at the L9-ENV-8 head (macOS):
- `tests.test_whole_window_analysis_clamp_flag`: `Ran 14 tests in 120.785s` / `OK`.
- With R4 applied: `Ran 14 tests in 120.730s` / `FAILED (failures=1)`.

The reviewer's own `pin_check.py` gave PIN FAIL on R2, R4 and R6 and PIN PASS on head.

**O1:** the tails cited in L9-ENV-6.md are at `555661945`, the L9-ENV-6 head. The delta is
tests-only, so no change is needed.
