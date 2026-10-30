STATUS: BLOCKED E1-E5 are implemented and pushed, but the ruling's goal (dry run passing) needs two further rulings: N1, the reduce.py estimator pin makes the live calibration acceptance stale; N3, the strict re-reduction no longer equals the stored summaries

# L9-ENV-2: clamp inverted corner windows in reduce.py (Ed's 2026-10-30 ruling)

Branch `lane/2026-10-30-l9-env-clamp` from origin/main `0f34b2ca20c443156b6e22d0a64250126ef1be61`.
Synthetic data only. No real block-5/6/BYTES data was opened or searched.

## SUMMARY

- `joulewise/reduce.py` `_corner_composed_anchor_shift_envelope`: a shifted window with
  `end_s < start_s` becomes a zero-length window at its shifted midpoint (0 J), where it used to
  `return None`. That is the whole code change (+16/-2 lines). Every other `None` guard is untouched.
- Every window that does not invert takes byte-for-byte the same path as before, and the tests
  confirm the envelopes are bit-identical to origin/main. They compare against origin/main's exact
  source, rebuilt by reversing the hunk and checked against the sealed digest `7b9c0d28…`.
- Synthetic reproduction: at origin/main the prefill envelope is dropped and the session refuses
  `anchor_energy_envelope_unrecorded`. After the clamp the envelope exists with `lower_j == 0`, covers
  the minted envelope, keeps the point estimate, and the session is ready. This holds both for
  summaries minted at origin/main (the block-5 situation) and for summaries minted after the ruling.
- The freeze test now binds reduce.py to `d37f731c…` and every other frozen file exactly as before.
- **Major side-effect (NEEDS_RULING N1, owner notified by push).** `joulewise/reduce.py` is one of the
  four `ESTIMATOR_CODE_PATHS` (`joulewise/calibration_bracketing.py:238-243`). The live acceptance
  `calibration_acceptance_d079_v2_n24_25g83_r2.json` pins its sha256 `7b9c0d28…`. With these bytes,
  `_current_estimator_code_sha256()` differs from that pin; I checked this and the other three files
  still match. That sets off `protocol_or_estimator_byte_change` (`calibration_bracketing.py:2536-2540`).
  The trigger is failing in both scopes (`:2780`), so every bracket evaluation returns
  `calibration_acceptance_bound_stale`. That includes the L9 bracket replay
  (`joulewise/b5_analysis/bracket.py:253-266` → `window_bracket_not_passed`), the whole-window session
  bracket (`joulewise/whole_window.py:1204`) and any collection-night bracket check. The dry run
  therefore cannot pass with this branch alone. It also needs a science-neutral acceptance reissue that
  rotates only the reduce.py estimator pin (the r4–r8 precedent). That reissue is outside this
  WRITE_SCOPE and was not done.
- **Second side-effect (NEEDS_RULING N3, owner notified by push).** The dry run's steps 1 and 2
  re-reduce every kept bundle and require `energy_anchor_shift_envelopes` and
  `window_evidence_precheck` to equal the stored summary
  (`joulewise/b5_analysis/dry_run.py:741-755`, `REREDUCTION_REFIT_DIFFERS`). The CLI strict validator
  does the same check (`summary_metrics.json does not match a fresh re-reduction ... differing keys:
  energy_anchor_shift_envelopes./phase_energy_j/tokenize, window_evidence_precheck.phase.tokenize.reasons`).
  With the clamp, a fresh mint defines envelopes for phases shorter than 2·edge_bound at the minted
  bound, which origin/main omitted. Summaries minted at origin/main, which includes every block-5
  night, therefore no longer match their re-reduction whenever such a phase exists. Synthetically
  that is tokenize and generation_setup, and it is very likely on real MLX runs. Step 1/2 would refuse
  `rereduction_calibration_dependent_fields_differ` before step 4 is reached.
