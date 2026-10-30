STATUS: DONE

# L9-ENV-5: L9-ENV-3-OPUS-REV fixes under the lead's rulings (opt-in analysis clamp)

Seat L9-ENV-5. Branch `lane/2026-10-30-l9-env-analysis-clamp`, continued from `0a799146c` (L9-ENV-4).
Review applied: `.codex-report/L9-ENV-3-OPUS-REV.md` on `origin/review/2026-10-30-l9-env3-opus-rev`
(`2c931f4c0`, ACCEPT_WITH_FIXES), under the lead rulings O-F1, O-F3, O-F4, O-F5 and O-F6 (joulewise-28).
I used synthetic data only (`JW_B5_SYNTHETIC_ONLY=1`). I did not open or search for real block-5/6/BYTES
data. I fetched the full history (`git fetch --unshallow origin`). Evidence is in `.codex-report/l9-env5/`.

## SUMMARY

- **O-F1 (opt-in clamp).** `AuthenticatedConsumptionSession` has a new keyword-only argument,
  `analysis_clamp: bool = False`. It is honoured only when it is literally `True`.
  - With the flag off, `_prepare` calls reduce's `_rederive_summary_for_authenticated_fiducial_bound`,
    exactly as origin/main does.
  - With the flag on, `_prepare` calls `_rederive_operative_summary`, which applies the clamp.
  - Removed-member audit sessions inherit the flag.
  - All 12 constructor calls in the 10 analysis consumers in WRITE_SCOPE opt in.
  - `scripts/run_campaign.py` is unchanged and never opts in. Its `_run_whole_window_verdict_locked`
    therefore refuses as at origin/main.
  - Tests:
    - (i) On the permanent-widening fixture, the default session reproduces origin/main's session
      state exactly (`json.dumps`-equal to a session built from origin/main's `whole_window.py`
      bytes) and refuses with `anchor_energy_envelope_unrecorded`.
    - (ii) Static: run_campaign never mentions the flag, every consumer passes `True`, and no other
      constructor call exists.
    - (iii) The dry-run step-4 floor extraction and the dry-run `_step_results` session are built
      with the flag on (runtime spies).
- **O-F3.** The clamp now needs at least one recorded member envelope that the mirror reproduces;
  otherwise it returns the summary unchanged. Tests cover this on both the 0.5.2 and the 0.6.2
  fixture. The reviewer's K3 fake-reader differential is ported. 0.6.2 sign flips (OPUS M09 =
  FABLE M11) and the summed-curve mutant are killed by the seat modules.
- **O-F4.** I ported K1 (mini oracle sweep with a mixed-sign trace), K2 (restamp invariants), K4
  (tail-refusal context and unknown `/phase_energy_j/*` pointer) and added ulp-level cases. OPUS
  M02, M06, M12 and M14 are killed. Of L9-ENV-4's survivors:
  - M01 (shifted start), M02 (shifted end) and M04 (dropped negative-power guard) are now **killed**.
    M01/M02 are not equivalent: they change the last bits of `lower_j` through the breakpoint set,
    and I found inputs that show it.
  - M03 (`<=`) is argued equivalent below.
- **O-F5.** The clamp returns `None` when any unshifted input window has `end_s < start_s`. A test
  covers this, with counterfactuals: e1b3a0510 and L9-ENV-4 both define an envelope for that input.
  Oracle equality on the ruled cases is unchanged; every sweep in the seat module still passes.
- **O-F6.** Noted (see OPEN ISSUES).
- **Mutation testing.** 39 mutants were run against both seat modules (table below). 35 are killed
  and 4 survive, each argued equivalent.
- **Verification.** The whole `tests/b5_analysis` directory is OK. I also ran 118 modules: every
  `tests/**/test_*.py` outside `tests/b5_analysis` that mentions `whole_window` or an edited call-site
  module. The 7 modules that fail also fail identically on origin/main `4c26b2e2c`, all because
  `/bin/zsh` is missing or the `backup command failed`. Exact tails are below.

## Findings

