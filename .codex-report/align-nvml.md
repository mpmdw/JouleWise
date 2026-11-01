# NVML lane: fix round 2

## SUMMARY

Added observed-data coverage, boundary and known-timing bounds to the printed interval.
Changed duration-varying integration to target mean-run energy.
Kept worst_case_bias_j diagnostic; unknown sensor age yields an infinite interval.
Plans that cannot tile warn, and unreplicated phases carry a finite flagged data envelope.
Passed final alignment discovery with twins (104 tests) and without twins (68 tests).
Passed both shard censuses, the 36-test twin suite and the installed-pynvml 19-test run.
Passed the required 400-seed short/long and spread-dominated reviewer calibrations.
Duration-jitter misses are 4/3/1/0 of 60; the new 400-seed median test chooses mean truth 400/400.
All changes remain on the lane; PR #524 is draft and no hardware was measured.

## FILES

This round changes only these six authorized paths:

- joulewise/align/power/duty.py: mean-run coefficients, observed-range coverage,
  local-boundary and known-timing bounds, unknown-age infinity, numeric
  diagnostic flags, finite unreplicated envelope and planning warning.
- tests/align/test_power_duty.py: late-start/no-bound, short-boundary 400-seed,
  duration/median 400-seed, mean-duration analytic and coarse-age regressions.
- tests/align/test_power_duty_twin.py: EXISTING in-scope direct-grid oracle,
  R2 bound formulas, local-boundary physical witness and N7's derived bar.
- tests/align/test_power_nvml.py: byref fake-array dereference and the R2
  unknown-age rule in the one-future-timestamp integration test.
- docs/align/nvidia_runbook.md: mean-run target, replay minimum/warning,
  interval terms, local/idle assumptions and all new flag spellings.
- .codex-report/align-nvml.md: this report.

No registry additions in R2. The prior tests/test_shard_tests.py namespace
registry fix is unchanged. The protected PIPELINE.md, records.py,
interfaces.py and the reused NVIDIA CSV parser are unchanged.
No .review2 script or external twin file is committed.

## PUBLIC API

```python
plan_offsets(period_ns: int, duty_fraction: float, repeats: int) -> list[int]
estimate_energy(runs: Sequence[tuple[PowerTrace, int, int]]) -> DutyEstimate
DutyEstimate(joules: float, half_width_j: float, coverage_fraction: float, flags: tuple[str, ...])
CtypesNvml(library: Any | None = None)
open_nvml(*, library: Any | None = None, prefer_pynvml: bool = False) -> Any
device_inventory(nvml: Any, index: int) -> dict[str, Any]
NvmlSampler(device_indices: Sequence[int] | None = None, *,
    interval_ns: int = 10_000_000, clock_domain: str | None = None,
    nvml: Any | None = None, library: Any | None = None,
    power_bound_w: float | None = None, repeat_group: str | int | None = None,
    clock_ns: Callable[[], int] = time.monotonic_ns,
    wall_clock_ns: Callable[[], int] = time.time_ns,
    stop_timeout_s: float = 5.0, wall_clock_slew_ppm: float = 500.0)
NvmlSampler.start() -> None
NvmlSampler.stop() -> tuple[PowerTrace, ...]
assess_power_movement(traces: Sequence[PowerTrace], idle_interval: tuple[int, int],
    load_interval: tuple[int, int], *, false_alarm_rate: float) -> dict[str, Any]
run_preflight(*, device_indices=None, idle_seconds=10.0, load_seconds=10.0,
    recovery_seconds=2.0, interval_ns=10_000_000, load_cmd=None,
    try_lock_clocks=False, graphics_clock_mhz=None, false_alarm_rate=0.01,
    matmul_size=2048, command_timeout_s=5.0, nvml=None, library=None) -> dict[str, Any]
main(argv: Sequence[str] | None = None) -> int
```

Signatures and DutyEstimate's four fields are unchanged.

New numeric flags, each spelled <name>=<repr(float)>:
observed_reading_range_w, coverage_bound_j, boundary_bound_j,
boundary_start_range_w, boundary_end_range_w, timing_bound_j,
unreplicated_phase_bound_j, repeatability_half_width_j, resolution_bound_j,
auxiliary_center_bound_j.

nominal_95pct_gaussian_repeatability is renamed to
nominal_95pct_gaussian_repeatability_plus_observed_range_bounds.
The new assumption flags are observed_range_bounds_assumed,
boundary_observed_range_assumed, outside_idle_baseline_assumed and
unreplicated_phase_observed_range_assumed. Missing local support adds
boundary_range_fallback_global. phase_without_replicates remains; its finite
range envelope does not identify a Gaussian variance.

worst_case_bias_j=<value> remains, including inf, plus
worst_case_bias_unbounded for nonzero mismatch without a supplied B.
sensor_window_time_unknown makes half_width_j infinite when a contributing
sample's sensor age is unknown, even with a period-plus-poll maximum age.

The other R1 spellings remain: durations_differ, duration_spread_ns=<integer>,
runs_retained=<integer>, sensor_duty_unknown, sensor_resolution_unknown,
invalid_power_samples:<integer>, mixed_channels, mixed_clock_domains;
query_midpoint_ns, timing_half_width_ns, window_end_ns,
window_timing_half_width_ns, sample_flags, unknown_sensor_age_bound_ns,
wall_clock_slew_ppm, sensor_age_unknown, sensor_age_bound_unknown;
cleanup presence_permission_denied and optional term_permission_denied /
kill_permission_denied.

A valid but under-tiled plan returns offsets and emits RuntimeWarning:
"<repeats> repeats cannot tile the period; need at least <minimum>".
Minimum repeats=ceil(1/d), four for 25-of-100 ms; two replicas per phase
(eight total) identify the within-phase statistical term.

## TESTS RUN

The executor initially returned "No usable execution environment is available"
for pwd and python3 --version. It later became usable; all final required
commands below EXECUTED on Python 3.12.14. The earlier execution-blocked
report is superseded. No whole-repository suite was launched by this seat.

Final numerical source: d391ece3eaa193de092818fad930563b92c974fe.
From /workspace/JouleWise, with JW_B5_SYNTHETIC_ONLY=1 set:

| Exact command | Twin files | Tests | Skips | Runtime (s) | Result |
|---|---|---:|---:|---:|---|
| python3 -m unittest discover -s tests/align -t . | present, local rule diff | 104 | 1 | 373.739 | PASS |
| python3 -m unittest discover -s tests/align -t . | absent | 68 | 1 | 450.992 | PASS |
| python3 -m unittest tests.test_shard_tests | present | 4 | 0 | 29.180 | PASS |
| python3 -m unittest tests.test_shard_tests | absent | 4 | 0 | 31.356 | PASS |
| python3 -m unittest tests.align.test_twin_nvml tests.align.twins.test_nvml_twin_selfcheck -v | present, local rule diff | 36 | 0 | 36.216 | PASS |
| python3 -m unittest discover -s tests/align -t . -p 'test_power_nvml*.py' | irrelevant | 19 | 1 | 0.296 | PASS |
| /tmp/nvml-venv/bin/python -m unittest discover -s tests/align -t . -p 'test_power_nvml*.py' | irrelevant | 19 | 0 | 0.808 | PASS |
| /tmp/nvml-venv/bin/python /workspace/JouleWise/.review2/pynvml_fixed_fake.py | irrelevant | 1 | 0 | 0.593 | PASS |

Discovery additionally sets PYTHONDONTWRITEBYTECODE=1; PYTHONUNBUFFERED=1
only flushes progress. The two discovery skips are the same optional test,
test_optional_pynvml_uses_the_same_sampler_path:
"optional nvidia-ml-py is not installed; ctypes path is tested".
The base interpreter remains without extras. The optional environment was
created by these executed commands:

```sh
python3 -m venv /tmp/nvml-venv
/tmp/nvml-venv/bin/pip install nvidia-ml-py==13.615.71
```

