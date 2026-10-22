# NVML lane: fix round 1

## SUMMARY

Retained differing replay durations, clipping each sensor window to its own run.
Made known sensor-window ends the shared PowerTrace.t_ns timestamps.
Corrected known one-second output-average channels and retained unknown duty.
Normalized native NVML scalars and added real-pynvml-body sampler/CLI coverage.
Separated nominal repeatability intervals from the worst-case bias receipt.
Added metadata, timestamp-slew, cleanup and fake-clock preflight regressions.
Updated calibration bars and added four 400-seed, 16-replay jitter worlds.
Kept the eight-replay minimum; four replays need an external repeatability model.
Execution remains blocked by Cloud startup; the required acceptance runs are incomplete.
All changes are scoped fast-forward commits; no hardware or paid service was used.

## FILES

This round modifies only these nine authorized paths:

- joulewise/align/power/nvml.py: scalar normalization, structured sensor endpoints, per-sample unknown-age bounds, one-second output metadata and configurable wall-clock slew.
- joulewise/align/power/duty.py: own-duration clipping, retained metadata-flagged runs, exact phase grouping, normalized phase variance with duration variability, and separate systematic-bias flags.
- joulewise/align/power/preflight.py: contract timestamps, native version scalars, EPERM cleanup receipts and derived runbook defaults.
- tests/align/test_power_nvml.py: four-device metadata and one-bad-timestamp regressions; real pynvml Python bodies over fake C functions, with fake nvidia-smi executables for CLI serialization.
- tests/align/test_power_duty.py: metadata retention, +/-300 us duration replay regression, four-case production-shaped calibration and corrected four-SE bar.
- tests/align/test_power_duty_twin.py: EXISTING in-scope lane oracle; F5 nominal-width rule, obsolete F8 run-drop cases removed, and N2-N4 agreement bars.
- tests/align/test_power_preflight.py: observation-driven fake-clock load/control world, zombie-group EPERM receipt and four-SE false-alarm check.
- docs/align/nvidia_runbook.md: corrected clocks/channels, duration and uncertainty semantics, sampling defaults and replay cost.
- .codex-report/align-nvml.md: this report.

A read-only end-of-work docs sweep (as requested by repository AGENTS.md)
corrected the missing-bound/zero-area condition and separated sampler retention
from estimator use of output-average channels.

No new modules or registry additions in this round. The previous lane's
tests/test_shard_tests.py namespace fix is unchanged. The protected
PIPELINE.md, records.py, interfaces.py and NVIDIA CSV parser are unchanged.
No .review1 file or fetched external twin file was committed.

## PUBLIC API

Preserved:

- plan_offsets(period_ns: int, duty_fraction: float, repeats: int) -> list[int]
- estimate_energy(runs: Sequence[tuple[PowerTrace, int, int]]) -> DutyEstimate
- DutyEstimate(joules: float, half_width_j: float, coverage_fraction: float, flags: tuple[str, ...])
- CtypesNvml(library: Any | None = None)
- open_nvml(*, library: Any | None = None, prefer_pynvml: bool = False) -> Any
- device_inventory(nvml: Any, index: int) -> dict[str, Any]
- NvmlSampler.start() -> None
- NvmlSampler.stop() -> tuple[PowerTrace, ...]

Updated constructor (new final parameter):

NvmlSampler(device_indices: Sequence[int] | None = None, *,
interval_ns: int = 10_000_000, clock_domain: str | None = None,
nvml: Any | None = None, library: Any | None = None,
power_bound_w: float | None = None, repeat_group: str | int | None = None,
clock_ns: Callable[[], int] = time.monotonic_ns,
wall_clock_ns: Callable[[], int] = time.time_ns,
stop_timeout_s: float = 5.0, wall_clock_slew_ppm: float = 500.0)

Preflight:

- assess_power_movement(traces: Sequence[PowerTrace], idle_interval: tuple[int, int], load_interval: tuple[int, int], *, false_alarm_rate: float) -> dict[str, Any]
- run_preflight(*, device_indices=None, idle_seconds=10.0, load_seconds=10.0, recovery_seconds=2.0, interval_ns=10_000_000, load_cmd=None, try_lock_clocks=False, graphics_clock_mhz=None, false_alarm_rate=0.01, matmul_size=2048, command_timeout_s=5.0, nvml=None, library=None) -> dict[str, Any]
- main(argv: Sequence[str] | None = None) -> int

