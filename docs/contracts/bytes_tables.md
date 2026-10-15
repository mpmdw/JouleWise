# BYTES analysis tables and input contract

Authority: `docs/design/bytes_pack_design.md` at `7a3cea2e0`, R3/R5/R8.3.
Implementation: `joulewise/bytes_analysis.py`; CLI: `scripts/bytes_analyze.py`.

**Status: implemented and verified with synthetic evidence only.** The BYTES-local
`estimate_phase_energy` follows Block-5 analysis-plan §4, including its canonical
full-module mean and its reduced-unit arithmetic. Block-5's registered library
is unchanged. The acceptance calibration bound joins the existing output-free
re-reducer. Real analysis still requires frozen R4 inputs and authorized staged
release; this desk build neither collects data nor grants paper custody.

No import-fence or inventory registry needs an entry for the current module:
it imports no measurement runtime, battery verdict seam, paper custody issuer,
ledger reader, or single-count discipline consumer. The import test checks that
importing it loads neither MLX nor the controller.

## Inputs

`--export DIR` locates native `*.runs.csv` filenames recursively and resolves
session archives through the manifest. The stage-1 CSV values are deliberately
not used as substitutes for phase bounds or DC-input energy. `--records PATH`
accepts one or more harvest archives or their `withheld/member-assessments.json` locator.
The archive reader consumes these native shapes:

| Input | Fields read / purpose |
|---|---|
| `derived/roster.json` | `members[].run_id`, `units[].cell_id,stratum,unit_id`; identify model and whole repeat/quad before opening model files. `stratum` is `repeat` or `quad`. |
| `derived/b6-acceptance.json` | `counting` must be true; `session_id`, member `excluding` records. This reader is not a paper-custody authentication capability. |
| `derived/flags.jsonl`, acceptance `emitted_flags` | `code`, `scope.run_id`; window flags propagate to all selected runs. All harvest member exclusions remove whole units in primary. |
| `sources/claim-runs/<run>/config.json` | `model.name` must match the manifest model. |
| `sources/claim-runs/<run>/metadata.json` | observed output count and sampling-start epoch/monotonic clock pair. |
| `sources/claim-runs/<run>/events.jsonl` | unique complete `decode` phase and own `idle_baseline` stage; `timestamp_s` and optional `metadata.monotonic_ns`. |
| `derived/b6-acceptance.json.calibration.operative_bound_s` | Already computed by `b6.calibration.evaluate`: max(pre, post) + max(drift, bracket screen). Passed to `reduce._rederive_summary_for_authenticated_fiducial_bound`; never recomputed in BYTES. Native energies, idle and phase envelopes come from that in-memory summary, not the stored pre-capture reduction. |
| `withheld/reductions/<run>.summary_metrics.rereduced.json` | Retained harvest locator; only an explicitly marked synthetic mock timing fixture may supply a zero phase envelope. |
| `sources/night-custody/hazards/meter/stream-*.jsonl` | native KM003C header, batches, trailer. `km003c_parse.parse` calls `clock_fit`; `integrate` integrates the decode and own idle spans. Raw/monotonic start/end pairs must agree. |

The actual harvest's `member-assessments.json` contains run paths, validation,
span and re-reduction provenance; it is a locator, not a second energy format.
No new fictional harvest run-record schema is introduced. Shared session meter
streams are parsed for their clock fit; only selected model spans enter fit
quantities. Held-out model configurations, metadata, events and reductions are
not opened in `fit` mode.

The BYTES manifest producer is not present at the requested base. This consumer
interface is explicit pending integration with R4. JSON object:

| Field | Meaning |
|---|---|
| `models` | Exactly ten model objects; exactly three `role=fit`, three MoE, six tier models. |
| `models[].model` | Exact native `config.model.name`; also the output row key. |
| `models[].role` | `fit` or `heldout`. |
| `models[].moe` | Boolean; true for the three R1 MoEs only. |
| `models[].tier` | Boolean; true for the six R5 Qwen3 4-bit models only. |
| `models[].W_bytes,KV_bytes,R_bytes` | Frozen R4 stored weight reads, mean KV reads, resident storage in bytes; GB is decimal 10^9. These are not inferred from parameter count, RSS or pilot estimates. |
| `models[].cell_ids` | Nonoverlapping native decode floor-family IDs from the roster. |
| `sessions[].session_id,archive,pass_id` | Native session ID, retained archive locator, pass ordering key. |
| `sessions[].drift_allowance_j` | Object keyed by `rails`, `DC input`, `rest`: frozen full gross-family allowances. Half is the member's Block-5 drift term. |
| `sessions[].drift_reference.energy_j` | Object keyed by boundary: positive E_ref values. |
| `sessions[].drift_reference.duration_s` | Positive T_ref. |
| `sessions[].drift_reference.test7_passed` | Boolean, prospectively declared for that regime; false applies max(1,E/E_ref,T/T_ref). |
| `synthetic` | Optional boolean. True permits `--stage all`; real inputs require separate stages. |

`tests/fixtures/bytes/campaign_design.json` is **synthetic only**: pilot-scale
regressors, an invented 8B-8bit row, and twenty explicit seeds per world. It is
not a frozen R4 manifest or hardware validation.

## Estimation and the operative-bracket join

`estimate_phase_energy(repeats, quads, repeat_bounds, quad_bounds)` accepts
arbitrary signed energies and counts of at least five kept units in each
stratum. Every quad retains four members. Every member must supply all three
nonnegative named bounds. It follows `analysis_plan_block5.md` §4 in order:
canonical `fmean` over 50 members at 10/10; otherwise fixed 0.2/0.8 stratified
mean; sample-SD variance; t with min(n_r,n_b)-1 df; stratified kind averages
summed with `math.fsum`; unclamped m-h-B and m+h+B. H1 replaces only the t
critical for its 21-check Bonferroni family. Comments cite each plan step.

Each planned model/pass is a 50-run module, ten repeats and ten null quads.
Loss of any member removes its whole unit. Primary reads the harvest's member
exclusions, including thermal and every other physical exclusion. The labelled
flagged-inclusive sensitivity restores every physically excluded unit with
usable data. The existing B6 catalog's `klass=PHYSICS` determines physical
exclusions. Representation, structural or unknown exclusions remain excluded;
failed or absent members are never reconstructed. Below five
kept units a rails cell refuses; missing meter data can make DC/rest unavailable
without refusing rails. Missing DC members remove whole DC/rest units; their
runs and reasons remain recorded. Missing a pass never silently changes the
pass average or the ten-model H2 roster: the affected result is unavailable.

H1 uses E/511 and tau=T/511. The printed output-token quantity is E/512 with the
fixed label. Gross is primary; secondary subtracts each run's own boundary idle
mean power times its decode duration before aggregation. Negative secondary
values remain. Rest is each run's paired DC-input minus rails energy, before
unit aggregation. Battery assistance is flagged; no battery energy is added.

DC integration uses `km003c_parse.clock_fit` (via `parse`) and `integrate` over
the mapped decode and own idle spans. The phase-edge ruling of 2026-10-15 fixes
per-member u=(P_start+P_end)*(r_max+sample_interval). r_max is the maximum
absolute value of the fit's recorded minimum and maximum residuals (ms converted
to seconds); the interval is `Samples.step_ms/1000`. A sample contains its time
through the next sample time; an exact edge uses the sample beginning there.
For both gross and secondary, the same decode u enters the first bound kind
for DC input, replacing rails timing. Rest's first kind is rails timing + u.
Their stratified means enter B once. The largest u is printed as
`meter_attribution_floor_j`, never added again. There is no extra common-shift
clock term. No usable fit/mapping/coverage gives `meter=null`, a recorded
`bytes.meter_decode_unavailable` flag and reason, while retaining rails.

`operative_summary` reads the accepted session's existing operative bound and
uses `_rederive_summary_for_authenticated_fiducial_bound`. The reducer still
checks the member calibration, rejects narrowing, dispatches by stored reducer
identity, and writes nothing. Missing `calibration.operative_bound_s` refuses
with that exact missing field. An absent native decode envelope reports the
needed native trace, clock stamps and member calibration. A native fixture
regression proves the envelope widens and every bundle file stays unchanged.