The installed-extra module run has no failures, errors or skips, and the
supplied fixed-fake repro prints OK. No optional test was replaced with a
mock of its Python binding bodies.

The four external twin files were fetched from
origin/lane/2026-10-21-align-nvml-twin (11abc4049), copied locally, and never
staged. The two required expectedFailure decorators were removed locally.
The unmodified agreement run then failed only
test_jittered_replays_keep_every_run_and_agree:
coverage differed by 1.308739141347992e-05 against its unchanged 1e-6 bar.
R2-M2 changes that reference's estimand. With the exact local rule diff in
OPEN ISSUES, all 36 twin tests pass. Resolution, one-phase spread and
equal-duration partial-gap identities pass without changes.

The initial discovery (global candidate and obsolete rules) ran 103 tests,
407.765 s, 3 failures, 1 skip: the unchanged F5 100 us calibration, the
obsolete finite-age assertion, and the old twin estimand reference.
The completed final runs in the table supersede that run. Earlier long
jobs were terminated/restarted when their candidate changed; no result
from an interrupted job is claimed. One attempted temporary twin move hit
EXDEV before moving anything; the mislabeled discovery was stopped and
the final absent-files run was restarted after confirming absence.

Additional focused final checks:
- python3 -m unittest tests.align.test_power_duty_twin:
  13 tests, PASS, zero skips, 0.178 s.
- python3 -m unittest tests.align.test_power_duty.DutyWorldTests.test_production_jitter_calibration_at_nominal_95_percent:
  1 test containing four 400-seed worlds, PASS, 135.567 s.
- An AST source-segment comparison confirms that the entire original F5
  calibration test body is byte-identical to 432f14c7a.
- git diff --check: PASS.

Reviewer scripts were materialized verbatim with only the required path
substitution. The following commands executed, each exit 0:

```sh
python3 /workspace/JouleWise/.review2/probe1.py
python3 /workspace/JouleWise/.review2/probe3_sampler.py
python3 /workspace/JouleWise/.review2/probe7_edges.py
python3 /workspace/JouleWise/.review2/probe10_tns_contract.py
python3 /workspace/JouleWise/.review2/r2_late_check.py
python3 /workspace/JouleWise/.review2/r2_calib_short.py short 0.0 400
python3 /workspace/JouleWise/.review2/r2_calib_short.py short 0.2 400
python3 /workspace/JouleWise/.review2/r2_calib_short.py short 0.5 400
python3 /workspace/JouleWise/.review2/r2_calib_short.py long 0.0 400
python3 /workspace/JouleWise/.review2/r2_calib_short.py short 2.0 400
python3 /workspace/JouleWise/.review2/r2_power_usage.py
python3 /workspace/JouleWise/.review2/r2_durjit_tail.py
python3 /workspace/JouleWise/.review2/r2_durjit_large.py
python3 /workspace/JouleWise/.review2/probe5_case.py 400 0
python3 /workspace/JouleWise/.review2/probe5_case.py 400 1
python3 /workspace/JouleWise/.review2/probe5_case.py 400 2
```

The long world and three probe5 cases ran concurrently in background exec
sessions. For the paired medians only, these exact scripts also ran with
PYTHONPATH=/tmp/nvml-r2-metrics. Its temporary sitecustomize wraps the real
lane estimator, returns its result unchanged, calls the real external twin,
and records returned numbers/truth. It changes no waveform, samples,
estimator output, bar or seed and leaves each supplied script untouched.
Its paired medians use statistics.median (average of middle two); the
verbatim scripts print the upper middle element. Both appear below where
needed. No probe/test performs a network request.

The temporary paired-unit calculation additionally calls the public lane
and twin functions on the same lane fixtures for every required median.
Its data are printed below, distinct from unittest pass counts.

Tests changed because R2 supersedes their old rule, never to loosen a bar:

- test_phase_plan_tiles_then_replicates now requires the warning while
  preserving the same integer plan.
- test_missing_coverage_needs_an_explicit_power_bound becomes
  test_missing_coverage_has_a_finite_observed_range_bound: property 2
  replaces infinity with a finite conditional envelope and truth containment.
- test_one_future_field_timestamp_keeps_other_window_ends retains every
  mapping/retention assertion; R2-M1(c) changes its finite-width expectation
  to infinity plus sensor_window_time_unknown for the one unknown-age sample.
- The in-scope direct-grid oracle's half-width formula follows the new
  coverage, boundary and timing terms. Its numerical bars are unchanged.
  test_sparse_coverage_with_and_without_explicit_power_bound compares the
  new data-bounded widths.
- test_unreplicated_geometry_cannot_estimate_spread becomes
  test_unreplicated_geometry_has_a_flagged_data_envelope; the unlabeled
  branch of test_declared_replicas_with_unequal_weights_and_analytic_jitter
  follows property 2 with the same non-identification flag.
- N7 changes only delta to .01*half_width_j with the stated derivation.
- The original production-jitter calibration remains byte-identical.

New detectability bars do not grow with unrelated interval terms: the late
test uses 1% of its isolated coverage bound; the analytic mean-duration test
uses 1% of q*M/2=.00075 J. The local-boundary witness compares a .120095 J
width at the unchanged 1e-6-relative width bar; substituting the global-range
bound gives 1.770095 J, an effect far above that bar. The existing tiled
exact worlds have zero coverage/boundary area, so their 1%-of-total-width
bars do not conceal the phase-tiling effect.

Quick-repro measured wall runtimes: r2_late_check .802 s (2 worlds),
probe1 9.716 s (4 cases), probe7_edges 2.493 s (16 rows),
probe10_tns_contract 6.670 s (1 sampled world, 3 reader checks),
r2_power_usage 9.837 s (2 channels), probe3_sampler 25.453 s (2 cases),
r2_durjit_tail 1.592 s (1 world), r2_durjit_large 291.646 s
(4 levels x60 seeds). Short0/.2/.5/2 measured wall runtimes are
38.922/22.229/39.215/22.450 s. Long and probe5 per-script runtimes appear
in the paired table. Extra diagnostics do not count as unittest cases.

Observed CI for numerical source d391ece3eaa193de092818fad930563b92c974fe:
https://github.com/mpmdw/JouleWise/actions/runs/39736731835
Build, fences, installed-wheel, quick and all exclusive jobs pass; ten
ordinary shards passed and two remained in progress at observation.
Quick command: python3 scripts/quick_suite.py --tier quick --workers 4,
212 modules, 179 excluded, zero failures, 128.196 s. Its log explicitly
excludes the alignment modules for unknown weight; it is not lane evidence.
The fences' python -m unittest -v tests.test_docs_freshness passed 31 tests,
zero skips, 0.812 s. No final-head green claim is made.
Gate-ledger run39736731799 fails because PR-body rows1-4 remain NOT-RUN;
these are independent review, main integration, final CI and cold gates,
not a failing local repro. The report-only final head gets its own run;
its available status is reported in the final response without waiting.

## END-TO-END

All worlds below ran through the real public estimate_energy; no mocked
estimator replaces it. No real hardware evidence is claimed.

Mean-run geometry: A(u)=active runs/n, M=integral A=mean duration,
C=integral_covered A. Coefficient mass is M after extrapolation, not max D.
The 100 W, 1 s / 2 s analytic regression returns 150 J (the old point was
200 J), a -50 J correction. Its 1%-of-quantum comparison bar is .0000075 J.

Late-start R2-B1(a), seed 42:
D=M=8.033797962 s, C=6.758797962 s, uncovered=1.275 s.
Observed R=293.738 W gives 1.275*293.738=374.515950 J coverage bound.
The final local end range is 184.277 W, giving 1.248919062 J boundary
bound; q*M/2=.004016898981 J, timing/spread/center=0.
Thus half_width_j=375.768885961 J. This was worked by hand before coding
at rounded D=8.034, coverage=.8413 (1.275 s missing); the executed
substitution verifies the derivation. The original global-range candidate's
prediction was 376.510747 J; local boundary evidence reduces it by
.741861054 J. The point is unchanged, 1313.231311623 J against truth
1393.312531878 J, error -80.081220255 J. From the original .004016899 J
width, the final width increases by 375.764869062 J.