New/changed output spellings:

- worst_case_bias_j=<repr(float)> carries the separate systematic bound; inf is a string inside the flag. When systematic mismatch/timing area is nonzero, missing B adds worst_case_bias_unbounded and does not itself make the nominal width infinite. Exact zero area needs no bound.
- durations_differ, duration_spread_ns=<integer>, runs_retained=<integer>.
- sensor_duty_unknown, sensor_resolution_unknown, invalid_power_samples:<integer>, mixed_channels, mixed_clock_domains.
- Query notes: query_midpoint_ns and timing_half_width_ns.
- Sensor notes: window_end_ns (None only for an unknown sample), window_timing_half_width_ns, sample_flags, unknown_sensor_age_bound_ns and wall_clock_slew_ppm. Known window_end_ns entries equal t_ns.
- Trace flags: sensor_age_unknown and sensor_age_bound_unknown.
- Cleanup receipt: presence_permission_denied, with optional term_permission_denied/kill_permission_denied text.

## TESTS RUN

The selected Cloud environment never became usable: environment_status continued
to report starting/offline, and every exec_command attempt returned
"No usable execution environment is available." Both startup waits remained
pending. Therefore this is an execution-blocked handoff, not an acceptance pass.

Required local commands: NOT RUN, zero executed tests, no claimed pass/skip count:

```sh
python3 -m unittest discover -s tests/align -t .
python3 -m unittest tests.test_shard_tests
python3 -m unittest tests.align.test_twin_nvml tests.align.twins.test_nvml_twin_selfcheck -v
```

The first two commands must each run once with external twin files present and
once without them. Neither variant ran. No whole-repository suite was launched
from this seat; existing CI is left to perform its configured jobs.

Reviewer repro commands: all NOT RUN for the same missing-runtime reason:

```sh
python3 /workspace/JouleWise/.review1/probe1.py
python3 /workspace/JouleWise/.review1/probe3_sampler.py
python3 /workspace/JouleWise/.review1/probe4_channels.py
python3 /workspace/JouleWise/.review1/probe5_calib.py 400
python3 /workspace/JouleWise/.review1/probe7_edges.py
/tmp/nvml-venv/bin/python /workspace/JouleWise/.review1/probe8_pynvml.py
python3 /workspace/JouleWise/.review1/probe9_metadata_drops.py
python3 /workspace/JouleWise/.review1/probe10_tns_contract.py
python3 /workspace/JouleWise/.review1/torchfail.py
python3 -c "import sys; sys.path.insert(0,'/workspace/JouleWise'); from joulewise.align.power.duty import plan_offsets; print(plan_offsets(100_000_000,0.25,6))"
```

The appendix scripts could not be written into the unavailable workspace.
The twin branch was read through GitHub, but not materialized locally.
These setup commands were consequently NOT RUN:

```sh
git -C /workspace/JouleWise fetch origin lane/2026-10-21-align-nvml
git -C /workspace/JouleWise checkout -B lane/2026-10-21-align-nvml origin/lane/2026-10-21-align-nvml
git -C /workspace/JouleWise fetch origin lane/2026-10-21-align-nvml-twin
python3 -m venv /tmp/nvml-venv
/tmp/nvml-venv/bin/pip install nvidia-ml-py==13.615.71
```

Extra-dependency run: NOT RUN. There was no shell in which to create the venv
or install nvidia-ml-py. The guarded optional test now exercises real pynvml
function bodies with only the native library/function-pointer boundary faked;
it skips when pynvml is not importable. No optional-test execution is claimed.
The six-of-six F7 run with one busy loop per CPU is also NOT RUN.

Static test-method inventory, NOT an execution count: 19 NVML + 13 duty +
12 existing lane-oracle + 14 preflight = 58 lane tests. No registry change was
needed because no test module was added.

