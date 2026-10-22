# align-jetson — FIX ROUND 1 / continuation fix1c

## SUMMARY

Continued the pushed lane from 13b86db3f; fix1c changes remain SOURCE-ONLY and UNVERIFIED.
Short trough leaves now use established idle/decode levels instead of disappearing into active neighbors.
Cadence inference and repeat removal share a conservative test that preserves native-rate quantized plateaus.
Unmatched edge-low waits overlapping visible calls are indeterminate when the trace cuts their timing.
Added three regression methods and strengthened all low-noise rows to require all three calls and no false candidates.
The lead's supplied 37-test pass and repro results at 13b86db3f are recorded separately from this seat.
The managed executor remains starting/offline; no current-head Python tests or reviewer probes could execute here.
The production study, sensitivity curves, concealment rates and shortest-duration answers remain pending.

## FILES

Fix1c changes only these four paths:

- `joulewise/align/phase_detect.py`: idle/decode least-squares labeling of short trough leaves; shared hold-evidence predicate for cadence inference and MAD; clipped-edge indeterminate handling.
- `tests/align/test_phase_detect_review1.py`: three new methods for single-exposure troughs, native-rate quantized plateaus and a trace cut inside a wait; strengthened existing low-noise regression with matched-count/false-candidate assertions.
- `docs/align/jetson_characterization.md`: corrected detector description and separate lead-versus-current execution status.
- `.codex-report/align-jetson.md`: this report, evidence separation and fix1c FIX LOG entries.

Existing lane deliverables are retained: `power/ina3221.py` (sampler,
characterization, alarms, OC counters and voltage extrema);
`sensor_sim.py` (analytic timelines and sensor convolution);
`tests/align/test_power_ina3221*.py`, `test_sensor_sim.py` and
`test_phase_detect.py` (fake sysfs, fixed and production worlds, study and
exact binomial intervals). Their source is unchanged by fix1c.

No registry change. No edit to PIPELINE.md, records.py, interfaces.py,
power/__init__.py or any other repository file. The scratch .review1
directory could not be created and has not been committed.
GitHub compare 13b86db3f...368bf757 confirmed the three source/test/doc
paths before this fourth report path was updated.

## PUBLIC API

Existing positional fields and the probe-imported helpers remain compatible.

- `Ina3221Sampler(*, sysfs_root="/sys", sample_interval_ns: int, update_interval_ms: int | None = None, averaging_window_ns: int | None = None, characterization: Characterization | None = None, shunt_resistance_ohm: float | None = None, clock_domain="host.monotonic", clock=time.monotonic_ns, read_text=None)`
- `Ina3221Sampler.discover() -> tuple[Rail, ...]`
- `Ina3221Sampler.sample_once() -> None`
- `Ina3221Sampler.start() -> None`
- `Ina3221Sampler.stop() -> tuple[PowerTrace, ...]`
- `Ina3221Sampler.characterize(*, reads: int, sleep=time.sleep) -> Characterization`
- `Rail(channel, label, device, voltage, current)`
- `RailCharacterization(channel, read_latency_ns, distinct_periods_ns, quantum_w, voltage_quantum_mv, current_quantum_ma, flags=())`
- `RailCharacterization.cadence_ns -> float | None`: mean distinct period, equivalently endpoint span / number of periods.
- `RailCharacterization.median_distinct_period_ns -> float | None`: retained literal median for compatibility; it is not the characterized cadence estimator.
- `Characterization(rails, update_intervals_ms, flags)`
- `TimelineModel(idle_w, prefill_base_w, prefill_token_w, context_token_w, decode_w, ripple_w, prefill_tokens_per_s)`
- `PowerInterval(start_ns, end_ns, mean_w, label, ripple_w=0, ripple_period_ns=None, ripple_origin_ns=0)`
- `Timeline(start_ns, end_ns, clock_domain, idle_w, intervals, flags=())`
- `Timeline.integral(start_ns: int, end_ns: int) -> float`: watt-nanoseconds.
- `Timeline.power_at(t_ns: int) -> float`
- `timeline_from_episode(episode: Episode, model: TimelineModel) -> Timeline`
- `SensorModel(sample_interval_ns, averaging_window_ns, duty_fraction, noise_sd_w, quantum_w, clock_offset_ns=0, clock_offset_uncertainty_ns=0, seed=0, source="mock", channel="synthetic", clock_domain=None)`
- `SensorModel.ina3221(*, cadence_ns, noise_sd_w, quantum_w, **kwargs) -> SensorModel`
- `SensorModel.nvml(*, noise_sd_w, quantum_w, **kwargs) -> SensorModel`
- `SensorModel.powermetrics(*, noise_sd_w, quantum_w, **kwargs) -> SensorModel`
- `simulate(timeline: Timeline, sensor: SensorModel) -> PowerTrace`
- `estimate_noise_sd(values: tuple[float, ...]) -> float`
- `Segment(start_ns, end_ns, mean_w, label, clock_domain="", sample_interval_ns=0, averaging_window_ns=0, flags=(), boundary_uncertainty_ns=0)`
- `ToolCallMatch(recall, precision, unmatched_logged, unlogged_candidates, flags=(), matched_count=0, tolerance_ns=0, indeterminate_candidates=())`
- `detect_phases(trace: PowerTrace, *, noise_sd_w=None) -> list[Segment]`
- `match_tool_calls(segments: list[Segment], episode: Episode) -> ToolCallMatch`