The collapsed-phase row changes from 1382.231 +/-2.800 J to
1382.230668032 +/-1785.787323426 J at coverage .248948257, containing
1393.312531878 J. The 2-replay probe7 world returns offsets [0,50000000],
J=1775.170688041 J, half-width=3591.430594871 J, coverage=.499467881,
truth=1779.579558169 J, plus RuntimeWarning and partial_coverage.

Final r2_late_check output:
```text
truth 1393.3125318779817 D s 8.033797962
lane 1313.2313116227854 375.7688859610247 0.8412954861410791 ['coverage_bound_j=374.51595', 'coverage_smoothing_or_timing_bound', 'partial_coverage', 'worst_case_bias_j=576.0529769784613']
twin 1104.815574727378 449.9368770165358 0.8412954861410791 True
collapsed: truth 1393.3125318779817 lane 1382.2306680321724 1785.7873234260937 0.24894825703360152 twin 344.103915625 2104.31553473917
```

The production-shaped six-turn lane world contains 4,608 prefill tokens,
240 decode tokens, six tool calls and 6 s of work, truth 1,161 J.
The phase-count chain PowerTrace -> estimate_energy -> Episode JSON round
trip gives J=966 / 1144.5 / 1161 / 1161 / 1161 at 1/2/4/8/16 repeats;
coverage=.25/.5/1/1/1. Eight and sixteen replays have .003 J width.
Unreplicated envelopes are intentionally wide and flagged.

The real fake-driver C ABI -> NvmlSampler worker -> PowerTrace -> duty
estimate -> Episode JSON round trip prints:
```text
NVML DRIVER END-TO-END {"truth_j": 1161.0, "joules": 1160.999993675, "half_width_j": 0.07239349997261459, "coverage": 0.9999999916666666, "repeats": 8, "samples_per_run": [60, 60, 60, 60, 60, 60, 60, 60]}
```

New 400-seed regressions (times from final with-twin discovery):
```text
NVML R2 SHORT CALIBRATION {"sigma_w": 0.0, "seeds": 400, "misses": 0, "fraction": 0.0, "one_sided_ceiling": 0.0935889894354068, "median_abs_error_j": 0.8638681444796958, "median_half_width_j": 1.7815683509067484, "elapsed_s": 6.6756461069999204}
```
```text
NVML R2 SHORT CALIBRATION {"sigma_w": 0.5, "seeds": 400, "misses": 0, "fraction": 0.0, "one_sided_ceiling": 0.0935889894354068, "median_abs_error_j": 0.8240673091173107, "median_half_width_j": 2.5824302897721676, "elapsed_s": 13.9955227559999}
```
```text
NVML R2 DURATION CALIBRATION {"seeds": 400, "misses": 0, "fraction": 0.0, "one_sided_ceiling": 0.0935889894354068, "nearer_mean": 400, "median_error_j": -0.7064764419320397, "median_half_width_j": 5.653932600936214, "elapsed_s": 17.30751301800001}
```

The short cases use 100-300 ms of 300-380 W prefill, .5-2.5 s of
200-240 W decode with 5-25 W/7 Hz ripple in 1 ms bins, a decode-to-55 W
idle ending, 8 labelled phases, .3 W reading noise and 0-1 ms dispatch
jitter. The ending step is large enough to expose the old boundary omission.
The duration regression uses that same waveform, 16 runs, 2 W shifts and
+/-50 ms durations. Only the waveform is shortened from the reviewer's
two-turn case. It chooses mean truth rather than longest truth in 400/400
seeds. Truth uses the mean of each run's shift-free own-duration integral.

Reviewer calibration results; medians are statistics.median, joules.
The lead's 400-seed one-sided ceiling is .0935889894; its two-sided
spread band is [.0064110106,.0935889894]. Every lane inf count is zero.

| World | Lane misses/S | Twin misses/S | Lane median abs err / hw | Twin median abs err / hw | Runtime (s) |
|---|---:|---:|---:|---:|---:|
| short 0.0 400 | 0/400 | 9/400 | 0.863868 / 1.781568 | 1.121555 / 3.879970 | 38.443 |
| short 0.2 400 | 0/400 | 6/400 | 0.850059 / 1.914466 | 1.113435 / 3.887289 | 21.971 |
| short 0.5 400 | 0/400 | 7/400 | 0.824067 / 2.582430 | 1.159188 / 3.946587 | 38.737 |
| short 2.0 400 | 0/400 | 8/400 | 1.004145 / 5.697770 | 1.320205 / 4.704921 | 22.164 |
| long 0.0 400 | 0/400 | 1/400 | 0.821741 / 4.815338 | 3.151068 / 14.149932 | 1090.751 |
| probe5 aligned, no labels | 14/400 | 13/400 | 5.670990 / 18.711714 | 5.670990 / 18.206670 | 1072.290 |
| probe5 aligned, labels | 14/400 | 13/400 | 5.670990 / 18.711714 | 5.670990 / 18.206670 | 972.075 |
| probe5 100us, labels | 11/400 | 15/400 | 5.652967 / 18.933586 | 5.652967 / 18.266829 | 927.663 |

All short/long cases pass the one-sided bar. All three probe5 cases pass
the TWO-SIDED bar, preserving F5 when 2 W run spread dominates.

The unchanged lane F5 cases give 17/11/10/4 misses in 400 (aligned /100 us/
2 ms/2 ms plus durations); both 0 and 400 misses would fail their bar.
Its paired medians, plus the new duration and original 1000-seed worlds:

| Lane world | Seeds | Lane misses | Twin misses | Lane median abs err / hw | Twin median abs err / hw | Paired-calculation runtime (s) |
|---|---:|---:|---:|---:|---:|---:|
| UNIT DURATION | 400 | 0 | 110 | 0.840312 / 5.653933 | 5.044953 / 8.722344 | 40.632 |
| UNIT F5 aligned | 400 | 17 | 20 | 1.295487 / 4.100429 | 1.295487 / 3.781867 | 36.458 |
| UNIT F5 100us | 400 | 11 | 16 | 1.173597 / 4.199227 | 1.179601 / 3.905752 | 58.436 |
| UNIT F5 2ms | 400 | 10 | 13 | 1.180060 / 4.561116 | 1.199963 / 3.918661 | 34.840 |
| UNIT F5 2ms_duration300us | 400 | 4 | 14 | 1.249053 / 4.607183 | 1.287545 / 4.040360 | 63.429 |
| UNIT ORIGINAL 1000 | 1000 | 52 | 0 | 0.986437 / 2.995582 | 0.986438 / 33.356023 | 307.481 |

Reviewer duration levels all pass the fixed m<=9 of 60 bar.
The script's upper-middle signed median errors are -.40/-.78/-.69/-.48 J
at +/- .3/5/20/50 ms; before they rose to +8.19 J at +/-50 ms.
The paired medians use the usual middle-pair average:

| Jitter ms | Lane misses | Twin misses | Lane median signed error | Lane median abs err / hw | Twin median abs err / hw |
|---|---:|---:|---:|---:|---:|
| 0.3 | 4/60 | 2/60 | -0.428549 | 3.159592 / 11.171769 | 3.195998 / 10.697510 |
| 5 | 3/60 | 2/60 | -0.782584 | 3.273186 / 10.532951 | 3.408383 / 10.859420 |
| 20 | 1/60 | 1/60 | -0.705728 | 2.541575 / 11.320290 | 3.183849 / 13.177409 |
| 50 | 0/60 | 2/60 | -0.537574 | 2.867381 / 12.459920 | 5.593592 / 15.981457 |