| Ruling | Change (this branch) | Evidence (test) | Counterfactual |
|---|---|---|---|
| O-F1 flag | `whole_window.py:1410` adds the keyword; `:1426` sets `self.analysis_clamp = analysis_clamp is True`; `:1748` passes the flag to removed-member sessions; `:1853-1857` picks `_rederive_operative_summary` only when the flag is on. | `FlagOffIsOriginMainTests` in `tests/test_whole_window_analysis_clamp_flag.py`: `test_default_is_off` (default `False`, keyword-only, `None`/`1`/`"yes"` → off); `test_flag_off_refuses_permanent_widening_like_origin_main` (default and explicit `False` sessions refuse `(anchor_energy_envelope_unrecorded,)` and their full state equals a session built from `7ebb7db2a:joulewise/whole_window.py`, which origin/main `4c26b2e2c` keeps byte-identical; contrast: `analysis_clamp=True` is ready, prefill `lower_j` 0); `test_flag_off_ready_session_is_origin_main_bytes` (just-over bound, ready, state equal); `test_flag_off_session_never_calls_the_clamp` (clamp patched to raise; reduce's function wrapped). | The seat modules run against `0a799146c`'s code: `Ran 43 tests` / `FAILED (failures=22, errors=8)`. Every O-F1 test fails, because there the default session clamps. Log: `l9-env5/counterfactual_0a799146c_code.log`. |
| O-F1 (ii) static | Call sites, all `analysis_clamp=True`: `floor_extraction.py:3181`; `analysis_engine/inputs.py:2031`, `:2135`, `:3801-3804` (gated, see DECISIONS); `b5_analysis/dry_run.py:1081`; `paper_reported_energy_issuer.py:149`; `window_duration_margins.py:802`; `floor_mint_estimator.py:490-491` (gated); `analysis_manifest_v3.py:3776`; `scripts/mint_floor_artifact.py:557`, `:1261`; `scripts/check_window_provenance.py:1055`; `scripts/produce_b5_disclosures.py:117`. | `CallSiteTests`: `test_run_campaign_never_passes_the_flag` (no `analysis_clamp` token in the file, one constructor, no `**` splat); `test_every_analysis_consumer_passes_true` (per-file call counts, literal `True`, or for the two gated sites the exact gated text); `test_no_unlisted_constructor` (the constructor appears in `joulewise/` and `scripts/` only in these files, run_campaign and whole_window); `test_removed_member_audit_sessions_inherit_the_flag`. | Mutants N01-N05 and N08-N12 are killed. |
| O-F1 (iii) dry run | — | `BlockFiveDryRunPathTests`: step 4 imports `scripts.extract_detection_floors.main`, whose `extract_indexed_pack` calls `floor_extraction.extract_cells(..., kept_units=kept, archive_context=context, ...)`; `test_floor_extraction_with_kept_units_opts_in` runs `extract_cells` with kept units on the S4 arithmetic fixture and the session kwargs carry `analysis_clamp=True`; `test_dry_run_step_results_session_opts_in` runs `dry_run._step_results` and its session is built with `analysis_clamp=True, mode='read_replay'`. | N08 (dry_run flag off) and N09 (floor_extraction flag dropped) are killed. |
| O-F3 0.6.2 | No code change (the mirror was already right; the tests are new). | `AxiV062ClampTests.test_fake_reader_differential_against_reduce_v060_grouping`: the reviewer's K3. Two sources × three requests × {prefill, decode, tokenize at −10 ms} with a 12.3 ms anchor shift; rows equal an independent rebuild of `_reduce_v060`'s per-(source, phase) union. Plus the existing real-AXI tests. | OPUS M09 (anchor-shift sign) is killed by 4 tests, and FABLE M17 (summed curve) by 2. |
| O-F3 guard | `whole_window.py:1261-1269` counts reproduced recorded member envelopes; `:1286-1289` returns `summary` when the count is 0. The L9-ENV-4 F2 key-insertion branch is now unreachable and removed (`:1331-1333`); see DECISIONS. | `PermanentWideningCaseTests.test_no_reproduced_member_envelope_is_not_clamped`: at 3× the critical bound (0.19926 s), reduce records no map. The analysis summary is then `json.dumps`-equal to reduce's and `_clamp…` returns the input object; an empty map does the same. The 0.6.2 sweep at 3× critical (0.13634 s) is unchanged from reduce, while the oracle still adds prefill. `expected_from_oracle` returns reduce's summary when no member envelope is recorded. | At `0a799146c` the same input gains `/phase_energy_j/decode` from an unproven mirror (asserted in the test). N06 (guard dropped) is killed by 3 tests. |
| O-F4 K1 | — | `AnalysisClampFunctionTests.test_reviewer_mini_sweep_with_mixed_sign_trace`: 2 epochs × {interval, point} × 2 edges × 7 lengths × 5 shapes × 2 spans, `json.dumps`-equal to e1b3a0510. The mixed-sign shape (one −1 W sample) refuses in all 112 cases; the positive-only control clamps. | OPUS M02 / FABLE M04 (guard dropped) is killed. |
| O-F4 ulp | — | `test_clamp_position_is_the_midpoint_to_the_last_bit`: four searched 40-point shapes (`_ulp_case` seeds 1618, 1760, 2352, 2353) that reduce refuses, the clamp defines, and that equal e1b3a0510 bit for bit. | M01 (shifted start) differs on 3 of the seeds, M02 (shifted end) on 1: `lower_j` changes in the last bits because the extra breakpoints differ. Search logs: `l9-env5/equiv_search.log` (`find_small.py` also checks that the midpoint equals the oracle on all 3000 cases). |
| O-F4 K2 | — | `RestampGateTests` (4 tests): only the stamp is replaced (outer and inner); a gate without the stamp is refused and left unchanged; an eligible gate is refused and left unchanged; eligibility never loosens. | OPUS M06 and M11 and FABLE M09 are killed. |
| O-F4 K4 | — | `test_tail_refusal_context_adds_envelopes_without_restamping`: `_derive_anchor_context` is wrapped to set `detail="post_window_trace_tail_shorter_than_anchor_bound"`. The envelopes are still added (prefill included) and the gates are unchanged. `test_unknown_recorded_member_pointer_fails_closed`: `/phase_energy_j/zz_unknown` at 3 bounds returns the input object. | OPUS M12 and M14 are killed. |
| O-F5 | `whole_window.py:990-992`: the guard tuple also refuses `any(window.end_s < window.start_s …)`. It runs after reduce's own mint call, so non-inverting input still gets reduce's bytes. | `test_input_window_inverted_at_zero_shift_is_refused`: `[5.1, 5.0]`, `[0.5, 0.6]+[0.81, 0.8]` and two-source `[2.0, 2.0−1e-9]` all give `None` (as reduce does); a zero-length input window still clamps. All oracle sweeps (`test_sweep_bit_identical_to_oracle`, K1, the fixture sweeps) are unchanged and pass. | e1b3a0510 and `0a799146c` both define an envelope for each of these cases (asserted). N07 is killed. |
| O-F6 | Note only. | — | — |

### Equivalence arguments for the four survivors

- **OPUS M03 (`end_s - eps_off_s`).** `eps_off` ranges over `{−e, +e}`, so the mutant visits the
  same four `(eps_on, eps_off)` corners in a different order. Any `None` corner refuses whatever the
  order. `min`/`max` over the same multiset of floats are exact and order-free, so the two are
  identical.
- **OPUS M08 / FABLE M03 (`<=` instead of `<`).** These differ only for a shifted window with
  `end_s == start_s`. That window becomes `Window(m, m)` with `m = (s + s) / 2.0`. For finite
  `|s| ≤ 8.98e307`, `s + s` is an exact doubling and `/ 2.0` an exact halving, so `m == s` bit for
  bit and the contribution list is unchanged. Re-origined trace times are many orders of magnitude
  below that bound. Random search found no difference (`equiv_search.log`, `M03_le: 0`).
- **FABLE M14 (always compute the body).** It drops the early `return minted`. If reduce defines an
  envelope, then no corner inverted and no input window inverted (reduce itself refuses both). The
  clamp list comprehension is then the identity, and the body performs reduce's operations in
  reduce's order, so it returns reduce's bytes. This rests on the body being an operation-for-operation
  copy of reduce's function. The oracle sweeps check that bit for bit against e1b3a0510, which
  equals reduce on non-inverting input.

## Mutation table

Each run: `python3.13 -m unittest tests.test_whole_window_inverted_corner_clamp tests.test_whole_window_analysis_clamp_flag`
in a `/tmp` worktree with the mutant applied in place and then restored (`l9-env5/mutation_runner.py`,
`l9-env5/mutants.py`). The worktrees were at `9641561fb`. N08-N12 were re-run at `d8050fca6` after the
gated call-site change. Mutants marked (rt) were re-targeted to this source. Format:
`mutant | verdict | Ran | last line | failing tests` (failing-test list truncated here; the full list
is in `l9-env5/mutation_results.txt`).

```
O-M01_clamp_to_start | KILLED | Ran 43 | FAILED (failures=3) | test_clamp_position_is_the_midpoint_to_the_last_bit
E-M02_clamp_to_end | KILLED | Ran 43 | FAILED (failures=1) | test_clamp_position_is_the_midpoint_to_the_last_bit
O-M02_drop_negative_power_guard(rt) [=E-M04] | KILLED | Ran 43 | FAILED (failures=1) | test_reviewer_mini_sweep_with_mixed_sign_trace
O-M03_eps_off_sign | SURVIVED (equivalent) | Ran 43 | OK
O-M04_mirror_drops_items | KILLED | Ran 43 | FAILED (failures=12, errors=1)
E-M06_mirror_drops_blocks | KILLED | Ran 43 | FAILED (failures=12, errors=1)
O-M05_restamp_all_member_gates [=E-M08] | KILLED | Ran 43 | FAILED (failures=15, errors=1)
O-M06_restamp_sets_eligible | KILLED | Ran 43 | FAILED (failures=3) | ...restamp_never_loosens_eligibility, ...refuses_an_eligible_gate
E-M09_restamp_ignores_eligible | KILLED | Ran 43 | FAILED (failures=2)
O-M07_skip_reconstruction_proof(rt) [=E-M10] | KILLED | Ran 43 | FAILED (failures=1)
O-M08_clamp_le [=E-M03] | SURVIVED (equivalent) | Ran 43 | OK
O-M09_v062_anchor_shift_sign [=E-M11] | KILLED | Ran 43 | FAILED (failures=6) | test_fake_reader_differential_against_reduce_v060_grouping, ...
O-M10_corner_none_continue | KILLED | Ran 43 | FAILED (failures=19)
O-M11_restamp_keeps_unrecorded | KILLED | Ran 43 | FAILED (failures=14)
O-M12_skip_tail_refusal_return | KILLED | Ran 43 | FAILED (failures=1) | test_tail_refusal_context_adds_envelopes_without_restamping
O-M13_flag_on_session_unclamped(rt) | KILLED | Ran 43 | FAILED (errors=5)
O-M14_unknown_pointer_guard_dropped [=E-M18] | KILLED | Ran 43 | FAILED (failures=4) | ..., test_unknown_recorded_member_pointer_fails_closed
O-M15_mirror_drops_levels | KILLED | Ran 43 | FAILED (failures=12, errors=1)
O-M16_edge_minus_span [=E-M05] | KILLED | Ran 43 | FAILED (failures=897)
O-M17_v052_raw_curve [=E-M07] | KILLED | Ran 43 | FAILED (failures=12, errors=1)
E-M12_clamped_appended_last | KILLED | Ran 43 | FAILED (failures=7)
E-M13_clamp_disabled | KILLED | Ran 43 | FAILED (failures=13, errors=1)
E-M14_always_recompute_body | SURVIVED (equivalent) | Ran 43 | OK
E-M15_restamp_skips_inner_windows | KILLED | Ran 43 | FAILED (failures=13)
E-M16_gate_reasons_without_joint_bound | KILLED | Ran 43 | FAILED (errors=1)
E-M17_v062_summed_curve | KILLED | Ran 43 | FAILED (failures=2)
E-MF1_keep_passing_envelope | KILLED | Ran 43 | FAILED (failures=1)
N01_default_flag_true | KILLED | Ran 43 | FAILED (failures=6, errors=1)
N02_flag_ignored_always_on | KILLED | Ran 43 | FAILED (failures=7, errors=1)
N03_prepare_always_clamps | KILLED | Ran 43 | FAILED (failures=6, errors=1)
N04_member_sessions_drop_flag | KILLED | Ran 43 | FAILED (failures=1)
N05_truthy_flag | KILLED | Ran 43 | FAILED (failures=1) | test_default_is_off
N06_drop_OF3_reproduced_guard | KILLED | Ran 43 | FAILED (failures=3)
N07_drop_OF5_input_inversion_guard | KILLED | Ran 43 | FAILED (failures=3)
N08_dry_run_flag_off | KILLED | Ran 43 | FAILED (failures=2) | test_dry_run_step_results_session_opts_in,test_every_analysis_consumer_passes_true
N09_floor_extraction_flag_dropped | KILLED | Ran 43 | FAILED (failures=1, errors=1) | test_every_analysis_consumer_passes_true,test_floor_extraction_with_kept_units_opts_in
N10_inputs_site3_flag_dropped(rt) | KILLED | Ran 43 | FAILED (failures=1) | test_every_analysis_consumer_passes_true
N11_issuer_flag_dropped | KILLED | Ran 43 | FAILED (failures=1) | test_every_analysis_consumer_passes_true
N12_floor_mint_estimator_gate_inverted | KILLED | Ran 43 | FAILED (failures=1) | test_every_analysis_consumer_passes_true
```

The table has 39 rows: 35 KILLED and 4 SURVIVED. All four survivors are argued equivalent above.
FABLE MF2 (map key appended last) no longer applies because its branch was removed. I did not
mutate `scripts/run_campaign.py`, even in a temporary worktree, because it is outside the write
scope. `test_run_campaign_never_passes_the_flag` covers it statically.

## FILES CHANGED

- `joulewise/whole_window.py`. Changes are limited to:
  - `_clamped_corner_composed_anchor_shift_envelope`: the O-F5 guard and docstring.
  - `_clamp_inverted_operative_envelopes`: the O-F3 guard, removal of the dead key-insertion branch,
    and docstring.
  - The `_rederive_operative_summary` docstring.
  - `AuthenticatedConsumptionSession.__init__`: the flag.
  - `_prepare`: flag propagation to removed-member sessions and the choice of re-derivation.
- The analysis call sites, which only gain the flag:
  - `joulewise/floor_extraction.py`
  - `joulewise/analysis_engine/inputs.py` (3 sites)
  - `joulewise/b5_analysis/dry_run.py`
  - `joulewise/paper_reported_energy_issuer.py`
  - `joulewise/window_duration_margins.py`
  - `joulewise/floor_mint_estimator.py`
  - `joulewise/analysis_manifest_v3.py`
  - `scripts/mint_floor_artifact.py` (2 sites)
  - `scripts/check_window_provenance.py`
  - `scripts/produce_b5_disclosures.py`
- `tests/test_whole_window_inverted_corner_clamp.py`:
  - New helpers `run_session` (module-level, flag-aware, runs against an origin/main shadow module)
    and `whole_window_at`.
  - `expected_from_oracle` handles the O-F3 case.
  - The F2 key-position test is replaced by the O-F3 test.
  - New tests: K1, ulp, O-F5, tail-refusal, unknown-pointer, `RestampGateTests` and K3.
  - The 0.6.2 sweep's expectations are updated for O-F3.
- `tests/test_whole_window_analysis_clamp_flag.py` (new): O-F1 tests (i)-(iii).
- `.codex-report/L9-ENV-5.md` and `.codex-report/l9-env5/` (evidence).
- Not touched: `joulewise/reduce.py`, every `ESTIMATOR_CODE_PATHS` file, `scripts/run_campaign.py`,
  `configs/**`, `tests/b5_analysis/test_frozen_files.py` and `tests/oracle_l9_env_2_reduce_clamp.py`.
  `git diff origin/main -- joulewise/reduce.py scripts/run_campaign.py configs tests/b5_analysis` is empty.
- None of the listed call sites is frozen. `frozen_digests()` contains `scripts/run_campaign.py`
  only; `whole_window.py` is explicitly excluded from pin4, and `FrozenFilesTests` passes in the
  `b5_analysis` run.

## DECISIONS

1. **Strict flag.** `analysis_clamp is True`, so a truthy non-bool such as `1` or `"yes"` does not
   opt in. The flag is keyword-only and defaults to `False`. Removed-member audit sessions inherit it,
   so a flagged session audits removed members the same way it treats survivors.
2. **Signature-gated opt-in at two sites.** At `analysis_engine/inputs.py:3801` (`load_analysis_inputs`)
   and `floor_mint_estimator.py:490`, the flag is passed only when
   `"analysis_clamp" in inspect.signature(AuthenticatedConsumptionSession).parameters`. This copies
   `load_analysis_inputs`' existing idiom for `calibration_ledger_snapshot`. I needed it because two
   existing tests outside the write scope pin the old call shape:
   - `tests.test_analysis_integration` uses a fake with `__init__(self, runs_root, bundle_ids, *, mode)`.
   - `tests.test_floor_mint_estimator` uses `assert_called_once_with(...)` with exact kwargs.

   With the real class the flag is always passed; `test_default_is_off` pins that the parameter
   exists. `CallSiteTests` pins the gated text exactly, so neither site can silently drop it.
   The first full run, before this change, failed exactly these two modules
   (`l9-env5/run1_module_tails_9641561fb.txt`).
3. **Line-number pin kept.** In `analysis_manifest_v3.py` the flag shares the line with
   `calibration_ledger_snapshot=snapshot,`. The reason is that `tests.test_authentication_io`'s
   `CLASSIFIED_NON_AUTHENTICATION_READS` pins `_write_append_only` read lines by number, and adding
   a line shifted them (also caught by run 1).
4. **O-F3 counts reproduced recorded member envelopes.** Only `/phase_energy_j/`,
   `/suite_item_energy_j/`, `/suite_block_energy_j/` and `/suite_level_energy_j/` count; the gross
   family does not, because it does not exercise the member mirror. Since a reproduced envelope
   implies reduce recorded the map, L9-ENV-4's F2 branch (inserting the map at its `SummaryMetrics`
   position) is unreachable. I replaced it with a plain assignment and a comment. The F2 test became
   the O-F3 test, because the 3× bound is exactly the unproven case.