- At mint time the clamp also creates envelopes for phases that were always shorter than
  2·edge_bound (in the fixture: `tokenize` and `generation_setup`), with `lower_j == 0`. Their precheck
  reason moves from `anchor_energy_envelope_unrecorded` to `anchor_energy_envelope_exceeds_quarter_metric`.
  Both reasons are metric-local, so those phases stay ineligible. The test pins this as the only change
  to a full mint.

## E1: derivation (valid conservative bound; point estimate unchanged)

Phase window [s, e], with D = e − s. Independent edge errors are ε_on, ε_off ∈ [−g, g], where
g = edge_bound_s = fiducial_bound_s + wall_minus_monotonic_span_s. There is also a common shift
δ ∈ [−b, b] (bundle bound). Power P(t) ≥ 0 (the negative-power guard is kept).
E(ε_on, ε_off, δ) = ∫ over [s+ε_on+δ, e+ε_off+δ] of P. Writing the integral as max(0, ·) overlap,
which is what `_shift_energy_j` and `_integrate` compute, gives:

1. E does not increase as ε_on grows and does not decrease as ε_off grows, because the integrand is
   non-negative. So for each δ the minimum over the box is at the corner (+g, −g) and the maximum is
   at (−g, +g). The existing scanner evaluates δ exactly at each corner.
2. If D < 2g, the (+g, −g) corner gives start > end. A physical window cannot invert. The admissible
   windows with ε_on − ε_off ≤ D include ε_on − ε_off = D, which is a zero-length interval. Its energy
   is 0 for every δ. So the infimum of the true attainable energy for that window is exactly 0 J,
   reached in the limit. Replacing the inverted window with a zero-length one gives exactly this
   value, so the lower bound is valid (it is ≤ every attainable energy) and tight. The clamp puts the
   zero-length window at the midpoint (s+e)/2, because ε_on + ε_off = 0 at that corner. The midpoint
   lies inside the original window, so `_anchor_coverage_ok` cannot fail where the original window
   passed.
3. The upper corner (−g, +g) and the corners (−g, −g) and (+g, +g) never invert, because
   end − start ≥ D ≥ 0. So `upper_j` is unaffected.
4. `point_j = _shift_energy_j(contributions, 0.0)` uses the unshifted windows and is computed before
   the corners. It is unchanged. The test checks `point_j` against both the minted envelope and
   origin/main (exact equality).
5. Contributions with several windows: only the inverted window becomes 0. The others keep their
   corner windows, and per-window monotonicity still holds.

Brute-force check (`test_clamped_bound_contains_every_admissible_window_energy`): the test samples a
grid of 21×21 (ε_on, ε_off) values and 9 values of δ, skipping inverted windows as physics requires.
Every attainable energy lies inside the clamped [lower_j, upper_j].

## E1–E5 table

