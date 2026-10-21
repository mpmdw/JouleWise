# BYTES analysis tables and verification

Authority: `docs/design/bytes_pack_design.md` at `db83dbb58`, including Addenda
1–7. Addendum 7 and Addendum 5 item 4 supersede the affected round-2 choices
at `fbd4b3f4f`; the round-2 verification below is historical evidence.
Implementation: `joulewise/bytes_analysis.py`; CLI: `scripts/bytes_analyze.py`.
Synthetic evidence only. No model inference or measurement was run.
`joulewise/paper_reported_energy.py` remains unchanged.

## Inputs and release

The frozen model manifest has ten distinct `models`, each with `model`, `role`
(`fit` or `heldout`), `moe`, `tier`, `W_bytes`, `KV_bytes`, `R_bytes`, and native
`cell_ids`. There are three fit models, three MoEs and six Qwen3 4-bit tier
models. GB means decimal 10^9 bytes. Sessions have `session_id`, `archive`,
`pass_id`, a `released_key_dir` locator and prospective `test7_passed` status.
Legacy `drift_allowance_j` and `drift_reference` numbers are ignored.

`--export DIR` reads native `*.runs.csv` files. `--records PATH ...` accepts
archives or their `withheld/member-assessments.json` locators, and requires the
matching export at `<archive-parent>/export/bytes/<session_id>.runs.csv`.
The export supplies NEG-8 energies and configuration identities; released
science energies and phase bounds use the archive join below.

`--key-dir DIR` overrides the session's release-directory locator. A relative
session locator is resolved against its archive. The directory must contain
the existing `pack.json` and configuration key files named by Block 6's
`blinding._config_filename`; analysis only calls `stored_factor`, never draws
keys. Only released keys belong there. The export sidecar's private key
directory is never used as release authority. `synthetic=true` allows the
convenience `all` stage and explicitly marked mock timing evidence; it never
authorizes a meter join. Even non-claim fixtures require release files.

Stages:

- `blinded`: CSV-only rails, both bases and both selections. No archive,
  withheld reduction, key or meter reads; no DC-input or rest values. Uses
  the export's blinded `phase_decode_j`, durations, idle power and exported
  timing-bound columns. This is the input for blinded twin agreement.
- `fit`: require fit configuration keys plus `neg8_reference`; compute and
  freeze fit points, rival lines and fit-model tier inputs. Held-out bundle
  configuration, metadata, events and reduction files are never opened.
- `heldout --predictions PATH`: verify exact prediction-file hash, manifest,
  source identity and frozen inputs before joining held-out records; their
  keys must now be present. Reuse the frozen fit points.
- `all`: synthetic-only sequential fit/heldout convenience, subject to the
  same release-key checks. It makes no historical commitment claim.

The user must commit predictions before releasing held-out keys. A matching
SHA-256 cannot prove when a historical Git commit happened.

## Archive join, selection and bounds

The reader uses `derived/roster.json` for whole repeat/quad identities and
`derived/b6-acceptance.json` for counting acceptance, member exclusions and the
already evaluated `calibration.operative_bound_s`. `derived/flags.jsonl`,
acceptance-emitted flags and exclusion codes are retained as labels.
`operative_summary` passes that bound to the existing output-free
`reduce._rederive_summary_for_authenticated_fiducial_bound`; it never writes
bundles or recomputes the calibration bracket.

A missing/unreadable bundle, failed status, strict-validity failure, bad
observed output count, missing/nonfinite decode energy, absent native decode
envelope or unavailable joint interpolation bound yields an unusable member
with `meter=null`. It removes the entire repeat/quad in every selection.
Primary also removes every harvest-excluded unit. Flagged-inclusive restores
all catalog exclusions with valid energy records, including NUMBER cooldown,
idle-window and envelope flags; `klass` does not decide restoration. Explicit
bundle/status/token/strict-validity codes establish an invalid record.

A stratum below five kept units makes that model/pass/boundary cell unavailable;
it does not abort the stage or erase other models' cells. H1 still evaluates
available held-out points if the three frozen fit cells exist. Active/resident
needs the three MoEs. Missing meter data changes only DC-input/rest selection.
Addendum 7 D9 makes a surviving pass the model's primary point, labelled
`pass_status="one_pass"`, `n_passes=1`; both refusals leave no point and no
H1 word. Two computed passes use `two_pass`; no computed pass uses `no_pass`.
All pass refusals and their original reasons remain printed. H2 uses every
available point, independently of whether H1 has complete fit cells. Each fit
prints n, p and df; n-p below 2 refuses that fit only. A refused or singular
fit has `status="refused"` and a reason, with no primary interval. Whenever
any model has fewer than two computed passes, a separate H2 row labelled
`analysis="two_pass_sensitivity"`, `description_only=true` fits only the
two-pass models; it never replaces the primary row.

Each native member requires observed output count 512, unique `decode` and
own `idle_baseline` spans, rails decode energy, its operative phase envelope,
and zero joint interpolation bound for interval-support telemetry. Gross is
primary; the secondary subtracts each member's own idle power times decode
duration. Signed secondary energies are retained. Rest is paired DC input minus
rails before aggregation. Battery assistance relies on the harvest's
`battery.assist` flag; analysis does not infer it anew or add battery energy.
For each selected cell with an assisted member, print `with_assisted_label`
and the nested `without_assisted` diagnostic side by side. The latter removes
whole repeat/quad units containing an assisted member and reruns the same
estimator, including duration, drift scale, h and B. Counts of assist members
and units are separate by stratum; `battery.assist_outside_request` does not
qualify. The line also appears in the idle-subtracted and flagged-inclusive
cells when their kept members contain assist. It decides nothing. Below five
units, print its counts and "below the registered minimum of 5 units"; with
2–4 units per stratum compute the diagnostic interval, with one unit print
the mean and a null interval (sample variance undefined), and with an empty
stratum print null mean/interval (fixed stratum weights undefined). A combined
model point retains every pass diagnostic and their mean/mean half-widths
when defined. No diagnostic is passed to H1, H2 or primary-pass selection.