The 1,000-run mock campaign has a real B6 `calibration.evaluate` output, but its
compact constant-power point traces lack **native powermetrics interval-support
traces, member instrument-calibration primary evidence, and an operative decode
envelope from that evidence**. The code cannot produce a native operative
phase bound for those traces. Its explicitly labelled
`bytes_synthetic_timing_fixture=true` supplies a zero timing envelope only in
synthetic mode, and every pass prints these three missing items. This fixture
is not hardware validation. Every energy nevertheless passes through the real
`reduce_bundle`, native B6 exporter, archive reader and analysis CLI.

## Ruling/code disagreements and external dependencies

* R3 says to use the library function unchanged. The existing registered
  `_project_cell` accepts only two model registrations and exactly 50 valid
  nonnegative members; it does not expose the plan's reduced-unit estimator.
  The orchestrator ruled a BYTES-local generalization, with equivalence tests.
  The Block-5 module remains byte-for-byte unchanged.
* Harvest reductions use stored capture calibration and request-span meter
  energy. BYTES now re-reduces with the harvest's session bound and integrates
  the meter over decode analysis-side, as R3 requires.
* R6's wording says thermal excludes and the rest are flags. The existing
  catalog excludes other physical failures. The continuation ruling fixes
  flagged-inclusive to restore all of them; primary follows harvest exclusions.
* Stage 1 blinding is per configuration, with no shared `bytes` group or subset
  release API. The CLI enforces fit/heldout read separation and commitment hashes;
  collection/release infrastructure remains owned elsewhere. A matching hash
  does not prove that a historical commit preceded release.
* No R4 manifest producer or independent twin is in these supplied commits or
  this write scope. Neither is claimed complete by this lane. Frozen reference
  energies, durations, drift allowances and test-7 status must be supplied.
  R3's “design section 14” has no target in the supplied ruling; BYTES uses the
  explicit max(1,E/E_ref,T/T_ref) scaling it states and invents no reference data.

## Output files and columns

All tables are JSON arrays of row objects; nested columns below are explicit
recomputation records. JSON uses null for undefined logs and absent second
passes, never NaN or Infinity. The CLI refuses to overwrite existing outputs.
No results are paper-custody capabilities.

### Predictions commitment

`--stage fit` writes `predictions.json`, `predictions.sha256`, and
`fit_pass_estimates.json`. The SHA-256 is over the exact UTF-8 JSON file bytes,
including its final newline. `--stage heldout --predictions PATH` verifies the
sidecar and exact manifest digest **before opening held-out archives**. It
reuses frozen fit points and lines, writes results elsewhere, and never rewrites
predictions. `all` is a synthetic-only sequential fit-then-heldout convenience;
it does not represent a separately committed unblinding event. A user must
commit the fit artifact before the actual held-out release; a matching hash
alone does not prove a historical commit.

| `predictions.json` field | Input / meaning |
|---|---|
| `schema` | `joulewise.bytes_predictions.v1`. |
| `manifest_sha256` | SHA-256 of canonical sorted compact JSON of the supplied frozen manifest. |
| `H1_checks,H2_intervals` | 21 and 23. |
| `fit_points` | Fit-only model-estimate rows, described below. |
| `rival_lines[]` | `selection,basis,boundary,lines`; twelve combinations. |
| `rival_lines[].lines.{bytes,resident,time}` | `line=[intercept,slope]`; `corners` contains eight such coefficient pairs, lower/upper combinations in product order over the three fit rows. No held-out duration is needed to freeze these prediction functions. |
| `tier_fit_inputs[]` | `model,boundary,basis,selection,BW,power`, restricted to fit-stage tier inputs. The six-model tier regression is necessarily completed after held-out release. |
| `note` | Dense held-out models test linearity over the format-derived bytes range; small rival splits do not identify the hypothesis. |

### Pass estimates

`fit_pass_estimates.json` and `heldout_pass_estimates.json` read selected native
runs, frozen regressors, drift policy, and the equivalent local estimator.
One row per model/pass/boundary/basis/selection:

| Columns | Meaning |
|---|---|
| `model,pass_id,session_id,boundary` | Identities; boundary exactly `rails`, `DC input`, or `rest`. |
| `basis,selection` | `gross primary` or `idle-subtracted secondary`; `primary` or `flagged-inclusive`. |
| `status` | `computed` or `unavailable`; unavailable DC/rest rows carry `reason,unavailable_runs,flags` and no energy. |
| `mean_j,lower_j,upper_j` | E and E ± (H1-adjusted h + B). |
| `h_j,B_j,kind_averages_j` | Statistical half-width, total systematic bound and its three stratified kind averages in joules. |
| `meter_phase_edge_mean_j` | Stratified mean u, already included once in B; zero for rails. |
| `variance,df,n_r,n_b` | Shared-library variance, conservative degrees of freedom, kept repeat/quad counts. |
| `duration_s,drift_scale` | Same-unit duration and boundary-specific R3 scaling factor. |
| `kept_runs,removed_runs,flags,meter_unavailable` | Unit selection and missing-meter reasons; union of kept flags, including session flags. |
| `attribution_floor_j,rails_attribution_floor_j,meter_attribution_floor_j` | Largest member first-kind bound, rails timing and meter u respectively; absent components null. Printed beside, never added again. |
| `operative` | Consumed bound and `rereduced` provenance, or explicit synthetic timing fixture with its missing evidence list. |
| `bytes,resident,role,moe,tier` | Frozen model metadata; GB per decode step, resident GB, and membership. |

### Model estimates

`model_estimates.json` reads pass estimates and frozen fit points. One row per
model/boundary/basis/selection. `predictions.fit_points` has the same row shape.

| Columns | Meaning |
|---|---|
| `model,boundary,basis,selection,bytes,resident,role,moe,tier` | As above. |
| `status` | `computed` or `unavailable` if any planned pass lacks a cell. |
| `mean_j,lower_j,upper_j,h_j,B_j,meter_phase_edge_mean_j,duration_s` | Equal-pass mean. Sampling variances add divided by pass count squared; systematic terms are averaged without independence shrinkage; df is the minimum pass df. The meter mean is diagnostic decomposition of B. |
| `attribution_floor_j,meter_attribution_floor_j` | Maxima over the passes, printed beside the combined cell. |
| `pass_values_j,pass_difference_j` | Ordered per-pass E values; pass 2 minus pass 1, or null at one pass. |
| `e,lower,upper` | Mean and interval in J per decode step, E/511. |
| `printed_j_per_output_token,output_label` | E/512; `512 output tokens, 511 generated in the decode phase`. |
| `time,power,BW` | tau=T/511 seconds per decode step; mean power E/T W; format-derived GB per step divided by tau, GB/s. |

### H1 and MoE tables

`h1.json` reads committed rival lines and model estimates. Each row has
`model,role,selection,basis,boundary,word,checks`. `word` is uniquely `bytes`,
`resident`, or `time`, otherwise `unresolved` (two/three matches) or `neither`.
Touching intervals count as meeting. Fit-row words are descriptive.

Each `checks[]` row has `hypothesis,predicted,prediction_lower,prediction_upper,
measured,measured_lower,measured_upper,consistent,log_ratio,log_status`.
Predictions are e units, corners determine the extrema, and `log_ratio` is
ln(measured/predicted). For a nonpositive argument it is null with
`log_status=undefined_nonpositive`; otherwise status is `computed`.

`moe.json` reads all three MoE H1 rows for a combination. Columns are
`selection,basis,boundary,answer,misses`. Answer is `active` when every resident
prediction interval is wholly above the measured interval, `resident` when
every bytes prediction interval is wholly below, otherwise `mixed`.
`misses[]` columns are `model,resident_above,bytes_below`.

### H2 tables

`h2.json` reads the ten model estimates and the matching rails powers. Each row
has `selection,basis,boundary,primary_intervals,two_term,resident_extended,
resident_adds_nothing,tier,tier_deviations,rest,loo_description`.

`two_term` coefficients are `[P0,epsilon]` for power versus BW.
`resident_extended` coefficients are `[P0,epsilon,rho]` for BW and R/tau.
`tier` is `[P0,epsilon]` over the six R5 tier models. `rest` is null outside
rest, otherwise `[c,epsilon_rest,lambda]` for BW and rails mean power.
`resident_adds_nothing` is true if rho's interval contains zero or rho <= 0.

Each regression record contains `n,df,coefficients,covariance,mse,critical,
family_size,intervals`: sample count, residual n-p df, coefficients in the
orders above, covariance matrix, residual mean square, exact Student-t critical,
23, and coefficient endpoint pairs. Intercept and extra extended-coefficient
intervals are diagnostic recomputation data, not additional primary tests.