Duration-script runtime: 291.241 s.

```text
mean-run truth 1777.201 J; lane 1776.440 +- 6.057 (err -0.761); twin 1780.486 +- 18.012 (err +3.285)
predicted tail bias (maxD-meanD)*p_end = 12.133 J; maxD-meanD = 58.8 ms, p_end 206.3 W
longest-run truth 1789.509140778557 lane flags ['duration_spread_ns=96377661', 'durations_differ']
```
The tail point changes from 1788.389 J (error +11.188 J) to
1776.440 J (error -.761 J), a -11.949 J correction, closer to mean
1777.201 J than longest 1789.509 J. Its final width is 6.057 J
(previous 4.507 J, +1.550 J).

probe1 retains finite containment in all four cases; lane/twin widths
are printed beside each other. The before lane widths were
.0134/.0637/1.317/2.628 J; the final widths are
1.1186/1.1893/2.7596/27.2021 J. The first three deterministic errors
that previously escaped are now covered.
```text
D s 26.740136002 truth J 5193.186095130263
lane offsets [0, 25000000, 50000000, 75000000, 0, 25000000, 50000000, 75000000] twin [0, 12500000, 25000000, 37500000, 50000000, 62500000, 75000000, 87500000]

exact: truth(mean over runs) 5193.1861
  lane  J=5192.0792 err=-1.1068 hw=1.1186 cov=1.000000 flags=('auxiliary_center_bound_j=0.0', 'boundary_bound_j=1.1052013192781416', 'boundary_end_range_w=185.062', 'boundary_observed_range_assumed', 'boundary_start_range_w=297.075', 'coverage_bound_j=0.0', 'coverage_smoothing_or_timing_bound', 'declared_phase_groups_auxiliary_interval', 'deterministic_workload_assumed', 'nominal_95pct_gaussian_repeatability_plus_observed_range_bounds', 'observed_range_bounds_assumed', 'observed_reading_range_w=297.075', 'outside_idle_baseline_assumed', 'repeatability_half_width_j=0.0', 'repeatability_interval_provisional', 'resolution_bound_j=0.013370068001000001', 'runs_retained=8', 'sensor_accuracy_not_included', 'timing_bound_j=0.0', 'unreplicated_phase_bound_j=0.0', 'worst_case_bias_j=2.687426882207928')
  twin  J=5192.0792 err=-1.1068 hw=11.4466 cov=1.000000 flags=()

dur_jitter: truth(mean over runs) 5193.1913
  lane  J=5192.0806 err=-1.1106 hw=1.1893 cov=0.999999 flags=('auxiliary_center_bound_j=7.490780262742192e-08', 'boundary_bound_j=1.1087291929270622', 'boundary_end_range_w=185.062', 'boundary_observed_range_assumed', 'boundary_start_range_w=297.075', 'coverage_bound_j=0.0050239838624999995', 'coverage_smoothing_or_timing_bound', 'declared_phase_groups_auxiliary_interval', 'deterministic_workload_assumed', 'duration_spread_ns=211143', 'durations_differ', 'nominal_95pct_gaussian_repeatability_plus_observed_range_bounds', 'observed_range_bounds_assumed', 'observed_reading_range_w=297.075', 'outside_idle_baseline_assumed', 'partial_coverage', 'repeatability_half_width_j=0.06221501810208058', 'repeatability_interval_provisional', 'resolution_bound_j=0.0133700793930625', 'runs_retained=8', 'sensor_accuracy_not_included', 'timing_bound_j=0.0', 'unreplicated_phase_bound_j=0.0', 'worst_case_bias_j=2.6767693706591307')
  twin  J=5192.0838 err=-1.1075 hw=11.4721 cov=0.999998 flags=('durations_differ', 'incomplete_coverage')

start_jitter: truth(mean over runs) 5193.1861
  lane  J=5191.7341 err=-1.4519 hw=2.7596 cov=1.000000 flags=('auxiliary_center_bound_j=0.0008586541707700235', 'boundary_bound_j=1.4421465723998692', 'boundary_end_range_w=185.09300000000002', 'boundary_observed_range_assumed', 'boundary_start_range_w=297.075', 'coverage_bound_j=0.0', 'coverage_smoothing_or_timing_bound', 'declared_phase_groups_auxiliary_interval', 'deterministic_workload_assumed', 'nominal_95pct_gaussian_repeatability_plus_observed_range_bounds', 'observed_range_bounds_assumed', 'observed_reading_range_w=297.075', 'outside_idle_baseline_assumed', 'phase_geometry_varies', 'repeatability_half_width_j=1.3031759062940644', 'repeatability_interval_provisional', 'resolution_bound_j=0.013370068001000001', 'runs_retained=8', 'sensor_accuracy_not_included', 'timing_bound_j=0.0', 'unreplicated_phase_bound_j=0.0', 'worst_case_bias_j=170.61493744736384')
  twin  J=5191.7341 err=-1.4519 hw=11.2376 cov=1.000000 flags=()

both: truth(mean over runs) 5193.1987
  lane  J=5191.7946 err=-1.4041 hw=27.2021 cov=0.997095 flags=('auxiliary_center_bound_j=0.00651174911945418', 'boundary_bound_j=1.4954687518340317', 'boundary_end_range_w=185.09300000000002', 'boundary_observed_range_assumed', 'boundary_start_range_w=297.075', 'coverage_bound_j=23.078797383421875', 'coverage_smoothing_or_timing_bound', 'declared_phase_groups_auxiliary_interval', 'deterministic_workload_assumed', 'duration_spread_ns=233424', 'durations_differ', 'nominal_95pct_gaussian_repeatability_plus_observed_range_bounds', 'observed_range_bounds_assumed', 'observed_reading_range_w=297.075', 'outside_idle_baseline_assumed', 'partial_coverage', 'phase_geometry_varies', 'repeatability_half_width_j=2.6079791067247435', 'repeatability_interval_provisional', 'resolution_bound_j=0.013370095778875001', 'runs_retained=8', 'sensor_accuracy_not_included', 'timing_bound_j=0.0', 'unreplicated_phase_bound_j=0.0', 'worst_case_bias_j=218.76344256419046')
  twin  J=5176.7162 err=-16.4825 hw=38.5573 cov=0.997093 flags=('durations_differ', 'incomplete_coverage')
```

probe10 retains min/mean/max lag .000 ms. Its lane width increases
from .005 to 1.477 J (about +1.472 J), covering error -1.060 J.
The real-sampler agreement world gives lane1709.260019717 +/-1.317163515 J,
twin1709.260019717 +/-5.641692205 J, truth1710.239856769 J.
The old lane width was .0043 J; the new width adds about1.3129 J.