Meter streams use native KM003C clock fitting and integration. The transport
is scanned incrementally for clock metadata and endpoint sequence numbers;
no out-of-selection power samples are unpacked or retained. Only authorized
science decode/idle spans, released NEG-8 request/idle spans and one adjacent
sample at each edge are decoded. Clock-fit metadata may cover the session;
held-out power is absent at fit stage. Tests compare this clock fit exactly
with the full native parser. No raw/monotonic mapping or fit gives a labelled
unavailable meter value, without changing rails. There is no hazard-journal
fallback.

At each edge, use the larger power of the two adjacent samples, including the
last in-phase sample at an aligned end. Per member,
`u=(P_start+P_end)*(r_max+sample_interval)`, with maximum absolute recorded
clock-fit excess latency (largest absolute recorded minimum or maximum,
including negative extremes) and native sample interval. Phase ends map to
integer nanoseconds by rounding to nearest, as in `_event_span`. The stratified mean u replaces
rails timing in DC input; rest carries rails timing plus u. The largest u is
printed as the meter attribution floor, never added again.

NEG-8 inputs come from export rows with `config_key=neg8_reference`, roles
`corpus`, `start`, `midpoint`, `end`, succeeded status and no exclusion. The
Block-6 corpus minimum/cap (6/12) and endpoint survivor minimum (2) apply.
For each boundary and separately for gross and idle-subtracted families,
call Block 5's `whole_window.neg8_count_adjusted_bound` on the kept corpus
using `aggregate.student_t_critical_95` (the registered 3-decimal table);
the allowance is max(repeatability bound, spread of the kept slot means).
Rails request energies come from the export, never withheld reference summaries.
DC-input/rest request energies use released reference meter spans.
E_ref and T_ref are means over all kept start/midpoint/end requests, excluding
corpus; native request events give the complete duration. CSV-only blinded
T_ref sums the exported nonoverlapping request-phase durations.

The per-cell drift term is half the appropriate family's allowance, multiplied
by max(1, gross-decode-m/E_ref, decode-T/T_ref) until the regime's test 7 passes.
The secondary uses its own family allowance with the same gross reference scale.
DC input uses its own DC-family allowance and scale, plus u in B (D2).
Rest uses its own rest-family allowance and scale, plus the rails anchor /
interpolation terms and u (D3). The meter edge never substitutes for drift.

## Arithmetic and output schema

`estimate_phase_energy` follows Block-5 plan §4 in registered order: canonical
50-member fmean at 10/10, otherwise fixed .2/.8 stratum weights; sample SDs;
variance .04*s_r^2/n_r+.64*s_b^2/n_b; min(n_r,n_b)-1 df; stratified means of
all three bound kinds summed by `math.fsum`; unclamped m-h-B and m+h+B.
Integers remain integers until the same arithmetic operations as the library.
Tests compare exact equality, including SDs, for 1,224 float/worked cases and
144 additional integer, constant, zero and subnormal cases across every
registered library shape. Negative secondary values and reduced counts are
additional BYTES generalizations outside the library's accepted domain.

H1 widens only h with t(1-.05/42,df). A combined point uses the mean of pass
energies and durations and the **mean of pass h+B**, without pooling h. Its
`power_half_w` is (mean h+mean B)/mean T. P-bar is mean E / mean T,
not the mean of the per-pass powers. All decode arithmetic uses **512 decode
forward passes**: e=E_dec/512, tau=T_dec/512 and BW=b/tau. The printed
per-token value is the same E/512, labelled exactly “512 decode forward
passes, one of which yields no returned token”. The first-token event and
512 observed returned tokens remain native validity inputs; this corrects the
analysis divisor without changing the runtime or measured phase spans.

`predictions.json` contains schema `joulewise.bytes_predictions.v1`, canonical
manifest SHA-256, `bytes_analysis_sha256` over exact source bytes, H1/H2 family
counts, full `neg8_inputs` by session, fit-only `fit_points`, `rival_lines`,
fit-model-only `tier_fit_inputs` (including BW, R/tau, power), and the dense
linearity note. `predictions.sha256` hashes the exact UTF-8 JSON file including
its final newline. Predictions are immutable and checked before stage 2.
The registration must say the tier inputs committed at stage 1 are **fit models
only**; the six-model tier fit is completed after held-out release.

Output arrays:

| File | Rows and principal fields |
|---|---|
| `fit_pass_estimates.json`, `heldout_pass_estimates.json` | model/pass/boundary/basis/selection; status; mean/endpoints; h, B, variance, df, counts; kept/removed runs; flags; duration; drift scale/family and full NEG-8 inputs; stratified meter edge and maximum attribution floors; operative provenance. |
| `blinded_pass_estimates.json` | Same rails-only table from the blinded CSV, labelled `blinded_export_bounds`. |
| `model_estimates.json` | Mean of passes with retained `passes`, values/difference, e/endpoints, power and `power_half_w`, tau, BW, frozen model metadata and output-token label. |
| `h1.json` | model/boundary/basis/selection; `pass_id="mean"` for primary words; numeric pass IDs with `description_only=true` for per-pass words; all three prediction intervals, measured intervals, consistency and log ratios. Nonpositive log ratios are explicit nulls with status. |
| `moe.json` | active/resident/mixed and every model's directional miss. |
| `h2.json` | simple, resident-extended and tier fits; per-fit n/p/df/status, actual k, point labels; primary intervals; tier deviations; rest fit and VIF; LOO description; separate two-pass sensitivity rows when required. |
| `unavailable.json` | Missing result groups and affected models; available H1 rows remain. |
| `analysis_record.json` | stage, manifest/prediction identities, family counts and synthetic status; blinded record restricts boundaries to rails. |

H2 retains OLS point estimates. Primary covariance is the HC3 sandwich with
residual/(1-leverage), transformed back from centered/scaled columns. Student-t
uses n-p df. `covariance`, `standard_errors` and `intervals` are HC3;
`se_method="HC3"`. `ols_covariance`, `ols_standard_errors` and `ols_intervals`
are labelled diagnostics. Every coefficient is printed; primary coefficients
also print `HC3_se` and `OLS_se` beside their intervals.

