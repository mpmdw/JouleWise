# align-jetson

## SUMMARY

Implemented the Jetson INA3221 sampler, including hwmon and legacy L4T discovery.
Added observed read-latency, distinct-change cadence and quantum characterization.
Added analytic episode power timelines and three configurable synthetic sensor models.
Added noise-penalized phase segmentation and clock-aware one-to-one tool matching.
Added production-shaped worlds, independent arithmetic oracles and a duration-study runner.
Saved the provisional borrowed-Orin characterization protocol.
Implementation and tests are UNVERIFIED: the managed executor never became usable.
No hardware results, passing-test counts or sensitivity measurements are claimed.

## FILES

- `joulewise/align/power/__init__.py`: required package bootstrap, containing only a one-line docstring; the package did not exist on the spine.
- `joulewise/align/power/ina3221.py`: discovery, background sampler, permission/read-error flags, interval readback/restoration, characterization records.
- `joulewise/align/sensor_sim.py`: caller-parameterized workload model, analytic window integration and seeded sensor simulation.
- `joulewise/align/phase_detect.py`: robust noise estimate, binary segmentation, labels, clock-aware maximum-cardinality matching.
- `tests/align/test_power_ina3221.py`: six fake-sysfs/lifecycle test methods.
- `tests/align/test_sensor_sim.py`: five episode/sensor/integration test methods and shared synthetic-world builder.
- `tests/align/test_phase_detect.py`: six phase/matching/penalty test methods and configurable many-seed sensitivity study.
- `docs/align/jetson_characterization.md`: provisional setup, interpretation, viability, limitations and rehearsal commands.
- `.codex-report/align-jetson.md`: this report.

No registry files changed. The three protected pipeline/records/interfaces files are unchanged.
The remote diff against spine `4d47c4362352ccd8d4d904134a79f0d8260b21b5`
was inspected through GitHub's compare endpoint. No other repository paths changed.

## PUBLIC API

- `Ina3221Sampler(*, sysfs_root="/sys", sample_interval_ns: int, update_interval_ms: int | None = None, averaging_window_ns: int | None = None, clock_domain="host.monotonic", clock=time.monotonic_ns, read_text=None)`
- `Ina3221Sampler.discover() -> tuple[Rail, ...]`
- `Ina3221Sampler.sample_once() -> None`
- `Ina3221Sampler.start() -> None`
- `Ina3221Sampler.stop() -> tuple[PowerTrace, ...]`
- `Ina3221Sampler.characterize(*, reads: int, sleep=time.sleep) -> Characterization`
- `Rail(channel, label, device, voltage, current)`
- `RailCharacterization(channel, read_latency_ns, distinct_periods_ns, quantum_w, voltage_quantum_mv, current_quantum_ma, flags=())`
- `Characterization(rails, update_intervals_ms, flags)`
- `TimelineModel(idle_w, prefill_base_w, prefill_token_w, context_token_w, decode_w, ripple_w, prefill_tokens_per_s)`
- `PowerInterval(start_ns, end_ns, mean_w, label, ripple_w=0, ripple_period_ns=None, ripple_origin_ns=0)`
- `Timeline(start_ns, end_ns, clock_domain, idle_w, intervals, flags=())`
- `Timeline.integral(start_ns, end_ns) -> float`: watt-nanoseconds.
- `Timeline.power_at(t_ns) -> float`
- `timeline_from_episode(episode: Episode, model: TimelineModel) -> Timeline`
- `SensorModel(sample_interval_ns, averaging_window_ns, duty_fraction, noise_sd_w, quantum_w, clock_offset_ns=0, clock_offset_uncertainty_ns=0, seed=0, source="mock", channel="synthetic", clock_domain=None)`
- `SensorModel.ina3221(*, cadence_ns, noise_sd_w, quantum_w, **kwargs) -> SensorModel`
- `SensorModel.nvml(*, noise_sd_w, quantum_w, **kwargs) -> SensorModel`
- `SensorModel.powermetrics(*, noise_sd_w, quantum_w, **kwargs) -> SensorModel`
- `simulate(timeline: Timeline, sensor: SensorModel) -> PowerTrace`
- `estimate_noise_sd(values: tuple[float, ...]) -> float`
- `Segment(start_ns, end_ns, mean_w, label, clock_domain="", sample_interval_ns=0, averaging_window_ns=0, flags=())`
- `ToolCallMatch(recall, precision, unmatched_logged, unlogged_candidates, flags=(), matched_count=0, tolerance_ns=0)`
- `detect_phases(trace: PowerTrace, *, noise_sd_w=None) -> list[Segment]`
- `match_tool_calls(segments: list[Segment], episode: Episode) -> ToolCallMatch`

