# align-jetson — FIX ROUND 3 (JET3)

## SUMMARY

Continued the pushed lane from b1613dad6; all code remains stdlib-only.
Removed episode-value inference from cadence, thinning and noise handling.
INA notes declare refresh period, provenance, uncertainty and register age per rail.
The detector carries declared age through exposure, observations and matching.
Added an optional seeded register simulator and an appended 840 us / 1 ms INA study row.
Added measured settling as a timing parameter and a first-board step-response protocol.
Wholly uncovered calls are reported separately and excluded from recall.
Absent alarm attributes no longer generate read-error flags; present-path failures remain visible.
Execution remains unavailable: no tests, probes or study ran in this round.
Source changes are APPLIED_UNVERIFIED; no scientific acceptance or new detection limit is claimed.

## FILES

- `joulewise/align/power/ina3221.py`: configuration/characterization timing notes, settling metadata, characterization retention, existing-path alarm discovery.
- `joulewise/align/phase_detect.py`: declared-timing thinning and latency propagation, settling terms, outside-coverage reporting.
- `joulewise/align/sensor_sim.py`: optional register period and seeded conversion phase; old default arithmetic and notes preserved.
- `tests/align/test_phase_detect.py`: appends held-register INA study row; original three rows and index 0 unchanged.
- `tests/align/test_phase_detect_review1.py`: authorized setup-only hold-period declaration.
- `tests/align/test_phase_detect_review2.py`: authorized setup-only declaration plus timing/dither/coverage regressions.
- `tests/align/test_power_ina3221_review1.py`: authorized changing-load characterization setup plus alarm and timing-note regressions.
- `tests/align/test_sensor_sim.py`: default compatibility oracle and seeded register end-to-end regression.
- `docs/align/jetson_characterization.md`: updated timing, step response, flags and execution status.
- `.codex-report/align-jetson.md`: this report, retaining Round 1/2 FIX LOG and open observability ruling.

No registry or power/__init__.py edit. No frozen contract file changed.
No scratch probe file is committed. Without an executor the requested
.review3 files could not yet be materialized in /workspace/JouleWise.

## PUBLIC API

Existing signatures retain their positional arguments. Appended keyword/default fields:

```python
Ina3221Sampler(*, sysfs_root="/sys", sample_interval_ns: int,
    update_interval_ms=None, averaging_window_ns=None, characterization=None,
    shunt_resistance_ohm=None, settling_time_ns: int | None = None,
    clock_domain="host.monotonic", clock=time.monotonic_ns, read_text=None)
Ina3221Sampler.discover() -> tuple[Rail, ...]
Ina3221Sampler.start() -> None
Ina3221Sampler.sample_once() -> None
Ina3221Sampler.stop() -> tuple[PowerTrace, ...]
Ina3221Sampler.characterize(*, reads: int, sleep=time.sleep) -> Characterization
SensorModel(sample_interval_ns, averaging_window_ns, duty_fraction, noise_sd_w,
    quantum_w, clock_offset_ns=0, clock_offset_uncertainty_ns=0, seed=0,
    source="mock", channel="synthetic", clock_domain=None,
    register_refresh_period_ns: int = 0, conversion_phase_ns: int | None = None)
SensorModel.ina3221(*, cadence_ns, noise_sd_w, quantum_w, **kwargs) -> SensorModel
SensorModel.nvml(*, noise_sd_w, quantum_w, **kwargs) -> SensorModel
SensorModel.powermetrics(*, noise_sd_w, quantum_w, **kwargs) -> SensorModel
simulate(timeline: Timeline, sensor: SensorModel) -> PowerTrace
timeline_from_episode(episode: Episode, model: TimelineModel) -> Timeline
estimate_noise_sd(values: tuple[float, ...], *, hold_period_ns: int = 0,
    sample_interval_ns: int = 0) -> float
detect_phases(trace: PowerTrace, *, noise_sd_w: float | None = None,
    hold_latency_ns: int | None = None,
    register_refresh_period_ns: int | None = None,
    settling_time_ns: int | None = None) -> list[Segment]
match_tool_calls(segments: list[Segment], episode: Episode) -> ToolCallMatch
```

