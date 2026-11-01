STATUS: DONE

# L9-ENV-3: analysis-only clamp of inverted corner windows (Ed's 2026-10-30 ruling)

Branch `lane/2026-10-30-l9-env-analysis-clamp` from origin/main `7ebb7db2a`. Synthetic data only;
no real block-5/6/BYTES data was opened or searched. `joulewise/reduce.py` is byte-identical to
origin/main (`7b9c0d28…`), as are the other three `ESTIMATOR_CODE_PATHS`, the calibration
acceptance, `tests/b5_analysis/test_frozen_files.py` and everything under `configs/`.

## SUMMARY

- The consumption session (`AuthenticatedConsumptionSession._prepare`, `joulewise/whole_window.py:1829`)
  now calls `_rederive_operative_summary` (`:1330`) instead of reduce's re-derivation directly. That
  wrapper runs reduce's unchanged `_rederive_summary_for_authenticated_fiducial_bound`, then
  `_clamp_inverted_operative_envelopes` (`:1197`): for every phase/item/block/level pointer the
  unchanged reducer omitted, it adds the clamped envelope from
  `_clamped_corner_composed_anchor_shift_envelope` (`:945`). It also moves that gate's
  `anchor_energy_envelope_unrecorded` to the clamped envelope's own gate reason (in practice
  `anchor_energy_envelope_exceeds_quarter_metric`; both are metric-local).
- The clamp is L9-ENV-2's: an inverted shifted corner window becomes a zero-length window at its
  shifted midpoint (0 J). Lower bound 0 J, envelope defined but wide, point estimate unchanged.
- Oracle: the whole re-derived operative summary is equal, dict and JSON bytes including key order,
  to what e1b3a0510's patched reducer re-derives on the real `_build_v052_bundle` fixture at 6
  operative bounds. At function level the clamped envelope is dict-equal to the vendored e1b3a0510
  function on L9-ENV-2's cases and on a 2,376-case sweep.
- Synthetic reproduction: at origin/main the session refuses `('anchor_energy_envelope_unrecorded',)`.
  With the clamp it is ready, and the prefill envelope covers the minted one (point equal, lower 0).
- No estimator pin moves, so the live acceptance stays current. L9-ENV-2's N1 (acceptance reissue)
  and O2 (sealed inventory drift) do not arise on this branch.

## Design (A1)

- **Where.** In `whole_window.py` itself, with no new module. `scripts/run_campaign.py` and
  `joulewise/b5/harvest.py` already import `whole_window`, so any new module that `whole_window`
  imported would be imported by collection paths, which the WRITE_SCOPE forbids. `whole_window.py`
  is pin4-exempt (`tests/b5_analysis/test_frozen_files.py:31`) and is not an estimator path.
- **Clamped function.** `_clamped_corner_composed_anchor_shift_envelope` first calls reduce's
  `_corner_composed_anchor_shift_envelope`. If reduce defines the envelope, that exact object is
  returned, so every non-inverting input matches origin/main by construction. Only when reduce
  returns `None` does it run the copied body. That body keeps every guard verbatim (None/non-finite/
  negative bounds and span, empty contributions, empty curve or windows, negative power, the
  `_anchor_shift_envelope` support/overlap `None`, the final finiteness/ordering check). The single
  changed branch is marked `# The one ruled change`. It reuses reduce's `_shift_energy_j`,
  `_anchor_shift_envelope` and `ANCHOR_SHIFT_METHOD` read-only. reduce is not monkeypatched: a test
  asserts reduce's functions are still its own code objects after a clamp session.
- **Contributions.** `_group_envelope_contributions` rebuilds each pointer's
  (curve, windows) from reader accessors and reduce's own helpers (`_derive_anchor_context` at the
  operative bound, `_union_windows`, `_shift_curve`, `_json_pointer_token`). It mirrors the
  current-wire window sets of `_reduce` (0.5.2: phases, suite items, blocks, levels) and
  `_reduce_v060` (0.6.2: per-source unioned request-phase windows).
