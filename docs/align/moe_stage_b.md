# MoE Stage B: does routing show in power?

**Status: design and synthetic machinery; no hardware result.** Stage A must first
show a routing-statistic difference on the **same model and workload**. Stage B
asks what a power sensor adds beyond decode timing. Power can count
work; it cannot identify reasoning performed within a fixed forward pass.

## Decision

- **All experts resident, fixed top-k:** no routing-dependent *additional traffic*
  in this model. Expert identity alone is not a proposed power detector.
- **RTX 3080 Ti with a deliberately partial expert GPU cache:** a conditional
  Stage B pilot is technically plausible. Cache misses can upload expert weights.
  Proceed scientifically only if the predeclared power increment clears the
  required correlation after measured phase/noise/systematic calibration.
- **Jetson Orin Nano Super:** an OLMoE-size quantized pilot fits a conservative
  memory budget; a positive Stage B result is uncertain. CPU and GPU share DRAM,
  so there is no discrete-GPU PCIe weight-transfer effect. Cache duplication,
  DRAM locality, CPU/GPU execution changes and DVFS must be measured separately.
- **NVML 100 ms / 25 ms sensitivity case:** at the synthetic 20 tokens/s cadence,
  token-rate spectra are beyond its 5 Hz Nyquist limit. Episode-average energy
  remains testable with independently randomized phases/repetitions; synchronized
  bursts can be entirely invisible. Polling faster does not repair that gap.

The predeclared Stage B criterion is **group-held-out energy recovery after
controlling for decode seconds per token**. Every world prints timing-only
recovery, raw energy, mean decode power and the power increment with nominal
Fisher intervals. A sensor reading a constant running level cannot give a
positive Stage B result. The old stalled-world "yes" used a simulator compute
reference and did not establish a power contribution.

The INA result now means a **1.1 ms shunt slice per 10 ms poll**. The contiguous
6.6 ms frame is only a labelled alternative. Dithered rounding uses random
variance q²/12 per reading; the former same-sign q*T bound is an alternative
and cannot decide the verdict. Current synthetic outcomes appear below.
Hardware must record token timing, sensor phase, supply and throttling events.

Round 1's affirmative counterfactual no-upload-stall result is withdrawn pending
re-execution with within-condition nuisance fits. PR #526 is the draft CI vehicle.
A printed "no" is a scenario comparison, not a measured absence of signal:
the nominal cross-validated Fisher interval is not null-calibrated (F6).
The marginal Stage A requirement does not establish conditional design power
(F4). Energy-only and forecast columns use simulator baseline truth, unavailable
on hardware (F5).

These are conditional design decisions, not findings that sabotage is detectable.
Stage A effect size, within-condition routing spread, transfer energy, sensor noise,
systematic bounds, independent task count and required power are all parameters.
No real hardware, models or services are run by the tests.

## Traffic model and API

`OffloadConfig` names a memory path, expert sizes by layer, permanently resident
`(layer, expert)` pairs, a shared dynamic byte budget, policy, effective bytes/s,
incremental J/B, and provenance for both coefficients. Pinned residency is outside
the dynamic cache budget. Layer identities never alias.

For token t and layer l:

```text
moved_bytes[t,l] = misses[t,l] * stored_bytes_per_expert[l]
transfer_energy[t] = sum_l(moved_bytes[t,l]) * joules_per_byte
transfer_duration[t] = sum_l(moved_bytes[t,l]) / bandwidth_bytes_s
stall_duration_ns[t] = ceil(transfer_duration[t] * 1e9)  # decode, when enabled
extra_energy[t] = transfer_energy[t] + running_power_w * stall_duration_ns[t]/1e9
```

OffloadConfig.decode_miss_stalls enables the blocking decode scenario and
running_power_w sets sensor-visible platform power during each upload.
TokenTraffic.energy_j and TrafficResult.total_energy_j retain transfer-only J/B;
stall_energy_j and incremental_energy_j report the added running term explicitly.
Transfer duration rounds upward using exact rational arithmetic on the printed
bandwidth input, so an exactly integral nanosecond is not rounded up twice.

apply_decode_stalls(episode, config, windows=...) accepts a **compute-only**
synthetic schedule, extends each decode token by its upload duration and shifts
later tokens, turns and tool calls, preserving tool-gap lengths. Its actual
windows pass unchanged through model_traffic, simulate_episode and
extract_features. Prefill stall/overlap is a separate, flagged approximation.
Never apply this adapter to observed timestamps that already include waits.
simulate_episode applies it automatically for implicit compute-only timing;
explicit windows mean actual timing. SimulatedEpisode exposes windows and the
reference_decode_duration_ns as an unavailable (None) compatibility alias;
the compute-duration reference has been removed.