Study/test helpers:

- `world(seed=0, tool_duration_ns=250_000_000, tools=True)`, `model()`, `sensor_models(seed)`: signatures and original scenario behavior unchanged.
- `production_world(seed=0, tool_duration_ns=250_000_000, tools=True, *, turns=30, client_gap_ns=20_000_000, calls_per_turn=(1, 3), bytes_per_result_token=4) -> Episode`
- `production_sensor_models(seed, *, ina_cadence_ns=1_000_000, shunt_resistance_ohm=0.005, operating_voltage_v=5.0, operating_current_a=2.0, noise_sd_by_sensor=None)`
- `clopper_pearson(successes, trials, *, confidence=0.95) -> tuple[float, float]`
- `run_duration_study(*, seeds=range(64), durations_ns=(1_000_000, 5_000_000, 10_000_000, 25_000_000, 50_000_000, 100_000_000, 250_000_000, 500_000_000), turns=30, client_gap_ns=20_000_000, sensors=production_sensor_models) -> dict`


No public API signature changed in fix1c.
New private helper: `_held_change_indices(values: tuple[float, ...]) -> list[int]`.

## TESTS RUN

**This seat, fix1c: 0 Python tests executed.** Collection, pass/fail and skip
counts are unavailable. Three added test methods were counted in source;
this is not an executed count. No extra dependency was installed or needed.
All source remains stdlib-only; no test performs network access.

The following exact shell attempts were rejected before any process
launched, with "No usable execution environment is available. Wait for an
environment to become available before using this tool.":

```sh
pwd
git fetch origin lane/2026-10-21-align-jetson
python3 -m unittest discover -s tests/align -t .
python3 -m unittest tests.test_battery_float_consumers tests.test_battery_float_sweep
mkdir -p /workspace/JouleWise/.review1 /tmp/jetson-review
TMPDIR=/tmp/jetson-review python3 -I /workspace/JouleWise/.review1/run_study.py
```

The git/Python/mkdir attempts selected workdir /workspace/JouleWise.
The managed environment repeatedly reports observed_phase=starting,
connectivity=offline, observations_current=true and failure=null.
Diagnostics return history_status=not_found and records=[].
The environment wait did not yield a usable executor. This is an
infrastructure failure, not an automatic approval-review rejection.
No local checkout, shell test, scratch script write, pip install or
hardware work is claimed. Repository reads, source checkpoints and branch
updates used the connected GitHub tools on the existing lane branch.

**Supplied lead verification, at 13b86db3f, before fix1c:**

- `python3 -m unittest discover -s tests/align -t .`: 37 tests, OK.
  A skip count was not separately supplied.
- `e1_hold.py`: all k=1,2,4,8 rows give 13 segments, 3/3 matched and
  zero candidates with estimated or supplied sd.
