STATUS: DONE

# L9-ENV-4: L9-ENV-3-FABLE-REV fixes for the analysis-side inverted-corner clamp

Seat L9-ENV-4. Branch `lane/2026-10-30-l9-env-analysis-clamp`, continued from `3e4d359c2`.
Review applied: `.codex-report/L9-ENV-3-FABLE-REV.md` on `origin/review/2026-10-30-l9-env3-fable-rev`
(`772b3537c`, ACCEPT_WITH_FIXES). Synthetic data only (`JW_B5_SYNTHETIC_ONLY=1`). No real
block-5/6/BYTES data was opened or searched. Full history fetched (`git fetch --unshallow origin`).
`joulewise/reduce.py`, every estimator path, `configs/**` and `tests/b5_analysis/test_frozen_files.py`
are untouched. `FreezeProofTests` still pins all of them to origin/main's digests.

## SUMMARY

- **F1 (medium) fixed, stricter reading.** `_clamp_inverted_operative_envelopes` now computes
  `_anchor_envelope_gate_reasons(envelope, joint_bound_j)` for each clamped pointer before it
  restamps anything. A pointer whose reasons are empty is not added: there is no envelope, and its
  gate keeps reduce's `anchor_energy_envelope_unrecorded` refusal. As a result a clamped envelope
  never makes a member eligible, and every gate the clamp leaves is ineligible with at least one
  reason. A regression test covers the reviewer's `[short, long]` phase, with a counterfactual at
  `3e4d359c2`. The oracle-equality tests now compare against an explicitly adjusted oracle that
  excludes only this case.
- **F2 (low) fixed.** When reduce recorded no envelope map, the map is now inserted at its
  `SummaryMetrics` field position (right before `window_evidence_precheck`). The analysis summary's
  JSON bytes therefore equal the oracle's. Tested, with a counterfactual at `3e4d359c2`.
- **F3 (low) done.** Every consumer that reaches the clamp is listed under *Reach* below.
- **F5 done.** The seat module now covers the 0.6.2 `_install_axi_shape` fixture, a two-source
  0.6.2 mirror, the `eligible` and inner-window fail-closed branches of `_restamp_clamped_gate`, the
  joint bound and the unknown-pointer guard. Reviewer mutants M09, M11 and M17 (and M16, M18) are now
  killed by `tests.test_whole_window_inverted_corner_clamp` alone (table below).
