# Apple alignment path (internal, provisional)

This is code and a prospective D1 plan for RQ-ALIGN-ENERGY-RESIDUAL.
Nothing is registered, armed, installed or measured here. The cloud executor
never became usable in the fix seat; all new checks remain NOT EXECUTED.
The lane report distinguishes source changes from observed results.

Energy can count inference work omitted from a visible log. It cannot identify
reasoning that fits inside the same forward passes.

## Execution and records

Use workload_profile.name = "align_episode". prompt_text holds canonical
EpisodeSpec JSON: one local AgentTask factory, condition and seed per member,
with repetitions = 1. Seed replication means another episode specification.
A factory declaring clock receives the controller's injected clock, so tools
and model calls share the production or simulated timeline.

The registry imports align code only on this workload branch. Supported
runtimes are mock and MLX. Missing tasks, bad specs, unsupported backends and
MLX without a local model mirror return RUNTIME_UNAVAILABLE during prepare,
before idle admission or warmup. The controller maps that reason to status
"unsupported"; it does not create a fictional benign episode. These are
unmeasurable configurations, not hazard refusals or discarded observations.

MLX uses the existing in-process MlxRuntimeAdapter._generate helper, as current
suite workloads do. This preserves model load, tokenizer, greedy sampler,
stream generation, detokenizer and phase events. A separate mlx_lm.server
would add another process and dispatch boundary. Identity records model,
local source, revision, artifact identity, mlx and mlx-lm versions; the wrapper
forwards the runtime's readiness identity projection. Heavy libraries remain
lazy optional imports. No implicit weight download is permitted.

The model's chat template receives messages and tools; encoding adds no
duplicate special tokens. Explicit Qwen-style <tool_call> envelopes become
calls; unknown formats remain text with flags. Retokenized reasoning counts,
nonzero temperature against the pinned greedy sampler, tool faults and budget
exhaustion are flags. Every prompt is rendered in full; cached_prompt_tokens
is zero.