| Item | Evidence (branch) | Counterfactual at origin/main |
|---|---|---|
| E1 clamp | `joulewise/reduce.py:2238-2253`. `test_inverted_corner_clamps_to_zero_energy`: flat 10 W, g=0.1, D ∈ {0.19, 0.1, 1e-6}, lower=0, point=P·D, upper=P·(D+2g). Soundness grid test passes. `test_other_none_guards_are_unchanged`: 9 guard cases still return None on both versions. | The inverted cases return None. When the "new" functions are swapped to origin/main, `test_inverted_corner_clamps_to_zero_energy` and `test_clamped_bound_contains_every_admissible_window_energy` fail. |
| E2 byte identity | `test_reversed_source_is_the_sealed_pre_ruling_bytes` (reversed hunk = sha `7b9c0d28…`). `test_non_inverted_windows_are_bit_identical_to_origin_main`: more than 300 cases with dict equality. The cases cover interval and point traces, epoch 0 and epoch 1.78e9, 3 seeds, 3 bound sets including the fixture's real-shape g, D/(2g) ∈ {1, 1+1e-9, 1.01, 1.5, 3, 10}, and 1 or 2 windows. Inversion is judged in the function's anchor-relative coordinates. `test_existing_reduce_corner_fixtures_are_bit_identical`: the 4 corner fixtures from tests/test_reduce.py. `test_mint_differs_from_origin_main_only_on_inverting_phases`: full `reduce_bundle` mint. Every envelope origin/main records is bit-identical, and after removing the inverting phases the whole summary JSON is identical. | Not applicable (identity). The sweep found that rounding at epoch scale can invert a window whose nominal length is exactly 2g. Those cases are inverting and are excluded from the identity set. |
| E3 reproduction | `tests/test_reduce_inverted_corner_clamp.py::PermanentWideningCaseTests`, real `_build_v052_bundle` fixture. Prefill D = 0.13286 s. The minted bound gives 2g ≈ 0.0429 s < D. The operative bound is chosen so that D = 2g − 0.004 (just under) or D = 2g + 0.004 (just over). Just under: origin/main's operative summary lacks `/phase_energy_j/prefill` and the session refuses exactly `('anchor_energy_envelope_unrecorded',)`. After the clamp the prefill envelope is present, point equal, lower 0 ≤ minted lower, upper ≥ minted upper, and anchor_bound widened by exactly (operative − minted). The session is ready with a block-5-shape mint (origin/main) and with a post-ruling mint. Just over: the prefill envelope is identical between versions and all three session combinations are ready. Genuinely missing pointer (prefill or gross removed for another reason) still refuses exactly `('anchor_energy_envelope_unrecorded',)`. | With the new functions swapped to origin/main, `test_short_prefill_under_dominating_bound` fails and `test_genuinely_missing_operative_envelope_still_refuses` errors (KeyError: the pointer was never produced). |
| E4 freeze | `tests/b5_analysis/test_frozen_files.py`: `RULING_REBOUND` binds reduce.py to `d37f731c…`, with a comment citing Ed's 2026-10-30 ruling and this lane. `sealed_digests()` keeps the old construction. `test_reduce_rebinding_is_the_only_change`: sealed and frozen differ only at reduce.py, and the inventory still holds `7b9c0d28…`. `test_any_other_reduce_byte_fails_the_freeze`: four one-byte or few-byte variants (appended newline, `/ 2.0,`→`/ 2.00,`, last byte dropped, an added space) each make `frozen_mismatches` report reduce.py, and the exact bytes report nothing. | origin/main's test against the new reduce.py fails: `Lists differ: ['joulewise/reduce.py'] != []` (Ran 3, FAILED failures=1). The new test against origin/main's reduce.py also fails `['joulewise/reduce.py']` (Ran 5, FAILED failures=2). |
| E5 recompute / comparator | See below. Nothing was changed there. | — |

## E5: independent recompute, comparator, collection paths (report only)

- The independent recompute is not on main. It lives on `lane/2026-10-14-independent-recompute`
  (9ca87bcee) and on `lane/2026-10-27-recompute-comparator` (110b3e371), as
  `scripts/independent_recompute_b5.py`.
  - The envelope is `shift_envelope` (9ca87bcee :214-232; 110b3e371 :224-242). It takes corners over
    `itertools.product((-g, g), repeat=2)` with g = b + span (:219 / :229) and evaluates
    `overlap(records, onset+e_on+shift, offset+e_off+shift)`. `overlap` (:203-211 / :213-221) uses
    `length = max(0.0, min(y, end) - max(x, start))` (:207 / :217). So an inverted corner contributes
    0 J and the recompute never refuses. That is the same lower value as the clamp. Before the ruling
    the recompute and L9 already differed: the recompute gave a defined bound with lower 0, while L9
    gave no envelope.
  - Pre-existing definition differences that remain, unrelated to inversion: the common shift is
    `clock` (m) in the recompute but `bundle_bound_s` in L9; the recompute has no anchor-relative
    re-origin; its breakpoint set is different. These were already in the recompute's agreement bars.
  - Stored-envelope check: `stored_envelope_mismatch` (9ca87bcee :466-470; 110b3e371 :476-480) compares
    the bundle's stored (minted) `max_abs_delta_j` for request/prefill/decode with the recompute's
    pre-bound envelope. Minted block-5 summaries were produced by origin/main, so this check is
    unaffected. Tokenize and generation_setup are not compared.
  - `phase_bound(member, phase, bound)` (9ca87bcee :888-893) recomputes at an operative bound with
    the same 0 J lower corner. So at release the recompute should agree in kind with the clamped L9
    values for inverted prefill phases.