Segment appends `hold_latency_ns=0, settling_time_ns=0` after its existing
power_uncertainty_w field. ToolCallMatch appends
`outside_trace_logged: tuple[ToolCall, ...] = ()`. Wholly uncovered calls are
excluded from unmatched_logged and recall's denominator and retained in that
new field. Existing recall/matched_count and precision semantics otherwise remain.

Timing notes are per trace: register_refresh_period_ns, register_refresh_source,
register_refresh_print_half_width_ns,
register_refresh_characterization_half_width_ns, hold_latency_ns and
settling_time_ns. Characterization supplies P preferentially; otherwise driver
update_interval supplies it; otherwise it is null with a rail-specific flag.
detect_phases keyword values override the respective JSON values. No declaration
means zero latency and no thinning, regardless of source or repeated values.

TimelineModel, PowerInterval, Timeline, Rail, RailCharacterization and
Characterization signatures are unchanged. characterize() now retains its
returned calibration on the sampler and clears rehearsal samples before the
episode. _held_change_indices remains importable only as a legacy diagnostic;
no acquisition/detection/noise path calls it. Existing study keywords and row
keys are unchanged, with four production sensors instead of three.

## TESTS RUN

**Nothing ran in this round. No pass, count, skip count, Python version or runtime
is claimed.** Repeated `exec_command({"cmd": "pwd"})` attempts failed before
launch with "No usable execution environment is available." The supported
environment wait remains pending; status progressed from pending to starting
with connectivity offline. No optional dependency was installed.

The requested commands still to run when execution is available:

```sh
python3 -m unittest discover -s tests/align -t .
python3 -m tests.align.test_phase_detect --study
TMPDIR=/tmp/jetson-review3 python3 -I /workspace/JouleWise/.review3/r3_sampler.py /tmp/jetson-review3 1100 1000 8 12 12
TMPDIR=/tmp/jetson-review3 python3 -I /workspace/JouleWise/.review3/r3_sampler.py /tmp/jetson-review3 840 1000 8 12 12
TMPDIR=/tmp/jetson-review3 python3 -I /workspace/JouleWise/.review3/r3_sampler.py /tmp/jetson-review3 1500 1000 8 8 12
WINDOW_NS=2200000 TMPDIR=/tmp/jetson-review3 python3 -I /workspace/JouleWise/.review3/r3_sampler.py /tmp/jetson-review3 1100 1000 8 12 12
LANEWORLD=20000000 TMPDIR=/tmp/jetson-review3 python3 -I /workspace/JouleWise/.review3/r3_sampler.py /tmp/jetson-review3 1100 1000 8 8 30
TMPDIR=/tmp/jetson-review3 python3 -I /workspace/JouleWise/.review3/r3_sampler.py /tmp/jetson-review3 1100 1000 8 12 12 none nolatency
TMPDIR=/tmp/jetson-review3 python3 -I /workspace/JouleWise/.review3/r3_sampler.py /tmp/jetson-review3 1100 500 8 12 12
TMPDIR=/tmp/jetson-review3 python3 -I /workspace/JouleWise/.review3/r3_sampler.py /tmp/jetson-review3 2000 1000 8 8 12
TMPDIR=/tmp/jetson-review3 python3 -I /workspace/JouleWise/.review3/r3_sampler.py /tmp/jetson-review3 3000 1000 8 8 12
TMPDIR=/tmp/jetson-review3 python3 -I /workspace/JouleWise/.review3/r6_study_held.py 5 0 24
TMPDIR=/tmp/jetson-review3 python3 -I /workspace/JouleWise/.review3/r6_study_held.py 5 24 48
TMPDIR=/tmp/jetson-review3 python3 -I /workspace/JouleWise/.review3/r6_study_held.py 5 48 72
TMPDIR=/tmp/jetson-review3 python3 -I /workspace/JouleWise/.review3/r6_study_held.py 2 0 24
TMPDIR=/tmp/jetson-review3 python3 -I /workspace/JouleWise/.review3/r4_heldfalse.py 5 12
TMPDIR=/tmp/jetson-review3 python3 -I /workspace/JouleWise/.review3/r4_heldfalse.py 5 12 1000
TMPDIR=/tmp/jetson-review3 python3 -I /workspace/JouleWise/.review3/r5_edges.py 3
TMPDIR=/tmp/jetson-review3 python3 -I /workspace/JouleWise/.review3/e12_thread.py /tmp/jetson-review3
```