## TESTS RUN

No Python test command ran. Executed tests: 0; passing/failing/skipped counts
are unavailable, not zero-result evidence. The source defines 17 new unittest
methods, which have not been collected by Python. All new code uses stdlib;
there are no extra-dependent tests and no packages were installed.

Two command attempts, `pwd` with workdir `/workspace` and later `pwd`
with workdir `/workspace/JouleWise`, both failed before shell launch:
"No usable execution environment is available. Wait for an environment to
become available before using this tool." A long-running
`wait_for_environment` request never returned readiness. Runtime status
alternated starting/pending, connectivity offline, failure null. Retained
diagnostic metadata had no records.

These are REQUIRED NEXT COMMANDS, not commands claimed as executed:

```sh
git -C /workspace/JouleWise fetch origin lane/2026-10-21-align-jetson
git -C /workspace/JouleWise checkout -B lane/2026-10-21-align-jetson origin/lane/2026-10-21-align-jetson
cd /workspace/JouleWise
python3 -m unittest discover -s tests/align -t .
python3 -m unittest discover -s tests
python3 -m tests.align.test_phase_detect --study
```

Fix failures only in the authorized scope, apply minimal registry additions
only if a registry test actually requires them, record real counts/results
here, then commit and push. No registry failure was observed from this seat.

Read-only independent arithmetic/review work used the explicitly selected
`gpt-6-astra` seat. It supplied a midpoint-quadrature error-bound oracle
and direct residual-sum split oracle; the parent integrated them as tests.
Neither oracle was executed. Review of `f4573344` found contextual-prefill
mislabeling, original-interval overwrite, lost token cycles during in-turn
waits, and gap ambiguity. Code/regressions address each; gaps/unknown windows
remain explicit flags. Delta inspection of `dfe91af1` confirmed those
changes by reading and found a missing duration-model-mismatch flag, now
restored with a regression. No fresh executing review is claimed.

## END-TO-END

The implemented chain is Episode -> timeline_from_episode -> simulate ->
detect_phases -> match_tool_calls, comparing a complete log with a copy
omitting one true call. It has NOT RUN. There are no measured recall or
false-alarm rates and no shortest passing duration to report.

Specified world inputs: four turns, 512 fresh tokens and 96 decode tokens
per turn; 2,048 fresh and 384 decoded tokens total; three tool waits; cached
context grows by 608 tokens per turn. Prefill is 256 ms at 2,000 tokens/s;
decode is 1.5 s at 64 tokens/s. Idle is 5 W, decode 13 W, prefill about 21 W
with explicit token/context coefficients, ripple amplitude 0.1 W. These are
synthetic configuration values, not measured instrument characteristics.

The study defines eight duration grid points (1/5/10/25/50/100/250/500 ms),
64 seeds per point, three sensors and separate null episodes without tools:
1,536 tool-bearing plus 1,536 null episode/sensor configurations, all pending.
The grid/budget are configurable simulation choices. False-alarm probability
has empirical resolution 1/64 per row. The reporting targets of at least 90%
recall and under 5% episode false alarms are supplied conventions, not physical
constants or confidence guarantees.

The INA scenario is explicitly a synthetic 1 ms full-window instrument,
not a measured Orin cadence. NVML is 100 ms / 25 ms duty-window sampling;
powermetrics is 100 ms whole-window averaging. Each uses specified 0.05 W
read noise and 0.01 W quantum. The study reports complete-call recall,
omitted-call recall and both tool-bearing/null episode false alarms.

## DECISIONS I MADE