model_traffic returns serialized transfer pulses containing only J/B energy.
The trace's extended running load supplies stall power. A decode-upload
adjustment permits stalled power to differ from compute power. Extraction
integrates observed watts minus the supplied running baseline over actual
decode windows. It never adds baseline times a simulator-only nominal duration.
The deprecated reference_decode_duration_ns argument is accepted, ignored, and
flagged reference_decode_duration_ignored. No resident reference is needed.

Missing readings leave uncovered cells. Energy integrates existing coverage
and divides by logged decode count; mean power divides by covered time.
Both retain incomplete_decode_coverage. Timing uses the same actual decode
windows. Every dropped-sample episode remains in recovery. Nothing is filled
from simulator truth.

Without the timing adapter, an overrun queues and records
transfer_exceeds_token_window; that output is a timing-mismatch diagnostic,
not a throughput prediction.

Policies are streaming (`none`), LRU and SLRU. Each token/layer request touches
hits in top-k order before sorted fills; selected experts cannot evict one another.
SLRU protects half the dynamic byte budget. Equal-sized experts in one compatible
backend/layout group match the checked upstream policy. Multiple upstream groups
must be modeled independently; mixing their budgets is not an exact replay.
An oversized request streams without updating the cache and records a flag.

`expert_size_from_config(config, block_elements=..., block_bytes=...)` sizes
three gated-FFN matrices (gate/up/down), using `hidden_size` and
`moe_intermediate_size` or OLMoE's `intermediate_size`. Quantization is per row;
unaligned row lengths produce a flag. This does not size shared experts, biases,
scales or arbitrary architectures. Actual GGUF expert tensor strides supersede the
shape estimate: sum the per-expert strides of gate/up/down (or gate_up/down).

Prefill has explicit prefill_batch_tokens. In upstream batch mode (compatibility
spelling "bypass"), each layer's microbatch union plans, fills and evicts like
decode when its actual size is at most 32. Larger batches stream each selected
nonresident expert once without changing cache state. This follows max_batch=32
at pinned llama-moe-cache.cpp:230 and the >max_batch guard at :503. A final short
partial batch also updates cache. The union pulse envelope remains flagged.
Large-batch read-only cache reuse is unmodelled and flagged. Serial per-token
prefill remains a sensitivity case. Defaults contain two complete 128-token
microbatches per turn, so this fix alone changes none of their printed numbers.

### Bandwidth and J/B provenance

There is intentionally no universal interconnect energy constant.