- **Fail closed.** The reconstruction is trusted only after it reproduces, with reduce's own
  function, every envelope the unchanged reducer recorded, compared exactly. On any mismatch,
  unknown recorded member pointer, read/derivation error, missing gate stamp, or gate that is
  not already ineligible, the unchanged reducer's summary is returned. That is origin/main
  behaviour: the session refuses if a minted pointer is missing.
- **Gates.** `anchor_energy_envelope_unrecorded` has one producer, the envelope gate for that
  pointer (`reduce.py:2335-2348`, stamped at `:2479/:2505`). So the restamp removes it and merges
  `_anchor_envelope_gate_reasons(clamped, joint_bound)`, which gives the reason set e1b3a0510 stamps.
  Inner `windows` gates are handled the same way (`include_inner_windows` is on for current wire).
  The `post_window_trace_tail_shorter_than_anchor_bound` resolved refusal, where reduce stamps no
  envelope reasons, adds envelopes only.

**Why the minted (collection) summaries and the precheck are untouched.** The mint is
`controller.py` → `reduce_bundle`, and reduce.py is origin/main's bytes. Nothing in reduce imports
whole_window, and nothing is patched at runtime. The new code runs only inside
`_rederive_operative_summary`, whose only caller is the consumption session. It works on an
in-memory copy (`json` round trip) and persists nothing, so `summary_metrics.json` and its
`window_evidence_precheck` stay exactly as minted. A4 shows the mint of the fixture is
JSON-byte-identical to a fresh execution of origin/main's reduce.py bytes, and that it still omits
inverting phases (`tokenize`) with `anchor_energy_envelope_unrecorded`.

## A1–A5

