# BYTES analysis tables and input contract

Authority: `docs/design/bytes_pack_design.md` at `7a3cea2e0`, R3/R5/R8.3.
Implementation: `joulewise/bytes_analysis.py`; CLI: `scripts/bytes_analyze.py`.

**Status: incomplete, fail-closed at the shared estimator.** At the requested
Block-6 base, the only registered Block-5 phase arithmetic function is
`paper_reported_energy._project_cell`. It is a private, non-issuing kernel
restricted to the two Block-5 model registrations and exactly 50 strictly valid,
nonnegative members. It does not implement the analysis plan's reduced-unit
estimator. No general `estimate_phase_energy` function exists. BYTES does not
fabricate registered model identities, clone the arithmetic, patch the library,
or publish replacement-estimator simulation rates. `_registered_estimate`
refuses explicitly until the shared interface below is available. The pending
scope request names `joulewise/paper_reported_energy.py`, which is outside the
user's WRITE list. End-to-end fit/heldout CLI success and the 60 campaign word
rates are therefore **not validated or complete**.

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
| `derived/flags.jsonl` | `code`, `scope.run_id`; window flags propagate to all selected runs. |
| `sources/claim-runs/<run>/config.json` | `model.name` must match the manifest model. |
| `sources/claim-runs/<run>/metadata.json` | observed output count and sampling-start epoch/monotonic clock pair. |
| `sources/claim-runs/<run>/events.jsonl` | unique complete `decode` phase and own `idle_baseline` stage; `timestamp_s` and optional `metadata.monotonic_ns`. |
| `withheld/reductions/<run>.summary_metrics.rereduced.json` | `status`, `phase_energy_j.decode`, `idle_baseline.power_w_mean`, decode `energy_anchor_shift_envelopes` and joint interpolation bound. |
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
| `sessions[].meter_clock_bound_ns` | Required nonnegative integer bound for a common meter/phase clock displacement; **no default or coverage interpretation inferred from fit diagnostics**. |
| `sessions[].drift_allowance_j` | Object keyed by `rails`, `DC input`, `rest`: frozen full gross-family allowances. Half is the member's Block-5 drift term. |
| `sessions[].drift_reference.energy_j` | Object keyed by boundary: positive E_ref values. |
| `sessions[].drift_reference.duration_s` | Positive T_ref. |
| `sessions[].drift_reference.test7_passed` | Boolean, prospectively declared for that regime; false applies max(1,E/E_ref,T/T_ref). |
| `synthetic` | Optional boolean. True permits `--stage all`; real inputs require separate stages. |

`tests/fixtures/bytes/campaign_design.json` is **synthetic only**: pilot-scale
regressors, an invented 8B-8bit row, and twenty explicit seeds per world. It is
not a frozen R4 manifest or hardware validation.

## Estimation and remaining integration gaps

The proposed shared call is
`estimate_phase_energy(repeats, quads, repeat_bounds, quad_bounds)` returning
`mean_j` and `interval {n_r,n_b,df,variance,B_j}`. Quads and quad bounds retain
all four members, with the three named Block-5 bound kinds. The existing
registered kernel should delegate to that same arithmetic without changing
its registered outputs; BYTES then changes only the statistical t critical
for H1 and adds the separately reported meter clock term. **This function has
not been added without write authority.**

Each model/pass is one 50-run module, ten repeats and ten complete null quads.
A removed member removes its whole unit; fewer than five kept units in either
stratum refuses. Durations and bound averages use the same 0.2/0.8 strata as
energy. H1 uses e=E/511, tau=T/511; the separately named printed output-token
value is E/512. Unclamped negative secondary values are retained.

Gross is primary. Secondary subtracts each run's own baseline power times that
run's decode duration before aggregation. DC input is Vbus*Ibus only: no battery
energy is added. Rest is the paired DC-input minus rails energy on each run.
The meter uncertainty enumerates all sample-crossing shifts within the supplied
common clock bound, including both sides of every discontinuity; it evaluates
gross and own-idle subtraction jointly. That is a deterministic shift envelope,
not a physical confidence guarantee. No samples or missing uncertainty terms
are replaced with zero. The phase joint interpolation term must explicitly be
zero, as for interval-support traces; unsupported traces refuse.

Further disagreements/gaps requiring integration before real analysis:

* Harvest re-reductions use the bundle's stored calibration. R3/Block-5 needs
  the authenticated operative max bracket, through the existing whole-window
  consumption session and in-memory re-reducer. Reading the harvest summary
  alone does not establish that wider phase bound; this route is not yet
  connected. Real reduction therefore refuses explicitly, even if the shared
  estimator is subsequently provided. The synthetic archive uses a labelled
  zero envelope, not a claim
  of live bracket validation.
* Stage 1 blinding draws per pack/configuration. It has no shared `bytes` group
  or subset unblind API. This CLI can preserve fit/heldout read separation,
  but cannot implement the missing collection/release operation. It reads
  already authorized archive material and never opens blinding keys.
* R3's reference to “design section 14” has no target in the supplied ruling.
  The provenance/values of E_ref, T_ref, test 7, and DC/rest drift allowances
  must be frozen outside this consumer; it invents none.
* The existing catalog excludes several physics failures, not just thermal
  pressure. R6 says thermal excludes and the rest are flags. The current
  adapter records harvest exclusions but applies the R6 thermal-only rule;
  missing/malformed data still refuses, rather than inventing an energy.
* The ruling does not define the derivation/coverage of a meter clock-fit
  uncertainty. Its parser only returns diagnostic residual/RTT statistics.
* An independent twin is not in the supplied commits or this WRITE list;
  twin agreement has not been tested.

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
runs, frozen regressors, drift policy, and the shared registered estimator.
One row per model/pass/boundary/basis/selection:

| Columns | Meaning |
|---|---|
| `model,pass_id,session_id,boundary` | Identities; boundary exactly `rails`, `DC input`, or `rest`. |
| `basis,selection` | `gross primary` or `idle-subtracted secondary`; `primary` or `flagged-inclusive`. |
| `mean_j,lower_j,upper_j` | E and E ± (H1-adjusted h + B + meter_clock). |
| `h_j,B_j,meter_clock_j` | Statistical, registered systematic, and separate meter clock half-widths in joules. Clock is zero for rails. |
| `variance,df,n_r,n_b` | Shared-library variance, conservative degrees of freedom, kept repeat/quad counts. |
| `duration_s,drift_scale` | Same-unit duration and boundary-specific R3 scaling factor. |
| `removed_runs,flags` | Removed whole-unit member IDs; union of kept flags, including session flags. |
| `attribution_floor_j` | Largest member decode anchor bound, printed beside and never added again. |
| `bytes,resident,role,moe,tier` | Frozen model metadata; GB per decode step, resident GB, and membership. |

### Model estimates

`model_estimates.json` reads pass estimates and frozen fit points. One row per
model/boundary/basis/selection. `predictions.fit_points` has the same row shape.

| Columns | Meaning |
|---|---|
| `model,boundary,basis,selection,bytes,resident,role,moe,tier` | As above. |
| `mean_j,lower_j,upper_j,h_j,B_j,meter_clock_j,duration_s` | Equal-pass mean. Sampling variances add divided by number of passes squared; systematic/clock terms are averaged without independence shrinkage; df is the minimum pass df. |
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

### Analysis record

`analysis_record.json` columns are `stage,predictions_sha256,manifest_sha256,
H1_checks,H2_intervals,output_label,note,synthetic`. It binds all result files to
the verified prediction artifact and manifest; it makes no claim of an actual
historical release/commit or twin agreement.

## Decisions I made

* Freeze line coefficient functions and all eight corner functions, so fit
  does not read held-out times. Heldout uses the frozen fit points rather than
  recomputing them from an expanded archive.
* Keep 511-step arithmetic and separately label the E/512 printed quantity.
* Count the explicitly named H2 intervals as 23 across boundaries; expose the
  primary rows separately from diagnostic regression matrices.
* Use ordinary OLS residual prediction intervals for tier signed deviations;
  leave-one-out values are description. Singular designs refuse.
* Average pass estimates equally; independent sampling variances add while
  deterministic bounds are averaged without shrinking them as random errors.
* Require explicit frozen reference/clock inputs; do not derive them from the
  pilot, and do not turn a diagnostic percentile into an uncertainty bound.
* Preserve negative secondary energies and use an explicit null log status.
* Keep all nonthermal flags in primary; remove entire thermal-affected units.
  The provisional flagged-inclusive calculation restores thermal-only losses,
  while a failed run status is never restored.

## NEEDS_RULING / remaining numerical policy

1. What prospectively validated rule supplies the DC-input clock bound and
   covers independent phase-edge timing, rather than only common clock shift?
   Options: register such a bound/envelope, or retain DC/rest as diagnostics.
   Recommendation: register and validate the bound before printing primary
   DC/rest intervals. This changes printed endpoints and H1 words.
2. Does “flagged-inclusive” restore thermal-excluded units, or repeat the
   thermal-valid primary with all its already-kept flags? Recommendation:
   keep thermal exclusions in both unless the registration explicitly permits
   a separate sensitivity calculation. This changes which data count. Current
   restoration behavior is provisional and cannot be a registered result.

The shared-kernel scope addition, operative-bracket join, manifest producer,
subset release infrastructure and twin are implementation/authority gaps,
not invented scientific rulings. The explicit test refuses the unavailable
kernel instead of reporting an end-to-end success.

## Verification in this build

All test commands used Python 3.13 with `JW_B5_SYNTHETIC_ONLY=1` and
`PYTHONDONTWRITEBYTECODE=1`. No model inference or measurement was run.

* Final `tests.test_bytes_analysis`: **24 cases, 23 passed, 1 skipped**
  (66.461 s). The skip is the complete 60-campaign word-rate test, not an
  optional hardware test.
* Native export and relevant battery/custody inventory fences: **37 passed**.
  No new registry entries were needed. Native Block-6 acceptance: **33 passed**.
* The 1000-run archive test uses ten models, fifty runs each, two passes,
  the real `reduce_bundle` path and actual `export_runs.export`; fit reads
  300 records and heldout reads 700. Poisoning held-out configurations and
  reductions leaves the fit records identical.
* Canonical `unittest discover -s tests` was attempted and interrupted after
  existing environment failures and slow monitor waits; there is no complete
  aggregate or green-suite claim. Two native plan-render tests independently
  reproduce `KeyError: TMPDIR`; focused checks set `TMPDIR=/tmp`. The required
  `/opt/homebrew/bin/python3.13` symlink could not be created: this account
  cannot write `/opt`, and `sudo` is absent. Other canonical failures were
  observed but were not fully diagnosed. The interrupted test's identified
  synthetic sleeping monitor was terminated.

| Synthetic truth | Registered seeds | Completed word campaigns | Correct-word rate |
|---|---|---:|---|
| bytes | 1100–1119 | 0/20 | unavailable: shared estimator missing |
| time | 2100–2119 | 0/20 | unavailable: shared estimator missing |
| resident | 3100–3119 | 0/20 | unavailable: shared estimator missing |

The bytes-world seed 1100 archive ingress was validated; that is not a word
campaign result. No percentages are inferred from the hand examples, the
upstream reducer check, or a stand-in for the missing registered library.