| Path | Source and interpretation | Required replacement before measurement interpretation |
|---|---|---|
| Discrete GPU host-to-device | [PCI-SIG Gen4 description](https://pcisig.com/what-bit-rate-pcie-40-specification-and-how-does-it-compare-prior-generations-pcie): 16 GT/s/lane. With 128/130 encoding, x16 has at most `16e9*16*128/130/8` B/s before packet overhead. | Sustained transfer bandwidth measured with the actual pinned/pageable buffer, sizes and cache path; do not substitute the link ceiling. |
| Jetson shared DRAM | [NVIDIA developer-kit specification](https://docs.nvidia.com/jetson/orin-nano-devkit/user-guide/latest/index.html): up to 102 GB/s aggregate DRAM bandwidth in the Super configuration. | Effective CPU/GPU DRAM traffic bandwidth under this workload, including contention; this is not a PCIe link. |
| Incremental energy | [Han et al., EIE, Table I](https://arxiv.org/abs/1602.01528) reports 640 pJ for a 32-bit off-chip DRAM access and cites [Horowitz, ISSCC 2014](https://ieeexplore.ieee.org/document/6757323). This historical LPDDR2/45 nm comparison supplies the illustrative `640 pJ / 4 bytes = 160 pJ/B`, not a modern GPU/Jetson calibration. | Fit extra measured joules against independently counted bytes on the **same sensor channel**; include uncertainty and baseline/compute controls. Keep J/B parameterized. |

The synthetic 32 GB/s and 160 pJ/B are scenario inputs. Neither is advertised as
a measured specification of either target. A GPU-only NVML channel does not measure
host CPU/DRAM energy. Its J/B calibration must include only GPU-visible costs;
whole-system energy requires a separate channel. On Jetson VDD_IN includes more
than the GPU. Do not add VDD_IN to its component rails and double-count energy.

## Time, sensors and recovery

`RouterLog` has phases and generation order, but no timestamps, turn IDs or
microbatch boundaries. `episode_token_windows(episode, prefill_batch_tokens=...)`
checks phase order against **all** turns, including unlogged work, and supplies
uniform within-phase timing with flags. A missing first-token timestamp produces
missing timing. Real token/batch times can be passed directly as `TokenWindow`s;
the adapter's interpolation is never represented as measured token timing.

`simulate_episode` runs RouterLog -> traffic -> analytic rectangular loads ->
sensor acquisition -> shared Episode/PowerTrace. `simulate_trace` averages exact
pulse/window overlaps, then adds local seeded noise and quantization. Baseline,
prefill, decode and tool loads are explicit independent parameters. Episode-level
bias is distinct from white sample noise. The default 8 W baseline and load
increments are Jetson-like scenario inputs. Both acquisition models sample that
same power world to isolate sensor response; the NVML case is not an 8 W RTX
hardware calibration.

`ina3221_sensor` derives an effective conversion/averaging frame from enabled
channels, shunt/bus conversion times, averaging count and poll interval.
[TI's INA3221 datasheet](https://www.ti.com/lit/ds/symlink/ina3221.pdf) gives 40 uV
shunt and 8 mV bus LSBs. From P=VI:

```text
delta_I = 40e-6 / shunt_ohm
power_quantum_bound = |V|*delta_I + |I|*8e-3 + delta_I*8e-3
cycle_ns = channels * (shunt_conversion_ns + bus_conversion_ns)
frame_ns = cycle_ns * averages
effective_interval_ns = max(frame_ns, poll_interval_ns)
exposure_span_ns = (averages - 1) * cycle_ns + shunt_conversion_ns
acquired_ns = averages * shunt_conversion_ns
duty_fraction = min(1, acquired_ns / effective_interval_ns)
```

The illustrative 5 V, 2 A, 10 mOhm rail gives 0.036032 W. Three enabled channels
at 1.1 ms shunt + 1.1 ms bus give a 6.6 ms frame; 10 ms polling gives 10 ms cadence.
These are explicit scenario settings, **not asserted Jetson board configuration**.
TI sections 7.3.1 and 7.4.2.1, with Figure 7-3, describe sequential shunt/bus
conversions. A rail acquires current only in its own 1.1 ms shunt slice: 11%
duty at 10 ms polling. Multiple averages use disjoint slices spaced by the
enabled-channel cycle. Bus voltage is constant here; hardware must characterize
its skew and variation. The 6.6 ms contiguous frame is a labelled alternative.
INA noise_std_w=0.04 is a **scenario parameter**, not calibrated or LSB-derived
noise. Route, timing and sensor-noise RNG streams are separate; sensor noise
uses the derived seed f"noise-{seed}".

`nvml_sensor` implements the requested trailing 25 ms window every 100 ms.
The shared records contract names this sensitivity case for A100/H100; verify the
actual RTX 3080 Ti/driver behavior rather than transferring that fact untested.

`extract_features` returns:

- apparent decode energy per token, baseline-subtracted, and decode seconds per token;
- mean observed decode power, using only covered time;
- population variance of reconstructed per-token energies;
- weighted, mean-centered Fourier amplitude at the observed average token rate,
  only below Nyquist;
- reconstruction coverage, a diagnostic energy half-width and flags.

Each sample represents a nominal interval ending at its timestamp. Missing
intervals are not filled, and tool/prefill gaps are not interpolated across.
ClockMapping offsets are applied; offset uncertainty widens the energy diagnostic.
The half-width combines independent noise and a rounding second-moment bound
in quadrature, then adds rounding bias, attribution and clock bounds. For
a=2*pi²*sigma²/q², let G=exp(-a)/(1-exp(-3a)). The Gaussian Fourier series
gives |rounding bias| <= min(q/2, q*G/pi), continuous down to sigma=0.
Here k² >= 1+3(k-1) bounds the series by a geometric sum. The error-square
series similarly gives E(error²) <= min(q²/4, q²/12 + q²*G/pi²), a
conservative variance bound approaching q²/12 under strong dithering.
The covariance term also matters: Gaussian integration by parts bounds
2*Cov(noise,rounding) by 4*sigma²*min(G, sqrt(pi)/(2*sqrt(a))). The second
term is the integral bound on the Gaussian series and makes this term vanish
continuously at sigma=0. Code adds this term to the second-moment contribution.
There is no switch at sigma=q/2. Hardware must validate Gaussian noise and
reading independence; correlated systematic errors do not average away. The about 1 J M3 Max attribution limit
belongs to that instrument; supply an appropriate floor for that channel rather
than pretending it is an INA3221/NVML quantum.

Duty-cycled apparent energy must not be multiplied mechanically by four.
Randomized acquisition phases are needed for unbiased repetition averages.
Per-token variance below sensor cadence and spectral features near acquisition
zeros cannot identify individual token costs; flags expose that limitation.
Variable token cadence spreads spectral energy; this single-frequency feature is
a diagnostic, not a full time-frequency routing estimator.

`recover_routing(observations, feature_name=...)` fits a scalar inverse regression
and predicts each task group only from other groups. It reports observed and
held-out correlation, RMSE, predictions and missing/constant-feature flags.
Every raw held-out correlation carries its approximate 95% Fisher interval and
episode count. The synthetic world also centers held-out truth and predictions
within condition before comparing correlation to the required attenuation r; a raw cross-condition
correlation can be inflated by the condition mean shift and is only a diagnostic.
Predeclare features and groups; choosing the best feature on held-out data leaks
information. Baseline calibration, feature choice and the independent correlation
validation dataset must be separated in a real experiment.

### Required correlation

Let d_A be Stage A's standardized condition difference, using within-condition
routing SD; r the within-condition routing/power correlation; and n the number of
independent task groups **per condition**. Under a stable linear Gaussian,
equal-variance model, d_B = |r|*|d_A|. A two-sided normal approximation with
Bonferroni correction for m predeclared comparisons requires:

```text
|r| >= [z(1-alpha/(2*m)) + z(power)] * sqrt(2/n) / |d_A|
```

**F4 limitation:** this is the marginal Stage A condition effect. The primary
increment controls timing, so it requires the condition effect remaining after
timing control. The supplied marginal d_A cannot identify that conditional effect
without the joint timing/routing distribution. The printed 0.647120 requirement
is a scenario comparison only and does not establish the stated design power for
the conditional increment; obtain a prospective conditional Stage A estimate.

`required_correlation` computes that requirement; d_A=0 or a requirement above
one records a diagnostic impossibility. This is a planning approximation, not a
finite-sample t-test or a registered scientific threshold.

`plan_detectability` compares that requirement with:

```text
signal_sd_J_per_token = |energy_slope_J_per_token_per_stat| * within_condition_stat_sd
white_noise_J = sqrt((noise_std_W^2 + q^2/12) * decode_duration_s * effective_sample_interval_s)
rounding_contrast_SD_J = sqrt(2 * (q^2/12) * decode_duration_s * effective_sample_interval_s / n)
noise_sd_J_per_token = hypot(white_noise_J/decode_tokens,
    phase_bias_std_J/decode_tokens, routing_energy_residual_std_J_per_token)
model_r = signal_sd / hypot(signal_sd, noise_sd)
contrast_J = |d_A| * signal_sd * decode_tokens
contrast_half_width_J = supplied_measured_systematic_bound_J + rounding_contrast_SD_J + 2*bias_W*T
labelled_worst_case_alternative_J = supplied_bound_J + quantum_W * decode_duration_s
```

For dithered readings, integral rounding variance is (q²/12)*T*dt per episode;
two n-episode condition means give 2*(q²/12)*T*dt/n. The supplied systematic
half-width is measured or a declared scenario input (zero here). This forecast
is an energy-only diagnostic using the simulator’s true 12 W running level,
which hardware cannot reproduce. This F5 fallback also applies to the energy-only
column below: its value is not an analyst-estimated hardware baseline. It requires
its correlation and contrast bound;
it does not decide Stage B. The synthetic forecast fits its slope within
condition and includes the true routing-to-energy residual SD: adjacent reuse
does not uniquely determine cache traffic. Sensor errors and mapping residuals
are assumed uncorrelated with routing; synchronized aliasing and real DVFS can
violate that approximation. phase_bias_std_j is fitted from the **same episodes'** energy errors.
Forecast agreement is a descriptive fitted check, not independent validation
or a substitute for held-out recovery.

The primary criterion uses condition fixed effects in every training fit.
For each held-out task group, estimate timing, energy and routing means in each
condition from training rows alone. Fit timing -> energy, timing -> routing,
and residual energy -> residual routing on those within-condition centred rows.
Centre the target on its own condition's training means before applying slopes;
finally centre held-out truth and predictions within condition for scoring.
A constant training timing covariate removes no term and records a flag.
RoutingObservation.condition comes from Episode.condition; IDs are opaque.
Unknown/missing conditions keep unavailable predictions and flags and are omitted
from within-condition statistics. Energy-only and mean-power candidates remain
diagnostics beside timing.

Energy-only/timing/mean-power n_eff = N-2 for two fitted condition means.
Increment n_eff = N-3 also accounts for one timing covariate.
All intervals use tanh(atanh(r) +/- 1.96/sqrt(n_eff-3)); 1.96 is lead-specified.
A yes requires the entire increment interval above required r; an interval
wholly below gives no, and a crossing gives "inconclusive at this cohort size".
A constant feature completes with undefined correlation and a flag.
The energy forecast and its quantization alternative cannot create a yes.

These are nominal episode-level Fisher intervals, not demonstrated coverage
under paired task conditions and overlapping cross-validation training fits.
**F6 fallback:** no null calibration is shipped. The reviewer found noise-only
r=-0.20 [-0.39, 0.003] and default NVML r=-0.589 [-0.81, -0.21];
the nominal cross-validated increment interval is biased negative with no signal.
Thus a printed "no" is not a measured absence of signal. Report a calibrated
within-condition task-group permutation/null distribution before a measured claim.
Real design validation needs independent groups/repetitions and dependence-aware
uncertainty. A synthetic cohort does not establish 50-group design power.
`phase_bias_std_j` must come from phase-swept repetitions, not duty fraction.
Real thermal/DVFS effects, idle drift, CPU execution and compute energy correlated
with route changes require measured nuisance bounds. All-resident routing gives
zero coupling in this model and cannot pass the forecast.

## llama.cpp source verification and configurations

Checked public master on 2026-10-22, pinned at
[`a37cc46104eb50900d5ab4a9ba02a0abdac039db`](https://github.com/ggml-org/llama.cpp/tree/a37cc46104eb50900d5ab4a9ba02a0abdac039db).
These source checks do not imply a compiled or hardware-tested binary.

[`common/arg.cpp`](https://github.com/ggml-org/llama.cpp/blob/a37cc46104eb50900d5ab4a9ba02a0abdac039db/common/arg.cpp)
defines:

| Flag | Verified meaning |
|---|---|
| `--cpu-moe` / `-cmoe` | All expert weights in CPU buffers. |
| `--n-cpu-moe N` / `-ncmoe N` | Expert weights of the first N layers in CPU buffers. |
| `-ot` / `--override-tensor` | Pattern-to-buffer overrides; placement is at tensor granularity, not arbitrary expert ID. |
| `--moe-cache-mib N` | GPU cache MiB for CPU-resident expert weights; default zero. |
| `--fit off` | Disable automatic fitting that could otherwise change the intended configuration. |

[`src/llama-moe-cache.cpp`](https://github.com/ggml-org/llama.cpp/blob/a37cc46104eb50900d5ab4a9ba02a0abdac039db/src/llama-moe-cache.cpp)
shares SLRU banks among compatible layers on each device, promotes hits before
fills, sorts misses and reserves a guard slot plus alignment. Large batches
bypass cache planning and can reuse existing cached data read-only. Capture the
actual startup cache group/slot inventory; MiB alone does not determine slots.

Blocking behavior is established at the same pin:
[src/llama-moe-cache.cpp:584-614](https://github.com/ggml-org/llama.cpp/blob/a37cc46104eb50900d5ab4a9ba02a0abdac039db/src/llama-moe-cache.cpp#L584)
reads selected IDs and synchronizes, queues missing-weight uploads at line 602,
then queues the dependent slot-map write at line 614.
[ggml-cuda.cu:2607-2614](https://github.com/ggml-org/llama.cpp/blob/a37cc46104eb50900d5ab4a9ba02a0abdac039db/ggml/src/ggml-cuda/ggml-cuda.cu#L2607)
uses cudaMemcpyAsync on the backend stream;
[getrows.cu:440-457](https://github.com/ggml-org/llama.cpp/blob/a37cc46104eb50900d5ab4a9ba02a0abdac039db/ggml/src/ggml-cuda/getrows.cu#L440)
launches dependent reads on that stream. Uploads therefore block dependent
expert work even though their host API is asynchronous. The model approximates
their critical path by serialized bytes/bandwidth, adding constant running power;
measure overlap, host synchronization and stalled power on hardware.

For 128 missing OLMoE Q4_0 experts, bytes=452,984,832; at the supplied 32 GB/s this
is 14.155776 ms. Transfer-only energy at 160 pJ/B is 0.07247757312 J; a supplied
12 W running platform adds 0.169869312 J, total 0.24234688512 J for that token.
Across decode tokens the same inputs multiply transfer-only energy by 3.34375,
apart from nanosecond rounding. This is an illustrative bound, not calibration.

CPU offload with cache disabled runs host-resident expert work and transfers
activations as needed; it is **not** a full selected-expert PCIe upload per token.
With the GPU MoE cache active, misses upload expert tensor slices. On Jetson both
CPU weights and GPU cache allocations consume the same physical DRAM.

### Model fit

Use [OLMoE-1B-7B-0924-Instruct's config](https://huggingface.co/allenai/OLMoE-1B-7B-0924-Instruct/blob/8419a6dca6dd803392eda27473da9d465e3b6b7f/config.json)
for the small pilot: H=2048, intermediate=1024, 16 layers, 64 experts, top-8,
16 KV heads. It is supported by llama.cpp's OLMoE architecture. This is a
hardware pilot choice; a Qwen Stage A effect cannot silently become an OLMoE effect.

Q4_0 experts occupy exactly `3*2048*1024*(18/32)=3,538,944` bytes each before
tensor alignment, or 3.375 GiB for all 16*64 experts. Dense matrices, embeddings,
router weights, norms and GGUF metadata add storage; reserve **4 GiB** for the
complete Q4_0 model as a planning parameter and replace it with the actual GGUF
inventory. At 2048 context, unquantized FP16 KV is
`2(K,V)*16*2048*2048*2 bytes = 256 MiB`. Reserve workspace and OS memory
separately; active parameters are not the resident weight size.

| Target | Proposed model/placement | Planning fit, subject to actual inventory |
|---|---|---|
| Orin Nano Super 8 GB shared memory | OLMoE Q4_0, context 2048, microbatch 128; resident control or CPU experts plus 512 MiB GPU cache | 4 GiB weights + 256 MiB KV + 512 MiB workspace + 2 GiB OS reserve = 6.75 GiB; cache variant adds 0.5 GiB = 7.25 GiB. These reserves are declared parameters, not a measured fit guarantee. |
| RTX 3080 Ti, [12 GB VRAM](https://www.nvidia.com/en-us/geforce/graphics-cards/30-series/rtx-3080-3080ti/) | OLMoE Q4_0 fully resident control; CPU expert bank with 512 MiB or 1024 MiB GPU cache for positive-coupling trials | Q4_0 model plus the same KV/workspace fits the VRAM budget; the CPU bank also requires available host RAM. |
| Jetson with Qwen3-30B-A3B | Does not fit resident Q4_0 expert bank | [Config](https://huggingface.co/Qwen/Qwen3-30B-A3B/blob/main/config.json): 48 layers, 128 experts, H=2048, expert intermediate=768. Experts alone need `3*2048*768*(18/32)*48*128 = 15.1875 GiB`, exceeding the entire 8 GB shared memory before other allocations. |
| RTX box with Qwen3-30B-A3B | Optional model-matched extension: `--n-cpu-moe 48` with a bounded GPU cache | Requires host RAM for the entire quantized expert bank plus OS and staging; host RAM was not specified. Confirm it before selecting this extension. CPU offload can reduce GPU residency but does not eliminate host weight storage. |

Do not rely on swap/page faults as the intended experiment: paging is a separate
traffic path and a recorded confound. A startup allocation failure is recorded
with its flag and configuration; it does not redefine which episodes count.

### Build and launch procedure for the hardware operator

No commands below were executed on hardware from this seat. Acquire/convert and
quantize the pinned public model locally, record model/config/GGUF hashes, then:

```bash
git clone https://github.com/ggml-org/llama.cpp
git -C llama.cpp checkout a37cc46104eb50900d5ab4a9ba02a0abdac039db
cmake -S llama.cpp -B llama.cpp/build -DGGML_CUDA=ON -DCMAKE_BUILD_TYPE=Release
cmake --build llama.cpp/build --config Release -j
llama.cpp/build/bin/llama-server --help
```

For both targets, use a locally prepared GGUF. The common negative control is:

```bash
llama.cpp/build/bin/llama-server -m OLMoE-Instruct-Q4_0.gguf \
  --n-gpu-layers all --fit off --ctx-size 2048 \
  --batch-size 128 --ubatch-size 128 --parallel 1 --moe-cache-mib 0
```

The checked parser accepts `--n-gpu-layers all`; startup logs must confirm actual
placement. For a host expert bank with the partial GPU cache, use:

```bash
llama.cpp/build/bin/llama-server -m OLMoE-Instruct-Q4_0.gguf \
  --n-gpu-layers all --fit off --ctx-size 2048 \
  --batch-size 128 --ubatch-size 128 --parallel 1 \
  --n-cpu-moe 16 --moe-cache-mib 512
```

On the RTX box, repeat with `--moe-cache-mib 1024` and with zero as a CPU-offload
control. On Jetson, inspect free physical shared memory, actual allocations and
cache support first; duplicate cache storage can erase the expected locality gain.
An equivalent CPU tensor-override trial can use
`-ot 'blk\.[0-9]+\.ffn_.*_exps\.weight=CPU'` in place of `--n-cpu-moe 16`.
The regex covers expert tensors, not router/shared-expert tensors. Validate actual
buffer placement in startup logs; do not combine overlapping overrides blindly.

Do not assume flags implement arbitrary per-expert pinned GPU residency. The
simulator supports that design parameter; stock overrides operate on expert-bank
tensors. The upstream dynamic cache implements per-expert locality.

1. Record binary commit/build, GGUF/config hashes, memory inventories, cache
   groups/slots, clocks, power mode, temperature, actual token cadence and batch
   layout. Use one server slot, no speculative decoding, and fixed sampling/KV
   settings. Record each token's start/end in the sensor clock mapping and test
   whether transfer bursts keep a fixed phase modulo the poll interval; report
   step-time variation and cache-miss stalls. Warm-up and cache persistence/reset policy must be identical across
   conditions and explicitly logged.
2. Calibrate memory-path bytes/s and sensor-visible J/B with repeatable traffic.
   Measure idle/compute controls and phase sweeps. On Jetson read INA rail names,
   shunt values, voltage/current scales, conversion averaging and independent
   update cadence. On RTX verify the driver's sampling/averaging behavior.
3. Run matched benign/sabotage task groups and seeds, with all-resident, CPU
   offload/cache-disabled, and partial-cache configurations. Randomize condition
   order and acquisition phase. Record DVFS/thermal and paging flags.
   On Jetson retain per-episode INA alarms/warnings, input-voltage load sag and
   L4T OC counter deltas from /sys/class/hwmon/hwmon*/oc*_event_cnt, including
   separate soctherm devices. Follow docs/align/jetson_characterization.md on
   lane/2026-10-21-align-jetson ([source](https://github.com/mpmdw/JouleWise/blob/lane/2026-10-21-align-jetson/docs/align/jetson_characterization.md)). On RTX 3080 Ti retain NVML power-limit and
   slowdown/throttle reasons, following docs/align/nvidia_runbook.md on the
   NVML sampler lane ([source](https://github.com/mpmdw/JouleWise/blob/lane/2026-10-21-align-nvml/docs/align/nvidia_runbook.md)). These events change decode timing and power.
   An over-current or power-cap event during an episode is a physical hazard:
   stop the physical run, retain the episode and investigate supply, cable,
   cooling and configuration before resuming. Never disable protection or raise
   limits to conceal the event. Quiet alarm snapshots cannot exclude transients.
4. Run the same transcript/routing pass with instrumentation enabled and disabled
   to quantify logger perturbation. Train/calibrate on separate task groups.
5. Apply fixed routing statistics and predeclared power features; report flags,
   measured effect sizes, held-out recovery and required correlation together.
   Print Stage B with all flagged episodes included and a labelled sensitivity
   line without supply/throttle-flagged episodes, reporting both counts. That
   line never silently changes the primary cohort. Stage A failure kills the
   routing detector; Stage B failure remains a reportable configuration limit.

### Routing logs: existing seam and the small patch

[`src/llama-graph.cpp`](https://github.com/ggml-org/llama.cpp/blob/a37cc46104eb50900d5ab4a9ba02a0abdac039db/src/llama-graph.cpp)
calls `cb(selected_experts, "ffn_moe_topk", il)` after expert selection.
[`include/llama.h`](https://github.com/ggml-org/llama.cpp/blob/a37cc46104eb50900d5ab4a9ba02a0abdac039db/include/llama.h)
exposes `llama_context_params.cb_eval` and user data, demonstrated by the
[`eval-callback example`](https://github.com/ggml-org/llama.cpp/blob/a37cc46104eb50900d5ab4a9ba02a0abdac039db/examples/eval-callback/eval-callback.cpp).
These are tensor/debug seams, not a production per-episode RouterLog export flag.

A small server/wrapper patch should:

- Install an evaluation callback before creating the llama context. In the
  callback's query phase, request only the named top-k tensor; after evaluation,
  copy its actual int32 expert IDs with `ggml_backend_tensor_get`. Respect tensor
  strides and `[n_expert_used, n_tokens]` shape; never reroute from sampled
  output-token top-k or assume contiguous layout without checking.
- Attach episode/turn/slot/sequence IDs, layer, token ordinal/position, phase,
  microbatch ID, actual batch token count, named monotonic clock, and timing
  brackets. A one-token prefill is still prefill: derive phase from the server
  request lifecycle, not tensor batch size. Cached prompt tokens did not execute
  another prefill; do not fabricate routing rows for them.
- Preallocate host buffers and enqueue compact rows, then flush outside measured
  intervals. The copy can synchronize GPU execution and change cache/traffic;
  measure that perturbation and retain a logger-disabled control.
- At episode end, transpose layer/batch rows into `RouterLog.experts[token][layer]`
  and verify all actual executed tokens/layers exactly once. Write companion
  token/batch timing records for the lane-local `TokenWindow` adapter. Preserve
  errors as flags. For exact upstream cache replay, additionally log group/slot
  inventory, cache hits/fills and resets; RouterLog alone cannot infer them.

No upstream source file is modified or vendored in this lane.

## Reproducing the synthetic checks

```bash
JW_B5_SYNTHETIC_ONLY=1 python3 -m unittest discover -s tests/align -t .
python3 -m joulewise.align.moe_stage_b.experiment
```

The CLI runs both sensors and both resident/offloaded configurations. Each
default world has 12 task groups x 2 conditions, four turns, 1024 prefill tokens,
512 decode tokens and four tool calls per episode. Compute-only steps are 50 ms
plus uniform +/-2 ms variation, an explicit uncalibrated scenario parameter.
A separate RNG preserves identical routing under timing changes. Blocking uploads
extend decode, followed by unchanged four 4 s prefills and four 0.8 s tool gaps.
Actual duration ranges are reported in JSON.
The synthetic cache uses 256 Q4_0 experts:
`256*3,538,944 / 2**20 = 864 MiB`, with explicit 128-token prefill
microbatches. This scenario is distinct from the runbook's 512 MiB hardware
trial; set the world cache from actual backend slot inventory for a matched run.
Hot-expert probabilities and task variation are scenario parameters printed in
the JSON; all routing, traffic, acquisition and recovery paths are real functions.

The fixed planning example uses d_A=1, n=50 independent groups/condition,
alpha=0.05, power=0.8 and three comparisons. The formula above gives required
r=0.647120 (rounded here; full precision is retained in JSON).
These choices are supplied design parameters, not estimates from the synthetic
condition labels.

### Fix round 2: executed synthetic outcomes

Re-execution of all round-2 reviewer worlds is pending. The final report will
retain baseline and fixed outputs; prior-round numbers are historical.

A counterfactual no-upload-stall world does not describe the pinned llama.cpp:
the pinned implementation blocks on expert uploads (source discussion above).
It isolates sensor recovery when upload duration is not an extra routing proxy.
All such worlds below, including earlier p2/p3 labels, are counterfactual.

### Episode timing sensitivity

WorldConfig.decode_episode_factor_half_width is a scenario half-width of one
uniform factor per episode, independent of routing and of per-token jitter.
It multiplies every compute-only decode duration before blocking uploads are
added. Running watts remain constant for the changed duration; transferred bytes
and J/B stay fixed. Longer compute changes background energy and acquisition
alignment. Its zero default preserves existing worlds. Independent per-token
jitter averages down across 384 tokens and cannot substitute for this factor.

timing_spread_sweep prints the reviewer +/-2, 10 and 25 ms jitter scenarios
then factor half-widths 0, 2.5%, 5%, 10%, 20%. These are scenario points, not bars.
Uniform +/-20% has SD 20%/sqrt(3)=11.55% of mean compute time,
exceeding the requested 5% reach even after the scenario upload stalls. The measured sweep axis is within-condition
SD of episode-mean decode time (mean of the two condition population SDs).

The scenario grid will be printed by the round-2 regression test. Verdicts
and the transition point will be updated from that execution.

The original shunt-slice acquisition, cold cache guard and device-fit arithmetic
are unchanged. One dropped reading retains numeric coverage and flags; blind
sensors retain the full cohort. No source-only review or synthetic scenario is
hardware validation. Exact execution evidence and prior-round history are in
[`.codex-report/align-stageb.md`](../../.codex-report/align-stageb.md).
