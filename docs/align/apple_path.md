# Apple alignment path (internal, provisional)

This is code and a prospective D1 plan for RQ-ALIGN-ENERGY-RESIDUAL.
Nothing is registered, armed or installed by this lane. The lead ran the
synthetic campaign and lane tests locally at 9162afd6d; the reviewer ran 19
lane tests and H1–H4 at b7739911b (H2 used real MLX with mock telemetry).
The lead's local run at 10352c24b ran 23 lane tests: 22 passed; the campaign
test failed strict validation because output_policy.emitted_tokens was absent.
The lead also ran H1/H3/H4/id_probe and real-MLX H2 at that head. The lead's
later local run at 86f441c93 executed the fix2c correction: all 23 lane tests
passed, including strict campaign validation; the MLX harness printed strict [].
Those results belong to the lead. Planning calculations remain derived.

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
Prepare also calls reset(seed), system_prompt and user_prompt before idle
admission. Tasks must tolerate repeated reset(seed): warmup and the measured
episode reset again. A measured episode with no model call returning generated
tokens fails with AdapterFailure(UNKNOWN_ERROR); later faults after returned
tokens remain recorded flags. A completion equal to max_tokens adds
turn_token_budget_reached:<turn index>, including an unclosed reasoning span.

MLX uses the existing in-process MlxRuntimeAdapter._generate helper, as current
suite workloads do. This preserves model load, tokenizer, greedy sampler,
stream generation, detokenizer and phase events. A separate mlx_lm.server
would add another process and dispatch boundary. Identity records model,
local source, revision, artifact identity, mlx and mlx-lm versions; the wrapper
projects the same model, sampler and fixed episode policy fields at readiness
and in the bundle. Model provenance forwards prepare's model_artifact_identity.
Sampler provenance records actual greedy settings, the requested temperature
and per-turn max_tokens; a nonzero request retains the mismatch flag and a
distinct identity. The fixed policy contains the registered turn/token budgets
and the stable stop rule episode_returns_or_turn_budget_reached.
The bundle's output_policy also carries the realized emitted_tokens, equal to
workload_observed.output_token_count, as strict campaign validation requires.
The identity builder projects only name, requested_tokens and stop_condition;
emitted_tokens therefore does not split identities. Readiness precedes
generation and carries only the fixed fields. episode_outcome retains
emitted_tokens and the actual stopping outcome outside governed identity.
Heavy libraries remain
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
attribution limit is distinct from the measured 0.29–0.49 J repeatability on
about 50 J points in windows a9/a10: [D-078 clause 11, 2026-07-25](../decision_log.md#d-078).
That entry contrasts repeatability with a per-member clock-anchor-shift envelope
of about 0.7–1.0 J. It also retains later provenance caveats on the old windows;
these are historical instrument diagnostics, not D1 calibration or claim authority.
Common attribution bounds do not average away.

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

The orchestrator's 2026-10-06 ruling corrects the -865 mA observation: it was
at model load, not during decode (both seats). Source:
~/night-archive/wallmeter-probe/verify/RULING_battery_assist_2026-10-06.md.
The synthetic battery test retains -865 mA because it exceeds the ruling's
200 mA limit by 665 mA; it is not a claim about inference load.

The measured overload validation, archived at
~/night-archive/wallmeter-probe/verify/b0ac_validation.md (2026-10-06 22:12Z),
used Qwen3-8B-4bit on MLX plus a 16-process CPU burner. System total (PSTR)
peaked at 158.3 W against the 140 W adapter, B0AC fell to -5331 mA, and
606.9 J was discharged during the 170 s load. When whole-machine draw
exceeds the adapter's supply, the battery supplies the difference. The ruling
reports unchanged 8B decode tokens/s under assist: 69.1–72.6 against 68.9–71.1.
That overloaded validation does not assign a quiet-machine draw to a D1 model.
Even a decode average below adapter capacity does not exclude transient assist.

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
new model. Inspect those readings beside B0AC during the pilot.
The lead's local lane tests at 9162afd6d, the reviewer's 19 passing tests at
b7739911b, and the 22 passing lane tests in the lead's local run at 10352c24b
exercised the real-bundle synthetic assist/charging regression. The sole
failure at 10352c24b was the campaign's missing emitted_tokens key.
These synthetic checks do not establish any D1 candidate's whole-machine draw.

D1 pilot battery checks (ruling item 6's evidence that would reopen it):

- Reproducible power-mode or power-limit transitions associated with assist.
- Lower rail power, frequency or tokens/s in assisted seconds against matched seconds.
- Battery-temperature rise concentrated in assisted stages.

Ruling item 5 requires each reported cell with and without battery.assist
members; print both, with neither selected after seeing the result.
Prepare, idle-baseline and warm-up reads are reported separately and decide
nothing about measured-request membership.

A model whose whole-machine draw stays above the adapter drains the battery
member after member. Once charging begins inside a later member's request,
that member is excluded under ruling item 2. Charging in prepare, idle or
warm-up decides nothing under item 5. For every pilot member record the
discharged energy already computed by battery.assist, registry state of charge
before and after, and whether IsCharging turns Yes inside a later request.
Battery capacity and the state of charge at which charging resumes under the
charge limit are parameters read at the pilot; no value is assumed here.
The lead owns whether cooldown should also wait for IsCharging = No.
The stale "during inference" docstring in joulewise/hazards/battery.py is also
outside this lane's write scope.

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

Let D_wi be the benign/sabotage pair's residual difference for pair i in
window w. Model D_wi = delta + W_w + epsilon_wi, where sigma_pair is the
standard deviation of one pair's residual difference conditional on its
window (the epsilon term), and sigma_w is the standard deviation of the shared
window effect W_w. Under independent pair errors within a window, independent
of W_w, the mean over n pairs has variance

    Var(mean_i D_wi) = sigma_w**2 + sigma_pair**2 / n
    sigma_window = sqrt(sigma_w**2 + sigma_pair**2 / n)

For independent windows with a fixed registered pair count n, N below counts
windows per model and sigma = sigma_window. Shared window noise does not
average down by adding pairs inside that window. N can instead count independent
pairs only when sigma is the spread of those independent pair differences
(for example one pair per independent window); pooling n pairs from one window
does not make them n independent units. Register covariance and unequal-n
handling rather than using the independent formula when those assumptions fail.

With h hidden tokens, e joules per hidden token, non-averaging decision-bound
charge B, two-sided false-alarm probability alpha and target power:

    delta = h * e
    N = ceil(((z_(1-alpha/2) + z_power) * sigma / (delta-B))**2)

This requires delta > B. Otherwise repetition cannot clear the bound.
Fitting uncertainty joins the registered variance/bound model. B never divides
by sqrt(N).

Historical design inputs (diagnostic/pre-genesis under D-117, not D1 claims):

- Qwen2.5-1.5B: (192.386 - 141.29) / 512 = 0.099796875 J/token,
  rounded to e = 0.0998 J/token. The reconstruction is at
  docs/legacy/strategy/2026-08-07-paper-portfolio/SYNTHESIS-IMPACT-FIRST.md:5952;
  141.29 J is the registered 7B minus 1.5B phase_energy_j.decode contrast in
  CLAIMS_STATUS.md. The 1.5B is smaller than every proposed D1 candidate.
- Qwen2.5-7B: 192.38623252628366 J / 512 output tokens =
  0.3757543604028978 J/token, rounded to e = 0.37575 J/token.
  This is the **absolute-cell member mean, n=10**, from
  window_7bfloor_20260729 (docs/decision_log.md:5445 and CLAIMS_STATUS.md's
  "7B decode floors" row). It covers the decode-phase energy
  (phase_energy_j.decode) of the 128-prompt/512-output-token df_ph_decode
  workload, not whole-machine draw or tool energy; see also
  docs/phase_2/splitwise_decode_campaign.md, floor plan.
  The 7B is the nearest measured model size to the proposed 8B–70B candidates.

The following **derived scenario** uses h = 128, alpha = 0.05, power = 0.80,
B = 2 J (two approximately 1 J per-run attribution charges), and
sigma = sigma_window = 5 J as a stated scenario parameter, not measured D1
noise. z_0.975 + z_0.80 = 2.801585218. The table uses the rounded e values above:

| Historical e (J/token) | delta (J) | Derived N windows/model | Two models' science windows / hours | Plus one 6 h pilot/model |
|---|---:|---:|---:|---:|
| 0.0998 (1.5B) | 12.7744 | 2 | 4 / 24 h | 6 windows / 36 h |
| 0.37575 (7B) | 48.096 | 1 | 2 / 12 h | 4 windows / 24 h |

Arithmetic: 128 * 0.0998 = 12.7744 J;
N = ceil((2.801585218 * 5 / (12.7744 - 2))**2)
= ceil(1.6902910574) = 2. At 0.37575, delta = 128 * 0.37575 = 48.096 J;
N = ceil((2.801585218 * 5 / 46.096)**2) = ceil(0.0923466619) = 1.
Science time is 2 models * N * 6 h; the illustrative pilot adds 2 * 6 h.
At 32–68 episode slots per window from the capacity scenarios, six windows
provide 6 * (32–68) = 192–408 slots; four provide 4 * (32–68) = 128–272 slots.
These slots include the pilot allowance, not just science episodes.

N = 1 or 2 assumes a known sigma and normal z quantiles. In practice the
pilot must estimate sigma_pair and sigma_w; the number of independent units
needed for that estimate, with t quantiles and their degrees of freedom,
sets the count rather than these small known-sigma answers. One pilot window
per model is a time allowance, not sufficient evidence for sigma_w.
Replace B with the operative registered bound and e/noise with pilot-supported
inputs. Calibration, admission, charging exclusions and failed recovery can
increase quiet time. These calculations are conditional planning, not
registered detection power.

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
256 hidden tokens give derived +2.56 s / +19.2 J. The lead's local run at
9162afd6d observed 82.028 s / 615.21 J and 84.588 s / 634.41 J through the
campaign/controller/mock-runtime/mock-telemetry/bundle path. The reviewer at
b7739911b ran the offset-clock H1 world at 100 Hz with phase-dependent power:
worst-turn integration error was 0.02 J, and hidden tokens added
+63.999944957700336 J against derived 64.0 J, with FAILURES 0.
Those are reviewer-measured at b7739911b, not this seat's observations.

The lead's local run at 10352c24b repeated H1 at 100 Hz: both members
succeeded, offset_ns=-1790901234567899904, uncertainty 5123/5004 ns,
dE turns=63.999944957700336 J against derived 64.0 J, FAILURES 0.
H3/H4 verified that reset faults stop at prepare with
unsupported/runtime_unavailable under both clocks and turn-0 no-output
calls fail/unknown_error; H3 also carries turn_token_budget_reached:5.
The lead's id_probe built the mock governed identity.

Lead-measured H2 at 10352c24b used real Qwen3-1.7B-4bit, local revision
3b1b1768f8f8cf8351c712464f906e86c2b8269e, mlx_lm 0.31.3,
SystemClock and mock telemetry. It succeeded with one turn, prefill 168,
decode 768 and episode 3.151 s; turn_token_budget_reached:0 and
unclosed_reasoning_span were recorded. Identity built, the readiness
fixed policy agreed with the bundle (requested_tokens=4608 and the stable
stop rule), output_token_count=768, and records round-trip True.
The native-plist world exercises the real parser/anchor at 100 ms cadence;
the HAZARD fixture tests an actual bundle span against the real battery judge.
The lead's 23-test lane run at that head had one strict campaign failure:
the bundle's output_policy lacked emitted_tokens. Fix2c restores that
realized count and checks equality with the observed member, retaining
identity/readiness equality checks. The lead executed the correction locally
at 86f441c93: all 23 lane tests passed, the campaign passed strict validation,
and the MLX normal/truncate/think harnesses printed strict []. This is the
lead's evidence, not a cloud-seat execution. See the lane report for exact
commands, attribution and remaining checks.
Never run the whole suite from this brief.
