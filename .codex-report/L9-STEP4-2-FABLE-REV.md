VERDICT: ACCEPT_WITH_FIXES

# L9-STEP4-2 delta review, second family (Fable), seat L9-STEP4-2-FABLE-REV

Reviewed `origin/main..8222d0e47` (merge base `0a9ff426a`; `a92026c7f` code, `8222d0e47` report) from branch
`review/2026-10-30-l9-step4-2-fable-rev`. Synthetic data only; I did not open or search any real block-5, block-6 or
BYTES data. Evidence files: `.codex-report/l9-step4-2-fable-rev/`.

The code is faithful to the registered table and fixes attempt B's defect: a tooling or unlisted reason can no longer
print as an outcome. The fixes are to the **table**, not the code: the blind MASK regex admitted codes that the plan
itself routes to R3, so some tooling-class refusals still print as `outcome-class refusal at step 4`.

## Findings (ranked)

**F1 (fix before the dry run repeats). `kept_units_below_minimum` is MASK; plan section 2.2 makes it an R3 stop.**
Emitted at `joulewise/floor_extraction.py:2461`, `:2515`, `:2820`, `:2974` when the kept units of a target cell
are below the minimum. Plan section 2.2: "Every target cell has at least 5 kept units in each stratum ... If an analysis
program finds fewer, the program and the exclusion function disagree: the analysis stops and the step goes to R3."
The driver's own namespace already lists the same literal as tooling (`configs/analysis/b5/dry_run_refusal_classes.json`,
`tooling_refusal`). Executed: `classify_step4_exit(1, {target: ['kept_units_below_minimum']}, spec)` ->
`floor_cell_not_extractable` (`classifier_counterfactuals.txt`). The L9-STEP4-2 report notes the namespace split
(OPEN ISSUES 3) but leaves the code as outcome.

**F2 (fix). The six reducer precheck codes forwarded onto kept units are member rules the harvest already applied; the
plan routes a kept-unit fire to R3.** `window_evidence_precheck` forwards the stored precheck reasons verbatim
(`joulewise/analysis_engine/inputs.py:4068-4070`), and `_evaluate_member` adds them to the cell
(`joulewise/floor_extraction.py:2245`). The MASK codes among `REDUCER_REASON_CODES` are exactly
`insufficient_in_window_samples`, `cadence_ratio_below_threshold`, `clock_bound_exceeds_quarter_window`,
`anchor_energy_envelope_exceeds_quarter_metric`, `instrument_calibration_stale`, `calibration_acceptance_bound_stale`
(executed set intersection). The harvest's exclusion function applies the first two and the fourth
(`joulewise/b5/harvest.py:323-324`, `INSTRUMENT_REASONS`, `ENVELOPE_REASON`). Plan section 2.2: member-level codes
"must not fire on a unit the exclusion function kept ... If one fires on a kept unit, the registration's member rules
and the code disagree: the analysis stops and the step goes to R3." Today each prints as the outcome.
`instrument_calibration_stale` is also emitted for a bundle-read exception at `joulewise/reduce.py:1505`
(`except (BundleReadError, KeyError, TypeError, ValueError): return None, "instrument_calibration_stale"`): a read
failure under a "stale" literal.

**F3 (fix, direction only; unreachable at n = 10). `admissible_set_uncertainty_dominates_point_floor` is terminal only
on the corner-enumeration cap.** The real dominance condition is a labelled condition with the floor kept
(`floor_extraction.py:1374-1392`, `terminal_refusal_reasons` drops it; `extractable` stays true). The only emission
that reaches `refusal_reasons` with `floor: null` is the computational cap `len(values) > MAX_EXACT_ADMISSIBLE_CORNER_N`
(`floor_extraction.py:2524-2531` absolute, `:2982-2991` comparative; `MAX_EXACT_ADMISSIBLE_CORNER_N = 16`,
`detection_floor.py:123`). Both block-5 specs plan 10 members per absolute cell
(`configs/campaigns/d117_floor_qwen3-*_v5/extraction_spec.json`), so this is not reachable in block 5, but as
registered it reports a tooling cap as a scientific outcome.

**F4 (fix). `calibration_bracket_exceeds_minted_bound` is a whole-window rederivation check, not an estimator.**
`joulewise/whole_window.py:6208` (`_current_core_rederivation_reasons`, called at `:7585`); it reaches every cell
through the consumption session (`floor_extraction.py:2195-2196`) or `whole_window_refusals` (`:3310`). It compares
the stored bracket bound with the authenticated minted bound (`bracket_bound > authenticated + 1e-12`): a provenance
and consistency gate of the kind RUN_STATE item 129 is diagnosing. Fail-closed direction: TOOLING.

