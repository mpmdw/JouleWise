```json
{"schema":"claude-codex-report/v1","genre":"review","status":"findings","completion":"complete","summary":"Activation requires floor-pipeline confirmation.","workspace":{"base_requested":"bookkeeping/2026-09-18-activation-d8ca3a36","base_mode":"exact","head_start":"00e16fedaf1e1fe8a9a7f941e1d6e2f362ab42f1","head_end":"00e16fedaf1e1fe8a9a7f941e1d6e2f362ab42f1","upstream_end":null,"branch":null},"pathspec":[],"unowned_dirty":[],"verdict":{"findings":[{"id":"F1","severity":"blocker","text":"Q4 activation evidence remains insufficient."}]},"verification":[{"id":"V1","kind":"inspection","cmd":"git diff --exit-code && git status --short --branch && git rev-parse HEAD","cwd":".","observed":{"result":"pass","exit_code":0,"tail":["## HEAD (no branch)","00e16fedaf1e1fe8a9a7f941e1d6e2f362ab42f1"]},"expected":{"exit_code":0,"tail_regex":"00e16fedaf1e1fe8a9a7f941e1d6e2f362ab42f1$"}}],"flags":[{"id":"R1","kind":"lead_ruling","level":"blocking","text":"Activation blocker.","needs":"Rule budget/boundary and authorize calibrated v2 confirmation."}]}
```

## Findings

**F1 — Activation remains blocked.**

**6. Harness.** `scripts/sample_quiet_predicate_evidence.py collect --state NAME --repeat ID --duration-s 480 --sample-interval-s 30 --power-interval-ms 100 --out DIR`; add `load` (§3) and offline `summarize`. Bench command:

`sudo -n /usr/bin/powermetrics -b 0 -i 100 --samplers cpu_power,gpu_power,ane_power,thermal --format plist -o RAW`

Bound/reap at 480 s; mark the incomplete final round. Argv: `joulewise/adapters/powermetrics.py:1472`; 100 ms matches r6. Bench-verify; 1000 ms CPU-only pilots differ.

Use `scripts.run_night.smoke_observation_round`; scope raw/stamp hooks.

One JSONL row/attempt, schema v1:
`{session,state,repeat,round,status,error,epoch,boot_id,load_setting,round_wall_start/end,round_mono_start/end,observation,observer_cpu_s,power:{cpu_w,gpu_w,ane_w,rail_sum_w,combined_w,dram_w,coverage_s},clusters:[{name,active_ratio,idle_ratio,down_ratio,online_ratio,freq_hz,cpus}],alignment:{anchor_lo/hi,ps_start/end,top_start/end,error_bound_j},raw:{paths,sha256}}`.
Keep observation/census, raw files, argv/identities; missing=null+reason. Bracket wall reads with monotonic reads; align native timestamp+elapsed_ns using the rate-aware anchor. Integrate support overlaps, not arrival times. Expose ps/top/round mismatch (`joulewise/quiet_admission.py:244`). Reuse capture telemetry.

No-sudo tests with fake clocks/processes: framing, units/missing rails, clock gaps, overlap/span mismatch, child accounting, census, duty control, cleanup, constant/B-only ABBA. Run canonical suite.

**7. Memo.** Pin dates/argv/epoch/hashes. AFFIRM/REJECT separately: (a) boundary/metric; (b) alignment/load validity; (c) clean distribution/observer; (d) candidate/10×/contaminant evidence; (e) contamination budget/margin; (f) Q4: “C*=NUMBER total busy cores is adequate for CLASS on Mac15,9/25G83, cpu_interval_v1, 30 s, k=2.” Include counterevidence/uncertainty; freeze C* before confirmation, not now.

**1. Co-recording fails item 1.** The Mac floor measures CPU+GPU+ANE, not external AC (`docs/contracts/measurement_methodology.md:249`). An external meter is needed for a separate whole-machine claim.

ABBA d=(B1+B2−A1−A2)/2 (`joulewise/detection_floor.py:1449`). Floor: max|d|, |mean(d)|+t·s·sqrt(1+1/n), small-n guard and uncertainty-set maximization (`:871`, `:1132`); anchor propagation: `joulewise/floor_extraction.py:2710`.