A100 legacy power_usage now has infinite width and the explicit
sensor_window_time_unknown flag; power_instant stays finite and covers
truth. Full required timestamp/channel outputs:
```text
t_ns minus sensor window end: min 0.000 ms, mean 0.000 ms, max 0.000 ms
truth 1916.969 J | lane (reads notes) 1915.910 +- 1.477 | contract reader (twin, reads t_ns) 1915.910 +- 6.903
contract reader on t_ns = window end: 1915.910 +- 6.903
power_instant: samples/run 109 truth 1916.969 J
   lane 1915.910 +- 1.477 cov 1.0000 err -1.060
   flags ['auxiliary_center_bound_j=0.0', 'boundary_bound_j=1.13629726632741', 'boundary_end_range_w=192.825', 'boundary_observed_range_assumed', 'boundary_start_range_w=297.075', 'coverage_bound_j=0.0', 'coverage_smoothing_or_timing_bound', 'declared_phase_groups_auxiliary_interval', 'deterministic_workload_assumed', 'nominal_95pct_gaussian_repeatability_plus_observed_range_bounds', 'observed_range_bounds_assumed', 'observed_reading_range_w=297.075', 'outside_idle_baseline_assumed', 'repeatability_half_width_j=0.0', 'repeatability_interval_provisional', 'resolution_bound_j=0.005104755856', 'runs_retained=8', 'sensor_accuracy_not_included', 'timing_bound_j=0.33560128088316676', 'unreplicated_phase_bound_j=0.0', 'worst_case_bias_j=3.1601441273070963']
   twin 1915.910 +- 6.903; trace flags ['driver_field_timestamp_is_wall_clock', 'resolution_is_quantum_not_accuracy']
power_usage: samples/run 1100 truth 1916.969 J
   lane 1908.960 +- inf cov 1.0000 err -8.009
   flags ['auxiliary_center_bound_j=0.0', 'boundary_bound_j=1.6090701501290612', 'boundary_end_range_w=122.88900000000001', 'boundary_observed_range_assumed', 'boundary_start_range_w=297.075', 'coverage_bound_j=0.0', 'coverage_smoothing_or_timing_bound', 'declared_phase_groups_auxiliary_interval', 'deterministic_workload_assumed', 'nominal_95pct_gaussian_repeatability_plus_observed_range_bounds', 'observed_range_bounds_assumed', 'observed_reading_range_w=297.075', 'outside_idle_baseline_assumed', 'repeatability_half_width_j=0.0', 'repeatability_interval_provisional', 'resolution_bound_j=0.005104755856000001', 'runs_retained=8', 'sensor_accuracy_not_included', 'sensor_window_time_unknown', 'timing_bound_j=3032.9906918424', 'unreplicated_phase_bound_j=0.0', 'worst_case_bias_j=inf']
   twin 1908.960 +- 11.44; trace flags ['resolution_is_quantum_not_accuracy', 'sensor_age_unknown', 'sensor_update_phase_unreported']
```

Full probe7 before/after outputs follow. The before run executes the
432f14c7a reducer source in an isolated module over the same supplied
world and unchanged records. No row raises after the fix; every
positive-coverage row contains truth and all eight explicitly required
rows have finite widths. Unknown window/empty/counter/zero-duration rows
remain flagged no-coverage outputs. Large values/dropouts are retained.

BEFORE:
```text
baseline 8 runs                               J=  1778.643 (truth 1779.580) hw=   0.00437 cov=1.0000 flags=['coverage_smoothing_or_timing_bound', 'runs_retained=8', 'worst_case_bias_j=2.628431395821198']
empty runs                                    J=     0.000 (truth 1779.580) hw=       inf cov=0.0000 flags=['no_covered_work', 'runs_retained=0']
one run                                       J=  1766.240 (truth 1779.580) hw=       inf cov=0.2488 flags=['coverage_smoothing_or_timing_bound', 'partial_coverage', 'phase_without_replicates', 'runs_retained=1', 'worst_case_bias_j=2954.56401765']
every trace starts 1.3 s after workload       J=  1715.960 (truth 1779.580) hw=   0.00437 cov=0.8513 flags=['coverage_smoothing_or_timing_bound', 'partial_coverage', 'runs_retained=8', 'worst_case_bias_j=586.8534688489942']
empty trace (failed sampler) + 8 runs         J=  1778.643 (truth 1779.580) hw=   0.00437 cov=1.0000 flags=['coverage_smoothing_or_timing_bound', 'mixed_clock_domains', 'run_without_coverage', 'runs_retained=8', 'timing_uncertainty_unreported', 'worst_case_bias_j=2.628431395821198']
8 identical copies of one run                 J=  1766.240 (truth 1779.580) hw=   0.00437 cov=0.2488 flags=['coverage_smoothing_or_timing_bound', 'partial_coverage', 'runs_retained=8', 'worst_case_bias_j=2954.56401765']
unknown sensor facts (window None)            J=     0.000 (truth 1779.580) hw=       inf cov=0.0000 flags=['invalid_or_unknown_sensor_run', 'no_covered_work', 'runs_retained=0']
window known, duty None                       J=  1778.643 (truth 1779.580) hw=   0.00437 cov=1.0000 flags=['coverage_smoothing_or_timing_bound', 'runs_retained=8', 'sensor_duty_unknown', 'worst_case_bias_j=2.628431395821198']
one reading 1e6 W (power bound 450)           J=  1778.643 (truth 1779.580) hw=   0.00437 cov=1.0000 flags=['coverage_smoothing_or_timing_bound', 'runs_retained=8', 'worst_case_bias_j=2.628431395821198']
energy-counter trace                          J=     0.000 (truth 1779.580) hw=       inf cov=0.0000 flags=['invalid_or_unknown_sensor_run', 'no_covered_work', 'runs_retained=0']
end == start                                  J=     0.000 (truth 1779.580) hw=       inf cov=0.0000 flags=['invalid_or_unknown_sensor_run', 'no_covered_work', 'runs_retained=0']
mixed channels                                J=  1778.643 (truth 1779.580) hw=   0.00437 cov=1.0000 flags=['coverage_smoothing_or_timing_bound', 'mixed_channels', 'runs_retained=8', 'worst_case_bias_j=2.628431395821198']
no power_bound_w (sampler default)            J=  1778.643 (truth 1779.580) hw=   0.00437 cov=1.0000 flags=['coverage_smoothing_or_timing_bound', 'runs_retained=8', 'worst_case_bias_j=inf', 'worst_case_bias_unbounded']
plain-text notes                              J=  1778.643 (truth 1779.580) hw=   0.00437 cov=1.0000 flags=['coverage_smoothing_or_timing_bound', 'runs_retained=8', 'timing_uncertainty_unreported', 'worst_case_bias_j=inf', 'worst_case_bias_unbounded']
mid-workload reading 1e6 W (bound 450)        J= 14277.578 (truth 1779.580) hw= 1.588e+05 cov=1.0000 flags=['coverage_smoothing_or_timing_bound', 'power_bound_violated', 'runs_retained=8', 'worst_case_bias_j=inf', 'worst_case_bias_unbounded']
mid-workload reading 0 W (dropout)            J=  1777.578 (truth 1779.580) hw=     13.54 cov=1.0000 flags=['coverage_smoothing_or_timing_bound', 'runs_retained=8', 'worst_case_bias_j=2.628431395821198']
```