5. **O-F5 placement.** The guard sits in the existing `None`-guard tuple, after reduce's own mint
   call. Any input reduce defines is still returned as reduce's bytes, and reduce returns `None` for
   inverted input windows anyway.
6. **Origin/main reference for (i).** The test builds a separate module from
   `7ebb7db2a:joulewise/whole_window.py`, the ruling's base, and runs the same session. I checked that
   `git diff 7ebb7db2a origin/main -- joulewise/whole_window.py` is empty at `4c26b2e2c`. The test is
   skipped only if that object is missing from the clone.

## OPEN ISSUES

- **O-F6 (note).** Behind the flag, every dominated member's tokenize and generation_setup gates
  move from `anchor_energy_envelope_unrecorded` to `anchor_energy_envelope_exceeds_quarter_metric`
  (both metric-local), not only the rare short-prefill case. Without the flag (run_campaign) nothing
  changes.
- **Gated sites are mock-friendly by design.** A future fake or `MagicMock` constructor at those two
  sites will not receive the flag. Production always does. Updating the two pinned tests to expect
  `analysis_clamp=True` would let both sites pass the keyword literally (see NEEDS_RULING).
- `origin/main` has moved to `4c26b2e2c` (62 commits). Those commits touch no file in this lane's
  scope and add no `AuthenticatedConsumptionSession` constructor (checked `scripts/compare_b5_recompute.py`
  and `scripts/independent_recompute_b5.py`). After a merge, `test_no_unlisted_constructor` will
  catch any new unflagged consumer.