| Item | Evidence (branch) | Counterfactual at origin/main |
|---|---|---|
| A1 clamp | `whole_window.py:945-1083` (clamped function), `:1086` (contributions), `:1168` (gate restamp), `:1197` (summary clamp), `:1330` (wrapper), `:1829` (session call). `AnalysisClampFunctionTests.test_other_none_guards_are_unchanged`: 14 guard cases return `None` from the analysis function, the oracle and origin/main reduce. `test_clamp_fails_closed_without_exact_reconstruction`: a 1e-9 J tamper of a recorded envelope gives back the same summary object (`assertIs`). A removed gross envelope is not re-added while prefill is. An unreadable path gives back the same summary. | With the clamp disabled (`_clamp_inverted_operative_envelopes` = identity, clamped function = reduce's), the L9-ENV-3 tests fail: 893 failures and 1 error. That covers inverted cases ×3, sweep ×883, short-prefill session, bounds sweep ×6, and missing-pointer KeyError. |
| A2 oracle | `tests/oracle_l9_env_2_reduce_clamp.py` vendors e1b3a0510's function verbatim (function sha256 `31ff400a…`). `OracleProvenanceTests`: putting it into origin/main's reduce.py rebuilds exactly e1b3a0510's file (`d37f731c…`) and matches the git object when present. `test_sweep_bit_identical_to_oracle`: dict equality analysis == oracle across 2 epochs × 3 seeds × interval/point traces × 3 bound sets × 11 duration factors (0 to 10 × 2g, including 1±1e-9) × 3 window layouts × 1 or 2 contributions. More than 200 inverting defined cases and more than 300 non-inverting ones; non-inverting are also equal to origin/main reduce. L9-ENV-2 inverted cases, 4 corner fixtures and soundness grid all pass. Summary level: `test_short_prefill_under_dominating_bound`, `test_prefill_just_over_twice_edge_bound_is_unchanged` and `test_bounds_sweep_equals_oracle` (6 bounds from 1.5× minted to 1.5× just-under) give `json.dumps(new) == json.dumps(oracle)` for the whole operative summary. | Clamp disabled: the sweep and the bounds sweep fail (above). At every dominating bound in the fixture, tokenize and generation_setup invert too, so even 1.5× minted differs from the oracle. |
| A3 reproduction | `PermanentWideningCaseTests`, real `_build_v052_bundle` fixture. The minted summary is origin/main's mint, which is the block-5 shape. Prefill D = 2g − 0.004 s (just under) at the operative bound: the analysis-side summary has `/phase_energy_j/prefill` with point = minted point, lower 0 ≤ minted lower, upper ≥ minted upper, and anchor_bound widened by exactly (operative − minted). The session is ready and `operative_envelopes[prefill].lower_j == 0`. Just over: the prefill envelope equals origin/main's, and sessions are ready for both re-derivations. Genuinely missing operative pointer (prefill or gross popped from the clamped summary): the session refuses exactly `('anchor_energy_envelope_unrecorded',)`. Global precheck classification is asserted equal for origin/main and the analysis summaries before it is neutralised (same isolation as L9-ENV-2 E3). | origin/main re-derivation: prefill is absent, and the session refuses `('anchor_energy_envelope_unrecorded',)`. This is asserted in the same test. |
| A4 freeze | `FreezeProofTests`: the 4 `ESTIMATOR_CODE_PATHS` hash to origin/main's digests, `_current_estimator_code_sha256()` equals them, and the live acceptance's `prospective_rederivation.estimator_code_sha256` equals the current code. `tests/b5_analysis/test_frozen_files.py` is unchanged (sha pinned in the test) and passes in the b5_analysis run below. The collection mint `reduce_bundle` on the fixture is JSON-byte-equal to a fresh execution of origin/main's reduce.py bytes, and equal to the stored summary. Reduce's functions are still its own code objects (no runtime patch). `git diff origin/main --stat` touches only whole_window.py, tests, and this report. | Not applicable (identity). |
| A5 recompute | See below. Report only; nothing changed there. | — |

## A5: independent recompute agreement (report only)

`scripts/independent_recompute_b5.py` at `origin/lane/2026-10-27-recompute-comparator` = `4fc643363`
(the branch has moved on from L9-ENV-2's `110b3e371`). `overlap` (:213-221) uses
`length = max(0.0, min(y, end) - max(x, start))` (:217). When a corner inverts (x > y), every record
gives 0, so `shift_envelope` (:224-242) evaluates that corner at 0 J for every common shift. That
is the same value the analysis clamp gives its zero-length window. **They agree in kind.**

Measured on the synthetic fixture (scratch script that execs only `overlap`/`shift_envelope` from
that file; prefill, recompute parameters b = fiducial, span = edge span, clock = bundle bound):

| bound | inverts | point Δ | lower (recompute / L9-analysis) | upper Δ |
|---|---|---|---|---|
| just under (0.06842 s) | yes | 0 | 0.0 / 0.0 | 1.13e-6 J |
| just over (0.06442 s) | no | 0 | 0.0103233 / 0.0103228 | −2.39e-6 J |

Definitional differences that remain. All existed before the ruling, none depends on inversion,
and all are inside the recompute's agreement bars:
1. Breakpoint set. The recompute scans record boundaries within ±clock of each shifted edge. L9's
   `_anchor_shift_breakpoints` also uses the clamped midpoint, and for point traces it uses
   interpolation knots. This causes the ~1e-6 J upper/lower differences above.
2. Float association. L9 re-origins to the first trace time (G7(c)). The recompute integrates in
   absolute epoch seconds.
3. Common shift. The recompute uses `clock` (member.m). L9 uses `bundle_bound_s`. On these members
   they are the same parameter, but the definitions are separate.
4. Window shape. The recompute takes one (onset, offset) per phase. L9 sums multi-interval
   (suite) phases at a shared shift. This makes no difference for block-5 prefill and decode.
5. Gross family. The analysis side never clamps gross, batch-group, idle or token pointers
   (NEEDS_RULING R1). The recompute would give lower 0 if a measured window could invert, which
   needs a measured window < 2g and cannot happen physically.
6. `stored_envelope_mismatch` (:479) compares minted envelopes. Mints are origin/main's on both
   past and future nights, so it is unaffected (unlike L9-ENV-2, where future mints changed).

## FILES CHANGED

- `joulewise/whole_window.py`: reduce private helpers imported read-only; the analysis-side
  clamp (5 functions plus 2 constants); the session calls `_rederive_operative_summary`.
- `tests/oracle_l9_env_2_reduce_clamp.py` (new): vendored e1b3a0510 function, with commit, file
  sha and function sha recorded.
- `tests/test_whole_window_inverted_corner_clamp.py` (new): A1–A4.
- `.codex-report/L9-ENV-3.md`: this report.

Not touched: `joulewise/reduce.py`, the other ESTIMATOR_CODE_PATHS, `tests/b5_analysis/test_frozen_files.py`,
`configs/**`, sealed registration files.

## DECISIONS I MADE

1. The clamp code lives in `whole_window.py` with no new module (collection-path import reason
   above).
2. Post-processing design: reduce's unchanged re-derivation, then an exact-reconstruction-gated
   clamp. The other ways to swap the corner function inside `reduce_bundle` are a runtime patch
   (forbidden) or a shadow copy of all of reduce (maximal duplication).
3. The gate restamp does not assign `eligible`. It requires the gate to be ineligible already,
   since reduce's merge set it so, and leaves it that way. Assigning `eligible=False` would add a
   refusal site to the hazard census (`configs/gates/hazard_refusals.json`, outside the scope); the
   first run of `tests.hazards.test_refusal_allowlist` caught exactly that.
4. Oracle loading: the test puts the vendored function into origin/main's reduce.py and proves
   the result is e1b3a0510's bytes (sha `d37f731c…`) before executing it as a separate test-only
   module. `joulewise/reduce.py` is never edited or patched.
5. A3 isolation follows L9-ENV-2 E3: a synthetic-session member carries the real minted summary,
   the session's re-derivation runs on the real bundle, and the global precheck classification is
   asserted equal before it is neutralised.

## OPEN ISSUES

- O1: newly defined tokenize/generation_setup operative envelopes (lower 0) appear in the
  session's in-memory summaries and `operative_envelopes` provenance whenever the bound dominates.
  Their gates stay ineligible with `anchor_energy_envelope_exceeds_quarter_metric`. A consumer that
  treated "envelope present" as eligibility would be wrong. I found none, but did not audit every
  downstream reader of `summary_for`.
- O2: the clamp adds one anchor-context derivation and one envelope pass per dominated member.
  It runs inside the session only.
- O4: `tests/test_harvest_v5_g2b_window.py:627` forbidden-token check is flaky: it scans bytes that contain
  random-path-dependent sha256 values. This is outside the WRITE_SCOPE (not a new test) and was left as is.
- O3: RC-CMP agreement should be rerun on the analysis-side values for block-5 at release
  (expected Δ ~1e-6 J, see A5).

## NEEDS_RULING

- R1 (stricter reading taken): gross-family pointers (`/gross_energy_j`,
  `/batch_group_gross_energy_j`, idle/request/token) are never clamped on the analysis side. Clamping
  gross would cascade into idle/token translations, `E_clock_anchor_shift_bound_j` and
  `energy_uncertainty_status`, which would mean duplicating more of reduce. It needs a measured
  window shorter than 2·edge_bound. If it happens, the session refuses as at origin/main.
- R2 (stricter reading taken): if a clamped envelope itself passed the quarter-metric gate (only
  possible for an all-zero-power window with no joint bound), the gate stays ineligible. In that
  case e1b3a0510 would have left it eligible.

## VERIFICATION (exact tails)

Commit `7ae587b89`. `TMPDIR=/tmp/lnine-env-three/tmp` (outside the checkout, no float-like token).
Env `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1`, python3.13. `python3.13 -m unittest discover -s
tests/b5_analysis -t .` (whole directory), plus every `tests/**/test_*.py` that mentions `whole_window`,
`joulewise.reduce` or `reduce_bundle` (79 modules), plus `tests.test_scored_reduce`. Each runs as its own process.
`tests.b5_analysis.test_frozen_files` alone: `Ran 3 tests in 0.617s` / `OK`.

Tails (`module | Ran line | last line`):

```
b5_analysis | Ran 1008 tests in 3670.009s | FAILED (errors=5, skipped=13)
tests.hazards.test_refusal_allowlist | Ran 23 tests in 27.010s | OK (skipped=1)
tests.test_analysis_claims | Ran 65 tests in 5.221s | OK
tests.test_analysis_finalizer | Ran 18 tests in 55.558s | OK
tests.test_analysis_integration | Ran 116 tests in 172.430s | OK
tests.test_analysis_manifest_v3 | Ran 19 tests in 1.029s | OK
tests.test_arm_readiness_dry_run | Ran 12 tests in 68.155s | OK
tests.test_arm_readiness_evidence_author | Ran 24 tests in 105.102s | OK
tests.test_arm_readiness_evidence_t0 | Ran 81 tests in 277.476s | OK (skipped=6)
tests.test_audit_bundle_validation | Ran 22 tests in 3.123s | OK
tests.test_audit_reduce_degenerate | Ran 4 tests in 0.483s | OK
tests.test_authentication_io | Ran 22 tests in 2.133s | OK
tests.test_axi_burst_reduce | Ran 15 tests in 1.124s | OK
tests.test_axi_request_validation | Ran 12 tests in 0.137s | OK
tests.test_b5_chain | Ran 25 tests in 3.089s | FAILED (errors=21)
tests.test_b5_chain_prune2 | Ran 44 tests in 19.801s | FAILED (failures=1, errors=10)
tests.test_battery_float_sweep | Ran 5 tests in 5.181s | OK
tests.test_bracket_binding_cli | Ran 19 tests in 45.161s | OK
tests.test_calibration_cadence_report | Ran 9 tests in 2.277s | OK
tests.test_calibration_ledger_custody | Ran 62 tests in 86.088s | OK
tests.test_check_window_provenance | Ran 44 tests in 92.108s | OK
tests.test_cli | Ran 11 tests in 1.084s | OK
tests.test_cli_run | Ran 98 tests in 29.712s | OK
tests.test_controller | Ran 74 tests in 53.484s | OK
tests.test_controller_hazard_flags | Ran 58 tests in 296.265s | OK
tests.test_custody_mode_inventory | Ran 7 tests in 113.443s | OK
tests.test_d078_reason_registry | Ran 14 tests in 0.165s | OK
tests.test_d117_floor_qwen25_1p5b_plan | Ran 22 tests in 26.173s | FAILED (errors=2)
tests.test_d117_floor_qwen25_7b_plan | Ran 20 tests in 49.795s | OK
tests.test_d117_gamma_d139a2_families | Ran 14 tests in 2.569s | OK
tests.test_d165_dominance_closeout | Ran 59 tests in 23.909s | OK
tests.test_detection_floor | Ran 131 tests in 6.138s | OK
tests.test_determinism_gate | Ran 40 tests in 22.238s | OK (skipped=1)
tests.test_envelope_gate | Ran 27 tests in 12.818s | OK
tests.test_finalize_analysis_manifest | Ran 13 tests in 65.531s | OK
tests.test_floor_extraction | Ran 145 tests in 22.969s | OK (skipped=2)
tests.test_floor_mint_estimator | Ran 38 tests in 31.265s | OK
tests.test_harvest_b5_p2harv | Ran 48 tests in 108.013s | OK (skipped=4)
tests.test_harvest_b5_p3harv | Ran 48 tests in 56.178s | OK
tests.test_harvest_b5_rehearsal_compare | Ran 1 test in 0.000s | OK (skipped=1)
tests.test_harvest_b5_sources | Ran 55 tests in 2.385s | FAILED (errors=3)
tests.test_harvest_b5_trigger_scope | Ran 28 tests in 203.458s | FAILED (errors=1)
tests.test_harvest_b5_window | Ran 208 tests in 566.286s | OK (skipped=26)
tests.test_harvest_v5_g2b_window | Ran 28 tests in 18.195s | FAILED (failures=1)
tests.test_hazard_neg8_mint_verdicts | Ran 14 tests in 6.237s | OK
tests.test_hazard_whole_window_verdict | Ran 20 tests in 40.743s | OK
tests.test_launch_window | Ran 39 tests in 476.614s | OK
tests.test_mint_analysis_admission | Ran 8 tests in 7.566s | OK
tests.test_mint_floor_artifact | Ran 42 tests in 12.632s | OK
tests.test_mint_floor_artifact_generalized | Ran 84 tests in 142.277s | OK (skipped=2)
tests.test_neg8_corpus_cap | Ran 19 tests in 102.128s | OK
tests.test_neg8_survivors | Ran 89 tests in 182.842s | FAILED (errors=4)
tests.test_p2038_production_path | Ran 8 tests in 461.000s | OK
tests.test_p2_ctl_calibration | Ran 17 tests in 84.563s | OK (skipped=1)
tests.test_p2_ctl_cli | Ran 8 tests in 1.927s | OK
tests.test_paper_comparison_placements | Ran 21 tests in 19.475s | OK
tests.test_paper_custody | Ran 33 tests in 59.165s | OK
tests.test_paper_rendering | Ran 6 tests in 3.386s | OK
tests.test_paper_reported_energy | Ran 30 tests in 4.802s | OK
tests.test_reason_code_partition | Ran 3 tests in 15.030s | OK
tests.test_reduce | Ran 132 tests in 512.858s | OK
tests.test_repin | Ran 47 tests in 48.457s | FAILED (failures=1)
tests.test_run_campaign | Ran 267 tests in 269.770s | OK (skipped=1)
tests.test_run_campaign_hazard_flags | Ran 46 tests in 16.278s | OK (skipped=3)
tests.test_run_d165_closeout_from_custody | Ran 35 tests in 263.766s | OK
tests.test_scored_reduce | Ran 64 tests in 169.517s | OK (skipped=1)
tests.test_select_g2a_prefill_length | Ran 8 tests in 0.044s | OK
tests.test_supersession_cross_consumer | Ran 15 tests in 0.103s | OK
tests.test_uncertainty_p2029 | Ran 27 tests in 3.086s | OK
tests.test_v5_block4_x12b | Ran 11 tests in 17.160s | FAILED (errors=1)
tests.test_v5_block4_x2 | Ran 15 tests in 30.034s | OK
tests.test_v5_s1_desk_closeout | Ran 7 tests in 4.223s | FAILED (errors=2)
tests.test_v5_s1_qualification | Ran 23 tests in 14.577s | OK
tests.test_whole_window | Ran 26 tests in 1.135s | OK
tests.test_whole_window_inverted_corner_clamp | Ran 17 tests in 105.400s | OK
tests.test_whole_window_parallel_strict | Ran 8 tests in 0.991s | OK
tests.test_whole_window_selection | Ran 57 tests in 194.879s | OK
tests.test_window_duration_margins | Ran 42 tests in 19.799s | OK
tests.test_window_lineage | Ran 52 tests in 103.865s | OK (skipped=1)
tests.twins.test_harvest_twin | Ran 16 tests in 0.003s | OK
tests.twins.test_harvest_twin_comparison | Ran 7 tests in 8.709s | OK
```

Failures and their causes. None involves `whole_window`'s clamp; see BASELINE below for the origin/main comparison:
- `b5_analysis` (5 errors), `test_harvest_b5_sources` (3), `test_harvest_b5_trigger_scope` (1),
  `test_d117_floor_qwen25_1p5b_plan` (2): `git show <sha>:...` exit 128. This clone lacks historical
  objects such as `b039c0257d1b…:joulewise/whole_window.py` and `224a264c5faa…:joulewise/b5/harvest.py`.
- `test_repin` (1): `declared commit bda1c180… is not an ancestor of HEAD`, the same missing history.
- `test_b5_chain` (21), `test_b5_chain_prune2` (10 errors and 1 failure), `test_neg8_survivors` (4):
  `/bin/zsh` is not installed in this container. The prune2 failure is the process-tree survivor check
  inside the sandbox.
- `test_v5_block4_x12b` (1), `test_v5_s1_desk_closeout` (2): `ValueError: backup command failed`.
- `test_harvest_v5_g2b_window` (1): `b'314159' unexpectedly found` in a replay-locators file under TMPDIR.

BASELINE (origin/main `7ebb7db2a` worktree at `/tmp/lnine-env-three/base`, same env and TMPDIR): each failing
module was rerun at origin/main and its sorted FAIL/ERROR test list compared with the branch's.
```
b5_analysis | Ran 1008 tests in 3708.896s | FAILED (errors=5, skipped=13) | same failing set
tests.test_b5_chain | Ran 25 tests in 1.867s | FAILED (errors=21) | same failing set
tests.test_b5_chain_prune2 | Ran 44 tests in 19.224s | FAILED (failures=1, errors=10) | same failing set
tests.test_d117_floor_qwen25_1p5b_plan | Ran 22 tests in 17.014s | FAILED (errors=2) | same failing set
tests.test_harvest_b5_sources | Ran 55 tests in 1.878s | FAILED (errors=3) | same failing set
tests.test_harvest_b5_trigger_scope | Ran 28 tests in 186.488s | FAILED (errors=1) | same failing set
tests.test_neg8_survivors | Ran 89 tests in 182.677s | FAILED (errors=4) | same failing set
tests.test_repin | Ran 47 tests in 49.244s | FAILED (failures=1) | same failing set
tests.test_v5_block4_x12b | Ran 11 tests in 14.712s | FAILED (errors=1) | same failing set
tests.test_v5_s1_desk_closeout | Ran 7 tests in 3.431s | FAILED (errors=2) | same failing set
tests.test_harvest_v5_g2b_window | Ran 28 tests in 17.214s | OK
```
`test_harvest_v5_g2b_window` is flaky, not a regression. Three reruns on the branch each gave `Ran 28 tests` / `OK`.
The failing assertion looks for the token `b'314159'` anywhere in the bytes of a locator file. That file contains
sha256 values that depend on the random temp-directory name, so one run matched by chance. This is
OPEN ISSUE O4. Every other failure appears identically at origin/main.

## CORRECTIONS (L9-ENV-4, after L9-ENV-3-FABLE-REV)

- SUMMARY "equal, dict and JSON bytes including key order": at `3e4d359c2` this held only when
  reduce recorded at least one envelope. When reduce recorded no map, the key was appended last
  (reviewer F2). L9-ENV-4 now inserts it at its `SummaryMetrics` position, so the claim holds.
- NEEDS_RULING R2 scope was wrong. A clamped envelope that passes the quarter-metric gate is
  reachable with ordinary multi-interval phases (one short inverting interval plus a long one), not
  only with all-zero power. At `3e4d359c2` such a gate was left `{"eligible": false, "reasons": []}`
  (reviewer F1). L9-ENV-4 does not add such an envelope (stricter reading). See L9-ENV-4 NR1.
- "only caller ... the consumption session": correct at function level. L9-ENV-4 *Reach* lists
  every consumer of `AuthenticatedConsumptionSession`, including `run_campaign.py whole-window-verdict`
  (reviewer F3).