- Comparator `scripts/compare_b5_recompute.py` (110b3e371) computes no envelopes. It compares the
  downstream bound terms (`KIND_ORDER`, :2687) and the reported values. It inherits whatever the two
  sides produce.
- Collection-time paths (future nights):
  - `joulewise/controller.py:2579` → `reduce_bundle` mints `summary_metrics.json` at collection.
    Reducers 0.5.2 and AXI 0.6.2 (`reduce.py` ~2555 and ~3209/3244) use this function; frozen
    0.5.1/0.6.1 do not. New nights will mint envelopes for every phase shorter than 2g with lower 0
    instead of omitting them. The precheck reason changes as described above (still ineligible). Old
    minted summaries are not re-minted.
  - `joulewise/flags/collect.py:788-816`: on a night collected under the v5 sealed inventory, the
    executed-inventory check would flag `code.executed_differs_from_sealed` (reduce.py changed). This
    matters only for nights collected against that inventory (OPEN ISSUE O2).
  - Calibration acceptance estimator pin (N1): every collection-night bracket and acceptance
    evaluation goes stale until the acceptance is reissued.

## FILES CHANGED

- `joulewise/reduce.py`: only the inversion handling in `_corner_composed_anchor_shift_envelope`
  (sha256 `d37f731c07116c025a7670043e13c6a0f37bee74d2217ae08d160f4ac0074f8f`).
- `tests/test_reduce_inverted_corner_clamp.py`: new.
- `tests/b5_analysis/test_frozen_files.py`: reduce.py rebound, plus two new tests.
- `.codex-report/L9-ENV-2.md`: this report.

Not touched: `sealed_inventory.json`, `seal_pins.json`, any sealed registration file, the calibration
acceptance artifacts, `calibration_bracketing.py`.

## DECISIONS I MADE

1. The clamped window is placed at the shifted-window midpoint, so it always sits inside the original
   window and inside its trace coverage. Its energy is 0 wherever it is placed, so the placement only
   affects the coverage guard and the extra breakpoints. Extra breakpoints are admissible shifts and
   can only refine the result.
2. The origin/main reference is built from the current file by reversing exactly the ruling hunk,
   then authenticated by the sealed sha256. This avoids depending on a git object that a force-push of
   main could orphan (main was force-updated at fetch: `341adaf...0f34b2c`).
3. E3 session isolation. The retained powermetrics fixture (a 0.4 s request) fails metric-scale
   precheck and member-era capture checks at a 66 ms bound, for reasons the ruling does not touch.
   The session test therefore uses the repository's synthetic-session member shape, carrying the real
   minted summary and the real re-derived operative summaries. `_classify_precheck_refusals` is
   neutralised only after the test asserts that origin/main and the branch produce equal global
   classifications.
4. E4: the freeze keeps the old construction as `sealed_digests()` and overlays one rebinding. The
   overlay refuses if the sealed digest is not the pre-ruling one.

## OPEN ISSUES

