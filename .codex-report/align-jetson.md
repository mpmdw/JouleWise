# align-jetson — FIX ROUND 1

## SUMMARY

Continued the existing lane from 08b493a1e; all fixes below are SOURCE-ONLY and UNVERIFIED.
INA characterization now reports endpoint-span cadence and propagates voltage/current steps to watts.
Traces carry driver exposure, averaging samples, resolution provenance and cadence-disagreement flags.
The sampler records alarms, L4T OC counter deltas and timestamped voltage extrema for supply checks.
Phase detection handles held observations, consolidates mixed edges and models local token variation.
Matching counts visible calls inside a logged idle run and marks per-call timing there unresolved.
The production study uses 30 turns, result-fed context, client gaps, mixed calls and exact binomial bounds.
Added 16 unittest regression methods; original test assertions were preserved.
Execution remains BLOCKED: the managed environment never became usable; no tests or study ran here.
No post-fix sensitivity result, shortest duration, hardware result or passing-test count is claimed.

## FILES

- `joulewise/align/power/ina3221.py`: summation-channel exclusion; mean cadence; propagated watt resolution; driver/supplied/inferred exposure; alarm/warning snapshots; separate L4T OC counters; voltage extrema.
- `joulewise/align/phase_detect.py`: held-cadence inference and thinning; distinct-change MAD; local nuisance variance; complete-span level grouping; mixed-edge handling and adjacent-label merging; logged idle-run matching; read-gap uncertainty and indeterminate candidates.
- `joulewise/align/sensor_sim.py`: cached interval endpoints and bounded analytic integration for long, dense traces; contribution order is preserved.
- `tests/align/test_power_ina3221_review1.py`: seven additional regression methods, including real fake-sysfs acquisition -> phase detection -> matching, cadence quantization, product resolution, alarms and advancing/missing OC attributes.
- `tests/align/test_phase_detect_review1.py`: eight additional methods: held reads; shared-call/client-gap matching; low-noise ripple; missing reads; scheduler jitter; production transition edges; closed-form binomial oracles; resolution derivation.
- `tests/align/test_sensor_sim.py`: unchanged world()/model(); new production_world() and one long-world/analytic-energy regression.
- `tests/align/test_phase_detect.py`: unchanged sensor_models() and original six test methods; production sensor set, exact binomial intervals and rewritten default duration study.
- `docs/align/jetson_characterization.md`: corrected cadence/resolution interpretation, supply/throttle preflight, verified counter path, study assumptions and explicit execution blocker.
- `.codex-report/align-jetson.md`: this report.

No registry was changed. No change to PIPELINE.md, records.py, interfaces.py,
power/__init__.py, existing sampler tests or any other repository path.
GitHub compare against 08b493a1e confirmed the eight source/test/doc paths
before this report was written; the report is the ninth authorized path.

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

## TESTS RUN

Executed Python tests: **0**. Collection, pass/fail and skip counts are
unavailable. Sixteen new methods were counted in source (seven sampler,
eight detector, one simulator); this is not a collected or passing count.
The reviewer's 21 passing tests at 08b493a1e are supplied pre-fix evidence,
not a result from this seat or the current tree.

These exact executor attempts failed before any shell/process launched,
with "No usable execution environment is available. Wait for an environment
to become available before using this tool.":

```sh
pwd
git status --short --branch
git fetch origin lane/2026-10-21-align-jetson
python3 -m unittest discover -s tests/align -t .
python3 -m unittest tests.test_battery_float_consumers tests.test_battery_float_sweep
```

The Python/git attempts used workdir /workspace/JouleWise; pwd was also
attempted with /workspace. No local checkout, status inspection, file write,
mkdir, script materialization, test run, pip install or hardware work could
execute. The requested environment wait never returned readiness.
Runtime status repeatedly reported starting/pending, connectivity offline,
failure null. Retained diagnostic metadata returned history_status=not_found
and records=[]; no diagnostic log contents were requested.

GitHub's connected public repository tools were the available fallback:
read the existing report and protected contracts first; confirmed the exact
existing branch head; created commits using its tree; fast-forwarded only
lane/2026-10-21-align-jetson with expected-head checks and force=false.
No local git command, force push, other-branch push, PR or CI run is claimed.
No extras were installed; all new code/tests are stdlib-only, with no
extra-dependent tests or test network access. The whole repository suite
was not run, as this fix brief expressly forbids it.

The mandatory next commands remain the following, after restoring an
executor and fetching/checking out the current lane head. They have NOT RUN.
First write every appendix script verbatim under .review1/; that directory
could not be materialized in this seat and must remain uncommitted.

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

For e13 only, the brief expressly allows adapting the print line to the
chosen cadence field. Replace BOTH accesses to
r.median_distinct_period_ns on that print line with r.cadence_ns.
Do not alter a world, seed, sensor, poll period, conversion period or bar.
This is the required planned attribute adaptation; no .review1 copy exists
here yet, so it is not represented as an executed edit.

## END-TO-END