Observed CI evidence at source d3bae44bbbe47c3f52b379afaa24690d7d72cdf4:
https://github.com/mpmdw/JouleWise/actions/runs/39719330972

- build PASS: python -m build produced wheel and sdist on Python 3.11.
- installed-wheel PASS: installation without dependencies and configured CLI/layout smokes.
- fences PASS, including python -m unittest -v tests.test_docs_freshness: 31 tests, zero failures/errors/skips, 0.818 s.
- quick had started; no completed quick or lane-unit result was available at report preparation. Subsequent code commits supersede that source.
- gate-ledger FAIL: rows 1-4 are still explicitly NOT-RUN (independent executing review, integrated-main whole suite, final-head green CI, cold Fable gate). No gate was falsely marked complete.

At implementation source 301ddafa6201908dcc0f6c36abcaf014131b2769,
CI run 39719804343 passed build, fences, installed-wheel and
python3 scripts/quick_suite.py --tier quick --workers 4: 212 modules,
179 excluded, zero failures, PASS in 186.127 s. The four lane modules were
explicitly excluded for unknown timing weight. Ordinary lane-test shards were
queued when observed. Subsequent timing-metadata/doc corrections are untested;
the final report-only commit will obtain its own CI run. No final-head green
claim is made.
Final implementation source: dd5fce21e15aab0604cbf4b6584189c4ad64d5d4.
The final branch commit after it changes only this report.

Tests changed because review findings replace their old rule (not to weaken a bar):

- NVML test_driver_timestamp_mapping_and_declared_repeat_label and test_nonincreasing_clock_is_flagged_without_invented_timestamps: F2 puts sensor ends in t_ns, with query midpoints in notes; F9 adds slew to bounds.
- NVML test_optional_pynvml_uses_the_same_sampler_path: F4 replaces high-level function substitution with real binding bodies over a C-ABI fake.
- Duty test_sensor_window_timing_and_call_timing_remain_distinct: F2 makes t_ns authoritative even when notes conflict.
- Duty test_invalid_and_noncontributing_runs_do_not_change_valid_estimate: F8 keeps missing-resolution runs, so only genuinely unmodelled/noncontributing inputs remain in this zero-contribution check. A new metadata regression asserts retained runs and the required infinite width for unknown resolution.
- Duty test_missing_coverage_needs_an_explicit_power_bound: F5 removes B from nominal width; it checks the separate unbounded systematic receipt and unidentified phase spread.
- Existing oracle test_sparse_coverage_with_and_without_explicit_power_bound, test_partial_window_keeps_its_outside_support and test_timing_whole_window_shift_bound: F5 removes worst-case bias from nominal widths; independent rational-grid bias computation remains diagnostic.
- Existing oracle test_invalid_runs_are_skipped_without_changing_valid_result: F1/F8 no longer authorize the former duration/duty/resolution/sample run-drop cases; the dedicated production regressions now require their retention.
- Duty test_seed_coverage_matches_declared_nominal_level and preflight test_predictive_criterion_has_its_stated_nominal_false_alarm_rate: N1 replaces one SE with four SE.
- Preflight test_load_and_no_load_control_use_real_sampler_and_executables: F7 uses fake-clock sensor updates with real worker threads, C pointers, programs and cleanup.

## END-TO-END

No fixed-code world has an observed local output yet. Do not reuse the previous
report's executed numbers as proof of this head. In particular, new nominal
half-widths, their deltas, lane-twin joules differences, single-seed misses and
the calibration runtime remain UNMEASURED until the commands above execute.

Implemented production chains ready for execution:

1. Existing six-turn Episode (4,608 prefill tokens, 240 decode tokens, six
   tool calls, 6 s, analytic 1,161 J) -> fake C-ABI driver -> real NvmlSampler
   worker -> contract PowerTrace -> estimate_energy -> Episode JSON round-trip.
   The previous source's observed 1,160.999993675 J and 0.103839916627 J width
   are historical. F5 removes the systematic term from the nominal width, so
   that old width is not the new result.