- `e14_gapsweep.py`: recall 1.00 and zero candidates at all eight gaps
  for INA/NVML; `e2_e3.py`: all nine lines match every call, zero candidates.
- `e6_sysfs.py`: end-to-end 3/3 and zero; exposure/resolution/tolerance,
  cadence poll limitation, product resolution and summation skip meet bars.
- `e13_cadence.py`: the lead used the allowed r.cadence_ns print
  adaptation; all three cadence errors meet the endpoint quantization bar.
- `e7_diag.py`: zero false candidates on all three sensors.
- `e4_long.py 16 slow`: 32 lines, zero false candidates, but short-call
  misses remained; detected-prefill counts 29–30 for 30 true.
- `e5_fa.py`: zero false candidates, but at 250 ms powermetrics missed
  calls in 35/64 seeds (23 with 0/3, five with 1/3, seven with 2/3).
  This FAILED the pass condition and motivated JET-M1 (fix1c).
- `e8_lownoise.py`: last sd=0, q=0.01 powermetrics row collapsed to one
  segment with 0/3 matched. This FAILED and motivated JET-M6 (fix1c).
- `e9_edges.py`: one-turn case idle/prefill/decode/idle; trace starting
  mid-wait produced one false candidate, addressed by the extra edge fix.
- `e10_gap.py`: 7/7 and zero false alarms; `e11_energy.py`: passes.
- `e12_thread.py`: no sample_gaps flag.
- No completed production-study result or current battery-census result
  was supplied for 13b86db3f.

These are the user's supplied local Python 3.13/macOS results, not runs
performed here and not evidence that the fix1c head passes.

**Pending executing checklist** (all NOT RUN on fix1c):

First materialize every APPENDIX script verbatim into .review1/ as the
brief specifies; do not commit it. For e13 only, replace both print-line
accesses to r.median_distinct_period_ns with r.cadence_ns. This is the
brief-authorized field adaptation already used by the lead, with no world,
sensor, seed, cadence, poll period or comparison-bar changes.

```sh
git -C /workspace/JouleWise fetch origin lane/2026-10-21-align-jetson
git -C /workspace/JouleWise checkout -B lane/2026-10-21-align-jetson origin/lane/2026-10-21-align-jetson
cd /workspace/JouleWise
python3 -m unittest discover -s tests/align -t .
python3 -m unittest tests.test_battery_float_consumers tests.test_battery_float_sweep
mkdir -p /tmp/jetson-review
TMPDIR=/tmp/jetson-review python3 -I /workspace/JouleWise/.review1/e1_hold.py
TMPDIR=/tmp/jetson-review python3 -I /workspace/JouleWise/.review1/e2_e3.py
TMPDIR=/tmp/jetson-review python3 -I /workspace/JouleWise/.review1/e4_long.py 16 slow
TMPDIR=/tmp/jetson-review python3 -I /workspace/JouleWise/.review1/e5_fa.py
TMPDIR=/tmp/jetson-review python3 -I /workspace/JouleWise/.review1/e6_sysfs.py /tmp/jetson-review
TMPDIR=/tmp/jetson-review python3 -I /workspace/JouleWise/.review1/e7_diag.py
TMPDIR=/tmp/jetson-review python3 -I /workspace/JouleWise/.review1/e8_lownoise.py
TMPDIR=/tmp/jetson-review python3 -I /workspace/JouleWise/.review1/e9_edges.py
TMPDIR=/tmp/jetson-review python3 -I /workspace/JouleWise/.review1/e10_gap.py
TMPDIR=/tmp/jetson-review python3 -I /workspace/JouleWise/.review1/e11_energy.py
TMPDIR=/tmp/jetson-review python3 -I /workspace/JouleWise/.review1/e12_thread.py /tmp/jetson-review
TMPDIR=/tmp/jetson-review python3 -I /workspace/JouleWise/.review1/e13_cadence.py /tmp/jetson-review
TMPDIR=/tmp/jetson-review python3 -I /workspace/JouleWise/.review1/e14_gapsweep.py
TMPDIR=/tmp/jetson-review python3 -I /workspace/JouleWise/.review1/run_study.py
```

The whole repository suite was not run, as this brief expressly forbids it.

## END-TO-END

