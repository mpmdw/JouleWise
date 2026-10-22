# Apple alignment path (internal, provisional)

This lane supplies code and a prospective D1 plan. It has not measured the M3
Max, registered a campaign, installed a job, started a sampler or loaded a model.
The cloud executor was unavailable during this build; the lane report states
the outstanding execution checks. Treat the implementation as an unverified
draft until those checks pass.

The electrical question remains RQ-ALIGN-ENERGY-RESIDUAL: does work omitted from
the visible log leave energy beyond a benign token/context prediction? SoC
power can count extra inference work. It cannot identify reasoning that fits
inside the same forward passes.

## Execution and records

Use workload_profile.name = "align_episode". Its prompt_text contains the
canonical EpisodeSpec JSON, not a prompt for the model. The runtime registry
wraps the selected existing runtime. Each member has repetitions = 1, one task
factory, condition and seed. Replicate by generating another member, preserving
the episode as the unit. The factory is an installed local module:callable that
returns the shared AgentTask protocol. If it declares a clock parameter, the
factory receives the controller's injected clock; this makes tools and model
calls share simulated time in tests.

MLX runs in process through MlxRuntimeAdapter._generate. Existing suite
workloads already use that helper, including natural EOS. Reusing it preserves
the model load, sampler pin, stream generation, detokenizer and phase-marker
path. A separate mlx_lm.server would introduce another process and dispatch
boundary without improving this instrument path. Identity includes model,
local source, revision, artifact identity, mlx and mlx-lm versions. MLX remains
a lazy optional dependency. Episode preparation requires an existing local
model directory and records an unavailable flag instead of downloading weights. The runtime's greedy sampler remains authoritative;
a nonzero requested temperature is a recorded mismatch. No KV prefix is claimed:
each chat call sends its full rendered prompt and cached_prompt_tokens is zero.

The endpoint uses the model tokenizer's chat template, with tools, then encodes
without adding special tokens a second time. Explicit Qwen-style <tool_call>
envelopes become tool requests. Other formats remain visible text. Thinking
spans are preserved in the full transcript; retokenized reasoning counts carry
a flag because delimiter token boundaries can differ from the stream.

The existing controller owns idle admission, warmup, sampling, hazard bindings,
post-window dwell, cleanup, raw custody and reduction. This lane adds no
campaign launcher or alternate admission policy. generate_campaign calls the
existing scripts.generate_matrix.build_config and shared campaign-generator
render/write-boundary functions. Its members are inputs to scripts/run_campaign.py.
A HAZARD_PACK launch supplies the same authenticated lineage and policy as any
other workload. The draft generator does not create or impersonate that lineage.

Each bundle contains outputs/align_episode.json, align_transcript.jsonl and
align_turns.jsonl, plus the ordinary power_trace.csv, raw telemetry, metadata,
events and summary. The episode written by the runtime points to the power
join in that bundle, because the controller stops telemetry after runtime return.
read_episode_bundle joins those immutable inputs in memory and returns an
Episode with power_traces and clock_mappings. It never rewrites a finalized
bundle. Standard prompt provenance hashes the actual concatenation of all
turn prompt token IDs; turn provenance retains the individual IDs and counts.

Turn.start_ns/end_ns delimit the model call, as records.py specifies. ToolCall
intervals follow their model call and are grouped under that turn. Episode end
includes the tools, but precedes task scoring and serialization. The controller
measured window also contains that harness tail; register which interval the
residual analysis integrates. Ordinary prefill/decode phase pairs are repeated
per turn with align_turn_index metadata. Additional align_turn_N and
align_tool_N_M phase pairs expose each call and tool separately.
BundleReader.phase_windows returns the repeated pairs; phase_boundary_envelope
can receive an adjacent prefill/decode pair from the chosen turn.

## Clock and power

ApplePowerSampler delegates to PowermetricsTelemetryAdapter.start_sampling and
stop_sampling_with_evidence. Native parsing and rate-aware set-membership
anchoring remain in the existing adapter and uncertainty_evidence modules.
There is no second plist parser and no spawn-midpoint anchor.