- L9-ENV-4's O1 (lower-0 envelopes appear in operative provenance for ineligible members) still
  applies, but only to flagged sessions now.

## NEEDS_RULING

- **NR1 (optional cleanup).** Should a follow-up lane widen the write scope to
  `tests/test_analysis_integration.py` (the fake session signature) and `tests/test_floor_mint_estimator.py`
  (the exact-kwargs assertion)? The two signature-gated call sites could then pass
  `analysis_clamp=True` literally. I recommend it; it is not required for correctness.
- Carried over: L9-ENV-4 NR1 (a clamped envelope never makes a member eligible), and gross-family
  pointers are never clamped.
- No listed call site is frozen, so I have no frozen-file ruling to request.

## VERIFICATION (exact tails)

Code commit `d8050fca6`, run from a clean `/tmp` worktree (`/tmp/lnine-env5/wt-final`). Python 3.13,
Linux container. `TMPDIR=/tmp/lnine-env5/tmp` is outside the checkout and contains no float-like
token. Environment: `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1`. I ran
`python3.13 -m unittest discover -s tests/b5_analysis -t .` over the whole directory. I then ran 118
modules, each as its own process: every `tests/**/test_*.py` outside `tests/b5_analysis` that
mentions `whole_window`, `floor_extraction`, `analysis_engine`, `dry_run`, `paper_reported_energy_issuer`,
`window_duration_margins`, `floor_mint_estimator`, `analysis_manifest_v3`, `mint_floor_artifact`,
`check_window_provenance` or `produce_b5_disclosures` (`l9-env5/run_modules.sh`). Format:
`module | Ran line | last line`.