This seat ran no Python end-to-end chain. Current-head matched counts,
false-alarm rates, prefill counts, study runtime, concealment rate and both
shortest-duration answers are unavailable. No source-only fix is a pass.

Supplied lead results on 13b86db3f:

| Chain / sensor | Lead outcome before fix1c |
|---|---|
| Fixed four-turn world -> simulate -> held polling -> detector -> matcher | 13 segments, 3/3 matched, zero candidates for k=1,2,4,8 and both sd modes |
| Fake sysfs -> real discovery/sample_once/stop -> detector -> matcher | 3/3, zero candidates; 4,000,000 ns window; 0.025784 W resolution; 8 ms tolerance |
| Cadence characterization | Errors -54, 0, +51 ns; within one actual poll period / number of change periods |
| Product quantum characterization | 0.057152 W from propagated V/I steps |
| 30-turn seed-1 e7, powermetrics / NVML / INA | Time-weighted label accuracy 0.984 / 0.983 / 1.000; zero false candidates each |
| e4 16 seeds, 30 turns, powermetrics | 441/464 calls matched; zero false candidates |
| e4 16 seeds, 30 turns, NVML | 455/464 calls matched; zero false candidates |
| e4 detected versus true prefills | Slow sensors 29–30 versus 30 per episode; separate INA count not supplied |
| e5 250 ms, powermetrics | 35/64 episodes lost at least one of three calls, despite zero false candidates |
| e8 sd=0, q=0.01, powermetrics | One segment and 0/3 matched; failed |

All values in that table are supplied lead observations at the preceding
head; their physical/comparison bars are those in the brief. They must
not be copied as post-fix measurements.

Prepared production chain remains:
Episode -> timeline_from_episode -> simulate -> detect_phases ->
match_tool_calls, comparing complete, uniformly selected omitted-call,
isolated omitted-call and second-back-to-back-call omitted logs.
Separate no-tool controls remove tool/client waits; they do not establish
immunity to unrelated non-tool idle periods.

Declared inputs (not measured outputs): 30 turns; first prefill 1800 tokens;
30–400 decoded tokens per turn at 64 tokens/s; 150–3000 result tokens per
call, whose total feeds the next prefill at 2000 tokens/s; cached context
grows by actual prefill+decode counts; one to three calls per tool turn,
with first two tool turns guaranteeing isolated and shared-run controls;
20 ms client/serving gap; random alignment within a 100 ms period.
The eight-duration grid and 64 independently seeded episodes per row are
explicit simulation-budget/design parameters, not physical thresholds.

INA production resolution is derived at the specified 5 V, 2 A point:
dV=0.008 V, dI=40 uV / 0.005 ohm=0.008 A;
dP=5*.008 + 2*.008 + .008*.008 = 0.056064 W.
The 5 milliohm shunt is in the public P3767 L4T device tree; actual
borrowed-board configuration still needs verification. The 1 ms cadence is
an explicit scenario parameter, never a characterized Orin claim.
NVML and selected powermetrics output precision is integer mW (q=0.001 W);
their modeled windows remain 100/25 ms and 100/100 ms. Default Gaussian
read sd=q/sqrt(12) is a declared resolution-scaled noise scenario in
addition to rounding, not measured analog noise.

Binomial algebra, not an executed study result: with 64 episodes and zero
false alarms the equal-tail 95% CP upper limit is
1 - 0.025**(1/64) = 0.056009089386636624. At least 72 zero-alarm
episodes are needed for an upper limit below 0.05, from
floor(log(0.025)/log(0.95))+1. Thus the default budget cannot certify the
brief's under-5% target from the bounds even at zero observed alarms.
The 90% / under-5% targets and 95% coverage are reporting conventions.
The runner prints point and bound answers and exposes a needs_ruling object
when they differ; no synthetic answer is invented without execution.



The exact 64-seed production study still needs to run. In particular,
there is no measured numerator/denominator for shared_run_concealed /
shared_run_trials and no point-estimate or bound-based duration answer.
No four-turn pre-fix result is substituted for the production study.

## DECISIONS I MADE