No end-to-end world has executed in this seat. All post-fix counts below
remain unavailable: matched calls, unlogged candidates, time-label accuracy,
detected/true-prefill counts by sensor, shared-run concealment fraction,
sensitivity curves, point-estimate shortest duration and bound-based shortest
duration. In particular, the requested M1/M5 numbers are NOT delivered.

Prepared production chain:
Episode -> timeline_from_episode -> simulate -> detect_phases ->
match_tool_calls, comparing complete, uniformly selected omitted-call,
isolated omitted-call and second-back-to-back-call omitted logs.
Separate no-tool controls retain multiple model turns but remove the tool
round-trip/client waits. This controlled null does not establish immunity
to arbitrary non-tool pauses.

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

The real-sysfs regression uses the unchanged four-turn world, a 4 ms
conversion held across 1 ms polls, and production discovery/read/stop paths
before real detection/matching. It asserts all three calls and zero false
candidates with estimated or supplied read sd. The regression is written,
not executed.

## DECISIONS I MADE

- Continue from the existing 08b493a1e lane, never restart from spine.
  Use connected GitHub fast-forward checkpoints while the executor is
  unavailable; preserve all work exclusively in the exhaustive scope.
- The records contract remains authoritative. Segment metadata and trace
  notes are lane-local adapters; no shared record or protocol was edited.
- Do not weaken any original assertion. The original six phase-test methods
  were compared as text and remain identical; existing sampler tests were
  not edited. world(), model() and sensor_models() retain their fixed worlds.
- Keep the literal median cadence property for compatibility; expose the
  endpoint-span estimate as cadence_ns and adapt only e13's allowed field
  access when the scratch probes can be written.
- A change every poll is poll-limited. The flag uses the brief's one-poll
  ambiguity: median observed change period <= two actual poll periods.
- Skip the mainline shunt summation label with a recorded flag; preserve
  other missing rail attributes as observable failures.
- Watt quantum is propagated at median observed V/I using
  (abs(V)*dI + abs(I)*dV + dV*dI)/1e6 for mV/mA. Product cancellation is
  not a power LSB. A constant coordinate is flagged as unobserved.
- Driver update_interval already incorporates averaging samples. Record
  both; never multiply samples into it a second time. Use supplied
  characterization where available; observed held cadence may conservatively
  widen exposure with an inference flag. Disagreement beyond one poll is flagged.
- Without a supplied board shunt/current characterization, integer-mA print
  precision is explicitly only a lower resolution bound, not an ADC claim.
  The production study separately derives its current LSB from the public
  P3767 5000-micro-ohm device tree.
- Snapshot all exposed alarms/warnings plus mainline critical/max alarm
  paths at start/stop. Discover OC counters at the documented class/hwmon
  path independently of INA rails, resolve aliases, retain missing/read
  failures and counter resets, and flag positive episode deltas.
- Supply limiting and OC throttling change the workload, not just the meter.
  Keep alarms/counters and timestamped input-voltage extrema. The protocol
  requires an idle/load supply-and-cable check without raising protection limits.
- Detector held-read treatment is sensor-independent. Preserve duration
  weights of truly constant plateaus; infer cadence from numerous changes
  rather than mistaking two long plateaus for slow conversions.
- Penalized binary segmentation remains practical for dense traces. Estimate
  local correlated variation at dyadic lags bounded by one exposure plus one
  sample, preventing slow sensors' seconds-scale true phases from becoming
  the noise floor. No fixed ripple-amplitude threshold was introduced.
- Complete-span grouping prevents transition chaining. Mixed exposures borrow
  neighboring sustained labels; significant short bursts above sustained
  decode remain prefill. Merge equal neighboring labels and compare duration
  rules on complete phase runs, not individual ripple leaves.
- A sample gap needs >= two nominal periods (one missed acquisition).
  Touching boundaries carry uncertainty enlarged by the missing interval.
  An unmatched trough with such uncertainty is indeterminate, not an unlogged
  candidate. Matching tolerance includes sample cadence, exposure, clock
  half-width and boundary-gap uncertainty.
- Build idle runs from the VISIBLE generation envelopes and visible tool
  intervals, extended to the next logged activity. All visible calls inside
  a matched run count toward recall. Their individual timing is unresolved;
  precision counts troughs/runs and cannot exceed one.
- A hidden call immediately after a logged call in the same idle run is
  unidentifiable by power. The study measures this separately and also uses
  a uniformly chosen omission as its main hidden-call population, preventing
  an isolated-only sensitivity curve from standing in for mixed-call recall.
- Pooled logged-call recall is descriptive. CP intervals use independent
  episode trials for one omitted call or any false alarm; correlated calls
  within one episode are not falsely treated as independent binomial trials.
- Cached interval endpoints accelerate analytic convolution while preserving
  the prior contribution order and units; no optional dependency was added.
- No live Orin work, paid service, hardware measurement, external messages,
  scope expansion, main push, force push, merge or whole-suite run occurred.

## CONTRACT-CHANGE

none. Optional fields appended to Segment/ToolCallMatch are lane-local.
PowerTrace.notes preserves sensor provenance and health snapshots.

## FIX LOG