AFTER:
```text
baseline 8 runs                               J=  1778.643 (truth 1779.580) hw=    0.9559 cov=1.0000 flags=['auxiliary_center_bound_j=0.0', 'boundary_bound_j=0.9514980062459311', 'boundary_end_range_w=162.901', 'boundary_observed_range_assumed', 'boundary_start_range_w=273.683', 'coverage_bound_j=0.0', 'coverage_smoothing_or_timing_bound', 'nominal_95pct_gaussian_repeatability_plus_observed_range_bounds', 'observed_range_bounds_assumed', 'observed_reading_range_w=273.683', 'outside_idle_baseline_assumed', 'repeatability_half_width_j=0.0', 'resolution_bound_j=0.0043703489085000005', 'runs_retained=8', 'timing_bound_j=0.0', 'unreplicated_phase_bound_j=0.0', 'worst_case_bias_j=2.628431395821198']
empty runs                                    J=     0.000 (truth 1779.580) hw=       inf cov=0.0000 flags=['no_covered_work', 'nominal_95pct_gaussian_repeatability_plus_observed_range_bounds', 'observed_range_bounds_assumed', 'runs_retained=0']
one run                                       J=  1766.240 (truth 1779.580) hw=      4189 cov=0.2488 flags=['auxiliary_center_bound_j=0.0', 'boundary_bound_j=0.0', 'boundary_end_range_w=160.99200000000002', 'boundary_observed_range_assumed', 'boundary_start_range_w=273.683', 'coverage_bound_j=1796.919875650011', 'coverage_smoothing_or_timing_bound', 'nominal_95pct_gaussian_repeatability_plus_observed_range_bounds', 'observed_range_bounds_assumed', 'observed_reading_range_w=273.683', 'outside_idle_baseline_assumed', 'partial_coverage', 'phase_without_replicates', 'repeatability_half_width_j=0.0', 'resolution_bound_j=0.0043703489085000005', 'runs_retained=1', 'timing_bound_j=0.0', 'unreplicated_phase_bound_j=2392.1804006500106', 'unreplicated_phase_observed_range_assumed', 'worst_case_bias_j=2954.56401765']
every trace starts 1.3 s after workload       J=  1715.960 (truth 1779.580) hw=       325 cov=0.8513 flags=['auxiliary_center_bound_j=0.0', 'boundary_bound_j=1.1177387861488075', 'boundary_end_range_w=162.901', 'boundary_observed_range_assumed', 'boundary_range_fallback_global', 'boundary_start_range_w=249.14800000000002', 'coverage_bound_j=323.89240000000007', 'coverage_smoothing_or_timing_bound', 'nominal_95pct_gaussian_repeatability_plus_observed_range_bounds', 'observed_range_bounds_assumed', 'observed_reading_range_w=249.14800000000002', 'outside_idle_baseline_assumed', 'partial_coverage', 'repeatability_half_width_j=0.0', 'resolution_bound_j=0.0043703489085', 'runs_retained=8', 'timing_bound_j=0.0', 'unreplicated_phase_bound_j=0.0', 'worst_case_bias_j=586.8534688489942']
empty trace (failed sampler) + 8 runs         J=  1778.643 (truth 1779.580) hw=    0.9559 cov=1.0000 flags=['auxiliary_center_bound_j=0.0', 'boundary_bound_j=0.9514980062459311', 'boundary_end_range_w=162.901', 'boundary_observed_range_assumed', 'boundary_start_range_w=273.683', 'coverage_bound_j=0.0', 'coverage_smoothing_or_timing_bound', 'mixed_clock_domains', 'nominal_95pct_gaussian_repeatability_plus_observed_range_bounds', 'observed_range_bounds_assumed', 'observed_reading_range_w=273.683', 'outside_idle_baseline_assumed', 'repeatability_half_width_j=0.0', 'resolution_bound_j=0.0043703489085000005', 'run_without_coverage', 'runs_retained=8', 'timing_bound_j=0.0', 'timing_uncertainty_unreported', 'unreplicated_phase_bound_j=0.0', 'worst_case_bias_j=2.628431395821198']
8 identical copies of one run                 J=  1766.240 (truth 1779.580) hw=      1797 cov=0.2488 flags=['auxiliary_center_bound_j=0.0', 'boundary_bound_j=0.0', 'boundary_end_range_w=160.99200000000002', 'boundary_observed_range_assumed', 'boundary_start_range_w=273.683', 'coverage_bound_j=1796.919875650011', 'coverage_smoothing_or_timing_bound', 'nominal_95pct_gaussian_repeatability_plus_observed_range_bounds', 'observed_range_bounds_assumed', 'observed_reading_range_w=273.683', 'outside_idle_baseline_assumed', 'partial_coverage', 'repeatability_half_width_j=0.0', 'resolution_bound_j=0.0043703489085000005', 'runs_retained=8', 'timing_bound_j=0.0', 'unreplicated_phase_bound_j=0.0', 'worst_case_bias_j=2954.56401765']
unknown sensor facts (window None)            J=     0.000 (truth 1779.580) hw=       inf cov=0.0000 flags=['invalid_or_unknown_sensor_run', 'no_covered_work', 'nominal_95pct_gaussian_repeatability_plus_observed_range_bounds', 'observed_range_bounds_assumed', 'runs_retained=0']
window known, duty None                       J=  1778.643 (truth 1779.580) hw=    0.9559 cov=1.0000 flags=['auxiliary_center_bound_j=0.0', 'boundary_bound_j=0.9514980062459311', 'boundary_end_range_w=162.901', 'boundary_observed_range_assumed', 'boundary_start_range_w=273.683', 'coverage_bound_j=0.0', 'coverage_smoothing_or_timing_bound', 'nominal_95pct_gaussian_repeatability_plus_observed_range_bounds', 'observed_range_bounds_assumed', 'observed_reading_range_w=273.683', 'outside_idle_baseline_assumed', 'repeatability_half_width_j=0.0', 'resolution_bound_j=0.0043703489085000005', 'runs_retained=8', 'sensor_duty_unknown', 'timing_bound_j=0.0', 'unreplicated_phase_bound_j=0.0', 'worst_case_bias_j=2.628431395821198']
one reading 1e6 W (power bound 450)           J=  1778.643 (truth 1779.580) hw=    0.9559 cov=1.0000 flags=['auxiliary_center_bound_j=0.0', 'boundary_bound_j=0.9514980062459311', 'boundary_end_range_w=162.901', 'boundary_observed_range_assumed', 'boundary_start_range_w=273.683', 'coverage_bound_j=0.0', 'coverage_smoothing_or_timing_bound', 'nominal_95pct_gaussian_repeatability_plus_observed_range_bounds', 'observed_range_bounds_assumed', 'observed_reading_range_w=999945.0', 'outside_idle_baseline_assumed', 'repeatability_half_width_j=0.0', 'resolution_bound_j=0.0043703489085000005', 'runs_retained=8', 'timing_bound_j=0.0', 'unreplicated_phase_bound_j=0.0', 'worst_case_bias_j=2.628431395821198']
energy-counter trace                          J=     0.000 (truth 1779.580) hw=       inf cov=0.0000 flags=['invalid_or_unknown_sensor_run', 'no_covered_work', 'nominal_95pct_gaussian_repeatability_plus_observed_range_bounds', 'observed_range_bounds_assumed', 'runs_retained=0']
end == start                                  J=     0.000 (truth 1779.580) hw=       inf cov=0.0000 flags=['invalid_or_unknown_sensor_run', 'no_covered_work', 'nominal_95pct_gaussian_repeatability_plus_observed_range_bounds', 'observed_range_bounds_assumed', 'runs_retained=0']
mixed channels                                J=  1778.643 (truth 1779.580) hw=    0.9559 cov=1.0000 flags=['auxiliary_center_bound_j=0.0', 'boundary_bound_j=0.9514980062459311', 'boundary_end_range_w=162.901', 'boundary_observed_range_assumed', 'boundary_start_range_w=273.683', 'coverage_bound_j=0.0', 'coverage_smoothing_or_timing_bound', 'mixed_channels', 'nominal_95pct_gaussian_repeatability_plus_observed_range_bounds', 'observed_range_bounds_assumed', 'observed_reading_range_w=273.683', 'outside_idle_baseline_assumed', 'repeatability_half_width_j=0.0', 'resolution_bound_j=0.0043703489085000005', 'runs_retained=8', 'timing_bound_j=0.0', 'unreplicated_phase_bound_j=0.0', 'worst_case_bias_j=2.628431395821198']
no power_bound_w (sampler default)            J=  1778.643 (truth 1779.580) hw=    0.9559 cov=1.0000 flags=['auxiliary_center_bound_j=0.0', 'boundary_bound_j=0.9514980062459311', 'boundary_end_range_w=162.901', 'boundary_observed_range_assumed', 'boundary_start_range_w=273.683', 'coverage_bound_j=0.0', 'coverage_smoothing_or_timing_bound', 'nominal_95pct_gaussian_repeatability_plus_observed_range_bounds', 'observed_range_bounds_assumed', 'observed_reading_range_w=273.683', 'outside_idle_baseline_assumed', 'repeatability_half_width_j=0.0', 'resolution_bound_j=0.0043703489085000005', 'runs_retained=8', 'timing_bound_j=0.0', 'unreplicated_phase_bound_j=0.0', 'worst_case_bias_j=inf', 'worst_case_bias_unbounded']
plain-text notes                              J=  1778.643 (truth 1779.580) hw=    0.9559 cov=1.0000 flags=['auxiliary_center_bound_j=0.0', 'boundary_bound_j=0.9514980062459311', 'boundary_end_range_w=162.901', 'boundary_observed_range_assumed', 'boundary_start_range_w=273.683', 'coverage_bound_j=0.0', 'coverage_smoothing_or_timing_bound', 'nominal_95pct_gaussian_repeatability_plus_observed_range_bounds', 'observed_range_bounds_assumed', 'observed_reading_range_w=273.683', 'outside_idle_baseline_assumed', 'repeatability_half_width_j=0.0', 'resolution_bound_j=0.0043703489085000005', 'runs_retained=8', 'timing_bound_j=0.0', 'timing_uncertainty_unreported', 'unreplicated_phase_bound_j=0.0', 'worst_case_bias_j=inf', 'worst_case_bias_unbounded']
mid-workload reading 1e6 W (bound 450)        J= 14277.578 (truth 1779.580) hw= 1.588e+05 cov=1.0000 flags=['auxiliary_center_bound_j=0.0', 'boundary_bound_j=0.9514980062459311', 'boundary_end_range_w=162.901', 'boundary_observed_range_assumed', 'boundary_start_range_w=273.683', 'coverage_bound_j=0.0', 'coverage_smoothing_or_timing_bound', 'nominal_95pct_gaussian_repeatability_plus_observed_range_bounds', 'observed_range_bounds_assumed', 'observed_reading_range_w=999945.0', 'outside_idle_baseline_assumed', 'power_bound_violated', 'repeatability_half_width_j=158814.02550542573', 'resolution_bound_j=0.0043703489085000005', 'runs_retained=8', 'timing_bound_j=0.0', 'unreplicated_phase_bound_j=0.0', 'worst_case_bias_j=inf', 'worst_case_bias_unbounded']
mid-workload reading 0 W (dropout)            J=  1777.578 (truth 1779.580) hw=     14.49 cov=1.0000 flags=['auxiliary_center_bound_j=0.0', 'boundary_bound_j=0.9514980062459311', 'boundary_end_range_w=162.901', 'boundary_observed_range_assumed', 'boundary_start_range_w=273.683', 'coverage_bound_j=0.0', 'coverage_smoothing_or_timing_bound', 'nominal_95pct_gaussian_repeatability_plus_observed_range_bounds', 'observed_range_bounds_assumed', 'observed_reading_range_w=328.683', 'outside_idle_baseline_assumed', 'repeatability_half_width_j=13.533696319580706', 'resolution_bound_j=0.0043703489085000005', 'runs_retained=8', 'timing_bound_j=0.0', 'unreplicated_phase_bound_j=0.0', 'worst_case_bias_j=2.628431395821198']
```