- Continue exactly from pushed 13b86db3f, preserving the existing sampler,
  simulator, production builder and study. Use GitHub source checkpoints
  because the explicitly anticipated executor failure recurred.
- Preserve the shared contracts and all public signatures. world(), model()
  and sensor_models() are unchanged; no reviewer world or bar was altered.
- Resolve a short leaf against established low/decode levels before borrowing
  temporal neighbors. The midpoint is the equal-variance least-squares level
  decision, not a new fitted watt threshold. A decode/prefill transition
  cannot cross below it; low portions at a real wait edge merge into that wait.
- Repeats are conversion evidence only when the existing sqrt(n) count and
  majority-repeat guards hold AND all completed change-to-change runs span
  more than one poll. A one-poll changing run supplies native-rate information
  that must be preserved. This is deliberately conservative, not a hardware
  cadence calibration; ambiguous streams remain unthinned.
- Apply that evidence test to the noise estimator too. Removing all flat
  values otherwise leaves only true transitions and invents large read noise.
  Constant quantized phases retain their zero-difference MAD evidence.
- Keep the existing noise/BIC, local modulation, complete-span grouping and
  adjacent-label consolidation; no original assertion was removed or weakened.
- Add three regression methods and require exactly all three true calls plus
  zero false candidates in every existing low-noise row. Port seed 50 and
  neighboring fixed seeds at 250/500 ms through the full production functions.
- Treat a failed full-run match on an admitted edge-low segment as
  indeterminate. A cut trace does not observe the missing endpoint and cannot
  turn that failure into evidence of an extra call.
- Retain prior decisions: endpoint-span cadence is cadence_ns; literal median
  remains compatible; product resolution is propagated from V/I; driver
  update_interval already incorporates samples; alarms/counters/voltage
  extrema remain recorded; gaps need at least two nominal intervals.
- Retain idle-run matching: every logged call inside a matched run counts
  toward recall, individual boundaries there are unresolved, and precision
  counts troughs/runs. Hidden work inside the same run is unidentifiable.
- Retain production study estimands and exact binomial bounds. Calls within
  one episode are correlated; CP trials are independently seeded episodes.
  Print both point/bound duration answers without choosing one silently.
- No hardware measurement, optional package installation, outside-scope
  write, external message, PR, merge, force push or other-branch push.

## CONTRACT-CHANGE

none. The shared records and cross-lane protocols are unchanged.

## FIX LOG

"fixed" denotes the source correction saved at the named commit. Prior
lead evidence and pending fix1c verification are distinguished explicitly.

