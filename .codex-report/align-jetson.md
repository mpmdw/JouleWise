# align-jetson — FIX ROUND 3 (JET3; verification pending)

## SUMMARY

Continued the pushed lane from b1613dad6; frozen contracts remain unchanged.
Register cadence now comes from characterization or driver configuration only.
Sampler trace notes declare per-rail refresh period, source and hold latency.
Detector propagation includes observation, transition exposure and matching bounds.
The simulator adds an optional seeded register-hold model; existing defaults are preserved.
The study appends an 840 us conversion / 1 ms poll INA scenario.
Wholly out-of-coverage logged calls are reported separately and excluded from recall.
Missing alarm paths are distinguished from failures reading previously present paths.
Execution environment is unavailable: this checkpoint is APPLIED_UNVERIFIED.
No tests, probes or study have run in this round; no pass is claimed.

## FILES

- `joulewise/align/power/ina3221.py`: shared robust hold predicate and span cadence; resolved-cadence poll-limit rule; existing rails, alarms, OC counters and voltage extrema retained.
- `joulewise/align/phase_detect.py`: all visible idle gaps; quantum plus statistical uncertainty; local burst/decode roles; observed exposure support and power-to-time edge uncertainty; decode-level ambiguity flag.
- `joulewise/align/sensor_sim.py`: common hold/cadence helpers and explicit documentation that prefill/decode coefficients are increments above idle; simulator behavior unchanged.
- `tests/align/test_phase_detect.py`: covered-call study, same-gap null, 72-seed default and stdlib parallel CLI; original hidden-call test now uses a covered envelope, retaining its assertions.
- `tests/align/test_phase_detect_review2.py`: six end-to-end regressions, including an observed in-turn omission and bit-identical unsampled-call counterfactual.
- `tests/align/test_power_ina3221_review1.py`: strengthens the existing cadence test to reject a spurious poll-limit flag when cadence is resolved.
- `docs/align/jetson_characterization.md`: first-board protocol, current algorithms, measured synthetic study and limits.
- `.codex-report/align-jetson.md`: this report and retained Round 1 FIX LOG.

No registry edit and no `power/__init__.py` edit. PIPELINE.md, records.py and
interfaces.py are unchanged. `model()`, `production_world()` and
`production_sensor_models()` retain their original signatures and behavior.
The untracked `.review2/` scripts and outputs are deliberately not committed.

## PUBLIC API

Unchanged sampler and simulator signatures:

```python
Ina3221Sampler(*, sysfs_root="/sys", sample_interval_ns: int,
    update_interval_ms=None, averaging_window_ns=None, characterization=None,
    shunt_resistance_ohm=None, clock_domain="host.monotonic",
    clock=time.monotonic_ns, read_text=None)
Ina3221Sampler.discover() -> tuple[Rail, ...]
Ina3221Sampler.start() -> None
Ina3221Sampler.sample_once() -> None
Ina3221Sampler.stop() -> tuple[PowerTrace, ...]
Ina3221Sampler.characterize(*, reads: int, sleep=time.sleep) -> Characterization
Rail(channel, label, device, voltage, current)
RailCharacterization(channel, read_latency_ns, distinct_periods_ns, quantum_w,
    voltage_quantum_mv, current_quantum_ma, flags=())
RailCharacterization.cadence_ns -> float | None  # mean / endpoint span
RailCharacterization.median_distinct_period_ns -> float | None
Characterization(rails, update_intervals_ms, flags)
TimelineModel(idle_w, prefill_base_w, prefill_token_w, context_token_w,
    decode_w, ripple_w, prefill_tokens_per_s)
PowerInterval(start_ns, end_ns, mean_w, label, ripple_w=0,
    ripple_period_ns=None, ripple_origin_ns=0)
Timeline(start_ns, end_ns, clock_domain, idle_w, intervals, flags=())
Timeline.integral(start_ns: int, end_ns: int) -> float  # W ns
Timeline.power_at(t_ns: int) -> float
SensorModel(sample_interval_ns, averaging_window_ns, duty_fraction, noise_sd_w,
    quantum_w, clock_offset_ns=0, clock_offset_uncertainty_ns=0, seed=0,
    source="mock", channel="synthetic", clock_domain=None)
SensorModel.ina3221(*, cadence_ns, noise_sd_w, quantum_w, **kwargs) -> SensorModel
SensorModel.nvml(*, noise_sd_w, quantum_w, **kwargs) -> SensorModel
SensorModel.powermetrics(*, noise_sd_w, quantum_w, **kwargs) -> SensorModel
timeline_from_episode(episode: Episode, model: TimelineModel) -> Timeline
simulate(timeline: Timeline, sensor: SensorModel) -> PowerTrace
```