Also pending: r9_dither_study.py plain/dither A B 1,2,5 for A/B
0/18,18/36,36/54,54/72; r1_null.py jetson 6 decay5 ina1.1ms,
jetson 6 decay10 ina1.1ms, jetson 12 decay50, and jetson 6 decay2 ina1.1ms.
The settling probes need the authorized argument supplying the measured term;
no script port has been made yet. All non-exempt probes need both b1613dad6
and final-source executions; no baseline probe was executed by this seat.
No whole-repository suite ran. No registry reader is needed: no registry edit.

Historical preceding-seat evidence: the branch report at b1613dad6 records
46 align tests, zero skips, Python 3.12.14 and a 1181.322 s study. These are
not executions by this seat and do not validate this source.

## END-TO-END

No new executed world or study numbers. New regression worlds are ready in
source: four realistic turns with 512 prefill and 96 decode tokens per turn,
three 250 ms tool calls, ripple, growing context, and register periods 840 us,
1.5 ms and 4 ms at 1 ms polling. The chain is Episode -> timeline_from_episode
-> simulate -> detect_phases -> match_tool_calls, with a physically unchanged
trace and a hidden-call log copy. A separate fake-sysfs chain rehearses a
4 ms changing conversion under a misreporting 1 ms driver, then samples the
episode through Ina3221Sampler.sample_once/stop -> detector -> matcher.
These are test scenarios, not executed results.

The unchanged default study grid is 1,5,10,25,50,100,250,500 ms, now four sensors,
72 seeds and four physical worlds per row: **9216 traces (derived 8*4*72*4)**.
The existing INA row remains index 0 and never holds. The appended register
row uses 840 us conversions, seeded uniform conversion phase and 1 ms polls,
with the original INA row's quantum/noise. 840 us is a scenario parameter from
140 us * bus/shunt * three enabled channels, replaced by hardware characterization.
Unheld defaults keep the original arithmetic and JSON notes.

No current point or 95%-bound shortest duration is claimed. Reviewer-measured
at b1613dad6, dithered counterfactual: INA 1 ms mid 8/72, stretch 59/72;
2 ms mid 51/72, stretch 72/72; 5 ms mid 72/72. The reviewer predicts a 5 ms
point and 95%-bound answer, with CP lower about .950 at 72/72. This prediction
is not a current study run. The prior printed 10 ms bound is superseded as
a current claim until the configuration-based detector is executed.
The 90% recall / under-5% FA targets and 95% coverage remain reporting
conventions; the 72-seed zero-FA bound is derived, not observed this round.

## DECISIONS I MADE

- Followed the user's explicit Round 3 cadence authority: no episode-value
  inference feeds sampling, latency, window, noise or labels.
- Driver P is rounded to integer ms, so its upper endpoint adds 0.5 ms,
  half one printed unit. Characterized P instead adds one actual poll
  (requested poll plus maximum measured read latency) divided by observed
  periods, from the two endpoint poll errors. Characterization is preferred.
- Observation uncertainty adds register age even when every value differs.
  Exposure bins include window + hold latency + measured settling, because
  all three can spread a step. Matching adds those terms, clock half-width
  and missing-read uncertainty by the triangle bound.
- Thinning uses declared P against poll interval. A trace declaring nothing
  follows records.py: exposure ends at t_ns and hold latency is zero.
- estimate_noise_sd can subsample by explicit timing; it never drops samples
  by value. detect_phases estimates on its already timing-thinned values.
  The existing out-and-back rounding floor and plateau-zero test are retained.
- Unknown settling is flagged per INA rail and defaults to zero. Supplied
  settling_time_ns is a measured timing input, never a fitted constant.
- Chose separate reporting plus denominator exclusion for wholly uncovered
  logged calls. Partial coverage keeps the existing trace-edge path.
- Existing alarm paths remain cached, so losing one later still records
  health_read_error. Attributes never present produce only availability flags.
- Retained all original assertions and scenarios; changed only the three
  specifically authorized held-fixture setups. Added independent regressions.
- Appended the held INA study row without changing the three existing rows,
  index 0, duration grid, keywords or output keys. Did not add 2 ms to the
  default grid; the required r6/r9 probes independently exercise it.