**F5 (note). `anchor_energy_envelope_exceeds_quarter_metric` has one in-memory emission the harvest could not
pre-apply** (`floor_extraction.py:2290-2298`, the envelope re-derived under the bracket bound). It is still a
precondition on timing uncertainty relative to the metric, not a registered estimator or minimum rule. I class it
TOOLING with the rest of F2, but it is the one code where a ruling could reasonably differ.

**F6 (note, no change). Refused p42 cells with tooling reasons stay the registered exit.** Plan section 3.1 conditions
the p42 exit on membership, not reasons, so the implementation follows the plan text; `test_R2_p42_cell_reasons_are_irrelevant`
pins it. Worth stating in the ruling because a tooling defect that hits only p42 cells would not stop the run.

No finding against the code paths: with the real extractor, `extractable: false` requires a non-empty terminal
reason list or `floor: null` (`floor_extraction.py:1392`), `absolute_false_effect_floor` and
`comparative_false_effect_floor` always return a `FloorEstimate` (`detection_floor.py:1099-1136`), and `as_row`
always writes both `refusal_reasons` and `floor` (`:1465-1466`), so the "no reason, no floor" outcome branch and the
"floor key absent" branch are unreachable from a real report.

## Answers

**1. Faithful to the table; no tooling or unlisted path to `floor_cell_not_extractable` or `ok`.**
`classify_step4_exit` returns the outcome only when every refused non-p42 cell has `set(reasons) <= mask` and, if
empty, `floor` present and `null` (`joulewise/b5_analysis/steps.py:98-108`). Any unlisted literal, including `''`, is
not in `mask`, so it is tooling (`test_R2_an_unclassified_reason_is_a_tooling_refusal`). `ok` is reached only for
exit 0 (`steps.py:58-59`), and the extractor exits 1 whenever any cell is refused or any member omitted
(`scripts/extract_detection_floors.py:270-287`). Malformed reason lists on any refused cell, p42 included, are
`extraction_report_malformed`. The driver passes every exit-1 class through as the code (`dry_run.py:796-800`).
Counterfactuals executed in `classifier_counterfactuals.txt`: `['summary_unreadable']` and
`['kept_units_below_minimum','summary_unreadable']` -> `extraction_cell_tooling_refusal`. Faithful to **plan 3.1/3.2**
only to the extent the table is: F1-F4 are mask codes that the plan routes to R3 or that encode integrity gates.

**2. Audit of the 42 MASK codes against their producers.** Each code was located in the 11 listed modules and
traced to whether it can enter a cell's `refusal_reasons` at step 4 (member reasons via `_evaluate_member`, precheck
forwarding, `deterministic_bounds`, environment admission, consumption session, `whole_window_refusals`).

Reachable at step 4 (11 codes); none is a registered estimator or minimum rule that the plan treats as a result:

| Code | Producer | Class | Why |
|---|---|---|---|
| `kept_units_below_minimum` | `floor_extraction.py:2461,2515,2820,2974` | **TOOLING** | plan 2.2 R3 rule (F1) |
| `insufficient_members_after_exclusion` | `floor_extraction.py:2512,2971` | TOOLING | only when `kept_unit_ids is None` (not block 5); same 2.2 rule |
| `admissible_set_uncertainty_dominates_point_floor` | `floor_extraction.py:2529,2989` (terminal only on the n>16 cap) | **TOOLING** | computational cap (F3); the real dominance is a labelled condition, not terminal |
| `insufficient_in_window_samples` | `reduce.py:981` -> precheck -> `floor_extraction.py:2245` | **TOOLING** | harvest member rule on a kept unit (F2) |
| `cadence_ratio_below_threshold` | `reduce.py:988` -> same | **TOOLING** | F2 |
| `clock_bound_exceeds_quarter_window` | `reduce.py:998` -> same | **TOOLING** | F2 |
| `anchor_energy_envelope_exceeds_quarter_metric` | `reduce.py:2358,2361`; `floor_extraction.py:2293,2297` | TOOLING (ruling, F5) | precondition on timing uncertainty |
| `instrument_calibration_stale` | `reduce.py:1505` (read exception), `:1524` (age) -> precheck | **TOOLING** | read failure and freshness gate (F2) |
| `calibration_acceptance_bound_stale` | `calibration_bracketing.py:2204…` -> precheck (`whole_window.py:702`) | TOOLING | calibration freshness gate |
| `calibration_bracket_exceeds_minted_bound` | `whole_window.py:6208` -> session -> every cell | **TOOLING** | rederivation consistency gate (F4) |
| `sensitivity_bound_below_operative` | `whole_window.py:1249` | TOOLING | fenced off the registered path (`steps.require_primary_context`); unreachable there |