The adapter already reconstructs sample endpoints in controller epoch seconds.
The lane converts them to integer epoch nanoseconds in a named trace domain,
then maps them onto the episode's monotonic domain using the paired ClockStamp
envelope. Mapping uncertainty carries the complete effective native-anchor
bound, the additional bridge envelope and float-to-integer representation.
Unresolved anchors retain traces with clock_anchor_unresolved. Such a flag
records missing attribution evidence; it does not fabricate a zero error bar.

Read powermetrics_fiducial.py, kernel_clock.py and load_transition_alignment.py
as complementary evidence: a fitted fiducial bound prices dispatch/fence and
load-transition mismatch; the kernel-frequency gate prices the correction-rate
residual; the transition artifact remains provisional until adjudicated.
This bridge replaces none of those calibrations, gate identities or transfer
assumptions. The ~1 J attribution limit is not the ~0.3 J repeatability noise,
and repeated episodes do not average away a common attribution bound.

Each native sample has interval-average support. records.v1 provides only one
averaging_window_ns per trace; varying supports therefore remain as integer
intervals in trace.notes and carry a flag, with the ordinary CSV/raw evidence
remaining authoritative for existing integration and phase-share tools. Do not
feed such a trace to a consumer that silently assumes instantaneous readings.
The mW-to-W conversion does not establish a sensor quantum; resolution is unknown.

## Prospective D1 pack and capacity