Analysis records retain their original positional fields and append optional
observed-exposure fields; times are integer nanoseconds and powers are watts:

```python
Segment(start_ns, end_ns, mean_w, label, clock_domain="", sample_interval_ns=0,
    averaging_window_ns=0, flags=(), boundary_uncertainty_ns=0,
    low_observation_windows=(), observation_uncertainty_ns=0,
    idle_floor_w=None, active_floor_w=None, power_uncertainty_w=0.0)
# low_observation_windows contains (exposure_start_ns, exposure_end_ns, observed_w).
ToolCallMatch(recall, precision, unmatched_logged, unlogged_candidates, flags=(),
    matched_count=0, tolerance_ns=0, indeterminate_candidates=())
estimate_noise_sd(values: tuple[float, ...]) -> float
detect_phases(trace: PowerTrace, *, noise_sd_w: float | None = None) -> list[Segment]
match_tool_calls(segments: list[Segment], episode: Episode) -> ToolCallMatch
```

Test/study helpers:

```python
model()
production_world(seed=0, tool_duration_ns=250_000_000, tools=True, *, turns=30,
    client_gap_ns=20_000_000, calls_per_turn=(1, 3), bytes_per_result_token=4)
production_sensor_models(seed, *, ina_cadence_ns=1_000_000,
    shunt_resistance_ohm=0.005, operating_voltage_v=5.0, operating_current_a=2.0,
    noise_sd_by_sensor=None)
clopper_pearson(successes, trials, *, confidence=0.95) -> tuple[float, float]
run_duration_study(*, seeds=range(72), durations_ns=(1_000_000, 5_000_000,
    10_000_000, 25_000_000, 50_000_000, 100_000_000, 250_000_000, 500_000_000),
    turns=30, client_gap_ns=20_000_000, sensors=production_sensor_models) -> dict
```

The study's `hidden_call_recall` is the minimum of its covered-mid and
covered-stretch recalls, whose separate CP intervals are printed. Shortest
answers use those covered calls. Between-turn omissions are labelled log-only;
shared-run concealment is reported separately. The two allowed r2 repro key
ports are `isolated_hidden_call_recall` -> `covered_stretch_hidden_call_recall`
and `isolated_only_shortest_passing_duration_ms` -> `shortest_passing_duration_ms`.
The repro's old printed label remains unchanged. No r7 private-name port.

Private helpers `_held_change_indices(values)` and `_mean_period_ns(periods)`
live in sensor_sim; phase_detect re-exports the former for the supplied probe.

## TESTS RUN

Round 3 checkpoint: no commands ran; exec_command refuses because no usable
execution environment is available. The environment wait remains pending.
All executions and numbers below belong to the preceding seat / Round 2.
They do not validate the Round 3 source. Required align/probe/study runs remain open.


Python 3.12.14. No extra was installed or required; no extra-dependent tests.
No test used network or real hardware. No whole-repository suite was run.
No registry was changed, so no registry-reader test was required.

- `python3 --version`: Python 3.12.14.
- Initial `python3 -m unittest discover -s tests/align -t .` on the VM's default
  `work` checkout failed collection because that checkout has no tests/align.
- The same discovery command at the exact review baseline 6fec76606: **40 tests,
  OK, zero skips**, 5.166 s. This is this seat's execution, not a copied result.
- The same command on the final source: **46 tests, OK, zero skips**;
  runtime recorded in END-TO-END below. Original assertions were retained.
  Intermediate drafts failed and were corrected before the final pass.
  Later comment/docstring-only changes were checked with ast.parse/ast.dump
  against 54ce0818d; executable ASTs are unchanged.
- `python3 -m unittest tests.align.test_phase_detect_review2`: five tests passed
  before the sixth observed-mid-call regression was added; final discovery
  includes all six.