The real preflight worker/executable load and no-load controls pass; the
1000-seed predictive noise criterion fires54/1000, inside its nominal
.05 +/- four-binomial-SE bar. No GPU, rented host, paid service or live
sensor was used. Sensor quantum is never called calibration accuracy.

## DECISIONS I MADE

- Continued from the existing 432f14c7a lane head, read its report first,
  then PIPELINE.md, records.py, interfaces.py and the NVIDIA parser.
  ACTIVE_STOP_CARD was NONE; TASK_QUEUE.md is empty on this branch.
  Read M0/orchestration. The explicit scope overrides lead-owned queue,
  kernel and whole-repository-suite instructions.
- Committed the pre-code derivation in b0b02acc2a0374e065317aaafaf0bd2e38550056.
  The original global bound was (M-C)*R for coverage,
  sum(d_i*outside_fraction_i)*R for boundary and
  sum(d_i*min(h_i/w_i,1))*R for timing. These follow respectively from
  extrapolated covered/missing mean contrast, whole/inside window-mean
  contamination and the replaced fraction of a translated sensor window.
  Bounds add linearly to 95% Welch spread, quantum and auxiliary-center
  displacement; no term needs a power_bound_w.
- Worked R2-B1(a) by hand before coding: D8.034s*(1-.8413)=1.275s missing;
  80.08J/1.275s=62.81W required contrast. An observed64W range already
  gives81.6J coverage bound. The executed range293.738W gives374.51595J.
  The range is the max minus min of valid readings in retained traces,
  including pre/post-roll. It is conditional on unobserved power staying
  in that range, explicitly flagged.
- The global boundary candidate passed aligned F5 (7/400) but failed
  unchanged100us F5 (2/400, below3); it used a350-to-55W range for a
 75-to-55W end step. Recorded a local derivation BEFORE implementing it.
  The nearest-only local candidate passed F5 but probe1 exact missed
  narrowly (1.1068J error >1.1000J width), since one inside reading does
  not represent its local temporal variation.
- Final boundary data: use both endpoints of each run's nearest fully
  inside sample interval (two is its structural endpoint count) and the
  nearest fully outside idle-baseline reading. Pool their observed range
  at each boundary; assume the inside/outside contrast stays within it
  and outside remains at the observed idle baseline. Missing either
  evidence falls back to globalR. A window straddling both boundaries
  uses the larger range. No radius, fitted multiplier, chosen confidence,
  seed count or test bar was tuned. The pre-implementation refinements
  and receipts are preserved in8d8900cdf, d0fce9251 and d391ece3e.
- Physical hand witness: a25ms window containing15ms at75W and10ms at55W
  reads67W. Clipping causes (75-67)*.015=.120 J,
  equivalently .015*(10/25)*(75-55)=.120J. The unrelated350W prefill gives
  a global1.770J bound. The new oracle world verifies .120+.000095J.
- R2-M2 estimand is mean run energy. Weight every aligned span by
  active-runs/n so coefficient mass is meanD, not maxD; scale by M/C.
  Duration spread stays in the unchanged phase-normalized run variance.
- Unknown sensor age is not a known timing bracket. A coarse maximum age
  cannot identify a window end: choose infinite width and a flag.
  Per-sample notes isolate contributing unknowns from outside observations.
- Property2 requires finite known-age positive-coverage intervals even
  without B. Unreplicated phases cannot identify a variance, but receive
  a conditional group-mass times observed-range center-error envelope and
  explicit flags. R1 F10's identification point still stands; eight
  replays identify four phases' within-phase spread, four do not.
- Under-tiled plans warn rather than raise, preserving useful incomplete
  data with partial_coverage and its bound. Minimumceil(1/d) is explicit
  in docstring and runbook. Invalid arguments still return an empty plan.
- Used GitHub leased fast-forwards while the shell was unavailable.
  After startup, used the required local checkout and pre-push fetches.
  The remote never advanced beyond our preceding commits; no merge or
  rewritten pushed history occurred. No merged commits need naming.
- N1-N6 remain unchanged. N7 uses1% of the finite printed half-width.
  The original F5 test body is byte-identical, all calibration seed
  counts/bars remain the lead's, and no skip/expected failure was added.
- The external twin source remains unchanged. Its max-D defect is routed
  in OPEN ISSUES. Only local uncommitted agreement tests adopt the new
  estimand reference; the in-scope lane oracle follows R2 independently.
- No physical measurement, network test, credential, service message,
  paid resource, sub-agent or independent-review completion is claimed.

## CONTRACT-CHANGE

none. The shared records contract wins: known sensor-window ends remain
t_ns, while query midpoints and uncertainties stay in notes. All new
quantities are numeric flag strings in the unchanged four-field
DutyEstimate. The three protected files are unchanged.

## OPEN ISSUES

- The external twin still integrates to maxD at full weight. R2-M2
  requires active-run weighting and mean-duration coverage. Route that
  algorithm defect to the twin author; its duration-world medians above
  disclose the remaining bias. Its source is unchanged here.
- The local twin-test diff below removes the two R2 expectedFailure
  decorators and replaces the duration-varying comparison target with an
  independent span-weighted reference using the twin's pooling helper.
  All comparison bars and all seeds remain unchanged. It also adds
  truth containment to the sampler-chain test. All 36 tests pass with it.
  The sole observed old-rule failure was jittered replay coverage.
  Resolution, single-phase spread and equal-duration gap tests need no diff.