2. New one-turn world: 1,500 prompt tokens at about 8k tokens/s (187.500137 ms,
   350 W), 135 decoded tokens at 45 tokens/s (3 s, 220 W with 15 W/7 Hz ripple
   in 1 ms steps), then a 483.271299 ms/75 W tool wait, with 55 W idle.
   Exact prefix integrals feed 25-of-100 ms sensor windows, 0.001 W rounding,
   2 W Gaussian run shifts and 0.3 W reading noise -> real estimate_energy.
   Each of four cases uses 400 seeds and 16 replays: aligned; 0-100 us starts;
   0-2 ms starts; 0-2 ms starts plus +/-300 us durations.
   The authorized four-SE bar is 4*sqrt(.05*.95/400)=0.0435889894; both zero
   misses and 400 misses fail. Counts and runtime must be printed by the test.
3. The preflight load and no-load controls use the real sampler and fake
   executable processes on PATH. A fake clock advances one 100 ms physical
   sensor period per driver update; each idle/load phase completes after
   100 observations (10 s of sensor time), recovery after 20 (2 s).
   The 250 versus 50 W load contrast is 1000 times the 0.2 W ripple. Wall time
   is only a deadlock guard, not the phase boundary.
4. The optional binding world runs real pynvml bodies over FakeNvmlLibrary
   through start/stop and preflight.main JSON with fake nvidia-smi on PATH.
5. A one-future-field-timestamp world retains all other mapped endpoints and
   exercises estimate_energy with a bounded unknown-age sample.

F3 structured field changes, from source inspection (NOT probe4 output):

| Device/channel | Before window ns / duty | After window ns / duty | Output span ns |
|---|---|---|---|
| A100 power_average | 25,000,000 / .25 | 1,000,000,000 / None | 1,000,000,000 |
| H100 power_usage | 25,000,000 / .25 | 1,000,000,000 / None | 1,000,000,000 |
| H100 power_average | 25,000,000 / .25 | 1,000,000,000 / None | 1,000,000,000 |

Each span increases by 975,000,000 ns (=1 s - 25 ms). Instant channels retain
25 ms/.25. A100 legacy remains 25 ms/.25; L4 and A10G structured window/duty
remain None; energy fields remain None. Sample counts and actual probe output
are unavailable. The four-device regression checks these same rows.

Probe7 whole before/after output: NOT AVAILABLE. The brief supplied the script,
not its complete output; no interpreter could produce either run here.
Probe1/3/10 single-world interval checks likewise remain unexecuted. F5 may
leave deterministic waveform bias outside the nominal repeatability interval;
the separate systematic receipt must be printed beside any such miss, and the
required calibration must execute without retuning to those seeds.

The older 1,000-seed tests use alpha=.05 and now four SE:
4*sqrt(.05*.95/1000)=0.0275680975 < .05. Thus neither a criterion that never
fires nor one that always fires passes. The prior 52/1000 duty and 54/1000
preflight counts are historical; no fresh counts are claimed.

## DECISIONS I MADE

### Round 2 boundary refinement, derived before implementation

The global-range candidate passes the aligned F5 case (7/400 misses) but
fails its unchanged 100 us case (2/400, below the lead lower limit .0064).
Its boundary term uses the entire 350-to-55 W workload range even though
the clipped end sees a 75-to-55 W tool-wait step. This is the wrong local
contrast for a spread-dominated world; no seed-specific constant is changed.

For each boundary, take each retained run's nearest fully inside sensor
window and nearest fully outside sensor window, using measured endpoints
(no chosen radius or timing threshold). Pool those readings across runs.
Use their observed range R_b in c_i * outside_fraction_i * R_b. This is
conditional on inside/outside power at that boundary staying within this
observed local range. If any run lacks either bracketing window, fall back
to the global observed range. A window straddling both boundaries uses the
larger boundary range. Coverage and known-timing terms remain global-range
bounds. All bounds add linearly; statistical calculation is unchanged.

Hand check: a 25 ms window with 15 ms inside at 75 W and 10 ms outside at
55 W reads 67 W. Assigning 67 W to 15 ms loses .120 J. The local bound is
.015*(10/25)*(75-55)=.120 J, while the unrelated 350 W prefill makes the
global bound .015*(10/25)*(350-55)=1.770 J. The local formula bounds this
error exactly and cannot let an unrelated prefill set interval size.
This derivation follows the lead's observed-data boundary-bound option;
it is not a fitted multiplier, tuned quantile, changed bar or changed seed.
New flags: boundary_observed_range_assumed, boundary_start_range_w=<value>,
boundary_end_range_w=<value>; fallback is boundary_range_fallback_global.