- `python3 -c "print(1-0.025**(1/64))"`: derived 0.056009089386636624.
- `TIMEFORMAT='study elapsed seconds: %R'; time python3 -m tests.align.test_phase_detect --study > .review2/study-final.json 2> .review2/study-final.err`:
  exit 0; 24 rows, 72 seeds per row, 1181.322 s. A prior `/usr/bin/time` wrapper failed before Python
  launched because that executable is absent. Provisional studies interrupted
  during detector correction supply no reported results.

Every supplied APPENDIX file was written verbatim into `.review2/`. Only r2's
above two output-key accesses were subsequently ported as authorized. The local
runner executed all 38 expanded commands before at 6fec76606 and after at the
final source. Canonical commands from the repository root are:

```sh
TMPDIR=/tmp/jetson-review2 python3 -I /workspace/JouleWise/.review2/r1d_lane_null.py 6
TMPDIR=/tmp/jetson-review2 python3 -I /workspace/JouleWise/.review2/r1_toolfree_gaps.py 8
TMPDIR=/tmp/jetson-review2 python3 -I /workspace/JouleWise/.review2/r8b_lane_world.py 32
TMPDIR=/tmp/jetson-review2 python3 -I /workspace/JouleWise/.review2/r8c_lane_ina.py 8
TMPDIR=/tmp/jetson-review2 python3 -I /workspace/JouleWise/.review2/r8_lsb_split.py 24
TMPDIR=/tmp/jetson-review2 python3 -I /workspace/JouleWise/.review2/r1c_diag.py
TMPDIR=/tmp/jetson-review2 python3 -I /workspace/JouleWise/.review2/r2_gap_confound.py ina 12
TMPDIR=/tmp/jetson-review2 python3 -I /workspace/JouleWise/.review2/r2_gap_confound.py nvml 16
TMPDIR=/tmp/jetson-review2 python3 -I /workspace/JouleWise/.review2/r5_covered_hidden.py 6
TMPDIR=/tmp/jetson-review2 python3 -I /workspace/JouleWise/.review2/r3_labels.py 3
TMPDIR=/tmp/jetson-review2 python3 -I /workspace/JouleWise/.review2/r3b_flags.py
TMPDIR=/tmp/jetson-review2 python3 -I /workspace/JouleWise/.review2/r4_ratio.py
TMPDIR=/tmp/jetson-review2 python3 -I /workspace/JouleWise/.review2/r4b_noripple.py
TMPDIR=/tmp/jetson-review2 python3 -I /workspace/JouleWise/.review2/e13_cadence.py /tmp/jetson-review2
```

The remaining 24 commands are `TMPDIR=/tmp/jetson-review2 python3 -I
/workspace/JouleWise/.review2/r7f_seeds.py skew noise conv poll seed`, expanded
for each seed 0..5 and configurations `(0,.08,1680,500)`, `(50,.08,1680,500)`,
`(0,.05,840,250)` and `(15,.05,840,250)`. Each was run beside its control.
Scratch orchestration commands were `python3 .review2/run_repros.py before`
and `python3 .review2/run_repros.py verified`; four subprocesses at a time.
A zero process exit is not claimed to mean every scientific pass condition
passed: the explicit exceptions are in FIX LOG / NEEDS_RULING.

## END-TO-END

Round 3: no executed world or study yet. The following is historical Round 2
execution, not a current result. All new shortest-duration claims remain pending.


Executed on this lane's numerical source 54ce0818dad4a3686ee41e78e4e1d6595bc3d5c3
with Python 3.12.14. `python3 -m unittest discover -s tests/align -t .`
passed **46 tests, zero skips**, in 26.287 s. The default production study
completed in **1181.322 s**: seeds 0..71, eight durations, three sensors and
four physical worlds per row (6912 simulated traces, derived as 72*8*3*4).
Later comment/docstring corrections preserve executable AST identity.

Shortest tested durations satisfying point recall >=90% in **both** covered
modes, logged recall >=90%, and all three episode-FA rates <5%:
**INA 5 ms; NVML 250 ms; powermetrics 250 ms**.
Using each covered-recall lower 95% CP bound >=90% and all FA upper bounds
<5% gives **INA 10 ms; NVML 250 ms; powermetrics 250 ms**.
These are per-column intervals, not simultaneous coverage of the search grid.

Every row has 72 episodes per covered mode and per FA control. All three
FA counts are 0/72 in every row; each exact equal-tail 95% CP upper bound
is 0.04994408, below .05. The table rounds that endpoint to .050;
the strict comparison uses the unrounded bound. Covered client gap is zero,
so call duration equals trough duration. The main and null worlds retain
20 ms client latency. Logged recall pools visible calls in the main world.
Covered FA counts whether either full-log covered world has a false candidate.