- O0: suites are red on the branch, and every branch-only failure is N1 or N3 (table below). Existing
  tests that pin the old behaviour were not edited, because WRITE_SCOPE allows only new tests and
  test_frozen_files.py: `tests/test_reduce.py::test_d138_reduce_source_bytes_remain_at_issued_pin`
  (pins reduce.py = `7b9c0d28…` against the r7 acceptance) and
  `tests/test_whole_window_selection.py::test_rederivation_covers_every_named_metric_family`
  (exact pointer set; now also has `/phase_energy_j/tokenize` and `/phase_energy_j/generation_setup`).
- O1 (= N1): the estimator-pin staleness blocks the dry run until the acceptance is reissued.
- O1a: N1 also hits collection tooling. `tests/test_repin.py` shows
  `scripts.validate_powermetrics_fiducial._AcceptancePreflightError: acceptance_artifact_stale`
  (`pin g2_phase_d stale`), and `tests/test_harvest_b5_trigger_scope.py` shows that harvest bracket
  evaluation returns `('failed', ('calibration_acceptance_bound_stale',))`.
- O2: the v5 sealed inventory still lists reduce.py at `7b9c0d28…`. Executed-inventory flags on any
  further night under that inventory will show reduce.py as changed.
- O3: newly defined tokenize/generation_setup envelopes in future mints (lower 0, ineligible). Check
  that no consumer treats "envelope present" as eligibility.
- O4: the RC-CMP agreement run should be repeated on the clamped L9 to confirm that the recompute's
  inverted-corner values agree within bars.

## NEEDS_RULING

- N1: authorise a science-neutral reissue of the D-079 25g83 acceptance that rotates only the
  `joulewise/reduce.py` estimator pin to `d37f731c…`, in its own lane, or rule that the clamp is
  exempt from `protocol_or_estimator_byte_change`. Stricter reading taken here: no change outside
  WRITE_SCOPE, acceptance left stale, flagged.
- N3: how to reconcile the strict re-reduction with the clamp. Options: (a) apply the clamp only on
  the authenticated-bound re-derivation path, for example a keyword argument passed only by
  `_rederive_summary_for_authenticated_fiducial_bound`, so that a fresh mint stays byte-identical to
  origin/main; (b) exempt newly defined envelopes of phases with D < 2g in
  `require_rereduction_matches_stored` and the strict validator; (c) re-mint the stored summaries
  (not acceptable for sealed nights). Option (a) needs a WRITE_SCOPE beyond "only the inversion
  handling". Stricter reading taken here: the ruling is implemented exactly as worded, and N3 is
  flagged.
- N4: whether lanes that rotate pins may update the two existing pin tests in O0.
- N2: whether the v5 sealed inventory or an addendum should record the post-ruling reduce.py digest.
  Stricter reading taken here: sealed files untouched, and the freeze test carries the rebinding.

## VERIFICATION (exact tails)

TMPDIR=/tmp/l9envclamp/tmp (outside the checkout, no float-like token). Env
`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1`, python3.13.
Reduce/whole_window modules: tests.test_reduce, test_whole_window, test_whole_window_selection,
test_whole_window_parallel_strict, test_axi_burst_reduce, test_audit_reduce_degenerate,
test_scored_reduce, test_envelope_gate, test_hazard_whole_window_verdict, plus the new
test_reduce_inverted_corner_clamp.

Baseline = origin/main 0f34b2ca in a separate worktree, same env. The first parallel b5_analysis
runs hit `OSError: [Errno 28] No space left on device` (disk allowance) and are discarded. The serial
runs below hit no ENOSPC (count 0).