- Used connected GitHub to checkpoint while execution is unavailable, with
  fresh remote-head reads, expected-head checks and force=false. No merge
  was needed at the first checkpoint; remote was b1613dad6.
- Explicit bounded user work takes priority over unrelated generated queue
  entries. No live hardware, external message, paid service or main push.
  The open observed-evidence ruling remains; elapsed time is not an answer.

## CONTRACT-CHANGE

Request explicit PowerTrace.register_refresh_period_ns, hold_latency_ns and
settling_time_ns (with provenance/uncertainty). Until then the documented
per-trace JSON notes keys above are the lane-local adapter. Segment and
ToolCallMatch additions are lane-local. PIPELINE.md, records.py and
interfaces.py are unchanged. The records statement that windows end at t_ns
needs this age term for physical INA registers.

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

"fixed" below means source implemented, **UNVERIFIED**, not a claimed repro pass.
Before summaries are reviewer-measured at b1613dad6; no before or after command
was executable in this seat.

- JET3-B1 — fixed in 530671e6c9c177dfbac6d88cffe2acf9bf73e5ad (source; follow-up regression/uncertainty commit pending). Before: "1100/1000 us FA 11/12; 840/1000 us 8/12; 1500/1000 us 6/8"; after: "NOT RUN — executor unavailable". Every seed's FA, matching and prefill non-regression bar remains unverified, as does the appended study row.
- JET3-M1 — fixed in 530671e6c9c177dfbac6d88cffe2acf9bf73e5ad (source). Before: "held inferred 71/72; mid hidden recall 67/72; with 1e-9 W dither 72/72"; after: "NOT RUN — executor unavailable". r4/r6/r9 equality and the full study are pending; no replacement scientific figures are asserted.
- JET3-m1 — fixed in 530671e6c9c177dfbac6d88cffe2acf9bf73e5ad (parameter/propagation source; protocol follow-up pending). Before: decay5 "FA episodes 2/6", recall "162/227"; decay10 "6/6", "79/227"; decay50 "11/12", "259/418"; after: "NOT RUN — executor unavailable". Both source and protocol require executable verification; no r1 script adaptation made yet.
- JET3-m2 — fixed in 530671e6c9c177dfbac6d88cffe2acf9bf73e5ad (source). Before cropped lines: "recall .545/.455 flags []"; after: "NOT RUN — executor unavailable". outside_trace_logged reports excluded calls; full/clock-control flag checks remain pending.
- JET3-m3 — fixed in 530671e6c9c177dfbac6d88cffe2acf9bf73e5ad (source; new regression pending commit). Before: "health_read_error ... FileNotFoundError" for absent alarms; after: "NOT RUN — executor unavailable". e12 and present-alarm read-failure checks remain pending.
- Authorized setup-only change: test_held_reads_with_estimated_and_supplied_noise declares each scenario's P and window; every hold scenario/assertion retained. Value-based inference is intentionally removed.
- Authorized setup-only change: test_held_noninteger_ratio_noise_is_nonzero_and_calls_survive declares 1.5/1.9 ms P in notes; all assertions retained.
- Authorized setup-only change: test_real_sysfs_path_through_detector_with_held_conversions runs characterize() under a changing load before episode sampling; driver still says 1 ms and episode converts every 4 ms. All assertions retained.

## OPEN ISSUES

- **No execution environment.** No syntax check, align test, baseline/final
  repro or full study ran. APPLIED_UNVERIFIED; the lead must execute all
  required commands and assess every seed, including prefill non-regression.
  No failing lines are available to diagnose because no process could launch.
- No live Orin validation. Cadence, shunt, read skew, settling, analog noise,
  clock mapping, power supply and polling overhead remain PROVISIONAL.
- The optional settling source requires the specified decay probes and a
  measured protocol value before a pass can be claimed.
- Value-based hold inference is removed; a wrong or unknown configuration
  remains a flagged instrumentation limitation, not an inferred substitute.
- Greedy segmentation and shared-run concealment limits remain. Prior-round
  short-call/prefill sensitivity findings are preserved in FIX LOG and ruling.
- No missing repository file. The unavailable capability is execution, which
  also prevents materializing the supplied scratch scripts and their outputs.

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
