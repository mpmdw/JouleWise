# Whole-GPU campaign kit (internal, build only)

Status: PROVISIONAL. No rental or hardware measurement is authorized by this kit.
Ed must approve the provider and spend before anyone starts a paid session.
Power counts work; it cannot identify what one forward pass computes.

## What is supplied

- configs/align/shade.json: five public SHADE pairs, benign/sabotage,
  Qwen3-8B and Qwen3-30B-A3B, three seed slots: 60 episodes.
- configs/align/moe_stage_a.json: the same pairs, conditions and seeds for
  the MoE model: 30 episodes. Join to the MoE subset of the baseline by
  task, condition, model and seed. This is an instrumented repeat.
- configs/align/budget.json: Qwen3-4B/8B/14B and Phi-3.5-mini-instruct,
  whose multi-head attention contrasts with Qwen3's grouped-query attention.
  There are 32 item slots, three seeds and 11 conditions: thinking on/off,
  concise, budgets 1/0.6/0.4/0.3 of the per-item median, and four matching
  random-deletion controls. This means 4,224 trial rows, 5,760 fresh
  generation episodes including calibration and paired no-hint generations,
  and 4,224 monitor calls. Deletion reuses generation energy.
- gpukit/matrix.schema.json describes the lane-local input format;
  matrix.validate adds expansion-count checks. The format is v2 after replacing
  invented rates with source-derived ceilings; the shared records are unchanged.
- runner_adapter.py writes one provisional runner-format matrix per model;
  the documented runner CLI is the default session command.
- bootstrap.sh and session.py install and orchestrate serial campaigns.
- cost.py calculates serial wall time, GPU-hours and a supplied hourly price.

The five public pair names come from jkutaso/SHADE-Arena at
6614e77191c1f8e2d0c44c123c6f915905ebafae: american_airlines_2,
api_key_calendar_agendas_2, bank_transfer_2, expenditure_accounting,
spam_filter_update. No upstream source is vendored.

## Estimate and approval

The configs derive optimistic, single-stream BF16 ceilings from the exact SKU
specifications and model-card active parameter counts. Every physical input
carries its URL, access date (2026-10-22), units and derivation:

- [NVIDIA A100 datasheet](https://images.nvidia.com/data-center/a100/a100-datasheet.pdf),
  page 1: A100 SXM4 80GB has 2,039 GB/s bandwidth and 312 dense BF16 TFLOPS.
- [NVIDIA H100 datasheet, hosted by Dell](https://i.dell.com/sites/csdocuments/App-Merchandizing_Documents/en/us/h100-gpu.pdf),
  page 1: H100 SXM 80GB has 3.35 TB/s bandwidth. Its 1,979 sparse BF16 TFLOPS
  become 989.5 dense TFLOPS by the datasheet's divide-by-two footnote.
  These match the [NVIDIA specification table](https://www.nvidia.com/en-us/data-center/h100/).
- [NVIDIA L40S datasheet, hosted by KRinfra](https://www.krinfra.co.kr/download/l40s-datasheet-2841316.pdf),
  page 2: L40S PCIe 48GB has 864 GB/s GDDR6 bandwidth and 362.05 dense BF16 TFLOPS.
  Use the printed dense column, not half its inconsistent sparse column.
  The [NVIDIA table](https://www.nvidia.com/en-us/data-center/l40s/) agrees.
- Hugging Face cards give Qwen3 [4B](https://huggingface.co/Qwen/Qwen3-4B)
  4.0B, [8B](https://huggingface.co/Qwen/Qwen3-8B) 8.2B,
  [14B](https://huggingface.co/Qwen/Qwen3-14B) 14.8B and
  [30B-A3B](https://huggingface.co/Qwen/Qwen3-30B-A3B) 30.5B total /
  3.3B active parameters. [Phi-3.5-mini](https://huggingface.co/microsoft/Phi-3.5-mini-instruct)
  is dense with 3.8B parameters. Dense models use total as active.

For active parameter count P, BF16 uses two bytes per weight and a multiply-add
uses two FLOPs. The ceiling rates are bandwidth/(2P) decoded tokens/s and
dense BF16 FLOP/s/(2P) prefill tokens/s. They omit KV reads and attention FLOPs,
which increase with context, as well as launch and serving overheads. These
are the brief's idealized full-weight-read bounds for serial single-stream BF16;
they do not describe batching, quantization, speculative decode or cache reuse.
The model-card counts are rounded inputs, not exact tensor inventories.
Total resident parameters determine weight fit, even for MoE: 30.5B * 2 bytes
already exceeds a 48GB L40S before KV cache. That profile needs another serving
configuration; this condition is a flag, never a discarded requested row.

The lower bound sums prefill_tokens / prefill_ceiling and
decode_tokens / decode_ceiling for all fresh generations and monitor calls.
It excludes setup, model loading, tool waiting, host overhead and router overhead,
whose current allowances are explicit operator inputs, not established minima.

Each model/GPU entry also has an efficiency fraction of the ceiling.
No suitable measurement is established in this build: efficiency and its source
are null, planning_wall_seconds is null, and throughput_efficiency_not_supplied
is recorded. A supplied efficiency must carry a public measurement URL and date
for the matching workload. Do not substitute an unrelated aggregate benchmark.
With sourced efficiencies, cost.estimate divides each inference term by its
efficiency, adds wait/host allowances, applies Stage A's router-overhead allowance,
adds monitor work, setup and (2 * model count + 1) model loads. This is the
retained serial swap policy. gpu_count multiplies billed time; it does not imply
tensor-parallel acceleration.

The API retains full arithmetic precision. Configs and the cost CLI print two
significant digits, matching the least precise active counts (4.0B and 3.3B).
Lower bounds round down to preserve direction; planning values round to nearest.
A lower bound cannot be used as Ed's rental budget.

| Matrix | A100 SXM4 80GB lower bound (s) | H100 SXM 80GB lower bound (s) | L40S PCIe 48GB lower bound (s) |
|---|---:|---:|---:|
| SHADE | 2,800 | 1,700 | 6,500 |
| MoE Stage A | 830 | 490 | 1,800 |
| Budget | 91,000 | 54,000 | 210,000 |

These are calculations on configured token-volume inputs, not observed run times.
Budget pilot size and workload allowances remain explicit operator parameters.
Its 32 slots and three seeds are not statistical recommendations. Unsupported
thinking controls on the attention comparison model remain flags.

Example prices are empty. Supply an actual quote:

    python3 -m joulewise.align.gpukit.cost configs/align/shade.json \
      --gpu-class H100-SXM-80GB --usd-per-gpu-hour "$APPROVED_HOURLY_USD"

Ed approves the provider/region, whole-GPU class/count, storage and return
destination; immutable repo/model/dataset revisions and pilot size; a dated
hourly quote, maximum billed hours and total spend; and who stops the instance.
The concrete runner/router integration must pass an offline rehearsal first.
GPU-hour estimates exclude provider storage, transfer, taxes and billing
granularity. Timeouts are operational parameters, not cost caps.
The kit does not provision, rent, terminate, or stop billing a VM.

## Integration dependency before rental

The spine contains shared records/interfaces only. Session invokes
python -m joulewise.align.power.preflight by module name, expecting the NVML
lane's module. Stdout/stderr and return code are retained in preflight.log.
A nonzero code becomes nvml_preflight_failed; evidence is retained.

The default runner command is:

    <session-python> -m joulewise.align run --matrix {runner_matrix}

Supply --runner-settings with an operator-authored JSON object. It requires
task_factory, endpoint_factory, monitor_factory, sampler_factory,
token_counter_factory (registered names), order_seed, max_turns, max_tokens
and temperature. Optional task_config, endpoint_config, monitor_config,
sampler_config, token_counter_config dictionaries and an imports list pass
through to the runner. Names and run limits are required parameters; no
unmerged lane's factory names or production cutoffs are guessed here.

The adapter injects task_pair, model/revision, loopback base_url ending /v1,
sampling interval_ns and router_logging into the appropriate factory config.
Factories must implement those parameters; the router request is not evidence
that routing was captured. The per-model runner-matrix.json is bundled for review.
Missing settings or unavailable factories remain flags and preserve the bundle.

The adapter follows docs/align/runner.md on lane/2026-10-21-align-runner and
remains PROVISIONAL until that lane merges and the real factories are rehearsed.
It supports SHADE and MoE Stage A. Budget effort conditions require the budget
driver: default translation records budget_runner_adapter_required, retains
the requested matrix, and does no generation. Supply its integrated command
with --runner-command; no budget conditions are relabeled.

A custom --runner-command remains a JSON argv array. Session substitutes these
fields, one model at a time:

| Placeholder | Meaning |
|---|---|
| {matrix} | Absolute path to bundled normalized gpukit matrix |
| {runner_matrix} | Per-model runner-format matrix (default adapter path only) |
| {model} | Model ID to select from that matrix |
| {endpoint} | Loopback vLLM base URL |
| {output} | Required shared-record Episode JSONL output |
| {sample_interval_ns} | Requested NVML polling cadence |
| {router_logging} | true for Stage A, otherwise false |

The runner reads the schema, selects the named model, runs requested rows
with a PowerSampler beside every episode, and writes shared Episode records.
For budget, export fresh generation episodes only: calibration plus hinted
and no-hint generations, never duplicated deletion views. Keep trial journals
and monitor outputs beside {output}; packaging includes them automatically.
All cross-lane outputs use the shared records.

The concrete factories and argv must be rehearsed on an integrated checkout
before rental. Missing runner, preflight, power, output or router logs remain
recorded flags. Missing default-runner settings produce no endpoint work.

The current MoE lane hooks target Hugging Face eager execution, not vLLM
workers. A vLLM router-capture bridge remains a MoE/runner integration dependency.
Session checks Episode.router_log and records episode_router_log_missing.
A populated RouterLog still needs the MoE lane's coverage validation.

Budget item slots must resolve to an immutable public item manifest through
the budget adapter; they are not invented MMLU examples. Committed model
revisions are null and flagged. Fill them with immutable Hub commit IDs,
use the same tokenizer revision, and recheck attention layouts before the
scientific run. No live compatibility or calibration claim is made for
the selected vLLM 0.10.2 install pin.

## Session procedure

Use a fresh Ubuntu 24.04-style host with NVIDIA driver, Python >=3.11, venv,
git and rsync (or AWS CLI for S3) available. Clone the reviewed integration
head. No credentials belong in files or command templates; SSH/AWS use
ambient operator authentication.

From the checkout root:

    bash joulewise/align/gpukit/bootstrap.sh --check-only

Inventory reads NVIDIA XML. Explicit MIG or vGPU refuses, as required by
the brief. Unknown/unavailable isolation information is flagged. Provider
confirmation and NVML preflight must complete the tenancy check. Session
checks the selected GPU; bootstrap's preliminary check uses GPU 0.

After the integrated offline rehearsal and Ed's approval, supply RUNNER_SETTINGS
as the path to the reviewed factory/limit settings JSON and timeouts from the
approved loading/campaign plan. Budget uses --runner-command instead:

    bash joulewise/align/gpukit/bootstrap.sh configs/align/shade.json \
      --output /data/campaign-unique-id \
      --runner-settings "$RUNNER_SETTINGS" \
      --ready-timeout-s "$APPROVED_MODEL_LOAD_TIMEOUT_S" \
      --command-timeout-s "$APPROVED_COMMAND_TIMEOUT_S" \
      --poll-s "$APPROVED_READINESS_POLL_S" \
      --destination return-host:/approved/results/ --copy-kind rsync

Bootstrap creates .gpukit-venv (JOULEWISE_VENV overrides it), installs
vllm==0.10.2 and this checkout, then enters session.py. --skip-install selects
$JOULEWISE_VENV/bin/python (default .gpukit-venv/bin/python) when executable
and exports its bin directory so vllm resolves from the same environment.
Without an existing venv it uses JOULEWISE_PYTHON or python3; that fallback
requires an already prepared interpreter. JOULEWISE_PYTHON chooses the creator
interpreter for a fresh installation; an existing venv wins on --skip-install.
No CUDA install has been tested by this build.

Session starts one agent endpoint on loopback, polls /health, invokes the
runner, and terminates its serving process group before loading another
model. Select GPU and port with --gpu-index and --port. GPU index is the
physical nvidia-smi index, exported to the child as CUDA_VISIBLE_DEVICES.
The runner owns monitor placement/scheduling and must prevent unrelated
work during sampled agent episodes.

--ready-command, --preflight-command and --vllm-command accept JSON argv arrays
for operational adapters and offline tests. Readiness commands replace HTTP
polling. Never substitute test stubs for scientific hardware preflight.

Output includes matrix, inventory/receipt, package list and Git head, preflight
log, server/runner logs, Episodes and runner sidecars. CLI exit 2 is explicit
MIG/vGPU refusal; exit 0 still requires reading flags and inspecting completeness.

## Copy-back and integrity

Existing output directories are never reused. Session hashes all regular
output files, creates a sibling tar.gz and detached archive checksum, then
copies both. Symlinks are omitted and flagged. The manifest does not hash
itself; the archive checksum covers it.

Use rsync, or --copy-kind s3 with an S3 destination and ambient AWS credentials.
The local copy kind is for offline rehearsal. Failed transfer preserves the
local archive and writes a sibling transfer receipt. This receipt is outside
the sealed archive because transfer happens after sealing. Retry the copy
from preserved files; do not rerun the campaign to repair a transfer.

At the destination use sha256sum -c on the detached checksum, extract into an
empty directory, then run:

    python3 -c 'from pathlib import Path; from joulewise.align.gpukit.session import verify_manifest; print(verify_manifest(Path("/returned/campaign-unique-id")))'

An empty tuple means inventory and bytes match. Hashes establish copy integrity,
not independent custody against an adversary who can rewrite data and manifest.
Keep an off-box copy and verify it before stopping billing in the provider console.

## Offline verification

Tests never contact a network or GPU:

    python3 -m unittest tests.align.test_gpukit -v
    python3 -m unittest discover -s tests/align -t .
    python3 -m unittest discover -s tests

The shell rehearsal uses fake NVIDIA XML, fake vLLM and a runner fixture writing
shared records through the real session, packer and copy-back. It does not
validate the agentic runner or CUDA stack. JSON Schema tests lazily import
optional jsonschema and skip if absent. See the lane report for actual commands
and results; test descriptions alone are not evidence.