A prospective output directory contains align_pack.json and members/*.json.
Before measurement it also needs registered task assets, upstream revision pins,
analysis/extraction definitions, model/tokenizer receipts, the campaign policy,
calibration and bracket references, the authenticated plan tree and launch
bindings. Those prospective objects are not generated as registered evidence by
this lane. Existing sealed block-5 packs and their bytes remain untouched.

Candidates that can plausibly fit a 128 GB unified-memory machine include:

| Candidate | Weight lower bound at 4 bits/parameter | Qualification |
|---|---:|---|
| Qwen3-8B | 4.0 GB | small-model pilot; BF16 weight lower bound is 16.0 GB |
| Qwen3-32B | 16.0 GB | larger dense comparison |
| Qwen3-30B-A3B | approximately 15.0 GB | all experts must reside, not only the active parameters |
| Llama-3.3-70B | 35.0 GB | larger optional comparison; establish performance before scheduling |

These are parameter_count * bits / 8 in decimal GB, not measured resident sets.
Quantization scales, tokenizer, activations, scratch allocation and KV cache add
memory. Derive KV bytes from the pinned config as
2 * layers * kv_heads * head_dim * context_tokens * bytes_per_element.
Check the local Metal working-set limit and observed peak RSS before selecting
a model/context. A fitting weight file alone is not a successful admission.

window_duration_margins.py is an authenticated margin calculator, not a
scheduler. It prints D_min - 2*B_operative, D_min/(2*B_operative), overlapping
interval counts, sample-count margin and reducer cadence ratio for registered
comparative cells. It imports MIN_PHASE_SAMPLES = 3 and
SHORT_WINDOW_CADENCE_RATIO_MIN = 2.0 from the reducer. D1 must use authenticated
bounds and membership, then inspect these same quantities for the intended
turn phases. Do not turn a missing registration into a passing receipt.
The existing extraction inventory is ABBA/contrast shaped; register the D1
cell/design mapping before requesting an authenticated margin receipt.

Capacity must be a separate, explicit planning calculation:

    member_seconds = episode_seconds + prepare_and_warmup_seconds
                     + idle_seconds + dwell_seconds
    pair_capacity = floor(floor((window_seconds - reserve_seconds)
                                / member_seconds) / 2)

For an illustrative planning parameter set, take a six-hour window,
reserve_seconds = 3600 for calibration/references/cooldown/cleanup,
episode_seconds = 180, prepare_and_warmup_seconds = 20, idle_seconds = 30
and dwell_seconds = 1. The last value is the existing minimum powermetrics
post-window dwell; the other durations are planning inputs to replace with
pilot observations. This gives 231 seconds/member, 77 member slots and
38 complete benign/sabotage pairs (76 episodes) per window. The spare slot
does not manufacture a pair. More cooldown, model load or slower episodes
reduce that capacity. Margin evidence can further constrain viable turn
durations; it cannot supply scheduling overhead that it never measured.

## Detection-power scenario and quiet time

Use windows as independent units when episodes share a calibration/drift
environment. Let e be the pilot joules per hidden token, h the hidden-token
effect, sigma_window the standard deviation of the paired window residual,
B the non-averaging decision-bound charge, alpha the two-sided false-alarm
probability and power the target detection probability. The normal planning
approximation is:

    delta = h * e
    N_windows = ceil(((z_(1-alpha/2) + z_power) * sigma_window
                      / (delta - B)) ** 2), when delta > B

When delta <= B, retain and report that the stipulated effect cannot clear
this bound by repetition. Include residual-model fitting uncertainty in
sigma_window or a separately registered bound. Do not divide B by sqrt(N).

One stated scenario uses planning parameters h = 128 tokens, e = 0.05 J/token,
sigma_window = 5 J, alpha = 0.05 and power = 0.80. Assign B = 2 J as the
illustrative sum of two 1 J per-run attribution bounds. These are scenario
parameters, not measured MLX performance or a replacement for the operative
registered bound. Then delta = 6.4 J, delta-B = 4.4 J and
ceil((2.801585218 * 5 / 4.4)^2) = 11 science windows per model.
The quantile sum is z_0.975 + z_0.80. Hold that systematic charge fixed.

At the 38-pair capacity, two models need 22 science windows, or 132 quiet
machine hours. If one additional six-hour benign fitting/pilot window per model
is sufficient (another planning input), the total is 24 windows, 144 hours,
and at most 1824 episode slots at 76/window. One fitting window is not asserted
to establish sigma_window or validate the normal model; increase that allowance
if the pilot cannot support them. A 256-token scenario with all other inputs
fixed gives ceil((2.801585218 * 5 / 10.8)^2) = 2 science windows/model, illustrating
how strongly the cost depends on the hypothesized hidden-work effect.

## Register and verify before a real run

Register the RQ, task-pair roster, SHADE code/environment pins, conditions, seeds,
model revisions, tokenizer/chat-template hashes, greedy sampling controls,
turn/output budgets, tool behavior and monitor visibility. Pin every source of
the full and visible token counts, reasoning-count approximation and tamper
transform. Record flags without silently removing episodes.

Register the fitting split and grouped evaluation, gross SoC energy interval,
harness-tail treatment, idle subtraction if any, phase/tool boundaries,
calibration transfer assumptions, operative bound, window grouping, multiplicity,
power target and the independent implementation used to check the analysis.
Bind the capacity inputs, references, calibration slots, hazard policy and
authenticated launch lineage. No registration, loading or arming is performed
by generating this draft pack.

The synthetic tests contain a six-turn, five-tool episode with 27,648 uncached
prompt tokens, 4,608 output tokens and 8.3 seconds in local tools. D-019's
1 ms/prompt-token and 10 ms/output-token mock runtime predicts 82.028 seconds
and 615.21 J at the existing 7.5 W mock power. Adding 256 hidden final-turn
tokens predicts 2.56 seconds and 19.2 J extra while visible decode counts stay
equal. A separate 61-second native plist world has a 100 ms cadence and
0.2 W rail oscillations. These are proposed test worlds, not executed results.

Run from the repository root, with a fresh external TMPDIR and
JW_B5_SYNTHETIC_ONLY=1:

    python3 -m unittest discover -s tests/align -t .
    python3 -m unittest discover -s tests

The first command must exercise the actual campaign subprocess and strict
bundle validation. The full suite must also determine whether new module/test
names need minimal additions to timing, import-fence or inventory registries.
No optional dependency has been installed in this seat.