- No unlisted source files or protected contracts were modified. Since no
  executor was available, public GitHub read/write tools created the lane
  from the spine and saved fast-forward checkpoints. No main push, force push,
  merge, PR creation or hardware session occurred.
- The sampler structurally implements PowerSampler. Unavailable devices,
  missing rails, permission errors, clamping, read loss and overruns remain
  notes/flags. Failed samples become gaps, never fabricated zero watts.
- Sysfs symlink aliases are resolved and deduplicated. Device path plus
  channel index preserves identity even when rail labels repeat.
- mV times mA divided by 1e6 gives watts. Acquisition timestamps are read-end
  times; voltage/current reads are not falsely treated as atomic.
- update_interval is read back and restored after sampling/probing. The first
  observed setting survives rediscovery. Restoration runs even after a probe
  fails. The requested scheduler interval is distinct from sensor cadence.
- Distinct-value periods and minimum observed nonzero steps are empirical
  observations. A flat signal does not prove a conversion period; insufficient
  changes are flagged. The datasheet's 840 us sweep is a comparison, never
  hardcoded as characterized cadence or ADC resolution.
- Timeline power coefficients are caller inputs. True activity includes
  unlogged turns/calls. Tool waits override turn envelopes; token ripple
  pauses through waits while preserving decoded-token count.
- Sensor windows end at sample timestamps. Duty never multiplies watts.
  Seeded Gaussian noise precedes quantization. No numpy or optional dependency
  is imported.
- Binary segmentation avoids a quadratic DP table for dense Jetson traces;
  its greedy short-balanced-trough limitation is disclosed. The BIC-style
  SSE penalty is 2 variance log(n), adding mean and location parameters.
- Noise uses first-difference MAD / (sqrt(2) Phi^-1(.75)); q-squared/12 bounds
  quantization variance. Level differences use the universal Gaussian noise
  excursion bound, and duration comparisons use the stated timeline model.
  All higher, shorter prefill groups can be labeled despite growing context.
- Segment's optional metadata is the lane-local adapter needed to retain
  clock domain, sample interval, window and flags through matching. Unknown
  windows, sample gaps, unsupported energy-counter input, flat traces and
  model mismatches remain explicit flags. Flagged gap segments may still span
  unavailable observations; they must not be interpreted as continuous proof.
- Matching converts trace time with Episode.clock_mappings and uses dt +
  averaging window + offset half-width. Both endpoints must agree, with
  one-to-one maximum-cardinality matching. Missing/ambiguous clocks are flagged.
- Empty-denominator recall/precision use vacuous 1 with explicit undefined
  flags. Unmatched low-power intervals are candidates, not proof of a tool.
- Numerical tests use required 1e-6 relative comparisons without physical
  uncertainty, or the independently derived quadrature/sampling-error bound.
  Scenario durations, coefficients and sample counts are explicit inputs.
- The Orin protocol remains PROVISIONAL. No real hardware, paid service,
  credential, test network access or installed extra is involved.

## CONTRACT-CHANGE

None. Existing records win. Trace notes carry acquisition flags, Episode
carries mappings, and optional Segment metadata preserves matching context.
No changes to PIPELINE.md, records.py or interfaces.py are requested.

## OPEN ISSUES

- Blocking: the selected cloud environment has no usable executor.
- All Python syntax/import checks, 17 new tests, align baseline, canonical
  suite, actual end-to-end measurements and duration study remain unexecuted.
- Obtain actual study curves and shortest passing grid duration per sensor.
  Do not infer these numbers from the unexecuted fixtures.
- Run a fresh executing independent review after tests can run.
- Borrowed Orin characterization and conversion/window validation are future
  physical work; all hardware claims remain provisional.
- Binary segmentation may miss short balanced troughs; robust differencing
  may confuse correlated sensor output or token ripple with read noise.
- Power cannot distinguish all idle causes and is blind to reasoning inside
  the same forward pass.

No repository file is missing or requires scope expansion. The precise
blocker is execution-environment readiness, not a missing contract.

## NEEDS_RULING

None. Restore a usable /workspace/JouleWise executor and continue from this
lane head; no research-methodology ruling is needed to run the pending checks.