1. `python3.13 -m unittest discover -s tests/b5_analysis -t .`
   - branch: `Ran 938 tests in 3058.087s` / `FAILED (failures=21, errors=12, skipped=12)` / exit=1
   - origin/main: `Ran 1008 tests in 3743.107s` / `FAILED (failures=1, errors=5, skipped=13)` / exit=1
   - Failing on both (environment: the clone lacks historical git objects, `git show <sha>:...` exit
     128): test_adapter_no_context_three_cases_match_pinned_base,
     test_build_roster_and_projection_helpers_are_source_equal_at_governing_pins,
     test_no_context_blocks_1_to_3_byte_identical_to_pinned_base,
     test_non_archive_session_attribute_matches_pinned_base_on_stored_failure,
     test_only_git_seams_replay_registered_history_and_tracked_index.
   - Failing only on origin/main: test_G6_finalizer_main.
   - Failing only on the branch:
     - N1 (`AssertionError: ('calibration_acceptance_bound_stale',)`): setUpClass of test_bracket,
       test_claim_replay ×2, test_floor_kept_units.IndexedCliTests, test_issuer.IndexedCompositionTests
       and test_sensitivity_guard. These six skip about 70 tests, which explains 938 vs 1008. Also
       test_real_index_builder_refuses_a_floor_shaped_archive_as_gamma, test_v1_real_compositions_*,
       test_v1_first_and_fourth_sites_*, test_f3a/f3b/f3c_*, test_ca_archive_changed_after_real_composition,
       test_f1_composed_identity_and_mismatch, test_governed_spy_retains_real_context_and_units,
       test_r8_report_without_context_first_refusal, test_real_composition_bracket_shape_and_allowance
       and test_guard_setup_after_s4_preserves_the_cached_source.
     - N3 (strict re-reduction / `rereduction_calibration_dependent_fields_differ` /
       `['rereduced_alpha_first']` / tooling_refusal): the DeadlineTripwireTests
       (test_tripwire_*, test_failed_reduce_*, test_step1_strict_validation_*, test_step2_deadline_hit_*,
       test_unforced_step2_record_*), ObserverSitesTests.test_neg8_replay_strict_invalid_callback_firing_is_observed,
       and SharedPhysicsCache / MetadataBoundPartition test_cached_and_uncached_*, test_cached_bound_*,
       test_cross_call_reuse_*, test_a_higher_bound_seed_*.
   - tests.b5_analysis.test_frozen_files alone: `Ran 5 tests` / `OK`.
2. Reduce/whole_window modules (list above):
   - branch: `Ran 363 tests in 878.767s` / `FAILED (failures=2, skipped=1)`
   - origin/main: `Ran 353 tests in 885.827s` / `OK (skipped=1)`
   - Branch-only: test_d138_reduce_source_bytes_remain_at_issued_pin
     (`'d37f731c…' != '7b9c0d28…'`, N1 family) and test_rederivation_covers_every_named_metric_family
     (extra `/phase_energy_j/tokenize`, `/phase_energy_j/generation_setup`, N3 family).
   - tests.test_reduce_inverted_corner_clamp alone: `Ran 10 tests in 28.165s` / `OK`. Counterfactual
     with origin/main functions swapped in: `Ran 10 tests` / `FAILED (failures=5, errors=2)`.
3. `discover -s tests/independent_recompute -t .`
   - On this branch and on origin/main: `ImportError: Start directory is not importable:
     'tests/independent_recompute'` (the directory does not exist on main) / exit=1.
   - On `origin/lane/2026-10-14-independent-recompute` 9ca87bcee: `Ran 114 tests in 73.889s` /
     `OK (skipped=18)` / exit=0. That code imports no reduce.py, so the clamp cannot affect it.
4. Extra estimator-pin modules (test_digest_pin_census, test_repin, test_calibration_bracketing,
   test_harvest_b5_trigger_scope):
   - branch: `Ran 192 tests in 265.756s` / `FAILED (failures=22, errors=703, skipped=1)`
   - origin/main: `Ran 192 tests in 293.989s` / `FAILED (failures=1, errors=702, skipped=1)`
   - The 701 census errors come from missing git objects and occur on both. Branch-only failures are
     N1: harvest trigger-scope tests `('failed', ('calibration_acceptance_bound_stale',))`, repin
     `acceptance_artifact_stale`, item5 error.
