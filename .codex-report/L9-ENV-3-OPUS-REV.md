VERDICT: ACCEPT_WITH_FIXES

# L9-ENV-3-OPUS-REV: blocking review of lane L9-ENV-3 (analysis-side inverted-corner clamp)

Seat: L9-ENV-3-OPUS-REV (one of two parallel blocking reviews, gate policy rule 3). Branch
`review/2026-10-30-l9-env3-opus-rev` = `3e4d359c2` plus this report and its evidence dir only.
Under review: `origin/main...3e4d359c2` (merge base `7ebb7db2a`; origin/main has since moved to
`8b2cec2f4`, which touches no `joulewise/` file and merges cleanly with the lane). Oracle:
`e1b3a0510:joulewise/reduce.py` (sha256 `d37f731c…`), loaded straight from the git object as a
separate module. I did not use the seat's vendored copy. Synthetic fixtures only; I did not open
or search for any real block-5/6/BYTES data. Evidence: `.codex-report/l9-env3-opus-rev/`.

## Bottom line

The clamp is right where it counts. Bit for bit, the analysis-side envelope equals e1b3a0510's
patched reducer on my own 9,118-case sweep. The 0.5.2 window-set mirror reproduces reduce's own
mint calls exactly, with all four pointer families exercised on the real fixture. reduce.py and
the minted bytes are untouched. Four issues need fixing or an explicit ruling before merge; none
needs reduce.py to change. F1 needs a lead/Ed ruling. F2 is a code fix plus a report correction.
F3 and F4 are test/guard additions. Nothing found loosens eligibility in the consumers I traced,
so I do not REJECT.

## Findings (ranked)

### F1 (High, R3 scope; needs a lead/Ed ruling or a gate). `run_campaign` reaches the clamp and persists its output

- Path: `scripts/run_campaign.py:8367` `_run_whole_window_verdict_locked` (`--whole-window-verdict`
  with `MAX_BRACKET`/`SALVAGE_DANGLER` consumption semantics) → `:8425`
  `AuthenticatedConsumptionSession(...)` → `:8433` `_prepare` → `joulewise/whole_window.py:1829`
  `_rederive_operative_summary` → clamp. The operative summaries replace the member summaries
  (`run_campaign.py:8449`). `consumption_provenance`, which includes `operative_envelopes`, then
  goes into `build_evaluation_basis` (`:8539`) and is appended to the campaign log (`:8596`
  `append_log`).
- So the seat's "only the consumption session … nothing is persisted" (L9-ENV-3.md, Design) is
  not the full picture. The lane brief lists `run_campaign` among the collection paths that must
  not reach the clamp. Before this lane, a dominated member whose operative re-derivation inverted
  made this verb raise (`authenticated survivor consumption refused`). With the lane, it appends a
  verdict row that carries clamped `lower_j = 0` envelopes.
- What does not reach it (verified, `r3_scope_probe.log`): reduce, controller,
  calibration_bracketing and harvest. harvest has zero `consumption_session` references and calls
  `validate_whole_window_verdict_row` without a session. The mint precheck can't reach it either:
  reduce.py has the same sha256 `7b9c0d28…` on both sides, and the new symbols have no caller
  outside whole_window.py. There is no monkeypatch and no mutable module state; the only new
  module-level names are a str constant and a tuple.
- Fix (either one):
  - (a) Ed or the lead rules that the whole-window verdict verb is analysis-side consumption, which
    in substance it is (post-collection, in-memory re-derivation, mints untouched). The report then
    has to say so, and a test should pin that a max-bracket verdict row's
    `evaluation_basis.consumption_provenance[*].operative_envelopes` carries the clamped envelope.
  - (b) Make the clamp opt-in on the session (`AuthenticatedConsumptionSession(...,
    analysis_clamp=False)`) and enable it only from the analysis consumers (analysis_engine,
    floor_extraction/mint, b5_analysis, issuers). The run_campaign verdict then refuses exactly as
    at origin/main.

  I recommend (a) because the verdict is the consumption the ruling is meant to unblock, but it
  must be an explicit ruling, not left implicit.

### F2 (Medium, R4). A clamped gate can end as `{"eligible": false, "reasons": []}`; the seat's NEEDS_RULING R2 is factually wrong

- Code: `joulewise/whole_window.py:1168-1194` `_restamp_clamped_gate`, called at `:1321-1325`.
  When `_anchor_envelope_gate_reasons(clamped, joint)` is `[]`, the restamp removes
  `anchor_energy_envelope_unrecorded` and adds nothing. `eligible` stays `false`.