| Call ms | Sensor | Covered mid recall [95% CP] | Covered stretch recall [95% CP] | Logged recall | FA episodes: main / null / covered |
| ---: | --- | --- | --- | ---: | --- |
| 1 | INA 1 ms | 0.153 [0.079, 0.257] | 0.264 [0.167, 0.381] | 1.000 | 0 / 0 / 0 |
| 1 | NVML 100/25 ms | 0.000 [0.000, 0.050] | 0.000 [0.000, 0.050] | 0.120 | 0 / 0 / 0 |
| 1 | powermetrics 100 ms | 0.000 [0.000, 0.050] | 0.000 [0.000, 0.050] | 0.000 | 0 / 0 / 0 |
| 5 | INA 1 ms | 0.931 [0.845, 0.977] | 1.000 [0.950, 1.000] | 1.000 | 0 / 0 / 0 |
| 5 | NVML 100/25 ms | 0.000 [0.000, 0.050] | 0.000 [0.000, 0.050] | 0.236 | 0 / 0 / 0 |
| 5 | powermetrics 100 ms | 0.000 [0.000, 0.050] | 0.000 [0.000, 0.050] | 0.000 | 0 / 0 / 0 |
| 10 | INA 1 ms | 1.000 [0.950, 1.000] | 1.000 [0.950, 1.000] | 1.000 | 0 / 0 / 0 |
| 10 | NVML 100/25 ms | 0.000 [0.000, 0.050] | 0.000 [0.000, 0.050] | 0.328 | 0 / 0 / 0 |
| 10 | powermetrics 100 ms | 0.000 [0.000, 0.050] | 0.000 [0.000, 0.050] | 0.000 | 0 / 0 / 0 |
| 25 | INA 1 ms | 1.000 [0.950, 1.000] | 1.000 [0.950, 1.000] | 1.000 | 0 / 0 / 0 |
| 25 | NVML 100/25 ms | 0.264 [0.167, 0.381] | 0.250 [0.155, 0.366] | 0.681 | 0 / 0 / 0 |
| 25 | powermetrics 100 ms | 0.000 [0.000, 0.050] | 0.000 [0.000, 0.050] | 0.391 | 0 / 0 / 0 |
| 50 | INA 1 ms | 1.000 [0.950, 1.000] | 1.000 [0.950, 1.000] | 1.000 | 0 / 0 / 0 |
| 50 | NVML 100/25 ms | 0.347 [0.239, 0.469] | 0.333 [0.227, 0.454] | 0.933 | 0 / 0 / 0 |
| 50 | powermetrics 100 ms | 0.319 [0.214, 0.440] | 0.028 [0.003, 0.097] | 0.846 | 0 / 0 / 0 |
| 100 | INA 1 ms | 1.000 [0.950, 1.000] | 1.000 [0.950, 1.000] | 1.000 | 0 / 0 / 0 |
| 100 | NVML 100/25 ms | 0.681 [0.560, 0.786] | 0.500 [0.380, 0.620] | 1.000 | 0 / 0 / 0 |
| 100 | powermetrics 100 ms | 1.000 [0.950, 1.000] | 0.694 [0.575, 0.798] | 0.982 | 0 / 0 / 0 |
| 250 | INA 1 ms | 1.000 [0.950, 1.000] | 1.000 [0.950, 1.000] | 1.000 | 0 / 0 / 0 |
| 250 | NVML 100/25 ms | 1.000 [0.950, 1.000] | 1.000 [0.950, 1.000] | 1.000 | 0 / 0 / 0 |
| 250 | powermetrics 100 ms | 1.000 [0.950, 1.000] | 1.000 [0.950, 1.000] | 1.000 | 0 / 0 / 0 |
| 500 | INA 1 ms | 1.000 [0.950, 1.000] | 1.000 [0.950, 1.000] | 1.000 | 0 / 0 / 0 |
| 500 | NVML 100/25 ms | 1.000 [0.950, 1.000] | 1.000 [0.950, 1.000] | 1.000 | 0 / 0 / 0 |
| 500 | powermetrics 100 ms | 1.000 [0.950, 1.000] | 1.000 [0.950, 1.000] | 1.000 | 0 / 0 / 0 |