### Round 2 derivation recorded before implementation

- R2-M2 estimand: the mean run. Let A(u)=count{r:D_r>u}/n.
  Pool readings on each covered span with coefficient A(u)/N(u), not
  1/N(u); M=integral A=mean(D_r), C=integral_covered A. Scale
  coefficients by M/C. Their sum is M, not max(D_r). Duration spread
  remains in the existing phase-normalized run-to-run variance.
- R2-B1 coverage: choose R=max(y)-min(y) over valid readings from
  retained runs, including pre/post-roll. Under the explicit assumption
  that unobserved power stays in this observed range, the extrapolation
  error is at most (M-C)*R/1e9 J. Range is used rather than maximum
  reading so a constant baseline cannot dominate spread calibration.
- R2-M1 boundary: for window i of width w_i and clipped inside length
  l_i, a whole-window mean differs from its inside mean by at most
  (1-l_i/w_i)*R. Multiply by its actual energy coefficient c_i and sum.
  Known endpoint error h_i contributes c_i*min(h_i/w_i,1)*R; each
  term is a bound under the same observed-range assumption, not a
  standard error. Add these linearly to the unchanged 95% Welch
  repeatability term, quantum term and auxiliary-center displacement.
  Compute them on the auxiliary coefficients to match the triangle-
  inequality center displacement already in the interval.
- Unknown sensor age is not a known endpoint bracket: any contributing
  sample flagged sensor_age_unknown (including legacy A100 power_usage)
  gives infinite half-width plus sensor_window_time_unknown, even when
  a coarse period-plus-poll age diagnostic exists.
- Hand-worked R2-B1(a): D=8.034 s, coverage=.8413, so missing time is
  8.034*(1-.8413)=1.275 s to the brief's precision. The -80.08 J error
  requires an observed range at least 80.08/1.275=62.81 W. At a 64 W
  range the coverage term alone is 81.6 J; at a 250 W range it is
  318.75 J. The world has prefill/decode/tool-wait levels separated
  by much more than 62.81 W. These are hand calculations, not measured
  new outputs.
- Under-tiled plans: warn with RuntimeWarning and retain the evenly
  spread offsets. Minimum repeats=ceil(1/d), four for 25-of-100 ms;
  eight identifies within-phase repeatability with two replicas.
- Positive coverage with known timing/resolution must have a finite
  data-bounded interval under property 2. If a phase has no replica,
  its variance is unidentified: retain phase_without_replicates and
  bound its possible center error by its group coefficient mass times
  R, under an explicit unreplicated_phase_observed_range_assumed flag.
  This is a conservative data-envelope fallback, not an identified
  Gaussian variance. Round-1 F10 remains true about identification.
- New numeric diagnostic flags will be coverage_bound_j=<repr(float)>,
  boundary_bound_j=<repr(float)>, timing_bound_j=<repr(float)>,
  unreplicated_phase_bound_j=<repr(float)> and
  repeatability_half_width_j=<repr(float)>.
  Rename the nominal flag to
  nominal_95pct_gaussian_repeatability_plus_observed_range_bounds.
  Preserve worst_case_bias_j=<repr(float)> separately.
- R2 is expressly authorized by the lead's properties and bars. No seed
  tuning and no new NEEDS_RULING is required for this derivation.

- Continued from the exact existing 95a37eef8 lane head, not the spine. Read its
  report first, followed by governing contracts and NVIDIA parser. ACTIVE_STOP_CARD
  was NONE. Exhaustive delegated scope overrides lead-owned queue/state edits.
- The shell never started, so used connected GitHub reads and fast-forward
  tree/commit/ref operations with an expected-head lease. No force push, main
  update, local checkout, staging or local test run is implied.
- F1: retain every contributing run on [0,max D_r], clip windows individually,
  and include duration variation in the normalized phase run-to-run variance:
  multiply a run's weighted mean by D_r/mean(D_g). This avoids an arbitrary
  instantaneous bound dominating nominal width.