The existing controller owns idle admission, warmup, sampling, hazard bindings,
post-window dwell, custody and reduction. generate_campaign uses
scripts.generate_matrix.build_config and the shared renderer/write-boundary
checks. It emits align_pack.json and members/*.json, including
members/order_manifest.json in scripts/run_campaign.py's executed_order schema.
Task/seed/control-matched pairs alternate AB and BA, giving ABBA over two pairs.
Unmatched cells remain present with a pack flag. A caller can explicitly retain
its own order with counterbalance=False. The persisted pack UUID makes run ids
unique across packs sharing a model_tag, while regeneration preserves bytes.
Episode ordinal tags say episodeN, without the matrix generator's repN/2m tags.

A bundle contains outputs/align_episode.json, align_transcript.jsonl and
align_turns.jsonl, plus the usual raw telemetry, power_trace.csv, events,
metadata and summary_metrics.json. The runtime's episode precedes telemetry
stop; read_episode_bundle joins the immutable episode and trace in memory.
It never rewrites a finalized bundle.

Turn intervals delimit model calls. first_token_ns is the prefill-end event
specified by records.Turn, before the first decode step. Following tool waits
remain grouped under their originating turn. The episode ends before scoring
and serialization; register whether the residual integrates that interval or
the controller's slightly longer measured window.

Prefill/decode events carry align_turn_index; align_turns.jsonl and Episode
expose the individual turn timing. There are no enclosing align_turn_N phase
pairs: those would overlap the inner phases on the same power source and make
reduction fail. align_tool_N_M pairs occupy the intervening tool waits.
BundleReader.phase_windows returns the repeated inner phase pairs.

The generic single-request summary fields ttft_s, decode_latency_s and
energy_token_j are not printed for align members: they respectively describe
the first turn only, a span crossing later prefills/tools, and an episode-wide
denominator including tool energy. Episode.flags and align_episode.json name
all three in single_request_summary_fields_not_episode_metrics. Use the
registered episode residual and per-turn/phase attribution for align reporting;
the unchanged reducer still stores its generic fields.

## Clock and standalone sampling

ApplePowerSampler delegates capture, parsing and anchoring to
PowermetricsTelemetryAdapter. There is no second parser or invented anchor.
Sample endpoints already use the adapter's current rate-aware native-second
anchor. The bridge uses existing paired ClockStamp observations to map epoch
nanoseconds onto episode monotonic nanoseconds.

Mapping uncertainty carries the complete effective anchor bound. That bound
already includes the full wall-minus-monotonic span: only observations outside
the anchor envelope add bridge extent. Resolution of the separate episode
observations, including serialized-stamp rounding, remains additive.
Unbounded mappings instead carry their
observed bracket and clock resolutions, with clock_anchor_unresolved.
Each seconds-to-nanoseconds product is priced at math.ulp(x * 1e9) / 2
(128 ns near an epoch of 1.8e18 ns), plus integer rounding when the spacing is
sub-ns. Serialized stamp restoration also carries quotient rounding.
joulewise/clock.py is unchanged.

powermetrics_fiducial.py, kernel_clock.py and load_transition_alignment.py own
the existing calibration, dispatch/fence, frequency-residual and provisional
transition evidence. The bridge replaces none of them. The approximately 1 J
attribution limit is distinct from approximately 0.3 J repeatability noise;
common attribution bounds do not average away.

Native readings are interval averages. PowerTrace has a single averaging
width, so variable supports remain as integer intervals in trace.notes with a
flag. The existing raw/CSV intervals remain authoritative. mW-to-W conversion
does not establish sensor quantization.

The standalone sampler used outside the campaign controller has no battery,
AC, thermal or contention judgment. Every returned trace, even an empty one,
carries hazard.unjudged:battery,ac,thermal,contention in notes.flags; sampler.flags
also carries it. Its stop marker precedes a one-second post-window dwell,
matching quiet_mac_exploratory.json:post_window_sampling_dwell_s, and the adapter
receives that required tail. This collects right-edge support without adding
dwell to the measured episode. It adds no hazard enforcement and does not turn
standalone numbers into hazard-gated measurements.

## Battery assist and the 140 W adapter

The remedy already lives in joulewise/hazards/battery.py:span_findings and
smc_span_findings under the 2026-10-06 battery-assist ruling. B0AC is sampled
once a second. Discharge on AC while not charging is battery.assist (DISCLOSE):
counted and flagged, with no data lost. Processor rails are regulated downstream
of the supply, so battery assistance does not invalidate their energy.
Charging above +200 mA, IsCharging, AC loss and missing evidence retain the
existing exclusion rules. Arm-time idle admission is unchanged.

The repository observed B0AC bursts to -865 mA during inference on the 140 W
adapter (tests/hazards/test_battery.py, the minus-865 mA burst control;
battery.py documents the ruling). Heavier models may raise the disclosure more
often. Even a decode average below adapter capacity does not exclude transient
assist, so do not predict the flag from the adapter label alone.

There is no matched decode whole-machine measurement for these D1 candidates
in this lane. Expected draw is therefore an explicit pilot input for each:

| Candidate | Expected decode whole-machine draw | Comparison to 140 W / assist expectation |
|---|---|---|
| Qwen3-8B | P_8 W, to measure | P_8 - 140 W draw excess; assist possible, frequency unknown |
| Qwen3-32B | P_32 W, to measure | P_32 - 140 W; sustained deficit predicts assistance |
| Qwen3-30B-A3B | P_30A3 W, to measure | P_30A3 - 140 W; active experts alone do not determine machine draw |
| Llama-3.3-70B | P_70 W, to measure | P_70 - 140 W; heavier decode may increase assist frequency |

These P values must include the whole machine at a supply-comparable boundary,
including conversion losses where applicable, rather than just SoC rails.
battery.py's archived evidence identifies SystemPowerIn as mW and
SystemLoad = SystemPowerIn - BatteryPower; neither is silently assigned to a
new model. Inspect those readings beside B0AC during the pilot. No current
inclusion gap was found by source inspection; the real-bundle regression is
still unexecuted.

## Prospective D1 layout and capacity

A draft pack needs task assets and SHADE revision/environment pins, registered
analysis/extraction definitions, model/tokenizer receipts, policy, calibration
bookends, authenticated plan tree and launch bindings before measurement.
The generator creates none of that authority. Existing sealed packs stay
immutable. configs/gates/hazard_refusals.json marks the prospective workload
as outside the current registered-pack census; extend that census before D1
registration.

Candidate 4-bit weight lower bounds on a 128 GB machine are 4.0 GB (Qwen3-8B),
16.0 GB (Qwen3-32B), approximately 15.0 GB (Qwen3-30B-A3B, all experts resident)
and 35.0 GB (Llama-3.3-70B). Each is parameter_count * 4 / 8 in decimal GB.
Scales, tokenizer, activations, scratch and KV allocation add memory.
For the pinned config, KV bytes =
2 * layers * kv_heads * head_dim * context_tokens * bytes_per_element.
Check the Metal working-set limit and peak RSS before selecting context.

window_duration_margins.py is an authenticated margin calculator, not a
scheduler: it supplies D_min - 2*B_operative, D_min/(2*B_operative), interval
counts, sample margin and reducer cadence ratio. It uses the reducer's
MIN_PHASE_SAMPLES = 3 and SHORT_WINDOW_CADENCE_RATIO_MIN = 2.0. Register D1's
mapping into the comparative-cell inventory before requesting its receipt.

Capacity separately includes per-member cooldown:

    member_s = episode_s + prepare_warmup_s + idle_s + dwell_s + cooldown_s
    pairs = floor(floor((window_s - reserve_s) / member_s) / 2)

Illustrative inputs are window_s = 21600 (six hours), reserve_s = 3600 for
calibration/references/cleanup, episode_s = 180, prepare_warmup_s = 20,
idle_s = 30 and dwell_s = 1. All except the policy dwell are planning parameters,
not measured D1 throughput. quiet_mac_exploratory.json:cooldown.sustained_window_s
requires 30 s of recovered idle and cooldown.cap_s is 300 s:

| Per-member cooldown scenario | Member seconds | Member slots | Complete pairs / episodes |
|---|---:|---:|---:|
| 30 s recovered-idle window | 261 | 68 | 34 / 68 |
| 300 s cap budget | 531 | 33 | 16 / 32 |

The cap is a scheduling allowance, not a guarantee of admission. Extra model
load, retries or slower episodes reduce capacity. The reserve does not double
count the cooldown shown here.

## Detection power and quiet time

Let h be hidden tokens, e joules per hidden token, sigma_window the standard
deviation of a paired window residual, B a non-averaging decision-bound charge,
alpha the two-sided false-alarm probability and power the target probability:

    delta = h * e
    N = ceil(((z_(1-alpha/2) + z_power) * sigma_window / (delta-B))**2)

This applies when delta > B. Otherwise retain the finding that repetition
cannot clear the bound. Register fitting uncertainty and shared-window
dependence; do not divide B by sqrt(N).

Repo evidence provides approximately 0.0998 J/decode-token for Qwen2.5-1.5B
on this Mac: docs/legacy/strategy/2026-08-07-paper-portfolio/
SYNTHESIS-IMPACT-FIRST.md:5952 reconstructs (192.386 - 141.29) / 512.
That is historical evidence, not a D1-model estimate. Print sensitivity at
e = 0.05 and e = 0.1 J/token as explicit parameters. sigma_window is also
unmeasured for D1; the following is the stated scenario sigma_window = 5 J,
not an inferred noise figure.

With h = 128, alpha = 0.05, power = 0.80 and illustrative B = 2 J
(two approximately 1 J per-run attribution charges), the quantile sum
z_0.975 + z_0.80 = 2.801585218 gives:

| e (J/token), planning input | delta (J) | Science windows/model | Two models' science hours | Plus one 6 h pilot/model |
|---|---:|---:|---:|---:|
| 0.05 | 6.4 | 11 | 132 | 144 h / 24 windows |
| 0.10 | 12.8 | 2 | 24 | 36 h / 6 windows |

These numbers follow the formula: ceil((2.801585218*5/4.4)^2) and
ceil((2.801585218*5/10.8)^2). Replace B with the operative registered bound;
replace sigma_window and e with pilot-supported inputs. A single pilot window
per model is an allowance, not asserted sufficient evidence. At the capacity
scenarios above, 24 windows provide 768–1632 episode slots; six provide
192–408. Do not turn these conditional calculations into registered power.

## Registration and synthetic checks

Register the RQ, task/condition/seed roster, model revisions, templates,
sampling controls, tool behavior, visibility/tamper transform, all count sources,
fitting split, grouping, energy interval, harness-tail treatment, operative
bound, multiplicity, power target and independent analysis implementation.
Bind references, timing allowances, policy and authenticated launch lineage.
Merging joulewise/adapters/__init__.py changes measurement-path code, so existing
registered packs carry code.changed_since_registration; the lead controls
merge timing.

The six-turn/five-tool synthetic world specifies 27,648 prompt and 4,608 base
output tokens, plus 8.3 s in tools. D-019's 1 ms/prompt-token and
10 ms/output-token mock parameters at 7.5 W predict 82.028 s / 615.21 J;
256 hidden tokens predict +2.56 s / +19.2 J. These are analytic predictions,
not results observed by this seat. The native-plist world exercises the real
parser/anchor at 100 ms cadence; the HAZARD fixture tests an actual bundle
span against the real battery judge. See the lane report for execution status
and exact required test commands. Never run the whole suite from this brief.