True main-world prefills are 2160 per sensor/duration (72*30). INA and
powermetrics detect all 2160 at every duration. NVML detects 2159 at 100 ms
and 500 ms and all 2160 elsewhere. Mean episode duration ranges from
147.868 s to 176.429 s across the grid (rounded to ms).

Shared-run omissions are concealed in every trial where the original logged
call was detected: INA 72/72 at every duration; NVML 3/3, 12/12, 27/27,
44/44, 72/72, 72/72, 72/72, 72/72 in duration-grid order; powermetrics has
no such detected trials at 1/5/10 ms, then 24/24, 67/67, 72/72, 72/72,
72/72. Concealment is conditional on detecting the original shared run;
0/0 is undefined, not a zero-concealment result. Between-turn log-only
isolated and mixed omissions yield zero hidden-call recall throughout.

All 38 expanded reviewer commands exited successfully before and after;
integer scientific pass conditions are assessed separately in the report.
B1/B2/B3/M2 and m2–m6 meet their requested checks. M1's strict r5 short-hit
non-regression and optional m1's universal phase counts remain unmet and
are disclosed below; a zero process exit is not a scientific pass.


Production chain: Episode -> timeline_from_episode -> simulate ->
detect_phases -> match_tool_calls. Physical traces are fixed before hiding
calls in log copies. Separate fake sysfs chains use real
Ina3221Sampler.start/sample_once/stop -> PowerTrace -> detector -> matcher.

The production study uses 30 turns, 1800 initial prefill tokens, 30..400 decode
tokens at 64 tokens/s, and 150..3000 result tokens per call feeding the next
prefill at 2000 tokens/s. Cached context grows by real token counts. One to
three calls share each non-final tool turn. Main and null controls retain
20 ms client latency; both covered-call worlds have zero client gap. A first
turn's isolated call is either moved inside decode or covered by a stretched
logged turn end. Call duration equals trough duration in those two worlds.
One hidden call per independently seeded episode is a Bernoulli trial;
pooled visible-call recall is descriptive, since calls within a run correlate.

INA's supplied 1 ms cadence is a scenario, not a measured board result.
At 5 V, 2 A and the public P3767 DT's 5 milliohm shunt, dV=.008 V and
dI=40 uV/.005 ohm=.008 A; dP=5*.008+2*.008+.008*.008=.056064 W.
NVML and selected powermetrics output use .001 W integer-mW resolution.
Independent read sd=q/sqrt(12) is a scenario in addition to rounding.
NVML is 100 ms sampling / 25 ms exposure (duty .25); powermetrics is
100 ms whole-window sampling. Hardware status remains PROVISIONAL.

The 90% recall, under-5% FA and equal-tail 95% CP coverage are reporting
conventions. Intervals are per column, not simultaneous coverage over the grid.
The default 72 is derived from n > log(.025)/log(.95)=71.9; zero alarms in 72
trials gives upper 1-.025**(1/72)<.05. Shortest answers are grid points, not
interpolated hardware limits. Neither nulls nor flagged episodes are discarded.

## DECISIONS I MADE

- Continued only the existing lane, preserving the frozen contracts and all
  reviewer fixed-world builders. The runtime became usable after initial
  launch refusals; GitHub checkpoints preceded local execution. The explicit
  user build brief selects this bounded AGENT task over unrelated queue work.
- Construct every idle complement of visible generation, including tool-free
  client gaps. Removing a call outside claimed generation supplies no new
  power evidence when the log already exposes the gap.
- Put shared private helpers in the already-authorized sensor_sim module.
  Both consumers use one majority-of-held-runs predicate and mean/span
  estimator. Two poll-quantized endpoints motivate the two-bin cadence band;
  the median/MAD majority breakdown motivates robustness to isolated V/I splits.
  No sqrt(n) evidence guard, lag cap or all-periods>1 rule remains.
- Use exposure duration and the available n-1 pairs as the lag cap. The
  2*variance*log(n) BIC split penalty, q^2/12 variance floor and accumulated
  ulp floor retain their stated derivations.
- Add a bounded one-quantum rounding term to statistical level uncertainty
  by the triangle inequality; it cannot average away without demonstrated
  dithering. Add the compared means' ulps at the grouping boundary. Local
  peak/fall roles and observed idle edges prevent one spurious level group
  from shifting labels everywhere. Decode may rise with context.