- Exact phase-grid grouping ignores terminal sample count, so measured duration
  differences do not destroy replicas. Jittered planned phases use explicit
  repeat_group labels; no endpoints are rounded to merge phases.
- F2: the code's PowerTrace contract wins over the earlier midpoint behavior.
  Unknown-age samples use a flagged query-time proxy; the known period plus
  polling interval supplies its stated age bound.
- F3: represent the one-second output span and set duty=None because ten
  disjoint slices cannot be represented as one physical duty window.
- F4: recursively normalize native integer/tuple scalars and replace only the
  native boundary in the optional test. Keep FakeNvmlLibrary constructor
  architecture/name parameters and _put helper; accept real c_uint/c_int inputs.
- F5: chose the explicitly authorized separate-bias option. Keep a nominal
  Gaussian/Welch repeatability interval plus quantum and auxiliary-center
  widening; report the worst-case kernel/timing bound only as
  worst_case_bias_j=<value>. Missing power_bound_w cannot alone cause infinity.
  This is conditional repeatability, not sensor accuracy or guaranteed waveform
  bias coverage; its calibration remains a required open verification gate.
- F6: EPERM means potentially present; reap the leader, retain presence/signal
  receipts, and preserve surviving-group evidence.
- F7: choose observation-driven fake clock phases rather than extending short
  wall-clock sleeps. Processes and production sampler paths still execute.
- F8: unknown resolution changes uncertainty only; missing duty does not enter
  energy computation. Malformed timing metadata also keeps the energy and makes
  its unidentified uncertainty infinite, rather than dropping the run. Drop/count individual invalid readings and flag mixed
  channels/clocks without refusing the result.
- F9: expose wall_clock_slew_ppm, default 500 ppm from Linux adjtimex MAXFREQ.
  Add ceil(age_bound_ns*ppm/1e6) to the mapping bracket plus full 1 us quantum.
  A bad field timestamp invalidates only its own endpoint.
- F10: reject a model-free finite four-run interval. Eight runs provide two
  replicas for each of four phases; the runbook states the cost and what
  external repeatability information a four-run method would need.
- N1: use four binomial SE. S=400 and S=1000 both exceed 304 for alpha=.05, so
  m=0 fails; m=S also fails. No seeds or thresholds were selected from results.
- N2-N4: use the lead's 1%-of-width joules bar, 1e-6-relative width bar and
  1e-6-absolute coverage bar below one.
- N5: 400 W is a synthetic diagnostic parameter above the deterministic 320 W
  peak, not a proven bound on unbounded Gaussian shifts and not a nominal term.
- N6: default 10 s idle/load contains 100 sensor or ten output-average periods;
  2 s recovery contains two output-average periods. Retained counts determine
  whether the predictive criterion is estimable.
- An automatic approval review initially confused the existing
  test_power_duty_twin.py with fetched external twin files. Supplied the
  explicit N2-N4 instructions and base-file evidence; the subsequent commit
  was approved. No unresolved automatic-review rejection remains.

## CONTRACT-CHANGE

No change needed to make t_ns obey the existing contract. Optional future
improvement: structured per-sample endpoint uncertainty/flags and a representation
of noncontiguous slices combined into a one-second output average. Current
JSON notes and output_average_not_single_window remain the lane-local adapter.
The three protected files were not edited.

## OPEN ISSUES

- Acceptance is INCOMPLETE. All required local repros, paired discovery/shard
  runs, optional nvidia-ml-py run, twin agreement and six loaded F7 repeats
  remain blocked by unavailable Cloud runtime. F1-F9/N1-N6 dispositions below
  describe implemented fixes, not passing repros.
- F5's four-case 400-seed test and probe5 400 must run before calling the
  statistical change calibrated. No miss count, runtime or new width is
  invented. Report single-world misses beside calibration rather than tuning.
- The external twin was read, not fetched into a working tree. The following
  decorator-only diff is ready for the lead/local copy; it is not an executed
  twin-test result. Existing resolution and one-phase spread identities are
  unchanged by separating bias, so no other twin test change is proposed
  absent actual failures.