- Bounds are conditional on observed global/local ranges and an outside
  idle baseline. Window averages do not prove instantaneous power stays
  in those ranges. The unreplicated envelope is not a statistically
  identified 95% repeatability interval. Preserve every assumption/diagnostic flag.
- No live sensor accuracy, timing semantics, Gaussian model, duty behavior,
  GPU isolation or hardware load response is validated by synthetic tests.
- PR #524 remains draft. Main integration, independent executing review,
  final-head green CI and cold measurement gates remain lead-owned.
  No required local acceptance repro remains unexecuted.

Twin-test diff (local-only, never staged/committed as a twin file):
```diff
--- a/tests/align/test_twin_nvml.py
+++ b/tests/align/test_twin_nvml.py
@@ -169,6 +169,24 @@
     return REL * max(abs(a.joules), abs(b.joules))


+def mean_run_pooled_reference(runs: list[tuple[PowerTrace, int, int]]) -> tuple[float, float]:
+    """Direct span reference for R2-M2; the external twin still targets max D."""
+    durations = [end-start for _, start, end in runs]
+    windows = [item for trace, start, end in runs for item in twin.sample_windows(
+        trace.t_ns, trace.values, trace.averaging_window_ns, start, end)]
+    cuts = sorted({0, *durations})
+    energy_parts, covered_parts = [], []
+    for left, right in zip(cuts, cuts[1:]):
+        clipped = [(max(a, left), min(b, right), watts) for a, b, watts in windows
+                   if max(a, left) < min(b, right)]
+        integral, covered = twin.pooled_integral(clipped)
+        active_fraction = sum(duration > left for duration in durations)/len(durations)
+        energy_parts.append(active_fraction*integral)
+        covered_parts.append(active_fraction*covered)
+    mean_duration = math.fsum(durations)/len(durations)
+    return math.fsum(energy_parts)/1e9, math.fsum(covered_parts)/mean_duration
+
+
 def tiles(offsets: list[int], period: int, window: int) -> bool:
     """True when windows [o, o + window) mod period cover the whole period (integers)."""
     starts = sorted({o % period for o in offsets})
@@ -182,13 +200,18 @@
     def assert_agree(self, runs: list[tuple[PowerTrace, int, int]], context: object) -> tuple:
         a, b = lane.estimate_energy(runs), twin.estimate_energy(runs)
         context = (context, a, b)
-        self.assertLessEqual(abs(a.coverage_fraction - b.coverage_fraction), COVERAGE_ABS, context)
+        if len({end-start for _, start, end in runs}) > 1:
+            # R2-M2 changes the lane's estimand. Until the twin is repaired,
+            # compare to its pooling helper weighted by the active-run fraction.
+            expected_joules, expected_coverage = mean_run_pooled_reference(runs)
+        else:
+            expected_joules, expected_coverage = b.joules, b.coverage_fraction
+        self.assertLessEqual(abs(a.coverage_fraction - expected_coverage), COVERAGE_ABS, context)
         bar = joules_bar(a, b)
-        # Gap reading: lane fills uncovered time with the covered mean (D/|C|),
-        # the twin does not; lane * coverage is the pooled integral both define.
-        self.assertLessEqual(abs(a.joules * a.coverage_fraction - b.joules), bar, context)
+        # Gap reading on the SAME estimand: the lane fills gaps by M/C.
+        self.assertLessEqual(abs(a.joules * a.coverage_fraction - expected_joules), bar, context)
         self.assertIn(f"runs_retained={len(runs)}", a.flags, context)
-        return a, b, abs(a.joules * a.coverage_fraction - b.joules) / bar
+        return a, b, abs(a.joules * a.coverage_fraction - expected_joules) / bar

     def test_offset_plans_agree_where_both_tile_without_repeats(self) -> None:
         for period in (100 * MS, 1_000_000_000, 33_333_333, 99_999_999):
@@ -374,8 +397,8 @@
         a, b, ratio = self.assert_agree(runs, "sampler chain")
         print("TWIN nvml r2 sampler chain: |dJ| / bar =", ratio, "lane", a.joules, a.half_width_j,
               "twin", b.joules, b.half_width_j, "truth", wave.truth_j())
-
-    @unittest.expectedFailure
+        self.assertLessEqual(abs(a.joules-wave.truth_j()), a.half_width_j)
+
     def test_lane_half_width_contains_truth_when_the_sampler_starts_late(self) -> None:
         # Review 2 finding: with 15% of the workload unobserved (sampler 1.3 s
         # late, eight tiled runs, no shift or noise) the lane extrapolates by
@@ -391,7 +414,6 @@
         self.assertLessEqual(abs(b.joules - truth), b.half_width_j)  # twin contains it
         self.assertLessEqual(abs(a.joules - truth), a.half_width_j, (a, truth))

-    @unittest.expectedFailure
     def test_lane_half_width_contains_truth_on_deterministic_replays(self) -> None:
         # Review 2 finding: deterministic replays (the protocol's premise),
         # eight exactly tiled runs, no run shift, 0.3 W reading noise. The
```

## NEEDS_RULING

none. The final derived candidate meets every supplied local bar; R2 explicitly authorizes these printed interval and mean-run changes.

## FIX LOG

R1 lines below are retained verbatim and describe committed code, not an executing acceptance pass from the R1 seat. R2 lines cite executed final-source receipts.

### Round 1

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

### Round 2 (R2)

R2-B1 fixed with 989daab67ea50426c5b27b9c0b734d55ecb74984, d7997925821e8d1a18c365ef45dde6625e3fbf32 and d391ece3eaa193de092818fad930563b92c974fe; before: "1313.231 +- 0.004017, coverage 0.8413" and "1382.231 +- 2.800, coverage 0.2489"; after: "lane 1313.2313116227854 375.7688859610247 0.8412954861410791" and "collapsed: truth 1393.3125318779817 lane 1382.2306680321724 1785.7873234260937 0.24894825703360152". Late, collapsed, all edge rows, no-bound regression and the warned 2-replay plan pass.
R2-M1 fixed with 989daab67ea50426c5b27b9c0b734d55ecb74984, 8d8900cdf, d0fce9251 and d391ece3eaa193de092818fad930563b92c974fe; before: "lane 26 of 40 outside, twin 0" and "power_usage -8.009 against 0.005105"; after: "TWIN nvml r2 deterministic replays: lane misses 0 twin misses 0 of 40" and "lane 1908.960 +- inf cov 1.0000 err -8.009" with sensor_window_time_unknown. Every short/long one-sided and spread-dominated two-sided 400-seed bar passes; probe1/10 and real sampler containment pass.
R2-M2 fixed with 989daab67ea50426c5b27b9c0b734d55ecb74984 and d391ece3eaa193de092818fad930563b92c974fe; before: "1788.389 +- 4.507, err +11.188, closer to the longest run"; after: "mean-run truth 1777.201 J; lane 1776.440 +- 6.057 (err -0.761)". Duration misses 4/3/1/0 of 60 pass; new 400-seed regression has 0 misses and nearer_mean=400.
R2-m1 fixed with 989daab67ea50426c5b27b9c0b734d55ecb74984 and 8d8900cdf; before: "1 failure, in test_optional_pynvml_uses_the_same_sampler_path" / "'_ctypes.CArgObject' object is not subscriptable"; after: "Ran 19 tests in 0.808s" / "OK" under nvidia-ml-py 13.615.71 and the supplied fixed-fake repro "OK". Without extras: 19 tests, one clean optional skip.
N7 fixed with d7997925821e8d1a18c365ef45dde6625e3fbf32; before: "assertAlmostEqual(estimate.joules, 20.0, delta=20e-6)"; after: "assertAlmostEqual(estimate.joules, 20.0, delta=0.01 * estimate.half_width_j)" with its derivation comment, and "Ran 13 tests" / "OK" in the in-scope oracle.