- Preserve an observable quantization floor when first-difference MAD is
  exactly zero but out-and-back small excursions exist. This is not analog
  calibration: conditional repeat removal and token ripple can bias it.
- Distinguish known-call runs from empty visible client gaps. For empty gaps,
  idle-compatible observed exposures may refute a too-short explanation;
  mixed exposures remain conservative because unobserved token ripple can
  vanish in whole windows and survive partial ones. Two power half-widths
  imply at most 2*bar/contrast active exposure, converted to timing uncertainty.
- Effective held cadence supplies conversion latency in addition to averaging,
  clock half-width and read-gap uncertainty. Positive alarms, OC deltas and
  voltage extrema remain in sampler notes; no protection settings are altered.
- Use zero-gap covered-call worlds for the deliverable. Keep ordinary-gap
  and shared-run omissions explicitly log-only controls. Print both point
  and per-column bound answers; no scientific choice is hidden.
- Code semantics win over reviewer prose: TimelineModel.decode_w is an
  increment above idle. w.py's idle=6, decode_w=7 therefore produces 13 W,
  not 7 W. Its +1 W wait remains separable. A new regression separately
  exercises a true 7 W decode (increment=1) and its equal-level ambiguity flag.
- Retain conservative labels where sparse exposure misses a prefill. Do not
  manufacture a burst count from an unobserved interval to satisfy m1's
  unconditional 20/20 criterion.
- Root AGENTS.md handoff item 8 requested a read-only document-consistency
  agent. That sweep checked API descriptions, Round 1 preservation, repro
  evidence and final numeric tables; its factual corrections were applied.
- No hardware, paid service, external message, PR, merge, force push, main
  push, registry edit or out-of-scope tracked write. Extra packages were unnecessary.

## CONTRACT-CHANGE

Request PowerTrace.register_refresh_period_ns, hold_latency_ns and settling_time_ns.
Current lane-local adapter uses those documented JSON keys in notes; source is
register_refresh_source, with register_refresh_print_half_width_ns for driver
precision. detect_phases keyword arguments override notes. The frozen files
are unchanged. Historical Round 2 contract statement follows.

none. Segment's appended fields are lane-local. Shared records and protocols
are unchanged. The decode_w prose disagreement is resolved by preserving the
existing code; no governing contract change is requested.

## FIX LOG

### Round 1

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

### Round 2

Before numbers below were executed by this seat at 6fec76606. After numbers
are executed on the final source; they are not copied reviewer measurements.
Full machine outputs remain in untracked .review2/before and .review2/verified.