"fixed" below means a source implementation was saved at the named commit,
NOT that the reviewer's pass conditions were executed or proven. Every
executing verification remains OPEN because the executor never became usable.

- JET-B1 — fixed in source 6811295b7e75dcf9f2702f294874dd5c25baedae; sampler-to-matcher regression added in 70c41860d77822687a454bc71565cddcfe11567c. Held cadence/noise/timing are handled in the detector itself. Verification blocked.
- JET-B2 — fixed in source 9cf7e8d9a947075c8a4a73901b3a61308ef2469d (initial idle-run matcher eea481251c601d77ca7864f0fd1d5e1aba748e20). Count all logged calls within a matched idle run; timing unresolved. Shared hidden-call concealment is instrumented but not measured.
- JET-M1 — fixed in source 6811295b7e75dcf9f2702f294874dd5c25baedae; mixed edges cannot chain levels, equal labels merge, and short significant prefills survive. Required per-sensor detected/true counts and repro outcomes remain unavailable.
- JET-M2 — fixed in source 975b64bed66a537206b9db0656d202ba75ba4b17, refined in 171a35fdda705966b3dcfe95afe383b1255cbe9a; driver exposure/samples/resolution and held-cadence disagreement are retained. Verification blocked.
- JET-M3 — fixed in source 2da5667c03d93cc1c67eedd9a96dec83e1ceb9f7: cadence_ns is the endpoint-span estimate; poll limitation is flagged. Planned allowed e13 adaptation replaces both median-property accesses with cadence_ns; no world/parameter changes. Probe file could not be materialized.
- JET-M4 — fixed in source 2da5667c03d93cc1c67eedd9a96dec83e1ceb9f7: propagate V/I steps including the product term; corrected doc interpretation. Verification blocked.
- JET-M5 — fixed in source 9cf7e8d9a947075c8a4a73901b3a61308ef2469d (production study introduced 171a35fdda705966b3dcfe95afe383b1255cbe9a); actual study outputs, point/bound shortest durations and reporting numbers remain OPEN and undelivered.
- JET-M6 — fixed in source 6811295b7e75dcf9f2702f294874dd5c25baedae: local modulation envelope, phase consolidation and run-duration comparisons; low-noise and one-turn behavior still need execution.
- JET-m1 — fixed in source 2da5667c03d93cc1c67eedd9a96dec83e1ceb9f7: flag/skip shunt sum, preserve genuine missing rail diagnostics. Verification blocked.
- JET-m2 — fixed in source eea481251c601d77ca7864f0fd1d5e1aba748e20: >=two nominal periods defines a missed-read gap. Real-thread repro still pending.
- JET-m3 — fixed in source eea481251c601d77ca7864f0fd1d5e1aba748e20: boundary-gap uncertainty, widened matching and separate indeterminate troughs. Verification blocked.
- JET-m4 — fixed in source 975b64bed66a537206b9db0656d202ba75ba4b17, refined in 171a35fdda705966b3dcfe95afe383b1255cbe9a and 9cf7e8d9a947075c8a4a73901b3a61308ef2469d: alarms, separate documented L4T counters, read-loss flags, voltage extrema and physical-hazard preflight; fake-sysfs tests written, not executed.

## OPEN ISSUES

- BLOCKING: no usable execution environment for /workspace/JouleWise.
  No repository file is missing; the missing capability is the executor.
- Every reviewer repro, all alignment tests, both battery-float census
  modules, Python syntax/import collection and all new regressions must run.
  Do not interpret any FIX LOG entry as a verified pass.
- .review1/ and /tmp/jetson-review could not be created. Materialize the
  appendix scripts verbatim, then make only the allowed e13 attribute edit.
- Required study rates, per-sensor true/detected prefill counts, shortest
  duration from point estimates and bounds, and actual seed-budget timing
  remain unavailable. Run the default study or reduce its budget honestly
  if measured runtime is too slow; do not substitute the reviewer's old
  four-turn numbers.
- The requested observed fraction of hidden calls concealed inside matched
  idle runs is NOT MEASURED. The new shared_run_concealed/shared_run_trials
  fields produce it; report numerator, denominator and rate after execution.
- Binary segmentation is greedy and may miss short balanced troughs.
  Every changed detector assumption needs the supplied production repros.
- The default 64-episode budget cannot certify under-5% false alarms with a
  two-sided 95% CP interval even at zero alarms; point/bound answers must
  remain distinct and any required choice goes under NEEDS_RULING.
- The null control removes tool/client waits; unrelated idle pauses remain
  physically confounded with tool waits. Power cannot split calls in the
  same idle run or identify reasoning within one forward pass.
- New binomial code has closed-form arithmetic regressions; no executing
  independent/cross-model review of this fix tree has occurred.
- Actual borrowed-Orin shunt, cadence, averaging, analog noise, sampling
  overhead, supply behavior and all live instrument viability remain
  PROVISIONAL.

## NEEDS_RULING

none yet. Execution readiness is an infrastructure blocker, not a choice
about which data count. After the study runs, copy both shortest-duration
answers here if point estimates and 95% bounds differ, as the brief requires.