Use separate v2 DIAGNOSTIC_NO_PACK payloads: legacy admission, settle, prescribed loads. At baseline/C*/10C*, run null ABBA with load across all members, plus B-only controls exposing cancellation. Replay phase/request energies and widened floors. Plan 10 blocks/condition; five is the minimum (`detection_floor.py:121`). Twelve slots yield three blocks: use multiple windows, preserving derivation plans.

Agent-free measurement costs quiet time. Telemetry misses interaction/cancellation/widened floors; Q4 stays refused.

**2. States.** After 600 s initial settle, collect three separated 480 s runs/state; stabilize 120 s after load changes. Clean controls: census-empty recorder-only idle, then full observer with/without recorder. Close every agent session. Report quantiles and session variability.

Pilot added loads: 0, .05, .1, .2, .5, 1, 2 cores, with §3 profiles. Confirm total C*/10C*. Clean, observer, synthetic and CPU-heavy daemon evidence are essential. Sample Spotlight/filesystem churn and mediaanalysisd for three 480 s episodes when reproducible, recording attribution/recovery; media work tests accelerator blind spots. Claude/Codex idle/active sessions, three 480 s episodes each, are ancillary census controls: census already vetoes them. Avoid forced system-wide rescans.

**3. Generator.** `load --cores S --duration-s 600 --period-ms 100 --qos background|user-initiated --profile scalar|memory --seed N`. Native workers budget S×elapsed CPU-seconds with thread CPU clocks, absolute sleep deadlines and bounded overshoot. Preallocate; log PID/start, CPU and overruns. Calibrate then freeze duty.

Require worker delta within max(.01 core,5%S); aggregate within paired observer-idle+S ±max(.02 core,10%S) for ≥90% of rounds, with first/last-third drift within that band. Otherwise flag nonstationarity. busy_cores=max(host,process), not worker setting (`quiet_admission.py:157`). C*/10C* mean TOTAL pre-capture idle readings; report injected increments separately and keep them fixed during workload captures.

QoS influences, not guarantees, placement ([Apple](https://developer.apple.com/videos/play/wwdc2020/10686/)). Record core/cluster residency/frequency; test E- and P-active cases. Compare kernels with real daemon energy/residency; use the worst supported profile.

**4. Derivation.** ΔJ480=480(Pload−Pidle) for stationary aligned averages; actual slots use Σ overlap_seconds×ΔP. Reference fresh bracketing 25G83 idle with identical instrumentation. R6 binds 25F84 (`configs/calibration/calibration_acceptance_d079_v2_n17_r6.json:20`): historical corroboration only. Residency cannot reconstruct historical cpu_interval_v1. Active-capture CPU includes intended work; compare admission with idle segments.

Propagate paired-reference covariance, block/session variability and clock/coverage bounds. Resample blocks/sessions, not 100 ms rows; systematic bounds never shrink by sqrt(n). Retain anchor envelopes in both floor and claim.

Propose a ruled upper prediction bound on incremental false effect ≤0.5 J and 20% CPU headroom below the tested safe boundary; confirm C* directly. Report floor+claim bound and target-effect margin. The ≈5 J clearance bar is NOT spare contamination allowance (`docs/decision_log.md:4797`). If clean and safe ranges do not overlap, no cutoff qualifies. Use CPU+GPU+ANE sum; combined is only a cross-check. Whole-machine DRAM/display/storage/PSU requires calibrated wall measurement.

**5. Observer.** Bracket SELF+reaped CHILDREN user/system CPU before launches through journal ACK/reaping (`scripts/run_night.py:2603`). Repeat cleanly. Record 30: 1.15 cpu-s/30 s=.0383 cores replaces the body-only figure. This is amortized cost, not a proven predicate minimum: pre/post checks extend outside CPU spans. Verify coverage; subtract nothing. Minimum feasibility comes from clean rounds plus margin; compare recorder on/off and k=2 cadence.

**8. Amend lane.** Correct 60→480 s; capture BUDGET (`scripts/gen_derivation_night.py:89`) differs from phase duration. Fix reference/boundary/quiet-time claims. Ordinary floor extraction needs current-epoch authority first (`configs/calibration/preregistration_d079_epoch_25g83_rev1.md:443`); diagnostic labels cannot bypass refusal. Constant cancellation proves neither burst safety nor post-GO cleanliness. Next: lead rules boundary/budget/lane split and scopes implementation.

## Residual risk

No writes/tests/measurements. Bundles: parallel seat. Native support/cutoff feasibility unverified.