- JET2-B1 — fixed in 8abbd500a61a9f46cd74610d844b0b3048559c90, completed in 54ce0818dad4a3686ee41e78e4e1d6595bc3d5c3. Before lane null +20 ms: INA `FA_candidates=174`, NVML `20`; after all six lane-null rows `FA_candidates=0`. Before mixed tool-free turns: INA `FA_candidates=66 mean_recall=1.000`, NVML `13 .872`, pm `2 .876`; after every one of nine r1_toolfree lines `FA_candidates=0 mean_recall=1.000`. No candidate remains. Study null retains the requested client gap.
- JET2-B2 — fixed in 7299f9371582b9c27c0cb9c698aeb052303fe4c3 and c19381b858bafe53158ee2555a7031377f92b9fa. Before skew50 seed1: `thinning_evidence=False`, `matched=8/9 FA=1 tol=2188120`; after `thinning_evidence=True`, `matched=9/9 FA=0 tol=3784296`. All 24 skew/control runs now have eight prefill/eight decode, every logged call matched (260/260 pooled), zero FA, and hold evidence. Every 1.68 ms run's tolerance exceeds the required derived 3.37 ms. Every run retains `hardware_alarm_set:...curr1_crit_alarm`, `overcurrent_throttle_events:...oc1_event_cnt` and OC delta 1.
- JET2-B3 — fixed in c19381b858bafe53158ee2555a7031377f92b9fa and 371d32d14033ae1479d6d1740aae540c6cc13b0e. Before zero ripple: NVML `with_FA=11 mean_recall=0.852 recall<0.5=4`, pm `9 .889 3`, INA `4 .979 0`; after both ripple settings/all sensors `with_FA=0 mean_recall=1.000 recall<0.5=0`. r8_lsb_split's four 24-episode rows now all show `recall<0.5 in 0 episodes, episodes with FA=0, mean recall=1.000`; grouping adds bounded one-quantum uncertainty.
- JET2-M1 — rejected as an unconditional short-call non-regression requirement: a hidden interval wholly outside sensor exposure cannot be identified from power (bit-identical counterfactual regression). Covered zero-gap study and same-gap null implemented in c19381b858bafe53158ee2555a7031377f92b9fa / 371d32d14033ae1479d6d1740aae540c6cc13b0e. Before r2 INA shortest changed `1.0` to `5.0` ms when gap20 became gap0; after both gaps give covered shortest `5.0` ms (covered recall `.250, 1.000, 1.000` at 1,5,10 ms). NVML covered-stretch curves are identical at both gaps (`.312, .188, .625` at 25,50,100 ms), no grid point passes. Only r2's two authorized output-key accesses were ported; printed legacy labels remain. r5 now has `full_log_FA_episodes=0/6` on all 24 lines; all 300 ms hits remain 6/6, but short-call hit counts fail the requested non-regression: stretch NVML 5/25 ms `3/6 -> 0/6,1/6`; stretch pm 100 ms `5/6 -> 1/6`. Mid pm improves 25 ms `0/6 -> 1/6`, 100 ms `5/6 -> 6/6`; all other r5 hit counts remain unchanged. Exact acceptance is NOT claimed; see NEEDS_RULING.
- JET2-M2 — fixed in c19381b858bafe53158ee2555a7031377f92b9fa. Before +.5 W seed0 all sensors `calls=28 matched=0`; after `calls=28 matched=28 FA=0`. All nine +.5 W seed/sensor rows have exactly their corresponding +0 W prefill/decode counts, every call matched and no FA. The supplied +1 W rows also match all calls: code's decode plateau is 6+7=13 W, not the review prose's 7 W. A separate true 7 W decode / 7 W wait regression checks `tool_wait_not_separated_from_decode_level` on the episode match.
- JET2-m1 — rejected as an unconditional phase-count guarantee for sparsely observed bursts; partial temporal-role improvement is in c19381b858bafe53158ee2555a7031377f92b9fa. Before +3 W seed1 INA/NVML/pm each `decode: 3`; after INA `prefills=20/20 decode:20`, NVML `prefills=17/20 decode:20`, pm `prefills=17/20 decode:21`. All INA +1/+3 W rows pass 20/20; slow-sensor rows do not all pass. NVML can miss a whole 60 ms prefill within its 75 ms blind interval. Powermetrics additionally retains unresolved extra/missing segment errors; not all failures are proved unobservable. No complete fix or count pass is claimed.
- JET2-m2 — fixed in c19381b858bafe53158ee2555a7031377f92b9fa and 371d32d14033ae1479d6d1740aae540c6cc13b0e. Before cropped no-tool INA `FA=11` on each seed, pm seed0 `FA=9`; after every cropped no-tool row `FA=0`, and every tools=True row remains clean with every logged call matched.
- JET2-m3 — fixed in 7299f9371582b9c27c0cb9c698aeb052303fe4c3 / c19381b858bafe53158ee2555a7031377f92b9fa. Before r4 at 1.9 ms / sd .05 `sigma_hat=0.0000`; after `.0629` with ripple and `.0524` without (true sd .05). At q=.056/true sd .016, before `.0000` at 1.0–1.9 ms (already `.1174` at 2.5/3 ms); after `.1174` throughout with ripple. Every r4/r4b estimate is nonzero; every line retains `segs=37 matched=19/19 FA=0`. Conditional repeat removal and ripple bias mean this is not a calibrated analog-noise estimate.
- JET2-m4 — fixed in 7299f9371582b9c27c0cb9c698aeb052303fe4c3. Before e13 `poll=500000 ... 840000 ... flags=('cadence_poll_limited', 'quantum_one_coordinate_unobserved')`; after same exact cadence with only `('quantum_one_coordinate_unobserved',)`. The existing every-read-changing test still requires poll-limited and passes.
- JET2-m5 — fixed in 7299f9371582b9c27c0cb9c698aeb052303fe4c3. Both consumers now use one held predicate and endpoint-span mean. Before r7 skew50 seed1 `window=1688120 thinning_evidence=False`; after `window=1892148 thinning_evidence=True`. All 24 runs infer their trace window exactly with common thinning evidence; no private-name repro port.
- JET2-m6 — fixed in c19381b858bafe53158ee2555a7031377f92b9fa. Before default 64 could only give derived zero-FA upper `0.056009089386636624`; after default is 72, the smallest integer making `1-.025**(1/n)<.05`. Both point and 95%-bound columns are computed and printed rather than choosing one silently.
- JET2-m7 — fixed in 22c08424776f928b40e4b76a782b1d50a17d6972. Before report said zero tests and doc had stale FIX1C status; after both contain this seat's 46-test execution, all repro outcomes, full 72-seed production grid and shortest answers. Historical Round 1 FIX LOG is preserved; current non-passes are explicit.