`primary_intervals[]` has `term,estimate,lower,upper`. Exactly 23 named intervals
across the three boundaries for gross primary/primary selection:
three all-model epsilon, three rho, three tier epsilon, twelve tier deviations,
and rest epsilon/lambda. These use t(1-0.05/(2*23),n-p); H1 energy statistical
half-widths use t(1-0.05/(2*21),min(n_r,n_b)-1). B is unchanged. Secondary and
flagged-inclusive results repeat the adjustment as labelled sensitivity outputs.

`tier_deviations[]` columns are `model,deviation_w,lower_w,upper_w,predicted_w`.
The sign is observed minus tier prediction. Its half-width is the tier t
critical times sqrt(residual MSE + prediction-mean variance), the ordinary
out-of-tier prediction interval. `loo_description[]` has
`model,predicted_w,observed_w`, from a separate nine-model two-term fit for each
omitted point, explicitly descriptive.

`unavailable.json` records each selection/basis/boundary whose fit or ten-model
roster is incomplete; no invented H1 word or H2 fit is issued for that group.
Other complete boundaries still export normally.

### Analysis record

`analysis_record.json` columns are `stage,predictions_sha256,manifest_sha256,
H1_checks,H2_intervals,output_label,note,synthetic`. It binds all result files to
the verified prediction artifact and manifest; it makes no claim of an actual
historical release/commit or twin agreement.

## Decisions I made

* Generalize §4 locally, preserving the canonical full-module arithmetic and
  all bound names; do not edit or impersonate Block-5 registrations.
* Keep 511-step regressions and the separately labelled E/512 printed value.
* Retain the previously chosen 23 named H2 primary intervals, ordinary OLS
  residual prediction intervals for tier deviations, descriptive leave-one-out
  fits, and equal-pass means with unshrunk deterministic bounds.
* Freeze line functions and eight corner functions without reading held-out
  model data; reuse the frozen fit points after held-out release.
* Follow harvest member exclusions for primary; restore every computable
  physically excluded unit for flagged-inclusive. Missing data remain missing.
* Use the ruled decode u for both bases. At an exact meter sample edge use the
  sample starting there; read the largest absolute fit residual, including a
  negative extreme. Keep attribution maxima beside the cell, inside B only as
  their weighted means, with no additional clock envelope.
* Treat a missing meter run as an unavailable DC/rest member, removing its
  whole unit for those boundaries only. Below the minimum retain an explicit
  unavailable cell; never silently use one pass or fewer models for H2.
* Consume the B6 harvest's bound and call the existing in-memory reducer;
  disclose mock timing fixture limitations exactly, alongside each pass.
* For simulations use the existing pilot-scale regressors, invented 8-bit row,
  two passes, 50 runs per model/pass, 0.2% independent member noise and fixed
  seed lists. Pure truths are e=0.01*b, e=3*tau, e=0.01*R. DC is twice rails;
  rest is their per-run difference. These are simulation assumptions, not data.
* Report H2 two-term coverage of the fixed ten-model population projection
  slope (resident truth has omitted-variable association); separately report
  resident-extended coverage of the structural epsilon, 0.01/0/0 for the
  bytes/time/resident worlds. Bonferroni-adjusted intervals are used in both.

## NEEDS_RULING

None for the authorized analysis implementation. The continuation rulings
settle the previous meter and inclusive questions. Frozen inputs, shared
unblinding infrastructure, independent twin agreement, registration/cold gate
and live calibration checks remain external prerequisites, not new choices
about which data count or a printed number.

## Verification

Python 3.13; `JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1`, with created
`TMPDIR=/tmp/jw-bytes-tests`. No inference or hardware measurement. The native
powermetrics path uses only the repository fake process and mock runtime.

The equivalence test compares both models × all four registered prefill lengths ×
all three cell shapes × 51 inputs: **1,224 exact-equality comparisons** (1,200
random valid inputs plus the full worked example in each shape). m, V, h, B,
kind averages and both endpoints are exactly equal, without a tolerance. The
reduced-unit worked example and counts 5/5, 5/9, 9/5, 17/23, signed secondary,
mandatory bounds, missing meter, unit restoration, stage separation, file hash
commitment, separately invoked fit/heldout CLI success, and operative
widening/immutability have additional regressions.