- JET-B1 — fixed in 6811295b7e75dcf9f2702f294874dd5c25baedae; sampler regression in 70c41860d77822687a454bc71565cddcfe11567c. Lead at 13b86db3f reports all held-read conditions passing. Re-run after fix1c's shared cadence/noise predicate.
- JET-B2 — fixed in 9cf7e8d9a947075c8a4a73901b3a61308ef2469d. Lead reports all gap/back-to-back rows passing. Concealment fraction remains unmeasured.
- JET-M1 — initial source fix in 6811295b7e75dcf9f2702f294874dd5c25baedae removed false candidates but missed short calls at 13b86db3f; see required fix1c entry below. Supplied slow-sensor prefill counts are 29–30 versus 30.
- JET-M2 — fixed in 975b64bed66a537206b9db0656d202ba75ba4b17, refined in 171a35fdda705966b3dcfe95afe383b1255cbe9a. Lead reports window/resolution/tolerance conditions passing.
- JET-M3 — fixed in 2da5667c03d93cc1c67eedd9a96dec83e1ceb9f7. cadence_ns endpoint-span estimate and poll-limited flag pass in supplied lead verification. Only allowed e13 print-field adaptation is both median-property accesses -> cadence_ns.
- JET-M4 — fixed in 2da5667c03d93cc1c67eedd9a96dec83e1ceb9f7. Lead reports propagated quantum_w=0.057152 W; the product-gap error is removed.
- JET-M5 — source study fixed in 9cf7e8d9a947075c8a4a73901b3a61308ef2469d (introduced 171a35fdda705966b3dcfe95afe383b1255cbe9a). Actual production study, concealment and shortest-duration numbers remain OPEN; no pass is claimed.
- JET-M6 — initial source fix in 6811295b7e75dcf9f2702f294874dd5c25baedae passed other supplied rows but failed noise-free quantized powermetrics; see fix1c below.
- JET-m1 — fixed in 2da5667c03d93cc1c67eedd9a96dec83e1ceb9f7; lead reports summation-channel exclusion/flag passing.
- JET-m2 — fixed in eea481251c601d77ca7864f0fd1d5e1aba748e20; lead reports real-thread repro without sample_gaps.
- JET-m3 — fixed in eea481251c601d77ca7864f0fd1d5e1aba748e20; lead reports e10 7/7, zero false alarms.
- JET-m4 — fixed in 975b64bed66a537206b9db0656d202ba75ba4b17, refined in 171a35fdda705966b3dcfe95afe383b1255cbe9a and 9cf7e8d9a947075c8a4a73901b3a61308ef2469d. Alarms, documented separate L4T counters, read failures, voltage extrema and supply-limit hazard protocol retained; no hardware validation claimed.
- JET-M1 (fix1c) — fixed in source 7f8e42d9e08f3320d2a7fe0afa642d377c88f176; short leaves use established idle/decode least-squares levels. Regression saved in d78557c78cf5cf47736ffe197d09fc96dd25804e. Executor unavailable; all required e5/e4 pass conditions remain UNVERIFIED.
- JET-M6 (fix1c) — fixed in source 1e2d3308db6f8a0dd2353558e61ad6563832ca19 and d24422d09074067356b200ea41954c15c6165bdd; cadence inference and repeat removal require conversion-like completed runs, preserving flat-phase MAD. Regression strengthened in d78557c78cf5cf47736ffe197d09fc96dd25804e. Executor unavailable; no current-head pass claimed.
- Trace-edge observation (fix1c) — fixed in source 49ef9ef1d882f125c63dbf0936a285d08275e7d6; unmatched admitted edge-low waits become indeterminate, not false candidates. Regression in d78557c78cf5cf47736ffe197d09fc96dd25804e; UNVERIFIED.

## OPEN ISSUES

- BLOCKING infrastructure: no usable executor for /workspace/JouleWise.
  No repository file is missing. Tests, scratch script creation and study
  cannot execute until the runtime becomes available. The user explicitly
  authorized source-only fixes followed by lead re-verification in this case.
- Every mandatory alignment/battery-census command and reviewer repro must
  be rerun on the fix1c head. The lead's earlier pass cannot establish
  regression freedom after these number-bearing detector changes.
- .review1/ and /tmp/jetson-review could not be materialized. The appendix
  scripts must be written verbatim; only e13's allowed attribute access changes.
- Production sensitivity/false-alarm curves, per-sensor detected/true prefill
  counts on the fixed head, runtime/seed budget and shortest durations from
  points/bounds remain undelivered. The unchanged runner prints all of them.
- Shared-run concealed-call numerator/denominator/rate remains unmeasured.
  Power cannot separate a hidden call immediately following a logged call
  inside the same idle run; the existing study measures this explicitly.
- A 64-episode budget cannot certify <5% episode false alarms from equal-tail
  95% CP bounds even with zero observed alarms. Keep bounds honest and retain
  both duration answers; any choice belongs in NEEDS_RULING after execution.
- Held-value inference is conservative and cannot prove physical conversion
  cadence from values alone. A stream with both held and native-rate changes
  remains unthinned; verify against characterization on actual instruments.
- Binary segmentation is greedy and may miss short balanced troughs.
  The restored short-leaf label must be checked for both recall and false
  alarms across all fixed-world seeds and production sensor models.
- Unrelated non-tool pauses remain physically confounded with tool waits.
  Reasoning within one forward pass is invisible to this measurement.
- Borrowed-Orin shunt, cadence, exposure, analog noise, acquisition overhead,
  supply behavior and hardware instrument viability remain PROVISIONAL.

## NEEDS_RULING

none yet. Infrastructure availability is not a scientific ruling. The
production study has not completed; no point/bound shortest-duration pair
can honestly be selected or printed as an observed answer. Once it runs,
copy both answers here if they differ, as the brief requires.