### Round 3 (JET3)

- JET3-B1 — source checkpoint; verification pending. Reviewer-measured at b1613dad6 before: conversion/poll 1100/1000 us FA 11/12, 840/1000 us 8/12, 1500/1000 us 6/8. After: not executed.
- JET3-M1 — source checkpoint; verification pending. Reviewer-measured before: "held inferred 71/72; mid hidden recall 67/72; with 1e-9 W dither 72/72". After: not executed.
- JET3-m1 — settling parameter propagated; protocol and repro verification pending. Before reviewer-measured decay5 "FA episodes 2/6"; after not executed.
- JET3-m2 — source checkpoint excludes wholly unobserved calls and reports them in outside_trace_logged. Before reviewer-measured cropped recalls ".545/.455 flags []"; after not executed.
- JET3-m3 — source checkpoint adds only existing alarm paths, retaining failures after discovery. Before reviewer: absent alarms yield health_read_error; after not executed.
- Setup-only ports: test_held_reads_with_estimated_and_supplied_noise and test_held_noninteger_ratio_noise_is_nonzero_and_calls_survive declare P in notes; test_real_sysfs_path_through_detector_with_held_conversions runs a changing-load characterization before sampling. Every scenario and assertion retained, as required by this brief.

## OPEN ISSUES

- No live Orin validation. Shunt, cadence, analog noise, exposure, sampler
  overhead and supply behavior still require the documented borrowed-board session.
- Held-value cadence inferred from power is confounded by quantization and
  steady/periodic loads. It remains flagged and does not replace characterization.
- Greedy binary segmentation can miss balanced short troughs; the measured
  covered-call curves state that limit rather than assuming perfect sensitivity.
- An idle run cannot reveal which remote tool ran, and a hidden call sharing
  an already logged idle run is generally unidentifiable.
- The M1 stretch-powermetrics 100 ms drop from 5/6 to 1/6 remains a
  sensitivity regression; it is not established to be unobservable. Conservative
  treatment of mixed exposures trades sensitivity for the required clean nulls.
- Strict M1 short-call non-regression and m1 guaranteed prefill/decode counts
  are not claimed as passes; see the specific observability ruling below.
- Infrastructure is available now. No repository file is missing. Tracked
  changes are confined to WRITE_SCOPE; .review2 remains untracked intentionally.

## NEEDS_RULING

Question: must an overlap-only hit be retained when the sensor did not observe
the hidden call, or should the result require observed power evidence?

Evidence: r5 NVML seed 3's 5 ms hidden call ends at 32274 ms; its next 25 ms
exposure begins at 32275 ms. Seed 4 similarly ends at 27175.2 ms while the
exposure begins at 27175 ms (only .2 ms is sampled). The old 100 ms segment's
support overlaps half the call, but this does not establish hidden work.
The new counterfactual regression gives bit-identical full sensor outputs
with and without a 5 ms covered call lying wholly in NVML's blind interval.

Options: retain overlap-only apparent hits and label them timestamp overlap,
or require observable power evidence and disclose misses / unidentifiability.
Recommendation: the latter, consistent with B1's ordinary-gap null control.
Blocked acceptance claim: M1's request that every r5 hidden-hit count be no
lower than before. The zero-gap covered-call deliverable and other fixes can
be completed independently. An async question was sent; no response is
assumed from elapsed time.

The optional m1 unconditional 20/20 phase-count bar has the same issue when
prefill fits within NVML's unobserved 75 ms. Context-dependent decode roles
are improved, but no complete count guarantee is asserted on unseen bursts.
Remaining errors also include powermetrics extra decode labels at zero rise
and missing prefills at +3 W; those are unresolved segmentation errors and
have not all been established to be unobservable.