All **28 BYTES test cases passed**, including the unskipped campaign case,
across the focused invocations below; no BYTES cases were skipped. A further
**85 dependency cases passed** (100 total in that command, including 15 BYTES
cases). The full repository suite was not run: this continuation explicitly
requires the touched modules' tests. Only the three existing authorized files
were edited; `paper_reported_energy.py` is unchanged.

Commands, all with the environment above:

* `python3.13 -m unittest tests.test_bytes_analysis.H1WorkedExamples tests.test_bytes_analysis.H2WorkedExamples tests.test_bytes_analysis.MeterWorkedExamples tests.test_bytes_analysis.RegisteredArithmeticTests tests.b6.test_calibration tests.b6.test_acceptance tests.b6.test_export_runs tests.test_custody_mode_inventory tests.test_paper_reported_energy`: 100 passed, 109.563 s.
* `python3.13 -m unittest tests.test_bytes_analysis.BoundaryAndStagingTests tests.test_bytes_analysis.ProductionArchiveTests tests.test_bytes_analysis.RegisteredArithmeticTests`: 15 passed, 69.180 s (native fixture, archive and arithmetic checks).
* `python3.13 -m unittest tests.test_bytes_analysis.CampaignWordRates`: 1 passed, 415.617 s. Sixty full campaigns, 60,000 run bundles through the reducer and exporter, including the full analysis CLI and result tables.
* Subsequent selection/archive checks cover the final catalog-class restoration guard and eight unavailable result groups; all pass.

## Simulation results

Synthetic only, 20 independent campaigns per truth world; 1,000 runs each
(ten models, fifty runs per model, two passes). Seeds are 1100–1119 for bytes,
2100–2119 for time, 3100–3119 for resident, as committed in the fixture. The
synthetic timing fixture limitations above apply. Primary gross selection is
reported here; both bases and both selections were reduced and exported.

Every table entry is rate ± Monte Carlo SE, with SE=sqrt(p*(1-p)/20), estimated
per model and boundary across campaigns, never pooled over correlated models.
An empirical rate of zero or one has plug-in SE zero; twenty campaigns do not
establish a population probability of zero or one.


