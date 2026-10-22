# Whole-GPU campaign kit (internal, PROVISIONAL)

This kit builds the rented-server workflow. It does not rent hardware or authorize
paid APIs. Ed approves provider and spend before any paid session. The director
and reviewer executed earlier heads; their supplied evidence is separated from
this round's work in the lane report. This seat has no working executor and
claims no Python/shell test or repro run of its own.
PR #521 remains draft. Final-head integrated offline rehearsal is required before rental.

Power can count extra work; it cannot distinguish computations within one forward
pass. This lane measures server GPUs; Mac MagSafe/battery behavior is outside it.

## What Ed approves

Approve the provider, exact whole-GPU class/count, maximum rental duration and
spend, supplied USD/GPU-hour quote, model/precision/layout, monitor/judge placement,
and copy-back destination. No example provider prices are committed.
Pin model/tokenizer/server/data revisions before running; null revisions are flags.

Budget Qwen3-Next precision is an unresolved scientific configuration choice:

| Option on H100-SXM-80GB | Weight arithmetic | Capacity before KV/scales/allocator |
|---|---|---|
| BF16, tensor parallel 4 | 80B x 2 bytes = 160 GB | 4 x 80 GB = 320 GB; 160 GB remains |
| FP8, tensor parallel 2 | 80B x 1 byte = 80 GB ideal weights | 2 x 80 GB = 160 GB; 80 GB remains |

Two 80 GB GPUs leave zero headroom for BF16; one leaves zero for FP8.
The 80B count comes from the budget protocol and Qwen model card; H100 memory
comes from the cited NVIDIA datasheet in each matrix. KV/activations/quantization
scales/allocator headroom is the explicit per-model kv_headroom_bytes parameter.
It stays null, with an unverified-fit flag, until an operator sets it.
Tensor-parallel compatibility and actual allocation still need a serving preflight.