- The seat says this is "only possible for an all-zero-power window with no joint bound"
  (L9-ENV-3.md NEEDS_RULING R2). That is false. Any multi-window member where only one short
  window inverts passes the quarter gate. Examples: a 0.5.2 suite phase spanning several items,
  or a 0.6.2 per-source union of many request windows.
- Evidence (`r4_restamp_probe.log`): a decode with four 2 s windows and one 0.1 s window at
  edge 0.0656 s. The mint gives `None`; the clamped envelope is point 81.0, lower 74.752,
  upper 87.56 (deviation 7.7 % < 25 %), so the gate reasons are `[]`. After the restamp, the gate
  and its inner window read `{"eligible": false, "reasons": []}`.
- Consequences I traced:
  - `_classify_precheck_refusals` returns `(set(), {})`, so `path_refusal_reasons` loses the path.
    `scripts/mint_floor_artifact.py:579-587` checks the target `("phase","decode")` only through
    `path_refusal_reasons`, so that check now passes.
  - Downstream `analysis_engine/inputs.py:4071-4076` still refuses, but as
    `window_evidence_precheck_missing` (a mislabelled reason, not a loosening).
  - `harvest.py:7706` and `run_campaign.py:8751` also refuse.
  - `scripts/check_sealed_bundle_compatibility.py:179` treats `eligible == bool(reasons)` as
    malformed.

  Eligibility did not loosen in any consumer I traced. But the restamped gate breaks the
  repository-wide `eligible ⇔ reasons == []` invariant, and the session-level per-path refusal
  map now disagrees with the gate.