- F10: a finite four-replay interval requires an external within-phase
  repeatability/noise model. Eight replays cost four extra workload durations
  over four; at the reviewer's printed 26.7 s duration this is about 106.8 s
  (=4*26.7 s) additional workload time, plus acquisition rolls/offset waits.
- No real sensor timestamp semantics, duty behavior, calibration accuracy,
  Gaussian model, GPU isolation or load response has been hardware-validated.
- Existing draft PR merge gates remain open. The prior report's unrelated
  courier timeout is historical, not a result of running the current suite.

Twin-test diff (external files deliberately not committed):

```diff
--- a/tests/align/test_twin_nvml.py
+++ b/tests/align/test_twin_nvml.py
@@ -247,7 +247,6 @@ class TwinAgreementTests(unittest.TestCase):
                 self.assertLessEqual(abs(a.joules - b.joules), joules_bar(a, b))
 
-    @unittest.expectedFailure
     def test_jittered_durations_keep_every_run(self) -> None:
         # Review finding: the lane drops every run whose measured duration
         # differs from the first by any nanosecond ("duration_mismatch"), so a
         # real replay set (durations jitter by microseconds) keeps one run.
```

## NEEDS_RULING

none

## FIX LOG

"Fixed" below means the implementation is committed. Execution-based acceptance
is still blocked and is not claimed complete.

F1 fixed with 1813efd72be981d354520c3f9cfeb0d33737ac73 and 301ddafa6201908dcc0f6c36abcaf014131b2769; all durations contribute and duration spread enters phase variance.
F2 fixed with 8e4f06316030214a6df2df9725c389eceeb71082; known sensor window ends populate t_ns and query timing stays in notes.
F3 fixed with 8e4f06316030214a6df2df9725c389eceeb71082; known output averages use a 1 s span and unknown duty.
F4 fixed with c05dfd6f2796a76689cee70210d994ad8ffc6424 and 301ddafa6201908dcc0f6c36abcaf014131b2769; normalize native scalars and exercise real pynvml bodies over a C-ABI fake.
F5 fixed with 1813efd72be981d354520c3f9cfeb0d33737ac73 and 301ddafa6201908dcc0f6c36abcaf014131b2769; separate worst_case_bias_j from nominal width; calibration execution remains blocked.
F6 fixed with 4244d060836ccfdcb6f47209ab4df00e5f3fab71; EPERM presence probes retain a cleanup receipt and reap the leader.
F7 fixed with 4244d060836ccfdcb6f47209ab4df00e5f3fab71 and cd377d6d2363ec0aae7a21f196b983c062a93a47; drive the real sampler/executable test phases by fake-clock update counts.
F8 fixed with 1813efd72be981d354520c3f9cfeb0d33737ac73 and dd5fce21e15aab0604cbf4b6584189c4ad64d5d4; retain metadata-flagged runs, omit invalid samples individually, and flag mixed channels/clocks.
F9 fixed with 8e4f06316030214a6df2df9725c389eceeb71082; parameterize slew and retain each unaffected sample's mapped endpoint.
F10 rejected; one run per phase cannot identify within-phase replay variation without an external noise model; retain the documented eight-replay minimum.
N1 fixed with 1813efd72be981d354520c3f9cfeb0d33737ac73 and 4244d060836ccfdcb6f47209ab4df00e5f3fab71; use four binomial SE and seed counts that reject never/always firing.
N2 fixed with 1813efd72be981d354520c3f9cfeb0d33737ac73; joules agreement uses 1% of the smallest printed half-width.
N3 fixed with 1813efd72be981d354520c3f9cfeb0d33737ac73; half-width agreement uses 1e-6 relative.
N4 fixed with 1813efd72be981d354520c3f9cfeb0d33737ac73; coverage below one uses 1e-6 absolute.
N5 fixed with 1813efd72be981d354520c3f9cfeb0d33737ac73; explain the synthetic bound and its exclusion from nominal width.
N6 fixed with 4244d060836ccfdcb6f47209ab4df00e5f3fab71; defaults match the runbook's derived 10 s idle, 10 s load and 2 s recovery.