| Truth | Boundary | Held-out model | bytes | resident | time | unresolved | neither |
|---|---|---|---:|---:|---:|---:|---:|
| bytes | rails | Llama-3.3-70B-Instruct-4bit | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| bytes | rails | Qwen3-14B-4bit | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| bytes | rails | Qwen3-30B-A3B-4bit | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| bytes | rails | Qwen3-32B-4bit | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| bytes | rails | Qwen3-Next-80B-A3B-Instruct-4bit | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| bytes | rails | Qwen3.5-122B-A10B-4bit | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| bytes | rails | Qwen3-8B-8bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 |
| bytes | DC input | Llama-3.3-70B-Instruct-4bit | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| bytes | DC input | Qwen3-14B-4bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 |
| bytes | DC input | Qwen3-30B-A3B-4bit | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| bytes | DC input | Qwen3-32B-4bit | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| bytes | DC input | Qwen3-Next-80B-A3B-Instruct-4bit | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| bytes | DC input | Qwen3.5-122B-A10B-4bit | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| bytes | DC input | Qwen3-8B-8bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 |
| bytes | rest | Llama-3.3-70B-Instruct-4bit | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| bytes | rest | Qwen3-14B-4bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 |
| bytes | rest | Qwen3-30B-A3B-4bit | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| bytes | rest | Qwen3-32B-4bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 |
| bytes | rest | Qwen3-Next-80B-A3B-Instruct-4bit | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| bytes | rest | Qwen3.5-122B-A10B-4bit | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| bytes | rest | Qwen3-8B-8bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 |
| time | rails | Llama-3.3-70B-Instruct-4bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| time | rails | Qwen3-14B-4bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| time | rails | Qwen3-30B-A3B-4bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| time | rails | Qwen3-32B-4bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| time | rails | Qwen3-Next-80B-A3B-Instruct-4bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| time | rails | Qwen3.5-122B-A10B-4bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| time | rails | Qwen3-8B-8bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| time | DC input | Llama-3.3-70B-Instruct-4bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 |
| time | DC input | Qwen3-14B-4bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 |
| time | DC input | Qwen3-30B-A3B-4bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| time | DC input | Qwen3-32B-4bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 |
| time | DC input | Qwen3-Next-80B-A3B-Instruct-4bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| time | DC input | Qwen3.5-122B-A10B-4bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| time | DC input | Qwen3-8B-8bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 |
| time | rest | Llama-3.3-70B-Instruct-4bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 |
| time | rest | Qwen3-14B-4bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 |
| time | rest | Qwen3-30B-A3B-4bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| time | rest | Qwen3-32B-4bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 |
| time | rest | Qwen3-Next-80B-A3B-Instruct-4bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| time | rest | Qwen3.5-122B-A10B-4bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| time | rest | Qwen3-8B-8bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 |
| resident | rails | Llama-3.3-70B-Instruct-4bit | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| resident | rails | Qwen3-14B-4bit | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| resident | rails | Qwen3-30B-A3B-4bit | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| resident | rails | Qwen3-32B-4bit | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| resident | rails | Qwen3-Next-80B-A3B-Instruct-4bit | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| resident | rails | Qwen3.5-122B-A10B-4bit | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| resident | rails | Qwen3-8B-8bit | 0.00 ± 0.000 | 0.05 ± 0.049 | 0.00 ± 0.000 | 0.95 ± 0.049 | 0.00 ± 0.000 |
| resident | DC input | Llama-3.3-70B-Instruct-4bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 |
| resident | DC input | Qwen3-14B-4bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 |
| resident | DC input | Qwen3-30B-A3B-4bit | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| resident | DC input | Qwen3-32B-4bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 |
| resident | DC input | Qwen3-Next-80B-A3B-Instruct-4bit | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| resident | DC input | Qwen3.5-122B-A10B-4bit | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| resident | DC input | Qwen3-8B-8bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 |
| resident | rest | Llama-3.3-70B-Instruct-4bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 |
| resident | rest | Qwen3-14B-4bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 |
| resident | rest | Qwen3-30B-A3B-4bit | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| resident | rest | Qwen3-32B-4bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 |
| resident | rest | Qwen3-Next-80B-A3B-Instruct-4bit | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| resident | rest | Qwen3.5-122B-A10B-4bit | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 |
| resident | rest | Qwen3-8B-8bit | 0.00 ± 0.000 | 0.00 ± 0.000 | 0.00 ± 0.000 | 1.00 ± 0.000 | 0.00 ± 0.000 |

H2 uses the Bonferroni-adjusted primary-family t intervals. The two-term target
is the fixed-roster population OLS projection slope of the noiseless powers.
In the resident world this is an association induced by omitting resident
reads; it is **not** the structural bytes coefficient. The resident-extended
target is the generative structural epsilon. All coverage estimates below are
per world/fit/boundary across 20 campaigns.

| Truth | Boundary | True two-term projection ε (J/GB) | True extended structural ε (J/GB) | Two-term coverage ± MCSE | Extended coverage ± MCSE |
|---|---|---:|---:|---:|---:|
| bytes | rails | 0.01 | 0.01 | 1.00 ± 0.000 | 1.00 ± 0.000 |
| bytes | DC input | 0.02 | 0.02 | 1.00 ± 0.000 | 1.00 ± 0.000 |
| bytes | rest | 0.01 | 0.01 | 1.00 ± 0.000 | 1.00 ± 0.000 |
| time | rails | 0 | 0 | 1.00 ± 0.000 | 1.00 ± 0.000 |
| time | DC input | 0 | 0 | 1.00 ± 0.000 | 1.00 ± 0.000 |
| time | rest | 0 | 0 | 1.00 ± 0.000 | 1.00 ± 0.000 |
| resident | rails | -0.125778025963 | 0 | 1.00 ± 0.000 | 1.00 ± 0.000 |
| resident | DC input | -0.251556051926 | 0 | 1.00 ± 0.000 | 1.00 ± 0.000 |
| resident | rest | -0.125778025963 | 0 | 1.00 ± 0.000 | 1.00 ± 0.000 |

SHA-256 of the exact JSON simulation report printed by the test: `7fc378852a7898439370e9b9a7ff6a2f3be96001161a1d3f697bebf576a7ef70`.