Not reachable at step 4 (31 codes), so their class is moot for this classifier; listed so the ruling is complete.
Step 5/9 transport rule (`detection_floor.py:4748-4805`, `transport_refusal_reasons`, not imported by
floor_extraction): `cell_stale`, `cadence_harder_than_calibration`, `clock_anchor_harder_than_calibration`,
`drift_harder_than_calibration`, `interpolation_harder_than_calibration`, `duration_outside_calibrated_envelope`,
`power_outside_calibrated_envelope`. Reduce-time anchor derivation, not in `REDUCER_REASON_CODES`
(`uncertainty_evidence.py` `derive_powermetrics_anchor_v2/v3`, `derive_idle_drift_evidence`):
`affine_clock_residual_exceeded`, `clock_fit_span_insufficient`, `clock_rate_limit_exceeded`,
`effective_clock_anchor_bound_exceeded`, `first_parse_lag_exceeded`, `numeric_padding_insufficient`,
`wall_minus_monotonic_rate_exceeded`, `wall_minus_monotonic_span_exceeded`, `insufficient_idle_samples` (the tests'
canonical MASK pick is therefore a synthetic-only literal at step 4). Prospective whole-window row diagnostics
(`whole_window.py:628-642`, "conveys no refusal-scope classification"; `environment_admission.py` emits only
`environment_admission_missing/failed`, `cpu_admission_unenforced`): `cpu_baseline_sample_count_insufficient`,
`cpu_busy_ratio_p95_exceeded`, `processor_combined_power_w_p95_exceeded`. NEG8 stored condition words, consumed as
`conditions`, surfaced to cells as `whole_window_neg8_verdict_failed`: `neg8_bracket_abs_delta_exceeded`,
`neg8_bracket_idle_sub_abs_delta_exceeded`, `neg8_bracket_rel_delta_exceeded`, `neg8_drift_bound_stale`,
`references_insufficient` (a `survivor_screen` value, `whole_window.py:2962,5771`). Field keys or role names, never
reasons: `minted_bound_dominated` (`whole_window.py:1470`), `minimum_n`, `minimum_claim_n`, `stale_lock_absent`,
`staleness_sentinel`. Other modules' paths: `proposal_count_exceeds_configured_cap` (`bundle_read.py:1282`, AXI
decode; the extractor's reader maps every read failure to `summary_unreadable`, `floor_extraction.py:1909-1918`),
`readiness_dry_run_stale` (`arm_readiness.py:8514`, arm time).

Consequence for the ruling: after F1-F4 the reachable MASK set at step 4 is empty, which matches plan 3.1, where the
only registered step-4 result is the p42 exit and target cells are expected to extract. A fail-closed re-registration
(by rule, without reading any outcome) is: MASK = codes emitted by a registered estimator or minimum rule on measured
data *and* treated by the plan as a result; everything else TOOLING. The attempt-B probe already showed the refused
cells carried only tooling reasons, so the re-registration selects no data.

**3. The regeneration test is a real guard for the listed modules.** `make_table.py` is byte-identical to the blind
generator (sha256 `051c13b2…a549d2` both at `08ea5c958` and in the copy; executed) and `mask`, `tooling`, `modules`,
`mask_rule` equal CLASS_TABLE.json at `08ea5c958` (executed). Regenerating over this checkout reproduces the lists
(executed, `True`). Mutation probe (`regen_mutation_probe.txt`): two literals appended to a scratch copy of
`floor_extraction.py` appear in the regenerated `mask` and `tooling` respectively, so the test would fail on either.
Limits, both fail-closed at the classifier: a literal in a module outside the 11 (for example `calibration_bracketing.py`,
`cooldown.py`, `salvage_dangler.py`) or a code built at run time is not seen by the generator, and the classifier then
treats it as unlisted, which is tooling. The generator also collects field keys and role names, which is why 5 of the 42
MASK entries are not reasons at all.

**4. Full run.** `TMPDIR=/tmp/jwrev_tmp JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1 python3.13 -m unittest discover -s tests/b5_analysis -t .`
(TMPDIR outside the checkout, no float-like token). Exact tail:

```
@@TAIL@@
```

Targeted run of the new tests plus T8/T8b/T8c (`targeted_tests_tail.txt`): `Ran 28 tests in 1.545s`, `OK`.

## Fix list

1. Re-register the step-4 table by rule (blind, before the dry run repeats): move the 11 reachable codes above to
   TOOLING, or equivalently make the step-4 MASK empty, and re-pin `step4_reason_classes.json` with its new source.
   The code in `steps.py` needs no change; `test_R2_mask_only_reasons_are_the_outcome_class` and the DriverDouble's
   default reason would need a mask pick that remains registered, or an explicit "no mask code" test.
2. State the p42 ruling (F6) in RUN_STATE so the registered exit's blindness to p42 reasons is a decision, not an
   omission.