The primary family per boundary is simple epsilon; extended epsilon and rho;
tier epsilon and rho; up to four non-tier deviations; plus rest epsilon and
lambda for rest. Thus k=9/9/11 at the full roster. With missing points or refused fits, count
only computed primary coefficients and deviations. A refused tier fit also
refuses its deviations. All computed primary fits use that actual k. The
sensitivity row reuses primary k and calls its intervals `sensitivity_intervals`;
it adds nothing to k. `analysis_record.H2_intervals` lists actual n/k by
selection/basis/boundary. The prediction commitment's `H2_intervals` retains
the full-roster expectation, since held-out availability is not known at fit
release. Tier predictors are BW and
R/tau, with intercept. Each deviation interval is t*sqrt(MSE+x'HC3*x) plus
that model's own (h+B)/T, with both components printed. Rest records
`correlation`, `vif=1/(1-correlation^2)`, `vif_status`; an infinite VIF is null
with explicit status, never JSON Infinity. Lambda yields no word. “Resident
adds nothing” keeps the ruled rho interval/sign criterion.

## Decisions I made and ruling/code disagreements

- Applied Addendum 4 over the old 23-interval contract, one-regressor tier,
  pooled h, physics-only restoration and OLS primary errors. These were actual
  implementation disagreements, now superseded explicitly.
- Kept integers exact, rather than narrowing the library-equivalence claim.
- Used Block 5's existing NEG-8 bound function and Block 6's native role,
  export-column and key-file conventions. No second allowance formula or
  release-key generator was introduced.
- Block 6 at `220166913` has stored key files and a whole-export unblinder,
  but no subset-release ledger/API or shared-group consumer. The supplied
  release directory is the analysis interface: operators expose only released
  key files there. Both CLI and record ingress require it; the private sidecar
  directory is ignored. Historical release/commit timing remains procedural.
- Native exports have request-level bound columns, not operative decode
  envelopes. Blinded agreement uses exactly those exported rails quantities;
  released analysis uses the native per-phase re-reduction. Their uncertainty
  inputs are labelled separately rather than treating CSV bounds as native
  phase evidence.
- The requested base has no integrated R4 manifest producer or independent
  twin in this lane. Frozen regressors retain the established manifest schema;
  twin agreement and registration prose are owned elsewhere. Registration
  must record fit-only tier commitments and reliance on `battery.assist`.
- Synthetic campaign: 1,000 science runs plus 26 NEG-8 runs, real mock reducer
  and native B6 exporter. Mock traces still lack native interval-support,
  member calibration and an operative decode envelope; only an explicitly
  marked mock may provide its timing envelope. A non-claim=false fixture tests
  real random export offsets and staged key availability.
- No import-fence or inventory registry change is needed: no custody replay,
  issuer or measurement entry point was added. The only new owning-library
  call is the lazy, pure `neg8_count_adjusted_bound`. Relevant import/custody
  inventories are included in verification. No other registry was edited.

## Round-2 regression and probe record

The 13 `Addendum4RegressionTests.test_a4_*` methods all fail on the old module
and CLI at `82c014c55` (loaded in memory with the new fixtures); all pass after
repair. Subtests include every stage and non-synthetic archive joins with a
fake re-reducer. Method suffixes identify Addendum items 1–10 and 12; item 1
has a second cell-isolation test, item 5 a second 400-draw coverage test.
`ReviewerProbeTests` also executes the adapted p02/p05/p06/p08/p10 scripts.
Their copies under `tests/fixtures/bytes/repro/` are tests, not loose probes.

| Addendum 4 item | Regression in `Addendum4RegressionTests` |
|---|---|
| 1 | `test_a4_01_unusable_member_all_stages_and_nonsynthetic`; `test_a4_01_below_minimum_refuses_only_affected_cell` |
| 2 | `test_a4_02_p02_primary_family_and_two_regressor_tier` |
| 3 | `test_a4_03_p06_deviation_adds_own_halfwidth` |
| 4 | `test_a4_04_p05_mean_halfwidth_and_per_pass_words` |
| 5 | `test_a4_05_hc3_independent_sandwich_and_ols_label`; `test_a4_05_p03_coverage` |
| 6 | `test_a4_06_p08_number_exclusion_restored_validity_stays_out` |
| 7 | `test_a4_07_neg8_export_inputs_whole_request_and_two_families` |
| 8 | `test_a4_08_blinded_release_and_commitment_end_to_end` |
| 9 | `test_a4_09_p05_rest_vif` |
| 10 | `test_a4_10_p05_both_adjacent_edge_samples` |
| 12 | `test_a4_12_exact_integer_constant_zero_equivalence` |

The additional `test_malformed_meter_is_unavailable_without_losing_rails`
checks that transport corruption removes DC/rest values without erasing rails.
The item-1 cases also include a missing export row. The item-8 test guards the
actual sample unpacker against held-out power, in addition to checking the
retained spans and native clock-fit equality.

Before values below are the reviewer's captured outputs at JouleWise-data
`6039fff`; after values are executing tests on this tree. p03 preserves the
reviewer's member order, seeds 11/22/33 and 0.2% redraw for 400 draws per world.
The fixture now has actual references, so composite B/width changes include
that correction as well as the statistical and phase-edge fixes.

| Probe / quantity | Before | After |
|---|---:|---:|
| p02: primary count rails / DC / rest | 7 / 7 / 9, k=23 everywhere | 9 / 9 / 11, matching k |
| p02: tier coefficients / df | 2 / 4 | 3 / 3 |
| p03: resident extended plain-95% coverage, OLS → HC3 | OLS 0.8025 | HC3 0.9975 |
| p05: 32B first-member DC edge u, J | 0.689495 | 1.338989 |
| p05: 1.7B rails two-pass half-width, J | 0.01089 | 0.01333 |
| p05: 70B rails two-pass half-width, J | 0.29498 | 0.36917 |
| p05: 70B DC two-pass half-width, J | 1.31117 | 2.14073 |
| p05: rest VIF printed | absent | 3,411,626.9 |
| p06: width-related word disagreements in 801-point sweep | 6 | 0 |
| p06: 8B-8bit DC deviation half-width at baseline, W | about 0.0032 | 0.1051 |
| p06: +0.2% power offset falsely outside own interval | yes | no |
| p08 A/B: lost member / bad token exits | [0,1] / [1] | [0,0] / [0,0] |
| p08 D: inclusive cooldown quad count | 9 | 10 |
| p08 F: maximum change with +5 s raw-clock offset, J | 0 | 0 |
| p10: failed/null-energy exits | [0,1] | [0,0] |
| p10: failed/present-energy exits, inclusive quad count | [0,0], 9 | [0,0], 9 |

All p08 defect worlds and both p10 cases complete; invalid units stay removed
in both selections. Thermal and NUMBER exclusions with valid data restore in
the inclusive line. Battery-assist flags remain disclosures.

Coverage is a fraction of 400 draws. Plain-95% coverage is identical on rails,
DC input and rest in this construction. The k=9 columns cover rails and DC
input; k=11 covers rest. Simple-fit resident coverage refers to a misspecified
population projection, not a structural bytes slope. B never enters H2;
Bonferroni coverage alone does not calibrate the standard errors.

| World | Fit | HC3 95% | OLS 95% | HC3 k=9 | OLS k=9 | HC3 k=11 | OLS k=11 |
|---|---|---:|---:|---:|---:|---:|---:|
| bytes | simple | .9700 | .9675 | .9925 | .9875 | .9925 | .9925 |
| bytes | extended | .9850 | .9925 | 1.0000 | .9975 | 1.0000 | .9975 |
| time | simple | .9600 | .9600 | .9900 | .9925 | .9925 | .9925 |
| time | extended | .9725 | .9450 | .9975 | .9975 | .9975 | .9975 |
| resident | simple | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| resident | extended | .9975 | .8025 | 1.0000 | .9875 | 1.0000 | .9900 |

HC3's minimum plain-95% coverage is .9600. The Addendum 4 threshold .93 does
not fire. NEEDS_RULING: none. No alternative method was chosen.

## Verification and environmental failures

All recorded test runs used Python 3.13.5 with
`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1`, and the seat's temporary
root. These are separate runs, with overlapping tests; their counts are not
added as a count of distinct tests.

| Run | Count / result |
|---|---|
| Final `python3.13 -m unittest -v tests.test_bytes_analysis` | **43 passed**, 349.647 s. Includes all required probes, 400 draws/world, 60 extended campaigns, non-claim=false staged release, native fixture plus fake non-synthetic failures, and 1,368 exact library comparisons. |
| Native dependencies: `tests.b6.test_calibration`, `test_acceptance`, `test_export_runs`, `test_blinding`; `tests.external.test_km003c_parse`; `tests.test_custody_mode_inventory`; `tests.test_paper_reported_energy` | **121 passed**, 78.038 s. |
| Final import/custody/docs fences: `tests.test_custody_mode_inventory`, `tests.test_docs_freshness`, `tests.flags.test_flags_import_graph`, `tests.hazards.test_import_graph` | **47 passed**, 53.361 s. |
| `scripts/quick_suite.py --tier touched --since 82c014c55 --workers 4` | **285 modules**, 4,729 discovered tests: **276 modules passed**, 9 environmental failing modules (9 assertions, 4 errors), 470.366 s; 137 modules excluded by the runner's declared policy. |
| Old implementation loaded in memory, final numbered regressions | **13/13 methods fail** at `82c014c55`; 59 failing subtests and 31 erroring subtests expose the old refusals/missing paths/number differences. |
| Fixture orphan census after verification | `[]`, count 0, exit 0. |

The touched run included the 42-test BYTES module before the final missing-CSV
and malformed-stream hardening. That hardening and the new 43rd test were
verified by the final full BYTES run and the final fences above; unaffected
touched modules were not rerun. The standalone coverage fixture was also
import-smoked from outside the checkout.

The 60 extended campaigns produced no wrong unique word. Their printed
simulation JSON SHA-256 is
`ae6b632334ce747d8c8cf9021e723fcf152849052a903d76e1fe1a68bd545aed`.
This supersedes the old fixture's simulation digest, not any hardware evidence.

Environmental failures, separate from the passing BYTES and dependency checks:

| Failing touched module | Cases | Environment symptom |
|---|---:|---|
| `tests.b6.test_lane_adapters` | 1 failure | Courier requires `/opt/homebrew/bin/python3.13`; seat setup could not create `/opt/homebrew` (permission denied). |
| `tests.test_b5_chain_prune2` | 2 failures | Process-group survivors remain visible after TERM/cleanup. |
| `tests.test_b5_driver_p2` | 2 failures | Monitor-outage tests return courier-failed 6 instead of aborted 4; chain termination proof depends on process cleanup. |
| `tests.test_harvest_b5_p2harv` | 1 failure | Timed-out writer grandchild still appears alive. |
| `tests.test_run_campaign_p2_rc` | 2 failures | Member-timeout grandchild cleanup checks fail. |
| `tests.test_fixture_orphan_census` | 1 failure | Killed orphan fixture PID still appears instead of ProcessLookupError. |
| `tests.test_v5_block4_x12a` | 2 errors | Fixture backup command fails. |
| `tests.test_v5_block4_composed` | 1 error | Fixture backup command fails. |
| `tests.test_validate_powermetrics_fiducial_hazard` | 1 error | Fixture repository copy raises ENOSPC. |

The canonical `python3.13 -m unittest discover -s tests` was attempted and
interrupted after repeated platform failures; it did **not** finish and is not
reported green. The Mac whole-suite gate remains unrun here. Real hardware
inference/measurement was prohibited; no real BYTES campaign, live power join,
real operational release or independent twin agreement was run. Native
operative-envelope behavior has one existing synthetic native fixture and
fake coverage of the required non-synthetic refusal paths, not live evidence.

No import-fence or inventory registry was changed. Repository state/queue and
registration files were outside the exhaustive write list and were preserved.
NEEDS_RULING: **none**.

## Round-3 decisions and disagreements

Authority is Addendum 7 at `db83dbb58`, not the comparer's proposed D9
reading (which the lead superseded). At `fbd4b3f4f`, any refused pass erased
the combined point and H2 required ten points; the new ruled fallback
replaces both behaviors. That head also omitted the registered battery line
and still divided by 511. Those are repaired here. The DC/rest allowances,
NEG-8 tabulated t and nearest-nanosecond mapping were already correct.
Block-6's 512 observed-token validity rule stays distinct from the corrected
512-forward-pass denominator; neither runtime nor Block-6 code is edited.

Decisions I made:

- Apply pass availability separately in each selection, basis and boundary;
  retain refused pass rows alongside a surviving primary point. Propagate
  `one_pass` through model/pass tables, H1, MoE misses, committed tier inputs,
  H2 inputs, deviations and LOO descriptions.
- Keep H2 independent of missing H1 fit points. Refuse each underdetermined
  or singular fit explicitly; a refused tier line cannot yield deviations.
  Count only computed primary intervals in k. The labelled sensitivity uses
  that primary k and contributes no intervals to it.
- Rerun the identical cell estimator for the battery diagnostic, with whole
  assisted units removed. Never replace the primary value with it. Undefined
  means or sample variances are null with their reason, rather than fabricated
  zero values; defined below-minimum diagnostic values are still printed.
- Give the generator optional `pass_duration_scales` and `clock_latency_ms`
  inputs. Defaults retain the existing campaign timing so comparison is
  controlled. Tests request scales (1,2) and clock latency (-8,3) ms; the latter
  produces native positive and negative fitted excess latency, with the
  negative extreme larger in magnitude. Clock statistics are not patched.
- Use 512 in the generator, coverage harness and adapted numeric probes as
  well as the analysis. Keep 511 only where it deliberately represents an
  invalid observed-token fixture or a historical quotation.
- Compare the new implementation against `fbd4b3f4f` loaded in memory on
  the exact same newly built archives. Normalize only its decode divisor and
  printed label to the ruled 512 before looking for unrelated drift; the
  explicit denominator test separately checks that change. No twin is run or
  edited in this round. All artifacts are synthetic and temporary.

Each required regression fails on the original implementation **and original
generator** at `fbd4b3f4f`, loaded in memory without changing the checkout:
8 of 8 methods fail. The two checks of already-correct rules pass there.
Errors for missing APIs/fields are regression failures, not hardware evidence.

| Addendum 7 item | `Addendum7RegressionTests` method suffix |
|---|---|
| D9(a), labels and sensitivity | `test_a7_09_one_pass_primary_all_tables_and_two_pass_sensitivity` |
| D9(b), no point/word, n and actual k | `test_a7_09_both_refused_no_point_no_word_h2_n_and_k` |
| D9(b), per-fit df refusal and missing H1 fit model | `test_a7_09_each_fit_refused_below_two_df_h2_survives_missing_fit_model` |
| D10, registered mean, atomic quads and all cell families | `test_a7_10_without_assisted_registered_example_all_cells_atomic_quad` |
| D10, counts and defined/undefined values below minimum | `test_a7_10_below_minimum_prints_value_counts_and_no_decision` |
| 12, P-bar and its half-width on unequal durations | `test_a7_12_unequal_pass_duration_power_is_ratio_of_means` |
| 12, signed native clock fit and r_max | `test_a7_12_generated_signed_clock_latency_uses_largest_absolute_extreme` |
| 13 / Addendum 5.4, every divisor and label | `test_a7_13_exact_512_decode_denominators_and_printed_label` |
| D2, D3, D8 retained | `test_a7_02_03_08_allowances_and_registered_tabulated_t_still_hold` |
| 11 retained | `test_a7_11_phase_ends_round_to_nearest_nanosecond_still_holds` |

The earlier item-1 below-minimum regression now expects the ruled surviving
point and both H2 lines; its old expectation deliberately withheld them.

## Round-3 campaign comparison

Used the comparer's unchanged `agreement/scripts/build_campaigns.py` from
JouleWise-data `3db4f02` on this tree for bytes, resident, time, defects and
minimum. Every campaign ran blinded, fit and held-out stages; every attempted
held-out meter join with only fit keys refused as before. The baseline in
memory is normalized only as described above. These counts compare all shared
JSON quantities, beyond the twin's narrower comparison surface.

| Campaign | Numeric comparisons | Other shared values | Unexplained changes |
|---|---:|---:|---:|
| bytes | 126,487 | 119,189 | 0 |
| resident | 126,487 | 119,189 | 0 |
| time | 126,487 | 119,189 | 0 |
| defects | 126,487 | 119,385 | 0 |
| minimum | 112,243 | 107,885 | 0 |
| Total | **618,191** | **584,837** | **0** |

For minimum, comparisons exclude the affected 32B model, the newly available
H2 table and the changed unavailable table; all other shared values are
compared. New labels, battery diagnostics, actual-count schema and prediction
hashes are expected additions/identity changes. Main-campaign H1 words,
active/resident answers, existing cell quantities and H2 numbers do not change
beyond the denominator correction.

Quantities that moved:

- On fixed archived energies, e and tau multiply by 511/512 and BW by 512/511;
  per-token E/512 itself is unchanged. H1 lines/endpoints and H2 bandwidth/rate
  coefficients transform accordingly, with no main-campaign word moving.
  The generator's bytes/resident truth energies now use 512 passes; that is
  synthetic input regeneration, not a change to any archive or measurement.
- Minimum: 32B's pass-2 point becomes primary `one_pass`; its words are bytes
  on rails, unresolved on DC input and rest. Primary H2 has n=10 and k=9/9/11;
  two-pass sensitivity has n=9, retaining primary k. Both-refused and small-n
  variants are exercised by the regression tests, including reduced k.
- Defects, 30B pass 1, gross primary: the new without-assisted line has n_r=9,
  n_b=10. With / without energies (J) are rails 9.921441750 / 9.921546360,
  DC input 19.644562336 / 19.843093001, rest 9.723120586 / 9.921546641.
  The primary values do not move.
- Unequal-duration and latency fixture modes change their synthetic powers,
  clock statistics and meter attribution terms by construction. Tests pin the
  ratio of means and largest absolute latency, respectively.

No unexplained quantity moved. NEEDS_RULING: **none**.

## Round-3 verification environment

All runs use Python 3.13.5 and the supplied seat setup, with
`JW_B5_SYNTHETIC_ONLY=1 PYTHONDONTWRITEBYTECODE=1` and its TMPDIR.
The unmodified baseline completed **43 tests**, all passing (714.421 s).
The initial complete round-3 class completed **10 tests**, all passing
(25.631 s); the final module also includes the strengthened independent
DC/rest-scale assertions. Loading the original module, CLI and generator in
memory gives eight failing required methods and two passing retained-rule
checks. HC3's minimum plain-95% coverage remains **0.9600** over the
400-draw/world harness, so the .93 ruling threshold does not fire.

The canonical `python3.13 -B -m unittest discover -s tests -v` was attempted
and interrupted, not completed or reported green. The compressed-source
reharvest fixture fails because `desk_compress.restore` requires its default
20 GiB free-space reserve on this seat's approximately 9 GiB temporary volume;
a focused replay reproduces `reharvest source restore failed`. This was not
repaired in analysis code. Seat setup also reports permission denied creating
`/opt/homebrew`, so the fixed Homebrew interpreter courier fixture cannot run.
The broader touched run is recorded separately below. No live model inference,
measurement, real BYTES archive, Mac whole-suite gate, or new twin run is claimed.

Final focused verification: `python3.13 -B -m unittest -v
tests.test_bytes_analysis` — **53 passed**, 1208.190 s, including all 60
campaigns, all numbered round-3 regressions, 400 draws/world for HC3/OLS,
staged release and native/fake archive paths, and **1,368 exact Block-5
library-equivalence comparisons** (1,224 float/worked + 144 integer/edge
cases). No expected failures or skips. The final-source shared-campaign
comparison again gives 618,191 numeric and 584,837 other shared comparisons,
with zero unexplained changes.

Final touched check: `python3.13 -B scripts/quick_suite.py --tier touched
--since fbd4b3f4f --workers 4` — **285 modules**, **276 passed**, **9 failed**
(10 assertions, 3 errors), 137 policy exclusions, 1332.015 s. `gen_state --check`
and the documentation fence passed. BYTES passed again in this runner
(1180.300 s). These overlapping runs are not added as distinct tests.

| Failing broader module | Cases | Observed limitation |
|---|---:|---|
| `tests.b6.test_lane_adapters` | 1 failure | Courier's fixed `/opt/homebrew/bin/python3.13` is absent; setup could not create it. |
| `tests.test_b5_chain_prune2` | 2 failures | Process-tree cleanup still reports survivors after TERM/grace. |
| `tests.test_b5_driver_p2` | 2 failures | Monitor/liveness stop fixtures return courier-failed 6 instead of expected aborted 4. |
| `tests.test_b5_driver_p3` | 1 failure | Unproven-chain fixture does not see its fake meter stream; isolated replay also fails (1 test, 0.760 s). No BYTES code is involved. |
| `tests.test_harvest_b5_p2harv` | 1 failure | Timed-out writer grandchild still appears alive. |
| `tests.test_run_campaign_p2_rc` | 2 failures | Member-timeout grandchild cleanup/liveness checks fail. |
| `tests.test_v5_block4_x12a` | 2 errors | Fixture backup command fails. |
| `tests.test_v5_block4_composed` | 1 error | Fixture backup command fails. |
| `tests.test_fixture_orphan_census` | 1 failure | Killed fixture PID still appears instead of ProcessLookupError. |

These failures were preserved, not repaired outside the write list. The final
standalone fixture census returned `[]`, count 0, exit 0. No registry, raw run,
state/queue, registration, runtime, Block-5 or Block-6 file was edited.
NEEDS_RULING: **none**.


## Round-4: Addendum 8 / B2 (2026-10-20)

The synthetic reference request energies are now E_rails = 10 + delta and E_rest = 10 + 100*delta joules, where delta is the existing reference's deviation from 10 J. The 0.01 J endpoint rails drift therefore accompanies 1 J rest drift, at the approximate per-run attribution limit. DC is their sum; the native 10 Hz meter carries these energies through the real join. Science DC remains twice rails. These are stress parameters, not measured noise estimates.

The main campaigns keep pass durations 1/2 and signed receive latencies -8/+3 ms enabled. The duration-aware p03 redraw uses each member's own duration for time-world truth; population projections use mean E / mean T, as R3 requires. RNG seeds and the inherited 0.2% member CV are retained. The CV is not validated against a measured Block-5 or pilot spread by this brief.

D3 is tested by rerunning the reducer after substituting the rails reference family and its scaling inputs for rest. Every model's two passes and mean, both bases and both selections are checked: 10 * 3 * 2 * 2 = 120 rest cells per campaign, 7,200 over 60 campaigns. Each gap must exceed 0.10*B and ten actual energy agreement bars, 10*0.01*(h+B). No per-cell bar was tightened.

D8 is pinned directly against `aggregate.student_t_critical_95(len(corpus)-1)` for every NEG-8 prediction term. Exact equality there tests identical registered arithmetic on identical inputs. The native timing world exposes the H2 coverage finding below. The sole runtime edit remains the explicitly requested F7 guard repair; the ruled statistical method is unchanged.

| Flag | Final bar and derivation |
| --- | --- |
| F1 | 1% of the cell's (h+B), including the B-composition slack; Addendum 8 energy agreement replaces 13 places and 1e-12 J. |
| F2 | Lambda recovery uses its own ruled HC3 coefficient half-width instead of 0.03. |
| F3 | 0.00005 J is half the last digit of the registered worked endpoints printed to four decimals; it lies inside the brief's [2.2e-6, 1.3e-4] J window. |
| F4 | Meter-vs-rails recovery uses the native (P_start+P_end)*(r_max+0.1 s) integration envelope, plus 0.5 microW times duration for integer-microW quantization. |
| F5 | The constant-power reducer oracle has no half-width: 1e-6 relative or absolute J, the prescribed no-half-width bar. |
| F6 | Default assertAlmostEqual now uses the prescribed 1e-6 relative or absolute unit bar instead of seven absolute decimal places. Explicit half-width/precision checks retain their derived bars. |
| F7 | Pivots use matrix dimension * epsilon * max(abs(matrix)); leverage uses observation count * epsilon * max(1,abs(h)). Comments derive these from scaled-matrix/dot-product roundoff. A regression checks scale invariance and exact unit-leverage refusal. |

D3 exercise results:

| World | Campaigns | Rest cells checked | Minimum gap / B | Minimum agreement bars |
| --- | ---: | ---: | ---: | ---: |
| bytes | 20 | 2400 | 0.418963 | 41.545 |
| time | 20 | 2400 | 0.388547 | 38.433 |
| resident | 20 | 2400 | 0.475775 | 47.221 |

400-draw p03 coverage:

| World | Boundary | Fit | HC3 95% | OLS 95% | HC3 ruled-k | OLS ruled-k | k |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| bytes | rails | simple | 0.9700 | 0.9675 | 0.9925 | 0.9875 | 9 |
| bytes | rails | extended | 0.9850 | 0.9925 | 1.0000 | 0.9975 | 9 |
| bytes | DC input | simple | 0.9700 | 0.9675 | 0.9925 | 0.9875 | 9 |
| bytes | DC input | extended | 0.9850 | 0.9925 | 1.0000 | 0.9975 | 9 |
| bytes | rest | simple | 0.9700 | 0.9675 | 0.9925 | 0.9925 | 11 |
| bytes | rest | extended | 0.9850 | 0.9925 | 1.0000 | 0.9975 | 11 |
| time | rails | simple | 0.9425 | 0.9500 | 0.9925 | 0.9925 | 9 |
| time | rails | extended | 0.9725 | 0.9525 | 0.9950 | 0.9975 | 9 |
| time | DC input | simple | 0.9425 | 0.9500 | 0.9925 | 0.9925 | 9 |
| time | DC input | extended | 0.9725 | 0.9525 | 0.9950 | 0.9975 | 9 |
| time | rest | simple | 0.9425 | 0.9500 | 0.9950 | 0.9925 | 11 |
| time | rest | extended | 0.9725 | 0.9525 | 0.9950 | 0.9975 | 11 |
| resident | rails | simple | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 9 |
| resident | rails | extended | 0.9975 | 0.8025 | 1.0000 | 0.9875 | 9 |
| resident | DC input | simple | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 9 |
| resident | DC input | extended | 0.9975 | 0.8025 | 1.0000 | 0.9875 | 9 |
| resident | rest | simple | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 11 |
| resident | rest | extended | 0.9975 | 0.8025 | 1.0000 | 0.9900 | 11 |

The p03 table uses 400 member redraws per world and reports the epsilon coefficient in each fit. Simple resident-world truth is the fixed-design population projection, not a structural bytes slope. The 0.93 decision floor is the prescribed rounded two-SE floor: 0.95 - 2*sqrt(0.95*0.05/400) = 0.9282, rounded to two decimals. It is not applied as a per-cell recovery tolerance or to the 20-campaign descriptive rates. Minimum p03 HC3 plain-95% coverage is **0.9425**, so its automatic Addendum 4.5 threshold does not fire. The native production-shaped campaign has the separate failure in NR1 below; its 20-campaign rates are descriptive and are not presented as a 400-draw calibration.

60-campaign native coverage (20 campaigns per world):

| World | Boundary | Fit | HC3 95% | OLS 95% | HC3 ruled-k | OLS ruled-k | k |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| bytes | rails | simple | 1.0000 | 0.9500 | 1.0000 | 1.0000 | 9 |
| bytes | rails | extended | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 9 |
| bytes | DC input | simple | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 9 |
| bytes | DC input | extended | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 9 |
| bytes | rest | simple | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 11 |
| bytes | rest | extended | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 11 |
| time | rails | simple | 0.9500 | 0.9500 | 1.0000 | 1.0000 | 9 |
| time | rails | extended | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 9 |
| time | DC input | simple | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 9 |
| time | DC input | extended | 1.0000 | 0.0000 | 1.0000 | 1.0000 | 9 |
| time | rest | simple | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 11 |
| time | rest | extended | 1.0000 | 0.0000 | 1.0000 | 1.0000 | 11 |
| resident | rails | simple | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 9 |
| resident | rails | extended | 1.0000 | 0.8500 | 1.0000 | 0.9500 | 9 |
| resident | DC input | simple | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 9 |
| resident | DC input | extended | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 9 |
| resident | rest | simple | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 11 |
| resident | rest | extended | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 11 |

Resident-world CLI timing counterexample:

| Resident seed 3100 | Boundary | Epsilon (J/GB) | HC3 ruled interval | OLS ruled interval |
| --- | --- | ---: | --- | --- |
| signed_latency | DC input | 0.0019170703 | [0.00058414515, 0.0032499954] | [0.0012586502, 0.0025754903] |
| signed_latency | rest | 0.0018973809 | [0.00055599801, 0.0032387638] | [0.0012270137, 0.0025677481] |
| zero_latency | DC input | 3.9379038e-05 | [-9.8006124e-05, 0.0001767642] | [-2.8550115e-05, 0.00010730819] |
| zero_latency | rest | 1.9689668e-05 | [-5.175489e-05, 9.1134226e-05] | [-1.5635626e-05, 5.5014962e-05] |

**NR1 — native H2 coefficient coverage under meter timing systematics.** Resident-world structural epsilon is zero. Native signed-latency campaigns miss it at DC input and rest even at ruled k; the complete HC3/OLS plain/ruled table above gives the counts. This is separate from p03's passing 400-draw check. Its redraw explicitly sets meter gross energy to 2*e and removes the native timing shift.

The two separate-process resident-world chains use the same seed 3100 and the same doubled second pass. With signed -8/+3 ms latency, both HC3 and OLS plain/ruled DC/rest intervals exclude zero; with latency disabled, all include it. Maximum absolute meter-minus-twice-rails error is 5.868698 J with signed latency and 0.000058085 J without. Both prediction commitment files and hashes remain unchanged through stage 2. These are counterexamples, not two-draw coverage estimates.

The existing h2 function forms coefficient intervals as coefficient +/- t*HC3_SE (and labelled OLS_SE); it carries no phase-energy B term into those coefficient intervals. The native meter edge allowance is present in cell B, and tier deviations already add their own measured power half-width. This diagnosis does not authorize replacing the ruled coefficient method.

Question: should native clock/phase-edge systematics be propagated into H2 coefficient intervals, or should the registered intervals be explicitly conditional on the mapped meter energies with this limitation disclosed? The first changes printed intervals; the second changes the interpretation of a claim-bearing result. Recommendation: leave the ruled HC3/OLS method unchanged until the lead rules. Blocked work: accepting native DC/rest H2 coefficient coverage as validated. Independent B2 implementation and tests are complete. Potential lead-owned follow-up paths are docs/design/bytes_pack_design.md for a ruling, docs/registrations/bytes_pack_v1.md for the registered claim wording, and the independent twin. They are outside this B2 edit scope and were not edited.

Held-out mean-view H1 counts (7 models * 3 boundaries * 20 campaigns = 420 per world):

| World | bytes | resident | time | unresolved | neither |
| --- | ---: | ---: | ---: | ---: | ---: |
| bytes | 240 | 0 | 0 | 180 | 0 |
| time | 0 | 0 | 259 | 161 | 0 |
| resident | 0 | 240 | 0 | 180 | 0 |

Verification:

| Check | Result |
| --- | --- |
| Full `python3.13 -m pytest tests/test_bytes_analysis.py -q -s -p no:cacheprovider` | 56 passed, 187 subtests passed in 872.96s (0:14:32) |
| Final 60-campaign test after expanded HC3/OLS reporting | 1 passed in 538.50s (0:08:58) |
| Resident-world signed/zero-latency CLI probes | Two complete blinded/fit/heldout chains; unchanged prediction commitments; isolates NR1. |
| Focused analysis, excluding the 60-campaign and p03 tests | 53 passed, 2 deselected, 187 subtests passed; 194.47 s. This preceded addition of the guard test. |
| New inverse/leverage guard regression | 1 passed; 1.07 s. |
| First-commit separate-process synthetic stage chain | 1 passed; 11.51 s. Repeated successfully inside the full module. |
| All five required registry modules | 103 passed, 1 skipped, 1 environmental failure, 435 subtests passed; 39.18 s. |
| Refusal census | Exit 0; unlisted, stale, miscounted, guard_changed and scope_gaps all empty. |
| Collection | 56 tests. |
| Diff, ancestry and protected-path checks | Passed; no protected number-bearing path or Block-6/registered Block-5 file changed. |

The registry failure is the already-known container orphan case, `FixtureOrphanCensusTests.test_live_an_orphaned_fake_meter_is_reported`: the census finds the fake meter and the reaper returns its PID, but the final ProcessLookupError assertion fails because PID 1 retains killed children as zombies. Observed Python children have PPID 1 and state Z. This was listed, not chased; no census or reaper was edited. The one skip is the absent historical Block-5 design branch.

All completed runs use Python 3.13.5, JW_B5_SYNTHETIC_ONLY=1, PYTHONDONTWRITEBYTECODE=1, a fresh TMPDIR=/tmp/jw-b2.EZWXVe and isolated uv-installed pytest 9.1.1 on PYTHONPATH=/tmp/jw-b2.EZWXVe/venv/lib/python3.13/site-packages. zsh and Python were already available; no tested path needed the unavailable Homebrew symlink. A detached launcher ended before completion and was restarted in a persistent tool session; that incomplete attempt is not counted. A read-only collection attempt could not create pytest capture files and was rerun successfully with write access.

No real archive or key directory was opened. No whole suite was run: Addendum 2 reserves the merge gate for the Mac. No twin/agreement claim or live-hardware validation is made. The end-to-end test uses the existing B1 stage chain with separate `blinded`, `fit` and `heldout` CLI processes, actual release files, commitment hashes and unreleased-key refusals. The 60-campaign diagnostic separately uses the inherited all-stage analysis entry point; it does not replace the process-level chain test.


## NR1 labelled meter-offset alternative (Addendum 9)

Authority: `docs/process_traces/2026-10-21-magistrate-a017b694/B2-NR1-RULING.md`
on `records/2026-10-21-a017`; JouleWise-data
`claude/b2-nr1-judge-7n0s7d:reports/b2-nr1-judge/fable.md`, section 1.
Registered H2 coefficients, covariance, k and intervals stay unchanged and print
first, labelled **statistical; conditional on the mapped meter energies**.

The meter record adds `offset_bound_j = max(edge_powers_w) *
(r_max_s + sample_interval_s)` in joules, `adjacent_before_edge_powers_w`
and their signed difference `offset_sensitivity_w`. The pass and model tables
carry `meter_offset_bound_j` and `meter_offset_sensitivity_w`, using the existing
repeat/quad weights and then the arithmetic mean over available passes as B
is averaged. In `combine_passes`, `meter_offset_bound_w` is the pass-averaged
joules divided by the point's mean `duration_s`, the same ratio of means as
the point's power. Missing values remain null; they do not change selection.

Every computed DC-input/rest fit prints `coefficient_C`, where
C_j = sum_i |A_ji| bound_i and A = (X'X)^(-1)X', plus `offset_intervals` and
`offset_ols_intervals` (registered endpoints widened by C). No shrinkage, t
multiplier, drift, rails anchor or h is added to C. All coefficients, including
intercepts and the separate rest fit, carry the alternative. `primary_intervals`
repeats these columns for each primary coefficient. `coefficient_decisions` and
`offset_decisions` print positive/negative/contains-zero for both choices;
`resident_adds_nothing_offset` applies the registered rho rule to the alternative.
Rails has no C or offset alternative. Missing/invalid bounds print
`systematics_flag`, leaving the registered fit available.

Disclosure with every H2 DC/rest row (`offset_disclosure`): **delta has not been
measured (block-6 M13); its structural bound is one sample period plus the poll
round trip, 22 to 25 ms on recorded 50 SPS streams.**
`d_beta_d_delta_per_ms` prints the signed sensitivity
sum_i A_ji (P_adj-before-start,i - P_adj-before-end,i) / T_i / 1000.
`sensitivity_units` is J/GB per ms for epsilon/rho, W per ms for intercepts,
and per ms for lambda. Adjacent powers use the same weights and pass means;
T is the point's mean duration, as in the registered ratio-of-means power.
The alternative is conditional on observed regressors and does not resolve
uncertainty in the separate rest fit's measured rails predictor or its VIF.
The fixture remains 10 Hz: for a fixed delta the flips are five times larger
and five times rarer than at 50 SPS, inflating HC3's apparent self-protection.

NR1 cloud verification (2026-10-21): 57 analysis tests and 187 subtests pass.
All 72 native registered coverage rates match the judge's variant A at their
printed precision; all 48 DC/rest offset coverage rates are 1.0000. Resident
extended DC/rest registered HC3 plain-95% is 0.6500, already decided by the
ruling's printed alternative. p03's minimum HC3 plain-95% is 0.9425. The earlier
round-4 open NR1 below its historical tables is superseded by Addendum 9.
Commands, both coverage tables, the killed mutation and the known container
orphan-registry failure are recorded in JouleWise-data
`codex/bytes-b2-nr1-fix:reports/bytes-b2-nr1-fix/REPORT.md`.