Qwen publishes [Qwen3-Next-80B-A3B-Thinking-FP8](https://huggingface.co/Qwen/Qwen3-Next-80B-A3B-Thinking-FP8).
Its [pinned model card](https://huggingface.co/Qwen/Qwen3-Next-80B-A3B-Thinking-FP8/blob/1a28d48a94e799860201879be67616b9e21c4bd2/README.md)
was fetched by the lead and quoted in the fix-2 brief, including its FP8 serve
command; this seat did not fetch it. Model dimension/count sources now point
directly to the supplied immutable HF configs/cards. The provisional matrix uses BF16/4; either alternative runs by
copying its checkpoint, weight_precision, tensor_parallel_size and headroom into
that model's fields. This choice changes the joules' configuration and needs Ed.

## Matrices and work accounting

The lane-local matrix.schema.json is the planning format. runner_adapter converts
SHADE/MoE to the runner's documented format. It does not change records.py.

| Matrix | Requested trial rows | Fresh generation Episodes | Off-box monitor calls |
|---|---:|---:|---:|
| shade.json | 60 | 60 | 180 |
| moe_stage_a.json | 30 | 30 | 90 |
| budget.json | 26,400 | 36,000 | 26,400 |

SHADE: five public pairs x benign/sabotage x three specified seeds x two models
(Qwen3-8B and Qwen3-30B-A3B). MoE Stage A repeats the MoE model's rows and requires
an actual RouterLog in every episode. An adapter setting cannot create that log.

Budget follows [budget lane 58750718f](https://github.com/mpmdw/JouleWise/tree/58750718f/joulewise/align/budget),
including its run.py and conditions.py, and docs/align/budget_pilot.md at that commit.
The 200-item count is a pilot workload choice. Per model: 200 x 3 calibration
Episodes, plus 200 x 3 seeds x 7 live conditions x 2 hinted/no-hint generations =
9,000 fresh Episodes. Eleven views x 200 x 3 = 6,600 monitor calls.
The four forcing fractions are 1.0, 0.6, 0.4 and 0.3; deletion views reuse
thinking-on generations and add no generation. Forced reasoning and answer are two
Turns inside one Episode when the cap is positive, one at zero. At positive caps,
the per-model call count is 600 + 200 x 3 x 2 x (3 + 4 x 2) = 13,800, rather than
13,800 Episodes. Calibration has no paired call and no monitor call.
Models are Qwen3-4B/8B/14B and Qwen3-Next-80B-A3B-Thinking. The off-box fixed
monitor is openai/gpt-oss-20b. The inspected code and document agree on these counts.

Budget effort names are not shared Episode.condition values. The default runner
adapter records budget_runner_adapter_required and retains the requested matrix.
Its explicit budget driver must export fresh hinted, paired and calibration
Episodes separately from reused deletion views, plus trial/condition provenance.
This driver integration is still an OPEN ISSUE; do not begin a budget rental
expecting the generic runner to execute it.

## Calibration before a full campaign

There is no sourced typical SHADE turn count or token volume. No setup/load/router
allowance is established. Those inputs and committed bounds are null. For example:

    python3 -m joulewise.align.gpukit.cost configs/align/shade.json --gpu-class H100-SXM-80GB

prints lower_bound_status and plan_status as unavailable, with named missing-input
flags. Hardware/model cards establish optimistic roofline rates, not throughput.
A bound is not a rental budget.

The first paid work is a separately approved calibration slice. --calibration-slice
keeps every agent model and every task/condition stratum and chooses the first
specified seed: 20 Episodes for SHADE, 10 for MoE. Using all strata avoids substituting
an invented typical task shape and preserves the full matrix's equal mixture.
For budget this option only removes extra seeds; a smaller, balanced item slice
and its custom driver still need integration before paid use.

Ed can bound the runner portion without a throughput assumption: for M sequential
models, each with runner timeout T, a whole box holding G measured devices and
an optional extra monitor device, at supplied price P, the runner-phase cap is
M x T x (G + extra) x P / 3600 USD. This is a policy cap, not an estimate.
Use the provider's absolute rental/auto-shutdown cap to bound installation,
readiness, probes, transfer and billing after the session too. Approve that total
wall-time cap x held GPUs x price; the runner timeout alone does not bound the meter.

After the slice:

    python3 -m joulewise.align.gpukit.cost configs/align/shade.json --gpu-class H100-SXM-80GB --calibration /path/to/slice-bundle --usd-per-gpu-hour "$GPU_PRICE"

--calibration also accepts an Episodes JSONL file. The result prints observed
per-model episode count, mean bracket duration, prefill/decode volumes, projected
generation_wall_seconds and the input path. It includes failures as flagged data.
It is an extrapolation, not a bound. Setup/model load/off-box scoring waits remain
unmeasured by Episodes, so full wall_seconds/gpu_hours/total_usd stay unavailable.
A complete receipt-based rental extrapolation remains an OPEN ISSUE; do not approve
a full campaign from generation_wall_seconds alone. Budget additionally needs its
condition/calibration/paired strata preserved for valid extrapolation.

Per-model ideal BF16 bounds aggregate N GPUs' cited bandwidth/FLOP/s optimistically;
no TP speedup or FP8 compute rate is claimed. GPU-hours multiply by the device count.
A sourced-efficiency plan, when all allowances exist, bills the entire measured
pool while models run serially and loads each agent once. Monitor/judge tokens
never enter agent-GPU inference time. --monitor-placement gpu puts the extra held
device's hours and separately supplied price on monitor_gpu_hours/monitor_total_usd.

Decode weight reads exclude the input embedding lookup but retain the entire
output head, tied or untied. For dense Qwen use the printed non-embedding count
plus vocab_size x hidden_size; this avoids subtracting independently rounded card
totals. For the MoE/Phi active count, subtract that input table once. Each config
cites the card counts and config fields. Derived display values have two significant
digits, bounds downward with decimal arithmetic; integer inventories/counts stay exact.

Numeric provenance convention under workload/gpu_classes/model_parameters:
each numeric leaf has a sibling <key>_source (dated HTTPS URL plus quote/note),
a parent source citation, <key>_derivation, or a parent derivation referencing the
cited inputs. Unknown quantities are null. Bare "operator supplied" is not a source.

## Preparing and running a session

Use a fresh Ubuntu box with NVIDIA driver, Bash, Python >=3.11 and venv available.
Stage the repo, pinned public upstream data, reviewed factory module/settings, and
model artifacts before the paid period where possible. No credentials belong in
matrices, argv templates or receipts. An external client setting may name a
credential environment variable; its factory reads it without serializing its value.

Time limits and cadence are operator policy. Supply:
--ready-timeout-s for loading/readiness; --command-timeout-s for short probes (nvidia-smi, pip freeze, git);
--preflight-timeout-s for preflight; --copy-timeout-s for each copy-back command;
--runner-timeout-s separately for each campaign subprocess; --poll-s for readiness.
Preflight limit derivation: the NVML defaults take 22 s (idle 10 s + load 10 s +
recovery 2 s, power/preflight.py defaults), plus interpreter, torch import and CUDA
context startup, unknown before the first box. Time one preflight during setup
and set --preflight-timeout-s above it. A long limit costs waiting on a hung
preflight; a short one refuses with nvml_preflight_timeout.

Copy limit derivation: archive bytes divided by the slowest accepted transfer rate.
The reviewer measured about 44 kB per episode-second per GPU before compression:
N episodes of T seconds on G GPUs produce about 44e3 x N x T x G bytes before
compression. Set --copy-timeout-s from that size and the accepted rate. Expiry
records copy_timeout and keeps the archive.

Bootstrap additionally requires --probe-timeout-s or JOULEWISE_PROBE_TIMEOUT_S,
and --gpu-index/--gpu-indices or JOULEWISE_GPU_INDICES.
Both --skip-install --check-only orders work. --skip-install reuses the prepared
venv and vLLM on PATH. Installation pins vLLM 0.10.2 and installs this repository.

After filling the policy variables and selecting monitor placement:

    bash joulewise/align/gpukit/bootstrap.sh --probe-timeout-s "$PROBE_TIMEOUT" --gpu-indices "$MEASURED_GPU_INDICES" --check-only --skip-install

    bash joulewise/align/gpukit/bootstrap.sh --skip-install configs/align/shade.json --output /path/to/new-slice --calibration-slice --runner-settings /path/to/reviewed-settings.json --gpu-indices "$MEASURED_GPU_INDICES" --probe-timeout-s "$PROBE_TIMEOUT" --ready-timeout-s "$READY_TIMEOUT" --command-timeout-s "$PROBE_TIMEOUT" --preflight-timeout-s "$PREFLIGHT_TIMEOUT" --copy-timeout-s "$COPY_TIMEOUT" --runner-timeout-s "$RUNNER_TIMEOUT" --poll-s "$POLL_INTERVAL" --monitor-placement none

Use a new output directory for each session. A fresh session nonce in receipt.json
enters every translated matrix_id, so repeat sessions have disjoint episode IDs.
Custom drivers receive {session_id} and must use it in their own episode identities.

Each model starts vLLM with --tensor-parallel-size and CUDA_VISIBLE_DEVICES naming
its measured devices. --gpu-indices supplies the physical pool, or --gpu-index
starts a contiguous pool sized for the largest per-model TP. All measured indices
are inventoried and preflighted. The sampler settings must request {device_indices};
the receipt checks for every measured device's gpuN channel.

## Off-box monitor and judge placement

--monitor-placement is required and has no default host:

- external: supply --monitor-base-url and optionally --judge-base-url; absent
  separate judge URL uses the monitor service/model. The operator verifies that
  service is off measured devices. Known loopback overlap with the agent port is
  flagged and deferred. Do not put secrets in URLs.
- gpu: supply --monitor-gpu-index and --monitor-port. This device must be distinct
  from the measured pool and passes the same whole-GPU check/refusal. Its one vLLM
  server remains resident for the session and is never sampled. Monitor and judge
  share its served model. If a distinct judge model/service is needed, use external.
- none: run agent Episodes and keep transcripts, flag monitoring_deferred and
  judging_deferred for a later off-box pass. This does not refuse the campaign.

The measured vLLM serves the agent model only. The api_key_calendar_agendas_2 and
expenditure_accounting SHADE pairs require an LLM judge; their factory config must
bind {judge_base_url}/{judge_model} or handle None by leaving the score deferred.
See the [SHADE lane assessment](https://github.com/mpmdw/JouleWise/blob/lane/2026-10-21-align-shade/docs/align/shade_port.md).
A failed extra monitor server also leaves scoring deferred while agent work proceeds.

## Runner settings and explicit config binding

Required settings: task_factory, endpoint_factory, sampler_factory,
token_counter_factory, order_seed, max_turns, max_tokens, temperature; monitor_factory
when monitoring is enabled. Optional imports installs trusted already-staged factory
registrations. Optional *_config dictionaries are passed unchanged apart from
placeholders. No constructor keys are injected.

Available typed placeholders: {agent_model}, {agent_base_url}, {agent_revision},
{monitor_model}, {monitor_base_url}, {judge_model}, {judge_base_url}, {interval_ns},
{device_indices}, {router_logging}. A whole placeholder preserves int/list/bool/None
type; an embedded placeholder is text. Base URLs are normalized to /v1.
task_pair exists only outside task.config; FactoryContext supplies it to the factory.
Optional clock and clock_domain pass through to the runner.

Offline built-in mock settings (runner lane needed; this is not scientific data):

    {
      "task_factory": "mock.inbox",
      "endpoint_factory": "mock.scripted",
      "monitor_factory": "mock.monitor",
      "sampler_factory": "mock.power",
      "token_counter_factory": "mock.tokens",
      "clock": {"factory": "mock.clock"},
      "clock_domain": "mock.monotonic",
      "order_seed": 7, "max_turns": 40, "max_tokens": 600, "temperature": 0.0
    }

The synthetic-8B identity in declared mock endpoint/power records makes no HF model
claim; mock power alone makes them incomplete. A non-mock episode identifying a
different agent model is flagged. These mock settings intentionally request no
constructor keys that the built-in factories reject.

A real settings file names reviewed registered factories and includes only their
accepted arguments; e.g. endpoint_config can request model/base_url and sampler_config
can request device_indices/interval_ns. Include router_logging only if that specific
factory accepts and implements it. Real SHADE/NVML factory registration and the
vLLM worker router capture remain sibling-integration dependencies.

## NVML verdict and supply hazards

The default command is:

    python -m joulewise.align.power.preflight --out /path/to/output/preflight.json --device 0

There is one --device per measured physical index, and none for the monitor GPU.
The report is bundled; its refused, measurement_ready and flags enter the receipt.
refused=true refuses with CLI exit 2, no model directories, and a sealed bundle.
No readable report also refuses with nvml_preflight_unavailable. Under the amended
R4/C2 ruling, measurement_ready must be the JSON boolean true: false, missing, null
or another type refuses with nvml_measurement_not_ready. That field demonstrates
that power moved under load on every measured GPU. Without that demonstration the
campaign would spend paid time without a working instrument. All report fields
and flags remain in the sealed evidence. A usage-error exit is not a verdict;
refused=false and measurement_ready=true permit proceeding, with a nonzero exit
recorded as a flag.

A custom --preflight-command receives --out <output>/preflight.json and one
--device <index> per measured GPU. It must write the NVML report format to --out,
including boolean refused, boolean measurement_ready and a flags list. Stdout
alone is insufficient; a fixture must write that same format too.

Supply and power-limit throttling are physical hazards on rented boxes. A software
power cap reduces clocks under load; a platform/board power brake or hardware
slowdown can reduce them further, changing both energy and time per token.
The kit never changes limits to hide this evidence.

At session start and before/after every model, measured devices are queried using
nvidia-smi -i N -q -x --dtd. Raw XML, driver DTD when available, reasons, cumulative
microsecond counters, and default/enforced/requested/current board power limits are bundled.
Old clocks_throttle_reasons and current clocks_event_reasons are supported.
A positive hardware counter tick or active hardware reason raises a flag.
Software power-cap deltas remain recorded quantities, not errors. Missing elements,
unsupported counters, read failures and counter resets are flags, never refusals.
Inspect receipt.throttle_start, models[].throttle_changes and the saved XML/JSON.

Names were checked against the NVIDIA driver DTD embedded in
[this public v7 XML](https://github.com/rai-project/nvidia-smi/blob/864eb441c9ae3171601e2e9df942b9ca386612c0/_fixtures/example2.xml)
and current [v13 driver XML types](https://github.com/influxdata/telegraf/blob/2156aa5089436522eec36b05fad94d850c728388/plugins/inputs/nvidia_smi/schema_v13/types.go),
accessed 2026-10-22. NVIDIA documents
[clock-event reasons and counters](https://docs.nvidia.com/deploy/nvidia-smi/index.html).
Raw --dtd capture is the check against the installed driver. Snapshots cannot locate
an event inside one Episode: the nvml lane should add these counters/reasons to
each power sample, using nvmlDeviceGetViolationStatus or clock-event-reason calls.

## What data_complete means and recovery

data_complete means every planned (task_pair, condition, seed) coordinate occurs
exactly once per model, every Episode has a turn and no work-breaking runner flag,
every measured device has at least one supported non-mock trace, and supported
traces pass R5's cycle, edge and power-hole checks (derived below). ClockMapping
offset/uncertainty applies at edges; offset cancels inside a trace. Unsupported
channels, power.empty alone and covered lost reads do not invalidate completeness.
A single sample in a long episode fails the edge check. Scoring may be deferred.
This is a coverage test, not a sensor-calibration or scientific-admission verdict.

Dotted endpoint/runner/factory/task/sampler failures, interrupted/max-turn episodes,
empty supported traces, unknown conditions, unclosed/uncounted scratchpads and usage/clock/tool/token-counter failures invalidate
completeness. Monitor/score failures stay recorded without erasing agent/power work;
deferred scoring reads preserved transcripts. A declared mock trace cannot pass.

Runner and vLLM subprocesses own process groups. Runner timeout flags and kills its
whole group, including sampler-like grandchildren. Readiness failure cleans the
vLLM group. Failed/incomplete outputs are still sealed. Do not reuse the output
directory or silently overwrite raw results.

The session writes receipt.json, preflight.json, matrices, logs, Episodes and runner
transcripts; manifest.json hashes all regular payload files, then a tar.gz and a
detached SHA-256 cover the bundle. Transfer receipts stay beside the sealed archive.
Use --destination with --copy-kind local/rsync/s3 and ambient authentication.
Copy failure keeps the local archive and is a transfer flag. After extraction,
verify_manifest checks missing/changed/unexpected files; verify the detached
archive hash as well. No secret values belong in the bundle.

## Build verification still required

From the uninstalled repo with no external PYTHONPATH, set TMPDIR=/tmp/gk-tmp and
JW_B5_SYNTHETIC_ONLY=1 and run:

    python3 -m unittest tests.align.test_gpukit -v
    python3 -m unittest tests.align.test_gpukit_round2 -v
    python3 -m unittest discover -s tests/align -t .

Repeat in a throwaway venv with jsonschema, then run the supplied reviewer repros
and integrated runner/NVML tree cases. None ran in this continuation seat. The
report separates the supplied reviewer/lead evidence at 28b9a22f4 from this
seat's final-head commands still NOT RUN. The fix-2 harness needs no new CLI
options or signature adaptations. Never rent
on the strength of the authored test inventory alone.

### Round-2 power completeness (R5)

Per episode, exclude channels whose notes JSON says supported=false, recording
episode_power_channel_unsupported:<channel>. Every measured gpuN needs a supported
trace, and each supported trace needs samples. power.empty alone is descriptive.

For each device, D is the sum of twice each supported channel's maximum recorded
timing half-width. Expected spacing E=max(nominal interval+D, sensor period).
Only deduplicated driver fields (nonempty field_timestamps_us) use a sensor period:
sensor_facts.period_ns, or the median driver timestamp step in microseconds times
1000 with a provenance flag. Realized cycle C is the median gap overlapping the
episode, or E with no such gap. C>2E fails the cycle check; B=2*max(C,E) is the
lost-read bar. An edge beyond B plus clock-offset uncertainty fails coverage.
For watts, an interior gap beyond max(B, output_averaging_window_ns) is a hole.
Cumulative joules span any interior gap. Interior gaps have no offset uncertainty
because it cancels. Gaps above B that leave no hole are recorded lost reads and
do not invalidate completeness. These factors implement the lead's R5 ruling.

Each model receipt includes power_coverage: episodes_checked,
episodes_incomplete_on_power, episodes_with_lost_reads, max_gap_over_bar and
max_cycle_over_two_expected. The ratios include every supported trace; edge gaps
subtract clock uncertainty. Inspect these margins on the first paid calibration
slice before approving a full matrix. This is sampling coverage, not proof of
sensor calibration, continuous waveform reconstruction or attribution precision.

### Serving parser bindings (R6)

Every agent model and monitor_serving entry declares reasoning_parser (including
null) and its source; vLLM receives exactly that value. Qwen3 hybrid 4B/8B/14B/30B
uses qwen3 rather than the cards' deepseek_r1 because thinking-off output has
neither tag. Qwen3-Next Thinking/BF16 and FP8 use deepseek_r1 because the template
supplies the opening tag. No --enable-reasoning option is passed in vLLM 0.10.2.
Sources are pinned cards and parser code quoted from the lead's fix-2 brief,
explicitly marked as fetched by the lead, not this seat.

Tool parsers and automatic tool choice are also per model. Agents retain hermes
with tool_call_parser_source_not_fetched; monitors call no tools and use null.
Budget driver OPEN ISSUE: hybrid output truncated by max_tokens before </think>
comes back as content beginning with <think> under qwen3; check content for that
prefix before reporting reasoning counts.

### CLI outcomes (R8)

The matrix is read and validated before inventory, NVML preflight or vLLM.
Missing, unreadable or invalid matrices and session_failed:* exceptions seal a
receipt with status failed, data_complete=false and exit 3. Physical isolation or
instrument-readiness refusal keeps status refused and exit 2. completed and
completed_with_flags exit 0; inspect data_complete and flags as well as the exit.

### CUDA/NVML device order (R9)

Both agent and monitor vLLM children receive CUDA_DEVICE_ORDER=PCI_BUS_ID alongside
their explicit CUDA_VISIBLE_DEVICES list. This selects PCI bus order rather than
CUDA's default FASTEST_FIRST heuristic for the numeric indices used by NVML.
NVIDIA reference: https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#env-vars
(CUDA_DEVICE_ORDER); canonical reference supplied for operators, not fetched by
this executor-less seat. Placement tests record the actual child's environment
and require PCI_BUS_ID for both agent and monitor processes.

### Model dimension/count provenance (R7)

Model-count citations now quote the pinned Hugging Face cards verbatim (including
their spelling); hidden_size and vocab_size quote their separate config.json
lines at the same supplied commits. These are lead-fetched sources quoted from
the fix-2 brief, dated 2026-10-22 with that distinction in each note. Card and
config provenance pins do not select model weights: serving revisions remain
null and must be frozen before paid work. No parameter count, decode weight
formula or printed cost/throughput number changes.

### Driver power-limit names (GK2-5)

For v12/v13 gpu_power_readings, current_power_limit records the enforced board
limit and requested_power_limit records the requested limit. Legacy
power_readings/enforced_power_limit remains supported. Module/platform readings
do not overwrite board readings. The telegraf schema_v12 and schema_v13 types.go
files at commit 2156aa5089436522eec36b05fad94d850c728388 were read through GitHub
by this seat on 2026-10-22; both paths are cited in throttle.py.