- Verification: the whole `tests/b5_analysis` directory plus all 63 test modules that mention
  `whole_window` (including the seat module and all 29 that import it). Exact tails are below.
  `b5_analysis` is `OK (skipped=13)`. Five modules fail, all for container-only reasons:
  `tests.test_b5_chain`, `tests.test_b5_chain_prune2` and `tests.test_neg8_survivors` (`/bin/zsh`
  missing, plus prune2's sandbox process-tree check), and `tests.test_v5_block4_x12b` and
  `tests.test_v5_s1_desk_closeout` (`backup command failed`). Each fails with the same counts, tests
  and exceptions on an origin/main `8b2cec2f4` worktree.

## Findings

| # | Fix | Evidence (branch) | Counterfactual at `3e4d359c2` |
|---|---|---|---|
| F1 | `whole_window.py:1280-1299`: `clamped_reasons` is computed from the summary's `E_interpolation_joint_edge_bound_j`, and pointers with `[]` are dropped before any write. `:1359` restamps with those same reasons. If nothing is left, the input summary object is returned. Docstrings of `_restamp_clamped_gate` and `_clamp_inverted_operative_envelopes` updated. | `PermanentWideningCaseTests.test_passing_clamped_envelope_is_not_added`. Real 0.5.2 fixture at the just-under bound. The mirror's prefill row is replaced by the reviewer's shape: flat 10 W, windows `[0.005 s, 8 s]`. The prefill gate is reduced to `[unrecorded]` (inner windows too), the shape of a long member whose other checks pass. Results: origin/main reduce gives `None`. The oracle gives `point 80.05 J`, `lower 78.63 J`, `upper 82.79 J`, gate reasons `[]`, and the analysis function equals it. The new analysis summary has **no** prefill envelope, its prefill gate equals the input (`["anchor_energy_envelope_unrecorded"]`), and `_classify_precheck_refusals` still refuses `("phase","prefill")` locally. tokenize/generation_setup still clamp with `exceeds_quarter_metric`. Control: with the joint bound set to 1e6 J, the same envelope refuses, so it is added and the gate becomes `[exceeds_quarter_metric]`. `assert_gates_self_consistent` (no `eligible: false` without a reason, outer and inner gates) now runs on every analysis summary in both fixture classes. | The same test runs `3e4d359c2`'s `whole_window.py` (`git show`, executed as a separate module) on the same input. It adds the prefill envelope and leaves the gate `{"eligible": false, "reasons": []}`, and `_classify_precheck_refusals` sees no prefill refusal. Running the new seat module against `3e4d359c2`'s `whole_window.py` gives `Ran 22 tests` / `FAILED (failures=3)`: this test plus the two F2 checks. |
| F1 oracle | `expected_from_oracle(old, oracle)` (test module) takes e1b3a0510's summary and removes each pointer the oracle added whose own gate reasons are `[]`. It restores that member's gate to reduce's, or returns reduce's summary when no addition is left. It also returns the excluded pointers. | `test_bounds_sweep_equals_oracle` (0.5.2, 7 bounds) and `AxiV062ClampTests.test_short_prefill_clamps_and_bounds_sweep_equals_oracle` (0.6.2, 5 bounds) assert `excluded == []` and `json.dumps(new) == json.dumps(expected)`. On the real fixtures every clamped member has a single window, so the analysis path equals the oracle exactly. The one case where they differ is asserted directly in the F1 test: the oracle envelope is defined and passes, and the analysis omits it. | — |
| F2 | `whole_window.py:1321-1339`: when the key is absent, it is inserted before the first present key that follows it in `dataclasses.fields(SummaryMetrics)`. Otherwise the existing key is replaced in place. The imports are local because the write scope covers these functions only. | `test_key_position_when_reduce_recorded_no_envelope_map`. 0.5.2 at 3× the critical bound, the reviewer's `0.199261` case: reduce records no map, and only `/phase_energy_j/decode` clamps. Then `list(new) == list(oracle)`, `json.dumps(new) == json.dumps(oracle)`, and the key is followed by `window_evidence_precheck`. That bound was also added to the bounds sweep. | `3e4d359c2` is dict-equal to the oracle but the key comes last, and `json.dumps` differs (asserted in the same test). Against `3e4d359c2`'s file, both `test_key_position_…` and `test_bounds_sweep_equals_oracle (bound=0.19926095008850098)` fail. |
| F3 | Report only: see *Reach*. | Lines re-checked by grep on this branch. | — |
| F5 | New tests: `AxiV062ClampTests` (real `_install_axi_shape` fixture minted with reduce 0.6.2; mirror reproduces every recorded envelope; anchor curve shifted from the raw curve; 5-bound sweep equals the adjusted oracle; prefill clamps at exactly the 3 dominating bounds, `unrecorded`→`exceeds_quarter_metric`, still ineligible); `test_mirror_groups_per_source_with_shifted_source_curves` (two sources, overlapping requests unioned, nonzero anchor shift); in `test_clamp_fails_closed_without_exact_reconstruction`: an eligible prefill gate, an inner window without the stamp, a gate without the stamp, an unknown recorded `/phase_energy_j/ghost` pointer each return the input object (`assertIs`), plus a positive control. | Mutation table below. | The fail-closed and 0.6.2 tests pass at `3e4d359c2` too, because they pin behaviour that already existed. Their value is the kills below. |

### Mutation (seat module only)

The reviewer's 18 mutants (`probes/mutants.py` on the review branch) were re-applied verbatim to this
branch's `whole_window.py`. Only M16's pattern was re-targeted at the new call site: `joint_bound_j`→`None`
in the `clamped_reasons` computation. Two new mutants cover this seat: MF1 removes the F1 filter, and
MF2 always appends the map last. Each mutant was run as `python3.13 -m unittest tests.test_whole_window_inverted_corner_clamp`
in a `/tmp` worktree at `831e174fd`, with no probes. Format: `mutant | verdict | Ran | last line`.

```
M01_clamp_to_shifted_start | SURVIVED | Ran 22 tests in 117.612s | OK
M02_clamp_to_shifted_end | SURVIVED | Ran 22 tests in 116.634s | OK
M03_clamp_condition_le | SURVIVED | Ran 22 tests in 115.732s | OK
M04_drop_negative_power_guard | SURVIVED | Ran 22 tests in 112.784s | OK
M05_edge_bound_wrong_sign | KILLED | Ran 22 tests in 82.375s | FAILED (failures=899)
M06_mirror_drops_item_family | KILLED | Ran 22 tests in 80.783s | FAILED (failures=10, errors=1)
M07_mirror_uses_raw_curve_052 | KILLED | Ran 22 tests in 84.500s | FAILED (failures=12, errors=1)
M08_restamp_every_group_gate | KILLED | Ran 22 tests in 85.161s | FAILED (failures=16, errors=1)
M09_restamp_ignores_eligible | KILLED | Ran 22 tests in 118.318s | FAILED (failures=1)
M10_drop_recorded_reconstruction_check | KILLED | Ran 22 tests in 121.217s | FAILED (failures=1)
M11_v062_anchor_shift_sign | KILLED | Ran 22 tests in 121.981s | FAILED (failures=6)
M12_clamped_pointers_appended_last | KILLED | Ran 22 tests in 106.175s | FAILED (failures=7)
M13_clamp_disabled | KILLED | Ran 22 tests in 88.546s | FAILED (failures=13, errors=2)
M14_always_recompute_body | SURVIVED | Ran 22 tests in 127.140s | OK
M15_restamp_skips_inner_windows | KILLED | Ran 22 tests in 87.839s | FAILED (failures=15)
M16_gate_reasons_without_joint_bound | KILLED | Ran 22 tests in 122.071s | FAILED (errors=1)
M17_v062_summed_curve_instead_of_source | KILLED | Ran 22 tests in 123.547s | FAILED (failures=1)
M18_skip_unknown_recorded_pointer_guard | KILLED | Ran 22 tests in 124.421s | FAILED (failures=1)
MF1_keep_passing_clamped_envelope | KILLED | Ran 22 tests in 128.025s | FAILED (failures=1)
MF2_envelope_key_appended_last | KILLED | Ran 22 tests in 129.308s | FAILED (failures=2)
```

Killing tests: M09 is killed by `test_clamp_fails_closed_without_exact_reconstruction` (eligible gate).
M11 is killed by `test_mirror_groups_per_source_with_shifted_source_curves`, `test_mirror_reproduces_every_recorded_envelope`
and the 0.6.2 sweep at the 3 dominating bounds. M17 is killed by `test_mirror_groups_per_source_with_shifted_source_curves`.
On the one-source AXI fixture, the source curve and the summed curve coincide, so only the two-source
shape separates them. M16 is killed by the joint-bound control in the F1 test (KeyError, so it counts
as an error), M18 by the ghost pointer, MF1 by the F1 test, and MF2 by both F2 checks. A first round at
`9a7d32e33`, before the two-source, joint and ghost tests, already killed M09 and M11, but M16, M17 and
M18 survived it. Those three tests were added because of that round.

The survivors (M01–M04, M14) are not part of F5, and I left them alone. I believe they are equivalent,
or can only be told apart at the ulp/support-edge level, within the seat module's input domain:
- M03: a zero-length window clamped to its own midpoint is the same window.
- M14: the body equals reduce's whenever reduce defines an envelope.
- M04: reduce's guard runs first.
- M01/M02: any zero-length window gives 0 J at the inverted corner.
I have not proven these; see O2.

## Reach (F3): every consumer of `AuthenticatedConsumptionSession`

The clamp runs only inside `_rederive_operative_summary` (`whole_window.py:1365`). That function's
only caller is `AuthenticatedConsumptionSession._prepare` (`whole_window.py:1864`), and only for a
member whose authenticated operative bound dominates its minted bound. So the clamp reaches every
artefact built through a consumption session. Constructors on this branch (`grep -n
"AuthenticatedConsumptionSession(" joulewise scripts`, excluding docs/process traces):

| Site | Path / mode | Artefact that now sees clamped operative envelopes |
|---|---|---|
| `scripts/run_campaign.py:8425` | `_run_whole_window_verdict_locked` (`:8367`), `whole-window-verdict` subcommand, `MAX_BRACKET` semantics | whole-window verdicts |
| `scripts/mint_floor_artifact.py:547` | floor-artifact mint session | floor artefacts |
| `scripts/mint_floor_artifact.py:1250` | `allowance_session` | floor allowance |
| `scripts/check_window_provenance.py:1048` | window-provenance check | provenance check reports |
| `scripts/produce_b5_disclosures.py:115` | `issuer.AuthenticatedConsumptionSession(..., mode="issuing")` | block-5 disclosures |
| `joulewise/b5_analysis/dry_run.py:1078` | `mode='read_replay'` | b5 analysis dry runs |
| `joulewise/paper_reported_energy_issuer.py:146` | `mode='issuing'` | paper-reported energy issuance |
| `joulewise/floor_extraction.py:3171` | `consumption_session` unless `kept_required` | floor extraction |
| `joulewise/analysis_engine/inputs.py:2029`, `:2125`, `:3799` | analysis-engine input loading | analysis-engine claims/inputs |
| `joulewise/window_duration_margins.py:796` | window duration margins | margin reports |
| `joulewise/floor_mint_estimator.py:480` | floor mint estimator | floor-mint estimates |
| `joulewise/analysis_manifest_v3.py:3771` | analysis manifest v3 | analysis manifests |
| `joulewise/whole_window.py:1740` | isolated per-member audit sessions for removed members, inside `_prepare` | same as the enclosing session |

None of these is a collection path. The clamp is not reached by `controller.py`, `reduce.py`,
`calibration_bracketing.py`, `joulewise/b5/harvest.py` (which imports `whole_window` for verdict
validation only), run_campaign's collection verbs, or the mint precheck. Minted
`summary_metrics.json` files are unchanged (`FreezeProofTests.test_collection_mint_is_origin_main_bytes`).
Release checklist: verdicts, floor artefacts/allowances/estimates, disclosures, paper issuance,
analysis manifests/inputs, margins and provenance reports produced after this lane may carry
clamped (lower 0 J) operative envelopes on dominated members. Each such member stays refused with
`anchor_energy_envelope_exceeds_quarter_metric` where it previously had `anchor_energy_envelope_unrecorded`.

## FILES CHANGED

- `joulewise/whole_window.py`: only `_clamp_inverted_operative_envelopes` (F1 filter and F2 key
  position) and the docstring of `_restamp_clamped_gate`. `_clamped_corner_composed_anchor_shift_envelope`,
  `_group_envelope_contributions` and `_rederive_operative_summary` are unchanged, and nothing
  outside the clamp functions was touched (`git diff 3e4d359c2 -- joulewise/whole_window.py`).
- `tests/test_whole_window_inverted_corner_clamp.py`: helpers `seat_base_whole_window`,
  `_gate_for`, `assert_gates_self_consistent`, `expected_from_oracle`; tests for F1, F2 and F5 as
  above; `AxiV062ClampTests`.
- `.codex-report/L9-ENV-4.md`: this report.
- `.codex-report/L9-ENV-3.md`: a CORRECTIONS section appended (claims superseded by F1/F2/F3).
- `tests/oracle_l9_env_2_reduce_clamp.py`: unchanged (the oracle stays e1b3a0510's bytes).

## DECISIONS I MADE

1. **Stricter reading kept (F1).** A clamped envelope never makes a member eligible. If its own
   gate reasons are empty, the envelope is not added and the member keeps reduce's
   `anchor_energy_envelope_unrecorded`. I did not take the alternative of setting `eligible: true`,
   which would loosen the gate, and I did not return the whole summary unchanged, which would
   needlessly drop other members' clamps. The rule applies uniformly, including the
   `post_window_trace_tail_shorter_than_anchor_bound` resolved-refusal path, where reduce stamps
   no envelope reasons.
2. **Documented oracle difference.** The e1b3a0510 oracle differs from the analysis path in exactly
   one case: a pointer the unchanged reducer omitted whose clamped envelope has empty gate reasons.
   The oracle records it and leaves the gate eligible; the analysis path omits it and keeps the
   `unrecorded` refusal. The oracle-equality tests exclude only that case, through
   `expected_from_oracle`, and assert `excluded == []` on both real fixtures. The F1 test asserts
   the difference explicitly.
3. F2 takes the exact fix (schema position) rather than qualifying the claim, so the analysis
   summary is JSON-byte-equal to the oracle wherever they are dict-equal.
4. The F2 imports (`dataclasses.fields`, `SummaryMetrics`) are function-local, so the change stays
   inside the clamp functions named in the write scope. `whole_window` already imports
   `joulewise.schemas`, so no new module enters any import graph.
5. Counterfactuals execute `3e4d359c2`'s `whole_window.py` from `git show` as a separate module. If
   that commit is absent from the clone, the test skips only the counterfactual part, after the
   branch assertions have run.

## OPEN ISSUES

- O1 (from L9-ENV-3 O1, narrowed): newly defined lower-0 operative envelopes still appear in
  `operative_envelopes` provenance for dominated members. Each such member's gate is ineligible with
  a reason. A consumer that read "envelope present" as eligibility would be wrong. The reach table
  above lists every consumer for the release check.
- O2: mutants M01–M04 and M14 survive the seat module (argued equivalent above, not proven). The
  reviewer's R1 oracle sweep is the stronger check for the function body. I did not import it into
  the seat module because it was not in scope for F5.
- O3: the reviewer's F4 (a second anchor derivation per dominated member) is unchanged and
  informational.

## NEEDS_RULING

- NR1 (stricter reading implemented): this confirms L9-ENV-3's R2 and corrects its scope. A clamped
  envelope that passes the quarter-metric gate is not an all-zero-power corner case. It is reachable
  with ordinary multi-interval phases (0.5.2 suite phases, 0.6.2 per-source unions) where one short
  interval inverts. Ed should rule whether such a member may ever become eligible from a clamped
  envelope. Today it may not, and the analysis path differs from e1b3a0510 in exactly this case.
- NR2 (unchanged from L9-ENV-3 R1): gross-family pointers are never clamped.

## VERIFICATION (exact tails)

Code commit `831e174fd`. That is the pre-rebase SHA; its code and tests are identical to pushed `c38ebf032`. The rebase onto the lane's report-only `a4340681d` changed no file under `joulewise/` or `tests/`, and the same holds for `9a7d32e33` = `fe35b3ca5`. The report commit that follows changes no code or test either. Python 3.13.17,
Linux container, 4 cores. `TMPDIR=/tmp/lnine-env4/tmp` is outside the checkout and contains no
float-like token. `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1`. The runs were
`python3.13 -m unittest discover -s tests/b5_analysis -t .` (whole directory) and every
`tests/**/test_*.py` outside `tests/b5_analysis` that mentions `whole_window` (63 modules). That set
includes `tests.test_whole_window_inverted_corner_clamp` and all 29 modules that import
`whole_window`. Each ran as its own process, 3 at a time. Format: `module | Ran line | last line`.

```
b5_analysis | Ran 1008 tests in 3731.786s | OK (skipped=13)
tests.hazards.test_refusal_allowlist | Ran 23 tests in 31.530s | OK (skipped=1)
tests.test_analysis_claims | Ran 65 tests in 5.377s | OK
tests.test_analysis_finalizer | Ran 18 tests in 60.275s | OK
tests.test_analysis_integration | Ran 116 tests in 181.439s | OK
tests.test_analysis_manifest_v3 | Ran 19 tests in 1.050s | OK
tests.test_arm_readiness_dry_run | Ran 12 tests in 69.045s | OK
tests.test_arm_readiness_evidence_author | Ran 24 tests in 100.052s | OK
tests.test_arm_readiness_evidence_t0 | Ran 81 tests in 245.076s | OK (skipped=6)
tests.test_authentication_io | Ran 22 tests in 2.347s | OK
tests.test_b5_chain | Ran 25 tests in 3.603s | FAILED (errors=21)
tests.test_b5_chain_prune2 | Ran 44 tests in 19.963s | FAILED (failures=1, errors=10)
tests.test_battery_float_sweep | Ran 5 tests in 5.171s | OK
tests.test_bracket_binding_cli | Ran 19 tests in 47.637s | OK
tests.test_calibration_ledger_custody | Ran 62 tests in 94.637s | OK
tests.test_check_window_provenance | Ran 44 tests in 92.500s | OK
tests.test_controller_hazard_flags | Ran 58 tests in 305.641s | OK
tests.test_custody_mode_inventory | Ran 7 tests in 129.263s | OK
tests.test_d078_reason_registry | Ran 14 tests in 0.176s | OK
tests.test_d117_floor_qwen25_1p5b_plan | Ran 22 tests in 22.276s | OK
tests.test_d117_floor_qwen25_7b_plan | Ran 20 tests in 25.364s | OK
tests.test_d117_gamma_d139a2_families | Ran 14 tests in 3.279s | OK
tests.test_d165_dominance_closeout | Ran 59 tests in 23.420s | OK
tests.test_detection_floor | Ran 131 tests in 6.055s | OK
tests.test_finalize_analysis_manifest | Ran 13 tests in 72.555s | OK
tests.test_floor_extraction | Ran 145 tests in 24.297s | OK (skipped=2)
tests.test_floor_mint_estimator | Ran 38 tests in 32.611s | OK
tests.test_harvest_b5_p2harv | Ran 48 tests in 108.917s | OK (skipped=4)
tests.test_harvest_b5_p3harv | Ran 48 tests in 61.646s | OK
tests.test_harvest_b5_rehearsal_compare | Ran 1 test in 0.000s | OK (skipped=1)
tests.test_harvest_b5_sources | Ran 55 tests in 3.285s | OK
tests.test_harvest_b5_trigger_scope | Ran 28 tests in 200.252s | OK
tests.test_harvest_b5_window | Ran 208 tests in 584.500s | OK (skipped=26)
tests.test_harvest_v5_g2b_window | Ran 28 tests in 17.271s | OK
tests.test_hazard_neg8_mint_verdicts | Ran 14 tests in 6.939s | OK
tests.test_hazard_whole_window_verdict | Ran 20 tests in 38.383s | OK
tests.test_launch_window | Ran 39 tests in 477.294s | OK
tests.test_mint_analysis_admission | Ran 8 tests in 6.339s | OK
tests.test_mint_floor_artifact | Ran 42 tests in 12.856s | OK
tests.test_mint_floor_artifact_generalized | Ran 84 tests in 149.789s | OK (skipped=2)
tests.test_neg8_corpus_cap | Ran 19 tests in 121.870s | OK
tests.test_neg8_survivors | Ran 89 tests in 205.705s | FAILED (errors=4)
tests.test_paper_comparison_placements | Ran 21 tests in 20.701s | OK
tests.test_paper_custody | Ran 33 tests in 62.885s | OK
tests.test_paper_rendering | Ran 6 tests in 3.697s | OK
tests.test_paper_reported_energy | Ran 30 tests in 5.266s | OK
tests.test_reason_code_partition | Ran 3 tests in 16.500s | OK
tests.test_repin | Ran 47 tests in 17.996s | OK
tests.test_run_campaign | Ran 267 tests in 316.443s | OK (skipped=1)
tests.test_run_campaign_hazard_flags | Ran 46 tests in 22.531s | OK (skipped=3)
tests.test_run_d165_closeout_from_custody | Ran 35 tests in 266.238s | OK
tests.test_supersession_cross_consumer | Ran 15 tests in 0.101s | OK
tests.test_v5_block4_x12b | Ran 11 tests in 13.880s | FAILED (errors=1)
tests.test_v5_block4_x2 | Ran 15 tests in 27.522s | OK
tests.test_v5_s1_desk_closeout | Ran 7 tests in 3.737s | FAILED (errors=2)
tests.test_v5_s1_qualification | Ran 23 tests in 12.348s | OK
tests.test_whole_window | Ran 26 tests in 1.171s | OK
tests.test_whole_window_inverted_corner_clamp | Ran 22 tests in 116.613s | OK
tests.test_whole_window_parallel_strict | Ran 8 tests in 1.417s | OK
tests.test_whole_window_selection | Ran 57 tests in 194.450s | OK
tests.test_window_duration_margins | Ran 42 tests in 24.365s | OK
tests.test_window_lineage | Ran 52 tests in 104.722s | OK (skipped=1)
tests.twins.test_harvest_twin | Ran 16 tests in 0.002s | OK
tests.twins.test_harvest_twin_comparison | Ran 7 tests in 8.130s | OK
```

Failing modules (5), with causes taken from the logs:
- `tests.test_b5_chain`: 21 errors, all `FileNotFoundError: [Errno 2] No such file or directory: '/bin/zsh'`.
- `tests.test_b5_chain_prune2`: 10 errors (`/bin/zsh` as above) and 1 failure,
  `AssertionError: 'survivors none' not found in 'b5 chain budget: wall budget 1 s expired; SIGTERM to 2 process(es)\nb5 chain budget: stopped; survivors …'`
  (the sandbox process-tree check).
- `tests.test_neg8_survivors`: 4 errors, all from the missing `/bin/zsh`.
- `tests.test_v5_block4_x12b` (1) and `tests.test_v5_s1_desk_closeout` (2): `ValueError: backup command failed`
  (`scripts/v5_s1_desk_closeout.py:50`, which shells out to `backup_runs.sh`).

Baseline: an `origin/main` worktree at `8b2cec2f4`, same container, same environment:

```
tests.test_b5_chain | Ran 25 tests in 2.772s | FAILED (errors=21)
tests.test_b5_chain_prune2 | Ran 44 tests in 22.295s | FAILED (failures=1, errors=10)
tests.test_neg8_survivors | Ran 89 tests in 197.568s | FAILED (errors=4)
tests.test_v5_block4_x12b | Ran 11 tests in 13.531s | FAILED (errors=1)
tests.test_v5_s1_desk_closeout | Ran 7 tests in 3.616s | FAILED (errors=2)
```

All five fail identically on origin/main: same counts, same tests, same exception lines. The
`/bin/zsh` count across `test_b5_chain`+`test_b5_chain_prune2` is 31 on both. No other module fails.
The `git show` / `bda1c180` history errors seen in the L9-ENV-3 run do not occur with full history
(`test_repin`, `test_harvest_b5_sources`, `test_harvest_b5_trigger_scope`,
`test_d117_floor_qwen25_1p5b_plan` and `b5_analysis` are all OK). `test_harvest_v5_g2b_window` is OK
with this TMPDIR.

Counterfactual run: the seat module at this branch, with `whole_window.py` taken from `3e4d359c2`:
`Ran 22 tests in 129.074s` / `FAILED (failures=3)`. The three failures are
`test_passing_clamped_envelope_is_not_added`, `test_key_position_when_reduce_recorded_no_envelope_map`
and `test_bounds_sweep_equals_oracle (bound=0.19926095008850098)`.