```
b5_analysis | Ran 1008 tests in 3892.212s | OK (skipped=13)
tests.hazards.test_refusal_allowlist | Ran 23 tests in 28.109s | OK (skipped=1)
tests.test_acc_25g83_rev6 | Ran 27 tests in 145.268s | OK
tests.test_analysis_claims | Ran 65 tests in 5.526s | OK
tests.test_analysis_engine | Ran 13 tests in 0.283s | OK
tests.test_analysis_engine_evidence_roots | Ran 3 tests in 64.995s | OK
tests.test_analysis_engine_v2_binding | Ran 9 tests in 103.905s | OK
tests.test_analysis_finalizer | Ran 18 tests in 65.170s | OK
tests.test_analysis_inputs | Ran 28 tests in 83.031s | OK (skipped=1)
tests.test_analysis_integration | Ran 116 tests in 191.267s | OK
tests.test_analysis_manifest | Ran 27 tests in 8.819s | OK
tests.test_analysis_manifest_v3 | Ran 19 tests in 2.081s | OK
tests.test_analysis_multiplicity | Ran 25 tests in 2.289s | OK
tests.test_analysis_ratio | Ran 2 tests in 0.001s | OK
tests.test_analysis_ratio_integration | Ran 11 tests in 0.044s | OK
tests.test_arm_readiness_dry_run | Ran 12 tests in 71.993s | OK
tests.test_arm_readiness_evidence_author | Ran 24 tests in 110.542s | OK
tests.test_arm_readiness_evidence_t0 | Ran 81 tests in 300.438s | OK (skipped=6)
tests.test_arm_readiness_integration | Ran 13 tests in 83.026s | OK
tests.test_arm_readiness_lifecycle | Ran 70 tests in 72.471s | OK (skipped=1)
tests.test_arm_readiness_schemas | Ran 51 tests in 1.459s | OK
tests.test_authentication_io | Ran 22 tests in 2.520s | OK
tests.test_axi_analysis_manifest | Ran 23 tests in 0.365s | OK
tests.test_axi_controller_events | Ran 7 tests in 1.021s | OK
tests.test_axi_mock_spec | Ran 11 tests in 11.317s | OK
tests.test_axi_output_identity | Ran 13 tests in 0.094s | OK
tests.test_b5_chain | Ran 25 tests in 3.268s | FAILED (errors=21)
tests.test_b5_chain_prune2 | Ran 44 tests in 19.987s | FAILED (failures=1, errors=10)
tests.test_battery_float_consumers | Ran 18 tests in 36.212s | OK
tests.test_battery_float_sweep | Ran 5 tests in 5.574s | OK
tests.test_bracket_binding_cli | Ran 19 tests in 47.592s | OK
tests.test_bundle_read | Ran 82 tests in 11.077s | OK
tests.test_calibration_custody_store | Ran 7 tests in 0.266s | OK
tests.test_calibration_ledger | Ran 95 tests in 13.295s | OK (skipped=1)
tests.test_calibration_ledger_custody | Ran 62 tests in 97.385s | OK
tests.test_capture_pipeline_era | Ran 10 tests in 2.446s | OK
tests.test_check_window_provenance | Ran 44 tests in 94.034s | OK
tests.test_claim_side_bound | Ran 26 tests in 0.062s | OK
tests.test_claims_index_lint | Ran 30 tests in 10.101s | OK
tests.test_collector_analysis_manifest_id | Ran 16 tests in 95.082s | OK
tests.test_controller_hazard_flags | Ran 58 tests in 317.979s | OK
tests.test_corpus_strict_validation | Ran 3 tests in 1.003s | OK (skipped=1)
tests.test_custody_mode_inventory | Ran 7 tests in 131.243s | OK
tests.test_d078_reason_registry | Ran 14 tests in 0.193s | OK
tests.test_d117_contrast_v5_pack | Ran 48 tests in 36.477s | OK
tests.test_d117_decode_contrast_plan | Ran 25 tests in 70.159s | OK (skipped=1)
tests.test_d117_floor_qwen25_1p5b_plan | Ran 22 tests in 27.225s | OK
tests.test_d117_floor_qwen25_7b_plan | Ran 20 tests in 37.726s | OK
tests.test_d117_gamma_d139a2_families | Ran 14 tests in 3.353s | OK
tests.test_d165_dominance_closeout | Ran 59 tests in 24.785s | OK
tests.test_decisive_reference_resolution | Ran 1 test in 0.101s | OK
tests.test_dependence_sensitivity | Ran 29 tests in 19.701s | OK
tests.test_detection_floor | Ran 131 tests in 6.326s | OK
tests.test_dominance_closeout | Ran 3 tests in 3.297s | OK
tests.test_emit_floor_mint_pinset | Ran 9 tests in 7.198s | OK
tests.test_finalize_analysis_manifest | Ran 13 tests in 72.558s | OK
tests.test_floor_extraction | Ran 145 tests in 23.972s | OK (skipped=2)
tests.test_floor_mint_estimator | Ran 38 tests in 32.661s | OK
tests.test_harvest_b5_p2harv | Ran 48 tests in 105.914s | OK (skipped=4)
tests.test_harvest_b5_p3harv | Ran 48 tests in 61.136s | OK
tests.test_harvest_b5_rehearsal_compare | Ran 1 test in 0.000s | OK (skipped=1)
tests.test_harvest_b5_sources | Ran 55 tests in 2.715s | OK
tests.test_harvest_b5_trigger_scope | Ran 28 tests in 209.644s | OK
tests.test_harvest_b5_window | Ran 208 tests in 581.679s | OK (skipped=26)
tests.test_harvest_v5_g2b_window | Ran 28 tests in 16.377s | OK
tests.test_hazard_neg8_mint_verdicts | Ran 14 tests in 6.533s | OK
tests.test_hazard_whole_window_verdict | Ran 20 tests in 38.936s | OK
tests.test_identity_pins | Ran 42 tests in 8.828s | OK
tests.test_issue_calibration_acceptance_generation | Ran 156 tests in 312.401s | OK (skipped=18)
tests.test_launch_window | Ran 39 tests in 477.883s | OK
tests.test_magistrate_watchdog | Ran 155 tests in 2.143s | FAILED (errors=3)
tests.test_magistrate_watchdog_cli | Ran 7 tests in 13.758s | OK
tests.test_magistrate_watchdog_span | Ran 24 tests in 0.207s | OK
tests.test_mint_analysis_admission | Ran 8 tests in 6.346s | OK
tests.test_mint_floor_artifact | Ran 42 tests in 12.526s | OK
tests.test_mint_floor_artifact_generalized | Ran 84 tests in 155.237s | OK (skipped=2)
tests.test_mint_floor_artifact_generalized_d165 | Ran 2 tests in 4.820s | OK
tests.test_mint_floor_v2_config_set | Ran 9 tests in 14.744s | OK
tests.test_neg8_corpus_cap | Ran 19 tests in 124.748s | OK
tests.test_neg8_survivors | Ran 89 tests in 203.557s | FAILED (errors=4)
tests.test_night_gate | Ran 112 tests in 2.273s | OK (skipped=1)
tests.test_paper_comparison_placements | Ran 21 tests in 21.678s | OK
tests.test_paper_custody | Ran 33 tests in 59.018s | OK
tests.test_paper_rendering | Ran 6 tests in 3.357s | OK
tests.test_paper_renumber_refs | Ran 3 tests in 0.351s | OK
tests.test_paper_reported_energy | Ran 30 tests in 4.818s | OK
tests.test_paper_terms_lint | Ran 16 tests in 3.317s | OK
tests.test_pipeline_smoke_tail | Ran 4 tests in 9.293s | OK (skipped=1)
tests.test_powermetrics_fiducial | Ran 76 tests in 158.149s | OK
tests.test_quick_suite | Ran 15 tests in 0.181s | OK
tests.test_r4_acceptance_oracle | Ran 10 tests in 4.532s | OK
tests.test_reason_code_partition | Ran 3 tests in 16.302s | OK
tests.test_reduce | Ran 132 tests in 518.177s | OK
tests.test_render_results_fills_live | Ran 4 tests in 1.891s | OK
tests.test_repin | Ran 47 tests in 16.631s | OK
tests.test_results_fill_adapter | Ran 6 tests in 0.215s | OK
tests.test_revision6_seal | Ran 3 tests in 0.772s | OK
tests.test_run_campaign | Ran 267 tests in 310.530s | OK (skipped=1)
tests.test_run_campaign_hazard_flags | Ran 46 tests in 23.353s | OK (skipped=3)
tests.test_run_campaign_max_blocks | Ran 22 tests in 7.874s | OK
tests.test_run_d165_closeout_from_custody | Ran 35 tests in 270.656s | OK
tests.test_single_count_discipline_census | Ran 6 tests in 35.100s | OK
tests.test_single_count_discipline_matrix | Ran 12 tests in 17.372s | OK
tests.test_supersession_cross_consumer | Ran 15 tests in 0.101s | OK
tests.test_v5_block4_replay | Ran 14 tests in 14.613s | FAILED (errors=1, skipped=6)
tests.test_v5_block4_x12b | Ran 11 tests in 13.717s | FAILED (errors=1)
tests.test_v5_block4_x2 | Ran 15 tests in 24.208s | OK
tests.test_v5_s1_desk_closeout | Ran 7 tests in 3.723s | FAILED (errors=2)
tests.test_v5_s1_qualification | Ran 23 tests in 12.993s | OK
tests.test_whole_window | Ran 26 tests in 0.927s | OK
tests.test_whole_window_analysis_clamp_flag | Ran 11 tests in 86.220s | OK
tests.test_whole_window_inverted_corner_clamp | Ran 32 tests in 132.795s | OK
tests.test_whole_window_parallel_strict | Ran 8 tests in 1.331s | OK
tests.test_whole_window_selection | Ran 57 tests in 201.860s | OK
tests.test_window_duration_margins | Ran 42 tests in 23.839s | OK
tests.test_window_lineage | Ran 52 tests in 102.376s | OK (skipped=1)
tests.twins.test_engine_twin_comparison | Ran 14 tests in 0.580s | OK
tests.twins.test_harvest_twin | Ran 16 tests in 0.002s | OK
tests.twins.test_harvest_twin_comparison | Ran 7 tests in 8.936s | OK
```

