# BYTES analysis tables and round-2 verification

Authority: `docs/design/bytes_pack_design.md` at `32790070e`, including Addenda
1–4. Addendum 4 supersedes the implementation choices at `82c014c55`.
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
available held-out points if the three frozen fit cells exist. H2 needs all ten
model cells, and active/resident needs the three MoEs. Missing meter data
changes only DC-input/rest selection. Missing a pass never silently changes
the pass average. Unavailable cells retain reasons.

Each native member requires observed output count 512, unique `decode` and
own `idle_baseline` spans, rails decode energy, its operative phase envelope,
and zero joint interpolation bound for interval-support telemetry. Gross is
primary; the secondary subtracts each member's own idle power times decode
duration. Signed secondary energies are retained. Rest is paired DC input minus
rails before aggregation. Battery assistance relies on the harvest's
`battery.assist` flag; analysis does not infer it anew or add battery energy.

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
clock-fit residual and native sample interval. The stratified mean u replaces
rails timing in DC input; rest carries rails timing plus u. The largest u is
printed as the meter attribution floor, never added again.

NEG-8 inputs come from export rows with `config_key=neg8_reference`, roles
`corpus`, `start`, `midpoint`, `end`, succeeded status and no exclusion. The
Block-6 corpus minimum/cap (6/12) and endpoint survivor minimum (2) apply.
For each boundary and separately for gross and idle-subtracted families,
call Block 5's `whole_window.neg8_count_adjusted_bound` on the kept corpus;
the allowance is max(repeatability bound, spread of the kept slot means).
Rails request energies come from the export, never withheld reference summaries.
DC-input/rest request energies use released reference meter spans.
E_ref and T_ref are means over all kept start/midpoint/end requests, excluding
corpus; native request events give the complete duration. CSV-only blinded
T_ref sums the exported nonoverlapping request-phase durations.

The per-cell drift term is half the appropriate family's allowance, multiplied
by max(1, gross-decode-m/E_ref, decode-T/T_ref) until the regime's test 7 passes.
The secondary uses its own family allowance with the same gross reference scale.

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
`power_half_w` is (mean h+mean B)/mean T. E/511 and T/511 are used internally;
E/512 is printed with “512 output tokens, 511 generated in the decode phase”.

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
| `h2.json` | simple, resident-extended and tier fits; primary intervals; tier deviations; rest fit and VIF; LOO description. |
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
lambda for rest. Thus k=9/9/11 at the full roster. Tier predictors are BW and
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