- Fix: in `_clamp_inverted_operative_envelopes`, when the clamped reasons are empty, do not
  restamp that gate: leave `anchor_energy_envelope_unrecorded`, which keeps a consistent,
  metric-local refusal, but still add the envelope so minted-pointer coverage passes. (Or get the
  ruling to set `eligible: true`, which is what e1b3a0510 would mint. That would add a census
  site and is out of this lane's scope.) Add a test with a multi-window phase, and correct R2 in
  L9-ENV-3.md.

### F3 (Medium, R2). 0.6.2 mirror has no runtime proof in the lane's tests; the reconstruction proof can be vacuous

- `_group_envelope_contributions` 0.6.2 branch (`whole_window.py:1100-1130`) matches
  `reduce._reduce_v060` (`reduce.py:2944-2965` and `:3218-3235`) by reading. My fake-reader
  differential (`reviewer_checks.py` K3) agrees. But no lane test exercises 0.6.2: mutant M09
  (anchor-shift sign flipped in the 0.6.2 branch) passes all 17 seat tests.
- In production, the guard at `:1253-1259` fails closed only if at least one member envelope was
  recorded and is reproduced. If every member pointer of a bundle is missing (every phase
  inverted), the proof is vacuous and the mirror goes unverified.
- I found no powermetrics 0.6.2/AXI bundle fixture in the tree (the AXI fixture is mock
  telemetry, so the anchor never runs). The 0.6.2 runtime comparison against `_reduce_v060`
  itself is therefore NOT done by this seat. Frozen 0.5.1/0.6.1 (and 0.5.0/0.6.0) re-derivations
  are returned untouched (`r2_frozen_probe.log`).
- Fix:
  - Add a 0.6.2 test: the K3 fake-reader differential at minimum, or a powermetrics AXI fixture
    instrumented as in `r2_mirror_probe.py`.
  - In `_clamp_inverted_operative_envelopes`, require at least one recorded member pointer to be
    reproduced before clamping (else `return summary`).

### F4 (Low, test strength). Seat tests miss four non-equivalent mutants

My checks kill M02, M06, M12 and M14, but the seat's test file does not (table below).

| Mutant | Why the seat's test misses it |
|---|---|
| M02 (negative-power guard dropped) | The seat's guard case is an all-negative trace. Reduce floors `lower_j` at 0, so the final `lower ≤ point` check refuses it anyway. |
| M06 (restamp ignores `eligible` and sets `eligible = not reasons`) | No test hands `_restamp_clamped_gate` an eligible gate. |
| M12 (tail-refusal early return removed) | No test covers `post_window_trace_tail_shorter_than_anchor_bound`. |
| M14 (unknown recorded member pointer guard removed) | No test covers it. |

Fix: port the K1/K2/K4 cases into `tests/test_whole_window_inverted_corner_clamp.py`: a
mixed-sign trace with one −1 W sample, restamp of an eligible gate, a stubbed tail-refusal
context, and an unknown recorded `/phase_energy_j/*` pointer.

### F5 (Low, R1 observation). Clamp and oracle also define an envelope for a window already inverted at zero shift

`guard/already-inverted-input*` in `r1_oracle_sweep.log`: input `Window(5.1, 5.0)`. origin/main
returns `None`; the clamp and e1b3a0510 both return a defined envelope, bit-identical. This is
outside the ruling, which covers corner inversion only. It is unreachable if the readers reject
inverted input windows, which I did not exhaustively verify. Fix: before clamping, return `None`
when any unshifted input window has `end_s < start_s`. Equality with the oracle on the ruled
cases is unchanged.

### F6 (Info). Every dominated member is affected, not only the rare short-prefill case

The R2 probe shows tokenize and generation_setup inverting at every resolved operative bound
≥ 0.0214 s on the fixture. Their gates move from `anchor_energy_envelope_unrecorded` to the
clamped reason, both metric-local, so per-path refusal reasons change for routine members. This
is harmless under F2's fix and consistent with the seat's O1. Noted so the lead expects it.

## Required checks

**R1 Oracle: PASS** (`r1_oracle_sweep.py/.log`). 9,118 cases, 0 mismatches, compared as
IEEE-754 bit patterns and in key order. Exceptions are compared as well.

- Coverage: epochs 0, 1.7617e9 and 1793232000.123456; interval and point traces; dt 0.01, 0.0731
  and 0.1; edges 0.03 to 0.079 s with span 0 and 0.0012.
- Window lengths: 0, ¼, ½, 0.999, 1−1e-9 and 1−1e-12 of 2·edge; exactly 2·edge; one ulp
  below/above 2·edge; ×(1+1e-12), ×(1+1e-9), ×1.001, ×3; and 7 s. Each is tried at three phase
  offsets.
- Shapes: single window; multi-window (short plus long); two-source; epoch-scale absolute windows.
- Zero-power and step traces put `point_j` at the lower or both bounds; zero bounds give
  lower = point = upper.
- 18 guard cases: None/NaN/inf/negative bundle, fiducial and span; empty contributions, curve or
  windows; a negative-power sample; no-overlap after, before and far. All return `None` except
  F5's already-inverted inputs.
- 4,186 cases where origin/main returns `None` get a clamped, defined envelope, all equal to the
  oracle.

**R2 Window-set mirror: PASS for 0.5.2; 0.6.2 by reading and fake-reader differential only (F3).**

- `r2_mirror_probe.py/.log`: the real `_build_v052_bundle` fixture (phases decode,
  generation_setup, prefill, tokenize; suite item `0:mock_item_001`; block `block_a`; level
  `block_a/level_1`) at 12 bounds. I recorded the contributions that reduce's own `_reduce`
  passes to `_corner_composed_anchor_shift_envelope`, by wrapping that global in the probe
  process only.
- At all 8 bounds where the anchor resolves, `_group_envelope_contributions` equals the mint's
  member calls element-wise. That includes the pointer order and the
  (bundle, fiducial or 0.0, span) bounds triple, and there is no unknown recorded pointer.
- The 4 rows marked `ok False` are anchor-unresolved bounds below the minted bound: 0 mint calls
  and 0 clamp additions. I annotated them in the log.
- What the clamp adds: tokenize and generation_setup from 0.0214 s; prefill from 0.0684 s; decode
  at 0.1208 s.
- No pointer was found whose window set differs from reduce's mint.

**R3 Scope: PASS except F1** (`r3_scope_probe.log`). reduce.py sha256 is `7b9c0d28…` at both
`7ebb7db2a` and `3e4d359c2`. `git diff` over reduce, controller, calibration_bracketing,
harvest, run_campaign, the other ESTIMATOR_CODE_PATHS, `configs/` and `tests/b5_analysis` is
empty. Since reduce.py is unchanged, minted summaries are byte-identical; the seat's
`test_collection_mint_is_origin_main_bytes` passes in my run. There is no runtime patch or
module state. F1 is the exception: run_campaign's whole-window-verdict reaches the clamp.

**R4 Gate re-stamp: PASS with F2** (`r4_restamp_probe.log`, mutants M05, M06 and M11).

- Only pointers the clamp supplied are restamped. Restamping all member gates (M05) makes the
  restamp hit a gate without the unrecorded reason, so the clamp fails closed and the oracle
  equality fails.
- Gates lacking `anchor_energy_envelope_unrecorded`, or already eligible, are refused (`False`),
  and the whole summary is returned unclamped.
- Other reasons, such as `negative_power_sample`, are kept, and inner `windows` are handled.
- A genuinely missing prefill or gross pointer still refuses exactly
  `('anchor_energy_envelope_unrecorded',)`; the seat test passed in my run.
- `anchor_energy_envelope_exceeds_quarter_metric` on a single-window clamped phase stays a
  metric-local refusal and the gate stays `eligible: false`, so eligibility does not loosen.
- The multi-window case is F2.

**R5 Tests:** see the "R5 tails" section below. TMPDIR=`/tmp/lnine-opus-rev/tmp` (outside the
checkout, no float-like token). Env: `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1`, Python
3.13. Full history comes from `git fetch --unshallow`. The run covers the whole `tests/b5_analysis`
directory (`unittest discover -s tests/b5_analysis -t .`) plus 80 modules: every
`tests/**/test_*.py` that mentions `whole_window`, `joulewise.reduce` or `reduce_bundle`
(includes `test_whole_window*.py`), plus `tests.test_scored_reduce`. Each module runs as its own
process. Module list: `r5_modules.txt`.

## Mutation testing (17 mutants; `mutants.py`, `mutation_runner.py`, `reviewer_checks.py`, `mutation_results.jsonl`)

Each mutant is applied in-process to `joulewise/whole_window.py` source and installed as
`sys.modules["joulewise.whole_window"]`; the file on disk is never changed. Each run executes the
seat's 17 tests plus reviewer checks:

- K1: oracle mini-sweep.
- K2: restamp invariants.
- K3: 0.6.2 fake-reader differential.
- K4: real-fixture oracle equality, mirror equal to the mint calls, unknown-pointer and
  tail-refusal guards.

BASELINE (unmutated): 17/17 seat tests pass and all K checks pass.

| Mutant | Seat tests | Reviewer | Result |
|---|---|---|---|
| M01 clamp to shifted start instead of midpoint | survive | survive | **equivalent**, see below |
| M02 drop negative-power guard | survive | K1 (112 mismatches) | killed (F4) |
| M03 wrong edge sign on eps_off | survive | survive | **equivalent**: eps_off ranges over {−e,+e}, so negation only reorders the same four corners and min/max is order-free |
| M04 mirror drops suite items | killed | K4 | killed |
| M05 restamp every member gate | killed | K4 | killed |
| M06 restamp ignores `eligible`, sets `eligible = not reasons` | survive | K2 | killed (F4) |
| M07 skip exact-reconstruction proof | killed | (K4 untampered) | killed |
| M08 clamp `<=` instead of `<` | survive | survive | **equivalent**: a zero-length window's midpoint is itself, `(s+s)/2 == s` exactly for finite s |
| M09 0.6.2 anchor-shift sign | survive | K3 | killed (F3) |
| M10 corner `None` → `continue` | killed | K1 | killed |
| M11 restamp keeps `unrecorded` | killed | K2, K4 | killed |
| M12 drop tail-refusal early return | survive | K4 | killed (F4) |
| M13 session calls the unclamped re-derivation | killed | (not targeted) | killed |
| M14 drop unknown-recorded-pointer guard | survive | K4 | killed (F4) |
| M15 mirror drops levels | killed | K4 | killed |
| M16 edge = fiducial − span | killed | K1, K4 | killed |
| M17 0.5.2 mirror uses raw curve, not anchor curve | killed | K4 | killed |

14 of 17 killed; 3 equivalent. The seat's own suite alone kills 9.

Why M01 is equivalent:

1. A zero-length window contributes 0 J at every shift.
2. Both the midpoint and the shifted start lie in [s−e, end+e]. The (−e,−e) and (+e,+e) corners
   must already pass `_anchor_coverage_ok`, so coverage cannot differ.
3. The extra breakpoint only adds an evaluation point on the same piecewise function.
4. A random search found no distinguishing input in 4,000 trials (`m01_equivalence_search.log`).

## Seat-claim check (L9-ENV-3.md)

- Confirmed: reduce.py is byte-identical, the oracle provenance holds (e1b sha `d37f731c…`), and
  operative summaries equal the e1b3a0510 re-derivation. K4 checks that independently at 3 bounds.
- Refuted: NEEDS_RULING R2's "only possible for all-zero-power" (F2), and "nothing is persisted /
  only the consumption session" (F1).
- The seat's R5 failures: with full history, `test_d117_floor_qwen25_1p5b_plan`,
  `test_harvest_b5_sources`, `test_harvest_b5_trigger_scope`, `test_repin` and the
  `b5_analysis` git-object errors (see tails) no longer reproduce. They came from the seat's
  shallow clone, not from the change.

## R5 tails (exact; `module | Ran line | last line`)

All 81 runs finished: the whole `tests/b5_analysis` directory plus 80 modules. 76 are OK,
including `b5_analysis | Ran 1008 tests | OK (skipped=13)`, all `test_whole_window*` modules and
`tests.test_reduce`. 5 FAILED, and each fails identically at base `7ebb7db2a` (origin/main worktree
run below) for environmental reasons:

- `test_b5_chain` (21 errors) and `test_neg8_survivors` (4 errors): `/bin/zsh` is not installed.
- `test_b5_chain_prune2` (10 errors and 1 failure): also `/bin/zsh`; the failure is the
  process-survivor check inside the sandbox.
- `test_v5_block4_x12b` (1 error) and `test_v5_s1_desk_closeout` (2 errors):
  `ValueError: backup command failed`.

None of these is caused by the lane.

```
b5_analysis | Ran 1008 tests in 3619.173s | OK (skipped=13)
tests.hazards.test_refusal_allowlist | Ran 23 tests in 25.288s | OK (skipped=1)
tests.test_analysis_claims | Ran 65 tests in 3.884s | OK
tests.test_analysis_finalizer | Ran 18 tests in 53.247s | OK
tests.test_analysis_integration | Ran 116 tests in 168.058s | OK
tests.test_analysis_manifest_v3 | Ran 19 tests in 0.956s | OK
tests.test_arm_readiness_dry_run | Ran 12 tests in 77.727s | OK
tests.test_arm_readiness_evidence_author | Ran 24 tests in 123.220s | OK
tests.test_arm_readiness_evidence_t0 | Ran 81 tests in 312.575s | OK (skipped=6)
tests.test_audit_bundle_validation | Ran 22 tests in 2.778s | OK
tests.test_audit_reduce_degenerate | Ran 4 tests in 0.528s | OK
tests.test_authentication_io | Ran 22 tests in 2.077s | OK
tests.test_axi_burst_reduce | Ran 15 tests in 1.277s | OK
tests.test_axi_request_validation | Ran 12 tests in 0.220s | OK
tests.test_b5_chain | Ran 25 tests in 2.838s | FAILED (errors=21)
tests.test_b5_chain_prune2 | Ran 44 tests in 19.780s | FAILED (failures=1, errors=10)
tests.test_battery_float_sweep | Ran 5 tests in 3.975s | OK
tests.test_bracket_binding_cli | Ran 19 tests in 42.585s | OK
tests.test_calibration_cadence_report | Ran 9 tests in 3.196s | OK
tests.test_calibration_ledger_custody | Ran 62 tests in 86.347s | OK
tests.test_check_window_provenance | Ran 44 tests in 77.698s | OK
tests.test_cli | Ran 11 tests in 0.986s | OK
tests.test_cli_run | Ran 98 tests in 29.242s | OK
tests.test_controller | Ran 74 tests in 51.320s | OK
tests.test_controller_hazard_flags | Ran 58 tests in 365.422s | OK
tests.test_custody_mode_inventory | Ran 7 tests in 130.596s | OK
tests.test_d078_reason_registry | Ran 14 tests in 0.110s | OK
tests.test_d117_floor_qwen25_1p5b_plan | Ran 22 tests in 25.944s | OK
tests.test_d117_floor_qwen25_7b_plan | Ran 20 tests in 42.061s | OK
tests.test_d117_gamma_d139a2_families | Ran 14 tests in 3.216s | OK
tests.test_d165_dominance_closeout | Ran 59 tests in 26.154s | OK
tests.test_detection_floor | Ran 131 tests in 7.340s | OK
tests.test_determinism_gate | Ran 40 tests in 26.752s | OK (skipped=1)
tests.test_envelope_gate | Ran 27 tests in 16.069s | OK
tests.test_finalize_analysis_manifest | Ran 13 tests in 106.684s | OK
tests.test_floor_extraction | Ran 145 tests in 40.819s | OK (skipped=2)
tests.test_floor_mint_estimator | Ran 38 tests in 53.164s | OK
tests.test_harvest_b5_p2harv | Ran 48 tests in 183.136s | OK (skipped=4)
tests.test_harvest_b5_p3harv | Ran 48 tests in 110.344s | OK
tests.test_harvest_b5_rehearsal_compare | Ran 1 test in 0.000s | OK (skipped=1)
tests.test_harvest_b5_sources | Ran 55 tests in 6.281s | OK
tests.test_harvest_b5_trigger_scope | Ran 28 tests in 325.042s | OK
tests.test_harvest_b5_window | Ran 208 tests in 829.536s | OK (skipped=26)
tests.test_harvest_v5_g2b_window | Ran 28 tests in 26.803s | OK
tests.test_hazard_neg8_mint_verdicts | Ran 14 tests in 12.494s | OK
tests.test_hazard_whole_window_verdict | Ran 20 tests in 57.447s | OK
tests.test_launch_window | Ran 39 tests in 616.672s | OK
tests.test_mint_analysis_admission | Ran 8 tests in 11.644s | OK
tests.test_mint_floor_artifact | Ran 42 tests in 17.993s | OK
tests.test_mint_floor_artifact_generalized | Ran 84 tests in 212.654s | OK (skipped=2)
tests.test_neg8_corpus_cap | Ran 19 tests in 136.412s | OK
tests.test_neg8_survivors | Ran 89 tests in 192.404s | FAILED (errors=4)
tests.test_p2038_production_path | Ran 8 tests in 390.761s | OK
tests.test_p2_ctl_calibration | Ran 17 tests in 76.472s | OK (skipped=1)
tests.test_p2_ctl_cli | Ran 8 tests in 1.735s | OK
tests.test_paper_comparison_placements | Ran 21 tests in 18.158s | OK
tests.test_paper_custody | Ran 33 tests in 54.608s | OK
tests.test_paper_rendering | Ran 6 tests in 2.909s | OK
tests.test_paper_reported_energy | Ran 30 tests in 4.443s | OK
tests.test_reason_code_partition | Ran 3 tests in 13.276s | OK
tests.test_reduce | Ran 132 tests in 416.428s | OK
tests.test_repin | Ran 47 tests in 17.031s | OK
tests.test_run_campaign | Ran 267 tests in 211.838s | OK (skipped=1)
tests.test_run_campaign_hazard_flags | Ran 46 tests in 12.968s | OK (skipped=3)
tests.test_run_d165_closeout_from_custody | Ran 35 tests in 231.699s | OK
tests.test_scored_reduce | Ran 64 tests in 141.078s | OK (skipped=1)
tests.test_select_g2a_prefill_length | Ran 8 tests in 0.042s | OK
tests.test_supersession_cross_consumer | Ran 15 tests in 0.074s | OK
tests.test_uncertainty_p2029 | Ran 27 tests in 2.763s | OK
tests.test_v5_block4_x12b | Ran 11 tests in 17.324s | FAILED (errors=1)
tests.test_v5_block4_x2 | Ran 15 tests in 26.213s | OK
tests.test_v5_s1_desk_closeout | Ran 7 tests in 4.156s | FAILED (errors=2)
tests.test_v5_s1_qualification | Ran 23 tests in 12.401s | OK
tests.test_whole_window | Ran 26 tests in 0.912s | OK
tests.test_whole_window_inverted_corner_clamp | Ran 17 tests in 87.318s | OK
tests.test_whole_window_parallel_strict | Ran 8 tests in 0.655s | OK
tests.test_whole_window_selection | Ran 57 tests in 160.280s | OK
tests.test_window_duration_margins | Ran 42 tests in 17.742s | OK
tests.test_window_lineage | Ran 52 tests in 92.167s | OK (skipped=1)
tests.twins.test_harvest_twin | Ran 16 tests in 0.001s | OK
tests.twins.test_harvest_twin_comparison | Ran 7 tests in 8.023s | OK
```

Baseline, same modules at `7ebb7db2a` (`r5_baseline_7ebb7db2a.txt`):

```
BASE 7ebb7db2a tests.test_b5_chain | Ran 25 tests in 6.173s | FAILED (errors=21)
BASE 7ebb7db2a tests.test_b5_chain_prune2 | Ran 44 tests in 21.139s | FAILED (failures=1, errors=10)
BASE 7ebb7db2a tests.test_neg8_survivors | Ran 89 tests in 167.645s | FAILED (errors=4)
BASE 7ebb7db2a tests.test_v5_block4_x12b | Ran 11 tests in 13.598s | FAILED (errors=1)
BASE 7ebb7db2a tests.test_v5_s1_desk_closeout | Ran 7 tests in 3.796s | FAILED (errors=2)
```