Baseline: the failing modules at origin/main `4c26b2e2c`, same container and environment:

```
tests.test_b5_chain | Ran 25 tests in 5.522s | FAILED (errors=21)
tests.test_b5_chain_prune2 | Ran 44 tests in 21.198s | FAILED (failures=1, errors=10)
tests.test_magistrate_watchdog | Ran 155 tests in 5.027s | FAILED (errors=3)
tests.test_neg8_survivors | Ran 89 tests in 226.166s | FAILED (errors=4)
tests.test_v5_block4_replay | Ran 14 tests in 21.655s | FAILED (errors=1, skipped=6)
tests.test_v5_block4_x12b | Ran 11 tests in 23.715s | FAILED (errors=1)
tests.test_v5_s1_desk_closeout | Ran 7 tests in 6.425s | FAILED (errors=2)
```

All 7 failing modules fail identically on origin/main: same counts and the same exception lines per
module. The only difference is the survivor PID in `test_b5_chain_prune2`'s sandbox process-tree
message. The causes are `FileNotFoundError: '/bin/zsh'` (`test_b5_chain` 21, `test_b5_chain_prune2` 10
plus the process-tree failure, `test_magistrate_watchdog` 3, `test_neg8_survivors` 4,
`test_v5_block4_replay` 1) and `ValueError: backup command failed` (`test_v5_block4_x12b` 1,
`test_v5_s1_desk_closeout` 2). The other 111 modules are OK, including `tests.test_whole_window_inverted_corner_clamp`
(32 tests) and `tests.test_whole_window_analysis_clamp_flag` (11 tests).

Run 1, at `9641561fb` (before DECISIONS 2 and 3), also failed `tests.test_analysis_integration`,
`tests.test_authentication_io` and `tests.test_floor_mint_estimator`. All three pass at `d8050fca6`.
Log: `l9-env5/run1_module_tails_9641561fb.txt`.
